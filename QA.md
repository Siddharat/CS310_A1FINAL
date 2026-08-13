# CS310 Assignment 1 - Instructor Q&A Prep (Detailed & Simple)

## 1. How does client-server communication work (protocol)?
**Explanation**: Step-by-step:
- Client connects socket, sends exact filename as bytes.
- Server checks file, computes size/MD5, sends header `"OK:{size}:{md5}"`.
- If OK, server reads/sends file in chunks until end.
- Client receives exact size bytes, writes to file.

**Show in Code**:
- Server: `fileserver.py` Ctrl+F `"OK:"` → see `header = f"OK:{file_size}:{checksum}"`.
- Client: `client.py` Ctrl+F `"split(":"` → `parts = response.split(":")` gets size/md5.

## 2. Explain MD5 checksum - purpose & how?
**Explanation**: MD5 creates unique 32-char hash of file. Server hashes before send, client after receive/compare. Mismatch = corruption/alert.

**Show in Code**:
- Both files: Ctrl+F `get_checksum` (top) → `md5 = hashlib.md5()` loops `chunk = f.read()`.
- Client verify: Ctrl+F `local_md5 ==` → `if local_md5 == server_md5: "✓"`.

## 3. How does progress bar, speed, ETA work?
**Explanation**: After header, client knows total bytes. Each chunk: % = received/total*100, speed = total_received/time_elapsed, ETA = remaining/speed. Updates GUI every chunk.

**Show in Code**:
- `client.py` Ctrl+F `speed =` → `_download_worker`: `speed = bytes_received / elapsed`, `eta = remaining_b / speed`.
- GUI update: Ctrl+F `_update_progress`.

## 4. Why doesn't GUI freeze during download?
**Explanation**: Download runs in separate thread (`threading.Thread`). GUI updates queued to main thread with `root.after()` to avoid blocking.

**Show in Code**:
- Client: Ctrl+F `Thread(` → `threading.Thread(target=self._download_worker)`.
- Update: Ctrl+F `root.after(0,` → e.g., `self.root.after(0, self._log, ...)`.

Server similar for accept loop.

## 5. How/where is transfer logging done?
**Explanation**: Server calls after each transfer: opens `transfer_log.txt` append mode, writes `[time] Client IP | File | Size | SUCCESS/FAIL`.

**Show in Code**:
- `fileserver.py` Ctrl+F `log_transfer` → function def + call after `conn.close()`.
- File: Open `transfer_log.txt` shows real logs.

## 6. What error handling is there?
**Explanation**: File missing → server sends msg (no crash). No server → client catches exception. Checksum fail → warning popup/log.

**Show in Code**:
- Server: Ctrl+F `os.path.exists(filename)` → `if not: send error`.
- Client: Ctrl+F `ConnectionRefusedError` → `self._log("Connection refused")`.

## 7. How does it handle large files?
**Explanation**: Fixed `BUFFER_SIZE=4096` chunks. Loops read/send until 0 bytes. Last chunk uses remaining size.

**Show in Code**:
- Top both files: `BUFFER_SIZE = 4096`.
- Client/server loops: Ctrl+F `min(BUFFER_SIZE, remaining)`.

## 8. Does it support multiple clients?
**Explanation**: `listen(5)` queues up to 5. Handles sequentially in loop (one finish → next).

**Show in Code**:
- `fileserver.py` Ctrl+F `listen(5)` → `self.server_socket.listen(5)`.
- Loop: Ctrl+F `_accept_loop`.

## 9. GUI details (dark theme, colors)?
**Explanation**: Tkinter standard + custom bg colors (`#1e1e2e` dark), progress `ttk.Style`, log colors via `tag_config("success", fg=green)`.

**Show in Code**:
- Any file Ctrl+F `bg="#1e` → themes.
- Logs: Ctrl+F `tag_config` → colored messages.

**Demo Tip**: Keep VSCode open with files; Ctrl+F during Q. Run live: `python fileserver.py` then client. Perfect!

## Q4: Why threading? GUI responsive?
**A**: Download in `threading.Thread(daemon=True)`; GUI updates via `root.after(0, callback)` marshals to main thread.

**Code**:
- Server: `_accept_loop` thread.
- Client: `threading.Thread(target=_download_worker)`

## Q5: How logging works? Format?
**A**: Server appends to `transfer_log.txt`: `[timestamp] Client:IP | File | Size | Status`. GUI `scrolledtext`.

**Code**: `fileserver.py` L~60 `log_transfer()`: `open("transfer_log.txt", "a")`; called post-transfer.

## Q6: Error handling examples?
**A**: File not exist → "File does not exist". Conn refused → `ConnectionRefusedError`. Chunk loss → checksum fail warning.

**Code**:
- Server: `if not os.path.exists(filename)`
- Client: `try/except ConnectionRefusedError`

## Q7: Buffer size role? Large files?
**A**: `BUFFER_SIZE=4096`: Chunks prevent memory overload. `min(BUFFER_SIZE, remaining)` last chunk.

**Code**: `client.py`/`fileserver.py` top: `BUFFER_SIZE=4096`; loops `chunk = recv/read(chunk_size)`

## Q8: Cross-platform? (Linux screenshot)
**A**: Std lib only (socket, tk, hashlib); paths/encodings neutral.

**Code**: `Images/Linux.png`; Windows paths ok.

## Q9: Multi-client support?
**A**: Server handles one-at-a-time (`_accept_loop` sequential); queue=5 `listen(5)`. Extensible to threads-per-client.

**Code**: `self.server_socket.listen(5)`

## Q10: GUI framework? Custom styling?
**A**: Tkinter (`ttk.Progressbar`); dark theme (`bg="#1e1e2e"`), tags for colored logs.

**Code**: `client.py`/`fileserver.py` `_build_*` methods; `self.log_area.tag_config(...)`

**Prep Tip**: Point to code lines in VSCode; run live transfer if asked. Use `QA.md` as cheat sheet.

