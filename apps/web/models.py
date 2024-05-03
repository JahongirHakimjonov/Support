from django.db import models
from apps.shared.models import AbstractBaseModel


class Home(AbstractBaseModel):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField()
    facebook = models.URLField()
    instagram = models.URLField()
    twitter = models.URLField()
    telegram = models.URLField()
    youtube = models.URLField()
    youtube_video = models.URLField()
    image = models.ImageField(upload_to="home/")
    logo = models.ImageField(upload_to="home/")

    class Meta:
        verbose_name = "Home"
        verbose_name_plural = "Home"
        db_table = "home"

    def __str__(self):
        return self.name
