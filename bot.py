import datetime
import os
import telebot
from dotenv import load_dotenv
import redis
import requests

load_dotenv()
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Redis client
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD", None),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True
)

# Define states for conversation flow
STATES = {
    "START": "START",
    "SUBJECT": "SUBJECT",
    "CLASS_LEVEL": "CLASS_LEVEL",
    "TOPIC": "TOPIC",
    "WEEK_ENDING": "WEEK_ENDING",
    "CLS_SIZE": "CLS_SIZE",
    "DURATION": "DURATION",
    "DAYS": "DAYS",
    "WEEK": "WEEK",
    "PHONE_NUMBER": "PHONE_NUMBER",
    "EMAIL": "EMAIL",
    "CUSTOM_INSTRUCTIONS": "CUSTOM_INSTRUCTIONS",
    "CONFIRM": "CONFIRM",
}

# Define state order for navigation
STATE_ORDER = [
    STATES["START"],
    STATES["SUBJECT"],
    STATES["CLASS_LEVEL"],
    STATES["TOPIC"],
    STATES["WEEK_ENDING"],
    STATES["CLS_SIZE"],
    STATES["DURATION"],
    STATES["DAYS"],
    STATES["WEEK"],
    STATES["PHONE_NUMBER"],
    STATES["EMAIL"],
    STATES["CUSTOM_INSTRUCTIONS"],
    STATES["CONFIRM"],
]

# Handler functions for each state
def handle_start(message):
    chat_id = message.chat.id
    redis_client.hset(f"bot_user:{chat_id}", mapping={
        "state": STATES["SUBJECT"],
        "prev_state": STATES["START"]
    })
    bot.send_message(chat_id, "Welcome to the Lesson Notes Bot! Let's create lesson notes.\nWhat's the subject?")

def handle_subject(message):
    chat_id = message.chat.id
    subject = message.text.strip()
    if not subject:
        bot.send_message(chat_id, "Subject cannot be empty. Please provide a subject.")
        return
    redis_client.hset(f"bot_user:{chat_id}", mapping={
        "subject": subject,
        "state": STATES["CLASS_LEVEL"],
        "prev_state": STATES["SUBJECT"]
    })
    bot.send_message(chat_id, "Got it. What's the class level (e.g., Basic Eight)?")

def handle_class_level(message):
    chat_id = message.chat.id
    class_level = message.text.strip()
    if not class_level:
        bot.send_message(chat_id, "Class level cannot be empty. Please provide a class level.")
        return
    redis_client.hset(f"bot_user:{chat_id}", mapping={
        "class_level": class_level,
        "state": STATES["TOPIC"],
        "prev_state": STATES["CLASS_LEVEL"]
    })
    bot.send_message(chat_id, "What's the topic of the lesson?")

def handle_topic(message):
    chat_id = message.chat.id
    topic = message.text.strip()
    if not topic:
        bot.send_message(chat_id, "Topic cannot be empty. Please provide a topic.")
        return
    redis_client.hset(f"bot_user:{chat_id}", mapping={
        "topic": topic,
        "state": STATES["WEEK_ENDING"],
        "prev_state": STATES["TOPIC"]
    })
    bot.send_message(chat_id, "What's the week ending date (e.g., 16th May, 2025)?")

def handle_week_ending(message):
    chat_id = message.chat.id
    week_ending = message.text.strip()
    if not week_ending:
        bot.send_message(chat_id, "Week ending cannot be empty. Please provide a date.")
        return
    redis_client.hset(f"bot_user:{chat_id}", mapping={
        "week_ending": week_ending,
        "state": STATES["CLS_SIZE"],
        "prev_state": STATES["WEEK_ENDING"]
    })
    bot.send_message(chat_id, "Provide class sizes in format 'A:28 B:28 C:28'.")

def handle_cls_size(message):
    chat_id = message.chat.id
    cls_size_str = message.text.strip()
    try:
        cls_size = {pair.split(':')[0].strip(): int(pair.split(':')[1].strip()) for pair in cls_size_str.split()}
        if not all(isinstance(v, int) and v > 0 for v in cls_size.values()):
            raise ValueError
        redis_client.hset(f"bot_user:{chat_id}", mapping={
            "cls_size": str(cls_size),
            "state": STATES["DURATION"],
            "prev_state": STATES["CLS_SIZE"]
        })
        bot.send_message(chat_id, "What's the duration (e.g., 4 periods per class)?")
    except Exception:
        bot.send_message(chat_id, "Invalid class sizes. Please provide in format 'A:28 B:28 C:28'.")

