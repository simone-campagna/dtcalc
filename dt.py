#!/usr/bin/env python3

import sys
import ast
import time
import copy

class DTType(type):
    def __new__(cls, class_name, class_bases, class_dict):
        t = type.__new__(cls, class_name, class_bases, class_dict)
        t.P_INF = t(t.P_INF_VALUE)
        t.M_INF = t(t.M_INF_VALUE)
        return t

class DT(int, metaclass=DTType):
    P_INF_VALUE = 2 ** 64
    M_INF_VALUE = -2 ** 64

    @classmethod
    def fromstring(cls, value):
        return cls(cls._string2int(value))

    @classmethod
    def _string2int(cls, value):
        raise NotImplemented()

    def __repr__(self):
       return "{0}({1})".format(self.__class__.__name__, str(self))

class Time(DT):
    P_INF_LABEL = '+TInf'
    M_INF_LABEL = '-TInf'
    DEFAULT_TIME_FORMAT = "%Y%m%d %H:%M:%S"
    TIME_FORMAT = DEFAULT_TIME_FORMAT
    ALTERNATE_TIME_FORMATS = (
        DEFAULT_TIME_FORMAT, 
	'%Y%m%d',
    )
    TIME_CONVERTER = time.localtime
    def __new__(cls, init=None):
        if init is None:
            init = time.time()
        elif isinstance(init, str):
            init = cls._string2int(init)
        return DT.__new__(cls, init)

    @classmethod
    def set_time_format(cls, time_format):
        cls.TIME_FORMAT = time_format

    @classmethod
    def _string2int(cls, value):
        if value == cls.P_INF_LABEL:
            value = cls.P_INF
        elif value == cls.M_INF_LABEL:
            value = cls.M_INF
        else:
            if cls.TIME_FORMAT != cls.DEFAULT_TIME_FORMAT:
                time_formats = (cls.TIME_FORMAT, ) + cls.ALTERNATE_TIME_FORMATS
            else:
                time_formats = cls.ALTERNATE_TIME_FORMATS
            for time_format in time_formats:
                try:
                    value = time.mktime(time.strptime(value, time_format))
                    break
                except ValueError:
                    pass
            else:
                raise ValueError("cannot convert string {0} to a Time object".format(value))
        return value

    def __str__(self):
        if self == 0:
            return ''
        elif self == self.P_INF:
            return repr(self.P_INF_LABEL)
        elif self == self.M_INF:
            return repr(self.M_INF_LABEL)
        else:
            return repr(time.strftime(self.TIME_FORMAT, self.TIME_CONVERTER(self)))

    def __add__(self, other):
       if self == self.P_INF:
           if other == Duration.M_INF:
               raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
           else:
               return self
       elif self == self.M_INF:
           if other == Duration.P_INF:
               raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
           else:
               return self
       if isinstance(other, Time):
           raise TypeError("invalid operands: {0} + {1}".format(self.__class__.__name__, other.__class__.__name__))
       elif isinstance(other, Duration):
           if other == Duration.P_INF:
               return self.__class__.P_INF
           elif other == Duration.M_INF:
               return self.__class__.M_INF
           else:
               return self.__class__(int(self) + other)
       elif isinstance(other, int):
           return self.__class__(int(self) + other)
       else:
           raise TypeError("invalid operands: {0} + {1}".format(self.__class__.__name__, other.__class__.__name__))

    def __sub__(self, other):
       if isinstance(other, Time):
           if self == self.P_INF:
               if other == Time.P_INF:
                   raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
               else:
                   return Duration.P_INF
           if self == self.M_INF:
               if other == Time.M_INF:
                   raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
               else:
                   return Duration.M_INF
           else:
               return Duration(int(self) - int(other))
       else:
           if not isinstance(other, Duration):
               other = Duration(other)
           if self == self.P_INF:
               if other == Duration.M_INF:
                   raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
               else:
                   return self
           elif self == self.M_INF:
               if other == Duration.P_INF:
                   raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
               else:
                   return self
           else:
               return Time(int(self) - int(other))

