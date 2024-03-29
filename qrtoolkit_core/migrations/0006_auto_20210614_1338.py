# Generated by Django 3.0.11 on 2021-06-14 13:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qrtoolkit_core', '0005_remove_erronous_hits'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiCall',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('payload', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='qrcode',
            name='mode',
            field=models.CharField(choices=[('kiosk', 'Kiosk Mode'), ('redirect', 'Redirect Mode'), ('info_page', 'Information Page Mode')], default='redirect', help_text='\nSets the mode this code is in.<br/>\nKiosk Mode: Show buttons to choose a link from<br/>\nRedirect Mode: Instantly redirects to the url with the highest priority.<br/>\nInformation Page Mode: Show basic info with links to different urls.\n', max_length=16),
        ),
        migrations.CreateModel(
            name='Header',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=128)),
                ('value', models.CharField(max_length=128)),
                ('api_call', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='headers', to='qrtoolkit_core.ApiCall')),
            ],
        ),
        migrations.AddField(
            model_name='apicall',
            name='code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_calls', to='qrtoolkit_core.QRCode'),
        ),
    ]
