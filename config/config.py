"""
Configuration options for running Spark performance tests.

When updating `spark-perf`, you should probably use `diff` to compare the updated template to
your modified `config.py` file and copy over any new configurations.
"""

import time
import os
import os.path
import socket

from sparkperf.config_utils import FlagSet, JavaOptionSet, OptionSet, ConstantOption


# ================================ #
#  Standard Configuration Options  #
# ================================ #

DEFAULT_HOME=os.environ['HOME']

# Point to an installation of Spark on the cluster.
SPARK_HOME_DIR = os.getenv('SPARK_HOME', DEFAULT_HOME)

# Use a custom configuration directory
SPARK_CONF_DIR = SPARK_HOME_DIR + "/conf"

# Master used when submitting Spark jobs.
# for ec2 clusters: open("/root/spark-ec2/cluster-url", 'r').readline().strip()
# For local clusters (default): "spark://%s:7077" % socket.gethostname()
# For Yarn clusters: "yarn"

SPARK_CLUSTER_URL="yarn"

IS_YARN_MODE = "yarn" in SPARK_CLUSTER_URL
IS_MESOS_MODE = "mesos" in SPARK_CLUSTER_URL

# Specify URI to download spark executor. This only applied for running with Mesos.
#SPARK_EXECUTOR_URI = "http://localhost:8000/spark.tgz"

# Path to the Mesos native library. This is only required for running with Mesos.
#MESOS_NATIVE_LIBRARY = "/usr/local/lib/libmesos.so"

# Run Mesos client in coarse or fine grain mode. This is only applied for running with Mesos.
#SPARK_MESOS_COARSE = True


# If this is true, we'll submit your job using an existing Spark installation.
# If this is false, we'll clone and build a specific version of Spark, and
# copy configurations from your existing Spark installation.
USE_CLUSTER_SPARK = True

# URL of the HDFS installation in the Spark EC2 cluster
HDFS_URL = "hdfs://%s:9000/test/" % socket.gethostname()

# Set the following if not using existing Spark installation
# Commit id and repo used if you are not using an existing Spark cluster
# custom version of Spark. The remote name in your git repo is assumed
# to be "origin".
#
# The commit ID can specify any of the following:
#     1. A git commit hash         e.g. "4af93ff3"
#     2. A branch name             e.g. "origin/branch-0.7"
#     3. A tag name                e.g. "origin/tag/v0.8.0-incubating"
#     4. A pull request            e.g. "origin/pr/675"
SPARK_COMMIT_ID = ""
SPARK_GIT_REPO = "https://github.com/apache/spark.git"
SPARK_MERGE_COMMIT_INTO_MASTER = False # Whether to merge the commit into master

# Whether to install and build Spark. Set this to true only for the
# first installation if an existing one does not already exist.
PREP_SPARK = not USE_CLUSTER_SPARK

# Whether to restart the Master and all Workers
# This should always be false for Yarn
RESTART_SPARK_CLUSTER = True
RESTART_SPARK_CLUSTER = RESTART_SPARK_CLUSTER and not IS_YARN_MODE

# Rsync SPARK_HOME to all the slaves or not
RSYNC_SPARK_HOME = True

# Which tests to run
RUN_SPARK_TESTS = False
RUN_PYSPARK_TESTS = False
RUN_STREAMING_TESTS = False
RUN_MLLIB_TESTS = True
RUN_PYTHON_MLLIB_TESTS = False

# Which tests to prepare. Set this to true for the first
# installation or whenever you make a change to the tests.
PREP_SPARK_TESTS = False
PREP_PYSPARK_TESTS = False
PREP_STREAMING_TESTS = False
PREP_MLLIB_TESTS = True

# Whether to warm up local disks (warm-up is only necesary on EC2).
DISK_WARMUP = False

# Total number of bytes used to warm up each local directory.
DISK_WARMUP_BYTES = 200 * 1024 * 1024

# Number of files to create when warming up each local directory.
# Bytes will be evenly divided across files.
DISK_WARMUP_FILES = 200

# Prompt for confirmation when deleting temporary files.
PROMPT_FOR_DELETES = True

# Files to write results to
SPARK_OUTPUT_FILENAME = "results/spark_perf_output_%s_%s" % (
    SPARK_COMMIT_ID.replace("/", "-"), time.strftime("%Y-%m-%d_%H-%M-%S"))
PYSPARK_OUTPUT_FILENAME = "results/python_perf_output_%s_%s" % (
    SPARK_COMMIT_ID.replace("/", "-"), time.strftime("%Y-%m-%d_%H-%M-%S"))
STREAMING_OUTPUT_FILENAME = "results/streaming_perf_output_%s_%s" % (
    SPARK_COMMIT_ID.replace("/", "-"), time.strftime("%Y-%m-%d_%H-%M-%S"))
MLLIB_OUTPUT_FILENAME = "results/mllib_perf_output_%s_%s" % (
    SPARK_COMMIT_ID.replace("/", "-"), time.strftime("%Y-%m-%d_%H-%M-%S"))
PYTHON_MLLIB_OUTPUT_FILENAME = "results/python_mllib_perf_output_%s_%s" % (
    SPARK_COMMIT_ID.replace("/", "-"), time.strftime("%Y-%m-%d_%H-%M-%S"))


