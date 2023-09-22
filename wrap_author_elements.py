# This script finds all "Id." instances and wraps them in an <author> tag

import os, re, sys
from lxml import etree
from xml.sax.saxutils import unescape


def main():

    arguments = sys.argv[1:]

    # Load the XML files
    path_from = arguments[0] if arguments else "../LSJLogeion/"
    path_to = arguments[1] if len(arguments) > 1 else "../LSJLogeionNew/"
    files = load_files(path_from)

    element_count = 0
    # Loop through the XML files
    for file in files:

        with open(path_from + file, "r") as f1:
            
            print(f"{file} in progress...")

            file_string = f1.read().encode("utf-8")
            root = etree.fromstring(file_string)

            elements_for_wrapping = get_elements_for_wrapping(root)
            if elements_for_wrapping:
                element_count += len(elements_for_wrapping)
            
            for element in elements_for_wrapping:
                wrap(element)

            with open(path_to + file, "w") as f2:
                file_string = etree.tostring(root, encoding="unicode")
                f2.write(file_string)

            print(f"{file} complete!")
            print(element_count)


def load_files(path):
    
    # Load XML files
    lsj_xml_files = os.listdir(path) # all files in the file path
    lsj_xml_files = [x for x in lsj_xml_files if x[-4:] == ".xml"] # only XML files please
    lsj_xml_files.remove("greatscott01.xml") # front matter; not required for search
    lsj_xml_files.sort()

    return lsj_xml_files

def get_elements_for_wrapping(root):
    elements_for_wrapping = []
    
    entry_wrapper = root.find(".//div1")

    for element in entry_wrapper.iterfind(".//*"):

        if not element.tail:
            continue
    
        re_id = r"Id\."
        matches = re.findall(re_id, element.tail)

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

main()