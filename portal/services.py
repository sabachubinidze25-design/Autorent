from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from .choices import BRANDS, GEORGIAN_CITIES
from .models import Car, Favorite, Notification, Rental

MAX_RENT_DAYS = 365
PAGE_SIZE = 9
PRICE_TABLE_DAYS = (1, 3, 7, 14, 30)

SORT_OPTIONS = [
    ("", "ნაგულისხმევი"),
    ("price_asc", "ფასი: ზრდადობით"),
    ("price_desc", "ფასი: კლებადობით"),
    ("year_new", "წელი: ახალი ჯერ"),
    ("year_old", "წელი: ძველი ჯერ"),
]
_SORT_FIELDS = {
    "price_asc": ("price", "-created_at"),
    "price_desc": ("-price", "-created_at"),
    "year_new": ("-year", "-created_at"),
    "year_old": ("year", "-created_at"),
}


class RentalError(Exception):
    """Raised with a ready-to-show Georgian message."""


def fmt_date(d):
    return d.strftime("%d.%m.%Y")


def money(value):
    """Decimal('90.00') -> '90', Decimal('12.50') -> '12.5'."""
    text = f"{Decimal(value):.2f}".rstrip("0").rstrip(".")
    return text or "0"


def to_int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def to_decimal(value):
    try:
        number = Decimal(str(value).strip().replace(",", "."))
    except (InvalidOperation, AttributeError):
        return None
    return number if number.is_finite() else None


def read_filters(params):
    """Clean the query string (a QueryDict or dict) into filter values."""
    sort = params.get("sort", "")
    brand = params.get("brand", "").strip()
    city = params.get("city", "").strip()
    return {
        "brand": brand if brand in BRANDS else "",
        "city": city if city in GEORGIAN_CITIES else "",
        "q": params.get("q", "").strip()[:60],
        "capacity": to_int(params.get("capacity")),
        "start_year": to_int(params.get("start_year")),
        "end_year": to_int(params.get("end_year")),
        "min_price": to_decimal(params.get("min_price")),
        "max_price": to_decimal(params.get("max_price")),
        "sort": sort if sort in _SORT_FIELDS else "",
    }


def filter_cars(filters):
    cars = Car.objects.select_related("owner")
    if filters["brand"]:
        cars = cars.filter(brand=filters["brand"])
    if filters["city"]:
        cars = cars.filter(city=filters["city"])
    if filters["q"]:
        cars = cars.filter(Q(model__icontains=filters["q"]) | Q(brand__icontains=filters["q"]))
    if filters["capacity"]:
        cars = cars.filter(capacity=filters["capacity"])
    if filters["start_year"]:
        cars = cars.filter(year__gte=filters["start_year"])
    if filters["end_year"]:
        cars = cars.filter(year__lte=filters["end_year"])
    if filters["min_price"] is not None:
        cars = cars.filter(price__gte=filters["min_price"])
    if filters["max_price"] is not None:
        cars = cars.filter(price__lte=filters["max_price"])
    if filters["sort"]:
        cars = cars.order_by(*_SORT_FIELDS[filters["sort"]])
    return cars


def popular_cars(limit=4):
    return (Car.objects.select_related("owner")
            .annotate(score=Count("rentals", filter=Q(rentals__status=Rental.ACTIVE), distinct=True)
                      + Count("favorites", distinct=True))
            .order_by("-score", "?")[:limit])


def random_cars(limit=12, exclude=()):
    return Car.objects.select_related("owner").exclude(pk__in=[c.pk for c in exclude]).order_by("?")[:limit]


def similar_cars(car, limit=4):
    found = list(Car.objects.filter(city=car.city).exclude(pk=car.pk).order_by("?")[:limit])
    if len(found) < limit:
        skip = [car.pk] + [c.pk for c in found]
        found += list(Car.objects.filter(brand=car.brand).exclude(pk__in=skip).order_by("?")[:limit - len(found)])
    return found


def liked_ids(user):
    if not user.is_authenticated:
        return set()
    return set(Favorite.objects.filter(user=user).values_list("car_id", flat=True))


def page_window(current, total, around=1):
    pages = sorted({1, total, *range(max(1, current - around), min(total, current + around) + 1)})
    out, prev = [], 0
    for p in pages:
        if p - prev == 2:
            out.append(p - 1) 
        elif p - prev > 2:
            out.append(None)
        out.append(p)
        prev = p
    return out


def toggle_favorite(user, car):
    favorite, created = Favorite.objects.get_or_create(user=user, car=car)
    if not created:
        favorite.delete()
    return created


def notify(user, text):
    Notification.objects.create(user=user, text=text[:300])


@transaction.atomic
def create_rental(user, car, start, end):
    today = timezone.localdate()
    if car.owner_id == user.pk:
        raise RentalError("საკუთარი მანქანის დაქირავება შეუძლებელია.")
    if start < today:
        raise RentalError("დაწყების თარიღი არ შეიძლება იყოს წარსულში.")
    if end < start:
        raise RentalError("დასრულების თარიღი არ შეიძლება იყოს დაწყებამდე.")
    days = (end - start).days + 1
    if days > MAX_RENT_DAYS:
        raise RentalError(f"მაქსიმალური ქირაობის ვადაა {MAX_RENT_DAYS} დღე.")

    clash = (Rental.objects.filter(car=car, status=Rental.ACTIVE, start_date__lte=end, end_date__gte=start)
             .order_by("start_date").first())
    if clash:
        raise RentalError(f"მანქანა ამ პერიოდში დაკავებულია ({fmt_date(clash.start_date)} – {fmt_date(clash.end_date)}). "
                          "აირჩიეთ სხვა თარიღები.")

    rental = Rental.objects.create(user=user, car=car, start_date=start, end_date=end,
                                   price_per_day=car.price, total_price=car.price * days)
    notify(car.owner, f"{user.get_full_name()} ({user.phone}) იქირავებს თქვენს მანქანას {car.brand} {car.model}: "
                      f"{fmt_date(start)} – {fmt_date(end)} ({days} დღე).")
    return rental


@transaction.atomic
def cancel_rental(user, rental):
    if rental.user_id != user.pk:
        raise RentalError("ეს ქირაობა თქვენი არ არის.")
    if rental.status == Rental.CANCELLED:
        raise RentalError("ქირაობა უკვე გაუქმებულია.")
    if not rental.can_cancel:
        raise RentalError("ქირაობის გაუქმება შესაძლებელია მხოლოდ დაწყებამდე.")
    rental.status = Rental.CANCELLED
    rental.cancelled_at = timezone.now()
    rental.save(update_fields=["status", "cancelled_at"])
    car = rental.car
    notify(car.owner, f"{user.get_full_name()} ({user.phone}) გააუქმა ქირაობა: {car.brand} {car.model}, "
                      f"{fmt_date(rental.start_date)} – {fmt_date(rental.end_date)}.")
    return rental


def booked_periods(car):
    return car.rentals.filter(status=Rental.ACTIVE, end_date__gte=timezone.localdate()).order_by("start_date")
