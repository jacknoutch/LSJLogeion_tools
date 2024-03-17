import csv, os, re
import pandas as pd
from lxml import etree

# REGEX STRINGS

re_stephanus = r"(\b[1-2]\.[1-9]\d{0,3}[a-f]\b)|(?<!\.)\b([1-9]\d{0,3}[a-f])\b"

max_plutarch_stephanus = "1147a"

# COLLECTION OF REFERENCES

def print_headword(element: etree.Element) -> None:
    """Prints the headword (the dictionary entry) for the current element. Useful for orientating oneself in the 
    lexicon."""
    div2 = [ancestor for ancestor in element.iterancestors() if ancestor.tag == "div2"]

    if len(div2) == 0:
        return
    
    head = div2[0].find(".//head")

    print(head.text)

def has_reference(text: str) -> bool:
    """Tests if the text input (a string) contains a valid stephanus reference.
    This function is intended to work on the text or tail node of an element, though it will work on any string.
    """
    if not text:
        return False
    
    # this regex matches for wyttenbach (2.123a) and stephanus (345b) references
    re_reference = r"(\b[1-2]\.[1-9]\d{0,3}[a-f]\b)|(?<!\.)\b([1-9]\d{0,3}[a-f])\b"

    match = re.search(re_reference, text)
    
    if not match:
        return False
    
    stephanus = clean_stephanus(match[0])

    # TODO: This is not enough; it is possible that there would be sufficiently-small, stephanus-like references in the text for, e.g., inscriptional references.
    # Consider testing for <author> elements only, not all elements.
    if is_larger_stephanus(max_plutarch_stephanus,  stephanus):
        return False

    return True

def get_string_reference(text: str, maxsplit: int=0) -> list[str]:
    """Returns a list of stephanus references in string format from the given string.

    maxsplit optionally sets a limit for the numberof references returned and defaults to no limit.
    """
    re_reference = r"(\b[1-2]\.[1-9]\d{0,3}[a-f]\b|(?<!\d\.)\b[1-9]\d{0,3}[a-f])\b"
    matches = re.split(re_reference, text, maxsplit)

    return matches

def etree_print(element: etree.Element) -> None:
    """A method for printing the string of an etree.Element to the terminal."""
    print(etree.tostring(element, encoding="unicode"))

# INSERTION OF NEW ELEMENTS

def clean_stephanus(raw_stephanus: str) -> str:
    """"""
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

def get_tlg_reference(stephanus: str, moralia_df: pd.DataFrame) -> tuple[str, str, str]:
    """
    """
    
    for row in moralia_df.itertuples():
        if is_larger_stephanus(row.end, stephanus):
            return (row.author, row.work, row.abbreviation)
    
    raise ValueError(f"stephanus ({stephanus}) is too large for Plutarch's Moralia")

def is_larger_stephanus(larger_ref: str, smaller_ref: str) -> bool:
    """Return True if larger_ref is larger than smaller_ref and vice versa.
    """
    if not isinstance(larger_ref, str) and not isinstance(smaller_ref, str):
        raise TypeError(f"one or both of larger_ref ({type(larger_ref)}) and smaller_ref ({type(smaller_ref)}) are not strings")

    # clean stephanus references are of the form '1234a'
    re_clean_stephanus = r"[1-9]\d{0,3}[a-f]"
    assert re.fullmatch(re_clean_stephanus, larger_ref), f"larger_ref ('{larger_ref}') is not a clean stephanus reference"
    assert re.fullmatch(re_clean_stephanus, smaller_ref), f"smaller_ref ('{smaller_ref}') is not a clean stephanus reference"

    page1, section1 = split_stephanus(larger_ref)
    page2, section2 = split_stephanus(smaller_ref)

    if page1 == page2:
        return section1 > section2

    return page1 > page2

def split_stephanus(stephanus: str) -> tuple[int, str]:
    """Split a simple stephanus reference str to return a tuple of the page and section.

    Argument 'stephanus' must consist of the reference only. Whitespace is acceptable.
    
    e.g. split_stephanus('512b') -> (512, 'b')
    e.g. split_stephanus('  2.432d ') -> (432, 'd')
    
    Returns False if a stephanus reference is not found."""

    stephanus = stephanus.strip()

    re_split_stephanus = r"\b(?:2\.){0,1}(?P<page>\d{1,4})(?P<section>[a-f])\b"
    match = re.fullmatch(re_split_stephanus, stephanus)

    if not match:
        raise ValueError(f"split_stephanus: No match found for 'stephanus' {stephanus}")

    page = int(match["page"])
    section = match["section"]
    
    return page, section

def parse_n_attribute(n_attribute: str) -> tuple[str, str, str]:
    """Returns the meaningful elements of an 'n' attribute for Plutarch's Moralia.   
    """

    re_n_attribute = r"Perseus:abo:tlg,(?P<author>0007|0094),(?P<work>\d{3}):(?P<stephanus>\d{1,4}[abcdef])"
    match = re.fullmatch(re_n_attribute, n_attribute)

    if match is None:
        return False
    
    return (match["author"], match["work"], match["stephanus"])

# Loading Moralia data

def load_moralia_abbreviations() -> pd.DataFrame:
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)

    tsv_path = os.path.join(script_dir, "../resources/moralia_abbreviations.tsv")
    
    df = pd.read_csv(tsv_path, sep="\t")
    
    return df

moralia_abbreviations = load_moralia_abbreviations()