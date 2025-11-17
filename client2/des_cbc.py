# Nama file: des_cbc.py
# Deskripsi: Implementasi DES-CBC dari nol (Tugas 2)

import os

# --- konstan DES wajib !!! ---
# (Diterjemahkan dari C++ const int[])
# Catatan: Index -1 karena Python 0-based, C++ 1-based
IP = [57, 49, 41, 33, 25, 17, 9, 1, 59, 51, 43, 35, 27, 19, 11, 3, 61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7, 56, 48, 40, 32, 24, 16, 8, 0, 58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4, 62, 54, 46, 38, 30, 22, 14, 6]
FP = [39, 7, 47, 15, 55, 23, 63, 31, 38, 6, 46, 14, 54, 22, 62, 30, 37, 5, 45, 13, 53, 21, 61, 29, 36, 4, 44, 12, 52, 20, 60, 28, 35, 3, 43, 11, 51, 19, 59, 27, 34, 2, 42, 10, 50, 18, 58, 26, 33, 1, 41, 9, 49, 17, 57, 25, 32, 0, 40, 8, 48, 16, 56, 24, 64, 31]
PC1 = [56, 48, 40, 32, 24, 16, 8, 0, 57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18, 10, 2, 59, 51, 43, 35, 62, 54, 46, 38, 30, 22, 14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 60, 52, 44, 36, 28, 20, 12, 4, 27, 19, 11, 3]
PC2 = [13, 16, 10, 23, 0, 4, 2, 27, 14, 5, 20, 9, 22, 18, 11, 3, 25, 7, 15, 6, 26, 19, 12, 1, 40, 51, 30, 36, 46, 54, 29, 39, 50, 44, 32, 47, 43, 48, 38, 55, 33, 52, 45, 41, 49, 35, 28, 31]
SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
E = [31, 0, 1, 2, 3, 4, 3, 4, 5, 6, 7, 8, 7, 8, 9, 10, 11, 12, 11, 12, 13, 14, 15, 16, 15, 16, 17, 18, 19, 20, 19, 20, 21, 22, 23, 24, 23, 24, 25, 26, 27, 28, 27, 28, 29, 30, 31, 0]
P = [15, 6, 19, 20, 28, 11, 27, 16, 0, 14, 22, 25, 4, 17, 30, 9, 1, 7, 23, 13, 31, 26, 2, 8, 18, 12, 29, 5, 21, 10, 3, 24]
S_BOX = [
    [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7], [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8], [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0], [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
    [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10], [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5], [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15], [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],
    [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8], [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1], [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7], [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],
    [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15], [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9], [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4], [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],
    [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9], [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6], [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14], [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],D
    [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11], [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8], [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6], [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],
    [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1], [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6], [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2], [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]],
    [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7], [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2], [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8], [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]
]


class DES_CBC:
    def __init__(self, key_int):
        self.key_int = key_int & 0xFFFFFFFFFFFFFFFF
        self.subkeys = self._generate_subkeys()

    def _permute(self, val, table, in_sz, out_sz):
        out = 0
        for i in range(out_sz):
            bit_pos = table[i]
            if (val >> (in_sz - 1 - bit_pos)) & 1:
                out |= (1 << (out_sz - 1 - i))
        return out

    def _generate_subkeys(self):
        subkeys = []
        pk = self._permute(self.key_int, PC1, 64, 56)
        c = (pk >> 28) & 0x0FFFFFFF
        d = pk & 0x0FFFFFFF
        for i in range(16):
            c = ((c << SHIFTS[i]) | (c >> (28 - SHIFTS[i]))) & 0x0FFFFFFF
            d = ((d << SHIFTS[i]) | (d >> (28 - SHIFTS[i]))) & 0x0FFFFFFF
            cd = (c << 28) | d
            subkeys.append(self._permute(cd, PC2, 56, 48))
        return subkeys

    def _des_core(self, block, is_encrypt):
        block = self._permute(block, IP, 64, 64)
        l = (block >> 32) & 0xFFFFFFFF
        r = block & 0xFFFFFFFF
        for i in range(16):
            temp_r = r
            key_idx = i if is_encrypt else 15 - i
            exp_r = self._permute(r, E, 32, 48)
            xored = exp_r ^ self.subkeys[key_idx]
            s_out = 0
            for j in range(8):
                sb_in = (xored >> (42 - j * 6)) & 0x3F
                row = ((sb_in & 0x20) >> 4) | (sb_in & 0x01)
                col = (sb_in >> 1) & 0x0F
                s_out |= S_BOX[j][row][col] << (28 - j * 4)
            p_out = self._permute(s_out, P, 32, 32)
            r = l ^ p_out
            l = temp_r
        return self._permute((r << 32) | l, FP, 64, 64)

    def _add_padding(self, data_bytes):
        pad_size = 8 - (len(data_bytes) % 8)
        pad_byte = bytes([pad_size])
        return data_bytes + (pad_byte * pad_size)

    def _remove_padding(self, data_bytes):
        if not data_bytes: raise ValueError("Data kosong")
        pad_size = data_bytes[-1]
        if pad_size > 8 or pad_size == 0: raise ValueError("Padding invalid (nilai salah)")
        if data_bytes[-pad_size:] != bytes([pad_size]) * pad_size: raise ValueError("Padding invalid (isi salah)")
        return data_bytes[:-pad_size]

    def encrypt(self, plaintext_bytes):
        padded = self._add_padding(plaintext_bytes)
        iv = os.urandom(8)
        ciphertext = bytearray(iv)
        prev_block = int.from_bytes(iv, 'big')
        for i in range(0, len(padded), 8):
            p_block_bytes = padded[i:i+8]
            p_block = int.from_bytes(p_block_bytes, 'big')
            xored_block = p_block ^ prev_block
            c_block = self._des_core(xored_block, is_encrypt=True)
            ciphertext.extend(c_block.to_bytes(8, 'big'))
            prev_block = c_block
        return bytes(ciphertext)

    def decrypt(self, ciphertext_bytes):
        if len(ciphertext_bytes) < 16 or len(ciphertext_bytes) % 8 != 0: raise ValueError("Ukuran ciphertext tidak valid")
        iv = ciphertext_bytes[:8]
        plaintext = bytearray()
        prev_block = int.from_bytes(iv, 'big')
        for i in range(8, len(ciphertext_bytes), 8):
            c_block_bytes = ciphertext_bytes[i:i+8]
            c_block = int.from_bytes(c_block_bytes, 'big')
            decrypted_block = self._des_core(c_block, is_encrypt=False)
            p_block = decrypted_block ^ prev_block
            plaintext.extend(p_block.to_bytes(8, 'big'))
            prev_block = c_block
        return self._remove_padding(bytes(plaintext))