# 2026-11-19: Wake of the Ravager's transfer program on modded saves

**Under test:** what SSI's `CHARTRAN.EXE` (Wake of the Ravager's folder) makes of a party played
with the mod, for the study in `reports/wake-of-the-ravager.md`. Not a play of either game: only
the text-mode utility ran, in a DOSBox of its own (`chartran.sh`, new today).

1. Both games extracted (`setup_game.sh`, `setup_ravager.sh`; innoextract, dosbox, Xvfb, xdotool
   installed by hand with apt first: the container had none of them).
2. `selling-junk-user` (Gerakis, K'ratchek, Cermak, Cilla): the paths screen, Enter; "Dark Sun
   Save Game Selection", "A) SAVE01.SAV, selling junk"; A; "Characters transferred." and SSI's
   note that items without a counterpart become cash. Roster slots 32-35 written.
3. The same with `DEBUG` on `trap-user` (Lex, Jenna, Ester, Seneca) and `rest-no-call-user`
   (Cromwell, Balthbeorn, Finster, Cenna): transferred; `DEBUG.DAT` maps the mod's items (2419-2448,
   2580-2637, 30032...) to 900, a money bag. "Spell: Player 0:, spell #10": one spell not carried.
4. In the written roster each member's kit byte (SL sheet `+43h`) is at the WotR sheet's `+3Dh`,
   the second sphere (`+45h`) at `+3Fh`; the weapon specs (`+14h`-`+17h`) are gone.

No stalls. DOSBox ran with `cycles=max`, `nosound=true` and `output=surface`; the window was found
by `xdotool search --pid` (the game's own `--class dosbox` would find another DOSBox if one ran).

**Water:** no area visited.
