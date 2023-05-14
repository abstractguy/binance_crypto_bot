#!/usr/bin/env bash

# File:        install_mqtts.sh
# By:          Samuel Duclos
# For:         Myself
# Description: Convenience script to secure MQTT connection over SSL (TLS).
# Usage:       bash install/install_mqtts.sh <PASSWORD>
# Example 1:   bash install/install_mqtts.sh password123
# Example 2:   bash install/install_mqtts.sh
# Arguments:   <PASSWORD>: optional sudo password    (default is "")

# Parse and set optional password argument from command-line.
PASSWORD=$(echo "${1:-}")

# Take password from command-line if set, else ask live.
if [[ "$(echo ${PASSWORD})" == "" ]]
then
    read -s -p "Enter your password: " PASSWORD
fi

# Rewrite to be non-interactive.
# Install and configure MQTTS with mosquitto non-interactively, generating keys for TLS.
# See https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-ubuntu-18-04
# See https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-ubuntu-20-04
# See https://www.digitalocean.com/community/tutorials/how-to-secure-the-mosquitto-mqtt-broker-on-ubuntu-20-04
# See https://www.digitalocean.com/community/tutorials/how-to-install-mosquitto-mqtt-on-ubuntu-20-04
# See https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-centos-8
# See https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-ubuntu-18-04
# See https://www.digitalocean.com/community/tutorials/how-to-secure-the-mosquitto-mqtt-broker-on-ubuntu-20-04
# See https://www.digitalocean.com/community/tutorials/how-to-install-mosquitto-mqtt-on-ubuntu-20-04
# See https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-centos-8
# See https://www.hivemq.com/blog/mqtt-security-fundamentals
# See https://www.hivemq.com/blog/mqtt-security-fundamentals-part-2
# See https://www.hivemq.com/blog/mqtt-security-fundamentals-part-3
# See https://www.hivemq.com/blog/mqtt-security-fundamentals-part-4
# See https://www.hivemq.com/blog/mqtt-security-fundamentals-part-5
# See https://www.hivemq.com/blog/mqtt-security-fundamentals-part-6
# See https://www.hivemq.com/blog/mqtt-security-fundamentals-part-7
# See https://www.hivemq.com/blog/mqtt-security-fundamentals-part-8
# See https://www.hivemq.com/blog/mqtt-security-fundamentals-part-9
# See https://www.hivemq.com/blog/mqtt-security-fundamentals-part-10

# Certificate authority.
echo ${PASSWORD} | sudo -S apt update && \
echo ${PASSWORD} | sudo -S apt install -y software-properties-common && \
echo ${PASSWORD} | sudo -S apt update && \
echo ${PASSWORD} | sudo -S apt-add-repository ppa:mosquitto-dev/mosquitto-ppa && \
echo ${PASSWORD} | sudo -S apt update && \
echo ${PASSWORD} | sudo -S apt install -y mosquitto mosquitto-clients && \
#echo ${PASSWORD} | sudo -S systemctl enable mosquitto.service && \
#echo ${PASSWORD} | sudo -S systemctl restart mosquitto && \
#echo ${PASSWORD} | sudo -S mosquitto_passwd -c /etc/mosquitto/passwd sam && \
cd && \
echo ${PASSWORD} | sudo -S rm -rf certs && \
mkdir -p certs && \
cd certs && \
#openssl req -new -x509 -days 365 -extensions v3_ca -keyout ca.key -out ca.crt && \
openssl genrsa -des3 -out ca.key 2048 && \
openssl req -new -x509 -days 365 -key ca.key -out ca.crt && \
#vmi1085106.contaboserver.net
# MQTTS broker.
openssl genrsa -out server.key 2048 && \
openssl req -new -out server.csr -key server.key && \
openssl rsa -in server.key -out server.key && \
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 100 && \
#rm broker.csr && \
echo ${PASSWORD} | sudo -S cp ca.crt /etc/mosquitto/ca_certificates && \
echo ${PASSWORD} | sudo -S cp server.crt /etc/mosquitto/certs && \
echo ${PASSWORD} | sudo -S cp server.key /etc/mosquitto/certs && \
# MQTTS client.
openssl genrsa -out client.key 2048 && \
openssl req -out client.csr -key client.key -new && \
openssl rsa -in client.key -out client.key && \
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 100 && \
cd .. && \
echo ${PASSWORD} | sudo -S chmod 0700 ~/certs && \
echo ${PASSWORD} | sudo -S chmod 0600 ~/certs/* && \
# MQTTS broker configuration.
#echo ${PASSWORD} | sudo -S chmod /etc/mosquitto/mosquitto.conf && \
#echo ${PASSWORD} | sudo -S cat > /etc/mosquitto/mosquitto.conf <<EOF
## Place your local configuration in /etc/mosquitto/conf.d/
##
## A full description of the configuration file is at
## /usr/share/doc/mosquitto/examples/mosquitto.conf.example
#
#per_listener_settings true
#
#persistence true
#persistence_location /var/lib/mosquitto/
#
#log_dest file /var/log/mosquitto/mosquitto.log
#
#include_dir /etc/mosquitto/conf.d
#
#allow_anonymous false
#listener 1883
#password_file /etc/mosquitto/passwd
#
#cafile /home/sam/certs/ca/ca.crt
##capath /home/sam/certs/ca
#
## Path to the PEM encoded server certificate.
#certfile /home/sam/certs/broker/broker.crt
#
## Path to the PEM encoded keyfile.
#keyfile /home/sam/certs/broker/broker.key
#require_certificate true
#EOF
#echo ${PASSWORD} | sudo -S cat > /etc/mosquitto/mosquitto.conf <<EOF
## Place your local configuration in /etc/mosquitto/conf.d/
##
## A full description of the configuration file is at
## /usr/share/doc/mosquitto/examples/mosquitto.conf.example
#
#listener 8883
#
#cafile /etc/mosquitto/ca_certificates/ca.crt
#
## Path to the PEM encoded server certificate.
#certfile /etc/mosquitto/certs/server.crt
#
## Path to the PEM encoded keyfile.
#keyfile /etc/mosquitto/certs/server.key
#
#tls_version tlsv1
#require_certificate true
#EOF
echo ${PASSWORD} | sudo -S systemctl enable mosquitto.service && \
echo ${PASSWORD} | sudo -S systemctl restart mosquitto && \
echo ${PASSWORD} | sudo -S systemctl status mosquitto

#echo ${PASSWORD} | sudo -S mosquitto -v -c /etc/mosquitto/mosquitto.conf && \
# MQTTS client configuration
#cd client && \
#mosquitto_pub -p 8883 --cafile ca.crt --cert client.crt --key client.key -h localhost -m hello -t /world && \
# Check configs.
#openssl x509 -in broker.crt -text -noout
