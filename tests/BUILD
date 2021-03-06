
licenses(["notice"])

TEST_HEADERS = [
   "test_macros.h",
   "test_common.h",
   "class_construction_tracker.h",
]

filegroup(
    name = "test_headers_filegroup",
    srcs = TEST_HEADERS,
    visibility = ["//third_party/fruit/tests:__subpackages__"],
)

cc_library(
    name = "test_headers",
    srcs = [],
    hdrs = TEST_HEADERS,
    visibility = ["//third_party/fruit/tests:__subpackages__"],
    includes = ["."],
)

[cc_test(
    name = filename[:-4],
    srcs = [filename],
    deps = [
        ":test_headers",
        "//third_party/fruit",
    ]
) for filename in glob(
    ["*.cpp"],
    exclude = ["include_test.cpp"])]

FRUIT_PUBLIC_HEADERS = [
    "component",
    "fruit",
    "fruit_forward_decls",
    "injector",
    "macro",
    "normalized_component",
    "provider",
]

genrule(
    name = "fruit_test_config_genrule",
    srcs = [
        "//third_party/fruit",
        "//third_party/fruit:fruit_headers",
        ":test_headers_filegroup",
    ],
    # Here we copy libfruit.so to work around an issue with py_test where the outputs of a cc_library in the data
    # attribute of a py_test are not taken into account.
    outs = [
        "fruit_test_config.py",
        "libfruit.so"
    ],
    visibility = ["//third_party/fruit/tests:__subpackages__"],
    cmd = ""
          + "FRUIT_HEADERS_LOCATION=`for f in $(locations //third_party/fruit:fruit_headers); do echo \"$$f\"; done | fgrep configuration/bazel/ | head -n 1 | sed 's|configuration/bazel/.*|./|'`;"
          + "TEST_HEADERS_LOCATION=`for f in $(locations :test_headers_filegroup); do echo \"$$f\"; done | fgrep test_macros.h | sed 's|test_macros.h|./|'`;"
          + "LIBFRUIT_LOCATION=`for f in $(locations //third_party/fruit); do echo \"$$f\"; done | fgrep libfruit.so | head -n 1 | sed 's|libfruit.so|./|'`;"
          + "cp $${LIBFRUIT_LOCATION}/libfruit.so $(location libfruit.so);"
          # The removal of ".*/genfiles" from the location is a bit of a hack, but that's how the path will look like in the py_tests
          # below.
          + "LIBFRUIT_COPY_LOCATION=`dirname $(location libfruit.so) | sed 's|.*/genfiles/|./|'`;"
          + "echo -e \""
          + "CXX='g++'\n"
          + "CXX_COMPILER_NAME='GNU'\n"
          + "FRUIT_COMPILE_FLAGS='$(CC_FLAGS) -std=c++0x -W -Wall -Wno-missing-braces -g -Werror'\n"
          + "PATH_TO_COMPILED_FRUIT='$${LIBFRUIT_COPY_LOCATION}'\n"
          + "PATH_TO_FRUIT_STATIC_HEADERS='$${FRUIT_HEADERS_LOCATION}/include'\n"
          + "PATH_TO_FRUIT_GENERATED_HEADERS='$${FRUIT_HEADERS_LOCATION}/configuration/bazel'\n"
          + "PATH_TO_FRUIT_TEST_HEADERS='$${TEST_HEADERS_LOCATION}'\n"
          + "ADDITIONAL_LINKER_FLAGS=''\n"
          + "RUN_TESTS_UNDER_VALGRIND='0'\n"
          + "VALGRIND_FLAGS=''\n"
          + "\" > $(location fruit_test_config.py)",
)

py_library(
    name = "fruit_test_common",
    srcs = ["fruit_test_common.py", "fruit_test_config.py", "conftest.py"],
    imports = ["."],
    srcs_version = "PY3",
    visibility = ["//third_party/fruit/tests:__subpackages__"],
)

exports_files(["pytest.ini"])

load("//third_party/fruit/tests:build_defs.bzl", "fruit_py_test")

[
    fruit_py_test(
        filename = filename
    )
    for filename in glob(["test_*.py"])
]
