import unittest
from LSJLogeion_tools.find_and_wrap_id_instances.find_and_wrap_id_instances import *

class TestFindAndWrapIdInstances(unittest.TestCase):
    def test_find_and_wrap_id_instances(self):
        # Test if find_and_wrap_id_instances function works as expected

        input_xml = """
            <root>
                <div1>
                    <p>Some text Id. some more text</p> but here is the Id. to wrap
                    <p>Id. even more text</p> again, another Id.
                </div1>
            </root>
        """

        expected_output = """
            <root>
                <div1>
                    <p>Some text Id. some more text</p> but here is the <author>Id.</author> to wrap
                    <p>Id. even more text</p> again, another <author>Id.</author>
                </div1>
            </root>
        """

        result = find_and_wrap_id_instances(input_xml)
        self.assertEqual(result.strip(), expected_output.strip())

if __name__ == '__main__':
    unittest.main()