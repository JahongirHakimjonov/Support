# Generated by Django 5.0.3 on 2024-05-04 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="About",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("full_name", models.CharField(max_length=255)),
                ("date", models.DateField()),
                ("age", models.IntegerField()),
                ("info", models.TextField()),
                ("image", models.ImageField(upload_to="about/")),
                ("resume_link", models.URLField()),
                ("github_link", models.URLField()),
                ("portfolio_link", models.URLField()),
                ("linkedin_link", models.URLField()),
                ("instagram_link", models.URLField()),
                ("telegram_link", models.URLField()),
            ],
            options={
                "verbose_name": "About",
                "verbose_name_plural": "About",
                "db_table": "about",
            },
        ),
    ]
