import tkinter as tk
from tkinter import ttk, messagebox, font
import socket
import threading
import json
from datetime import datetime


class ChatApp:
   

    def __init__(self, host='127.0.0.1', port=2323):
   
        self.server_addr = (host, port)
        self.sock = None
        self.sockfile = None
        

        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Chat")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)

        # Define custom fonts for consistency
        self.custom_font = font.Font(family="Helvetica", size=12)
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.time_font = font.Font(family="Helvetica", size=9)

        # Configure widget styles and show login screen
        self.setup_styles()
        self.setup_login_ui()
        self.root.mainloop()

    def setup_styles(self):
       
        
        st = ttk.Style()
        st.configure("TButton", font=self.custom_font, padding=10,background="#ffffff")
        st.configure("TEntry", font=self.custom_font, padding=8)
        st.configure("TLabel", font=self.custom_font )
        st.configure("TFrame", background="#f9f9f9")
        # Striped Treeview for online users
        st.configure(
            "Striped.Treeview",
            font=self.custom_font,
            background="#ffffff",
            fieldbackground="#ffffff",
            rowheight=30,
            
        )
        st.theme_use('clam') 
        st.configure("TButton", background="#02033b", foreground="white")
        st.map(
            "Treeview",
            background=[('selected', '#4CAF50')],
            foreground=[('selected', '#050101')]
        )

    def setup_login_ui(self):
        
        self.login_frame = ttk.Frame(self.root, padding=40)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Application title
        ttk.Label(
            self.login_frame,
            text="Chat",
            font=self.title_font
        ).grid(row=0, column=0, columnspan=2, pady=(0, 30))

        # Username input
        ttk.Label(self.login_frame, text="Username:").grid(
            row=1, column=0, sticky="e")
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=1, column=1, pady=5, ipady=5)

        # Password input
        ttk.Label(self.login_frame, text="Password:").grid(
            row=2, column=0, sticky="e")
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5, ipady=5)

        # Login/Register buttons
        ttk.Button(
            self.login_frame, text="Login", command=self.login
        ).grid(row=3, column=0, columnspan=2, sticky="we", pady=15)
        ttk.Button(
            self.login_frame, text="Register", command=self.show_register
        ).grid(row=4, column=0, columnspan=2, pady=5)

    def show_register(self):
       
        self.reg_win = tk.Toplevel(self.root)
        self.reg_win.title("Register")
        self.reg_win.geometry("400x300")

        ttk.Label(self.reg_win, text="New Username:").pack(pady=5)
        self.new_user = ttk.Entry(self.reg_win)
        self.new_user.pack()

        ttk.Label(self.reg_win, text="Password:").pack(pady=5)
        self.new_pass = ttk.Entry(self.reg_win, show="*")
        self.new_pass.pack()

        ttk.Label(self.reg_win, text="Confirm Password:").pack(pady=5)
        self.conf_pass = ttk.Entry(self.reg_win, show="*")
        self.conf_pass.pack()

        ttk.Button(
            self.reg_win, text="Create Account", command=self.register
        ).pack(pady=10)

    def setup_chat_ui(self):
        
        # Remove login form
        self.login_frame.destroy()

        # Online Users panel
        self.users_frame = ttk.LabelFrame(
            self.root, text="Online Users", width=250
        )
        self.users_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.users_frame.columnconfigure(0, weight=1)
        self.users_frame.rowconfigure(1, weight=1)
        

        # Treeview inside a frame for scrollbar
        tree_frame = ttk.Frame(self.users_frame)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.user_list = ttk.Treeview(
            tree_frame, show="tree", style="Striped.Treeview")
        scrollbar_u = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.user_list.yview)
        self.user_list.configure(yscrollcommand=scrollbar_u.set)
        self.user_list.pack(side="left", fill="both", expand=True)
        scrollbar_u.pack(side="right", fill="y")
        self.user_list.tag_configure('oddrow', background='#f0f0f0')
        self.user_list.tag_configure('evenrow', background='#ffffff')

        # Chat area frame (canvas + scrollbar)
        self.chat_frame = ttk.Frame(self.root)
        self.chat_frame.pack(side="right", expand=True,
                             fill="both", padx=10, pady=10)
        self.chat_frame.rowconfigure(0, weight=1)
        self.chat_frame.rowconfigure(1, weight=0)
        self.chat_frame.columnconfigure(0, weight=1)

        # Canvas displays message bubbles
        self.chat_canvas = tk.Canvas(
            self.chat_frame, bg="#f5f7fa", bd=0, highlightthickness=0
        )
        self.chat_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            self.chat_frame, orient="vertical", command=self.chat_canvas.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)

        # Container frame inside canvas
        self.chat_container = tk.Frame(self.chat_canvas, bg="#f5f7fa")
        self.chat_canvas.create_window(
            (0, 0), window=self.chat_container, anchor="nw")
        self.chat_container.bind(
            "<Configure>", lambda e: self.chat_canvas.configure(
                scrollregion=self.chat_canvas.bbox("all")
            )
        )

        # Message entry field and send button
        self.send_frame = ttk.Frame(self.chat_frame)
        self.send_frame.grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=5)
        self.send_frame.columnconfigure(0, weight=1)
        self.send_frame.columnconfigure(1, weight=0)

        self.msg_entry = ttk.Entry(self.send_frame)
        self.msg_entry.grid(row=0, column=0, sticky="ew", ipady=8, padx=(5, 2))

        send_button = tk.Button(
            self.send_frame,
            text="➤",
            font=(None, 14),
            bd=0,
            bg="#25D366",
            fg="white",
            activebackground="#128C7E",
            activeforeground="white",
            command=self.send_message
        )
        send_button.grid(row=0, column=1, sticky="e", padx=(2, 5))

        self.msg_entry.bind("<Return>", self.send_message)
        self.msg_entry.focus_set()

    def connect(self):
        
        try:
            if self.sock:
                self.sock.close()
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(self.server_addr)
            self.sockfile = self.sock.makefile('r')
            return True
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            return False

    def send_credentials(self, creds):
        
        data = json.dumps(creds) + "\n"
        self.sock.sendall(data.encode())
        raw = self.sockfile.readline()
        if not raw:
            raise ConnectionError("No response from server")
        return json.loads(raw.strip())

    def login(self):
       
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Warning", "Please enter both fields")
            return
        if not self.connect():
            return
        try:
            resp = self.send_credentials(
                {"action": "login", "username": username, "password": password})
            if resp.get("status") == "success":
                self.username = username
                self.setup_chat_ui()
                threading.Thread(target=self.recv_messages,
                                 daemon=True).start()
            else:
                messagebox.showerror(
                    "Error", resp.get("message", "Login failed"))
                self.sock.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.sock.close()

    def register(self):
        
        username = self.new_user.get().strip()
        password = self.new_pass.get().strip()
        confirm = self.conf_pass.get().strip()
        if not username or not password:
            messagebox.showwarning("Warning", "Please fill all fields")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords don't match")
            return
        if not self.connect():
            return
        try:
            resp = self.send_credentials(
                {"action": "register", "username": username, "password": password})
            if resp.get("status") == "success":
                messagebox.showinfo("Success", "Account created!")
                self.reg_win.destroy()
            else:
                messagebox.showerror("Error", resp.get(
                    "message", "Registration failed"))
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.sock.close()

    def recv_messages(self):
        
        while True:
            try:
                raw = self.sockfile.readline()
                if not raw:
                    raise ConnectionError
                msg = json.loads(raw.strip())
                if msg.get("type") == "user_list":
                    self.root.after(0, self.update_users,
                                    msg.get("content", []))
                elif msg.get("type") == "message":
                    self.root.after(0, self.display_message,
                                    msg.get("sender", ""), msg.get("content", ""), msg.get("time", ""))
            except Exception:
                messagebox.showerror("Error", "Connection lost")
                self.root.quit()
                break

    def update_users(self, users):
       
        self.user_list.delete(*self.user_list.get_children())
        for idx, user in enumerate(users):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.user_list.insert("", "end", text=user, tags=(tag,))

    def display_message(self, sender, content, time):
        
        bubble_frame = tk.Frame(self.chat_container, bg="#f5f7fa")
        if sender == getattr(self, 'username', None):
            color, anchor, justify = "#dcf8c6", 'w', 'left'
        else:
            color, anchor, justify = "#ffffff", 'e', 'right'

        bubble = tk.Label(
            bubble_frame,
            text=content,
            bg=color,
            wraplength=400,
            justify=justify,
            font=self.custom_font,
            padx=15,
            pady=10,
            bd=0,
            relief="ridge"
        )
        meta = tk.Label(
            bubble_frame,
            text=f"{sender}  {time}",
            font=self.time_font,
            fg="gray",
            bg="#f5f7fa"
        )

        bubble_frame.pack(fill="x", pady=4, padx=10)
        meta.pack(anchor=anchor)
        bubble.pack(anchor=anchor)
        self.chat_canvas.yview_moveto(1.0)

    def send_message(self, event=None):
        
        text = self.msg_entry.get().strip()
        if text and self.sock:
            try:
                packet = json.dumps(
                    {"type": "message", "content": text}) + "\n"
                self.sock.sendall(packet.encode())
                self.msg_entry.delete(0, "end")
            except Exception as e:
                messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    ChatApp()