#!/usr/bin/env python3

import sys
import copy

from dt import *

from optparse import Option, OptionParser, IndentedHelpFormatter, OptionValueError

def _check_generic_type(opt_type, option, opt, value):
    try:
        ovalue = opt_type(value)
        return opt_type(value)
    except ValueError:
        raise OptionValueError("option {0}: invalid {1} value: {2!r}".format(opt, opt_type.__name__, value))


class DtOptionParser (OptionParser):
    def error(self, msg):
        raise LiteBS_Error(msg)

class DtOption(Option):
    TYPES = Option.TYPES + ("Time", "Duration",)
    TYPE_CHECKER = copy.copy(Option.TYPE_CHECKER)
    TYPE_CHECKER["Time"] = lambda option, opt, value: _check_generic_type(Time, option, opt, value)
    TYPE_CHECKER["Duration"] = lambda option, opt, value: _check_generic_type(Duration, option, opt, value)
