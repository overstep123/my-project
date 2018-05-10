import os
a = os.path.dirname(os.path.dirname(os.path.relpath(__file__)))
b = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(1)
print(a)
print(2)
print(b)