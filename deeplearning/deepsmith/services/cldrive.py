import subprocess
import tempfile
import time
import typing
from concurrent import futures

import grpc
from absl import app
from absl import flags
from absl import logging

from deeplearning.deepsmith.proto import deepsmith_pb2
from deeplearning.deepsmith.proto import harness_pb2
from deeplearning.deepsmith.proto import harness_pb2_grpc
from deeplearning.deepsmith.proto import service_pb2
from deeplearning.deepsmith.services import harness
from deeplearning.deepsmith.services import services
from gpu import cldrive as cldrive_lib
from gpu.cldrive import cldrive
from gpu.cldrive import env
from lib.labm8 import fs
from lib.labm8 import labdate
from lib.labm8 import system


FLAGS = flags.FLAGS


class CldriveHarness(harness.HarnessBase,
                     harness_pb2_grpc.HarnessServiceServicer):
  """A harness for running OpenCL testcases using cldrive."""

  def __init__(self, config: harness_pb2.CldriveHarness):
    """Instantiate a CLdrive harness service.

    Args:
      config: A CldriveHarness proto.

    Raises:
      LookupError: If a requested 'opencl_env' is not available.
      EnvironmentError: If no 'opencl_env' were requested, and none are
        available on the host.
    """
    super(CldriveHarness, self).__init__(config)

    # Match and instantiate the OpenCL environments.
    all_envs = {env.name: env for env in cldrive.GetOpenClEnvironments()}
    if self.config.opencl_env:
      self.envs = []
      for opencl_env in sorted(set(self.config.opencl_env)):
        if opencl_env in all_envs:
          self.envs.append(all_envs[opencl_env])
        else:
          raise LookupError(
              f"Requested OpenCL environment not available: '{opencl_env}'")
    else:
      self.envs = all_envs.values()
    if not self.envs:
      raise EnvironmentError('No OpenCL environments available')

    self.testbeds = [OpenClEnvironmentToTestbed(e) for e in self.envs]
    self.ids = [e.ids() for e in self.envs]

    # Logging output.
    for testbed in self.testbeds:
      logging.info('OpenCL testbed:\n%s', testbed)

  def GetHarnessCapabilities(self,
                             request: harness_pb2.GetHarnessCapabilitiesRequest,
                             context) -> harness_pb2.GetHarnessCapabilitiesResponse:
    """Get the harness capabilities."""
    del context
    logging.info('GetHarnessCapabilities() client=%s', request.status.client)
    response = services.BuildDefaultResponse(
        harness_pb2.GetHarnessCapabilitiesRequest)
    response.harness.name = 'cldrive'
    response.testbed.extend(self.testbeds)
    return response

  def RunTestcases(self, request: harness_pb2.RunTestcasesRequest,
                   context) -> harness_pb2.RunTestcasesResponse:
    del context
    logging.info('RunTestcases() client=%s', request.status.client)
    response = services.BuildDefaultResponse(harness_pb2.RunTestcasesResponse)
    if request.testbed not in self.testbeds:
      response.status.returncode = service_pb2.ServiceStatus.INVALID_REQUEST_PARAMETERS
      response.status.error_message = 'Requested testbed not found.'
      return response

    testbed_idx = self.testbeds.index(request.testbed)
    for testcase in request.testcases:
      response.results.extend([RunTestcase(
          self.ids[testbed_idx], self.testbeds[testbed_idx], testcase)])

    return response


def OpenClEnvironmentToTestbed(
    opencl_environment: env.OpenCLEnvironment) -> deepsmith_pb2.Testbed:
  """Instantiate a DeepSmith testbed from an OpenCL environment.

  Args:
    opencl_environment: A cldrive OpenCLEnvironment instance.

  Returns:
    A Testbed proto instance.
  """
  testbed = deepsmith_pb2.Testbed()
  testbed.toolchain = 'opencl'
  testbed.name = opencl_environment.name
  testbed.opts['platform'] = opencl_environment.platform_name
  testbed.opts['device'] = opencl_environment.device_name
  testbed.opts['driver'] = opencl_environment.driver_version
  testbed.opts['device_type'] = opencl_environment.device_type
  testbed.opts['opencl_version'] = opencl_environment.opencl_version
  return testbed


