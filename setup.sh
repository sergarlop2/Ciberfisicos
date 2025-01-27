#!/bin/bash

sudo chmod -R 777 ./grafana/grafana_data
docker-compose pull
docker-compose build
docker-compose up -d base_datos
sleep 5
docker-compose down
