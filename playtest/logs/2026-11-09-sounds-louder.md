# The mod's sounds made as loud as the game's (2026-11-09)

The user barely heard the hide (140) and pickpocket (141) sounds. Analysis (read-only agent): same
playback routine, volume byte (6Eh) and format as the game's; the WAVs were saved at 55% and 70% of
full scale (sound-data/make.py), and their priority byte (descriptor +6) was 1, the lowest, while the
game's fight sounds have 9 and 10: the game plays a sound only if its priority is at least the one
playing's (3172:073Ah "cmp al,[2A6h] / jnc"), so a hide during a fight sound was dropped.

Changed: make.py saves hide-1 at full scale plus 3 dB through a tanh soft limiter, pocket-2 at full
scale; the descriptor's +6 is 10. Loudest 400 ms (K-weighted, from the WAVs): hide -19.0 -> -10.6
LUFS, pick -12.8 -> -9.7; the game's 115 clips' median -11.1.

In DOSBox (`PT_AUDIO=$WORK/audio.raw`, `loadsave.sh pens-after-scar`, `playsound.py N` with 3 s
between, the raw file's size before and after each): peak and loudest 400 ms RMS of DOSBox's output

| Sound | Peak | RMS dBFS |
|---|---|---|
| 140 hide (mod) | 2,957 | -32.9 |
| 141 pick (mod) | 2,769 | -36.1 |
| 104 (game, fight) | 2,963 | -26.7 |
| 106 (game, fight) | 2,967 | -31.3 |
| 23 (game, fight) | 2,984 | -31.3 |
| 53 (game, quest) | 2,814 | -34.2 |

Both played twice, the same each time. The pick is short (0.4 s, clinks in its first 0.2 s), so
its 400 ms RMS reads lower than its loudness. Priority not tested against a playing fight sound
(playsound.py plays one at a time).
