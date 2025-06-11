# SNMP_Honeypot_v2.py

import socket
import threading
import struct
import random
import os
from datetime import datetime
from telegram import send_telegram_message

class SNMPHoneypot:
    def __init__(self, host='0.0.0.0', port=161):
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        print(f"[SNMPHoneypot] Listening on UDP port {self.port} (SNMP)...")

        while True:
            data, addr = sock.recvfrom(4096)
            threading.Thread(target=self.handle_packet, args=(sock, data, addr), daemon=True).start()

    def handle_packet(self, sock, data, addr):
        try:
            print(f"[SNMPHoneypot] Packet from {addr}")

            if len(data) < 20:
                return

            idx = 2
            if data[idx] != 0x02:
                return
            ver_len = data[idx+1]
            version = data[idx+2]
            idx += 2 + ver_len

            if data[idx] != 0x04:
                return
            comm_len = data[idx+1]
            community = data[idx+2:idx+2+comm_len].decode(errors='ignore')
            idx += 2 + comm_len

            pdu_type = data[idx]
            if pdu_type != 0xA0:
                print(f"[SNMPHoneypot] Not a GetRequest (type {pdu_type:#x}), ignoring")
                return
            pdu_len = data[idx+1]
            pdu_start = idx + 2
            pdu_end = pdu_start + pdu_len
            pdu_data = data[pdu_start:pdu_end]

            idx = 2 + 2 + 2

            try:
                oid_start = pdu_start + 20
                oid_str = self.parse_oid(data[oid_start:])
            except Exception:
                oid_str = "<unknown>"

            msg = f"*SNMP GetRequest!* 🐝\n"
            msg += f"`{datetime.utcnow().isoformat()}`\n"
            msg += f"*IP:* `{addr[0]}`\n"
            msg += f"*Community:* `{community}`\n"
            msg += f"*OID:* `{oid_str}`"

            send_telegram_message(msg)

            # Build response based on OID
            response = self.build_response(data, community, oid_str)
            sock.sendto(response, addr)

        except Exception as e:
            print(f"[SNMPHoneypot] Exception: {e}")

    def parse_oid(self, oid_data):
        if len(oid_data) < 4:
            return "<invalid OID>"
        if oid_data[0] != 0x30:
            return "<not a sequence>"
        oid_start = 4
        if oid_data[oid_start-2] != 0x06:
            return "<not an OID>"
        oid_len = oid_data[oid_start-1]
        oid_bytes = oid_data[oid_start:oid_start+oid_len]
        oid_numbers = []
        if len(oid_bytes) < 1:
            return "<empty OID>"
        first_byte = oid_bytes[0]
        oid_numbers.append(first_byte // 40)
        oid_numbers.append(first_byte % 40)
        val = 0
        for b in oid_bytes[1:]:
            if b & 0x80:
                val = (val << 7) | (b & 0x7F)
            else:
                val = (val << 7) | b
                oid_numbers.append(val)
                val = 0
        return '.'.join(map(str, oid_numbers))

    def build_response(self, request_data, community, oid_str):
        # Randomize based on OID
        if oid_str == "1.3.6.1.2.1.1.1.0":  # sysDescr
            descr_options = [
                "HP LaserJet 4050",
                "Cisco Catalyst 2960",
                "Ubiquiti EdgeRouter X",
                "Synology NAS",
                "Generic Printer",
                "Linux server Ubuntu 22.04",
                "TP-Link Archer C6"
            ]
            value_str = random.choice(descr_options)
            value_bytes = value_str.encode()
            value_field = (
                b'\x04' + bytes([len(value_bytes)]) + value_bytes
            )

        elif oid_str == "1.3.6.1.2.1.1.3.0":  # sysUpTime
            uptime = random.randint(10000, 10000000)
            value_field = (
                b'\x43\x04' + struct.pack(">I", uptime)
            )

        elif oid_str == "1.3.6.1.2.1.1.5.0":  # sysName
            name_str = f"device-{random.randint(1,99)}"
            name_bytes = name_str.encode()
            value_field = (
                b'\x04' + bytes([len(name_bytes)]) + name_bytes
            )

        else:
            # Default: fake integer
            fake_int = random.randint(1, 100)
            value_field = (
                b'\x02\x01' + bytes([fake_int])
            )

        # Build response
        response = (
            b'\x30' +  # SEQUENCE
            b'\x30' +  # length placeholder (approx, not strict ASN.1)
            b'\x02\x01\x00' +  # version v1
            b'\x04' + bytes([len(community)]) + community.encode() +
            b'\xA2' + b'\x23' +  # GetResponse PDU
            b'\x02\x04\x00\x00\x00\x01' +  # request-id
            b'\x02\x01\x00' +  # error-status
            b'\x02\x01\x00' +  # error-index
            b'\x30' + b'\x17' +  # varbinds sequence
            b'\x30' + b'\x15' +
            b'\x06\x08\x2b\x06\x01\x02\x01\x01\x03\x00' +  # OID: sysUpTime.0 (placeholder OID, can be faked)
            value_field
        )
        return response

if __name__ == '__main__':
    honeypot = SNMPHoneypot()
    honeypot.run()
