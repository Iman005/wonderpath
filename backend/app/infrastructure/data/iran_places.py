"""
Well-known Iranian attractions with Wikimedia Commons thumbnails.

image is a Commons filename (not a full URL). Seed code turns it into a
Special:FilePath URL so the frontend can render a photo without a live
Neshan key.
"""

TOURIST_PLACES: list[dict] = [
    # تهران
    {"city": "تهران", "name": "کاخ گلستان", "description": "کاخ تاریخی دوره قاجار، ثبت میراث جهانی یونسکو.", "category": "تاریخی", "lat": 35.6803, "lng": 51.4195, "fee": 500000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "میدان ارگ، خیابان ۱۵ خرداد", "image": "Golestan Palace.jpg"},
    {"city": "تهران", "name": "برج میلاد", "description": "بلندترین برج مخابراتی ایران با دید ۳۶۰ درجه.", "category": "دیدنی شهری", "lat": 35.7448, "lng": 51.3753, "fee": 800000, "hours": "۹:۰۰ تا ۲۳:۰۰", "address": "بزرگراه همت", "image": "Milad Tower at night.jpg"},
    {"city": "تهران", "name": "بازار بزرگ تهران", "description": "یکی از بزرگ‌ترین بازارهای سرپوشیده خاورمیانه.", "category": "بازار", "lat": 35.6742, "lng": 51.4173, "fee": None, "hours": "۹:۰۰ تا ۲۰:۰۰", "address": "خیابان ۱۵ خرداد", "image": "Tehran Grand Bazaar.jpg"},
    {"city": "تهران", "name": "موزه ملی ایران", "description": "مهم‌ترین موزه باستان‌شناسی کشور.", "category": "موزه", "lat": 35.6872, "lng": 51.4165, "fee": 400000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "خیابان امام خمینی", "image": "National Museum of Iran.jpg"},
    {"city": "تهران", "name": "کاخ سعدآباد", "description": "مجموعه کاخ‌های سلطنتی در دامنه توچال.", "category": "تاریخی", "lat": 35.8195, "lng": 51.4240, "fee": 600000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "میدان دربند", "image": "Saadabad Palace.jpg"},
    {"city": "تهران", "name": "برج آزادی", "description": "نماد مدرن تهران در ورودی غربی شهر.", "category": "دیدنی شهری", "lat": 35.6997, "lng": 51.3381, "fee": 200000, "hours": "۹:۰۰ تا ۱۹:۰۰", "address": "میدان آزادی", "image": "Azadi Tower 2015.jpg"},
    {"city": "تهران", "name": "دربند", "description": "مسیر کوهپیمایی و کافهٔ دامنه توچال در شمال تهران.", "category": "طبیعی", "lat": 35.8197, "lng": 51.4256, "fee": None, "hours": "شبانه‌روزی", "address": "میدان دربند", "image": "Darband Tehran.jpg"},
    {"city": "تهران", "name": "کاخ نیاوران", "description": "مجموعه کاخ پهلوی در باغ نیاوران.", "category": "تاریخی", "lat": 35.8117, "lng": 51.4728, "fee": 500000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "میدان نیاوران", "image": "Niavaran Palace.jpg"},
    {"city": "تهران", "name": "پارک ملت تهران", "description": "پارک بزرگ شمال تهران با دریاچه و مسیر پیاده‌روی.", "category": "طبیعی", "lat": 35.7786, "lng": 51.4119, "fee": None, "hours": "۶:۰۰ تا ۲۴:۰۰", "address": "بزرگراه نیایش", "image": "Mellat Park Tehran.jpg"},
    # شیراز / فارس
    {"city": "شیراز", "name": "مسجد نصیرالملک", "description": "مسجد صورتی، مشهور به نورهای رنگی صبحگاهی.", "category": "مذهبی-تاریخی", "lat": 29.6084, "lng": 52.5488, "fee": 300000, "hours": "۷:۳۰ تا ۱۰:۳۰", "address": "خیابان لطفعلی‌خان زند", "image": "Nasir ol molk mosque.jpg"},
    {"city": "شیراز", "name": "باغ ارم", "description": "باغ تاریخی ایرانی با کاخ قاجاری در میان آن.", "category": "باغ تاریخی", "lat": 29.6362, "lng": 52.5296, "fee": 400000, "hours": "۸:۰۰ تا ۱۸:۰۰", "address": "خیابان ارم", "image": "Eram Garden 1.jpg"},
    {"city": "شیراز", "name": "حافظیه", "description": "آرامگاه حافظ شیرازی و باغ پیرامون آن.", "category": "فرهنگی", "lat": 29.6254, "lng": 52.5585, "fee": 200000, "hours": "۸:۰۰ تا ۲۲:۰۰", "address": "میدان حافظیه", "image": "Tomb of Hafez.jpg"},
    {"city": "شیراز", "name": "سعدیه", "description": "آرامگاه سعدی در شمال شرق شیراز.", "category": "فرهنگی", "lat": 29.6225, "lng": 52.5822, "fee": 200000, "hours": "۸:۰۰ تا ۲۱:۰۰", "address": "خیابان بوستان", "image": "Tomb of Saadi.jpg"},
    {"city": "شیراز", "name": "شاهچراغ", "description": "حرم احمد بن موسی؛ مهم‌ترین زیارتگاه شیراز.", "category": "مذهبی", "lat": 29.6097, "lng": 52.5453, "fee": None, "hours": "شبانه‌روزی", "address": "خیابان احمدی", "image": "Shah Cheragh shrine.jpg"},
    {"city": "شیراز", "name": "ارگ کریم‌خان", "description": "ارگ زندیه در مرکز شیراز با برج‌های آجری.", "category": "تاریخی", "lat": 29.6175, "lng": 52.5447, "fee": 300000, "hours": "۸:۰۰ تا ۲۰:۰۰", "address": "میدان شهدا", "image": "Karim Khan Citadel.jpg"},
    {"city": "شیراز", "name": "بازار وکیل", "description": "بازار زندیه کنار حمام و مسجد وکیل.", "category": "بازار", "lat": 29.6153, "lng": 52.5456, "fee": None, "hours": "۹:۰۰ تا ۲۱:۰۰", "address": "خیابان طالقانی", "image": "Vakil Bazaar Shiraz.jpg"},
    {"city": "شیراز", "name": "نارنجستان قوام", "description": "خانه و باغ قاجاری قوام با آینه و نارنج.", "category": "تاریخی", "lat": 29.6078, "lng": 52.5511, "fee": 200000, "hours": "۸:۰۰ تا ۱۸:۰۰", "address": "خیابان لطفعلی‌خان زند", "image": "Qavam House Shiraz.jpg"},
    {"city": "شیراز", "name": "باغ دلگشا", "description": "باغ تاریخی با عمارت زندیه و نارنجستان.", "category": "باغ تاریخی", "lat": 29.6356, "lng": 52.5986, "fee": 150000, "hours": "۸:۰۰ تا ۲۰:۰۰", "address": "پای کوه شرقی", "image": "Delgosha Garden Shiraz.jpg"},
    {"city": "مرودشت", "name": "تخت جمشید", "description": "پایتخت باستانی هخامنشیان، میراث جهانی یونسکو.", "category": "باستانی", "lat": 29.9354, "lng": 52.8916, "fee": 1000000, "hours": "۸:۰۰ تا ۱۷:۰۰", "address": "مرودشت، استان فارس", "image": "Gate of all nations persepolis.jpg"},
    {"city": "پاسارگاد", "name": "آرامگاه کوروش", "description": "آرامگاه کوروش بزرگ در دشت پاسارگاد.", "category": "باستانی", "lat": 30.1939, "lng": 53.1672, "fee": 500000, "hours": "۸:۰۰ تا ۱۷:۰۰", "address": "پاسارگاد", "image": "Pasargad Tomb Cyrus3.jpg"},
    # اصفهان
    {"city": "اصفهان", "name": "میدان نقش جهان", "description": "میدان تاریخی ثبت یونسکو، قلب اصفهان.", "category": "تاریخی", "lat": 32.6575, "lng": 51.6776, "fee": None, "hours": "شبانه‌روزی", "address": "میدان امام", "image": "Naghsh-e-Jahan Square Isfahan.jpg"},
    {"city": "اصفهان", "name": "مسجد امام اصفهان", "description": "شاهکار معماری صفوی در ضلع جنوبی نقش جهان.", "category": "مذهبی-تاریخی", "lat": 32.6546, "lng": 51.6786, "fee": 400000, "hours": "۹:۰۰ تا ۱۷:۰۰", "address": "میدان نقش جهان", "image": "Shah Mosque Isfahan.jpg"},
    {"city": "اصفهان", "name": "کاخ عالی‌قاپو", "description": "کاخ شش‌طبقه صفوی مشرف به میدان.", "category": "تاریخی", "lat": 32.6574, "lng": 51.6763, "fee": 400000, "hours": "۹:۰۰ تا ۱۷:۰۰", "address": "میدان نقش جهان", "image": "Ali Qapu.jpg"},
    {"city": "اصفهان", "name": "پل خواجو", "description": "یکی از زیباترین پل‌های تاریخی ایران.", "category": "تاریخی", "lat": 32.6289, "lng": 51.6839, "fee": None, "hours": "شبانه‌روزی", "address": "پل خواجو", "image": "Khaju Bridge Isfahan.jpg"},
    {"city": "اصفهان", "name": "سی‌وسه‌پل", "description": "پل تاریخی زاینده‌رود با ۳۳ دهانه.", "category": "تاریخی", "lat": 32.6444, "lng": 51.6675, "fee": None, "hours": "شبانه‌روزی", "address": "خیابان چهارباغ پایین", "image": "Si-o-se Pol.jpg"},
    {"city": "اصفهان", "name": "کاخ چهل‌ستون اصفهان", "description": "کاخ صفوی با تالار آینه و باغ ایرانی.", "category": "تاریخی", "lat": 32.6572, "lng": 51.6678, "fee": 400000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "خیابان استانداری", "image": "Chehel Sotoun Isfahan.jpg"},
    {"city": "اصفهان", "name": "کلیسای وانک", "description": "کلیسای تاریخی ارامنه در جلفا.", "category": "مذهبی-تاریخی", "lat": 32.6350, "lng": 51.6561, "fee": 300000, "hours": "۸:۳۰ تا ۱۷:۳۰", "address": "جلفا", "image": "Vank Cathedral Isfahan.jpg"},
    {"city": "اصفهان", "name": "منارجنبان", "description": "آرامگاه با مناره‌هایی که با تکان یکی، دیگری هم می‌جنبد.", "category": "تاریخی", "lat": 32.6406, "lng": 51.5703, "fee": 200000, "hours": "۹:۰۰ تا ۱۷:۰۰", "address": "کارلادان", "image": "Monar Jonban.jpg"},
    {"city": "کاشان", "name": "خانه بروجردی‌ها", "description": "خانه تاریخی اعیانی دوره قاجار.", "category": "تاریخی", "lat": 33.9747, "lng": 51.4411, "fee": 300000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "محله سلطان امیراحمد", "image": "Borujerdiha house.jpg"},
    {"city": "کاشان", "name": "باغ فین", "description": "باغ ایرانی ثبت یونسکو با چشمه‌های کهن.", "category": "باغ تاریخی", "lat": 33.9464, "lng": 51.3725, "fee": 400000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "خیابان امیرکبیر", "image": "Fin Garden Kashan.jpg"},
    # مشهد
    {"city": "مشهد", "name": "حرم امام رضا (ع)", "description": "مهم‌ترین زیارتگاه شیعیان در ایران.", "category": "مذهبی", "lat": 36.2880, "lng": 59.6157, "fee": None, "hours": "شبانه‌روزی", "address": "حرم مطهر", "image": "Imam Reza shrine.jpg"},
    {"city": "مشهد", "name": "آرامگاه فردوسی", "description": "آرامگاه حکیم ابوالقاسم فردوسی در توس.", "category": "فرهنگی", "lat": 36.4864, "lng": 59.5181, "fee": 200000, "hours": "۸:۰۰ تا ۱۹:۰۰", "address": "توس", "image": "Ferdowsi mausoleum.jpg"},
    {"city": "مشهد", "name": "آرامگاه نادرشاه", "description": "آرامگاه نادرشاه افشار با موزه سلاح در باغ نادری.", "category": "فرهنگی", "lat": 36.2889, "lng": 59.6042, "fee": 200000, "hours": "۸:۰۰ تا ۱۸:۰۰", "address": "خیابان شیرازی", "image": "Nader Shah Mausoleum.jpg"},
    {"city": "مشهد", "name": "کوهسنگی", "description": "تپه و بوستان معروف جنوب مشهد با دید به شهر.", "category": "طبیعی", "lat": 36.2581, "lng": 59.5864, "fee": None, "hours": "شبانه‌روزی", "address": "کوهسنگی", "image": "Koohsangi Mashhad.jpg"},
    {"city": "نیشابور", "name": "آرامگاه خیام", "description": "آرامگاه ریاضی‌دان و شاعر در باغ امامزاده محروق.", "category": "فرهنگی", "lat": 36.1661, "lng": 58.8225, "fee": 150000, "hours": "۸:۰۰ تا ۲۰:۰۰", "address": "خیابان خیام", "image": "Omar Khayyam Tomb.jpg"},
    # یزد
    {"city": "یزد", "name": "بافت تاریخی یزد", "description": "بزرگ‌ترین بافت خشتی جهان، ثبت یونسکو.", "category": "تاریخی", "lat": 31.8974, "lng": 54.3675, "fee": None, "hours": "شبانه‌روزی", "address": "بافت قدیم", "image": "Yazd old city.jpg"},
    {"city": "یزد", "name": "آتشکده یزد", "description": "آتشکده زرتشتیان با آتش ۱۵۰۰ ساله.", "category": "مذهبی", "lat": 31.8856, "lng": 54.3708, "fee": 200000, "hours": "۸:۰۰ تا ۲۰:۰۰", "address": "خیابان آیت‌الله کاشانی", "image": "Yazd Fire Temple.jpg"},
    {"city": "یزد", "name": "برج خاموشان", "description": "دخمه‌های آیینی زرتشتیان در حاشیه شهر.", "category": "تاریخی-مذهبی", "lat": 31.8631, "lng": 54.3906, "fee": 200000, "hours": "۸:۰۰ تا ۱۹:۰۰", "address": "صفائیه", "image": "Towers of Silence Yazd.jpg"},
    {"city": "یزد", "name": "مجموعه امیرچخماق", "description": "تکیه و میدان تاریخی در مرکز یزد.", "category": "تاریخی", "lat": 31.8922, "lng": 54.3694, "fee": None, "hours": "شبانه‌روزی", "address": "میدان امیرچخماق", "image": "Amir Chakhmaq Complex.jpg"},
    # تبریز
    {"city": "تبریز", "name": "بازار تبریز", "description": "بزرگ‌ترین بازار سرپوشیده جهان، ثبت یونسکو.", "category": "بازار", "lat": 38.0808, "lng": 46.2928, "fee": None, "hours": "۹:۰۰ تا ۲۰:۰۰", "address": "بازار بزرگ", "image": "Tabriz Bazaar.jpg"},
    {"city": "تبریز", "name": "ارگ علیشاه", "description": "باقی‌مانده مسجد و ارگ ایلخانی.", "category": "تاریخی", "lat": 38.0736, "lng": 46.2936, "fee": None, "hours": "شبانه‌روزی", "address": "امام خمینی", "image": "Arg of Tabriz.jpg"},
    {"city": "تبریز", "name": "کاخ شهرداری تبریز", "description": "ساختمان تاریخی شهرداری با ساعت معروف.", "category": "تاریخی", "lat": 38.0739, "lng": 46.2958, "fee": 150000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "میدان ساعت", "image": "Tabriz Municipality Palace.jpg"},
    {"city": "تبریز", "name": "ائل‌گلی", "description": "استخر و عمارت صفوی-قاجاری در جنوب تبریز.", "category": "باغ تاریخی", "lat": 38.0028, "lng": 46.3656, "fee": None, "hours": "شبانه‌روزی", "address": "ائل‌گلی", "image": "El Goli Tabriz.jpg"},
    {"city": "تبریز", "name": "مسجد کبود", "description": "مسجد جهانشاه با کاشی فیروزه‌ای؛ فیروزه اسلام.", "category": "مذهبی-تاریخی", "lat": 38.0736, "lng": 46.3006, "fee": 150000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "خیابان امام خمینی", "image": "Blue Mosque Tabriz.jpg"},
    {"city": "تبریز", "name": "موزه آذربایجان", "description": "موزه باستان‌شناسی کنار مسجد کبود.", "category": "موزه", "lat": 38.0739, "lng": 46.3003, "fee": 200000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "خیابان امام خمینی", "image": "Azerbaijan Museum Tabriz.jpg"},
    {"city": "تبریز", "name": "خانه مشروطه تبریز", "description": "خانه قاجاری مرکز تجمع مشروطه‌خواهان تبریز.", "category": "تاریخی", "lat": 38.0814, "lng": 46.2911, "fee": 150000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "راسته کوچه", "image": "Constitution House of Tabriz.jpg"},
    {"city": "جلفا", "name": "کلیسای سنت استپانوس", "description": "کلیسای تاریخی ارمنی در کرانه ارس.", "category": "مذهبی-تاریخی", "lat": 38.9794, "lng": 45.4731, "fee": 300000, "hours": "۸:۰۰ تا ۱۷:۰۰", "address": "جلفا", "image": "Saint Stepanos Monastery.jpg"},
    # همدان
    {"city": "همدان", "name": "گنجنامه", "description": "کتیبه‌های هخامنشی و آبشار در دامنه الوند.", "category": "باستانی", "lat": 34.7606, "lng": 48.4383, "fee": None, "hours": "شبانه‌روزی", "address": "جاده گنجنامه", "image": "Ganjnameh inscriptions.jpg"},
    {"city": "همدان", "name": "آرامگاه بوعلی سینا", "description": "آرامگاه ابن‌سینا با معماری مدرن ایرانی.", "category": "فرهنگی", "lat": 34.7914, "lng": 48.5131, "fee": 150000, "hours": "۸:۰۰ تا ۲۰:۰۰", "address": "میدان بوعلی", "image": "Avicenna Mausoleum.jpg"},
    {"city": "همدان", "name": "تپه هگمتانه", "description": "محوطه باستانی پایتخت مادها.", "category": "باستانی", "lat": 34.8064, "lng": 48.5164, "fee": 200000, "hours": "۸:۰۰ تا ۱۸:۰۰", "address": "خیابان اکباتان", "image": "Ecbatana.jpg"},
    # کرمانشاه
    {"city": "کرمانشاه", "name": "طاق بستان", "description": "سنگ‌نگاره‌های ساسانی کنار چشمه.", "category": "باستانی", "lat": 34.3878, "lng": 47.1322, "fee": 300000, "hours": "۸:۰۰ تا ۲۰:۰۰", "address": "طاق بستان", "image": "Taq-e Bostan.jpg"},
    {"city": "کرمانشاه", "name": "بیستون", "description": "کتیبه داریوش بزرگ، ثبت یونسکو.", "category": "باستانی", "lat": 34.3906, "lng": 47.4364, "fee": 300000, "hours": "۸:۰۰ تا ۱۸:۰۰", "address": "بیستون", "image": "Behistun Inscription.jpg"},
    # کرمان
    {"city": "کرمان", "name": "گنجعلی‌خان", "description": "مجموعه بازار، حمام و میدان صفوی.", "category": "تاریخی", "lat": 30.2914, "lng": 57.0786, "fee": 200000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "بازار بزرگ", "image": "Ganjali Khan Complex.jpg"},
    {"city": "کرمان", "name": "گنبد جبلیه", "description": "بنای سنگی ساسانی-سلجوقی در شرق کرمان.", "category": "تاریخی", "lat": 30.2928, "lng": 57.0956, "fee": 100000, "hours": "۸:۰۰ تا ۱۸:۰۰", "address": "کوه صاحب‌الزمان", "image": "Jabalieh Dome Kerman.jpg"},
    {"city": "بم", "name": "ارگ بم", "description": "بزرگ‌ترین بنای خشتی جهان.", "category": "تاریخی", "lat": 29.1167, "lng": 58.3667, "fee": 400000, "hours": "۸:۰۰ تا ۱۷:۰۰", "address": "بم", "image": "Arg-e Bam.jpg"},
    {"city": "ماهان", "name": "باغ شاهزاده ماهان", "description": "باغ ایرانی پلکانی در دامنه جوپار.", "category": "باغ تاریخی", "lat": 30.0583, "lng": 57.2833, "fee": 400000, "hours": "۸:۰۰ تا ۲۰:۰۰", "address": "ماهان", "image": "Shazdeh Garden.jpg"},
    # گیلان
    {"city": "رشت", "name": "میدان شهرداری رشت", "description": "میدان تاریخی و عمارت شهرداری.", "category": "دیدنی شهری", "lat": 37.2783, "lng": 49.5892, "fee": None, "hours": "شبانه‌روزی", "address": "میدان شهرداری", "image": "Rasht Municipality.jpg"},
    {"city": "رشت", "name": "بازار بزرگ رشت", "description": "بازار سنتی مرکز رشت؛ سبزی، ماهی و خوراک گیلکی.", "category": "بازار", "lat": 37.2768, "lng": 49.5899, "fee": None, "hours": "۸:۰۰ تا ۲۰:۰۰", "address": "سبزه‌میدان", "image": "Rasht Bazaar.jpg"},
    {"city": "رشت", "name": "موزه میراث روستایی گیلان", "description": "خانه‌های بومی گیلان که به محوطه روباز سراوان منتقل شده‌اند.", "category": "موزه", "lat": 37.1681, "lng": 49.6319, "fee": 250000, "hours": "۹:۰۰ تا ۱۷:۰۰", "address": "پارک جنگلی سراوان", "image": "Gilan Rural Heritage Museum.jpg"},
    {"city": "رشت", "name": "استخر عینک", "description": "تالاب شهری رشت با مسیر پیاده‌روی و قایق.", "category": "طبیعی", "lat": 37.2689, "lng": 49.5628, "fee": None, "hours": "شبانه‌روزی", "address": "بلوار امام خمینی", "image": "Eynak Lagoon Rasht.jpg"},
    {"city": "رشت", "name": "باغ محتشم", "description": "پارک تاریخی با عمارت کلاه‌فرنگی کنار رودخانه گوهررود.", "category": "باغ تاریخی", "lat": 37.2711, "lng": 49.5897, "fee": None, "hours": "۶:۰۰ تا ۲۴:۰۰", "address": "خیابان حافظ", "image": "Mohtasham Garden Rasht.jpg"},
    {"city": "رشت", "name": "خانه میرزا کوچک خان", "description": "خانه پدری میرزا کوچک خان جنگلی؛ امروز موزه.", "category": "تاریخی", "lat": 37.2736, "lng": 49.5881, "fee": 150000, "hours": "۹:۰۰ تا ۱۷:۰۰", "address": "استادسرا", "image": "Mirza Kuchak Khan house.jpg"},
    {"city": "رشت", "name": "پارک ملت رشت", "description": "پارک شهری کنار گوهررود با مسیر پیاده‌روی.", "category": "طبیعی", "lat": 37.2694, "lng": 49.5892, "fee": None, "hours": "۶:۰۰ تا ۲۴:۰۰", "address": "خیابان سعدی", "image": "Mellat Park Rasht.jpg"},
    {"city": "ماسوله", "name": "ماسوله", "description": "روستای پلکانی با معماری منحصربه‌فرد.", "category": "روستای تاریخی", "lat": 37.1550, "lng": 48.9911, "fee": None, "hours": "شبانه‌روزی", "address": "ماسوله", "image": "Masuleh village.jpg"},
    {"city": "بندر انزلی", "name": "تالاب انزلی", "description": "یکی از مهم‌ترین تالاب‌های ایران.", "category": "طبیعی", "lat": 37.4181, "lng": 49.4600, "fee": None, "hours": "شبانه‌روزی", "address": "انزلی", "image": "Anzali Lagoon.jpg"},
    {"city": "لاهیجان", "name": "بام سبز لاهیجان", "description": "تپه و تله‌کابین مشرف به استخر و شهر.", "category": "طبیعی", "lat": 37.2078, "lng": 50.0206, "fee": 200000, "hours": "۹:۰۰ تا ۲۳:۰۰", "address": "شیخانبر", "image": "Lahijan cable car.jpg"},
    {"city": "لاهیجان", "name": "استخر لاهیجان", "description": "استخر مصنوعی پای تپه با مسیر پیاده‌روی چای.", "category": "دیدنی شهری", "lat": 37.2031, "lng": 50.0172, "fee": None, "hours": "شبانه‌روزی", "address": "پایین تپه", "image": "Lahijan pool.jpg"},
    # مازندران
    {"city": "رامسر", "name": "کاخ مرمر رامسر", "description": "کاخ پهلوی در باغ‌های مرکبات.", "category": "تاریخی", "lat": 36.9036, "lng": 50.6669, "fee": 250000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "رامسر", "image": "Ramsar Palace.jpg"},
    {"city": "رامسر", "name": "تله‌کابین رامسر", "description": "تله‌کابین از ساحل تا جنگل و هتل بام رامسر.", "category": "طبیعی", "lat": 36.9214, "lng": 50.6486, "fee": 400000, "hours": "۹:۰۰ تا ۲۳:۰۰", "address": "جاده جواهرده", "image": "Ramsar cable car.jpg"},
    {"city": "رامسر", "name": "جنگل دالخانی", "description": "جنگل ابری مسیر جواهرده با مه و پیچ جاده.", "category": "طبیعی", "lat": 36.8500, "lng": 50.5500, "fee": None, "hours": "شبانه‌روزی", "address": "جاده جواهرده", "image": "Dalkhani forest Ramsar.jpg"},
    {"city": "بابلسر", "name": "ساحل بابلسر", "description": "ساحل معروف خزر با پیاده‌راه.", "category": "طبیعی", "lat": 36.7078, "lng": 52.6500, "fee": None, "hours": "شبانه‌روزی", "address": "بلوار دریا", "image": "Caspian Sea Iran.jpg"},
    {"city": "ساری", "name": "خانه کلبادی", "description": "خانه قاجاری ساری؛ امروز موزه.", "category": "تاریخی", "lat": 36.5658, "lng": 53.0594, "fee": 150000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "محله آب‌انبار نو", "image": "Kolbadi house Sari.jpg"},
    {"city": "ساری", "name": "برج سلطان زین‌العابدین", "description": "برج آرامگاهی آجری دوره تیموری در ساری.", "category": "تاریخی", "lat": 36.5667, "lng": 53.0583, "fee": None, "hours": "شبانه‌روزی", "address": "خیابان انقلاب", "image": "Soltan Zeyn-ol-Abedin tower.jpg"},
    {"city": "کرج", "name": "سد امیرکبیر", "description": "سد کرج در ورودی جاده چالوس؛ دریاچه و کوه.", "category": "طبیعی", "lat": 35.9569, "lng": 51.0906, "fee": None, "hours": "شبانه‌روزی", "address": "جاده چالوس", "image": "Karaj Dam.jpg"},
    {"city": "کرج", "name": "کاخ شهرستانک", "description": "کاخ ییلاقی پهلوی در دره شهرستانک.", "category": "تاریخی", "lat": 36.0333, "lng": 51.3667, "fee": 150000, "hours": "۹:۰۰ تا ۱۷:۰۰", "address": "شهرستانک", "image": "Shahrestanak palace.jpg"},
    # خوزستان
    {"city": "شوش", "name": "چغازنبیل", "description": "زیگورات ایلامی، نخستین میراث یونسکو در ایران.", "category": "باستانی", "lat": 32.0083, "lng": 48.5217, "fee": 400000, "hours": "۸:۰۰ تا ۱۷:۰۰", "address": "شوش", "image": "Chogha Zanbil.jpg"},
    {"city": "شوش", "name": "کاخ آپادانا شوش", "description": "بقایای کاخ هخامنشی در شوش.", "category": "باستانی", "lat": 32.1894, "lng": 48.2506, "fee": 300000, "hours": "۸:۰۰ تا ۱۷:۰۰", "address": "شوش", "image": "Apadana Palace Susa.jpg"},
    {"city": "شوشتر", "name": "سازه‌های آبی شوشتر", "description": "سیستم آبی باستانی ثبت یونسکو.", "category": "تاریخی", "lat": 32.0494, "lng": 48.8486, "fee": 300000, "hours": "۸:۰۰ تا ۱۸:۰۰", "address": "شوشتر", "image": "Shushtar Historical Hydraulic System.jpg"},
    {"city": "اهواز", "name": "پل سفید اهواز", "description": "پل معلق معروف روی کارون؛ نماد شهر.", "category": "دیدنی شهری", "lat": 31.3225, "lng": 48.6786, "fee": None, "hours": "شبانه‌روزی", "address": "کارون", "image": "White Bridge Ahvaz.jpg"},
    {"city": "اهواز", "name": "رود کارون", "description": "پیاده‌راه و ساحل کارون در مرکز اهواز.", "category": "طبیعی", "lat": 31.3206, "lng": 48.6764, "fee": None, "hours": "شبانه‌روزی", "address": "بلوار ساحلی", "image": "Karun River Ahvaz.jpg"},
    {"city": "ارومیه", "name": "دریاچه ارومیه", "description": "بزرگ‌ترین دریاچه داخلی ایران؛ شور و پرنده.", "category": "طبیعی", "lat": 37.7000, "lng": 45.3167, "fee": None, "hours": "شبانه‌روزی", "address": "شرق ارومیه", "image": "Lake Urmia.jpg"},
    {"city": "ارومیه", "name": "بازار ارومیه", "description": "بازار سرپوشیده تاریخی مرکز شهر.", "category": "بازار", "lat": 37.5522, "lng": 45.0764, "fee": None, "hours": "۹:۰۰ تا ۲۰:۰۰", "address": "بازار بزرگ", "image": "Urmia Bazaar.jpg"},
    {"city": "ارومیه", "name": "مسجد جامع ارومیه", "description": "مسجد تاریخی با گنبد سلجوقی در کنار بازار.", "category": "مذهبی-تاریخی", "lat": 37.5514, "lng": 45.0756, "fee": None, "hours": "۸:۰۰ تا ۲۰:۰۰", "address": "بازار", "image": "Urmia Jameh Mosque.jpg"},
    # قم / قزوین / زنجان / اردبیل
    {"city": "قزوین", "name": "کاخ چهل‌ستون قزوین", "description": "کوشک صفوی در باغ تاریخی.", "category": "تاریخی", "lat": 36.2686, "lng": 50.0036, "fee": 200000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "خیابان هلال احمر", "image": "Chehel Sotoun Qazvin.jpg"},
    {"city": "قزوین", "name": "حسینیه امینی‌ها", "description": "خانه اعیانی قاجاری با تالار آینه و ارسی.", "category": "تاریخی", "lat": 36.2681, "lng": 50.0047, "fee": 150000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "خیابان مولوی", "image": "Aminiha Hosseiniyeh.jpg"},
    {"city": "قم", "name": "حرم حضرت معصومه (س)", "description": "زیارتگاه مهم شیعیان در قم.", "category": "مذهبی", "lat": 34.6419, "lng": 50.8792, "fee": None, "hours": "شبانه‌روزی", "address": "حرم مطهر", "image": "Fatima Masumeh Shrine.jpg"},
    {"city": "قم", "name": "مسجد جمکران", "description": "مسجد زیارتی معروف حاشیه قم.", "category": "مذهبی", "lat": 34.5831, "lng": 50.9119, "fee": None, "hours": "شبانه‌روزی", "address": "جمکران", "image": "Jamkaran Mosque.jpg"},
    {"city": "سلطانیه", "name": "گنبد سلطانیه", "description": "بزرگ‌ترین گنبد آجری جهان، ثبت یونسکو.", "category": "تاریخی", "lat": 36.4344, "lng": 48.7942, "fee": 300000, "hours": "۸:۰۰ تا ۱۸:۰۰", "address": "سلطانیه", "image": "Soltaniyeh Dome.jpg"},
    {"city": "اردبیل", "name": "بقعه شیخ صفی‌الدین", "description": "مجموعه خانقاه و آرامگاه صفوی، ثبت یونسکو.", "category": "مذهبی-تاریخی", "lat": 38.2486, "lng": 48.2914, "fee": 300000, "hours": "۸:۰۰ تا ۲۰:۰۰", "address": "اردبیل", "image": "Sheikh Safi al-din Khanegah.jpg"},
    {"city": "اردبیل", "name": "دریاچه شورابیل", "description": "دریاچه داخل شهر اردبیل با مسیر پیاده‌روی.", "category": "طبیعی", "lat": 38.2111, "lng": 48.2856, "fee": None, "hours": "شبانه‌روزی", "address": "شورابیل", "image": "Shorabil Lake.jpg"},
    {"city": "زنجان", "name": "رختشویخانه زنجان", "description": "رختشویخانه قاجاری؛ امروز موزه مردم‌شناسی.", "category": "تاریخی", "lat": 36.6706, "lng": 48.5014, "fee": 150000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "خیابان سعدی", "image": "Zanjan Rakhtshooy Khaneh.jpg"},
    {"city": "زنجان", "name": "بازار زنجان", "description": "یکی از طولانی‌ترین بازارهای سرپوشیده ایران.", "category": "بازار", "lat": 36.6719, "lng": 48.5006, "fee": None, "hours": "۹:۰۰ تا ۲۰:۰۰", "address": "بازار بالا", "image": "Zanjan Bazaar.jpg"},
    {"city": "سرعین", "name": "آبگرم سرعین", "description": "چشمه‌های آب گرم معروف شمال غرب.", "category": "طبیعی", "lat": 38.1514, "lng": 48.0708, "fee": 150000, "hours": "۶:۰۰ تا ۲۴:۰۰", "address": "سرعین", "image": "Sarein hot springs.jpg"},
    # هرمزگان / کیش
    {"city": "کیش", "name": "شهر زیرزمینی کاریز", "description": "قنات تاریخی تبدیل‌شده به سایت گردشگری.", "category": "تاریخی", "lat": 26.5328, "lng": 53.9806, "fee": 500000, "hours": "۱۰:۰۰ تا ۲۲:۰۰", "address": "کیش", "image": "Kish Island.jpg"},
    {"city": "کیش", "name": "ساحل کشتی یونانی", "description": "لاشه کشتی معروف در ساحل غرب کیش.", "category": "دیدنی شهری", "lat": 26.5306, "lng": 53.9400, "fee": None, "hours": "شبانه‌روزی", "address": "ساحل غربی کیش", "image": "Greek Ship Kish.jpg"},
    {"city": "قشم", "name": "ژئوپارک قشم", "description": "تنها ژئوپارک جهانی ایران.", "category": "طبیعی", "lat": 26.7583, "lng": 55.8000, "fee": 200000, "hours": "۸:۰۰ تا ۱۸:۰۰", "address": "قشم", "image": "Qeshm Island.jpg"},
    {"city": "قشم", "name": "غار نمکدان", "description": "از بلندترین غارهای نمکی جهان.", "category": "طبیعی", "lat": 26.6167, "lng": 55.5000, "fee": 200000, "hours": "۸:۰۰ تا ۱۷:۰۰", "address": "غرب قشم", "image": "Namakdan Salt Cave.jpg"},
    {"city": "قشم", "name": "دره ستارگان", "description": "فرسایش رسوبی شبیه دالان‌های ماه؛ ژئوسایت معروف قشم.", "category": "طبیعی", "lat": 26.8167, "lng": 55.9500, "fee": 150000, "hours": "۸:۰۰ تا ۱۸:۰۰", "address": "نزدیک روستای برکه خلف", "image": "Stars Valley Qeshm.jpg"},
    {"city": "قشم", "name": "جنگل حرا قشم", "description": "مانگروهای خلیج فارس؛ قایق‌سواری بین درختان در جزر و مد.", "category": "طبیعی", "lat": 26.8167, "lng": 55.7500, "fee": 200000, "hours": "۸:۰۰ تا ۱۷:۰۰", "address": "شمال قشم", "image": "Hara forests Qeshm.jpg"},
    {"city": "قشم", "name": "دره چاهکوه", "description": "دره سنگی با دیواره‌های صیقلی و حفره‌های فرسایش.", "category": "طبیعی", "lat": 26.6667, "lng": 55.5333, "fee": 100000, "hours": "۸:۰۰ تا ۱۷:۰۰", "address": "غرب قشم", "image": "Chahkooh canyon Qeshm.jpg"},
    {"city": "بندرعباس", "name": "معبد هندوها", "description": "معبد تاریخی بازرگانان هندی.", "category": "مذهبی-تاریخی", "lat": 27.1836, "lng": 56.2772, "fee": 100000, "hours": "۸:۰۰ تا ۲۰:۰۰", "address": "خیابان امام خمینی", "image": "Hindu Temple Bandar Abbas.jpg"},
    {"city": "بندرعباس", "name": "ساحل سورو", "description": "ساحل غربی بندرعباس با غروب خلیج فارس.", "category": "طبیعی", "lat": 27.1736, "lng": 56.2328, "fee": None, "hours": "شبانه‌روزی", "address": "سورو", "image": "Suru Beach Bandar Abbas.jpg"},
    {"city": "بندرعباس", "name": "بازار ماهی بندرعباس", "description": "بازار تازه ماهی و میگو کنار اسکله.", "category": "بازار", "lat": 27.1831, "lng": 56.2936, "fee": None, "hours": "۶:۰۰ تا ۱۴:۰۰", "address": "اسکله شهید حقانی", "image": "Bandar Abbas fish market.jpg"},
    {"city": "بندرعباس", "name": "حمام گله‌داری", "description": "حمام تاریخی دوره قاجار در بافت قدیم بندر.", "category": "تاریخی", "lat": 27.1814, "lng": 56.2778, "fee": 100000, "hours": "۸:۰۰ تا ۱۸:۰۰", "address": "بافت قدیم", "image": "Galedari Bath Bandar Abbas.jpg"},
    # کردستان / لرستان / ایلام
    {"city": "سنندج", "name": "عمارت خسروآباد", "description": "کاخ اردلان‌ها در سنندج.", "category": "تاریخی", "lat": 35.3119, "lng": 46.9928, "fee": 150000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "خیابان کشاورز", "image": "Khosro Abad mansion.jpg"},
    {"city": "مریوان", "name": "دریاچه زریبار", "description": "دریاچه آب شیرین در دامنه زاگرس.", "category": "طبیعی", "lat": 35.5431, "lng": 46.1358, "fee": None, "hours": "شبانه‌روزی", "address": "مریوان", "image": "Zarivar Lake.jpg"},
    {"city": "خرم‌آباد", "name": "فلک‌الافلاک", "description": "قلعه ساسانی مشرف به خرم‌آباد.", "category": "تاریخی", "lat": 33.4836, "lng": 48.3536, "fee": 300000, "hours": "۸:۰۰ تا ۲۰:۰۰", "address": "خیابان انقلاب", "image": "Falak-ol-Aflak Castle.jpg"},
    {"city": "الیگودرز", "name": "آبشار بیشه", "description": "آبشار معروف لرستان در مسیر راه‌آهن.", "category": "طبیعی", "lat": 33.3333, "lng": 48.8750, "fee": None, "hours": "شبانه‌روزی", "address": "بیشه", "image": "Bisheh waterfall.jpg"},
    # گلستان / سمنان / خراسان شمالی
    {"city": "گنبد کاووس", "name": "برج گنبد قابوس", "description": "بلندترین برج آجری جهان، ثبت یونسکو.", "category": "تاریخی", "lat": 37.2578, "lng": 55.1692, "fee": 200000, "hours": "۸:۰۰ تا ۲۰:۰۰", "address": "میدان امام", "image": "Gonbad-e Qabus.jpg"},
    {"city": "گرگان", "name": "ناهارخوران", "description": "جنگل و تفرجگاه جنوبی گرگان.", "category": "طبیعی", "lat": 36.7644, "lng": 54.4642, "fee": None, "hours": "شبانه‌روزی", "address": "جاده ناهارخوران", "image": "Naharkhoran Gorgan.jpg"},
    {"city": "گرگان", "name": "بافت تاریخی گرگان", "description": "محله‌های قاجاری با خانه‌های چوبی استرآباد.", "category": "تاریخی", "lat": 36.8419, "lng": 54.4344, "fee": None, "hours": "شبانه‌روزی", "address": "نعلبندان", "image": "Gorgan historic fabric.jpg"},
    {"city": "شاهرود", "name": "جنگل ابر", "description": "جنگل ابری در البرز شرقی.", "category": "طبیعی", "lat": 36.6167, "lng": 55.0833, "fee": None, "hours": "شبانه‌روزی", "address": "شمال شاهرود", "image": "Abr Forest.jpg"},
    {"city": "بجنورد", "name": "عمارت مفخم", "description": "کاخ و آینه‌خانه قاجاری.", "category": "تاریخی", "lat": 37.4764, "lng": 57.3319, "fee": 150000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "بجنورد", "image": "Mofakham mansion.jpg"},
    # سیستان / بوشهر / کهگیلویه / چهارمحال
    {"city": "زابل", "name": "شهر سوخته", "description": "محوطه عصر مفرغ، ثبت یونسکو.", "category": "باستانی", "lat": 30.5917, "lng": 61.3250, "fee": 200000, "hours": "۸:۰۰ تا ۱۷:۰۰", "address": "جاده زابل-زاهدان", "image": "Shahr-e Sukhteh.jpg"},
    {"city": "بوشهر", "name": "عمارت ملک", "description": "خانه تاریخی مشرف به خلیج فارس.", "category": "تاریخی", "lat": 28.9239, "lng": 50.8386, "fee": 100000, "hours": "۹:۰۰ تا ۱۸:۰۰", "address": "بافت قدیم", "image": "Bushehr historic mansion.jpg"},
    {"city": "یاسوج", "name": "تنگ مهریان", "description": "دره و رودخانه معروف بویراحمد.", "category": "طبیعی", "lat": 30.7167, "lng": 51.5500, "fee": None, "hours": "شبانه‌روزی", "address": "شمال یاسوج", "image": "Yasuj nature.jpg"},
    {"city": "شهرکرد", "name": "چشمه کوهرنگ", "description": "سرچشمه زاینده‌رود.", "category": "طبیعی", "lat": 32.4667, "lng": 50.1333, "fee": None, "hours": "شبانه‌روزی", "address": "کوهرنگ", "image": "Koohrang spring.jpg"},
    {"city": "بیرجند", "name": "باغ اکبریه", "description": "باغ ایرانی ثبت یونسکو.", "category": "باغ تاریخی", "lat": 32.8569, "lng": 59.2214, "fee": 200000, "hours": "۸:۰۰ تا ۱۸:۰۰", "address": "خیابان معلم", "image": "Akbarieh Garden.jpg"},
    {"city": "اراک", "name": "بازار اراک", "description": "بازار چهارسوق دوره قاجار.", "category": "بازار", "lat": 34.0911, "lng": 49.6897, "fee": None, "hours": "۹:۰۰ تا ۲۰:۰۰", "address": "بازار تاریخی", "image": "Arak Bazaar.jpg"},
    {"city": "ساوه", "name": "مسجد جامع ساوه", "description": "مسجد تاریخی با مناره سلجوقی.", "category": "مذهبی-تاریخی", "lat": 35.0219, "lng": 50.3561, "fee": None, "hours": "۸:۰۰ تا ۱۸:۰۰", "address": "ساوه", "image": "Saveh Jameh Mosque.jpg"},
]


# Demo hospitality catalog lives in demo_hospitality.py — synthetic rates,
# rooms, and menus so the product can be demoed before a paid API exists.
from app.infrastructure.data.demo_hospitality import DINING_PLACES, LODGING_PLACES


def commons_image_url(filename: str | None, width: int = 640) -> str | None:
    if not filename:
        return None
    from urllib.parse import quote

    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{quote(filename)}?width={width}"
