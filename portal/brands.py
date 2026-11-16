import re
import unicodedata

_BRANDS = [
    "Abarth", "Acura", "Aixam", "Alfa Romeo", "Alpine", "Aston Martin", "Audi", "Austin",
    "Bentley", "BMW", "Brilliance", "Bugatti", "Buick", "BYD",
    "Cadillac", "Changan", "Chery", "Chevrolet", "Chrysler", "Citroen", "Cupra",
    "Dacia", "Daewoo", "Daihatsu", "Datsun", "Dodge", "DS",
    "Ferrari", "Fiat", "Fisker", "Ford",
    "GAZ", "Geely", "Genesis", "GMC", "Great Wall",
    "Haval", "Honda", "Hummer", "Hyundai",
    "Infiniti", "Isuzu", "Iveco",
    "Jaguar", "Jeep",
    "Kia", "Koenigsegg",
    "Lada", "Lamborghini", "Lancia", "Land Rover", "Lexus", "Lincoln", "Lotus", "Lucid", "Lynk & Co",
    "Mahindra", "Maserati", "Maybach", "Mazda", "McLaren", "Mercedes-Benz", "Mercury", "MG", "Mini",
    "Mitsubishi",
    "Nio", "Nissan",
    "Opel",
    "Pagani", "Peugeot", "Plymouth", "Polestar", "Pontiac", "Porsche",
    "RAM", "Renault", "Rivian", "Rolls-Royce", "Rover",
    "Saab", "SEAT", "Skoda", "Smart", "SsangYong", "Subaru", "Suzuki",
    "Tesla", "Toyota",
    "UAZ",
    "VAZ", "Volkswagen", "Volvo",
    "Xpeng",
    "ZAZ", "Zeekr",
]


def _sort_key(name):
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return plain.casefold()


BRANDS = sorted(set(_BRANDS), key=_sort_key)


def _normal(name):
    return re.sub(r"[^a-z0-9]", "", _sort_key(name or ""))


def same_brand(chosen, stored):
    a, b = _normal(chosen), _normal(stored)
    if not a or not b:
        return False
    if a == b:
        return True
    short, long_ = sorted((a, b), key=len)
    return len(short) >= 5 and long_.startswith(short)
