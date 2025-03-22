# server.py - Run this on your primary control computer

import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import os

class LabControlServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}  # {address: socket}
        self.is_running = False
        self.saved_links = self.load_saved_links()
        
    def load_saved_links(self):
        try:
            if os.path.exists('saved_links.json'):
                with open('saved_links.json', 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading saved links: {e}")
            return {}
    
    def save_links(self):
        try:
            with open('saved_links.json', 'w') as f:
                json.dump(self.saved_links, f)
        except Exception as e:
            print(f"Error saving links: {e}")
    
    def start_server(self):
        if self.is_running:
            return
            
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(100)  # Allow up to 100 queued connections
        
        self.is_running = True
        self.accept_thread = threading.Thread(target=self.accept_connections)
        self.accept_thread.daemon = True
        self.accept_thread.start()
        return f"Server started on {self.host}:{self.port}"
    
    def stop_server(self):
        if not self.is_running:
            return
            
        self.is_running = False
        
        # Close all client connections
        for client_socket in list(self.clients.values()):
            try:
                client_socket.close()
            except:
                pass
        
        self.clients.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        return "Server stopped"
    
    def accept_connections(self):
        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                self.clients[client_address] = client_socket
                
                # Start a thread to handle this client
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
                self.log_message(f"New connection from {client_address[0]}:{client_address[1]}")
            except:
                if self.is_running:
                    continue
                break
    
    def handle_client(self, client_socket, address):
        while self.is_running:
            try:
                # Just keep the connection alive, no need to receive data
                data = client_socket.recv(1024)
                if not data:
                    break
                
                # Process any incoming messages from clients if needed
                message = data.decode('utf-8')
                self.log_message(f"Message from {address[0]}: {message}")
                
            except:
                break
        
        # Remove disconnected client
        if address in self.clients:
            del self.clients[address]
            self.log_message(f"Client {address[0]} disconnected")
    
    def broadcast_link(self, url):
        successful = 0
        failed = 0
        
        for address, client_socket in list(self.clients.items()):
            try:
                message = json.dumps({"action": "open_link", "url": url})
                client_socket.send(message.encode('utf-8'))
                successful += 1
            except:
                failed += 1
                # Remove broken connection
                del self.clients[address]
        
        return successful, failed
    
    def broadcast_multiple_links(self, urls):
        successful = 0
        failed = 0
        
        for address, client_socket in list(self.clients.items()):
            try:
                message = json.dumps({"action": "open_multiple_links", "urls": urls})
                client_socket.send(message.encode('utf-8'))
                successful += 1
            except:
                failed += 1
                # Remove broken connection
                del self.clients[address]
        
        return successful, failed
    
    def log_message(self, message):
        # This will be overridden by the GUI to display logs
        print(message)


class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lab Control Server")
        self.root.geometry("800x600")
        
        self.server = LabControlServer()
        
        # Override the log_message method
        self.server.log_message = self.log_message
        
        self.create_widgets()
    
    def create_widgets(self):
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main control tab
        self.control_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.control_frame, text="Control Panel")
        
        # Saved links tab
        self.saved_links_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.saved_links_frame, text="Saved Links")
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Create the control panel widgets
        self.setup_control_panel()
        
        # Create the saved links panel
        self.setup_saved_links_panel()
        
        # Create the settings panel
        self.setup_settings_panel()
    
    def setup_control_panel(self):
        # Server controls section
        server_frame = ttk.LabelFrame(self.control_frame, text="Server Control")
        server_frame.pack(fill=tk.X, padx=10, pady=10)
        
        server_btn_frame = ttk.Frame(server_frame)
        server_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_button = ttk.Button(server_btn_frame, text="Start Server", command=self.start_server)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(server_btn_frame, text="Stop Server", command=self.stop_server)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(server_btn_frame, text="Server Status: Stopped")
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        self.client_count_label = ttk.Label(server_btn_frame, text="Connected Clients: 0")
        self.client_count_label.pack(side=tk.RIGHT, padx=5)
        
        # Link control section
        link_frame = ttk.LabelFrame(self.control_frame, text="Open Link")
        link_frame.pack(fill=tk.X, padx=10, pady=10)
        
        link_input_frame = ttk.Frame(link_frame)
        link_input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(link_input_frame, text="URL:").pack(side=tk.LEFT, padx=5)
        
        self.url_entry = ttk.Entry(link_input_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.send_button = ttk.Button(link_input_frame, text="Open on All Computers", command=self.send_link)
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        self.save_link_button = ttk.Button(link_input_frame, text="Save Link", command=self.save_current_link)
        self.save_link_button.pack(side=tk.LEFT, padx=5)
        
        # Multiple links section
        multiple_links_frame = ttk.LabelFrame(self.control_frame, text="Open Multiple Links")
        multiple_links_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(multiple_links_frame, text="Enter one URL per line:").pack(anchor=tk.W, padx=10, pady=5)
        
        self.multiple_links_text = scrolledtext.ScrolledText(multiple_links_frame, height=5)
        self.multiple_links_text.pack(fill=tk.X, padx=10, pady=5)
        
        multiple_links_btn_frame = ttk.Frame(multiple_links_frame)
        multiple_links_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.send_multiple_button = ttk.Button(
            multiple_links_btn_frame, 
            text="Open All Links", 
            command=self.send_multiple_links
        )
        self.send_multiple_button.pack(side=tk.LEFT, padx=5)
        
        # Log section
        log_frame = ttk.LabelFrame(self.control_frame, text="Server Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.log_text.config(state=tk.DISABLED)
        
        # Update client count
        self.update_client_count()
    
    def setup_saved_links_panel(self):
        # Create a frame for controls
        controls_frame = ttk.Frame(self.saved_links_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(controls_frame, text="Name:").pack(side=tk.LEFT, padx=5)
        self.link_name_entry = ttk.Entry(controls_frame, width=20)
        self.link_name_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(controls_frame, text="URL:").pack(side=tk.LEFT, padx=5)
        self.link_url_entry = ttk.Entry(controls_frame, width=40)
        self.link_url_entry.pack(side=tk.LEFT, padx=5)
        
        self.add_link_button = ttk.Button(controls_frame, text="Add Link", command=self.add_saved_link)
        self.add_link_button.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the treeview
        tree_frame = ttk.Frame(self.saved_links_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the treeview to display saved links
        self.links_tree = ttk.Treeview(
            tree_frame, 
            columns=("name", "url"),
            show="headings"
        )
        
        self.links_tree.heading("name", text="Name")
        self.links_tree.heading("url", text="URL")
        
        self.links_tree.column("name", width=150)
        self.links_tree.column("url", width=450)
        
        self.links_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.links_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.links_tree.configure(yscrollcommand=scrollbar.set)
        
        # Add buttons for actions
        button_frame = ttk.Frame(self.saved_links_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.open_selected_button = ttk.Button(
            button_frame, 
            text="Open Selected Link", 
            command=self.open_selected_link
        )
        self.open_selected_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_link_button = ttk.Button(
            button_frame, 
            text="Delete Selected Link", 
            command=self.delete_selected_link
        )
        self.delete_link_button.pack(side=tk.LEFT, padx=5)
        
        # Load saved links
        self.refresh_saved_links()
    
    def setup_settings_panel(self):
        # Network settings section
        network_frame = ttk.LabelFrame(self.settings_frame, text="Network Settings")
        network_frame.pack(fill=tk.X, padx=10, pady=10)
        
        host_frame = ttk.Frame(network_frame)
        host_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(host_frame, text="Host:").pack(side=tk.LEFT, padx=5)
        self.host_entry = ttk.Entry(host_frame, width=15)
        self.host_entry.insert(0, self.server.host)
        self.host_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(host_frame, text="Port:").pack(side=tk.LEFT, padx=5)
        self.port_entry = ttk.Entry(host_frame, width=6)
        self.port_entry.insert(0, str(self.server.port))
        self.port_entry.pack(side=tk.LEFT, padx=5)
        
        self.save_settings_button = ttk.Button(
            host_frame, 
            text="Save Settings", 
            command=self.save_settings
        )
        self.save_settings_button.pack(side=tk.LEFT, padx=20)
        
        # Help section
        help_frame = ttk.LabelFrame(self.settings_frame, text="Setup Instructions")
        help_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_text = scrolledtext.ScrolledText(help_frame)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        instructions = """Lab Control System Setup Instructions:

1. Server Setup (This Computer):
   - Run this program on your teacher computer
   - Start the server by clicking "Start Server"
   - Note the IP address and port in the settings tab
   
2. Client Setup (Student Computers):
   - Copy the client.py file to all student computers
   - Create a shortcut to run it on startup with the correct server IP:
     Python client.py <your_server_ip> <port>
   - Or create a batch file (.bat) with this command to run on startup
   
3. Usage:
   - Type a URL into the URL field and click "Open on All Computers"
   - For multiple URLs, enter them in the multiple links section
   - Save frequently used links in the Saved Links tab
   
4. Troubleshooting:
   - Make sure all computers are on the same network
   - Check for firewall settings blocking the connection
   - The client count label shows connected computers
   - Check the server log for connection issues
"""
        
        help_text.insert(tk.END, instructions)
        help_text.config(state=tk.DISABLED)
    
    def start_server(self):
        try:
            result = self.server.start_server()
            self.log_message(result)
            self.status_label.config(text="Server Status: Running")
            # Start the updater for client count
            self.update_client_count()
        except Exception as e:
            self.log_message(f"Error starting server: {e}")
    
    def stop_server(self):
        try:
            result = self.server.stop_server()
            self.log_message(result)
            self.status_label.config(text="Server Status: Stopped")
            self.client_count_label.config(text="Connected Clients: 0")
        except Exception as e:
            self.log_message(f"Error stopping server: {e}")
    
    def send_link(self):
        url = self.url_entry.get().strip()
        if not url:
            self.log_message("Please enter a URL")
            return
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
        
        try:
            successful, failed = self.server.broadcast_link(url)
            self.log_message(f"Link sent to {successful} clients ({failed} failed)")
        except Exception as e:
            self.log_message(f"Error sending link: {e}")
    
    def save_current_link(self):
        url = self.url_entry.get().strip()
        if not url:
            self.log_message("Please enter a URL to save")
            return
            
        # Create a simple name from the URL
        name = url.replace('https://', '').replace('http://', '').split('/')[0]
        
        # Ask for a name
        name_window = tk.Toplevel(self.root)
        name_window.title("Save Link")
        name_window.geometry("300x100")
        name_window.resizable(False, False)
        
        ttk.Label(name_window, text="Name for this link:").pack(padx=10, pady=5)
        
        name_entry = ttk.Entry(name_window, width=30)
        name_entry.pack(padx=10, pady=5)
        name_entry.insert(0, name)
        
        def save_and_close():
            link_name = name_entry.get().strip()
            if link_name:
                self.server.saved_links[link_name] = url
                self.server.save_links()
                self.refresh_saved_links()
                self.log_message(f"Link saved: {link_name}")
                name_window.destroy()
        
        ttk.Button(name_window, text="Save", command=save_and_close).pack(pady=10)
    
    def send_multiple_links(self):
        text = self.multiple_links_text.get("1.0", tk.END)
        urls = [line.strip() for line in text.splitlines() if line.strip()]
        
        if not urls:
            self.log_message("Please enter at least one URL")
            return
        
        # Add http:// or https:// to URLs that don't have it
        formatted_urls = []
        for url in urls:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            formatted_urls.append(url)
        
        try:
            successful, failed = self.server.broadcast_multiple_links(formatted_urls)
            self.log_message(f"Multiple links sent to {successful} clients ({failed} failed)")
        except Exception as e:
            self.log_message(f"Error sending multiple links: {e}")
    
    def add_saved_link(self):
        name = self.link_name_entry.get().strip()
        url = self.link_url_entry.get().strip()
        
        if not name or not url:
            self.log_message("Please enter both name and URL")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.link_url_entry.delete(0, tk.END)
            self.link_url_entry.insert(0, url)
        
        self.server.saved_links[name] = url
        self.server.save_links()
        self.refresh_saved_links()
        
        # Clear the entries
        self.link_name_entry.delete(0, tk.END)
        self.link_url_entry.delete(0, tk.END)
        
        self.log_message(f"Link added: {name}")
    
    def open_selected_link(self):
        selected = self.links_tree.selection()
        if not selected:
            self.log_message("Please select a link first")
            return
        
        item = self.links_tree.item(selected[0])
        name = item['values'][0]
        url = item['values'][1]
        
        try:
            successful, failed = self.server.broadcast_link(url)
            self.log_message(f"Link '{name}' sent to {successful} clients ({failed} failed)")
        except Exception as e:
            self.log_message(f"Error sending link: {e}")
    
    def delete_selected_link(self):
        selected = self.links_tree.selection()
        if not selected:
            self.log_message("Please select a link first")
            return
        
        item = self.links_tree.item(selected[0])
        name = item['values'][0]
        
        # Remove from the saved links
        if name in self.server.saved_links:
            del self.server.saved_links[name]
            self.server.save_links()
            self.refresh_saved_links()
            self.log_message(f"Link deleted: {name}")
    
    def refresh_saved_links(self):
        # Clear the treeview
        for item in self.links_tree.get_children():
            self.links_tree.delete(item)
        
        # Add all saved links
        for name, url in self.server.saved_links.items():
            self.links_tree.insert("", tk.END, values=(name, url))
    
    def save_settings(self):
        try:
            host = self.host_entry.get().strip()
            port = int(self.port_entry.get().strip())
            
            # Save the new settings
            self.server.host = host
            self.server.port = port
            
            # If the server is running, restart it
            was_running = self.server.is_running
            if was_running:
                self.server.stop_server()
            
            if was_running:
                self.server.start_server()
            
            self.log_message(f"Settings saved. Server will use {host}:{port}")
        except Exception as e:
            self.log_message(f"Error saving settings: {e}")
    
    def update_client_count(self):
        if hasattr(self, 'client_count_label'):
            client_count = len(self.server.clients)
            self.client_count_label.config(text=f"Connected Clients: {client_count}")
        
        # Schedule the next update
        if self.server.is_running:
            self.root.after(2000, self.update_client_count)
    
    def log_message(self, message):
        # Enable the widget to insert text
        self.log_text.config(state=tk.NORMAL)
        
        # Add timestamp and message
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        # Auto-scroll to the end
        self.log_text.see(tk.END)
        
        # Disable the widget again
        self.log_text.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = ServerGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.server.stop_server(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    main()