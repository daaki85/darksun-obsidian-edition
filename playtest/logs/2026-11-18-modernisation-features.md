# The modernisation features on the current branch, the owner's changes, 2.19.0's play checks (2026-11-18)

Build: branch `claude/modernisation-features` (the nine commits of
`claude/modernisation-integration` rebased onto `obsidian-edition` at 1051ee3, #112, then the
owner's changes). `dos/DSCLOG.EXE` 71,440 bytes, signature `DSCLOGve`, the same as a fresh build
(`cmp`). DOSBox 0.74-3 on Linux, the Loader's patched game, the dice log (`start.sh`); the Loader's
own window for the last part. Window 320x240. Saves: `fountain-user`, `pens-after-scar`. No other
agent's game was running; Xvfb `:55` and `:77`, DOSBox, the dice logs and the watchdog were this
session's, stopped by pid at the end.

## 1. The helper (fountain-user)

- `buildcheck.py`: every routine the same as the EXE, 129 vectors at their handlers, the tail's
  data the same: OK. Again after each restart (three), and in the arena: OK.
- `memaudit.py` in Pehtucl's ambush, the overhead map open: upper memory from CA00h (UMBPLUS):
  DSCLOG 71,664 bytes (4,479 paragraphs), the overlay buffer 32,992, **24,576 bytes free in one
  piece**, the see-through tables 14,160, the music buffer 12,016. Conventional: 96,960 bytes free
  in one piece after the game (the view needs 60,000). `map open flag 1`.
- The overhead map (M) opened and closed in the fight; no "Out of memory in OEOpenGraph" in the
  dice log or DOSBox's.
- The squares' crosses are drawn from the map in DSCLOG's PSP, by the code in the tail
  (`TINT_FAR`): seen on Seneca's, Jenna's and Ester's turns in the pens and Cilla's in the arena.
  Quick save's routine in the tail (`SAVE_FAR`): the autosave of part 4 was made by it.

## 2. The owner's changes (fountain-user, Pehtucl's ambush)

- **R hides and shows the squares** (the game's own answer to R first: nothing to see, the turn,
  the view and the pointer as they were). Seneca's turn, the crosses up: `r`: the crosses gone,
  "Squares hidden" over her, the dice log's `Squares in reach: hidden (R shows them)`,
  `"squares_shown": false` in settings.json; Shift+R: `Squares in reach: shown (R hides them)`,
  `true`, the crosses back. In the arena on Cilla's turn the same ([picture](img/2026-11-18-squares-arena-r.png):
  the crosses on the sand, then "Squares hidden"). DSCLOG's key counts untouched (`qsave.py
  state`: seq 0 0).
- **No chance under the look pointer** (`hoverlabel.py foe 25`, the Templar): the walk arrow
  `"12+ (45%)"`, the eye `no label`, the sword `"12+ (45%)"`.
- **The panel only on the map**: L, the panel up; F2: the LOAD window whole, the QUICK button and
  the list clear ([picture](img/2026-11-18-load-window-no-panel.png)), `DS:0BC9h` 2; EXIT: the
  panel back, 1. A member's END menu (a click on Seneca): 2, the panel away, the menu where the
  panel is ([picture](img/2026-11-18-end-menu-no-panel.png)); Escape: back.
- **F10**, three cases, each with `movestate.py` before and after:
  1. *Movement left*: Seneca walked from (55,96) to (56,93), 80 points left; F10: (55,96), 120,
     flags 3EFh. The game's own; no line from the Loader.
  2. *After the last step*: (55,96) to (55,84), twelve straight steps, 0 points, flags 3EEh, the
     END menu (Escape); F10: (55,96), 120 points, **flags 3EFh**, `F10: Seneca's move taken back
     (can walk again)`; a click on (58,93) walked her there. Again with Jenna after the Loader's
     second version was started (below): the same.
  3. *After an attack*. An attack ends the member's turn (Seneca's, Jenna's: the flags zeroed,
     `turnwatch.py`), so F10 after it is the next member's. **An attack that kills leaves the
     turn**: Ester, walked to her last step beside the Templar (4 HP left by then), killed it;
     `+181h` 0, `+1ABh` 1, flags 3EEh, the turn still hers. F10 put her back with 120 points,
     **and the first version of the mend gave her the walk** (it read only `+181h`): `F10:
     Ester's move taken back`. Mended at once (`+1ABh` read too, a unit test for it), the dice log
     restarted, and played again: Ester walked to her last step beside an Arena Guard (her
     second leg's points and the guard's 1 HP set in memory, the autosave off), killed it, F10:
     (54,95), 120 points, **flags 3EEh, no line, and a click on (55,93) walked nobody**.
