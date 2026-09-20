"""
Demo catalog of lodging and dining for the MVP.

These records are intentionally synthetic (prices, menus, amenities) so the
product can be designed and demoed before a paid hospitality API exists.
Seed code persists them as `seed:{kind}:...` rows and will refresh fees /
catalog JSON on each startup.
"""
from __future__ import annotations

HOTEL_IMAGES = (
    "Abbasi Hotel Isfahan.jpg",
    "Azadi Hotel Tehran.jpg",
    "Espinas Palace Hotel.jpg",
)
FOOD_IMAGES = (
    "Chelow kabab.jpg",
    "Iranian cuisine.jpg",
    "Ghormeh sabzi.jpg",
)

_CITIES: dict[str, tuple[float, float]] = {
    "تهران": (35.6892, 51.3890),
    "شیراز": (29.5918, 52.5837),
    "اصفهان": (32.6546, 51.6675),
    "یزد": (31.8974, 54.3675),
    "مشهد": (36.2605, 59.6168),
    "تبریز": (38.0800, 46.2919),
    "کاشان": (33.9850, 51.4100),
    "رشت": (37.2808, 49.5832),
    "کرمان": (30.2839, 57.0834),
    "همدان": (34.7992, 48.5146),
    "قم": (34.6401, 50.8764),
    "کرمانشاه": (34.3142, 47.0650),
}


def _xy(city: str, dlat: float, dlng: float) -> tuple[float, float]:
    lat, lng = _CITIES[city]
    return round(lat + dlat, 4), round(lng + dlng, 4)


def _rooms(*pairs: tuple[str, int]) -> list[dict]:
    return [{"name": name, "price": price} for name, price in pairs]


def _menu(*rows: tuple[str, str, int]) -> list[dict]:
    return [{"section": section, "name": name, "price": price} for section, name, price in rows]


def _shift(menu: list[dict], delta: int) -> list[dict]:
    return [{**row, "price": max(50_000, int(row["price"]) + delta)} for row in menu]


KABAB_MENU = _menu(
    ("پیش‌غذا", "زیتون پرورده", 180_000),
    ("پیش‌غذا", "کشک بادمجان", 220_000),
    ("غذای اصلی", "چلوکباب کوبیده", 480_000),
    ("غذای اصلی", "چلوبرگ", 620_000),
    ("غذای اصلی", "جوجه کباب", 540_000),
    ("غذای اصلی", "چلوخورش قورمه", 390_000),
    ("نوشیدنی", "دوغ محلی", 70_000),
    ("دسر", "بستنی سنتی", 150_000),
)

TRADITIONAL_MENU = _menu(
    ("پیش‌غذا", "آش رشته", 210_000),
    ("پیش‌غذا", "نیمرو محلی", 160_000),
    ("غذای اصلی", "دیزی سنگی", 450_000),
    ("غذای اصلی", "فسنجان با مرغ", 580_000),
    ("غذای اصلی", "باقالی‌پلو با ماهیچه", 720_000),
    ("غذای اصلی", "ته‌چین مرغ", 510_000),
    ("نوشیدنی", "شربت بهارنارنج", 90_000),
    ("دسر", "فالوده شیرازی", 140_000),
)

GILAKI_MENU = _menu(
    ("پیش‌غذا", "میرزاقاسمی", 230_000),
    ("پیش‌غذا", "باقلاقاتوق", 200_000),
    ("غذای اصلی", "ماهی سفید کبابی", 690_000),
    ("غذای اصلی", "موتن‌جن", 560_000),
    ("غذای اصلی", "ترش‌واش", 410_000),
    ("نوشیدنی", "چای گیلانی", 60_000),
    ("دسر", "رشته‌خشکار", 170_000),
)

AZERI_MENU = _menu(
    ("پیش‌غذا", "کوفته تبریزی (نصف)", 280_000),
    ("غذای اصلی", "کوفته تبریزی", 520_000),
    ("غذای اصلی", "کباب بناب", 610_000),
    ("غذای اصلی", "آش دوغ", 240_000),
    ("نوشیدنی", "دوغ آذری", 80_000),
    ("دسر", "نوقا", 130_000),
)

