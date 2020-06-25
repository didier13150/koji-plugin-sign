# Koji callback for GPG signing RPMs before import
#
# Author:
#     Paul B Schroeder <paulbsch "at" vbridges "dot" com>
# Modified by:
#     Didier Fabert <didier "at" tartarefr "dot" eu>

from koji.plugin import register_callback
import logging
import koji

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
    rpms = ''
    for relpath in [kws['srpm']] + kws['rpms']:
       rpms += '%s/%s ' % (uploadpath, relpath)

    # Get the packages signed
    import pexpect
    LOG.info('Attempting to sign packages'
       ' (%s) with key "%s"' % (rpms, gpg_name))
    rpm_cmd = "%s --resign"
    # According to gpg man page, loopback redirect Pinentry queries to the caller.
    # Default values for macros can be printed with "rpm --showrc" command
    rpm_cmd += " --define '_gpg_sign_cmd_extra_args --pinentry-mode=loopback'"
    #rpm_cmd += " --define '__gpg_sign_cmd %{__gpg} gpg --pinentry-mode=loopback --no-verbose --no-armor --no-secmem-warning -u "%{_gpg_name}" -sbo %{__signature_filename} %{__plaintext_filename}'"
    #rpm_cmd += " --define '__gpg_check_password_cmd /bin/true'"
    rpm_cmd += " --define '_signature gpg'" % rpm
    rpm_cmd += " --define '_gpgbin %s'" % gpgbin
    rpm_cmd += " --define '_gpg_path %s'" % gpg_path
    rpm_cmd += " --define '_gpg_name %s' %s" % (gpg_name, rpms)
    pex = pexpect.spawn(rpm_cmd, timeout=1000)
    pex.expect('(E|e)nter (P|p)ass (P|p)hrase:', timeout=1000)
    pex.sendline(gpg_pass)
    i = pex.expect(['good', 'failed', 'skipping', pexpect.TIMEOUT])
    if i == 0:
        LOG.info('Package sign successful!')
    elif i == 1:
        LOG.error('Pass phrase check failed!')
    elif i == 2:
        LOG.error('Package sign skipped!')
    elif i == 3:
        LOG.error('Package sign timed out!')
    else:
        LOG.error('Unexpected sign result!')
    if i != 0:
        raise Exception('Package sign failed!')
    pex.expect(pexpect.EOF)

register_callback('preImport', sign)
