git pull

docker stack rm bittrade

docker-compose down --rmi all -v

sleep 5

docker stack deploy -c docker-compose.yml publisher


