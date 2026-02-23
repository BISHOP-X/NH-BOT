#!/bin/bash
# NH BOT - Termux One-Time Setup Script
# Run this ONCE to install everything

echo "========================================="
echo "   NH PDF Bot - Termux Setup"
echo "========================================="

# Update packages
echo "[1/6] Updating packages..."
pkg update -y && pkg upgrade -y

# Install required packages
echo "[2/6] Installing Python and Git..."
pkg install -y python git

# Clone the repo
echo "[3/6] Cloning bot repo..."
git clone https://github.com/BISHOP-X/NH-BOT
cd NH-BOT

# Install Python dependencies
echo "[4/6] Installing Python packages..."
pip install -r requirements.txt

# Create .env file with credentials
echo "[5/6] Setting up credentials..."
cat > .env << 'EOF'
TELEGRAM_API_ID=31146988
TELEGRAM_API_HASH=390cb38783524c22eeac03f7c686919e
TELEGRAM_BOT_TOKEN=8513146174:AAHTAHnBZuS5uQMIygqVOnw5BfQrXvvZcgo
EOF

# Create start script
echo "[6/6] Creating start script..."
cat > start.sh << 'STARTEOF'
#!/bin/bash
cd ~/NH-BOT
echo "Starting NH PDF Bot..."
python bot.py
STARTEOF
chmod +x start.sh

echo ""
echo "========================================="
echo "   Setup Complete!"
echo "========================================="
echo ""
echo "To START the bot, run:"
echo "   bash ~/NH-BOT/start.sh"
echo ""
echo "Or add shortcut - run this:"
echo "   echo 'alias nhbot=\"bash ~/NH-BOT/start.sh\"' >> ~/.bashrc && source ~/.bashrc"
echo ""
echo "Then just type: nhbot"
echo "========================================="
