# TermShare - Terminal FTP Application

TermShare is a terminal-based FTP application with a user-friendly interface built with Python and Tkinter. It supports both synchronous and asynchronous file transfers using asyncio.

## Features

- Efficient FTP File Sharing: Designed for seamless file transfer among connected users via FTP
- User Customization: Allows users to select a display name for personalized interactions
- Automatic Port Assignment: Implements automatic port assignment for easy and efficient connections
- Both Synchronous and Asynchronous Operations: Supports both traditional FTP and modern async FTP
- Cross-platform: Works on Linux, Windows, and macOS

## Installation

1. Clone the repository:
https://github.com/ashishpathak07/TermShare


2. Install dependencies:
pip install -r requirements.txt


## Usage

Run the application:


### Connection Settings
- Set your display name for personalized interactions
- Enter the FTP server host address and port
- Provide username and password (use "anonymous" for anonymous FTP)
- Choose between synchronous or asynchronous mode

### Server Operations
- Click "Start Server" to run a simple FTP server on your machine
- The application will automatically assign an available port

### File Operations
- Upload files using the "Upload File" button
- Download files by double-clicking or using the "Download File" button
- Create directories with the "Create Directory" button
- Navigate directories by double-clicking on them

## Project Structure
TermShare/
├── main.py # Main entry point
├── ftp_client.py # FTP client operations
├── ftp_server.py # FTP server operations
├── gui.py # User interface
├── utils.py # Utility functions
├── requirements.txt # Dependencies
└── README.md # This file


## Dependencies

- Python 3.7+
- Tkinter (usually included with Python)
- aioftp (for asynchronous FTP operations)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

How to Run

Install the required dependencies:
pip install aioftp

Run the application:
python main.py