# ============================ #
#  Test Configuration Options  #
# ============================ #

# The default values configured below are appropriate for approximately 20 m1.xlarge nodes,
# in which each node has 15 GB of memory. Use this variable to scale the values (e.g.
# number of records in a generated dataset) if you are running the tests with more
# or fewer nodes. When developing new test suites, you might want to set this to a small
# value suitable for a single machine, such as 0.001.
SCALE_FACTOR = 0.05

assert SCALE_FACTOR > 0, "SCALE_FACTOR must be > 0."

# If set, removes the first N trials for each test from all reported statistics. Useful for
# tests which have outlier behavior due to JIT and other system cache warm-ups. If any test
# returns fewer N + 1 results, an exception is thrown.
IGNORED_TRIALS = 2

# Command used to launch Scala or Java.

# Set up OptionSets. Note that giant cross product is done over all JavaOptionsSets + OptionSets
# passed to each test which may be combinations of those set up here.

# Java options.
COMMON_JAVA_OPTS = [
    # Fraction of JVM memory used for caching RDDs.
    JavaOptionSet("spark.storage.memoryFraction", [0.66]),
    JavaOptionSet("spark.serializer", ["org.apache.spark.serializer.JavaSerializer"]),
    # JavaOptionSet("spark.executor.memory", ["9g"]),
    # Turn event logging on in order better diagnose failed tests. Off by default as it crashes
    # releases prior to 1.0.2
    # JavaOptionSet("spark.eventLog.enabled", [True]),
    # To ensure consistency across runs, we disable delay scheduling
    JavaOptionSet("spark.locality.wait", [str(60 * 1000 * 1000)])
]
# Set driver memory here
SPARK_DRIVER_MEMORY = "1g"

# The following options value sets are shared among all tests.
COMMON_OPTS = [
    # How many times to run each experiment - used to warm up system caches.
    # This OptionSet should probably only have a single value (i.e., length 1)
    # since it doesn't make sense to have multiple values here.
    OptionSet("num-trials", [10]),
    # Extra pause added between trials, in seconds. For runs with large amounts
    # of shuffle data, this gives time for buffer cache write-back.
    OptionSet("inter-trial-wait", [3])
]

# The following options value sets are shared among all tests of
# operations on key-value data.
SPARK_KEY_VAL_TEST_OPTS = [
    # The number of input partitions.
    OptionSet("num-partitions", [400], can_scale=True),
    # The number of reduce tasks.
    OptionSet("reduce-tasks", [400], can_scale=True),
    # A random seed to make tests reproducable.
    OptionSet("random-seed", [5]),
    # Input persistence strategy (can be "memory", "disk", or "hdfs").
    # NOTE: If "hdfs" is selected, datasets will be re-used across runs of
    #       this script. This means parameters here are effectively ignored if
    #       an existing input dataset is present.
    OptionSet("persistent-type", ["memory"]),
    # Whether to wait for input in order to exit the JVM.
    FlagSet("wait-for-exit", [False]),
    # Total number of records to create.
    OptionSet("num-records", [200 * 1000 * 1000], True),
    # Number of unique keys to sample from.
    OptionSet("unique-keys",[20 * 1000], True),
    # Length in characters of each key.
    OptionSet("key-length", [10]),
    # Number of unique values to sample from.
    OptionSet("unique-values", [1000 * 1000], True),
    # Length in characters of each value.
    OptionSet("value-length", [10]),
    # Use hashes instead of padded numbers for keys and values
    FlagSet("hash-records", [False]),
    # Storage location if HDFS persistence is used
    OptionSet("storage-location", [
        HDFS_URL + "/spark-perf-kv-data"]),
    OptionSet("skew", [2])
]


# ======================= #
#  Spark Core Test Setup  #
# ======================= #

# Set up the actual tests. Each test is represtented by a tuple:
# (short_name, test_cmd, scale_factor, list<JavaOptionSet>, list<OptionSet>)

SPARK_KV_OPTS = COMMON_OPTS + SPARK_KEY_VAL_TEST_OPTS
SPARK_TESTS = []

SCHEDULING_THROUGHPUT_OPTS = [
    # The number of tasks that should be launched in each job:
    OptionSet("num-tasks", [10 * 1000]),
    # The number of jobs that should be run:
    OptionSet("num-jobs", [1]),
    # The size of the task closure (in bytes):
    OptionSet("closure-size", [0]),
    # A random seed to make tests reproducible:
    OptionSet("random-seed", [5]),
]

SPARK_TESTS += [("scheduling-throughput", "spark.perf.TestRunner",
    SCALE_FACTOR, COMMON_JAVA_OPTS,
    [ConstantOption("scheduling-throughput")] + COMMON_OPTS + SCHEDULING_THROUGHPUT_OPTS)]

# SPARK_TESTS += [("scala-agg-by-key", "spark.perf.TestRunner", SCALE_FACTOR,
#     COMMON_JAVA_OPTS, [ConstantOption("aggregate-by-key")] + SPARK_KV_OPTS)]

# # Scale the input for this test by 2x since ints are smaller.
# SPARK_TESTS += [("scala-agg-by-key-int", "spark.perf.TestRunner", SCALE_FACTOR * 2,
#     COMMON_JAVA_OPTS, [ConstantOption("aggregate-by-key-int")] + SPARK_KV_OPTS)]

