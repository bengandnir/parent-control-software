import socket
import threading
import logging
import concurrent.futures
import json
import subprocess
import pyaes, pbkdf2, binascii, os, secrets
import rsa
import time
import ctypes
import os
import lock
import history_printer
import lock as site_blocker


IP = '0.0.0.0'
SERVER_PORT = 610
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
server_socket.bind((IP, SERVER_PORT))

sockets = ['empty'] * 5  # ניהול פשוט


def chatting(number):
    # משתנה לשמירת המפתח של הלקוח הנוכחי
    client_aes_key = None

    # --- פונקציות עזר פנימיות ---
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
            iv_data = sock.recv(128).decode()
            if not iv_data: return "exit"  # זיהוי ניתוק
            iv = int(iv_data)

            length_data = sock.recv(10).decode()
            if not length_data: return "exit"
            length = int(length_data)

            data = b""
            while len(data) < length:
                packet = sock.recv(length - len(data))
                if not packet: break
                data += packet

            aes = pyaes.AESModeOfOperationCTR(client_aes_key, pyaes.Counter(iv))
            return aes.decrypt(data).decode("utf-8")
        except:
            return "exit"


    while True:
        print(f"\nServer is listening on port {SERVER_PORT}...")
        try:
            server_socket.listen()
            (client_socket, address) = server_socket.accept()
            sockets[number] = client_socket
            print(f"Client connected from {address}")

            # --- שלב Handshake ---
            try:
                (pub, priv) = rsa.newkeys(512)
                client_socket.send(pub.save_pkcs1())

                enc_key = client_socket.recv(64)
                if not enc_key: raise Exception("Client disconnected during handshake")

                client_aes_key = rsa.decrypt(enc_key, priv)
                print("Handshake Complete.")
            except Exception as e:
                print(f"Handshake failed: {e}")
                client_socket.close()
                continue  # חוזר לתחילת ה-While ומחכה ללקוח הבא

            # --- לולאת השיחה ---
            while True:
                data = rcv_secure(client_socket)

                print(f"Command received: {data}")

                if data == "exit":
                    print("Client sent exit.")
                    break  # יוצא מלולאת השיחה, אבל נשאר בלולאת השרת



                # --- ביצוע הפקודות ---
                if data == 'lock':
                    print("Executing Lock Command...")
                    try:

                        ctypes.windll.user32.LockWorkStation()
                        send_secure('locked', client_socket)
                        print("PC Locked successfully (Method 1).")

                    except Exception as e:
                        print(f"Method 1 failed: {e}")
                        try:

                            os.system("rundll32.exe user32.dll,LockWorkStation")
                            send_secure('locked', client_socket)
                            print("PC Locked successfully (Method 2).")
                        except Exception as e2:
                            print(f"All lock methods failed: {e2}")


                elif data == 'get_history':
                    print("Command: Get History")
                    history_json = history_printer.get_chrome_history()
                    send_secure(history_json, client_socket)
                    print("History sent.")

                elif data == 'close':

                    try:
                        cmd = 'powershell "Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object -Property Id, MainWindowTitle | Format-Table -HideTableHeaders"'
                        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                        out, err = proc.communicate()
                        send_secure('closing', client_socket)
                        time.sleep(0.5)
                        for line in out.decode(errors='ignore').splitlines():
                            if line.strip(): send_secure(line.strip(), client_socket)
                        time.sleep(0.5)
                        send_secure('done', client_socket)
                    except:
                        print("close falied")
                        send_secure('close failed', client_socket)

                elif data == 'kill':
                    pid = rcv_secure(client_socket)
                    if pid and pid != 'exit':
                        print(f"Killing {pid}")
                        try:
                            os.kill(int(pid), 9)
                        except:
                            pass
                elif data == 'block':
                    print("Command: Block Sites")
                    status = site_blocker.block_sites()
                    send_secure(status, client_socket)

                    # 6. שחרור (Release)
                elif data == 'release':
                    print("Command: Release Sites")
                    status = site_blocker.release_sites()
                    send_secure(status, client_socket)

                    # 7. הוספת אתר (Add)
                elif data == 'add':
                    print("Command: Add Site")
                    # השרת מחכה לקבל את שם האתר מהלקוח
                    site_name = rcv_secure(client_socket)
                    status = site_blocker.add_site_to_list(site_name)
                    send_secure(status, client_socket)


                # --- סוף ביצוע פקודות ---

        except Exception as e:
            print(f"Server error: {e}")

        # שלב הניתוק
        print("Closing connection with current client...")
        try:
            client_socket.close()
        except:
            pass

        print("Ready for next client.")


def main():

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(chatting, range(1))


if __name__ == "__main__":
    main()