cc_library(
    name = "main",
    srcs = glob(["src/*.cc"]),
    hdrs = glob(["include/phd/*"]),
    copts = [
        "-Ilib/phd/include",
        "-Iexternal/gtest/include",
        "-Iexternal/benchmark/include",
    ],
    visibility = ["//visibility:public"],
    deps = [
        "@com_github_google_benchmark//:benchmark",
        "@gtest//:main",
    ],
)
