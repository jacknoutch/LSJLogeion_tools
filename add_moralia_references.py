# This script searches LSJ to find all Plu. Moralia references and wrap them in an appropriate <bibl> XML element
#
# LSJ refers to Plutarch's Moralia according to the 2 volume Wyttenbach edition.
#
# Wyttenbach references are of the following kind: 2.1234a, composed of the volumn of Wyttenbach, a period, and a stephanus number.
# If LSJ refers to several references in the Moralia, it first uses a Wyttenbach reference, followed by stephanus numbers alone.
#
# The TLG and Wyttenbach references for Plutarch's Moralia can be found in plutarch_stephanus_tlg_references.csv


# Examples of references to be caught:
# 2.510f, 625b, 693a;
# cf. <author>Plu.</author> 2.961e
# <author>Plu.</author> <title>Crass.</title> 8</bibl></cit>; <cit><quote lang="greek">οἰκέτας ὠνίους ἐξάγειν</quote> <author>Id.</author> 2.680e</cit>
# <author>Plu.</author> <title>Agis</title> 4</bibl>; <i>refinement,</i> <author>Id.</author> 2.972d;

# Examples of references not to be caught:
# <bibl n="Perseus:abo:tlg,0007,069:38c"><author>Plu.</author> <title>[Aud.phil.]</title> 2.38c</bibl></cit>, cf. 145b
# <author>Plu.</author> l.c.

# Prepatory work for this script:
# - Make sure all "Id." references are surrounded by <author> tags

import csv, os, re, string, sys
from lxml import etree

# MAIN

def main():

    arguments = sys.argv[1:]
    
    # Load XML files
    path_LSJ = arguments[0] if arguments else "../LSJLogeionOld/"
    lsj_xml_files = os.listdir(path_LSJ) # all files in the file path
    lsj_xml_files = [x for x in lsj_xml_files if x[-4:] == ".xml"] # only XML files please
    lsj_xml_files.remove("greatscott01.xml") # front matter; not required for search
    lsj_xml_files.sort()
    
    # Initialise the collector
    plutarch_elements = []
    
    references_added = 0
    
    for file in lsj_xml_files:

        # Reset the collector for each file
        plutarch_elements[:] = []

        with open(path_LSJ + file, "r") as f1:

            print(f"{file} in progress...")
            
            file_string = f1.read().encode("utf-8") # encoding required for lxml
            
            root = etree.fromstring(file_string)
            plutarch_elements += get_plutarch_elements(root)
    
            # Wrap the references in <bibl> elements
            new_elements = wrap_bibl_elements(plutarch_elements)
            references_added += len(new_elements)

            # Save the new XML
            new_path = arguments[1] if len(arguments) == 2 else "../LSJLogeion/"
            with open(new_path + file, "w") as f2:
                file_string = etree.tostring(root, encoding="unicode")
                f2.write(file_string)
                print(f"{file} done!")

            # output the file's added references
            print(f"{references_added} references added")
    
# COLLECTION OF REFERENCES

def get_plutarch_elements(root: etree.Element) -> list:
    plutarch_elements = []

    # Assumes that all references will be in the tail of an <author> tag, either with text "Plu.", or
    # with text "Id.", referring back to an <author> tag with text "Plu."
    author_elements = root.findall(".//author")

    # Find all Plutarch references in each 
    preceding_element = None
    for element in author_elements:

        if element.text == "Plu.":              # A Plutarch author tag
            preceding_element = element.text
            plutarch_elements.append(element)
        
        elif not element.text == "Id.":         # An author tag with neither Plu. nor Id.
            preceding_element = element.text
        
        elif preceding_element == "Plu.":
            plutarch_elements.append(element)   # An Id. author tag preceded by one with Plu.

    return [e for e in plutarch_elements if has_wyttenbach_reference(e)]

def has_wyttenbach_reference(element: etree.Element) -> bool:
    # elements without a tail are not required
    tail = element.tail
    if not tail: return False

    # check for a Wyttenbach reference in the tail
    re_wyttenbach = r"\b[1-2]\.[1-9]\d{0,3}[a-f]\b"
    return re.search(re_wyttenbach, tail)

# INSERTION OF NEW ELEMENTS

def wrap_bibl_elements(elements: list):    
    new_elements = []

    # Open the CSV file containing the references for Plutarch's Moralia, for converting the stephanus
    plutarch_rows = get_plutarch_rows_from_csv("plutarch_stephanus_tlg_references.csv")

    for element in elements:
        new_elements.append(wrap_bibl_element(element, plutarch_rows))
        
    return new_elements

