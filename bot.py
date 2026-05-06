import telebot
from telebot import types
from google import genai
import time

# --- الإعدادات المباشرة ---
TELEGRAM_TOKEN = '8640971249:AAExWw_HSrylYVdMk8Fz-R3DPg0UdMfScxY'
GEMINI_KEY = 'AIzaSyABZMq8soZFuB0esoKvfbyl9_hNY7qPfx4'
MY_PERSONAL_ID = 7098691973
ENGINEERS_GROUP_ID = -1003817618471 
LOGO_URL = "https://i.imgur.com/8f8v9K4.png" 

# روابط الفيديوهات المباشرة من مستودعك في GitHub
# ملاحظة: تم تعديل الرابط لاستخدام raw ليعمل الفيديو مباشرة
VIDEO_TPLINK = "https://github.com/awoadak-glitch/future-bot/raw/main/tplink.mp4"
VIDEO_OTHER = "https://github.com/awoadak-glitch/future-bot/raw/main/other.mp4"

client = genai.Client(api_key=GEMINI_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

registered_users = set()
user_context = {}

# --- خزان الكلمات (نفس كودك السابق) ---
ORDER_WORDS = ["اشتراك", "نت جديد", "توصيل", "بكم", "باقات"]
COMPLAINT_WORDS = ["بلاغ", "عطل", "مشكلة", "طافي", "خربان"]
CANCEL_WORDS = ["الغاء", "بطلت", "تراجع"]

PRICES_INFO = """
🌐 **باقات المستقبل نت - المنصورة / كابوتا:**
🎟️ **200 ريال** ⬅️ 750 ميجا (يومان)
🎟️ **500 ريال** ⬅️ 1900 ميجا (أسبوع)
🎟️ **1000 ريال** ⬅️ 3900 ميجا (أسبوعان)
🎟️ **3000 ريال** ⬅️ 12.5 جيجا (شهر)
🎟️ **6000 ريال** ⬅️ 24 جيجا (شهر)
📍 *موقعنا: المنصورة - كابوتا*
"""

# --- دوال الأزرار ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('🆕 اشتراك جديد', '🚨 بلاغ عطل', '📊 الأسعار والباقات', '🛠 برمجة الراوتر')
    return markup

def programming_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('TP-Link 🌐', 'نوع آخر 📶', '🔙 رجوع للقائمة')
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    registered_users.add(message.chat.id)
    user_context.pop(message.chat.id, None)
    bot.send_photo(message.chat.id, LOGO_URL, caption="مرحباً بك في **مؤسسة المستقبل نت (كابوتا)** 🌐\nاختر الخدمة المطلوبة:", reply_markup=main_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.chat.type == 'private' and m.text)
def handle_logic(message):
    cid = message.chat.id
    u_text = message.text.strip()
    u_text_low = u_text.lower()
    registered_users.add(cid)

    # --- إدارة القوائم ---
    if u_text == '📊 الأسعار والباقات':
        bot.send_message(cid, PRICES_INFO, parse_mode="Markdown")
        return

    if u_text == '🛠 برمجة الراوتر':
        bot.send_message(cid, "اختر نوع الراوتر لمشاهدة فيديو الشرح:", reply_markup=programming_menu())
        return

    if u_text == '🔙 رجوع للقائمة':
        bot.send_message(cid, "تم العودة للقائمة الرئيسية:", reply_markup=main_menu())
        return

    # --- إرسال الفيديوهات من GitHub ---
    if u_text == 'TP-Link 🌐':
        bot.send_message(cid, "جاري إرسال فيديو شرح TP-Link... ⏳")
        try:
            bot.send_video(cid, VIDEO_TPLINK, caption="🎬 شرح برمجة راوتر TP-Link\n(المستقبل نت - كابوتا)")
        except:
            bot.send_message(cid, "⚠️ عذراً، تعذر تحميل الفيديو. تأكد من وجود tplink.mp4 في المستودع.")
        return

    if u_text == 'نوع آخر 📶':
        bot.send_message(cid, "جاري إرسال فيديو شرح النوع الآخر... ⏳")
        try:
            bot.send_video(cid, VIDEO_OTHER, caption="🎬 شرح برمجة راوتر (نوع آخر)\n(المستقبل نت - كابوتا)")
        except:
            bot.send_message(cid, "⚠️ عذراً، تعذر تحميل الفيديو. تأكد من وجود other.mp4 في المستودع.")
        return

    # --- منطق البلاغات والاشتراكات ---
    if any(word in u_text_low for word in CANCEL_WORDS):
        user_context.pop(cid, None)
        bot.send_message(cid, "تم إلغاء العملية. 👍", reply_markup=main_menu())
        return

    if cid in user_context:
        validate_and_process(message)
        return

    if any(word in u_text_low for word in ORDER_WORDS) or u_text == '🆕 اشتراك جديد':
        user_context[cid] = "waiting_order"
        bot.send_message(cid, "📝 **طلب اشتراك جديد**\nأرسل (اسمك + موقعك + رقمك) في رسالة واحدة.")
        return

    if any(word in u_text_low for word in COMPLAINT_WORDS) or u_text == '🚨 بلاغ عطل':
        user_context[cid] = "waiting_complaint"
        bot.send_message(cid, "🛠 **فتح بلاغ صيانة**\nاكتب (اسمك + موقعك + وصف المشكلة).")
        return

    # رد الذكاء الاصطناعي
    try:
        res = client.models.generate_content(model="gemini-2.0-flash", contents=f"زبون يقول {u_text}. رد بلهجة عدنية.")
        bot.send_message(cid, res.text, reply_markup=main_menu())
    except:
        bot.send_message(cid, "كيف نخدمك؟ استخدم الأزرار بالأسفل.", reply_markup=main_menu())

def validate_and_process(message):
    cid = message.chat.id
    state = user_context[cid]
    u_text = message.text.strip()
    
    tag = "🆕 **اشتراك جديد**" if state == "waiting_order" else "🚨 **بلاغ عطل**"
    report = f"{tag} (كابوتا)\n👤 العميل: {message.from_user.first_name}\n📝 التفاصيل: {u_text}\n⏰ {time.strftime('%H:%M')}"
    
    bot.send_message(ENGINEERS_GROUP_ID, report, parse_mode="Markdown")
    if state == "waiting_order": bot.send_message(MY_PERSONAL_ID, report)
    
    bot.send_message(cid, "✅ تم استلام بياناتك بنجاح. فريق كابوتا بيتواصل بك.", reply_markup=main_menu())
    del user_context[cid]

bot.infinity_polling()
