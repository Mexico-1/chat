# ChatSphere

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-orange)
![SQLite](https://img.shields.io/badge/SQLite-Database-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

ChatSphere is a real-time chat application built with Python, designed for seamless communication. It leverages Tkinter for a clean, user-friendly GUI, TCP sockets for instant messaging, and SQLite for robust user management. The application provides secure authentication, dynamic user tracking, and a WhatsApp-inspired chat interface, making it ideal for developers and users seeking a lightweight, extensible chat solution.

## Table of Contents
- [Why ConnectSphere?](#why-connectsphere)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Dependencies](#dependencies)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## Why ChatSphere?
ChatSphere is a practical solution for real-time communication, offering:
- **Developer-Friendly**: Clean, modular code with extensive comments for easy customization.
- **Lightweight**: Runs efficiently using only Python’s standard library, with no external dependencies.
- **Educational Value**: Ideal for learning about socket programming, GUI development, and database integration.
- **Extensible**: Built with scalability in mind, allowing for features like private chats or file sharing.

Whether you're a student exploring network programming or a developer building a custom chat tool, ChatSphere provides a solid foundation.

## Features
- **Secure Authentication**: Register and log in with credentials stored in an SQLite database.
- **Real-Time Messaging**: Broadcast messages instantly to all connected users via TCP sockets.
- **Dynamic User List**: Displays online users with alternating row colors for clarity.
- **Intuitive GUI**: Tkinter-based interface with message bubbles, custom fonts, and smooth scrolling.
- **Error Handling**: Robust client-server communication with graceful disconnection management.
- **Cross-Platform**: Runs on Windows, macOS, and Linux without modification.

## Architecture
ConnectSphere uses a client-server model:
- **Server (`server.py`)**: Handles client connections, authenticates users, and broadcasts messages using multi-threaded TCP sockets. SQLite manages user data.
- **Client (`client.py`)**: Provides a Tkinter GUI for login, registration, and chatting, with real-time updates for messages and user lists.
- **Database (`database.py`)**: Manages SQLite operations for user registration and credential validation.

### Data Flow
1. Clients connect to the server via TCP sockets.
2. Users authenticate or register, with credentials verified against the SQLite database.
3. The server updates all clients with the online user list and broadcasts messages.
4. The client GUI renders messages as styled bubbles and refreshes the user list dynamically.

## Installation
### Prerequisites
- Python 3.8 or higher
- Git (optional, for cloning)

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Youssaf-Mohamed/ChatSphere.git
   cd ChatSphere
