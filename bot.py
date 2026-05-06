import telebot
from telebot import types
from google import genai
import time

# الإعدادات
TELEGRAM_TOKEN = '8640971249:AAEtUNa9LlAQe3uSxHPpY3sWXTtsZ39XKlM'
GEMINI_KEY = 'AIzaSyABZMq8soZFuB0esoKvfbyl9_hNY7qPfx4'
MY_PERSONAL_ID = 7098691973
ENGINEERS_GROUP_ID = -1003817618471 
LOGO_URL = "https://i.imgur.com/8f8v9K4.png" # لوجو المستقبل نت

client = genai.Client(api_key=GEMINI_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

registered_users = set()

# مصفوفة الباقات المحدثة (المنصورة - كابوتا)
PRICES_INFO = """
🌐 **باقات المستقبل نت - المنصورة / كابوتا:**

🎟️ **باقة 200 ريال**
   ⬅️ الحجم: 750 ميجا | ⏳ يومان

🎟️ **باقة 500 ريال**
   ⬅️ الحجم: 1900 ميجا | ⏳ أسبوع

🎟️ **باقة 1000 ريال**
   ⬅️ الحجم: 3900 ميجا | ⏳ أسبوعان

🎟️ **باقة 3000 ريال**
   ⬅️ الحجم: 12500 ميجا | ⏳ شهر

🎟️ **باقة 6000 ريال**
   ⬅️ الحجم: 24 جيجا | ⏳ شهر

---
📍 *موقعنا: المنصورة - كابوتا - شبكة المستقبل نت*
"""

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton('🆕 اشتراك جديد')
    btn2 = types.KeyboardButton('🚨 بلاغ عطل')
    btn3 = types.KeyboardButton('📊 الأسعار والباقات')
    btn4 = types.KeyboardButton('🛠 كيف أبرمج راوتري؟')
    markup.add(btn1, btn2, btn3, btn4)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    registered_users.add(message.chat.id)
    bot.send_photo(
        message.chat.id, 
        LOGO_URL, 
        caption="مرحباً بك في **مؤسسة المستقبل نت (فرع المنصورة - كابوتا)** 🌐\n\nنحن هنا لخدمتك، اختر العملية المطلوبة من الأزرار أدناه:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# نظام الإشعارات (رقم 5)
@bot.message_handler(commands=['broadcast'])
def start_broadcast(message):
    if message.chat.id == MY_PERSONAL_ID:
        msg = bot.send_message(MY_PERSONAL_ID, "📢 اكتب الآن الرسالة التي تريد إرسالها لجميع المشتركين في كابوتا:")
        bot.register_next_step_handler(msg, execute_broadcast)

def execute_broadcast(message):
    count = 0
    for user in registered_users:
        try:
            bot.send_message(user, f"⚠️ **تنبيه إداري من المستقبل نت**\n\n{message.text}", parse_mode="Markdown")
            count += 1
        except: continue
    bot.send_message(MY_PERSONAL_ID, f"✅ تم الإرسال لـ {count} مشترك بنجاح.")

@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    cid = message.chat.id
    text = message.text
    registered_users.add(cid)

    if text == '📊 الأسعار والباقات':
        bot.send_message(cid, PRICES_INFO, parse_mode="Markdown")
    
    elif text == '🛠 كيف أبرمج راوتري؟':
        bot.send_message(cid, "🛠 **إعدادات البرمجة:**\n\n1️⃣ تأكد من إغلاق **DHCP**.\n2️⃣ اضبط الـ IP على **Static**.\n3️⃣ للمساعدة المباشرة في كابوتا تواصل معنا.", parse_mode="Markdown")

    elif text == '🆕 اشتراك جديد':
        msg = bot.send_message(cid, "📝 **طلب اشتراك جديد**\n\nأرسل الآن (اسمك + موقعك في كابوتا + رقمك) في رسالة واحدة.\n\n_أو اكتب 'الغاء' للتراجع._", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_order)
    
    elif text == '🚨 بلاغ عطل':
        msg = bot.send_message(cid, "🛠 **فتح بلاغ صيانة**\n\nاكتب (اسمك + موقعك + وصف العطل) بوضوح.\n\n_أو اكتب 'الغاء' للتراجع._", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_complaint)

def process_order(message):
    if any(word in message.text.lower() for word in ["الغاء", "بطلت"]):
        bot.send_message(message.chat.id, "❌ تم إلغاء العملية.", reply_markup=main_menu())
        return
    
    report = (
        f"🌟 **طلب اشتراك جديد - كابوتا** 🌟\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 **العميل:** {message.from_user.first_name}\n"
        f"📝 **البيانات:**\n`{message.text}`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📅 الوقت: {time.strftime('%Y-%m-%d %H:%M')}"
    )
    bot.send_message(ENGINEERS_GROUP_ID, report, parse_mode="Markdown")
    bot.send_message(MY_PERSONAL_ID, report, parse_mode="Markdown")
    bot.send_message(message.chat.id, "✅ **تم استلام طلبك!**\nفريق كابوتا سيتواصل معك قريباً.", reply_markup=main_menu(), parse_mode="Markdown")

def process_complaint(message):
    if any(word in message.text.lower() for word in ["الغاء", "بطلت"]):
        bot.send_message(message.chat.id, "❌ تم الإلغاء.", reply_markup=main_menu())
        return
    
    report = (
        f"🚨 **بلاغ عطل فني - كابوتا** 🚨\n"
        f"━━━━━━━━━━━━━━━\n"
        f"👤 **من:** {message.from_user.first_name}\n"
        f"🛠 **الوصف:**\n`{message.text}`\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⏰ يرجى المعالجة الفورية."
    )
    bot.send_message(ENGINEERS_GROUP_ID, report, parse_mode="Markdown")
    bot.send_message(message.chat.id, "✅ **تم رفع البلاغ بنجاح.**\nالمهندس في طريقه لموقعك في كابوتا.", reply_markup=main_menu(), parse_mode="Markdown")

bot.infinity_polling()
