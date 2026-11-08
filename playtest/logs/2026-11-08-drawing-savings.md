# DSCLOG's faster drawing: frame rate before and after (2026-11-08)

pens-after-arena, the whole party walking, `framerate.py 20`, from `2026-11-08-drawing-savings-runs.sh`:

```
before cycles 20000, all on, steady pace: 20.1 s: frames shown 10.3/s, undrawn (steady pace) 7.4/s, main loop 286/s; BIOS clock 18.0/s (18.2 = real time); game clock 95/s, steps run 69/s, lost while drawing 26/s (steady pace on only); walking 113 map units/s; DOSBox CPU 20%
before cycles 20000, all on, steady pace off: 20.1 s: frames shown 16.8/s, undrawn (steady pace) 0.0/s, main loop 114/s; BIOS clock 18.2/s (18.2 = real time); game clock 96/s, steps run 0/s, lost while drawing 0/s (steady pace on only); walking 81 map units/s; DOSBox CPU 21%
before cycles 35000, all on, steady pace: 20.2 s: frames shown 15.9/s, undrawn (steady pace) 1.6/s, main loop 387/s; BIOS clock 18.2/s (18.2 = real time); game clock 96/s, steps run 72/s, lost while drawing 24/s (steady pace on only); walking 112 map units/s; DOSBox CPU 29%
after cycles 20000, all on, steady pace: 20.2 s: frames shown 15.6/s, undrawn (steady pace) 3.3/s, main loop 259/s; BIOS clock 18.0/s (18.2 = real time); game clock 95/s, steps run 68/s, lost while drawing 26/s (steady pace on only); walking 112 map units/s; DOSBox CPU 20%
after cycles 20000, all on, steady pace off: 20.1 s: frames shown 18.9/s, undrawn (steady pace) 0.0/s, main loop 156/s; BIOS clock 18.0/s (18.2 = real time); game clock 95/s, steps run 0/s, lost while drawing 0/s (steady pace on only); walking 104 map units/s; DOSBox CPU 21%
after cycles 35000, all on, steady pace: 20.1 s: frames shown 18.9/s, undrawn (steady pace) 0.1/s, main loop 381/s; BIOS clock 18.2/s (18.2 = real time); game clock 96/s, steps run 81/s, lost while drawing 14/s (steady pace on only); walking 141 map units/s; DOSBox CPU 30%
before cycles 20000, all on, steady pace: 20.1 s: frames shown 10.1/s, undrawn (steady pace) 7.5/s, main loop 291/s; BIOS clock 18.2/s (18.2 = real time); game clock 96/s, steps run 70/s, lost while drawing 26/s (steady pace on only); walking 113 map units/s; DOSBox CPU 20%
before cycles 20000, all on, steady pace off: 20.0 s: frames shown 16.8/s, undrawn (steady pace) 0.0/s, main loop 114/s; BIOS clock 18.2/s (18.2 = real time); game clock 96/s, steps run 0/s, lost while drawing 0/s (steady pace on only); walking 80 map units/s; DOSBox CPU 21%
before cycles 35000, all on, steady pace: 20.0 s: frames shown 16.1/s, undrawn (steady pace) 1.6/s, main loop 388/s; BIOS clock 18.2/s (18.2 = real time); game clock 96/s, steps run 71/s, lost while drawing 25/s (steady pace on only); walking 114 map units/s; DOSBox CPU 29%
after cycles 20000, all on, steady pace: 20.2 s: frames shown 15.3/s, undrawn (steady pace) 3.6/s, main loop 270/s; BIOS clock 18.0/s (18.2 = real time); game clock 95/s, steps run 68/s, lost while drawing 25/s (steady pace on only); walking 112 map units/s; DOSBox CPU 21%
after cycles 20000, all on, steady pace off: 20.0 s: frames shown 18.9/s, undrawn (steady pace) 0.0/s, main loop 153/s; BIOS clock 18.0/s (18.2 = real time); game clock 95/s, steps run 0/s, lost while drawing 0/s (steady pace on only); walking 103 map units/s; DOSBox CPU 20%
after cycles 35000, all on, steady pace: 20.0 s: frames shown 18.9/s, undrawn (steady pace) 0.2/s, main loop 390/s; BIOS clock 18.2/s (18.2 = real time); game clock 96/s, steps run 81/s, lost while drawing 14/s (steady pace on only); walking 142 map units/s; DOSBox CPU 27%
RUNS-DONE
```

Screenshots afterwards: shadows and dust while walking looked as before; the dust cleared within a few seconds of stopping (DUST_NUDGE's rectangle); with the combat log panel up, the party walked beside it and nothing was drawn over it.
