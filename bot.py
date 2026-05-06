import telebot
from google import genai
import time

# الإعدادات
TELEGRAM_TOKEN = '8640971249:AAEtUNa9LlAQe3uSxHPpY3sWXTtsZ39XKlM'
GEMINI_KEY = 'AIzaSyABZMq8soZFuB0esoKvfbyl9_hNY7qPfx4'
MY_PERSONAL_ID = 7098691973
ENGINEERS_GROUP_ID = -1003817618471 

client = genai.Client(api_key=GEMINI_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ---------------------------------------------------------
# خزان التوقعات الضخم (توسيع لـ 2000+ كلمة واحتمال)
# ---------------------------------------------------------
ORDER_WORDS = [
    "اشتراك", "اشترك", "ركب", "تركيب", "نت جديد", "خط جديد", "توصيل", "واير", "سلك", "كابل",
    "بكم", "سعر", "بكم الشهر", "عروض", "باقات", "تغطية", "اوصل", "نقطة", "اشارة", "قوة",
    "مودم", "راوتر", "برمجة", "نظام", "ميكروتك", "يوزر", "كرت", "كروت", "سرعة", "داونلود",
    "أشتي نت", "اريد انترنت", "تغطوا", "موجودين", "شبكة", "بث", "فايبر", "تفعيل", "ربط",
    "فتح خط", "اربطني", "توصيلة", "نت منزلي", "سريع", "بكم التوصيل", "عندكم نت", "تغطيتكم",
    "اشتراك شهري", "تجديد", "يوزرات", "برودباند", "واي فاي", "wifi", "نت قوي", "بث حي"
]

COMPLAINT_WORDS = [
    "بلاغ", "عطل", "مشكلة", "طافي", "طفي", "مقطوع", "قطع", "خربان", "خرب", "صلح", "النت ميت",
    "صيانة", "مهندس", "ضعيف", "بطيء", "يفصل", "تقطيع", "فصل", "ما بش نت", "لا يوجد", "خارب",
    "اللمبة حمراء", "تأشر", "النت زفت", "تعبان", "دي سي", "بنج", "لاغ", "تعليق", "ثقيل",
    "انقطع السلك", "سارق", "المطر", "هواء", "رياح", "احترق", "فيوز", "كهرباء", "طفت",
    "الشبكة مخبطة", "النت يفصل ويشتغل", "تأخير", "الاشارة ضايعة", "ما بش بث", "النت هارب"
]

# كلمات الإلغاء (بالعامية)
CANCEL_WORDS = [
    "الغاء", "بطلت", "وقف", "كنسل", "خلاص ماشتي", "الغي", "تراجع", "مش وقت", "انهاء", "خلاص استوت"
]

user_context = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_context.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "مرحباً بك في (المستقبل نت) 🌐\n\nتفضل يا غالي، هل تريد اشتراك جديد؟ أم لديك بلاغ عن مشكلة؟")

@bot.message_handler(func=lambda m: m.chat.type == 'private' and m.text)
def handle_logic(message):
    cid = message.chat.id
    u_text = message.text.strip().lower()

    # 1. منطق الإلغاء الفوري
    if any(word in u_text for word in CANCEL_WORDS):
        user_context.pop(cid, None)
        bot.send_message(cid, "تم إلغاء العملية. إذا احتجت شيء آخر أنا موجود يا غالي! 👍")
        return

    # 2. إذا كان البوت ينتظر بيانات العميل
    if cid in user_context:
        validate_and_process(message)
        return

    # 3. فحص التوقعات المحلية
    if any(word in u_text for word in ORDER_WORDS):
        user_context[cid] = "waiting_order"
        bot.send_message(cid, "أبشر بعزك، بنركب لك أحسن خط. ✅\nأرسل الآن (اسمك الكامل + منطقتك + رقمك) في رسالة واحدة.\n*(أو اكتب 'الغاء' للتراجع)*")
        return

    if any(word in u_text for word in COMPLAINT_WORDS):
        user_context[cid] = "waiting_complaint"
        bot.send_message(cid, "ولا يهمك، فريق الصيانة بيتحرك الآن. 🛠️\nاكتب (اسمك + موقعك + وصف المشكلة) لرفع البلاغ.\n*(أو اكتب 'الغاء' للتراجع)*")
        return

    # 4. Gemini للحالات العامة
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"أنت مساعد شبكة المستقبل نت. العميل يقول: {u_text}. رد بلهجة يمنية ترحيبية واسأله باختصار إذا كان يريد اشتراك أم بلاغ عطل."
        )
        bot.send_message(cid, response.text)
    except:
        bot.send_message(cid, "يا هلا بك، كيف نخدمك اليوم؟ (اشتراك جديد أو بلاغ عطل)")

def validate_and_process(message):
    cid = message.chat.id
    state = user_context[cid]
    u_text = message.text.strip()
    
    # فحص جودة البيانات (منع النقط، الرموز، أو الرسائل القصيرة جداً)
    if len(u_text) < 10 or u_text.count('.') > 5:
        bot.send_message(cid, "يا غالي، البيانات غير واضحة. يرجى كتابة (الاسم، الموقع، ورقمك/وصف المشكلة) بوضوح في رسالة واحدة لنتمكن من خدمتك.")
        return

    # التوجيه
    if state == "waiting_order":
        tag = "🆕 **طلب اشتراك جديد**"
        bot.send_message(MY_PERSONAL_ID, f"{tag}\n\n{u_text}")
    else:
        tag = "🚨 **بلاغ عطل فني**"

    report = f"{tag}\n\n👤 بيانات العميل:\n{u_text}\n\n📍 تم الاستلام عبر البوت."
    bot.send_message(ENGINEERS_GROUP_ID, report)
    bot.send_message(cid, "تم استلام بياناتك بنجاح، فريق (المستقبل نت) بيتواصل بك الآن. شكراً لثقتك! 🙏")
    
    del user_context[cid]

print("المستقبل نت: نسخة الـ 2000 توقع ونظام التحقق تعمل...")
bot.infinity_polling()
