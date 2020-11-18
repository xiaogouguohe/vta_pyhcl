class Base:
    _member = 1

class D1(Base):
    pass

class D2(D1):
    pass

d2 = D2()
print(d2._member)