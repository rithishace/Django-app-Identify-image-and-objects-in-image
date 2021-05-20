# Generated by Django 3.1.6 on 2021-05-20 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ImageClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Image', models.ImageField(upload_to='images/')),
                ('text', models.CharField(blank=True, max_length=500, null=True)),
                ('Recognised', models.ImageField(blank=True, null=True, upload_to='recog/')),
            ],
        ),
    ]