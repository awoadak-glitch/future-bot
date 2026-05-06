import telebot
import re
import os
import time
from telebot import types
from google import genai

# --- الإعدادات المباشرة ---
TELEGRAM_TOKEN = '8640971249:AAExWw_HSrylYVdMk8Fz-R3DPg0UdMfScxY'
GEMINI_KEY = 'AIzaSyABZMq8soZFuB0esoKvfbyl9_hNY7qPfx4'
MY_PERSONAL_ID = 7098691973
ENGINEERS_GROUP_ID = -1003817618471 
LOGO_URL = "https://i.imgur.com/8f8v9K4.png" 

VIDEO_TPLINK = "https://github.com/awoadak-glitch/future-bot/raw/main/tplink.mp4"
VIDEO_OTHER = "https://github.com/awoadak-glitch/future-bot/raw/main/other.mp4"

client = genai.Client(api_key=GEMINI_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- نظام قاعدة بيانات بسيطة (ملف نصي) ---
USERS_FILE = "users.txt"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_user(user_id):
    users = load_users()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

user_context = {}

# --- دوال المنيو ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🆕 اشتراك جديد', '🚨 بلاغ عطل', '📊 الأسعار والباقات', '🛠 برمجة الراوتر')
    return markup

def programming_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('TP-Link 🌐', 'نوع آخر 📶', '🔙 رجوع للقائمة')
    return markup

# --- ميزة المنشن في جروب المهندسين للإذاعة العامة ---
@bot.message_handler(func=lambda m: m.chat.id == ENGINEERS_GROUP_ID and m.text and f"@{bot.get_me().username}" in m.text)
def handle_broadcast(message):
    # استخراج النص بدون المنشن
    raw_text = message.text.replace(f"@{bot.get_me().username}", "").strip()
    
    if not raw_text:
        bot.reply_to(message, "⚠️ يا هندسة، اكتب نص الرسالة مع المنشن عشان أرسلها للكل.")
        return

    users = load_users()
    bot.reply_to(message, f"⏳ جاري الإرسال إلى {len(users)} مشترك...")
    
    count = 0
    for user_id in users:
        try:
            bot.send_message(user_id, f"📢 **إعلان من المستقبل نت:**\n\n{raw_text}", parse_mode="Markdown")
            count += 1
            time.sleep(0.05) # حماية من الحظر
        except:
            continue
    
    bot.send_message(ENGINEERS_GROUP_ID, f"✅ تم الإرسال بنجاح لـ {count} مشترك.")

# --- استقبال الرسائل الخاصة ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.chat.id)
    bot.send_photo(message.chat.id, LOGO_URL, caption="مرحباً بك في **مؤسسة المستقبل نت (كابوتا)** 🌐\nاختر الخدمة المطلوبة:", reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.chat.type == 'private' and m.text)
def handle_logic(message):
    cid = message.chat.id
    save_user(cid) # تسجيل المستخدم تلقائياً
    u_text = message.text.strip()
    u_text_low = u_text.lower()

    if u_text == '📊 الأسعار والباقات':
        PRICES_INFO = "🌐 **باقات المستقبل نت:**\n200 ريال (كرت البيض)\n500 ريال (باقة البطاط)\n1000 ريال (باقة الدجاج)\n📍 المنصورة - كابوتا"
        bot.send_message(cid, PRICES_INFO, parse_mode="Markdown")
        return

    if u_text == '🛠 برمجة الراوتر':
        bot.send_message(cid, "اختر نوع الراوتر:", reply_markup=programming_menu())
        return

    if u_text == '🔙 رجوع للقائمة':
        bot.send_message(cid, "القائمة الرئيسية:", reply_markup=main_menu())
        return

    if u_text == 'TP-Link 🌐':
        bot.send_message(cid, "جاري إرسال فيديو الشرح... ⏳")
        try: bot.send_video(cid, VIDEO_TPLINK, caption="🎬 شرح برمجة TP-Link")
        except: bot.send_message(cid, "⚠️ تعذر تحميل الفيديو.")
        return

    if u_text == 'نوع آخر 📶':
        bot.send_message(cid, "جاري إرسال فيديو الشرح... ⏳")
        try: bot.send_video(cid, VIDEO_OTHER, caption="🎬 شرح برمجة راوتر")
        except: bot.send_message(cid, "⚠️ تعذر تحميل الفيديو.")
        return

    if cid in user_context:
        validate_and_process(message)
        return

    if any(word in u_text_low for word in ["اشتراك", "نت جديد"]) or u_text == '🆕 اشتراك جديد':
        user_context[cid] = "waiting_order"
        bot.send_message(cid, "📝 **طلب اشتراك**\nأرسل (اسمك + موقعك + رقمك) بوضوح.")
        return

    if any(word in u_text_low for word in ["عطل", "بلاغ"]) or u_text == '🚨 بلاغ عطل':
        user_context[cid] = "waiting_complaint"
        bot.send_message(cid, "🛠 **فتح بلاغ**\nاكتب اسمك وموقعك ووصف المشكلة.")
        return

    try:
        res = client.models.generate_content(model="gemini-2.0-flash", contents=f"زبون يقول {u_text}. رد بلهجة عدنية.")
        bot.send_message(cid, res.text)
    except:
        bot.send_message(cid, "كيف نخدمك؟ استخدم الأزرار بالأسفل.")

def validate_and_process(message):
    cid = message.chat.id
    state = user_context[cid]
    u_text = message.text.strip()

    # الفلتر المحلي الذكي
    if len(u_text) < 10 or not any(char.isdigit() for char in u_text) or re.match(r'^[\W_]+$', u_text):
        bot.send_message(cid, "⚠️ البيانات غير كافية. يرجى كتابة (الاسم، الموقع، ورقم الجوال) بوضوح.")
        return

    tag = "🆕 **اشتراك جديد**" if state == "waiting_order" else "🚨 **بلاغ عطل**"
    report = f"{tag}\n👤 العميل: {message.from_user.first_name}\n📝 التفاصيل: {u_text}\n⏰ {time.strftime('%H:%M')}"
    
    bot.send_message(ENGINEERS_GROUP_ID, report, parse_mode="Markdown")
    if state == "waiting_order": bot.send_message(MY_PERSONAL_ID, report)
    
    bot.send_message(cid, "✅ تم استلام بياناتك بنجاح. فريق كابوتا بيتواصل بك قريباً.", reply_markup=main_menu())
    del user_context[cid]

bot.infinity_polling()