CAFE_MENU = _menu(
    ("نوشیدنی", "اسپرسو", 120_000),
    ("نوشیدنی", "لاته", 160_000),
    ("نوشیدنی", "چای دبش", 90_000),
    ("نوشیدنی", "شیک شکلات", 210_000),
    ("میان‌وعده", "کیک روز", 180_000),
    ("میان‌وعده", "کروسان", 150_000),
    ("میان‌وعده", "املت", 220_000),
)

FAST_MENU = _menu(
    ("غذای اصلی", "برگر مخصوص", 390_000),
    ("غذای اصلی", "ساندویچ مرغ", 320_000),
    ("غذای اصلی", "پیتزا مخلوط", 480_000),
    ("پیش‌غذا", "سیب‌زمینی سرخ‌کرده", 140_000),
    ("نوشیدنی", "نوشابه", 50_000),
)

STAR_AMENITIES = {
    3: ["وای‌فای", "صبحانه", "پذیرش ۲۴ساعته"],
    4: ["وای‌فای", "صبحانه", "پارکینگ", "رستوران", "سرویس اتاق"],
    5: ["وای‌فای", "صبحانه بوفه", "استخر", "اسپا", "پارکینگ", "ترانسفر فرودگاه"],
}
GUESTHOUSE_AMENITIES = ["وای‌فای", "صبحانه خانگی", "حیاط مرکزی", "چای‌خانه"]


def _hotel(
    city: str,
    name: str,
    dlat: float,
    dlng: float,
    *,
    fee: int,
    stars: int,
    address: str,
    desc: str,
    category: str = "هتل",
    rooms: list[dict] | None = None,
    amenities: list[str] | None = None,
    image_index: int = 0,
) -> dict:
    lat, lng = _xy(city, dlat, dlng)
    nightly = fee
    room_list = rooms or _rooms(
        ("یک‌تخته", nightly),
        ("دو تخته", int(nightly * 1.25)),
        ("سوئیت", int(nightly * 1.8)),
    )
    return {
        "city": city,
        "name": name,
        "description": desc,
        "category": category,
        "lat": lat,
        "lng": lng,
        "fee": nightly,
        "hours": "شبانه‌روزی",
        "address": address,
        "image": HOTEL_IMAGES[image_index % len(HOTEL_IMAGES)],
        "catalog": {
            "is_demo": True,
            "stars": stars,
            "amenities": amenities or STAR_AMENITIES.get(stars, STAR_AMENITIES[4]),
            "rooms": room_list,
        },
    }


def _eatery(
    city: str,
    name: str,
    dlat: float,
    dlng: float,
    *,
    fee: int,
    address: str,
    desc: str,
    category: str,
    menu: list[dict],
    hours: str = "۱۲:۰۰ تا ۲۳:۰۰",
    image_index: int = 0,
) -> dict:
    lat, lng = _xy(city, dlat, dlng)
    return {
        "city": city,
        "name": name,
        "description": desc,
        "category": category,
        "lat": lat,
        "lng": lng,
        "fee": fee,
        "hours": hours,
        "address": address,
        "image": FOOD_IMAGES[image_index % len(FOOD_IMAGES)],
        "catalog": {"is_demo": True, "menu": menu},
    }


