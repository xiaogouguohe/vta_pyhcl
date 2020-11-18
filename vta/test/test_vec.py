from pyhcl import *

import sys 
sys.path.append("..") 

from util.ext_funcs import *

if __name__ == "__main__":
    """ vec = Vec(10, U(0))
    vec2 = Vec(10, valid(U(0)))
    res = isinstance(vec, Vec)
    res2 = isinstance(vec2, List)
    print("res:", res) #False
    print("res2:", res2) #True
    vec_size = vec.size 
    vec2_size = vec2.size
    print("vec_size:", vec_size) #10
    print("vec2_size:", vec2_size) #10
    print("vec[0]:", vec[0])
    print("type of vec[0]:", type(vec[0]))
    print("vec2[0]:", vec2[0])
    
    vec3 = Vec(10, flipped(valid(U.w(10))))
    print("vec3[0]:", vec3[0])
    print("type of vec3[0]:", type(vec3[0])) """
    vec4 = [1 for i in range(10)]
    print("vec4[0]:", vec4[0])
    print("len of vec4:", len(vec4))

