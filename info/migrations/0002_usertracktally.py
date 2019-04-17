# Generated by Django 2.2 on 2019-04-12 18:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('info', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTrackTally',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=1)),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_track_tally', related_query_name='user_track_tally', to='info.Track')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='track_tally', related_query_name='track_tally', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
