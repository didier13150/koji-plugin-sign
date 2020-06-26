# Koji callback for GPG signing RPMs before import
#
# Author:
#     Paul B Schroeder <paulbsch "at" vbridges "dot" com>
# Modified by:
#     Didier Fabert <didier "at" tartarefr "dot" eu>

from koji.plugin import register_callback
import logging

CONFIG_FILE = '/etc/koji-hub/plugins/sign.conf'
CONFIG = None
LOG = logging.getLogger('koji.plugin.sign')

def sign(cbtype, *args, **kws):
    if kws['type'] != 'build':
       return

    # Get the tag name from the buildroot map
    import sys
    sys.path.insert(0, '/usr/share/koji-hub')
    from kojihub import get_buildroot
    br_id = list(kws['brmap'].values())[0]
    br = get_buildroot(br_id)
    tag_name = br['tag_name']

    # Get GPG info using the config for the tag name
    import koji
    global CONFIG
    if not CONFIG:
        CONFIG = koji.read_config_files([(CONFIG_FILE, True)])
    rpm = CONFIG.get(tag_name, 'rpm')
    gpgbin = CONFIG.get(tag_name, 'gpgbin')
    gpg_path = CONFIG.get(tag_name, 'gpg_path')
    gpg_name = CONFIG.get(tag_name, 'gpg_name')
    gpg_pass = CONFIG.get(tag_name, 'gpg_pass')

    # Get the package paths set up
    from koji import pathinfo
    uploadpath = pathinfo.work()
    rpms = []
    for relpath in [kws['srpm']] + kws['rpms']:
       rpms.append('%s/%s' % (uploadpath, relpath))

    # Get the packages signed
    LOG.info('Attempting to sign packages'
       ' (%s) with key "%s"' % (rpms, gpg_name))
    
    signcmd = []
    signcmd.append(rpm)
    signcmd.append("--resign")    
    
    # According to gpg man page, loopback redirect Pinentry queries to the caller.
    # Default values for macros can be printed with "rpm --showrc" command
    signcmd.append("--define='_gpg_sign_cmd_extra_args --batch --pinentry-mode=loopback --passphrase %s'" % (gpg_pass))
    signcmd.append("--define='_signature gpg'")
    signcmd.append("--define='_gpgbin %s'" % (gpgbin))
    signcmd.append("--define='_gpg_path %s'" % (gpg_path))
    signcmd.append("--define='_gpg_name %s'" % (gpg_name))
    for rpm in rpms:
        signcmd.append("%s" % (rpm))
    
    import os
    retval = os.system(" ".join(signcmd))
    if retval == 0:
        LOG.info('Package sign successful!')
    else:
        LOG.error('Package sign failed!')
        raise Exception('Package sign failed!')
    #import subprocess
    #try:
        #sigproc = subprocess.run(signcmd, check=True, timeout=1000, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #LOG.info('Package sign successful!')
    #except subprocess.TimeoutExpired:
        #LOG.error('Package sign timed out!')
        #raise Exception('Package sign failed: timed out!')
    #except subprocess.CalledProcessError as e:
        #LOG.error('RETVAL: %d, STDOUT: "%s", STDERR: "%s"' %(e.returncode,e.stdout.decode('utf-8'),e.stderr.decode('utf-8')))
        #raise Exception('Package sign failed!')

register_callback('preImport', sign)