def handle_duration(message):
    chat_id = message.chat.id
    duration = message.text.strip()
    if not duration:
        bot.send_message(chat_id, "Duration cannot be empty. Please provide a duration.")
        return
    redis_client.hset(f"bot_user:{chat_id}", mapping={
        "duration": duration,
        "state": STATES["DAYS"],
        "prev_state": STATES["DURATION"]
    })
    bot.send_message(chat_id, "What are the days (e.g., Monday - Friday)?")

def handle_days(message):
    chat_id = message.chat.id
    days = message.text.strip()
    if not days:
        bot.send_message(chat_id, "Days cannot be empty. Please provide the days.")
        return
    redis_client.hset(f"bot_user:{chat_id}", mapping={
        "days": days,
        "state": STATES["WEEK"],
        "prev_state": STATES["DAYS"]
    })
    bot.send_message(chat_id, "What's the week number (e.g., 3)?")

def handle_week(message):
    chat_id = message.chat.id
    week = message.text.strip()
    if not week.isdigit():
        bot.send_message(chat_id, "Week number must be a digit. Please provide a valid week number.")
        return
    redis_client.hset(f"bot_user:{chat_id}", mapping={
        "week": week,
        "state": STATES["PHONE_NUMBER"],
        "prev_state": STATES["WEEK"]
    })
    bot.send_message(chat_id, "What's your phone number (e.g., +233123456789)?")

def handle_phone_number(message):
    chat_id = message.chat.id
    phone_number = message.text.strip()
    if not phone_number.startswith('+233') or not phone_number[4:].isdigit() or len(phone_number) != 13:
        bot.send_message(chat_id, "Invalid phone number. Please provide in format +233 followed by 9 digits.")
        return
    redis_client.hset(f"user:{phone_number}", mapping={
        "chat_id": chat_id,
        "updated_at": datetime.datetime.now(datetime.UTC).isoformat()
    })
    redis_client.hset(f"bot_user:{chat_id}", mapping={
        "phone_number": phone_number,
        "state": STATES["EMAIL"],
        "prev_state": STATES["PHONE_NUMBER"]
    })
    bot.send_message(chat_id, "What's your email address?")

def handle_email(message):
    chat_id = message.chat.id
    email = message.text.strip()
    if not email:
        bot.send_message(chat_id, "Email cannot be empty. Please provide an email.")
        return
    redis_client.hset(f"bot_user:{chat_id}", mapping={
        "email": email,
        "state": STATES["CUSTOM_INSTRUCTIONS"],
        "prev_state": STATES["EMAIL"]
    })
    bot.send_message(chat_id, "Any custom instructions? (Send 'skip' to proceed.)")

def handle_custom_instructions(message):
    chat_id = message.chat.id
    custom_instructions = message.text.strip()
    if custom_instructions.lower() == 'skip':
        custom_instructions = ""
    redis_client.hset(f"bot_user:{chat_id}", mapping={
        "custom_instructions": custom_instructions,
        "state": STATES["CONFIRM"],
        "prev_state": STATES["CUSTOM_INSTRUCTIONS"]
    })
    user_data = redis_client.hgetall(f"bot_user:{chat_id}")
    summary = (
        f"Subject: {user_data['subject']}\n"
        f"Class Level: {user_data['class_level']}\n"
        f"Topic: {user_data['topic']}\n"
        f"Week Ending: {user_data['week_ending']}\n"
        f"Class Sizes: {user_data['cls_size']}\n"
        f"Duration: {user_data['duration']}\n"
        f"Days: {user_data['days']}\n"
        f"Week: {user_data['week']}\n"
        f"Phone Number: {user_data['phone_number']}\n"
        f"Email: {user_data['email']}\n"
        f"Custom Instructions: {user_data.get('custom_instructions', 'None')}"
    )
    bot.send_message(chat_id, f"Here's what you provided:\n{summary}\nSend 'yes' to confirm or 'no' to start over.")

