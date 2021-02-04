import numpy as np
np.random.seed(789)


# f = x
def function1(x): return x


# f = x sin(x^2)
def function2(x):  return x * np.sin(x ** 2)


def aprox(function, a, b, n):
    Value = 0.0
    the_range = np.random.uniform(a, b, n)
    for i in the_range:
        Value = Value + function(float(i))
    Value = (b-a)/n * Value
    return Value


a = 1
b = 4
n = 1000
function = function1
print(aprox(function, a, b, n))