def RunTestcase(ids: typing.Tuple[int, int],
                testbed: deepsmith_pb2.Testbed,
                testcase: deepsmith_pb2.Testcase) -> deepsmith_pb2.Result:
  """Run a testcase."""
  assert testcase.toolchain == 'opencl'
  result = deepsmith_pb2.Result()
  result.testcase.CopyFrom(testcase)
  result.testbed.CopyFrom(testbed)
  platform_id, device_id = ids
  driver = MakeDriver(testcase)
  # Get a temporary file to write and run the driver from.
  with tempfile.NamedTemporaryFile(prefix='deepsmith_', delete=False) as f:
    path = f.name
  try:
    CompileDriver(driver, path, platform_id, device_id)
    timeout = testcase.harness.opts.get('timeout_seconds', '60')
    cmd = ['timeout', '-s9', timeout, f.name]
    logging.debug('$ %s', ' '.join(cmd))
    start_time = labdate.GetUtcMillisecondsNow()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True)
    stdout, stderr = proc.communicate()
    end_time = labdate.GetUtcMillisecondsNow()
    # Build result message.
    result.returncode = proc.returncode
    result.outputs['stdout'] = stdout
    result.outputs['stderr'] = stderr
    runtime = result.profiling_events.add()
    runtime.client = system.HOSTNAME
    runtime.type = 'runtime'
    runtime.duration_ms = int(round(
        (end_time - start_time).total_seconds() * 1000))
    runtime.event_start_epoch_ms = labdate.MillisecondsTimestamp(start_time)
  finally:
    fs.rm(path)
  return result


def MakeDriver(testcase: deepsmith_pb2.Testcase) -> str:
  """Generate a self-contained C program for the given test case."""
  try:
    # Generate a compile-and-execute test harness.
    gsize = cldrive_lib.NDRange(
        *[int(x) for x in testcase.inputs['gsize'].split(',')])
    lsize = cldrive_lib.NDRange(
        *[int(x) for x in testcase.inputs['lsize'].split(',')])
    size = max(gsize.product * 2, 256)
    inputs = cldrive_lib.make_data(
        src=testcase.inputs['src'], size=size,
        data_generator=cldrive_lib.Generator.ARANGE,
        scalar_val=size)
    src = cldrive_lib.emit_c(
        src=testcase.inputs['src'], inputs=inputs, gsize=gsize, lsize=lsize)
  except Exception:
    # Create a compile-only stub if not possible.
    try:
      src = cldrive_lib.emit_c(
          src=testcase.inputs['src'], inputs=None, gsize=None, lsize=None,
          compile_only=True)
    except Exception:
      # Create a compiler-only stub without creating kernel.
      src = cldrive_lib.emit_c(
          src=testcase.inputs['src'], inputs=None, gsize=None, lsize=None,
          compile_only=True, create_kernel=False)
  return src


def CompileDriver(src: str, path: str, platform_id,
                  device_id, cc: str = 'gcc',
                  cflags: typing.Optional[typing.List[str]] = None,
                  timeout: int = 60) -> None:
  """Compile driver binary from source."""
  # Assign default compilation flags.
  cflags = cflags or ["-std=c99", "-Wno-deprecated-declarations"]
  if system.is_linux():
    cflags.append('-lOpenCL')
  elif system.is_mac():
    cflags += ['-framework', 'OpenCL']

  cmd = ['timeout', '-s9', str(timeout), cc, '-xc', '-', '-o', str(path),
         f'-DPLATFORM_ID={platform_id}', f'-DDEVICE_ID={device_id}'] + cflags
  logging.debug('$ %s', ' '.join(cmd))
  proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
  proc.communicate(src.encode('utf-8'))
  if not proc.returncode == 0:
    raise EnvironmentError(
        f'Driver compilation failed with returncode {proc.returncode}.\n'
        f'Driver source:\n{src}')
  return path


def main(argv):
  if len(argv) > 1:
    raise app.UsageError('Unrecognized arguments')
  harness_config = services.ServiceConfigFromFlag(
      'harness_config', harness_pb2.CldriveHarness())
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  services.AssertLocalServiceHostname(harness_config.service)
  service = CldriveHarness(harness_config)
  harness_pb2_grpc.add_HarnessServiceServicer_to_server(service, server)
  server.add_insecure_port(f'[::]:{harness_config.service.port}')
  logging.info('%s listening on %s:%s', type(service).__name__,
               harness_config.service.hostname,
               harness_config.service.port)
  server.start()
  try:
    while True:
      time.sleep(3600 * 24)
  except KeyboardInterrupt:
    server.stop(0)


if __name__ == '__main__':
  app.run(main)
