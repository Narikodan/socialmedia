# Generated by Django 4.2.1 on 2023-07-16 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_post_created_at'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='like',
            unique_together={('user', 'post')},
        ),
    ]
