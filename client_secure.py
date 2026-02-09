import socket
import threading
import time
import pyaes, pbkdf2, binascii, os, secrets
import rsa


def get_ip_address():
    # פונקציה למציאת IP או הגדרה ידנית
    return '127.0.0.1'


IP = get_ip_address()
SERVER_PORT = 610


class client:
    def __init__(self):
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.aes_key = None  # המפתח הסודי נשמר כאן
        self.hold = None
        self.data = None

        # לולאת התחברות עקשנית
        while True:
            try:
                print(f"Connecting to {IP}:{SERVER_PORT}...")
                self.my_socket.connect((IP, SERVER_PORT))
                print("Connected.")
                break
            except:
                time.sleep(2)

        # ביצוע לחיצת יד מיידית
        if not self.perform_handshake():
            print("Handshake failed, closing.")
            self.my_socket.close()
            return

        # התחלת האזנה
        x = threading.Thread(target=self.gett, args=(), daemon=True)
        x.start()

    def perform_handshake(self):
        try:
            print("Starting handshake...")
            # 1. קבלת המפתח הציבורי
            pem_key = self.my_socket.recv(1024)
            public_key = rsa.PublicKey.load_pkcs1(pem_key)

            # 2. יצירת מפתח AES
            password = str(secrets.randbits(128))
            salt = os.urandom(16)
            self.aes_key = pbkdf2.PBKDF2(password, salt).read(32)

            # 3. הצפנה ושליחה
            encrypted_key = rsa.encrypt(self.aes_key, public_key)
            self.my_socket.send(encrypted_key)
            print("Handshake success!")
            return True
        except Exception as e:
            print(f"Handshake error: {e}")
            return False

    def send(self, msg):
        try:
            if type(msg) == str: msg = msg.encode()

            # הצפנה עם המפתח השמור
            iv = secrets.randbits(256)
            aes = pyaes.AESModeOfOperationCTR(self.aes_key, pyaes.Counter(iv))
            encrypted_msg = aes.encrypt(msg)

            # פרוטוקול חדש: IV (128) + LEN (10) + DATA
            iv_str = str(iv).zfill(128)
            length_str = str(len(encrypted_msg)).zfill(10)

            self.my_socket.send(iv_str.encode())
            self.my_socket.send(length_str.encode())
            self.my_socket.send(encrypted_msg)
        except Exception as e:
            print(f"Send error: {e}")

    def rcv(self):
        try:
            # קריאת IV
            iv_data = self.my_socket.recv(128).decode()
            if not iv_data: return "exit"
            iv = int(iv_data)

            # קריאת אורך
            length_str = self.my_socket.recv(10).decode()
            length = int(length_str)

            # קריאת מידע
            data = b""
            while len(data) < length:
                packet = self.my_socket.recv(length - len(data))
                if not packet: break
                data += packet

            # פענוח עם המפתח השמור
            aes = pyaes.AESModeOfOperationCTR(self.aes_key, pyaes.Counter(iv))
            return aes.decrypt(data).decode("utf-8")
        except:
            return "error"

    def gett(self):
        while True:
            self.data = self.rcv()
            if self.data in ['exit', 'error']: break

            # לוגיקה לקליטת רשימות וכו'
            if self.data == 'closing':
                apps = []
                temp = self.rcv()
                while temp != 'done' and temp != 'error':
                    apps.append(temp)
                    temp = self.rcv()
                self.hold = apps
            elif self.data:
                self.hold = self.data

    def chatt(self, msg):
        self.send(msg)

    def get_hold(self):
        return self.hold

    def close(self):
        self.my_socket.close()


if __name__ == "__main__":
    client()