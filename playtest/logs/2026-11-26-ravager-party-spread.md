# Party formation after loading Wake of the Ravager

Loaded the after-ambush save in DOSBox and read the game’s formation byte at DGROUP:13FA. It was 1 after returning to the map. DSCLOG2 occupied 50,928 bytes in upper memory, with a largest free block of 104,528 bytes.

The load and post-fight gather sites at file offsets 0x70DA6 and 0x6A823 clear the same formation byte. Site 221 preserves that write and requests the native spread command (0x6A6D1) on a map tick. In a separate DOSBox run with both patches skipped, the same save loaded with formation 0. Post-fight framing still needs a completed fight.

## Combat camera

The combatant step at 0x2008A loads the current figure’s map coordinates into SI and DI. Its two camera paths recentre near an edge or scroll by a step. Site 223 at 0x200B7 skips both when combat is active and the feet lie strictly inside the 320 by 200 viewport. The sequel keeps its existing handling for a figure on or outside the edge.

A 16-bit instruction check ran the assembled handler in combat and exploration for eight positions, including (0,100), (1,1), (319,199), (320,100), (10,200) and a negative x. All 16 returned to the expected game instruction with the stack balanced and the displaced read intact. A live fight is still needed to check the visual result.

The camera build loaded the same save in DOSBox. DSCLOG2 occupied 50,976 bytes and the largest free upper-memory block was 104,480 bytes. The map opened at (1080,1280).

The manual gather shares its final store with the two combat exits. Its call returns to 18C9:0ED6, while the combat exits return to 18C9:21C6 and 18C9:31A9 (segments relative to the game load). Only the combat exits request an automatic spread. A scripted gather during loading must preserve the pending load request. In DOSBox the after-ambush save returned to the map with formation 1, key 6 left it at 0, and key 5 restored it to 1.

Completed the opening Draxan fight on the map-controls branch. To shorten the encounter, the disposable test party had 200 HP each and the four hostile Draxans had 1 HP each. No edited state was saved. Across eight combatants, 76 consecutive sample pairs showed the active figure moving inside the viewport with the camera stationary. Gerakis dealt the finishing blow to each Draxan. After combat, the native fight-state word was zero and the formation byte was 1.
