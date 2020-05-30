# all
LOG_MODE_VERBOSE = 0
# brief
LOG_MODE_INFO = 1

LOG_MODE_ERROR = 2

LOG_MODE_NONE = 3

log_mode = 1


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def mode(mode: int):
    if mode in [LOG_MODE_VERBOSE, LOG_MODE_INFO, LOG_MODE_NONE]:
        global log_mode
        log_mode = mode


def v(tag, *args):
    if log_mode <= LOG_MODE_VERBOSE:
        print(bcolors.OKBLUE, tag, ":", *args, bcolors.ENDC)


def i(tag, *args):
    if log_mode <= LOG_MODE_INFO:
        print(bcolors.OKGREEN, tag, ":", *args, bcolors.ENDC)


def e(tag, *args):
    if log_mode <= LOG_MODE_ERROR:
        print(bcolors.FAIL, tag, ":", *args, bcolors.ENDC)
