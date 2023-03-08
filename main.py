import mysql.connector
import queue
import threading
import socket
from time import sleep
import re
import select
import requests

nickname = 'USERNAME'
token = 'OAUTH TOKEN'
channel = '#CHANNEL'
clientID = 'clientid'
apptoken = "token"

cnx_pool = mysql.connector.pooling.MySQLConnectionPool(
    host="",
    user="",
    password="",
    database=""
)

server = 'irc.chat.twitch.tv'
port = 6667

message_queue = queue.Queue()
unprocessedqueue = queue.Queue()

def send_message(sock, message):
    sock.send((message + "\r\n").encode())

def connect_to_server():
    sock = socket.socket()
    sock.connect((server, port))
    send_message(sock, f"PASS {token}")
    send_message(sock, f"NICK {nickname}")
    send_message(sock, f"JOIN {channel}")
    return sock 

def ping(sock):
    while True:
        send_message(sock, "PING :tmi.twitch.tv")
        sleep(30)

def write_to_database(message_queue):
    while True:
        if not message_queue.empty():
            username, message, live = message_queue.get()

            cnx = cnx_pool.get_connection()

            cursor = cnx.cursor()
            add_record = ("INSERT INTO twitch_logs "
              "(channel_live, username, message) "
              "VALUES (%s, %s, %s)")
            record_data = (live, username, message)
            cursor.execute(add_record, record_data)

            print(f"Inserting: {live}, {username}, {message}")

            cnx.commit()

            cursor.close()
            cnx.close()

            message_queue.task_done()
        else:
            sleep(0.5)

def process_messages(unprocessedqueue):
    regex = re.compile(r":(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.+)")
    while True:
        if not unprocessedqueue.empty():
            data = unprocessedqueue.get()
            if data.startswith("PING"):
                send_message(sock, "PONG :tmi.twitch.tv")
            else:
                match = regex.search(data)
                if match:
                    username, message = match.group(1, 2)
                    message_queue.put((username, message, live))

                else:
                    print(f"No match found: {data}")
        else:
            sleep(0.5)

url = f"https://api.twitch.tv/helix/streams?user_login={channel[1:]}"
live = False

def online_check():
    global live

    headers = {
        'Authorization': f'Bearer {apptoken}',
        'Client-ID': f'{clientID}'
    }
    while True:
        response = requests.get(url, headers=headers)
        response_json = response.json()
        if response_json['data']:
            print("Channel is live")
            live = True
        else:
            print("Channel is offline")
            live = False
        sleep(60)

sql_thread = threading.Thread(target=write_to_database, args=(message_queue,))
sql_thread.start()

process_thread = threading.Thread(target=process_messages, args=(unprocessedqueue,))
process_thread.start()

online_thread = threading.Thread(target=online_check,)
online_thread.start()

sock = connect_to_server()

while True:
    ready = select.select([sock], [], [], 10)
    if ready[0]:
        data = sock.recv(65536).decode("utf-8")
        unprocessedqueue.put(data)
