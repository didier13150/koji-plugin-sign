# koji-plugin-sign

Koji plugin to sign rpm

* Python 3 ready

File /etc/koji-hub/plugins/sign.conf

```
[DEFAULT]
rpm = /usr/bin/rpm
gpgbin = /usr/bin/gpg
gpg_path = /var/lib/koji-sign
gpg_name = default-pkgs
gpg_pass = *******

[centos-7-build]
rpm = /usr/bin/rpm
gpgbin = /usr/bin/gpg
gpg_path = /var/lib/koji-sign
gpg_name = CentOS-7-pkgs
gpg_pass = *******

```

Original file can be found on [fedora mailing list](https://lists.fedoraproject.org/pipermail/buildsys/2011-February/003566.html)

Thanks to Paul B Schroeder who wrote this plugin.
