#!/usr/bin/env bash

# File:          install/install_on_remote_server_part_2.sh
# By:            Samuel Duclos
# For:           Myself
# Usage:         bash install/install_on_remote_server_part_2.sh
# Description:   Installs all packages required for the crypto_logger.
# Documentation: https://contabo.com/blog/first-steps-with-contabo/
#                https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-18-04
#                https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu-18-04
#                https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-vnc-on-ubuntu-18-04

# Initial configuration.
echo "This will guide you through the initial server configuration (part 2)." && \
SERVER_IP=$(cat server_keys.txt | cut -d':' -f1) && \
NEW_PASSWORD=$(cat server_keys.txt | cut -d':' -f2-) && \
echo "Enter your server's new user: " && \
read NEW_USER && \
read -s -p "Enter your server's initial root password: " SERVER_INITIAL_PASSWORD && \
echo "" && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} apt-get update && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} apt-get install -y mosh supervisor && \
sshpass -p ${SERVER_INITIAL_PASSWORD} scp conf.d/*.conf root@${SERVER_IP}:/etc/supervisor/conf.d && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "adduser --disabled-login --gecos \"\" \"${NEW_USER}\"" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "echo \"${NEW_USER}:${NEW_PASSWORD}\" | chpasswd" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "usermod -aG sudo ${NEW_USER}" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "sed -i 's/IPV6=no/IPV6=yes/g' /etc/default/ufw" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "ufw default deny incoming" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "ufw default allow outgoing" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "ufw allow OpenSSH" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "ufw allow 60000:61000/udp" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "ufw allow 8883/tcp" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "yes | ufw enable" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo -e "echo \"AllowUsers\t${NEW_USER}\" >> /etc/ssh/sshd_config" ) && \
sshpass -p ${SERVER_INITIAL_PASSWORD} ssh root@${SERVER_IP} $( echo "systemctl restart sshd" ) && \
sshpass -p ${NEW_PASSWORD} ssh ${NEW_USER}@${SERVER_IP} $( echo "echo ${NEW_PASSWORD} | sudo -S supervisorctl reread" ) && \
sshpass -p ${NEW_PASSWORD} ssh ${NEW_USER}@${SERVER_IP} $( echo "echo ${NEW_PASSWORD} | sudo -S supervisorctl reload" ) && \
sshpass -p ${NEW_PASSWORD} ssh ${NEW_USER}@${SERVER_IP} $( echo "sed -i 's/HISTSIZE=1000/HISTSIZE=100000/g' /home/${NEW_USER}/.bashrc" ) && \
sshpass -p ${NEW_PASSWORD} ssh ${NEW_USER}@${SERVER_IP} $( echo "sed -i 's/HISTFILESIZE=2000/HISTFILESIZE=200000/g' /home/${NEW_USER}/.bashrc" ) && \
sshpass -p ${NEW_PASSWORD} ssh ${NEW_USER}@${SERVER_IP} $( echo "mkdir -p ~/workspace" ) && \
sshpass -p ${NEW_PASSWORD} ssh < ./install/install_conda.sh ${NEW_USER}@${SERVER_IP} "bash -s -- '${NEW_PASSWORD}'" && \
sshpass -p ${NEW_PASSWORD} ssh < ./install/install_conda_crypto_logger_environment.sh ${NEW_USER}@${SERVER_IP} "bash -s"
