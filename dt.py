#!/usr/bin/env python3

import time

class MetaDT(type):
    def __new__(cls, class_name, class_bases, class_dict):
        t = super().__new__(cls, class_name, class_bases, class_dict)
        t.P_INF = t(t.P_INF_VALUE)
        t.M_INF = t(t.M_INF_VALUE)
        t.P_INF_LABELS = set(t.P_INF_ADDITIONAL_LABELS)
        t.P_INF_LABELS.add(t.P_INF_LABEL)
        t.M_INF_LABELS = set(t.M_INF_ADDITIONAL_LABELS)
        t.M_INF_LABELS.add(t.M_INF_LABEL)
        return t

class DT(int, metaclass=MetaDT):
    P_INF_VALUE = 2**64
    P_INF_LABEL = '+Inf'
    P_INF_ADDITIONAL_LABELS = {'Inf'}
    P_INF_LABELS = {P_INF_LABEL.lower(), 'Inf'.lower()}
    M_INF_VALUE = -2**64
    M_INF_LABEL = '-Inf'
    M_INF_ADDITIONAL_LABELS = {}
    M_INF_LABELS = {M_INF_LABEL.lower()}

    @classmethod
    def fromstring(cls, init):
        return cls(cls._string2int(init))

    @classmethod
    def _string2int(cls, init):
        raise NotImplemented()

    def __repr__(self):
       return "{0}({1})".format(self.__class__.__name__, str(self))

