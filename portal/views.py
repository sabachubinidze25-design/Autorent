import smtplib
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from users.forms import flatten_errors

from . import services
from .choices import BRANDS, GEORGIAN_CITIES, TRANSMISSIONS
from .forms import CarForm, RentForm
from .models import Car, Notification, Rental
from .services import RentalError


def _redirect_back(request, fallback, **kwargs):
    target = request.POST.get("next", "")
    if target and url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()}):
        return redirect(target)
    return redirect(fallback, **kwargs)


def _page(request, queryset, per_page=services.PAGE_SIZE):
    page = Paginator(queryset, per_page).get_page(request.GET.get("page"))
    return page, services.page_window(page.number, page.paginator.num_pages)


def _querystring(request):
    query = request.GET.copy()
    query.pop("page", None)
    return query.urlencode()


def home(request):
    popular = list(services.popular_cars())
    context = {
        "popular": popular,
        "random": services.random_cars(exclude=popular),
        "liked_ids": services.liked_ids(request.user),
    }
    return render(request, "home.html", context)


def car_list(request):
    filters = services.read_filters(request.GET)
    page, links = _page(request, services.filter_cars(filters))
    context = {
        "page": page,
        "cars": page.object_list,
        "page_links": links,
        "querystring": _querystring(request),
        "cities": GEORGIAN_CITIES,
        "brands": BRANDS,
        "sort_options": services.SORT_OPTIONS,
        "liked_ids": services.liked_ids(request.user),
        "filters": {k: ("" if v is None else v) for k, v in filters.items()},
        "has_filter": any(v not in (None, "") for v in filters.values()),
    }
    return render(request, "car_list.html", context)


def car_detail(request, car_id):
    car = get_object_or_404(Car.objects.select_related("owner"), pk=car_id)
    user = request.user
    rent_values = {}

    if request.method == "POST":
        if not user.is_authenticated:
            messages.info(request, "გასაგრძელებლად გაიარეთ ავტორიზაცია.")
            return redirect(f"/login/?next=/cars/{car_id}/")
        rent_values = request.POST
        form = RentForm(request.POST)
        if form.is_valid():
            try:
                rental = services.create_rental(user, car, form.cleaned_data["start_date"], form.cleaned_data["end_date"])
            except RentalError as exc:
                messages.error(request, str(exc))
            else:
                return redirect("rent_success", rental_id=rental.pk)
        else:
            for error in flatten_errors(form):
                messages.error(request, error.split(": ", 1)[-1])

    liked = services.liked_ids(user)
    today = timezone.localdate()
    context = {
        "car": car,
        "photos": car.photos,
        "is_owner": user.is_authenticated and car.owner_id == user.pk,
        "is_liked": car.pk in liked,
        "liked_ids": liked,
        "owner_phone": car.owner.phone,
        "price_table": [{"days": d, "total": services.money(car.price * d)} for d in services.PRICE_TABLE_DAYS],
        "similar": services.similar_cars(car),
        "booked": services.booked_periods(car),
        "today": today.isoformat(),
        "rent_values": rent_values,
    }
    return render(request, "car_detail.html", context)


@require_POST
@login_required
def like_car(request, car_id):
    car = get_object_or_404(Car, pk=car_id)
    if services.toggle_favorite(request.user, car):
        messages.success(request, "მანქანა დაემატა მოწონებულებში.")
    else:
        messages.info(request, "მანქანა ამოღებულია მოწონებულებიდან.")
    return _redirect_back(request, "car_detail", car_id=car_id)


@login_required
def add_car(request):
    form = CarForm()
    if request.method == "POST":
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.owner = request.user  
            car.save()
            messages.success(request, "თქვენი მანქანა გაქირავებისთვის განთავსებულია.")
            return redirect("car_detail", car_id=car.pk)
        for error in flatten_errors(form):
            messages.error(request, error)
    context = {"values": request.POST, "transmissions": TRANSMISSIONS, "cities": GEORGIAN_CITIES, "brands": BRANDS}
    return render(request, "add_car.html", context)


@login_required
def rental_detail(request, rental_id):
    rental = get_object_or_404(Rental.objects.select_related("car__owner", "user"), pk=rental_id, user=request.user)
    return render(request, "rent_success.html", {"rental": rental, "car": rental.car})


@require_POST
@login_required
def rental_cancel(request, rental_id):
    rental = get_object_or_404(Rental.objects.select_related("car__owner"), pk=rental_id, user=request.user)
    try:
        services.cancel_rental(request.user, rental)
    except RentalError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "ქირაობა გაუქმდა.")
    return _redirect_back(request, "profile")


@login_required
def profile(request):
    user = request.user
    liked = [f.car for f in user.favorites.select_related("car__owner")]
    context = {
        "rentals": user.rentals.select_related("car"),
        "liked": liked,
        "liked_ids": {c.pk for c in liked},
        "mine": user.cars.all(),
    }
    return render(request, "profile.html", context)


@login_required
def notifications(request):
    page, links = _page(request, request.user.notifications.all(), per_page=15)
    items = list(page.object_list)  # evaluate before marking as read, so new ones can be highlighted
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, "notifications.html", {"page": page, "items": items, "page_links": links,
                                                  "querystring": _querystring(request)})


SUPPORT_COOLDOWN_SECONDS = 60


def support(request):
    user = request.user
    values = {
        "name": user.get_full_name() if user.is_authenticated else "",
        "email": user.email if user.is_authenticated else "",
        "message": "",
    }

    if request.method == "POST":
        values = {k: request.POST.get(k, "").strip() for k in ("name", "email", "message")}

        if request.POST.get("website"):
            messages.success(request, "შეტყობინება გაიგზავნა. მადლობა!")
            return redirect("support")

        error = None
        try:
            validate_email(values["email"])
        except ValidationError:
            error = "შეიყვანეთ სწორი ელფოსტის მისამართი."
        if not values["name"]:
            error = "შეიყვანეთ თქვენი სახელი."
        elif len(values["message"]) < 10:
            error = "შეტყობინება ძალიან მოკლეა (მინიმუმ 10 სიმბოლო)."
        elif time.time() - request.session.get("support_sent_at", 0) < SUPPORT_COOLDOWN_SECONDS:
            error = "გთხოვთ, ცოტა ხანში სცადოთ ხელახლა."

        if error:
            messages.error(request, error)
        else:
            name = " ".join(values["name"].split())[:80]  
            phone = user.phone if user.is_authenticated else "-"
            body = (
                f"სახელი: {name}\n"
                f"ელფოსტა: {values['email']}\n"
                f"ტელეფონი (თუ ავტორიზებულია): {phone}\n\n"
                f"{values['message']}\n"
            )
            mail = EmailMessage(
                subject=f"AutoRent დახმარება: {name}",
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.SUPPORT_EMAIL],
                reply_to=[values["email"]],
            )
            try:
                mail.send(fail_silently=False)
            except (OSError, smtplib.SMTPException):
                messages.error(request, "გაგზავნა ვერ მოხერხდა. სცადეთ მოგვიანებით ან მოგვწერეთ პირდაპირ ელფოსტაზე.")
            else:
                request.session["support_sent_at"] = time.time()
                messages.success(request, "შეტყობინება გაიგზავნა. მადლობა, მალე გიპასუხებთ!")
                return redirect("support")

    return render(request, "support.html", {"values": values})


def page_not_found(request, exception=None):
    return render(request, "404.html", status=404)
