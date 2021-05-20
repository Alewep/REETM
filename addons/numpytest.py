import numpy as np


def functiontest(numpyarray):
    numpyarray = numpyarray + 1


a = np.arange(1, 5)

print(a)
functiontest(a)
print(a)
