# LSJLogeion_tools
This repository containts two scripts for amending the LSJLogeion XML files for LSJ. The scripts are designed to fix those instances in the text where Plutarch's *Moralia* are referenced, but which do not have appropriate `<bibl>` tags.

In total these scripts find and wrap 2,112 `Id.` references and 5,159 *Moralia* references.

## find_and_wrap_id_instances
This script finds all the instances of `Id.` in the text and wraps them in an `<author>` tag. This is necessary as the `add_moralia_references/main.py` searches for references to the *Moralia* by `<author>` tag.

To execute, run the command `python3 main.py [source] [destination]`, where `[source]` and `[destination]` are folders where containing the LSJ XML files to be amended and the intended destination for amended files. You must be in the right folder.

The default values of `[source]` and `[destination]` are `../../LSJLogeion/` and `../../LSJLogeionNew/` respectively.

## add_moralia_references
This script searches for all references to Plutarch's *Moralia* and wraps each of them in a `<bibl>` tag.

The script works by searching for references in the tail of `<author>` tags which refer to Plutarch. (So, either `<author>Plu.</author>` or and `<author>Id.</author>` element which refers back to Plutarch.)

Executing the script is done in the same way as for the `find_and_wrap_id_instances` script. Make sure you are in the right folder.

## Testing
These scripts have some small testing scripts to ensure some kind of accuracy.

For the `add_moralia_references` script, the tests focus on the validity of the Stephanus references, to make sure only *Moralia* references are captured. Within the `main.py` script itself, an error is also raised if the actual text of the XML (as opposed to the  lement objects within it) is changed. This should ensure the script does not alter the LSJ text.

For the `find_and_wrap_id_instances` script, the only test is to ensure the actual text of the LSJ is not changed in the process. Unlike `add_moralia_references`, this is in a proper test module rather than the `main.py`.

## Known issues
The assumption for the `add_moralia_refences` tag is not quite correct: not all references to the *Moralia* are in the tail of `<author>` tags referring to Plutarch. Some appear in the tails of `<cit>` and `<sense>` tags. Particularly, there are occurences after `ib.` or `cf.`, which are often references in proper Stephanus (not Wyttenbach) format (so 123b rather than 2.123b). Further investigation should be done to see where else references may be hiding!