# SPARK_TESTS += [("scala-agg-by-key-naive", "spark.perf.TestRunner", SCALE_FACTOR,
#     COMMON_JAVA_OPTS, [ConstantOption("aggregate-by-key-naive")] + SPARK_KV_OPTS)]

# # Scale the input for this test by 0.10.
# SPARK_TESTS += [("scala-sort-by-key", "spark.perf.TestRunner", SCALE_FACTOR * 0.1,
#     COMMON_JAVA_OPTS, [ConstantOption("sort-by-key")] + SPARK_KV_OPTS)]

# SPARK_TESTS += [("scala-sort-by-key-int", "spark.perf.TestRunner", SCALE_FACTOR * 0.2,
#     COMMON_JAVA_OPTS, [ConstantOption("sort-by-key-int")] + SPARK_KV_OPTS)]

# SPARK_TESTS += [("scala-count", "spark.perf.TestRunner", SCALE_FACTOR,
#     COMMON_JAVA_OPTS, [ConstantOption("count")] + SPARK_KV_OPTS)]

# SPARK_TESTS += [("scala-count-w-fltr", "spark.perf.TestRunner", SCALE_FACTOR,
#     COMMON_JAVA_OPTS, [ConstantOption("count-with-filter")] + SPARK_KV_OPTS)]


# ==================== #
#  Pyspark Test Setup  #
# ==================== #

PYSPARK_TESTS = []

BROADCAST_TEST_OPTS = [
    # The size of broadcast
    OptionSet("broadcast-size", [200 << 20], can_scale=True),
]

PYSPARK_TESTS += [("python-scheduling-throughput", "core_tests.py",
    SCALE_FACTOR, COMMON_JAVA_OPTS,
    [ConstantOption("SchedulerThroughputTest"), OptionSet("num-tasks", [5000])] + COMMON_OPTS)]

PYSPARK_TESTS += [("python-agg-by-key", "core_tests.py", SCALE_FACTOR,
    COMMON_JAVA_OPTS, [ConstantOption("AggregateByKey")] + SPARK_KV_OPTS)]

# Scale the input for this test by 2x since ints are smaller.
PYSPARK_TESTS += [("python-agg-by-key-int", "core_tests.py", SCALE_FACTOR * 2,
    COMMON_JAVA_OPTS, [ConstantOption("AggregateByKeyInt")] + SPARK_KV_OPTS)]

PYSPARK_TESTS += [("python-agg-by-key-naive", "core_tests.py", SCALE_FACTOR,
    COMMON_JAVA_OPTS, [ConstantOption("AggregateByKeyNaive")] + SPARK_KV_OPTS)]

# Scale the input for this test by 0.10.
PYSPARK_TESTS += [("python-sort-by-key", "core_tests.py", SCALE_FACTOR * 0.1,
    COMMON_JAVA_OPTS, [ConstantOption("SortByKey")] + SPARK_KV_OPTS)]

PYSPARK_TESTS += [("python-sort-by-key-int", "core_tests.py", SCALE_FACTOR * 0.2,
    COMMON_JAVA_OPTS, [ConstantOption("SortByKeyInt")] + SPARK_KV_OPTS)]

PYSPARK_TESTS += [("python-count", "core_tests.py", SCALE_FACTOR,
                 COMMON_JAVA_OPTS, [ConstantOption("Count")] + SPARK_KV_OPTS)]

PYSPARK_TESTS += [("python-count-w-fltr", "core_tests.py", SCALE_FACTOR,
    COMMON_JAVA_OPTS, [ConstantOption("CountWithFilter")] + SPARK_KV_OPTS)]

PYSPARK_TESTS += [("python-broadcast-w-bytes", "core_tests.py", SCALE_FACTOR,
    COMMON_JAVA_OPTS, [ConstantOption("BroadcastWithBytes")] + SPARK_KV_OPTS + BROADCAST_TEST_OPTS)]

PYSPARK_TESTS += [("python-broadcast-w-set", "core_tests.py", SCALE_FACTOR,
    COMMON_JAVA_OPTS, [ConstantOption("BroadcastWithSet")] + SPARK_KV_OPTS + BROADCAST_TEST_OPTS)]


# ============================ #
#  Spark Streaming Test Setup  #
# ============================ #

STREAMING_TESTS = []

# The following function generates options for setting batch duration in streaming tests
def streaming_batch_duration_opts(duration):
    return [OptionSet("batch-duration", [duration])]

# The following function generates options for setting window duration in streaming tests
def streaming_window_duration_opts(duration):
    return [OptionSet("window-duration", [duration])]

STREAMING_COMMON_OPTS = [
    OptionSet("total-duration", [60]),
    OptionSet("hdfs-url", [HDFS_URL]),
]

STREAMING_COMMON_JAVA_OPTS = [
    # Fraction of JVM memory used for caching RDDs.
    JavaOptionSet("spark.storage.memoryFraction", [0.66]),
    JavaOptionSet("spark.serializer", ["org.apache.spark.serializer.JavaSerializer"]),
    # JavaOptionSet("spark.executor.memory", ["9g"]),
    JavaOptionSet("spark.executor.extraJavaOptions", [" -XX:+UseConcMarkSweepGC "])
]

