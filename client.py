# client.py - Run this on each student computer

import socket
import json
import sys
import threading
import webbrowser
import time
import os
import subprocess

class LabClient:
    def __init__(self, server_host, server_port=9999):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = None
        self.connected = False
        self.retry_interval = 5  # seconds to wait between connection attempts
        self.max_retries = 0  # 0 means infinite retries
    
    def connect(self):
        retries = 0
        
        while not self.connected and (self.max_retries == 0 or retries < self.max_retries):
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.server_host, self.server_port))
                self.connected = True
                print(f"Connected to server at {self.server_host}:{self.server_port}")
                return True
            except Exception as e:
                print(f"Connection failed: {e}. Retrying in {self.retry_interval} seconds...")
                time.sleep(self.retry_interval)
                retries += 1
        
        if not self.connected:
            print("Maximum connection retries reached. Giving up.")
            return False
    
    def listen(self):
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    # Connection closed by server
                    print("Server closed the connection")
                    self.connected = False
                    break
                
                try:
                    message = json.loads(data.decode('utf-8'))
                    self.handle_message(message)
                except json.JSONDecodeError:
                    print("Received invalid JSON data")
            
            except Exception as e:
                print(f"Error receiving data: {e}")
                self.connected = False
                break
        
        # Try to reconnect if the connection was lost
        self.reconnect()
    
    def reconnect(self):
        if not self.connected:
            print("Connection lost. Attempting to reconnect...")
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
            
            self.connect()
            if self.connected:
                # Start listening for commands again
                thread = threading.Thread(target=self.listen)
                thread.daemon = True
                thread.start()
    
    def handle_message(self, message):
        try:
            if 'action' not in message:
                print("Received message without action")
                return
            
            action = message['action']
            
            if action == 'open_link' and 'url' in message:
                url = message['url']
                print(f"Opening URL: {url}")
                self.open_url(url)
            
            elif action == 'open_multiple_links' and 'urls' in message:
                urls = message['urls']
                print(f"Opening multiple URLs: {urls}")
                for url in urls:
                    self.open_url(url)
                    time.sleep(0.5)  # Small delay between opening tabs
            
            else:
                print(f"Unknown action: {action}")
                
        except Exception as e:
            print(f"Error handling message: {e}")
    
    def open_url(self, url):
        try:
            # Try to use the default browser
            webbrowser.open(url, new=2)
        except Exception as e:
            print(f"Error opening URL with default browser: {e}")
            
            # Try platform-specific fallbacks
            try:
                if sys.platform.startswith('win'):
                    os.system(f'start {url}')
                elif sys.platform.startswith('darwin'):  # macOS
                    subprocess.call(['open', url])
                else:  # Linux and others
                    subprocess.call(['xdg-open', url])
            except Exception as e2:
                print(f"Error opening URL with fallback method: {e2}")
    
    def run(self):
        if self.connect():
            print("Starting to listen for commands...")
            thread = threading.Thread(target=self.listen)
            thread.daemon = True
            thread.start()
            
            # Keep the main thread alive
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Client stopping...")
            finally:
                if self.socket:
                    self.socket.close()

def main():
    # Get server address from command line arguments
    if len(sys.argv) >= 2:
        server_host = sys.argv[1]
    else:
        # Default to localhost if not specified
        server_host = '192.168.100.58'
    
    # Get server port from command line or use default
    if len(sys.argv) >= 3:
        try:
            server_port = int(sys.argv[2])
        except ValueError:
            print("Invalid port number. Using default port 9999.")
            server_port = 9999
    else:
        server_port = 9999
    
    client = LabClient(server_host, server_port)
    client.run()

if __name__ == "__main__":
    main()