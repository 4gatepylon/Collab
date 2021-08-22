#!callname:fib
# hello!
def fib(n):
    if n == 1 or n == 2:
        return 1
    else:
        return fib(n-1) + fib(n-2)

def ping_latency(addr):
    from subprocess import Popen, PIPE
    outs, errs = Popen(["ping", "-c", "5", addr], stdout=PIPE, stderr=PIPE).communicate()
    if len(errs) > 0:
        # used to mark inf basically
        return -1.0
    else:
        st = outs.decode("utf-8")
        lines = (st.split("\n"))[1:]
        lines = list(filter(lambda l: "time=" in l, lines))
        if len(lines) <= 0:
            return -2.0
        indices = map(lambda line: line.index("time="), lines)
        total = 0.0
        count = 0.0
        for line, idx in zip(lines, indices):
            idx_start = idx + len("time=")
            # print(line[idx_start: ])
            idx_end = idx_start + 1
            while line[idx_end].isdigit():
                idx_end += 1
            # print(line[idx_start : idx_end])
            if line[idx_end] != ".":
                return -3.0
            idx_end += 1
            while line[idx_end].isdigit():
                idx_end += 1
            # print(line[idx_start : idx_end])
            # print("including number " + str(line[idx_start: idx_end]))
            try:
                total += float(line[idx_start:idx_end])
                count += 1.0
            except ValueError:
                return -4.0
        return total / count
# expect 2
def main(n=10, m=0):
    if type(n) == int:
        if m == 0:
            return fib(n)
        else:
            return fib(n) + m*2
    elif type(n) == str:
        return ping_latency(n)
    else:
        return "PY ERR"