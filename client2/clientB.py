# Nama file: client_b.py
# Deskripsi: Klien B (Penerima Pertukaran Kunci)

import socket
import threading
from des_cbc import DES_CBC
from rsa_from_scratch import RSA

# Ganti dengan IP Server (Laptop) Anda
SERVER_IP = '192.168.1.10' # <-- GANTI INI
SERVER_PORT = 12345

# Global DES object (di-set setelah handshake)
des_cipher = None
sock = None

def start_chat_receiver():
    """Thread untuk menerima pesan chat DES."""
    global des_cipher, sock
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                print("\n[Chat] Koneksi terputus.")
                break
            
            decrypted = des_cipher.decrypt(data).decode('utf-8')
            print(f"\r[Client A]: {decrypted}\n[Anda (B)]: ", end="")
            
    except Exception as e:
        print(f"\n[Error Receive] {e}")

def start_chat_sender():
    """Thread untuk mengirim pesan chat DES."""
    global des_cipher, sock
    try:
        while True:
            msg_to_send = input("[Anda (B)]: ")
            encrypted = des_cipher.encrypt(msg_to_send.encode('utf-8'))
            sock.sendall(encrypted)
    except (EOFError, KeyboardInterrupt):
        print("\nMemutuskan koneksi...")
    except Exception as e:
        print(f"\n[Error Send] {e}")

def main():
    global des_cipher, sock
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER_IP, SERVER_PORT))
        print(f"[Klien B] Terhubung ke server {SERVER_IP}.")
    except Exception as e:
        print(f"Gagal terhubung ke server: {e}")
        return

    try:
        # --- FASE 1: HANDSHAKE RSA ---
        print("[Klien B] Memulai handshake...")
        
        # 1. Buat keypair RSA
        rsa_b = RSA(bits=256)
        e_b, n_b = rsa_b.public_key
        
        # 2. Terima public key A (dari server)
        data_a = sock.recv(4096).decode('utf-8')
        if not data_a.startswith("PUBKEY:"):
            raise Exception("Protokol error: Mengharapkan PUBKEY dari A")
            
        parts = data_a.split(':')
        e_a, n_a = int(parts[1]), int(parts[2])
        print(f"[Klien B] Menerima public key A.")

        # 3. Kirim public key ke A (via server)
        key_str_b = f"PUBKEY:{e_b}:{n_b}"
        sock.sendall(key_str_b.encode('utf-8'))
        print(f"[Klien B] Mengirim public key...")

        # --- FASE 2: TERIMA KUNCI DES ---
        
        # 4. Terima kunci DES terenkripsi
        data_des = sock.recv(4096).decode('utf-8')
        if not data_des.startswith("DES_KEY:"):
            raise Exception("Protokol error: Mengharapkan DES_KEY")
            
        encrypted_des_key = int(data_des.split(':')[1])
        print(f"[Klien B] Menerima kunci DES terenkripsi.")

        # 5. DEKRIPSI kunci DES dengan private key B
        des_key_int = rsa_b.decrypt(encrypted_des_key)
        des_key_bytes = des_key_int.to_bytes(8, 'big') # Konversi ke 8 byte
        print(f"[Klien B] Kunci DES berhasil didekripsi: {des_key_bytes.hex()}")

        # 6. Inisialisasi DES_CBC dengan kunci rahasia
        des_cipher = DES_CBC(des_key_int)
        
        # --- FASE 3: CHATTING ---
        print("\n" + "="*30)
        print("HANDSHAKE SELESAI. CHAT AMAN (DES) DIMULAI.")
        print("Ketik pesan Anda dan tekan Enter.")
        print("="*30)

        # Mulai thread penerima
        receiver = threading.Thread(target=start_chat_receiver, daemon=True)
        receiver.start()
        
        # Gunakan thread utama untuk pengirim
        start_chat_sender()

    except Exception as e:
        print(f"\n[ERROR] Terjadi kesalahan: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()