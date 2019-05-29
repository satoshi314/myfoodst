# Generated by Django 2.2.1 on 2019-05-28 14:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20190523_2125'),
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=30)),
                ('symbol', models.ImageField(blank=True, upload_to='system')),
            ],
        ),
        migrations.AddField(
            model_name='shop',
            name='comment',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name='shop',
            name='state',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.State'),
        ),
    ]