STREAMING_KEY_VAL_TEST_OPTS = STREAMING_COMMON_OPTS + streaming_batch_duration_opts(2000) + [
    # Number of input streams.
    OptionSet("num-streams", [1], can_scale=True),
    # Number of records per second per input stream
    OptionSet("records-per-sec", [10 * 1000]),
    # Number of reduce tasks.
    OptionSet("reduce-tasks", [10], can_scale=True),
    # memory serialization ("true" or "false").
    OptionSet("memory-serialization", ["true"]),
    # Number of unique keys to sample from.
    OptionSet("unique-keys",[100 * 1000], can_scale=True),
    # Length in characters of each key.
    OptionSet("unique-values", [1000 * 1000], can_scale=True),
    # Send data through receiver
    OptionSet("use-receiver", ["true"]),
]

STREAMING_HDFS_RECOVERY_TEST_OPTS = STREAMING_COMMON_OPTS + streaming_batch_duration_opts(5000) + [
    OptionSet("records-per-file", [10000]),
    OptionSet("file-cleaner-delay", [300])
]

# This test is just to see if everything is setup properly
STREAMING_TESTS += [("basic", "streaming.perf.TestRunner", SCALE_FACTOR,
    STREAMING_COMMON_JAVA_OPTS, [ConstantOption("basic")] + STREAMING_COMMON_OPTS + streaming_batch_duration_opts(1000))]

STREAMING_TESTS += [("state-by-key", "streaming.perf.TestRunner", SCALE_FACTOR,
    STREAMING_COMMON_JAVA_OPTS, [ConstantOption("state-by-key")] + STREAMING_KEY_VAL_TEST_OPTS)]

STREAMING_TESTS += [("group-by-key-and-window", "streaming.perf.TestRunner", SCALE_FACTOR,
    STREAMING_COMMON_JAVA_OPTS, [ConstantOption("group-by-key-and-window")] + STREAMING_KEY_VAL_TEST_OPTS + streaming_window_duration_opts(10000) )]

STREAMING_TESTS += [("reduce-by-key-and-window", "streaming.perf.TestRunner", SCALE_FACTOR,
    STREAMING_COMMON_JAVA_OPTS, [ConstantOption("reduce-by-key-and-window")] + STREAMING_KEY_VAL_TEST_OPTS + streaming_window_duration_opts(10000) )]

STREAMING_TESTS += [("hdfs-recovery", "streaming.perf.TestRunner", SCALE_FACTOR,
    STREAMING_COMMON_JAVA_OPTS, [ConstantOption("hdfs-recovery")] + STREAMING_HDFS_RECOVERY_TEST_OPTS)]


# ================== #
#  MLlib Test Setup  #
# ================== #

MLLIB_TESTS = []
MLLIB_PERF_TEST_RUNNER = "mllib.perf.TestRunner"

# Set this to 1.0, 1.1, 1.2, ... (the major version) to test MLlib with a particular Spark version.
# Note: You should also build mllib-perf using -Dspark.version to specify the same version.
# Note: To run perf tests against a snapshot version of Spark which has not yet been packaged into a release:
#  * Build Spark locally by running `build/sbt assembly; build/sbt publishLocal` in the Spark root directory
#  * Set `USE_CLUSTER_SPARK = True` and `MLLIB_SPARK_VERSION = {desired Spark version, e.g. 1.5}`
#  * Don't use PREP_MLLIB_TESTS = True; instead manually run `cd mllib-tests; sbt/sbt -Dspark.version=1.5.0-SNAPSHOT clean assembly` to build perf tests

MLLIB_SPARK_VERSION = 2.0

MLLIB_JAVA_OPTS = COMMON_JAVA_OPTS
if MLLIB_SPARK_VERSION >= 1.1:
    MLLIB_JAVA_OPTS = MLLIB_JAVA_OPTS + [
        # Shuffle manager: SORT, HASH
        JavaOptionSet("spark.shuffle.manager", ["SORT"])
    ]

# The following options value sets are shared among all tests of
# operations on MLlib algorithms.
MLLIB_COMMON_OPTS = COMMON_OPTS + [
    # The number of input partitions.
    # The default setting is suitable for a 16-node m3.2xlarge EC2 cluster.
    OptionSet("num-partitions", [128], can_scale=True),
    # A random seed to make tests reproducable.
    OptionSet("random-seed", [5])
]

# Algorithms available in Spark-1.0 #

# Regression and Classification Tests #
MLLIB_REGRESSION_CLASSIFICATION_TEST_OPTS = MLLIB_COMMON_OPTS + [
    # The number of rows or examples
    OptionSet("num-examples", [100000], can_scale=True)
]

# Generalized Linear Model (GLM) Tests #

MLLIB_GLM_TEST_OPTS = MLLIB_REGRESSION_CLASSIFICATION_TEST_OPTS + [
    # The number of features per example
    OptionSet("num-features", [10000], can_scale=False),
    # The number of iterations for SGD
    OptionSet("num-iterations", [20]),
    # The step size for SGD
    OptionSet("step-size", [0.001]),
    # Regularization type: none, l1, l2
    OptionSet("reg-type", ["l2"]),
    # Regularization parameter
    OptionSet("reg-param", [0.1])
]

if MLLIB_SPARK_VERSION >= 1.5:
    MLLIB_GLM_TEST_OPTS += [
        # Ignored, but required for config
        OptionSet("elastic-net-param", [0.0])
    ]

