

import socket
import threading
import json
import sqlite3
from datetime import datetime
from contextlib import closing


class Database:
   

    def __init__(self, db_name='chat.db'):
       
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()
        self.add_default_users()

    def create_tables(self):
        """Create the users table if it does not already exist."""
        with closing(self.conn.cursor()) as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            self.conn.commit()

    def add_default_users(self):
        
        default_users = [
            ('mex', '111'),
            ('osama', '111')
        ]
        with closing(self.conn.cursor()) as cursor:
            for u, p in default_users:
                cursor.execute('''
                    INSERT OR IGNORE INTO users (username, password)
                    VALUES (?, ?)
                ''', (u, p))
            self.conn.commit()

    def register_user(self, username, password):
       
        try:
            with closing(self.conn.cursor()) as cursor:
                cursor.execute('''
                    INSERT INTO users (username, password)
                    VALUES (?, ?)
                ''', (username, password))
                self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def validate_user(self, username, password):
        
        with closing(self.conn.cursor()) as cursor:
            cursor.execute('''
                SELECT 1 FROM users
                WHERE username = ? AND password = ?
            ''', (username, password))
            return cursor.fetchone() is not None

    def close(self):
        
        self.conn.close()


class ChatServer:
    
    def __init__(self, host='0.0.0.0', port=2323):
       
        self.db = Database()
        self.active_clients = []  # list of (username, socket)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(20)
        print(f"[SERVER] Running on {host}:{port}")
        self.accept_loop()

    def accept_loop(self):
        
        while True:
            client_sock, addr = self.server_socket.accept()
            threading.Thread(
                target=self.client_handler, args=(client_sock,), daemon=True
            ).start()

    def client_handler(self, client_sock):
       
        username = self.handle_auth(client_sock)
        if not username:
            client_sock.close()
            return

        # Successful login
        self.active_clients.append((username, client_sock))
        self.broadcast_user_list()

        # Start listening for chat messages
        threading.Thread(
            target=self.listen_for_messages, args=(
                client_sock, username), daemon=True
        ).start()

    def handle_auth(self, sock):
     
        raw = sock.recv(2048).decode()
        if not raw:
            print("[ERROR] No data received for auth")
            return None

        try:
            creds = json.loads(raw.strip())
        except json.JSONDecodeError:
            print(f"[ERROR] Invalid JSON from client: {raw!r}")
            sock.sendall((json.dumps({
                "status": "error", "message": "Invalid JSON"
            }) + "\n").encode())
            return None

        action = creds.get("action")
        user = creds.get("username")
        pwd = creds.get("password")

        if action == "register":
            ok = self.db.register_user(user, pwd)
            resp = {"status": "success"} if ok else {
                "status": "error", "message": "Username already exists"}
            sock.sendall((json.dumps(resp) + "\n").encode())
            return None

        elif action == "login":
            if self.db.validate_user(user, pwd):
                sock.sendall(
                    (json.dumps({"status": "success"}) + "\n").encode())
                return user
            else:
                sock.sendall((json.dumps({
                    "status": "error", "message": "Invalid credentials"
                }) + "\n").encode())
                return None

        else:
            sock.sendall((json.dumps({
                "status": "error", "message": "Unknown action"
            }) + "\n").encode())
            return None

    def broadcast_user_list(self):
        
        users = [u for u, _ in self.active_clients]
        msg = json.dumps({"type": "user_list", "content": users}) + "\n"
        for u, sock in list(self.active_clients):
            try:
                sock.sendall(msg.encode())
            except:
                self.remove_client(u)

    def listen_for_messages(self, sock, username):
       
        buffer = ""
        while True:
            try:
                data = sock.recv(2048).decode()
                if not data:
                    raise ConnectionError
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if not line.strip():
                        continue
                    try:
                        pkt = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if pkt.get("type") == "message":
                        broadcast = json.dumps({
                            "type": "message",
                            "sender": username,
                            "content": pkt["content"],
                            "time": datetime.now().strftime("%H:%M")
                        }) + "\n"
                        self.broadcast_message(broadcast)
            except:
                print(f"[INFO] {username} disconnected")
                self.remove_client(username)
                break

    def broadcast_message(self, message):
       
        for u, sock in list(self.active_clients):
            try:
                sock.sendall(message.encode())
            except:
                self.remove_client(u)

    def remove_client(self, username):
        
        self.active_clients = [(u, s)
                               for u, s in self.active_clients if u != username]
        self.broadcast_user_list()


if __name__ == "__main__":
    """Entry point for running the chat server."""
    ChatServer()
