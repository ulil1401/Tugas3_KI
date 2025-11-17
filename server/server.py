# Nama file: server.py
# Deskripsi: Server "Jembatan" (DENGAN PERBAIKAN RACE CONDITION)

import socket
import threading
import time # <-- TAMBAHAN WAJIB

# Menyimpan koneksi klien
clients = {} # "A": conn_A, "B": conn_B
client_lock = threading.Lock()

def handle_client(conn, client_name):
    """Menangani satu klien (A atau B) dan me-relay pesannya."""
    print(f"[SERVER] Klien '{client_name}' terhubung.")
    
    # Tentukan target relay
    target_name = "B" if client_name == "A" else "A"
    
    try:
        while True:
            # Terima data (buffer besar untuk key)
            data = conn.recv(4096)
            if not data:
                print(f"[SERVER] Klien '{client_name}' terputus.")
                break
            
            print(f"[RELAY] Menerima {len(data)} bytes dari '{client_name}', meneruskan ke '{target_name}'...")
            
            # --- PERBAIKAN RACE CONDITION DIMULAI ---
            #
            # Jika Klien A mengirim pesan, kita harus TUNGGU
            # sampai Klien B benar-benar ada di dictionary 'clients'.
            #
            target_conn = None
            while not target_conn:
                with client_lock:
                    target_conn = clients.get(target_name)
                
                if target_conn:
                    # Target sudah ditemukan, lanjutkan
                    break
                
                # Jika target belum ada, tunggu sebentar lalu cek lagi
                print(f"[RELAY] Menunggu Klien '{target_name}' terhubung sebelum me-relay...")
                time.sleep(0.5) # Cek setiap 0.5 detik
            #
            # --- PERBAIKAN RACE CONDITION SELESAI ---
                
            # Sekarang kita YAKIN target_conn ada
            target_conn.sendall(data)
            
    except Exception as e:
        print(f"[ERROR] Error pada handler '{client_name}': {e}")
    
    finally:
        with client_lock:
            clients.pop(client_name, None)
        conn.close()

def start_server():
    HOST = '0.0.0.0'
    PORT = 12345
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[SERVER] Server berjalan di {HOST}:{PORT}")
    print("[SERVER] Menunggu 2 klien (A dan B)...")

    # Terima Klien A
    try:
        conn_a, addr_a = server_socket.accept()
        with client_lock:
            clients["A"] = conn_a
        
        thread_a = threading.Thread(target=handle_client, args=(conn_a, "A"))
        thread_a.start()

        # Terima Klien B
        conn_b, addr_b = server_socket.accept()
        with client_lock:
            clients["B"] = conn_b
            
        thread_b = threading.Thread(target=handle_client, args=(conn_b, "B"))
        thread_b.start()
        
        print("[SERVER] Klien A dan B terhubung. Mode relay aktif.")
        
        # Jaga agar server tetap hidup
        thread_a.join()
        thread_b.join()

    except KeyboardInterrupt:
        print("\n[SERVER] Mematikan server...")
    finally:
        server_socket.close()
        print("[SERVER] Server ditutup.")

if __name__ == "__main__":
    start_server()