from __future__ import print_function

import time

from Crypto.Cipher import ARC4
from StreamCipher import StreamCipher


class RC4Cipher(StreamCipher):

    def __init__(self, input_file_name, key, iv):
        super(RC4Cipher, self).__init__(input_file_name, key, iv)

    def encrypt(self, plaintext):
        cipher = ARC4.new(key=self.key)
        ciphertext = cipher.encrypt(plaintext)
        return ciphertext

    def decrypt(self, ciphertext):
        cipher = ARC4.new(key=self.key)
        plaintext = cipher.decrypt(ciphertext)
        print(plaintext, file=self.output_file, end=" ")

    def encrypt_file(self):
        start_setup_time = time.time()
        cipher = ARC4.new(key=self.key)
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
