# vim: ft=python

import logging
from stephens_little_package import traceit, PrettyLog

log = logging.getLogger(__name__)


@traceit
def ext_pillar(minion_id, pillar):
    retval = {}

    if __grains__.get('wants_me_some_id_info', False):

        id = __opts__['id']
        exp = __salt__['id_info.explode'](id)

        if exp['project'] != 'mten':
            retval['project_list'] = exp['project_list']
            del(exp['project_list'])

        retval.update(exp)
        retval['id_info'] = exp

        log.critical('and then, PILLAR ID_INFO: \n{0}'.format(PrettyLog(retval)))

    return retval
