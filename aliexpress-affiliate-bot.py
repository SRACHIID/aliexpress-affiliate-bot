import requests
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import time

# Your API Credentials from the Image
TELEGRAM_BOT_TOKEN = "7601389265AAHMx6qeOsHjO7dCKgXcfYEXGcfLZw5lXNM"  # Replace with your actual bot token
APP_KEY = "512774"  # From the screenshot
AFFILIATE_ID = "_oBQINda"  # Your AliExpress affiliate ID
CHANNEL_ID = "@TopDealsEverBot"  # Your actual channel username

# Convert normal AliExpress links to affiliate links
def convert_to_affiliate_link(product_url):
    api_url = "https://api.aliexpress.com/sync?method=aliexpress.affiliate.link.generate"
    params = {
        "app_key": APP_KEY,
        "sign_method": "md5",
        "format": "json",
        "fields": "promotion_link",
        "source_values": product_url,
        "tracking_id": AFFILIATE_ID,
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        try:
            return data["aliexpress_affiliate_link_generate_response"]["promotion_link"]
        except KeyError:
            return "❌ Failed to convert link."
    return "⚠️ API request failed."

# Fetch trending & discounted products
def get_trending_products():
    api_url = "https://api.aliexpress.com/sync?method=aliexpress.affiliate.hotproduct.query"
    params = {
        "app_key": APP_KEY,
        "format": "json",
        "fields": "product_title,product_url,sale_price,image_url",
        "tracking_id": AFFILIATE_ID,
        "sort": "volumeDown",
        "page_size": 5
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        try:
            return data["aliexpress_affiliate_hotproduct_query_response"]["products"]
        except KeyError:
            return []
    return []

# Handle user messages for affiliate link conversion
def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text
    if "aliexpress.com/item" in user_message:
        update.message.reply_text("🔄 Converting your link...")
        affiliate_link = convert_to_affiliate_link(user_message)
        update.message.reply_text(f"✅ Here is your affiliate link: {affiliate_link}")
    else:
        update.message.reply_text("⚠️ Please send a valid AliExpress product link.")

# Send trending products in response to the /trending command
def send_trending_products(update: Update, context: CallbackContext):
    update.message.reply_text("🔄 Fetching trending deals...")
    products = get_trending_products()
    if not products:
        update.message.reply_text("❌ No trending products found.")
        return
    for product in products:
        message = f"🔥 *{product['product_title']}*\n💰 Price: {product['sale_price']}\n🔗 [Buy Now]({product['product_url']})"
        context.bot.send_photo(chat_id=update.message.chat_id, photo=product["image_url"], caption=message, parse_mode="Markdown")

# Auto-post trending deals to your Telegram channel
def auto_post_trending():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    while True:
        products = get_trending_products()
        if products:
            for product in products:
                message = f"🔥 *{product['product_title']}*\n💰 Price: {product['sale_price']}\n🔗 [Buy Now]({product['product_url']})"
                bot.send_photo(chat_id=CHANNEL_ID, photo=product["image_url"], caption=message, parse_mode="Markdown")
        time.sleep(86400)  # Post once every 24 hours

# Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 Welcome! Send me an AliExpress product link, and I'll convert it into an affiliate link. Use /trending to get hot deals!")

# Main bot function
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("trending", send_trending_products))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
