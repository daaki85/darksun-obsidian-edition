# The mod's sounds made denser (2026-11-10)

The user: "The audio just seems to still be very low for the custom sounds" (after
logs/2026-11-09-sounds-louder.md had brought both clips to full scale).

## The volume byte is not a volume
The game's sound descriptors have +0Ah 6Eh for 127 sounds, 7Eh for sounds 7 and 63, 64h for 4 and
3Ch for 58. Our two (DSCLOG's `mod_desc`) have 6Eh. In DOSBox (`PT_AUDIO`, `pens-after-scar`) the
byte was set in memory (the descriptors at linear CA233h and CA23Fh that run) to 110, 127, 60, 20
and 110, and sound 140 played after each: the output's peak was 2,957 every time. DOSBox plays
every clip at the same peak (about 9% of full scale), the game's and ours.

## So the clips' average was raised
`sound-data/make.py`: the hide clip through its tanh soft limiter 12 dB harder (was 3), the pick 9
dB (was none). Each clip's loudest 400 ms is now 5.9 and 7.0 dB under its peak (11.2 and 12.5
before). make.py was checked to reproduce the old WAVs exactly first, so only the drive changed.

DOSBox's output, `playsound.py N` with 3 s between, loudest 400 ms RMS (stereo averaged):

| Sound | Peak | RMS dBFS (before) | RMS dBFS now |
|---|---|---|---|
| 140 hide (mod) | 2,964 | -32.9 | -27.5 |
| 141 pick (mod) | 2,892 | -36.1 | -30.5 |
| 104 (game, fight) | 2,963 | -26.7 | -26.7 |
| 106 (game, fight) | 2,967 | -31.3 | -31.2 |
| 23 (game, fight) | 2,984 | -31.3 | -31.2 |

Both played twice, the same each time. The hide is now as loud as the game's loudest fight sound,
the pick between the fight sounds.
