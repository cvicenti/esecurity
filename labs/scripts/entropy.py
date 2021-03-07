import math

# n_phrases = 36**8
# n_phrases = 128
# n_phrases = 9.13439*(10**46)
n_phrases = 26*(36**6)*10

# [a-z] -> 26
# [a-z][A-Z] -> 52
# [a-z][A-Z][0-9] -> 62
# 4-letter [a-z] word = 26**4

entropy = math.log(n_phrases, 2)
print("total number of phrases: {0}".format(n_phrases))
print("entropy: {0}".format(entropy))
print("entropy = {0} Bits".format(round(entropy)))
