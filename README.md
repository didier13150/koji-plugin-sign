# koji-plugin-sign

Koji plugin to sign rpm

* Python 3 ready
* Tested with koji 1.21.1 on CentOS 8

## Create gnupg key

1. Create gnupg root directory for apache

    ```
    mkdir /var/lib/koji-sign
    ```
2. Create gnupg template file for all keys

    ```
    cat << EOF > /var/lib/koji-sign/key.template
    %echo Generating Signing Key
    Key-Type: RSA
    Key-Length: @GPG_SIZE@
    Subkey-Type: default
    Name-Real: @GPG_NAME@
    Name-Comment: @GPG_COMMENT@
    Name-Email: @GPG_EMAIL@
    Expire-Date: 0
    Passphrase: @GPG_PASS@
    %commit
    EOF
    ```
3. Create gnupg config file for centos 7

    ```
    sed \
        -e 's/@GPG_SIZE@/2048/' \
        -e 's/@GPG_NAME@/CentOS-7-pkgs/' \
        -e 's/@GPG_COMMENT@/CentOS 7 Signing Key/' \
        -e 's/@GPG_EMAIL@/me@example.com/' \
        -e 's/@GPG_PASS@/*******/' \
        /var/lib/koji-sign/key.template > /var/lib/koji-sign/centos-7-key.template
    ```
4. Create gnupg key for centos 7

    ```
    export GNUPGHOME=/var/lib/koji-sign
    su - apache -s /bin/bash -c "GNUPGHOME=${GNUPGHOME} gpg --batch --gen-key /var/lib/koji-sign/centos-7-key.template"
    ```

## Installation

1. Copy sign.conf to /etc/koji-hub/plugins/sign.conf
2. Copy sign.py to /usr/lib/koji-hub-plugins/sign.py
3. Modify /etc/koji-hub/plugins/sign.conf to adapt to your own
    * gpg_path is the gnupg directory for apache user
    * gpg_name is the name of the gnupg key
    * gpg_pass is the passphrase for the gnupg key
    * centos-7-build is the koji tag for centos 7 build (```koji add-tag --parent "centos-7" --arches 'x86_64' centos-7-build```)

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

## Off

Original file can be found on [fedora mailing list](https://lists.fedoraproject.org/pipermail/buildsys/2011-February/003566.html)

Thanks to Paul B Schroeder who wrote this plugin.
