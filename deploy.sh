git pull
docker-compose down --rmi all
docker stack deploy -c docker-compose.yml publisher

