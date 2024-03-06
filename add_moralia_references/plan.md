# The problem

To find all the references to Plutarch's *Moralia* which are not yet wrapped with a `<bibl>` tag and wrap it in one.

# Issues
- Where do "lost" references exist? Are they only in the tails of XML elements? Are there any in the text nodes of the XML?

# Log

01/03/2024
- Are there any "lost" references in the text nodes of XML elements?
-- data004.txt contains all the elements whose text nodes include a matching reference but which is not in a `<bibl>` tag; there are only two such elements, and neither of them are relevant.
-- All other elements with matching references in the text nodes are `<bibl>` elements. There are 7353 of them.

-- Do any of these `<bibl>` elements contain *more* than the stephanus reference in their text node?
-- No, data011.txt show all of the elements whose match objects return a list of more than three text strings. There are none.

-- Are the `<bibl>` elements correct in that their "n" attributes match the stephanus in the text node?
--- **TODO:** Two such elements do not have an "n" attribute. These are printed in data005.txt. They are both for Plutarch references and should be amended.
--- All `<bibl>` elements bar one (in data012.txt) which have an "n" attribute have a stephanus value in that attribute which matches the stephanus in the text node.
--- **TODO:** Do the "n" attributes match the author and work?

-- What kind of references are there in these `<bibl>` elements? Which authors do they represent?
--- A list of the number of elements by tlg author code is given in data006.txt.
--- Some of these author codes appear not to be valid... e.g. 0009 **TODO:** rectify this
--- data007.txt contains the five instances of `<bibl>` tags which do not have author/work n references, apparently because they are inscriptions?
--- The `<bibl>` n_references for 7 of the references in the text node show the wrong tlg author and work; they are down as being 0007 (Plutarch), whereas they should be 0094 (Pseudo Plutarch). These instances are in data008.txt
--- The other 5411 references to 0007 are correct. They are listed in data009.txt.
--- **TODO:** Some of the references erroneously maintain a **2.** for the stephanus ref.