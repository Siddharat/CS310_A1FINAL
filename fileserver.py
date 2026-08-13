# ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
# fileserver.py
# CS310 - Computer Networks - Assignment 1
# Author: Praheel Kumar - [S11229535]
#       : Shivan Prasad - [S11231502]
# Description: TCP File Transfer Server with Tkinter GUI
# _________________________________________________________

# library imports
from socket import *       # Socket programming
import os                  # File system operations
import threading           # Run server in background without freezing GUI
import datetime            # Timestamps for activity log
import hashlib             # MD5 checksum for file integrity verification

# GUI library
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
# Configuration
# _______________
SERVER_IP   = '127.0.0.1'
SERVER_PORT = 5000
BUFFER_SIZE = 4096


# ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
# Helper function - MD5 checksum
# Generates a unique fingerprint of a file
# Used to verify the client received an uncorrupted file
# _______________________________________________________
def get_checksum(filepath):
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            md5.update(chunk)
    return md5.hexdigest()


# ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
# Helper function - transfer log
# Appends every transfer result to a log file on disk
# ____________________________________________________
def log_transfer(filename, size, client_address, status):
    with open("transfer_log.txt", "a") as log:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.write(
            f"[{timestamp}] Client: {client_address} | "
            f"File: {filename} | Size: {size} bytes | Status: {status}\n"
        )


# ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
# Main sever GUI class
# All GUI elements and server logic live here
# ____________________________________________
class FileServerGUI:

    def __init__(self, root):
        """
        Constructor — builds the entire GUI when the app starts.
        root: the main Tkinter window passed in from the bottom of the file
        """
        self.root = root
        self.root.title("File Transfer Application")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")   # Dark background

        # Server state variables
        self.server_running = False          # Tracks if server is active
        self.server_socket  = None           # The main listening socket

        # Build all GUI sections
        self._build_header()
        self._build_status_bar()
        self._build_controls()
        self._build_log_area()
        self._build_footer()

        # Handle window close button
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)


    # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
    # GUI builder methods
    # Each method builds one section of the interface
    # ________________________________________________

    def _build_header(self):
        """Top banner with title"""
        header_frame = tk.Frame(self.root, bg="#313244", pady=10)
        header_frame.pack(fill=tk.X)

        tk.Label(
            header_frame,
            text="File Transfer Application",
            font=("Helvetica", 16, "bold"),
            fg="#cdd6f4",
            bg="#313244"
        ).pack()

        tk.Label(
            header_frame,
            text="TCP Socket Application  |  Computer Networks",
            font=("Helvetica", 9),
            fg="#a6adc8",
            bg="#313244"
        ).pack()


    def _build_status_bar(self):
        """Shows current server IP, port, and running status"""
        status_frame = tk.Frame(self.root, bg="#1e1e2e", pady=8)
        status_frame.pack(fill=tk.X, padx=15)

        # Status indicator dot - red when stopped, green when running
        self.status_dot = tk.Label(
            status_frame,
            text="🔴",
            font=("Helvetica", 14),
            fg="#f38ba8",   # Red = stopped
            bg="#1e1e2e"
        )
        self.status_dot.pack(side=tk.LEFT)

        self.status_label = tk.Label(
            status_frame,
            text="  Server Stopped",
            font=("Helvetica", 11),
            fg="#cdd6f4",
            bg="#1e1e2e"
        )
        self.status_label.pack(side=tk.LEFT)

        # Show IP and Port on the right side
        tk.Label(
            status_frame,
            text=f"IP: {SERVER_IP}   Port: {SERVER_PORT}",
            font=("Helvetica", 10),
            fg="#6c7086",
            bg="#1e1e2e"
        ).pack(side=tk.RIGHT)


    def _build_controls(self):
        """Start and Stop buttons"""
        control_frame = tk.Frame(self.root, bg="#1e1e2e", pady=5)
        control_frame.pack(fill=tk.X, padx=15)

        # Start server button
        self.start_btn = tk.Button(
            control_frame,
            text="🟢  Start Server",
            font=("Helvetica", 11, "bold"),
            bg="#a6e3a1",       # Green
            fg="#1e1e2e",
            relief=tk.FLAT,
            padx=20, pady=6,
            cursor="hand2",
            command=self._start_server   # Calls _start_server when clicked
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Stop server button
        self.stop_btn = tk.Button(
            control_frame,
            text="🟥  Stop Server",
            font=("Helvetica", 11, "bold"),
            bg="#f38ba8",        # Red
            fg="#1e1e2e",
            relief=tk.FLAT,
            padx=20, pady=6,
            cursor="hand2",
            state=tk.DISABLED,   # Disabled until server starts
            command=self._stop_server
        )
        self.stop_btn.pack(side=tk.LEFT)

        # Clear log button
        tk.Button(
            control_frame,
            text="🗑  Clear Log",
            font=("Helvetica", 10),
            bg="#313244",
            fg="#cdd6f4",
            relief=tk.FLAT,
            padx=15, pady=6,
            cursor="hand2",
            command=self._clear_log
        ).pack(side=tk.RIGHT)


    def _build_log_area(self):
        """Scrollable activity log showing all server events"""
        log_frame = tk.Frame(self.root, bg="#1e1e2e")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 5))

        tk.Label(
            log_frame,
            text="Activity Log",
            font=("Helvetica", 10, "bold"),
            fg="#a6adc8",
            bg="#1e1e2e"
        ).pack(anchor=tk.W)

        # ScrolledText widget — like a text box with a scrollbar
        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            font=("Courier", 9),
            bg="#181825",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief=tk.FLAT,
            state=tk.DISABLED,   # Read only — only code can write to it
            height=16
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)

        # colour tags for different message types
        self.log_area.tag_config("info",    foreground="#89b4fa")   # Blue
        self.log_area.tag_config("success", foreground="#a6e3a1")   # Green
        self.log_area.tag_config("error",   foreground="#f38ba8")   # Red
        self.log_area.tag_config("warning", foreground="#fab387")   # Orange
        self.log_area.tag_config("time",    foreground="#6c7086")   # Grey


    def _build_footer(self):
        """Bottom bar showing transfer count"""
        footer_frame = tk.Frame(self.root, bg="#313244", pady=5)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.transfer_count = tk.Label(
            footer_frame,
            text="Transfers completed: 0",
            font=("Helvetica", 9),
            fg="#a6adc8",
            bg="#313244"
        )
        self.transfer_count.pack()

        # Keep a counter
        self._transfers = 0


    # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
    # Logging method
    # All server messages go through here to appear in the log
    # _________________________________________________________

    def _log(self, message, tag="info"):
        """
        Write a timestamped message to the activity log.
        tag: controls the colour ("info", "success", "error", "warning")
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # Must enable the widget to write, then disable again
        self.log_area.config(state=tk.NORMAL)

        # Insert timestamp in grey
        self.log_area.insert(tk.END, f"[{timestamp}] ", "time")

        # Insert message with colour based on tag
        self.log_area.insert(tk.END, f"{message}\n", tag)

        # Auto-scroll to bottom so latest message is always visible
        self.log_area.see(tk.END)

        self.log_area.config(state=tk.DISABLED)


    def _clear_log(self):
        """Clears all text from the activity log"""
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state=tk.DISABLED)


    # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
    # Server control methods
    # _______________________

    def _start_server(self):
        """
        Called when Start button is clicked.
        Creates the socket and starts the listening loop
        in a background thread so the GUI stays responsive.
        """
        if self.server_running:
            return

        try:
            # Create TCP socket
            # AF_INET = IPv4, SOCK_STREAM = TCP
            self.server_socket = socket(AF_INET, SOCK_STREAM)

            # SO_REUSEADDR lets us restart quickly without address in use error
            self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

            # Bind to all interfaces on the configured port
            self.server_socket.bind(('', SERVER_PORT))

            # Listen queue up to 5 incoming connections
            self.server_socket.listen(5)

            self.server_running = True

            # Update GUI to show running state
            self.status_dot.config(fg="#a6e3a1")        # Green dot
            self.status_label.config(text="  Server Running — Waiting for clients...")
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)

            self._log(f"Server started on {SERVER_IP}:{SERVER_PORT}", "success")
            self._log("Waiting for client connections...", "info")

            # Start the accept loop in a background thread
            # daemon=True means this thread dies when the main window closes
            self.server_thread = threading.Thread(
                target=self._accept_loop,
                daemon=True
            )
            self.server_thread.start()

        except Exception as e:
            messagebox.showerror("Server Error", str(e))
            self._log(f"Failed to start: {e}", "error")


    def _stop_server(self):
        """Called when Stop button is clicked. Shuts down the server."""
        self.server_running = False

        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        # Reset GUI to stopped state
        self.status_dot.config(fg="#f38ba8")     # Red dot
        self.status_label.config(text="  Server Stopped")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

        self._log("Server stopped by user.", "warning")


    # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
    # Core server logic
    # This runs in a background thread
    # _________________________________

    def _accept_loop(self):
        """
        Waits for one client connection at a time.
        Fully handles each client before accepting the next.
        Runs in a background thread only to keeep the GUI responsive.
        """
        while self.server_running:
            try:
                # Block here waiting for a client to connect
                connection_socket, client_address = self.server_socket.accept()

                # Log the new connection
                self.root.after(0, self._log,
                    f"Client connected from {client_address}", "info")
                
                self._handle_client(connection_socket, client_address)
            except:
                # Socket was closed
                break


    def _handle_client(self, conn, addr):
        """
        Handles one complete client file transfer.
        conn: the connection socket for this specific client
        addr: (ip, port) tuple of the client
        """
        try:
            # Receive the filename request
            filename = conn.recv(BUFFER_SIZE).decode().strip()
            self.root.after(0, self._log,
                f"File requested: '{filename}' by {addr}", "info")

            # Check if file exists
            if not os.path.exists(filename):
                conn.send("File does not exist".encode())
                self.root.after(0, self._log,
                    f"File '{filename}' not found — error sent.", "error")
                log_transfer(filename, 0, addr, "FAILED - Not Found")
                return

            # File exists, get size and checksum
            file_size = os.path.getsize(filename)
            checksum  = get_checksum(filename)

            # Send header
            # This is our custom application-layer protocol header
            # The client reads this to know how much data to expect
            # and the checksum to verify integrity after download
            header = f"OK:{file_size}:{checksum}"
            conn.send(header.encode())

            self.root.after(0, self._log,
                f"Sending '{filename}' ({file_size} bytes)...", "info")

            # Send the file in chunks
            bytes_sent = 0
            with open(filename, 'rb') as f:
                while True:
                    chunk = f.read(BUFFER_SIZE)
                    if not chunk:
                        break
                    conn.send(chunk)
                    bytes_sent += len(chunk)

            # Transfer complete
            self._transfers += 1
            self.root.after(0, self._log,
                f"Transfer complete: '{filename}' ({bytes_sent} bytes) ✓", "success")
            self.root.after(0, self._update_transfer_count)

            # Log to file
            log_transfer(filename, file_size, addr, "SUCCESS")

        except Exception as e:
            self.root.after(0, self._log, f"Transfer error: {e}", "error")

        finally:
            conn.close()


    def _update_transfer_count(self):
        """Updates the footer counter label"""
        self.transfer_count.config(
            text=f"Transfers completed: {self._transfers}"
        )


    def _on_close(self):
        """Called when user clicks the X to close the window"""
        if self.server_running:
            self._stop_server()
        self.root.destroy()


# ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
# Run the application
# __________________________________
if __name__ == "__main__":
    root = tk.Tk()
    app  = FileServerGUI(root)
    root.mainloop()    # Starts the GUI event loop