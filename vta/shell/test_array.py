class Person:
    def __init__(self, name = "Alice"):
        self.name = name
        
a1, a2, a3, a4, a5 = [i for i in range(5)]
b = [Person() for i in range(5)]
print(a1, a2)
print(b)