def wrap_bibl_element(element: etree.Element, plutarch_rows: list) -> list:
    parent = element.getparent()
    index = parent.index(element) + 1 # +1 because we will insert *after* the existing author element
    tail = element.tail
    
    # For debugging:
    # print(etree.tostring(parent, encoding="unicode"))

    # Get all individual references from tail of each element
    stephanus_references = []
    tails = []

    # Find the first stephanus references, e.g. 2.1234a
    re_wyttenbach_stephanus = r"\b([1-2]\.[1-9]\d{0,3}[a-f])\b"
    wyttenbach_stephanus_pieces = re.split(re_wyttenbach_stephanus, tail)
    
    assert(len(wyttenbach_stephanus_pieces) == 3) # To protect against multiple "first" stephanus references

    # Replace the element's tail with any string preceding the reference
    element.tail = wyttenbach_stephanus_pieces[0]

    stephanus_references.append(wyttenbach_stephanus_pieces[1])

    # Find the remaining, "simply" stephanus references, e.g. 1234b
    re_simple_stephanus = r"(?<!\d\.)\b([1-9]\d{0,3}[a-f])\b"
    remaining_pieces = re.split(re_simple_stephanus, wyttenbach_stephanus_pieces[2])

    if len(remaining_pieces) > 1: 
        # remaining stephanus references were found
        stephanus_references += remaining_pieces[1::2]

    # The rest of the strings will be tails to the new elements    
    tails += remaining_pieces[::2]

    # Create the new <bibl> elements
    for i, raw_reference in enumerate(stephanus_references):

        stephanus = clean_stephanus(raw_reference)
        author, work = get_tlg_reference(stephanus, plutarch_rows)
        
        new_bibl_element = etree.Element("bibl", {"n": f"Perseus:abo:tlg,{author},{work}:{stephanus}"})
        new_bibl_element.text = raw_reference
        new_bibl_element.tail = tails[i]
        
        parent.insert(index + i, new_bibl_element)

    # For debugging:
    # print(etree.tostring(parent, encoding="unicode"))
    
    return stephanus_references

def get_plutarch_rows_from_csv(source):
    csv_rows = []
    with open(source) as csv_file:
        csv_reader = csv.reader(csv_file)
        fields = next(csv_reader)
        for row in csv_reader:
            csv_rows.append(row)
        return csv_rows

def clean_stephanus(raw_stephanus: str) -> str:
    # TODO: raw_stephanus could be, e.g. "1.234a, 345b"  and this function not raise an exception
    if not isinstance(raw_stephanus, str):
        raise TypeError(f"raw_stephanus is of the wrong type: {type(raw_stephanus)}")

    re_wyttenbach_stephanus = r"(?<=\b[1-2]\.)[1-9]\d{0,3}[a-f]" # e.g. 2.1234a
    match = re.search(re_wyttenbach_stephanus, raw_stephanus)

    if not match:
        re_simple_stephanus = r"(?<!\d\.)\b[1-9]\d{0,3}[a-f]" # e.g. 1234a
        match = re.search(re_simple_stephanus, raw_stephanus)

    if not match:
        raise ValueError(f"raw_stephanus ({raw_stephanus}) does not contain a stephanus reference")

    return match.group()

def get_tlg_reference(stephanus_reference: str, csv_rows: list) -> tuple:

    for row in csv_rows:
        tlg_author = row[7]
        tlg_work = row[8]
        if is_larger_stephanus(stephanus_reference, row[6]): # row[6] is the stephanus reference representing the last section of the work
            return (tlg_author, tlg_work)
        
    raise ValueError(f"stephanus_reference ({stephanus_reference})is too large for Plutarch's Moralia")

def is_larger_stephanus(ref1: str, ref2: str) -> bool:
    if not isinstance(ref1, str) and not isinstance(ref2, str):
        raise TypeError(f"one or both of ref1 ({type(ref1)}) and ref2 ({type(ref2)}) are not strings")

    # clean stephanus references are of the form '1234a'
    re_clean_stephanus = r"[1-9]\d{0,3}[a-f]"
    assert re.fullmatch(re_clean_stephanus, ref1), f"ref1 ('{ref1}') is not a clean stephanus reference"
    assert re.fullmatch(re_clean_stephanus, ref2), f"ref2 ('{ref2}') is not a clean stephanus reference"

    # all characters except the last is the page number
    page1 = int(ref1[:-1])
    page2 = int(ref2[:-1])

    # the last character is the section letter [a-f]
    section1 = ref1[-1:]
    section2 = ref2[-1:]

    # if the page number is the same, the section letter differentiates the two
    alphabet = string.ascii_lowercase
    if page1 == page2:

        alphabet_ref1 = alphabet.index(section1)
        alphabet_ref2 = alphabet.index(section2)

        return alphabet_ref1 <= alphabet_ref2
    
    return page1 < page2

# RUN

if __name__ == "__main__":
    main()