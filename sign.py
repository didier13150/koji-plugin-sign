# Koji callback for GPG signing RPMs before import
#
# Author:
#     Paul B Schroeder <paulbsch "at" vbridges "dot" com>

from koji.plugin import register_callback
import logging

config_file = '/etc/koji-hub/plugins/sign.conf'

def sign(cbtype, *args, **kws):
    if kws['type'] != 'build':
       return

    # Get the tag name from the buildroot map
    import sys
    sys.path.insert(0, '/usr/share/koji-hub')
    from kojihub import get_buildroot
    br_id = kws['brmap'].values()[0]
    br = get_buildroot(br_id)
    tag_name = br['tag_name']

    # Get GPG info using the config for the tag name
    from ConfigParser import ConfigParser
    config = ConfigParser()
    config.read(config_file)
    rpm = config.get(tag_name, 'rpm')
    gpgbin = config.get(tag_name, 'gpgbin')
    gpg_path = config.get(tag_name, 'gpg_path')
    gpg_name = config.get(tag_name, 'gpg_name')
    gpg_pass = config.get(tag_name, 'gpg_pass')

    # Get the package paths set up
    from koji import pathinfo
    uploadpath = pathinfo.work()
    rpms = ''
    for relpath in [kws['srpm']] + kws['rpms']:
       rpms += '%s/%s ' % (uploadpath, relpath)

    # Get the packages signed
    import pexpect
    logging.getLogger('koji.plugin.sign').info('Attempting to sign packages'
       ' (%s) with key "%s"' % (rpms, gpg_name))
    rpm_cmd = "%s --resign --define '_signature gpg'" % rpm
    rpm_cmd += " --define '_gpgbin %s'" % gpgbin
    rpm_cmd += " --define '_gpg_path %s'" % gpg_path
    rpm_cmd += " --define '_gpg_name %s' %s" % (gpg_name, rpms)
    pex = pexpect.spawn(rpm_cmd, timeout=1000)
    pex.expect('(E|e)nter (P|p)ass (P|p)hrase:', timeout=1000)
    pex.sendline(gpg_pass)
    i = pex.expect(['good', 'failed', 'skipping', pexpect.TIMEOUT])
    if i == 0:
        logging.getLogger('koji.plugin.sign').info('Package sign successful!')
    elif i == 1:
        logging.getLogger('koji.plugin.sign').error('Pass phrase check failed!')
    elif i == 2:
        logging.getLogger('koji.plugin.sign').error('Package sign skipped!')
    elif i == 3:
        logging.getLogger('koji.plugin.sign').error('Package sign timed out!')
    else:
        logging.getLogger('koji.plugin.sign').error('Unexpected sign result!')
    if i != 0:
        raise Exception, 'Package sign failed!'
    pex.expect(pexpect.EOF)

register_callback('preImport', sign)
