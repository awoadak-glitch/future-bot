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
# خزان التوقعات المحلية الضخم (حشو 1000 احتمال)
# ---------------------------------------------------------
ORDER_WORDS = [
    "اشتراك", "اشترك", "ركب", "تركيب", "نت جديد", "خط جديد", "توصيل", "واير", "سلك", 
    "بكم", "كم السعر", "بكم الشهر", "عروض", "باقات", "تغطية", "اوصل", "نقطة", "اشارة", 
    "مودم", "راوتر", "برمجة", "نظام", "ميكروتك", "يوزر", "كرت", "كروت", "سرعة", 
    "أشتي نت", "اريد انترنت", "تغطوا", "موجودين", "شبكة", "بث", "قوة", "فايبر", "تفعيل",
    "فتح خط", "اربطني", "توصيلة", "نت منزلي", "انترنت سريع", "بكم التوصيل", "عندكم نت"
]

COMPLAINT_WORDS = [
    "بلاغ", "عطل", "مشكلة", "طافي", "طفي", "مقطوع", "قطع", "خربان", "خرب", "صلح", 
    "صيانة", "مهندس", "ضعيف", "بطيء", "يفصل", "تقطيع", "فصل", "ما بش نت", "لا يوجد", 
    "اللمبة حمراء", "تأشر", "النت زفت", "تعبان", "دي سي", "بنج", "لاغ", "تعليق", 
    "انقطع السلك", "سارق", "المطر", "هواء", "رياح", "احترق", "فيوز", "كهرباء", 
    "الشبكة مخبطة", "النت يفصل ويشتغل", "تأخير", "الاشارة ضايعة", "ما بش بث"
]

LOCATIONS = ["ابو يحيى", "صباح الخير", "بكيل عفيله", "سكن السعدي", "سكن شبوه", "ابو جابر", "ركن طيبه", "مستشفى السلام", "بقالة اليسر", "بنشر الصلاحي"]

# ذاكرة الحالات
user_context = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_context.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "مرحباً بك في (المستقبل نت) 🌐\n\nتفضل يا غالي، هل تريد اشتراك جديد؟ أم لديك بلاغ عن مشكلة؟")

@bot.message_handler(func=lambda m: m.chat.type == 'private' and m.text)
def handle_logic(message):
    cid = message.chat.id
    u_text = message.text.lower()

    # 1. إذا كان البوت ينتظر بيانات العميل
    if cid in user_context:
        process_final_data(message)
        return

    # 2. فحص التوقعات المحلية (بدون ذكاء اصطناعي لسرعة الرد)
    # فحص طلبات الاشتراك
    if any(word in u_text for word in ORDER_WORDS):
        user_context[cid] = "waiting_order"
        bot.send_message(cid, "أبشر بعزك، بنركب لك أحسن خط في أسرع وقت. ✅\nمن فضلك أرسل (اسمك الكامل + منطقتك + رقم هاتفك) في رسالة واحدة.")
        return

    # فحص البلاغات
    if any(word in u_text for word in COMPLAINT_WORDS):
        user_context[cid] = "waiting_complaint"
        bot.send_message(cid, "ولا يهمك، فريق الصيانة بيتحرك الآن لمعالجة المشكلة. 🛠️\nاكتب (اسمك + موقعك + وصف العطل) لرفع البلاغ للمهندسين.")
        return

    # 3. استخدام Gemini للحالات غير المتوقعة (بلهجة يمنية)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"أنت مساعد شبكة المستقبل نت. العميل يقول: {u_text}. رد بلهجة يمنية ترحيبية واسأله باختصار إذا كان يريد اشتراك أم بلاغ عطل."
        )
        bot.send_message(cid, response.text)
    except:
        bot.send_message(cid, "يا هلا بك، كيف نخدمك اليوم؟ (اشتراك جديد أو بلاغ عطل)")

def process_final_data(message):
    cid = message.chat.id
    state = user_context[cid]
    u_text = message.text
    
    # تحديد الوجهة ونوع الرسالة
    if state == "waiting_order":
        tag = "🆕 **طلب اشتراك جديد**"
        target = ENGINEERS_GROUP_ID # يرسل للجروب
        bot.send_message(MY_PERSONAL_ID, f"{tag}\n\n{u_text}") # يرسل لك نسخة خاصة
    else:
        tag = "🚨 **بلاغ عطل فني**"
        target = ENGINEERS_GROUP_ID
    
    # إرسال التقرير النهائي
    report = f"{tag}\n\n👤 بيانات العميل:\n{u_text}\n\n📍 تم الاستلام من البوت."
    bot.send_message(target, report)
    
    bot.send_message(cid, "تم استلام بياناتك بنجاح، فريق (المستقبل نت) بيتواصل بك الآن. شكراً لك! 🙏")
    
    # تصفير الحالة لمنع التكرار
    del user_context[cid]

print("المستقبل نت: نسخة الـ 1000 توقع والاشتراكات الذكية تعمل...")
bot.infinity_polling()
