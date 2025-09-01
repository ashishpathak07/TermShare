#!/usr/bin/env python3
"""
TermShare - Terminal FTP Application
Main entry point for the application
"""

import tkinter as tk
from gui import TermShareApp

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = TermShareApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()