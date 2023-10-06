import csv, unittest
from LSJLogeion_tools.add_moralia_references.add_moralia_references import *

class TestCleanStephanus(unittest.TestCase):
    def test_input_incorrect_stephanus(self):
        # none of these are stephanus references for Plutarch's Moralia
        incorrect_inputs = [ 
            "a123", 
            "12.123c", 
            "1.1a23",
            "1b23",
            "0001a",
            "1.1a2.",
            "1a2",
            "1.12ab",
            "123ab",
        ]
        for incorrect_input in incorrect_inputs:
            with self.assertRaises(ValueError, msg=f"{incorrect_input}"):
                clean_stephanus(incorrect_input)

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

class TestGetTLGReference(unittest.TestCase):
    def setUp(self):
        self.csv_rows = []
        path = os.path.join(os.getcwd(), "LSJLogeion_tools", "plutarch_stephanus_tlg_references.csv")
        with open(path) as csv_file:
            csv_reader = csv.reader(csv_file)
            fields = next(csv_reader)
            for row in csv_reader:
                self.csv_rows.append(row)

    def test_input_stephanus_too_large(self):
        with self.assertRaises(ValueError):
            get_tlg_reference("9999b", self.csv_rows)

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
                get_tlg_reference(incorrect_input, self.csv_rows)

class TestIsLargerStephanus(unittest.TestCase):
    def test_input_incorrect_stephanus(self):
        incorrect_inputs = [
            ["2.34b", "123a"],
            ["12345b", "123a"],
            ["1234g", "123a"],
            ["a123", "123a"],
            ["1b23", "123a"],
            ["0001a", "123a"],
        ]
        for incorrect_input in incorrect_inputs:
            with self.assertRaises(AssertionError):
                is_larger_stephanus(incorrect_input[0], incorrect_input[1])
                
            with self.assertRaises(AssertionError):
                is_larger_stephanus(incorrect_input[1], incorrect_input[0])

    def test_input_incorrect_type(self):
        incorrect_inputs = [
            [123, "123a"],
            [False, "123a"],
            [None, "123a"],
            [{"a123"}, "123a"],
            [["1b23"], "123a"],
        ]
        for incorrect_input in incorrect_inputs:
            with self.assertRaises(TypeError):
                is_larger_stephanus(incorrect_input[0], incorrect_input[1])

if __name__ == "__main__":
    unittest.main()