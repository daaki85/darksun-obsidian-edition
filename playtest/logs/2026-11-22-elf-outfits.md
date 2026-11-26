# Elf outfits in the slave pens

The test used the patched DOSBox build, an isolated copy of the owner’s game, and the PENS save. The female and male elf each have 37 playable builds and 29 native poses.

- The loader generated both picture chunks for each staged outfit. The walk and combat bytes in the disposable game file matched its output before launch. Two Clerics, a male Preserver with magical plate, and a female Fighter/Psionicist/Thief with boots appeared together at 320 × 240. [DOSBox capture](../../obsidian-edition/docs/class-outfits/elf-in-game.png)
- The ordinary loader attach failed because the process-memory file was read-only. Live equip and remove actions remain pending.
- The loader’s party fixture read all 37 combinations on both figures, including reversed slot order. In all 74 cases, Boots of Speed changed both picture chunks and removal restored their original bytes. Disabling the option restored the stock chunks.
- The separate renderer sweep checked 19,314 poses with empty slots, boots, a cloak, a shield, a sword, bow and ammunition, mundane plate, magical plate, and mixed gear. The mixed case caught a floating pixel above the side bow on both elves. After registering the helmet to the crown, each rendered figure was connected and fit its allocated picture space. The registered bow survived each equipment state. Magical plate changes stayed within the chest mask.
- Original and cleaned heads were compared in all 29 poses. The source mouth highlight and jaw shadows in the front walk and strikes now survive the body redraw. The comparison includes the exposed face, Cleric, Thief and Psionicist. [Face loop](../../obsidian-edition/docs/class-outfits/elf-faces.gif)