class DateTime(DT):
    DEFAULT_TIME_FORMAT = "%Y%m%d %H:%M:%S"
    TIME_FORMAT = DEFAULT_TIME_FORMAT
    ALTERNATE_TIME_FORMATS = (
	DEFAULT_TIME_FORMAT,
	'%Y%m%d',
    )
    TIME_CONVERTER = time.localtime
    #TIME_CONVERTER = time.gmtime
    QUANTUM = 0
    P_INF_LABEL = '+TInf'
    P_INF_ADDITIONAL_LABELS = {'TInf', '+Inf', 'Inf'}
    M_INF_LABEL = '-TInf'
    M_INF_ADDITIONAL_LABELS = {'-Inf'}
    def __new__(cls, init=None):
        if init is None:
            init = time.time()
        elif isinstance(init, str):
            init = cls._string2int(init)
        t_seconds = init
        if cls.QUANTUM > 0:
            t_seconds = (int(t_seconds + time_quantum - 1) // time_quantum ) * time_quantum
        return DT.__new__(cls, t_seconds)

    @classmethod
    def set_time_format(cls, time_format):
        DateTime.TIME_FORMAT = time_format

    @classmethod
    def quantized(cls, time_quantum, t):
        if time_quantum > 0:
            qt = (int(t + time_quantum - 1) // time_quantum ) * time_quantum
            return cls(qt)
        else:
            return cls(t)

    @classmethod
    def _string2int(cls, init):
        l_init = init.lower()
        if l_init in cls.P_INF_LABELS:
            init = cls.P_INF
        elif l_init in cls.M_INF_LABELS:
            init = cls.M_INF
        else:
            if cls.TIME_FORMAT != cls.DEFAULT_TIME_FORMAT:
                time_formats = (cls.TIME_FORMAT, ) + cls.ALTERNATE_TIME_FORMATS
            else:
                time_formats = cls.ALTERNATE_TIME_FORMATS
            for time_format in time_formats:
                try:
                    init = time.mktime(time.strptime(init, time_format))
                    break
                except ValueError:
                    pass
            else:
                raise ValueError("cannot convert string {0} to a Time object".format(init))
        return init

    def __str__(self):
        return repr(self.tostring(self.TIME_FORMAT))

    def tostring(self, format):
        if self == 0:
            return ''
        elif self <= self.M_INF_VALUE:
            return self.M_INF_LABEL
        elif self >= self.P_INF_VALUE:
            return self.P_INF_LABEL
        else:
            return time.strftime(format, self.TIME_CONVERTER(self))

    def __add__(self, other):
        if self == self.M_INF_VALUE:
            if other == Duration.P_INF_VALUE:
                raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
            else:
                return self
        elif self == self.P_INF_VALUE:
            if other == Duration.M_INF_VALUE:
                raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
            else:
                return self
        if isinstance(other, DateTime):
            raise TypeError("invalid operands: {0} + {1}".format(self.__class__.__name__, other.__class__.__name__))
        elif isinstance(other, Duration):
            if other >= Duration.P_INF_VALUE:
                #print(">>> + {0} + {1} ===> {2}".format(self, other, self.P_INF))
                return self.P_INF
            elif other <= Duration.M_INF_VALUE:
                #print(">>> - {0} + {1} ===> {2}".format(self, other, self.P_INF))
                return self.M_INF
            else:
                return self.__class__(int(self) + other)
        elif isinstance(other, int):
            return self.__class__(int(self) + other)
        else:
            raise TypeError("invalid operands: {0} + {1}".format(self.__class__.__name__, other.__class__.__name__))

    def __sub__(self, other):
       if isinstance(other, DateTime):
           if self == self.P_INF_VALUE:
               if other == self.P_INF_VALUE:
                   raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
               else:
                   return Duration.P_INF
           if self == self.M_INF_VALUE:
               if other == self.M_INF_VALUE:
                   raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
               else:
                   return Duration.M_INF
           else:
               return Duration(int(self) - int(other))
       else:
           if not isinstance(other, Duration):
               other = Duration(other)
           if self == self.P_INF_VALUE:
               if other == Duration.M_INF_VALUE:
                   raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
               else:
                   return self
           elif self == self.M_INF_VALUE:
               if other == Duration.P_INF_VALUE:
                   raise OverflowError("invalid operation {0!r} + {1!r}".format(self, other))
               else:
                   return self
           else:
               return Duration(int(self) - int(other))

    def date(self):
        return Date(self)
     

#class DateTime(DateTimeType):
#    TIME_QUANTUM = 0
#    def date(self):
#        return Date(self)
    
class Time(DateTime):
    pass

class Date(DateTime):
    DEFAULT_TIME_FORMAT = "%Y%m%d"
    TIME_FORMAT = DEFAULT_TIME_FORMAT
    ALTERNATE_TIME_FORMATS = (
	DEFAULT_TIME_FORMAT,
    )
    TIME_QUANTUM = 86400
    
    def datetime(self):
        return DateTime(self)
    
class Duration(DT):
    P_INF_LABEL = '+DInf'
    P_INF_ADDITIONAL_LABELS = {'DInf', '+Inf', 'Inf'}
    M_INF_LABEL = '-DInf'
    M_INF_ADDITIONAL_LABELS = {'-Inf'}
    def __new__(cls, init=None):
        if init is None:
            init = -1
        elif isinstance(init, str):
            if init == cls.M_INF_LABEL:
                init = cls.M_INF
            elif init == cls.P_INF_LABEL:
                init = cls.P_INF
            else:
                init = int(cls._string2int(init))
        return DT.__new__(cls, init)

    @classmethod
    def _string2int(cls, init):
        l_init = init.lower()
        if l_init in cls.M_INF_LABELS:
            init = cls.M_INF
        elif l_init in cls.P_INF_LABELS:
            init = cls.P_INF
        else:
            l = init.split('+', 1)
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
            elif len(l) == 1:
                n_hours = 0
                n_minutes = 0
                n_seconds = int(l[0].strip())
            init = n_seconds + 60 * (n_minutes + 60 * (n_hours + 24 * n_days))
        return init

    @classmethod
    def fromstring(cls, init):
        return cls(cls._string2int(init))

    def __str__(self):
        return repr(self.tostring())

    def tostring(self, days=True, microseconds=False):
        if self == 0:
            return '0'
        elif self <= self.M_INF_VALUE:
            return self.M_INF_LABEL
        elif self >= self.P_INF_VALUE:
            return self.P_INF_LABEL
        else:
            i_self = int(self)
            n_microseconds = (self - i_self) * 1000000
            n_days, i_rest = divmod(i_self, 86400)
            n_hours, i_rest = divmod(i_rest, 3600)
            n_minutes, n_seconds = divmod(i_rest, 60)
            if microseconds and n_microseconds:
                ms = '.{0:6d}'.format(n_microseconds)
            else:
                ms = ''
            if n_days and not days:
                n_hours += n_days * 24
                n_days = 0
            if n_days or n_hours:
                l_hms = [n_hours, n_minutes, n_seconds]
            else:
                l_hms = [n_minutes, n_seconds]
            hms = ':'.join('{0:02d}'.format(n) for n in l_hms)
            if n_days:
                fmt = "{0}+{1}{2}"
            else:
                fmt = "{1}{2}"
            return fmt.format(n_days, hms, ms)

def create_dt(s):
    if isinstance(s, (int, float)):
        return Duration(s)
    elif isinstance(s, DT):
        return s
    else:
        for dtClass in Date, DateTime, Duration:
            try:
                #print("DBG: CREATE_DT(s={0}, type={1}, {2}) ->".format(s, type(s), dtClass))
                t = dtClass(s)
            except ValueError:
                pass
            else:
                return t
        else:
            return s

