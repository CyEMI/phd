__kernel void fn_A(__global float* A, __global float* B) {
  int C = (int)get_global_id(0);
  B[C] = min(A[C], A[0]);
}