from lsj_logeion_tools.utilities.utilities import *

def test_is_larger_stephanus():
    assert is_larger_stephanus("1234a", "123a")
    assert is_larger_stephanus("100b", "100a")
    assert is_larger_stephanus("101a", "100a")