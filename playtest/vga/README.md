# VGA tests for zooming the view (2026-11-19)

Small DOS programs that check what DOSBox 0.74-3's emulated VGA and S3 card allow. They don't
need the game. Build each one with `nasm -f bin X.asm -o X.COM`, then run it in DOSBox with
`machine=svga_s3` and `vmemsize=8`. A space moves to the next step. Grab the window with
`import -window` (the run in RESEARCH.md's "Zooming the view" used Xvfb :77, so it never met the
game's :55).

| Program | Steps | Result |
|---|---|---|
| `zoom.asm` | the game's video mode (mode X); doubled rows (CR09=43h); halved dot clock (SR01 bit 3); moved start | rows doubled: yes; dot clock: **ignored**; moved start: yes |
| `big.asm` | mode X; S3 bank 1 (CR6A) for writes; start bit 16 (CR69); 640 wide (CR00-05, CR13=80) | bank: **ignored** in mode X (writes wrap into the first 256 KB); 640 wide: yes |
| `mix.asm` | mode X picture; S3 8-bit display on (CR31 bit 3, CR3A bit 4, CR13=40); planar drawing again; bank 4 | the planar picture shows right in the S3 mode; planar drawing still works there |
| `mix3.asm` | as mix, then bank 4 filled (map mask 0Fh) and CR69 stepped 0-31 | bank 4's bands show at CR69=4, page 0 at 0; it repeats every 8 (2 MB seen, with vmemsize=8) |
