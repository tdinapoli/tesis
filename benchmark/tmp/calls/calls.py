
def func1():
    return None

def func2():
    return func1()

for _ in range(1000000):
    func2()