if MLLIB_SPARK_VERSION < 2.0:
    MLLIB_GLM_TEST_OPTS += [
        # The scale factor for the noise in feature values.
        # Currently ignored for regression.
        # Only available in Spark 1.x
        OptionSet("feature-noise", [1.0])
    ]


# GLM Regression Tests #
MLLIB_GLM_REGRESSION_TEST_OPTS = MLLIB_GLM_TEST_OPTS + [
    # Optimization algorithm: sgd
    OptionSet("optimizer", ["sgd"]),
    # The intercept for the data
    OptionSet("intercept", [0.0]),
    # The scale factor for label noise
    OptionSet("label-noise", [0.1]),
    # Loss to minimize: l2 (squared error)
    OptionSet("loss", ["l2"])
]

MLLIB_TESTS += [("glm-regression", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
    MLLIB_JAVA_OPTS, [ConstantOption("glm-regression")] + MLLIB_GLM_REGRESSION_TEST_OPTS)]

# Classification Tests #
MLLIB_CLASSIFICATION_TEST_OPTS = MLLIB_GLM_TEST_OPTS + [
    # Expected fraction of examples which are negative
    OptionSet("per-negative", [0.3]),
    # Optimization algorithm: sgd, l-bfgs
    OptionSet("optimizer", ["sgd", "l-bfgs"])
]

# GLM Classification Tests #
MLLIB_GLM_CLASSIFICATION_TEST_OPTS = MLLIB_CLASSIFICATION_TEST_OPTS + [
    # Loss to minimize: logistic, hinge (SVM)
    OptionSet("loss", ["logistic"])
]

MLLIB_TESTS += [("glm-classification", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
                 MLLIB_JAVA_OPTS, [ConstantOption("glm-classification")] +
                 MLLIB_GLM_CLASSIFICATION_TEST_OPTS)]

if MLLIB_SPARK_VERSION >= 1.5:
    MLLIB_GLM_ELASTIC_NET_TEST_OPTS = MLLIB_REGRESSION_CLASSIFICATION_TEST_OPTS + [
        # The max number of iterations for LBFGS/OWLQN
        OptionSet("num-iterations", [20]),
        # LBFGS/OWLQN is used with elastic-net regularization.
        OptionSet("optimizer", ["auto"]),
        # Using elastic-net regularization.
        OptionSet("reg-type", ["elastic-net"]),
        # Runs with L2 (param = 0.0), L1 (param = 1.0).
        OptionSet("elastic-net-param", [0.0, 1.0]),
        # Regularization param (lambda)
        OptionSet("reg-param", [0.01]),
        # The scale factor for the noise in feature values
        OptionSet("feature-noise", [1.0]),
        # The step size is not used in LBFGS, but this is required in parameter checking.
        OptionSet("step-size", [0.0])
    ]

    MLLIB_GLM_ELASTIC_NET_REGRESSION_TEST_OPTS = MLLIB_GLM_ELASTIC_NET_TEST_OPTS + [
        # The scale factor for the noise in label values
        OptionSet("label-noise", [0.1]),
        # The intercept for the data
        OptionSet("intercept", [0.2]),
        # Loss to minimize: l2 (squared error)
        OptionSet("loss", ["l2"])
    ]

    # Test L-BFGS
    MLLIB_TESTS += [("glm-regression", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
        MLLIB_JAVA_OPTS, [ConstantOption("glm-regression")] +
        MLLIB_GLM_ELASTIC_NET_REGRESSION_TEST_OPTS +
        [OptionSet("num-features", [10000], can_scale=False)])]
    # Test normal equation solver
    MLLIB_TESTS += [("glm-regression", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
                     MLLIB_JAVA_OPTS, [ConstantOption("glm-regression")] +
                     MLLIB_GLM_ELASTIC_NET_REGRESSION_TEST_OPTS +
                     [OptionSet("num-features", [200], can_scale=False)])]

    MLLIB_GLM_ELASTIC_NET_CLASSIFICATION_TEST_OPTS = MLLIB_GLM_ELASTIC_NET_TEST_OPTS + [
        # Expected fraction of examples which are negative
        OptionSet("per-negative", [0.3]),
        # In GLM classification with elastic-net regularization, only logistic loss is supported.
        OptionSet("loss", ["logistic"])
    ]

    # Test L-BFGS
    MLLIB_TESTS += [("glm-classification", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
                     MLLIB_JAVA_OPTS, [ConstantOption("glm-classification")] +
                     MLLIB_GLM_ELASTIC_NET_CLASSIFICATION_TEST_OPTS +
                     [OptionSet("num-features", [10000], can_scale=False)])]
    # Test normal equation solver
    MLLIB_TESTS += [("glm-classification", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
                     MLLIB_JAVA_OPTS, [ConstantOption("glm-classification")] +
                     MLLIB_GLM_ELASTIC_NET_CLASSIFICATION_TEST_OPTS +
                     [OptionSet("num-features", [200], can_scale=False)])]

