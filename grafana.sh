#/bin/bash
chmod -R 777 ./grafana/grafana_data
sudo systemctl restart docker
docker-compose down
