import socket
import threading
import logging
import concurrent.futures
import json
import subprocess
import pyaes, pbkdf2, binascii, os, secrets
import rsa
import time

# ודא שיש לך את הייבואים הנחוצים ללוגיקת ההיסטוריה וכו'

IP = '0.0.0.0'  # מאזין לכולם
SERVER_PORT = 610
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
server_socket.bind((IP, SERVER_PORT))

sockets = ['empty'] * 5  # ניהול פשוט


def chatting(number):
    # משתנה לשמירת המפתח של הלקוח הנוכחי
    client_aes_key = None

    # --- פונקציות עזר פנימיות (מכירות את client_aes_key) ---
    def send_secure(msg, sock):
        try:
            if type(msg) == str: msg = msg.encode()
            iv = secrets.randbits(256)
            aes = pyaes.AESModeOfOperationCTR(client_aes_key, pyaes.Counter(iv))
            encrypted = aes.encrypt(msg)

            sock.send(str(iv).zfill(128).encode())
            sock.send(str(len(encrypted)).zfill(10).encode())
            sock.send(encrypted)
        except Exception as e:
            print(f"Send Error: {e}")

    def rcv_secure(sock):
        try:
            iv = int(sock.recv(128).decode())
            length = int(sock.recv(10).decode())
            data = b""
            while len(data) < length:
                packet = sock.recv(length - len(data))
                if not packet: break
                data += packet

            aes = pyaes.AESModeOfOperationCTR(client_aes_key, pyaes.Counter(iv))
            return aes.decrypt(data).decode("utf-8")
        except:
            return "exit"

    # --- התחלת הטיפול בלקוח ---
    server_socket.listen()
    print(f"Waiting for client {number}...")
    (client_socket, address) = server_socket.accept()
    sockets[number] = client_socket
    print(f"Client connected from {address}")

    # --- שלב Handshake ---
    try:
        (pub, priv) = rsa.newkeys(512)  # מפתח RSA זמני
        client_socket.send(pub.save_pkcs1())  # שליחת הציבורי

        enc_key = client_socket.recv(64)  # קבלת המפתח המוצפן
        client_aes_key = rsa.decrypt(enc_key, priv)  # פענוח ושמירה
        print("Handshake Complete. Secure channel established.")
    except Exception as e:
        print(f"Handshake failed: {e}")
        client_socket.close()
        return

    # --- לולאת הפקודות ---
    while True:
        data = rcv_secure(client_socket)

        if data == "exit":
            break

        print(f"Client sent: {data}")

        if data == 'lock':
            # לוגיקה של נעילה...
            send_secure('locked', client_socket)

        elif data == 'get_history':
            # הלוגיקה החדשה שלך (עם SQLite וכו')
            # ... (הכנס את הקוד שכתבנו קודם כאן) ...
            # דוגמה:
            send_secure(json.dumps({'google.com': 5}), client_socket)

        elif data == 'close':
            # שליחת רשימת אפליקציות
            # חובה להשתמש בפקודות Secure החדשות!
            cmd = 'powershell "Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object -Property Id, MainWindowTitle | Format-Table -HideTableHeaders"'
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            out, err = proc.communicate()

            send_secure('closing', client_socket)  # התחלה
            time.sleep(0.5)
            for line in out.decode(errors='ignore').splitlines():
                if line.strip():
                    send_secure(line.strip(), client_socket)
            time.sleep(0.5)
            send_secure('done', client_socket)  # סיום

        elif data == 'kill':
            pid = rcv_secure(client_socket)  # קבלת PID בטוחה
            print(f"Killing {pid}")
            try:
                os.kill(int(pid), 9)
            except:
                pass
        elif data == 'block':



    client_socket.close()
    print("Client disconnected.")


def main():
    # הפעלת השרת
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(chatting, range(1))


if __name__ == "__main__":
    main()