NAIVE_BAYES_TEST_OPTS = MLLIB_REGRESSION_CLASSIFICATION_TEST_OPTS + [
    # The number of features per example
    OptionSet("num-features", [10000], can_scale=False),
    # Expected fraction of examples which are negative
    OptionSet("per-negative", [0.3]),
    # The scale factor for the noise in feature values
    #OptionSet("feature-noise", [1.0]),
    # Naive Bayes smoothing lambda.
    OptionSet("nb-lambda", [1.0]),
    # Model type: either multinomial or bernoulli (bernoulli only available in Spark 1.4+)
    OptionSet("model-type", ["multinomial"]),
]

MLLIB_TESTS += [("naive-bayes", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
    MLLIB_JAVA_OPTS, [ConstantOption("naive-bayes")] +
    NAIVE_BAYES_TEST_OPTS)]

# Decision Trees #
MLLIB_DECISION_TREE_TEST_OPTS = MLLIB_COMMON_OPTS + [
    # The number of rows or examples
    OptionSet("num-examples", [100000], can_scale=True),
    # The number of features per example
    OptionSet("num-features", [500], can_scale=False),
    # Type of label: 0 indicates regression, 2+ indicates classification with this many classes
    # Note: multi-class (>2) is not supported in Spark 1.0.
    OptionSet("label-type", [0, 2], can_scale=False),
    # Fraction of features which are categorical
    OptionSet("frac-categorical-features", [0.5], can_scale=False),
    # Fraction of categorical features which are binary. Others have 20 categories.
    OptionSet("frac-binary-features", [0.5], can_scale=False),
    # Depth of true decision tree model used to label examples.
    # WARNING: The meaning of depth changed from Spark 1.0 to Spark 1.1:
    #          depth=N for Spark 1.0 should be depth=N-1 for Spark 1.1
    OptionSet("tree-depth", [5, 10], can_scale=False),
    # Maximum number of bins for the decision tree learning algorithm.
    OptionSet("max-bins", [32], can_scale=False),
]

if MLLIB_SPARK_VERSION >= 1.2:
    ensembleTypes = ["RandomForest"]
    if MLLIB_SPARK_VERSION >= 1.3:
        ensembleTypes.append("GradientBoostedTrees")
    if MLLIB_SPARK_VERSION >= 1.4:
        ensembleTypes.extend(["ml.RandomForest", "ml.GradientBoostedTrees"])
    MLLIB_DECISION_TREE_TEST_OPTS += [
        # Ensemble type: mllib.RandomForest, mllib.GradientBoostedTrees,
        #                ml.RandomForest, ml.GradientBoostedTrees
        OptionSet("ensemble-type", ensembleTypes),
        # Path to training dataset (if not given, use random data).
        OptionSet("training-data", [""]),
        # Path to test dataset (only used if training dataset given).
        # If not given, hold out part of training data for validation.
        OptionSet("test-data", [""]),
        # Fraction of data to hold out for testing
        #  (Ignored if given training and test dataset, or if using synthetic data.)
        OptionSet("test-data-fraction", [0.2], can_scale=False),
        # Number of trees. If 1, then run DecisionTree. If >1, then run RandomForest.
        OptionSet("num-trees", [1, 10], can_scale=False),
        # Feature subset sampling strategy: auto, all, sqrt, log2, onethird
        # (only used for RandomForest)
        OptionSet("feature-subset-strategy", ["auto"])
    ]

MLLIB_TESTS += [("decision-tree", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
    MLLIB_JAVA_OPTS, [ConstantOption("decision-tree")] +
    MLLIB_DECISION_TREE_TEST_OPTS)]

# Recommendation Tests #
MLLIB_RECOMMENDATION_TEST_OPTS = MLLIB_COMMON_OPTS + [
     # The number of users
     OptionSet("num-users", [600000], can_scale=True),
     # The number of products
     OptionSet("num-products", [500000], can_scale=False),
     # The number of ratings
     OptionSet("num-ratings", [10000], can_scale=True),
     # The number of iterations for ALS
     OptionSet("num-iterations", [10]),
     # The rank of the factorized matrix model
     OptionSet("rank", [10]),
     # The regularization parameter
     OptionSet("reg-param", [0.1]),
     # Whether to use implicit preferences or not
     FlagSet("implicit-prefs", [False])
]

MLLIB_TESTS += [("als", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
    MLLIB_JAVA_OPTS, [ConstantOption("als")] +
    MLLIB_RECOMMENDATION_TEST_OPTS)]

# Clustering Tests #
MLLIB_CLUSTERING_TEST_OPTS = MLLIB_COMMON_OPTS + [
     # The number of examples
     OptionSet("num-examples", [100000], can_scale=True),
     # The number of features per point
     OptionSet("num-features", [10000], can_scale=False),
     # The number of centers
     OptionSet("num-centers", [20]),
     # The number of iterations for KMeans
     OptionSet("num-iterations", [20])
]

MLLIB_TESTS += [("kmeans", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
    MLLIB_JAVA_OPTS, [ConstantOption("kmeans")] + MLLIB_CLUSTERING_TEST_OPTS)]

MLLIB_GMM_TEST_OPTS = MLLIB_COMMON_OPTS + [
    OptionSet("num-examples", [100000], can_scale=True),
    OptionSet("num-features", [100], can_scale=False),
    OptionSet("num-centers", [20], can_scale=False),
    OptionSet("num-iterations", [20])]

if MLLIB_SPARK_VERSION >= 1.3:
    MLLIB_TESTS += [("gmm", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
        MLLIB_JAVA_OPTS, [ConstantOption("gmm")] + MLLIB_GMM_TEST_OPTS)]

