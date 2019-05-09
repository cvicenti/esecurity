from __future__ import print_function

import time

from Crypto.Cipher import Salsa20
from StreamCipher import StreamCipher


class Salsa20Cipher(StreamCipher):

    def __init__(self, input_file_name, key, iv):
        super(Salsa20Cipher, self).__init__(input_file_name, key, iv)

    def encrypt(self, plaintext):
        cipher = Salsa20.new(key=self.key)
        ciphertext = cipher.nonce + cipher.encrypt(plaintext)
        return ciphertext

    def decrypt(self, ciphertext):
        cipher = Salsa20.new(key=self.key, nonce=ciphertext[:8])
        plaintext = cipher.decrypt(ciphertext[8:])
        print(plaintext, file=self.output_file, end=" ")

    def encrypt_file(self):
        start_setup_time = time.time()
        cipher = Salsa20.new(key=self.key)
        finish_setup_time = time.time()
        print("Setup completed in:", finish_setup_time - start_setup_time, "seconds")
        input_file_name = self.input_file_name
        input_file = open(input_file_name)
        start_cipher_file_time = time.time()
        for word in input_file.read().split():
            self.gather_metrics()
            cipher.encrypt(word)
            self.gather_metrics()
        finish_cipher_file_time = time.time()
        print("File encrypted in:", finish_cipher_file_time - start_cipher_file_time, "seconds")
        input_file.close()
        self.metrics_file.close()
