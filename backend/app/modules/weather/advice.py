"""
Persian weather labels and activity suitability for a single day.

Kept as pure functions so the provider can be swapped without rewriting copy.
WMO weather interpretation codes: https://open-meteo.com/en/docs
"""
from dataclasses import dataclass

from app.modules.weather.interfaces import WeatherObservation


@dataclass(frozen=True)
class WeatherAdvice:
    condition_label: str
    suitable: tuple[str, ...]
    unsuitable: tuple[str, ...]
    hint: str


_CODE_LABELS: dict[int, str] = {
    0: "آسمان صاف",
    1: "عمدتاً صاف",
    2: "نیمه‌ابری",
    3: "ابری",
    45: "مه",
    48: "مه یخی",
    51: "نم‌نم باران",
    53: "باران ریز",
    55: "باران ریز شدید",
    56: "نم‌نم یخ‌زده",
    57: "باران یخ‌زده",
    61: "باران ملایم",
    63: "باران",
    65: "باران شدید",
    66: "باران یخ‌زده",
    67: "باران یخ‌زده شدید",
    71: "برف ملایم",
    73: "برف",
    75: "برف شدید",
    77: "دانه‌های برف",
    80: "رگبار ملایم",
    81: "رگبار",
    82: "رگبار شدید",
    85: "رگبار برف",
    86: "رگبار برف شدید",
    95: "رعدوبرق",
    96: "رعدوبرق با تگرگ",
    99: "رعدوبرق شدید با تگرگ",
}

WALKING = "پیاده‌روی در بافت شهری و بازار"
OUTDOOR_SIGHTS = "بازدید فضای باز و عکاسی از جاذبه‌ها"
GARDENS = "گشت در باغ‌ها و محوطه‌های تاریخی"
HIKING = "کوهنوردی و طبیعت‌گردی طولانی"
BEACH = "ساحل، شنا و تفریحات آبی"
MUSEUMS = "موزه، بازار سرپوشیده و مکان‌های سرپوشیده"
FOOD = "کافه و رستوران"
NIGHT = "گشت عصرگاهی در شهر"
DRIVE = "رانندگی بین شهری"

HOT = "گشت طولانی زیر آفتاب ظهر"
COLD_LONG = "ایستادن طولانی در فضای باز بدون پوشش گرم"
WET_HIKE = "کوهنوردی و مسیرهای خاکی لغزنده"
STORM_OUT = "فعالیت فضای باز در رعدوبرق"
WINDY = "قایق، دوچرخه و فضای کاملاً باز در باد شدید"
ICY = "پیاده‌روی روی معابر یخ‌زده"


def condition_label(code: int) -> str:
    if code in _CODE_LABELS:
        return _CODE_LABELS[code]
    if 50 <= code <= 59:
        return "باران ریز"
    if 60 <= code <= 69:
        return "باران"
    if 70 <= code <= 79:
        return "برف"
    if 80 <= code <= 84:
        return "رگبار"
    if 95 <= code <= 99:
        return "رعدوبرق"
    return "وضعیت جوی نامشخص"


def advise(observation: WeatherObservation) -> WeatherAdvice:
    code = observation.weather_code
    tmin = observation.temp_min_c
    tmax = observation.temp_max_c
    precip = observation.precipitation_probability or 0
    wind = observation.wind_kmh or 0
    wet = code in {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82} or precip >= 50
    snow = code in {71, 73, 75, 77, 85, 86}
    storm = code >= 95
    fog = code in {45, 48}
    hot = tmax >= 35
    cold = tmin <= 5
    windy = wind >= 40
    mild = 12 <= tmax <= 32 and not wet and not snow and not storm

    suitable: list[str] = [MUSEUMS, FOOD]
    unsuitable: list[str] = []

    if storm:
        unsuitable.extend([STORM_OUT, HIKING, BEACH, OUTDOOR_SIGHTS])
        suitable = [MUSEUMS, FOOD]
        hint = "رعدوبرق است؛ برنامه‌های فضای باز را به سرپوشیده تغییر بده."
    elif snow:
        suitable.extend([WALKING])
        unsuitable.extend([BEACH, WET_HIKE, ICY])
        hint = "برفی است؛ مسیرهای کوتاه شهری بهتر از طبیعت‌گردی طولانی‌اند."
    elif wet:
        suitable.extend([WALKING])
        unsuitable.extend([HIKING, BEACH, WET_HIKE])
        hint = "احتمال بارش بالاست؛ چتر ببر و جاذبه‌های سرپوشیده را اولویت بده."
    elif hot:
        suitable.extend([MUSEUMS, FOOD, NIGHT])
        unsuitable.extend([HOT, HIKING, BEACH] if tmax >= 38 else [HOT, HIKING])
        hint = "هوا گرم است؛ بازدید فضای باز را به صبح زود یا غروب منتقل کن."
    elif cold:
        suitable.extend([WALKING, MUSEUMS])
        unsuitable.extend([BEACH, COLD_LONG])
        hint = "هوا سرد است؛ پوشش گرم لازم است و ایستادن طولانی در فضای باز سخت می‌شود."
    elif fog:
        suitable.extend([WALKING, GARDENS])
        unsuitable.extend([DRIVE, HIKING])
        hint = "مه دید را کم می‌کند؛ رانندگی بین‌شهری و مسیرهای کوهستانی احتیاط می‌خواهد."
    elif windy:
        suitable.extend([WALKING, OUTDOOR_SIGHTS, GARDENS])
        unsuitable.extend([WINDY, BEACH])
        hint = "باد شدید است؛ فضای باز کوتاه اشکال ندارد، تفریحات آبی را کنار بگذار."
    elif mild:
        suitable.extend([WALKING, OUTDOOR_SIGHTS, GARDENS, HIKING, NIGHT, DRIVE])
        if tmax >= 28:
            suitable.append(BEACH)
        unsuitable.extend([HOT] if tmax >= 30 else [])
        hint = "هوا برای گشت شهری و بازدید فضای باز مناسب است."
    else:
        suitable.extend([WALKING, OUTDOOR_SIGHTS, GARDENS])
        hint = "وضعیت معمولی است؛ با توجه به دمای هوا لباس مناسب انتخاب کن."

    if hot and BEACH not in unsuitable and tmax >= 36:
        unsuitable.append(BEACH)

    # Deduplicate while preserving order.
    seen_s: set[str] = set()
    seen_u: set[str] = set()
    suitable_out = tuple(item for item in suitable if not (item in seen_s or seen_s.add(item)))
    unsuitable_out = tuple(
        item for item in unsuitable if item not in suitable_out and not (item in seen_u or seen_u.add(item))
    )
    return WeatherAdvice(
        condition_label=condition_label(code),
        suitable=suitable_out,
        unsuitable=unsuitable_out,
        hint=hint,
    )
