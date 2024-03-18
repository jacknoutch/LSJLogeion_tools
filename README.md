# LSJLogeion_tools
This repository containts scripts for amending the LSJLogeion XML files for LSJ. The scripts are designed to fix those instances in the text where Plutarch's *Moralia* are referenced, but which do not have appropriate `<bibl>` tags.

## find_and_wrap_id_instances
This script finds all the instances of `Id.` in the text and wraps them in an `<author>` tag. This prepares the ground for subsequent scipting.

To execute, run the command `python main.py id [source] [destination]`, where `[source]` and `[destination]` are folders where containing the LSJ XML files to be amended and the intended destination for amended files. You must be in the right folder.

The default values of `[source]` and `[destination]` are `../../LSJLogeion/` and `../../LSJLogeionNew/` respectively.

## add_moralia_references
This script searches for all references to Plutarch's *Moralia* and wraps each of them in a `<bibl>` tag.

The script works by searching for references in the tail of elements tags which refer to Plutarch. That is, its nearest preceding `<author>` element is either  `<author>Plu.</author>` or `<author>Id.</author>`, where the `Id.` refers back to a previous Plutarch `<author>` element.

To execute run the command `python main.py add [source] [destination]` where the `[source]` and `[destination]` are where to read from and save to the LSJ XML files. Make sure you are in the right folder.

The default values of `[source]` and `[destination]` are `../../LSJLogeion/` and `../../LSJLogeionNew/` respectively.

## amend_moralia_references
This script finds all `<bibl>` elements referring to Plutarch's *Moralia* and checks the following:
1. Is the stephanus reference in the text the same as that in the "n" reference of the `<bibl>` element?
2. Is the stephanus in the correct range of the work identified in the "n" reference?
3. Is there a suitable `<title>` element within the `<bibl>` element? If so, is the abbreviation correct? If no `<title>` is present, one is added with the appropriate abbreviation, after an `<author>` element if one is present.

## Testing
These scripts have some small testing scripts to ensure some kind of accuracy. 

Following exploratory testing, I am confident that there are no relevant references in the text nodes of any elements. The assumption on which these scripts are based, that it is the tail node of elements which contains unwrapped *Moralia* elements appears to hold.

## Known issues
~~The assumption for the `add_moralia_refences` tag is not quite correct: not all references to the *Moralia* are in the tail of `<author>` tags referring to Plutarch. Some appear in the tails of `<cit>` and `<sense>` tags. Particularly, there are occurences after `ib.` or `cf.`, which are often references in proper Stephanus (not Wyttenbach) format (so 123b rather than 2.123b).~~

Update 10 Mar 2024: the scripts have been rewritten to look for references in the tail of *any* element. This has captured a few hundred more references (264 on my last execution of the script). There is one exception: `<title>` elements are specifically ignored, since apparently in all instances for which an apparent stephanus reference is found, the reference is actually for an inscription, not Plutarch's *Moralia*.
