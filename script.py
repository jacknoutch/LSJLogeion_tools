# This script searches LSJ to find all Plu. Moralia references

# Examples of references to be caught:

# 2.510f, 625b, 693a;
# cf. <author>Plu.</author> 2.961e
# <bibl n="Perseus:abo:tlg,0007,069:38c"><author>Plu.</author> <title>[Aud.phil.]</title> 2.38c</bibl></cit>, cf. 145b
# <author>Plu.</author> <title>Crass.</title> 8</bibl></cit>; <cit><quote lang="greek">οἰκέτας ὠνίους ἐξάγειν</quote> <author>Id.</author> 2.680e</cit>
# <author>Plu.</author> <title>Agis</title> 4</bibl>; <i>refinement,</i> <author>Id.</author> 2.972d;
# <author>Plu.</author> l.c.

# Beware of Pl. [Plato] who has Stephanus numbers too!

# The search is conducted twice.
# First, all instances of "Plu." are compiled.
# Second, all instances of "Id." following "Plu." are compiled.
# Third, all instances of LSJ Stephanus (of the type 1.2345a) references are compiled.

# TODO: What about "l. c. " and "ll. cc."? Should these be done by hand?

# 

import csv, os, re
from lxml import etree
from pprint import pprint

#

def main():

    # Load XML files
    path_LSJ = "../LSJLogeion/"
    lsj_xml_files = os.listdir(path_LSJ) # all files in the file path
    lsj_xml_files = [x for x in lsj_xml_files if x[-4:] == ".xml"] # only XML files please
    lsj_xml_files.remove("greatscott01.xml") # front matter; not required for search
    lsj_xml_files.sort()
    
    # Loop through the files and retrieve all references to Plutarch's Moralia
    plutarch_references = [] # a reference is a dictionary: {"file": "greatscott86.xml", "parent": <element>, "child": <author>, "index": 1, "raw_stephanus": "1.2345f", "tail": <str>}
    counter = 0
    for file in lsj_xml_files:

        plutarch_references[:] = []

        with open(path_LSJ + file, "r") as f1:

            print(f"{file} in progress...")
            
            file_string = f1.read().encode("utf-8")
            root = etree.fromstring(file_string)
            
            plutarch_references += get_plutarch_references(root)
            counter += len(plutarch_references)
            for reference in plutarch_references:
                reference["file"] = file
    
            # Wrap the references in <bibl> elements
            wrap_bibl_element(plutarch_references)

            # Save the new XML
            new_path = path_LSJ # "../LSJLogeionNew/"
            with open(new_path + file, "w") as f2:
                file_string = etree.tostring(root, encoding="unicode")
                f2.write(file_string)
                print(f"{file} done!")

            print(f"{counter} references complete")
    
#

def get_plutarch_references(root) -> list:
    plutarch_references = []

    # All references will either be in the tail of an <author> tag with text "Plu.", or
    # in the tail of an <author> tag with "Id." which refers back to an <author> tag with text "Plu."
    
    # Find the parent elements of all author elements with the text "Plu."
    # Parents are required in order to insert new elements correctly
    plutarch_parent_elements = root.findall(".//author[.='Plu.']..")
    plutarch_parent_elements = list(set(plutarch_parent_elements))

    for plutarch_parent in plutarch_parent_elements:
        true_plutarch_references = get_true_plutarch_references(plutarch_parent)
        plutarch_references += true_plutarch_references


    # Find all entries, within which to search for author elements
    entry_elements = root.findall(".//div2")
    for entry_element in entry_elements:
        id_plutarch_references = get_id_plutarch_references(entry_element)
        plutarch_references += id_plutarch_references

    return plutarch_references

def get_true_plutarch_references(parent):
    true_plutarch_references = []

    # True Plutarch references are in <author> tags with text "Plu."
    plutarch_elements = parent.findall("./author[.='Plu.']")

    # Only author tags with a Stephanus reference in its tail are needed
    for plutarch_element in plutarch_elements:
        
        raw_stephanus_references = get_raw_stephanus_references(plutarch_element)
        index = parent.index(plutarch_element)
        
        for raw_stephanus_reference in raw_stephanus_references:
            reference = {"parent": parent, "child": plutarch_element, "index": index, "raw_stephanus": raw_stephanus_reference, "tail": plutarch_element.tail}
            true_plutarch_references.append(reference)

    return true_plutarch_references

def get_raw_stephanus_references(plutarch_element):
    raw_stephanus_references = []

    # Stephanus references are in the tail of the <author> element
    tail = plutarch_element.tail
    if not tail:
        return []
    
    # The first Stephanus reference is always of the format 1.2345f
    re_stephanus = r"[1-2]\.\d{1,4}[a-f]"
    stephanus_match = re.search(re_stephanus, tail)
    
    if not stephanus_match:
        return []
    
    stephanus = str(stephanus_match.group())
    raw_stephanus_references.append(stephanus)
    
    # There may be further Stephanus references, of the format 1234f
    tail = tail.replace(stephanus, "")
    re_short_stephanus = r",.{0,8}\b(\d{1,4}[a-f])"
    matches = list(re.finditer(re_short_stephanus, tail))
    for match in matches:
        raw_stephanus_references.append(match.groups()[0])
    
    return raw_stephanus_references

