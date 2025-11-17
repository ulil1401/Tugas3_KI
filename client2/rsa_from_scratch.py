# Nama file: rsa_from_scratch.py
# Deskripsi: Implementasi RSA dari nol untuk pertukaran kunci.

import random

class RSA:
    def __init__(self, bits=256):
        # Kita butuh n > 64 bit (kunci DES), jadi 256 bit n sudah aman.
        # Key generation bisa lambat, tergantung keberuntungan.
        print(f"[RSA] Membuat keypair {bits}-bit... (mungkin butuh waktu)")
        self.public_key, self.private_key = self._generate_keypair(bits)
        print("[RSA] Keypair selesai dibuat.")

    def _is_prime_miller_rabin(self, n, k=40):
        """Tes primality Miller-Rabin. k adalah jumlah putaran."""
        if n == 2 or n == 3: return True
        if n <= 1 or n % 2 == 0: return False

        # Tulis n-1 sebagai (2^r) * d
        d = n - 1
        r = 0
        while d % 2 == 0:
            d //= 2
            r += 1

        # Lakukan tes k kali
        for _ in range(k):
            a = random.randrange(2, n - 1)
            x = pow(a, d, n) # x = (a^d) % n

            if x == 1 or x == n - 1:
                continue # Lanjut ke iterasi berikutnya

            # Ulangi r-1 kali
            for _ in range(r - 1):
                x = pow(x, 2, n) # x = (x^2) % n
                if x == n - 1:
                    break # Lanjut ke tes 'a' berikutnya
            else:
                # Jika tidak break (x != n-1), n adalah komposit
                return False
        
        return True # Kemungkinan besar prima

    def _find_prime(self, bits):
        """Mencari bilangan prima dengan n-bit."""
        while True:
            num = random.getrandbits(bits)
            # Pastikan ganjil dan n-bit
            num |= (1 << (bits - 1)) | 1
            
            if self._is_prime_miller_rabin(num):
                return num

    def _generate_keypair(self, bits):
        p = self._find_prime(bits // 2)
        q = self._find_prime(bits // 2)
        
        while p == q:
            q = self._find_prime(bits // 2)

        n = p * q
        phi_n = (p - 1) * (q - 1)
        
        e = 65537 # Standar public exponent
        
        # d = (e^-1) mod phi_n
        d = pow(e, -1, phi_n)
        
        # Public: (e, n), Private: (d, n)
        return ((e, n), (d, n))

    def encrypt(self, message_int, public_key):
        """Enkripsi integer menggunakan public key (e, n)."""
        e, n = public_key
        if message_int >= n:
            raise ValueError("Pesan terlalu besar untuk n")
        return pow(message_int, e, n)

    def decrypt(self, ciphertext_int):
        """Dekripsi integer menggunakan private key (d, n)."""
        d, n = self.private_key
        return pow(ciphertext_int, d, n)