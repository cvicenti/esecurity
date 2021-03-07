PHI = 120


def int_gcd(a, b):

    while b != 0:
        rem = a % b
        a = b
        b = rem
    return a


def is_gcd_one(phi):
    b = 2
    while b < phi:
        if int_gcd(b, phi) == 1:
            print(b)

        b = b + 1


print("Valid options are:")
is_gcd_one(PHI)
