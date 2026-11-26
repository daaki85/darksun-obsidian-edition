# Party formation after loading Wake of the Ravager

Loaded the after-ambush save in DOSBox and read the game’s formation byte at DGROUP:13FA. It was 1 after returning to the map. DSCLOG2 occupied 50,928 bytes in upper memory, with a largest free block of 104,528 bytes.

The load and post-fight gather sites at file offsets 0x70DA6 and 0x6A823 clear the same formation byte. Site 221 preserves that write and requests the native spread command (0x6A6D1) on a map tick. In a separate DOSBox run with both patches skipped, the same save loaded with formation 0. Post-fight framing still needs a completed fight.