class Duration(DT):
    P_INF_LABEL = '+DInf'
    M_INF_LABEL = '-DInf'
    def __new__(cls, init=None):
        if init is None:
            init = -1
        elif isinstance(init, str):
            init = int(cls._string2int(init))
        return DT.__new__(cls, init)

    @classmethod
    def _string2int(cls, value):
        if value == cls.P_INF_LABEL:
            value = cls.P_INF
        elif value == cls.M_INF_LABEL:
            value = cls.M_INF
        else:
            l = value.split('+', 1)
            if len(l) == 2:
                n_days = int(l[0].strip())
                s_rest = l[1].strip()
            else:
                n_days = 0
                s_rest = l[0].strip()
            l = s_rest.split(':', 2)
            if len(l) == 3:
                n_hours = int(l[0].strip())
                n_minutes = int(l[1].strip())
                n_seconds = int(l[2].strip())
            elif len(l) == 2:
                n_hours = 0
                n_minutes = int(l[0].strip())
                n_seconds = int(l[1].strip())
            #elif len(l) == 1:
            #    n_hours = 0
            #    n_minutes = 0
            #    n_seconds = int(l[0].strip())
            else:
                raise ValueError("invalid init {0!r} for {1}".format(value, cls.__name__))
            value = n_seconds + 60 * (n_minutes + 60 * (n_hours + 24 * n_days))
        return value

    @classmethod
    def fromstring(cls, value):
        return cls(cls._string2int(value))

    def __str__(self):
        if self == 0:
            return '0'
        elif self == self.P_INF_VALUE:
            return repr(self.P_INF_LABEL)
        elif self == self.M_INF_VALUE:
            return repr(self.M_INF_LABEL)
        else:
            i_self = int(self)
            n_microseconds = (int(self) - i_self) * 1000000
            n_days, i_rest = divmod(i_self, 86400)
            n_hours, i_rest = divmod(i_rest, 3600)
            n_minutes, n_seconds = divmod(i_rest, 60)
            if n_microseconds:
                ms = '.{0:6d}'.format(n_microseconds)
            else:
                ms = ''
            if n_days or n_hours:
                l_hms = [n_hours, n_minutes, n_seconds]
            else:
                l_hms = [n_minutes, n_seconds]
            hms = ':'.join('{0:02d}'.format(n) for n in l_hms)
            if n_days:
                fmt = "{0}+{1}{2}"
            else:
                fmt = "{1}{2}"
            return repr(fmt.format(n_days, hms, ms))

    def __add__(self, other):
       klass = self.__class__
       if isinstance(other, Time):
           return other.__add__(self)
       if not isinstance(other, klass):
           other = klass(other)
       if self == klass.P_INF:
           if other == klass.M_INF:
               raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
           else:
               return self
       elif self == klass.M_INF:
           if other == klass.P_INF:
               raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
           else:
               return self
       else:
           return klass(int(self) + other)

    def __sub__(self, other):
       klass = self.__class__
       if isinstance(other, Time):
           raise TypeError("invalid operands: {0} + {1}".format(self.__class__.__name__, other.__class__.__name__))
       if self == klass.P_INF:
           if other == klass.P_INF:
               raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
           else:
               return self
       elif self == klass.M_INF:
           if other == klass.M_INF:
               raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
           else:
               return self
       else:
           return self.__class__(int(self) + other)

def create_dt(s):
    if isinstance(s, (int, float)):
        return Duration(s)
    elif isinstance(s, DT):
        return s
    else:
        for dtClass in Time, Duration:
            try:
                t = dtClass(s)
            except ValueError:
                pass
            else:
                return t
        else:
            return s

if __name__ == '__main__':
    import sys
    from dt_ast import dt_eval

    for expr in sys.argv[1:]:
        print(">>> {0!r} => {1}".format(expr, dt_eval(expr)))

