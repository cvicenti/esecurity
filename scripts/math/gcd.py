x1 = 63
x2 = 48


def int_gcd(a, b):

    while b != 0:
        rem = a % b
        a = b
        b = rem
    return a


print(int_gcd(x1, x2))
