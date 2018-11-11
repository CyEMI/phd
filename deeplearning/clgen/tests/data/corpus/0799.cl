__attribute__((__overloadable__)) float fn_A(float A, float B) {
  typedef int iscalar_t;
  typedef int jscalar_t;
  typedef int kscalar_t;
  typedef float scalar_t;
  typedef int ivector_t;
  typedef int jvector_t;
  typedef int kvector_t;
  typedef float vector_t;

  return ({
    vector_t C = atan(A / B);
    B > (scalar_t)0 ? C : B < (scalar_t)0 ? C + copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(3.14) : (scalar_t)(0x1.921fb6p+1f))), A) : copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(0x1.921fb54442d18p+0) : (scalar_t)(0x1.921fb6p+0f))), A);
  });
}

__attribute__((__overloadable__)) float2 fn_A(float2 A, float2 B) {
  typedef int iscalar_t;
  typedef int jscalar_t;
  typedef int kscalar_t;
  typedef float scalar_t;
  typedef int2 ivector_t;
  typedef int2 jvector_t;
  typedef int2 kvector_t;
  typedef float2 vector_t;

  return ({
    vector_t C = atan(A / B);
    B > (scalar_t)0 ? C : B < (scalar_t)0 ? C + copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(3.14) : (scalar_t)(0x1.921fb6p+1f))), A) : copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(0x1.921fb54442d18p+0) : (scalar_t)(0x1.921fb6p+0f))), A);
  });
}

__attribute__((__overloadable__)) float3 fn_A(float3 A, float3 B) {
  typedef int iscalar_t;
  typedef int jscalar_t;
  typedef int kscalar_t;
  typedef float scalar_t;
  typedef int3 ivector_t;
  typedef int3 jvector_t;
  typedef int3 kvector_t;
  typedef float3 vector_t;

  return ({
    vector_t C = atan(A / B);
    B > (scalar_t)0 ? C : B < (scalar_t)0 ? C + copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(3.14) : (scalar_t)(0x1.921fb6p+1f))), A) : copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(0x1.921fb54442d18p+0) : (scalar_t)(0x1.921fb6p+0f))), A);
  });
}

__attribute__((__overloadable__)) float4 fn_A(float4 A, float4 B) {
  typedef int iscalar_t;
  typedef int jscalar_t;
  typedef int kscalar_t;
  typedef float scalar_t;
  typedef int4 ivector_t;
  typedef int4 jvector_t;
  typedef int4 kvector_t;
  typedef float4 vector_t;

  return ({
    vector_t C = atan(A / B);
    B > (scalar_t)0 ? C : B < (scalar_t)0 ? C + copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(3.14) : (scalar_t)(0x1.921fb6p+1f))), A) : copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(0x1.921fb54442d18p+0) : (scalar_t)(0x1.921fb6p+0f))), A);
  });
}

__attribute__((__overloadable__)) float8 fn_A(float8 A, float8 B) {
  typedef int iscalar_t;
  typedef int jscalar_t;
  typedef int kscalar_t;
  typedef float scalar_t;
  typedef int8 ivector_t;
  typedef int8 jvector_t;
  typedef int8 kvector_t;
  typedef float8 vector_t;

  return ({
    vector_t C = atan(A / B);
    B > (scalar_t)0 ? C : B < (scalar_t)0 ? C + copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(3.14) : (scalar_t)(0x1.921fb6p+1f))), A) : copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(0x1.921fb54442d18p+0) : (scalar_t)(0x1.921fb6p+0f))), A);
  });
}

__attribute__((__overloadable__)) float16 fn_A(float16 A, float16 B) {
  typedef int iscalar_t;
  typedef int jscalar_t;
  typedef int kscalar_t;
  typedef float scalar_t;
  typedef int16 ivector_t;
  typedef int16 jvector_t;
  typedef int16 kvector_t;
  typedef float16 vector_t;

  return ({
    vector_t C = atan(A / B);
    B > (scalar_t)0 ? C : B < (scalar_t)0 ? C + copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(3.14) : (scalar_t)(0x1.921fb6p+1f))), A) : copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(0x1.921fb54442d18p+0) : (scalar_t)(0x1.921fb6p+0f))), A);
  });
}

