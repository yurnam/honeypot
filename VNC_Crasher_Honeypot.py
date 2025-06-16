# VNC_Crasher_Honeypot.py

import socket
import threading
import time
from datetime import datetime
from telegram import send_telegram_message
import os
import struct

class VNCCrasherHoneypot:
    def __init__(self, host='0.0.0.0', port=5900):
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(100)
        print(f"[VNCCrasherHoneypot] Listening on port {self.port} (VNC)...")

        while True:
            client, addr = sock.accept()
            threading.Thread(target=self.handle_client, args=(client, addr), daemon=True).start()

    def handle_client(self, client, addr):
        try:
            print(f"[VNCCrasherHoneypot] Connection from {addr}")

            client.settimeout(10.0)

            # 1️⃣ Send version string (valid)
            server_version = b"RFB 003.008\n"  # VNC 3.8
            client.sendall(server_version)

            # 2️⃣ Receive client version
            client_version = client.recv(1024)

            msg = f"*VNC connection!* 🐝\n"
            msg += f"`{datetime.utcnow().isoformat()}`\n"
            msg += f"*IP:* `{addr[0]}`\n"
            msg += f"*Client version:* `{client_version.decode(errors='ignore').strip()}`\n"

            send_telegram_message(msg)

            # 3️⃣ Send SecurityTypes → NoAuth
            client.sendall(b'\x01\x01')  # One security type, None

            # 4️⃣ Send SecurityResult OK
            client.sendall(b'\x00\x00\x00\x00')

            # 5️⃣ Receive ClientInit (shared flag)
            shared_flag = client.recv(1)

            # Framebuffer size (matching ServerInit)
            frame_width = 128
            frame_height = 96

            # Pixel format — valid format
            pixel_format = (
                b'\x20' +  # bitsPerPixel = 32
                b'\x18' +  # depth = 24
                b'\x00' +  # bigEndianFlag
                b'\x01' +  # trueColourFlag
                b'\x00\xff' +  # redMax
                b'\x00\xff' +  # greenMax
                b'\x00\xff' +  # blueMax
                b'\x10' +  # redShift
                b'\x08' +  # greenShift
                b'\x00' +  # blueShift
                b'\x00\x00\x00'  # padding (3 bytes)
            )

            # 6️⃣ Send ServerInit
            serverinit = (
                frame_width.to_bytes(2, 'big') +
                frame_height.to_bytes(2, 'big') +
                pixel_format +
                b'\x00\x00\x00\x0a' +  # name length 10
                b'GooseVNC  '  # this VNC Server has the mentality of a goose. 🦢
            )

            client.sendall(serverinit)

            # 7️⃣ FramebufferUpdateRequest handling loop
            while True:
                try:
                    # Read message type (1 byte)
                    msg_type = client.recv(1)
                    if not msg_type:
                        break

                    if msg_type == b'\x03':  # FramebufferUpdateRequest
                        # Read rest of the FramebufferUpdateRequest (9 bytes)
                        payload = client.recv(9)
                        if len(payload) < 9:
                            break

                        incremental = payload[0]
                        x, y, w, h = struct.unpack(">HHHH", payload[1:9])

                        print(f"[VNC] FramebufferUpdateRequest: x={x} y={y} w={w} h={h}")

                        # Clamp requested area to framebuffer
                        x = min(x, frame_width)
                        y = min(y, frame_height)
                        w = min(w, frame_width - x)
                        h = min(h, frame_height - y)

                        if w == 0 or h == 0:
                            continue  # skip zero-size requests

                        # Send FramebufferUpdate matching request
                        header = b'\x00\x00' + (1).to_bytes(2, 'big')

                        rectangle = (
                            x.to_bytes(2, 'big') +
                            y.to_bytes(2, 'big') +
                            w.to_bytes(2, 'big') +
                            h.to_bytes(2, 'big') +
                            (0).to_bytes(4, 'big', signed=True)  # Raw encoding
                        )

                        rectangle += os.urandom(w * h * 4)  # 32bpp random pixel data

                        client.sendall(b'\x00' + b'\x00' + header + rectangle)
                        print("[VNC] Sent FramebufferUpdate with random pixels")

                        # Optional delay → looks realistic
                        time.sleep(0.05)

                    else:
                        # Other message types → ignore for now
                        msg_type_int = ord(msg_type)
                        print(f"[VNC] Ignoring client message type {msg_type_int}")
                        # Read and discard message payload (variable length per type → for now, we skip)
                        # You could parse ClientCutText and SetEncodings here if wanted

                except Exception as e:
                    print(f"[VNCCrasherHoneypot] Exception while sending updates: {e}")
                    break

            client.close()

        except Exception as e:
            print(f"[VNCCrasherHoneypot] Exception: {e}")
            try:
                client.close()
            except:
                pass

if __name__ == '__main__':
    honeypot = VNCCrasherHoneypot()
    honeypot.run()