def handle_confirm(message):
    chat_id = message.chat.id
    confirmation = message.text.strip().lower()
    if confirmation == 'yes':
        user_data = redis_client.hgetall(f"bot_user:{chat_id}")
        payload = {
            "subject": user_data["subject"],
            "class_level": user_data["class_level"],
            "topic": user_data["topic"],
            "week_ending": user_data["week_ending"],
            "cls_size": eval(user_data["cls_size"]),  # Convert string back to dict
            "duration": user_data["duration"],
            "days": user_data["days"],
            "week": user_data["week"],
            "phone_number": user_data["phone_number"],
            "email": user_data["email"],
            "custom_instructions": user_data.get("custom_instructions", ""),
        }
        try:
            # Replace <server-ip> with your actual server IP or domain
            response = requests.post("http://localhost:3000/lng/v1/generate-notes", json=payload, verify=False)
            print(response.status_code)
            print(response.text)
            if response.status_code == 201 or response.status_code == 200:
                bot.send_message(chat_id, f"Lesson notes is being generated. You will receive a notification once it's ready.")
            else:
                bot.send_message(chat_id, "Failed to generate lesson notes. Please try again later.")
        except Exception as e:
            bot.send_message(chat_id, "An error occurred. Please try again later.")
        redis_client.delete(f"bot_user:{chat_id}")
    elif confirmation == 'no':
        redis_client.delete(f"bot_user:{chat_id}")
        bot.send_message(chat_id, "Canceled. You can start over with /start.")
    else:
        bot.send_message(chat_id, "Please send 'yes' to confirm or 'no' to cancel.")

# Command handlers
@bot.message_handler(commands=['start', 'hello'])
def start_command(message):
    handle_start(message)

@bot.message_handler(commands=['restart'])
def restart_command(message):
    handle_start(message)

@bot.message_handler(commands=['prev'])
def prev_command(message):
    chat_id = message.chat.id
    user_data = redis_client.hgetall(f"bot_user:{chat_id}")
    current_state = user_data.get("state", STATES["START"])
    prev_state = user_data.get("prev_state", STATES["START"])

    if current_state == STATES["START"] or prev_state == STATES["START"]:
        bot.send_message(chat_id, "You're at the start. Use /start to begin.")
        return

    # Move to previous state
    redis_client.hset(f"bot_user:{chat_id}", "state", prev_state)
    # Update prev_state to the state before the previous state
    current_index = STATE_ORDER.index(prev_state)
    new_prev_state = STATE_ORDER[max(0, current_index - 1)]
    redis_client.hset(f"bot_user:{chat_id}", "prev_state", new_prev_state)

    # Prompt for the previous state's input
    prompts = {
        STATES["SUBJECT"]: "What's the subject?",
        STATES["CLASS_LEVEL"]: "What's the class level (e.g., Basic Eight)?",
        STATES["TOPIC"]: "What's the topic of the lesson?",
        STATES["WEEK_ENDING"]: "What's the week ending date (e.g., 16th May, 2025)?",
        STATES["CLS_SIZE"]: "Provide class sizes in format 'A:28 B:28 C:28'.",
        STATES["DURATION"]: "What's the duration (e.g., 4 periods per class)?",
        STATES["DAYS"]: "What are the days (e.g., Monday - Friday)?",
        STATES["WEEK"]: "What's the week number (e.g., 3)?",
        STATES["PHONE_NUMBER"]: "What's your phone number (e.g., +233123456789)?",
        STATES["EMAIL"]: "What's your email address?",
        STATES["CUSTOM_INSTRUCTIONS"]: "Any custom instructions? (Send 'skip' to proceed.)",
        STATES["CONFIRM"]: "Please review the summary and send 'yes' to confirm or 'no' to start over."
    }
    bot.send_message(chat_id, prompts.get(prev_state, "Please provide the input for the previous step."))

@bot.message_handler(commands=['cancel'])
def cancel(message):
    chat_id = message.chat.id
    redis_client.delete(f"bot_user:{chat_id}")
    bot.send_message(chat_id, "Canceled. You can start over with /start.")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "This bot helps you create lesson notes.\nCommands:\n/start or /restart - Begin or restart the process\n/prev - Go back to the previous step\n/cancel - Reset the process\n/help - Show this message")

# Main message handler to dispatch based on state
@bot.message_handler(func=lambda message: True)
def message_handler(message):
    chat_id = message.chat.id
    user_data = redis_client.hgetall(f"bot_user:{chat_id}")
    state = user_data.get("state", STATES["START"])

    handlers = {
        STATES["START"]: handle_start,
        STATES["SUBJECT"]: handle_subject,
        STATES["CLASS_LEVEL"]: handle_class_level,
        STATES["TOPIC"]: handle_topic,
        STATES["WEEK_ENDING"]: handle_week_ending,
        STATES["CLS_SIZE"]: handle_cls_size,
        STATES["DURATION"]: handle_duration,
        STATES["DAYS"]: handle_days,
        STATES["WEEK"]: handle_week,
        STATES["PHONE_NUMBER"]: handle_phone_number,
        STATES["EMAIL"]: handle_email,
        STATES["CUSTOM_INSTRUCTIONS"]: handle_custom_instructions,
        STATES["CONFIRM"]: handle_confirm,
    }
    handlers.get(state, handle_start)(message)

# Start the bot
bot.infinity_polling()