
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="car",
            name="image1",
            field=models.ImageField(
                upload_to="cars/%Y/%m/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        ["png", "jpg", "jpeg", "jfif"],
                        message="ფოტო უნდა იყოს .png, .jpg, .jpeg ან .jfif ფორმატის.",
                    )
                ],
                verbose_name="ფოტო 1",
            ),
        ),
        migrations.AlterField(
            model_name="car",
            name="image2",
            field=models.ImageField(
                upload_to="cars/%Y/%m/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        ["png", "jpg", "jpeg", "jfif"],
                        message="ფოტო უნდა იყოს .png, .jpg, .jpeg ან .jfif ფორმატის.",
                    )
                ],
                verbose_name="ფოტო 2",
            ),
        ),
        migrations.AlterField(
            model_name="car",
            name="image3",
            field=models.ImageField(
                upload_to="cars/%Y/%m/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        ["png", "jpg", "jpeg", "jfif"],
                        message="ფოტო უნდა იყოს .png, .jpg, .jpeg ან .jfif ფორმატის.",
                    )
                ],
                verbose_name="ფოტო 3",
            ),
        ),
    ]
