#!/bin/sh
mkdir -p /opt/asdf
cp ./asdf.py /opt/asdf/asdf.py
ln -sf /opt/asdf/asdf.py /usr/bin/asdf
