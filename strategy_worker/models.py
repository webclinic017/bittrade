from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
import docker

# Create your models here.


class StrategyWorker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    docker_container_id = models.CharField(
        max_length=150, null=True, blank=True)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username + '[strategy]'

    @property
    def container(self):
        client = docker.from_env()

        return client.containers.get(self.docker_container_id)


@receiver(post_save, sender=User)
def create_strategy_worker(sender, instance, created, **kwargs):
    if created:
        StrategyWorker.objects.create(
            user=instance,
            docker_container_id='.',
            enabled=False
        )
