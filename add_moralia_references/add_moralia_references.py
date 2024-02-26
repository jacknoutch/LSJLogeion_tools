import csv, os, re, string
from lxml import etree

class Reference(object):
    pass

# COLLECTION OF REFERENCES

def get_plutarch_elements(root: etree.Element) -> list:
    plutarch_elements = []

    # Load the csv file which specifies the author and work from any Plutarch Stephanus reference.
    plutarch_rows = load_moralia_tlg_csv()

    # Loop through the elements, keeping a track of the last <author> tag
    elements = root.findall(".//")
    last_author = None

    for element in elements:

        if element.tag == "author" and element.text != "Id.":
            last_author = element
        
        if last_author is not None and last_author.text != "Plu.":
            continue

        text = element.text
        tail = get_tail(element)

        if has_reference(text) or has_reference(tail):
            plutarch_elements.append(element)

        # stephanus = get_stephanus(tail)

        # if stephanus:
        #     # try:
        #     #     get_tlg_reference(stephanus, plutarch_rows)
        #     # except ValueError:
        #     #     continue

        #     if last_author.text == "Plu." and last_author.getparent().tag == "bibl":
        #         plutarch_elements.append(element)

    return plutarch_elements

def has_reference(text: str) -> bool:
    if not text:
        return False
    
    # this regex matches for wyttenbach (2.123a) and stephanus (345b) references
    re_reference = r"(\b[1-2]\.[1-9]\d{0,3}[a-f]\b)|(?<!\d\.)\b([1-9]\d{0,3}[a-f])\b"

    return re.search(re_reference, text)

def get_references_old(text: str) -> list:
    references = []
    
    # this regex matches for wyttenbach (2.123a) and stephanus (345b) references
    re_reference = r"(\b[1-2]\.[1-9]\d{0,3}[a-f]\b)|(?<!\d\.)\b([1-9]\d{0,3}[a-f])\b"

    matches = re.split(re_reference, text)

    tails = matches[::2] # every 2nd string
    refs = matches[1::2] # every second string beginning with the second

    for i, ref in enumerate(refs):
        references.append({"reference": ref, "tail": tails[i+1]})

    return references


def has_wyttenbach_reference(element: etree.Element) -> bool:
    # elements without a tail are not required
    tail = element.text
    if not tail: return False

    # check for a Wyttenbach reference in the tail
    re_wyttenbach = r"\b[1-2]\.[1-9]\d{0,3}[a-f]\b"
    return re.search(re_wyttenbach, tail)

def get_references(element: etree.Element) -> list:
    
    text = element.text
    tail = get_tail(element)

    print(text,tail)
    etree_print(element)

    text_refs = []
    tail_refs = []
    
    # this regex matches for wyttenbach (2.123a) and stephanus (345b) references
    re_reference = r"(\b[1-2]\.[1-9]\d{0,3}[a-f]\b|(?<!\d\.)\b[1-9]\d{0,3}[a-f])\b"

    text_matches = re.split(re_reference, text)

    text_inbetweens = text_matches[::2]
    text_references = text_matches[1::2]

    text_refs.append({"reference": None, "location": "text", "inbetween": text_inbetweens[0]})
    for i, reference in enumerate(text_references):
        text_refs.append({"reference": reference, "location": "text", "inbetween": text_inbetweens[i+1]})

    if tail is None:
        return text_refs

    tail_matches = re.split(re_reference, tail)

    tail_inbetweens = tail_matches[::2]
    tail_references = tail_matches[1::2]

    tail_refs.append({"reference": None, "location": "tail", "inbetween": tail_inbetweens[0]})
    for j, reference in enumerate(tail_references):
        tail_refs.append({"reference": reference, "location": "tail", "inbetween": tail_inbetweens[j+1]})

    return (text_refs, tail_refs)

def get_stephanus(text: str) -> bool:
    if not text:
        return ""
    re_stephanus = r"(?<!\d\.)\b([1-9]\d{0,3}[a-f])\b"
    try:
        return re.search(re_stephanus, text).group(0)
    except AttributeError:
        return False

def get_tail(element: etree.Element) -> str:
    try:
        return element.tail
    except AttributeError:
        return ""

