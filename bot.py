import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from googleapiclient.discovery import build
from google.oauth2 import service_account

TOKEN = os.getenv("TOKEN")
FOLDER_ID = os.getenv("FOLDER_ID")

STATE_FILE = "state.txt"

SCOPES = ['https://www.googleapis.com/auth/drive']
creds = service_account.Credentials.from_service_account_file(
    'credentials.json', scopes=SCOPES)

drive = build('drive', 'v3', credentials=creds)

def get_videos():
    results = drive.files().list(
        q=f"'{FOLDER_ID}' in parents and mimeType contains 'video/'",
        fields="files(id, name)",
        orderBy="createdTime"
    ).execute()
    return results.get('files', [])

def get_index():
    if not os.path.exists(STATE_FILE):
        return 0
    return int(open(STATE_FILE).read())

def save_index(i):
    with open(STATE_FILE, "w") as f:
        f.write(str(i))

async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    videos = get_videos()
    i = get_index()

    if i >= len(videos):
        await update.message.reply_text("❌ Video finiti")
        return

    video = videos[i]
    link = f"https://drive.google.com/uc?id={video['id']}&export=download"

    await update.message.reply_text(f"🎬 {video['name']}\n{link}")

    save_index(i + 1)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("video", send_video))

app.run_polling()
