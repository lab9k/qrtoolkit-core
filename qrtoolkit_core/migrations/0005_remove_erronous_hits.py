from django.conf import settings
from django.db import migrations, models


def remove_error_hits(apps, schema_editor):
    ApiHit = apps.get_model("qrtoolkit_core", "ApiHit")
    db_alias = schema_editor.connection.alias
    ApiHit.objects.using(db_alias).filter(message__icontains='does not exist.').delete()


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('qrtoolkit_core', '0004_auto_20210512_0733'),
    ]

    operations = [
        migrations.RunPython(remove_error_hits)
    ]
