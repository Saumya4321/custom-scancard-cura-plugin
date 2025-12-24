"""
Sends the packets to everyone on ethernet broadcast IP
"""
import socket # use this instead of netifaces - netifaces doesn't work inside Cura
import time 
import platform
import subprocess
import re

class UDPSender:
    def __init__(self, parent = None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.parent = parent
        self.Logger = self.parent.Logger 

    def get_ethernet_broadcast(self):
        system = platform.system().lower()

        if "windows" in system:
            # Run ipconfig and look for "Subnet Mask" and "IPv4 Address"
            output = subprocess.check_output("ipconfig", text=True)
            ip_match = re.search(r"IPv4 Address.*?: ([\d\.]+)", output)
            mask_match = re.search(r"Subnet Mask.*?: ([\d\.]+)", output)
            if ip_match and mask_match:
                ip = ip_match.group(1)
                mask = mask_match.group(1)
            else:
                return None
        else:
            # On Linux/macOS use `ip addr`
            output = subprocess.check_output(["ip", "addr"], text=True)
            match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/(\d+)", output)
            if not match:
                return None
            ip = match.group(1)
            prefix = int(match.group(2))
            mask = socket.inet_ntoa((0xffffffff << (32 - prefix)) .to_bytes(4, 'big'))

        # Compute broadcast address manually
        ip_bytes = [int(o) for o in ip.split('.')]
        mask_bytes = [int(o) for o in mask.split('.')]
        broadcast = [ip_bytes[i] | (~mask_bytes[i] & 255) for i in range(4)]
        return '.'.join(map(str, broadcast))


    def send_loop(self, payloads):
        broadcast_ip = self.get_ethernet_broadcast()
        UDP_PORT = 5005
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        for i, packet in enumerate(payloads):
                try:
                    sock.sendto(packet, (broadcast_ip, UDP_PORT))
                    print(f"[{i}] Sent: {packet.hex()}")
                    self.Logger.log("d", f"[LaserToolpathPlugin] Sent packet [{i}]: {packet.hex()} to {broadcast_ip}:{UDP_PORT}")
                    time.sleep(0.02)
                except Exception as e:
                    print(f"socket issue {e}")

    def close(self):
        self.sock.close()

if __name__ == "__main__":
    udp_sender = UDPSender()
    print("Broadcast IP:", udp_sender.get_ethernet_broadcast())