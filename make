#!/usr/bin/env bash
if (( $EUID != 0 )); then
    echo "Please run via sudo"
    exit
fi

PIP=`which pip || which pip3`
sudo -u ${SUDO_USER} ${PIP} install -e .

npm init --yes
npm install -g @apidevtools/swagger-cli
npm install "openapi-types@>=7" --save-dev
