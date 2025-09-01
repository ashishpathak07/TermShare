"""
FTP Server module for TermShare
Handles FTP server operations with asyncio support
"""

import socket
import threading
import asyncio
from typing import Tuple, List

class FTPServer:
    def __init__(self):
        self.running = False
        self.host = "0.0.0.0"
        self.port = None
        self.server_socket = None
        self.clients = []
        self.thread = None
        
    def start_server(self, port_range: Tuple[int, int] = (2121, 2140)) -> Tuple[bool, str]:
        """Start a synchronous FTP server"""
        if self.running:
            return False, "Server is already running"
        
        # Find an available port in the range
        for port in range(port_range[0], port_range[1] + 1):
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.bind((self.host, port))
                self.port = port
                break
            except:
                if port == port_range[1]:
                    return False, "No available ports in the specified range"
                continue
        
        self.server_socket.listen(5)
        self.running = True
        self.thread = threading.Thread(target=self._accept_clients)
        self.thread.daemon = True
        self.thread.start()
        
        return True, f"Server started on port {self.port}"
    
    def stop_server(self) -> Tuple[bool, str]:
        """Stop the synchronous FTP server"""
        if not self.running:
            return False, "Server is not running"
        
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        
        for client in self.clients:
            client.close()
        
        return True, "Server stopped"
    
    def _accept_clients(self):
        """Accept client connections"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                self.clients.append(client_socket)
                client_thread = threading.Thread(target=self._handle_client, args=(client_socket, address))
                client_thread.daemon = True
                client_thread.start()
            except:
                break
    
    def _handle_client(self, client_socket, address):
        """Handle client connection"""
        try:
            client_socket.send(b"220 Welcome to TermShare FTP Server\r\n")
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                # Echo back the received data
                client_socket.send(data)
        except:
            pass
        finally:
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)
    
    async def async_start_server(self, port_range: Tuple[int, int] = (2121, 2140)) -> Tuple[bool, str]:
        """Asynchronously start server"""
        return await asyncio.get_event_loop().run_in_executor(
            None, self.start_server, port_range
        )
    
    async def async_stop_server(self) -> Tuple[bool, str]:
        """Asynchronously stop server"""
        return await asyncio.get_event_loop().run_in_executor(None, self.stop_server)