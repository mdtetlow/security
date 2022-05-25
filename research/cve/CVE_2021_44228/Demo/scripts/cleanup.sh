#!/bin/bash

docker compose stop
docker network rm demo_log4j demo_default
docker rm $(docker ps -qa)
