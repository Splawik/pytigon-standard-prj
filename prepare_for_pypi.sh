#!/bin/bash

cd pytigon_standard_prj   
ptig --dev manage_schdevtools prepare_installer_files --output-path ${PWD}/install
cd ..
echo -n "[DEFAULT]
GEN_TIME='" > ./pytigon_standard_prj/install.ini
echo -n $(date +"%Y-%m-%d %H:%M:%S") >> ./pytigon_standard_prj/install.ini
echo "'" >> ./pytigon_standard_prj/install.ini
