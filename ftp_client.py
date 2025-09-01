"""
FTP Client module for TermShare
Handles all FTP client operations with asyncio support
"""

import os
import ftplib
from ftplib import FTP
import asyncio
from typing import Tuple, List, Optional

class FTPClient:
    def __init__(self):
        self.ftp = None
        self.connected = False
        self.host = None
        self.port = None
        
    def connect(self, host: str, port: int, username: str, password: str) -> Tuple[bool, str]:
        """Connect to FTP server"""
        try:
            self.ftp = FTP()
            self.ftp.connect(host, port)
            self.ftp.login(username, password)
            self.connected = True
            self.host = host
            self.port = port
            return True, "Connected successfully"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    def disconnect(self) -> Tuple[bool, str]:
        """Disconnect from FTP server"""
        if self.connected:
            try:
                self.ftp.quit()
            except:
                try:
                    self.ftp.close()
                except:
                    pass
            self.connected = False
            return True, "Disconnected"
        return False, "Not connected"
    
    def list_files(self) -> Tuple[bool, List[str]]:
        """List files in directory"""
        if not self.connected:
            return False, ["Not connected to server"]
        
        try:
            files = []
            self.ftp.retrlines('LIST', files.append)
            return True, files
        except Exception as e:
            return False, [f"Failed to list files: {str(e)}"]
    
    def download_file(self, remote_path: str, local_path: str) -> Tuple[bool, str]:
        """Download a file"""
        if not self.connected:
            return False, "Not connected to server"
        
        try:
            with open(local_path, 'wb') as f:
                self.ftp.retrbinary(f'RETR {remote_path}', f.write)
            return True, f"Downloaded {remote_path} to {local_path}"
        except Exception as e:
            return False, f"Download failed: {str(e)}"
    
    def upload_file(self, local_path: str, remote_path: str) -> Tuple[bool, str]:
        """Upload a file"""
        if not self.connected:
            return False, "Not connected to server"
        
        try:
            with open(local_path, 'rb') as f:
                self.ftp.storbinary(f'STOR {remote_path}', f)
            return True, f"Uploaded {local_path} to {remote_path}"
        except Exception as e:
            return False, f"Upload failed: {str(e)}"
    
    def create_directory(self, dir_name: str) -> Tuple[bool, str]:
        """Create a directory"""
        if not self.connected:
            return False, "Not connected to server"
        
        try:
            self.ftp.mkd(dir_name)
            return True, f"Created directory {dir_name}"
        except Exception as e:
            return False, f"Failed to create directory: {str(e)}"
    
    def change_directory(self, dir_name: str) -> Tuple[bool, str]:
        """Change directory"""
        if not self.connected:
            return False, "Not connected to server"
        
        try:
            self.ftp.cwd(dir_name)
            return True, f"Changed to directory {dir_name}"
        except Exception as e:
            return False, f"Failed to change directory: {str(e)}"
    
    def get_current_directory(self) -> Tuple[bool, str]:
        """Get current directory"""
        if not self.connected:
            return False, "Not connected to server"
        
        try:
            return True, self.ftp.pwd()
        except Exception as e:
            return False, f"Failed to get current directory: {str(e)}"
    
    async def async_connect(self, host: str, port: int, username: str, password: str) -> Tuple[bool, str]:
        """Asynchronously connect to FTP server"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.connect, host, port, username, password
        )
    
    async def async_disconnect(self) -> Tuple[bool, str]:
        """Asynchronously disconnect from FTP server"""
        return await asyncio.get_event_loop().run_in_executor(None, self.disconnect)
    
    async def async_list_files(self) -> Tuple[bool, List[str]]:
        """Asynchronously list files in directory"""
        return await asyncio.get_event_loop().run_in_executor(None, self.list_files)
    
    async def async_download_file(self, remote_path: str, local_path: str) -> Tuple[bool, str]:
        """Asynchronously download a file"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.download_file, remote_path, local_path
        )
    
    async def async_upload_file(self, local_path: str, remote_path: str) -> Tuple[bool, str]:
        """Asynchronously upload a file"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.upload_file, local_path, remote_path
        )
    
    async def async_create_directory(self, dir_name: str) -> Tuple[bool, str]:
        """Asynchronously create a directory"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.create_directory, dir_name
        )
    
    async def async_change_directory(self, dir_name: str) -> Tuple[bool, str]:
        """Asynchronously change directory"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.change_directory, dir_name
        )
    
    async def async_get_current_directory(self) -> Tuple[bool, str]:
        """Asynchronously get current directory"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.get_current_directory
        )