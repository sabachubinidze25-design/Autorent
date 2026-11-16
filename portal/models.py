from django.conf import settings
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from .choices import BRANDS, GEORGIAN_CITIES, TRANSMISSIONS

image_validator = FileExtensionValidator(
    ["png", "jpg", "jpeg", "jfif"], message="ფოტო უნდა იყოს .png, .jpg, .jpeg ან .jfif ფორმატის."
)


class Car(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name="cars", verbose_name="მფლობელი")
    brand = models.CharField("ბრენდი", max_length=40, choices=[(b, b) for b in BRANDS])
    model = models.CharField("მოდელი", max_length=60)
    year = models.PositiveSmallIntegerField("გამოშვების წელი",
                                            validators=[MinValueValidator(1950), MaxValueValidator(2100)])
    price = models.DecimalField("ფასი დღეში (₾)", max_digits=8, decimal_places=2,
                                validators=[MinValueValidator(1)])
    capacity = models.PositiveSmallIntegerField("ტევადობა", validators=[MinValueValidator(1), MaxValueValidator(60)])
    fuel_capacity = models.DecimalField("ბაკის მოცულობა (ლიტრი)", max_digits=6, decimal_places=1,
                                        validators=[MinValueValidator(1)])
    transmission = models.CharField("ტრანსმისია", max_length=20, choices=[(t, t) for t in TRANSMISSIONS])
    city = models.CharField("ქალაქი", max_length=40, choices=[(c, c) for c in GEORGIAN_CITIES])
    image1 = models.ImageField("ფოტო 1", upload_to="cars/%Y/%m/", validators=[image_validator])
    image2 = models.ImageField("ფოტო 2", upload_to="cars/%Y/%m/", validators=[image_validator])
    image3 = models.ImageField("ფოტო 3", upload_to="cars/%Y/%m/", validators=[image_validator])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "მანქანა"
        verbose_name_plural = "მანქანები"

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

    @property
    def photos(self):
        return [p for p in (self.image1, self.image2, self.image3) if p]

    @property
    def owner_phone(self):
        return self.owner.phone


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="favorites")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "car"], name="one_like_per_user_and_car")]
        ordering = ["-created_at"]
        verbose_name = "მოწონებული"
        verbose_name_plural = "მოწონებულები"

    def __str__(self):
        return f"{self.user.phone} ♥ {self.car}"


class Rental(models.Model):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    STATUSES = [(ACTIVE, "აქტიური"), (CANCELLED, "გაუქმებული")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rentals")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="rentals")
    start_date = models.DateField("დაწყება")
    end_date = models.DateField("დასრულება")
    price_per_day = models.DecimalField(max_digits=8, decimal_places=2)  # price at the moment of renting
    total_price = models.DecimalField("გადასახდელი", max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUSES, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-start_date", "-id"]
        verbose_name = "ქირაობა"
        verbose_name_plural = "ქირაობები"

    def __str__(self):
        return f"{self.car} · {self.start_date} – {self.end_date}"

    @property
    def days(self):
        return (self.end_date - self.start_date).days + 1  # both the first and the last day count

    @property
    def can_cancel(self):
        """Cancelling is possible only until the rental starts."""
        return self.status == self.ACTIVE and timezone.localdate() < self.start_date

    @property
    def phase(self):
        today = timezone.localdate()
        if self.status == self.CANCELLED:
            return "cancelled"
        if today < self.start_date:
            return "upcoming"
        if today <= self.end_date:
            return "ongoing"
        return "finished"

    @property
    def phase_label(self):
        return {"cancelled": "გაუქმებულია", "upcoming": "მომავალი",
                "ongoing": "მიმდინარე", "finished": "დასრულებულია"}[self.phase]


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    text = models.CharField(max_length=300)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "შეტყობინება"
        verbose_name_plural = "შეტყობინებები"

    def __str__(self):
        return self.text[:60]
