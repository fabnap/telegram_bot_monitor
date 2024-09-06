#!/bin/bash

# Set your Telegram bot token and chat ID
TELEGRAM_BOT_TOKEN=""
TELEGRAM_CHAT_ID1="" # group

TELEGRAM_CHAT_ID2=""  # fabrizio 
# Set the URL of the website you want to monitor
WEBSITE_URL="http://___the_prometheus_ip___:___prometh_port___/metrics"

# Set the word you want to check
WORD_TO_CHECK="xxx"

check_for_word() {
    # Fetch the current webpage content
    CURRENT_PAGE=$(curl -s $WEBSITE_URL)

    # Check if the word is in the webpage content
    if echo "$CURRENT_PAGE" | grep -q "$WORD_TO_CHECK"; then
        # Send a message to the Telegram chat
        echo "CZT is running"
    else
        curl -s -X POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage -d chat_id=$TELEGRAM_CHAT_ID1 -d text="CZT is NOT running. Stop me with /stop_cztchecker"
    fi
}

# Run the script every two hours
while true; do
    check_for_word
    sleep 15m
done