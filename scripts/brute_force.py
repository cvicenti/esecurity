hashes_per_second = 1e12
# attempts_per_ns = 1e12(2**20)/10  #20 bit key, 10ns to break a key
attempts_per_ns = 2821109907456

# attempts_per_ns = 28**7
print(attempts_per_ns / hashes_per_second)