MLLIB_LDA_TEST_OPTS = MLLIB_COMMON_OPTS + [
    OptionSet("num-documents", [50000], can_scale=True),
    OptionSet("num-vocab", [10000], can_scale=False),
    OptionSet("num-topics", [20], can_scale=False),
    OptionSet("num-iterations", [20]),
    OptionSet("document-length", [100]),
    OptionSet("optimizer", ["em", "online"])]

if MLLIB_SPARK_VERSION >= 1.4:
    MLLIB_TESTS += [("lda", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
        MLLIB_JAVA_OPTS, [ConstantOption("lda")] + MLLIB_LDA_TEST_OPTS)]

MLLIB_PIC_TEST_OPTS = MLLIB_COMMON_OPTS + [
    OptionSet("num-examples", [100000], can_scale=True),
    OptionSet("node-degree", [20], can_scale=False),
    OptionSet("num-centers", [40], can_scale=False),
    OptionSet("num-iterations", [20])]

if MLLIB_SPARK_VERSION >= 1.3:
    MLLIB_TESTS += [("pic", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
        MLLIB_JAVA_OPTS, [ConstantOption("pic")] + MLLIB_PIC_TEST_OPTS)]

# Linear Algebra Tests #
MLLIB_LINALG_TEST_OPTS = MLLIB_COMMON_OPTS + [
    # The number of rows for the matrix
    OptionSet("num-rows", [1000000], can_scale=True),
    # The number of columns for the matrix
    OptionSet("num-cols", [1000], can_scale=False),
    # The number of top singular values wanted for SVD and PCA
    OptionSet("rank", [50], can_scale=False)
]
# Linear Algebra Tests which take more time (slightly smaller settings) #
MLLIB_BIG_LINALG_TEST_OPTS = MLLIB_COMMON_OPTS + [
    # The number of rows for the matrix
    OptionSet("num-rows", [1000000], can_scale=True),
    # The number of columns for the matrix
    OptionSet("num-cols", [500], can_scale=False),
    # The number of top singular values wanted for SVD and PCA
    OptionSet("rank", [10], can_scale=False)
]

MLLIB_TESTS += [("svd", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
    MLLIB_JAVA_OPTS, [ConstantOption("svd")] + MLLIB_BIG_LINALG_TEST_OPTS)]

MLLIB_TESTS += [("pca", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
    MLLIB_JAVA_OPTS, [ConstantOption("pca")] + MLLIB_LINALG_TEST_OPTS)]

MLLIB_TESTS += [("summary-statistics", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
    MLLIB_JAVA_OPTS, [ConstantOption("summary-statistics")] +
    MLLIB_BIG_LINALG_TEST_OPTS)]

MLLIB_BLOCK_MATRIX_MULT_TEST_OPTS = MLLIB_COMMON_OPTS + [
    OptionSet("m", [20000], can_scale=True),
    OptionSet("k", [10000], can_scale=False),
    OptionSet("n", [10000], can_scale=False),
    OptionSet("block-size", [1024], can_scale=False)]

if MLLIB_SPARK_VERSION >= 1.3:
   MLLIB_TESTS += [("block-matrix-mult", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
                   MLLIB_JAVA_OPTS, [ConstantOption("block-matrix-mult")] + MLLIB_BLOCK_MATRIX_MULT_TEST_OPTS)]

# Statistic Toolkit Tests #
MLLIB_STATS_TEST_OPTS = MLLIB_COMMON_OPTS

MLLIB_PEARSON_TEST_OPTS = MLLIB_STATS_TEST_OPTS + \
                          [OptionSet("num-rows", [1000000], can_scale=True),
                           OptionSet("num-cols", [1000], can_scale=False)]

MLLIB_SPEARMAN_TEST_OPTS = MLLIB_STATS_TEST_OPTS + \
                           [OptionSet("num-rows", [1000000], can_scale=True),
                            OptionSet("num-cols", [100], can_scale=False)]

MLLIB_CHI_SQ_FEATURE_TEST_OPTS = MLLIB_STATS_TEST_OPTS + \
                                 [OptionSet("num-rows", [2000000], can_scale=True),
                                  OptionSet("num-cols", [500], can_scale=False)]

MLLIB_CHI_SQ_GOF_TEST_OPTS = MLLIB_STATS_TEST_OPTS + \
                             [OptionSet("num-rows", [50000000], can_scale=True),
                              OptionSet("num-cols", [0], can_scale=False)]

MLLIB_CHI_SQ_MAT_TEST_OPTS = MLLIB_STATS_TEST_OPTS + \
                             [OptionSet("num-rows", [20000], can_scale=True),
                              OptionSet("num-cols", [0], can_scale=False)]

if MLLIB_SPARK_VERSION >= 1.1:
    MLLIB_TESTS += [("pearson", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
        MLLIB_JAVA_OPTS, [ConstantOption("pearson")] + MLLIB_PEARSON_TEST_OPTS)]

    MLLIB_TESTS += [("spearman", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
        MLLIB_JAVA_OPTS, [ConstantOption("spearman")] + MLLIB_SPEARMAN_TEST_OPTS)]

    MLLIB_TESTS += [("chi-sq-feature", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
        MLLIB_JAVA_OPTS, [ConstantOption("chi-sq-feature")] + MLLIB_CHI_SQ_FEATURE_TEST_OPTS)]

    MLLIB_TESTS += [("chi-sq-gof", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
        MLLIB_JAVA_OPTS, [ConstantOption("chi-sq-gof")] + MLLIB_CHI_SQ_GOF_TEST_OPTS)]

    MLLIB_TESTS += [("chi-sq-mat", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
        MLLIB_JAVA_OPTS, [ConstantOption("chi-sq-mat")] + MLLIB_CHI_SQ_MAT_TEST_OPTS)]

