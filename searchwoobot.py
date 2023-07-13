import telebot
import pymysql
import os



# Replace YOUR_BOT_TOKEN with your bot's token
bot = telebot.TeleBot("YourTokenHere")

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(message.chat.id, "Hi there, I'm a Telegram bot that bulk searches for products in your WooCommerce store. To use me, send me product name with values separated by commas.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(message.from_user.id)

    # Split the values by comma, ignoring whitespaces
    values = [value.strip() for value in message.text.split(",")]

    # Send a message to the user to inform them that the search is being prepared
    bot.send_message(message.chat.id, 'Please wait while I prepare your results...')

    try:
        # Connect to the WooCommerce database
        conn = pymysql.connect(
            host='yourhost',
            user='db_username',
            password='db_password',
            database='wordpress_db_name'
        )

        # Loop through each value and execute a MySQL query to search for products
        for value in values:
            with conn.cursor() as cursor:
                cursor.execute(
                    'SELECT post_name FROM wp_posts WHERE post_type = %s AND (post_title LIKE %s OR post_content LIKE %s OR post_excerpt LIKE %s)',
                    ('product', f'%{value}%', f'%{value}%', f'%{value}%')
                )
                result = cursor.fetchall()

            # If a product is found, prompt the URL
            if result:
                for product in result:
                    product_url = f"https://www.websiteurl.com/shop/{product['post_name']}"
                    bot.send_message(message.chat.id, f"Product found: {product_url}")
                    print(f"Product found: {product_url}")
            else:
                bot.send_message(message.chat.id, f"No product found for value: {value}")
                print(f"No product found for value: {value}")

        # Close the connection
        conn.close()
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'An error occurred. Please try again later.')

@bot.polling()
def handle_polling_error(error):
    print(error)

