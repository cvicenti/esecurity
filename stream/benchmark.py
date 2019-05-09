from __future__ import print_function

import errno
import os
import sys

import Chacha20Cipher
import RC4Cipher
import RabbitCipher
import Salsa20Cipher
import triviumcipher


##################### salsa20 ##########################

# print "salsa20 test:"
# salsa20.init(key)
# cipher = salsa20.encrypt(plaintext)
# salsa20.decrypt(cipher)


##################### chacha20 ##########################


# print "\nchacha20 test:"
# chacha20.init(key)
# cipher = chacha20.encrypt(plaintext)
# chacha20.decrypt(cipher)#




def usage():
    print("USAGE: {} [input-file-path] [key] [iv/nonce] [algorithm] [mode]".format(sys.argv[0]))
    print("Available algorithms:")
    print("-- 0 ==> RC4")
    print("-- 1 ==> Salsa20")
    print("-- 2 ==> ChaCha20")
    print("-- 3 ==> Trivium")
    print("-- 4 ==> Rabbit")
    print("Available Modes:")
    print("-- 0 ==> run setup once")
    print("-- 1 ==> Single initialization")


def pick_algorithm(option, input_file_name, key, nonce):
    if option == '0':
        return RC4Cipher.RC4Cipher(input_file_name, key, nonce)
    elif option == '1':
        return Salsa20Cipher.Salsa20Cipher(input_file_name, key, nonce)
    elif option == '2':
        return Chacha20Cipher.Chacha20Cipher(input_file_name, key, nonce)
    elif option == '3':
        return triviumcipher.TriviumCipher(input_file_name, key, nonce)
    elif option == '4':
        return RabbitCipher.RabbitCipher(input_file_name, key, nonce)


# --------------  main program ---------------#
num_args = len(sys.argv)
if num_args != 6:
    print("Wrong number of arguments: {} Expected {}".format(num_args, 5))
    usage()
    exit(-1)
key, iv = sys.argv[2], sys.argv[3]
print(key, iv)
input_file_name = sys.argv[1]
if not os.path.isfile(input_file_name):
    print("input file does not exists or not readable: ", input_file_name)
algorithm = sys.argv[4]
print(algorithm)

cipher = pick_algorithm(algorithm, input_file_name, key, iv)
class_name = cipher.__class__.__name__

print("Algorithm chosen: ", class_name)
print("Reading from: ", input_file_name)

execution_mode = sys.argv[5]
# todo missing setup?
if execution_mode == '0':
    cipher.process_file()
    cipher.finalize_and_check()
else:
    cipher.encrypt_file()



