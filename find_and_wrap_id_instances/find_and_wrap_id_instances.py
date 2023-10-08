import re
from lxml import etree

def find_and_wrap_id_instances(input_xml: str) -> str:
    root = etree.fromstring(input_xml)

    elements_for_wrapping = get_elements_for_wrapping(root)
    
    for element in elements_for_wrapping:
        wrap(element)

    print(f"{len(elements_for_wrapping)} new elements added")
    return etree.tostring(root, encoding="unicode")

def get_elements_for_wrapping(root):
    # elements with "Id." in the *tail* are required
    elements_for_wrapping = []

    entry_wrapper = root.find(".//div1")

    for element in entry_wrapper.iterfind(".//*"):

        if not element.tail:
            continue
    
        re_id = r"Id\."
        matches = re.findall(re_id, element.text)

        if matches:
            elements_for_wrapping.append(element)

    return elements_for_wrapping

def wrap(element):

    parent = element.getparent()
    index = parent.index(element) + 1

    re_id = r"(Id\.)"
    string_pieces = re.split(re_id, element.tail)

    tails = string_pieces[::2]
    element.tail = tails.pop(0)

    for i, tail in enumerate(tails):
        new_element = etree.Element("author")
        new_element.text = "Id."
        new_element.tail = tail
        parent.insert(index + i, new_element)
