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

# Some references have already been fixed. These will need to be stripped out.

# 

import csv, os, re
from lxml import etree
from pprint import pprint

#

def main():

    # Load XML files
    path_LSJ = "../LSJLogeionOld/"
    lsj_xml_files = os.listdir(path_LSJ) # all files in the file path
    lsj_xml_files = [x for x in lsj_xml_files if x[-4:] == ".xml"] # only XML files please
    lsj_xml_files.remove("greatscott01.xml") # front matter; not required for search
    
    # Loop through the files and retrieve all references to Plutarch's Moralia
    plutarch_references = [] # a reference is a dictionary: {"file": "greatscott86.xml", "parent": <element>, "child": <author>, "raw_stephanus": "1.2345f", "tail": <str>}

    for file in lsj_xml_files:

        with open(path_LSJ + file, "r") as f1:

            print(f"{file} in progress...")
            
            file_string = f1.read().encode("utf-8")
            root = etree.fromstring(file_string)
            
            plutarch_references += get_plutarch_references(root)
            for reference in plutarch_references:
                reference["file"] = file
    
    # Wrap the references in <bibl> elements
    new_elements = []
    for plutarch_reference in plutarch_references:
        new_elements.append(wrap_bibl_element(plutarch_reference))

    # Save the new XML
    new_path = "./LSJLogeionNew/"
    for file in lsj_xml_files:
        with open(new_path + file, "w") as f2:
            file_string = etree.tostring(root, encoding="unicode")
            f2.write(file_string)
            print(f"{file} done!")
    
#

def get_previous_author_element(origin, author_elements):
    origin_index = author_elements.index(origin)
    if author_elements.index(origin) > 0:
        return author_elements[origin_index - 1]
    
def get_short_stephanus_references(tail):
    # For Stephanus references of the format 1234f
    raw_stephanus_references = []

    re_short_stephanus = r",.{0,8}\b(\d{1,4}[a-f])"
    matches = list(re.finditer(re_short_stephanus, tail))
    for match in matches:
        raw_stephanus_references.append(match.groups()[0])
    
    return raw_stephanus_references

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

def get_true_plutarch_references(parent):
    true_plutarch_references = []

    # True Plutarch references are in <author> tags with text "Plu."
    plutarch_elements = parent.findall("./author[.='Plu.']")

    # Only author tags with a Stephanus reference in its tail are needed
    for plutarch_element in plutarch_elements:
        
        raw_stephanus_references = get_raw_stephanus_references(plutarch_element)
        
        for raw_stephanus_reference in raw_stephanus_references:
            reference = {"parent": parent, "child": plutarch_element, "raw_stephanus": raw_stephanus_reference, "tail": plutarch_element.tail}
            true_plutarch_references.append(reference)

    return true_plutarch_references

def get_id_plutarch_references(parent):
    id_plutarch_references = []

    # Find all the author elements, and Id. author elements
    author_elements = parent.findall(".//author")
    id_elements = parent.findall(".//author[.='Id.']")

    # Only "Id." author tags immediately preceded by "Plu." author tags are needed
    for id_element in id_elements:
        previous_author_element = get_previous_author_element(id_element, author_elements)
        if previous_author_element:

            # A reference to an actual author may be followed by several "Id." elements; we must find the previous instance which isn't "Id."
            while previous_author_element.text == "Id.":
                previous_author_element = get_previous_author_element(previous_author_element, author_elements)

            if previous_author_element.text == "Plu.":
                
                # The direct parent is required to insert new elements correctly 
                parent_elements = parent.findall(".//author[.='Id.']..")
                for parent_element in parent_elements:
                    if id_element in parent_element:
                        id_parent = parent_element

                raw_stephanus_references = get_raw_stephanus_references(id_element)
                for raw_stephanus_reference in raw_stephanus_references:
                    reference = {"parent": id_parent, "child": id_element, "raw_stephanus": raw_stephanus_reference, "tail": id_element.tail}
                    id_plutarch_references.append(reference)
    
    return id_plutarch_references

def get_plutarch_references(root) -> list:
    plutarch_references = []

    # All references will either be in the tail of an <author> tag with text "Plu.", or
    # in the tail of an <author> tag with "Id." which refers back to an <author> tag with text "Plu."
    
    # Find the parent elements of all author elements with the text "Plu."
    # Parents are required in order to insert new elements correctly
    plutarch_parent_elements = root.findall(".//author[.='Plu.']..")

    for plutarch_parent in plutarch_parent_elements:
        true_plutarch_references = get_true_plutarch_references(plutarch_parent)
        plutarch_references += true_plutarch_references

    # Find all entries, within which to search for author elements
    entry_elements = root.findall(".//div2")
    for entry_element in entry_elements:
        id_plutarch_references = get_id_plutarch_references(entry_element)
        plutarch_references += id_plutarch_references

    return plutarch_references

#

def clean_stephanus(raw_stephanus):
    re_lsj = r"(?<=[1-2]\.)\d{1,4}[a-f]"
    match = re.search(re_lsj, raw_stephanus)
    return match.group() if match else raw_stephanus

def is_larger_stephanus(ref1: str, ref2: str):
    # clean stephanus references are of the form '1234a'

    alphabet = "abcdefghijklmnopqrstuvwxyz"

    if ref1.find("."):
        ref1 = ref1[2:]

    re_stephanus = r"\d{1,4}[a-f]"

    try:     
        page1 = int(ref1[:-1])
    except ValueError:
        print(ValueError)
        return True
    page2 = int(ref2[:-1])
    section1 = ref1[-1:]
    section2 = ref2[-1:]
    if page1 == page2:
        alphabet_ref1 = alphabet.index(section1)
        alphabet_ref2 = alphabet.index(section2)
        return alphabet_ref1 <= alphabet_ref2
    return page1 < page2

def get_tlg_reference(stephanus_reference, rows):
    for row in rows:
        tlg_author = row[7]
        tlg_work = row[8][3:]
        if is_larger_stephanus(stephanus_reference, row[6]):
            return (tlg_author, tlg_work)
    return None

def wrap_bibl_element(reference):
    
    # Open the CSV file containing the references for Plutarch's Moralia
    csv_rows = []
    with open("plutarch_stephanus_tlg_references.csv") as csv_file:
        csv_reader = csv.reader(csv_file)
        fields = next(csv_reader)
        for row in csv_reader:
            csv_rows.append(row)

    # Get the requisite details for <bibl> element
    stephanus = clean_stephanus(reference["raw_stephanus"])
    author, work = get_tlg_reference(stephanus, csv_rows)
   
    new_bibl_element = etree.Element("bibl", {"n": f"Perseus:abo:tlg,{author},{work},{stephanus}"})

    raw_reference = reference["raw_stephanus"]

    bibl_elements = reference["parent"].findall(".//bibl")
    author_elements = reference["parent"].findall(".//author")
    combined_elements = bibl_elements + author_elements

    reference_element_index = None

    for element in combined_elements:
        if not element.tail:
            continue
        if raw_reference in element.tail:
            old_tail = element.tail
            re_split = re.compile(raw_reference)
            tail_pieces = re.split(re_split, old_tail)
            element.tail = tail_pieces[0]
            new_bibl_element.tail = tail_pieces[1]
            new_bibl_element.text = raw_reference
            try:
                reference_element_index = reference["parent"].index(element) + 1
            except ValueError:
                print(ValueError)
                continue
    
    # Find the location of the reference to insert it
    if not reference_element_index:
        reference_element_index = reference["parent"].index(reference["child"]) + 1
    reference["parent"].insert(reference_element_index, new_bibl_element)
    
    return new_bibl_element

#

main()