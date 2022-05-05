#!/bin/bash

docker compose stop
docker network rm example_log4j
docker rm $(docker ps -qa)