LODGING_PLACES: list[dict] = [
    _hotel("تهران", "هتل اسپیناس پالاس", 0.091, -0.024, fee=18_500_000, stars=5, address="سعادت‌آباد، میدان بهرود", desc="هتل پنج‌ستاره غرب تهران با چشم‌انداز شهر. نرخ‌ها نمونهٔ دمو هستند و برای برنامه‌ریزی بودجه گذاشته شده‌اند.", image_index=2),
    _hotel("تهران", "هتل پارسیان آزادی", 0.049, -0.008, fee=9_800_000, stars=5, address="بزرگراه چمران", desc="هتل بلندمرتبه نزدیک برج میلاد. مناسب گروه و سفر کاری؛ قیمت هر شب برای کل اتاق است.", image_index=1),
    _hotel("تهران", "هتل فردوسی", 0.004, 0.018, fee=4_200_000, stars=4, address="خیابان فردوسی", desc="هتل چهارستاره در مرکز شهر، دسترسی آسان به بازار و موزه‌ها.", image_index=0),
    _hotel("تهران", "اقامتگاه خانه باغ تجریش", 0.112, 0.012, fee=2_600_000, stars=3, address="تجریش، خیابان دربند", desc="اقامتگاه بوم‌گردی با فضای خانگی در شمال تهران.", category="اقامتگاه", amenities=GUESTHOUSE_AMENITIES, image_index=1),
    _hotel("شیراز", "هتل زندیه", 0.027, -0.038, fee=11_200_000, stars=5, address="خیابان فردوسی، نزدیک ارگ", desc="هتل پنج‌ستاره کنار مجموعه زندیه. اتاق‌ها برای دو نفر قیمت‌گذاری شده‌اند.", image_index=0),
    _hotel("شیراز", "هتل پارسه", 0.019, -0.039, fee=3_400_000, stars=3, address="نزدیک ارگ کریم‌خان", desc="اقامتگاه سنتی در بافت تاریخی شیراز با صبحانه محلی.", category="اقامتگاه", amenities=GUESTHOUSE_AMENITIES, image_index=2),
    _hotel("شیراز", "هتل چمران", 0.041, 0.008, fee=7_500_000, stars=4, address="بلوار چمران", desc="هتل چهارستاره با استخر و رستوران؛ مناسب اقامت چندشبه.", image_index=1),
    _hotel("شیراز", "خانه سنتی نیایش", 0.022, -0.021, fee=2_100_000, stars=3, address="محله سنگ‌سیاه", desc="اتاق‌های خشتی دور حیاط، آرام و نزدیک حافظیه.", category="اقامتگاه", amenities=GUESTHOUSE_AMENITIES),
    _hotel("اصفهان", "هتل عباسی", 0.0, 0.003, fee=14_800_000, stars=5, address="خیابان آمادگاه", desc="هتل تاریخی در کاروانسرای صفوی. نرخ دمو برای سوئیت و اتاق استاندارد.", image_index=0),
    _hotel("اصفهان", "هتل پارسیان کوثر", -0.017, 0.001, fee=8_400_000, stars=4, address="چهارباغ پایین", desc="هتل مشرف به زاینده‌رود؛ مناسب خانواده.", image_index=1),
    _hotel("اصفهان", "هتل سنتی نقش جهان", 0.004, 0.012, fee=3_900_000, stars=3, address="نزدیک میدان نقش جهان", desc="خانه تاریخی بازسازی‌شده با صبحانه در ایوان.", category="اقامتگاه", amenities=GUESTHOUSE_AMENITIES, image_index=2),
    _hotel("اصفهان", "مهمانسرا چهارباغ", -0.008, -0.006, fee=2_200_000, stars=3, address="چهارباغ عباسی", desc="گزینه اقتصادی نزدیک سی‌وسه‌پل.", category="اقامتگاه", amenities=GUESTHOUSE_AMENITIES),
    _hotel("یزد", "هتل سنتی مهر", -0.001, 0.001, fee=3_600_000, stars=4, address="بافت قدیم", desc="اقامتگاه خشتی در بافت تاریخی یزد با بادگیر و حیاط.", category="اقامتگاه", amenities=GUESTHOUSE_AMENITIES, image_index=0),
    _hotel("یزد", "هتل داد", -0.003, 0.003, fee=4_100_000, stars=4, address="خیابان امام خمینی", desc="خانه تاریخی تبدیل‌شده به هتل، مناسب سفر دونفره.", category="اقامتگاه", amenities=GUESTHOUSE_AMENITIES, image_index=1),
    _hotel("یزد", "کاروانسرای شرق", 0.008, -0.004, fee=2_400_000, stars=3, address="صفائیه", desc="اتاق‌های ساده با صبحانه یزدی.", category="اقامتگاه", amenities=GUESTHOUSE_AMENITIES, image_index=2),
    _hotel("مشهد", "هتل قصر طلایی", 0.026, -0.009, fee=12_500_000, stars=5, address="خیابان امام رضا", desc="هتل لوکس نزدیک حرم. نرخ هر شب برای اتاق دو تخته است.", image_index=2),
    _hotel("مشهد", "هتل درویشی", 0.018, -0.004, fee=9_200_000, stars=5, address="خیابان امام رضا", desc="هتل پنج‌ستاره زیارتی با ترانسفر به حرم.", image_index=0),
    _hotel("مشهد", "هتل آپارتمان رضوی", 0.012, 0.006, fee=3_300_000, stars=3, address="خیابان شیرازی", desc="سوئیت خانوادگی اقتصادی نزدیک حرم.", category="آپارتمان", amenities=["وای‌فای", "آشپزخانه", "پذیرش ۲۴ساعته"], image_index=1),
    _hotel("تبریز", "هتل پارس ائل‌گلی", -0.078, 0.074, fee=10_600_000, stars=5, address="ائل‌گلی", desc="هتل پنج‌ستاره کنار ائل‌گلی با رستوران و فضای سبز.", image_index=0),
    _hotel("تبریز", "هتل شهریار", 0.004, 0.006, fee=5_100_000, stars=4, address="مرکز شهر", desc="هتل چهارستاره با دسترسی به بازار تبریز.", image_index=1),
    _hotel("تبریز", "اقامتگاه خانه بهار", -0.006, -0.008, fee=2_000_000, stars=3, address="محله مقصودیه", desc="خانه قدیمی با اتاق‌های چوبی و صبحانه محلی.", category="اقامتگاه", amenities=GUESTHOUSE_AMENITIES),
    _hotel("کاشان", "هتل سنتی مانگشت", -0.006, 0.033, fee=3_800_000, stars=4, address="بافت تاریخی", desc="خانه تاریخی قاجاری با حوض‌خانه؛ نرخ دمو برای اتاق دو تخته.", category="اقامتگاه", amenities=GUESTHOUSE_AMENITIES, image_index=0),
    _hotel("کاشان", "خانه منوچهری", -0.008, 0.028, fee=4_500_000, stars=4, address="محله سلطان امیراحمد", desc="بوتیک‌هتل در خانه اعیانی کاشان.", category="اقامتگاه", amenities=GUESTHOUSE_AMENITIES, image_index=2),
    _hotel("رشت", "هتل کادوس", 0.0, 0.0, fee=4_800_000, stars=4, address="میدان شهرداری", desc="هتل شناخته‌شده مرکز رشت، نزدیک بازار و میدان شهرداری.", image_index=1),
    _hotel("رشت", "اقامتگاه گیل‌خانه", 0.012, -0.01, fee=2_300_000, stars=3, address="گلسار", desc="اقامتگاه مدرن با صبحانه گیلکی.", category="اقامتگاه", amenities=GUESTHOUSE_AMENITIES),
    _hotel("کرمان", "هتل پارس کرمان", 0.006, 0.004, fee=5_400_000, stars=4, address="بلوار جمهوری", desc="هتل چهارستاره مناسب توقف بین راهی کویر.", image_index=0),
    _hotel("کرمان", "اقامتگاه گنجعلی", -0.004, -0.002, fee=2_500_000, stars=3, address="نزدیک بازار گنجعلی‌خان", desc="اتاق سنتی نزدیک مجموعه گنجعلی‌خان.", category="اقامتگاه", amenities=GUESTHOUSE_AMENITIES),
    _hotel("همدان", "هتل باباطاهر", 0.002, 0.008, fee=3_700_000, stars=4, address="میدان امام", desc="هتل مرکز همدان با دسترسی به گنجنامه.", image_index=1),
    _hotel("همدان", "اقامتگاه الوند", 0.018, -0.012, fee=1_900_000, stars=3, address="جاده گنجنامه", desc="اقامتگاه کوهپایه‌ای نزدیک گنجنامه.", category="اقامتگاه", amenities=GUESTHOUSE_AMENITIES),
    _hotel("قم", "هتل کریمه", 0.006, 0.004, fee=4_400_000, stars=4, address="نزدیک حرم", desc="هتل زیارتی با اتاق خانوادگی.", image_index=2),
    _hotel("کرمانشاه", "هتل پارسیان کرمانشاه", 0.01, 0.006, fee=4_900_000, stars=4, address="بلوار طاق‌بستان", desc="هتل نزدیک طاق بستان؛ مناسب سفر غرب کشور.", image_index=0),
]


