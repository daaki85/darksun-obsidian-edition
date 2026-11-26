# For OpenDS: runtime QA of darkfix-ds1 0.2.0-beta.4, first sites (2026-11-24)

*Status: not posted. Written as their QA packet asks (`docs/qa/qa-packet-ds1-script-repairs-beta.md`:
"beta QA: <site> <pass/fail>"). The play's log: [playtest/logs/2026-11-24-darkfix-beta-qa.md](../../playtest/logs/2026-11-24-darkfix-beta-qa.md).*

```
site(s):       G (played); T, H (static notes); R, L, F, W, M, S, A2 not yet played
result:        G pass, with two faults in the lines it prints
game version:  GOG 1.10
fixes enabled: all twelve in manifest.toml at OpenDS 4425eb5 (001-012)
```

**How it was run.** The stock GOG 1.10 install, its GPLDATA.GFF given all twelve fixes' repairs (read
from the fix files' REPAIRS lists and applied by the rules of `compute_patched_chunk`: every
fingerprint matched, and the patched GPL 31, 58, 204 and 210 equal the sha256 the fix pages give).
Plain DOSBox 0.74-3 with GOG's `dosbox_darksun.conf`; nothing of the Obsidian Edition running. The
save was one of ours from the slave pens, loaded into the stock game without trouble.

## G: the sewer grate (fix.ds1.grate-hack): pass, two faults in its lines

The party (Cromwell leading: a Metal Axe in the weapon hand, a Bow in the other) beside the grate.

- (a) **Pass.** Walking onto the grate: "The grate is locked. Do you open the grate?", then "Rip it
  open. / Hack the lock off. / Leave the grate."
- (b) **Pass.** Hack, first two tries: "Cromwell's Bow breaks against the grate." (the script's
  1-in-3 branch, GPL 137 @0x9C5: RAND(3) < 2, or item -1576, succeeds). Third try: "Cromwell
  successfully hacks the lock off with his Bow. The grate opens.", GF[505] = 1, and walking onto it
  again asks "Do you go into the sewers?"
- (c) **Pass.** Attacking the grate: first "Cromwellfails to damage the lock.", a later attack
  broke it (GF[505] = 1, then the sewers question). A roll, not always.

Faults seen:

1. **The wrong weapon is named.** Both lines say "Bow" while the weapon that qualified is the Axe in
   the weapon hand. The weapon search (from @0xA5B) copies each item into the scratch object (field
   2Bh) and names it on a find, but the loop goes round once more and the next item (the Bow) is
   copied over the found one. The Obsidian Edition hit the same thing with yuan-ti's version of this
   repair and leaves the loop on the find (a jump to the loop's RETURN at 0xA96).
2. **A missing space.** "Cromwellfails to damage the lock.": the string at 0xB9B ("fails to damage
   the lock. ") has no leading space, unlike " breaks the lock. ". The line was unreachable before
   this fix, so the fix is what makes it show.

Also: the hack is offered for any item in a hand, so a bow or a sling hacks a lock. The Obsidian
Edition asks for a melee weapon there (its own choice, not a bug in the original).

**A testing note:** reloading a save replays the same rolls (the RNG isn't reseeded by a load), so a
check with a roll needs a different wait before it each time.

## T: tracking (fix.ds1.tracking): a static doubt, not played

The patched GPL 210 doesn't decode with the Obsidian Edition's script reader (checked against every
stock script). The three class-slot detours (@0x60C, 0x622, 0x638) read:

```
18 e2 8c 20 [b1 80 26 02 47 23  d9 8f 0c] e1  d5  e2 [b1 80 26 02 47 23  da 8f 11] e1
```

`8c 20` is `gpl bitsnoop`, which reads **two** operands (OpenDS's own gpl-opcodes.md, "Verified
semantics"). In the stock bytes its two operands were the field and `02 00`. In the repair, the first
operand is `field > 12`, and the second operand starts at the `e1` that was meant to close the
bracket. Read that way, the line's brackets don't balance and the rest of it is read out of step
(what the engine then does is not known: it wants a play). The intent, `(code > 12) and (code < 17)`, wants no bitsnoop:
`18 e2 b1 80 26 02 47 23 d9 8f 0c e1 d5 e2 b1 80 26 02 47 23 da 8f 11 e1` (2 bytes shorter). This
is a reading of the bytes, not a play (region 8 with a ranger is far from our saves). The first
repair (@0x5FD) keeps bitsnoop's two operands and decodes cleanly.

## H: the halfling (fix.ds1.halfling-race): the site is not in the slave pens

GPL 31 is started only by MAS 26 (a talk trigger on -206) and by MAS 42 (entry 6). It opens with the
caravan scripts' check, GF[123] == 1 or the object's +32 field set. So "the slave pens' halfling" in
the packet looks wrong: the halfling is the caravan's (region 26 by its MAS). Not played.

## Not played yet

R (the Trustee), L (Legcrusher gone) and F (the battlefield slave) are next. The slave pens'
saves reach R and L. W, M, S and A2 need saves further on. For A2, see
[the GF123 note](2026-11-24-opends-cure-and-alhena.md#2-gf123-is-never-set-in-a-normal-playthrough-so-alhena-isnt-unreachable).
