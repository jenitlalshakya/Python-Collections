import os
import socket
from socketserver import ThreadingMixIn
import urllib.parse
from http.server import SimpleHTTPRequestHandler, HTTPServer

MUSIC_FOLDER = r"D:\YouTube Musics"
PORT = 8000

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def make_safe_filename(filename):
    name, ext = os.path.splitext(filename)
    safe_name = name
    safe_name = safe_name.replace(" ", "_")

    for ch in [f'[', ']', '(', ')', '{', '}', '&', '#', '%']:
        safe_name = safe_name.replace(ch, "")
    return safe_name + ext

def prepare_files(folder):
    mapping ={}
    for file in os.listdir(folder):
        safe_name = make_safe_filename(file)
        mapping[safe_name] = file
    return mapping

class MusicHandler(SimpleHTTPRequestHandler):
    file_mapping = prepare_files(MUSIC_FOLDER)

    def translate_path(self, path):
        path = urllib.parse.unquote(path[1:])
        if path in self.file_mapping:
            path = self.file_mapping[path]
        return os.path.join(MUSIC_FOLDER, path)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

if __name__ == "__main__":
    HOST = "0.0.0.0"
    local_ip = get_local_ip()

    print(f"📂 Serving music from: {MUSIC_FOLDER}")
    print(f"🌐 Access on mobile via: http://{local_ip}:{PORT}/<filename>")
    print("💡 Example URL:")
    for safe, actual in MusicHandler.file_mapping.items():
        print(f"  http://{local_ip}:{PORT}/{safe}")
    print("\nPress CTRL+C to stop.\n")

    server = ThreadedHTTPServer((HOST, PORT), MusicHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped.")
        server.server_close()