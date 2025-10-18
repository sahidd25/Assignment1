# server.py
import socket
import threading

clients = {}

def handle_client(conn, username):
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break

            if b'|' in data:
                target, msg = data.split(b'|', 1)
                target = target.decode()

                print(f"[Server] Message for {target}: {msg[:30]}...")
                if target in clients:
                    clients[target].send(msg)
        except Exception as e:
            print(f"[Server] Error: {e}")
            break
    conn.close()

def main():
    server = socket.socket()
    server.bind(('localhost', 9999))
    server.listen()
    print("[Server] Listening on port 9999")

    while True:
        conn, addr = server.accept()
        username = conn.recv(1024).decode()
        clients[username] = conn
        print(f"[Server] {username} connected")
        threading.Thread(target=handle_client, args=(conn, username)).start()

if __name__ == "__main__":
    main()
