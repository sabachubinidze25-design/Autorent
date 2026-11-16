
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Car",
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
                (
                    "brand",
                    models.CharField(
                        choices=[
                            ("Abarth", "Abarth"),
                            ("Acura", "Acura"),
                            ("Aixam", "Aixam"),
                            ("Alfa Romeo", "Alfa Romeo"),
                            ("Alpine", "Alpine"),
                            ("Aston Martin", "Aston Martin"),
                            ("Audi", "Audi"),
                            ("Austin", "Austin"),
                            ("Bentley", "Bentley"),
                            ("BMW", "BMW"),
                            ("Brilliance", "Brilliance"),
                            ("Bugatti", "Bugatti"),
                            ("Buick", "Buick"),
                            ("BYD", "BYD"),
                            ("Cadillac", "Cadillac"),
                            ("Changan", "Changan"),
                            ("Chery", "Chery"),
                            ("Chevrolet", "Chevrolet"),
                            ("Chrysler", "Chrysler"),
                            ("Citroen", "Citroen"),
                            ("Cupra", "Cupra"),
                            ("Dacia", "Dacia"),
                            ("Daewoo", "Daewoo"),
                            ("Daihatsu", "Daihatsu"),
                            ("Datsun", "Datsun"),
                            ("Dodge", "Dodge"),
                            ("DS", "DS"),
                            ("Ferrari", "Ferrari"),
                            ("Fiat", "Fiat"),
                            ("Fisker", "Fisker"),
                            ("Ford", "Ford"),
                            ("GAZ", "GAZ"),
                            ("Geely", "Geely"),
                            ("Genesis", "Genesis"),
                            ("GMC", "GMC"),
                            ("Great Wall", "Great Wall"),
                            ("Haval", "Haval"),
                            ("Honda", "Honda"),
                            ("Hummer", "Hummer"),
                            ("Hyundai", "Hyundai"),
                            ("Infiniti", "Infiniti"),
                            ("Isuzu", "Isuzu"),
                            ("Iveco", "Iveco"),
                            ("Jaguar", "Jaguar"),
                            ("Jeep", "Jeep"),
                            ("Kia", "Kia"),
                            ("Koenigsegg", "Koenigsegg"),
                            ("Lada", "Lada"),
                            ("Lamborghini", "Lamborghini"),
                            ("Lancia", "Lancia"),
                            ("Land Rover", "Land Rover"),
                            ("Lexus", "Lexus"),
                            ("Lincoln", "Lincoln"),
                            ("Lotus", "Lotus"),
                            ("Lucid", "Lucid"),
                            ("Lynk & Co", "Lynk & Co"),
                            ("Mahindra", "Mahindra"),
                            ("Maserati", "Maserati"),
                            ("Maybach", "Maybach"),
                            ("Mazda", "Mazda"),
                            ("McLaren", "McLaren"),
                            ("Mercedes-Benz", "Mercedes-Benz"),
                            ("Mercury", "Mercury"),
                            ("MG", "MG"),
                            ("Mini", "Mini"),
                            ("Mitsubishi", "Mitsubishi"),
                            ("Nio", "Nio"),
                            ("Nissan", "Nissan"),
                            ("Opel", "Opel"),
                            ("Pagani", "Pagani"),
                            ("Peugeot", "Peugeot"),
                            ("Plymouth", "Plymouth"),
                            ("Polestar", "Polestar"),
                            ("Pontiac", "Pontiac"),
                            ("Porsche", "Porsche"),
                            ("RAM", "RAM"),
                            ("Renault", "Renault"),
                            ("Rivian", "Rivian"),
                            ("Rolls-Royce", "Rolls-Royce"),
                            ("Rover", "Rover"),
                            ("Saab", "Saab"),
                            ("SEAT", "SEAT"),
                            ("Skoda", "Skoda"),
                            ("Smart", "Smart"),
                            ("SsangYong", "SsangYong"),
                            ("Subaru", "Subaru"),
                            ("Suzuki", "Suzuki"),
                            ("Tesla", "Tesla"),
                            ("Toyota", "Toyota"),
                            ("UAZ", "UAZ"),
                            ("VAZ", "VAZ"),
                            ("Volkswagen", "Volkswagen"),
                            ("Volvo", "Volvo"),
                            ("Xpeng", "Xpeng"),
                            ("ZAZ", "ZAZ"),
                            ("Zeekr", "Zeekr"),
                        ],
                        max_length=40,
                        verbose_name="ბრენდი",
                    ),
                ),
                ("model", models.CharField(max_length=60, verbose_name="მოდელი")),
                (
                    "year",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1950),
                            django.core.validators.MaxValueValidator(2100),
                        ],
                        verbose_name="გამოშვების წელი",
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=8,
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="ფასი დღეში (₾)",
                    ),
                ),
                (
                    "capacity",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(60),
                        ],
                        verbose_name="ტევადობა",
                    ),
                ),
                (
                    "fuel_capacity",
                    models.DecimalField(
                        decimal_places=1,
                        max_digits=6,
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="ბაკის მოცულობა (ლიტრი)",
                    ),
                ),
                (
                    "transmission",
                    models.CharField(
                        choices=[
                            ("ავტომატიკა", "ავტომატიკა"),
                            ("მექანიკა", "მექანიკა"),
                            ("ტიპტრონიკი", "ტიპტრონიკი"),
                        ],
                        max_length=20,
                        verbose_name="ტრანსმისია",
                    ),
                ),
                (
                    "city",
                    models.CharField(
                        choices=[
                            ("თბილისი", "თბილისი"),
                            ("ბათუმი", "ბათუმი"),
                            ("ქუთაისი", "ქუთაისი"),
                            ("რუსთავი", "რუსთავი"),
                            ("გორი", "გორი"),
                            ("ზუგდიდი", "ზუგდიდი"),
                            ("ფოთი", "ფოთი"),
                            ("ხაშური", "ხაშური"),
                            ("სამტრედია", "სამტრედია"),
                            ("სენაკი", "სენაკი"),
                            ("ზესტაფონი", "ზესტაფონი"),
                            ("მარნეული", "მარნეული"),
                            ("თელავი", "თელავი"),
                            ("ახალციხე", "ახალციხე"),
                            ("ოზურგეთი", "ოზურგეთი"),
                            ("ქობულეთი", "ქობულეთი"),
                            ("მცხეთა", "მცხეთა"),
                            ("ბორჯომი", "ბორჯომი"),
                            ("საგარეჯო", "საგარეჯო"),
                            ("გარდაბანი", "გარდაბანი"),
                            ("ყვარელი", "ყვარელი"),
                            ("ლანჩხუთი", "ლანჩხუთი"),
                            ("წყალტუბო", "წყალტუბო"),
                            ("ახალქალაქი", "ახალქალაქი"),
                        ],
                        max_length=40,
                        verbose_name="ქალაქი",
                    ),
                ),
                (
                    "image1",
                    models.ImageField(
                        upload_to="cars/%Y/%m/",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                ["png", "jpg", "jpeg"],
                                message="ფოტო უნდა იყოს .png, .jpg ან .jpeg ფორმატის.",
                            )
                        ],
                        verbose_name="ფოტო 1",
                    ),
                ),
                (
                    "image2",
                    models.ImageField(
                        upload_to="cars/%Y/%m/",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                ["png", "jpg", "jpeg"],
                                message="ფოტო უნდა იყოს .png, .jpg ან .jpeg ფორმატის.",
                            )
                        ],
                        verbose_name="ფოტო 2",
                    ),
                ),
                (
                    "image3",
                    models.ImageField(
                        upload_to="cars/%Y/%m/",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                ["png", "jpg", "jpeg"],
                                message="ფოტო უნდა იყოს .png, .jpg ან .jpeg ფორმატის.",
                            )
                        ],
                        verbose_name="ფოტო 3",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "მანქანა",
                "verbose_name_plural": "მანქანები",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="Favorite",
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
            ],
            options={
                "verbose_name": "მოწონებული",
                "verbose_name_plural": "მოწონებულები",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Notification",
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
                ("text", models.CharField(max_length=300)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "შეტყობინება",
                "verbose_name_plural": "შეტყობინებები",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="Rental",
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
                ("start_date", models.DateField(verbose_name="დაწყება")),
                ("end_date", models.DateField(verbose_name="დასრულება")),
                ("price_per_day", models.DecimalField(decimal_places=2, max_digits=8)),
                (
                    "total_price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="გადასახდელი"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "აქტიური"), ("cancelled", "გაუქმებული")],
                        default="active",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("cancelled_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "verbose_name": "ქირაობა",
                "verbose_name_plural": "ქირაობები",
                "ordering": ["-start_date", "-id"],
            },
        ),
    ]
