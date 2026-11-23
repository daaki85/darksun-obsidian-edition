# Dwarf and human map outfits

Used the branch’s patched DOSBox build, a disposable copy of the owner’s game, and the `pens-after-arena` save. Quick save and autosave were disabled for the test. The window was 320 × 240. The loader’s normal live attachment was blocked by the environment’s process-memory permissions.

1. Generated walk and combat picture chunks through `sprites.Pictures.build`. Staged a male dwarf Fighter/Psionicist/Thief with Boots of Speed, a female dwarf Cleric with a cloak, a male human Mage with magical plate, and a female human Fighter with a shield in the disposable pictures file. Checked the eight staged walk/combat chunks against the renderer’s output before launch.
2. Ran DOSBox with the loader detached, loaded PENS, inspected the party on the ground, and clicked to move it. All four staged figures appeared together. Several captures during movement were followed by a stationary sequence with the pointer clear of the party.
3. Seventeen stationary captures showed two cycling pixels on the male Mage’s plate. The combined shield and sword swings, bow frames, other class combinations, and equip/remove transitions were checked separately with the loader renderer or its test-party fixture. Live inventory changes remain pending.

[Review, screenshots, and frame sheets](../../obsidian-edition/docs/class-outfits/checklist-review.md)
