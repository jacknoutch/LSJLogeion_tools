from lxml import etree
from utilities import *

# COLLECTION OF REFERENCES.

# TODO: Abstract the collection functions to create single-action functions.

def get_plutarch_elements(root: etree.Element) -> list[etree.Element]:
    """Returns a list of those elements in the root which contain a valid, unwrapped stephanus reference in its tail
    node, and which is nearest, preceding <author> element refers to Plutarch.
    """

    # Loop through the elements, keeping a track of the last <author> tag
    last_author = {"author": None}

    def traverse(node: etree.Element, cache, result: list[etree.Element]):
        if node is None:
            return result
        
        if node.tag == "author" and node.text != "Id.":
            cache["author"] = node.text

        for child in node:
            result = traverse(child, cache, result)

        if has_unwrapped_reference(node, cache["author"]):
            result.append(node)
    
        return result

    return traverse(root, last_author, [])

def has_unwrapped_reference(node: etree.Element, author: str) -> bool:

    if not author == "Plu.":
        return False
    
    if node.tag == "title":
        return False
    
    bibl_ancestor = [e for e in node.iterancestors() if e.tag == "bibl"]
    
    if len(bibl_ancestor) > 0:
        assert(len(bibl_ancestor) == 1)
        return False
    
    if not has_reference(node.tail):
        return False

    return True

# INSERTION OF NEW ELEMENTS

def wrap_references(element: etree.Element, new_elements: list) -> bool:

    plutarch_rows = load_moralia_tlg_csv()

    new_element = wrap_bibl_element(element, plutarch_rows)
    new_elements.append(new_element)

    while has_reference(new_element.tail):
        new_element = wrap_bibl_element(new_element, plutarch_rows)
        new_elements.append(new_element)

    return new_elements

def wrap_bibl_element(element: etree.Element, plutarch_rows: list) -> etree.Element:
    parent = element.getparent()
    index = parent.index(element) + 1 # +1 because we will insert *after* the existing author element
    tail = element.tail

    separated_tail = get_string_reference(tail, 1)
    
    assert(len(separated_tail) == 3) # one reference was found

    # Replace the element's tail with any string preceding the reference
    element.tail = separated_tail[0]

    stephanus = clean_stephanus(separated_tail[1])
    author, work = get_tlg_reference(stephanus, plutarch_rows)
    
    new_bibl_element = etree.Element("bibl", {"n": f"Perseus:abo:tlg,{author},{work}:{stephanus}"})
    new_bibl_element.text = separated_tail[1]
    new_bibl_element.tail = separated_tail[2]
        
    parent.insert(index, new_bibl_element)
    
    return new_bibl_element