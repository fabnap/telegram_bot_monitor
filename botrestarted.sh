#!/bin/bash

# sleep 10

# Set your Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN=""
TELEGRAM_CHAT_ID1=""



# Get the status of the bot service
BOT_SERVICE_STATUS=$(systemctl is-active telegramMain.service)

# Send a message to the Telegram chat
curl -s -X POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage -d chat_id=$TELEGRAM_CHAT_ID1 -d text="INFO: bot restarted. Status of the Bot: $BOT_SERVICE_STATUS. This is a watchdog script. *** You have to start the bot again with /start ***. If not starting, please pay attention to the experimental parameters. If daytime notify the Run Coordinator."

echo "Bot restarted. Status of the Bot: $BOT_SERVICE_STATUS" >> /home/fabrizio/telegramnotifs/botkilled.log