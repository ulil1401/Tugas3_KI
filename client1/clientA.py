# Nama file: client_a.py
# Deskripsi: Klien A (Inisiator Pertukaran Kunci)

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
            print(f"\r[Client B]: {decrypted}\n[Anda (A)]: ", end="")
            
    except Exception as e:
        print(f"\n[Error Receive] {e}")

def start_chat_sender():
    """Thread untuk mengirim pesan chat DES."""
    global des_cipher, sock
    try:
        while True:
            msg_to_send = input("[Anda (A)]: ")
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
        print(f"[Klien A] Terhubung ke server {SERVER_IP}.")
    except Exception as e:
        print(f"Gagal terhubung ke server: {e}")
        return

    try:
        # --- FASE 1: HANDSHAKE RSA ---
        print("[Klien A] Memulai handshake...")
        
        # 1. Buat keypair RSA
        rsa_a = RSA(bits=256) # 256-bit n (cukup > 64 bit DES)
        e_a, n_a = rsa_a.public_key
        
        # 2. Kirim public key ke B (via server)
        key_str_a = f"PUBKEY:{e_a}:{n_a}"
        sock.sendall(key_str_a.encode('utf-8'))
        print(f"[Klien A] Mengirim public key...")

        # 3. Terima public key B (dari server)
        data_b = sock.recv(4096).decode('utf-8')
        if not data_b.startswith("PUBKEY:"):
            raise Exception("Protokol error: Mengharapkan PUBKEY dari B")
            
        parts = data_b.split(':')
        e_b, n_b = int(parts[1]), int(parts[2])
        print(f"[Klien A] Menerima public key B.")

        # --- FASE 2: KIRIM KUNCI DES ---
        
        # 4. Buat kunci DES (secret key) 64-bit
        des_key_bytes = os.urandom(8)
        des_key_int = int.from_bytes(des_key_bytes, 'big')
        print(f"[Klien A] Membuat kunci DES: {des_key_bytes.hex()}")

        # 5. Enkripsi kunci DES dengan public key B
        encrypted_des_key = rsa_a.encrypt(des_key_int, (e_b, n_b))
        
        # 6. Kirim kunci DES terenkripsi ke B
        key_str_des = f"DES_KEY:{encrypted_des_key}"
        sock.sendall(key_str_des.encode('utf-8'))
        print(f"[Klien A] Mengirim kunci DES terenkripsi ke B.")

        # 7. Inisialisasi DES_CBC dengan kunci rahasia
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