- **The tabs' names** in the Loader's window at 1320x780: Dice log, Dialogue, Journal, Spells,
  Memory tools, Options, each whole, before the change and after it (Linux's fonts); with the
  notebook made exactly as wide as `tabs_width` says, still whole. The cut names were on the
  owner's Windows: not seen here.

**A slip**: DOSBox was killed in place of the dice log once (two pid files read in the wrong
order; HISTORY.md, the shell). The fight was lost and the save loaded again.

## 3. The game's keys

For the key that hides the squares (the owner: "The A key already toggles animations on and
off"). The game's three tables for the map and a fight, from DSUN.EXE (`gamekeys.py`):

- the root's, 1BC5Bh (the routine at 1B7DEh; 26 keys, then 26 handlers): 1-6, P, N, Space, F5,
  F6, F9, F10, Home, End, the four arrows, PgUp, PgDn, Alt+F1, Alt+F2, Alt+F4;
- a key not among them goes, with the map up, to overlay 4272h's entry 0020h (file 71153h): its
  table at 71C1Bh, 33 keys: Esc, 1-4, =, Tab, Q, W, T, A, S, G, H, Alt+X, Ctrl+C, M, ?, Space,
  F1-F6. **A and F6 share a routine (715CDh): DS:11ACh flipped, a message, the animations.** S,
  T, M and ? begin with `cmp word [11B0h], 0` and do nothing when it is 0;
- and a letter not among those, from c to v, through the jump table at 71BE3h: C, E, I, U, V
  (717A5h, the screens), O and P (71799h); **d, f, g, h, j, k, l, m, n, q, r, s, t go to the
  routine's end**.

So B, D, F, J, K, L, R, X and Z are bound nowhere; L is the mod's already. **R** was chosen
(Reach). It is read by the Loader from the BIOS keyboard buffer, so DSCLOG is not changed for
it, and the game still gets the key and does nothing with it.

## 4. Autosave on an area change, loaded and played on; the champions' bout

No memory edit up to the autosave: `pens-after-scar`, the walk to the fire room, two rests,
Kurzak's call, up to the gate, Y (toalarm.sh's and arenatrip.sh's steps without Cilla's thief
level: now `PT_NO_EDIT=1`).

- Region 2Ah at (488, 200); four seconds on: `Autosave: "Auto - Day 2, 17:01 - The arena" (the
  QUICK page, slot 6)`, `SAVQ06.SAV` 120,492 bytes.
- `loadquick.sh 6` (a fresh start, the QUICK page, row 6): region 2Ah, (488, 200).
  `buildcheck.py` OK. **Played on**: the bone wall's gap, the platform, the Announcer's
  champions' speech, `fight_on 1`.
- The squares on Cilla's turn and R (part 2).
- **#108's check on this helper** (the autosave and quick save switched off first, the dice log
  restarted; then memory edits, nothing saved): the other five champions Paralyzed (`foeset.py C
  eff=34`), the elf (combatant 45) at 200 HP, turns passed (`passn.sh 1`, `healparty.py`). The
  elf's two shots at Cilla, as the dice log wrote them:
  ```
  Champion attacks Cilla with Wooden Fine Bow (1d8): d20 = 7, needs 4+ (85%), hits AC 2, target AC 5 -> HIT
      THAC0 14, +4 DEX, +1 fine = 9
    Champion hits Cilla for 5: 1d8 = [4] +1 weapon
  Chill Touch damage: 1d4 = [1] = 1
      Chill Touch lasts 60 rounds (caster level 7: 1 from the dice; dice 1d1)
  Cilla's saving throw vs Chill Touch from Champion (spell): d20 = 2 +5 DEX 21 dodging = 7, needs 12 (70% to save) -> failed: full damage, 1
  ```
  and the second saved against (`no damage (not 3)`). As 2026-11-18-champion-chill-arrows.md has
  it: Chill Touch on each hit, caster level 7, the arrows +1.
