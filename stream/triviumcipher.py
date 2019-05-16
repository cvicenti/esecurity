from __future__ import print_function

import time
from collections import deque
from itertools import repeat

# Code adapted from https://github.com/mortasoft/Trivium

from StreamCipher import StreamCipher

_allbytes = dict([("%02X" % i, i) for i in range(256)])


def _hex_to_bytes(s):
    return [_allbytes[s[i:i + 2].upper()] for i in range(0, len(s), 2)]


def hex_to_bits(s):
    return [(b >> i) & 1 for b in _hex_to_bytes(s)
            for i in range(8)]


def bits_to_hex(b):
    return "".join(["%02X" % sum([b[i + j] << j for j in range(8)])
                    for i in range(0, len(b), 8)])


class TriviumCipher(StreamCipher):

    iv_hash = ""
    key_hash = ""

    def __init__(self, input_file_name, key, iv):
        self.key_hash, self.iv_hash = self.prepare_keys(key, iv)
        super(TriviumCipher, self).__init__(input_file_name, key, iv)
        """in the beginning we need to transform the key as well as the IV.
        Afterwards we initialize the state."""
        self.state = None
        self.counter = 0

        # Initialize state
        # len 100
        init_list = list(map(int, list(self.key_hash)))
        init_list += list(repeat(0, 20))
        # len 84
        init_list += list(map(int, list(self.iv_hash)))
        init_list += list(repeat(0, 4))
        # len 111
        init_list += list(repeat(0, 108))
        init_list += list([1, 1, 1])
        self.state = deque(init_list)

        # Do 4 full cycles, drop output
        for i in range(4 * 288):
            self._gen_keystream()

    def encrypt(self, message):
        plaintext_hex = message.encode('hex').upper()
        plaintext_bin = hex_to_bits(plaintext_hex)

        ciphertext = []
        for i in range(len(plaintext_bin)):
            ciphertext.append(self._gen_keystream() ^ plaintext_bin[i])

        return bits_to_hex(ciphertext)


    def decrypt(self, cipher):

        plaintext_bin = []
        ciphertext_bin = hex_to_bits(cipher)
        for i in range(len(ciphertext_bin)):
            plaintext_bin.append(self._gen_keystream() ^ ciphertext_bin[i])

        plaintext_hex = bits_to_hex(plaintext_bin)
        plaintext = plaintext_hex.decode('hex')
        print(plaintext, file=self.output_file, end=" ")
        return plaintext

    def prepare_keys(self, key, nonce):

        key_hex = key.encode('hex').upper()
        iv_hex = nonce.encode('hex').upper()
        KEY = hex_to_bits(key_hex)[::-1]
        IV = hex_to_bits(iv_hex)[::-1]
        if len(KEY) < 80:
            for k in range(80 - len(KEY)):
                KEY.append(0)
        if len(IV) < 80:
            for i in range(80 - len(IV)):
                IV.append(0)
        return KEY, IV


    def keystream(self):
        """output keystream
        only use this when you know what you are doing!!"""
        while self.counter < 2 ** 64:
            self.counter += 1
            yield self._gen_keystream()

    def _setLength(self, input_data):
        """we cut off after 80 bits, alternatively we pad these with zeros."""
        input_data = "{0:080b}".format(input_data)
        if len(input_data) > 80:
            input_data = input_data[:(len(input_data) - 81):-1]
        else:
            input_data = input_data[::-1]
        return input_data

    def _gen_keystream(self):
        """this method generates triviums keystream"""

        a_1 = self.state[90] & self.state[91]
        a_2 = self.state[181] & self.state[182]
        a_3 = self.state[292] & self.state[293]

        t_1 = self.state[65] ^ self.state[92]
        t_2 = self.state[168] ^ self.state[183]
        t_3 = self.state[249] ^ self.state[294]

        out = t_1 ^ t_2 ^ t_3

        s_1 = a_1 ^ self.state[177] ^ t_1
        s_2 = a_2 ^ self.state[270] ^ t_2
        s_3 = a_3 ^ self.state[68] ^ t_3

        self.state.rotate(1)

        self.state[0] = s_3
        self.state[100] = s_1
        self.state[184] = s_2

        return out

    def process_file(self):
        input_file = open(self.input_file_name)
        start_setup_time = time.time()
        encrypt = TriviumCipher(self.input_file_name, self.key, self.iv)
        finish_setup_time = time.time()
        print("Setup completed in:", finish_setup_time - start_setup_time, "seconds")
        decrypt = TriviumCipher(self.input_file_name, self.key, self.iv)
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
        encrypt = TriviumCipher(self.input_file_name, self.key, self.iv)
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
