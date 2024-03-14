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
    """A quicker method for printing the string of an etree.Element to the terminal."""
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

def get_tlg_reference(stephanus: str, moralia_df: pd.DataFrame) -> tuple[str, str]:
    """
    """
    
    for row in moralia_df.itertuples():
        author = row.author
        work = row.work
        if is_larger_stephanus(stephanus, row.end):
            return (author, work)
    
    raise ValueError(f"stephanus ({stephanus}) is too large for Plutarch's Moralia")

def is_larger_stephanus(ref1: str, ref2: str) -> bool:
    """Return True if ref2 is larger than ref1 and vice versa.
    """
    if not isinstance(ref1, str) and not isinstance(ref2, str):
        raise TypeError(f"one or both of ref1 ({type(ref1)}) and ref2 ({type(ref2)}) are not strings")

    # clean stephanus references are of the form '1234a'
    re_clean_stephanus = r"[1-9]\d{0,3}[a-f]"
    assert re.fullmatch(re_clean_stephanus, ref1), f"ref1 ('{ref1}') is not a clean stephanus reference"
    assert re.fullmatch(re_clean_stephanus, ref2), f"ref2 ('{ref2}') is not a clean stephanus reference"

    page1, section1 = split_stephanus(ref1)
    page2, section2 = split_stephanus(ref2)

    if page1 == page2:
        return section1 > section2

    return page1 < page2

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