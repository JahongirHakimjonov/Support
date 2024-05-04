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


class About(AbstractBaseModel):
    full_name = models.CharField(max_length=255)
    date = models.DateField()
    age = models.IntegerField()
    info = models.TextField()
    image = models.ImageField(upload_to="about/")
    resume_link = models.URLField()
    github_link = models.URLField()
    portfolio_link = models.URLField()
    linkedin_link = models.URLField()
    instagram_link = models.URLField()
    telegram_link = models.URLField()

    class Meta:
        verbose_name = "About"
        verbose_name_plural = "About"
        db_table = "about"

    def __str__(self):
        return self.full_name


class SiteUsers(AbstractBaseModel):
    useremail = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.useremail}"

    class Meta:
        verbose_name_plural = "Sayt Foydalanuvchilar"
        db_table = "site_user"
