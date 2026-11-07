import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- 1. Load and auto-update data ---
FILE_PATH = 'subscribers.txt'
df = None

def load_data():
    global df
    try:
        df = pd.read_csv(FILE_PATH, sep=';', dtype=str, on_bad_lines='skip')
        print("[SUCCESS] Subscribers file loaded and updated.")
    except Exception as e:
        print(f"[ERROR] Failed to read file: {e}")

load_data()

class FileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(FILE_PATH):
            print("[INFO] File modified, updating data instantly...")
            load_data()

observer = Observer()
observer.schedule(FileHandler(), path='.', recursive=False)
observer.start()

# --- 2. Search function ---
def check_subscription(subscriber_id):
    global df
    if df is None:
        return "Sorry, database is currently unavailable."
    
    sub_id = str(subscriber_id).strip().zfill(6)
    result = df[df['Subscriber ID'] == sub_id]
    
    if not result.empty:
        status = result.iloc[0]['Status']
        paid_till = result.iloc[0]['Paid till']
        name = result.iloc[0].get('Name', '')
        
        msg = f"Subscription Details:\n"
        if pd.notna(name) and str(name).strip() != '':
            msg += f"👤 Name: {name}\n"
        msg += f"📌 Status: {status}\n"
        msg += f"📅 Valid Till: {paid_till}"
        return msg
    else:
        return "Sorry, subscriber ID not found. Please check the number and try again."

# --- 3. Telegram handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Please send your Subscriber ID to check your subscription status.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    reply = check_subscription(user_text)
    await update.message.reply_text(reply)

# --- 4. Run bot ---
if __name__ == '__main__':
    TOKEN = "9287900195:AAGD6ZqLSobq8dHiGJRk0UOVy2hrBogilik"
    
    app = ApplicationBuilder().token(TOKEN).read_timeout(30).write_timeout(30).connect_timeout(30).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Telegram bot is running and monitoring the file automatically...")
    app.run_polling()