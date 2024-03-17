from lsj_logeion_tools.utilities.utilities import *

def test_is_larger_stephanus():
    valid_args = [
        ["1234a", "123a"],
        ["100b", "100a"],
        ["101a", "100a"],
    ]

    for entry in valid_args:
        assert is_larger_stephanus(entry[0], entry[1])