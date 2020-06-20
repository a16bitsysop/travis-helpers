#!/bin/sh
curl -fsSL "https://github.com/docker/docker-credential-helpers/releases/download/v0.6.3/docker-credential-pass-v0.6.3-amd64.tar.gz" | tar -xvz
chmod +x docker-credential-pass
mv docker-credential-pass ~/bin/

echo "%echo Generating OpenPGP key
%transient-key
%no-protection
Key-Type: default
Subkey-Type: default
Name-Real: Travis Builder
Name-Comment: Travis Builder user
Name-Email: travis@example.com
Expire-Date: 1
%commit
%echo done" > keygen.txt

gpg --batch --gen-key keygen.txt
rm keygen.txt
gpg --check-trustdb

pass init $(gpg --list-secret-keys | grep -A1 ^sec | tail -n1 | sed 's+^[[:space:]]*++')
mkdir ~/.docker

echo '{
"credsStore":"pass",
"experimental":"enabled"
}' > ~/.docker/config.json