# Feature Transformation Tests #

MLLIB_FEATURE_TEST_OPTS = MLLIB_COMMON_OPTS

MLLIB_WORD2VEC_TEST_OPTS = MLLIB_FEATURE_TEST_OPTS + \
                           [OptionSet("num-sentences", [1000000], can_scale=True),
                            OptionSet("num-words", [10000], can_scale=False),
                            OptionSet("vector-size", [100], can_scale=False),
                            OptionSet("num-iterations", [3], can_scale=False),
                            OptionSet("min-count", [5], can_scale=False)]

if MLLIB_SPARK_VERSION >= 1.3:  # TODO: make it work in 1.2
    MLLIB_TESTS += [("word2vec", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
        MLLIB_JAVA_OPTS, [ConstantOption("word2vec")] + MLLIB_WORD2VEC_TEST_OPTS)]

# Frequent Pattern Matching Tests #

MLLIB_FPM_TEST_OPTS = MLLIB_COMMON_OPTS

MLLIB_FP_GROWTH_TEST_OPTS = MLLIB_FPM_TEST_OPTS + \
                            [OptionSet("num-baskets", [5000000], can_scale=True),
                             OptionSet("avg-basket-size", [10], can_scale=False),
                             OptionSet("num-items", [1000], can_scale=False),
                             OptionSet("min-support", [0.01], can_scale=False)]

if MLLIB_SPARK_VERSION >= 1.3:
    MLLIB_TESTS += [("fp-growth", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
        MLLIB_JAVA_OPTS, [ConstantOption("fp-growth")] + MLLIB_FP_GROWTH_TEST_OPTS)]

# TODO: tune test size to have runtime within 30-60 seconds
MLLIB_PREFIX_SPAN_TEST_OPTS = MLLIB_FPM_TEST_OPTS + \
                            [OptionSet("num-sequences", [5000000], can_scale=True),
                             OptionSet("avg-sequence-size", [5], can_scale=False),
                             OptionSet("avg-itemset-size", [2], can_scale=False),
                             OptionSet("num-items", [500], can_scale=False),
                             OptionSet("min-support", [0.5], can_scale=False),
                             OptionSet("max-pattern-len", [10], can_scale=False),
                             OptionSet("max-local-proj-db-size", [32000000], can_scale=False)]

if MLLIB_SPARK_VERSION >= 1.5:
    MLLIB_TESTS += [("prefix-span", MLLIB_PERF_TEST_RUNNER, SCALE_FACTOR,
        MLLIB_JAVA_OPTS, [ConstantOption("prefix-span")] + MLLIB_PREFIX_SPAN_TEST_OPTS)]

# Python MLlib tests
PYTHON_MLLIB_TESTS = []

PYTHON_MLLIB_TESTS += [("python-glm-classification", "mllib_tests.py", SCALE_FACTOR,
                         MLLIB_JAVA_OPTS, [ConstantOption("GLMClassificationTest")] +
                         MLLIB_GLM_CLASSIFICATION_TEST_OPTS)]

PYTHON_MLLIB_TESTS += [("python-glm-regression", "mllib_tests.py", SCALE_FACTOR,
                         MLLIB_JAVA_OPTS, [ConstantOption("GLMRegressionTest")] +
                         MLLIB_GLM_REGRESSION_TEST_OPTS)]

PYTHON_MLLIB_TESTS += [("python-naive-bayes", "mllib_tests.py", SCALE_FACTOR,
                         MLLIB_JAVA_OPTS, [ConstantOption("NaiveBayesTest")] +
                         NAIVE_BAYES_TEST_OPTS)]

PYTHON_MLLIB_TESTS += [("python-als", "mllib_tests.py", SCALE_FACTOR,
                         MLLIB_JAVA_OPTS, [ConstantOption("ALSTest")] +
                         MLLIB_RECOMMENDATION_TEST_OPTS)]

PYTHON_MLLIB_TESTS += [("python-kmeans", "mllib_tests.py", SCALE_FACTOR,
                         MLLIB_JAVA_OPTS, [ConstantOption("KMeansTest")] + MLLIB_CLUSTERING_TEST_OPTS)]

if MLLIB_SPARK_VERSION >= 1.1:
    PYTHON_MLLIB_TESTS += [("python-pearson", "mllib_tests.py", SCALE_FACTOR,
                             MLLIB_JAVA_OPTS, [ConstantOption("PearsonCorrelationTest")] +
                             MLLIB_PEARSON_TEST_OPTS)]

    PYTHON_MLLIB_TESTS += [("python-spearman", "mllib_tests.py", SCALE_FACTOR,
                             MLLIB_JAVA_OPTS, [ConstantOption("SpearmanCorrelationTest")] +
                             MLLIB_SPEARMAN_TEST_OPTS)]

