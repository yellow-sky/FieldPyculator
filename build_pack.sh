#!/bin/bash

#Build zip packet

#Create if need
rm -R /tmp/build_plugin/field_pyculator
mkdir /tmp/build_plugin/
mkdir /tmp/build_plugin/field_pyculator
cp -R ./src/* /tmp/build_plugin/field_pyculator

#Clean
rm /tmp/build_plugin/field_pyculator/*.pyc
rm /tmp/build_plugin/field_pyculator.zip

cd /tmp/build_plugin/
zip -r field_pyculator.zip ./field_pyculator

echo "Pack for load: /tmp/build_plugin/field_pyculator.zip"