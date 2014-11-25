#!py

import logging

log = logging.getLogger(__name__)

def run():
  retval = {}

  id = __opts__['id']
  exp = __salt__['id_info.explode'](id)

  if exp['project'] != 'mten':
      retval['project_list'] = exp['project_list']
      del(exp['project_list'])

  retval.update(exp)
  retval['id_info'] = exp


  log.debug('**<*>** {0}'.format(retval))

  return retval