def load_moralia_tlg_csv() -> list:
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    csv_path = os.path.join(script_dir, "../plutarch_stephanus_tlg_references.csv")
    
    return get_plutarch_rows_from_csv(os.path.join(csv_path))

def wrap_element_references(element: etree.Element) -> bool:

    plutarch_rows = load_moralia_tlg_csv()

    if element.tag == "bibl":
        print(element.text)
    
    text_references, tail_references = get_references(element)

    # references are a list of dicts; each dict is as follow:
    #   {
    #       "reference": 2.1234a,
    #       
    #   }

    

    # for reference in text_references:
    #     # is the reference already in a <bibl> element?
    #     if reference["location"] == "tail":
    #         # add a 
    #         pass
        
    #     if element.tag != "bibl":
    #         pass

    #     elif reference["location"] == "tail":
    #         pass

    #     else:
    #         etree_print(element)
    #         print("REFERENCE ALREADY IN TEXT OF BIBL TAG")

        


    # parent = element.getparent()
    # index = parent.index(element) + 1 # new elements to be inserted *after* the existing element
    # tail = element.tail


    # for i, ref in enumerate(references):
    #     if ref["reference"]:
    #         print(ref)
    #         stephanus = clean_stephanus(ref["reference"])
    #         author, work = get_tlg_reference(stephanus, plutarch_rows)
    #         n_reference = f"Perseus:abo:tlg,{author},{work}:{stephanus}"

    #         ancestor = parent
    #         while ancestor is not None:
    #             stephanus_already_wrapped = False
    #             ancestor_stephanus = None
    #             ancestor_n = ancestor.get("n")
    #             if ancestor_n:
    #                 ancestor_stephanus = ancestor_n[ancestor_n.rfind(":") + 1:]
    #             if ancestor.tag == "bibl" and ancestor_stephanus == stephanus:
    #                 stephanus_already_wrapped = True
    #                 break
    #             ancestor = ancestor.getparent()
            
    #         if stephanus_already_wrapped:
    #             continue

    #         new_bibl_element = etree.Element("bibl", {"n": n_reference})
    #         new_bibl_element.text = stephanus
    #         new_bibl_element.tail = ref["inbetween"]
                
    #         parent.insert(index + i, new_bibl_element)

    #         etree_print(parent)

    # author, work = get_tlg_reference(stephanus_pieces[1], plutarch_rows)
    # n_reference = f"Perseus:abo:tlg,{author},{work}:{stephanus_pieces[1]}"

    # ancestor = parent
    # while ancestor is not None:
    #     ancestor_stephanus = None
    #     ancestor_n = ancestor.get("n")
    #     if ancestor_n:
    #         ancestor_stephanus = ancestor_n[ancestor_n.rfind(":")+1:]
    #     if ancestor.tag == "bibl" and ancestor_stephanus == stephanus_pieces[1]:
    #         return False
    #     ancestor = ancestor.getparent()

    # element.tail = stephanus_pieces[0]

    # new_bibl_element = etree.Element("bibl", {"n": n_reference})
    # new_bibl_element.text = stephanus_pieces[1]
    # if len(stephanus_pieces) > 2:
    #     new_bibl_element.tail = stephanus_pieces[2]
        
    # parent.insert(index + 1, new_bibl_element)

    # etree_print(parent)
    return True

def etree_print(element: etree.Element) -> None:
    print(etree.tostring(element, encoding="unicode"))

# INSERTION OF NEW ELEMENTS

def wrap_bibl_elements(elements: list):    
    new_elements = []

    # Open the CSV file containing the references for Plutarch's Moralia, for converting the stephanus
    plutarch_rows = get_plutarch_rows_from_csv(os.path.join(os.getcwd() + "/../" + "plutarch_stephanus_tlg_references.csv"))

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

    re_wyttenbach_stephanus = r"(?<=\b[1-2]\.)[1-9]\d{0,3}[a-f]\b" # e.g. 2.1234a
    match = re.search(re_wyttenbach_stephanus, raw_stephanus)

    if not match:
        re_simple_stephanus = r"(?<!\d\.)\b[1-9]\d{0,3}[a-f]\b" # e.g. 1234a
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
        
    raise ValueError(f"stephanus_reference ({stephanus_reference}) is too large for Plutarch's Moralia")

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