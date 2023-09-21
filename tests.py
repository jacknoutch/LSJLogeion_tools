import unittest
from LSJLogeion_tools.add_moralia_references import *

class TestAddMoraliaReferences(unittest.TestCase):
    def test_input_incorrect_stephanus(self):
        # none of these are stephanus references for Plutarch's Moralia
        incorrect_inputs = [ 
            "a123", 
            "12.123c", 
            "1.1a23",
            "1b23",
        ]
        for incorrect_input in incorrect_inputs:
            result = clean_stephanus(incorrect_input)
            self.assertEqual(False, result)

    def test_input_incorrect_type(self):
        incorrect_inputs = [
            123,
            False,
            None,
            {"123a"},
            ["2.34b"],
        ]
        for incorrect_input in incorrect_inputs:
            with self.assertRaises(TypeError):
                clean_stephanus(incorrect_input)

if __name__ == "__main__":
    unittest.main()