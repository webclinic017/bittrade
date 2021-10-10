git pull

docker stack rm $(docker stack ls)
docker rmi $(docker images -a -q)
docker container prune
docker image prune
docker volume prune

sleep 5

docker stack deploy -c docker-compose.yml publisher


