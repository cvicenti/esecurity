from __future__ import print_function
import errno
import hashlib
import os
import ntpath
import time

import psutil


class StreamCipher(object):

    output_file_name = ""
    input_file_name = ""
    output_file = ""
    metrics_file = ""
    secret = ""
    iv = ""
    key = ""
    input_file_checksum = ""
    encrypt_cipher = ""
    decrypt_cipher = ""

    def __init__(self, input_file_name, key, iv):
        global secret
        classname = self.__class__.__name__
        output_dir = '../output/' + os.path.splitext(self.path_leaf(input_file_name))[0] + '/'
        self.mkdir_p(output_dir)
        metrics_output_file_name = output_dir + classname + '.dat'
        print("metrics written at : ", metrics_output_file_name)

        self.secret = hashlib.sha256()
        # self.secret.update(key)
        self.output_file_name = output_dir + classname + ".out"
        self.output_file = open(self.output_file_name, 'w')
        self.input_file_name = input_file_name
        self.metrics_file = open(metrics_output_file_name, 'w')
        self.iv = iv
        self.key = key

    def path_leaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def finalize_and_check(self):
        self.output_file.close()
        # Check results
        checksum_output = self.sha256sum(self.output_file_name)
        if self.input_file_checksum == checksum_output:
            print("Both input-examples and output files match")
            print("Deleting copy from: ", self.output_file_name)
            os.remove(self.output_file_name)
        else:
            print("Input and output files do not match. There must have been a problem during encryption")
        self.output_file.close()

    def sha256sum(self, file_name):
        h = hashlib.sha256()
        b = bytearray(128 * 1024)
        mv = memoryview(b)
        with open(file_name, 'rb', buffering=0) as f:
            for n in iter(lambda: f.readinto(mv), 0):
                h.update(mv[:n])
        f.close()
        return h.hexdigest()

    def process_file(self):
        input_file_name = self.input_file_name
        input_file = open(input_file_name)
        start_cipher_file_time = time.time()

        for word in input_file.read().split():
            self.gather_metrics()
            self.encrypt_decrypt(word)
            self.gather_metrics()

        finish_cipher_file_time = time.time()
        print("File processed in:", finish_cipher_file_time - start_cipher_file_time, "seconds")

        input_file.close()
        self.input_file_checksum = self.sha256sum(input_file_name)
        self.metrics_file.close()

    def encrypt_decrypt(self, word):
        cipher = self.encrypt(word)
        self.decrypt(cipher)

    def encrypt(self, word):
        pass

    def decrypt(self, cipher):
        pass

    def gather_metrics(self):
        print(psutil.virtual_memory(), file=self.metrics_file)
        print(psutil.swap_memory(), file=self.metrics_file)
        print(psutil.cpu_times(), file=self.metrics_file)