def get_id_plutarch_references(parent):
    id_plutarch_references = []

    # Find all the author elements, and Id. author elements
    author_elements = parent.findall(".//author")
    id_elements = parent.findall(".//author[.='Id.']")

    # Only "Id." author tags immediately preceded by "Plu." author tags are needed
    for id_element in id_elements:
        previous_author_element = get_previous_author_element(id_element, author_elements)
        if previous_author_element is not None:

            # A reference to an actual author may be followed by several "Id." elements; we must find the previous instance which isn't "Id."
            while previous_author_element.text == "Id.":
                previous_author_element = get_previous_author_element(previous_author_element, author_elements)

            if previous_author_element.text == "Plu.":
                
                # The direct parent is required to insert new elements correctly 
                parent_elements = parent.findall(".//author[.='Id.']..")
                for parent_element in parent_elements:
                    if id_element in parent_element:
                        id_parent = parent_element

                index = id_parent.index(id_element)

                raw_stephanus_references = get_raw_stephanus_references(id_element)
                for raw_stephanus_reference in raw_stephanus_references:
                    reference = {"parent": id_parent, "child": id_element, "index": index, "raw_stephanus": raw_stephanus_reference, "tail": id_element.tail}
                    id_plutarch_references.append(reference)
    
    return id_plutarch_references

def get_previous_author_element(origin, author_elements):
    origin_index = author_elements.index(origin)
    if author_elements.index(origin) > 0:
        return author_elements[origin_index - 1]

#

def wrap_bibl_element(references):
    # Insertion into the XML tree requires the references to be sorted, from lowest to highest index
    references = sorted(references, key=lambda reference: reference["index"])
    
    # As elements are inserted, a tally must be kept so that later elements with the same parents can have their index offset correctly
    parent_count = []

    for reference in references:
        # for ease of use...
        parent = reference["parent"]
        index = reference["index"]
        raw_reference = reference["raw_stephanus"]
        
        # Open the CSV file containing the references for Plutarch's Moralia, for converting the stephanus
        csv_rows = []
        with open("plutarch_stephanus_tlg_references.csv") as csv_file:
            csv_reader = csv.reader(csv_file)
            fields = next(csv_reader)
            for row in csv_reader:
                csv_rows.append(row)

        # Create the new <bibl> element
        stephanus = clean_stephanus(reference["raw_stephanus"])
        author, work = get_tlg_reference(stephanus, csv_rows)
        new_bibl_element = etree.Element("bibl", {"n": f"Perseus:abo:tlg,{author},{work},{stephanus}"})

        # The target element is the one whose tail contains the stephanus reference
        # This is kept track of using the reference's index, offset by the number of previous insertions
        target_element = parent[index + parent_count.count(parent)]
        
        # Split the tail into three parts:
        # part 1 is the tail of the target_element
        # part 2 is the text of the new <bibl> element
        # part 3 is the tail of the new <bibl> element    
        old_tail = target_element.tail
        re_split = re.compile(f"({raw_reference})")
        tail_pieces = re.split(re_split, old_tail)

        target_element.tail = tail_pieces[0]
        new_bibl_element.text = tail_pieces[1]
        new_bibl_element.tail = tail_pieces[2]

        # Insert the <bibl> after (+1) the target element
        parent.insert(parent.index(target_element) + 1, new_bibl_element)
        
        # Since an insertion has occurred, add this parent to the tally list
        parent_count.append(parent)

def clean_stephanus(raw_stephanus):
    re_lsj = r"(?<=[1-2]\.)\d{1,4}[a-f]"
    match = re.search(re_lsj, raw_stephanus)
    return match.group() if match else raw_stephanus

def get_tlg_reference(stephanus_reference, rows):
    for row in rows:
        tlg_author = row[7]
        tlg_work = row[8][3:]
        if is_larger_stephanus(stephanus_reference, row[6]):
            return (tlg_author, tlg_work)
    return None

def is_larger_stephanus(ref1: str, ref2: str):
    # clean stephanus references are of the form '1234a'

    alphabet = "abcdefghijklmnopqrstuvwxyz"

    page1 = int(ref1[:-1])
    page2 = int(ref2[:-1])
    section1 = ref1[-1:]
    section2 = ref2[-1:]
    if page1 == page2:
        alphabet_ref1 = alphabet.index(section1)
        alphabet_ref2 = alphabet.index(section2)
        return alphabet_ref1 <= alphabet_ref2
    return page1 < page2

#

main()