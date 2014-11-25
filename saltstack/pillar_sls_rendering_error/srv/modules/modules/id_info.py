# _*_ encoding: utf-8 _*_


from __future__ import print_function
import os
import re
import socket
from subprocess import Popen, PIPE
from stephens_little_package import traceit, PrettyLog
import logging

log = logging.getLogger(__name__)

__virtualname__ = 'id_info'

def __virtual__():
    return __virtualname__

@traceit
def hostinfo(id):
    '''
         host,
         domain,
         host_canonical,
         domain_canonical,
         fqdn_canonical,
    '''

    log.critical(' minion_id = {0}'.format(id))

    salty = __salt__
    import salt.syspaths
    import salt.utils

    cache_dir = os.path.join(salt.syspaths.CACHE_DIR, "master")
    hi_cache_dir = os.path.join(cache_dir, "hostinfo_cache")

    id_fq_path = os.path.join(hi_cache_dir, id )
    id_file_path = os.path.join(id_fq_path, id)

    for pathel in [ hi_cache_dir, id_fq_path ]:
        if not salty['file.directory_exists'](pathel):
            salty['file.mkdir'](pathel)

    if salty['file.file_exists'](id_file_path):
        with open(id_file_path, 'r') as fh_ifp:
            domain = fh_ifp.read()
        host = re.sub(r'.{0}'.format(domain), '', id)
    else:

        grains = {}

        DIG = salt.utils.which('dig')
        HOSTNAME = salt.utils.which('hostname')

        host = socket.getfqdn()

        cmdlist ='{0} {1} SOA +noanswer +noquestion +nocomments +noadditional +nostats'.format(
            DIG, host).split(' ')
        proc = Popen(cmdlist, stdout=PIPE, stderr=PIPE)

        out, err = proc.communicate()

        domain_res = re.search(r'^.*\n([^;][\w.-]+)\..*$', out, re.MULTILINE)

        if domain_res is None:
            cmdlist = [ HOSTNAME ]

            proc = Popen(cmdlist, stdout=PIPE, stderr=PIPE)
            out, err = proc.communicate()
            hostname = out.strip().split('.')
            host = hostname[0]
            domain = '.'.join(hostname[1:]) if len(hostname) > 1 else ''
        else:
            domain = domain_res.group(1) if domain_res is not None else ''

            host = re.sub('.{0}'.format(domain), '', host)

        with open(id_file_path, 'w') as fh_ifp:
            print(domain, file=fh_ifp)


    host_canonical = re.sub(r'\.', '_', host)
    domain_canonical = re.sub(r'\.', '_', domain)
    fqdn_canonical = re.sub(r'\.', '_', "%s.%s" % (host, domain))


    retval = {
            "host": host,
            "domain": domain,
            "host_canonical": host_canonical,
            "domain_canonical": domain_canonical,
            "fqdn_canonical": fqdn_canonical,
    }

    return retval


@traceit
def explode(id):
    '''
    return a dict with the given (minion) id split up:

    example: app-01.mt.widpi.prod.iad3.caltesting.org
        subcomponent (-instance number): app
        component: mt
        project: widpi
        environment: prod
        location: iad3
    '''

    h_info = hostinfo(id)
    retval = {}

    log.critical(' minion_id = {0}'.format(id))

    domain = h_info['domain']

    try:
        host = re.sub(r'.{domain}'.format(domain=domain), '', id)
        log.critical('Host lookup successful.  host = "{0}"'.format(host))
    except Exception as e:
        log.critical('Not able to determine the host name.  Domain not available\nEXCEPTION: {0}'.format(
            PrettyLog(e)))

    bits = host.split('.')
    dom_bits = domain.split('.')

    number_host_bits = len(bits)

    try:
        if number_host_bits > 0:
            retval['subcomponent'] = re.sub(r'-\d+$', '', bits[0])
            retval['instance'] = re.sub(r'^.*-(\d+)$', r'\1', bits[0])
        else:
            retval['subcomponent'] = 'unknown'

        if number_host_bits > 1:
            retval['component'] = bits[1]
        else:
            retval['component'] = 'unknown'

        if number_host_bits > 2:
            retval['project'] = bits[2]
        else:
            retval['project'] = 'unknown'

        if number_host_bits > 3:
            retval['environment'] = bits[3]
        else:
            retval['environment'] = 'unknown'

        if number_host_bits > 4:
            retval['location'] = bits[4]
        else:
            retval['location'] = 'unknown'

        if len(dom_bits) > 2:
            retval['location'] = dom_bits[0]

        p = retval['project']
        sc = retval['subcomponent']
        co = retval['component']

        if p != 'mten':
            retval['project_list'] = {p: {co: [sc]}}
    except Exception as e:
        log.critical('id_info() has just shit its pants.\nERROR: {0}\n'.format(
            PrettyLog(e)))
        retval

    log.critical('and now, ID_INFO() (the ext_module): \n{0}'.format(
        PrettyLog(retval)))
    return retval
