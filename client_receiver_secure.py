# client_receiver_secure.py
import socket
import json
from base64 import b64decode
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA

# Load Bob's private RSA key
with open("bob_private.pem", "rb") as f:
    private_key = RSA.import_key(f.read())

cipher_rsa = PKCS1_OAEP.new(private_key)
session_key = None
got_key = False

# Connect to server
s = socket.socket()
s.connect(('localhost', 9999))
s.send(b'Bob')
print("[Bob] Connected. Waiting for messages...")

# Message receiving loop
while True:
    data = s.recv(4096)
    if not data:
        continue

    if not got_key:
        try:
            session_key = cipher_rsa.decrypt(data)
            got_key = True
            print("[Bob] AES session key received and decrypted.")
        except Exception as e:
            print("[Bob] Error decrypting session key:", e)
        continue

    try:
        msg_json = json.loads(data.decode())
        nonce = b64decode(msg_json['nonce'])
        ciphertext = b64decode(msg_json['ciphertext'])
        tag = b64decode(msg_json['tag'])

        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        plaintext = cipher_aes.decrypt_and_verify(ciphertext, tag)

        print(f"\n[Bob] Encrypted: {msg_json['ciphertext']}")
        print(f"[Bob] Decrypted: {plaintext.decode()}")
    except Exception as e:
        print("[Bob] Error decrypting message:", e)
