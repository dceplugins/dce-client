import sys

from .version import version

DEFAULT_DCE_VERSION = '2.7.14'
MINIMUM_DCE_VERSION = '2.6.0'
DEFAULT_TIMEOUT_SECONDS = 60
STREAM_HEADER_SIZE_BYTES = 8

IS_WINDOWS_PLATFORM = (sys.platform == 'win32')

DEFAULT_USER_AGENT = "dce-sdk-python/{0}".format(version)

DOCKER_MODE = 'docker'
KUBE_MODE = 'kubernetes'
DCE_MODES = {DOCKER_MODE, KUBE_MODE}
