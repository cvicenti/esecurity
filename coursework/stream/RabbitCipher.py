from __future__ import print_function

import time

from StreamCipher import StreamCipher

# This class is an adaptation from https://asecuritysite.com/encryption/rabbit2
def enc_long(n):
    '''Encodes arbitrarily large number n to a sequence of bytes.
    Big endian byte order is used.'''
    s = ""
    while n > 0:
        s = chr(n & 0xFF) + s
        n >>= 8
    return s


WORDSIZE = 0x100000000

rot08 = lambda x: ((x << 8) & 0xFFFFFFFF) | (x >> 24)
rot16 = lambda x: ((x << 16) & 0xFFFFFFFF) | (x >> 16)


def _nsf(u, v):
    '''Internal non-linear state transition'''
    s = (u + v) % WORDSIZE
    s = s * s
    return (s ^ (s >> 32)) % WORDSIZE


class RabbitCipher(StreamCipher):

    def __init__(self, input_file_name, key, iv):
        super(RabbitCipher, self).__init__(input_file_name, key, iv)
        '''Initialize Rabbit cipher using a 128 bit integer/string'''

        if isinstance(key, str):
            # interpret key string in big endian byte order
            if len(key) < 16:
                key = '\x00' * (16 - len(key)) + key
            # if len(key) > 16 bytes only the first 16 will be considered
            k = [ord(key[i + 1]) | (ord(key[i]) << 8)
                 for i in xrange(14, -1, -2)]
        else:
            # k[0] = least significant 16 bits
            # k[7] = most significant 16 bits
            k = [(key >> i) & 0xFFFF for i in xrange(0, 128, 16)]

        # State and counter initialization
        x = [(k[(j + 5) % 8] << 16) | k[(j + 4) % 8] if j & 1 else
             (k[(j + 1) % 8] << 16) | k[j] for j in xrange(8)]
        c = [(k[j] << 16) | k[(j + 1) % 8] if j & 1 else
             (k[(j + 4) % 8] << 16) | k[(j + 5) % 8] for j in xrange(8)]

        self.x = x
        self.c = c
        self.b = 0
        self._buf = 0  # output buffer
        self._buf_bytes = 0  # fill level of buffer

        self.next()
        self.next()
        self.next()
        self.next()

        for j in xrange(8):
            c[j] ^= x[(j + 4) % 8]

        self.start_x = self.x[:]  # backup initial key for IV/reset
        self.start_c = self.c[:]
        self.start_b = self.b

        if iv != None:
            self.set_iv(iv)

    def reset(self, iv=None):
        '''Reset the cipher and optionally set a new IV (int64 / string).'''

        self.c = self.start_c[:]
        self.x = self.start_x[:]
        self.b = self.start_b
        self._buf = 0
        self._buf_bytes = 0
        if iv != None:
            self.set_iv(iv)

    def set_iv(self, iv):
        '''Set a new IV (64 bit integer / bytestring).'''

        if isinstance(iv, str):
            i = 0
            for c in iv:
                i = (i << 8) | ord(c)
            iv = i

        c = self.c
        i0 = iv & 0xFFFFFFFF
        i2 = iv >> 32
        i1 = ((i0 >> 16) | (i2 & 0xFFFF0000)) % WORDSIZE
        i3 = ((i2 << 16) | (i0 & 0x0000FFFF)) % WORDSIZE

        c[0] ^= i0
        c[1] ^= i1
        c[2] ^= i2
        c[3] ^= i3
        c[4] ^= i0
        c[5] ^= i1
        c[6] ^= i2
        c[7] ^= i3

        self.next()
        self.next()
        self.next()
        self.next()

    def next(self):
        '''Proceed to the next internal state'''

        c = self.c
        x = self.x
        b = self.b

        t = c[0] + 0x4D34D34D + b
        c[0] = t % WORDSIZE
        t = c[1] + 0xD34D34D3 + t // WORDSIZE
        c[1] = t % WORDSIZE
        t = c[2] + 0x34D34D34 + t // WORDSIZE
        c[2] = t % WORDSIZE
        t = c[3] + 0x4D34D34D + t // WORDSIZE
        c[3] = t % WORDSIZE
        t = c[4] + 0xD34D34D3 + t // WORDSIZE
        c[4] = t % WORDSIZE
        t = c[5] + 0x34D34D34 + t // WORDSIZE
        c[5] = t % WORDSIZE
        t = c[6] + 0x4D34D34D + t // WORDSIZE
        c[6] = t % WORDSIZE
        t = c[7] + 0xD34D34D3 + t // WORDSIZE
        c[7] = t % WORDSIZE
        b = t // WORDSIZE

        g = [_nsf(x[j], c[j]) for j in xrange(8)]

        x[0] = (g[0] + rot16(g[7]) + rot16(g[6])) % WORDSIZE
        x[1] = (g[1] + rot08(g[0]) + g[7]) % WORDSIZE
        x[2] = (g[2] + rot16(g[1]) + rot16(g[0])) % WORDSIZE
        x[3] = (g[3] + rot08(g[2]) + g[1]) % WORDSIZE
        x[4] = (g[4] + rot16(g[3]) + rot16(g[2])) % WORDSIZE
        x[5] = (g[5] + rot08(g[4]) + g[3]) % WORDSIZE
        x[6] = (g[6] + rot16(g[5]) + rot16(g[4])) % WORDSIZE
        x[7] = (g[7] + rot08(g[6]) + g[5]) % WORDSIZE

        self.b = b
        return self

    def derive(self):
        '''Derive a 128 bit integer from the internal state'''

        x = self.x
        return ((x[0] & 0xFFFF) ^ (x[5] >> 16)) | \
               (((x[0] >> 16) ^ (x[3] & 0xFFFF)) << 16) | \
               (((x[2] & 0xFFFF) ^ (x[7] >> 16)) << 32) | \
               (((x[2] >> 16) ^ (x[5] & 0xFFFF)) << 48) | \
               (((x[4] & 0xFFFF) ^ (x[1] >> 16)) << 64) | \
               (((x[4] >> 16) ^ (x[7] & 0xFFFF)) << 80) | \
               (((x[6] & 0xFFFF) ^ (x[3] >> 16)) << 96) | \
               (((x[6] >> 16) ^ (x[1] & 0xFFFF)) << 112)

    def keystream(self, n):
        '''Generate a keystream of n bytes'''

        res = ""
        b = self._buf
        j = self._buf_bytes
        next = self.next
        derive = self.derive

        for i in xrange(n):
            if not j:
                j = 16
                next()
                b = derive()
            res += chr(b & 0xFF)
            j -= 1
            b >>= 1

        self._buf = b
        self._buf_bytes = j
        return res

    def encrypt(self, data):
        '''Encrypt/Decrypt data of arbitrary length.'''

        res = ""
        b = self._buf
        j = self._buf_bytes
        next = self.next
        derive = self.derive

        for c in data:
            if not j:  # empty buffer => fetch next 128 bits
                j = 16
                next()
                b = derive()
            res += chr(ord(c) ^ (b & 0xFF))
            j -= 1
            b >>= 1
        self._buf = b
        self._buf_bytes = j
        return res

    # decrypt = encrypt
    def decrypt(self, data):
        plaintext = self.encrypt(data)
        print(plaintext, file=self.output_file, end=" ")
        return plaintext

    def encrypt_decrypt(self, word):
        cipher = self.encrypt(word)
        return RabbitCipher(self.key, self.iv).decrypt(cipher)

    def process_file(self):
        input_file = open(self.input_file_name)
        start_setup_time = time.time()
        encrypt = RabbitCipher(self.input_file_name, self.key, self.iv)
        finish_setup_time = time.time()
        print("Setup completed in:", finish_setup_time - start_setup_time, "seconds")
        decrypt = RabbitCipher(self.input_file_name, self.key, self.iv)
        start_cipher_file_time = time.time()
        for word in input_file.read().split():
            self.gather_metrics()
            cipher = encrypt.encrypt(word)
            decrypt.decrypt(cipher)
            self.gather_metrics()
        finish_cipher_file_time = time.time()
        print("File processed in:", finish_cipher_file_time - start_cipher_file_time, "seconds")

        input_file.close()
        self.input_file_checksum = self.sha256sum(self.input_file_name)
        self.metrics_file.close()

    def encrypt_file(self):
        input_file = open(self.input_file_name)
        start_setup_time = time.time()
        encrypt = RabbitCipher(self.input_file_name, self.key, self.iv)
        finish_setup_time = time.time()
        print("Setup completed in:", finish_setup_time - start_setup_time, "seconds")
        start_cipher_file_time = time.time()
        for word in input_file.read().split():
            self.gather_metrics()
            encrypt.encrypt(word)
            self.gather_metrics()
        finish_cipher_file_time = time.time()
        print("File processed in:", finish_cipher_file_time - start_cipher_file_time, "seconds")

        input_file.close()
        self.input_file_checksum = self.sha256sum(self.input_file_name)
        self.metrics_file.close()
