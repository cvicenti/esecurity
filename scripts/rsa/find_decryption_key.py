# d x e mod PHI = 1

e = 7
PHI = 120


def find_d(e, phi):
    d = 1
    while d <= phi:
        if d*e % phi == 1:
            return d
        d = d + 1

    return 0


print(find_d(e, PHI))
