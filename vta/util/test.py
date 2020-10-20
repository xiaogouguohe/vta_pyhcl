from pyhcl import *
from generic_parameterized_bundle import *

def test_generic_parameterized_bundle_init():
    params = "init params"
    generic_parameterized_bundle = GenericParameterizedBundle(params)
    print("in func test_generic_parameterized_bundle_init, generic_parameterized_bundle.params:", \
        generic_parameterized_bundle.params)


if __name__ == "__main__":
    test_generic_parameterized_bundle_init()
    