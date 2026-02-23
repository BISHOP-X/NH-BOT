#!/bin/bash
# NH BOT - Full Auto Setup (run once, bot starts on every phone boot)

pkg update -y && pkg install -y python git termux-services
git clone https://github.com/BISHOP-X/NH-BOT ~/NH-BOT
cd ~/NH-BOT
pip install -r requirements.txt

# Save credentials
cat > ~/NH-BOT/.env << 'EOF'
TELEGRAM_API_ID=31146988
TELEGRAM_API_HASH=390cb38783524c22eeac03f7c686919e
TELEGRAM_BOT_TOKEN=8513146174:AAHTAHnBZuS5uQMIygqVOnw5BfQrXvvZcgo
EOF

# Setup auto-start on boot via Termux:Boot
mkdir -p ~/.termux/boot
cat > ~/.termux/boot/start-nhbot.sh << 'BOOTEOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/NH-BOT
python bot.py &
BOOTEOF
chmod +x ~/.termux/boot/start-nhbot.sh

echo ""
echo "✅ DONE! Bot will now start automatically every time your phone boots."
echo "➡️  Install Termux:Boot from F-Droid to activate auto-start."
echo "➡️  Then restart your phone - bot will run in background forever."
