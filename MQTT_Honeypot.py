# MQTT_Honeypot.py

import socket
import threading
import struct
import random
import time
from datetime import datetime
from telegram import send_telegram_message

class MQTTHoneypot:
    def __init__(self, host='0.0.0.0', port=1883):
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(100)
        print(f"[MQTTHoneypot] Listening on port {self.port} (MQTT)...")

        while True:
            client, addr = sock.accept()
            threading.Thread(target=self.handle_client, args=(client, addr), daemon=True).start()

    def handle_client(self, client, addr):
        try:
            print(f"[MQTTHoneypot] Connection from {addr}")

            client.settimeout(10.0)

            while True:
                header = client.recv(2)
                if not header or len(header) < 2:
                    break

                msg_type = header[0] >> 4
                remaining_len = header[1]
                payload = client.recv(remaining_len)

                if msg_type == 1:  # CONNECT
                    client_id = self.parse_connect(payload)
                    msg = f"*MQTT CONNECT!* 🐝\n"
                    msg += f"`{datetime.utcnow().isoformat()}`\n"
                    msg += f"*IP:* `{addr[0]}`\n"
                    msg += f"*Client ID:* `{client_id}`"
                    send_telegram_message(msg)

                    # Send CONNACK with random session_present and return code
                    session_present = random.choice([0, 1])
                    return_code = random.choice([0x00, 0x01, 0x02])  # accept, unacceptable protocol, identifier rejected

                    connack = struct.pack("!BBBB", 0x20, 0x02, session_present, return_code)
                    client.sendall(connack)

                elif msg_type == 8:  # SUBSCRIBE
                    packet_id = payload[0:2]
                    topics = self.parse_subscribe(payload[2:])
                    msg = f"*MQTT SUBSCRIBE!* 🐝\n"
                    msg += f"`{datetime.utcnow().isoformat()}`\n"
                    msg += f"*IP:* `{addr[0]}`\n"
                    msg += f"*Topics:* `{topics}`"
                    send_telegram_message(msg)

                    # Send SUBACK with random granted QoS (0/1/2)
                    granted_qos = [random.choice([0, 1, 2]) for _ in topics]
                    suback_payload = b''.join(bytes([qos]) for qos in granted_qos)

                    suback = b'\x90' + bytes([len(packet_id) + len(suback_payload)]) + packet_id + suback_payload
                    client.sendall(suback)

                elif msg_type == 3:  # PUBLISH
                    topic, message = self.parse_publish(payload)
                    msg = f"*MQTT PUBLISH!* 🐝\n"
                    msg += f"`{datetime.utcnow().isoformat()}`\n"
                    msg += f"*IP:* `{addr[0]}`\n"
                    msg += f"*Topic:* `{topic}`\n"
                    msg += f"*Payload:* ```{message}```"
                    send_telegram_message(msg)

                    # Send PUBACK with random packet ID (not required but looks real)
                    if len(payload) >= 2 + len(topic):
                        packet_id = payload[2 + len(topic):2 + len(topic) + 2]
                        puback = b'\x40\x02' + packet_id
                        client.sendall(puback)

                elif msg_type == 12:  # PINGREQ
                    pingresp = b'\xD0\x00'
                    client.sendall(pingresp)

                else:
                    print(f"[MQTTHoneypot] Unknown or unhandled message type {msg_type}")
                    # You can choose to close or ignore → we ignore

                # Random small delay → looks more real
                time.sleep(random.uniform(0.05, 0.2))

            client.close()

        except Exception as e:
            print(f"[MQTTHoneypot] Exception: {e}")
            try:
                client.close()
            except:
                pass

    def parse_connect(self, payload):
        try:
            # Skip Protocol Name, Version, Connect Flags, Keep Alive
            proto_name_len = struct.unpack("!H", payload[0:2])[0]
            idx = 2 + proto_name_len + 4
            client_id_len = struct.unpack("!H", payload[idx:idx+2])[0]
            client_id = payload[idx+2:idx+2+client_id_len].decode(errors='ignore')
            return client_id
        except Exception:
            return "<unknown>"

    def parse_subscribe(self, payload):
        try:
            topics = []
            idx = 0
            while idx < len(payload):
                topic_len = struct.unpack("!H", payload[idx:idx+2])[0]
                idx += 2
                topic = payload[idx:idx+topic_len].decode(errors='ignore')
                idx += topic_len
                qos = payload[idx]
                idx += 1
                topics.append(topic)
            return topics
        except Exception:
            return []

    def parse_publish(self, payload):
        try:
            topic_len = struct.unpack("!H", payload[0:2])[0]
            topic = payload[2:2+topic_len].decode(errors='ignore')
            message = payload[2+topic_len:].decode(errors='ignore')
            return topic, message
        except Exception:
            return "<unknown>", "<unknown>"

if __name__ == '__main__':
    honeypot = MQTTHoneypot()
    honeypot.run()
