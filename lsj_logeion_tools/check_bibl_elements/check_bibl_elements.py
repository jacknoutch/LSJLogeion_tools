import os, re
import pandas as pd
from lxml import etree
from copy import deepcopy

def get_plutarch_bibls(root: etree.Element) -> list[etree.Element]:
    return [e for e in root.iter() if is_valid(e)]

def is_valid(element: etree.Element) -> bool:
    if not element.tag == "bibl":
        return False
    
    n_attribute = element.get("n")

    if not n_attribute:
        return False
    
    re_author = r".*tlg,(0007|0094),.*"
    if not re.fullmatch(re_author, n_attribute):
        return False

    return True

def process_plutarch_bibls(bibls: list[etree.Element]) -> list[etree.Element]:
    
    return [e for e in bibls if process_plutarch_bibl(e) is not False]

def process_plutarch_bibl(bibl: etree.Element) -> bool:
    old_bibl = deepcopy(bibl)
    amendments = []
    
    global moralia_abbreviations

    moralia_works = moralia_abbreviations["work"].unique()

    n_attribute = bibl.get("n")
    re_n_attribute = r"Perseus:abo:tlg,(?P<author>0007|0094),(?P<work>\d{3}):(?P<stephanus>\d{1,4}[abcdef])"

    matches = re.fullmatch(re_n_attribute, n_attribute)

    # Does the bibl have a valid "n" attribute?
    if not matches:
        # TODO: Check that there aren't Moralia references in here?
        return False
    
    n_author = matches["author"]
    n_work = int(matches["work"])
    
    # Is this a Moralia work?
    if not n_work in moralia_works:
        return False
    
    # Does the "n" stephanus match the one in the text?
    bibl_text = "".join(bibl.itertext())
    re_stephanus = r"\b([1-9]\d{0,3}[a-f])\b"
    text_stephanus = re.search(re_stephanus, bibl_text).group()
    n_stephanus = matches["stephanus"]

    if n_stephanus != text_stephanus:
        n_stephanus = text_stephanus
        bibl.attrib["n"] = f"Perseus:abo:tlg,{n_author},{n_work:03}:{n_stephanus}"
        amendments.append("fixed_n_stephanus")
    
    # Is the n reference's stephanus within the work's stephanus range?
    df_work = moralia_abbreviations.query(f"work == {n_work}")
    n_abbreviation = df_work["abbreviation"].iloc[0]

    n_work_start = df_work["start"].iloc[0]
    n_work_end = df_work["end"].iloc[0]
    
    if is_larger_stephanus(n_work_start, n_stephanus) or is_larger_stephanus (n_stephanus, n_work_end):
        n_author, n_work, n_abbreviation = get_tlg_reference(n_stephanus, moralia_abbreviations)
        bibl.attrib["n"] = f"Perseus:abo:tlg,{n_author:04},{n_work:03}:{n_stephanus}"
        amendments.append("fixed_n_work")

    # Test author element
    author_element = bibl.find("author")
    valid_author_text = ["Plu.", "Id.", "id.", "Ps.-Plu."]
    
    if author_element is not None:
        if author_element.text not in valid_author_text:
            print(author_element)
            

    # Test title element
    # Is the abbreviation in <title> correct?
    title_element = bibl.find("title")

    if title_element is not None:
        title = title_element.text
        title = title.replace("[","")
        title = title.replace("]","")
        if n_abbreviation != title:
            title_element.text = f"[{n_abbreviation}]"
            amendments.append("title_element_text_fixed")

    else:
        new_title_element = etree.SubElement(bibl, "title")
        new_title_element.text = f"[{n_abbreviation}]"    

        if author_element is not None:
                
            new_title_element.tail = author_element.tail
            author_element.tail = " "
            amendments.append("title_element_added_post_author")

        else:
            new_title_element.tail = f" {bibl.text}"
            bibl.text = ""
            amendments.append("title_element_added_no_author")

    if len(amendments) > 0:
        # etree_print(old_bibl)
        # etree_print(bibl)
        return bibl
    
    return False

# Loading of tlg references

def load_moralia_abbreviations() -> pd.DataFrame:
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)

    tsv_path = os.path.join(script_dir, "../moralia_abbreviations.tsv")
    
    df = pd.read_csv(tsv_path, sep="\t")
    
    return df

def etree_print(element: etree.Element) -> None:
    """A method for printing the string of an etree.Element to the terminal."""
    print(etree.tostring(element, encoding="unicode"))

def get_tlg_reference(stephanus: str, moralia_df: pd.DataFrame) -> tuple[str, str, str]:
    """
    """
    
    for row in moralia_df.itertuples():
        if is_larger_stephanus(row.end, stephanus):
            return (row.author, row.work, row.abbreviation)
    
    raise ValueError(f"stephanus ({stephanus}) is too large for Plutarch's Moralia")

def is_larger_stephanus(ref1: str, ref2: str) -> bool:
    """Return True if ref1 is larger than ref2 and vice versa.
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

moralia_abbreviations = load_moralia_abbreviations()