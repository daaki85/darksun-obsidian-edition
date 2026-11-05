# The scripts' jumps filled (2026-11-05)

Build: `obsidian-edition` after the audit's fixes (`gpl.put_jumps`). DOSBox.

1. `loadsave.sh pens-thornwall-rack` (start.sh's rebuild writes `dos/GPLDATA.GFF`).
2. The built copy: script 3 has the champions' jump at 3A7h (`64 09 65 61`: GOTO 965h, then the
   fill) with Semyon on, as it hadn't before the fix; all 254 GPL and MAS scripts in it decode.
3. In the pens (region 29h): walked south and back north; the game and the dice log ran on.

Not seen: the champions' bout after Scar's death in a real run (the arena's route to Scar is
long); the changed scripts' own talks (Dinos, the Trustee, Alagorn, Garyn, the Elven Leader) in
play. Their commands are unchanged: only bytes past a jump, never run, are now one-byte commands.
