git pull

docker stack rm bittrade

docker rm -vf $(docker ps -a -q)

docker rmi -f $(docker images -a -q)

sleep 5

docker stack deploy -c docker-compose.yml bittrade


