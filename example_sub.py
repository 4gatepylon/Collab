import subprocess
from subprocess import Popen, PIPE

outs, errs = Popen(["python3", "example_error.py"], stdout=PIPE, stderr=PIPE).communicate()
print("errs: " + str(errs))
print("outs: " + str(outs))

print("\nWorking:\n")
outs, errs = Popen(["python3", "example_src.py"], stdout=PIPE, stderr=PIPE).communicate()
print("errs: " + str(errs), "\t", errs is None)
print("outs: " + str(outs))