__attribute__((__overloadable__)) double fn_A(double A, double B) {
  typedef long iscalar_t;
  typedef int jscalar_t;
  typedef int kscalar_t;
  typedef double scalar_t;
  typedef long ivector_t;
  typedef int jvector_t;
  typedef int kvector_t;
  typedef double vector_t;

  return ({
    vector_t C = atan(A / B);
    B > (scalar_t)0 ? C : B < (scalar_t)0 ? C + copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(3.14) : (scalar_t)(0x1.921fb6p+1f))), A) : copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(0x1.921fb54442d18p+0) : (scalar_t)(0x1.921fb6p+0f))), A);
  });
}

__attribute__((__overloadable__)) double2 fn_A(double2 A, double2 B) {
  typedef long iscalar_t;
  typedef long jscalar_t;
  typedef int kscalar_t;
  typedef double scalar_t;
  typedef long2 ivector_t;
  typedef long2 jvector_t;
  typedef int2 kvector_t;
  typedef double2 vector_t;

  return ({
    vector_t C = atan(A / B);
    B > (scalar_t)0 ? C : B < (scalar_t)0 ? C + copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(3.14) : (scalar_t)(0x1.921fb6p+1f))), A) : copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(0x1.921fb54442d18p+0) : (scalar_t)(0x1.921fb6p+0f))), A);
  });
}

__attribute__((__overloadable__)) double3 fn_A(double3 A, double3 B) {
  typedef long iscalar_t;
  typedef long jscalar_t;
  typedef int kscalar_t;
  typedef double scalar_t;
  typedef long3 ivector_t;
  typedef long3 jvector_t;
  typedef int3 kvector_t;
  typedef double3 vector_t;

  return ({
    vector_t C = atan(A / B);
    B > (scalar_t)0 ? C : B < (scalar_t)0 ? C + copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(3.14) : (scalar_t)(0x1.921fb6p+1f))), A) : copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(0x1.921fb54442d18p+0) : (scalar_t)(0x1.921fb6p+0f))), A);
  });
}

__attribute__((__overloadable__)) double4 fn_A(double4 A, double4 B) {
  typedef long iscalar_t;
  typedef long jscalar_t;
  typedef int kscalar_t;
  typedef double scalar_t;
  typedef long4 ivector_t;
  typedef long4 jvector_t;
  typedef int4 kvector_t;
  typedef double4 vector_t;

  return ({
    vector_t C = atan(A / B);
    B > (scalar_t)0 ? C : B < (scalar_t)0 ? C + copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(3.14) : (scalar_t)(0x1.921fb6p+1f))), A) : copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(0x1.921fb54442d18p+0) : (scalar_t)(0x1.921fb6p+0f))), A);
  });
}

__attribute__((__overloadable__)) double8 fn_A(double8 A, double8 B) {
  typedef long iscalar_t;
  typedef long jscalar_t;
  typedef int kscalar_t;
  typedef double scalar_t;
  typedef long8 ivector_t;
  typedef long8 jvector_t;
  typedef int8 kvector_t;
  typedef double8 vector_t;

  return ({
    vector_t C = atan(A / B);
    B > (scalar_t)0 ? C : B < (scalar_t)0 ? C + copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(3.14) : (scalar_t)(0x1.921fb6p+1f))), A) : copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(0x1.921fb54442d18p+0) : (scalar_t)(0x1.921fb6p+0f))), A);
  });
}

__attribute__((__overloadable__)) double16 fn_A(double16 A, double16 B) {
  typedef long iscalar_t;
  typedef long jscalar_t;
  typedef int kscalar_t;
  typedef double scalar_t;
  typedef long16 ivector_t;
  typedef long16 jvector_t;
  typedef int16 kvector_t;
  typedef double16 vector_t;

  return ({
    vector_t C = atan(A / B);
    B > (scalar_t)0 ? C : B < (scalar_t)0 ? C + copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(3.14) : (scalar_t)(0x1.921fb6p+1f))), A) : copysign(((sizeof(scalar_t) == sizeof(double) ? (scalar_t)(0x1.921fb54442d18p+0) : (scalar_t)(0x1.921fb6p+0f))), A);
  });
}