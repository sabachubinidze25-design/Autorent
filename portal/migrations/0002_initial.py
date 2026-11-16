
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("portal", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="car",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cars",
                to=settings.AUTH_USER_MODEL,
                verbose_name="მფლობელი",
            ),
        ),
        migrations.AddField(
            model_name="favorite",
            name="car",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites",
                to="portal.car",
            ),
        ),
        migrations.AddField(
            model_name="favorite",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notifications",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="rental",
            name="car",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="rentals",
                to="portal.car",
            ),
        ),
        migrations.AddField(
            model_name="rental",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="rentals",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="favorite",
            constraint=models.UniqueConstraint(
                fields=("user", "car"), name="one_like_per_user_and_car"
            ),
        ),
    ]
