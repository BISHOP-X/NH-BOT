import os
import logging
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message
from downloader import NHentaiDownloader

# Load .env file if it exists (used in Termux/local)
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration from environment variables
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize Pyrogram client (supports 2GB files via MTProto)
app = Client(
    "nhentai_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Initialize downloader
downloader = NHentaiDownloader()


@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Welcome message"""
    await message.reply_text(
        "🔥 **NH PDF Downloader Bot**\n\n"
        "📖 **How to use:**\n"
        "Send me a 6-digit code and I'll download it as PDF\n\n"
        "**Examples:**\n"
        "• Just send: `123456`\n"
        "• Or use: `/d 123456`\n\n"
        "⚡ Powered by Pyrogram (supports up to 2GB files!)"
    )


@app.on_message(filters.command("d"))
async def download_command(client: Client, message: Message):
    """Handle /d command"""
    try:
        # Extract code from command
        if len(message.command) < 2:
            await message.reply_text("❌ Please provide a code!\n\nUsage: `/d 123456`")
            return
        
        code = message.command[1]
        await process_download(message, code)
    except Exception as e:
        logger.error(f"Error in download_command: {e}")
        await message.reply_text(f"❌ Error: {str(e)}")


@app.on_message(filters.text & filters.private)
async def text_handler(client: Client, message: Message):
    """Handle plain text messages (6-digit codes)"""
    code = message.text.strip()
    
    # Check if it's a valid 6-digit code
    if code.isdigit() and len(code) == 6:
        await process_download(message, code)
    elif code.isdigit():
        await message.reply_text("❌ Please send a valid 6-digit code!")


async def process_download(message: Message, code: str):
    """Process the download request"""
    try:
        # Validate code
        if not code.isdigit():
            await message.reply_text("❌ Code must be numeric!")
            return
        
        # Send processing message
        status_msg = await message.reply_text(
            f"⏳ Processing code: `{code}`\n\n"
            "⬇️ Fetching manga info..."
        )
        
        # Get manga info
        manga_info = downloader.get_manga_info(code)
        if not manga_info:
            await status_msg.edit_text("❌ Failed to fetch manga info. Invalid code or network issue.")
            return
        
        title, page_count, _server, _path = manga_info
        
        # Update status
        await status_msg.edit_text(
            f"📖 **{title}**\n\n"
            f"📄 Pages: {page_count}\n"
            f"⬇️ Downloading..."
        )
        
        # Download and convert to PDF
        pdf_path = downloader.download_and_convert(code, title, page_count)
        
        if not pdf_path or not os.path.exists(pdf_path):
            await status_msg.edit_text("❌ Failed to create PDF. Please try again.")
            return
        
        # Get file size
        file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
        
        # Update status - uploading
        await status_msg.edit_text(
            f"📖 **{title}**\n\n"
            f"📄 Pages: {page_count}\n"
            f"📦 Size: {file_size_mb:.2f} MB\n"
            f"⬆️ Uploading..."
        )
        
        # Send PDF file (Pyrogram supports up to 2GB!)
        await message.reply_document(
            document=pdf_path,
            caption=f"📖 **{title}**\n\n📄 Pages: {page_count}\n🔢 Code: `{code}`",
            file_name=f"{code}.pdf"
        )
        
        # Delete status message
        await status_msg.delete()
        
        # Clean up temporary PDF and folder
        try:
            temp_dir = os.path.dirname(pdf_path)
            os.remove(pdf_path)
            if os.path.isdir(temp_dir) and temp_dir.startswith("temp_"):
                os.rmdir(temp_dir)
            logger.info(f"Cleaned up: {pdf_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {pdf_path}: {e}")
            
    except Exception as e:
        logger.error(f"Error processing download for code {code}: {e}")
        await message.reply_text(
            f"❌ **Error:**\n`{str(e)}`\n\n"
            "Please try again or contact support."
        )


@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Show help message"""
    await message.reply_text(
        "🔥 **NH PDF Downloader Bot**\n\n"
        "**Commands:**\n"
        "• `/start` - Start the bot\n"
        "• `/d <code>` - Download by code\n"
        "• `/help` - Show this message\n\n"
        "**Quick Download:**\n"
        "Just send any 6-digit code directly!\n\n"
        "**Features:**\n"
        "✅ Fast concurrent downloads\n"
        "✅ Automatic PDF conversion\n"
        "✅ Supports files up to 2GB\n"
        "✅ Clean and organized output"
    )


if __name__ == "__main__":
    logger.info("🚀 Starting NH PDF Bot...")
    logger.info(f"Bot configured with API_ID: {API_ID}")
    app.run()
