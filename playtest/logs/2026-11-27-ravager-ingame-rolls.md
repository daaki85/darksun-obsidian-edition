# Wake of the Ravager with the in-game rolls (`play --ravager`), 2026-11-27

**Under test**: `python -m dsloader play --ravager` (the new `Play Wake of the Ravager (in-game rolls).bat`):
the sequel started from its folder, and its dice log made by the helper the game loads (`ravlog.make`), not
Shattered Lands'. Branch `claude/sequel-ingame-rolls`.

**Set-up**: Xvfb `:55`, the DOSBox lock held by this session. The Loader's start with GOG's own DOSBox runs
`DOSBOX/DOSBox.exe` from the sequel's folder, a Windows program: on Linux it can't run (PermissionError). A
copy of the sequel's folder (`/tmp/playtest/ravplay`) with `DOSBox.exe` replaced by a shell shim running
`/usr/bin/dosbox` with the same arguments (less `-noconsole`) stands in for it.

**Steps and what was seen**

1. First start: the game stopped at once, `DARKSAVE.GFF to DARKRUN.GFF failed. Path = .\` (the mod's own
   error screen after it). The folder lacked GOG's `__support/save/` files (`ravstart.sh` copies them in
   itself; the Loader's start doesn't). Copied in by hand. Nothing of the change under test.
2. Second start: `play.log` said `Starting Wake of the Ravager from /tmp/playtest/ravplay in DOSBox.` and,
   2 s later, `The dice log follows Wake of the Ravager.` The helper in memory was DSCLOG2's (header at
   CA1B0h, its rules word +170 written: FBE5h).
3. Shift past the logos: the sequel's intro played (the hooded figure in the hall).
4. DOSBox closed by pid: `play.log` said `DOSBox closed.` and saved a crash report (a killed DOSBox's
   non-zero exit, as expected), and the Loader quit.

**Result**: the sequel starts with the in-game rolls, its own dice log attached. Shattered Lands' path is
unchanged (the same `ravlog.make`, which the window already uses; `test_gamelock` covers both).
