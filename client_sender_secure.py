# client_sender_secure.py
import socket
import json
from base64 import b64encode
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

# Load Bob's public RSA key
with open("bob_public.pem", "rb") as f:
    bob_public_key = RSA.import_key(f.read())

cipher_rsa = PKCS1_OAEP.new(bob_public_key)

# Generate AES session key
session_key = get_random_bytes(16)
encrypted_session_key = cipher_rsa.encrypt(session_key)
sent_key = False

# Connect to server
s = socket.socket()
s.connect(('localhost', 9999))
s.send(b'Alice')
print("[Alice] Connected to server.")

# First, send encrypted AES key
s.send(b'Bob|' + encrypted_session_key)
print("[Alice] Encrypted AES session key sent to Bob.")

# Function to encrypt message using AES
def encrypt_message(msg):
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(msg.encode())

    payload = {
        'nonce': b64encode(cipher_aes.nonce).decode(),
        'ciphertext': b64encode(ciphertext).decode(),
        'tag': b64encode(tag).decode()
    }

    return json.dumps(payload).encode()

# Chat loop
while True:
    msg = input("You: ")
    encrypted = encrypt_message(msg)
    s.send(b'Bob|' + encrypted)
