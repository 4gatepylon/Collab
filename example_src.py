#!callname:fib
# hello!
def fib(n):
    if n == 1 or n == 2:
        return 1
    else:
        return fib(n-1) + fib(n-2)

# expect 2
def main(n=10, m=0):
    if m == 0:
        return fib(n)
    else:
        return fib(n) + m*2