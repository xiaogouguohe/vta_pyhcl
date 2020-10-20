class Parent:
    def __init__(self, name):
        Parent.name = name

class Children(Parent):
    def __init__(self, name, operation):
        super().__init__(name)
        Children.operation = operation

if __name__ == '__main__':
    p = Parent('papa')
    c = Children('child', 'walk')
    print("child's name", c.name, "child's operaion", c.operation, "finish")