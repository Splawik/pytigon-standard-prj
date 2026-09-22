#!/bin/bash

cd pytigon_standard_prj   
ptig --dev manage_schdevtools prepare_installer_files --output-path ${PWD}/install
cd ..
echo -n "[DEFAULT]
GEN_TIME='" > ./pytigon_standard_prj/install.ini
echo -n $(date +"%Y-%m-%d %H:%M:%S") >> ./pytigon_standard_prj/install.ini
echo "'" >> ./pytigon_standard_prj/install.ini
rm -rf /tmp/pytigon
mkdir /tmp/pytigon
export DATA_PATH=/tmp/pytigon
ptig manage__schdata makeallmigrations
ptig manage__schtools makeallmigrations
ptig manage__schwiki makeallmigrations
ptig manage_schdevtools makeallmigrations
ptig manage_schdevtools migrate
ptig manage_schdevtools createautouser
ptig manage_schdevtools import_projects
prit pip_schpytigondemo upgradelocallibs
ptig manage_schpytigondemo makeallmigrations
ptig manage_schpytigondemo migrate
ptig manage_schpytigondemo createautouser
ptig manage_schmanage makeallmigrations
ptig manage_schmanage migrate
ptig manage_schmanage createautouser
ptig manage_schwebtrapper makeallmigrations
ptig manage_schwebtrapper migrate
ptig manage_schwebtrapper createautouser
ptig manage_scheditor makeallmigrations
ptig manage_scheditor migrate
ptig manage_scheditor createautouser
ptig manage_schportal makeallmigrations
ptig manage_schportal migrate
ptig manage_schportal createautouser
echo -n "[DEFAULT]
GEN_TIME='" > /tmp/pytigon/install.ini
echo -n $(date +"%Y-%m-%d %H:%M:%S") >> /tmp/pytigon/install.ini
echo "'" >> /tmp/pytigon/install.ini
echo "" > ./pytigon_standard_prj/install/__init__.py
rm ./pytigon_standard_prj/install/.pytigon.zip
rm -rf /tmp/pytigon/prg/{*,.*}
find /tmp/pytigon -mindepth 1 -path '*/prjlib/*' -delete
7z a ./pytigon_standard_prj/install/.pytigon.zip /tmp/pytigon/*
cd ..
