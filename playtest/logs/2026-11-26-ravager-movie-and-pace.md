# The pointer in Ravager’s opening movies

In a DOSBox start using the real game files, the opening movie entered the FLI wait hook with the pointer at (160, 100). The Loader supplied ten pointer colours. A mouse click advanced the movie and incremented the helper’s accepted-click counter from zero to one. The relative-motion sample stayed at the centre, so it does not verify tracking.

Steady pace now wraps the native movement pass and redraw calls at file offsets 21AB6h and 21AFAh. Only the first three bytes of each far call are replaced. The relocated segment words are retained. The native movement list holds 320 records of ten bytes.

On the after-ambush save, three walk clicks increased the helper’s movement counter from 520 to 1,210. Combined redraws increased from 93 to 101. DSCLOG2 occupied 52,800 upper-memory bytes and the largest free upper-memory block was 102,656 bytes.
