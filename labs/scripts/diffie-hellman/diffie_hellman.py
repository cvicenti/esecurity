G = 201
N = 31
x = 12
y = 7

A = (G**y) % N
B = (G**x) % N
print "A ", A
print "B ", B

key_A = (A**x) % N
key_B = (B**y) % N

print "key_A ", key_A
print "key_B ", key_B