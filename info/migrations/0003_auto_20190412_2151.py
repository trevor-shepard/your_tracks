# Generated by Django 2.2 on 2019-04-12 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('info', '0002_usertracktally'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertracktally',
            name='count',
            field=models.IntegerField(default=0),
        ),
    ]
