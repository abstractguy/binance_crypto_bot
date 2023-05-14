#!/usr/bin/env bash

# File:        install/install_virtualbox.sh
# By:          Samuel Duclos
# For:         Myself
# Usage:       bash install/install_virtualbox.sh
# Description: VirtualBox 6.1.22 installer.

sudo echo "deb [arch=amd64] https://download.virtualbox.org/virtualbox/debian bionic contrib" >> /etc/apt/sources.list
wget -q https://www.virtualbox.org/download/oracle_vbox_2016.asc -O- | sudo apt-key add -
wget -q https://www.virtualbox.org/download/oracle_vbox.asc -O- | sudo apt-key add -
sudo apt-get update
sudo apt-get install virtualbox-6.1
wget https://download.virtualbox.org/virtualbox/6.1.22/Oracle_VM_VirtualBox_Extension_Pack-6.1.22.vbox-extpack
echo "Install downloaded Oracle_VM_VirtualBox_Extension_Pack-6.1.22.vbox-extpack by clicking!"

