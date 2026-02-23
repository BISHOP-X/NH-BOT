# NHentai Telegram Bot

A Telegram bot that downloads nhentai content and converts it to PDF files. Uses Pyrogram (MTProto) to support file uploads up to **2GB** (vs 50MB limit with standard Bot API).

## Features

- ✅ Download by 6-digit code
- ✅ Automatic PDF conversion
- ✅ Concurrent image downloading (6 workers)
- ✅ Support for multiple image formats (PNG, JPG, WebP)
- ✅ Up to 2GB file uploads via MTProto
- ✅ Clean temporary file management
- ✅ Deploy to Render for 24/7 operation

## Setup Instructions

### 1. Get Telegram Credentials

#### A. Get API ID and API Hash
1. Go to https://my.telegram.org/apps
2. Log in with your phone number
3. Click "API development tools"
4. Create a new application (any name/description)
5. Copy your `api_id` and `api_hash`

#### B. Create a Bot
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Local Testing (Optional)

```bash
# Clone/navigate to the project
cd nhentai-downloader

# Install dependencies
pip install -r requirements.txt

# Copy .env.example to .env
cp .env.example .env

# Edit .env with your credentials
# TELEGRAM_API_ID=your_api_id
# TELEGRAM_API_HASH=your_api_hash
# TELEGRAM_BOT_TOKEN=your_bot_token

# Run the bot locally
python bot.py
```

### 3. Deploy to Render

#### Option A: Deploy via Dashboard

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will detect `render.yaml` automatically
5. Add environment variables:
   - `TELEGRAM_API_ID` - Your API ID
   - `TELEGRAM_API_HASH` - Your API hash
   - `TELEGRAM_BOT_TOKEN` - Your bot token
6. Click **"Apply"**

#### Option B: Deploy via Git

1. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. In Render Dashboard:
   - Click **"New +"** → **"Web Service"**
   - Connect your repository
   - Select the repository
   - Configure:
     - **Name**: nhentai-telegram-bot
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python bot.py`
   - Add environment variables (see above)
   - Click **"Create Web Service"**

### 4. Use the Bot

1. Open Telegram and search for your bot (using the username you set)
2. Send `/start` to begin
3. Send a 6-digit code, e.g., `123456`
4. Wait for the bot to download and send the PDF

#### Commands

- `/start` - Welcome message
- `/help` - Show help
- `/d <code>` - Download by code
- Or just send a 6-digit code directly!

## Project Structure

```
nhentai-downloader/
├── bot.py                 # Main Telegram bot (Pyrogram)
├── downloader.py          # Download logic & PDF conversion
├── download nhentai.py    # Original CLI version
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment config
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Technical Details

### Why Pyrogram?

Pyrogram uses the **MTProto protocol** (Telegram's native API), which allows:
- **2GB file uploads** (vs 50MB with standard Bot API)
- Direct server-to-server communication
- Better performance for large files

### Dependencies

- `pyrogram` - Telegram MTProto client
- `TgCrypto` - Crypto for Pyrogram (speeds up encryption)
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests
- `Pillow` - Image processing
- `img2pdf` - PDF conversion
- `dnspython` - DNS resolution

### Render Configuration

The bot is configured as a **Web Service** on Render:
- **Region**: Oregon (change in `render.yaml`)
- **Plan**: Free tier (can upgrade for better performance)
- **Auto-deploy**: Enabled (deploys on git push)
- **Health check**: Disabled (bot doesn't need HTTP endpoint)

## Troubleshooting

### Bot not responding
- Check Render logs for errors
- Verify environment variables are set correctly
- Ensure bot token is valid

### Download fails
- Some codes may not exist or be invalid
- Network issues with nhentai servers
- Try changing DNS in `downloader.py`

### File too large error
- Pyrogram supports up to 2GB
- Check available disk space on Render
- Large PDFs may take longer to upload

### Render keeps restarting
- Free tier instances spin down after inactivity
- They restart when receiving new requests
- First message after restart may be slow

## Free Tier Limitations

Render's free tier includes:
- ✅ 750 hours/month runtime
- ✅ Automatic HTTPS
- ✅ Auto-deploys from Git
- ⚠️ Spins down after 15 min inactivity
- ⚠️ Limited CPU/memory

For 24/7 operation without spin-down, upgrade to a paid plan ($7/month).

## Security Notes

- Never commit `.env` file to Git
- Keep your API credentials private
- Bot has full access to conversations (use private chats)
- Downloaded files are temporarily stored, then deleted

## License

MIT License - Use at your own risk

## Disclaimer

This tool is for educational purposes. Ensure you comply with nhentai's terms of service and applicable laws in your jurisdiction.
