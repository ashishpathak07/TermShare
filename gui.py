"""
GUI module for TermShare
Handles the user interface using Tkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import asyncio
import threading
import random
import os
from datetime import datetime
from ftp_client import FTPClient
from ftp_server import FTPServer

class TermShareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TermShare - Terminal FTP Application")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Initialize FTP client and server
        self.ftp_client = FTPClient()
        self.ftp_server = FTPServer()
        
        # User settings
        self.display_name = "User" + str(random.randint(1000, 9999))
        self.host_address = "localhost"
        self.port_number = 2121
        self.username = "anonymous"
        self.password = ""
        self.use_async = True  # Use asynchronous operations by default
        
        # Create the UI
        self.setup_ui()
        
        # Log startup message
        self.log_message("TermShare started. Ready to connect.")
    
    def setup_ui(self):
        # Create main frames
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Connection frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="5")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        conn_frame.columnconfigure(1, weight=1)
        
        ttk.Label(conn_frame, text="Display Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = ttk.Entry(conn_frame)
        self.name_entry.insert(0, self.display_name)
        self.name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(conn_frame, text="Host:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.host_entry = ttk.Entry(conn_frame)
        self.host_entry.insert(0, self.host_address)
        self.host_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(conn_frame, text="Port:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.port_entry = ttk.Entry(conn_frame, width=10)
        self.port_entry.insert(0, str(self.port_number))
        self.port_entry.grid(row=2, column=1, sticky=tk.W, pady=2, padx=(5, 0))
        
        ttk.Label(conn_frame, text="Username:").grid(row=0, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        self.user_entry = ttk.Entry(conn_frame)
        self.user_entry.insert(0, self.username)
        self.user_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(conn_frame, text="Password:").grid(row=1, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        self.pass_entry = ttk.Entry(conn_frame, show="*")
        self.pass_entry.insert(0, self.password)
        self.pass_entry.grid(row=1, column=3, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        # Async checkbox
        self.async_var = tk.BooleanVar(value=self.use_async)
        self.async_check = ttk.Checkbutton(conn_frame, text="Use Async", variable=self.async_var)
        self.async_check.grid(row=2, column=2, sticky=tk.W, pady=2, padx=(10, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(conn_frame)
        button_frame.grid(row=2, column=3, sticky=(tk.W, tk.E), pady=2)
        
        self.connect_btn = ttk.Button(button_frame, text="Connect", command=self.connect_ftp)
        self.connect_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.disconnect_btn = ttk.Button(button_frame, text="Disconnect", command=self.disconnect_ftp, state=tk.DISABLED)
        self.disconnect_btn.grid(row=0, column=1, padx=(0, 5))
        
        self.server_btn = ttk.Button(button_frame, text="Start Server", command=self.toggle_server)
        self.server_btn.grid(row=0, column=2)
        
        # File operations frame
        file_frame = ttk.LabelFrame(main_frame, text="File Operations", padding="5")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.upload_btn = ttk.Button(file_frame, text="Upload File", command=self.upload_file, state=tk.DISABLED)
        self.upload_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.download_btn = ttk.Button(file_frame, text="Download File", command=self.download_file, state=tk.DISABLED)
        self.download_btn.grid(row=0, column=1, padx=(0, 5))
        
        self.refresh_btn = ttk.Button(file_frame, text="Refresh List", command=self.refresh_file_list, state=tk.DISABLED)
        self.refresh_btn.grid(row=0, column=2, padx=(0, 5))
        
        self.mkdir_btn = ttk.Button(file_frame, text="Create Directory", command=self.create_directory, state=tk.DISABLED)
        self.mkdir_btn.grid(row=0, column=3, padx=(0, 5))
        
        # File list frame
        list_frame = ttk.LabelFrame(main_frame, text="Remote Files", padding="5")
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # File list with scrollbar
        file_list_frame = ttk.Frame(list_frame)
        file_list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        file_list_frame.columnconfigure(0, weight=1)
        file_list_frame.rowconfigure(0, weight=1)
        
        columns = ("name", "size", "type", "modified")
        self.file_tree = ttk.Treeview(file_list_frame, columns=columns, show="headings")
        
        self.file_tree.heading("name", text="Name")
        self.file_tree.heading("size", text="Size")
        self.file_tree.heading("type", text="Type")
        self.file_tree.heading("modified", text="Modified")
        
        self.file_tree.column("name", width=200)
        self.file_tree.column("size", width=100)
        self.file_tree.column("type", width=100)
        self.file_tree.column("modified", width=150)
        
        scrollbar = ttk.Scrollbar(file_list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind double-click to change directory or download file
        self.file_tree.bind("<Double-1>", self.on_file_double_click)
        
        # Current directory label
        self.current_dir_label = ttk.Label(list_frame, text="Current directory: Not connected")
        self.current_dir_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="5")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=80, height=15, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
    def log_message(self, message):
        """Add a message to the log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def set_status(self, message):
        """Set the status bar message"""
        self.status_var.set(message)
    
    def connect_ftp(self):
        """Connect to FTP server"""
        self.display_name = self.name_entry.get()
        self.host_address = self.host_entry.get()
        
        try:
            self.port_number = int(self.port_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")
            return
        
        self.username = self.user_entry.get()
        self.password = self.pass_entry.get()
        self.use_async = self.async_var.get()
        
        self.log_message(f"Connecting to {self.host_address}:{self.port_number} as {self.username}...")
        self.set_status("Connecting...")
        
        # Run connection in a separate thread to avoid blocking the UI
        if self.use_async:
            threading.Thread(target=self._async_connect_thread, daemon=True).start()
        else:
            threading.Thread(target=self._sync_connect_thread, daemon=True).start()
    
    def _async_connect_thread(self):
        """Thread for asynchronous connection to FTP server"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success, message = loop.run_until_complete(
                self.ftp_client.async_connect(
                    self.host_address, self.port_number, self.username, self.password
                )
            )
        finally:
            loop.close()
        
        # Schedule UI update on the main thread
        self.root.after(0, self._connection_complete, success, message)
    
    def _sync_connect_thread(self):
        """Thread for synchronous connection to FTP server"""
        success, message = self.ftp_client.connect(
            self.host_address, self.port_number, self.username, self.password
        )
        
        # Schedule UI update on the main thread
        self.root.after(0, self._connection_complete, success, message)
    
    def _connection_complete(self, success, message):
        """Handle connection result"""
        if success:
            self.log_message(message)
            self.set_status(f"Connected to {self.host_address}:{self.port_number}")
            
            # Update UI for connected state
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            self.upload_btn.config(state=tk.NORMAL)
            self.download_btn.config(state=tk.NORMAL)
            self.refresh_btn.config(state=tk.NORMAL)
            self.mkdir_btn.config(state=tk.NORMAL)
            
            # Refresh file list
            self.refresh_file_list()
        else:
            self.log_message(message)
            self.set_status("Connection failed")
            messagebox.showerror("Connection Error", message)
    
    def disconnect_ftp(self):
        """Disconnect from FTP server"""
        self.log_message("Disconnecting...")
        
        if self.use_async:
            threading.Thread(target=self._async_disconnect_thread, daemon=True).start()
        else:
            threading.Thread(target=self._sync_disconnect_thread, daemon=True).start()
    
    def _async_disconnect_thread(self):
        """Thread for asynchronous disconnection from FTP server"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success, message = loop.run_until_complete(
                self.ftp_client.async_disconnect()
            )
        finally:
            loop.close()
        
        # Schedule UI update on the main thread
        self.root.after(0, self._disconnection_complete, success, message)
    
    def _sync_disconnect_thread(self):
        """Thread for synchronous disconnection from FTP server"""
        success, message = self.ftp_client.disconnect()
        
        # Schedule UI update on the main thread
        self.root.after(0, self._disconnection_complete, success, message)
    
    def _disconnection_complete(self, success, message):
        """Handle disconnection result"""
        if success:
            self.log_message(message)
            self.set_status("Disconnected")
            
            # Update UI for disconnected state
            self.connect_btn.config(state=tk.NORMAL)
            self.disconnect_btn.config(state=tk.DISABLED)
            self.upload_btn.config(state=tk.DISABLED)
            self.download_btn.config(state=tk.DISABLED)
            self.refresh_btn.config(state=tk.DISABLED)
            self.mkdir_btn.config(state=tk.DISABLED)
            
            # Clear file list
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            self.current_dir_label.config(text="Current directory: Not connected")
        else:
            self.log_message(message)
            messagebox.showerror("Disconnection Error", message)
    
    def toggle_server(self):
        """Start or stop the FTP server"""
        if not self.ftp_server.running:
            # Start server
            if self.use_async:
                threading.Thread(target=self._async_start_server, daemon=True).start()
            else:
                success, message = self.ftp_server.start_server()
                self._server_toggle_complete(success, message)
        else:
            # Stop server
            if self.use_async:
                threading.Thread(target=self._async_stop_server, daemon=True).start()
            else:
                success, message = self.ftp_server.stop_server()
                self._server_toggle_complete(success, message)
    
    def _async_start_server(self):
        """Start asynchronous FTP server"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success, message = loop.run_until_complete(
                self.ftp_server.async_start_server()
            )
        finally:
            loop.close()
        
        # Schedule UI update on the main thread
        self.root.after(0, self._server_toggle_complete, success, message)
    
    def _async_stop_server(self):
        """Stop asynchronous FTP server"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success, message = loop.run_until_complete(
                self.ftp_server.async_stop_server()
            )
        finally:
            loop.close()
        
        # Schedule UI update on the main thread
        self.root.after(0, self._server_toggle_complete, success, message)
    
    def _server_toggle_complete(self, success, message):
        """Handle server start/stop result"""
        if success:
            self.log_message(message)
            if self.ftp_server.running:
                self.set_status(f"Server running on port {self.ftp_server.port}")
                self.server_btn.config(text="Stop Server")
                
                # Update port field with the assigned port
                self.port_entry.delete(0, tk.END)
                self.port_entry.insert(0, str(self.ftp_server.port))
            else:
                self.set_status("Server stopped")
                self.server_btn.config(text="Start Server")
        else:
            self.log_message(message)
            messagebox.showerror("Server Error", message)
    
    def refresh_file_list(self):
        """Refresh the list of files on the FTP server"""
        if not self.ftp_client.connected:
            return
        
        # Get current directory
        if self.use_async:
            threading.Thread(target=self._async_get_current_dir, daemon=True).start()
        else:
            success, current_dir = self.ftp_client.get_current_directory()
            self._current_dir_complete(success, current_dir)
        
        # Get file list
        if self.use_async:
            threading.Thread(target=self._async_list_files, daemon=True).start()
        else:
            success, files = self.ftp_client.list_files()
            self._file_list_complete(success, files)
    
    def _async_get_current_dir(self):
        """Asynchronously get current directory"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success, current_dir = loop.run_until_complete(
                self.ftp_client.async_get_current_directory()
            )
        finally:
            loop.close()
        
        # Schedule UI update on the main thread
        self.root.after(0, self._current_dir_complete, success, current_dir)
    
    def _current_dir_complete(self, success, current_dir):
        """Handle current directory result"""
        if success:
            self.current_dir_label.config(text=f"Current directory: {current_dir}")
        else:
            self.log_message(current_dir)  # In this case, current_dir is the error message
    
    def _async_list_files(self):
        """Asynchronously list files"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success, files = loop.run_until_complete(
                self.ftp_client.async_list_files()
            )
        finally:
            loop.close()
        
        # Schedule UI update on the main thread
        self.root.after(0, self._file_list_complete, success, files)
    
    def _file_list_complete(self, success, files):
        """Handle file list result"""
        if not success:
            self.log_message(files)  # files is the error message in this case
            return
        
        # Clear current file list
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Parse and add files to the list
        for file_info in files:
            # Simple parsing of FTP LIST output
            parts = file_info.split()
            if len(parts) >= 9:
                # Extract filename (everything after the 8th part)
                filename = " ".join(parts[8:])
                file_type = "DIR" if parts[0].startswith("d") else "FILE"
                file_size = parts[4] if file_type == "FILE" else ""
                modified = " ".join(parts[5:8])
                
                self.file_tree.insert("", tk.END, values=(filename, file_size, file_type, modified))
    
    def on_file_double_click(self, event):
        """Handle double-click on a file/directory in the list"""
        if not self.ftp_client.connected:
            return
        
        item = self.file_tree.selection()[0]
        item_values = self.file_tree.item(item, "values")
        name = item_values[0]
        item_type = item_values[2]
        
        if item_type == "DIR":
            # Change to the directory
            if self.use_async:
                threading.Thread(target=self._async_change_dir, args=(name,), daemon=True).start()
            else:
                success, message = self.ftp_client.change_directory(name)
                self._change_dir_complete(success, message)
        else:
            # Download the file
            self.download_file(name)
    
    def _async_change_dir(self, dir_name):
        """Asynchronously change directory"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success, message = loop.run_until_complete(
                self.ftp_client.async_change_directory(dir_name)
            )
        finally:
            loop.close()
        
        # Schedule UI update on the main thread
        self.root.after(0, self._change_dir_complete, success, message)
    
    def _change_dir_complete(self, success, message):
        """Handle directory change result"""
        if success:
            self.log_message(message)
            self.refresh_file_list()
        else:
            self.log_message(message)
    
    def upload_file(self):
        """Upload a file to the FTP server"""
        if not self.ftp_client.connected:
            return
        
        file_path = filedialog.askopenfilename(title="Select file to upload")
        if not file_path:
            return
        
        # Use the same filename for remote
        remote_filename = os.path.basename(file_path)
        
        self.log_message(f"Uploading {file_path} as {remote_filename}...")
        self.set_status("Uploading file...")
        
        # Run upload in a separate thread
        if self.use_async:
            threading.Thread(target=self._async_upload, args=(file_path, remote_filename), daemon=True).start()
        else:
            threading.Thread(target=self._sync_upload, args=(file_path, remote_filename), daemon=True).start()
    
    def _async_upload(self, local_path, remote_path):
        """Asynchronously upload a file"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success, message = loop.run_until_complete(
                self.ftp_client.async_upload_file(local_path, remote_path)
            )
        finally:
            loop.close()
        
        # Schedule UI update on the main thread
        self.root.after(0, self._upload_complete, success, message)
    
    def _sync_upload(self, local_path, remote_path):
        """Synchronously upload a file"""
        success, message = self.ftp_client.upload_file(local_path, remote_path)
        
        # Schedule UI update on the main thread
        self.root.after(0, self._upload_complete, success, message)
    
    def _upload_complete(self, success, message):
        """Handle upload completion"""
        if success:
            self.log_message(message)
            self.set_status("Upload complete")
            self.refresh_file_list()
        else:
            self.log_message(message)
            self.set_status("Upload failed")
            messagebox.showerror("Upload Error", message)
    
    def download_file(self, remote_filename=None):
        """Download a file from the FTP server"""
        if not self.ftp_client.connected:
            return
        
        if not remote_filename:
            # If no filename provided, get selected item
            selection = self.file_tree.selection()
            if not selection:
                messagebox.showwarning("Download", "Please select a file to download")
                return
            
            item = selection[0]
            item_values = self.file_tree.item(item, "values")
            remote_filename = item_values[0]
            
            if item_values[2] == "DIR":
                messagebox.showwarning("Download", "Please select a file, not a directory")
                return
        
        # Ask for save location
        local_path = filedialog.asksaveasfilename(
            title="Save file as",
            initialfile=remote_filename
        )
        
        if not local_path:
            return
        
        self.log_message(f"Downloading {remote_filename} to {local_path}...")
        self.set_status("Downloading file...")
        
        # Run download in a separate thread
        if self.use_async:
            threading.Thread(target=self._async_download, args=(remote_filename, local_path), daemon=True).start()
        else:
            threading.Thread(target=self._sync_download, args=(remote_filename, local_path), daemon=True).start()
    
    def _async_download(self, remote_path, local_path):
        """Asynchronously download a file"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success, message = loop.run_until_complete(
                self.ftp_client.async_download_file(remote_path, local_path)
            )
        finally:
            loop.close()
        
        # Schedule UI update on the main thread
        self.root.after(0, self._download_complete, success, message)
    
    def _sync_download(self, remote_path, local_path):
        """Synchronously download a file"""
        success, message = self.ftp_client.download_file(remote_path, local_path)
        
        # Schedule UI update on the main thread
        self.root.after(0, self._download_complete, success, message)
    
    def _download_complete(self, success, message):
        """Handle download completion"""
        if success:
            self.log_message(message)
            self.set_status("Download complete")
        else:
            self.log_message(message)
            self.set_status("Download failed")
            messagebox.showerror("Download Error", message)
    
    def create_directory(self):
        """Create a new directory on the FTP server"""
        if not self.ftp_client.connected:
            return
        
        dir_name = tk.simpledialog.askstring("Create Directory", "Enter directory name:")
        if not dir_name:
            return
        
        if self.use_async:
            threading.Thread(target=self._async_create_dir, args=(dir_name,), daemon=True).start()
        else:
            success, message = self.ftp_client.create_directory(dir_name)
            self._create_dir_complete(success, message)
    
    def _async_create_dir(self, dir_name):
        """Asynchronously create a directory"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success, message = loop.run_until_complete(
                self.ftp_client.async_create_directory(dir_name)
            )
        finally:
            loop.close()
        
        # Schedule UI update on the main thread
        self.root.after(0, self._create_dir_complete, success, message)
    
    def _create_dir_complete(self, success, message):
        """Handle directory creation result"""
        if success:
            self.log_message(message)
            self.refresh_file_list()
        else:
            self.log_message(message)
            messagebox.showerror("Create Directory Error", message)