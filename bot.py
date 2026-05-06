import telebot
from telebot import types
from google import genai
import time

# الإعدادات
TELEGRAM_TOKEN = '8640971249:AAEtUNa9LlAQe3uSxHPpY3sWXTtsZ39XKlM'
GEMINI_KEY = 'AIzaSyABZMq8soZFuB0esoKvfbyl9_hNY7qPfx4'
MY_PERSONAL_ID = 7098691973
ENGINEERS_GROUP_ID = -1003817618471 
LOGO_URL = "https://i.imgur.com/8f8v9K4.png" 

client = genai.Client(api_key=GEMINI_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

registered_users = set()
user_context = {}

# ---------------------------------------------------------
# خزان التوقعات الضخم (كامل كما هو في كودك الأصلي)
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

CANCEL_WORDS = ["الغاء", "بطلت", "وقف", "كنسل", "خلاص ماشتي", "الغي", "تراجع", "مش وقت", "انهاء", "خلاص استوت"]

# مصفوفة باقات كابوتا (الاقتراح 4)
PRICES_INFO = """
🌐 **باقات المستقبل نت - المنصورة / كابوتا:**

🎟️ **باقة 200 ريال** ⬅️ 750 ميجا | ⏳ يومان
🎟️ **باقة 500 ريال** ⬅️ 1900 ميجا | ⏳ أسبوع
🎟️ **باقة 1000 ريال** ⬅️ 3900 ميجا | ⏳ أسبوعان
🎟️ **باقة 3000 ريال** ⬅️ 12500 ميجا | ⏳ شهر
🎟️ **باقة 6000 ريال** ⬅️ 24 جيجا | ⏳ شهر

📍 *موقعنا: المنصورة - كابوتا*
"""

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🆕 اشتراك جديد', '🚨 بلاغ عطل', '📊 الأسعار والباقات', '🛠 برمجة الراوتر')
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    registered_users.add(message.chat.id)
    user_context.pop(message.chat.id, None)
    bot.send_photo(
        message.chat.id, 
        LOGO_URL, 
        caption="مرحباً بك في **مؤسسة المستقبل نت (كابوتا)** 🌐\n\nاختر الخدمة المطلوبة من الأزرار أو اكتب ما تريد:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['broadcast'])
def start_broadcast(message):
    if message.chat.id == MY_PERSONAL_ID:
        msg = bot.send_message(MY_PERSONAL_ID, "📢 أدخل الرسالة المراد إرسالها لجميع المشتركين:")
        bot.register_next_step_handler(msg, execute_broadcast)

def execute_broadcast(message):
    count = 0
    for user in registered_users:
        try:
            bot.send_message(user, f"⚠️ **تنبيه إداري:**\n\n{message.text}", parse_mode="Markdown")
            count += 1
        except: continue
    bot.send_message(MY_PERSONAL_ID, f"✅ تم الإرسال لـ {count} مشترك.")

@bot.message_handler(func=lambda m: m.chat.type == 'private' and m.text)
def handle_logic(message):
    cid = message.chat.id
    u_text = message.text.strip().lower()
    registered_users.add(cid)

    if message.text == '📊 الأسعار والباقات':
        bot.send_message(cid, PRICES_INFO, parse_mode="Markdown")
        return
    elif message.text == '🛠 برمجة الراوتر':
        bot.send_message(cid, "🛠 **إعدادات كابوتا:**\n1. أغلق DHCP.\n2. اضبط الـ IP على Static.\n3. تواصل معنا للمساعدة.")
        return

    if any(word in u_text for word in CANCEL_WORDS):
        user_context.pop(cid, None)
        bot.send_message(cid, "تم إلغاء العملية. 👍", reply_markup=main_menu())
        return

    if cid in user_context:
        validate_and_process(message)
        return

    if any(word in u_text for word in ORDER_WORDS) or message.text == '🆕 اشتراك جديد':
        user_context[cid] = "waiting_order"
        bot.send_message(cid, "📝 **طلب اشتراك - كابوتا**\nأرسل (اسمك + موقعك + رقمك) في رسالة واحدة.", parse_mode="Markdown")
        return

    if any(word in u_text for word in COMPLAINT_WORDS) or message.text == '🚨 بلاغ عطل':
        user_context[cid] = "waiting_complaint"
        bot.send_message(cid, "🛠 **فتح بلاغ**\nاكتب (اسمك + موقعك + وصف المشكلة).", parse_mode="Markdown")
        return

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"أنت مساعد شبكة المستقبل نت في كابوتا. العميل يقول: {u_text}. رد بلهجة يمنية ووجهه للأزرار."
        )
        bot.send_message(cid, response.text, reply_markup=main_menu())
    except:
        bot.send_message(cid, "يا هلا بك، استخدم الأزرار بالأسفل لخدمتك.", reply_markup=main_menu())

def validate_and_process(message):
    cid = message.chat.id
    state = user_context[cid]
    u_text = message.text.strip()
    
    if len(u_text) < 10 or u_text.count('.') > 5:
        bot.send_message(cid, "⚠️ البيانات ناقصة. يرجى كتابة التفاصيل بوضوح (الاسم والموقع والرقم).")
        return

    tag = "🆕 **اشتراك جديد**" if state == "waiting_order" else "🚨 **بلاغ عطل**"
    report = (
        f"{tag} (كابوتا)\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 **العميل:** {message.from_user.first_name}\n"
        f"📝 **التفاصيل:**\n`{u_text}`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⏰ {time.strftime('%H:%M - %Y/%m/%d')}"
    )
    
    bot.send_message(ENGINEERS_GROUP_ID, report, parse_mode="Markdown")
    if state == "waiting_order": bot.send_message(MY_PERSONAL_ID, report, parse_mode="Markdown")
    
    bot.send_message(cid, "✅ تم استلام بياناتك بنجاح. فريق كابوتا بيتواصل بك.", reply_markup=main_menu())
    del user_context[cid]

bot.infinity_polling()
