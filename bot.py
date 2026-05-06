import telebot
from google import genai
import time

# الإعدادات - تم حذف البروكسي لأنه غير مطلوب في Render
TELEGRAM_TOKEN = '8640971249:AAEtUNa9LlAQe3uSxHPpY3sWXTtsZ39XKlM'
GEMINI_KEY = 'AIzaSyABZMq8soZFuB0esoKvfbyl9_hNY7qPfx4'
MY_PERSONAL_ID = 7098691973
ENGINEERS_GROUP_ID = -1003817618471 

client = genai.Client(api_key=GEMINI_KEY)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ترسانة التوقعات المحلية (100+ كلمة)
ORDER_WORDS = ["اشتراك", "اشترك", "ركب", "نت جديد", "خط جديد", "توصيل", "واير", "بكم", "سعر", "عروض", "باقات", "مودم", "راوتر", "أشتي نت", "واي فاي", "تفعيل"]
COMPLAINT_WORDS = ["بلاغ", "عطل", "مشكلة", "طافي", "مقطوع", "خربان", "صلح", "صيانة", "ضعيف", "بطيء", "يفصل", "النت زفت", "انقطع", "اللمبة حمراء"]
GREETING_WORDS = ["السلام", "هلا", "مرحبا", "سلام", "حياك", "يا هندسة", "صباح الخير", "مساء الخير", "قوة", "اللو"]

user_context = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_context.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "مرحباً بك في (المستقبل نت) 🌐\n\nتفضل يا غالي، هل تريد اشتراك جديد؟ أم لديك بلاغ عن مشكلة؟")

@bot.message_handler(func=lambda m: m.chat.type == 'private' and m.text)
def handle_logic(message):
    cid = message.chat.id
    u_text = message.text.lower()

    if cid in user_context:
        process_final_data(message)
        return

    if any(word in u_text for word in ORDER_WORDS):
        user_context[cid] = "waiting_order"
        bot.send_message(cid, "أبشر بعزك، بنركب لك أحسن خط. ✅\nأرسل الآن (اسمك الكامل + منطقتك + رقم هاتفك) في رسالة واحدة.")
        return

    if any(word in u_text for word in COMPLAINT_WORDS):
        user_context[cid] = "waiting_complaint"
        bot.send_message(cid, "ولا يهمك، فريق الصيانة بيتحرك الآن. 🛠️\nاكتب (اسمك + موقعك + وصف العطل) لرفع البلاغ.")
        return

    if any(word in u_text for word in GREETING_WORDS):
        bot.send_message(cid, "يا هلا وغلا بك في المستقبل نت! أؤمرني، أشتي تركب نت جديد ولا معك بلاغ؟")
        return

    try:
        ai_res = client.models.generate_content(model="gemini-2.0-flash", contents=f"الزبون يقول: {u_text}. رد بلهجة يمنية محترمة واسأله هل يريد (اشتراك جديد) أم (بلاغ عطل).").text
        bot.send_message(cid, ai_res)
    except:
        bot.send_message(cid, "يا غالي تفضل، هل تريد اشتراك جديد أم بلاغ عطل؟")

def process_final_data(message):
    cid = message.chat.id
    state = user_context[cid]
    
    # تنسيق الرسالة لترسل للجروب ولك شخصياً
    report_type = "اشتراك جديد" if state == "waiting_order" else "بلاغ عطل"
    report = f"📦 **{report_type}**\n\n👤 البيانات:\n{message.text}"
    
    bot.send_message(ENGINEERS_GROUP_ID, report)
    if state == "waiting_order":
        bot.send_message(MY_PERSONAL_ID, report)
        
    bot.send_message(cid, "تم استلام بياناتك بنجاح، فريقنا بيتواصل بك الآن.")
    del user_context[cid]

bot.infinity_polling()
