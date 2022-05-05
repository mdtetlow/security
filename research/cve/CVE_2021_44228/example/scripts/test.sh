#!/bin/bash

subnet="172.18.0"
nodes="1 2 3 4"
services="log4jldapserver vulnerable_app wireshark"

for service in ${services}
do
  echo "${service}"
  for node in ${nodes};
  do
    docker compose exec ${service} ping -c 1 "${subnet}.${node}"
  done
done
