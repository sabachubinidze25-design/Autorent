import json
from functools import wraps

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from users.forms import LoginForm, RegisterForm
from users.models import ApiToken

from . import services
from .forms import CarForm, RentForm
from .models import Car, Rental
from .services import RentalError

MAX_PAGE_SIZE = 50


def error(message, status=400, **extra):
    return JsonResponse({"error": message, **extra}, status=status, json_dumps_params={"ensure_ascii": False})


def ok(data, status=200):
    return JsonResponse(data, status=status, safe=False, json_dumps_params={"ensure_ascii": False})


def form_errors(form):
    return error("მონაცემები არასწორია.", 400, fields={k: [str(e) for e in v] for k, v in form.errors.items()})


def api(*methods, auth=False):
    
    def decorator(view):
        @csrf_exempt
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.method not in methods:
                return error("მეთოდი დაუშვებელია.", 405)

            request.api_user = None
            header = request.headers.get("Authorization", "")
            if header.lower().startswith(("token ", "bearer ")):
                token = ApiToken.objects.select_related("user").filter(key=header.split(None, 1)[1].strip()).first()
                if token and token.user.is_active:
                    request.api_user = token.user
            if auth and request.api_user is None:
                return error("საჭიროა ავტორიზაცია (Authorization: Token <გასაღები>).", 401)

            request.data = request.POST
            if request.content_type == "application/json" and request.body:
                try:
                    body = json.loads(request.body)
                except ValueError:
                    return error("არასწორი JSON.")
                if not isinstance(body, dict):
                    return error("JSON უნდა იყოს ობიექტი.")
                request.data = body
            return view(request, *args, **kwargs)

        return wrapper

    return decorator


def car_json(request, car):
    def url(f):
        return request.build_absolute_uri(f.url) if f else None

    return {
        "id": car.pk, "brand": car.brand, "model": car.model, "year": car.year,
        "price": float(car.price), "capacity": car.capacity, "fuel_capacity": float(car.fuel_capacity),
        "transmission": car.transmission, "city": car.city,
        "images": [url(car.image1), url(car.image2), url(car.image3)],
        "owner_phone": car.owner.phone,
        "url": request.build_absolute_uri(reverse("api_car", args=[car.pk])),
    }


def rental_json(rental):
    return {
        "id": rental.pk, "car_id": rental.car_id, "car": f"{rental.car.brand} {rental.car.model}",
        "city": rental.car.city, "start_date": rental.start_date.isoformat(), "end_date": rental.end_date.isoformat(),
        "days": rental.days, "price_per_day": float(rental.price_per_day), "total_price": float(rental.total_price),
        "status": rental.status, "phase": rental.phase, "can_cancel": rental.can_cancel,
    }


def paged(request, queryset, serialize, default_size=services.PAGE_SIZE):
    try:
        size = min(max(int(request.GET.get("page_size", default_size)), 1), MAX_PAGE_SIZE)
    except ValueError:
        size = default_size
    paginator = Paginator(queryset, size)
    page = paginator.get_page(request.GET.get("page"))
    return ok({
        "count": paginator.count, "page": page.number, "page_size": size,
        "total_pages": paginator.num_pages,
        "has_next": page.has_next(), "has_previous": page.has_previous(),
        "results": [serialize(x) for x in page.object_list],
    })


@api("GET")
def index(request):
    def link(path):
        return request.build_absolute_uri(path)

    return ok({
        "name": "AutoRent API",
        "auth": "POST /api/login/ returns a token; send it as 'Authorization: Token <token>'",
        "endpoints": {
            "POST /api/register/": link("/api/register/"),
            "POST /api/login/": link("/api/login/"),
            "GET /api/me/": link("/api/me/"),
            "GET|POST /api/cars/": link("/api/cars/"),
            "GET /api/cars/<id>/": link("/api/cars/1/"),
            "POST /api/cars/<id>/like/": link("/api/cars/1/like/"),
            "POST /api/cars/<id>/rent/": link("/api/cars/1/rent/"),
            "GET /api/rentals/": link("/api/rentals/"),
            "POST /api/rentals/<id>/cancel/": link("/api/rentals/1/cancel/"),
            "GET /api/favorites/": link("/api/favorites/"),
            "GET /api/notifications/": link("/api/notifications/"),
        },
    })


@api("POST")
def register(request):
    form = RegisterForm(request.data)
    if not form.is_valid():
        return form_errors(form)
    user = form.save()
    return ok({"id": user.pk, "phone": user.phone}, 201)


@api("POST")
def login(request):
    form = LoginForm(request.data)
    if not form.is_valid():
        return form_errors(form)
    token, _ = ApiToken.objects.get_or_create(user=form.user)
    return ok({"token": token.key, "user": user_json(form.user)})


def user_json(user):
    return {"id": user.pk, "first_name": user.first_name, "last_name": user.last_name,
            "phone": user.phone, "email": user.email}


@api("GET", auth=True)
def me(request):
    return ok(user_json(request.api_user))


@api("GET", "POST")
def cars(request):
    if request.method == "POST":
        if request.api_user is None:
            return error("საჭიროა ავტორიზაცია (Authorization: Token <გასაღები>).", 401)
        form = CarForm(request.POST, request.FILES)  # photos need multipart/form-data
        if not form.is_valid():
            return form_errors(form)
        car = form.save(commit=False)
        car.owner = request.api_user
        car.save()
        return ok(car_json(request, car), 201)

    filters = services.read_filters(request.GET)
    return paged(request, services.filter_cars(filters), lambda c: car_json(request, c))


@api("GET")
def car(request, car_id):
    return ok(car_json(request, get_object_or_404(Car.objects.select_related("owner"), pk=car_id)))


@api("POST", auth=True)
def like(request, car_id):
    """Toggles: first call likes the car, the second one removes the like."""
    liked = services.toggle_favorite(request.api_user, get_object_or_404(Car, pk=car_id))
    return ok({"car_id": car_id, "liked": liked})


@api("POST", auth=True)
def rent(request, car_id):
    car = get_object_or_404(Car.objects.select_related("owner"), pk=car_id)
    form = RentForm(request.data)
    if not form.is_valid():
        return form_errors(form)
    try:
        rental = services.create_rental(request.api_user, car, form.cleaned_data["start_date"],
                                        form.cleaned_data["end_date"])
    except RentalError as exc:
        return error(str(exc), 409)
    return ok(rental_json(rental), 201)


@api("GET", auth=True)
def rentals(request):
    return paged(request, request.api_user.rentals.select_related("car"), rental_json)


@api("POST", auth=True)
def rental_cancel(request, rental_id):
    rental = get_object_or_404(Rental.objects.select_related("car__owner"), pk=rental_id, user=request.api_user)
    try:
        services.cancel_rental(request.api_user, rental)
    except RentalError as exc:
        return error(str(exc), 409)
    return ok(rental_json(rental))


@api("GET", auth=True)
def favorites(request):
    qs = Car.objects.select_related("owner").filter(favorites__user=request.api_user).order_by("-favorites__created_at")
    return paged(request, qs, lambda c: car_json(request, c))


@api("GET", auth=True)
def notifications(request):
    return paged(request, request.api_user.notifications.all(), lambda n: {
        "id": n.pk, "text": n.text, "is_read": n.is_read, "created_at": n.created_at.isoformat()})
