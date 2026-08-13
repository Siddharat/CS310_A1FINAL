# ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
# client.py
# CS310 - Computer Networks - Assignment 1
# Author: Praheel Kumar - [S11229535]
#       : Shivan Prasad - [S11231502]
# Description: TCP File Transfer Client with Tkinter GUI
# _______________________________________________________

# library imports
from socket import *
import os
import threading
import time
import hashlib

# GUI library
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# ¯¯¯¯¯¯¯¯¯¯¯¯¯¯
# Configuration
# ______________
DEFAULT_IP   = '127.0.0.1'
DEFAULT_PORT = '5000'
BUFFER_SIZE  = 4096


# ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
# Helper - MD5 Checksum
# ______________________
def get_checksum(filepath):
    """Generate MD5 checksum of a local file for integrity check"""
    md5 = hashlib.md5()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            md5.update(chunk)
    return md5.hexdigest()


# ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
# Main client GUI class
# ______________________
class FileClientGUI:

    def __init__(self, root):
        """
        Constructor — builds the entire client GUI.
        root: main Tkinter window
        """
        self.root = root
        self.root.title("Client Application")
        self.root.geometry("560x580")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        # Track download state
        self.downloading = False

        # Build GUI sections
        self._build_header()
        self._build_connection_frame()
        self._build_file_frame()
        self._build_progress_frame()
        self._build_log_area()
        self._build_footer()


    # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
    # GUI builder methods
    # ____________________

    def _build_header(self):
        """Top banner"""
        header = tk.Frame(self.root, bg="#313244", pady=10)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="Client Application",
            font=("Helvetica", 16, "bold"),
            fg="#cdd6f4",
            bg="#313244"
        ).pack()

        tk.Label(
            header,
            text="TCP Socket Application  |  Computer Networks",
            font=("Helvetica", 9),
            fg="#a6adc8",
            bg="#313244"
        ).pack()


    def _build_connection_frame(self):
        """Server IP and Port input fields"""
        conn_frame = tk.LabelFrame(
            self.root,
            text=" Server Connection ",
            font=("Helvetica", 9, "bold"),
            fg="#a6adc8",
            bg="#1e1e2e",
            bd=1,
            relief=tk.GROOVE
        )
        conn_frame.pack(fill=tk.X, padx=15, pady=(10, 5))

        inner = tk.Frame(conn_frame, bg="#1e1e2e")
        inner.pack(padx=10, pady=8)

        # Server IP
        tk.Label(
            inner,
            text="Server IP:",
            font=("Helvetica", 10),
            fg="#cdd6f4",
            bg="#1e1e2e",
            width=10,
            anchor=tk.W
        ).grid(row=0, column=0, padx=(0, 5))

        self.ip_entry = tk.Entry(
            inner,
            font=("Helvetica", 10),
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief=tk.FLAT,
            width=20
        )
        self.ip_entry.insert(0, DEFAULT_IP)   # Pre-fill with default
        self.ip_entry.grid(row=0, column=1, padx=(0, 20))

        # Port
        tk.Label(
            inner,
            text="Port:",
            font=("Helvetica", 10),
            fg="#cdd6f4",
            bg="#1e1e2e",
            width=5,
            anchor=tk.W
        ).grid(row=0, column=2, padx=(0, 5))

        self.port_entry = tk.Entry(
            inner,
            font=("Helvetica", 10),
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief=tk.FLAT,
            width=8
        )
        self.port_entry.insert(0, DEFAULT_PORT)
        self.port_entry.grid(row=0, column=3)


    def _build_file_frame(self):
        """Filename input with Browse button and Download button"""
        file_frame = tk.LabelFrame(
            self.root,
            text=" File Request ",
            font=("Helvetica", 9, "bold"),
            fg="#a6adc8",
            bg="#1e1e2e",
            bd=1,
            relief=tk.GROOVE
        )
        file_frame.pack(fill=tk.X, padx=15, pady=5)

        inner = tk.Frame(file_frame, bg="#1e1e2e")
        inner.pack(padx=10, pady=8, fill=tk.X)

        tk.Label(
            inner,
            text="Filename:",
            font=("Helvetica", 10),
            fg="#cdd6f4",
            bg="#1e1e2e",
            width=10,
            anchor=tk.W
        ).grid(row=0, column=0, padx=(0, 5))

        # Filename entry box
        self.file_entry = tk.Entry(
            inner,
            font=("Helvetica", 10),
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief=tk.FLAT,
            width=28
        )
        self.file_entry.grid(row=0, column=1, padx=(0, 5))

        # Browse button - opens file dialog to pick filename
        tk.Button(
            inner,
            text="Browse",
            font=("Helvetica", 9),
            bg="#313244",
            fg="#cdd6f4",
            relief=tk.FLAT,
            padx=8,
            cursor="hand2",
            command=self._browse_file   # Opens file picker dialog
        ).grid(row=0, column=2, padx=(0, 5))

        # Download button
        self.download_btn = tk.Button(
            inner,
            text="⬇  Download",
            font=("Helvetica", 11, "bold"),
            bg="#89b4fa",    # Blue
            fg="#1e1e2e",
            relief=tk.FLAT,
            padx=15, pady=4,
            cursor="hand2",
            command=self._start_download   # Starts the download
        )
        self.download_btn.grid(row=1, column=0, columnspan=3,
                                pady=(10, 0), sticky=tk.W)


    def _build_progress_frame(self):
        """Progress bar and transfer statistics"""
        prog_frame = tk.LabelFrame(
            self.root,
            text=" Transfer Progress ",
            font=("Helvetica", 9, "bold"),
            fg="#a6adc8",
            bg="#1e1e2e",
            bd=1,
            relief=tk.GROOVE
        )
        prog_frame.pack(fill=tk.X, padx=15, pady=5)

        inner = tk.Frame(prog_frame, bg="#1e1e2e")
        inner.pack(padx=10, pady=8, fill=tk.X)

        # Progress bar widget
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "custom.Horizontal.TProgressbar",
            troughcolor="#313244",
            background="#89b4fa",
            thickness=20
        )

        self.progress_bar = ttk.Progressbar(
            inner,
            style="custom.Horizontal.TProgressbar",
            orient=tk.HORIZONTAL,
            length=500,
            mode='determinate'    # Shows actual percentage
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))

        # Stats row: percentage, speed, ETA
        stats_frame = tk.Frame(inner, bg="#1e1e2e")
        stats_frame.pack(fill=tk.X)

        self.percent_label = tk.Label(
            stats_frame,
            text="0%",
            font=("Helvetica", 10, "bold"),
            fg="#89b4fa",
            bg="#1e1e2e",
            width=6
        )
        self.percent_label.pack(side=tk.LEFT)

        self.speed_label = tk.Label(
            stats_frame,
            text="Speed: —",
            font=("Helvetica", 9),
            fg="#a6adc8",
            bg="#1e1e2e"
        )
        self.speed_label.pack(side=tk.LEFT, padx=20)

        self.eta_label = tk.Label(
            stats_frame,
            text="ETA: —",
            font=("Helvetica", 9),
            fg="#a6adc8",
            bg="#1e1e2e"
        )
        self.eta_label.pack(side=tk.LEFT)

        self.bytes_label = tk.Label(
            stats_frame,
            text="0 / 0 bytes",
            font=("Helvetica", 9),
            fg="#6c7086",
            bg="#1e1e2e"
        )
        self.bytes_label.pack(side=tk.RIGHT)


    def _build_log_area(self):
        """Activity log for client events"""
        log_frame = tk.Frame(self.root, bg="#1e1e2e")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 5))

        tk.Label(
            log_frame,
            text="Activity Log",
            font=("Helvetica", 10, "bold"),
            fg="#a6adc8",
            bg="#1e1e2e"
        ).pack(anchor=tk.W)

        self.log_area = scrolledtext.ScrolledText(
            log_frame,
            font=("Courier", 9),
            bg="#181825",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief=tk.FLAT,
            state=tk.DISABLED,
            height=8
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)

        # Colour tags
        self.log_area.tag_config("info",    foreground="#89b4fa")
        self.log_area.tag_config("success", foreground="#a6e3a1")
        self.log_area.tag_config("error",   foreground="#f38ba8")
        self.log_area.tag_config("warning", foreground="#fab387")
        self.log_area.tag_config("time",    foreground="#6c7086")


    def _build_footer(self):
        """Bottom status bar"""
        footer = tk.Frame(self.root, bg="#313244", pady=5)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_bar = tk.Label(
            footer,
            text="Ready",
            font=("Helvetica", 9),
            fg="#a6adc8",
            bg="#313244"
        )
        self.status_bar.pack()


    # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
    # Logging method
    # _______________

    def _log(self, message, tag="info"):
        """Write a timestamped message to the activity log"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"[{timestamp}] ", "time")
        self.log_area.insert(tk.END, f"{message}\n", tag)
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)


    # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
    # Action methods
    # _______________

    def _browse_file(self):
        """
        Opens a file dialog so user can browse to a file.
        Only fills in the filename — the server must have the file.
        """
        filepath = filedialog.askopenfilename(
            title="Select a file to request from server"
        )
        if filepath:
            # Extract just the filename from the full path
            filename = os.path.basename(filepath)
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)


    def _start_download(self):
        """
        Called when Download button is clicked.
        Validates inputs then starts download in background thread.
        """
        if self.downloading:
            self._log("Download already in progress.", "warning")
            return

        # Validate inputs
        server_ip   = self.ip_entry.get().strip()
        port_str    = self.port_entry.get().strip()
        filename    = self.file_entry.get().strip()

        if not server_ip or not port_str or not filename:
            messagebox.showwarning("Missing Input",
                "Please fill in Server IP, Port, and Filename.")
            return

        try:
            server_port = int(port_str)
        except ValueError:
            messagebox.showerror("Invalid Port", "Port must be a number.")
            return

        # Reset progress display
        self.progress_bar['value'] = 0
        self.percent_label.config(text="0%")
        self.speed_label.config(text="Speed: —")
        self.eta_label.config(text="ETA: —")
        self.bytes_label.config(text="0 / 0 bytes")

        # Disable button during download
        self.download_btn.config(state=tk.DISABLED)
        self.downloading = True

        # Run download in background thread so GUI stays responsive
        thread = threading.Thread(
            target=self._download_worker,
            args=(server_ip, server_port, filename),
            daemon=True
        )
        thread.start()


    def _download_worker(self, server_ip, server_port, filename):
        """
        Core download logic — runs in a background thread.
        Handles: connect → request → receive header → 
                 receive file → verify checksum → save file
        """
        client_socket = socket(AF_INET, SOCK_STREAM)

        try:
            # Connect to server
            self.root.after(0, self._log,
                f"Connecting to {server_ip}:{server_port}...", "info")
            self.root.after(0, self._set_status, "Connecting...")

            client_socket.connect((server_ip, server_port))
            self.root.after(0, self._log, "Connected to server!", "success")

            # Send filename request
            client_socket.send(filename.encode())
            self.root.after(0, self._log,
                f"Requested file: '{filename}'", "info")

            # Receive server response
            response = client_socket.recv(BUFFER_SIZE).decode()

            # Check for error
            if not response.startswith("OK:"):
                self.root.after(0, self._log,
                    f"Server: {response}", "error")
                self.root.after(0, self._set_status, "Failed")
                return

            # Parse header
            parts      = response.split(":")
            total_size = int(parts[1])
            server_md5 = parts[2]

            self.root.after(0, self._log,
                f"File size: {total_size} bytes | MD5: {server_md5[:12]}...",
                "info")
            self.root.after(0, self._set_status, "Downloading...")

            # Build save filename with _downloaded suffix
            name, ext = os.path.splitext(filename)
            save_name = name + "_downloaded" + ext

            # Receive file data
            bytes_received = 0
            start_time     = time.time()

            with open(save_name, 'wb') as f:
                while bytes_received < total_size:
                    # Calculate how much to request this time
                    remaining = total_size - bytes_received
                    chunk_size = min(BUFFER_SIZE, remaining)

                    chunk = client_socket.recv(chunk_size)

                    if not chunk:
                        self.root.after(0, self._log,
                            "Connection lost during transfer!", "error")
                        break

                    f.write(chunk)
                    bytes_received += len(chunk)

                    # Calculate progress statistics
                    progress    = (bytes_received / total_size) * 100
                    elapsed     = time.time() - start_time
                    speed       = bytes_received / elapsed if elapsed > 0 else 0
                    remaining_b = total_size - bytes_received
                    eta         = remaining_b / speed if speed > 0 else 0

                    # Format speed nicely
                    if speed >= 1024 * 1024:
                        speed_str = f"{speed/1024/1024:.1f} MB/s"
                    elif speed >= 1024:
                        speed_str = f"{speed/1024:.1f} KB/s"
                    else:
                        speed_str = f"{speed:.0f} B/s"

                    # Format ETA
                    eta_str = f"{eta:.1f}s" if eta > 0 else "0s"

                    # Update GUI from main thread using after()
                    self.root.after(0, self._update_progress,
                        progress, speed_str, eta_str,
                        bytes_received, total_size)

            # Verify file integrity with MD5 checksum
            self.root.after(0, self._log,
                "Verifying file integrity...", "info")

            local_md5 = get_checksum(save_name)

            if local_md5 == server_md5:
                self.root.after(0, self._log,
                    "File integrity verified ✓ (MD5 match)", "success")
            else:
                self.root.after(0, self._log,
                    "WARNING: Checksum mismatch — file may be corrupted!",
                    "error")

            # ---- Done ----
            self.root.after(0, self._log,
                f"Download complete! Saved as '{save_name}'", "success")
            self.root.after(0, self._set_status, "Download Complete ✓")
            self.root.after(0, self._update_progress,
                100, "—", "Done", total_size, total_size)

        except ConnectionRefusedError:
            self.root.after(0, self._log,
                "Connection refused. Is the server running?", "error")
            self.root.after(0, self._set_status, "Connection Failed")

        except Exception as e:
            self.root.after(0, self._log, f"Error: {e}", "error")
            self.root.after(0, self._set_status, "Error")

        finally:
            client_socket.close()
            self.downloading = False
            # Re-enable button
            self.root.after(0, lambda: self.download_btn.config(
                state=tk.NORMAL))


    # ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
    # GUI update methods
    # ___________________

    def _update_progress(self, percent, speed, eta,
                         received, total):
        """Updates all progress display elements"""
        self.progress_bar['value'] = percent
        self.percent_label.config(text=f"{percent:.1f}%")
        self.speed_label.config(text=f"Speed: {speed}")
        self.eta_label.config(text=f"ETA: {eta}")
        self.bytes_label.config(text=f"{received:,} / {total:,} bytes")


    def _set_status(self, message):
        """Updates the footer status bar"""
        self.status_bar.config(text=message)


# ¯¯¯¯¯¯¯¯¯¯¯¯
# Entry point
# ____________
if __name__ == "__main__":
    root = tk.Tk()
    app  = FileClientGUI(root)
    root.mainloop()