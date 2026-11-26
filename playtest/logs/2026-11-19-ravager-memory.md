# 2026-11-19: memory in Wake of the Ravager and Shattered Lands, unmodded, with the map open

**Under test:** how much memory the sequel leaves free in DOSBox (conventional, upper, the game's
heap) against Shattered Lands, to see whether a helper like DSCLOG would fit. Both games are
unmodded, each with GOG's own DOSBox settings (WotR memsize 16, cycles fixed 15000; SL memsize 32,
cycles fixed 7000; XMS, EMS and upper memory on in both). Sound off (`nosound=true`).

## Run 1: Wake of the Ravager, GOG's settings (EMS on)

- Started `DSUN -W0 -L` with C: the game folder and D: the CD's data track (a cue of track 1 only:
  Linux's DOSBox 0.74 can't take GOG's `game.ins`, whose music tracks are .ogg). Shift skipped the
  intro; the menu at 6 s. DOSBox captures the mouse, so `xdotool mousemove_relative` moves the
  pointer (START GAME at window 310,170 in its 640x480). The narrated cinematic (about 60 s, no
  skip), then Tyr: the woman's "Hurry! You must come with me to the Veiled Alliance!" over the map.
- **At the menu:** the game's block 519,168 bytes, 129,728 free after it; upper memory one free
  block of 65,520 bytes (D000h; EMS's page frame takes E000h-EFFFh).
- **In Tyr, the map drawn:** the game's block 584,704 bytes, **64,192 free after it**; upper
  memory the same 65,520. Its Borland far heap is at load + **135Bh** (first, last, rover; SL's is
  at 0FE7h): 5982h-8FD9h, 217 KB, **48,528 bytes free in one piece**.

## Run 2: Wake of the Ravager, the mod's memory setup (EMS off, UMBPLUS.COM first)

- `ems=false`, `UMBPLUS.COM` (the mod's `dos/`, on E:) run before the game. The game started and
  played as in run 1 (menu, START GAME, the cinematic, Tyr's opening talk): **its memory layer runs
  on XMS without EMS.** The first click on the menu only captures the mouse (DOSBox); moves after it.
- **UMBPLUS.COM works on it:** upper memory one free block at C900h, **159,728 bytes** (9,983
  paragraphs), nothing of the game's in it.
- **In Tyr:** the game's block 584,704 bytes, **64,192 free after it**, its heap 217 KB with
  **48,656 bytes free in one piece**: the same as with EMS on.
- **Overlays** (the FBOV segment table): 49 modules, the largest 16,732 bytes (Shattered Lands: 52,
  the largest 15,537); its buffer, twice the largest, about 2.4 KB bigger than SL's 32,992.

## Run 3: Shattered Lands, unmodded, the same setup (EMS off, UMBPLUS.COM first)

- GOG's settings (memsize 32, cycles fixed 7000) with `ems=false` and `UMBPLUS.COM`, `darksun`
  run plain (no Loader, no helper). Escape five times through the intro, START GAME, the decree and
  the gladiators' scene, then the arena's opening scene (Tithian on his balcony) at 75 s.
- **Upper memory:** the same free block at C900h, 159,728 bytes.
- **In the arena:** the game's block 589,824 bytes, **59,072 free after it**, its heap 241 KB with
  **nothing free in it** (the mod's docs: 57 KB, "the unmodded game's"; the same).

## What it means

| With the map open | Shattered Lands (arena) | Wake of the Ravager (Tyr) |
|---|---|---|
| Conventional memory free after the game | 59,072 | 64,192 |
| Free in the game's own heap | 0 | 48,656 (one piece) |
| Upper memory free (EMS off, UMBPLUS.COM) | 159,728 | 159,728 |
| Overlay buffer (twice the largest overlay) | 32,992 (measured) | about 33,500-35,500 (estimated) |

The sequel leaves about 110 KB spare in the 640 KB against Shattered Lands' 57 KB, runs without
EMS, and has the same upper memory. A helper of DSCLOG's size, the sequel's overlay buffer and the
see-through tables would fit upper memory with room over (DSCLOG's set there today: 8,117 of 9,983
paragraphs). Not checked: whether the sequel has a music buffer to move (its music is CD audio),
and memory deeper in the game (one scene each, at the start). The helper's own 64 KB segment
(688 bytes spare) is the limit that stays: a matter of the helper's code size, not the game.

No stalls beyond the mouse capture. **Water:** none seen (the opening scenes only).
