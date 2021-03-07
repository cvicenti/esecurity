
p = 11


def getG(p):
    for x in range(1, p):
        rand = x
        exp = 1
        next_n = rand % p

        while next_n != 1:
            # print(next_n)
            next_n = (next_n * rand) % p
            exp = exp + 1


        if exp == p - 1:
            print("{0} is a solution".format(rand))
        print(" ")

getG(p)