- The bout and the arena's next waves fought out (`fightout.sh`, every foe at 1 HP in memory).
  K'ratchek's PICK A PSIONIC POWER stopped it: a power's icon clicked, then the screen left
  (EXIT; with a pick still owed it asks YOU HAVE MORE: EXIT / CANCEL).
- **Alt in the arena** (after the fight, the Announcer's yes/no answered N): 10 rings, 4 names:
  gold rings under the door, three bodies, the vulture, the tied-up prisoner and what lies on the
  sand; "Door", "Dead Body", "Vulture" ([picture](img/2026-11-18-alt-arena.png)). At the gate and
  at the bone wall's gap before the bout: no ring (nothing but the party in view).

## 5. The Loader's own window (the arena, after the bout)

The dice log stopped and `/usr/bin/python3.12 -m dsloader view` started on the second display
(`:77`; the Loader reads the game through its process, so its window needs no share of DOSBox's
display or mouse). "Connected to the game".

- **The Characters tab was empty**: `Loader error in the party table: KeyError: 'stealth'
  (viewer.py:1986)`. `viewer.py` still asked for two switches "Fewer switches" (#110) took off
  the tab (`stealth`, `aging`), on a path only a game attached reaches. Both made always-on
  there, a test for it (`test_switch_names`), the window started again: the four cards, ages and
  ranger skills and all.
- **Journal**: 37 entries of this play (Kurzak's call, the Announcer, the champions' speech, the
  level-ups, the yes/no question with its answers).
- **Quests** (the Show box's last choice), read from the running game: `0 open, 1 finished`:
  **King of the pens - The arena**, "The champions sent to test the new king of the pens were
  fought." ([picture](img/2026-11-18-quests-live.png)).

## Not seen

- Windows: GOG's DOSBox, the tabs' cut names, the picture modes, the music device.
- A region other than the slave pens and the arena (no save of the kit is past them: a save in
  the sewers or the wastes would be needed for the squares' and Alt's marks on other floors and
  for the quests given there).
- The squares' dark crosses on a floor the dust has no colours for; a hasted walker.
- F10 after a spell cast, and after an effect that pins a member (held by the unit tests only). Seen
  2026-11-20 ([log](2026-11-20-f10-after-spell.md)): after a spell the mend stays out; a pin put
  on after the last step (a memory edit) got the walk back, mended the same day.
- Of #107's checks (the champions' gear) only what the elf's shots show was seen again: its
  Wooden Fine Bow ("+1 fine"), its Chill Arrows and its DEX 22 (`foeset.py`'s scores; the
  Tohr-kreen's and the halfling's 22 too). The halfling's staff sling and the defiler's bracers
  were not looked at; the bout itself was fought through on this helper.

Water: none new (the arena has none: ROUTE.md).

## After #115 (2026-11-19): the base merged in

`obsidian-edition` gained #115 (the always-on switches' off paths out of DSCLOG and the Loader,
about 1.1 KB freed) while the pull request waited; it was merged into this branch. `dsclog.asm`
merged with no conflict (checked all the same: `test_header_offsets` passes, the signature stays
`DSCLOGve`); the Loader's conflicts were where #115 took out the switches our code passed along
(`combat_log`, `use_targeting`, `show_dust`, `show_shadows`), kept as theirs with our additions.
DSCLOG.EXE rebuilt: 70,256 bytes, 1,232 bytes of the segment and 75 paragraphs of upper memory
spare (48 bytes and 1 paragraph before).

Seen on the merged build (DOSBox 0.74-3, no memory edit): `buildcheck.py` OK in
`pens-after-arena` and in `fountain-user`'s ambush; F5 wrote `SAVQ01.SAV` ("Quick - Day 1,
00:21": the routine that runs from the tail); the squares in reach drawn on Lex's turn (the pass
that runs from the tail). 2,183 tests with the game's files; the window tests pass.