DINING_PLACES: list[dict] = [
    _eatery("تهران", "رستوران نایب", 0.011, 0.017, fee=520_000, address="خیابان ولیعصر", desc="چلوکباب کلاسیک تهران. مبلغ کارت، هزینه تقریبی یک وعده برای هر نفر است.", category="رستوران", menu=KABAB_MENU, image_index=0),
    _eatery("تهران", "کافه نادری", 0.006, 0.032, fee=280_000, address="خیابان جمهوری", desc="کافه تاریخی با کیک و قهوه. قیمت‌ها نمونهٔ دمو هستند.", category="کافه", menu=CAFE_MENU, hours="۸:۰۰ تا ۲۲:۰۰", image_index=1),
    _eatery("تهران", "رستوران شرف‌الاسلامی", -0.008, 0.02, fee=610_000, address="خیابان سی‌تیر", desc="غذای ایرانی کامل در مرکز تهران؛ مناسب ناهار بین موزه‌ها.", category="رستوران", menu=_shift(TRADITIONAL_MENU, 40_000), image_index=2),
    _eatery("تهران", "کافه ویونا تجریش", 0.11, 0.01, fee=240_000, address="تجریش", desc="کافه زنجیره‌ای با صبحانه و نوشیدنی.", category="کافه", menu=_shift(CAFE_MENU, 20_000), hours="۸:۰۰ تا ۲۳:۰۰"),
    _eatery("تهران", "برگر باکس", 0.02, -0.01, fee=360_000, address="ونک", desc="فست‌فود برای شام سریع بعد از بازدید شهری.", category="فست‌فود", menu=FAST_MENU, hours="۱۲:۰۰ تا ۰۰:۳۰"),
    _eatery("شیراز", "رستوران شاطرعباس", 0.035, -0.027, fee=490_000, address="بلوار کریمخان زند", desc="غذای ایرانی نزدیک حافظیه. یک وعده متوسط برای هر نفر در بودجه حساب می‌شود.", category="رستوران", menu=_shift(TRADITIONAL_MENU, -20_000), image_index=1),
    _eatery("شیراز", "فالوده بستنی دادلی", 0.03, -0.018, fee=160_000, address="نزدیک حافظیه", desc="دسر شیرازی؛ مناسب عصرانه.", category="کافه", menu=_menu(("دسر", "فالوده شیرازی", 140_000), ("دسر", "بستنی سنتی", 160_000), ("نوشیدنی", "شربت خاکشیر", 70_000)), hours="۱۱:۰۰ تا ۲۴:۰۰", image_index=2),
    _eatery("شیراز", "کافه کتاب زمان", 0.02, 0.004, fee=220_000, address="خیابان لطفعلی‌خان زند", desc="کافه آرام برای صبحانه و قهوه.", category="کافه", menu=CAFE_MENU, hours="۹:۰۰ تا ۲۲:۰۰"),
    _eatery("شیراز", "کباب‌سرای زندیه", 0.016, -0.04, fee=450_000, address="نزدیک ارگ", desc="کباب تازه و دوغ محلی.", category="رستوران", menu=_shift(KABAB_MENU, -30_000)),
    _eatery("اصفهان", "رستوران شهرزاد", 0.0, 0.0, fee=470_000, address="چهارباغ عباسی", desc="غذای سنتی مشرف به چهارباغ. هزینه کارت معادل یک پرس اصلی به‌علاوه نوشیدنی است.", category="رستوران", menu=_shift(TRADITIONAL_MENU, 10_000), image_index=0),
    _eatery("اصفهان", "بریان اصفهان", 0.008, 0.01, fee=380_000, address="خیابان عبدالرزاق", desc="بریان معروف اصفهان؛ یک پرس برای هر نفر.", category="رستوران", menu=_menu(("غذای اصلی", "بریان مخصوص", 380_000), ("غذای اصلی", "بریان با دوغ", 420_000), ("نوشیدنی", "دوغ", 70_000)), image_index=1),
    _eatery("اصفهان", "کافه نقش جهان", 0.004, 0.012, fee=210_000, address="میدان امام", desc="قهوه و میان‌وعده با دید به میدان.", category="کافه", menu=_shift(CAFE_MENU, -10_000), hours="۹:۰۰ تا ۲۳:۰۰"),
    _eatery("اصفهان", "فست‌فود سی‌وسه", -0.01, 0.0, fee=340_000, address="چهارباغ پایین", desc="شام سریع نزدیک پل.", category="فست‌فود", menu=_shift(FAST_MENU, 20_000), hours="۱۲:۰۰ تا ۱:۰۰"),
    _eatery("یزد", "رستوران سنتی ترمه‌چی", -0.002, 0.002, fee=430_000, address="بافت قدیم", desc="غذای یزدی در حیاط خشتی. قیمت‌ها ساختگی و فقط برای دموی بودجه هستند.", category="رستوران", menu=_shift(TRADITIONAL_MENU, -40_000), image_index=2),
    _eatery("یزد", "کافه فهادان", 0.0, 0.004, fee=190_000, address="فهادان", desc="چای و شیرینی یزدی در بافت تاریخی.", category="کافه", menu=_menu(("نوشیدنی", "چای کوزه‌ای", 80_000), ("میان‌وعده", "قطب یزدی", 120_000), ("میان‌وعده", "باقلوا", 150_000), ("نوشیدنی", "شربت به‌لیمو", 90_000)), hours="۹:۰۰ تا ۲۲:۰۰"),
    _eatery("یزد", "آش و حلیم سنتی", 0.006, -0.002, fee=180_000, address="امیرچخماق", desc="صبحانه محلی؛ آش و حلیم.", category="رستوران", menu=_menu(("صبحانه", "حلیم", 180_000), ("صبحانه", "آش شولی", 160_000), ("نوشیدنی", "چای", 50_000)), hours="۷:۰۰ تا ۱۳:۰۰"),
    _eatery("مشهد", "رستوران پدیدار", 0.037, -0.011, fee=540_000, address="خیابان احمدآباد", desc="چلوگوشت مشهدی. یک وعده کامل برای هر نفر در بودجه ضرب می‌شود.", category="رستوران", menu=_shift(KABAB_MENU, 50_000), image_index=0),
    _eatery("مشهد", "شله مشهدی", 0.022, 0.0, fee=220_000, address="نزدیک حرم", desc="شله و حلیم زیارتی.", category="رستوران", menu=_menu(("غذای اصلی", "شله", 220_000), ("غذای اصلی", "حلیم", 200_000), ("نوشیدنی", "چای", 50_000)), hours="۱۱:۰۰ تا ۲۴:۰۰"),
    _eatery("مشهد", "کافه کتاب آفتاب", 0.01, 0.008, fee=230_000, address="پارک ملت", desc="کافه برای استراحت بین زیارت.", category="کافه", menu=CAFE_MENU, hours="۱۰:۰۰ تا ۲۳:۰۰"),
    _eatery("تبریز", "رستوران حاج علی", -0.004, -0.001, fee=500_000, address="نزدیک بازار", desc="کوفته تبریزی و غذای آذری. نرخ‌ها نمونهٔ دمو هستند.", category="رستوران", menu=AZERI_MENU, hours="۱۲:۰۰ تا ۲۲:۰۰", image_index=1),
    _eatery("تبریز", "کافه ائل‌گلی", -0.077, 0.072, fee=200_000, address="ائل‌گلی", desc="نوشیدنی با دید باغ.", category="کافه", menu=_shift(CAFE_MENU, 10_000), hours="۹:۰۰ تا ۲۳:۰۰"),
    _eatery("تبریز", "کباب بناب", 0.002, 0.01, fee=470_000, address="خیابان تربیت", desc="کباب بناب و نان محلی.", category="رستوران", menu=_shift(KABAB_MENU, 20_000)),
    _eatery("کاشان", "رستوران سنتی مانگشت", -0.006, 0.033, fee=410_000, address="بافت تاریخی", desc="غذای ایرانی در خانه تاریخی؛ مناسب ناهار بعد از خانه بروجردی‌ها.", category="رستوران", menu=_shift(TRADITIONAL_MENU, -30_000), hours="۱۲:۰۰ تا ۲۲:۰۰", image_index=2),
    _eatery("کاشان", "کافه حوض‌خانه", -0.007, 0.03, fee=180_000, address="سلطان امیراحمد", desc="چای و گلاب در حیاط.", category="کافه", menu=_menu(("نوشیدنی", "گلاب و زعفران", 90_000), ("نوشیدنی", "چای", 60_000), ("میان‌وعده", "باقلوا", 140_000)), hours="۹:۰۰ تا ۲۲:۰۰"),
    _eatery("رشت", "رستوران گیلانه", -0.004, 0.005, fee=480_000, address="خیابان مطهری", desc="غذای گیلکی. مبلغ تقریبی یک پرس ماهی یا خورش برای هر نفر است.", category="رستوران", menu=GILAKI_MENU, image_index=0),
    _eatery("رشت", "کافه گلسار", 0.014, -0.008, fee=210_000, address="گلسار", desc="قهوه و کیک در گلسار.", category="کافه", menu=CAFE_MENU, hours="۹:۰۰ تا ۲۴:۰۰"),
    _eatery("رشت", "فست‌فود کاسپین", 0.002, 0.004, fee=330_000, address="میدان شهرداری", desc="شام سریع مرکز شهر.", category="فست‌فود", menu=FAST_MENU, hours="۱۲:۰۰ تا ۱:۰۰"),
    _eatery("کرمان", "رستوران گنجعلی‌خان", -0.004, -0.002, fee=390_000, address="بازار بزرگ", desc="غذای ایرانی کنار مجموعه تاریخی.", category="رستوران", menu=_shift(TRADITIONAL_MENU, -50_000)),
    _eatery("کرمان", "کافه بازار", -0.003, 0.0, fee=170_000, address="بازار", desc="چای و قهوه در بازار.", category="کافه", menu=_shift(CAFE_MENU, -30_000), hours="۹:۰۰ تا ۲۱:۰۰"),
    _eatery("همدان", "رستوران بوعلی", -0.008, -0.001, fee=400_000, address="میدان بوعلی", desc="کباب و غذای ایرانی نزدیک آرامگاه.", category="رستوران", menu=_shift(KABAB_MENU, -40_000)),
    _eatery("همدان", "کافه گنجنامه", 0.03, -0.07, fee=200_000, address="جاده گنجنامه", desc="میان‌وعده بعد از گنجنامه.", category="کافه", menu=CAFE_MENU, hours="۱۰:۰۰ تا ۲۲:۰۰"),
    _eatery("قم", "رستوران رضوی", 0.004, 0.002, fee=360_000, address="نزدیک حرم", desc="چلوکباب زیارتی.", category="رستوران", menu=_shift(KABAB_MENU, -60_000)),
    _eatery("کرمانشاه", "رستوران طاق‌بستان", 0.07, 0.06, fee=420_000, address="طاق بستان", desc="غذای کردی و کباب نزدیک محوطه.", category="رستوران", menu=_shift(KABAB_MENU, -20_000)),
]
