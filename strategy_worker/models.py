from django.db import models
from django.contrib.auth.models import User
import docker

# Create your models here.


class StrategyWorker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    docker_container_id = models.CharField(max_length=150)

    def __str__(self):
        return self.docker_container_id

    @property
    def container(self):
        client = docker.from_env()

        return client.containers.get(self.docker_container_id)

    def kill_container(self):
        try:
            self.container.kill()
            self.container.delete()
        except:
            pass
