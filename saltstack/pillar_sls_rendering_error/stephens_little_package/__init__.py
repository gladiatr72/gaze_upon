
# _*_ encoding:utf-8 _*_
# pylint: disable=too-few-public-methods,logging-format-interpolation,unused-argument

'''
    the wrapt module is not packaged by epel.  Install via pip.

'''
import pprint
import logging

try:
    import wrapt
    WRAPT = True
except ImportError:
    WRAPT = False

log = logging.getLogger(__name__)


class PrettyLog(object):
    ''' 
    a thing to make log output sparkle 
    '''
    def __init__(self, obj):
        self.obj = obj
    def __repr__(self):
        return pprint.pformat(self.obj)

def traceit(*args, **kwargs):
    '''
    decorator to mark function ingress/egress and dump its indicators
    to a log object
    '''
    if WRAPT:
        @wrapt.decorator
        def _wrapper(wrapped, instance, args, kwargs):
            ''' the moving bits '''
            log.critical('---> {1}.{0}, line, {2}'.format(
                wrapped.func_name,
                wrapped.__module__,
                wrapped.func_code.co_firstlineno))
            retval = wrapped(*args, **kwargs)
            log.critical('         <--- {1}.{0}, line, {2}'.format(
                wrapped.func_name,
                wrapped.__module__,
                wrapped.func_code.co_firstlineno))
            return retval

        return _wrapper(*args, **kwargs)
    else:
        pass

