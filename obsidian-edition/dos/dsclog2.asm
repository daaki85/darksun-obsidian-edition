; DSCLOG2.EXE - the dice log helper for Wake of the Ravager (the Obsidian Edition's port).
;
; Wake of the Ravager runs on Shattered Lands' engine, recompiled with other addresses and record
; sizes, so the port of DSCLOG.EXE (dsclog.asm, Shattered Lands') is a helper of its own, built up
; feature by feature from DSCLOG's routines with the sequel's addresses (the port plan:
; reports/wake-of-the-ravager-port-plan.md in the repository). Each routine taken from dsclog.asm
; keeps its name there; what differs is said where it is.
;
; Now: the dice log's ring and rand() (the patched copy, DSUNLOG2.EXE, starts rand() at 5A22h with
; INT VEC_RAND, as DSUNLOG.EXE does at 5C22h: the same function, its seed at DS:384Ah, SL's 4122h),
; and DOS's file opens, so the game reads the Loader's copies of RESOURCE.GFF (D:\RESOURC2.GFF, with
; the spell records' fixes) and GPLDATA.GFF (D:\GPLDAT2.GFF, with the scripts' fixes:
; dsloader/ravager.py) in place of its own. Then the engine fixes ported in step 4 (each at its
; vector below), the spell slots on the USE screen (PROBE_USE, PROBE_WIN: the Loader's lines) and
; the charges in item boxes (PROBE_ITEM_BOX), THAC0, saves and thief skills on the inventory
; (PROBE_CHAR).
;
; The header keeps DSCLOG's layout for the fields the Loader's dice log reads (the ring, the seed,
; the filters, the far block), under a signature of its own, so a Loader that doesn't know the
; sequel never takes it for Shattered Lands'.
;
; Build: nasm -f bin -o dos/DSCLOG2.EXE dos/dsclog2.asm

BITS 16
CPU 386
%include "save_bands.inc"       ; (SAVE_BASE's code and tables, DSCLOG's too)
%include "shared_routines.inc"  ; (the routines both helpers have the same: SHARED_name)

VEC_RAND equ 0x60       ; rand() (DSUNLOG2.EXE: INT 60h at the start of rand(), 5A22h)
VEC_SAVE equ 0x61       ; PROBE_SAVE (DSUNLOG2.EXE: INT 61h at the saving throw's end, 66EA6h)
VEC_AC   equ 0x62       ; PROBE_AC (DSUNLOG2.EXE: INT 62h at the AC function's end, 5D6E6h)
VEC_PIC_FULL  equ 0xC0  ; PIC_FULL  (2A5E7h: the picture cache's 300 slots taken)
VEC_PIC_PLACE equ 0xC1  ; PIC_PLACE (2A6FDh: a reused slot's place in the store)
VEC_PIC_COUNT equ 0xC2  ; PIC_COUNT (2A75Ch: the slot's number, the count raised for a new one)
VEC_PIC_FAIL  equ 0xC3  ; PIC_FAIL  (2A58Eh: no picture loaded)
VEC_REAR      equ 0xC4  ; MISSILE_REAR (5C99Fh: an attack's "from behind" pushed for the AC function)
VEC_REST_POISON equ 0xC5 ; REST_POISON (8D02Dh: the rest's test for the Poisoned, after the free cures)
VEC_NPP       equ 0xC6  ; NPP_SAVE (84DDAh: Negative Plane Protection's save, against an undead's touch)
VEC_ACID_ROUNDS equ 0xC7 ; ACID_ROUNDS (7FAA6h: an effect added, Acid's time made rounds as charges)
VEC_ACID_BURN   equ 0xC8 ; ACID_BURN (82BF3h: Acid's burn starting)
VEC_ACID_ONCE   equ 0xC9 ; ACID_ONCE (651FEh: a spell's damage putting its effect on: none from a burn)
VEC_ACID_USE    equ 0xCA ; ACID_USE (7FD99h: an effect's charges spent: Acid's only from ACID_ROUND)
VEC_ACID_ROUND  equ 0xCB ; ACID_ROUND (5B592h: a round starting: each creature's Acid burns)
VEC_IMAGE     equ 0xCC  ; IMAGE_SPELL (84BF8h: an image taking a spell: only a foe's)
VEC_BLOW      equ 0xCD  ; IMAGE_BLOW (5D09Fh: an attack's hit: an image may take it)
VEC_USE       equ 0xCE  ; PROBE_USE (79543h: the USE screen's LEVEL button labelled: its spell slots drawn)
VEC_WIN       equ 0xCF  ; PROBE_WIN (303BEh: a window brought to the front: the USE screen's slots again)
VEC_ITEM_BOX  equ 0xD0  ; PROBE_ITEM_BOX (9A4FEh: an item's box filled: its charges, or a weapon's material)
VEC_CHAR      equ 0xD1  ; PROBE_CHAR (91286h: the inventory panel's lines: THAC0, saves, thief skills)
VEC_CAST      equ 0xD2  ; PROBE_CAST (80585h: a spell or power cast, its caster read: recorded)
VEC_SCROLL    equ 0xD3  ; PROBE_SCROLL (20230h: the map's main loop asking where the pointer is: LABEL_TICK)
VEC_TICK      equ 0xD4  ; PROBE_TICK (3DA2Ch: the game's timer: LABEL_STAMP)
VEC_FLIP      equ 0xD5  ; FLIP_SITE (16974h: the game's flip of its two screens: the panel on the new one)
VEC_POINTER   equ 0xD6  ; PROBE_POINTER (3326Ah: the game's pointer drawn: the panel put first)
VEC_CENTRE    equ 0xD7  ; PROBE_CENTRE (21A5Ah: the view centred: drawn again at once while the panel is shown)
VEC_LOOK      equ 0xDA  ; PROBE_LOOK (640FBh: the Look box's first rows drawn: the monster's defences)
VEC_VIEW      equ 0xD9  ; PROBE_VIEW (987FBh: View Character's panels drawn: the saves, MOVE and THAC0)
VEC_HELM_AC   equ 0xDD  ; PROBE_HELM_AC (5D663h, 5D67Bh: a worn item's type's AC read: a Helm's 1 with RULE_HELMS)
VEC_BOX_AC    equ 0xDE  ; PROBE_BOX_AC (9A4B7h: the item box's AC BONUS: the same)
VEC_HELD_HIT  equ 0xDF  ; HELD_HIT (5D088h: the natural 20's test: a helpless target hit too)
VEC_HELD_DAMAGE equ 0xE0 ; HELD_DAMAGE (5D1B7h: a helpless target's damage, not doubled)
VEC_TWO       equ 0xE1  ; PROBE_TWO (5DE7Ch: the two-weapon to-hit adjustment: AD&D's -2/-4 with RULE_TWO_WEAPONS)
VEC_ROLL_MAX  equ 0xE3  ; ROLL_MAX_HP (9506Ch: a fix: the most hit points worked out again after a hit die, as SL's)
VEC_CAH_TWO   equ 0xE5  ; CAH_TWO (5DE6Fh: the two-weapon routine on for the cahulaks, RULE_HI_CAHULAKS)
VEC_CAH_SWING equ 0xE6  ; CAH_SWING (5D052h: a swing's start: the off head's more)
VEC_CAH_HIT   equ 0xE7  ; CAH_HIT (5D1FEh: a weapon's hit has done damage: the cahulaks' tangle)
VEC_CAH_MOVE  equ 0xE8  ; CAH_MOVE (5B838h: a creature's turn starts: a tangled one's taken)
VEC_REACH     equ 0xE9  ; REACH (25CDDh: the combatant distance routine's result: a polearm's two squares)
VEC_RANGER_LEVEL equ 0xEA ; RANGER_LEVEL (629F0h: a class's level for a spell's duration and damage: a ranger's 7 less)
VEC_ENL_ROLL  equ 0xEB  ; ENL_ROLL (5D0C8h: a weapon's damage rolled: its dice kept for Enlarge)
VEC_ENL_SITE  equ 0xEC  ; ENL_SITE (863E7h: Enlarge's x(100 + 10 a level)%: the weapon's dice only)
VEC_SCROLL_LEARN equ 0xED ; SCROLL_LEARN (99A2Fh: whether a scroll's spell is known: INT's chance and most)
VEC_LEARN_SAID equ 0xEE  ; LEARN_SAID (99A7Fh: YOU LEARN THE SPELL: a failed try taken back)
VEC_LEARN_REFUSED equ 0xEF ; LEARN_REFUSED (99A86h: YOU ALREADY KNOW THIS SPELL: a full level's message)
VEC_PICK_ANY  equ 0xF0  ; PICK_ANY (9317Fh: a preserver's level up: CHOOSE A SPELL only with a spell its INT has room for)
VEC_PICK_PAGE equ 0xF2  ; PICK_PAGE (93487h: CHOOSE A SPELL's first page: the highest level with room)
VEC_BLUR_SAVE equ 0xF3  ; BLUR_SAVE (8373Ah: Barkskin's +1 on saves, and Blur's)
VEC_FSHIELD_SAVE equ 0xF4 ; FSHIELD_SAVE (837F7h: Protection from Cold's +3, and Fire Shield's +2)
VEC_SITE      equ 0xF5  ; SITE: INT F5h + a byte, the site's number (SITE_TABLE)
VEC_PICK_LIST equ 0xF1  ; PICK_LIST (93246h: CHOOSE A SPELL's page: none of a level the reader's INT has full)
VEC_TWO_HANDED equ 0xE4 ; TWO_HANDED (77976h, 77A0Dh: an item type's two-handed bit in the inventory: not a half-giant's with RULE_HALF_GIANT)
VEC_OFF_HAND  equ 0xE2  ; OFF_HAND (5CEE8h: the attacks a round stored: one in the off hand with RULE_TWO_WEAPONS)
VEC_HP_BEST   equ 0xDC  ; PROBE_HP_BEST (95025h: a level's hit die rolled: twice with RULE_HP_BEST, the better kept)
VEC_CR_HP     equ 0xDB  ; PROBE_CR_HP (6B84Ch, 6BC62h, 6D6AEh, 6B79Ch: the creation screen's hit points drawn: its THAC0)
VEC_FOLLOW    equ 0xD8  ; PROBE_FOLLOW (1E3ECh, 20193h, 2143Eh: the view moved after a figure: the same)
SEED     equ 0x384A     ; DS: the game's 32-bit rand seed (SL's 4122h)
TARGET   equ 0x4206     ; DS word: the combatant the current attack is at (SL's 494Ah, TARGET_GLOBAL)

NENT    equ 63          ; entries in the ring (as DSCLOG's)
ESIZE   equ 192         ; bytes per entry (DSCLOG's ENTRY LAYOUT)
TSIZE   equ 2048        ; the text buffer's size (DSCLOG's: a power of two), in the far block (FAR_TBUF)
STACK   equ 256         ; bytes of stack while installing
HDR_SIZE equ 1872       ; DSCLOG's header to its last field (dicelog.py's TSR_ offsets end at +1867)

; ---- MZ header: no relocations, and only as much memory as the image needs (as DSCLOG's) ----
; The image is three parts, each a section of its own that starts its labels at 0 (THE IMAGE'S PARTS,
; at the end): the segment (IMAGE: the header and all the code that stays, reached through CS), the
; tail (TAIL: tables and buffers that stay, outside the segment, TAIL_PARAS paragraphs on) and the
; install (INSTALL: its code and data, not kept, INSTALL_PARAS paragraphs on: DOS starts it there, the
; header's CS:IP). Only the segment has to fit 64 KB (tests/test_dsclog2_room.py keeps a margin).
section mz start=0
        db 'MZ'
        dw file_len % 512                       ; bytes in the last page
        dw (file_len + 511) / 512               ; pages
        dw 0                                    ; relocations
        dw 2                                    ; header size in paragraphs
        dw LOAD_EXTRA                           ; min extra paragraphs
        dw LOAD_EXTRA                           ; max extra paragraphs (so the whole fits in upper memory)
        dw image_len / 16                       ; SS (relative to the image): just past it
        dw STACK                                ; SP
        dw 0                                    ; checksum
        dw install                              ; IP (in the install's own segment)
        dw INSTALL_PARAS                        ; CS (relative to the image): the install's
        dw 0x1C                                 ; relocation table offset
        dw 0                                    ; overlay
        align 32, db 0

section image follows=mz vstart=0
section tail follows=image vstart=0 align=16           ; (the tail's tables, with their values)
tail_start:
tail_sig db 'DSCLOG2 TAIL', 0, 0, 0, 0  ; (so that nothing of the Loader's is at the tail's offset 0)
NAMES_ROOM  equ 160                 ; (ITEM_NAMES: SITE_NAME's)
NAME_KEPT   equ 16                  ; (each: 15 letters at most and a NUL, as DSCLOG's EXTRA_NAMES)
item_names times NAMES_ROOM * NAME_KEPT db 0    ; (first in the tail, zeros in the file though buffers, with
; LBL_SLOTS after: the emulator tests' way back, a HLT at CS:FFF0, lands in them, not in a table, as in DSCLOG)
LBL_SLOTS  equ 4                    ; (LABELS': a slot for each label the Loader writes)
LBL_ROW    equ 16
LBL_H_MOST equ 11
LBL_MASK   equ LBL_ROW * LBL_H_MOST
LBL_SIZE   equ 8 + 2 * LBL_MASK
lbl_slots times LBL_SLOTS * LBL_SIZE db 0 ; (the Loader's: LABELS, the header's +1834:+1838)
tail_tables:
section tailz follows=tail vfollows=tail align=16     ; (then its buffers, zeros in the file: the same segment)
tailz_start:
section install follows=tailz vstart=0 align=16
section image

; ---- header, found by the Loader via SIG (16-byte aligned): DSCLOG's layout and length ----
hdr:
sig      db 'DSCLOGR1'          ; +0   (Wake of the Ravager's helper, its first header)
seq      dw 0                   ; +8   entries written so far (wraps at 65536)
widx     dw 0                   ; +10  ring slot the next entry goes to
nent     dw NENT                ; +12
esize    dw ESIZE               ; +14
ring_off dw FAR_RING            ; +16  offset of the ring in RING_SEG's segment (the far block's)
stub_off dw stub                ; +18  offset of STUB in this segment
hdr_off  dw hdr                 ; +20  offset of this header in this segment
seed_off dw SEED                ; +22  DS offset of the game's 32-bit rand seed
glob     dw TARGET, 0, 0        ; +24  DS offsets of 3 game words to capture (0 = none): the attack's
                                ;      target first, as the Loader's dice log has DSCLOG's (TARGET_GLOBAL)
hdr_len  dw hdr_end - hdr       ; +30  the header's length: the Loader writes no word of it past +2012 at or
                                ;      beyond this (an older helper has a 0 here, the fourth capture's
                                ;      none: its code may lie where a later header's words are)
nfilt    dw NFILT               ; +32  number of filters in use (0 = record every call)
filt:                           ; +34  DSCLOG's filters: the calling code a roll starts with
        db 7, 0x66,0x0F,0xBF,0xC0,0x66,0x6B,0xC0, 0     ; imul eax,eax,imm8
        db 7, 0x66,0x0F,0xBF,0xC0,0x66,0x69,0xC0, 0     ; imul eax,eax,imm32
        db 7, 0x66,0x0F,0xBF,0xC0,0x66,0xC1,0xE0, 0     ; shl eax,n
        db 8, 0x66,0x0F,0xBF,0xC0,0x66,0x0F,0xBF,0x56   ; N = word [bp+x] (the dice routines)
        db 8, 0xBB,0x64,0x00,0x99,0xF7,0xFB,0x3B,0x56   ; percentile check
NFILT   equ ($ - filt) / 9
        times (8 - NFILT) * 9 db 0
skipped  dw 0                   ; +106 calls not recorded because no filter matched
probe_save_off dw probe_save    ; +108 offset of PROBE_SAVE in this segment
probe_ac_off   dw probe_ac      ; +110 offset of PROBE_AC in this segment
vectors  db VEC_RAND, VEC_SAVE, VEC_AC, 0, 0 ; +112 the interrupts the patched game uses
hooked   db 0                   ; +117 1 once the vectors are ours
int_rand_off dw int_rand        ; +118 offset of INT_RAND (VEC_RAND's handler) in this segment
gpl_hook_off dw 0               ; +120 (none yet)
gpl_chain dd 0                  ; +122
tpos     dw 0                   ; +126 the text buffer's write position (wrapping at TSIZE): DSCLOG's TEXT
tbuf_off dw FAR_TBUF            ; +128 offset of the text buffer in the far block (TBUF_SEG's)
tsize    dw TSIZE               ; +130
probe_text_off dw probe_text    ; +132 offset of PROBE_TEXT in this segment (site 93)
probe_msg_off dw probe_msg      ; +134 offset of PROBE_MSG in this segment (site 94)
probe_char_off dw 0             ; +136
tbuf_seg  dw 0                  ; +138 the text buffer's segment: the far block's (FAR_SEG), set as it loads
panel_off dw FAR_PANEL          ; +140 the panel's picture's offset in the far block (PANEL_BLIT)
far_seg   dw 0                  ; +142 the far block's segment (FAR_INIT): its buffers from FAR_RING on
vec_table dw all_vectors        ; +144 where ALL_VECTORS is in the install (its segment: the EXE header's CS)
copied    dw 0                  ; +146 bits: 1 the Loader's RESOURCE.GFF copy opened, 2 its GPLDATA.GFF, 4 its OBJEX.GFF, 8 its RGN03A.GFF, 16 its RGN001.GFF, 32 its RGN033.GFF, 64 its RGN03D.GFF, 128 its RGN03E.GFF, 256 its RGN038.GFF
slots_off dw slots_text         ; +148 offset of SLOTS_TEXT in the tail (+1834's): 4 x SLOTS_SIZE bytes, one a party member,
                                ;      written by the Loader (DSCLOG's: dicelog.DiceLog._write_slots)
look_seq   dw 0                 ; +150 monsters looked at in a fight (PROBE_LOOK counts them)
look_reply dw 0                 ; +152 the Loader sets this to LOOK_SEQ once LOOK_TEXT is ready
look_who   dw 0                 ; +154 the combatant looked at
look_off   dw look_text         ; +156 offset of LOOK_TEXT: up to 3 short lines for the Look box, "|"
                                ;      between them (a first byte 1: beside LEVEL), written by the Loader
look_full_off dw look_full      ; +158 offset of LOOK_FULL in the tail (+1834's): the whole description, shown in the dialogue
                                ;      window as the Look box closes (UNLOOK), written by the Loader
look_on    dw 0                 ; +160 the Loader sets 1 to have monsters described
        times 164 - ($ - hdr) db 0  ; (DSCLOG's fields +162 to +163: none of them here yet, zero)
stats_stamp dw 0                ; +164 the BIOS timer when the Loader last passed (RavDiceLog): older
                                ;      than STATS_FRESH, the panel is taken off
        times 170 - ($ - hdr) db 0  ; (DSCLOG's fields +166 to +169: none of them here yet, zero)
rules      dw 0                 ; +170 the rule changes the Loader turns on, as DSCLOG's (RULE_HP_BEST, ...;
                                ;      the Loader writes only the ported ones: ravager.RULES_PORTED)
        times 196 - ($ - hdr) db 0  ; (DSCLOG's fields +172 to +195: none of them here yet, zero)
names_off  dw item_names        ; +196 offset of ITEM_NAMES in the tail (+1834's): the item names past the
names_count dw NAMES_ROOM       ; +198   game's 256 (as DSCLOG's EXTRA_NAMES), NAME_KEPT bytes each,
                                ;        written by the Loader (dsloader/ravager.item_names)
        times 204 - ($ - hdr) db 0  ; (DSCLOG's fields +200 to +203: none of them here yet, zero)
stealth    dw 0                 ; +204 the Loader sets bit N when party member N is hidden and unheard
                                ;      (RULE_STEALTH, stealth.py): their next attack is from behind
stealth_used dw 0               ; +206 counted up each time one is (the bit cleared: MISSILE_REAR)
        times 228 - ($ - hdr) db 0  ; (DSCLOG's fields +208 to +227: none of them here yet, zero)
scroll_on  dw SCROLL_MIDDLE     ; +228 as DSCLOG's: SCROLL_MIDDLE has a drag with the wheel pressed scroll
                                ;      the map (SCROLLING; on from the start: the Loader writes nothing)
pan_x      dw 0                 ; +230 the Loader adds to these (wrapping) to scroll the view by as many
pan_y      dw 0                 ; +232   pixels, as DSCLOG's (to the enemy chosen with Tab: PAN_TICK)
        times 238 - ($ - hdr) db 0  ; (DSCLOG's fields +234 to +237: none of them here yet, zero)
dac_off  dw FAR_DAC             ; +238 offset of DAC in the far block: the palette as last read (DAC_TICK),
                                ;      768 values 0-63, for the colours of the Loader's labels and panel
dac_changes dw 0                ; +240 (DSCLOG2's own) counted up when DAC_TICK finds the palette changed:
                                ;      the Loader draws its panel again in it (DSCLOG's DARK count)
        times 244 - ($ - hdr) db 0  ; (DSCLOG's fields +242 to +243: none of them here yet, zero)
rings_on   dw 0                 ; +244 the Loader sets 1 to have a ring drawn under the enemy chosen with
                                ;      Tab (RINGS: HIT_TARGET's), once RED is made
ring_tab_off dw FAR_RING_TAB    ; +246 offset of RING_TAB in the far block: a byte a thing, the kind of
                                ;      ring under it (1: two pixels thick, tinted twice; 0 none), the
                                ;      Loader's (usable.py: what can be used, while Alt is held)
red_off    dw FAR_RED           ; +248 offset of RED in the far block: each colour's reddened one (0:
                                ;      none), the Loader's (rings.red_table)
target_on  dw 0                 ; +250 the Loader sets 1 while Tab chooses an enemy (TARGETING)
tab_seq    dw 0                 ; +252 Tab pressed (counted) ...
back_seq   dw 0                 ; +254 ... and Shift+Tab
hit_target dw 0xFFFF            ; +256 the enemy chosen (the Loader sets it; FFFFh: none)
attack_seq dw 0                 ; +258 Enter pressed on it (counted)
main_ticks dw 0                 ; +260 passes of the map's main loop (PROBE_SCROLL), as DSCLOG's: the Loader
                                ;      sees the loop running by it (quicksave.py)
        times 268 - ($ - hdr) db 0  ; (DSCLOG's fields +262 to +267: none of them here yet, zero)
ring_seg dw 0                   ; +268 the ring's segment: the far block's (FAR_SEG), as DSCLOG's
rules_hi   dw 0                 ; +270 the rules' second word, as DSCLOG's
learn_seq  dw 0                 ; +272 a wizard's try at a scroll's spell (INT_LEARN), counted ...
learn_who  db 0                 ; +274 ... the party member ...
learn_spell db 0                ; +275 ... the spell ...
learn_int  db 0                 ; +276 ... its INT ...
learn_chance db 0               ; +277 ... the chance to learn (%) ...
learn_roll db 0                 ; +278 ... the d100 (LEARN_FULL: the spells of that level known) ...
learn_result db 0               ; +279 ... and LEARN_LEARNT, LEARN_FAILED or LEARN_FULL (DSCLOG's)
rl_seq     dw 0                 ; +280 an ability's 4d4 rolled on the creation screen (RL_TRY), counted
rl_tries   times 24 db 0        ; +282 the last four 4d4 of each ability, STR to CHA (DSCLOG's: the dice
                                ;      log's, as the die tumbles faster than its ring is read)
        times 326 - ($ - hdr) db 0  ; (DSCLOG's fields +306 to +325: none of them here yet, zero)
panel_on   dw 0                 ; +326 the Loader sets 1 to have the combat log's panel drawn
panel_seg  dw 0                 ; +328 the panel's picture's segment: the far block's (PANEL_W x
                                ;      PANEL_H_MOST, each row its planes in turn: combatlog.planar)
panel_new  dw 0                 ; +330 the Loader sets 1 once it has put a new picture there
panel_mx   dw 0                 ; +332 the pointer, as the game's main loop last asked (game pixels): x,
panel_my   dw 0                 ; +334   y
panel_held dw 0                 ; +336 1 while the left button pressed on the panel is held
panel_hits dw 0                 ; +338 the presses on the panel, counted, and where the last was: x,
panel_hx   dw 0                 ; +340
panel_hy   dw 0                 ; +342   y
panel_top  dw PANEL_Y0          ; +344 the Loader's: the panel's top on the screen and its height
panel_rows dw PANEL_H           ; +346   (at most PANEL_H_MOST), set before PANEL_NEW
panel_keys dw 0                 ; +348 L pressed on the map with the panel shown (or to open it), counted
kit_outdoors db 0               ; +350 the Loader sets bit N while party member N stands under the open
                                ;      sky (stealth.daylight: the Military Scout's to hit, skills and
                                ;      initiative; KITS)
kit_dance  times 4 db 0         ; +351 each party member's Battle Dancer's dance, the Loader's (dance.py):
                                ;      +1 danced well, -1 stumbled, 0 none; to hit, damage and AC
kit_wild   db 0                 ; +355 Wild Fighting, the Loader's (wild.py): bit N party member N fights
                                ;      wild (3 worse to hit, AC 3 worse), bit N + 4 its check passed too
                                ;      (1 more attack a round in melee, 3 more damage)
tick_off   dw ticks             ; +356 offset of TICKS in the tail (TAIL_SEG), as DSCLOG's: where the game was
                                ;      as its timer struck (PROBE_TICK), TICK_SLOTS records of TICK_SIZE bytes
tick_seq   dw 0                 ; +358 records taken, counted: the newest in slot (TICK_SEQ - 1) mod TICK_SLOTS
                                ;      (the Loader's freeze report, freeze.py)
        times 1814 - ($ - hdr) db 0 ; (DSCLOG's fields +360 to +1813: none of them here yet, zero)
blast_hp   times 4 dw 0         ; +1814 the hit points Psionic Blast took from each party member this fight
                                ;      (BLAST_LOSS), for the Loader to give back and clear as the fight
                                ;      ends (psiblast.py); while one is owed, BLAST_KO knocks out
        times 1830 - ($ - hdr) db 0 ; (DSCLOG's fields +1822 to +1829: none of them here yet, zero)
gear_due   db 0                 ; +1830 a new character just made (GEAR_DONE, at DONE): the Loader gives its
                                ;      starting gear (startgear.py), then clears it (DSCLOG's GEAR_DUE)
gear_given db 0                 ; +1831 ... bit N: party member N's items changed by it (DSCLOG's GEAR_GIVEN)
        times 1834 - ($ - hdr) db 0 ; (DSCLOG's fields +1832 to +1833: none of them here yet, zero)
tail_seg dw 0                   ; +1834 the tail's segment, as DSCLOG's (TAIL: the tables and buffers kept
tail_paras dw TAIL_PARAS        ; +1836   outside this segment), set as it loads: this one's + TAIL_PARAS
lbl_off  dw lbl_slots           ; +1838 offset of LBL_SLOTS there: the Loader's names over figures (labels.py)
big_off  dw 0                   ; +1840 (DSCLOG's BIG, the cahulaks' too-big list: none here, the Loader's LARGE_BITS serve)
large_off dw large_bits         ; +1842 offset of LARGE_BITS there: the Loader's, a bit per combatant large or bigger
                                ;      (sizes.Large, by name and race: the creature size rule, IS_LARGE)
        times 1846 - ($ - hdr) db 0 ; (DSCLOG's +1844, LOCK_BARRED's offset: none here, zero)
loot_seq   dw 0                 ; +1846 T or Shift+T read with a container's window open, counted (LOOT_KEY,
                                ;      DSCLOG's): the Loader takes what is in it (loot.py)
loot_thing dw 0xFFFF            ; +1848 ... the container's map thing (the game's DS:05D6h then); FFFFh again
                                ;      once the Loader has taken it (none pending)
loot_mode  dw 0                 ; +1850 ... 0 T: everything; 1 Shift+T: all but plain weapons
sell_seq   dw 0                 ; +1852 S read on a shop's screen, counted (SELL_KEY, DSCLOG's): the Loader
                                ;      sells the plain gear in the backpack of ...
sell_member dw 0                ; +1854 ... the party member on show then (selector 370h:0B44h) ...
sell_merchant dw 0              ; +1856 ... to the shop's merchant (DS:1A30h)
shop_at    dw 0                 ; +1858 the BIOS tick of the shop's loop's last pass (SHOP_LOOP)
        times 1862 - ($ - hdr) db 0 ; (DSCLOG's fields +1860 to +1861: none of them here yet, zero)
bad_luck db 0                   ; +1862 a Swashbuckler's bad luck as KIT_SKILL last rolled it (0-25) ...
bad_luck_who dw 0               ; +1863 ... and whose (the creature), for the dice log (kits.TSR_BAD_LUCK)
loader_beat dw 0                ; +1865 the BIOS timer at the Loader's last pass (DSCLOG's LOADER_BEAT): GEAR_DONE
                                ;      waits for the Loader only while it is fresh
gear_who   db 0xFF              ; +1867 the sheet index of the character DONE just made (DSCLOG's GEAR_WHO)
        times HDR_SIZE - ($ - hdr) db 0  ; (the rest of DSCLOG's header, to its last field: zero, so
                                ;   whatever the Loader reads of it is a defined 0, never this helper's code)
wall_shadows dw 1               ; +1872 (DSCLOG2's own, past DSCLOG's header) 1: the walls cast shadows on
                                ;      the floor (WALL SHADOWS)
wall_passes  dw 0               ; +1874 floor passes shadowed (counted)
dark_builds  dw 0               ; +1876 times DARK was made
attack_clicks dw 0              ; +1878 Enter's clicks given on the chosen enemy (TARGETING, counted)
hit_answers  dw 0               ; +1880 the finder's answers made the chosen enemy (PROBE_HIT, counted)
ring_draws   dw 0               ; +1882 rings drawn into the floor (RINGS, counted)
sell_done    dw 0               ; +1884 the Loader's: SELL_SEQ as it last saw to it (sold, or nothing to
                                ;      sell): SHOP_LOOP holds the shut shop's way back to its talk till then
        times 1904 - ($ - hdr) db 0 ; (+1886 to +1903: none yet, zero. DSCLOG's quick save fields are at
                                ;   +1878 to +1889 there, where this header has others: here they follow)
qs_keys    dw 0xFFFF, 0xFFFF    ; +1904 the Loader's: the quick save key and the quick load key, as INT 16h
                                ;      gives them (FFFFh: none), taken on the map (QS_KEY) ...
qs_seq     dw 0, 0              ; +1908 ... and counted, each in its word: the Loader acts (DSCLOG's +1878, +1882)
save_req   dw 0                 ; +1912 the Loader sets 1 to have the game saved from the map's main loop
                                ;      (SAVE_TICK: the file and the name in SAVE_TEXT), 2 to have the game's
                                ;      LOAD window opened; 0 while DSCLOG2 is at it, then 3 done, 4 the game's
                                ;      save failed, 5 not in a fight (DSCLOG's +1886)
save_off   dw save_text         ; +1914 offset of SAVE_TEXT in the tail (+1834's): the Loader's: the save's
                                ;      file (SAVE_FILE bytes with its NUL), then its name (DSCLOG's +1888)
save_greq  dw 0                 ; +1916 the Loader's, with a save's request: the number of the save's GREQ
                                ;      chunk (the map's limits, kept in the roster file: GREQ_WRITE), 0 none
greq_saves dw 0                 ; +1918 GREQ chunks written (GREQ_WRITE, counted) ...
greq_loads dw 0                 ; +1920 ... and a load's taken from the quick saves' (GREQ_LOAD, counted)
view_redraw dw 0                ; +1922 the Loader sets 1 to have the view drawn again, all of it, from the map's
                                ;      main loop (REDRAW_TICK; DSCLOG's VIEW_REDRAW, its +242)
squares_on dw 0                 ; +1924 the Loader sets 1 to have the squares SQ_MAP marks drawn on the floor
                                ;      (SQUARES: where the party member whose turn it is in a fight can still
                                ;      walk, squares.py; DSCLOG's +1890). SQ_MAP is in this helper's PSP
light_off  dw FAR_LIGHT         ; +1926 offset of LIGHT in the far block: each colour's lighter one (0: none),
                                ;      the Loader's (dust.light_table; DSCLOG's +236)
square_draws dw 0               ; +1928 floor passes the squares were drawn in (SQUARES, counted)
f10_moves  dw 0                 ; +1930 F10's moves taken back (F10_PIN, counted) ...
f10_kept   dw 0                 ; +1932 ... and those refused to a pinned member (counted)
mark_draws dw 0                 ; +1934 rings drawn under the things RING_TAB marks (RINGS, counted)
        times 1960 - ($ - hdr) db 0 ; (+1936 to +1959: none yet, zero; kept free for the open ports' fields)
fig_shadows dw 1                ; +1960 1: the figures cast shadows on the floor (FIGURE SHADOWS; 0 none)
fig_passes  dw 0                ; +1962 floor passes the figures' shadows were drawn in (counted) ...
fig_drawn   dw 0                ; +1964 ... and shadows cast in them (counted) ...
fig_wides   dw 0                ; +1966 ... and redrawn rectangles widened for them (FIG_WIDE, FIG_WIDE_ALL)
fig_kept    dw 0                ; +1968 frames' shadows kept as the game drew them (FIG_KEEP, site 162) ...
fig_from_kept dw 0              ; +1970 ... and shadows cast from them, the picture out of memory (FIG_OF)
dust_on     dw 0                ; +1972 the Loader sets 1 once LIGHT is made, to have walkers raise dust (DUST)
dust_puffs  dw 0                ; +1974 puffs of dust raised (counted)
dust_sig    dw 0x7544           ; +1976 DUST's signature: the Loader writes DUST_ON only where it finds it
fig_other   dw 0                ; +1978 shadows cast from another kept frame of the picture (FIG_OF) ...
fig_missed  dw 0                ; +1980 ... and figures that cast none, their picture out with none kept
shine_turns dw 0                ; +1982 the colour cycles turned on a shop's screen (SHINE_TURN, counted)
ghost_seg   dw 0                ; +1984 GHOST's block in upper memory (its pixels and spans; 0: none, no see-through)
ghost_on    dw 0                ; +1986 the Loader sets 1 once BLEND and REP are made for the palette
ghost_blend dw FAR_GH_BLEND     ; +1988 BLEND's offset in the far block (REP_COUNT x 256 bytes) ...
ghost_rep   dw FAR_GH_REP       ; +1990 ... REP's (256) ...
ghost_tab   dw FAR_GH_TAB       ; +1992 ... and GHOST_TAB's (80: a bit a thing; +79 GH_CHANGED)
ghost_draws dw 0                ; +1994 figures drawn see-through (GHOST_DRAW, counted)
        times 2000 - ($ - hdr) db 0 ; (+1936 to +1999: none here yet, zero)
pick_on    dw 0                 ; +2000 the Loader sets PICK_BUTTON (2) to have a thief's Pick Pockets button on
                                ;      the USE screen (PICK POCKETS; DSCLOG's PICK_ON, its +178)
pick_seq   dw 0                 ; +2002 a pocket to pick: someone clicked on with the thief's pointer, counted
                                ;      (PP_HAND; DSCLOG's USE_SEQ, its +180) ...
pick_reply dw 0                 ; +2004 ... the Loader sets this to PICK_SEQ once it has answered (USE_REPLY)
pick_who   dw 0                 ; +2006 ... the thing clicked on (the map's object: a creature's, the
                                ;      combatants' 388h:0C33h kind 2) (USE_WHO)
pick_thief dw 0                 ; +2008 ... the thief: the party member whose button it was
pick_taken dw 0                 ; +2010 the Loader's: 1 it tried the pocket (PICK_TEXT shown, no talk), 0 the
                                ;      talk as the game has it (USE_TAKEN)
pick_off   dw pick_text         ; +2012 offset of PICK_TEXT: what came of it, NUL-terminated, the Loader's
                                ;      (PICK_SIZE bytes; DSCLOG's PICK_OFF, its +176)
pick_shown dw 0                 ; +2014 purses shown on the USE screen (PP_SHOW, counted) ...
pick_armed dw 0                 ; +2016 ... picks readied, the pointer the one for talking (PP_ARM) ...
pick_late  dw 0                 ; +2018 ... and picks the Loader didn't answer in time (PP_HAND: the talk)
sf_swings  dw 0                 ; +2020 lotulis or double spear specialists' last swings turned on a second
                                ;      foe (SF_SWING, counted) ...
sf_lesses  dw 0                 ; +2022 ... the double spear's of them done 1 less (SF_LESS, counted) ...
sf_backs   dw 0                 ; +2024 ... and the first targets put back as the round ended (SF_BACK)
trip_saves dw 0                 ; +2026 a trikal specialist's hits that asked a save against paralysis ...
trips      dw 0                 ; +2028 ... and the targets tripped (CAH_HIT, counted)
        times 2060 - ($ - hdr) db 0  ; (+2030 to +2059: this block's, free)
cosmos_more dw 0xFFFF, 0xFFFF   ; +2060 two spells more a Healer's cleric casts as the sphere of the cosmos's
                                ;      (HEALER_COSMOS), FFFFh none: for Whirlwind and Restore Youth, their
                                ;      sequel numbers once those spells are ported (kits.RAV_COSMOS_MORE)
kc_levels  dw 0                 ; +2064 spells' levels a kit changed (KIT_CAST_LEVEL, counted) ...
kc_cures   dw 0                 ; +2066 ... cures it made stronger (KIT_CURE) ...
kc_causes  dw 0                 ; +2068 ... Cause Wounds stronger (AV_CAUSE) ...
kc_cosmos  dw 0                 ; +2070 ... the cosmos's spells a Healer was let cast (HEALER_COSMOS) ...
kc_barred  dw 0                 ; +2072 ... spells a kit never knows refused (KIT_BARS) ...
kc_cells   dw 0                 ; +2074 ... Cell Adjustments it made stronger (CELL_MORE)
        times 2076 - ($ - hdr) db 0 ; (none: +2076 follows +2075)
learn_read db 0                 ; +2076 a Shinobi's try at a scroll (LEARN_SEQ): the d100 to read it ...
learn_read_chance db 0          ; +2077 ... and its chance (SH_ROLLS: DSCLOG's +366 and +367)
learn_spell_hi db 0             ; +2078 LEARN_SPELL's high byte (a new spell's, 320-325: a Shinobi's tries)
        db 0                    ; +2079 (none)
sh_levels_n dw 0                ; +2080 casting levels made a Shinobi's (SH_CAST_LEVEL, SH_PLACE_LEVEL) ...
sh_asks    dw 0                 ; +2082 ... CHOOSE A SPELL asked for one (SH_PICK_ANY) ...
sh_paged   dw 0                 ; +2084 ... its pages cut to its own spells (SH_PAGE_CUT) ...
sh_scrolls dw 0                 ; +2086 ... and its tries at a scroll (SH_ROLLS, SH_NOT_ITS), counted
        times 2088 - ($ - hdr) db 0 ; (none: +2088 follows +2087)
poison_used  dw 0               ; +2088 a Poisoner's weapons that have poisoned this fight (POISON_HIT): bit N
                                ;      party member N's main hand, N + 4 its off hand (DSCLOG's +1860);
                                ;      cleared at a fight's first round (ACID_ROUND)
poison_doses dw 0               ; +2090 Poisoners' hits made poisoned (POISON_HIT, counted) ...
poison_casts dw 0               ; +2092 ... and their poison cast on the target (PLAIN_ARROW)
arrow_pluses dw 0               ; +2094 spell arrows made better by their archer's level (ARROW_PLUS, counted)
fine_hits    dw 0               ; +2096 attacks with the Fine Bow, 1 better to hit (FINE_HIT, counted)
arrows_on    dw 0               ; +2098 the Loader sets 1 to have a Spellarcher's arrows buttons on the USE screen
                                ;      (SPELL ARROWS; DSCLOG's PP_SHOW arrows, under its PICK_ON)
arrows_seq   dw 0               ; +2100 arrows asked for: an arrows button let go of, counted (ARROWS_ASK) ...
arrows_reply dw 0               ; +2102 ... the Loader sets this to ARROWS_SEQ once it has answered (PICK_TEXT
                                ;      its words if refused, empty if made: spellarrows.SpellArrows.make)
arrows_who   dw 0               ; +2104 ... the Spellarcher: the party member on show
arrows_row   dw 0               ; +2106 ... the touch spell's place in ARROW_SPELLS (spellarrows.ARROWS: 1-3)
arrows_shown dw 0               ; +2108 arrows buttons shown on the USE screen (PP_SHOW, counted) ...
arrows_late  dw 0               ; +2110 ... and arrows asked for the Loader didn't answer in time (ARROWS_ASK)
extras_drawn dw 0               ; +2112 buttons drawn beside Turn Undead's (PP_EXTRA_DRAW, counted)
lock_off     dw lock_barred     ; +2114 offset of LOCK_BARRED in the tail: the Loader's, the locks each party
                                ;      member may not try again yet (LOCK_SITE; DSCLOG's +1844, locks.py)
lock_bars    dw 0               ; +2116 open locks checks LOCK_SITE put out of reach (counted)
gl_bare      dw 0               ; +2118 gladiators' AC worked out with no armour on, no optimisation (GL_ARMOUR, counted)
ai_walls     dw 0               ; +2120 walls the computer cast across the line of fire (AI_WALL, counted)
kreen_cuts   dw 0               ; +2122 a party thri-kreen's natural attacks made edged (KREEN_CLAWS, counted)
berserk_sides dw 0              ; +2124 Berserks put on with the side kept in their record (BERSERK_ADD, counted) ...
berserk_ends dw 0               ; +2126 ... and Berserks ended with that side given back (BERSERK_END, counted)
ef_charge_lines dw 0            ; +2128 Effects screen lines named with their charges (EF_CHARGES, counted)
arrows_barred dw 0              ; +2130 spell arrows a party member not a Spellarcher was kept from readying
                                ;      (ARROWS_FORBID, counted)
arrows_sounds dw 0              ; +2132 spell arrows made with their cast sound played (ARROWS_ASK, counted)
ef_stats_off dw ef_stats        ; +2134 offset of EF_STATS in the tail: the Loader's, EF_STATS_SIZE bytes a party member
                                ;      (Enlarge's level, the three armour spells' AC: RavDiceLog._ef_stats_pass)
ef_mod_lines dw 0               ; +2136 Effects screen lines named by Enlarge's damage, an armour spell's AC or
                                ;      Reflected Image's name (EF_CHARGES' EC_MOD and EC_REFLECT, counted; its
                                ;      charges count in EF_CHARGE_LINES too)
hdr_end:                        ; +2138 (HDR_LEN: the header's end; new words go above this line)
align 16
kind     dw 0                   ; the entry kind RECORD writes (0: a rand() call)
extra    dw 0                   ; RECORD's +186 (none yet)
old21    dd 0                   ; DOS, as it was

; ---- rand(): DSCLOG's INT_RAND and STUB, but its seed's address and the psionic range filter ----
; The patched rand() starts with INT VEC_RAND. Drop the interrupt frame (restoring the caller's
; flags) and be rand(): the same numbers (seed = seed * 015A4E35h + 1, (seed >> 16) & 7FFFh),
; and each call whose calling code matches a filter recorded.
        SHARED_int_rand
stub:
        push eax                ; rand() leaves the upper half of EAX alone; so do we
        push si
        mov si, sp              ; SS:SI+6 = return IP, SS:SI+8 = return CS
        mov bx, [cs:seed_off]   ; DS is the game's data segment here
        mov eax, [bx]
        imul eax, eax, 0x015A4E35
        inc eax
        mov [bx], eax
        shr eax, 16
        cwd                     ; as the original: DX = sign of the high word
        and ax, 0x7FFF
        push ax
        push dx
        push di
        push es
        push cx
        mov cx, [cs:nfilt]      ; only record calls whose calling code matches a filter
        jcxz .record
        push ds
        push si
        push di
        lds si, [ss:si+6]       ; DS:SI = the code after this rand() call
        mov bx, filt
.filter:
        push si
        push cx
        push cs
        pop es
        mov di, bx
        xor cx, cx
        mov cl, [cs:bx]         ; the filter's length
        inc di
        repe cmpsb
        pop cx
        pop si
        je .matched
        add bx, 9
        loop .filter
        pop di
        pop si
        pop ds
        inc word [cs:skipped]
        jmp .done
.matched:
        pop di
        pop si
        pop ds
.record:
        mov word [cs:kind], 0
        call record
.done:
        pop cx
        pop es
        pop di
        pop dx
        pop ax
        mov bx, ax              ; BX is scratch for rand() callers
        pop si
        pop eax
        mov ax, bx
        retf

; RECORD: DSCLOG's, an entry added to the ring (ENTRY LAYOUT there), but +188 (the target's
; helplessness: none of the sequel's records known yet) left 0.
;   SS:SI+6 = the return address of the call being logged; BP = the caller's frame;
;   AX = the value at +6; [kind] = the entry's kind. Keeps every register but the flags.
record:
        push bx
        push cx
        push di
        push es
        mov es, [cs:ring_seg]
        mov di, [cs:widx]
        imul di, di, ESIZE
        add di, FAR_RING
        mov word [es:di], 0xFFFF
        mov cx, [cs:kind]
        mov [es:di+184], cx
        mov cx, [cs:extra]
        mov [es:di+186], cx
        mov word [cs:extra], 0
        mov word [es:di+188], 0
        mov cx, [ss:si+6]
        mov [es:di+2], cx
        mov cx, [ss:si+8]
        mov [es:di+4], cx
        mov [es:di+6], ax
        mov [es:di+8], bp
        mov [es:di+10], ss
        mov [es:di+12], ds
        mov cx, [bp]            ; BP-relative: SS
        mov [es:di+14], cx
        push ds
        push si
        push ss
        pop ds
        lea si, [bp+2]
        add di, 16
        mov cx, 16
        rep movsw               ; +16..+47
        mov si, [bp]
        add si, 2
        mov cx, 16
        rep movsw               ; +48..+79
        pop si
        pop ds
        xor bx, bx
.glob:
        push bx
        xor cx, cx
        cmp bx, 6               ; (the fourth word: HDR_LEN, no game word's offset)
        je .noglob
        mov bx, [cs:glob+bx]
        or bx, bx
        jz .noglob
        mov cx, [bx]            ; game DS
.noglob:
        mov [es:di], cx
        add di, 2
        pop bx
        add bx, 2
        cmp bx, 8
        jb .glob
        push ds                 ; DI is at +88: the caller's locals
        push si
        push ss
        pop ds
        lea si, [bp-16]
        mov cx, 8
        rep movsw
        pop si
        pop ds
        push ds                 ; DI is at +104: the calling code
        push si
        lds si, [ss:si+6]
        mov cx, 12
        rep movsw
        pop si
        push si
        lds si, [ss:bp+2]       ; the return address in the caller's frame
        mov cx, 8
        rep movsw
        push ss                 ; DI is at +144: the caller's caller's locals
        pop ds
        mov si, [bp]
        sub si, 0x28
        mov cx, 20
        rep movsw
        pop si
        pop ds
        sub di, 184             ; back to the start of the entry
        mov cx, [cs:seq]        ; publish: entry seq first, then the header's
        inc cx
        mov [es:di], cx
        mov [cs:seq], cx
        mov cx, [cs:widx]
        inc cx
        cmp cx, NENT
        jb .slot
        xor cx, cx
.slot:
        mov [cs:widx], cx
        pop es
        pop di
        pop cx
        pop bx
        ret

; ---- the saving throw: DSCLOG's PROBE_SAVE, without the spell table's segment ----
; INT VEC_SAVE replaces "mov al,[bp-2] / cmp al,[bp-1]" (6 bytes) at the saving throw's end (66EA6h):
; the total and the number needed (AX: AL the total, AH the save) recorded, kind 1, then the compare
; done, its flags kept for the branch after (the "jl" the save_signed fix makes of the game's "jb").
; DSCLOG also records the spell table's segment (+186): the sequel has no table in its program (its
; spells are RESOURCE.GFF's records: the Loader reads them), so 0.
probe_save:
        sti
        push si
        mov si, sp
        sub si, 4               ; SS:SI+6 = our return address (as RECORD wants it)
        push ax
        mov word [cs:extra], 0
        call size_spared        ; (the creature size rule: Hold and Charm Person on a large target)
        mov ax, [bp-2]          ; AL = total, AH = save value
        mov word [cs:kind], 1
        call record
        pop ax
        pop si
        mov al, [bp-2]
        cmp al, [bp-1]
        retf 2

; INT VEC_AC replaces "mov ax,[bp-4] / add ax,[bp-6]" (6 bytes) at the AC function's end (5D6E6h):
; the AC the attack uses recorded, kind 2 (DSCLOG's PROBE_AC without its features' changes, which
; aren't ported yet, but for the kits': KIT_AC), and left in AX as the game's code would.
probe_ac:
        sti
        push si
        mov si, sp
        sub si, 4               ; SS:SI+6 = our return address (as RECORD wants it)
        mov word [cs:extra], 0
        mov ax, [bp-4]
        add ax, [bp-6]
        call kit_ac             ; (the kits' AC: KITS)
        mov word [cs:kind], 2
        call record
        pop si
        retf 2

; ---- MISSILE_REAR: DSCLOG's, at the sequel's attack set-up, with its STEALTH (PROBE_STEALTH) ----
; The routine setting up an attack makes it one from behind by the target's facing alone, at any distance:
; "from behind" (the byte [BP-19h]: +2 to hit, 2 off THAC0 [BP-1Eh], and the AC function leaves out the
; target's DEX and shield), so a missile from across a room counted so too. Only melee ([BP+0Eh] 1) is
; from behind: a missile's taken back, but for a hidden archer's shot. INT VEC_REAR replaces "mov al,[bp-19h]"
; (5C99Fh: "push ax" after it kept), so it ends with AL as the game's. All registers but AL kept.
; STEALTH (RULE_STEALTH, SL's PROBE_STEALTH): a party member (SI 0-3) whose bit the Loader set in STEALTH
; (hidden in shadows and unheard: stealth.py) has the bit cleared (attacking gives them away) and this
; attack made one from behind (unless the target is an object, [BP-1Ah]: no back), and a backstab
; ([BP-21h], 2 more off THAC0) on the game's own conditions (5C952h-5C983h): a thief (the sheet's word
; +10h, bit 400h; [BP-12h] the sheet), in melee, with a weapon whose type's byte +2 is 28h or less
; ([BP-4] the type, 0Fh bytes each).
missile_rear:
        call rear_fresh
        mov byte [cs:st_now], 0
        test word [cs:rules], RULE_STEALTH
        jz .rear
        cmp si, 3
        ja .rear
        btr word [cs:stealth], si
        jnc .rear
        inc word [cs:stealth_used]
        mov byte [cs:st_now], 1         ; (this attack the hidden one's: a shot stays from behind)
        cmp byte [bp - 0x1A], 0
        jne .rear
        push ax
        push bx
        push es
        cmp byte [bp - 0x19], 0
        jne .stab
        mov byte [bp - 0x19], 1
        sub word [bp - 0x1E], 2
.stab:  cmp byte [bp - 0x21], 0
        jne .done
        mov ax, [bp - 0x12]
        imul ax, ax, SHEET_SIZE
        les bx, [SHEETS_PTR]
        add bx, ax
        test word [es:bx + 0x10], 0x400
        jz .done
        cmp word [bp + 0x0E], 1
        jne .done
        mov ax, [bp - 4]
        imul ax, ax, 0x0F
        les bx, [TYPES_PTR]
        add bx, ax
        cmp byte [es:bx + 2], 0x28
        ja .done
        sub word [bp - 0x1E], 2
        mov byte [bp - 0x21], 1
.done:  pop es
        pop bx
        pop ax
.rear:  cmp word [bp + 0x0E], 1
        je .out
        cmp byte [cs:st_now], 0
        jne .out
        cmp byte [bp - 0x19], 0
        je .out
        mov byte [bp - 0x19], 0
        add word [bp - 0x1E], 2
        inc word [cs:rear_taken]
.out:   call kit_rear                   ; (the kits': KITS)
        call item_rear                  ; (the girdles: ITEM_REAR)
        call thief_rear                 ; (class restrictions: no backstab in heavy armour)
        call stab_first                 ; (Thieves as in AD&D: a member's first attack of a round only)
        mov al, [bp - 0x19]
        iret
RULE_STEALTH equ 64
st_now  db 0                            ; (1 while MISSILE_REAR runs for a hidden one's attack)

; REAR_FRESH (SL's): first in MISSILE_REAR, each attack's from behind and backstab its own. The routine
; clears [BP-19h] and [BP-21h] once a call (5C5FEh, 5C606h) but runs all of a round's attacks in it (the
; loop back to 5C6DDh, [BP-1Eh] the creature's THAC0, its +16h, again each time), and sets them, with
; their 2 off THAC0 each, only when this attack is from behind: a flag left from an earlier attack (a
; hidden thief's backstab, then their second swing) had no 2 off this one, and the probes after it
; (ITEM_REAR, THIEF_REAR) gave back 2 it hadn't had. What the game took off the THAC0 this time says
; which flags it paid for; the others are cleared. All registers kept.
rear_fresh:
        push ax
        push bx
        push es
        mov ax, [bp - 0x0E]
        imul ax, ax, 0x31
        les bx, [CREATURES_PTR]
        add bx, ax
        mov al, [es:bx + 0x16]
        cbw
        sub ax, [bp - 0x1E]             ; (what the game's from behind and backstab took off)
        cmp ax, 2
        jge .stab
        mov byte [bp - 0x19], 0
.stab:  cmp ax, 4
        jge .out
        mov byte [bp - 0x21], 0
.out:   pop es
        pop bx
        pop ax
        ret
rear_taken dw 0                         ; missiles' "from behind" taken back (for the tests)

; ---- REST_POISON: the rest killed the Poisoned after a druid's free Neutralize Poison ----
; The rest (its pass 2 for each member, SI: 8CD25h) reads the member's effects as a bitset into [BP-1Eh]
; (8CD2Ah), then casts the free cures of a druid of 5th level and more (8CD47h-8CDCAh: Neutralize Poison
; among them), then kills the member if the copy says Poisoned (8D02Dh, "test byte [bp-16h],80h", effect
; 71; 1000 damage): from the copy taken before the cure. (SL's rest_cures_* moved the casts before the
; read.) INT VEC_REST_POISON replaces the test (4 bytes, 2 NOPs after the INT): whether the member has
; effect 71 now, from the active effects themselves (10 bytes each, +0 whom it's on, +6 the effect; at
; the load + 3E71h:24Dh, the count at DS:2100h), handed back as the test's ZF for the jz after it.
EFFECTS_GAP   equ 0x47E0 - 0x3E71    ; (the effects' segment below DS)
EFFECTS_BASE  equ 0x24D
EFFECTS_COUNT equ 0x2100
POISONED      equ 71
rest_poison:
        push bp
        mov bp, sp                      ; [bp+2] IP, [bp+4] CS, [bp+6] FLAGS
        push ax
        push bx
        push cx
        push es
        mov ax, ds
        sub ax, EFFECTS_GAP
        mov es, ax
        mov bx, EFFECTS_BASE
        mov cx, [EFFECTS_COUNT]
        or word [bp + 6], 0x0040        ; (ZF: not Poisoned, unless one is found)
        cmp cx, 400
        ja .out
        jcxz .out
.next:  cmp [es:bx], si
        jne .on
        cmp byte [es:bx + 6], POISONED
        jne .on
        and word [bp + 6], ~0x0040
        jmp .out
.on:    add bx, 10
        loop .next
.out:   inc word [cs:rest_reread]
        pop es
        pop cx
        pop bx
        pop ax
        pop bp
        iret
rest_reread dw 0                        ; times the test was answered (for the tests)

; ---- NPP_SAVE: DSCLOG's NS_NPP ----
; Where an undead's draining touch meets Negative Plane Protection (effect 79) on its target (84DD2h:
; the effect taken off, then "add sp,4 / push 6 / push 26h" and the save, 598h:75h, the protection
; stopping the touch and hurting the undead if saved), the save was as against Vampiric Touch (38),
; whose record allows none (+1Fh A0h: bit 0 clear), so the protection never stopped anything. INT
; VEC_NPP in the 7 bytes' place (5 NOPs after it) makes the two words still pushed (the effect's
; removal's arguments) the save's: 6, and POISON's record (179: +1Fh 21h, a save against paralysis,
; poison and death allowed, AD&D's against death magic; the sequel has no spare record to copy
; Vampiric Touch into, as DSCLOG does).
NPP_RECORD equ 179
npp_save:
        push bp
        mov bp, sp                      ; [bp+2] IP, [bp+4] CS, [bp+6] FLAGS, [bp+8] the next pushed
        mov word [bp + 8], NPP_RECORD
        mov word [bp + 10], 6
        inc word [cs:npp_count]
        pop bp
        iret
npp_count dw 0                          ; times it was asked (for the tests)

; ---- MIRROR IMAGE: DSCLOG's NS_IMAGE and NS_BLOW ----
; Mirror Images (effect 46) stopped no weapon blow, and took a spell for one creature three times in
; four whoever cast it (Armor cast on oneself lost, an image with it; the sequel already leaves out
; area spells, its 680h:20h test).
; IMAGE_SPELL: "cmp ax,4Bh" (84BF8h; 3 bytes) where a spell lands on thing SI ([BP+8] the caster, AX
; the d100): with caster and target on one side (party members, below 4, or not) the chance is 0, as
; if the d100 were over; else 75. Its flags into the INT's frame.
; IMAGE_BLOW: "cmp word [bp+1Ah],0" (5D09Fh; 4 bytes) where an attack (its d20 rolled) hits combatant
; [TARGET]: with Mirror Images on it, a d100 with the game's rand (rand() at the load segment's 822h)
; of 75 or less strikes an image instead: one used up through the charge spender (stub 608h:57h, as
; the game's spells use one: the effect ended with the last), and the attack goes on as a miss
; (5D0E9h), in a frame the overlay manager can fix up (the spender is overlay code). Else on as
; before, the compare's flags into the INT's frame. (Reflected Image's 50: NS_IMAGE_CHANCE.)
MIRROR_EFFECT equ 46
IMAGE_CHANCE  equ 75
IMAGE_PARTY   equ 4
BLOW_MISS     equ 0x5D0E9 - 0x5D0A1 ; (the miss, less the INT's way back)
RAND_OFF      equ 0x0822            ; (rand(), at the load segment)
DGROUP_GAP    equ 0x47E0            ; (DS less the load segment)
image_far     dd 0
image_spells  dw 0                  ; (for the tests: images that took a spell, and a blow)
image_blows   dw 0
image_spell:
        pushad
        push es
        push ax
        mov ax, si
        call ns_image_chance            ; (IMAGE_CHANCE, or Reflected Image's)
        pop ax
        mov bx, [bp + 8]
        cmp bx, IMAGE_PARTY
        setb bl
        cmp si, IMAGE_PARTY
        setb bh
        cmp bl, bh
        jne .cmp
        xor dx, dx
.cmp:   cmp ax, dx
        pushf
        jg .flags
        inc word [cs:image_spells]
.flags: pop ax
        jmp acid_flags

; effect_amount: AL the amount (+9) of thing AX's effect CL, 0 if it has none. DS the game's; others kept.
effect_amount:
        push bx
        push dx
        push es
        mov dx, ds
        sub dx, EFFECTS_GAP
        mov es, dx
        mov dx, [EFFECTS_COUNT]
        mov bx, EFFECTS_BASE
        mov al, 0
        cmp dx, 400
        ja .out
.each:  or dx, dx
        jz .out
        cmp [es:bx], ax
        jne .on
        cmp [es:bx + 6], cl
        jne .on
        mov al, [es:bx + 9]
        jmp .out
.on:    add bx, 10
        dec dx
        jmp .each
.out:   pop es
        pop dx
        pop bx
        ret

; has_effect: ZF set if thing AX has effect CL (the active effects). DS the game's; all kept.
has_effect:
        push bx
        push dx
        push es
        mov dx, ds
        sub dx, EFFECTS_GAP
        mov es, dx
        mov dx, [EFFECTS_COUNT]
        mov bx, EFFECTS_BASE
        cmp dx, 400
        ja .none
.each:  or dx, dx
        jz .none
        cmp [es:bx], ax
        jne .on
        cmp [es:bx + 6], cl
        je .out                         ; (ZF set)
.on:    add bx, 10
        dec dx
        jmp .each
.none:  or sp, sp                       ; (ZF clear)
.out:   pop es
        pop dx
        pop bx
        ret

image_blow:
        sti
        pushad
        push es
        mov di, sp
        cmp word [bp + 0x1A], 0
        pushf
        pop ax
        and ax, FLAGS_MASK
        and word [ss:di + 38], ~FLAGS_MASK
        or [ss:di + 38], ax
        mov ax, [TARGET]
        mov cl, MIRROR_EFFECT
        call has_effect
        jnz .out
        mov ax, ds
        sub ax, DGROUP_GAP
        mov [cs:image_far + 2], ax
        mov word [cs:image_far], RAND_OFF
        call far [cs:image_far]         ; (rand(): 0 to 32767)
        mov cx, 100
        mul cx
        shl ax, 1
        rcl dx, 1                       ; (rand() x 100 / 32768: 0 to 99)
        inc dx
        push dx
        mov ax, [TARGET]
        call ns_image_chance            ; (IMAGE_CHANCE, or Reflected Image's)
        mov ax, dx
        pop dx
        cmp dx, ax
        ja .out
        inc word [cs:image_blows]
        mov bx, sp
        add word [ss:bx + 34], BLOW_MISS ; (before the call: the overlay manager may leave its
        push word [ss:bx + 36]          ;   trap in place of the way back, as a far call's frame)
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        mov ax, ds
        add ax, USE_STUB
        mov [cs:image_far + 2], ax
        mov word [cs:image_far], USE_ENTRY
        push word MIRROR_EFFECT
        push word [TARGET]
        call far [cs:image_far]
        add sp, 4
        pop bp
        pop ax                          ; (the way back, as the overlay manager has left it)
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
.out:   pop es
        popad
        iret

; ---- ACID: DSCLOG's ACID_ROUNDS, ACID_BURN, ACID_ONCE, ACID_USE, ACID_ROUND ----
; Acid Arrow's Acid (effect 1) never burned after the arrow's hit, as in Shattered Lands: the routine
; spending a creature's charges of an effect (7FD94h, stub 608h:57h: each charge spent burns, Acid's
; burn 82BECh, 2d4 acid as Acid Arrow, spell 12h) is called for Acid only on a chance event (81FC6h),
; and Acid's time is seconds on the game clock, a timer that only ends it. ACID_ROUNDS makes the time
; rounds (1 a started minute) as charges; ACID_ROUND, at each round's start, spends one for each
; creature with Acid, through the stub; ACID_USE lets no other call spend Acid's. The burn's damage
; is Acid Arrow's, whose record would put Acid on again: ACID_BURN notes a burn starting and
; ACID_ONCE has its damage put no effect on. (DSCLOG's, without Sunstroke's
; heat or Whirlwind's damage, which the sequel doesn't have from the mod yet.) Each INT is followed
; by NOPs to the site's length; its way back is right after the INT.
ACID_EFFECT   equ 1
ROUND_SECONDS equ 60
PERMANENT_DUR equ -9999
USE_STUB      equ 0x473B - 0x47E0   ; (the spender's stub segment, 608h's, less DS's)
USE_ENTRY     equ 0x57
USE_OUT       equ 0x7FE8F - 0x7FD9B ; (the spender's "pop di / pop si / pop bp / retf", from the INT's return)
FIRST_ROUND   equ 0x54E             ; DS byte: set for a fight's first round (SL's word at 55Ah)
FLAGS_MASK    equ 0x08D5            ; (CF, PF, AF, ZF, SF, OF: a compare's)
acid_burning db 0                   ; (1 from ACID_BURN until its damage's effect is passed: ACID_ONCE)
acid_mine    db 0                   ; (1 while ACID_ROUND's call spends Acid: ACID_USE)
acid_far     dd 0
acid_burns   dw 0                   ; Acid charges spent by ACID_ROUND (for the tests)

; acid_flags: the way back from a handler that did PUSHAD, then ES, with AX's flags (a compare's) in
; its frame's FLAGS (SS:SP+38 at the jump).
acid_flags:
        mov di, sp
        and ax, FLAGS_MASK
        and word [ss:di + 38], ~FLAGS_MASK
        or [ss:di + 38], ax
        pop es
        popad
        iret

; ACID_ROUNDS: "cmp dword [bp+0Eh],-9999" (7FAA6h; 8 bytes) in the routine adding an effect ([BP+0Ch]
; the effect, [BP+0Eh] its time, a dword; less than 0 charges, kept in the entry's +8): an Acid's time
; in seconds made rounds as charges (at least 1, at most 127); Low Resistance's (61) amount (+9, ES:BX
; the entry less 24Dh) Lower Resistance's cast's level (CAST_LEVEL, LOWRES_SITE's); then the compare
; made, its flags returned.
acid_rounds:
        pushad
        push es
        cmp byte [bp + 0x0C], LOWRES_EFFECT
        jne .acid
        cmp word [bp + 0x0A], LOWRES_SPELL
        jne .acid
        mov al, [cs:cast_level]
        mov [es:bx + EFFECTS_BASE + 9], al
.acid:  cmp byte [bp + 0x0C], ACID_EFFECT
        jne .test
        mov eax, [bp + 0x0E]
        or eax, eax
        jle .test
        add eax, ROUND_SECONDS - 1
        xor edx, edx
        mov ecx, ROUND_SECONDS
        div ecx
        cmp eax, 0x7F
        jbe .neg
        mov eax, 0x7F
.neg:   neg eax
        mov [bp + 0x0E], eax
.test:  cmp dword [bp + 0x0E], PERMANENT_DUR
        pushf
        pop ax
        jmp acid_flags

; ACID_BURN: "mov si,[bp+6]" (82BF3h; 3 bytes) at the start of Acid's burn ([BP+6] the creature): noted
; (ACID_BURNING), the move made.
acid_burn:
        mov byte [cs:acid_burning], 1
        mov si, [bp + 6]
        iret

; ACID_ONCE: "cmp word [bp-0Ah],0" (651FEh; 4 bytes) where a spell's damage (64F5Fh) puts the record's
; effect ([BP-0Ah]) on the target it hurt: during an Acid burn (ACID_BURNING, then cleared) none, as if
; the record had none; else the compare made, its flags returned.
acid_once:
        pushad
        push es
        cmp byte [cs:acid_burning], 0
        je .test
        mov byte [cs:acid_burning], 0
        xor ax, ax                      ; (ZF set: "none")
        jmp .flags
.test:  cmp word [bp - 0x0A], 0
.flags: pushf
        pop ax
        jmp acid_flags

; ACID_USE: "mov di,[bp+6]" (7FD99h; 3 bytes) at the start of the routine spending creature [BP+6]'s
; charges of effect [BP+8] (7FD94h): Acid's spent only from ACID_ROUND (ACID_MINE), any other call
; returning at once (its "pop di / pop si / pop bp / retf"); else the move made.
acid_use:
        cmp byte [bp + 8], ACID_EFFECT
        jne .go
        cmp byte [cs:acid_mine], 0
        jne .go
        push bx
        mov bx, sp
        add word [ss:bx + 2], USE_OUT   ; (none spent: return at once)
        pop bx
        iret
.go:    mov di, [bp + 6]
        iret

; ACID_ROUND: "cmp byte [54Eh],0" (5B592h; 5 bytes) in the routine starting each round (5B585h: the
; clock moved on, then the initiative): each creature with Acid charges (ACID_ROUNDS) has one spent
; (7FD94h through its stub, the way back in a frame the overlay manager can fix up, as it may load
; that code over the caller's), the creatures in turn by their number (the table changes as entries
; go); then the compare made, its flags returned. DS the game's; all registers kept.
acid_round:
        pushad
        push es
        sti
        mov bx, sp                      ; (BX+34: the INT's way back, its IP then CS)
        call burn_pass
        cmp byte [FIRST_ROUND], 0
        je .on
        call tangle_clear               ; (the cahulaks' tangles: none at a fight's start)
        call tu_clear                   ; (and no failed turnings)
        mov word [cs:poison_used], 0    ; (and each Poisoner's weapon poisons again: POISON_HIT)
        cmp byte [FIRST_ROUND], 0
.on:
        pushf
        pop ax
        jmp acid_flags

burn_pass:
        mov dx, -1                      ; (DX the last creature done)
.next:  mov ax, ds
        sub ax, EFFECTS_GAP
        mov es, ax
        mov di, 0xFFFF                  ; (DI the least creature past DX with Acid charges)
        xor cx, cx
.scan:  cmp cx, [EFFECTS_COUNT]
        jae .found
        cmp cx, 400
        jae .found
        imul si, cx, 10
        add si, EFFECTS_BASE
        inc cx
        cmp byte [es:si + 6], ACID_EFFECT
        jne .scan
        cmp byte [es:si + 8], 0
        je .scan
        mov ax, [es:si]
        cmp dx, -1
        je .first
        cmp ax, dx
        jbe .scan
.first: cmp ax, di
        jae .scan
        mov di, ax
        jmp .scan
.found: cmp di, 0xFFFF
        je .done
        mov dx, di
        push bx
        push dx
        push word [ss:bx + 36]
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        mov ax, ds
        add ax, USE_STUB
        mov [cs:acid_far + 2], ax
        mov word [cs:acid_far], USE_ENTRY
        mov byte [cs:acid_mine], 1
        inc word [cs:acid_burns]
        push word ACID_EFFECT
        push di
        call far [cs:acid_far]
        add sp, 4
        mov byte [cs:acid_mine], 0
        pop bp
        pop ax                          ; (the way back, as the overlay manager has left it)
        pop cx
        pop dx
        pop bx
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], cx
        jmp .next
.done:  ret

; ---- PIC_REUSE: DSCLOG's, on the sequel's picture cache ----
; The game's picture cache (DSUNLOG2.EXE 2A568h, SL's 25FA6h) has 300 slots, 16 bytes each (the
; picture's number, length, place in the store, memory, flags: 2 in memory, 4 its kind), at the load
; + 42A2h:0CA8h (CACHE_SEG below DS, CACHE_BASE), the count at DS:265Dh, and gives none back until a
; region loads: at 300 a new picture got no slot and wasn't drawn (SSI's note 2712, "graphics
; disappear"; 253 of the 300 are taken at the start of Tyr). The slots that hold a number are the map
; things' (DS:67BBh, 25h bytes, the slot at +10h; the sequel's walls don't come through this cache).
; So with all 300 taken a slot is reused: one out of memory that no thing names, one let go (STALE)
; first; its picture goes in the first gap in the store it fits (CACHE_STORE bytes: 123360h, its
; allocation at 6743Fh), else past the furthest end. Below 300 the game's own way. As DSCLOG's, but:
; no walls, the table's offset, the jumps counted from after a 2-byte INT, and a reused slot's flags
; cleared as it is taken (the sequel's kind bit, 4, is only ever set).
CACHE_MOST   equ 300
CACHE_GAP    equ 0x47E0 - 0x42A2  ; (the table's segment, below the game's DS: DGROUP - 42A2h)
CACHE_BASE   equ 0x0CA8
CACHE_LAST   equ 0x265D           ; DS: the count
CACHE_STORE  equ 0x123360
CACHE_STALE  equ 0xFFFE
MAP_SLOTS    equ 0x67BB + 0x10    ; DS: each map thing's slot
MAP_STRIDE   equ 0x25
MAP_COUNT    equ 0x141
PF_FAIL      equ 0x2A58E - 0x2A5E9  ; (from after PIC_FULL's INT: the loader's "no slot")
PF_PLACED    equ 0x2A73E - 0x2A6FF  ; (from after PIC_PLACE's INT: past the game's place, the store written)

; PIC_FULL (2A5E7h, "cmp word [265Dh],12Ch / jae no slot / mov ax,[265Dh]", 11 bytes): the slot
; for a new picture in AX: the next, or with all taken one reused (none: no slot, as the game).
pic_full:
        mov byte [cs:pf_reuse], 0
        mov ax, [CACHE_LAST]
        cmp ax, CACHE_MOST
        jae .full
        iret
.full:  sti
        push es
        push di
        push si
        push cx
        push bx
        push cs
        pop es
        mov di, pf_used
        mov cx, PF_USED_WORDS
        cld
        xor ax, ax
        rep stosw
        mov si, MAP_SLOTS
        mov cx, MAP_COUNT
.thing: mov bx, [si]
        call pf_mark
        add si, MAP_STRIDE
        loop .thing
        mov ax, ds
        sub ax, CACHE_GAP
        mov es, ax
        mov si, [cs:pf_next]            ; (round from the one after the last reused)
        cmp si, CACHE_MOST
        jb .from
        xor si, si
.from:  mov cx, CACHE_MOST
        mov di, 0xFFFF                  ; (the first free one with a number)
.scan:  mov bx, si
        shl bx, 4
        test byte [es:bx + CACHE_BASE + 0x0E], 2
        jnz .next                       ; (in memory)
        bt word [cs:pf_used], si
        jc .next                        ; (named by a thing)
        cmp word [es:bx + CACHE_BASE], CACHE_STALE
        je .take
        cmp di, 0xFFFF
        jne .next
        mov di, si
.next:  inc si
        cmp si, CACHE_MOST
        jb .round
        xor si, si
.round: loop .scan
        mov si, di
        cmp si, 0xFFFF
        je .none
        mov bx, si
        shl bx, 4
.take:  mov word [es:bx + CACHE_BASE], CACHE_STALE ; (found by no number until its picture is in)
        mov byte [es:bx + CACHE_BASE + 0x0E], 0
        mov [cs:pf_slot], si
        lea ax, [si + 1]
        mov [cs:pf_next], ax
        mov byte [cs:pf_reuse], 1
        inc word [cs:pf_count]
        mov ax, si
        pop bx
        pop cx
        pop si
        pop di
        pop es
        iret
.none:  pop bx
        pop cx
        pop si
        pop di
        pop es
        push bp
        mov bp, sp
        add word [bp + 2], PF_FAIL
        pop bp
        iret
        SHARED_pf_mark

; PIC_PLACE (2A6FDh, "les bx,[bp-4]" before the place is worked out, 3 bytes): a reused slot's
; place, the first gap of its length in the store, else the furthest end.
pic_place:
        les bx, [bp - 4]
        cmp byte [cs:pf_reuse], 0
        jne .reused
        iret
.reused:
        sti
        pushad
        mov edx, [es:bx + 2]            ; its length
        mov ax, ds
        sub ax, CACHE_GAP
        mov es, ax
        xor ecx, ecx                    ; a place to try: the store's start, then each slot's end
        mov word [cs:pf_cand], 0
.try:   mov eax, ecx
        add eax, edx
        cmp eax, CACHE_STORE
        ja .another
        mov bx, CACHE_BASE
        xor si, si
.check: call pf_slot_end                ; (EDI its place, EBP its end; CF: none to count)
        jc .clear
        cmp edi, eax
        jge .clear                      ; (starts past the place's end)
        cmp ecx, ebp
        jl .another                     ; (overlaps)
.clear: add bx, 16
        inc si
        cmp si, CACHE_MOST
        jb .check
        jmp .found
.another:
        mov si, [cs:pf_cand]
        cmp si, CACHE_MOST
        jae .last
        inc word [cs:pf_cand]
        mov bx, si
        shl bx, 4
        add bx, CACHE_BASE
        call pf_slot_end
        jc .another
        mov ecx, ebp
        jmp .try
.last:  xor ecx, ecx                    ; (no gap: the furthest end)
        mov bx, CACHE_BASE
        xor si, si
.end:   call pf_slot_end
        jc .past
        cmp ebp, ecx
        jbe .past
        mov ecx, ebp
.past:  add bx, 16
        inc si
        cmp si, CACHE_MOST
        jb .end
.found: mov [cs:pf_place], ecx
        popad
        les bx, [bp - 4]
        push eax
        mov eax, [cs:pf_place]
        mov [es:bx + 6], eax
        pop eax
        push bp
        mov bp, sp
        add word [bp + 2], PF_PLACED
        pop bp
        iret
pf_slot_end:                            ; slot SI at ES:BX: EDI its place, EBP its end; CF if it
        cmp si, [cs:pf_slot]            ;   holds no place (the one reused, a STALE one, none)
        je .none
        cmp si, [CACHE_LAST]            ; (past the count: never used in this region)
        jae .none
        cmp word [es:bx], CACHE_STALE
        je .none
        mov edi, [es:bx + 6]
        or edi, edi
        js .none
        mov ebp, [es:bx + 2]
        or ebp, ebp
        jz .none
        add ebp, edi
        clc
        ret
.none:  stc
        ret

; PIC_COUNT (2A75Ch, "mov si,[265Dh] / inc word [265Dh]", 8 bytes): the slot's number in SI; the
; count raised for a new slot, not a reused one.
pic_count:
        cmp byte [cs:pf_reuse], 0
        jne .reused
        mov si, [CACHE_LAST]
        inc word [CACHE_LAST]
        iret
.reused:
        mov si, [cs:pf_slot]
        mov byte [cs:pf_reuse], 0
        iret

; PIC_FAIL (2A58Eh, "mov ax,0FFFFh", 3 bytes: the loader's "no picture", every failure's way out): a
; slot reused by PIC_FULL whose picture then failed to load is let go again (STALE, not in memory).
pic_fail:
        cmp byte [cs:pf_reuse], 0
        je .out
        push es
        push bx
        mov bx, ds
        sub bx, CACHE_GAP
        mov es, bx
        mov bx, [cs:pf_slot]
        shl bx, 4
        mov word [es:bx + CACHE_BASE], CACHE_STALE
        and byte [es:bx + CACHE_BASE + 0x0E], ~2
        mov byte [cs:pf_reuse], 0
        inc word [cs:pf_failed]
        pop bx
        pop es
.out:   mov ax, 0xFFFF
        iret
PF_USED_WORDS equ (CACHE_MOST + 15) / 16
pf_used    times PF_USED_WORDS dw 0
pf_reuse   db 0
pf_slot    dw 0
pf_next    dw 0
pf_cand    dw 0
pf_place   dd 0
pf_count   dw 0                         ; slots reused (for the tests: the Loader can read it)
pf_failed  dw 0                         ; reused slots let go after a failed read

; ---- DOS's file opens: DSCLOG's PROBE_DOS_OPEN, for the Loader's copies ----
; Opening a file (AH=3Dh) named in COPIES (the whole path, or after a \, : or /, in any case) opens the
; Loader's copy instead (with the same mode) and sets its bit in COPIED: RESOURCE.GFF is D:\RESOURC2.GFF
; (bit 1), GPLDATA.GFF D:\GPLDAT2.GFF (bit 2), OBJEX.GFF D:\OBJEX2.GFF (bit 4: the mod's item types),
; RGN03A.GFF D:\RGN03A2.GFF (bit 8: the Mines3 dining room for its redrawn figures, ravfigures.REGIONS).
; RGN001 and RGN033 use their copies for the Forest dining sets and Alliance crate.
; RGN038 uses its copy for the northern barrel stack in Mines 1.
; RGN03D and RGN03E use their copies for the Volcano silver seats and the Volcano 2 barrel stack.
; With no copy there, the game's own. Everything else goes on to DOS.
probe_dos_open:
        cmp ah, 3Dh
        jne .chain
        push ax
        push bx
        push cx
        push si
        push di
        mov si, dx
        mov cx, 128
.end:   cmp byte [si], 0
        je .at_end
        inc si
        loop .end
        jmp .no
.at_end:
        mov cx, si
        sub cx, dx              ; CX: the path's length
        mov bx, copies          ; each: its name's length, the name, the copy's path, its COPIED bit
.entry: xor ax, ax
        mov al, [cs:bx]
        or ax, ax
        jz .no                  ; (none of them)
        cmp cx, ax
        jb .next
        mov si, dx
        add si, cx
        sub si, ax              ; where the name would start
        cmp cx, ax
        je .compare             ; (the path is just the name)
        mov ah, [si - 1]
        cmp ah, '\'
        je .compare
        cmp ah, ':'
        je .compare
        cmp ah, '/'
        jne .next
.compare:
        push cx
        xor cx, cx
        mov cl, [cs:bx]
        lea di, [bx + 1]
.cmp:   mov al, [si]
        cmp al, 'a'
        jb .upper
        cmp al, 'z'
        ja .upper
        sub al, 20h
.upper: cmp al, [cs:di]
        jne .differ
        inc si
        inc di
        loop .cmp
        pop cx
        jmp .match              ; (DI: the entry's copy path)
.differ:
        pop cx
.next:  xor ax, ax
        mov al, [cs:bx]
        add bx, ax
        add bx, 5               ; (the length byte, the path's word, the bit's word)
        jmp .entry
.match: mov si, [cs:di]         ; the copy's path
        mov di, [cs:di + 2]     ; its COPIED bit
        mov [cs:dos_bit], di
        mov [cs:dos_path], si
        pop di
        pop si
        pop cx
        pop bx
        pop ax
        sti
        push ax                 ; (the game's AX, for its own file if there's no copy)
        push ds
        push dx
        push cs
        pop ds
        mov dx, [cs:dos_path]
        pushf
        call far [cs:old21]
        pop dx
        pop ds
        jc .own
        add sp, 2               ; (CF clear, AX the handle)
        push ax
        mov ax, [cs:dos_bit]
        or [cs:copied], ax
        pop ax
        retf 2
.own:   pop ax
        jmp .chain
.no:    pop di
        pop si
        pop cx
        pop bx
        pop ax
.chain: jmp far [cs:old21]

dos_path dw 0
dos_bit  dw 0
copies  db 12, 'RESOURCE.GFF'
        dw res_copy, 1
        db 11, 'GPLDATA.GFF'
        dw gpl_copy, 2
        db 9, 'OBJEX.GFF'
        dw obj_copy, 4
        db 10, 'RGN03A.GFF'
        dw rgn_copy, 8
        db 10, 'RGN001.GFF'
        dw forest_copy, 16
        db 10, 'RGN033.GFF'
        dw alliance_copy, 32
        db 10, 'RGN03D.GFF'
        dw volcano_copy, 64
        db 10, 'RGN03E.GFF'
        dw volcano1_copy, 128
        db 10, 'RGN038.GFF'
        dw mines1_copy, 256
        db 0
res_copy db 'D:\RESOURC2.GFF', 0
gpl_copy db 'D:\GPLDAT2.GFF', 0
obj_copy db 'D:\OBJEX2.GFF', 0
rgn_copy db 'D:\RGN03A2.GFF', 0
forest_copy db 'D:\RGN0012.GFF', 0
alliance_copy db 'D:\RGN0332.GFF', 0
volcano_copy db 'D:\RGN03D2.GFF', 0
volcano1_copy db 'D:\RGN03E2.GFF', 0
mines1_copy db 'D:\RGN0382.GFF', 0

; ---- SPELL SLOTS ON USE: DSCLOG's PROBE_USE, PROBE_WIN and USE_DRAW ----
; The same routines as Shattered Lands' (the USE screen's code is SL's, at other addresses): PROBE_USE
; replaces "add sp,0Ch" (79543h; SL's 70FBBh) after the USE screen's LEVEL button is labelled, PROBE_WIN
; "xor ax,ax / pop si" (303BEh; SL's 2BBA9h) at the end of the routine bringing a window to the front
; (its window the argument at its BP+6). USE_DRAW prints the selected character's heading and the line
; of the list and level on show from SLOTS_TEXT (the Loader's, in DSCLOG's format) with the game's text
; routine. What differs is the addresses: the window on show DS:1431h (SL's 11A4h), the level on show
; DS:43ECh (4AECh), the list a byte a member at DS:43E8h (4AE8h), the character on show at
; (load + 3E71h):0B44h (the selector 370h's; SL's 3931h:25Bh), the USE screen's window at
; (load + 45C9h):0 (the selector 4D8h's; SL's 40BCh:0), the text routine 301Bh:172h (SL's 2B7Ah:16Dh),
; its colours DS:2D16h and 2D14h (3270h, 326Eh) and its format "%C%C%C%s" at DS:0F6Ah. DSCLOG's
; PROBE_WIN also labels the save window; that isn't here.
WIN_SHOWN    equ 0x1431            ; DS: the window on show (a far pointer)
USE_LEVEL    equ 0x43EC            ; DS: the spell level the USE screen shows (its LEVEL button's)
USE_LIST     equ 0x43E8            ; DS: the list it shows, a byte a member: 1 MAGE, 2 CLERIC, 3 PSIONIC
USE_WHO_SEG  equ 0x3E71 - 0x47E0   ; the selected character's number is at this segment:USE_WHO_OFF
USE_WHO_OFF  equ 0x0B44
WIN_USE_SEG  equ 0x45C9 - 0x47E0   ; the USE screen's window pointer is at this segment:0
USE_TEXT_SEG equ 0x301B - 0x47E0   ; the text routine's segment less DS's
USE_TEXT_OFF equ 0x0172
TEXT_COLOUR  equ 0x2D16            ; DS: the colours the game sets for its AC line (SL's 3270h, 326Eh)
TEXT_INK     equ 0x2D14
TEXT_FORMAT  equ 0x0F6A            ; DS: "%C%C%C%s"
SLOTS_SIZE   equ 128
SLOT_KEY     equ 0x80
USE_X        equ 0x96              ; the panel under the spells (window coordinates), as SL's
USE_FIRST_Y  equ 0x6C
USE_STEP     equ 7
probe_use:
        push bp                 ; the replaced "add sp,0Ch": move the interrupt frame (and BP)
        mov bp, sp              ; up over the 12 bytes
        push ax
        mov ax, [bp + 6]
        mov [bp + 18], ax
        mov ax, [bp + 4]
        mov [bp + 16], ax
        mov ax, [bp + 2]
        mov [bp + 14], ax
        mov ax, [bp]
        mov [bp + 12], ax
        pop ax
        mov sp, bp
        add sp, 12
        pop bp
        sti
        pushad
        push es
        push fs
        mov eax, [WIN_SHOWN]    ; the USE screen is up: PROBE_WIN may redraw on this window
        mov [cs:use_win], eax
        inc word [cs:use_count]
        call use_draw
        pop fs
        pop es
        popad
        iret

probe_win:
        push bp
        mov bp, sp              ; BP+2 the interrupt frame, BP+8 the routine's saved SI
        sti
        pushad
        push es
        push fs
        mov di, [bp]            ; the routine's BP
        mov eax, [ss:di + 6]    ; its window
        or eax, eax
        jz .done
        cmp eax, [cs:use_win]
        jne .done               ; not a USE screen PROBE_USE has drawn on
        cmp eax, [WIN_SHOWN]
        jne .done               ; not the window on show
        mov bx, ds
        add bx, WIN_USE_SEG
        mov es, bx
        cmp eax, [es:0]
        jne .done               ; not the USE screen
        inc word [cs:win_count]
        call use_draw
.done:  pop fs
        pop es
        popad
        xor ax, ax              ; the replaced "xor ax,ax"
        mov si, [bp + 8]        ; ... and "pop si": move the interrupt frame up over it
        push dx
        mov dx, [bp + 6]
        mov [bp + 8], dx
        mov dx, [bp + 4]
        mov [bp + 6], dx
        mov dx, [bp + 2]
        mov [bp + 4], dx
        pop dx
        mov sp, bp
        pop bp
        add sp, 2
        iret

; TAIL_FS: FS the tail's segment (TAIL: CS + TAIL_PARAS, as TAIL_SEG has it once installed; worked out
; here so that it holds before the install too, and in the tests). All else kept, the flags too.
tail_fs:
        push ax
        pushf
        mov ax, cs
        add ax, TAIL_PARAS
        mov fs, ax
        popf
        pop ax
        ret

use_draw:                       ; the selected character's slots in the USE screen's panel (SLOTS_TEXT
        push fs                 ;   and U_LINE: the tail's, FS)
        call tail_fs
        call .draw
        pop fs
        ret
.draw:  mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov bx, [es:USE_WHO_OFF] ; the character on show
        cmp bx, 3
        ja .done
        imul si, bx, SLOTS_SIZE
        add si, slots_text
        cmp byte [fs:si], 0
        je .done                ; no spells
        mov ax, ds
        add ax, USE_TEXT_SEG
        mov [cs:c_draw + 2], ax
        mov word [cs:c_draw], USE_TEXT_OFF
        mov eax, [WIN_SHOWN]    ; the screen's window
        mov [cs:c_winptr], eax
        mov bl, [bx + USE_LIST] ; (BX still the member)
        and bl, 7
        shl bl, 4
        or bl, SLOT_KEY         ; (BL the heading's key, BH the level's line's)
        mov bh, [USE_LEVEL]
        and bh, 0x0F
        or bh, bl
        push si
        mov dx, USE_FIRST_Y
        call .find
        pop si
        jc .done                ; (no heading: no spells of that list)
        mov bl, bh
        mov dx, USE_FIRST_Y + USE_STEP
        call .find
.done:  ret
.find:  cmp [fs:si], bl         ; the line keyed BL from SI drawn at y DX, carry clear; carry set
        je .line                ; if none
.next:  mov al, [fs:si]
        inc si
        cmp al, '|'
        je .find
        or al, al
        jnz .next
        stc
        ret
.line:  inc si                  ; (past its key)
        mov di, u_line          ; copy the line (up to "|" or the end) and draw it
.copy:  mov al, [fs:si]
        cmp al, '|'
        je .cut
        cmp al, 0
        je .cut
        mov [fs:di], al
        inc si
        inc di
        cmp di, u_line + SLOTS_SIZE - 1
        jb .copy
.cut:   mov byte [fs:di], 0
        push bx
        push dx
        push dx                 ; y
        push word USE_X         ; x
        push fs
        push word u_line
        call c_draw_line
        call tail_fs            ; (the game's text routine may change FS)
        pop dx
        pop bx
        clc
        ret

c_draw_line:                    ; DSCLOG's: stack: text far pointer, x, y (near return address first)
        push bp
        mov bp, sp
        push dword [bp + 4]     ; the text, for the format's %s
        push word [TEXT_COLOUR] ; the colours, as the game sets them for its AC line
        push word 0x14
        push word [TEXT_INK]
        push dword 0x00FE00FF
        push word 0
        push ds
        push word TEXT_FORMAT   ; the format: "%C%C%C%s"
        push dword [bp + 8]     ; x, y
        push dword [cs:c_winptr]  ; the window
        call far [cs:c_draw]
        add sp, 0x1C
        pop bp
        ret 8

use_win  dd 0                   ; the USE screen's window, as PROBE_USE last saw it
c_draw   dd 0                   ; the text routine
c_winptr dd 0                   ; the window it prints in
use_count dw 0                  ; PROBE_USE's and PROBE_WIN's draws (for the tests)
win_count dw 0
section tailz                   ; (U_LINE and SLOTS_TEXT: the tail's)
u_line   times SLOTS_SIZE db 0
slots_text times 4 * SLOTS_SIZE db 0
section image


; ---- CHARGES IN ITEM BOXES: DSCLOG's PROBE_ITEM_BOX, IB_CHARGES and IB_MATERIAL ----
; PROBE_ITEM_BOX: INT VEC_ITEM_BOX replaces "push 0" (9A4FEh; SL's 8C1A1h) at the end of the routine
; filling an item's box (the same code: SI the item's type, DI the row after its lines but for AC
; BONUS's, [BP+6] the item, [BP+8] the box's window, [BP-0Ch] the x; the text routine's far address
; in the call before). In the next row: an item that casts a spell with charges, "Charges: n"
; (IB_CHARGES); else a plain weapon of a weaker material, its to-hit ("Hit -2": IB_MATERIAL, the
; game's attack's own). What differs from DSCLOG's: the sequel's records (items 17h bytes at the far
; pointer DS:19C1h, the charges a word at +0Eh, the spell + 1 a word at +10h, the plus +16h; item types
; 0Fh bytes at DS:19CDh, SL's +08h at +04h, +0Dh at +09h, +0Fh at +0Bh), fruit type 9, the box's own
; colours (C200B5h, SL's 960081h), and none of the mod's (the thief skills' lines, the Fine Bow).
IB_DRAW       equ 0x9A4F7 - 0x9A500 ; the text routine's far address in the call before, less the way back
ITEMS_PTR     equ 0x19C1            ; DS: far pointer to the items, 17h bytes each
ITEM_SIZE     equ 0x17
ITEM_CHARGES  equ 0x0E              ; (a word: the charges left)
ITEM_SPELL    equ 0x10              ; (a word: the spell + 1, or one of the game's own effects)
ITEM_PLUS     equ 0x16
TYPES_PTR     equ 0x19CD            ; DS: far pointer to the item types, 0Fh bytes each
TYPE_SIZE     equ 0x0F
TYPE_KIND     equ 0x04              ; (SL's +08h: the material, low nibble; 80h the game's exemption, 40h none)
TYPE_DICE     equ 0x09              ; (SL's +0Dh: the damage dice' count, 0 for no weapon)
TYPE_ARMOUR   equ 0x0B              ; (SL's +0Fh: 80h, AC BONUS drawn)
TYPE_FRUIT    equ 9
TYPE_SCENERY  equ 0x60              ; (in TYPE_KIND: doors, shutters...)
SPELLS_ALL    equ 320               ; (a spell + 1 above this: one of the game's own effects)
IB_COLOURS    equ 0x00C200B5        ; (as the box draws its lines)
probe_item_box:
        pushad
        push es
        cmp si, 0x270F
        jae .push
        les bx, [TYPES_PTR]             ; (DS: the game's)
        imul ax, si, TYPE_SIZE
        add bx, ax
        call ib_charges                 ; (DX the line, or 0)
        or dx, dx
        jnz .draw
        call ib_material                ; (a weaker material's to-hit: DX the line, or 0)
        or dx, dx
        jz .push
.draw:  mov ax, di                      ; the row: after AC BONUS's, if the box drew it
        test byte [es:bx + TYPE_ARMOUR], 0x80
        jz .row
        add ax, 7
.row:   mov si, sp
        mov bx, [ss:si + 34]            ; the way back (after ES and the PUSHAD)
        mov es, [ss:si + 36]
        mov ecx, [es:bx + IB_DRAW]
        mov [cs:ib_draw], ecx
        inc word [cs:ib_count]
        push dword IB_COLOURS
        push ax                         ; y
        push word [bp - 0x0C]           ; x
        push cs
        push dx
        push dword [bp + 8]             ; the box's window
        call far [cs:ib_draw]
        add sp, 16
.push:  pop es
        popad
        sub sp, 2                       ; the PUSH 0: the interrupt's frame moved down a word
        push bp
        mov bp, sp
        push ax
        mov ax, [bp + 4]
        mov [bp + 2], ax                ; IP
        mov ax, [bp + 6]
        mov [bp + 4], ax                ; CS
        mov ax, [bp + 8]
        mov [bp + 6], ax                ; flags
        mov word [bp + 8], 0            ; the word pushed
        pop ax
        pop bp
        iret

; IB_CHARGES: DX IB_CHARGES_TEXT with the charges of PROBE_ITEM_BOX's item ([BP+6]; SI its type,
; ES:BX its type's record) if it casts a spell with charges, else 0. Not for fruit (eaten whole) nor
; scenery (doors: their +0Eh and +10h hold something else). DS the game's; others kept.
ib_charges:
        xor dx, dx
        cmp si, TYPE_FRUIT
        je .ret
        push ax
        push bx
        push cx
        push es
        mov al, [es:bx + TYPE_KIND]
        and al, TYPE_SCENERY
        cmp al, TYPE_SCENERY
        je .none
        les bx, [ITEMS_PTR]
        imul ax, [bp + 6], ITEM_SIZE
        add bx, ax
        mov ax, [es:bx + ITEM_SPELL]
        or ax, ax
        jz .none
        cmp ax, SPELLS_ALL
        ja .none
        mov ax, [es:bx + ITEM_CHARGES]
        or ax, ax
        jz .none
        push di                         ; (up to 65535: five digits at most)
        mov di, ib_charges_num + 6
        mov byte [cs:di], 0
        mov cx, 10
        mov byte [cs:ib_charges_num], 0
        cmp ax, 100                     ; (a space after the colon below 100: three digits and more
        jae .digit                      ;   reach the box's INFO button with it)
        mov byte [cs:ib_charges_num], ' '
.digit: xor dx, dx
        div cx
        add dl, '0'
        dec di
        mov [cs:di], dl
        or ax, ax
        jnz .digit
        mov si, di                      ; (the digits moved to the front, after the space if any)
        mov di, ib_charges_num
        cmp byte [cs:di], ' '
        jne .move
        inc di
.move:  mov al, [cs:si]
        mov [cs:di], al
        inc si
        inc di
        or al, al
        jnz .move
        pop di
        mov dx, ib_charges_text
        jmp .out
.none:  xor dx, dx
.out:   pop es
        pop cx
        pop bx
        pop ax
.ret:   ret

; IB_MATERIAL: DX IB_HIT_TEXT with the to-hit penalty of PROBE_ITEM_BOX's item ([BP+6]; ES:BX its
; type's record) if it is a weapon (its type's dice not 0) of a weaker material with no plus: the
; type not marked 80h (clubs, staves) nor 40h (no material), its material (low nibble) wood -3, bone
; -1, stone or obsidian -2, as the game's attack has it (game.MATERIAL_TO_HIT). Else 0. DS the game's;
; others kept.
ib_material:
        xor dx, dx
        cmp byte [es:bx + TYPE_DICE], 0
        je .ret
        push ax
        push bx
        push es
        mov al, [es:bx + TYPE_KIND]
        test al, 0x80 | 0x40
        jnz .out                        ; (a club's, a staff's; 40h: no material)
        and al, 0x0F
        cmp al, 3
        ja .out                         ; (metal, leather)
        les bx, [ITEMS_PTR]
        imul dx, [bp + 6], ITEM_SIZE
        add bx, dx
        xor dx, dx
        cmp byte [es:bx + ITEM_PLUS], 0
        jne .out                        ; (a plus: none)
        movzx bx, al
        mov al, [cs:ib_hit_by + bx]
        mov [cs:ib_hit_num], al
        mov dx, ib_hit_text
.out:   pop es
        pop bx
        pop ax
.ret:   ret

ib_hit_by  db '3', '1', '2', '2'      ; (wood, bone, stone, obsidian)
ib_hit_text db 'Hit -'
ib_hit_num  db '0', 0
ib_draw    dd 0
ib_count   dw 0                     ; lines drawn (for the tests)
ib_charges_text db 'Charges:'
ib_charges_num  db '000000', 0          ; (a space, then the number, or the number alone)

; ---- THAC0, SAVES AND THIEF SKILLS ON THE INVENTORY: DSCLOG's PROBE_CHAR (its sheet's numbers) ----
; PROBE_CHAR: INT VEC_CHAR replaces "add sp,0Eh" (91286h; SL's 6F6BFh) in the inventory screen's
; routine for its right-hand panel, straight after the weapon lines. Does the add, then adds in the
; game's lettering: THAC0 and the five saving throws above STR, the DEX reaction adjustment right of
; SP, the DEX defensive adjustment right of the AC line, and for a character with thief levels six
; thief skills right of the abilities, level with STR to CHA. The routine's code holds the text
; routine's far address and the selected character's segment at the same distances before the patch
; as SL's (IV_DRAW, IV_WHO). What differs from DSCLOG's: the sequel's records (sheets 42h bytes at
; DS:19C5h: its entity +0Eh, race +12h, classes +1Bh, levels +1Eh, saves +31h-35h; creatures 31h bytes
; at DS:19C9h: THAC0 +16h, DEX +1Ah), the character's number at +0B44h, the DEX tables (DS:084Ch, 0866h),
; the thief tables (load + 449Bh:0, two more race rows: DEX limits at A0h, A8h, B0h), the abilities a
; row lower (STR at y 38h, SL's 35h); and the numbers are always the sheet's and the game's tables'
; (the Loader's STATS, with equipment and effects, and a ranger's stealth aren't ported); and with
; ages the age in the row between the saves and STR, from the sheet (RULE_HI_AGING, below).
IV_DRAW     equ -0x99           ; (from the patch) "lcall SEG:OFF" operand: the text routine
IV_WHO      equ -0x8B           ; (from the patch) "mov ax,0370h" operand: the character number's selector
WHO_OFF     equ 0x0B44
SHEETS_PTR  equ 0x19C5
SHEET_SIZE  equ 0x48                ; (the Loader's sheet: ravager.SHEET_SIZE; the game's 42h)
CREATURES_PTR equ 0x19C9
CREATURE_SIZE equ 0x31
SHEET_ENTITY equ 0x0E
SHEET_RACE  equ 0x12
SHEET_CLASSES equ 0x1B
SHEET_LEVELS equ 0x1E
SHEET_SAVES equ 0x31
CREATURE_THAC0 equ 0x16
CREATURE_DEX equ 0x1A
THIEF_CLASS equ 17
THIEF_TABLE equ 0x449B - 0x47E0 ; the thief tables' segment, relative to DS
THIEF_RACE  equ 8
THIEF_LOW   equ 0xA0
THIEF_HIGH  equ 0xA8
THIEF_TOP   equ 0xB0
DEX_REACTION equ 0x084C         ; DS: the DEX reaction adjustment (bytes, by score: SL's 7DCh)
DEX_DEFENCE equ 0x0866          ; DS: the DEX defensive adjustment (on AC: SL's 7F6h)
NO_REACT    equ 0x80
REACT_Y     equ 0x22            ; the saves' last row, right of SP
REACT_VALUE_X equ 0x130
DEF_Y       equ 0x71            ; the AC line's y
DEF_VALUE_X equ 0x12D
; ages (RULE_HI_AGING, the Loader's aging.py): the age at the sheet's +41h, a byte the sequel's program
; never touches (the Loader's SHEET_AGE there): the years past the race's base starting age, + 1 (0 none)
RULE_HI_AGING equ 256
SHEET_AGE   equ 0x41
AGE_RACES   equ 8
AGE_Y       equ 0x2D            ; (the free row between SP's at 22h and STR's at 38h)
probe_char:
        pop word [cs:t_ip]
        pop word [cs:t_cs]
        pop word [cs:t_fl]
        add sp, 0x0E            ; the replaced instruction
        sti
        pushad
        push es
        push fs
        push gs
        mov es, [cs:t_cs]
        mov di, [cs:t_ip]
        sub di, 2               ; ES:DI = the patch
        mov eax, [es:di + IV_DRAW]
        mov [cs:c_draw], eax
        mov fs, [es:di + IV_WHO]
        mov eax, [WIN_SHOWN]    ; the panel's window
        mov [cs:c_winptr], eax
        mov bx, [fs:WHO_OFF]    ; the character on show
        cmp bx, 3
        ja .done
        mov [cs:c_who], bx
        imul ax, bx, SHEET_SIZE
        les si, [SHEETS_PTR]
        add si, ax              ; ES:SI = the character sheet
        cmp word [es:si + SHEET_ENTITY], 0
        je .done                ; an empty slot
        imul bx, bx, CREATURE_SIZE
        lfs di, [CREATURES_PTR]
        add di, bx              ; FS:DI = the creature record
        inc word [cs:char_count]
        mov al, [fs:di + CREATURE_THAC0]  ; THAC0 and the saves
        mov [cs:c_vals], al
        mov eax, [es:si + SHEET_SAVES]
        mov [cs:c_vals + 1], eax
        mov al, [es:si + SHEET_SAVES + 4]
        mov [cs:c_vals + 5], al
        mov bx, c_cells_top
        mov byte [cs:c_signed], 1  ; (THAC0 can be below 0)
        mov cx, 6
        call c_cells
        mov byte [cs:c_react], NO_REACT ; the DEX adjustments, worked out now
        movzx bx, byte [fs:di + CREATURE_DEX]
        cmp bx, 26
        jae .thieves
        mov al, [bx + DEX_REACTION]
        mov [cs:c_react], al
        mov al, [bx + DEX_DEFENCE]
        mov [cs:c_defence], al
.thieves:
        xor cx, cx              ; thief skills, for a character with thief levels
        mov bx, SHEET_CLASSES
.cls:   cmp byte [es:si + bx], THIEF_CLASS
        je .thief
        inc bx
        inc cx
        cmp cx, 3
        jb .cls
        jmp .react
.thief: mov al, [es:si + bx + 3]  ; the thief level (levels follow the classes)
        call c_thief
.react: test word [cs:rules_hi], RULE_HI_AGING  ; the age (the Loader's: SHEET_AGE) in the free
        jz .reac                        ;   row between the saves and STR, "AGE: 23"
        movzx ax, byte [es:si + SHEET_AGE]
        or ax, ax
        jz .reac                        ; (none given yet)
        movzx bx, byte [es:si + SHEET_RACE]
        dec bx
        cmp bx, AGE_RACES
        jae .reac
        movzx bx, byte [cs:age_bases + bx]
        lea ax, [eax + ebx - 1]         ; the race's base starting age, + the byte - 1
        mov di, c_age_n
        call c_wtoa
        push word AGE_Y
        push word 0xEC
        push cs
        push word c_age
        call c_draw_line
.reac:  mov al, [cs:c_react]      ; right of SP in the saves: "REAC +4"
        cmp al, NO_REACT
        je .done
        mov di, c_num
        test al, al
        jle .sign
        mov byte [cs:di], '+'
        inc di
.sign:  call c_itoa_s
        push word REACT_Y
        push word 0x113
        push cs
        push word l_react
        call c_draw_line
        push word REACT_Y
        push word REACT_VALUE_X
        push cs
        push word c_num
        call c_draw_line
        mov al, [cs:c_defence]    ; right of the AC line: "DEF -4"
        mov di, c_num
        test al, al
        jle .dsign
        mov byte [cs:di], '+'
        inc di
.dsign: call c_itoa_s
        push word DEF_Y
        push word 0x113
        push cs
        push word l_defence
        call c_draw_line
        push word DEF_Y
        push word DEF_VALUE_X
        push cs
        push word c_num
        call c_draw_line
.done:
        pop gs
        pop fs
        pop es
        popad
        push word [cs:t_fl]
        push word [cs:t_cs]
        push word [cs:t_ip]
        iret

; C_THIEF: DSCLOG's, from the sequel's tables: the six thief skills shown (sheet ES:SI, creature
; FS:DI, thief level AL): base + 4 a level + the race's adjustment + DEX's (before equipment and
; effects); with Thieves as in AD&D (RULE_THIEF_TABLE) AD&D's average for the level +
; the race's + Dark Sun's DEX adjustment, no more than THIEF_MOST, as the thief skill routine has them
; (THIEF_SKILL).
c_thief:
        push si
        mov dl, al
        shl dl, 2               ; 4 a level
        mov ax, ds
        add ax, THIEF_TABLE
        mov gs, ax
        mov dh, [fs:di + CREATURE_DEX]
        movzx di, byte [es:si + SHEET_RACE]
        shl di, 3
        add di, THIEF_RACE      ; + race * 8
        xor bx, bx
.skill: movsx ax, byte [gs:bx + di]  ; race
        test word [cs:rules], RULE_THIEF_TABLE
        jz .game
        push si                 ; (Thieves as in AD&D: AD&D's average and Dark Sun's DEX, THIEF_ADND)
        push ax
        movzx si, dl
        shr si, 2
        movzx cx, dh
        call thief_adnd
        pop cx
        pop si
        add ax, cx
        cmp ax, THIEF_MOST
        jle .sum
        mov ax, THIEF_MOST
        jmp .sum
.game:  movsx cx, byte [gs:bx]  ; base
        add ax, cx
        movzx cx, dl
        add ax, cx
        push dx                 ; DEX: -5 a point below LOW, +5 a point above HIGH, -3 above TOP
        movzx dx, dh
        movzx cx, byte [gs:bx + THIEF_LOW]
        sub cx, dx
        jle .nolow
        imul cx, cx, 5
        sub ax, cx
.nolow: mov cx, dx
        push dx
        movzx dx, byte [gs:bx + THIEF_HIGH]
        sub cx, dx
        pop dx
        jle .nohigh
        imul cx, cx, 5
        add ax, cx
.nohigh:
        mov cx, dx
        push dx
        movzx dx, byte [gs:bx + THIEF_TOP]
        sub cx, dx
        pop dx
        jle .notop
        imul cx, cx, 3
        sub ax, cx
.notop: pop dx
.sum:
        cmp ax, 0
        jge .pos
        xor ax, ax              ; below 0: shown as 0
.pos:   cmp ax, 255
        jbe .fits
        mov ax, 255
.fits:  mov [cs:c_vals + bx], al
        inc bx
        cmp bx, 8
        jb .skill
        pop si
        mov al, [cs:c_vals + 6] ; pick pockets, open locks, find traps, move silently, hide in
        mov [cs:c_vals + 5], al ; shadows and climb walls (not hear noise nor read languages)
        mov bx, c_cells_thief
        mov cx, 6
        mov byte [cs:c_signed], 0
        ; fall through

; C_CELLS: DSCLOG's: CX cells at CS:BX, each x, y, label offset, value's x (words); the values are
; C_VALS in order. Keeps ES, SI, DI.
        SHARED_c_cells

        SHARED_c_itoa

c_wtoa:                         ; AX (unsigned) -> decimal at CS:DI, NUL-terminated; keeps BX, CX
        push bx
        push cx
        push dx
        mov bx, 10
        xor cx, cx
.div:   xor dx, dx
        div bx
        push dx
        inc cx
        or ax, ax
        jnz .div
.put:   pop ax
        add al, '0'
        mov [cs:di], al
        inc di
        loop .put
        mov byte [cs:di], 0
        pop dx
        pop cx
        pop bx
        ret

        SHARED_c_itoa_s

; cells: x, y, label, value's x (window coordinates, as DSCLOG's: the stats' labels at x 0ECh)
        SHARED_c_cells_top
c_cells_thief:                  ; right of the abilities, level with STR..CHA (the sequel's rows: 38h on)
        dw 0x113, 0x38, l_pick, 0x12D
        dw 0x113, 0x3F, l_lock, 0x12D
        dw 0x113, 0x46, l_trap, 0x12D
        dw 0x113, 0x4D, l_move, 0x12D
        dw 0x113, 0x54, l_hide, 0x12D
        dw 0x113, 0x5B, l_clmb, 0x12D
l_thac0 db 'THAC0:', 0
l_ppd   db 'PPD', 0
l_rsw   db 'RSW', 0
l_pp    db 'PP', 0
l_bw    db 'BW', 0
l_sp    db 'SP', 0
l_pick  db 'PICK', 0
l_lock  db 'LOCK', 0
l_trap  db 'TRAP', 0
l_move  db 'SLNT', 0
l_hide  db 'HIDE', 0
l_clmb  db 'CLMB', 0
l_react db 'REAC', 0
c_age   db 'AGE: '
c_age_n times 6 db 0
age_bases db 15, 25, 15, 15, 20, 25, 15, 6  ; the races' base starting ages (Table 7: aging.RACES)
l_defence db 'DEF', 0
c_react db 0
c_defence db 0
c_signed db 0
c_who   dw 0
c_vals  times 8 db 0
c_num   db 0, 0, 0, 0, 0
t_ip    dw 0
t_cs    dw 0
t_fl    dw 0
char_count dw 0                 ; panels drawn on (for the tests)

;---- the Look box: DSCLOG's PROBE_LOOK ----
; PROBE_LOOK: INT VEC_LOOK replaces "mov si,ax / mov word [bp-0Ah],0" (640FBh, 7 bytes: INT + 5 NOPs;
; SL's "mov si,ax / xor di,di" at 5FCDAh) in the routine that fills the Look box (a creature looked at
; in a fight), where its first status rows have been drawn and AX says how many. Asks the Loader for up
; to three short lines about the monster (LOOK_TEXT), prints them in the rows left with the game's text
; routine, as the box prints the monster's level, and moves the game's row count past them, so its own
; status lines follow in any row still free. The routine is SL's but for: the combatant in DI (SL's
; [BP+0Ah]), the status lines' count in [BP-0Ah] (SL's DI), the text routine's far address -20h from the
; patch (SL's -22h), the box's colours F3h, AFh (SL's 1Fh, 11h). If the Loader also gave the whole
; description (LOOK_FULL), UNLOOK shows it in the dialogue window as the box closes.
LOOK_DRAW  equ -0x20            ; (from the patch) "lcall SEG:OFF" operand: the text routine
LOOK_ROWS  equ 4                ; the box's status rows: y = (row + 2) * 7 + 10h
LOOK_SIDE  equ 1                ; a line starting with this goes on LEVEL's row (row -1), to its right
LOOK_SIDE_X equ 60              ;   at this x (past LEVEL: 10)
LOOK_INK   equ 0xF3             ; the box's colours (its "push dword 00AF00F3h")
LOOK_PAPER equ 0xAF
LOOK_SIZE  equ 80
probe_look:
        sti
        pushad
        push es
        mov si, sp              ; SS:SI: ES, then EDI, ESI, EBP, ESP, EBX, EDX, ECX, EAX, IP, CS, flags
        mov ax, [ss:si + 30]
        mov [cs:l_row], ax      ; the rows the game has used
        cmp word [cs:look_on], 0
        je .done
        call loader_fresh
        jne .done
        mov [cs:look_who], di   ; the combatant
        mov byte [cs:look_text], 0
        push fs
        call tail_fs
        mov byte [fs:look_full], 0      ; (the tail's)
        pop fs
        inc word [cs:look_seq]
        xor ax, ax
        mov es, ax
        mov dx, [es:0x46C]      ; the BIOS timer
        call rtc_begin
.wait:  mov ax, [cs:look_reply]
        cmp ax, [cs:look_seq]
        je .ready
        mov ax, [es:0x46C]
        sub ax, dx
        cmp ax, LOOK_WAIT
        jae .done               ; no answer: the Loader isn't reading
        call rtc_waited         ; (the BIOS clock can stand still: at most 2 s by the real-time clock)
        jnc .wait
        jmp .done
.ready: push fs
        call tail_fs
        cmp byte [fs:look_full], 0
        pop fs
        je .short
        mov byte [cs:look_pending], 1   ; (the whole description: UNLOOK's, as the box closes)
.short: mov es, [ss:si + 36]
        mov di, [ss:si + 34]
        sub di, 2               ; ES:DI = the patch
        mov eax, [es:di + LOOK_DRAW]
        mov [cs:l_draw], eax
        mov eax, [bp + 6]       ; the box's window
        mov [cs:l_win], eax
        mov di, look_text
.line:  mov byte [cs:l_side], 0
        cmp byte [cs:di], LOOK_SIDE
        jne .rows
        inc di
        mov byte [cs:l_side], 1
        jmp .take
.rows:  cmp word [cs:l_row], LOOK_ROWS
        jae .done
        cmp byte [cs:di], 0
        je .done
.take:  mov bx, l_line          ; the next line, up to "|", into L_LINE
.copy:  mov al, [cs:di]
        cmp al, '|'
        je .cut
        or al, al
        je .cut
        cmp bx, l_line + L_LINE_SIZE - 1
        jae .skip
        mov [cs:bx], al
        inc bx
.skip:  inc di
        jmp .copy
.cut:   mov byte [cs:bx], 0
        cmp byte [cs:di], '|'
        jne .draw
        inc di
.draw:  push di
        mov ax, [cs:l_row]
        mov cx, 6
        cmp byte [cs:l_side], 0
        je .at
        mov ax, -1              ; (LEVEL's row, above the status rows, to its right)
        mov cx, LOOK_SIDE_X
.at:    add ax, 2
        imul ax, ax, 7
        add ax, 0x10
        push word LOOK_PAPER    ; as the box prints LEVEL
        push word LOOK_INK
        push ax                 ; y
        push cx                 ; x
        push cs
        push word l_line
        push dword [cs:l_win]
        call far [cs:l_draw]
        add sp, 16
        pop di
        cmp byte [cs:l_side], 0
        jne .line               ; (beside LEVEL: no row of its own)
        inc word [cs:l_row]
        jmp .line
.done:  mov ax, [cs:l_row]      ; the replaced code: SI = the rows used, [BP-0Ah] = 0
        mov si, sp
        mov [ss:si + 6], ax
        mov word [bp - 0x0A], 0
        inc word [cs:look_count]
        pop es
        popad
        iret
LOOK_WAIT equ 7                 ; timer ticks (55 ms each) the Loader has to answer (DSCLOG's TURN_WAIT)
L_LINE_SIZE equ 24
l_row    dw 0
l_side   db 0
l_draw   dd 0
l_win    dd 0
l_line   times L_LINE_SIZE db 0
look_count dw 0                 ; boxes filled (for a look in play)
look_text times LOOK_SIZE db 0  ; (LOOK_OFF's)
LOOK_FULL_SIZE equ 700
section tailz
look_full times LOOK_FULL_SIZE db 0 ; (LOOK_FULL_OFF's: the tail's)
section image
look_pending db 0               ; 1 once LOOK_FULL has a description UNLOOK hasn't shown

; UNLOOK (site 75 at 6378Dh, "mov word [08CAh],270Fh", SL's PROBE_UNLOOK at 5F2AAh): the end of the routine
; that closes the Look box (the game forgets whom it was looking at). Does that, then shows the monster's
; whole description (LOOK_FULL) in the dialogue window (SHOW_WINDOW), in a frame the overlay manager can fix
; up (the window may load other overlays over this routine's while it waits for Continue).
unlook:
        mov word [0x8CA], 0x270F  ; the replaced instruction (DS the game's)
        sti
        pushad
        push es
        cmp byte [cs:look_pending], 0
        je .out
        cmp byte [cs:showing], 0
        jne .out
        mov byte [cs:look_pending], 0
        inc word [cs:unlook_count]
        mov word [cs:show_text], look_full
        mov byte [cs:show_tail], 1      ; (LOOK_FULL: the tail's)
        mov bx, sp              ; the frame at BX+34: IP, CS, flags
        push word [ss:bx + 36]  ; the way back, pushed as a far call's, with BP
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        call show_window
        pop bp
        pop ax                  ; (the way back, as the overlay manager has left it)
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
.out:   pop es
        popad
        iret
unlook_count dw 0               ; (descriptions shown, for a look in play)

; SHOPS AS IN AD&D: SL's CHA_PRICE, PROBE_PRICE, PROBE_PRICE_EAX, SELL_PRICE and SELL_KEEP
; (RULE_HI_CHA_PRICES, the Loader's "cha_prices", always on; dsloader/prices.py), on the sequel's shop
; (90xxxh, SL's 83xxxh). Its item records are 17h bytes (DS:19C1h), the price the word at +6 as SL's;
; the shop's own markups (370h:36h buying, 34h selling: 914A5h, 915B8h, a shopkeeper's discount) are
; worked out after, from the price these give. Each site does the instruction it replaces first.
; - PRICE_CX (site 54, "price_shown"): "mov cx,[es:bx+6]" (90E2Ah; 4 bytes), the price under an item.
; - PRICE_EAX (site 55, "price_afford", "price_buy"): "movzx eax,word [es:bx+6]" (9036Ch, the list
;   greying what the party can't afford; 90AA7h, the price charged; 6 bytes).
; - SELL_PRICE (site 56, "sell_price"): "movzx eax,word [es:bx+6]" (90F4Dh; 6 bytes), what the shop
;   offers and pays: SELL_PERCENT of it (rounded down, never below 1; 9999 kept), so nothing bought at
;   the best discount sells for more than it cost (prices.sell_price).
; - SELL_KEEP (site 57, "sell_keep"): "push word [1A32h]" (91043h; 4 bytes) where the shop has paid and
;   frees the item list of the thing holding the item sold (the pointer's, 523; c8:2410h, which does
;   nothing for 270Fh). A magical item (a plus, +16h, or a power, +10h: scrolls, rings, wands...),
;   the only one on the pointer, goes first into the last item list of the shop's merchant (the thing
;   DS:1A30h, a creature, its lists at +08h, +0Ah, +0Ch), in a backpack cell no item of the merchant's
;   holds (+13h: 14-25; the pack full, its own kept), where the shop lists it; the pointer's thing
;   emptied as the game leaves it (all 0) and 270Fh pushed. Anything else is pushed and freed as the
;   game does. All in the game's own call: no Loader (SL's needed one to move the item).
; The leader is the member whose turn it is out of a fight (DS:426Dh), its CHA the creature's +1Eh.
RULE_HI_CHA_PRICES equ 16
CHA_PRICE_FIRST equ 18          ; (prices.CHA_FIRST: 5% off at CHA 18, 5% more a point ...)
CHA_PRICE_STEPS equ 8           ; (... to 40% at CHA 25)
SELL_PERCENT equ 60
CREATURE_CHA  equ 0x1E
SHOP_MERCHANT equ 0x1A30        ; DS: the shop's merchant (a thing) ...
SOLD_THING    equ 0x1A32        ; ... and the thing holding the item sold
ITEM_PLUS_AT  equ 0x16
ITEM_POWER_AT equ 0x10
ITEM_SLOT_AT  equ 0x13
THING_ITEMS   equ 1
THING_PERSON  equ 2
THING_COUNT   equ 520           ; (the things past it the game's own: the pointer's 523)
PACK_FIRST    equ 14            ; (the backpack's cells, 14-25: 0-13 worn)
PACK_CELLS    equ 12
SELL_ITEMS_MOST equ 200         ; (a list walked no further: a torn one)
cha_price:
        test word [cs:rules_hi], RULE_HI_CHA_PRICES
        jz .out
        cmp cx, NO_ITEM
        je .out
        jcxz .out
        push ax
        push bx
        push dx
        push es
        mov bx, [WHOSE_TURN]
        cmp bx, 3
        ja .done
        les ax, [CREATURES_PTR]
        imul bx, bx, CREATURE_SIZE
        add bx, ax
        mov al, [es:bx + CREATURE_CHA]
        sub al, CHA_PRICE_FIRST - 1
        jle .done
        cmp al, CHA_PRICE_STEPS
        jbe .pct
        mov al, CHA_PRICE_STEPS
.pct:   mov ah, 5
        mul ah                          ; (AX the discount in %)
        mov bx, 100
        sub bx, ax
        mov ax, cx
        mul bx
        mov bx, 100
        div bx
        or ax, ax
        jnz .set
        inc ax
.set:   mov cx, ax
        inc word [cs:cha_prices]
.done:  pop es
        pop dx
        pop bx
        pop ax
.out:   ret
price_cx:
        mov cx, [es:bx + 6]
        call cha_price
        iret
price_eax:
        push cx
        mov cx, [es:bx + 6]
        call cha_price
        movzx eax, cx
        pop cx
        iret
sell_price:
        movzx eax, word [es:bx + 6]
        test word [cs:rules_hi], RULE_HI_CHA_PRICES
        jz .out
        cmp ax, NO_ITEM
        je .out
        cmp ax, 1
        jbe .out
        push edx
        imul eax, eax, SELL_PERCENT
        xor edx, edx
        push ecx
        mov ecx, 100
        div ecx
        pop ecx
        pop edx
        or eax, eax
        jnz .out
        inc eax
.out:   iret
sell_keep:
        push ax
        push bx
        push cx
        push dx
        push si
        push di
        push es
        push fs
        mov cx, [SOLD_THING]
        test word [cs:rules_hi], RULE_HI_CHA_PRICES
        jz .push
        cmp cx, NO_ITEM
        jae .push
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov fs, ax
        imul si, cx, 3                  ; (FS:SI+FIGHTERS_OFF the thing sold)
        cmp byte [fs:si + FIGHTERS_OFF], THING_ITEMS
        jne .push
        mov ax, [fs:si + FIGHTERS_OFF + 1]
        cmp ax, NO_ITEM
        jae .push
        les bx, [ITEMS_PTR]
        imul di, ax, ITEM_SIZE
        add di, bx                      ; (ES:DI the item)
        cmp word [es:di + 4], NO_ITEM   ; (the only one on the pointer)
        jb .push
        cmp byte [es:di + ITEM_PLUS_AT], 0
        jg .magic
        cmp word [es:di + ITEM_POWER_AT], 0
        je .push
.magic: mov bx, [SHOP_MERCHANT]
        cmp bx, THING_COUNT
        jae .push
        imul bx, bx, 3
        cmp byte [fs:bx + FIGHTERS_OFF], THING_PERSON
        jne .push
        push es
        push di
        mov dx, [fs:bx + FIGHTERS_OFF + 1]      ; (the merchant's creature)
        imul dx, dx, CREATURE_SIZE
        mov [cs:sk_merchant], dx
        mov dx, NO_ITEM                 ; (DX its last list of items, a thing)
        mov word [cs:sk_cells], 0
        push si
        mov si, 8
.list:  les bx, [CREATURES_PTR]
        add bx, [cs:sk_merchant]        ; (ES:BX the merchant)
        mov ax, [es:bx + si]
        cmp ax, THING_COUNT
        jae .nextl
        push bx
        imul bx, ax, 3
        cmp byte [fs:bx + FIGHTERS_OFF], THING_ITEMS
        jne .nl
        mov dx, ax
        mov ax, [fs:bx + FIGHTERS_OFF + 1]
        call sk_used                    ; (its items' backpack cells marked in SK_CELLS)
.nl:    pop bx
.nextl: add si, 2
        cmp si, 0x0E
        jb .list
        pop si
        pop di
        pop es
        cmp dx, NO_ITEM
        je .push                        ; (no list: freed, as the game does)
        imul bx, dx, 3                  ; (FS:BX the merchant's list)
        mov ax, [fs:bx + FIGHTERS_OFF + 1]
        mov [es:di + 4], ax             ; (the item first in it ...
        mov ax, [fs:si + FIGHTERS_OFF + 1]
        mov [fs:bx + FIGHTERS_OFF + 1], ax
        mov ax, [cs:sk_cells]           ;  ... in a free cell of the pack)
        xor dl, dl
.cell:  test ax, 1
        jz .free
        shr ax, 1
        inc dl
        cmp dl, PACK_CELLS
        jb .cell
        jmp .empty
.free:  add dl, PACK_FIRST
        mov [es:di + ITEM_SLOT_AT], dl
.empty: cmp cx, THING_COUNT             ; (the thing sold emptied: the pointer's all 0)
        jb .one
        mov byte [fs:si + FIGHTERS_OFF], 0
        mov word [fs:si + FIGHTERS_OFF + 1], 0
        jmp .kept
.one:   mov word [fs:si + FIGHTERS_OFF + 1], NO_ITEM
.kept:  inc word [cs:sold_kept]
        mov cx, NO_ITEM
.push:  mov bx, sp                      ; (SS:BX: FS, ES, DI, SI, DX, CX, BX, AX, then IP, CS, flags)
        sub sp, 2
        mov dx, 11
.down:  mov ax, [ss:bx]
        mov [ss:bx - 2], ax
        add bx, 2
        dec dx
        jnz .down
        mov [ss:bx - 2], cx             ; (the word pushed)
        pop fs
        pop es
        pop di
        pop si
        pop dx
        pop cx
        pop bx
        pop ax
        iret
; SK_USED: the backpack cells of the items in the list from AX (ES the items' segment once ITEMS_PTR's)
; marked in SK_CELLS. ES, AX, BX changed.
sk_used:
        push cx
        push di
        mov cx, SELL_ITEMS_MOST
.item:  cmp ax, NO_ITEM
        jae .ret
        les di, [ITEMS_PTR]
        imul ax, ax, ITEM_SIZE
        add di, ax
        mov al, [es:di + ITEM_SLOT_AT]
        sub al, PACK_FIRST
        jb .next
        cmp al, PACK_CELLS
        jae .next
        push cx
        mov cl, al
        mov ax, 1
        shl ax, cl
        or [cs:sk_cells], ax
        pop cx
.next:  mov ax, [es:di + 4]
        loop .item
.ret:   pop di
        pop cx
        ret
sk_cells   dw 0
sk_merchant dw 0
cha_prices dw 0                 ; (prices lowered, for a look in play)
sold_kept  dw 0                 ; (magical items kept by a merchant, for a look in play)

; MESSAGES SHOWN: the sequel's message box (560h:2Ah, 59A0Bh; SL's 4D0h:2Ah, which waits in the game's
; event loop) opens its window (5B0h:48h, kept at 300h:7, 59AD3h), puts the text in it and then waits
; [26B7h] x 100 ms (the options' message time, 5 seconds at first: 59B62h) with the game's delay (0:12FAh)
; before closing it. The game draws its windows only when it shows a new picture (3328h:0B4Ch: the
; windows drawn, 309Bh:1675h, on the screen not on show, then the two screens flipped, 0BF3h:5814h), which
; its main loop does: so the box was never seen (the scroll's messages, I COULDN'T SELL THAT and the
; rest of the 56 calls).
; - MSG_WINDOW (site 59, "message_window"): "mov [es:9],dx" (59AD3h; 5 bytes), the window just opened
;   (counted).
; - MSG_SHOWN (site 58, "message_shown"): "mov ax,[26B7h]" (59B62h; 3 bytes), the wait about to start: a
;   new picture shown first, as the routine's own call before the text does (0B0h:2A81h with 1: drawing
;   allowed, the picture marked new, 3328h:0B4Ch), so the box is on screen while the game waits. A left
;   or right click (MOUSE_EVENT) or a key (INT16) ends the wait at once and goes no further, as Shattered
;   Lands' box (its event loop, 4D0h:2Ah) takes the click or key that closes it.
MSG_TIME     equ 0x26B7
MSG_DRAW_SEG equ 0x18C9 - 0x47E0   ; (selector 0B0h's segment, the root's, less DS's)
MSG_DRAW_OFF equ 0x2A81
msg_draw dd 0
msg_window:
        mov [es:9], dx
        inc word [cs:msg_windows]
        iret
msg_shown:
        inc word [cs:msg_waits]
        pusha
        push es
        mov ax, ds
        add ax, MSG_DRAW_SEG
        mov word [cs:msg_draw], MSG_DRAW_OFF
        mov [cs:msg_draw + 2], ax
        push word 1
        call far [cs:msg_draw]
        add sp, 2
        mov ax, [MSG_TIME]              ; (tenths of a second: in BIOS ticks, x 100 / 55)
        mov dx, 100
        mul dx
        mov cx, 55
        div cx
        mov cx, ax
        xor ax, ax
        mov es, ax
        mov bx, [es:0x46C]
        mov byte [cs:msg_ended], 0
        mov byte [cs:msg_waiting], 1
        sti
.wait:  cmp byte [cs:msg_ended], 0      ; (a click or a key: the box closed, as Shattered Lands' does)
        jne .ended
        mov ax, [es:0x46C]
        sub ax, bx
        cmp ax, cx
        jb .wait
.ended: mov byte [cs:msg_waiting], 0
        pop es
        popa
        xor ax, ax                      ; (the game's own wait: none left)
        iret
msg_waiting db 0                ; (1 while MSG_SHOWN waits: a press or a key ends it, MSG_ENDED, and
msg_ended   db 0                ;   isn't the game's: MOUSE_EVENT, INT16)
msg_windows dw 0                ; (message windows opened, for a look in play)
msg_waits   dw 0                ; (waits shown)

; TEXT: DSCLOG's PROBE_TEXT and PROBE_MSG, what the game shows as text copied into the text buffer (the
; far block's FAR_TBUF, TSIZE bytes, its write position TPOS: header +126 to +138, DSCLOG's) for the
; Loader's Dialogue and Journal tabs and the dice log's "Message:" lines (textlog.py: each record FEh, the
; kind, the far pointer, the word, the text's length and the text, at most 400 bytes). Both are SITEs on
; the routine's "push bp / mov bp,sp" (3 bytes), done after the record as DSCLOG's do:
; - PROBE_TEXT (site 93, "text"): the dialogue window's input (87BA0h, SL's 7CE83h; the sequel's dialogue
;   stub 476Ch's entry 25h, SHOW_WINDOW's DLG_FEED): (kind, far text, word), the kinds as SL's (0 a reply,
;   1 a portrait, the word its number, 2 text, 3 the replies shown). Not DSCLOG's SWAP (the arena ring's
;   search: SL's story).
; - PROBE_MSG (site 94, "message"): the message box (560h:2Ah, 59A0Bh; SL's 4D0h:2Ah, 5536Eh): (far text),
;   recorded as kind 16.
probe_text:
        call text_enter         ; SS:BP+16 = the routine's arguments
        inc word [cs:text_records]
        mov cl, [bp+16]
        lds si, [bp+18]
        mov dx, [bp+22]
        jmp text_leave

probe_msg:
        call text_enter
        inc word [cs:msg_records]
        mov cl, 16
        lds si, [bp+16]
        xor dx, dx
        jmp text_leave

text_enter:                     ; take the interrupt frame off, save registers, BP = SP (DSCLOG's)
        pop word [cs:xt_ret]
        pop word [cs:xt_ip]      ; the routine's stack is underneath the interrupt frame
        pop word [cs:xt_cs]
        pop word [cs:xt_fl]
        sti
        push ax
        push bx
        push cx
        push dx
        push si
        push ds
        push bp
        mov bp, sp              ; SS:BP+14 = return address of the routine, +18 its arguments
        add bp, 2               ; ... so that +16 is the first argument
        jmp [cs:xt_ret]

text_leave:                     ; record CL = kind, DS:SI = dword, DX = word, then return (DSCLOG's)
        mov bx, [cs:tpos]
        mov al, 0xFE
        call tput
        mov al, cl
        call tput
        mov ax, si
        call tputw
        mov ax, ds
        call tputw
        mov ax, dx
        call tputw
        xor ax, ax
        cmp cl, 0
        je .text
        cmp cl, 2
        je .text
        cmp cl, 16
        jne .len                ; the other kinds have no text (and no pointer)
.text:
        mov ax, ds
        or ax, si
        jz .len
        push si
        xor ax, ax
.count:
        cmp byte [si], 0
        je .counted
        inc si
        inc ax
        cmp ax, 400
        jb .count
.counted:
        pop si
.len:
        mov cx, ax
        call tputw
        jcxz .done
.copy:
        lodsb
        call tput
        loop .copy
.done:
        mov [cs:tpos], bx       ; publish the record
        pop bp
        pop ds
        pop si
        pop dx
        pop cx
        pop bx
        pop ax
        push bp                 ; the replaced instructions
        mov bp, sp
        push word [cs:xt_fl]
        push word [cs:xt_cs]
        push word [cs:xt_ip]
        iret

tput:                           ; AL -> text buffer at position BX (DSCLOG's)
        push bx
        push es
        and bx, TSIZE - 1
        mov es, [cs:far_seg]
        mov [es:FAR_TBUF + bx], al
        pop es
        pop bx
        inc bx
        ret

        SHARED_tputw

xt_ret  dw 0                   ; (TEXT's own: the other probes' T_IP, T_CS and T_FL may be in use)
xt_ip   dw 0
xt_cs   dw 0
xt_fl   dw 0
text_records dw 0               ; (the dialogue window's inputs recorded, for a look in play)
msg_records  dw 0               ; (message boxes recorded)

; SHOW_WINDOW: DSCLOG's: the text at CS:SHOW_TEXT in the game's dialogue window (its stub 476Ch, SL's 42CAh:
; the entries 25h, the window's input, and 34h, the wait for a reply, as SL's), with "Press continue" and
; one reply, Continue, until it's clicked, then the window closed. DS the game's.
DLG_STUB  equ 0x476C - 0x47E0   ; the stub's segment less DS's
DLG_FEED  equ 0x25              ; the window's input: (kind, far text, word)
DLG_WAIT  equ 0x34              ; wait for a reply to be clicked
S_PRESS   equ 0x1956            ; DS: "Press continue" (SL's 15E8h)
S_CONT    equ 0x1965            ; DS: "Continue" (15F7h)
S_CLOSE   equ 0x25C8            ; DS: "CLOSE" (1F11h)
show_window:
        mov byte [cs:showing], 1
        mov ax, ds
        add ax, DLG_STUB
        mov [cs:dlg + 2], ax
        mov word [cs:dlg], DLG_FEED
        xor bx, bx
        push word 0             ; the emblem (portrait 0)
        push bx
        push bx
        push word 1
        call far [cs:dlg]
        add sp, 8
        push word 0             ; the text: in this segment, or with SHOW_TAIL the tail's
        mov ax, cs
        cmp byte [cs:show_tail], 0
        je .here
        add ax, TAIL_PARAS
        mov byte [cs:show_tail], 0
.here:  push ax
        push word [cs:show_text]
        push word 2
        call far [cs:dlg]
        add sp, 8
        push word 0             ; "Press continue": the replies' title, then the one reply
        push ds
        push word S_PRESS
        push word 0
        call far [cs:dlg]
        add sp, 8
        push word 0
        push ds
        push word S_CONT
        push word 0
        call far [cs:dlg]
        add sp, 8
        push word 0             ; show the reply
        push dword 0
        push word 3
        call far [cs:dlg]
        add sp, 8
        mov word [cs:dlg], DLG_WAIT
        call far [cs:dlg]       ; until it's clicked
        mov word [cs:dlg], DLG_FEED
        push word 0             ; and close the window
        push ds
        push word S_CLOSE
        push word 2
        call far [cs:dlg]
        add sp, 8
        mov byte [cs:showing], 0
        ret
show_text dw 0                  ; the text SHOW_WINDOW shows
show_tail db 0                  ; 1: SHOW_TEXT is in the tail (once: SHOW_WINDOW clears it)
dlg     dd 0                    ; the dialogue window routine being called
showing db 0                    ; 1 while SHOW_WINDOW has its window up

; ---- ITEM NAMES: the mod's items' names, past the game's 256 ----
; The game's item names are RESOURCE.GFF's TEXT 1000, a name a line, read into a table of 256 far
; pointers at DS:56F3h (line k is name k + 1, name 0 the first line too): more lines run past the
; table and break the game (playtest/logs/2026-11-22-ravager-item-types.md). An item names its entry by
; a word (+14h), and the game's 7 reads of the table, "push dword [bx+56F3h]" with BX the number x4
; (59296h, 716A3h, 75E36h, 75E81h, 93AAAh, 95027h, 95052h: the inventory, the item box, the shops...),
; are SITE_NAME: name 256 on is ITEM_NAMES' (the Loader's, from the party transfer), an empty name past them.
NAMES_TABLE equ 0x56F3
NAMES_GAME  equ 256
name_push:
        pop word [cs:np_ip]
        pop word [cs:np_cs]
        pop word [cs:np_fl]
        cmp bx, NAMES_GAME * 4
        jb .game
        cmp bx, (NAMES_GAME + NAMES_ROOM) * 4
        jae .none
        push cs
        push ax
        mov ax, bx
        sub ax, NAMES_GAME * 4
        shl ax, 2                   ; (x4 to x16: NAME_KEPT)
        add ax, item_names
        push bp
        mov bp, sp
        xchg ax, [bp + 2]           ; (the offset in place of the AX pushed, AX back)
        add word [bp + 4], TAIL_PARAS   ; (and the tail's segment in place of CS: ITEM_NAMES is there)
        pop bp
        jmp .back
.none:  push cs
        push word no_name
        jmp .back
.game:  push dword [bx + NAMES_TABLE]
.back:  push word [cs:np_fl]
        push word [cs:np_cs]
        push word [cs:np_ip]
        iret
np_ip   dw 0
np_cs   dw 0
np_fl   dw 0
no_name db 0

; RTC_BEGIN, RTC_WAITED: DSCLOG's: a wait for the Loader ends after its BIOS ticks, or, as the BIOS
; clock can stand still in fights, once the real-time clock's second has changed twice (1 to 2 s)
        SHARED_rtc_begin
        SHARED_rtc_waited
        SHARED_rtc_second
w_sec   db 0
w_flips db 0

; ---- View Character: DSCLOG's PROBE_VIEW ----
; PROBE_VIEW: INT VEC_VIEW replaces "push dword 000B0140h" (987FBh, SL's 8A471h; 6 bytes: INT + 4 NOPs)
; near the end of the View Character screen's routine for its panels, once the game has drawn its own
; lines. Adds the five saves under the item icons, each with its label, and MOVE and THAC0 in the
; lower panel right of HP and PSI (as DAM is right of AC), then does the push. The routine is SL's, its
; code at the same distances: the text routine's far address (-1A9h from the patch), the segment of the
; panel's window handle (-1B4h) and the selected character's segment (-19Bh: the number at +0B44h,
; as PROBE_CHAR's). What differs from DSCLOG's: the sequel's records (PROBE_CHAR's), the movement at
; the creature's +13h (SL's +1Bh); the numbers the sheet's (no Loader's STATS, and no GEAR_WAIT: the
; sequel's creation screen gets none of the Loader's gear).
CH_DRAW   equ -0x1A9            ; (from the patch) "lcall SEG:OFF" operand: the text routine
CH_WIN    equ -0x1B4            ; (from the patch) "mov ax,04E0h" operand: the window's far pointer's segment
CH_WHO    equ -0x19B            ; (from the patch) "mov ax,0370h" operand: the character number's selector
CREATURE_MOVE equ 0x13
probe_view:
        pop word [cs:t_ip]
        pop word [cs:t_cs]
        pop word [cs:t_fl]
        sti
        pushad
        push es
        push fs
        mov es, [cs:t_cs]
        mov di, [cs:t_ip]
        sub di, 2               ; ES:DI = the patch
        mov eax, [es:di + CH_DRAW]
        mov [cs:c_draw], eax
        mov fs, [es:di + CH_WIN]
        mov eax, [fs:0]         ; the panel's window
        mov [cs:c_winptr], eax
        mov fs, [es:di + CH_WHO]
        mov bx, [fs:WHO_OFF]    ; the character on show
        cmp bx, 3
        ja .done
        mov [cs:c_who], bx
        imul ax, bx, SHEET_SIZE
        les si, [SHEETS_PTR]
        add si, ax              ; ES:SI = the character sheet
        cmp word [es:si + SHEET_ENTITY], 0
        je .done                ; an empty slot
        imul bx, bx, CREATURE_SIZE
        lfs di, [CREATURES_PTR]
        add di, bx              ; FS:DI = the creature record
        inc word [cs:view_count]
        mov eax, [es:si + SHEET_SAVES]  ; (read now: the text routine changes ES)
        mov [cs:c_vals], eax
        mov al, [es:si + SHEET_SAVES + 4]
        mov [cs:c_vals + 4], al
        mov al, [fs:di + CREATURE_MOVE]
        mov [cs:v_move_val], al
        mov al, [fs:di + CREATURE_THAC0]
        mov di, v_thac0 + 7
        call c_itoa_s
        mov byte [cs:di], 0
        mov di, v_move + 7
        mov al, [cs:v_move_val]
        call c_itoa_s
        mov byte [cs:di], 0
        xor bp, bp              ; the saves, each with its label (V_SAVES)
.save:  mov bx, bp
        shl bx, 2
        mov di, [cs:v_saves + bx]
        add di, 4
        mov al, [cs:c_vals + bp]
        call v_two
        push word [cs:v_saves + bx + 2]  ; (its place: y, then x)
        mov ax, bp
        and ax, 1
        imul ax, ax, V_SAVE_GAP
        add ax, V_SAVE_X
        push ax
        push cs
        push word [cs:v_saves + bx]
        call c_draw_line
        inc bp
        cmp bp, 5
        jb .save
        push word V_LOW_Y       ; right of HP and PSI in the lower panel, as DAM is right of AC
        push word V_LOW_X
        push cs
        push word v_move
        call c_draw_line
        push word V_LOW_Y + 7
        push word V_LOW_X
        push cs
        push word v_thac0
        call c_draw_line
.done:  pop fs
        pop es
        popad
        push dword 0x000B0140   ; the replaced instruction
        push word [cs:t_fl]
        push word [cs:t_cs]
        push word [cs:t_ip]
        iret

v_two:                          ; DSCLOG's: AL (0-99) -> two digits (a space for a leading 0) and a
        push bx                 ;   space at CS:DI; DI moves on
        xor ah, ah
        mov bl, 10
        div bl
        add ax, '00'
        cmp al, '0'
        jne .tens
        mov al, ' '
.tens:  mov [cs:di], al
        mov [cs:di + 1], ah
        mov byte [cs:di + 2], ' '
        add di, 3
        pop bx
        ret

v_thac0  db 'THAC0: ', 0, 0, 0, 0
v_move   db 'MOVE:  ', 0, 0, 0, 0  ; (its number under THAC0's)
v_move_val db 0
view_count dw 0                 ; screens drawn on (for a look in play)
; the saves under the item icons, two to a row (PPD and RSW, PP and BW, SP), with the short labels
; the inventory panel gives them: each its text and its row's y (DSCLOG's places: the screen is SL's)
V_SAVE_X   equ 0xCD
V_SAVE_GAP equ 36
V_LOW_X    equ 0xD8             ; (clear of HP's value, 7 letters from the game's place for it)
V_LOW_Y    equ 0x7F             ; (HP's line; PSI's 7 below)
v_saves  dw .ppd, 0x3A, .rsw, 0x3A, .pp, 0x41, .bw, 0x41, .sp, 0x48
.ppd     db 'PPD 00 ', 0
.rsw     db 'RSW 00 ', 0
.pp      db 'PP  00 ', 0
.bw      db 'BW  00 ', 0
.sp      db 'SP  00 ', 0

; ---- THE CREATION SCREEN'S THAC0: DSCLOG's CR_HP and CR_THAC0_DRAW ----
; INT VEC_CR_HP replaces "add sp,10h" (3 bytes: INT + NOP) after the creation screen draws its hit
; points again (6B84Ch, a click on them; 6BC62h; SL's 63AC3h, 63EDAh) and after it draws PSP, which
; follows the hit points (6D6AEh at the die, a choice and the screen opening; 6B79Ch at a click on
; CON; SL's 65A89h, 63A13h, its CR_AGE's sites). "THAC0: M18 R19" right of the hit points, on their
; line: the creature's THAC0 (it follows the classes chosen as they change) less STR's to-hit
; adjustment (M, melee) and less DEX's missile adjustment (R, ranged), none below 0, as the
; inventory's THAC0 with no weapon. The hit points' box (the 7th, DS:1224h) widened to x 243 (DONE's
; left 244: ravager.py's "cr_thac0_box"), so its saved background clears it. What differs from
; DSCLOG's: the sequel's records (the creature being made at DS:142Dh, 31h bytes: THAC0 +16h, STR
; +19h, DEX +1Ah; the STR to-hit table at DS:0832h, SL's 7C2h); a new character's kit by KIT_MADE (CR_KIT_THAC0).
CR_CREATURE equ 0x142D          ; DS: far pointer to the creature being made (SL's 11A0h)
CR_HP_BOX   equ 0x1224          ; DS: the hit points' box: x1, y1, x2, y2 (SL's F92h)
CR_THAC0_X  equ 146             ; (RECALL's left edge, as DSCLOG's CR_AGE_X)
CREATURE_STR equ 0x19
STR_HIT     equ 0x0832          ; DS: the STR to-hit adjustment (bytes, by score)
probe_cr_hp:
        pop word [cs:t_ip]
        pop word [cs:t_cs]
        pop word [cs:t_fl]
        add sp, 0x10            ; the replaced instruction
        sti
        pushad
        push es
        call cr_changed         ; (a new character's class only now shown: its picture, CR_DRAW)
        jz .drawn
        push word [cs:t_cs]     ; (the way back, as a far call's, with BP)
        push word [cs:t_ip]
        push bp
        mov bp, sp
        call cr_draw
        pop bp
        pop word [cs:t_ip]      ; (as the overlay manager has left it)
        pop word [cs:t_cs]
.drawn:
        les bx, [CR_CREATURE]
        mov cl, [es:bx + CREATURE_THAC0]
        call cr_kit_thac0
        mov di, cr_thac0_text + 8       ; (after "THAC0: M")
        mov si, STR_HIT
        mov dl, [es:bx + CREATURE_STR]
        call cr_less
        mov word [cs:di], ' R'
        add di, 2
        mov si, DEX_REACTION
        mov dl, [es:bx + CREATURE_DEX]
        call cr_less
        inc word [cs:cr_count]
        mov eax, [WIN_SHOWN]
        mov [cs:c_winptr], eax
        mov ax, ds
        add ax, USE_TEXT_SEG
        mov [cs:c_draw + 2], ax
        mov word [cs:c_draw], USE_TEXT_OFF
        mov ax, [CR_HP_BOX + 2]
        sub ax, 2
        push ax
        push word CR_THAC0_X
        push cs
        push word cr_thac0_text
        call c_draw_line
        cmp byte [cs:cr_age_mode], 0
        je .aged
        call cr_age_show                ; (PSP drawn: the age beside it, CR_AGE)
        mov byte [cs:cr_age_mode], 0
.aged:  pop es
        popad
        push word [cs:t_fl]
        push word [cs:t_cs]
        push word [cs:t_ip]
        iret
cr_less:                        ; at CS:DI, CL less DS:SI's entry for score DL (none below 0)
        xor dh, dh
        cmp dl, 25
        jbe .in
        mov dl, 25
.in:    add si, dx
        mov al, cl
        sub al, [si]
        jns .put
        xor al, al
.put:   jmp c_itoa
cr_thac0_text db 'THAC0: M', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
cr_count dw 0                   ; THAC0s drawn (for a look in play)
;
; THE CREATION SCREEN'S AGE: DSCLOG's CR_AGE (RULE_HI_AGING). CR_AGE_NEW (site 235, "cr_thac0_psp": PSP drawn
; at the die, a choice and the screen opening, 6D6AEh) and CR_AGE_CON (site 236, "cr_thac0_con": a click on
; CON, 6B79Ch) replace those two INTs of PROBE_CR_HP, which they go on to, and which then draws "AGE: 23"
; on PSP's line at CR_THAC0_X (the PSP box's saved background widened to x 200: ravager.py's "cr_age_box").
; The age is the one the character will have, kept in the sheet being made at SHEET_AGE (+41h, the last
; byte of the game's 42h sheet, which DONE copies with the rest; the creature follows at +42h, so the roll
; has no room there: the Loader's aging.give_ages works it out from the age). A new roll of Table 7's dice
; (AGE_DICE) at the die, a choice and the screen's opening; a click on CON, a RECALL (CR_AGE_HOLD, with the
; byte among STORE's fields) and EDIT's member keep the age the sheet has. Others kept.
CR_PSP_BOX  equ 0x122C          ; DS: the PSP box: x1, y1, x2, y2 (SL's F9Ah)
cr_age_new:
        mov byte [cs:cr_age_mode], 1
        jmp probe_cr_hp
cr_age_con:
        mov byte [cs:cr_age_mode], 2
        jmp probe_cr_hp
; CR_AGE_SHOW: the age put in the sheet being made (rolled, or kept) and drawn (DS the game's, C_DRAW and
; C_WINPTR set). Changes all but DS.
cr_age_show:
        test word [cs:rules_hi], RULE_HI_AGING
        jz .ret
        les bx, [WP_CREATION]
        movzx si, byte [es:bx + SHEET_RACE]
        dec si
        cmp si, AGE_RACES
        jae .ret                        ; (no race yet)
        mov al, [es:bx + SHEET_AGE]
        or al, al
        jz .roll                        ; (none yet: one rolled)
        cmp word [CR_EDITING], -1
        jne .show                       ; (EDIT: the member's own)
        cmp byte [cs:cr_age_mode], 2
        je .show                        ; (CON: the roll kept)
        cmp byte [cs:cr_age_hold], 0
        jne .show                       ; (RECALL: the stored one)
.roll:  shl si, 1
        movzx cx, byte [cs:si + age_dice]
        mov dl, cl
        inc dl                          ; (the byte: the dice's count + their roll less it + 1)
        jcxz .put
.die:   call age_rand
        shr ax, 8
        push dx
        xor dx, dx
        movzx di, byte [cs:si + age_dice + 1]
        div di
        mov al, dl
        pop dx
        add dl, al
        loop .die
.put:   mov [es:bx + SHEET_AGE], dl
        shr si, 1
        mov al, dl
.show:  movzx ax, al
        movzx dx, byte [cs:age_bases + si]
        add ax, dx
        dec ax                          ; (the race's base, + the byte - 1)
        mov di, c_age_n
        call c_wtoa
        mov ax, [CR_PSP_BOX + 2]
        sub ax, 2
        push ax
        push word CR_THAC0_X
        push cs
        push word c_age
        call c_draw_line
        inc word [cs:cr_ages]
.ret:   ret
; AGE_RAND: AX a random word (DSCLOG's: AGE_SEED, h * 25173 + 13849, mixed with the BIOS's tick count).
        SHARED_age_rand
age_dice db 1, 8,  4, 6,  3, 4,  2, 4,  5, 4,  3, 6,  1, 6,  0, 1  ; Table 7's dice by race (aging.RACES)
age_seed dw 0x5A17
cr_age_mode db 0                ; (1: PSP drawn anew, 2: CON clicked; 0: no age to draw)
cr_age_hold db 0                ; (1: a RECALL's redraw: the stored age kept)
cr_ages  dw 0                   ; ages drawn (for a look in play)
;
; FLIP_WAIT (site 237, "flip_wait"): DSCLOG's PROBE_FLIP. "push cs / call 3BA4h" (1698Fh; 4 bytes: the INT,
; the site's number, a NOP) in the game's page flip (the CRT controller's start address set to the other
; page, then a wait for the next vertical retrace, 13BA4h, as SL's 11674h). With a full screen up
; (SCREEN_IS 2: the inventory, View Character, USE, a talk) no wait: the game redraws its screen after each
; item picked up or put down, flipping as it goes, and the pointer stands still meanwhile. Elsewhere the
; wait as the game's (the map's pace may hang on it), with interrupts on if the game had them on. All kept.
flip_wait:
        inc word [cs:flip_waits]
        push bp
        mov bp, sp
        test byte [bp + 7], 2           ; (the caller's flags' IF)
        jz .quiet
        sti
.quiet: push ax
        push dx
        push es
        mov ax, [cs:pointer_ds]
        or ax, ax
        jz .wait                        ; (not known yet)
        mov es, ax
        cmp word [es:SCREEN_IS], 2
        jne .wait
        inc word [cs:flip_quick]
        jmp .out
.wait:  mov ax, 0x40                    ; as the game's 13BA4h: out of any retrace, then into the next
        mov es, ax
        mov dx, [es:0x63]               ; (the CRT controller's port: 3D4h, its status 3DAh)
        add dl, 6
.in:    in al, dx
        test al, 8
        jnz .in
.next:  in al, dx
        test al, 8
        jz .next
.out:   pop es
        pop dx
        pop ax
        pop bp
        iret
flip_waits dw 0                 ; page flips (for a look in play)
flip_quick dw 0                 ; ... of them with no wait
; CR_KIT_THAC0: CL (the creature's THAC0) with the kit chosen for a new character (KIT_MADE): a Scholar's 1
; worse (kits.thac0, DSCLOG's CR_THAC0_BASE; a warrior THAC0 kit's is the chosen weapon's alone, WAR_HIT, so
; not here). The game works the creature's THAC0 out again at a roll, through SCHOLAR_THAC0, which notes
; whether the kit is in it (CR_THAC0_SCHOLAR, none when the screen opens: KP_OPEN): the line has the kit
; chosen now, put in or taken out. An EDIT's creature has its kit in its own THAC0. Others kept.
cr_kit_thac0:
        cmp word [CR_EDITING], -1
        jne .ret
        push ax
        call kit_made
        cmp al, KIT_SCHOLAR
        sete al
        sub al, [cs:cr_thac0_scholar]
        jz .out
        add cl, al
        inc word [cs:cr_kits]
.out:   pop ax
.ret:   ret
cr_kits dw 0                    ; (THAC0s a kit changed, for a look in play)
cr_thac0_scholar db 0           ; (1: the creature's THAC0 has a Scholar's in it)

; ---- THE RULES ----
; The rule changes, as DSCLOG's bits in its header's RULES (+170) and RULES_HI (+270); the Loader
; sets only those ported (ravager.RULES_PORTED).
RULE_HELMS   equ 1              ; helms count AC 1 (PROBE_HELM_AC, PROBE_BOX_AC)
RULE_HP_BEST equ 32768          ; a hit die rolled twice, the better kept (PROBE_HP_BEST)
RULE_HI_HELD equ 32768          ; (RULES_HI) a held or Out Cold target hit automatically, normal damage (HELD)

; HELD: DSCLOG's (RULE_HI_HELD, the Loader's rule "held_hit"), AD&D's held target ("defender sleeping
; or held: automatic": the attack hits and does normal damage). The sequel's attack routine is SL's:
; - HELD_HIT replaces "cmp word [bp-6],14h" (5D088h, SL's 589E9h; 4 bytes, INT + 2 NOPs), the natural
;   20's test before its "je" to the hit: ZF in the INT's frame, set on the game's 20 or, with the rule,
;   a helpless target (whatever the d20);
; - HELD_DAMAGE replaces "mov ax,[bp-4] / shl ax,1" (5D1B7h, SL's 58B0Dh; 5 bytes), what a helpless
;   target takes: the damage, doubled only without the rule.
; Helpless as the game has it: Paralyzed (the sequel's effect 69, SL's 34) or Out Cold (the creature's
; +14h 3, SL's +1Ch). The combatants: 3 bytes each at (load + 3F49h):C33h, kind 2 a creature, its
; number the word after (the AC function's own reads, 5D544h). Both sides alike.
HELD_EFFECT   equ 69
HELD_OUT_COLD equ 3
CREATURE_STATUS equ 0x14
FIGHTERS_SEG  equ 0x3F49 - 0x47E0   ; (the combatants' segment less DS's)
FIGHTERS_OFF  equ 0x0C33
        SHARED_held_hit
; RANGER_LEVEL: SL's PROBE_RANGER_LEVEL (RULE_HI_RANGER, the Loader's rangers' casting level, always on):
; INT VEC_RANGER_LEVEL replaces "mov al,es:[bx+1Eh] / mov ah,0" (629F0h; 6 bytes: INT + 4 NOPs) where
; the routine giving the level a spell is cast at for its duration and damage (628AFh, SL's 5E25Ch)
; takes the level of a class of the caster's that casts the spell (ES:BX the sheet + the class's place:
; +1Bh the class, +1Eh its level). The caster level routine (SL's 81B16h) counts a ranger 7 less
; ("sub dx,7" at 97E00h, SL's 81B6Ah); this one took it whole. AX that level, a ranger's (classes 13-16) 7
; less with the rule, no less than 0; with the kits a Seeker's 5 and a Justifier's 9 (RANGER_DROP).
RULE_HI_RANGER equ 2
RANGER_FIRST equ 13
ranger_level:
        mov al, [es:bx + 0x1E]
        mov ah, 0
        push cx
        mov cl, [es:bx + 0x1B]
        sub cl, RANGER_FIRST
        cmp cl, 3
        ja .thief               ; (not a ranger)
        call ranger_drop
        sub al, cl
        jnc .most
        xor al, al
.most:  call ranger_most
        jmp .out
.thief: call sh_place_level     ; (a Shinobi's thief class: its casting level, THE SHINOBI'S SPELLS)
.out:   pop cx
        iret
; RANGER_MOST: AX a ranger's casting level, CL what its level loses (RANGER_DROP), no more than AD&D's 9
; (RANGER_CAST_MOST: a ranger's of 16th level and up) with the level cap by XP (RULE_LEVEL_10, which takes
; rangers past the game's 15th); a Seeker's (CL 5) no more than 11 and a Justifier's (CL 9) 7, the owner's
; tables' last rows (16th+: kits.ranger_cast_most). Others kept.
RANGER_CAST_MOST equ 9
ranger_most:
        test word [cs:rules], RULE_LEVEL_10
        jz .ret
        push dx
        mov dx, RANGER_CAST_MOST
        cmp cl, 5
        jne .just
        mov dx, RANGER_CAST_MOST + 2
.just:  cmp cl, 9
        jne .cap
        mov dx, RANGER_CAST_MOST - 2
.cap:   cmp ax, dx
        jle .out
        mov ax, dx
.out:   pop dx
.ret:   ret
; RANGER_DROP: CL what a ranger's level loses for its spells (ES:BX its sheet + the class's place): 7 with
; the rule, else 0; with the kits a Seeker's 5, a Justifier's 9 (kits.ranger_cast_drop), whatever the
; rule. DS the game's; others kept.
ranger_drop:
        xor cl, cl
        test word [cs:rules_hi], RULE_HI_RANGER
        jz .kit
        mov cl, 7
.kit:   test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        push ax
        push dx
        push bx
        push cx
        mov ax, bx              ; (the sheet: BX less the place, (BX - the table's start) mod its size)
        sub ax, [SHEETS_PTR]
        xor dx, dx
        mov cx, SHEET_SIZE
        div cx
        pop cx
        sub bx, dx
        call kit_is_b
        db KIT_SEEKER
        jne .justifier
        mov cl, 5
.justifier:
        call kit_is_b
        db KIT_JUSTIFIER
        jne .out
        mov cl, 9
.out:   pop bx
        pop dx
        pop ax
.ret:   ret
; KIT_RANGER_CAST (site 61, "kit_ranger_cast"): the caster level routine's "sub dx,7" (97E00h, SL's
; PROBE_RANGER_CAST at 81B6Ah; 3 bytes) for a ranger class (DX its level; [BP+6] the combatant): a
; Seeker's 5, a Justifier's 9 with the kits, else the game's 7. Others kept.
kit_ranger_cast:
        push bx
        mov bx, 7
        test word [cs:rules_hi], RULE_HI_KITS
        jz .take
        push ax
        mov ax, [bp + 6]
        call fighter_creature
        jc .game
        call cr_is
        db KIT_SEEKER
        jne .justifier
        mov bx, 5
.justifier:
        call cr_is
        db KIT_JUSTIFIER
        jne .game
        mov bx, 9
.game:  pop ax
.take:  sub dx, bx
        xchg ax, dx
        push cx
        mov cl, bl
        call ranger_most                ; (AD&D's most, 9; a Seeker's 11, a Justifier's 7)
        pop cx
        xchg ax, dx
        pop bx
        iret
; EL_SPHERE (sites 90-92): the Elementalist's second sphere (SL's EL_SPHERES, PROBE_EL_GRANT,
; PROBE_EL_KNOW, PROBE_EL_CAST, PROBE_EL_LEVEL: kits.spell_spheres). The sequel keeps no spells known
; for a priest: it asks 62B45h (spell, class: AL 1 if the class casts it) every time, by a byte a spell
; (selector 3D0h:7D3h, SPHERES_OFF: 1 air, 2 earth, 4 fire, 8 water, 10h every priest's, 20h the
; druids') met by the class's (a cleric's 10h and its element's, a druid's 30h and its element's, a
; ranger's as its element's cleric). 62B45h has no character, but each of its three callers that asks
; for one has it, and each is followed by "add sp,4 / or al,al" (the call's two words, spell then
; class, on the stack): INT + the site's byte replace the ADD (3 bytes), the OR kept.
; - site 90 (62CAEh): 62C00h (spell, member: does a class of member DI cast it), which the USE screen's
;   list (6260Ah, "member knows spell") asks before the spell's level against the member's highest;
; - site 91 (629BEh): 628AFh (member [BP+6], spell: the highest level of its classes that cast it),
;   the cast's level (625F0h) and the spells' effects' (91E88h on);
; - site 92 (97DE1h): 97DC5h (member [BP+6], spell: the caster level, each class 0-19 asked; site 61
;   in its loop).
; For an Elementalist (awake, the kits' rule on), the game's 0 for its own cleric class (KIT_WHERE's)
; made 1 when the spell (73h-EAh, the priests') has its second sphere's bit (SPHERE2's low three bits:
; the sphere + 1; EL_SECOND); for a Healer's own cleric class the sphere of the cosmos's (HEALER_COSMOS: the
; druids' 20h spells, which no cleric casts in the sequel, and COSMOS_MORE's). Then a yes, the game's or
; made, made 0 for a spell the member's kit never knows (KIT_BARS: a Wilderness Avenger's healing spells, a
; Healer's or Lifebinder's harming ones; SL's AV_KNOW), so the USE screen never lists it and the casting
; levels never count it. Then the call's two words taken off as the ADD did. Others kept.
KIT_ELEMENTALIST equ 5
SPHERE2       equ 0x3F              ; (SL's +45h: ravlog's layout, kits.SPHERE2)
SPHERE2_MASK  equ 0x07              ; (the bits above it SL's new spells known: NEW_KNOWN)
SPHERES_SEG   equ 0x41F1 - 0x47E0   ; (the spheres' segment, selector 3D0h's, less DS's)
SPHERES_OFF   equ 0x07D3
PRIEST_FIRST  equ 0x73
PRIEST_END    equ 0xEB
el_sphere_di:
        push ax
        mov ax, di
        jmp el_sphere
el_sphere_bp:
        push ax
        mov ax, [bp + 6]
el_sphere:                          ; ([BP+2] the game's AX, +4 the INT's IP, CS, FLAGS, +0Ah the
        push bp                     ;   spell, +0Ch the class)
        mov bp, sp
        push bx
        push es
        cmp ax, 400                 ; (a combatant: its creature, as the game reads it, 388h:0C34h)
        jae .out
        imul bx, ax, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        mov ax, [es:bx + FIGHTERS_OFF + 1]
        call kit_sheet
        cmp byte [bp + 2], 0
        jne .bar                    ; (the game's yes: a kit may bar it)
        call el_own_second
        jnc .cosmos
        inc word [cs:el_spheres]
        jmp .yes
.cosmos:
        call healer_cosmos
        jnc .out
        inc word [cs:kc_cosmos]
.yes:   mov byte [bp + 2], 1
.bar:   call kit_bars
        jnc .out
        mov byte [bp + 2], 0
        inc word [cs:kc_barred]
.out:   pop es
        pop bx
.back:  mov ax, [bp + 8]            ; (the INT's frame moved over the call's two words; AX the
        mov [bp + 0x0C], ax         ;   game's, its AL the answer, popped after)
        mov ax, [bp + 6]
        mov [bp + 0x0A], ax
        mov ax, [bp + 4]
        mov [bp + 8], ax
        pop bp
        pop ax
        add sp, 4
        iret
; EL_OWN_SECOND: (EL_SPHERE's, its frame; ES:BX the member's sheet) CF set if class [BP+0Ch] is an Elementalist's
; own cleric class (awake, the kits' rule on) and spell [BP+0Ah] a priest spell of its second sphere
; (SPHERE2's low three bits: the sphere + 1). All registers kept.
el_own_second:
        push ax
        push cx
        push si
        push es
        call kit_is_b
        db KIT_ELEMENTALIST
        jne .no
        mov si, [cs:kit_where]
        movzx cx, byte [es:bx + si + SH_CLASSES]
        cmp cx, [bp + 0x0C]
        jne .no                     ; (not its cleric class)
        mov cl, [es:bx + SPHERE2]
        and cl, SPHERE2_MASK
        jz .no
        dec cl
        cmp cl, 3
        ja .no
        mov si, [bp + 0x0A]
        cmp si, PRIEST_FIRST
        jb .no
        cmp si, PRIEST_END
        jae .no
        mov ax, ds
        add ax, SPHERES_SEG
        mov es, ax
        mov al, 1
        shl al, cl
        test [es:si + SPHERES_OFF], al
        jz .no
        stc
        jmp .out
.no:    clc
.out:   pop es
        pop si
        pop cx
        pop ax
        ret
el_spheres dw 0                     ; (the game's no made yes, counted for a look in play)
; SHINOBI_MAGE (site 190, "shinobi_mage"): "add sp,4" after the slot routine's (626B7h, SL's 5E0ACh) call
; to 62B45h (spell 8, the class: does the class cast wizard spells) at 627D6h, the "or al,al" after kept:
; the member SI, the call's two words under the INT's frame as at EL_SPHERE. The game's no made yes for a
; Shinobi's own thief class (17), awake, the kits' rule on, so that ADND_SLOTS is asked its slots (KIT_TABLE:
; the Seeker's table by thief level, SL's PROBE_SLOTS). Then the call's two words taken off as the ADD did.
shinobi_mage:
        push ax
        push bp
        mov bp, sp                  ; ([BP+2] the game's AX, +4 the INT's IP, CS, FLAGS, +0Ah the
        cmp byte [bp + 2], 0        ;   spell, +0Ch the class)
        jne .back
        test word [cs:rules_hi], RULE_HI_KITS
        jz .back
        cmp word [bp + 0x0C], THIEF_CLASS
        jne .back
        push bx
        push si
        push es
        mov ax, si
        cmp ax, 400                 ; (a combatant: its creature, as the game reads it, 388h:0C34h)
        jae .out
        imul bx, ax, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        mov ax, [es:bx + FIGHTERS_OFF + 1]
        call kit_sheet
        call kit_is_b
        db KIT_SHINOBI
        jne .out
        mov si, [cs:kit_where]
        cmp byte [es:bx + si + SH_CLASSES], THIEF_CLASS
        jne .out
        mov byte [bp + 2], 1
        inc word [cs:sh_mages]
.out:   pop es
        pop si
        pop bx
.back:  jmp el_sphere.back
sh_mages dw 0                       ; (likewise)
; ---- THE KITS' CASTING LEVELS, CURES AND SPELLS KNOWN (sites 205-208; EL_SPHERE's HEALER_COSMOS and
; KIT_BARS, CELL_HEAL's CELL_MORE): SL's PROBE_SPELL_LEVEL (SKY_LEVEL, ARC_LEVEL), PROBE_CURE, AREA_DMG and
; HARM_SITE's AV_CAUSE, PROBE_EL_GRANT's and PROBE_EL_KNOW's Healer and AV_KNOW, CELL_SITE's kits, in the
; sequel's spell numbers (RESOURCE.GFF's names). Counted in the header (+2064 on) for a look in play.
KIT_ARCANIST      equ 23
KIT_SPIRIT_CALLER equ 69
KIT_WASTE_SEER    equ 73
COSMOS_BIT        equ 0x20          ; (a spell's sphere byte: the druids', which no cleric casts)
; HEALER_COSMOS: (EL_SPHERE's, its frame; ES:BX the member's sheet) CF set if class [BP+0Ch] is a Healer's
; own cleric class (1-4; awake, the kits' rule on) and spell [BP+0Ah] one of the sphere of the cosmos: a
; priest spell whose sphere byte has COSMOS_BIT (every druid casts it, no cleric: in the sequel Cure Serious
; and Critical Wounds, Free Action, Neutralize Poison, Raise Dead, Heal and the rest; SL's HEALER_COSMOS, its
; element's druid's bit), or one of COSMOS_MORE's (the header's +2060: for Whirlwind and Restore Youth once
; they are in the sequel, FFFFh till then). All registers kept.
healer_cosmos:
        push ax
        push si
        push es
        call kit_is_b
        db KIT_HEALER
        jne .no
        mov si, [cs:kit_where]
        movzx ax, byte [es:bx + si + SH_CLASSES]
        cmp ax, [bp + 0x0C]
        jne .no                     ; (not its own class)
        dec ax
        cmp ax, 3
        ja .no                      ; (a cleric's, 1-4: not a ranger's after DUAL)
        mov si, [bp + 0x0A]
        cmp si, [cs:cosmos_more]
        je .yes
        cmp si, [cs:cosmos_more + 2]
        je .yes
        cmp si, PRIEST_FIRST
        jb .no
        cmp si, PRIEST_END
        jae .no
        mov ax, ds
        add ax, SPHERES_SEG
        mov es, ax
        test byte [es:si + SPHERES_OFF], COSMOS_BIT
        jz .no
.yes:   stc
        jmp .out
.no:    clc
.out:   pop es
        pop si
        pop ax
        ret
; KIT_BARS: (EL_SPHERE's, its frame; ES:BX the member's sheet) CF set if spell [BP+0Ah] is one the sheet's kit
; (awake, the kits' rule on) never knows (kits.knows_heal): a Wilderness Avenger's healing ones (AV_HEALS), a
; Healer's or Lifebinder's harming ones (AV_HARMS). All registers kept.
kit_bars:
        push ax
        push cx
        push si
        mov ax, [bp + 0x0A]
        call kit_is_b
        db KIT_AVENGER
        jne .harm
        mov si, av_heals
        mov cx, AV_HEALS_COUNT
        jmp .find
.harm:  call kit_is_b
        db KIT_HEALER
        je .harms
        call kit_is_b
        db KIT_LIFEBINDER
        jne .no
.harms: mov si, av_harms
        mov cx, AV_HARMS_COUNT
.find:  cmp ax, [cs:si]
        je .yes
        add si, 2
        loop .find
.no:    clc
        jmp .out
.yes:   stc
.out:   pop si
        pop cx
        pop ax
        ret
; the healing spells a Wilderness Avenger never knows (kits.AVENGER_NO_HEAL): Cure Light Wounds, Blood Flow,
; Cure Serious Wounds, Cure Critical Wounds, Heal, Waters of Life; the harming ones a Healer or Lifebinder
; never knows (kits.NO_HARM): Cause Light, Serious and Critical Wounds, Cause Disease, Poison, Slay Living,
; Harm, and the sequel's own Heartseeker, Energy Drain and Symbol of Pain (ravager.RAV_SEQUEL_HARMS: they harm
; or kill the body as those do; the sequel's numbers)
av_heals dw 117, 166, 170, 194, 210, 215
AV_HEALS_COUNT equ ($ - av_heals) / 2
av_harms dw 118, 171, 195, 149, 179, 204, 211, 212, 225, 229
AV_HARMS_COUNT equ ($ - av_harms) / 2
; KIT_CAST_LEVEL (site 205, "kit_cast_level"): in the routine giving the level a spell is cast at for its
; duration and damage (628AFh, SL's 5E25Ch: [BP+6] the caster, [BP+8] the spell, DI the best level of its
; classes that cast it, [BP-1] the class place its loop is at; the cast's level, 625F0h, so the spell's
; dice and rounds), "inc byte [bp-1]" (629FEh; 3 bytes) at its loop's end: done, and after the third place
; DI with the kits' (SL's PROBE_SPELL_LEVEL's SKY_LEVEL and ARC_LEVEL; kits.arc_level, kits.sky_level), for a
; party member (creatures 0-3) whose classes cast the spell (DI above 0): an Arcanist's wizard spell
; (0-72h, and the new spells NS_FIRST on) 1 more (ARC_MORE); a Spirit Caller's or Wasteland Seer's priest spell (73h-EAh; or the sequel's own
; party's thri-kreen psionicist's, OWN_RACE_B: SL's K'ratchek) 2 more under the open sky (its KIT_OUTDOORS
; bit, the Loader's), 1 less under a roof but no less than 1. The spell levels it may cast stay the caster
; level routine's (97DC5h), its own level's. Counted (KC_LEVELS). The flags are the game's CMP's after.
ARC_MORE equ 1
SKY_MORE equ 2
kit_cast_level:
        inc byte [bp - 1]
        cmp byte [bp - 1], 3
        jl .ret                     ; (not the loop's end)
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        or di, di
        jle .ret                    ; (no class of its casts it)
        push ax
        push bx
        push es
        mov ax, [bp + 6]
        call fighter_creature
        jc .out
        cmp ax, 3
        ja .out                     ; (not a party member)
        mov bx, [bp + 8]
        cmp bx, PRIEST_FIRST
        jb .wizard
        cmp bx, NS_FIRST
        jb .priest
        cmp bx, NS_FIRST + NS_COUNT
        jb .wizard                  ; (the six new spells: wizard spells, SL's ARC_LEVEL's too)
        jmp .out
.priest:
        cmp bx, PRIEST_END
        jae .out
        call cr_is
        db KIT_SPIRIT_CALLER
        je .sky
        call cr_is
        db KIT_WASTE_SEER
        je .sky
        push ax
        call kit_sheet
        call own_race_b             ; (the own party's thri-kreen psionicist, as a Wasteland Seer)
        cmp al, OWN_KREEN
        jne .not_own
        mov al, OWN_PSI
        call own_has
.not_own:
        pop ax
        jne .out
.sky:   bt word [cs:kit_outdoors], ax
        jnc .roof
        add di, SKY_MORE
        jmp .made
.roof:  cmp di, 1
        jle .out
        dec di
        jmp .made
.wizard:
        call cr_is
        db KIT_ARCANIST
        jne .out
        add di, ARC_MORE
.made:  inc word [cs:kc_levels]
.out:   pop es
        pop bx
        pop ax
.ret:   iret
; KIT_CURE (site 206, "kit_cure"): in the handler for spells with rules of their own (656D0h on, SL's
; 7936Dh: [BP+0Eh] the spell, [BP+8] the caster, DI the target), "push ax / jmp 65811h" (66545h; 4 bytes)
; where Cure Light Wounds' 1d8, Cure Serious Wounds' 2d8+1, Cure Critical Wounds' 3d8+3 and Blood Flow's 2d6
; (on its caster's own side: healing) go to the routine that heals (65811h: "push di / call 628h:43h"), and
; Cell Adjustment's from CELL_HEAL (its kit's more in already: CELL_MORE): AX with the caster's kit's (SL's
; PROBE_CURE: kits.cure_bonus, kits.cure_die), pushed under the INT's frame and the way back made 65811h, as
; the game's two instructions. A Healer's and a Rescuer's Cure Light, Serious and Critical Wounds 1 more a
; die (CURE_DICE's dice: +1, +2, +3), a Lifebinder's those and Blood Flow a die more (CURE_DICE's sides).
; Counted (KC_CURES).
CURE_BACK  equ 0x65811 - (0x66545 + 3)
BLOOD_FLOW equ 166
cure_dice db 117, 1, 8,  170, 2, 8,  194, 3, 8,  BLOOD_FLOW, 2, 6    ; spell, dice, sides (kits.CURE_DICE)
CURE_DICE_END:
kit_cure:
        sub sp, 2
        push bp
        mov bp, sp                      ; ([BP+2] the room, +4 the INT's IP, CS, FLAGS)
        push ax
        mov ax, [bp + 4]
        mov [bp + 2], ax
        mov ax, [bp + 6]
        mov [bp + 4], ax
        mov ax, [bp + 8]
        mov [bp + 6], ax                ; (the INT's frame a word down: [BP+8] the game's push)
        pop ax
        add word [bp + 2], CURE_BACK
        push ax
        call cure_more
        mov [bp + 8], ax
        pop ax
        pop bp
        iret
; CURE_MORE: (KIT_CURE's; [BP] the game's BP) AX (the healing of spell [game BP+0Eh] by combatant [+8]) with
; the caster's kit's, the kits' rule on. Others kept.
cure_more:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        push bx
        push cx
        push dx
        push si
        mov si, [bp]
        mov dx, [ss:si + 0x0E]
        or dh, dh
        jnz .out
        mov bx, cure_dice
.find:  cmp dl, [cs:bx]
        je .spell
        add bx, 3
        cmp bx, CURE_DICE_END
        jb .find
        jmp .out
.spell: mov cx, ax
        mov ax, [ss:si + 8]
        call fighter_creature
        jc .done
        call cr_is
        db KIT_HEALER
        je .plus
        call cr_is
        db KIT_RESCUER
        je .plus
        call cr_is
        db KIT_LIFEBINDER
        jne .done
        movzx ax, byte [cs:bx + 2]
        call game_die
        add cx, ax
        jmp .count
.plus:  cmp dl, BLOOD_FLOW              ; (a Healer's and a Rescuer's: the cures alone)
        je .done
        movzx ax, byte [cs:bx + 1]
        add cx, ax
.count: inc word [cs:kc_cures]
.done:  mov ax, cx
.out:   pop si
        pop dx
        pop cx
        pop bx
.ret:   ret
; AVENGER_AREA (site 207, "avenger_cause_area"): "mov [bp-14h],ax" (7E7A6h; 3 bytes) where the routine dealing
; a spell's damage to the creatures it reaches (7E6xxh, SL's 7511Bh: AREA_DMG; DI the spell; a touch spell's on
; one too) has rolled it (AX, 80278h's), the most it could roll at [BP-16h] (what a helpless target takes):
; AV_CAUSE's more on both. AVENGER_ONE (site 208, "avenger_cause_one"): the same at "mov [bp-6],ax" (7F727h;
; 3 bytes) in the routine for a spell on one creature (SL's 76175h: HARM_SITE), the most at [BP-8]. Then the
; move done.
avenger_area:
        push bx
        call av_cause
        add [bp - 0x16], bx
        pop bx
        mov [bp - 0x14], ax
        iret
avenger_one:
        push bx
        call av_cause
        add [bp - 8], bx
        pop bx
        mov [bp - 6], ax
        iret
; AV_CAUSE: AX the damage spell DI has rolled: a Wilderness Avenger's Cause Light, Serious and Critical Wounds
; 1 more a die (+1, +2, +3; kits.harm_bonus) added, BX that more (0 none), when its caster (CAST_WHO: TH_CAST's,
; the last spell cast) cast that spell (CAST_SPELL), the kits' rule on. Counted (KC_CAUSES). Others kept.
av_causes dw 118, 1,  171, 2,  195, 3   ; (the sequel's Cause Light, Serious, Critical Wounds; kits.CAUSE_DICE)
AV_CAUSES_END:
av_cause:
        xor bx, bx
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        cmp di, [cs:cast_spell]
        jne .ret
        push si
        mov si, av_causes
.find:  cmp di, [cs:si]
        je .spell
        add si, 4
        cmp si, AV_CAUSES_END
        jb .find
        jmp .out
.spell: push ax
        mov ax, [cs:cast_who]
        call fighter_creature
        jc .none
        call cr_is
        db KIT_AVENGER
        jne .none
        pop ax
        mov bx, [cs:si + 2]
        add ax, bx
        inc word [cs:kc_causes]
        jmp .out
.none:  pop ax
.out:   pop si
.ret:   ret
; CELL_MORE: (CELL_HEAL's) CX what the kit of combatant AX (Cell Adjustment's user) adds to its healing (SL's
; CELL_SITE: kits.CELL_MORE, CELL_PLUS): a Lifebinder's a d4, a Healer's or Rescuer's 1 (as their cures a die
; and 1 a die more); 0 for anyone else. Counted (KC_CELLS). Others kept.
CELL_MORE equ 4
CELL_PLUS equ 1
cell_more:
        xor cx, cx
        push ax
        call fighter_creature
        jc .out
        call cr_is
        db KIT_LIFEBINDER
        jne .plus
        mov ax, CELL_MORE
        call game_die
        mov cx, ax
        jmp .count
.plus:  call cr_is
        db KIT_HEALER
        je .one
        call cr_is
        db KIT_RESCUER
        jne .out
.one:   mov cx, CELL_PLUS
.count: inc word [cs:kc_cells]
.out:   pop ax
        ret
; ENLARGE DICE: SL's (RULE_HI_ENLARGE, the Loader's "enlarge_dice", always on): the game's Enlarge
; (863B2h, SL's 7C211h, called by the attack for a melee hit: 628h:57h; after STR's bonus: SI the
; damage, AX the levels of the Enlarges on the attacker, 608h:52h) multiplies the whole of the damage
; by 100 + 10 a level percent, rounded down; AD&D's enlarges the weapon, so only its dice.
; - ENL_ROLL replaces the attack's "cmp word [bp+16h],1" (5D0C8h, SL's 58A29h, STAB_ROLL's site; 4
;   bytes, INT + 2 NOPs) after the damage roll (AX the roll, [BP-14h] what it added to the dice: the
;   sequel's frame, SL's [BP-12h]): the dice's sum kept, ENL_KNOWN for a melee hit (the compare's
;   "not greater"), then the compare made, its flags in the INT's frame;
; - ENL_SITE replaces "imul ax,ax,0Ah ... idiv ebx / mov si,ax" (863E7h; 32 bytes, SL's 7C246h): with
;   the rule and the hit's dice known (once: ENL_KNOWN), the dice multiplied, rounded up, the rest added
;   once, and the dice kept made the enlarged ones (a backstab multiplies those); else the game's.
; - STAB_TIMES (site 53, "backstab_dice", Thieves as in AD&D: RULE_THIEF_TABLE) replaces "push ax / mov
;   ax,[bp-4] / pop dx / imul dx / mov [bp-4],ax" (5D11Bh; 10 bytes, SL's 58A80h, the same) where the
;   attack multiplies a backstab's damage ([BP-4], STR's bonus and Enlarge's in it) by AX (x2 to x5 by
;   thief level: 5DE0Ch, SL's 595C4h; on the round's first two attacks, the game's test at 5D10Ch): with
;   the rule, the dice's sum (ENL_DICE, ENL_ROLL's, Enlarge's after ENL_SITE) added again for each time
;   past the first, only on the round's first attack ([BP-16h] the attacks so far, SL's [BP-14h]; a miss,
;   [BP-4] 0, none); else the game's. Either way, with the kits (RULE_HI_KITS), an Assassin's multiplier
;   one more (x3 to x6: SL's STAB_TIMES, kits.backstab_times; the attacker [BP+0Eh], a party member).
RULE_HI_ENLARGE equ 512
enl_dice  dw 0
enl_known db 0
enl_roll:
        push bx
        push ax
        sub ax, [bp - 0x14]
        mov [cs:enl_dice], ax
        call sf_less                    ; (the double spear's swing at a second foe: 1 less)
        cmp word [bp + 0x16], 1
        pushf
        setle byte [cs:enl_known]
        pop ax                  ; (the compare's flags)
        mov bx, sp
        and word [ss:bx + 8], ~0x08D5
        and ax, 0x08D5          ; (OF SF ZF AF PF CF)
        or [ss:bx + 8], ax
        pop ax
        pop bx
        iret
enl_site:
        push ebx
        push edx
        imul ax, ax, 10
        movsx eax, ax
        add eax, 100                    ; (the percent)
        test word [cs:rules_hi], RULE_HI_ENLARGE
        jz .whole
        cmp byte [cs:enl_known], 0
        je .whole
        movsx ebx, word [cs:enl_dice]
        or ebx, ebx
        jle .whole
        imul eax, ebx
        add eax, 99
        cdq
        push ebx
        mov ebx, 100
        idiv ebx                        ; (the dice enlarged, rounded up)
        pop ebx
        sub ax, bx
        add si, ax
        add [cs:enl_dice], ax           ; (the dice enlarged: a backstab's, STAB_TIMES)
        inc word [cs:enlarges]
        jmp .done
.whole: movsx edx, si
        imul eax, edx
        mov ebx, 100
        cdq
        idiv ebx
        mov si, ax
.done:  mov byte [cs:enl_known], 0
        pop edx
        pop ebx
        iret
enlarges dw 0                   ; (hits enlarged by the dice, for a look in play)
stab_times:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .rule
        cmp word [bp + 0x0E], 3
        ja .rule                        ; (not a party member)
        push ax
        mov ax, [bp + 0x0E]
        call cr_is
        db KIT_ASSASSIN
        pop ax
        jne .rule
        inc ax                          ; (an Assassin: one more)
        inc word [cs:kit_stabs]
.rule:  test word [cs:rules], RULE_THIEF_TABLE
        jz .whole
        cmp word [bp - 0x16], 0
        je .first
        mov ax, 1                       ; (the round's second attack: no backstab, as in AD&D)
        jmp .whole
.first: cmp word [bp - 4], 0
        jle .whole                      ; (a miss: none)
        dec ax
        imul word [cs:enl_dice]
        add ax, [bp - 4]
        inc word [cs:stabs]
        jmp .put
.whole: imul word [bp - 4]
.put:   mov [bp - 4], ax
        iret
stabs   dw 0                    ; (backstabs by the dice, for a look in play)
kit_stabs dw 0                  ; (an Assassin's backstabs, one more, for a look in play)

; PRESERVERS' INT: SL's INT_LEARN (RULE_HI_INT, the Loader's "int_learning", always on; dsloader/intlearn.py).
; The sequel's scroll (its box's icon clicked, 99xxxh, SL's 8B690h) tests the reader's bit in the known
; wizard spells (selector 320h:39Ch + 15 a member, bit n spell n; the reader at 370h:0B44h, the spell
; [BP-4]): known, YOU ALREADY KNOW THIS SPELL (99A86h: "push ds / push 2EABh"); else the bit set, the
; scroll used up (5F8h:43h) and YOU LEARN THE SPELL (99A7Fh: "push ds / push 2E97h").
; - SCROLL_LEARN replaces "or ax,ax" (99A2Fh; 2 bytes, then the game's "jnz" to the known path; AX 1
;   known): for a wizard (class 11 or the sequel's 18) and a wizard spell (below WIZ_SPELLS), with the
;   rule, INT's row (the creature's +1Ch) gives the chance (INT_CHANCE) and the most of a spell level
;   (INT_MOST); knowing that many of the spell's level (SPELL_STARTS, the game's table at DS:0656h: the
;   first spell of each level, 1 to 10), AX 1 and LEARN_FULL (the scroll kept, LEARN_REFUSED's text);
;   else a d100 (the game's seed): above the chance, LEARN_FAILED (AX 0: the game teaches it and uses the
;   scroll up, LEARN_SAID takes it back). The try told to the Loader (+272, as DSCLOG's). ZF as "or ax,ax".
; - LEARN_SAID, LEARN_REFUSED: the message pushed (a far pointer), the helper's text in place of the
;   game's after a failed try or a full level.
RULE_HI_INT  equ 4
WIZ_SPELLS   equ 115
SPELL_STARTS equ 0x0656
WIZ_LEVELS   equ 10
PRESERVER_CLASS equ 11
WIZARD_NEW_CLASS equ 18
KNOWN_OFF    equ 0x39C                      ; (the known spells' place in selector 320h's segment)
CREATURE_INT equ 0x1C
INT_FIRST    equ 9
INT_ROWS     equ 17
INT_ALL      equ 255
int_chance   db 35, 40, 45, 50, 55, 60, 65, 70, 75, 85, 95, 96, 97, 98, 99, 100, 100
int_most     db 6, 7, 7, 7, 9, 9, 11, 11, 14, 18, INT_ALL, INT_ALL, INT_ALL, INT_ALL, INT_ALL, INT_ALL, INT_ALL
LEARN_LEARNT equ 0
LEARN_FAILED equ 1
LEARN_FULL   equ 2
learn_msg    db 0
learn_es     dw 0                           ; (the bit's place: the game's ES:BX at SCROLL_LEARN ...
learn_bx     dw 0
learn_mask   db 0                           ;  ... and its bit)
learnt_tries dw 0                           ; (tries, for a look in play)
scroll_learn:
        or ax, ax
        jnz .flags                          ; (known: the game's)
        call sh_scroll                      ; (a Shinobi's: THE SHINOBI'S SPELLS)
        jc .flags
        test word [cs:rules_hi], RULE_HI_INT
        jz .flags
        pushad
        push es
        mov [cs:learn_es], es
        lea ax, [bx + KNOWN_OFF]
        mov [cs:learn_bx], ax                ; (the game's BX: the member x 15 + the spell / 8)
        mov dx, [bp - 4]                    ; (the spell)
        cmp dx, WIZ_SPELLS
        jae .out
        mov cl, dl
        and cl, 7
        mov al, 1
        shl al, cl
        mov [cs:learn_mask], al
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov si, [es:USE_WHO_OFF]            ; (SI the reader)
        cmp si, 3
        ja .out
        imul di, si, CREATURE_SIZE
        les bx, [CREATURES_PTR]
        add bx, di
        movzx ax, byte [es:bx + CREATURE_INT]
        mov [cs:learn_int], al
        mov di, [es:bx + 4]
        imul di, di, SHEET_SIZE
        les bx, [SHEETS_PTR]
        add bx, di
        mov cx, 3
.class: mov ah, [es:bx + SHEET_CLASSES]
        cmp ah, PRESERVER_CLASS
        je .wizard
        cmp ah, WIZARD_NEW_CLASS
        je .wizard
        inc bx
        loop .class
        jmp .out
.wizard:
        movzx bx, byte [cs:learn_int]       ; (BX the INT's row)
        sub bx, INT_FIRST
        jge .high
        xor bx, bx
.high:  cmp bx, INT_ROWS - 1
        jbe .row
        mov bx, INT_ROWS - 1
.row:   mov ax, si
        mov [cs:learn_who], al
        mov [cs:learn_spell], dl
        mov byte [cs:learn_spell_hi], 0
        mov byte [cs:learn_read], 0         ; (no read roll: a Shinobi's last one isn't this try's)
        mov byte [cs:learn_read_chance], 0
        mov al, [cs:int_chance + bx]
        mov [cs:learn_chance], al
        mov ch, [cs:int_most + bx]          ; (CH the most a level)
        mov ax, dx
        call spell_level                    ; (CL the spell's level)
        mov es, [cs:learn_es]               ; (the reader's known spells: ES:DI)
        mov di, [cs:learn_bx]
        mov ax, dx
        shr ax, 3
        sub di, ax
        xor ax, ax                          ; (AL a spell, AH those of that level known)
.count: push cx
        push ax
        movzx bx, al
        shr bx, 3
        mov cl, al
        and cl, 7
        mov ch, 1
        shl ch, cl
        test [es:di + bx], ch
        pop ax
        pop cx
        jz .next
        push cx
        mov dl, cl
        call spell_level
        cmp cl, dl
        pop cx
        jne .next
        inc ah
.next:  inc al
        cmp al, WIZ_SPELLS
        jb .count
        mov [cs:learn_roll], ah
        cmp ah, ch
        jb .roll
        mov byte [cs:learn_result], LEARN_FULL
        mov byte [cs:learn_msg], LEARN_FULL
        inc word [cs:learn_seq]
        pop es
        popad
        mov ax, 1                           ; (the game's "known" path: the scroll kept)
        jmp .flags
.roll:  mov ax, 100
        call game_die
        mov [cs:learn_roll], al
        mov byte [cs:learn_result], LEARN_LEARNT
        cmp al, [cs:learn_chance]
        jbe .told
        mov byte [cs:learn_result], LEARN_FAILED
        mov byte [cs:learn_msg], LEARN_FAILED
.told:  inc word [cs:learn_seq]
        inc word [cs:learnt_tries]
.out:   pop es
        popad
.flags: push bp                             ; (ZF in the flags IRET gives back)
        mov bp, sp
        and word [bp + 6], ~0x40
        or ax, ax
        jnz .done
        or word [bp + 6], 0x40
.done:  pop bp
        iret
; SPELL_LEVEL: CL the level (1 to WIZ_LEVELS) of wizard spell AL, from the game's SPELL_STARTS. DS the
; game's; others kept.
spell_level:
        push bx
        mov bx, SPELL_STARTS + 1
        mov cl, 1
.next:  cmp cl, WIZ_LEVELS
        jae .ret
        cmp al, [bx]
        jb .ret
        inc bx
        inc cl
        jmp .next
.ret:   pop bx
        ret
learn_failed_text db 'YOU FAIL TO LEARN THE SPELL', 0
learn_full_text   db 'TOO MANY SPELLS OF THAT LEVEL', 0
learn_unread_text db 'YOU CAN NOT READ THE SCROLL', 0
learn_not_its_text db 'THAT IS NOT A SHINOBI SPELL', 0
lm_ip dw 0
lm_cs dw 0
lm_fl dw 0
learn_said:
        pop word [cs:lm_ip]
        pop word [cs:lm_cs]
        pop word [cs:lm_fl]
        mov word [cs:lm_text], learn_failed_text
        cmp byte [cs:learn_msg], LEARN_FAILED
        je .back
        mov word [cs:lm_text], learn_unread_text    ; (a Shinobi's scroll not read: THE SHINOBI'S SPELLS)
        cmp byte [cs:learn_msg], LEARN_UNREAD
        jne .game
.back:  push es
        push bx
        push ax
        mov es, [cs:learn_es]
        mov bx, [cs:learn_bx]
        mov al, [cs:learn_mask]
        not al
        and [es:bx], al                     ; (the spell taken back)
        pop ax
        pop bx
        pop es
        mov byte [cs:learn_msg], 0
        push cs
        push word [cs:lm_text]
        jmp learn_back
.game:  push ds
        push 0x2E97
        SHARED_learn_back
learn_refused:
        pop word [cs:lm_ip]
        pop word [cs:lm_cs]
        pop word [cs:lm_fl]
        mov word [cs:lm_text], learn_full_text
        cmp byte [cs:learn_msg], LEARN_FULL
        je .said
        mov word [cs:lm_text], learn_not_its_text   ; (not a Shinobi's spell: THE SHINOBI'S SPELLS)
        cmp byte [cs:learn_msg], LEARN_NOT_ITS
        jne .game
.said:  mov byte [cs:learn_msg], 0
        push cs
        push word [cs:lm_text]
        jmp learn_back
.game:  push ds
        push 0x2EAB
        jmp learn_back
lm_text dw 0
; PICK_ANY: INT VEC_PICK_ANY replaces "mov [bp-2],ax / or ax,ax" (9317Fh; 5 bytes: INT + 3 NOPs) in the
; routine a preserver's level up calls (688h:66h, 93160h; SI the member, AX its preserver level), which
; goes on (the JG after) to ask the game's list (94C7Ch) for a spell to learn at each spell level from
; [BP-2] down, and opens CHOOSE A SPELL (93378h) if one is found. With the rule: [BP-2] and AX the
; highest spell level it casts (as 698h:39h works it out: (level + 1) / 2 below 10th, level / 2 from it,
; WIZ_LEVELS the most; the game's own counted from the class level, past the wizard spells' rows), or 0
; (the window not opened) when no level up to it has a spell it doesn't know and room for one more
; (PICK_ROOM). While CR_SPELLS picks (CR_CAP set), the same with the levels no higher than CR_CAP, rule
; or none. Flags as "or ax,ax".
pick_any:
        mov [bp - 2], ax
        call sh_pick_any                    ; (a Shinobi: its own, THE SHINOBI'S SPELLS)
        jc .flags
        cmp ax, 0
        jle .flags
        cmp si, 3
        ja .flags
        test word [cs:rules_hi], RULE_HI_INT
        jnz .levels
        push ax
        call pick_most
        or al, al
        pop ax
        jz .flags
.levels:
        push cx
        cmp ax, 10
        jae .half
        inc ax
.half:  shr ax, 1
        cmp ax, WIZ_LEVELS
        jbe .top
        mov ax, WIZ_LEVELS
.top:   push ax                     ; (CR_SPELLS's CR_CAP, or a level up's 9th: PICK_MOST)
        call pick_most
        mov cl, al
        pop ax
        or cl, cl
        je .capped
        cmp al, cl
        jbe .capped
        movzx ax, cl
.capped:
        mov [bp - 2], ax
        test word [cs:rules_hi], RULE_HI_INT
        jz .pop
        mov cl, al
.level: call pick_room
        jc .found
        dec cl
        jnz .level
.found: movzx ax, cl                        ; (0: none)
        mov [bp - 2], ax
        inc word [cs:pick_asks]
.pop:   pop cx
.flags: push bp
        mov bp, sp
        push cx
        or ax, ax
        pushf
        pop cx
        and cx, 0x08D5                      ; (OF, SF, ZF, AF, PF, CF)
        and word [bp + 6], ~0x08D5
        or [bp + 6], cx
        pop cx
        pop bp
        iret
; PICK_LIST: INT VEC_PICK_LIST replaces "mov di,ax" (93246h; 2 bytes) in CHOOSE A SPELL's page, after
; the game's list (94C7Ch) put the spells of the page's level (DS:[43ECh]) the reader (USE_WHO's) doesn't
; know at 370h:7: with the rule, none of them (DI 0) when the reader knows its INT's most of that level.
PICK_SHOWN equ 0x43EC
pick_list:
        mov di, ax
        push ax
        push cx
        push si
        push es
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov si, [es:USE_WHO_OFF]
        call ns_page_add                    ; (the new spells: NEW SPELLS)
        call sh_page_cut                    ; (a Shinobi's: its own alone, THE SHINOBI'S SPELLS)
        jc .out
        test word [cs:rules_hi], RULE_HI_INT
        jz .out
        cmp si, 3
        ja .out
        mov cl, [PICK_SHOWN]
        call pick_full
        jnc .out
        xor di, di
        inc word [cs:pick_cut]
.out:   pop es
        pop si
        pop cx
        pop ax
.ret:   iret
; PICK_PAGE: INT VEC_PICK_PAGE replaces "mov [43ECh],al" (93487h; 3 bytes: INT + NOP) where CHOOSE A
; SPELL opens on the highest spell level the reader (USE_WHO's) casts (AL, 698h:39h's): with the rule,
; the highest of them its INT has room in (PICK_ROOM; AL kept if none), so the first page isn't an empty
; one. AL the page's level, as the code goes on to show it.
pick_page:
        call sh_pick_page                   ; (a Shinobi's: its own, THE SHINOBI'S SPELLS)
        jc .set
        push cx                             ; (CR_SPELLS's CR_CAP, or a level up's 9th: PICK_MOST)
        push ax
        call pick_most
        mov cl, al
        pop ax
        or cl, cl
        jz .most
        cmp al, cl
        jbe .most
        mov al, cl
.most:  pop cx
.rule:  test word [cs:rules_hi], RULE_HI_INT
        jz .set
        push cx
        push si
        push es
        push ax
        mov cx, ds
        add cx, USE_WHO_SEG
        mov es, cx
        mov si, [es:USE_WHO_OFF]
        cmp si, 3
        ja .keep
        mov cl, al
        cmp cl, WIZ_LEVELS
        jbe .level
        mov cl, WIZ_LEVELS
.level: or cl, cl
        jz .keep
        call pick_room
        jc .room
        dec cl
        jmp .level
.room:  pop ax
        mov al, cl
        jmp .out
.keep:  pop ax
.out:   pop es
        pop si
        pop cx
.set:   mov [PICK_SHOWN], al
        iret
pick_asks dw 0                              ; (counts, for a look in play)
pick_cut  dw 0
; PICK_ROOM: CF set if party member SI doesn't know a wizard spell of level CL (1 to WIZ_LEVELS) and
; knows fewer of that level than its INT's most (PICK_FULL). DS the game's; all registers kept.
pick_room:
        call pick_full
        jc .no
        pusha
        push es
        call known_bits
        movzx di, cl
        mov al, [SPELL_STARTS + di - 1]     ; (the level's first spell ...
        mov dl, [SPELL_STARTS + di]         ;  ... and the next level's)
.each:  cmp al, dl
        jae .new
        call bit_known
        jz .yes
        inc al
        jmp .each
.new:   mov byte [cs:ns_want], 0        ; (a new spell of the level not known: NEW SPELLS)
        call ns_level_new
        or ax, ax
        jz .none
.yes:   pop es
        popa
        stc
        ret
.none:  pop es
        popa
.no:    clc
        ret
; PICK_FULL: CF set if party member SI knows as many wizard spells of level CL (1 to WIZ_LEVELS) as its
; INT lets it (INT_MOST, its row from the creature's +1Ch). DS the game's; all registers kept.
pick_full:
        cmp cl, 1
        jb .not
        cmp cl, WIZ_LEVELS
        ja .not
        pusha
        push es
        imul di, si, CREATURE_SIZE
        les bx, [CREATURES_PTR]
        movzx ax, byte [es:bx + di + CREATURE_INT]
        sub ax, INT_FIRST
        jge .high
        xor ax, ax
.high:  cmp ax, INT_ROWS - 1
        jbe .row
        mov ax, INT_ROWS - 1
.row:   mov bx, ax
        mov dh, [cs:int_most + bx]          ; (DH the most)
        call known_bits
        movzx di, cl
        mov al, [SPELL_STARTS + di - 1]
        mov dl, [SPELL_STARTS + di]
        xor ch, ch                          ; (CH those known)
.each:  cmp al, dl
        jae .done
        call bit_known
        jz .next
        inc ch
.next:  inc al
        jmp .each
.done:  mov byte [cs:ns_want], 1        ; (the new spells known of the level count too, as SL's)
        call ns_level_new
        add ch, al
        cmp ch, dh                          ; (CF while fewer)
        cmc
        pop es
        popa
        ret
.not:   clc
        ret
; KNOWN_BITS: ES:BX party member SI's known wizard spells (selector 320h's segment, KNOWN_OFF + 15 a
; member: bit n spell n, as the game's list and scroll read them). DS the game's; others kept.
KNOWN_SEG  equ 0x3D62 - 0x47E0
KNOWN_SIZE equ 15
known_bits:
        push ax
        mov ax, ds
        add ax, KNOWN_SEG
        mov es, ax
        imul bx, si, KNOWN_SIZE
        add bx, KNOWN_OFF
        pop ax
        ret
; BIT_KNOWN: ZF clear if spell AL's bit is set in ES:BX's (KNOWN_BITS). All registers kept.
bit_known:
        push ax
        push bx
        push cx
        mov cl, al
        and cl, 7
        movzx ax, al
        shr ax, 3
        add bx, ax
        mov al, 1
        shl al, cl
        test [es:bx], al
        pop cx
        pop bx
        pop ax
        ret
; SPELLS AS THE MANUAL HAS THEM (SL's spells_manual; gamepatch.SPELLS_MANUAL, the Loader's copy without them
; with the option off). In the sequel's save modifiers (83606h, SL's 79D46h; DI the modifier, [BP+0Ah]
; the target's effects' bits, far: bit n effect n, the sequel's numbers; [BP-4] the spell's flags, 2
; fire, 4 cold):
; - BLUR_SAVE replaces Barkskin's "les bx,[bp+0Ah] / test byte [es:bx],40h / jz / inc di" (8373Ah; 10
;   bytes): its +1, the game's, and Blurry's (13) +1 against magic, as the manual's.
; - FSHIELD_SAVE replaces Protection from Cold's "test word [bp-4],4 / jz / les bx,[bp+0Ah] / test byte
;   [es:bx+9],2 / jz / add di,3" (837F7h; 20 bytes): its +3, the game's, and Fire Shielded's (38) +2
;   against fire and cold, as the manual's.
BLURRY_EFFECT equ 13
FIRE_SHIELD_EFFECT equ 38
blur_save:
        les bx, [bp + 0x0A]
        test byte [es:bx], 0x40
        jz .blur
        inc di
.blur:  test byte [es:bx + BLURRY_EFFECT / 8], 1 << (BLURRY_EFFECT % 8)
        jz .out
        inc di
        inc word [cs:manual_saves]
.out:   iret
fshield_save:
        les bx, [bp + 0x0A]
        test word [bp - 4], 4
        jz .shield
        test byte [es:bx + 9], 2
        jz .shield
        add di, 3
.shield:
        test word [bp - 4], 6
        jz .out
        test byte [es:bx + FIRE_SHIELD_EFFECT / 8], 1 << (FIRE_SHIELD_EFFECT % 8)
        jz .out
        add di, 2
        inc word [cs:manual_saves]
.out:   iret
manual_saves dw 0                           ; (Blur's and Fire Shield's, counted for a look in play)
; ---- THE INVENTORY'S FULL-LENGTH PICTURE: DSCLOG's inventory_figure and inventory_load ----
; Its key in the Loader's RESOURC2.GFF matches inventoryart.py: 6000h + figure * 256 + one bit per class
; group (inventoryart.rav_chunks: Shattered Lands' dressed figures in the sequel's steady colours). What
; differs from DSCLOG's: the sequel's creature has the figure at +10h and its pictures are preloaded from
; 15h (SL's +18h, 12h), its sheets are 48h bytes at DS:19C5h (race +12h, classes +1Bh), and the loader of a
; preloaded picture is 7B827h (SL's 73034h), its way back with the picture at 7B89Eh (SL's 730ABh).
INV_ART_BASE equ 0x6000
INV_ART_FIGURES equ 14
INV_PRELOAD equ 0x15
INV_LOAD_DONE equ 0x7B89E - (0x7B831 + 3)
; INV_FIGURE (site 251, "inventory_figure"): "mov ax,[es:bx+10h] / add ax,15h" (75DD0h, SL's 6D5A3h): the
; picture of the selected creature ES:BX, its classes' key (a human's active class alone), or its figure's
; preloaded one for a figure past the 14.
inv_figure:
        mov ax, [es:bx + 0x10]
        cmp ax, INV_ART_FIGURES
        jae .stock
        push bx
        push cx
        push dx
        push si
        push di
        push es
        mov dx, ax
        shl dx, 8
        add dx, INV_ART_BASE
        mov ax, [es:bx + 4]
        call kit_sheet_ax               ; (ES:BX its sheet)
        mov cx, 3
        cmp byte [es:bx + SHEET_RACE], 1
        jne .slots
        mov cx, 1                       ; (a human dual class: the active class)
.slots: xor si, si
.next:  movzx di, byte [es:bx + si + SHEET_CLASSES]
        dec di
        cmp di, 16
        ja .skip
        movzx di, byte [cs:di + kit_class_of]
        dec di
        bts dx, di
.skip:  inc si
        loop .next
        mov ax, dx
        pop es
        pop di
        pop si
        pop dx
        pop cx
        pop bx
        iret
.stock: add ax, INV_PRELOAD
        iret

; CR_FIGURE (site 253, "creation_portrait"): "mov ax,[es:bx+10h] / add ax,15h" (6B04Fh, a race or portrait
; clicked; 6DBC4h, the screen opening; SL's 632BFh, 65F9Ch): the creation screen's full-length picture of
; the creature being made (ES:BX) made the inventory's for the classes of the sheet being made (CR_KEY).
cr_figure:
        call cr_key
        pushad
        push es
        call cr_look
        mov [cs:cr_seen], eax           ; (what is drawn: CR_REDRAW draws it again when it changes)
        pop es
        popad
        iret

; CR_LOOK: EAX the classes of the sheet being made, the figure in its top byte. BX, EDX, ES changed.
cr_look:
        les bx, [WP_CREATION]
        call sheet_classes_cr
        les bx, [CR_CREATURE]
        movzx edx, byte [es:bx + 0x10]
        shl edx, 24
        or eax, edx
        ret

; CR_KEY: AX the picture for the creation screen's figure (ES:BX its creature): INV_FIGURE's key for the
; classes of the sheet being made (WP_CREATION: numbered 1-8, the class groups; a human's one class), else
; INV_PRELOAD + the figure. All other registers kept.
cr_key:
        mov ax, [es:bx + 0x10]
        cmp ax, INV_ART_FIGURES
        jae .stock
        push bx
        push cx
        push dx
        push si
        push es
        mov dx, ax
        mov cx, 3
        cmp ax, 2
        jae .key
        mov cx, 1                       ; (a human: its one class)
.key:   shl dx, 8
        add dx, INV_ART_BASE
        les bx, [WP_CREATION]
        xor si, si
.next:  movzx ax, byte [es:bx + si + SH_CLASSES]
        dec ax
        cmp ax, 7
        ja .skip
        bts dx, ax
.skip:  inc si
        loop .next
        mov ax, dx
        pop es
        pop si
        pop dx
        pop cx
        pop bx
        ret
.stock: add ax, INV_PRELOAD
        ret

; CR_CHANGED: (KP_CLASS, after every click on the creation screen; CR_HP, as a new character's class is
; first shown) ZF clear if the classes or the figure being made have changed since the full-length picture
; was drawn (CR_FIGURE; the game draws it after a race's or a portrait's click, not after a class's), and
; then taken as drawn. EAX, BX, EDX, ES changed.
cr_changed:
        call cr_look
        cmp eax, [cs:cr_seen]
        je .ret
        mov [cs:cr_seen], eax
.ret:   ret

; CR_DRAW: the full-length picture drawn again, as after a race's click: its box's backdrop put back (the
; root's 0C8h:3B30h, with the words at 1120h) and the picture drawn (the overlay's 5F0h:98h, CR_KEY's).
; Called in a frame the overlay manager can fix up (BP pushed last, the far way back below it): the draw
; may load its overlay over the creation screen's. DS the game's; AX, BX, ES changed.
CR_BACK_SEG  equ 0x1D40 - 0x47E0        ; (0C8h's segment less DS's: 3B30h the backdrop put back)
CR_BACK_PUT  equ 0x3B30
CR_BACK      equ 0x1120                 ; (DS: the picture's box's saved backdrop, two words)
CR_DRAW_SEG  equ 0x471F - 0x47E0        ; (5F0h's stub segment less DS's: 98h a preloaded picture drawn)
CR_DRAW      equ 0x98
cr_draw:
        push word [CR_BACK]
        push word [CR_BACK + 2]
        mov ax, ds
        add ax, CR_BACK_SEG
        mov [cs:cr_call + 2], ax
        mov word [cs:cr_call], CR_BACK_PUT
        call far [cs:cr_call]
        add sp, 4
        push dword 0x3C
        push word 0x32                  ; (its place, as the game pushes it)
        les bx, [CR_CREATURE]
        call cr_key
        push ax
        mov ax, ds
        add ax, CR_DRAW_SEG
        mov [cs:cr_call + 2], ax
        mov word [cs:cr_call], CR_DRAW
        call far [cs:cr_call]
        add sp, 8
        ret
; CR_SMALL_DRAW: the small figure drawn again, as after a race's click (6B05Fh-6B07Fh): its box's backdrop put
; back (the words at 111Ch) and the figure drawn (the overlay's 5D0h:2Ah, SMALL_FIG's outfit). Called as CR_DRAW.
CR_SMALL_BACK equ 0x111C                ; (DS: the small figure's box's saved backdrop, two words)
CR_SMALL_SEG equ 0x488B - 0x4982        ; (5D0h's stub segment less DS's, read in a run: 2Ah the small figure drawn)
CR_SMALL     equ 0x2A
cr_small_draw:
        push word [CR_SMALL_BACK]
        push word [CR_SMALL_BACK + 2]
        mov ax, ds
        add ax, CR_BACK_SEG
        mov [cs:cr_call + 2], ax
        mov word [cs:cr_call], CR_BACK_PUT
        call far [cs:cr_call]
        add sp, 4
        push dword 0x160091             ; (its place: x 91h, y 16h)
        push dword [CR_CREATURE]
        mov ax, ds
        add ax, CR_SMALL_SEG
        mov [cs:cr_call + 2], ax
        mov word [cs:cr_call], CR_SMALL
        call far [cs:cr_call]
        add sp, 8
        ret
small_seen dw 0xFFFF                    ; (the creation screen's small figure as KP_CLASS last drew it)
cr_seen dd 0xFFFFFFFF
cr_call dd 0

; SMALL_FIG (site 254, "small_figure"): "mov ax,[es:bx+10h] / add ax,23h" (6F7EAh, SL's 6797Ah: DSCLOG's
; SMALL_FIGURE), the small figure of the creature ES:BX (the inventory's party column, the creation screen's):
; the Loader's frame 0 of the figure's walking picture in the outfit of its classes, BMP SMALL_BASE + INV_FIGURE's
; key (the figure * 256 + a bit per class group: ravdress.small_chunks, in OBJEX2.GFF), which INV_LOAD reads,
; the preloaded picture where there is none; the creature being made has the creation sheet's classes (CR_KEY's), drawn again
; after a class's click by KP_CLASS (CR_SMALL_DRAW). With no class (a class clicked off), the preloaded picture: a
; class-less key, absent from the GFF, quit the game with "Math Err" (2026-11-27).
SMALL_BASE equ 0x7000
SMALL_PRELOAD equ 0x23
small_fig:
        call small_key
        iret

; SMALL_KEY: AX SMALL_FIG's picture for the creature ES:BX. All other registers kept.
small_key:
        mov ax, [es:bx + 0x10]
        cmp ax, INV_ART_FIGURES
        jae .stock
        push bx
        push cx
        push dx
        push si
        push di
        push es
        mov dx, ax
        shl dx, 8
        add dx, SMALL_BASE
        mov di, es
        cmp di, [CR_CREATURE + 2]       ; (DS the game's: the creature being made?)
        jne .party
        cmp bx, [CR_CREATURE]
        jne .party
        mov cx, 3
        cmp ax, 2
        jae .cr
        mov cx, 1                       ; (a human: its one class)
.cr:    les bx, [WP_CREATION]
        xor si, si
.crnx:  movzx di, byte [es:bx + si + SH_CLASSES]
        dec di
        cmp di, 7                       ; (numbered 1-8, the class groups, on the creation sheet)
        ja .crsk
        bts dx, di
.crsk:  inc si
        loop .crnx
        jmp .done
.party: mov ax, [es:bx + 4]
        call kit_sheet_ax               ; (ES:BX its sheet)
        mov cx, 3
        cmp byte [es:bx + SHEET_RACE], 1
        jne .slots
        mov cx, 1                       ; (a human dual class: the active class)
.slots: xor si, si
.next:  movzx di, byte [es:bx + si + SHEET_CLASSES]
        dec di
        cmp di, 16
        ja .skip
        movzx di, byte [cs:di + kit_class_of]
        dec di
        bts dx, di
.skip:  inc si
        loop .next
.done:  mov ax, dx
        test al, al
        jnz .key
        sub ax, SMALL_BASE              ; (no class, as between a class's click off and another's on:
        shr ax, 8                       ;   the preloaded picture, there being no outfit to read)
        add ax, SMALL_PRELOAD
.key:   pop es
        pop di
        pop si
        pop dx
        pop cx
        pop bx
        ret
.stock: add ax, SMALL_PRELOAD
        ret

; INV_LOAD (site 252, "inventory_load"): "mov dword [bp-4],0" (7B831h, SL's 7303Eh), the preloaded
; picture SI's loader starting: an INV_FIGURE or SMALL_FIG key is read from the GFF as the game reads a
; chunk, and given back by the loader's own way out; with none (a figure or class without one), the
; figure's own preloaded picture.
inv_load:
        mov dword [bp - 4], 0
        cmp si, SMALL_BASE
        jb .art
        cmp si, SMALL_BASE + INV_ART_FIGURES * 256
        jb .read
.art:   cmp si, INV_ART_BASE
        jb .out
        cmp si, INV_ART_BASE + INV_ART_FIGURES * 256
        jae .out
.read:  call kp_if_frame                ; (it calls the game: interrupts as the caller had them)
        pusha
        push es
        push ss
        lea ax, [bp - 4]
        push ax
        movzx eax, si
        push eax
        push dword 'BMP '
        mov ax, LOAD_SEG
        mov dx, LOAD_OFF
        call pp_aim
        call far [cs:pp_call]
        add sp, 12
        pop es
        test ax, ax
        jnz .none
        cmp dword [bp - 4], 0
        je .none
        popa
        push bx
        mov bx, sp
        add word [ss:bx + 2], INV_LOAD_DONE
        pop bx
        iret
.none:  popa
        mov dword [bp - 4], 0
        cmp si, SMALL_BASE
        jb .big
        sub si, SMALL_BASE
        shr si, 8
        add si, SMALL_PRELOAD
        jmp .out
.big:   sub si, INV_ART_BASE
        shr si, 8
        add si, INV_PRELOAD
.out:   iret

; SITE: INT VEC_SITE followed by a byte, the site's number in SITE_TABLE (gamepatch's _site, as
; DSCLOG's): its routine is run as if INT had called it (the way back past the byte; registers and the
; game's BP as they were). Saves the vectors (one for many sites).
site_int:
        push bp
        mov bp, sp
        push bx
        push ds
        lds bx, [bp + 2]                    ; (the way back: the site's byte)
        movzx bx, byte [bx]
        inc word [bp + 2]
        pop ds
        shl bx, 1
        push fs
        call tail_fs
        mov bx, [fs:site_table + bx]        ; (SITE_TABLE: the tail's)
        pop fs
        mov [cs:site_jump], bx
        pop bx
        pop bp
        jmp [cs:site_jump]
site_jump dw 0
site_none:
        iret
section tail                                ; (SITE_TABLE: the tail's, to RULE_NEW_SPELLS)
site_table:
        dw stink_round                      ; 0 SITE_STINK
        dw hd_save                          ; 1 SITE_HD_SAVE
        dw chaos_save                       ; 2 SITE_CHAOS
        dw spray_save                       ; 3 SITE_SPRAY
        dw cloud_save                       ; 4 SITE_CLOUD_SAVE
        dw cloud_kill                       ; 5 SITE_CLOUD_KILL
        dw flame_count                      ; 6 SITE_FLAME
        dw bio_least                        ; 7 SITE_BIO
        dw cast_start                       ; 8 SITE_CAST
        dw lowres_site                      ; 9 SITE_LOWRES
        dw strength_dice                    ; 10 SITE_STRENGTH
        dw cell_heal                        ; 11 SITE_CELL
        dw psi_feeble                       ; 12 SITE_PSI
        dw rainbow_hurt                     ; 13 SITE_RAINBOW
        dw hold_hd                          ; 14 SITE_HOLD_HD
        dw tu_site                          ; 15 SITE_TURN
        dw th_site                          ; 16 SITE_TO_HIT
        dw rest_hp                          ; 17 SITE_REST_HP
        dw rest_pre                         ; 18 SITE_REST_PRE
        dw cu_site                          ; 19 SITE_CAN_USE
        dw belt_site                        ; 20 SITE_THIEF_SKILL
        dw cast_armour                      ; 21 SITE_CAST_ARMOUR
        dw item_weapon                      ; 22 SITE_ITEM_WEAPON
        dw item_skip                        ; 23 SITE_ITEM_SKIP
        dw item_armour                      ; 24 SITE_ITEM_ARMOUR
        dw mc_con                           ; 25 SITE_MC_CON
        dw mc_uncon                         ; 26 SITE_MC_UNCON
        dw rl_score                         ; 27 SITE_RL_SCORE
        dw rl_hp                            ; 28 SITE_RL_HP
        dw rl_roll                          ; 29 SITE_RL_ROLL
        dw rl_con                           ; 30 SITE_RL_CON
        dw rl_sum                           ; 31 SITE_RL_SUM
        dw xp_need                          ; 32 SITE_XP_NEED
        dw priest_thac0                     ; 33 SITE_PRIEST_THAC0
        dw adnd_slots                       ; 34 SITE_ADND_SLOTS
        dw regen_site                       ; 35 SITE_REGEN
        dw con_save                         ; 36 SITE_CON_SAVE
        dw dual_level                       ; 37 SITE_DUAL_LEVEL
        dw dual_old                         ; 38 SITE_DUAL_OLD
        dw dual_new                         ; 39 SITE_DUAL_NEW
        dw probe_floor_all                  ; 40 SITE_FLOOR_ALL (WALL SHADOWS: the view's floor drawn, 2B81Ch)
        dw probe_floor_rect                 ; 41 SITE_FLOOR_RECT (... a rectangle of it, 2B97Fh)
        dw name_push                        ; 42 SITE_NAME (an item's name read, ITEM NAMES)
        dw prot_ac                          ; 43 SITE_PROT_AC (a worn item's AC counted, PROTECTION)
        dw prot_save                        ; 44 SITE_PROT_SAVE (a save's modifiers started)
        dw amulet_mr                        ; 45 SITE_AMULET_MR (a target's magic resistance tested)
        dw weapon_cast                      ; 46 SITE_WEAPON_CAST (a weapon's spell cast on a hit)
        dw join_ready                       ; 47 SITE_JOIN_READY (a member joined: its worn items readied)
        dw tome_read                        ; 48 SITE_TOME (the Tome of Understanding read: +1 WIS)
        dw plain_arrow                      ; 49 SITE_PLAIN_ARROW (a spell arrow shot by a non-preserver: no spell)
        dw new_sheet                        ; 50 SITE_NEW_SHEET (a character made: its sheet's last 6 bytes cleared)
        dw spec_damage                      ; 51 SITE_SPEC_DAMAGE (a weapon's damage bonus: weapon specialization's)
        dw thief_skill                      ; 52 SITE_THIEF_TABLE (a thief skill: AD&D's table, Dark Sun's DEX)
        dw stab_times                       ; 53 SITE_STAB (a backstab: the weapon's dice multiplied; an Assassin's one more)
        dw price_cx                           ; 54 SITE_PRICE_CX (a shop's price shown: the leader's CHA)
        dw price_eax                          ; 55 SITE_PRICE_EAX (... charged, or the list's affordable test)
        dw sell_price                         ; 56 SITE_SELL_PRICE (what a shop pays: 60%)
        dw sell_keep                          ; 57 SITE_SELL_KEEP (a magical item sold: into the merchant's pack)
        dw msg_shown                          ; 58 SITE_MSG_SHOWN (a message box's wait: the window on show)
        dw msg_window                         ; 59 SITE_MSG_WINDOW (a message box's window opened: counted)
        dw kit_init                         ; 60 SITE_KIT_INIT (a combatant's initiative: the kits')
        dw kit_ranger_cast                  ; 61 SITE_KIT_RANGER_CAST (a ranger's caster level: a Seeker's, a Justifier's)
        dw kp_disc_win                     ; 62 SITE_KP_DISC_WIN (the creation panel's disciplines opened: KITS for their button)
        dw kp_sphere_win                   ; 63 SITE_KP_SPHERE_WIN (... its spheres)
        dw kp_disc_click                   ; 64 SITE_KP_DISC_CLICK (a click on the disciplines: KITS opens the kit page)
        dw kp_sphere_click                 ; 65 SITE_KP_SPHERE_CLICK (... on the spheres, or a kit page)
        dw kp_shown                        ; 66 SITE_KP_SHOWN (the spheres' window up? A kit page too)
        dw kp_class                        ; 67 SITE_KP_CLASS (a click on the creation screen: the kit and the panel for the classes)
        dw kp_race                         ; 68 SITE_KP_RACE (a new race: the panel for its class)
        dw kp_open                         ; 69 SITE_KP_OPEN (the creation screen opening)
        dw dam_line                         ; 70 SITE_DAM_LINE (the inventory's DAM line, a melee weapon's attacks)
        dw missile_line                     ; 71 SITE_MISSILE_LINE (... a missile weapon's, or an item box's)
        dw view_dam                         ; 72 SITE_VIEW_DAM (View Character's DAM line)
        dw ef_rows                          ; 73 SITE_EF_ROWS (the Effects screen's cells filled: the kits and weapon kinds)
        dw ef_click                         ; 74 SITE_EF_CLICK (a click on its cells: the next page of them)
        dw unlook                           ; 75 SITE_UNLOOK (the Look box closed: the whole description)
        dw dual_kit                         ; 76 SITE_DUAL_KIT (a human's new class: its kit asked on the game's menu)
        dw probe_hit                        ; 77 SITE_HIT (29DBDh: the finder of what is under the pointer: the chosen enemy after Enter)
        dw rg_two                           ; 78 SITE_RG_TWO (5DE67h: a ranger with two weapons: none of the penalty in light armour only)
        dw blast_loss                       ; 79 SITE_BLAST_LOSS (6662Dh: Psionic Blast's loss: BLAST_HP for a party member)
        dw blast_ko                         ; 80 SITE_BLAST_KO (5CC51h: the death test: knocked out while BLAST_HP is owed)
        dw rl_try                           ; 81 SITE_RL_TRY (6C585h: an ability's 4d4 on the creation screen, for the dice log)
        dw shop_loop                        ; 82 SITE_SHOP_LOOP (88D99h: the shop's loop's test: SHOP_AT for S, SELL_KEY)
        dw rs_click                         ; 83 SITE_RS_CLICK (6DE85h: a button on the creation screen: STORE and RECALL)
        dw greq_load                        ; 84 SITE_GREQ_LOAD (7DA30h: a loaded save's GREQ number: the quick saves' own)
        dw gear_done                        ; 85 SITE_GEAR_DONE (6E2F2h: DONE has given a new character the game's gear: the Loader's)
        dw ns_info                          ; 86 SITE_NS_INFO (9AA95h: an item's INFO text: no new spell's on an item's own effect)
        dw cr_picks                        ; 87 SITE_CR_PICKS (6ED55h: a new member's spells and powers given: picked on the game's windows)
        dw psi_grant                       ; 88 SITE_PSI_GRANT (6E9C9h, 6E9F7h: a new member's power given: a pick, or kept on EDIT)
        dw site_none                        ; 89 (none here)
        dw sh_sphere_di                     ; 90 SITE_EL_KNOW (62C00h: a class of the member casts a spell: the Elementalist's second sphere, a Shinobi's wizard spells)
        dw sh_sphere_bp                     ; 91 SITE_EL_LEVEL (628AFh: the cast's level, the same)
        dw sh_sphere_bp                     ; 92 SITE_EL_CAST (97DC5h: the caster level, the same)
        dw probe_text                       ; 93 SITE_TEXT (87BA0h: the dialogue window's input: TEXT, for the Loader's Dialogue tab)
        dw probe_msg                        ; 94 SITE_MSG (59A0Bh: the message box: TEXT, the same)
        dw psi_count                       ; 95 SITE_PSI_COUNT (93B95h: the psionicists' pop-up opening: PSI_DUE's picks)
        dw psi_list                        ; 96 SITE_PSI_LIST (93E1Bh: its list: no power known)
        dw psi_cycle                       ; 97 SITE_PSI_CYCLE (93FF1h: its discipline button: its own only for one not a psionicist)
        dw psi_click                       ; 98 SITE_PSI_CLICK (94245h: a known power clicked: nothing)
        dw pick_top                        ; 99 SITE_PICK_TOP (93831h: CHOOSE A SPELL's level button: no higher than CR_CAP)
        dw f10_pin                          ; 100 SITE_F10_PIN (1EC36h: F10's standing-still test: a pinned member left where it is)
        dw site_none                        ; 101 (none here)
        dw site_none                        ; 102 (none here)
        dw site_none                        ; 103 (none here)
        dw site_none                        ; 104 (none here)
        dw site_none                        ; 105 (none here)
        dw site_none                        ; 106 (none here)
        dw site_none                        ; 107 (none here)
        dw site_none                        ; 108 (none here)
        dw site_none                        ; 109 (none here)
        dw lv_up                            ; 110 SITE_LV_UP (959A5h: the level up's cap: RAV_XP_CAP's share, LEVEL_ROOM)
        dw lv_view                          ; 111 SITE_LV_VIEW (6FB51h: View Character's next level: the same)
        dw lv_clamp                         ; 112 SITE_LV_CLAMP (958BDh: the level up's hold on XP: none past the table)
        dw hd_roll                          ; 113 SITE_HD_ROLL (94FECh: a level's hit die: a thief's d6 to 10th)
        dw hd_con                           ; 114 SITE_HD_CON (95460h: the most hit points' dice levels: the same)
        dw hd_clamp                         ; 115 SITE_HD_CLAMP (95471h: ... kept)
        dw save_base                        ; 116 SITE_SAVE_BASE (955DFh: a save: the Player's Handbook's table)
        dw xp_suffix_site                   ; 117 SITE_XP_SUFFIX (6FC08h: View Character's next XP: the class it is for)
        dw lv_ordinal                       ; 118 SITE_LV_ORDINAL (959D3h: the level up's "21st", not "21th")
        dw site_none                        ; 119 (none here)
        dw cr_weapons                      ; 120 SITE_CR_WEAPONS (6E2ECh: DONE before the game's gear: a new member's weapon specs picked on the weapon window)
        dw pk_win                          ; 121 SITE_PK_WIN (93C94h: the psionicists' pop-up's window: the weapon window in weapon mode)
        dw pk_title                        ; 122 SITE_PK_TITLE (93D63h: its title: none in weapon mode)
        dw pk_fill                         ; 123 SITE_PK_FILL (93DECh: its powers' list: the weapon slots in use or not)
        dw pk_click                        ; 124 SITE_PK_CLICK (93FABh: a button clicked: a weapon slot taken)
        dw pk_hover                        ; 125 SITE_PK_HOVER (93BBAh: its event loop: the weapon slot under the pointer named)
        dw site_none                        ; 126 (none here)
        dw site_none                        ; 127 (none here)
        dw site_none                        ; 128 (none here)
        dw site_none                        ; 129 (none here)
        dw site_none                        ; 130 (another's)
        dw site_none                        ; 131 (another's)
        dw site_none                        ; 132 (another's)
        dw site_none                        ; 133 (another's)
        dw site_none                        ; 134 (another's)
        dw site_none                        ; 135 (another's)
        dw site_none                        ; 136 (another's)
        dw site_none                        ; 137 (another's)
        dw site_none                        ; 138 (another's)
        dw site_none                        ; 139 (another's)
        dw ns_cmp                           ; 140 SITE_NS_CMP (a spell's compare with a range's end: a new spell a wizard's)
        dw ns_know                          ; 141 SITE_NS_KNOW (62625h: "does member know spell": a new one's sheet bit)
        dw ns_level                         ; 142 SITE_NS_LEVEL (62AD0h: a spell's level: a new one's own)
        dw ns_list                          ; 143 SITE_NS_LIST (6254Fh: the USE screen's list of a level: the new ones known)
        dw ns_cast                          ; 144 SITE_NS_CAST (656D0h: the spell handler's case: Cat's Grace's and Friends' Strength's)
        dw ns_effect                        ; 145 SITE_NS_EFFECT (6623Bh: Strength's case's effect: Cat's Grace's, Friends' own)
        dw ns_ability                       ; 146 SITE_NS_ABILITY (85351h: the abilities' effects: DEX for Cat's Grace, CHA for Friends)
        dw ns_claw                          ; 147 SITE_NS_CLAW (86A45h: a natural attack's dice: Erdlu Claw's 1d6+1)
        dw ns_scroll                        ; 148 SITE_NS_SCROLL (999FBh: a wizard scroll read: a new spell taught from it)
        dw ns_learn                         ; 149 SITE_NS_LEARN (936B4h: CHOOSE A SPELL's pick: a new one's sheet bit)
        dw lv_weapons                       ; 150 SITE_LV_WEAPONS (957BEh: the level up: weapon specs due picked on the weapon window)
        dw site_none                        ; 151 (none here)
        dw site_none                        ; 152 (none here)
        dw site_none                        ; 153 (none here)
        dw site_none                        ; 154 (none here)
        dw site_none                        ; 155 (none here)
        dw site_none                        ; 156 (none here)
        dw site_none                        ; 157 (none here)
        dw site_none                        ; 158 (none here)
        dw site_none                        ; 159 (none here)
        dw fig_wide_all                     ; 160 SITE_FIG_WIDE_ALL (2868Ch: the redraw of what moved: wider, for the figures' shadows)
        dw fig_wide                         ; 161 SITE_FIG_WIDE (2828Ch: the redraw of a rectangle of the view: the same)
        dw fig_keep                         ; 162 SITE_FIG_KEEP (2A347h: a thing drawn: its frame's shadow kept, for when its picture is out)
        dw shop_shine                       ; 163 SITE_SHOP_SHINE (2F7BEh: the wait for an event, its test: a shop's magic items shine)
        dw site_none                        ; 164 (none here)
        dw site_none                        ; 165 (none here)
        dw site_none                        ; 166 (none here)
        dw site_none                        ; 167 (none here)
        dw site_none                        ; 168 (none here)
        dw site_none                        ; 169 (none here)
        dw mouse_init                       ; 170 SITE_MOUSE_INIT (39F0Bh: the mouse driver reset at the start: as fast up and down as across)
        dw mouse_set                        ; 171 SITE_MOUSE_SET (2F110h: the mouse given its ranges: the pointer where it was)
        dw speech_wait                      ; 172 SITE_SPEECH_WAIT (69BE2h: the wait while a narration plays: the pointer, a click ends it)
        dw fli_key                          ; 173 SITE_FLI_KEY (8335Ch: a FLI's frame shown, Shift tested: the pointer, a click as Shift)
        dw fli_end                          ; 174 SITE_FLI_END (8324Dh: the FLI played or ended: the pointer wiped)
        dw site_none                        ; 175 (none here)
        dw site_none                        ; 176 (none here)
        dw site_none                        ; 177 (none here)
        dw site_none                        ; 178 (none here)
        dw site_none                        ; 179 (none here)
        dw pp_show                          ; 180 SITE_PP_SHOW (97AF4h: the USE screen's Turn Undead button shown: a thief's purse)
        dw pp_click                         ; 181 SITE_PP_CLICK (97623h: ... let go of: the thief's as pressed)
        dw pp_lit                           ; 182 SITE_PP_LIT (9767Bh: ... the screen closed: the menu button's icon as it was)
        dw pp_arm                           ; 183 SITE_PP_ARM (97699h: ... Turn Undead readied: the thief's pick readied instead)
        dw pp_text                          ; 184 SITE_PP_TEXT (975CBh, 97702h: ... its name under the screen: PICK POCKETS)
        dw pp_info                          ; 185 SITE_PP_INFO (97716h: ... a right click: no spell's description for the purse)
        dw pp_hand                          ; 186 SITE_PP_HAND (630F8h: a click on the map with the talk pointer: the pick)
        dw site_none                        ; 187 (none here)
        dw site_none                        ; 188 (none here)
        dw site_none                        ; 189 (none here)
        dw shinobi_mage                     ; 190 SITE_SHINOBI_MAGE (627D6h: the slot routine's "casts wizard spells": a Shinobi's thief class)
        dw psp_use                          ; 191 SITE_PSP_USE (6178Eh: a power's cost used: the kits', KIT_PSP)
        dw psp_table                        ; 192 SITE_PSP_TABLE (6162Dh, 6183Dh: a power's cost checked, half taken when it fails)
        dw psp_defence                      ; 193 SITE_PSP_DEFENCE (61FA1h: a psionic defence's cost paid)
        dw psp_keep                         ; 194 SITE_PSP_KEEP (619DCh: a power's cost to keep it up)
        dw psp_keep_dx                      ; 195 SITE_PSP_KEEP_DX (616A8h: ... checked, the combatant in DX)
        dw kit_hit_die                      ; 196 SITE_HIT_DIE (95014h: a level's hit die: a Battle Mage's d6, an Arcanist's d3)
        dw kit_hit_gain                     ; 197 SITE_HIT_GAIN (95000h: a level's gain past the dice: a Battle Mage's 2, an Arcanist's 1)
        dw kit_max_psp                      ; 198 SITE_MAX_PSP (95172h: the level up's most PSP: a Mind Warrior's a fifth fewer)
        dw hit_round                        ; 199 SITE_HIT_ROUND (5CD76h: a hit's mark against casting: a Battle Mage none)
        dw cr_die                           ; 200 SITE_CR_DIE (6D28Fh: the creation hit points' most, a level's die: a Battle Mage's d6, an Arcanist's d3)
        dw cr_psp                           ; 201 SITE_CR_PSP (6D85Eh: the creation PSP's end: a Mind Warrior's a fifth fewer)
        dw sf_site                          ; 202 SITE_SF_BACK (5D308h: the swing loop's "cmp ax,[bp-0Ah]": a second foe's swing over, the first target back)
        dw site_none                        ; 203 (none here: held for other work)
        dw site_none                        ; 204 (none here: held for other work)
        dw kit_cast_level                   ; 205 SITE_KIT_CAST_LEVEL (629FEh: a spell's level for its duration and damage: an Arcanist's, a Spirit Caller's, a Wasteland Seer's)
        dw kit_cure                         ; 206 SITE_KIT_CURE (66545h: a cure's healing: a Healer's, Lifebinder's, Rescuer's more)
        dw avenger_area                     ; 207 SITE_AVENGER_AREA (7E7A6h: a spell's damage rolled: a Wilderness Avenger's Cause Wounds)
        dw avenger_one                      ; 208 SITE_AVENGER_ONE (7F727h: ... a one-creature spell's)
        dw sh_cast_level                    ; 209 SITE_SHINOBI_CAST_LEVEL (97DF1h: the caster level's class level: a Shinobi's thief level less 5)
        dw scholar_level_up                 ; 210 SITE_SHINOBI_LEVEL_UP (957ABh: a level up's preserver's spell pick: a Scholar's one more, a Shinobi's at its thief level up)
        dw site_none                        ; 211 (none here: held for other work)
        dw site_none                        ; 212 (none here: held for other work)
        dw site_none                        ; 213 (none here: held for other work)
        dw poison_hit                       ; 214 SITE_POISON_HIT (5D20Dh: a weapon hit's "does it cast": a Poisoner's poison)
        dw arrow_plus                       ; 215 SITE_ARROW_PLUS (5D456h: the ammunition's plus kept: a Spellarcher's spell arrows')
        dw page_open                        ; 216 SITE_PAGE_OPEN (7D691h: the save or load window drawn as it opens: its page's label)
        dw ammo_cap                         ; 217 SITE_AMMO_CAP (5D031h: a shot's attacks cut to the arrows left: the round's kept)
        dw ammo_turn                        ; 218 SITE_AMMO_TURN (5D32Ch: the attacks spent: a party member's turn kept with shots due)
        dw ammo_okay                        ; 219 SITE_AMMO_OKAY (5CA92h, 5CAF7h, 5CB64h: the attack command's target Okay: fallen for it)
        dw save_sum                         ; 220 SITE_SAVE_SUM (66E86h: a save's d20 and modifiers added: kept in its byte)
        dw save_nat                         ; 221 SITE_SAVE_NAT (66EA3h: a natural 20 saves unless the save can't be made)
        times 230 - ($ - site_table) / 2 dw site_none
        dw camera_walk                      ; 230 SITE_CAMERA_WALK (200B7h: a fight's figure stepped: the view kept while it is on screen)
        dw party_load                       ; 231 SITE_PARTY_LOAD (70DA6h: a game loaded with the party in one figure: spread out)
        dw party_gather                     ; 232 SITE_PARTY_GATHER (6A823h: the party put in one figure: after a fight, spread out again)
        dw pace_pass                        ; 233 SITE_PACE_PASS (21AB6h: the map's step for everything: STEADY PACE's count)
        dw pace_draw                        ; 234 SITE_PACE_DRAW (21AFAh: the drawing of what moved and the flip: STEADY PACE)
        dw cr_age_new                       ; 235 SITE_CR_AGE_NEW (6D6AEh: PSP drawn anew on the creation screen)
        dw cr_age_con                       ; 236 SITE_CR_AGE_CON (6B79Ch: PSP drawn after a click on CON)
        dw flip_wait                        ; 237 SITE_FLIP_WAIT (1698Fh: the page flip's wait for the retrace: none with a full screen up)
        dw page_key                         ; 238 SITE_PAGE_KEY (7DABCh: a key the save and load window has no use for: PgUp, PgDn the pages)
        dw greq_save                        ; 239 SITE_GREQ_SAVE (7D8A1h, 7D8BAh: a save's GREQ number: its page's own)
        times 240 - ($ - site_table) / 2 dw site_none
        dw pp_close                         ; 240 SITE_PP_CLOSE (9659Eh: the USE screen closing lets go of Turn Undead's icon: the arrows' too)
        dw lock_site                        ; 241 SITE_LOCK (8C7E6h: a thief skill check's chance: a lock failed at this thief level barred)
        dw gl_armour                        ; 242 SITE_GL_ARMOUR (5D6B3h: the AC routine's gladiator test: armour optimisation needs armour)
        dw ai_wall                          ; 243 SITE_AI_WALL (5EE6Bh: the computer's cast, its two points: a wall across the line of fire)
        dw kreen_claws                      ; 244 SITE_KREEN_CLAWS (5C86Dh: a natural attack's magic tested: a party thri-kreen's claws and bite cut)
        dw berserk_add                      ; 245 SITE_BERSERK_ADD (822A1h: an effect's add, no case of its own: Berserk keeps the side it had)
        dw berserk_end                      ; 246 SITE_BERSERK_END (827D6h: an effect's end, no case of its own: Berserk gives the side back)
        dw ef_charges                       ; 247 SITE_EF_CHARGES (8ABBDh: the Effects screen's line under the pointer: an effect's charges)
        dw scholar_thac0                    ; 248 SITE_SCHOLAR_THAC0 (953A1h: the THAC0 routine's end: a Scholar's 1 worse)
        dw size_line                        ; 249 SITE_SIZE_LINE (7B1CFh: a weapon's damage line drawn: an item box's large dice)
        dw size_pre                         ; 250 SITE_SIZE_PRE (7B1B2h: ... about to be drawn: Shillelagh's 1D6+1)
        dw inv_figure                       ; 251 SITE_INV_FIGURE (75DD0h: the inventory's full-length picture: the class's)
        dw inv_load                         ; 252 SITE_INV_LOAD (7B831h: a preloaded picture's loader: the class's from the GFF)
        dw cr_figure                        ; 253 SITE_CR_FIGURE (6B04Fh, 6DBC4h: the creation screen's full-length picture: the class's)
        dw small_fig                        ; 254 SITE_SMALL_FIG (6F7EAh: the party column's small figure: the outfit's)
; NEW SPELLS (the sequel; dsloader/ravspells.py, RULE_NEW_SPELLS): the mod's six new wizard spells, numbered
; past the sequel's 320 records (NS_FIRST: 320-325, Cat's Grace, Erdlu Claw, Fogbolt, Reflected Image, Spook,
; Friends; their records, icons and descriptions in the Loader's RESOURC2.GFF), known by the sheet's bits as
; in Shattered Lands (NS_KNOWN_AT, NS_KNOWN_BIT: +3Fh, the Elementalist's second sphere's byte, and the kit
; byte's top bit for Friends), which the party transfer carries.
; - NS_CMP (site 140): the game's compares of a spell's number with its ranges' ends (73h the priests',
;   EBh the psionic powers', 10Dh the monsters'), found by the way back's IP and the word there in
;   NS_CMP_TABLE (ns_cmp_table.inc, ravspells.cmp_table_asm), each made with a new spell as wizard spell
;   NS_AS: the compare's flags into the INT's frame.
; - NS_KNOW (site 141): "does member know spell" (6260Ah), its "cmp word [bp+8],73h" (62625h): a new spell
;   answered from member [BP+6]'s sheet (AL, out at 626B0h), else the compare.
; - NS_LEVEL (site 142): a spell's level (62AC5h), its "cmp dx,73h" (62AD0h): a new spell's own (CL, out at
;   62B19h), else the compare.
; - NS_LIST (site 143): the USE screen's list of a level's spells (62500h; [BP+6] the member, [BP+8] the
;   list, far, or 0 to count, [BP+0Ch] bit 0 the wizards', [BP+0Eh] the level, [BP-4] the most), its "xor
;   si,si / cmp di,[bp-2]" (6254Fh) as it starts: the new spells of that level the member knows put first
;   (SI their count), then the compare.
section image
RULE_NEW_SPELLS equ 32
NS_FIRST     equ 320
NS_COUNT     equ 6
NS_AS        equ 0x72               ; (a wizard spell's number for the compares: any below 73h)
NS_PRIESTS   equ 0x73
NS_PLUS1     equ 0x80               ; (NS_CMP_TABLE's form: the operand is the spell + 1, an item's power)
NS_KNOW_OUT  equ 0x626B0 - 0x62628  ; (the known test's way out, AL the answer, less the INT's way back)
NS_LEVEL_OUT equ 0x62B19 - 0x62AD3  ; (the level's way out, CL the level, the same)
NS_LIST_MOST equ -4                 ; ([BP-4] the list's room)
NS_LIST_END  equ -2                 ; ([BP-2] the level's end)
ns_known_at  db SPHERE2, SPHERE2, SPHERE2, SPHERE2, SPHERE2, KIT_BYTE
ns_known_bit db 0x10, 0x20, 0x40, 0x08, 0x80, 0x80
ns_levels    db 2, 1, 1, 1, 1, 1
ns_cmps      dw 0                   ; (counts for a look in play: compares made a wizard's, ...
ns_lost      dw 0                   ;   ... an NS_CMP site not in the table, ...
ns_knows_n   dw 0                   ;   ... new spells answered known, ...
ns_listed    dw 0                   ;   ... and put on the USE screen's lists)
; NS_NEW: CF set if AX is a new spell and the rule is on, BX then its place (0 to NS_COUNT - 1). Others kept.
ns_new:
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .no
        cmp ax, NS_FIRST
        jb .no
        cmp ax, NS_FIRST + NS_COUNT
        jae .no
        mov bx, ax
        sub bx, NS_FIRST
        stc
        ret
.no:    clc
        ret
; NS_KNOWS: ZF clear if party member SI knows new spell BX (0 to NS_COUNT - 1): its sheet's bit. DS the
; game's; all registers kept.
ns_knows:
        push ax
        push bx
        push di
        push es
        mov di, bx
        mov ax, si
        call kit_sheet
        movzx ax, byte [cs:di + ns_known_at]
        add bx, ax
        mov al, [es:bx]
        cmp byte [cs:di + ns_known_at], KIT_BYTE
        jne .bit
        sub bx, KIT_BYTE
        call kit_open_at
        lea bx, [bx + KIT_BYTE]     ; (the flags kept)
        jne .bit
        xor al, al                  ; (no kit chosen: no bit)
.bit:   test al, [cs:di + ns_known_bit]
        pop es
        pop di
        pop bx
        pop ax
        ret
ns_cmp:
        pushad
        push es
        mov di, sp
        les bx, [ss:di + 34]        ; (the way back: its IP, and the word there)
        mov ax, bx
        mov dx, [es:bx]
        push fs
        call tail_fs                ; (NS_CMP_TABLE: the tail's)
        mov si, ns_cmp_table
.find:  cmp si, ns_cmp_table_end
        jae .lost
        cmp [fs:si], ax
        jne .next
        cmp [fs:si + 2], dx
        je .found
.next:  add si, 10
        jmp .find
.lost:  pop fs
        inc word [cs:ns_lost]
        pop es
        popad
        iret
.found: mov eax, [fs:si + 4]        ; (the entry's form to its immediate into NS_ENTRY, SI there)
        mov [cs:ns_entry + 4], eax
        mov ax, [fs:si + 8]
        mov [cs:ns_entry + 8], ax
        pop fs
        mov si, ns_entry
        mov al, [cs:si + 4]         ; (the form; its NS_PLUS1 bit apart)
        and al, ~NS_PLUS1
        cmp al, 0
        jne .bp
        movzx bx, byte [cs:si + 5]  ; (a register: PUSHAD's, EAX at +30 down to EDI at +2)
        shl bx, 2
        neg bx
        add bx, di
        mov ax, [ss:bx + 30]
        jmp .have
.bp:    cmp al, 1
        jne .mem
        mov bx, [ss:di + 10]        ; ([BP+disp], the game's BP)
        add bx, [cs:si + 6]
        mov ax, [ss:bx]
        jmp .have
.mem:   cmp al, 2
        jne .es_bx
        mov bx, [cs:si + 6]         ; ([disp], DS the game's)
        mov ax, [bx]
        jmp .have
.es_bx: mov es, [ss:di]             ; (ES:[BX+disp], the game's ES and BX)
        mov bx, [ss:di + 18]
        add bx, [cs:si + 6]
        mov ax, [es:bx]
.have:  push bx
        push ax
        test byte [cs:si + 4], NS_PLUS1
        jz .new
        dec ax                      ; (an item's power: the spell + 1)
.new:   call ns_new
        jnc .old
        test byte [cs:si + 4], NS_PLUS1
        jz .old
        mov bx, [cs:si + 6]
        call ns_book                ; (an item's power: a new spell's only on a scroll or a book)
.old:   pop ax
        pop bx
        jnc .cmp
        mov ax, NS_AS
        inc word [cs:ns_cmps]
.cmp:   cmp ax, [cs:si + 8]
        pushf
        pop ax
        jmp acid_flags
ns_entry times 10 db 0         ; (NS_CMP's entry found, copied from the tail)
; NS_BOOK: CF set if the item an NS_PLUS1 compare reads the power of is a wizard's scroll or spellbook (type
; NS_BOOK_TYPE, the game's and the mod's scrolls', spellbooks' and rods'): the item at the game's ES:BX, or (BX,
; the entry's displacement, not 0) the item numbered by the word at the game's [BP+BX]. The game's own effects of an item
; (powers 140h to 147h: the psionic powerstone's 146h, the Ioun stones' 142h, a staff's 143h...) take the
; powers the new spells' scrolls have (141h to 146h): on any other item the power is the game's effect
; (the walkthrough's bugs, 2026-11-28: the stones' effect never taken off with the rule, their pictures the
; new spells'). DI NS_CMP's frame; DS the game's; all registers kept.
NS_BOOK_TYPE equ 77
ns_book:
        push ax
        push bx
        push es
        or bx, bx
        jnz .index
        mov es, [ss:di]             ; (the game's ES and BX)
        mov bx, [ss:di + 18]
        jmp .type
.index: add bx, [ss:di + 10]        ; ([BP+disp], the game's BP: the item's number)
        imul ax, [ss:bx], ITEM_SIZE
        les bx, [ITEMS_PTR]
        add bx, ax
.type:  cmp word [es:bx + ITEM_TYPE], NS_BOOK_TYPE
        stc
        je .out
        clc
.out:   pop es
        pop bx
        pop ax
        ret
; - NS_INFO (site 86): the item box's INFO (9A94Eh, [BP+6] the item's +2 word, the spell + 1, its caller's SI
;   the item at [BP-0Eh]), its "movzx eax,di" (9AA95h) before the SPIN text is looked up: a number a new
;   spell's text has (141h to 146h, ravspells' SPIN 321-326) on an item that isn't a wizard's scroll or book
;   (NS_BOOK) is one of the game's own item effects, which have no text: NS_NO_TEXT, so the box says UNKNOWN as
;   the game's does, not a new spell's description (the lemon, the powerstone, Ioun stones; 2026-11-28).
NS_NO_TEXT   equ 0x7FFF               ; (no SPIN chunk has it)
ns_info:
        pushad
        push es
        mov di, sp
        movzx eax, word [ss:di + 2]     ; (the game's DI)
        dec ax                          ; (the spell + 1)
        call ns_new
        inc ax
        jnc .put
        mov bx, -0x0E                   ; (the item's number at the game's [BP-0Eh])
        call ns_book
        jc .put
        mov eax, NS_NO_TEXT
.put:   mov [ss:di + 30], eax           ; (the game's EAX)
        pop es
        popad
        iret
section tail
ns_cmp_table:
%include "ns_cmp_table.inc"
ns_cmp_table_end:
section image
ns_know:
        pushad
        push es
        mov ax, [bp + 8]
        call ns_new
        jnc .cmp
        mov si, [bp + 6]
        call ns_knows
        setnz al
        mov di, sp
        mov [ss:di + 30], al        ; (the game's AL)
        add word [ss:di + 34], NS_KNOW_OUT
        inc word [cs:ns_knows_n]
        pop es
        popad
        iret
.cmp:   cmp ax, NS_PRIESTS
        pushf
        pop ax
        jmp acid_flags
ns_level:
        pushad
        push es
        mov ax, dx
        call ns_new
        jnc .cmp
        mov al, [cs:bx + ns_levels]
        mov di, sp
        mov [ss:di + 26], al        ; (the game's CL)
        add word [ss:di + 34], NS_LEVEL_OUT
        pop es
        popad
        iret
.cmp:   cmp ax, NS_PRIESTS
        pushf
        pop ax
        jmp acid_flags
ns_list:
        pushad
        push es
        xor cx, cx                  ; (CX the new spells put)
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .done
        test byte [bp + 0x0C], 1
        jz .done                    ; (not the wizards')
        mov dx, [bp + 0x0E]         ; (DL the level)
        cmp dx, 1
        jl .done
        cmp dx, 9
        jg .done
        mov si, [bp + 6]
        cmp si, 4
        jae .done
        xor bx, bx
.each:  cmp [cs:bx + ns_levels], dl
        jne .next
        call ns_knows
        jz .next
        cmp cx, [bp + NS_LIST_MOST]
        jge .done
        cmp dword [bp + 8], 0
        je .count
        les di, [bp + 8]
        mov ax, cx
        shl ax, 1
        add di, ax
        lea ax, [bx + NS_FIRST]
        mov [es:di], ax
.count: inc cx
        inc word [cs:ns_listed]
.next:  inc bx
        cmp bx, NS_COUNT
        jb .each
.done:  mov di, sp
        mov [ss:di + 6], cx         ; (the game's SI: the count so far)
        mov ax, [ss:di + 2]         ; (the game's DI, the level's first spell)
        cmp ax, [bp + NS_LIST_END]
        pushf
        pop ax
        jmp acid_flags

; - NS_CAST (site 144): the spell handler's "mov ax,[bp+0Eh] / mov [bp-1Eh],ax" (656D0h), the number its
;   switch looks up: Cat's Grace and Friends go to Strength's case (23), as in Shattered Lands.
; - NS_EFFECT (site 145): Strength's case's choice of effect (6623Bh to 6624Eh: Adrenalin Control's 2, else
;   Strength's 98) with Cat's Grace's (NS_GRACE_EFFECT, DEX) and Friends' (NS_FRIENDS_EFFECT, CHA), the
;   sequel's empty effect records 113 and 116 (the Loader's "ns_effects" names them). Friends rolls 2d4:
;   its dice pushed under the INT's frame, on past the game's "push dword 60001h" (66254h); the others on
;   to it (6624Eh: STRENGTH_DICE's, Cat's Grace's die by class with the spells as the manual has them).
; - NS_ABILITY (site 146): the abilities routine's effect switch, "mov [bp-0Ch],ax / mov cx,9" (85351h; AX
;   the effect, ES:BX its active record): Cat's Grace's adds its amount (+9) to DEX ([BP-346h]), 3 to 24
;   as Strength's to STR; Friends' to CHA ([BP-33Eh]), at most 25 (NS_FRIENDS_MOST); out at 8543Bh. The
;   game's "[BP-9] 0: no wizard's or priest's spell's effect" kept for them.
; - NS_CLAW (site 147): a natural attack's dice (86A45h, "or dx,dx / jnz 86A90h"; SI the thing, DX the
;   attack, far [BP+0Eh] the count, [BP+12h] the sides, [BP+16h] the bonus): with Erdlu Claw's effect
;   (NS_CLAW_EFFECT) the first attack 1d6+1 where that is better (SL's NS_CLAW).
; Erdlu Claw's +1 to hit unarmed and Fogbolt's -3 and +2 are NS_SWING's (from STINK_SWING), Reflected
; Image's 50 IMAGE_CHANCE's, Spook's save NS_SPOOK_SAVE's (from PROT_SAVE).
NS_GRACE_EFFECT   equ 113
NS_CLAW_EFFECT    equ 114
NS_FOG_EFFECT     equ 115
NS_FRIENDS_EFFECT equ 116
NS_GRACE      equ 0
NS_REFLECT    equ NS_FIRST + 3
NS_SPOOK      equ NS_FIRST + 4
NS_FRIENDS    equ 5
NS_FRIENDS_MOST equ 25
NS_EFFECT_ON  equ 0x6624E - 0x6623E ; (on to the dice's push, less the INT's way back)
NS_EFFECT_ROLL equ 0x66254 - 0x6623E ; (past it: Friends' own dice)
NS_ABILITY_OUT equ 0x8543B - 0x85354
NS_CLAW_PAST  equ 0x86A90 - 0x86A48
NS_SPOOK_MOST equ 6
NS_PRESERVER  equ 11                ; (the sheet's classes that cast wizard spells: the preserver, ...
NS_WIZARD     equ 18                ;   ... and the sequel's wizard)
ns_casts      dw 0                  ; (counts for a look in play: cases made Strength's, ...
ns_abilities  dw 0                  ;   ... abilities raised, ...
ns_claws      dw 0                  ;   ... claws' dice made 1d6+1, ...
ns_swings     dw 0                  ;   ... swings changed, ...
ns_spooks     dw 0                  ;   ... Spook's saves made worse, ...
ns_reflects   dw 0                  ;   ... and Reflected Image's 50s)
ns_cast:
        mov ax, [bp + 0x0E]
        push bx
        call ns_new
        jnc .set
        cmp bx, NS_GRACE
        je .str
        cmp bx, NS_FRIENDS
        jne .set
.str:   mov ax, STRENGTH_SPELL
        inc word [cs:ns_casts]
.set:   pop bx
        mov [bp - 0x1E], ax
        iret
ns_effect:
        push ax
        push bx
        mov word [bp - 0x12], 0x62
        mov ax, [bp + 0x0E]
        cmp ax, 0xF5
        jne .new
        mov word [bp - 0x12], 2
        jmp .on
.new:   call ns_new
        jnc .on
        cmp bx, NS_GRACE
        jne .friends
        mov word [bp - 0x12], NS_GRACE_EFFECT
        jmp .on
.friends:
        cmp bx, NS_FRIENDS
        jne .on
        mov word [bp - 0x12], NS_FRIENDS_EFFECT
        pop bx
        pop ax
        sub sp, 4                       ; (room for the dice, under the INT's frame)
        push bp
        mov bp, sp
        push ax
        mov ax, [bp + 6]
        add ax, NS_EFFECT_ROLL
        mov [bp + 2], ax
        mov ax, [bp + 8]
        mov [bp + 4], ax
        mov ax, [bp + 10]
        mov [bp + 6], ax
        mov word [bp + 8], 2            ; (2d4: the count, then the sides)
        mov word [bp + 10], 4
        pop ax
        pop bp
        iret
.on:    pop bx
        pop ax
        push bp
        mov bp, sp
        add word [bp + 2], NS_EFFECT_ON
        pop bp
        iret
ns_ability:
        mov [bp - 0x0C], ax
        mov cx, 9
        cmp ax, NS_GRACE_EFFECT
        je .new
        cmp ax, NS_FRIENDS_EFFECT
        je .new
        iret
.new:   test byte [cs:rules], RULE_NEW_SPELLS
        jz .game
        push ax
        cmp byte [bp - 9], 0
        je .out                         ; (as the game's for a wizard's spell)
        movsx ax, byte [es:bx + 0x256]
        cmp word [bp - 0x0C], NS_GRACE_EFFECT
        jne .cha
        add ax, [bp - 0x346]
        cmp ax, 24
        jle .low
        mov ax, 24
.low:   cmp ax, 3
        jge .dex
        mov ax, 3
.dex:   mov [bp - 0x346], ax
        jmp .done
.cha:   add ax, [bp - 0x33E]
        cmp ax, NS_FRIENDS_MOST
        jle .put
        mov ax, NS_FRIENDS_MOST
.put:   mov [bp - 0x33E], ax
.done:  inc word [cs:ns_abilities]
.out:   pop ax
        push bp
        mov bp, sp
        add word [bp + 2], NS_ABILITY_OUT
        pop bp
.game:  iret
ns_claw:
        pushad
        push es
        mov di, sp
        or dx, dx
        jnz .on
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .on
        mov ax, si
        mov cl, NS_CLAW_EFFECT
        call has_effect
        jne .on
        les bx, [bp + 0x0E]             ; (its average, twice over: dice x (sides + 1) + 2 x bonus)
        mov ax, [es:bx]
        les bx, [bp + 0x12]
        mov cx, [es:bx]
        inc cx
        imul ax, cx
        les bx, [bp + 0x16]
        add ax, [es:bx]
        add ax, [es:bx]
        cmp ax, 9                       ; (1d6+1's: 4.5)
        jge .on
        mov word [es:bx], 1
        les bx, [bp + 0x0E]
        mov word [es:bx], 1
        les bx, [bp + 0x12]
        mov word [es:bx], 6
        inc word [cs:ns_claws]
.on:    cmp word [ss:di + 22], 0        ; (the game's DX: "jnz 86A90h")
        je .out
        add word [ss:di + 34], NS_CLAW_PAST
.out:   pop es
        popad
        iret
; NS_SWING (from STINK_SWING, each call's first swing: [BP+18h] the attacker, [TARGET] the target, [BP+0Ah]
; the THAC0, [BP+12h] the item): Fogbolt's 3 worse for a fogged attacker and 2 better against a fogged
; target; Erdlu Claw's 1 better for an unarmed attack (no item) of the first set (the set-up's natural
; attacks' set, [BP-20h], 0: a thri-kreen's claws, not its bite, as SL's). All kept.
NS_NATURAL_SET equ -0x20
ns_swing:
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .ret
        push ax
        mov ax, [bp - 0x16]
        cmp ax, [bp - 0x0C]
        jne .out                        ; (once a call: [BP+0Ah] holds for its swings)
        push cx
        mov ax, [bp + 0x18]
        mov cl, NS_FOG_EFFECT
        call has_effect
        jne .target
        add word [bp + 0x0A], 3
        inc word [cs:ns_swings]
.target:
        mov ax, [TARGET]
        call has_effect
        jne .claw
        sub word [bp + 0x0A], 2
        inc word [cs:ns_swings]
.claw:  cmp word [bp + 0x12], NO_ITEM
        jb .done
        mov ax, [bp]                    ; (the set-up's frame: the caller's BP ...
        xchg ax, bx
        cmp byte [ss:bx + NS_NATURAL_SET], 0
        xchg ax, bx                     ;  ... its set of natural attacks)
        jne .done                       ; (the first set's alone, as SL's: not a thri-kreen's bite)
        mov ax, [bp + 0x18]
        mov cl, NS_CLAW_EFFECT
        call has_effect
        jne .done
        dec word [bp + 0x0A]
        inc word [cs:ns_swings]
.done:  pop cx
.out:   pop ax
.ret:   ret
; NS_IMAGE_CHANCE: DX Mirror Images' chance for thing AX: IMAGE_CHANCE, or NS_REFLECT_CHANCE when its
; effect is Reflected Image's (the effect's spell, +4). DS the game's; others kept.
NS_REFLECT_CHANCE equ 50
ns_image_chance:
        mov dx, IMAGE_CHANCE
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .ret
        push bx
        push cx
        push es
        mov cx, ds
        sub cx, EFFECTS_GAP
        mov es, cx
        mov cx, [EFFECTS_COUNT]
        mov bx, EFFECTS_BASE
        cmp cx, 400
        ja .out
.each:  jcxz .out
        cmp [es:bx], ax
        jne .on
        cmp byte [es:bx + 6], MIRROR_EFFECT
        jne .on
        cmp word [es:bx + 4], NS_REFLECT
        jne .out
        mov dx, NS_REFLECT_CHANCE
        inc word [cs:ns_reflects]
        jmp .out
.on:    add bx, 10
        dec cx
        jmp .each
.out:   pop es
        pop cx
        pop bx
.ret:   ret
; NS_SPOOK_SAVE (from PROT_SAVE: [BP+8] the caster, [BP+14h] the spell, DI the modifiers): against Spook
; 1 worse for each 2 levels of the caster's preserver or wizard class, or a Shinobi's casting level (SH_CAST:
; kits.spook_penalty), the more, at most NS_SPOOK_MOST. All kept.
ns_spook_save:
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .ret
        cmp word [bp + 0x14], NS_SPOOK
        jne .ret
        pusha
        push es
        mov ax, [bp + 8]
        call fighter_creature
        jc .out
        call kit_sheet
        xor dx, dx                      ; (DL the best level)
        xor si, si
.each:  mov al, [es:bx + si + SHEET_CLASSES]
        cmp al, NS_PRESERVER
        je .class
        cmp al, NS_WIZARD
        jne .next
.class: mov al, [es:bx + si + SHEET_LEVELS]
        cmp al, dl
        jbe .next
        mov dl, al
.next:  inc si
        cmp si, 3
        jb .each
        call sh_sheet_is                ; (a Shinobi's casting level, where more: THE SHINOBI'S SPELLS)
        jne .half
        movzx ax, al
        call sh_cast
        cmp al, dl
        jbe .half
        mov dl, al
.half:  shr dx, 1
        cmp dx, NS_SPOOK_MOST
        jbe .take
        mov dx, NS_SPOOK_MOST
.take:  or dx, dx
        jz .out
        mov bx, sp
        sub [ss:bx + 2], dx             ; (the game's DI, under ES in PUSHA's)
        inc word [cs:ns_spooks]
.out:   pop es
        popa
.ret:   ret

; - NS_SCROLL (site 148): a wizard scroll's reading (99xxxh), "mov es,ax / mov bx,es:[0B44h]" (999FBh) where its
;   power ([BP-4], the spell) has been found a wizard spell's (NS_CMP at 999EEh): a new spell known by the
;   reader (USE_WHO's), on to YOU ALREADY KNOW THIS SPELL (99A86h); else its sheet bit set (NS_TEACH) and on
;   to the scroll used up and YOU LEARN THE SPELL (99A5Ch). (No INT roll for them: SCROLL_LEARN's is the
;   bitset's.) Else the two instructions. Not the "mov ax,370h" before them (999F8h): the overlay manager
;   fixes up its segment word as it loads the code, which made a site there another INT.
; - NS_LEARN (site 149): CHOOSE A SPELL's pick (9367Ch: the page's spell DI, [370h:7 + 2 DI], for member
;   [370h:0B44h]), "mov es,ax / or es:[bx+39Ch],dl" (936B4h) setting its known bit: a new spell's sheet bit
;   instead (PICK_LIST puts them on the page), else the two instructions.
NS_SCROLL_KNOWN  equ 0x99A86 - 0x999FE    ; (from the site's frame IP, 999FBh + 3)
NS_SCROLL_TAUGHT equ 0x99A5C - 0x999FE
NS_PAGE      equ 7                  ; (CHOOSE A SPELL's list: words at 370h:7)
NS_PAGE_MOST equ 20                 ; (its room: 370h:2Fh after it is the game's)
ns_taught    dw 0                   ; (counts, for a look in play: new spells taught, from a scroll ...
ns_scrolls_n dw 0                   ;   ... of them, and put on CHOOSE A SPELL's page)
ns_paged     dw 0
; NS_TEACH: party member SI knows new spell BX (0 to NS_COUNT - 1): its sheet's bit set (a KIT_OPEN kit byte
; made 0, no kit, first, as SL's NS_SHEET_LEARN). DS the game's; all registers kept.
ns_teach:
        pusha
        push es
        mov di, bx
        mov ax, si
        call kit_sheet
        movzx ax, byte [cs:di + ns_known_at]
        add bx, ax
        cmp byte [cs:di + ns_known_at], KIT_BYTE
        jne .set
        sub bx, KIT_BYTE
        call kit_open_at
        lea bx, [bx + KIT_BYTE]     ; (the flags kept)
        jne .set
        mov byte [es:bx], 0
.set:   mov al, [cs:di + ns_known_bit]
        or [es:bx], al
        inc word [cs:ns_taught]
        pop es
        popa
        ret
; NS_LEVEL_NEW: AX the new spells of level CL member SI knows (KNOWN set) or doesn't (clear), with the rule;
; 0 without it. DS the game's; others kept.
ns_level_new:
        push bx
        push dx
        xor ax, ax
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .out
        cmp si, 3
        ja .out
        xor bx, bx
.each:  cmp [cs:bx + ns_levels], cl
        jne .next
        call ns_knows
        setnz dl
        cmp dl, [cs:ns_want]
        jne .next
        inc ax
.next:  inc bx
        cmp bx, NS_COUNT
        jb .each
.out:   pop dx
        pop bx
        ret
ns_want db 0
ns_scroll:
        pushad
        push es
        mov di, sp
        mov ax, [bp - 4]
        call ns_new
        jnc .game
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov si, [es:USE_WHO_OFF]
        cmp si, 3
        ja .known
        call ns_knows
        jnz .known
        call sh_ns_scroll               ; (a Shinobi: AL 1 not its own, 2 learnt, 3 not: THE SHINOBI'S SPELLS)
        cmp al, 1
        je .known
        cmp al, 3
        je .used
        call ns_teach
        inc word [cs:ns_scrolls_n]
.used:  add word [ss:di + 34], NS_SCROLL_TAUGHT
        jmp .out
.known: add word [ss:di + 34], NS_SCROLL_KNOWN
        jmp .out
.game:  mov ax, [ss:di + 30]           ; (the game's AX, selector 370h: its ES ...
        mov [ss:di], ax
        mov es, ax
        mov ax, [es:USE_WHO_OFF]        ;  ... and BX the reader)
        mov [ss:di + 18], ax
.out:   pop es
        popad
        iret
ns_learn:
        push bx
        push ax
        mov ax, [es:si + NS_PAGE]       ; (the spell: ES 370h, SI the page's place x 2)
        call ns_new
        jnc .game
        push si
        mov si, [es:USE_WHO_OFF]
        call ns_teach
        pop si
        pop ax
        pop bx
        mov es, ax
        iret
.game:  pop ax
        pop bx
        mov es, ax
        or [es:bx + KNOWN_OFF], dl
        iret
; NS_PAGE_ADD (from PICK_LIST): the new spells of the page's level (PICK_SHOWN) member SI doesn't know put
; after the game's DI on CHOOSE A SPELL's page (NS_PAGE_MOST at most), DI their count more. DS the game's;
; others kept.
ns_page_add:
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .ret
        cmp si, 3
        ja .ret
        pusha
        push es
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov cl, [PICK_SHOWN]
        xor bx, bx
.each:  cmp [cs:bx + ns_levels], cl
        jne .next
        call ns_knows
        jnz .next
        cmp di, NS_PAGE_MOST
        jae .done
        push bx
        lea dx, [bx + NS_FIRST]
        mov bx, di
        shl bx, 1
        mov [es:bx + NS_PAGE], dx
        pop bx
        inc di
        inc word [cs:ns_paged]
.next:  inc bx
        cmp bx, NS_COUNT
        jb .each
.done:  mov bx, sp
        mov [ss:bx + 2], di             ; (the DI PUSHA saved: under ES)
        pop es
        popa
.ret:   ret

; ---- THE SHINOBI'S SPELLS (the sequel; sites 209-210, and EL_SPHERE's, RANGER_LEVEL's, PICK_ANY's,
; PICK_PAGE's, PICK_LIST's, PICK_TOP's, SCROLL_LEARN's, NS_SCROLL's and CR_PICKS' Shinobi parts): SL's
; SHINOBI_WIZARD, SHINOBI_LEVEL, LV_SHINOBI, PROBE_PICK_ANY, PROBE_PICK_LEVEL, PROBE_PICK_LIST and SHINOBI_READ
; in the sequel's spell numbers (RESOURCE.GFF's names; kits.rav_shinobi_spells). A Shinobi (the kits' rule
; on, its kit awake, its own class the thief's, no preserver or wizard class: SH_MEMBER) casts wizard spells
; with its thief class: the sequel asks 62B45h (spell, class) whether a class casts a spell, wizard spells
; classes 11 and 18 alone, so SH_YES answers yes for its thief class and a wizard spell (0-72h, and the new
; spells while their rule is on) after the three callers that know the member (EL_SPHERE's sites 90-92: the
; spells it knows on USE, the cast's level, the caster level; SHINOBI_MAGE has the slot routine's, site 190).
; Its caster level is its thief level less SH_FIRST - 1 (SH_CAST: 1st at 6th, 8th at 13th, SH_CAST_MOST at
; most), the USE screen's MAGE list and its spell levels with it (97E9Ch: half of it, rounded up), and its
; spells' duration and damage (RANGER_LEVEL); it learns one of its own (SH_SPELLS) at each thief level up
; from SH_FIRST, and at creation one for each thief level from SH_FIRST, on CHOOSE A SPELL with its own
; spells alone and the levels up to SH_PICK_LEVEL's; from a scroll only one of its own, after a d100 against
; its read languages (SH_READ_LANG) and then INT's chance (SH_ROLLS). Counted in the header (+2078 on).
SH_FIRST      equ 6                 ; (the thief level its spells start at: SL's SHINOBI_FIRST)
SH_FOURTH     equ 13                ; (the thief level its 4th-level spells come at: SHINOBI_FOURTH)
SH_CAST_MOST  equ 11                ; (its casting level at most: a Seeker's, kits.SEEKER_CAST_MOST)
SH_READ_SKILL equ 7                 ; (read languages: the thief tables' eighth skill)
LEARN_UNREAD  equ 3                 ; (a Shinobi: the scroll not read: SL's)
LEARN_NOT_ITS equ 4                 ; (a Shinobi: not one of its spells: SL's)
; its spells (kits.SHINOBI_SPELLS as the sequel numbers them: kits.rav_shinobi_spells): 1st level Gaze
; Reflection, Charm Person, Shield, Color Spray, Wall of Fog, Fogbolt, Reflected Image, Spook, Friends (the
; last four the new spells, with their rule); 2nd Invisibility, Mirror Image, Blur, Detect Invisible, Fog
; Cloud; 3rd Blink, Haste, Protection from Missiles, Hold Person; 4th Improved Invisibility, Solid Fog, Confusion
sh_spells dw 6, 2, 9, 4, 11, NS_FIRST + 2, NS_FIRST + 3, NS_FIRST + 4, NS_FIRST + 5
          dw 17, 19, 12, 13, 15,  25, 29, 35, 30,  44, 50, 40
SH_COUNT equ ($ - sh_spells) / 2
sh_levels db 1, 1, 1, 1, 1, 1, 1, 1, 1,  2, 2, 2, 2, 2,  3, 3, 3, 3,  4, 4, 4
; SH_CAST: AX the level a Shinobi of thief level AX casts at: less SH_FIRST - 1, no less than 0, no more than
; SH_CAST_MOST (kits.shinobi_cast). Others kept.
sh_cast:
        sub ax, SH_FIRST - 1
        jns .most
        xor ax, ax
.most:  cmp ax, SH_CAST_MOST
        jle .ret
        mov ax, SH_CAST_MOST
.ret:   ret
; SH_PICK_LEVEL: AL the highest spell level a Shinobi of thief level AL may learn: half its casting level,
; rounded up, 3rd at most before SH_FOURTH, 4th from it (kits.shinobi_pick_level). Others kept.
sh_pick_level:
        push cx
        mov cl, 3
        cmp al, SH_FOURTH
        jb .cast
        inc cl
.cast:  movzx ax, al
        call sh_cast
        inc ax
        shr ax, 1
        cmp al, cl
        jbe .out
        mov al, cl
.out:   pop cx
        ret
; SH_SHEET_IS: ZF set if sheet ES:BX is a Shinobi's (the kits' rule on, its kit awake: KIT_IS) whose kit's
; class is the thief's, AL then its thief level (KIT_LEVEL). Others kept.
sh_sheet_is:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .no
        push si
        call kit_is_b
        db KIT_SHINOBI
        jne .out
        mov si, [cs:kit_where]
        cmp byte [es:bx + si + SH_CLASSES], THIEF_CLASS
        jne .out
        call kit_level          ; (ZF still set)
.out:   pop si
        ret
.no:    push ax
        or al, 1                ; (ZF clear)
        pop ax
        ret
; SH_MEMBER: CF set if party member SI (0-3) is a Shinobi (SH_SHEET_IS) with no preserver or wizard class
; (one has a preserver's spells as a preserver), AL its thief level. DS the game's; others kept.
sh_member:
        cmp si, 3
        ja .no
        push ax
        push bx
        push es
        mov ax, si
        call kit_sheet
        call sh_sheet_is
        jne .not
        push ax
        mov al, PRESERVER_CLASS
        call sh_has_class
        je .pres
        mov al, WIZARD_NEW_CLASS
        call sh_has_class
.pres:  pop ax
        je .not
        mov [cs:sh_level_of], al
        pop es
        pop bx
        pop ax
        mov al, [cs:sh_level_of]
        stc
        ret
.not:   pop es
        pop bx
        pop ax
.no:    clc
        ret
sh_level_of db 0
; SH_HAS_CLASS: ZF set if sheet ES:BX has class AL at one of its three places. All registers kept.
sh_has_class:
        cmp [es:bx + SH_CLASSES], al
        je .ret
        cmp [es:bx + SH_CLASSES + 1], al
        je .ret
        cmp [es:bx + SH_CLASSES + 2], al
.ret:   ret
; SH_FIGHTER_IS: ZF set if combatant AX (the game's, as 62B45h's callers and the caster level routine have
; it: its creature at 388h:0C34h, as EL_SPHERE reads it) is a Shinobi (SH_SHEET_IS), AL its thief level. DS
; the game's; others kept.
sh_fighter_is:
        cmp ax, 400
        jae .no
        push bx
        push es
        imul bx, ax, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        mov ax, [es:bx + FIGHTERS_OFF + 1]
        call kit_sheet
        call sh_sheet_is
        pop es
        pop bx
        ret
.no:    or al, 1
        ret
; SH_OWN: CF set if spell AX is one of the Shinobi's (SH_SPELLS; a new one only while its rule is on and its
; record has room: NS_NEW), CL its level. Others kept.
sh_own:
        push bx
        push di
        xor di, di
.each:  cmp ax, [cs:sh_spells + di]
        je .found
        add di, 2
        cmp di, SH_COUNT * 2
        jb .each
.no:    pop di
        pop bx
        clc
        ret
.found: cmp ax, NS_FIRST
        jb .yes
        call ns_new             ; (BX its place: kept by the pops)
        jnc .no
.yes:   shr di, 1
        mov cl, [cs:sh_levels + di]
        pop di
        pop bx
        stc
        ret
; SH_KNOWS: ZF clear if party member SI knows spell AX: its known bit (KNOWN_BITS), or a new spell's sheet
; bit (NS_KNOWS). DS the game's; all registers kept.
sh_knows:
        push bx
        push es
        cmp ax, NS_FIRST
        jae .new
        call known_bits
        call bit_known
        jmp .out
.new:   mov bx, ax
        sub bx, NS_FIRST
        call ns_knows
.out:   pop es
        pop bx
        ret
; SH_TOP: AL the highest spell level, CL or lower, with one of the Shinobi's spells (SH_OWN) party member
; SI doesn't know (SH_KNOWS); 0 if none. Others kept.
sh_top:
        push bx
        push cx
        push dx
        mov dl, cl              ; (DL the most, AL the best found)
        xor al, al
        xor bx, bx
.each:  push ax
        mov ax, [cs:sh_spells + bx]
        call sh_own
        jnc .next_pop
        cmp cl, dl
        ja .next_pop
        call sh_knows
        jnz .next_pop
        pop ax
        cmp cl, al
        jbe .next
        mov al, cl
        jmp .next
.next_pop:
        pop ax
.next:  add bx, 2
        cmp bx, SH_COUNT * 2
        jb .each
        pop dx
        pop cx
        pop bx
        ret
; SH_KNOWN_COUNT: AX how many of the Shinobi's spells party member SI knows. Others kept.
sh_known_count:
        push bx
        push cx
        push dx
        xor dx, dx
        xor bx, bx
.each:  mov ax, [cs:sh_spells + bx]
        call sh_own
        jnc .next
        call sh_knows
        jz .next
        inc dx
.next:  add bx, 2
        cmp bx, SH_COUNT * 2
        jb .each
        mov ax, dx
        pop dx
        pop cx
        pop bx
        ret

; SH_YES: (from EL_SPHERE's entries, SH_SPHERE_DI and SH_SPHERE_BP: AX the member, the game's AX pushed under
; the way back, the INT's IP, CS and FLAGS over 62B45h's two words, the spell and the class) the game's no
; made yes for a Shinobi's thief class (SH_FIGHTER_IS) and a wizard spell (below PRIEST_FIRST, or a new one:
; NS_NEW), so that the USE screen lists the wizard spells it knows, they are cast with its thief class
; (RANGER_LEVEL), and its caster level counts it (SH_CAST_LEVEL). Counted (SH_MAGES). All registers kept.
sh_yes:
        push bp
        mov bp, sp              ; ([BP+4] the game's AX, +6 the INT's IP, CS, FLAGS, +0Ch the spell, +0Eh
        cmp byte [bp + 4], 0    ;   the class)
        jne .ret
        cmp word [bp + 0x0E], THIEF_CLASS
        jne .ret
        push ax
        push bx
        mov bx, ax
        mov ax, [bp + 0x0C]
        cmp ax, PRIEST_FIRST
        jb .wizard
        push bx
        call ns_new
        pop bx
        jnc .out
.wizard:
        mov ax, bx
        call sh_fighter_is
        jne .out
        mov byte [bp + 4], 1
        inc word [cs:sh_mages]
.out:   pop bx
        pop ax
.ret:   pop bp
        ret
; SH_SPHERE_DI, SH_SPHERE_BP (sites 90, 91 and 92, before EL_SPHERE's own entries): SH_YES for the member DI
; (62C00h's) or [BP+6] (628AFh's, 97DC5h's), then EL_SPHERE.
sh_sphere_di:
        push ax
        mov ax, di
        call sh_yes
        pop ax
        jmp el_sphere_di
sh_sphere_bp:
        push ax
        mov ax, [bp + 6]
        call sh_yes
        pop ax
        jmp el_sphere_bp

; SH_CAST_LEVEL (site 209, "shinobi_cast_level"): "add sp,4" (97DF1h; 3 bytes) after the caster level
; routine's (97DC5h, SL's 81B16h: [BP+6] the combatant, [BP+8] the spell; each class SI 0-19 that casts the
; spell asked its level, 98h:0C1h, the best kept in DI) call for a class's level: the call's two words
; taken off as the ADD did; for the thief class (17) of a Shinobi (SH_FIGHTER_IS: SH_YES let it in), AX its
; casting level (SH_CAST: the thief level less 5, at most SH_CAST_MOST), SL's SHINOBI_LEVEL. Counted
; (SH_LEVELS). The caster level is the USE screen's spell levels (97E9Ch, half of it rounded up) and Dispel
; Magic's weighing; RANGER_LEVEL has the same for the spell's duration and damage.
sh_cast_level:
        push bp
        mov bp, sp              ; ([BP+2] the INT's IP, CS, FLAGS; +8 the call's two words)
        push ax
        mov ax, [bp + 6]
        mov [bp + 0x0A], ax     ; (the INT's frame moved over the two words)
        mov ax, [bp + 4]
        mov [bp + 8], ax
        mov ax, [bp + 2]
        mov [bp + 6], ax
        mov ax, [bp]
        mov [bp + 4], ax
        pop ax
        add bp, 4
        mov sp, bp
        pop bp
        cmp si, THIEF_CLASS
        jne .ret
        push ax
        push bx
        mov bx, ax              ; (BX the level)
        mov ax, [bp + 6]        ; (BP the game's: its [BP+6] the combatant)
        call sh_fighter_is
        jne .out
        mov ax, bx
        call sh_cast
        mov bx, ax
        inc word [cs:sh_levels_n]
.out:   mov ax, bx
        pop bx
        add sp, 2               ; (the AX pushed: AX is the answer)
.ret:   iret
; SH_PLACE_LEVEL: (RANGER_LEVEL's) AX the level of the class at ES:BX (a sheet + the class's place, in the
; routine of a spell's level for its duration and damage, 628AFh) a Shinobi's casting level (SH_CAST) if
; that class is a Shinobi's thief class (SH_SHEET_IS; SH_YES let it cast), SL's SHINOBI_WIZARD. Counted
; (SH_LEVELS). DS the game's; others kept.
sh_place_level:
        cmp byte [es:bx + SH_CLASSES], THIEF_CLASS
        jne .ret
        push bx
        push cx
        push dx
        mov cx, ax
        mov ax, bx              ; (the sheet: BX less the place, (BX - the table's start) mod its size)
        sub ax, [SHEETS_PTR]
        xor dx, dx
        push cx
        mov cx, SHEET_SIZE
        div cx
        pop cx
        sub bx, dx
        call sh_sheet_is
        jne .keep
        cmp dx, [cs:kit_where]
        jne .keep               ; (not its kit's class)
        mov ax, cx
        call sh_cast
        mov cx, ax
        inc word [cs:sh_levels_n]
.keep:  mov ax, cx
        pop dx
        pop cx
        pop bx
.ret:   ret

; SH_LEVEL_UP (site 210, "shinobi_level_up"): "cmp word [bp+8],0Bh" (957ABh; 4 bytes: the site and a NOP)
; in the routine that raises a character a level in a class ([BP+8] the class, SI the member; then "jnz" past
; the preserver's spell pick, 688h:66h, CHOOSE A SPELL, when [BP-6] says the level is a new one), SL's
; LV_SHINOBI: the compare's flags, but ZF set for a Shinobi's thief class (SH_MEMBER) at thief level SH_FIRST
; or more, so that it learns one of its own (PICK_ANY's, PICK_PAGE's, PICK_LIST's and PICK_TOP's Shinobi
; parts). Counted (SH_UPS).
; SCHOLAR_LEVEL_UP (site 210's entry): a party member SI gone up a new level ([BP-6] not 0) as a preserver
; ([BP+8] 0Bh) with the Scholar kit awake picks one more spell, on the game's CHOOSE A SPELL (688h:66h, CR_ONE's
; way: the way back in a frame the overlay manager can fix up, as CR_PICKS'), before the game's own (SL's
; LV_SCHOLAR, kits: a Scholar learns one more spell at each preserver level). Counted (SCHOLAR_PICKS). Then
; SH_LEVEL_UP, as for anyone.
scholar_level_up:
        cmp word [ss:bp + 8], 0x0B
        jne sh_level_up
        cmp byte [ss:bp - 6], 0
        je sh_level_up
        cmp si, 4
        jae sh_level_up
        push bx
        push es
        push ax
        mov ax, si
        call kit_sheet_ax
        pop ax
        call kit_is_b
        db KIT_SCHOLAR
        pop es
        pop bx
        jne sh_level_up
        call kp_if_frame        ; (interrupts as the caller had them)
        pushad
        push es
        mov bx, sp              ; the interrupt frame at BX+34: IP, CS, flags
        push word [ss:bx + 36]
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        mov ax, ds
        add ax, CR_STUB
        mov [cs:cr_far + 2], ax
        mov word [cs:cr_far], CR_SPELL_ENTRY
        push si
        call far [cs:cr_far]
        add sp, 2
        inc word [cs:scholar_picks]
        pop bp
        pop ax                  ; the way back, as the overlay manager has left it
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
        pop es
        popad
        ; (on to SH_LEVEL_UP: the compare's flags, and the game's own pick)
sh_level_up:
        push bp
        mov bp, sp              ; ([BP+2] the INT's IP, CS, FLAGS; [BP] the game's BP)
        push ax
        push bx
        mov bx, [bp]
        cmp word [ss:bx + 8], THIEF_CLASS
        jne .game
        call sh_member
        jnc .game
        cmp al, SH_FIRST
        jb .game
        inc word [cs:sh_ups]
        cmp al, al              ; (ZF set: on to the pick)
        jmp .flags
.game:  cmp word [ss:bx + 8], 0x0B
.flags: pushf
        pop ax
        and ax, 0x08D5          ; (OF, SF, ZF, AF, PF, CF)
        and word [bp + 6], ~0x08D5
        or [bp + 6], ax
        pop bx
        pop ax
        pop bp
        iret

; SH_PICK_ANY: (PICK_ANY's: SI the member, AX its preserver level, [BP-2] the level the routine 93160h looks
; for spells to learn from, down) CF set for a Shinobi (SH_MEMBER) with no preserver level: AX and [BP-2] the
; highest spell level up to its own (SH_PICK_LEVEL) with one of its spells it doesn't know (SH_TOP), 0 (the
; window not opened) if none (SL's PROBE_PICK_ANY). Counted (SH_ASKS). Else CF clear, all kept.
sh_pick_any:
        or ax, ax
        jg .no
        push cx
        call sh_member
        jnc .not
        call sh_pick_level
        mov cl, al
        call sh_top
        movzx ax, al
        mov [bp - 2], ax
        inc word [cs:sh_asks]
        pop cx
        stc
        ret
.not:   pop cx
.no:    clc
        ret
; SH_READER: CF set if the reader (USE_WHO's: CHOOSE A SPELL's, a scroll's) is a Shinobi (SH_MEMBER), SI it
; and AL its thief level. DS the game's; others kept.
sh_reader:
        push es
        mov si, ds
        add si, USE_WHO_SEG
        mov es, si
        mov si, [es:USE_WHO_OFF]
        pop es
        jmp sh_member
; SH_PICK_PAGE: (PICK_PAGE's: AL the page CHOOSE A SPELL opens on) CF set for a Shinobi reader (SH_READER):
; AL the highest level up to its own (SH_PICK_LEVEL) with one of its spells it doesn't know (SH_TOP), its own
; if none; else CF clear, AL kept. Others kept.
sh_pick_page:
        push cx
        push si
        push ax
        call sh_reader
        jnc .no
        call sh_pick_level
        mov cl, al
        call sh_top
        or al, al
        jnz .page
        mov al, cl
.page:  pop cx                  ; (the game's AX: AH kept)
        mov ah, ch
        pop si
        pop cx
        stc
        ret
.no:    pop ax
        pop si
        pop cx
        clc
        ret
; SH_PAGE_CUT: (PICK_LIST's: ES 370h's segment, its words at NS_PAGE the page's DI spells, SI the reader)
; CF set for a Shinobi (SH_MEMBER): the page its own spells alone (SH_OWN), DI their count (SL's
; PROBE_PICK_LIST). Counted (SH_PAGED). Else CF clear. Others kept.
sh_page_cut:
        push ax
        call sh_member
        pop ax
        jnc .ret
        push ax
        push bx
        push cx
        push dx
        xor bx, bx              ; (BX the page's place read, DX the kept)
        xor dx, dx
.each:  cmp bx, di
        jae .done
        push bx
        shl bx, 1
        mov ax, [es:bx + NS_PAGE]
        pop bx
        call sh_own
        jnc .next
        push bx
        mov bx, dx
        shl bx, 1
        mov [es:bx + NS_PAGE], ax
        pop bx
        inc dx
.next:  inc bx
        jmp .each
.done:  mov di, dx
        inc word [cs:sh_paged]
        pop dx
        pop cx
        pop bx
        pop ax
        stc
.ret:   ret
; SH_PAGE_TOP: (PICK_TOP's: CX the highest page CHOOSE A SPELL's level button goes to) CX no more than a
; Shinobi reader's own (SH_READER, SH_PICK_LEVEL), SL's PROBE_PICK_LEVEL. Others kept.
sh_page_top:
        push ax
        push si
        call sh_reader
        jnc .out
        call sh_pick_level
        movzx ax, al
        cmp cx, ax
        jle .out
        mov cx, ax
.out:   pop si
        pop ax
        ret

; SH_FIRST_SPELLS: (CR_PICKS': SI the new member, the game having given it no spells) a new Shinobi
; (SH_MEMBER) of thief level SH_FIRST or more picks one of its own on CHOOSE A SPELL (CR_ONE's way, the level
; up's 688h:66h: PICK_ANY's Shinobi part) for each thief level from SH_FIRST, as its level ups would have
; given them; on EXIT the rest are its first ones not known, in SH_SPELLS' order, up to its level's
; (SH_FILL). Counted (SH_ASKS, by the windows). Registers changed.
sh_first_spells:
        cmp word [CR_EDITING], -1
        jne .ret
        call sh_member
        jnc .ret
        sub al, SH_FIRST - 1
        jbe .ret
        movzx cx, al            ; (CX the picks due)
.one:   push cx
        call sh_known_count
        push ax
        mov ax, ds
        add ax, CR_STUB
        mov [cs:cr_far + 2], ax
        mov word [cs:cr_far], CR_SPELL_ENTRY
        push si
        call far [cs:cr_far]
        add sp, 2
        inc word [cs:cr_windows]
        call sh_known_count
        pop cx
        cmp ax, cx
        pop cx
        je .fill                ; (EXIT: none learnt)
        loop .one
.ret:   ret
.fill:  jmp sh_fill
; SH_FILL: CX more of the Shinobi's spells party member SI (SH_MEMBER, AL its thief level) doesn't know given
; it (their known bits; a new one's sheet bit: NS_TEACH), the first in SH_SPELLS' order whose level is up to
; its own (SH_PICK_LEVEL). Registers changed.
sh_fill:
        call sh_member
        jnc .ret
        call sh_pick_level
        mov dl, al              ; (DL the most)
        xor di, di
.each:  jcxz .ret
        cmp di, SH_COUNT * 2
        jae .ret
        mov ax, [cs:sh_spells + di]
        add di, 2
        push cx
        call sh_own
        mov dh, cl
        pop cx
        jnc .each
        cmp dh, dl
        ja .each
        call sh_knows
        jnz .each
        cmp ax, NS_FIRST
        jae .new
        push es
        push bx
        call known_bits
        call bit_set
        pop bx
        pop es
        jmp .given
.new:   push bx
        mov bx, ax
        sub bx, NS_FIRST
        call ns_teach
        pop bx
.given: inc word [cs:sh_filled]
        dec cx
        jmp .each
.ret:   ret

; SH_READ_LANG: AL party member SI's chance to read languages (a Shinobi's: SH_MEMBER, AL its thief level), as
; the thief tables have it for the inventory's skills (C_THIEF, SH_READ_SKILL): with Thieves as in AD&D
; (RULE_THIEF_TABLE) AD&D's average for the level (THIEF_ADND) + the race's, no more than THIEF_MOST; else
; the table's base + 4 a level + the race's; 0 to 100. DS the game's; others kept.
sh_read_lang:
        push bx
        push cx
        push si
        push es
        push gs
        movzx cx, al            ; (CX the thief level)
        mov ax, si
        call kit_sheet
        movzx si, byte [es:bx + SHEET_RACE]
        shl si, 3
        mov ax, ds
        add ax, THIEF_TABLE
        mov gs, ax
        movsx bx, byte [gs:si + THIEF_RACE + SH_READ_SKILL]   ; (BX the race's)
        test word [cs:rules], RULE_THIEF_TABLE
        jz .game
        push bx
        mov bx, SH_READ_SKILL
        mov si, cx
        call thief_adnd
        pop bx
        add ax, bx
        cmp ax, THIEF_MOST
        jle .clip
        mov ax, THIEF_MOST
        jmp .clip
.game:  movsx ax, byte [gs:SH_READ_SKILL]
        shl cx, 2
        add ax, cx
        add ax, bx
.clip:  cmp ax, 0
        jge .high
        xor ax, ax
.high:  cmp ax, 100
        jle .out
        mov ax, 100
.out:   pop gs
        pop es
        pop si
        pop cx
        pop bx
        ret
; SH_ROLLS: party member SI, a Shinobi (SH_MEMBER: AL its thief level), tries to learn its spell DX from a
; scroll (SL's SHINOBI_READ): a d100 against its read languages (SH_READ_LANG; LEARN_READ, LEARN_READ_CHANCE):
; above it LEARN_UNREAD (the scroll used up, nothing learnt); read, with RULE_HI_INT a d100 against INT's
; chance (INT_CHANCE; no most a level: its spells are few): above it LEARN_FAILED; else LEARN_LEARNT. The try
; told to the Loader (LEARN_SEQ...). CF set if learnt. DS the game's; others kept.
sh_rolls:
        push ax
        push bx
        push es
        mov [cs:learn_spell], dl
        mov [cs:learn_spell_hi], dh
        mov bx, si
        mov [cs:learn_who], bl
        mov byte [cs:learn_roll], 0
        mov byte [cs:learn_chance], 0
        call sh_read_lang
        mov [cs:learn_read_chance], al
        push ax
        mov ax, 100
        call game_die
        mov [cs:learn_read], al
        pop bx
        cmp al, bl
        jbe .read
        mov byte [cs:learn_result], LEARN_UNREAD
        mov byte [cs:learn_msg], LEARN_UNREAD
        jmp .no
.read:  imul bx, si, CREATURE_SIZE
        les ax, [CREATURES_PTR]
        add bx, ax
        mov al, [es:bx + CREATURE_INT]
        mov [cs:learn_int], al
        mov byte [cs:learn_result], LEARN_LEARNT
        test word [cs:rules_hi], RULE_HI_INT
        jz .yes
        movzx bx, al
        sub bx, INT_FIRST
        jge .row
        xor bx, bx
.row:   cmp bx, INT_ROWS - 1
        jbe .chance
        mov bx, INT_ROWS - 1
.chance:
        mov al, [cs:int_chance + bx]
        mov [cs:learn_chance], al
        mov ax, 100
        call game_die
        mov [cs:learn_roll], al
        cmp al, [cs:learn_chance]
        jbe .yes
        mov byte [cs:learn_result], LEARN_FAILED
        mov byte [cs:learn_msg], LEARN_FAILED
.no:    inc word [cs:learn_seq]
        inc word [cs:sh_scrolls]
        pop es
        pop bx
        pop ax
        clc
        ret
.yes:   inc word [cs:learn_seq]
        inc word [cs:sh_scrolls]
        pop es
        pop bx
        pop ax
        stc
        ret
; SH_NOT_ITS: the try at scroll spell DX by party member SI, a Shinobi, refused: not one of its spells
; (LEARN_NOT_ITS: the scroll kept, LEARN_REFUSED's text), told to the Loader. Others kept.
sh_not_its:
        push ax
        mov ax, si
        mov [cs:learn_who], al
        mov [cs:learn_spell], dl
        mov [cs:learn_spell_hi], dh
        mov byte [cs:learn_roll], 0
        mov byte [cs:learn_chance], 0
        mov byte [cs:learn_read], 0
        mov byte [cs:learn_read_chance], 0
        mov byte [cs:learn_result], LEARN_NOT_ITS
        mov byte [cs:learn_msg], LEARN_NOT_ITS
        inc word [cs:learn_seq]
        inc word [cs:sh_scrolls]
        pop ax
        ret
; SH_SCROLL: (SCROLL_LEARN's: the game's ES:BX the reader's byte of the known bits, [BP-4] the spell, a wizard
; spell it doesn't know) CF set for a Shinobi reader (SH_READER): AX 1 (the game's "known" path, the scroll
; kept, LEARN_REFUSED's text) for a spell not its own (SH_NOT_ITS); else its rolls (SH_ROLLS), AX 0 (the game
; teaches it and uses the scroll up; LEARN_SAID takes it back after LEARN_UNREAD or LEARN_FAILED). Else CF
; clear. Others kept.
sh_scroll:
        push cx
        push si
        push dx
        push ax
        call sh_reader
        jnc .no
        mov dx, [bp - 4]
        push ax
        push cx
        mov ax, dx
        call sh_own
        pop cx
        pop ax
        jc .its
        call sh_not_its
        pop ax
        mov ax, 1
        jmp .yes
.its:   mov [cs:learn_es], es
        push ax
        lea ax, [bx + KNOWN_OFF]
        mov [cs:learn_bx], ax
        mov cl, dl
        and cl, 7
        mov al, 1
        shl al, cl
        mov [cs:learn_mask], al
        pop ax
        call sh_rolls
        pop ax
        xor ax, ax
.yes:   pop dx
        pop si
        pop cx
        stc
        ret
.no:    pop ax
        pop dx
        pop si
        pop cx
        clc
        ret
; SH_NS_SCROLL: (NS_SCROLL's: SI the reader, AX a new spell it doesn't know, BX its place) AL 0 if the
; reader isn't a Shinobi (SH_MEMBER: the game's way, NS_SCROLL's); for one, AL 1 for a spell not its own
; (SH_NOT_ITS: the scroll kept), else its rolls (SH_ROLLS): AL 2 learnt, 3 not (the scroll used up, nothing
; taken back: LEARN_MASK 0). Others kept.
sh_ns_scroll:
        push dx
        push cx
        mov dx, ax
        push ax
        call sh_member
        jnc .none
        push ax
        mov ax, dx
        call sh_own
        pop ax
        jc .its
        call sh_not_its
        pop ax
        mov al, 1
        jmp .out
.its:   mov [cs:learn_es], ds
        mov word [cs:learn_bx], 0
        mov byte [cs:learn_mask], 0     ; (no bit to take back: LEARN_SAID's AND keeps it)
        call sh_rolls
        pop ax
        mov al, 2
        jc .out
        inc al
        jmp .out
.none:  pop ax
        mov al, 0
.out:   pop cx
        pop dx
        ret
sh_filled  dw 0                     ; (spells given at creation's EXIT: SH_FILL, counted for a look in play)
sh_ups     dw 0                     ; (level ups let on to the pick: SH_LEVEL_UP, the same)

; STINK_ROUND (site 0, "stinking_cloud_round"): in the routine of a spell's time from its record
; (80171h, SL's 76CB3h), "les bx,[bp-4]" (80249h) before the rounds are multiplied by the unit, EAX the
; rounds: Stinking Cloud's (22; its record's dice made 1d4) a round more, AD&D's 1d4+1. [BP+6] the spell.
STINKING_CLOUD equ 22
stink_round:
        les bx, [bp - 4]
        cmp word [bp + 6], STINKING_CLOUD
        jne .r
        inc eax
        inc word [cs:manual_count]
.r:     iret
; HD_SAVE (site 1, "classless_save_level"): the save modifiers' "mov [bp-6],ax" (83656h), AX the target's
; level (98h:154h), 0 for a creature with no class (the sheet's +1Bh..+1Dh all 0): its hit dice then
; (the first level byte, +1Eh; the sheet [BP-0Eh], far). Read after by Dismissal, Cloudkill, Scare,
; Color Spray.
hd_save:
        or ax, ax
        jnz .set
        push es
        push bx
        les bx, [bp - 0x0E]
        cmp byte [es:bx + 0x1B], 0
        jne .keep
        cmp word [es:bx + 0x1C], 0
        jne .keep
        mov al, [es:bx + 0x1E]
        cbw
        inc word [cs:manual_count]
.keep:  pop bx
        pop es
.set:   mov [bp - 6], ax
        iret
; CHAOS_SAVE (site 2, "chaos_int"): Chaos's "sub di,100" (83E83h) for a creature with no warrior
; levels: none for INT 21 or more or 4 or less, as the manual has it (the creature [BP-0Ah], far; INT +1Ch).
chaos_save:
        push es
        push bx
        push ax
        les bx, [bp - 0x0A]
        mov al, [es:bx + 0x1C]
        cmp al, 21
        jge .save
        cmp al, 4
        jle .save
        sub di, 100
        jmp .out
.save:  inc word [cs:manual_count]
.out:   pop ax
        pop bx
        pop es
        iret
; SPRAY_SAVE (site 3, "color_spray_level"): Dismissal's "cmp word [bp+14h],3Ch / jnz" (83E86h; 6 bytes):
; Color Spray (4) lets only creatures of more levels ([BP-6]) than its caster ([BP+16h]) save (-100).
; Then Dismissal's case (83E8Ch) or past it (83E98h).
COLOR_SPRAY equ 4
DISMISSAL   equ 0x3C
SPRAY_PAST  equ 0x83E98 - (0x83E86 + 3)
SPRAY_CASE  equ 0x83E8C - (0x83E86 + 3)
spray_save:
        push ax
        cmp word [bp + 0x14], COLOR_SPRAY
        jne .test
        mov al, [bp + 0x16]
        mov ah, 0
        cmp [bp - 6], ax
        jg .test
        sub di, 100
        inc word [cs:manual_count]
.test:  mov ax, SPRAY_CASE
        cmp word [bp + 0x14], DISMISSAL
        je .back
        mov ax, SPRAY_PAST
.back:  push bp
        mov bp, sp
        add [bp + 4], ax                    ; (the way back)
        pop bp
        pop ax
        iret
; CLOUD_SAVE (site 4, "cloudkill_save"): Cloudkill's "cmp word [bp+14h],39h / jnz / cmp word [bp-6],6 /
; jg / sub di,100" (83E98h; 15 bytes): AD&D's bands, no save under 4 levels (hit dice); from 4 the record's
; save (CLOUD_KILL: to 5, a failed one kills).
CLOUDKILL  equ 57
CLOUD_DIES equ 4
CLOUD_SAVES equ 5
cloud_save:
        cmp word [bp + 0x14], CLOUDKILL
        jne .out
        cmp word [bp - 6], CLOUD_DIES
        jge .out
        sub di, 100
.out:   iret
; CLOUD_KILL (site 5, "cloudkill_kills"): where a spell's damage on one creature (DI the combatant, SI the
; spell, [BP-6] the percent it takes, a dword) keeps the save's answer, "mov [bp-1],al" (651C5h; AL 0 not
; saved): a Cloudkill not saved against by a creature of CLOUD_SAVES levels or fewer (its highest, the
; first a classless one's hit dice) takes its damage a thousand times over, as SL's.
CLOUD_PERCENT equ 100000
cloud_kill:
        mov [bp - 1], al
        or al, al
        jnz .out
        cmp si, CLOUDKILL
        jne .out
        pusha
        push es
        cmp di, 400
        jae .done
        imul bx, di, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        cmp byte [es:bx + FIGHTERS_OFF], 2
        jne .done
        mov ax, [es:bx + FIGHTERS_OFF + 1]
        imul ax, ax, CREATURE_SIZE
        les bx, [CREATURES_PTR]
        add bx, ax
        mov ax, [es:bx + 4]
        imul ax, ax, SHEET_SIZE
        les bx, [SHEETS_PTR]
        add bx, ax
        mov al, [es:bx + 0x1E]
        cmp al, [es:bx + 0x1F]
        jae .a
        mov al, [es:bx + 0x1F]
.a:     cmp al, [es:bx + 0x20]
        jae .b
        mov al, [es:bx + 0x20]
.b:     cmp al, CLOUD_SAVES
        ja .done
        mov dword [bp - 6], CLOUD_PERCENT
        inc word [cs:manual_count]
.done:  pop es
        popa
.out:   iret
; FLAME_COUNT (site 6, "flame_arrow_count"): in a cast's tail (the routine at 7E32Ch, SL's 7511Bh: [BP+0Ah]
; the spell, [BP+0Ch] the cast's level), "mov dl,[es:bx]" (7E8E0h), the record's +0, bits 2-7 the times
; the spell is cast: Flaming Arrow's (28) one for every five levels, at least one (AD&D's bolts).
FLAME_ARROW equ 28
flame_count:
        mov dl, [es:bx]
        cmp word [bp + 0x0A], FLAME_ARROW
        jne .out
        push ax
        movzx ax, byte [bp + 0x0C]
        mov dl, 5
        div dl
        cmp al, 1
        adc al, 0                           ; (at least one)
        shl al, 2
        mov dl, al
        pop ax
        inc word [cs:manual_count]
.out:   iret
; BIO_LEAST (site 7, "biofeedback_least"): Bio-Feedback's (8) "sub si,2" in the damage adjustments
; (8348Bh; SI the damage): at least 1 left of a blow of 2 or less, as the manual (none stays none).
BIO_LESS equ 2
bio_least:
        cmp si, BIO_LESS + 1
        jl .least
        sub si, BIO_LESS
        iret
.least: cmp si, 1
        jl .out
        mov si, 1
        inc word [cs:manual_count]
.out:   iret
; CAST_START (site 8, "cast_level_kept"): the cast's tail (7E32Ch, every cast from the USE screen, a
; monster's, an item's or a scroll's: [BP+0Ah] the spell, [BP+0Ch] the cast's level) at its start, "mov
; di,[bp+0Ah]" (7E338h): the level kept (CAST_LEVEL) for ACID_ROUNDS, which puts Lower Resistance's into
; its effect's amount as the cast puts the effect on (SL's TH_LEVEL, CAST_SITE's).
cast_start:
        mov di, [bp + 0x0A]
        push ax
        mov al, [bp + 0x0C]
        mov [cs:cast_level], al
        pop ax
        mov word [cs:tu_more], 0        ; (a D*'s more: this cast's only, TU_SITE's)
        iret
cast_level db 0
; LOWRES_SITE (site 9, "lower_resistance_manual"): the magic resistance routine (84AB5h, SL's 7A4A8h:
; [BP+6] the combatant, SI the spell, [BP+0Ah] the cast's level, [BP-2] the resistance, [BP-0Bh] 20h
; the Low Resistance effect, 61, on), 84B2Eh-84B4Eh (33 bytes: the effect's halving, then Lower
; Resistance's own 30 + the level off): 30% + 1% a level of the caster off, AD&D's (the manual's), the
; effect's level its amount (+9, ACID_ROUNDS'), the cast's own the same, the two not added up; the
; game's next test makes it 0 at least.
LOWRES_EFFECT equ 61
LOWRES_SPELL  equ 64
LOWRES_BASE   equ 30
lowres_site:
        push ax
        push cx
        push dx
        xor dx, dx
        test byte [bp - 0x0B], 0x20
        jz .cast
        mov ax, [bp + 6]
        mov cl, LOWRES_EFFECT
        call effect_amount
        movzx dx, al
        add dx, LOWRES_BASE
.cast:  cmp si, LOWRES_SPELL
        jne .take
        movzx ax, byte [bp + 0x0A]
        add ax, LOWRES_BASE
        cmp ax, dx
        jbe .take
        mov dx, ax
.take:  or dx, dx
        jz .out
        sub [bp - 2], dx
        inc word [cs:manual_count]
.out:   pop dx
        pop cx
        pop ax
        iret
; STRENGTH_DICE (site 10, "strength_dice"): Strength's handler's dice, "push dword 60001h" (6624Eh, SL's
; 79483h; 6 bytes: 1d6; DI the target, [BP+0Eh] the spell; Adrenalin Control's, 245, the same code):
; Strength's (23) by the target's classes, AD&D's (warriors 1d8, priests, rogues and psionicists 1d6,
; wizards 1d4), a multiclass character's best; Adrenalin Control's, and a creature with no class's, 1d6.
; Cat's Grace (a new spell, NS_FIRST, with RULE_NEW_SPELLS) by class too, as Shattered Lands' (GRACE_SIDES).
; The dice pushed under the INT's frame (its IP, CS and flags moved down 4 bytes). The sequel's classes
; SL's 1-17, then 18 (a wizard's) and 19 (a priest's); the sheet's classes at +1Bh.
STRENGTH_SPELL equ 23
STR_SIDES:              ; classes 1-19: Strength's sides
        db 6, 6, 6, 6, 6, 6, 6, 6       ; (clerics, druids)
        db 8, 8, 4, 6, 8, 8, 8, 8       ; (fighter, gladiator, preserver, psionicist, rangers)
        db 6, 4, 6                      ; (thief; the sequel's 18, a wizard's, and 19, a priest's)
GRACE_SIDES:            ; classes 1-19: Cat's Grace's (SL's: rogues 1d8, priests 1d4, the rest 1d6)
        db 4, 4, 4, 4, 4, 4, 4, 4
        db 6, 6, 6, 6, 6, 6, 6, 6
        db 8, 6, 4
strength_dice:
        sub sp, 4                       ; (room for the dice)
        push bp
        mov bp, sp                      ; ([BP+2] the room, [BP+6] the INT's IP, CS and flags)
        pusha
        push es
        mov cx, 6
        mov si, [bp]                    ; (the game's BP)
        mov bp, STR_SIDES
        cmp word [ss:si + 0x0E], STRENGTH_SPELL
        je .class
        mov bp, GRACE_SIDES             ; (Cat's Grace, a new spell, by class too: NS_EFFECT)
        cmp word [ss:si + 0x0E], NS_FIRST
        jne .put
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .put
.class:
        cmp di, 400
        jae .put
        imul bx, di, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        cmp byte [es:bx + FIGHTERS_OFF], 2
        jne .put
        mov ax, [es:bx + FIGHTERS_OFF + 1]
        imul ax, ax, CREATURE_SIZE
        les bx, [CREATURES_PTR]
        add bx, ax
        mov ax, [es:bx + 4]
        imul ax, ax, SHEET_SIZE
        les bx, [SHEETS_PTR]
        add bx, ax
        xor dx, dx                      ; (DL the best sides)
        xor si, si
.each:  movzx di, byte [es:bx + si + 0x1B]
        dec di
        cmp di, 19 - 1
        ja .skip
        mov al, [cs:bp + di]
        cmp al, dl
        jbe .skip
        mov dl, al
.skip:  inc si
        cmp si, 3
        jb .each
        or dl, dl
        jz .put
        movzx cx, dl
        inc word [cs:manual_count]
.put:   mov bp, sp                      ; (BP back: PUSHA's and ES under it)
        add bp, 18
        mov ax, [bp + 6]
        mov [bp + 2], ax
        mov ax, [bp + 8]
        mov [bp + 4], ax
        mov ax, [bp + 10]
        mov [bp + 6], ax
        mov word [bp + 8], 1            ; (the count, then the sides)
        mov [bp + 10], cx
        pop es
        popa
        pop bp
        iret
; CELL_HEAL (site 11, "cell_adjustment_heal"): Cell Adjustment's (248) case in the handler for spells
; with rules of their own (DI the target, [BP+8] the user), "push 2 / jmp 65811h" (664C5h, SL's
; 795A2h; 5 bytes: 2 HP): 1d4 HP, AX for the game's "push ax / jmp 65811h" (66545h, Neutralize
; Poison's and the rest's: KIT_CURE's site, site 206) and the healing after it; its record's cure of disease
; is the game's own. With the kits a Lifebinder's a d4 more, a Healer's or Rescuer's 1 more (CELL_MORE, SL's
; CELL_SITE's). Recorded (MN_CELL: the target, the user, the healing, the kit's more in +6's high byte).
MN_CELL   equ 3
CELL_BACK equ 0x66545 - (0x664C5 + 3)
cell_heal:
        push bp
        mov bp, sp
        add word [bp + 2], CELL_BACK
        push bx
        push cx
        mov bx, [ss:bp]                 ; (the game's BP)
        mov ax, [ss:bx + 8]
        call cell_more                  ; (CX the kit's more)
        mov ax, 4
        call game_die
        add ax, cx
        pusha
        mov [cs:mn_frame], di
        mov bx, [ss:bp]
        mov bx, [ss:bx + 8]
        mov [cs:mn_frame + 2], bx
        mov [cs:mn_frame + 4], ax
        mov ch, cl                      ; (the low byte 0: no disease cured said here)
        xor cl, cl
        mov [cs:mn_frame + 6], cx
        mov ax, MN_CELL
        call mn_rec
        popa
        pop cx
        pop bx
        inc word [cs:manual_count]
        pop bp
        iret
; PSI_FEEBLE (site 12, "feeblemind_psionics"): the psionic power check (61D2Eh, SL's 5D59Dh: SI the
; user, DI the power), "or ax,ax / jnz 61D50h / mov al,0" (61D47h; 6 bytes) after the test that the user
; has the power: a feebleminded user (the sequel's effect 37) can use none, as the manual has it (0:
; the check fails, 61D4Dh). Recorded (MN_PSIONIC).
MN_PSIONIC     equ 6
FEEBLE_EFFECT  equ 37
PSI_ON  equ 0x61D50 - (0x61D47 + 3)
PSI_NO  equ 0x61D4D - (0x61D47 + 3)
psi_feeble:
        push bx
        push cx
        mov bx, PSI_NO
        or ax, ax
        jz .way
        mov ax, si
        mov cl, FEEBLE_EFFECT
        call has_effect
        mov bx, PSI_ON
        jnz .way
        mov [cs:mn_frame], si
        mov [cs:mn_frame + 2], di
        pusha
        mov ax, MN_PSIONIC
        call mn_rec
        popa
        inc word [cs:manual_count]
        mov bx, PSI_NO
        xor ax, ax
.way:   push bp
        mov bp, sp
        add [bp + 6], bx                ; (the INT's return address)
        pop bp
        pop cx
        pop bx
        iret
; RAINBOW_HURT (site 13, "rainbow_pattern_damage"): the start of the routine taking hit points off a
; combatant (5CBE4h, SL's 5859Ah: every blow's and spell's damage), "mov di,[bp+6] / mov dx,[bp+8]"
; (5CBECh; 6 bytes: the combatant, the damage): any damage to a combatant Paralyzed (the sequel's 69) by
; Rainbow Pattern (49: the entry's spell, not Hold Person's or another's) ends that hold, through
; 608h:48h (7FB63h: the combatant, the entry's handle, +7; as the game ends an effect, its abilities
; worked out again), in a frame the overlay manager can fix up (as ACID_ROUND's). Recorded
; (MN_RAINBOW). Then the moves made.
MN_RAINBOW     equ 4
RAINBOW_SPELL  equ 49
HELD_EFFECT    equ 69
END_STUB       equ 0x473B - 0x47E0  ; (608h's stub segment less DS's)
END_ENTRY      equ 0x48
rainbow_hurt:
        mov di, [bp + 6]
        mov dx, [bp + 8]
        sti
        pushad
        push es
        mov bx, sp                      ; (BX+34: the INT's way back, its IP then CS)
        or dx, dx
        jle .out
        mov ax, ds
        sub ax, EFFECTS_GAP
        mov es, ax
        mov si, EFFECTS_BASE
        mov cx, [EFFECTS_COUNT]
        cmp cx, 400
        ja .out
.each:  jcxz .out
        cmp [es:si], di
        jne .next
        cmp byte [es:si + 6], HELD_EFFECT
        jne .next
        cmp word [es:si + 4], RAINBOW_SPELL
        je .free
.next:  add si, 10
        loop .each
.out:   pop es
        popad
        iret
.free:  movzx ax, byte [es:si + 7]      ; (its handle)
        pusha
        mov [cs:mn_frame], di
        mov [cs:mn_frame + 2], dx
        mov word [cs:mn_frame + 4], 0
        mov word [cs:mn_frame + 6], 0
        mov ax, MN_RAINBOW
        call mn_rec
        popa
        inc word [cs:manual_count]
        push bx
        push word [ss:bx + 36]          ; (the way on, in a frame the overlay manager can fix up)
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        mov cx, ds
        add cx, END_STUB
        mov [cs:end_far + 2], cx
        mov word [cs:end_far], END_ENTRY
        push ax
        push di
        call far [cs:end_far]           ; (the combatant, the handle)
        add sp, 4
        pop bp
        pop ax                          ; (the way back, as the overlay manager has left it)
        pop cx
        pop bx
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], cx
        jmp .out
end_far dd 0
; HOLD_HD (site 14, "hold_undead_level"): near the end of the spells' immunity routine (8451Ah: DI the
; target combatant, SI the spell, [BP+14h] the cast's level; AX 1 immune, 0 not), where every spell
; not yet found immune passes, "mov ax,si / cmp ax,0FCh" (84A65h; 5 bytes): Hold Undead (31) leaves
; an undead of more levels (hit dice: the most of its sheet's +1Eh..+20h, CLOUD_KILL's) than the
; cast's immune (to 84A62h's "jmp 84562h"), as the manual (SL's hold_undead_level); else the move and
; the compare made, its flags returned. The game's own Hold Undead holds only the undead (seen
; 2026-11-21: a Draxan took nothing).
HOLD_UNDEAD    equ 31
HOLD_IMMUNE    equ (0x84A65 + 3) - 0x84A62
HOLD_FLAGS     equ 0x08D5           ; (OF, SF, ZF, AF, PF, CF)
hold_hd:
        push bp
        mov bp, sp                      ; ([BP+2] the INT's IP, [BP+6] its flags; [BP] the game's BP)
        cmp si, HOLD_UNDEAD
        jne .go
        pusha
        push es
        cmp di, 400
        jae .no
        imul bx, di, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        cmp byte [es:bx + FIGHTERS_OFF], 2
        jne .no
        mov ax, [es:bx + FIGHTERS_OFF + 1]
        imul ax, ax, CREATURE_SIZE
        les bx, [CREATURES_PTR]
        add bx, ax
        mov ax, [es:bx + 4]
        imul ax, ax, SHEET_SIZE
        les bx, [SHEETS_PTR]
        add bx, ax
        mov al, [es:bx + 0x1E]
        cmp al, [es:bx + 0x1F]
        jae .a
        mov al, [es:bx + 0x1F]
.a:     cmp al, [es:bx + 0x20]
        jae .b
        mov al, [es:bx + 0x20]
.b:     mov si, [bp]
        cmp al, [ss:si + 0x14]
        jbe .no
        inc word [cs:manual_count]
        sub word [bp + 2], HOLD_IMMUNE
        pop es
        popa
        pop bp
        iret
.no:    pop es
        popa
.go:    mov ax, si
        push ax
        cmp ax, 0xFC
        pushf
        pop ax
        and ax, HOLD_FLAGS
        and word [bp + 6], ~HOLD_FLAGS
        or [bp + 6], ax
        pop ax
        pop bp
        iret
; TU_SITE (site 15, "turn_undead_manual"): Turn Undead AD&D's way, SL's TURN_SITE (tu_site). The
; game's turning of one undead (97C50h, SL's 7ADB7h, called from the handler for spells with rules of
; their own, 66179h, Turn Undead's case 310: [BP+6] the target, [BP+8] the priest, [BP+0Ch] the priest
; level, [BP-4] the undead's sheet number, ES:BX its sheet) works out its number from "mov
; al,[es:bx+1Eh]" (97C9Ch; 4 bytes: the hit dice, SL's +24h), rolls a d20 at 97CE9h, destroys at 97CFCh
; (598:7Fh, 1000 damage) and calls 0C8h:6E1h on a failure (97D12h). The site never comes back to the
; byte after it: the way back set to one of those, or the routine's end (97D1Bh), before any far call:
; TU_CELL's cell from the hit dice and level; a number: a d20 (GAME_DIE), at or over it turned, under
; it the failure's way and the priest's bit (combatants 0-7) set in TU_FAILED (a byte a target, under
; TANGLE_MOST), a later try by the same priest refused with no roll (cleared at a fight's first round,
; ACID_ROUND, and by a turning out of a fight); T turned; turned: 3d4 rounds Afraid (the sequel's 35)
; through 608h:3Eh (7F9E6h, the add: target, priest, spell 310, 35, dword rounds x 60, 0) in a frame
; the overlay manager can fix up (RAINBOW_HURT's); D the destroy; D*: the destroy, and 2d4 more of
; that sheet this cast (TU_MORE, cleared by CAST_START) destroyed with no roll; "---" the end.
; Recorded as KIND_TURN (13, SL's): the d20 (0 none) and TU_FRAME (dicelog's _turn_manual).
KIND_TURN  equ 13
TU_BACK    equ 0x97C9C + 3              ; (the INT's way back: the site's byte's next)
TU_DESTROY equ 0x97CFC - TU_BACK
TU_FAIL    equ 0x97D12 - TU_BACK
TU_END     equ 0x97D1B - TU_BACK
TU_SPELL   equ 310
TU_AFRAID  equ 35
ADD_ENTRY  equ 0x3E                     ; (608h's: the effect adder, END_STUB's stub segment)
TU_T       equ 21                       ; (TU_CELL's: 1-20 the number, 0 none)
TU_D       equ 22
TU_DSTAR   equ 23
TU_NOT     equ 0                        ; (the outcomes, TU_OUTCOME: SL's)
TU_TURNED  equ 1
TU_DESTROYED equ 2
TU_DSTARRED equ 3
TU_MORE_ONE equ 4
TU_AGAIN   equ 5
TU_NONE    equ 6
TU_MOST    equ 512                      ; (the combatants TU_FAILED covers, TANGLE_MOST's)
tu_site:
        sti
        pushad
        push es
        movzx ax, byte [es:bx + 0x1E]
        mov [cs:tu_hd], ax
        mov si, [bp + 6]
        mov [cs:tu_target], si
        mov cx, [bp + 8]
        mov [cs:tu_caster], cx
        mov ax, si
        call tu_creature
        mov [cs:tu_target_c], ax
        mov ax, cx
        call tu_creature
        mov [cs:tu_caster_c], ax
        movzx ax, byte [bp + 0x0C]
        mov [cs:tu_level], ax
        xor ax, ax
        mov [cs:tu_d20], ax
        mov [cs:tu_rounds], ax
        mov [cs:tu_need], ax
        cmp byte [IN_COMBAT], 0
        jne .fight
        call tu_clear                   ; (out of a fight: a new one, nothing failed yet)
.fight: mov word [cs:tu_outcome], TU_MORE_ONE
        mov dx, TU_DESTROY
        cmp word [cs:tu_more], 0
        je .again
        mov ax, [bp - 4]
        cmp ax, [cs:tu_kind]
        jne .again
        dec word [cs:tu_more]
        jmp .done
.again: mov word [cs:tu_outcome], TU_AGAIN
        mov dx, TU_END
        call tu_bit
        jz .cell
        push fs
        call tail_fs
        test [fs:tu_failed + si], al
        pop fs
        jnz .done
.cell:  mov al, [cs:tu_hd]
        mov cl, [cs:tu_level]
        call tu_cell
        mov [cs:tu_need], ax
        mov word [cs:tu_outcome], TU_NONE
        test al, al
        jz .done
        mov word [cs:tu_outcome], TU_DESTROYED
        mov dx, TU_DESTROY
        cmp al, TU_D
        je .done
        ja .dstar
        cmp al, TU_T
        je .turned
        mov ax, 20
        call game_die
        mov [cs:tu_d20], ax
        cmp ax, [cs:tu_need]
        jge .turned
        mov word [cs:tu_outcome], TU_NOT
        mov dx, TU_FAIL
        call tu_bit
        jz .done
        push fs
        call tail_fs
        or [fs:tu_failed + si], al
        pop fs
        jmp .done
.dstar: mov word [cs:tu_outcome], TU_DSTARRED
        mov ax, [bp - 4]
        mov [cs:tu_kind], ax
        mov ax, 4
        call game_die
        mov [cs:tu_more], ax
        mov ax, 4
        call game_die
        add [cs:tu_more], ax
        mov dx, TU_DESTROY
        jmp .done
.turned:
        mov word [cs:tu_outcome], TU_TURNED
        mov cx, 3
.fear:  mov ax, 4
        call game_die
        add [cs:tu_rounds], ax
        loop .fear
        mov dx, TU_END
.done:  mov bx, sp
        add [ss:bx + 34], dx            ; (the way on, before any call)
        inc word [cs:manual_count]
        mov si, tu_frame
        mov cx, (tu_frame_end - tu_frame) / 2
        mov ax, [cs:tu_d20]
        mov word [cs:kind], KIND_TURN
        call rec_frame
        cmp word [cs:tu_outcome], TU_TURNED
        jne .out
        mov bx, sp
        push bx
        push word [ss:bx + 36]          ; (the way on, in a frame the overlay manager can fix up)
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        mov cx, ds
        add cx, END_STUB
        mov [cs:end_far + 2], cx
        mov word [cs:end_far], ADD_ENTRY
        push word 0
        push word 0
        imul ax, [cs:tu_rounds], ROUND_SECONDS
        push ax
        push word TU_AFRAID
        push word TU_SPELL
        push word [cs:tu_caster]
        push word [cs:tu_target]
        call far [cs:end_far]           ; (target, priest, spell, effect, time, 0)
        add sp, 14
        pop bp
        pop ax                          ; (the way back, as the overlay manager has left it)
        pop cx
        pop bx
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], cx
.out:   pop es
        popad
        iret

; TU_BIT: for TU_SITE, AL the priest's bit (TU_CASTER, 0-7) and SI the target (TU_TARGET) in
; TU_FAILED; ZF set when there is none (a combatant past them). CL changed.
tu_bit:
        mov si, [cs:tu_target]
        mov cx, [cs:tu_caster]
        xor al, al
        cmp si, TU_MOST
        jae .out
        cmp cx, 8
        jae .out
        mov al, 1
        shl al, cl
.out:   test al, al
        ret
tu_clear:                       ; (no failed turnings). All kept.
        push ax
        push cx
        push di
        push es
        mov ax, cs
        add ax, TAIL_PARAS
        mov es, ax                      ; (TU_FAILED: the tail's)
        mov di, tu_failed
        mov cx, TU_MOST
        xor al, al
        cld
        rep stosb
        pop es
        pop di
        pop cx
        pop ax
        ret
; TU_CELL: SL's (AX AD&D's turning table's cell, 0 "---", 1-20 the d20 needed, TU_T, TU_D, TU_DSTAR,
; for undead of AL hit dice and a priest of level CL; dicelog's turn_cell). BX changed.
        SHARED_tu_cell
; TU_CREATURE: AX the creature of combatant AX (FFFFh: none, not a creature). All else kept.
tu_creature:
        push bx
        push es
        cmp ax, TU_MOST
        jae .none
        imul bx, ax, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        cmp byte [es:bx + FIGHTERS_OFF], 2
        jne .none
        mov ax, [es:bx + FIGHTERS_OFF + 1]
        jmp .ret
.none:  mov ax, 0xFFFF
.ret:   pop es
        pop bx
        ret
tu_cells  db 20, 19, 16, 13, 10, 7, 4, TU_T, TU_T, TU_D, TU_D
tu_kind   dw 0                  ; (TU_MORE's kind: a sheet's number)
tu_d20    dw 0                  ; (the d20, 0 none: the entry's value)
tu_frame:                       ; KIND_TURN's frame, from +6 (SL's):
tu_caster dw 0                  ;   the priest
tu_target dw 0                  ;   +8 the undead
tu_need   dw 0                  ;   +0Ah the cell (TU_CELL's)
tu_level  dw 0                  ;   +0Ch the priest level
tu_hd     dw 0                  ;   +0Eh its hit dice
tu_outcome dw 0                 ;   +10h TU_NOT ... TU_NONE
tu_rounds dw 0                  ;   +12h turned: the rounds it flees
tu_more   dw 0                  ;   +14h D*: how many more of its kind this cast (counted down)
tu_caster_c dw 0                ;   +16h the priest's creature (FFFFh: not a creature)
tu_target_c dw 0                ;   +18h the undead's
tu_frame_end:
section tailz
tu_failed times TU_MOST db 0 ; (a byte a target: the priests, 0-7, who failed against it this fight)
section image
; TH_SITE (site 16, "spell_hit"): spells that roll to hit, SL's SPELL_HIT (th_hit). The sequel has no
; always-hit stub and no table of the missile spells (SL's 7A1A7h): its routine of what spell SI does
; to target DI (8451Ah, SL's 7A085h; [BP-4] 1 for the computer's look ahead, 5F2D2h's, not a cast)
; answers 0 (not immune) only through "xor ax,ax / pop di" (84AAFh; 3 bytes), and an answer of 1 makes
; the spell's damage and effect routine (651A0h) skip both, as SL's 7A0BEh. There the cast PROBE_CAST
; last saw (TH_CAST: armed, not a weapon's spell on a hit, not an Acid's burn) of this spell at this
; target rolls to hit once, as SL's: the missile spells (TH_MISSILES, the sequel's numbers: Acid
; Arrow 18, Pebble to Boulder 53, Magic Stone 121, Condense 169, Minute Meteors 33 with its own +2; the
; spines have no record in the sequel) as missiles (kind 2, DEX), the touch spells (TH_TOUCHES: Chill
; Touch 3, Shocking Grasp 10, Vampiric Touch 38, Cause Light Wounds 118, Cause Disease 149, Cause
; Serious 171, Poison 179, Cause Critical 195) at a creature of another side (+15h's low 3 bits, SL's
; +1Dh) as melee (kind 1, STR). The caster's THAC0 (its creature's +16h, SL's +1Fh; Acid Arrow's 21
; less the cast's level), less the game's to-hit adjustments (628h:66h, 85B??h in overlay 83400h:
; target, attacker, no weapon, kind; their STR or DEX part 98h:2C0h or 2D9h, for the log) and a
; monster's difficulty ([143Ah] - 1, SL's 11AEh), against the AC (4671h:7Ah, 5D520h: target, attacker,
; not from behind, the weapon attack's), a d20 (GAME_DIE): a 20 hits, a 1 misses. A miss answers 1,
; so the spell does nothing. The "pop di" done here (the word under the INT's frame, the frame moved
; up over it); the far calls in a frame the overlay manager can fix up (RAINBOW_HURT's), the way back
; never changed. Recorded (KIND_TOHIT, 12: the d20, TH_FRAME, SL's; dicelog's _spell_to_hit).
KIND_TOHIT    equ 12
TH_ACID       equ 18
TH_METEORS    equ 33
TH_DIFFICULTY equ 0x143A
TH_ADJ_STUB   equ 0x475A - 0x47E0       ; (628h's stub segment less DS's: 66h the to-hit adjustments)
TH_AC_STUB    equ 0x4671 - 0x47E0       ; (the attack overlay's stub: 7Ah the AC, 5D520h)
TH_ABIL_SEG   equ 0x17E5 - 0x47E0       ; (98h's segment, the root's: 2C0h STR's to-hit, 2D9h DEX's)
TH_SIDE       equ 0x15                  ; (the creature's side, low 3 bits; SL's +1Dh)
TH_THAC0      equ 0x16                  ; (the creature's THAC0; SL's +1Fh)
%macro th_far 2                         ; a far call to segment DS + %1, offset %2
        mov ax, ds
        add ax, %1
        mov [cs:th_call + 2], ax
        mov word [cs:th_call], %2
        call far [cs:th_call]
%endmacro
th_site:
        sti
        pushad
        push es
        mov bx, sp                      ; (BX+34: IP, +36 CS, +38 FLAGS, +40 the DI to pop)
        mov byte [cs:th_miss], 0
        cmp byte [cs:th_armed], 0
        je .done
        cmp word [bp - 4], 0
        jne .done                       ; (the computer's look ahead: no cast)
        cmp si, [cs:cast_spell]
        jne .done
        cmp di, [cs:th_target]
        jne .done
        mov byte [cs:th_armed], 0       ; (one roll a cast)
        cmp byte [cs:acid_burning], 0
        jne .done
        cmp si, 0xFF
        ja .done
        mov ax, si
        push bx
        mov bx, th_missiles
        mov cx, TH_SPELLS
.find:  cmp al, [cs:bx]
        je .found
        inc bx
        loop .find
        pop bx
        jmp .done
.found: mov word [cs:th_kind], 2        ; (a missile: DEX)
        cmp bx, th_touches
        pop bx
        jb .who
        mov word [cs:th_kind], 1        ; (a touch: STR)
.who:   mov ax, [cs:cast_who]
        mov [cs:th_caster], ax
        call tu_creature
        cmp ax, 0xFFFF
        je .done
        imul cx, ax, CREATURE_SIZE
        mov ax, di
        call tu_creature
        cmp ax, 0xFFFF
        je .done
        imul ax, ax, CREATURE_SIZE
        push bx
        les bx, [CREATURES_PTR]
        add ax, bx
        add bx, cx                      ; (ES:BX the caster's creature, ES:AX the target's)
        xchg ax, bx
        mov dl, [es:bx + TH_SIDE]
        xchg ax, bx
        cmp word [cs:th_kind], 1
        jne .thac0
        xor dl, [es:bx + TH_SIDE]
        test dl, 7
        jnz .thac0
        pop bx
        jmp .done                       ; (a touch on one's own side: as the game has it)
.thac0: movsx ax, byte [es:bx + TH_THAC0]
        pop bx
        cmp si, TH_ACID
        jne .own
        mov ax, 21
        movzx cx, byte [cs:th_level]
        sub ax, cx                      ; (a fighter's of the cast's level)
.own:   mov [cs:th_thac0], ax
        xor ax, ax
        cmp word [cs:th_caster], IMAGE_PARTY
        jb .diff
        mov ax, [TH_DIFFICULTY]
        dec ax
.diff:  mov [cs:th_diff], ax
        push bx
        push word [ss:bx + 36]          ; (the way back, in a frame the overlay manager can fix up)
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        push word [cs:th_kind]
        push dword 0
        push word [cs:th_caster]
        push di
        th_far TH_ADJ_STUB, 0x66        ; (target, attacker, no weapon, kind)
        add sp, 10
        cmp si, TH_METEORS
        jne .bonus
        add ax, 2                       ; (Minute Meteors' own +2, as the manual's)
.bonus: mov [cs:th_bonus], ax
        push word [cs:th_caster]
        cmp word [cs:th_kind], 1
        je .str
        th_far TH_ABIL_SEG, 0x2D9
        jmp .part
.str:   th_far TH_ABIL_SEG, 0x2C0
.part:  add sp, 2
        mov [cs:th_part], ax
        push word 0
        push word [cs:th_caster]
        push di
        th_far TH_AC_STUB, 0x7A         ; (target, attacker, not from behind)
        add sp, 6
        mov [cs:th_ac], ax
        pop bp
        pop ax                          ; (the way back, as the overlay manager has left it)
        pop cx
        pop bx
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], cx
        mov ax, 20
        call game_die
        mov [cs:th_d20], ax
        mov dx, ax
        mov ax, [cs:th_thac0]
        sub ax, [cs:th_bonus]
        sub ax, [cs:th_diff]
        sub ax, [cs:th_ac]              ; (the d20 needed)
        cmp dx, 20
        je .rec
        cmp dx, 1
        je .miss
        cmp dx, ax
        jge .rec
.miss:  mov byte [cs:th_miss], 1
.rec:   mov [cs:th_frame + 2], di
        mov [cs:th_frame + 4], si
        movzx ax, byte [cs:th_miss]
        xor al, 1
        mov [cs:th_hitw], ax
        inc word [cs:manual_count]
        mov si, th_frame
        mov cx, (th_frame_end - th_frame) / 2
        mov ax, [cs:th_d20]
        mov word [cs:kind], KIND_TOHIT
        call rec_frame
.done:  mov bx, sp
        movzx ax, byte [cs:th_miss]
        mov [ss:bx + 30], ax            ; (AX: 1 a miss, "immune"; else 0, the game's)
        mov ax, [ss:bx + 40]
        mov [ss:bx + 2], ax             ; (DI popped)
        mov ax, [ss:bx + 38]
        mov [ss:bx + 40], ax
        mov ax, [ss:bx + 36]
        mov [ss:bx + 38], ax
        mov ax, [ss:bx + 34]
        mov [ss:bx + 36], ax            ; (the INT's frame up over it)
        pop es
        popad
        add sp, 2
        iret
; TH_CAST: PROBE_CAST's for TH_SITE: the cast's caster ([BP+6]), target ([BP+8]), spell ([BP+0Ah]) and
; level ([BP+0Ch]) kept, the cast armed for one roll unless it is a weapon's spell on a hit (the cast
; routine's way back followed by WEAPON_BACK's bytes, 5D2D1h's: the call at 5D2CCh, level 6). All kept.
th_cast:
        push ax
        push bx
        push es
        mov ax, [bp + 6]
        mov [cs:cast_who], ax
        mov ax, [bp + 8]
        mov [cs:th_target], ax
        mov ax, [bp + 0x0A]
        mov [cs:cast_spell], ax
        mov al, [bp + 0x0C]
        mov [cs:th_level], al
        mov byte [cs:th_armed], 1
        cmp byte [cs:th_weapon], 0      ; (WEAPON_CAST's: a weapon's spell on a hit, no roll)
        je .back
        mov byte [cs:th_weapon], 0
        mov byte [cs:th_armed], 0
        jmp .out
.back:  les bx, [bp + 2]                ; (the caller's way back)
        cmp dword [es:bx], WEAPON_BACK
        jne .out
        cmp byte [es:bx + 4], WEAPON_BACK4
        jne .out
        mov byte [cs:th_armed], 0
.out:   pop es
        pop bx
        pop ax
        ret
WEAPON_BACK  equ 0x6A18C483           ; ("add sp,18h / push 2": 83 C4 18 6A 02)
WEAPON_BACK4 equ 0x02
th_missiles db 18, 53, 121, 169, 33              ; Acid Arrow, Pebble to Boulder, Magic Stone, Condense, Minute Meteors
th_touches  db 3, 10, 38, 118, 149, 171, 179, 195 ; Chill Touch, Shocking Grasp, Vampiric Touch, Cause Light
TH_SPELLS equ $ - th_missiles                     ;   Wounds, Cause Disease, Cause Serious, Poison, Cause Critical
th_call   dw 0, 0
th_armed  db 0
th_miss   db 0
th_weapon db 0                                    ; (WEAPON_CAST: the next cast a weapon's)
; WEAPON_CAST (site 46, "weapon_cast"): "push 6 / push word [bp-18h]" (5D2C2h; 5 bytes), the level and
; the spell pushed for the cast of a weapon's spell on the target hit (608h:89h, 5D2CCh; SL's
; ARROW_LEVEL at 58BE6h). The pushes made, under the INT's frame as they would have been, and the cast
; marked a weapon's (TH_WEAPON) so it rolls no attack (TH_CAST). TH_CAST's test of the way back's bytes
; failed in play (2026-11-23: a Cause Light Wounds and an arrow's Chill Touch from a hit each rolled a
; touch attack; the overlay manager's return to the attack's overlay need not be its code). All
; registers kept.
WEAPON_CAST_LEVEL equ 6
; The spell arrows (the user's choice, 2026-11-23: SL's ARCHER_LEVEL, "the caster's spell level"): a
; shot's ammunition casting one of the Spellarcher's arrows' spells (WC_ARROWS; the hit's spell is the
; ammunition's, 308h:[7], when it isn't the weapon's own, item SI's +10h less 1; played 2026-11-24)
; casts it at the archer's level (the attacker, combatant DI): a
; party member's (creatures 0-3) preserver's level; anyone else's highest level, as SL's. A party member
; with no preserver class casts nothing (PLAIN_ARROW, below: a plain arrow). A weapon's own spell keeps
; level 6 (the Searing Blade's 2d6+6).
wc_arrows db 3, 10, 38                    ; Chill Touch, Shocking Grasp, Vampiric Touch (the sequel's)
WC_ARROWS equ $ - wc_arrows
wc_level  dw 0
weapon_cast:
        push ax
        call wc_archer
        jnc .level
        mov ax, WEAPON_CAST_LEVEL       ; (no cast is left to come here: PLAIN_ARROW's)
.level: mov [cs:wc_level], ax
        pop ax
        sub sp, 4
        push bx
        push ax
        mov bx, sp                      ; (BX+8 the INT's IP, +10 CS, +12 FLAGS: moved 4 down)
        mov ax, [ss:bx + 8]
        mov [ss:bx + 4], ax
        mov ax, [ss:bx + 10]
        mov [ss:bx + 6], ax
        mov ax, [ss:bx + 12]
        mov [ss:bx + 8], ax
        mov ax, [bp - 0x18]             ; (the spell + 1, less 1: the game's [BP-18h])
        mov [ss:bx + 10], ax
        mov ax, [cs:wc_level]
        mov [ss:bx + 12], ax
        mov byte [cs:th_weapon], 1
        inc word [cs:weapon_casts]
        pop ax
        pop bx
        iret
; PLAIN_ARROW (site 49, "plain_arrow"): "mov [bp-18h],ax / dec word [bp-18h]" (5D248h; 6 bytes), where
; the attack takes the spell + 1 of the hit (AX: the ammunition's for a shot, else the weapon's). Made;
; then for a spell arrow (WC_ARCHER's carry: a party archer with no preserver class) the spell put past
; the game's (PA_NONE), so the game's own test (5D24Eh) skips the cast as for an item with no spell
; (5D2DCh): a plain arrow. ARROWS_PLAIN counts them. A melee hit ([BP+16h] 1, as the routine's Fire Shield
; test at 5D1D6h has it) casts the weapon's own spell alone: the game takes the quiver's arrows' (308h:[7])
; first whatever the weapon, so a member with Shocking Arrows in the quiver cast Shocking Grasp with a
; sword hit, and the game died a few turns later (2026-11-24, with or without WEAPON_CAST); the arrows'
; spell is put past the game's too (MELEE_ARROWS counts them). All registers kept.
PA_NONE equ 0x148
plain_arrow:
        mov [bp - 0x18], ax
        dec word [bp - 0x18]
        cmp word [bp + 0x16], 1
        jne .shot
        cmp byte [cs:pz_armed], 0       ; (POISON_HIT's: a Poisoner's dose, the monsters' poison)
        je .melee
        mov byte [cs:pz_armed], 0
        mov word [bp - 0x18], RAV_POISON_POWER
        inc word [cs:poison_casts]
        iret
.melee:
        push ax
        push bx
        push es
        cmp si, NO_ITEM
        jae .none
        imul bx, si, ITEM_SIZE
        les ax, [ITEMS_PTR]             ; (AX the offset, ES the segment)
        add bx, ax
        mov ax, [es:bx + 0x10]
        dec ax
        cmp ax, [bp - 0x18]
        je .own                         ; (the weapon's own spell)
.none:  mov word [bp - 0x18], PA_NONE
        inc word [cs:melee_arrows]
.own:   pop es
        pop bx
        pop ax
        iret
.shot:  push ax
        call wc_archer
        pop ax
        jnc .out
        mov word [bp - 0x18], PA_NONE
        inc word [cs:arrows_plain]
.out:   iret
melee_arrows dw 0
; WC_ARCHER: AX the level the hit's spell ([BP-18h]) is cast at by combatant DI with item SI, carry set
; for none (a plain arrow). All else kept.
wc_archer:
        push bx
        push cx
        push dx
        push si
        push di
        push es
        mov [cs:wc_archer_is], di
        mov ax, [bp - 0x18]
        cmp si, NO_ITEM
        jae .six
        imul bx, si, ITEM_SIZE
        les di, [ITEMS_PTR]
        add bx, di
        mov cx, [es:bx + 0x10]
        dec cx
        cmp cx, ax
        je .six                         ; (the weapon's own spell, not its ammunition's: 308h:[7])
        mov cx, WC_ARROWS
        mov di, wc_arrows
.arrow: cmp al, [cs:di]
        je .archer
        inc di
        loop .arrow
        jmp .six
.archer:
        mov bx, [cs:wc_archer_is]
        cmp bx, 400
        jae .six
        imul bx, bx, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        cmp byte [es:bx + FIGHTERS_OFF], 2
        jne .six
        mov si, [es:bx + FIGHTERS_OFF + 1]
        imul bx, si, CREATURE_SIZE
        les di, [CREATURES_PTR]
        add bx, di
        imul bx, [es:bx + 4], SHEET_SIZE
        les di, [SHEETS_PTR]
        add bx, di
        xor ax, ax
        mov cx, 3
        cmp si, 3
        ja .foe
.pres:  mov dl, [es:bx + SHEET_CLASSES]
        cmp dl, PRESERVER_CLASS
        je .got
        cmp dl, WIZARD_NEW_CLASS
        je .got
        inc bx
        loop .pres
        stc
        jmp .out
.got:   mov al, [es:bx + SHEET_LEVELS]
        inc word [cs:arrows_cast]
        jmp .least
.foe:   mov dl, [es:bx + SHEET_LEVELS]
        cmp dl, al
        jbe .next
        mov al, dl
.next:  inc bx
        loop .foe
        inc word [cs:arrows_foe]
.least: or ax, ax
        jnz .ok
        inc ax
        jmp .ok
.six:   mov ax, WEAPON_CAST_LEVEL
.ok:    clc
.out:   pop es
        pop di
        pop si
        pop dx
        pop cx
        pop bx
        ret
arrows_plain dw 0
arrows_cast  dw 0                         ; (a party preserver's, counted for a look in play)
arrows_foe   dw 0                         ; (anyone else's)
wc_archer_is dw 0
weapon_casts dw 0
; JOIN_READY (site 47, "join_ready"): "cmp byte [13FAh],0" (58D81h; 5 bytes) in the ADD screen's routine,
; right after a roster character is loaded into the party (its CHAR, c8h:0Ah, at 58D33h). The game puts
; an item's spell (its +10h, the spell + 1) on its wearer only when the item is readied on the inventory
; screen (77C1Ah, 5E8h:39h, as Shattered Lands' 6F7F7h), so a member added from the roster (the party
; carried over from Shattered Lands, or the sequel's own) wore its magic armour with no spell on. Each
; worn item (+13h below JR_WORN) with a spell is readied once through that routine (the creature, the
; item), in a frame the overlay manager can fix up (as IMAGE_BLOW's). The compare's flags into the INT's
; frame. (logs/2026-11-23-ravager-worn.md)
JR_STUB    equ 0x4713 - 0x47E0  ; (5E8h's stub segment less DS's: 39h the ready routine)
JR_ENTRY   equ 0x39
JR_WORN    equ 14               ; (worn slots 0-13; 15 the backpack, 255 on the pointer)
JR_POWER   equ 0x10
JR_FLAG    equ 0x13FA
join_ready:
        sti
        pushad
        push es
        mov di, sp
        cmp byte [JR_FLAG], 0
        pushf
        pop ax
        and ax, FLAGS_MASK
        and word [ss:di + 38], ~FLAGS_MASK
        or [ss:di + 38], ax
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov ax, [es:USE_WHO_OFF]
        mov [cs:jr_who], ax
        mov bx, sp
        push word [ss:bx + 36]          ; (the way back as a far call's frame, for the overlay manager)
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        mov word [cs:jr_list], 8
.list:  imul bx, [cs:jr_who], CREATURE_SIZE
        les si, [CREATURES_PTR]
        add bx, si
        add bx, [cs:jr_list]
        mov dx, [es:bx]
        cmp dx, NO_ITEM
        jae .next
        imul bx, dx, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        cmp byte [es:bx + FIGHTERS_OFF], 1
        jne .next                       ; not an item
        mov dx, [es:bx + FIGHTERS_OFF + 1]
        mov word [cs:jr_left], 100      ; (no more than 100 in a list)
.item:  cmp dx, NO_ITEM
        jae .next
        dec word [cs:jr_left]
        js .next
        mov [cs:jr_item], dx
        imul bx, dx, ITEM_SIZE
        les si, [ITEMS_PTR]
        add bx, si
        mov dx, [es:bx + ITEM_NEXT]
        cmp byte [es:bx + ITEM_SLOT], JR_WORN
        jae .item
        cmp word [es:bx + JR_POWER], 0
        je .item
        mov [cs:jr_next], dx
        mov ax, ds
        add ax, JR_STUB
        mov [cs:jr_far + 2], ax
        mov word [cs:jr_far], JR_ENTRY
        push word [cs:jr_item]
        push word [cs:jr_who]
        call far [cs:jr_far]            ; (the creature, the item)
        add sp, 4
        inc word [cs:join_readied]
        mov dx, [cs:jr_next]
        jmp .item
.next:  add word [cs:jr_list], 2
        cmp word [cs:jr_list], 0x0E
        jb .list
        pop bp
        pop ax                          ; (the way back, as the overlay manager has left it)
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
        pop es
        popad
        iret
jr_far   dd 0
jr_who   dw 0
jr_list  dw 0
jr_item  dw 0
jr_next  dw 0
jr_left  dw 0
join_readied dw 0               ; worn items readied as a member joined (for the tests)
; TOME (site 48, "tome_read"): "dec word [bp-4]" (999CDh; 3 bytes) in the routine run when a scroll's
; icon is clicked in its box (SL's 8B690h, DSCLOG's PROBE_TOME): SI the item, DI its object, [BP-4] its
; power (+10h, the spell + 1). The Tome of Understanding as the transfer makes it (ravtransfer's
; WOTR_TOME_SPELL, the Loader's object TM_OBJECT) gives the one on show a point of WIS, in the sheet and
; the creature record, at most TM_MOST, and the game goes on as for a psionic power taught (99B44h): the
; tome used up and the message in its buffer at [BP-56h] shown, "<name> reads the tome: WIS <n>." At
; TM_MOST already, only the message ("... can grow no wiser.", 99B67h) and the tome kept. Anything
; else: the DEC, and on.
TM_OBJECT   equ 21446               ; (ravitems.own_object(1446))
TM_POWER    equ 317 + 1
TM_MOST     equ 25
TM_SHEET_WIS equ 0x19
TM_CRE_WIS  equ 0x1D
TM_NAME     equ 0x21
TM_USE      equ 0x99B44 - 0x999D0
TM_SHOW     equ 0x99B67 - 0x999D0
tome_read:
        cmp di, TM_OBJECT
        jne .game
        cmp word [bp - 4], TM_POWER
        je .tome
.game:  dec word [bp - 4]
        iret
.tome:  pushad
        push es
        push fs
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov bx, [es:USE_WHO_OFF]        ; the reader
        mov byte [cs:tr_used], 0
        les di, [SHEETS_PTR]
        imul ax, bx, SHEET_SIZE
        add di, ax                      ; ES:DI: their sheet
        lfs si, [CREATURES_PTR]
        imul ax, bx, CREATURE_SIZE
        add si, ax                      ; FS:SI: their creature record
        mov al, [es:di + TM_SHEET_WIS]
        cmp al, TM_MOST
        jae .text
        inc al
        mov [es:di + TM_SHEET_WIS], al
        mov byte [cs:tr_used], 1
        cmp byte [fs:si + TM_CRE_WIS], TM_MOST
        jae .text
        inc byte [fs:si + TM_CRE_WIS]
.text:  mov [cs:tr_wis], al
        push ss
        pop es
        lea di, [bp - 0x56]             ; ES:DI: the game's message buffer
        mov cx, 15
        add si, TM_NAME
.name:  mov al, [fs:si]
        or al, al
        jz .named
        stosb
        inc si
        loop .name
.named: push ds
        push cs
        pop ds
        mov si, tr_reads
        cmp byte [cs:tr_used], 0
        jne .copy
        mov si, tr_wiser
.copy:  lodsb
        stosb
        or al, al
        jnz .copy
        pop ds
        mov ax, TM_SHOW
        cmp byte [cs:tr_used], 0
        je .on
        dec di                          ; (the number, after "WIS ")
        mov al, [cs:tr_wis]
        aam                             ; AH tens, AL ones
        or ax, 0x3030
        cmp ah, 0x30
        je .ones
        mov [es:di], ah
        inc di
.ones:  mov [es:di], al
        mov word [es:di + 1], '.'
        inc word [cs:tomes_read]
        mov ax, TM_USE
.on:    mov si, sp
        add [ss:si + 36], ax            ; (the INT's IP, above FS, ES and PUSHAD's 32 bytes)
        pop fs
        pop es
        popad
        iret
tr_wis   db 0
tr_used  db 0
tr_reads db " reads the tome: WIS ", 0
tr_wiser db " can grow no wiser.", 0
tomes_read dw 0                 ; (for the tests)
; NEW_SHEET (site 50, "sheet_new_tail"): "add sp,0Ah" (6957Dh; 3 bytes) after the creation screen's
; memcpy (0:3F5Ah) of its template (360h:29h, the game's 42h bytes: GAME_SHEET_SIZE) into the new
; character's sheet, the Loader's 48h (SHEET_SIZE: ravager's sheet patches): the six bytes past the
; template's (the weapon specs and the starting age's roll, +42h..+44h, then three spare) cleared, else
; they were the slot's last owner's; then the ADD SP done (the way back, its CS and flags and the
; game's BP moved up 10 over memcpy's arguments, the destination far at [BP+8] here). SHEETS_MADE
; counts them. All registers kept.
GAME_SHEET_SIZE equ 0x42
new_sheet:
        push bp
        mov bp, sp
        push es
        push di
        push cx
        push ax
        les di, [bp + 8]                ; (memcpy's destination: the sheet)
        cmp byte [es:di + KIT_BYTE], KIT_OPEN
        jne .kit                        ; (a kit taken back on the KIT page and none chosen: none)
        mov byte [es:di + KIT_BYTE], 0
.kit:   add di, GAME_SHEET_SIZE
        xor ax, ax
        mov cx, (SHEET_SIZE - GAME_SHEET_SIZE) / 2
        cld
        rep stosw
        inc word [cs:sheets_made]
        mov ax, [bp]                    ; (the game's BP, the way back, its CS, the flags: 10 up)
        mov [bp + 10], ax
        mov ax, [bp + 2]
        mov [bp + 12], ax
        mov ax, [bp + 4]
        mov [bp + 14], ax
        mov ax, [bp + 6]
        mov [bp + 16], ax
        pop ax
        pop cx
        pop di
        pop es
        lea sp, [bp + 10]
        pop bp
        iret
sheets_made dw 0                ; (for the tests)
th_level  db 0
th_target dw 0xFFFF
cast_who  dw 0
cast_spell dw 0
th_frame:                       ; (SL's: the frame's +6 on)
th_caster dw 0
          dw 0                  ; (+8 the target, +0Ah the spell)
          dw 0
th_thac0  dw 0
th_bonus  dw 0
th_part   dw 0
th_diff   dw 0
th_ac     dw 0
th_d20    dw 0
th_kind   dw 0
th_hitw   dw 0                  ; (+1Ah 1 a hit)
th_frame_end:
; REST_HP (site 17, "rest_hp"; RULE_HI_REST, the Loader's "rest_heal", always on): SL's REST_HP. The
; sequel's rest (8CA7Bh(mode [BP+6], hours [BP+8]), SL's 8066Dh) sets an Okay member's HP to its sheet's
; most in pass 2 with "mov [es:bx],ax" (8CF79h; 3 bytes: ES:BX the creature, AX the most, SI the
; member). With the rule and mode 0: HP + REST_NATURAL (3) + CON's hit point bonus (the creature's
; +1Bh, at most 25; the game's level hit point table, load + 45BEh (selector 4D0h, SL's 40B1h): +52h +
; CON, a warrior's in full if one of the sheet's classes (+1Bh..+1Dh) is of group 1 there (+10h +
; class), else at most +2), at least 1, no more than the most, never less than it had nor 1. Mode 1
; (the scripts' full restore) and the rule off: the move as the game's. Recorded (KIND_REST, RS_HEAL:
; the member, HP before, CON's part, after, the most, CON; dicelog's rest lines).
RULE_HI_REST  equ 4096
KIND_REST     equ 15
RS_HEAL       equ 2
REST_NATURAL  equ 3
LEVEL_HP_GAP  equ 0x47E0 - 0x45BE       ; (the level hit point table's segment below DS)
LEVEL_HP_CON  equ 0x52
WARRIOR_GROUP equ 1
REST_CON_AT   equ 0x1B                  ; (the creature's CON; SL's +24h)
rest_hp:
        cmp word [bp + 6], 0
        jne .game
        test word [cs:rules_hi], RULE_HI_REST
        jnz .rule
.game:  mov [es:bx], ax
        iret
.rule:  pushad
        push es
        mov cx, ax
        mov di, [es:bx]
        mov [cs:rs_frame], si
        mov [cs:rs_frame + 2], di
        mov [cs:rs_frame + 8], cx
        call rest_con2
        mov [cs:rs_frame + 4], ax
        add ax, REST_NATURAL
        cmp ax, 1
        jge .heal
        mov ax, 1
.heal:  add ax, di
        cmp ax, cx
        jle .most
        mov ax, cx
.most:  cmp ax, di
        jge .least
        mov ax, di
.least: cmp ax, 1
        jge .set
        mov ax, 1
.set:   mov [es:bx], ax
        mov [cs:rs_frame + 6], ax
        movzx ax, byte [es:bx + REST_CON_AT]
        mov [cs:rs_frame + 10], ax
        inc word [cs:manual_count]
        mov si, rs_frame
        mov cx, 6
        mov word [cs:kind], KIND_REST
        mov ax, RS_HEAL
        call rec_frame
        pop es
        popad
        iret
; REST_CON2: AX CON's hit point bonus of creature ES:BX (REST_HP's). Others kept.
rest_con2:
        push bx
        push cx
        push dx
        push si
        push es
        push fs
        movzx cx, byte [es:bx + REST_CON_AT]
        cmp cx, 25
        jbe .con
        mov cx, 25
.con:   mov ax, [es:bx + 4]
        imul ax, ax, SHEET_SIZE
        les bx, [SHEETS_PTR]
        add bx, ax
        mov ax, ds
        sub ax, LEVEL_HP_GAP
        mov fs, ax
        xor dx, dx
        xor si, si
.class: push bx
        movzx bx, byte [es:bx + si + 0x1B]
        or bx, bx
        jz .other
        cmp bx, 32
        jae .other
        cmp byte [fs:bx + 0x10], WARRIOR_GROUP
        jne .other
        mov dl, 1
.other: pop bx
        inc si
        cmp si, 3
        jb .class
        mov bx, cx
        movsx ax, byte [fs:bx + LEVEL_HP_CON]
        or dl, dl
        jnz .out
        cmp ax, 2
        jle .out
        mov ax, 2
.out:   pop fs
        pop es
        pop si
        pop dx
        pop cx
        pop bx
        ret
rs_frame dw 0, 0, 0, 0, 0, 0
; REST_PRE (site 18, "rest_spells"; RULE_HI_REST): SL's REST_PRE, the party's priests spending the
; spells they have left on the party before the night. The rest's first move, "mov word [bp-6],0"
; (8CA82h; 5 bytes), before its fight test and its slots' refill. With the rule, mode 0 and no fight
; (DS:13FAh): RP_PASS in a frame the overlay manager can fix up (the casts load the spells' overlay
; over the rest's). Each member's priest level: the best level of its cleric, druid or class-19 classes
; (the sheet's +1Bh..+1Dh, levels +1Eh..), 0 if it can't cast (RP_ABLE: status, creature +14h, Okay or
; New; not Feebleminded 37, Can't Cast 68 or Paralyzed 69). Then Neutralize Poison (178) on the
; Poisoned (71), Cure Blindness (146) on the Blind (10), Cure Disease (148) on the Diseased (27) only
; with no priest of FREE_CURES (5) or more (the rest's own pass casts it free then), then the wounds:
; the member (status Okay to Out Cold) with the most hit points missing after the night's natural
; healing (REST_HP's), the biggest cure (Cure Light 117, Serious 170, Critical 194, Heal 210: for 4,
; 10, 16 and 30 or more missing) of no more than that someone can cast, else the smallest, at most
; RP_MOST_CASTS. A priest knows every priest spell (the sequel has no spheres: its USE screen shows a
; cleric all of them); it casts with a slot of the spell's level left (DS:4474h + 22h a member + the
; level, taken: pass 1 fills them again), through the rest's own free-cure cast (4787h:25h, 8D074h:
; spell, target, caster, level; 598h:66h with the rest's arguments). Then, as SL's, a psionicist's Cell
; Adjustment (RP_PSI_CAST) on the Diseased, and on the most wounded when no cure is left. Recorded
; (KIND_REST, RS_CAST: caster, target, spell, the slot's level (0 for a power), left (slots or PSP), 0).
RS_CAST       equ 1
RP_MEMBERS    equ 4
RP_MOST_CASTS equ 24
FREE_CURES    equ 5
RP_STATUS     equ 0x14              ; (the creature's status: 1 Okay, 0 New ... 3 Out Cold)
PRIEST_SLOTS2 equ 0x4474            ; DS: a priest's slots left, + the level, 22h a member
SLOTS_STRIDE2 equ 0x22
RP_CAST_STUB  equ 0x4787 - 0x47E0   ; (the rest's overlay stub: 25h the free cure's cast)
rest_pre:
        mov word [bp - 6], 0            ; (the move replaced)
        cmp word [bp + 6], 0
        jne .iret
        test word [cs:rules_hi], RULE_HI_REST
        jz .iret
        cmp byte [IN_COMBAT], 0
        jne .iret
        sti
        pushad
        push es
        mov bx, sp
        push bx
        push word [ss:bx + 36]          ; (the way back, in a frame the overlay manager can fix up)
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        call rp_pass
        mov sp, bp
        pop bp
        pop ax                          ; (the way back, as the overlay manager has left it)
        pop cx
        pop bx
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], cx
        pop es
        popad
.iret:  iret
rp_pass:
        mov byte [cs:rp_best], 0
        xor si, si
.level: mov byte [cs:rp_level + si], 0
        call rp_able
        jnz .next
        call rp_priest
        mov [cs:rp_level + si], al
        cmp al, [cs:rp_best]
        jbe .next
        mov [cs:rp_best], al
.next:  inc si
        cmp si, RP_MEMBERS
        jb .level
        mov ax, 178                     ; (Neutralize Poison on the Poisoned)
        mov cl, 71
        call rp_effect
        mov ax, 146                     ; (Cure Blindness on the Blind)
        mov cl, 10
        call rp_effect
        cmp byte [cs:rp_best], FREE_CURES
        jae .wounds
        mov ax, 148                     ; (Cure Disease on the Diseased)
        mov cl, 27
        call rp_effect
.wounds:
        xor si, si                      ; (a psionicist's Cell Adjustment on the Diseased still: its
.ill:   call rp_alive                   ;  record's cure of disease)
        jnz .well
        mov ax, si
        mov cl, 27
        call has_effect
        jnz .well
        call rp_psi_cast
.well:  inc si
        cmp si, RP_MEMBERS
        jb .ill
        mov cx, RP_MOST_CASTS
.again: push cx
        call rp_worst
        jc .done
        call rp_choose
        jc .psi
        call rp_cast
        jmp .on
.psi:   call rp_psi_cast                ; (no cure left: a psionicist's Cell Adjustment)
        jc .done
.on:    pop cx
        loop .again
        ret
.done:  pop cx
        ret
; RP_CREATURE: ES:BX member SI's creature (the party's creatures 0-3, as the rest reads them). All kept.
rp_creature:
        push ax
        imul ax, si, CREATURE_SIZE
        les bx, [CREATURES_PTR]
        add bx, ax
        pop ax
        ret
; RP_ABLE: ZF set if member SI can cast (Okay or New, none of RP_STOPS). All kept.
rp_able:
        push ax
        push bx
        push cx
        push es
        call rp_creature
        cmp byte [es:bx + RP_STATUS], 1
        ja .no
        mov bx, rp_stops
.each:  mov cl, [cs:bx]
        or cl, cl
        jz .yes
        mov ax, si
        call has_effect
        jz .no
        inc bx
        jmp .each
.yes:   xor ax, ax
        jmp .out
.no:    or sp, sp
.out:   pop es
        pop cx
        pop bx
        pop ax
        ret
; RP_PRIEST: AL member SI's priest level (its best cleric's, druid's or class 19's level). Others kept.
rp_priest:
        push bx
        push cx
        push di
        push es
        call rp_creature
        mov bx, [es:bx + 4]
        imul bx, bx, SHEET_SIZE
        push bx
        les bx, [SHEETS_PTR]
        pop di
        add bx, di
        xor al, al
        xor di, di
.class: mov cl, [es:bx + di + 0x1B]
        cmp cl, 0
        je .next
        cmp cl, 8
        jbe .priest
        cmp cl, 19
        jne .next
.priest:
        cmp al, [es:bx + di + 0x1E]
        jae .next
        mov al, [es:bx + di + 0x1E]
.next:  inc di
        cmp di, 3
        jb .class
        pop es
        pop di
        pop cx
        pop bx
        ret
; RP_ALIVE: ZF set if member SI is Okay, New, Stunned or Out Cold; ES:BX its creature. Others kept.
rp_alive:
        call rp_creature
        cmp byte [es:bx + RP_STATUS], 3
        ja .no
        cmp al, al
        ret
.no:    or sp, sp
        ret
; RP_EFFECT: spell AX on each member with effect CL (RP_ALIVE), by the first who can (RP_FIND).
rp_effect:
        mov [cs:rp_spell], ax
        mov [cs:rp_effect_n], cl
        xor si, si
.each:  call rp_alive
        jnz .next
        mov ax, si
        mov cl, [cs:rp_effect_n]
        call has_effect
        jnz .next
        call rp_find
        jc .next
        call rp_cast
.next:  inc si
        cmp si, RP_MEMBERS
        jb .each
        ret
; RP_FIND: DI a member with a priest level and a slot of RP_SPELL's level left, RP_SLOT the level; CF
; set if none. Others kept.
rp_find:
        push ax
        push bx
        mov ax, [cs:rp_spell]
        call rp_spell_level
        mov [cs:rp_slot], al
        xor di, di
.each:  cmp byte [cs:rp_level + di], 0
        je .next
        imul bx, di, SLOTS_STRIDE2
        movzx ax, byte [cs:rp_slot]
        add bx, ax
        cmp byte [bx + PRIEST_SLOTS2], 0
        je .next
        clc
        jmp .out
.next:  inc di
        cmp di, RP_MEMBERS
        jb .each
        stc
.out:   pop bx
        pop ax
        ret
; RP_SPELL_LEVEL: AL priest spell AX's level (the sequel's table at DS:0656h + 11, the first spell of
; each level). Others kept.
rp_spell_level:
        push bx
        push cx
        mov cx, ax
        xor al, al
        mov bx, 0x0656 + 11
.lvl:   cmp cl, [bx]
        jb .out
        inc al
        inc bx
        cmp al, 10
        jb .lvl
.out:   pop cx
        pop bx
        ret
; RP_CAST: member DI casts RP_SPELL on member SI with a slot of RP_SLOT's level (taken) at its priest
; level, recorded (RS_CAST), through 4787h:25h. SI and DI kept.
rp_cast:
        imul bx, di, SLOTS_STRIDE2
        movzx ax, byte [cs:rp_slot]
        add bx, ax
        dec byte [bx + PRIEST_SLOTS2]
        movzx ax, byte [bx + PRIEST_SLOTS2]
        mov cl, [cs:rp_level + di]
; RP_CAST_AT: member DI casts RP_SPELL on member SI at level CL, recorded (RS_CAST: RP_SLOT the slot's
; level, AX what is left), through 4787h:25h. SI and DI kept.
rp_cast_at:
        mov [cs:rp_cast_level], cl
        push si
        push di
        mov [cs:rs_frame], di
        mov [cs:rs_frame + 2], si
        mov [cs:rs_frame + 8], ax
        mov ax, [cs:rp_spell]
        mov [cs:rs_frame + 4], ax
        movzx ax, byte [cs:rp_slot]
        mov [cs:rs_frame + 6], ax
        mov word [cs:rs_frame + 10], 0
        inc word [cs:manual_count]
        mov si, rs_frame
        mov cx, 6
        mov word [cs:kind], KIND_REST
        mov ax, RS_CAST
        call rec_frame
        pop di
        pop si
        movzx ax, byte [cs:rp_cast_level]
        push ax                         ; (the level)
        push di                         ; (the caster)
        push si                         ; (the target)
        push word [cs:rp_spell]
        th_far RP_CAST_STUB, 0x25       ; (spell, target, caster, level: the rest's free cure)
        add sp, 8
        ret
; RP_WORST: SI the member (RP_ALIVE) with the most hit points missing after the night's natural healing
; (REST_HP's), AX how many; CF set if none is wounded.
rp_worst:
        xor ax, ax
        mov [cs:rp_wound], ax
        mov di, -1
        xor si, si
.each:  call rp_alive
        jnz .next
        call rest_con2
        add ax, REST_NATURAL
        cmp ax, 1
        jge .nat
        mov ax, 1
.nat:   add ax, [es:bx]
        push bx
        push es
        mov bx, [es:bx + 4]
        imul bx, bx, SHEET_SIZE
        push bx
        les bx, [SHEETS_PTR]
        pop dx
        add bx, dx
        mov dx, [es:bx + 8]             ; (the most)
        pop es
        pop bx
        sub dx, ax
        cmp dx, [cs:rp_wound]
        jle .next
        mov [cs:rp_wound], dx
        mov di, si
.next:  inc si
        cmp si, RP_MEMBERS
        jb .each
        mov si, di
        mov ax, [cs:rp_wound]
        cmp di, -1
        je .none
        clc
        ret
.none:  stc
        ret
; RP_CHOOSE: for a wound of AX, RP_SPELL the biggest cure (RP_CURES) of no more than it that someone
; can cast (RP_FIND: DI, RP_SLOT), else the smallest that someone can; CF set if none. SI kept.
        SHARED_rp_choose
; RP_PSI_CAST: Cell Adjustment (CELL_ADJUST) on member SI by the first member who can (RP_ABLE), knows it
; (its byte at 370h:9CDh + 22h a member + the power's place from 235: bits 1-7, the game's own test at
; 5C340h) and has its PSP (the powers' table 3D0h:7E0h, 3 bytes a power, +1 the cost: 5), taken off
; (the creature's +2); cast at level 1, as SL's; CF set if none. SI kept.
CELL_ADJUST     equ 248
CELL_PLACE      equ CELL_ADJUST - 235
PSI_KNOWN_SEG   equ 0x47E0 - 0x3E71     ; (selector 370h: DS less this)
PSI_KNOWN       equ 0x9CD
PSI_COSTS_SEG   equ 0x47E0 - 0x41F1     ; (selector 3D0h)
PSI_COSTS       equ 0x7E0
rp_psi_cast:
        mov word [cs:rp_spell], CELL_ADJUST
        mov byte [cs:rp_slot], 0
        xor di, di
.each:  call rp_able_di
        jnz .next
        mov ax, ds
        sub ax, PSI_KNOWN_SEG
        mov es, ax
        imul bx, di, 0x22
        test byte [es:bx + PSI_KNOWN + CELL_PLACE], 0xFE
        jz .next
        mov ax, ds
        sub ax, PSI_COSTS_SEG
        mov es, ax
        movzx dx, byte [es:PSI_COSTS + CELL_PLACE * 3 + 1]
        push si
        mov si, di
        call rp_creature
        pop si
        mov ax, [es:bx + 2]
        sub ax, dx
        jl .next
        mov [es:bx + 2], ax
        mov cl, 1
        call rp_cast_at                 ; (AX the PSP left)
        clc
        ret
.next:  inc di
        cmp di, RP_MEMBERS
        jb .each
        stc
        ret
; RP_ABLE_DI: RP_ABLE for member DI. All kept.
rp_able_di:
        push si
        mov si, di
        call rp_able
        pop si
        ret
rp_cast_level db 0
rp_level   times RP_MEMBERS db 0
rp_best    db 0
rp_slot    db 0
rp_effect_n db 0
rp_spell   dw 0
rp_wound   dw 0
rp_stops   db 37, 68, 69, 0         ; (Feebleminded, Can't Cast, Paralyzed)
rp_cures   dw 117, 4, 170, 10, 194, 16, 210, 30 ; (Cure Light, Serious, Critical Wounds, Heal)
RP_CURES_END equ $
; CLASS RESTRICTIONS (SL's, DSCLOG's PROBE_CAN_USE, CLASS_FORBIDS, PROBE_BELT's and THIEF_REAR's
; THIEF_HEAVY; game.RULE_RESTRICT, always on in SL; dsloader/restrict.py). The sequel's records: an item
; type's flags +0 (4 a shield, 2 missile, 10h thrown), material +4 (its low nibble; 40h with 0 none),
; armour +0Bh 80h, the classes that may use it +0Ch; a sheet's class bits +10h, race +12h (1 human),
; classes +1Bh, levels +1Eh. The mod's bracers, robes and Cloak of Protection (its types 102-145 in
; OBJEX2.GFF, with the party transfer) aren't armour (ARMOUR_TYPE). Not in the sequel, so not here:
; the Spellarcher's arrows. The kits' gear limits and own gear: KITS' GEAR, below.
; - CU_SITE (site 19) replaces "mov [bp-1],al" (775FDh) at the end of the sequel's "may this character
;   equip this item" (77525h on; SL's 6EE5xh, the same tests but its answer a byte): AL 1 if the item
;   type's classes include one of the character's, DX the type, [BP+0Ah] the sheet (far). An item the
;   game allows that the classes' limits forbid (CLASS_FORBIDS) is refused, the game then saying it can't
;   use it, as SL's. With the kits (RULE_HI_KITS), as SL's PROBE_CAN_USE: the kit's own (KIT_ALLOWS) are
;   allowed whatever the game's lists and the classes' limits, and the kit's limits (KIT_FORBIDS) hold
;   over everything; the slot is the equip routine's (7761Bh: [BP+8], the frame under this one's), 14
;   the off hand. Every other "no" of the routine (no such item, a thri-kreen's, the item's own flags)
;   leaves before this site (to 77561h), so AL 0 here is the classes' lists alone.
; - BELT_SITE (site 20) replaces "mov ax,si / pop di" (8C7C5h) at the end of the thief skill routine
;   (8C647h; SL's 803B2h): SI the chance, DI the thief's combatant. 0 for a thief in armour that isn't
;   light (THIEF_HEAVY).
; - THIEF_REAR, called from MISSILE_REAR (5C99Fh, in the attack's set-up after its from behind, [BP-19h],
;   and backstab, [BP-21h], bytes; [BP-1Eh] the THAC0 both lower by 2; SI the attacker): a party thief in
;   armour that isn't light backstabs no more.
; - CAST_ARMOUR (site 21) replaces "mov ax,1" (84F6Eh) at the "yes" of the casting case of the sequel's
;   "can this creature do it" (84E94h: [BP+6] the kind, DI the creature; the casting case at 84EE7h tests
;   a sheet, Okay, not hit this round, and its effect bits: Can't Cast 68, Feebleminded 37 and the rest,
;   SL's 89B4Dh's test inside it): a multiclass preserver can't while it wears armour, a helm too
;   (ARMOUR_WORN; a shield doesn't count), nor a human who has been a preserver and a fighter, gladiator
;   or ranger (CLASS_AND_WARRIOR): SL's PROBE_NO_CAST. Ar'Anda (OWN_LIGHT) only in armour that isn't light.
RULE_RESTRICT equ 8192
CU_TYPE_SIZE equ 0x0F
CU_FLAGS    equ 0x00
CU_MATERIAL equ 0x04
CU_KIND_FLAGS equ 0x0B
CU_CLASSES  equ 0x0C
SH_CLASS_BITS equ 0x10
SH_RACE     equ 0x12
SH_CLASSES  equ 0x1B
SH_LEVELS   equ 0x1E
CU_SHEET_SIZE equ SHEET_SIZE
CU_HUMAN    equ 1
NO_MATERIAL equ 0xFF
LEATHER     equ 5
THIEF_BIT   equ 0x400
PSI_KINDS   equ 0x20701E        ; bits by kind: club, dagger, short sword, mace, chatkcha, bow, sling, darts
SPHERE_EARTH equ 0x1D           ; bits by material: wood, stone, obsidian, metal
SPHERE_FIRE equ 0x08            ; obsidian
SPHERE_WATER equ 0x03           ; wood, bone
CU_BOW_KIND equ 14              ; (KIND_OF_TYPE's bow)
CU_FIGHTER  equ 9
CU_GLADIATOR equ 10
KIND_TYPES  equ 147             ; (KIND_OF_TYPE's types: the sequel's 102, the mod's 44, SL's 1: ravager.SL_EXTRA_TYPES)
ARM_SLOT    equ 0               ; (an item's +13h while worn: arms, legs, head, chest)
LEG_SLOT    equ 6
HEAD_SLOT   equ 7
CHEST_SLOT  equ 9
cu_site:
        push bx
        push es
        les bx, [bp + 0x0A]
        or al, al
        jnz .game
        call kit_allows                 ; (the game's lists say no: the kit's own, all the same)
        jnc .out
        inc al
        inc word [cs:kit_allowed]
.game:  call arrows_forbid                ; (a Spellarcher's arrows: only a Spellarcher readies them)
        jc .arrows_no
        push si
        mov si, [bp]                    ; (the equip routine's frame: its [BP+8] the slot, 14 the off hand)
        cmp word [ss:si + 8], EQUIP_OFF_HAND
        pop si
        sete [cs:kf_off_hand]
        call kit_forbids
        mov byte [cs:kf_off_hand], 0
        jc .kit_no
        call kit_allows                 ; (the kit's own: whatever the classes' restrictions)
        jc .out
        test word [cs:rules], RULE_RESTRICT
        jz .out
        call class_forbids
        jnc .out
        xor al, al
        inc word [cs:restrict_count]
        jmp .out
.kit_no:
        xor al, al
        inc word [cs:kit_refused]
        jmp .out
.arrows_no:
        xor al, al
        inc word [cs:arrows_barred]
.out:   pop es
        pop bx
        mov [bp - 1], al
        iret

; ARROWS_FORBID (from CU_SITE): CF set if the item being equipped (the equip routine's [BP+6], 7761Bh: the
; frame under the can-use routine's) is a Spellarcher's spell arrows (named AP_ARROW_NAME to +3, the Loader's
; names) and the character whose sheet is at ES:BX isn't a Spellarcher (KIT_SPELLARCHER awake): DSCLOG's, on
; the sequel's items. The game asks nothing of an item put in a backpack, so only readying is refused there
; (the Loader's return_strays still takes another member's back, out of a fight). With the kits (RULE_HI_KITS)
; only: without them no one is a Spellarcher, and the arrows are as any. DS the game's; all registers kept.
arrows_forbid:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ok
        push ax
        push si
        push es
        push bx
        mov si, [bp]                    ; (the equip routine's frame)
        imul ax, [ss:si + 6], ITEM_SIZE
        les si, [ITEMS_PTR]
        add si, ax
        mov ax, [es:si + ITEM_NAME_W]
        sub ax, AP_ARROW_NAME
        cmp ax, 4
        pop bx
        pop es
        jae .not
        call kit_is_b
        db KIT_SPELLARCHER
        je .not
        pop si
        pop ax
        stc
        ret
.not:   pop si
        pop ax
.ok:    clc
        ret
belt_site:
        sti
        mov ax, si
        call kit_skill                  ; (the kits': KITS)
        test word [cs:rules], RULE_THIEF_TABLE
        jz .heavy
        cmp ax, THIEF_MOST
        jle .heavy
        mov ax, THIEF_MOST              ; (Thieves as in AD&D: AD&D's most, SL's PROBE_BELT)
.heavy: test word [cs:rules], RULE_RESTRICT
        jz .pop
        push ax
        mov ax, di
        call fighter_creature
        jc .game
        call thief_heavy
        jnc .game
        pop ax
        xor ax, ax
        inc word [cs:restrict_count]
        jmp .pop
.game:  pop ax
.pop:   push bp                         ; (the replaced "pop di": the INT's frame moved up over it)
        mov bp, sp
        push ax
        mov ax, [bp + 8]
        mov di, ax
        mov ax, [bp + 6]
        mov [bp + 8], ax                ; FLAGS
        mov ax, [bp + 4]
        mov [bp + 6], ax                ; CS
        mov ax, [bp + 2]
        mov [bp + 4], ax                ; IP
        mov ax, [bp]
        mov [bp + 2], ax                ; BP
        pop ax
        pop bp                          ; (the old [BP] slot: thrown away)
        pop bp
        iret
; THIEVES AS IN AD&D: SL's RULE_THIEF_TABLE (game.RULE_THIEF_TABLE, its RULE_BACKSTAB; the Loader's
; "thief_table", always on; DSCLOG's PROBE_THIEF_SKILL, PROBE_BELT's THIEF_MOST and STAB_TIMES):
; - THIEF_SKILL (site 52, "thief_table") replaces "mov ax,si / shl ax,2 / add dx,ax / mov si,dx"
;   (8C716h; 9 bytes, SL's 80307h, the same) in the thief skill routine (8C647h): INT VEC_SITE, 52, then
;   "jc" past the game's DEX formula to its armour and effects (8C795h) and 4 NOPs. DX the skill's base
;   plus the race's adjustment, SI the thief level, ES:0 the thief tables (the base at +skill), [BP+8]
;   the skill, [BP-2] DEX (SL's [BP-0Ch]). With the rule and a thief level, SI = AD&D's average for the
;   level (THIEF_ADND) + the race's + Dark Sun's DEX adjustment, CF set; else the game's sum (SI = DX + 4
;   a level), CF clear, on to the game's DEX formula.
; - BELT_SITE (above): with the rule, the chance (armour and effects counted) no more than THIEF_MOST.
; - C_THIEF (the inventory's skills): with the rule, AD&D's average + race + DEX, no more than THIEF_MOST.
; - STAB_TIMES (ENLARGE DICE, below): a backstab multiplies the weapon's dice only.
RULE_THIEF_TABLE equ 256
THIEF_MOST  equ 95
THIEF_LEVELS equ 17
thief_skill:
        sti
        test word [cs:rules], RULE_THIEF_TABLE
        jz .game
        cmp si, 1
        jl .game
        push bx
        push cx
        mov bx, [bp + 8]
        and bx, 7
        movsx ax, byte [es:bx]          ; (the game's base, out)
        sub dx, ax
        mov cx, [bp - 2]
        call thief_adnd
        add dx, ax
        pop cx
        pop bx
        mov si, dx
        push bp
        mov bp, sp
        or byte [bp + 6], 1             ; (CF in the flags IRET restores: past the game's DEX formula)
        pop bp
        iret
.game:  shl si, 2
        add si, dx
        push bp
        mov bp, sp
        and byte [bp + 6], 0xFE
        pop bp
        iret
; THIEF_ADND: AX = AD&D's average for thief skill BX (0-7) at thief level SI (1 on; past THIEF_LEVELS as
; THIEF_LEVELS) + Dark Sun's DEX adjustment for DEX CX (below 9 as 9, past 22 as 22; the first five
; skills only): game.AD_D_THIEF, DEX_ADJUST. Others kept.
thief_adnd:
        push bx
        push cx
        push si
        push fs                 ; (THIEF_TABLE and DEX_TABLE: the tail's)
        call tail_fs
        cmp si, THIEF_LEVELS
        jbe .level
        mov si, THIEF_LEVELS
.level: imul ax, bx, THIEF_LEVELS
        add si, ax
        movzx ax, byte [fs:thief_table + si - 1]
        cmp bx, 5
        jae .out
        cmp cx, 9
        jge .low
        mov cx, 9
.low:   cmp cx, 22
        jle .high
        mov cx, 22
.high:  imul cx, cx, 5
        add bx, cx
        movsx cx, byte [fs:dex_table + bx - 9 * 5]
        add ax, cx
.out:   pop fs
        pop si
        pop cx
        pop bx
        ret
section tail                    ; (the tables in the tail: room in the segment, 2026-11-28)
; AD&D's average thief skills, levels 1-17, a row per skill (game.AD_D_THIEF: the owner's table, 2026-11-25,
; the same as SL's to 13th; flat past 17th)
thief_table:
        db 30, 35, 40, 45, 50, 55, 60, 65, 70, 80, 90, 95, 99, 99, 99, 99, 99 ; pick pockets
        db 25, 29, 33, 37, 42, 47, 52, 57, 62, 67, 72, 77, 82, 87, 92, 97, 99 ; open locks
        db 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 99 ; find/remove traps
        db 15, 21, 27, 33, 40, 47, 55, 62, 70, 78, 86, 94, 99, 99, 99, 99, 99 ; move silently
        db 10, 15, 20, 25, 31, 37, 43, 49, 56, 63, 70, 77, 85, 93, 99, 99, 99 ; hide in shadows
        db 10, 10, 15, 15, 20, 20, 25, 25, 30, 30, 35, 35, 40, 40, 50, 50, 55 ; hear noise
        db 85, 86, 87, 88, 90, 92, 94, 96, 98, 99, 99, 99, 99, 99, 99, 99, 99 ; climb walls
        db 0, 0, 0, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 80 ; read languages
; Dark Sun's DEX adjustments, DEX 9-22, a row per DEX: pick, open, traps, move, hide (game.DEX_ADJUST)
dex_table:
        db -15, -10, -10, -20, -10
        db -10, -5, -10, -15, -5
        db -5, 0, -5, -10, 0
        db 0, 0, 0, -5, 0
        times 3 * 5 db 0
        db 0, 5, 0, 0, 0
        db 5, 10, 0, 5, 5
        db 10, 15, 5, 10, 10
        db 15, 20, 10, 15, 15
        db 20, 25, 12, 20, 17
        db 25, 27, 15, 25, 20
        db 27, 30, 17, 30, 22
section image
; STAB_FIRST (SL's, called from MISSILE_REAR: SI the attacker, DS the game's): with the rule, only a party
; member's first attack of a round is a backstab, as in AD&D. The game's own test (5D10Ch) lets two through
; and the round's count STAB_TIMES reads ([BP-16h] in the hit routine) leaves the off-hand swing out (two
; weapons: OFF_HAND), so a third attack could be multiplied after a first that missed. Each party
; member's attack keeps the game's clock (the dword through DS:9C0Ch's far pointer, SL's 9B72h: in a fight
; it moves a round at a time); a later attack at the same clock has its backstab taken back ([BP-21h]
; cleared, its 2 off THAC0 [BP-1Eh] given back); from behind stays. All registers kept.
GAME_CLOCK  equ 0x9C0C
stab_first:
        test word [cs:rules], RULE_THIEF_TABLE
        jz .ret
        cmp si, 3
        ja .ret
        push eax
        push bx
        push es
        les bx, [GAME_CLOCK]
        mov eax, [es:bx]
        mov bx, si
        shl bx, 2
        cmp eax, [cs:bx + stab_clock]
        mov [cs:bx + stab_clock], eax
        jne .done                       ; (the round's first)
        cmp byte [bp - 0x21], 0
        je .done
        mov byte [bp - 0x21], 0
        add word [bp - 0x1E], 2
.done:  pop es
        pop bx
        pop eax
.ret:   ret
stab_clock dd -1, -1, -1, -1    ; (each party member's last attack, by the game's clock)
thief_rear:
        test word [cs:rules], RULE_RESTRICT
        jz .ret
        cmp si, 3
        ja .ret
        cmp byte [bp - 0x21], 0
        je .ret
        push ax
        mov ax, si
        call fighter_creature
        jc .no
        call thief_heavy
        jnc .no
        mov byte [bp - 0x21], 0
        add word [bp - 0x1E], 2
        inc word [cs:restrict_count]
.no:    pop ax
.ret:   ret
cast_armour:
        mov ax, 1
        test word [cs:rules], RULE_RESTRICT
        jz .out
        cmp di, 3
        ja .out
        push bx
        push dx
        push es
        imul bx, di, CREATURE_SIZE
        les dx, [CREATURES_PTR]
        add bx, dx
        mov bx, [es:bx + 4]             ; (its sheet)
        imul bx, bx, CU_SHEET_SIZE
        les dx, [SHEETS_PTR]
        add bx, dx
        cmp byte [es:bx + SH_RACE], CU_HUMAN
        jne .multi
        call preserver_warrior
        jc .pres
        jmp .done
.multi: cmp byte [es:bx + SH_CLASSES + 1], 0     ; one class: none
        je .done
        cmp byte [es:bx + SH_CLASSES], PRESERVER_CLASS
        je .pres
        cmp byte [es:bx + SH_CLASSES + 1], PRESERVER_CLASS
        je .pres
        cmp byte [es:bx + SH_CLASSES + 2], PRESERVER_CLASS
        jne .done
.pres:  mov dx, di
        call own_light                  ; (Ar'Anda: only armour that isn't light keeps her from casting)
        call armour_worn
        mov byte [cs:aw_heavy], 0
        jnc .done
        xor ax, ax
        inc word [cs:restrict_count]
.done:  pop es
        pop dx
        pop bx
.out:   iret
; OWN_LIGHT: AW_HEAVY set for Ar'Anda, sheet ES:BX (an elf of the own party with no druid class:
; kits.own_light_cast), so ARMOUR_WORN counts only armour that isn't light. All kept.
OWN_ELF      equ 3
own_light:
        push ax
        call own_race_b
        cmp al, OWN_ELF
        jne .out
        mov al, 5
.druid: call own_has
        je .out
        inc al
        cmp al, 8
        jbe .druid
        mov byte [cs:aw_heavy], 1
.out:   pop ax
        ret
; PRESERVER_WARRIOR: carry set if the character (sheet ES:BX) has the preserver class and a warrior
; class among its classes (SL's CLASS_AND_WARRIOR with AL the preserver). All kept.
preserver_warrior:
        push ax
        push cx
        push si
        xor cx, cx                      ; CL the preserver found, CH a warrior
        xor si, si
.each:  mov al, [es:bx + si + SH_CLASSES]
        cmp al, PRESERVER_CLASS
        jne .war
        mov cl, 1
.war:   call warrior_al
        jnc .next
        mov ch, 1
.next:  inc si
        cmp si, 3
        jb .each
        and cl, ch
        cmp cl, 1                       ; (CF set if CL < 1)
        cmc
        pop si
        pop cx
        pop ax
        ret
restrict_count dw 0             ; (items refused, skills and backstabs taken: for a look in play)

; CLASS_FORBIDS: carry set if the classes of the character whose sheet is at ES:BX keep it from
; item type DX (SL's, restrict.py says why): a psionicist, a thief (light armour, but a multiclass
; one, or a human thief once a warrior, as its other class allows: CU_DUAL; a multiclass one its shields
; too), a preserver of that class alone (or a human once a warrior), a druid, a cleric. A human's first
; class alone holds it (the one it has now); another race's every class. DS the game's; all kept.
class_forbids:
        pusha
        push ds
        mov ax, dx
        imul ax, ax, CU_TYPE_SIZE
        lds si, [ITEM_TYPES_PTR]
        add si, ax
        mov al, [si + CU_FLAGS]         ; the flags: 1 melee, 2 missile, 4 shield, 10h thrown
        mov [cs:cu_flags], al
        mov al, [si + CU_MATERIAL]
        mov ah, al
        and al, 0x0F
        jnz .mat
        test ah, 0x40
        jz .mat
        mov al, NO_MATERIAL
.mat:   mov [cs:cu_mat], al
        push es                         ; armour (ARMOUR_TYPE): not a shield, bracers, a robe or a cloak
        push bx
        push ds
        pop es
        mov bx, si
        call armour_type
        pop bx
        pop es
        setc al
        mov [cs:cu_armour], al
        mov ax, [si + CU_CLASSES]       ; the classes but thief that may use it
        and ax, [es:bx + SH_CLASS_BITS]
        and ax, 0xFFFF - THIEF_BIT
        mov [cs:cu_others], ax
        pop ds
        mov byte [cs:cu_kind], 0xFF     ; a weapon's kind (0FFh none)
        test byte [cs:cu_flags], 3
        jz .kind
        cmp dx, KIND_TYPES
        jae .kind
        mov si, dx
        mov al, [cs:si + kind_of_type]
        dec al
        mov [cs:cu_kind], al
.kind:  call ranger_bow                 ; (a ranger's bow: its own, as the game has it)
        jnc .holds0
        mov byte [cs:cu_kind], 0xFF
.holds0:
        call dual_warrior
        mov cx, 3                       ; CL the classes that hold, CH more than one (not human)
        cmp byte [es:bx + SH_RACE], CU_HUMAN
        jne .multi
        mov cl, 1
        jmp .holds
.multi: cmp byte [es:bx + SH_CLASSES + 1], 0
        je .holds
        inc ch
.holds: xor di, di
.each:  mov al, [es:bx + di + SH_CLASSES]
        or al, al
        jz .next
        call class_forbids_one
        jc .out
.next:  inc di
        cmp di, cx                      ; (CH 1: DI never reaches it, and the third slot ends it)
        jae .out                        ; (CF clear)
        cmp di, 3
        jb .each
        clc
.out:   popa
        ret
; RANGER_BOW: carry set if CU_KIND is the bow and the character (sheet ES:BX) is a ranger, a
; multiclass one always, a human while a ranger or once its new class's level has passed its ranger
; level (SL's SPECIALIZED_BACK's bow; the sequel has no weapon specs). All kept.
ranger_bow:
        pusha
        cmp byte [cs:cu_kind], CU_BOW_KIND - 1
        jne .no
        xor si, si
.class: mov al, [es:bx + si + SH_CLASSES]
        cmp al, 13
        jb .next
        cmp al, 16
        ja .next
        cmp byte [es:bx + SH_RACE], CU_HUMAN
        jne .yes
        or si, si
        jz .yes
        mov al, [es:bx + si + SH_LEVELS]
        cmp al, [es:bx + SH_LEVELS]
        jb .yes
.next:  inc si
        cmp si, 3
        jb .class
.no:    popa
        clc
        ret
.yes:   popa
        stc
        ret
; CLASS_FORBIDS_ONE: carry set if class AL keeps the character (sheet ES:BX, CH 1 if multiclass)
; from the item CLASS_FORBIDS has described in CU_*.
class_forbids_one:
        cmp al, 12                      ; psionicist
        jne .thief
        call cu_heavy
        jc .ret
        call shield_not_leather
        jc .ret
        mov dl, [cs:cu_kind]
        cmp dl, 0xFF
        je .ok
        push cx
        push edx
        mov cl, dl
        mov edx, 1
        shl edx, cl
        test edx, PSI_KINDS
        pop edx
        pop cx
        jnz .ok
        stc
        ret
.thief: cmp al, THIEF_CLASS
        jne .pres
        call cu_heavy                   ; (a thief: light armour only, but a multiclass one, or a
        jnc .tshield                    ;   human once a warrior: as its other class allows, its
        or ch, ch                       ;   thief skills lost in it: THIEF_HEAVY)
        jnz .tshield
        cmp byte [cs:cu_dual], 0
        jne .ok
        stc
        ret
.tshield:
        or ch, ch                       ; (a multiclass one: a leather shield another class allows)
        jz .ok
        call shield_not_leather
        jc .ret
        test byte [cs:cu_flags], 4
        jz .ok
        cmp word [cs:cu_others], 0
        jne .ok
        stc
        ret
.pres:  cmp al, PRESERVER_CLASS
        jne .druid
        or ch, ch
        jnz .ok
        cmp byte [cs:cu_dual], 0        ; (a human once a warrior: as a multiclass one)
        jne .ok
        jmp .bare
.druid: cmp al, 5
        jb .cleric
        cmp al, 8
        ja .ok
.bare:  cmp byte [cs:cu_armour], 0      ; no armour, no shield
        jne .no
        test byte [cs:cu_flags], 4
        jz .ok
.no:    stc
        ret
.cleric:                                ; (1-4)
        cmp byte [cs:cu_kind], 0xFF
        je .ok
        push si
        xor si, si
.sphere:
        mov al, [es:bx + si + SH_CLASSES] ; a cleric's or ranger's sphere: its class less 1 (13 a ranger's), mod 4
        dec al
        cmp al, 4
        jb .is
        sub al, 12
        cmp al, 4
        jae .nexts
.is:    call sphere_allows
        jnc .yes
.nexts: inc si
        cmp si, 3
        jb .sphere
        call el_second                  ; (an Elementalist's second sphere's too: SL's)
        jz .none
        call sphere_allows
        jnc .yes
.none:  pop si
        stc
        ret
.yes:   pop si
.ok:    clc
.ret:   ret
; DUAL_WARRIOR: CU_DUAL 1 if the character (sheet ES:BX) is a human whose class now is thief or
; preserver and who was a fighter, gladiator or ranger before, or a thief who was a cleric before
; (restrict.dual_warrior), else 0. All registers kept.
dual_warrior:
        push ax
        push cx
        mov byte [cs:cu_dual], 0
        cmp byte [es:bx + SH_RACE], CU_HUMAN
        jne .out
        mov cl, [es:bx + SH_CLASSES]
        cmp cl, THIEF_CLASS
        je .was
        cmp cl, PRESERVER_CLASS
        jne .out
.was:   mov al, [es:bx + SH_CLASSES + 1]
        call .before
        jc .yes
        mov al, [es:bx + SH_CLASSES + 2]
        call .before
        jnc .out
.yes:   mov byte [cs:cu_dual], 1
.out:   pop cx
        pop ax
        ret
.before:                        ; (carry set: class AL a warrior, or a cleric for a thief, CL, now)
        call warrior_al
        jc .ret
        cmp cl, THIEF_CLASS
        jne .no
        cmp al, 1
        jb .no
        cmp al, 4
        ja .no
        stc
        ret
.no:    clc
.ret:   ret
; WARRIOR_AL: carry set if class AL is a fighter, gladiator or ranger. All registers kept.
warrior_al:
        cmp al, CU_FIGHTER
        je .yes
        cmp al, CU_GLADIATOR
        je .yes
        cmp al, 13
        jb .no
        cmp al, 16
        ja .no
.yes:   stc
        ret
.no:    clc
        ret
; ARMOUR_TYPE: carry set if the item type at ES:BX is armour (restrict.is_armour): +0Bh 80h, and not a
; shield (+0 4), nor of these the mod's types bring (OBJEX2.GFF's 102-145): bracers of defense (worn on
; the arms, +5 3, of no material: +4 40h), a robe (on the chest, +5 1, +4 40h, for preservers,
; psionicists and druids alone: +0Ch 190h) or a cloak of protection (+5 8, as a cloak). All kept.
CU_WORN     equ 0x05
CU_BRACERS_WORN equ 3
CU_ROBE_WORN equ 1
CU_CLOAK_WORN equ 8
CU_ROBE_CLASSES equ 0x0190
armour_type:
        push ax
        test byte [es:bx + CU_KIND_FLAGS], 0x80
        jz .no
        test byte [es:bx + CU_FLAGS], 4
        jnz .no
        mov al, [es:bx + CU_WORN]
        cmp al, CU_CLOAK_WORN
        je .no
        mov ah, [es:bx + CU_MATERIAL]
        cmp al, CU_BRACERS_WORN
        jne .robe
        test ah, 0x40
        jz .yes
        test ah, 0x0F
        jz .no
        jmp .yes
.robe:  cmp al, CU_ROBE_WORN
        jne .yes
        cmp ah, 0x40
        jne .yes
        cmp word [es:bx + CU_CLASSES], CU_ROBE_CLASSES
        je .no
.yes:   pop ax
        stc
        ret
.no:    pop ax
        clc
        ret
; CU_HEAVY: carry set for armour not light (not leather, and of a material)
cu_heavy:
        cmp byte [cs:cu_armour], 0
        je .light
        cmp byte [cs:cu_mat], LEATHER
        je .light
        cmp byte [cs:cu_mat], NO_MATERIAL
        je .light
        stc
        ret
.light: clc
        ret
; SHIELD_NOT_LEATHER: carry set for a shield of a material not leather
        SHARED_shield_not_leather
; SPHERE_ALLOWS: carry clear if sphere AL (0 air, 1 earth, 2 fire, 3 water) allows the weapon:
; air, missile and thrown weapons, daggers and the cahulaks; the others by material (SL's).
        SHARED_sphere_allows
cu_flags   db 0
cu_mat     db 0
cu_armour  db 0
cu_kind    db 0
cu_dual    db 0
cu_others  dw 0

; ---- KITS' GEAR: DSCLOG's KIT_FORBIDS and KIT_ALLOWS (kits.forbids, kits.allows; restrict.kit_forbids,
; restrict.kit_allows) in the sequel, from CU_SITE (site 19) as SL's PROBE_CAN_USE calls them. With the
; kits' rule (RULE_HI_KITS: KIT_AT finds none without it), each kit awake holds its character to its gear
; and lets it use its own; a kit asleep after a change of class, neither. The sequel's item type record
; (0Fh bytes: KG_* below) for SL's (14h: its +8 here +4, its +9 +5, its +0Fh +0Bh), the sheet's as
; CLASS_FORBIDS reads it. Its kinds are KIND_OF_TYPE's (the sequel's own weapons too: the cahulaks its
; type 24 and the mod's two, kind 12; an item past KIND_TYPES, or of no kind, has none: as the game has it).
; Not here: KF_SPEC (choosing a weapon spec: the sequel's weapon window doesn't ask the kits). The
; Spellarcher's arrows are ARROWS_FORBID's, called from CU_SITE before these checks.
KG_FLAGS     equ 0x00               ; (1 melee, 2 missile, 4 shield, 10h thrown)
KG_MATERIAL  equ 0x04               ; (the low nibble; 40h with 0 none: SL's +8)
KG_WORN      equ 0x05               ; (where it is worn: 8 a cloak; SL's +9)
KG_KINDS     equ 0x0B               ; (80h armour, 40h two-handed: SL's +0Fh)
KG_MELEE     equ 0x01
KG_MISSILE   equ 0x02
KG_SHIELD    equ 0x04
KG_THROWN    equ 0x10
KG_ARMOUR    equ 0x80
KG_TWO_HANDED equ 0x40
KG_CLOAK     equ 8
KG_CAHULAKS  equ 12                 ; (KIND_OF_TYPE's cahulaks: the kind + 1)
KG_BLUNT     equ 0xC112             ; bits by kind: club, mace, quarterstaff, sling, staff sling
KG_HALF_GIANT equ 5
EQUIP_OFF_HAND equ 14               ; (the equip routine's slot for the off hand: the worn slot 10 + 4)

; KIT_FORBIDS: carry set if the kit of the character whose sheet is at ES:BX keeps it from item type DX
; (DSCLOG's): a Ravager a shield, a missile or thrown weapon, and armour that isn't light; a Twin-blade a
; shield, and a two-handed weapon (but a half-giant's, with RULE_HALF_GIANT; the cahulaks its own); a
; Brute a one-handed melee weapon (the cahulaks too), and a shield (but a half-giant's, with the rule); a
; Stalker armour that isn't light; an Assassin, Shinobi, Shadowblade or Poisoner armour that isn't light,
; a Spellarcher any armour, helm or shield (KIT_LIGHT); a Grove Warden or a Seeker a weapon its druid's or
; ranger's sphere doesn't allow (SPHERE_ALLOWS, the bow too); a Lifebinder a weapon of a kind not blunt; a
; Shinobi a shield, and a weapon not of its kinds; a Battle Dancer a shield, and a weapon not of its kinds;
; a Shadowblade, Ghetto Fighter or Rescuer a shield. A weapon of a kind it specialized in (its specs
; counting: SPECS_AWAKE) none of these but KIT_LIGHT's. To the off hand (KF_OFF_HAND): nothing for a
; Battle Mage, no weapon for a Healer. DS the game's; all registers kept.
kit_forbids:
        push ax
        push cx
        push di
        call kit_place          ; (each of its kits awake: KIT_AT, KIT_AWAKE)
        jc .ok
.place: call kit_at
        jz .next
        call kit_awake
        jc .next                ; (a kit asleep: its limits too)
        call kit_light
        jc .out
        mov [cs:kit_where], di
        call kit_forbids_one
        jc .out
.next:  dec di
        jns .place
.ok:    clc
.out:   pop di
        pop cx
        pop ax
        ret

; KG_TYPE: ES:BX the record of item type DX (ITEM_TYPES_PTR's). Others kept.
kg_type:
        push ax
        imul ax, dx, CU_TYPE_SIZE
        les bx, [ITEM_TYPES_PTR]
        add bx, ax
        pop ax
        ret

; KG_LIGHT: carry clear if the item type at ES:BX is light (KIT_FORBIDS' "light"): not armour, a
; shield, or of leather or no material. All kept.
kg_light:
        push ax
        test byte [es:bx + KG_KINDS], KG_ARMOUR
        jz .yes
        test byte [es:bx + KG_FLAGS], KG_SHIELD
        jnz .yes
        mov al, [es:bx + KG_MATERIAL]
        and al, 0x4F
        cmp al, LEATHER
        je .yes
        cmp al, 0x40
        je .yes
        pop ax
        stc
        ret
.yes:   pop ax
        clc
        ret

; KG_KIND: AL the kind + 1 of item type DX (KIND_OF_TYPE's; 0 none or past it). Others kept.
kg_kind:
        xor al, al
        cmp dx, KIND_TYPES
        jae .ret
        push si
        mov si, dx
        mov al, [cs:si + kind_of_type]
        pop si
.ret:   ret

; KIT_LIGHT: carry set if kit AL keeps its character to light armour (an Assassin, Shinobi, Shadowblade
; or Poisoner: kits.LIGHT_KITS) and item type DX is armour that isn't light; or, a Spellarcher
; (kits.BARE_KITS), if DX is armour, a helm or a shield at all (bracers, robes and a cloak of
; protection aren't: ARMOUR_TYPE's). All registers kept.
kit_light:
        push ax
        push bx
        push si
        push es
        call kg_type
        cmp al, KIT_SPELLARCHER
        je .bare
        mov si, kg_light_kits
.kit:   cmp byte [cs:si], 0
        je .no
        cmp [cs:si], al
        je .type
        inc si
        jmp .kit
.type:  test byte [es:bx + KG_KINDS], KG_ARMOUR
        jz .no
        call kg_light
        jmp .out
.bare:  test byte [es:bx + KG_KINDS], KG_ARMOUR
        jz .no                  ; (not armour, a helm or a shield)
        test byte [es:bx + KG_FLAGS], KG_SHIELD
        jnz .yes
        call armour_type        ; (not bracers, a robe or a cloak: its CF)
        jmp .out
.yes:   stc
        jmp .out
.no:    clc
.out:   pop es
        pop si
        pop bx
        pop ax
        ret
kg_light_kits db KIT_ASSASSIN, KIT_SHINOBI, KIT_SHADOWBLADE, KIT_POISONER, 0

; KIT_FORBIDS_ONE: carry set if kit AL (its class's place KIT_WHERE) of sheet ES:BX keeps it from item
; type DX (KIT_FORBIDS' rules but KIT_LIGHT's). All registers kept.
kit_forbids_one:
        push ax
        push bx
        push cx
        push si
        push es
        mov cl, al              ; CL the kit, CH 1 for a half-giant with RULE_HALF_GIANT
        xor ch, ch
        cmp byte [es:bx + SH_RACE], KG_HALF_GIANT
        jne .sphere0
        test word [cs:rules], RULE_HALF_GIANT
        jz .sphere0
        call kg_kind
        cmp al, KG_CAHULAKS     ; (a blade in each hand: both hands, a half-giant's too)
        je .sphere0
        inc ch
.sphere0:
        call kit_class_of_sheet ; (the class's sphere, a Seeker's ranger's or a Grove Warden's druid's:
        dec al                  ;   its class less 1, mod 4)
        and al, 3
        mov [cs:kf_sphere], al
        mov byte [cs:kf_chosen], 0      ; (a weapon of a kind it specialized in: the kit keeps it from
        call specs_awake                ;   none, but for the off hand's rules)
        jc .forbids
        call kg_kind
        or al, al
        jz .forbids
        call spec_find
        jne .forbids
        mov byte [cs:kf_chosen], 1
.forbids:
        call kg_type
        mov al, [es:bx + KG_FLAGS]      ; AL the flags, AH the kind flags
        mov ah, [es:bx + KG_KINDS]
        cmp byte [cs:kf_off_hand], 0    ; the off hand: nothing for a Battle Mage, no weapon for a Healer
        je .ravager
        cmp cl, KIT_BATTLE_MAGE
        je .no
        cmp cl, KIT_HEALER
        jne .ravager
        test al, KG_MELEE | KG_MISSILE | KG_THROWN
        jnz .no
.ravager:
        cmp byte [cs:kf_chosen], 0
        jne .ok
        cmp cl, KIT_SHADOWBLADE ; a Shadowblade, Ghetto Fighter or Rescuer: no shield
        je .unshielded
        cmp cl, KIT_RESCUER
        je .unshielded
        cmp cl, KIT_GHETTO
        jne .ravager_kit
.unshielded:
        test al, KG_SHIELD
        jnz .no
        jmp .ok
.ravager_kit:
        cmp cl, KIT_RAVAGER     ; a Ravager: no shield, no missile or thrown weapon, light armour only
        jne .twin
        test al, KG_SHIELD | KG_MISSILE | KG_THROWN
        jnz .no
        jmp .light
.twin:  cmp cl, KIT_TWIN_BLADE
        jne .brute
        test al, KG_SHIELD
        jnz .no
        test al, KG_MELEE | KG_MISSILE
        jz .ok
        call .cahulaks          ; (the cahulaks: a blade in each hand, a Twin-blade's own)
        je .ok
        test ah, KG_TWO_HANDED
        jz .ok
        or ch, ch
        jnz .ok
        jmp .no
.brute: cmp cl, KIT_BRUTE
        jne .stalker
        test al, KG_SHIELD
        jz .melee
        or ch, ch
        jnz .ok
        jmp .no
.melee: test al, KG_MELEE       ; (a missile weapon: only a spec chosen is kept from it, KF_SPEC's)
        jz .ok
        call .cahulaks          ; (the cahulaks: two weapons, not one two-handed one)
        je .no
        test ah, KG_TWO_HANDED
        jz .no
        jmp .ok
.stalker:
        cmp cl, KIT_STALKER
        jne .warden
.light: call kg_light
        jc .no
        jmp .ok
.warden:
        cmp cl, KIT_GROVE_WARDEN        ; a Grove Warden: its druid sphere's weapons, as a cleric's
        je .sphere
        cmp cl, KIT_SEEKER      ; a Seeker: its ranger sphere's weapons (SPHERE_ALLOWS), the bow too
        jne .blunt
.sphere:
        test al, KG_MELEE | KG_MISSILE
        jz .ok
        push ax
        call kg_kind
        mov ah, al
        pop si                  ; (SI the flags in its low byte)
        sub ah, 1
        jc .ok                  ; (no kind: as the game has it)
        mov [cs:cu_kind], ah
        mov ax, si
        mov [cs:cu_flags], al
        mov al, [es:bx + KG_MATERIAL]   ; (the material, as CLASS_FORBIDS keeps it)
        mov ah, al
        and al, 0x0F
        jnz .mat
        test ah, 0x40
        jz .mat
        mov al, NO_MATERIAL
.mat:   mov [cs:cu_mat], al
        mov al, [cs:kf_sphere]
        call sphere_allows
        jc .no
        jmp .ok
.blunt: mov si, kg_blunt
        cmp cl, KIT_LIFEBINDER
        je .kind
        mov si, kg_dancer       ; a Battle Dancer: no shield, the long sword and the bow only
        cmp cl, KIT_BATTLE_DANCER
        jne .shinobi
        test al, KG_SHIELD
        jnz .no
        jmp .kind
.shinobi:
        cmp cl, KIT_SHINOBI
        jne .ok
        test al, KG_SHIELD      ; a Shinobi: no shield, light armour, its own weapons
        jnz .no
        test ah, KG_ARMOUR
        jz .weapon
        jmp .light
.weapon:
        mov si, kg_shinobi
.kind:  call kg_kind            ; a weapon's kind in the mask at CS:SI (no kind: as the game has it)
        movzx ax, al
        dec ax
        js .ok
        bt word [cs:si], ax
        jc .ok
.no:    pop es
        pop si
        pop cx
        pop bx
        pop ax
        stc
        ret
.ok:    pop es
        pop si
        pop cx
        pop bx
        pop ax
        clc
        ret
.cahulaks:                      ; (ZF set: item type DX is the cahulaks)
        push ax
        call kg_kind
        cmp al, KG_CAHULAKS
        pop ax
        ret

; KIT_ALLOWS: carry set if the kit of the character whose sheet is at ES:BX lets it use item type DX
; whatever its classes' lists and restrictions (DSCLOG's): a Battle Mage the weapons of its chosen
; weapon spec (the first) and light armour (leather, or of no material; not a shield); a Battle Dancer
; long swords and bows, whatever its cleric's sphere. DS the game's; all registers kept.
kit_allows:
        push ax
        push bx
        push cx
        push si
        push es
        call kg_kind
        mov ah, al              ; AH the kind + 1
        call kit_is_b
        db KIT_BATTLE_DANCER
        jne .mage
        movzx cx, ah
        jcxz .no                ; (not a weapon of a kind)
        dec cx
        mov si, [cs:kg_dancer]
        shr si, cl
        test si, 1
        jnz .yes
        jmp .no
.mage:  call kit_is_b
        db KIT_BATTLE_MAGE
        jne .no
        push ax
        xor si, si
        call spec_get
        mov cl, al              ; CL the chosen kind + 1
        pop ax
        call kg_type
        test byte [es:bx + KG_KINDS], KG_ARMOUR
        jz .weapon
        test byte [es:bx + KG_FLAGS], KG_SHIELD
        jnz .no
        call kg_light
        jnc .yes
        jmp .no
.weapon:
        or ah, ah
        jz .no
        cmp ah, cl
        jne .no
.yes:   pop es
        pop si
        pop cx
        pop bx
        pop ax
        stc
        ret
.no:    pop es
        pop si
        pop cx
        pop bx
        pop ax
        clc
        ret

; SPECS_AWAKE: CF clear if the weapon specs of the character (sheet ES:BX) count (DSCLOG's): one class,
; or not a human; a human's warrior class (fighter, gladiator, ranger) now, or before and passed by the
; class it has now; a Battle Mage's kit awake. Set while the class or kit that gave them sleeps. All kept.
specs_awake:
        pusha
        cmp byte [es:bx + SH_CLASSES + 1], 0
        je .yes
        cmp byte [es:bx + SH_RACE], CU_HUMAN
        jne .yes
        xor si, si
.class: mov al, [es:bx + si + SH_CLASSES]
        call warrior_al
        jnc .next
        or si, si
        jz .yes
        mov al, [es:bx + si + SH_LEVELS]
        cmp al, [es:bx + SH_LEVELS]
        jb .yes
.next:  inc si
        cmp si, 3
        jb .class
        call kit_is_b
        db KIT_BATTLE_MAGE
        je .yes
        popa
        stc
        ret
.yes:   popa
        clc
        ret

; SPEC_FIND: ZF set when kind + 1 AL is in one of the specs (SPEC_GET's slots) of sheet ES:BX. All kept.
spec_find:
        push ax
        push cx
        push si
        mov cl, al
        xor si, si
.each:  call spec_get
        cmp al, cl
        je .out
        inc si
        cmp si, SPEC_COUNT
        jb .each
        or si, si               ; (ZF clear)
.out:   pop si
        pop cx
        pop ax
        ret

; KIT_CLASS_OF_SHEET: AL the class (1-17) of the kit KIT_IS last found (KIT_WHERE) on sheet ES:BX.
kit_class_of_sheet:
        push di
        mov di, [cs:kit_where]
        mov al, [es:bx + di + SH_CLASSES]
        pop di
        ret

; EL_SECOND: AL the second sphere (0-3) of the Elementalist (awake) whose sheet is at ES:BX, ZF clear; ZF
; set if none (DSCLOG's: its weapons are allowed as well as its own sphere's, CLASS_FORBIDS_ONE). Others
; kept.
el_second:
        push cx
        mov cl, [es:bx + SPHERE2]
        and cl, SPHERE2_MASK
        call kit_is_b
        db KIT_ELEMENTALIST
        jne .none
        mov al, cl
        dec al
        cmp al, 3
        ja .none
        or cl, 1                ; (ZF clear)
        pop cx
        ret
.none:  cmp al, al
        pop cx
        ret

kg_blunt   dd KG_BLUNT          ; (dwords: KIT_FORBIDS' BT reads 32 bits, the kinds being 22)
kg_dancer  dd 0x2001            ; bits by kind: the long sword, the bow (a Battle Dancer's)
kg_shinobi dd 0x20F10C          ; bits by kind: dagger, short sword, quarterstaff, chatkcha, bow, sling,
                                ;   staff sling, darts
kf_off_hand db 0                ; (KIT_FORBIDS: the item going to the off hand)
kf_sphere  db 0                 ; (a ranger's or druid's sphere, 0 air to 3 water)
kf_chosen  db 0                 ; (a weapon of a kind it specialized in)
kit_refused dw 0                ; (items a kit kept from its character, for a look in play)
kit_allowed dw 0                ; (items a kit let its character use that the game's lists didn't)
; THIEF_HEAVY: carry set if creature AX (DS the game's) has a thief class and wears armour that isn't
; light (HEAVY_WORN): a multiclass thief, or a human thief once a warrior, may wear it, but loses its
; thief skills and backstab in it (restrict.thief_heavy). All registers kept.
thief_heavy:
        pusha
        push es
        mov dx, ax
        imul bx, ax, CREATURE_SIZE
        les si, [CREATURES_PTR]
        mov ax, [es:bx + si + 4]        ; (its sheet's number)
        imul bx, ax, CU_SHEET_SIZE
        les si, [SHEETS_PTR]
        add bx, si
        mov cx, 3
        xor si, si
.class: cmp byte [es:bx + si + SH_CLASSES], THIEF_CLASS
        je .thief
        inc si
        loop .class
        pop es
        popa
        clc
        ret
.thief: mov byte [cs:aw_heavy], 1
        call armour_worn
        mov byte [cs:aw_heavy], 0
        pop es
        popa
        ret
; ARMOUR_WORN: carry set if creature DX (DS the game's) wears armour, a helm too: an item of a type
; marked armour (+0Bh 80h), not a shield, on its arms, legs, head or chest, in any of its item lists
; (as MELEE_IN reads them); with AW_HEAVY only armour that isn't light (not leather, and of a material).
; All registers kept.
armour_worn:
        pusha
        push es
        imul bx, dx, CREATURE_SIZE
        mov [cs:mi_creature], bx
        mov cx, 8
.list:  les bx, [CREATURES_PTR]
        add bx, [cs:mi_creature]
        add bx, cx
        mov dx, [es:bx]
        cmp dx, NO_ITEM
        jae .next
        imul bx, dx, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        cmp byte [es:bx + FIGHTERS_OFF], 1
        jne .next                       ; not an item
        mov dx, [es:bx + FIGHTERS_OFF + 1]
        mov si, 100                     ; (no more than 100 in a list)
.item:  cmp dx, NO_ITEM
        jae .next
        dec si
        js .next
        imul bx, dx, ITEM_SIZE
        les di, [ITEMS_PTR]
        add bx, di
        mov dx, [es:bx + ITEM_NEXT]
        mov al, [es:bx + ITEM_SLOT]
        cmp al, ARM_SLOT
        je .slot
        cmp al, LEG_SLOT
        je .slot
        cmp al, HEAD_SLOT
        je .slot
        cmp al, CHEST_SLOT
        jne .item
.slot:  imul bx, [es:bx + ITEM_TYPE], CU_TYPE_SIZE
        les di, [ITEM_TYPES_PTR]
        add bx, di
        call armour_type
        jnc .item
        cmp byte [cs:aw_heavy], 0
        je .yes
        mov al, [es:bx + CU_MATERIAL]   ; (light: leather, or of no material: SL's)
        and al, 0x4F
        cmp al, LEATHER
        je .item
        cmp al, 0x40
        je .item
.yes:   pop es
        popa
        stc
        ret
.next:  add cx, 2
        cmp cx, 0x0E
        jb .list
        pop es
        popa
        clc
        ret
aw_heavy db 0

; ITEM SAVES: DSCLOG's RULE_ITEM_SAVES (always on), the sequel's routines SL's. Acid and a corroding
; touch after a failed save can destroy an item (DSUN.EXE 7CEC0h, the first melee weapon held, SL's
; 7AA5Ah; 7D02Ah, the first worn arm, leg or chest piece that fails, SL's 7ABC4h): a weapon on a d20
; under 8 less its plus (+16h); armour with no magical power (the word at +10h, ITEM_SPELL) at once,
; without a roll, else on a d20 under 10 less that word. With the rule the item needs the lower (the
; easier) of the game's number and AD&D's save against acid for its material (the DMG's: wood 8,
; bone 11, metal 13, leather 10, cloth 12; glass's 5 for stone and obsidian), less its plus, and 1 less
; again for a magical power; armour always rolls. Each check is recorded as DSCLOG's (kind KIND_ITEM:
; the d20 in the low byte, the number needed in the high, 0 for none rolled; EXTRA the item, 8000h
; for armour).
RULE_ITEM_SAVES equ 2048
KIND_ITEM     equ 4
ITEM_ARMOUR   equ 0x8000
MATERIAL_CLOTH equ 6
MATERIAL_METAL equ 4
; ITEM_WEAPON (site 22, "item_weapon"): "mov dx,8 / sub dx,[bp-2]" (7CF22h; 6 bytes), AX the d20,
; [BP-2] the weapon's plus, SI its entry in the list at BP-324h (the item at BP-320h + SI*0Ah). DX the
; number needed (a roll under it corrodes).
item_weapon:
        mov dx, 8
        sub dx, [bp - 2]
        test word [cs:rules], RULE_ITEM_SAVES
        jz .r
        push si
        push ax
        push bx
        push cx
        push di
        mov di, si
        imul di, di, 0x0A
        mov bx, [bp + di - 0x320]
        call adnd_needed
        cmp cx, dx
        jge .log
        mov dx, cx
.log:   xor cx, cx                      ; (a weapon)
        jmp item_record
.r:     iret
; ITEM_SKIP (site 23, "item_skip"): "cmp word [bp-2],0" (7D0AAh; 4 bytes) before the game's "jz
; <destroyed>", [BP-2] the armour's magical power. With the rule ZF clear: it rolls; else the game's
; compare.
item_skip:
        push ax
        mov ax, [bp - 2]
        push bp
        mov bp, sp                      ; ([BP+8]: the flags IRET takes back)
        or word [bp + 8], 0x40
        test word [cs:rules], RULE_ITEM_SAVES
        jnz .roll
        or ax, ax
        jz .out
.roll:  and word [bp + 8], ~0x40
.out:   pop bp
        pop ax
        iret
; ITEM_ARMOUR (site 24, "item_armour"): "mov dx,0Ah / sub dx,[bp-2]" (7D0BEh; 6 bytes), AX the d20,
; [BP-2] the armour's magical power, SI its entry in the list at BP-322h (the item at BP-31Eh +
; SI*0Ah). DX the number needed.
item_armour:
        mov dx, 10
        sub dx, [bp - 2]
        test word [cs:rules], RULE_ITEM_SAVES
        jz .r
        push si
        push ax
        push bx
        push cx
        push di
        cmp word [bp - 2], 0
        jne .game
        mov dx, 21                      ; (no power: the game's, destroyed whatever the roll)
.game:  mov di, si
        imul di, di, 0x0A
        mov bx, [bp + di - 0x31E]
        call adnd_needed
        cmp cx, dx
        jge .log
        mov dx, cx
.log:   mov cx, ITEM_ARMOUR
        jmp item_record
.r:     iret
; ITEM_RECORD: (jumped to with SI, AX, BX, CX, DI pushed, in that order, on the INT's frame) records
; the check: AL the d20, DL the number needed, BX the item, CX ITEM_ARMOUR or 0; then IRETs with
; those registers back and DX as given.
item_record:
        or cx, bx
        mov [cs:extra], cx
        mov ah, dl
        mov si, sp
        add si, 4                       ; (SS:SI+6: the INT's return address)
        mov word [cs:kind], KIND_ITEM
        call record
        inc word [cs:item_count]
        pop di
        pop cx
        pop bx
        pop ax
        pop si
        iret
item_count dw 0                         ; (the checks made, for a look in play)
; ADND_NEEDED: CX = AD&D's save against acid for item BX (DS the game's): its material's number, less
; its plus, less 1 for a magical power. Keeps every other register.
adnd_needed:
        push ax
        push bx
        push di
        push es
        imul di, bx, ITEM_SIZE
        les bx, [ITEMS_PTR]
        add bx, di
        mov al, [es:bx + ITEM_PLUS]
        cbw
        mov cx, ax
        cmp word [es:bx + ITEM_SPELL], 0
        je .type
        inc cx                          ; a magical power: one plus more
.type:  imul di, [es:bx + ITEM_TYPE], CU_TYPE_SIZE
        les bx, [ITEM_TYPES_PTR]
        add bx, di
        mov al, [es:bx + CU_MATERIAL]   ; (40h with 0: none, cloth)
        mov ah, al
        and al, 0x0F
        test ah, 0x40
        jz .known
        or al, al
        jnz .known
        mov al, MATERIAL_CLOTH
.known: cmp al, MATERIAL_CLOTH
        jbe .look
        mov al, MATERIAL_METAL          ; (no other is used)
.look:  xor ah, ah
        mov bx, ax
        mov al, [cs:acid_saves + bx]
        sub ax, cx
        mov cx, ax
        pop es
        pop di
        pop bx
        pop ax
        ret
acid_saves db 8, 11, 5, 5, 13, 10, 12   ; wood, bone, stone, obsidian, metal, leather; cloth

; MULTICLASS HIT POINTS: DSCLOG's CON_SHARE (RULE_MULTI_HP, always on), the sequel's routines SL's: the
; most hit points (95193h, SL's 874B0h: the sheet's total of rolled dice, +0Ah, scaled by the levels now,
; +1Eh, over the levels before any were lost, +39h, divided by the classes, 9521Ah, plus CON's bonus,
; 95261h) and its reverse (954A5h, SL's 877BEh: the most, +8, less CON's bonus, times the classes).
; MC_CON (site 25, "mc_con"): "add di,ax / mov ax,di" (95208h; 4 bytes), AX the game's CON hit points,
; DI the total shared, SI the sheet's number. MC_UNCON (site 26, "mc_uncon"): "mov dx,[es:bx+8] / sub
; dx,ax" (954BDh; 6 bytes), ES:BX the sheet, AX the game's CON hit points, SI the number. Each puts in
; CON_SHARE's.
RULE_MULTI_HP equ 16384
LEVEL_HP_FROM_DS equ 0x47E0 - 0x45BE    ; the game's hit point table (SL's): +group x 4 (die, its last
LEVEL_HP_CON  equ 0x52                  ;   level, then a fixed gain), +10h + class: its group; +52h +
WARRIOR_GROUP equ 1                     ;   CON a warrior's bonus a level
mc_con:
        call con_share
        add di, ax
        mov ax, di
        iret
mc_uncon:
        mov dx, [es:bx + 8]
        call con_share
        sub dx, ax
        iret
; CON_SHARE: for a character of more than one class (MC_CLASSES; SI the sheet's and creature's number)
; with the rule, CON's hit points as Demihuman Deities (TSR 1998) has a multiclassed character's: each
; hit die so far with CON's bonus on it, all in the total, the total divided by the classes. The bonus
; is a warrior's (LEVEL_HP_CON + CON, the creature's +1Bh) on every die if any class is a warrior's,
; else at most +2; the dice, each class's levels up to its group's last that rolls one. AX (the game's
; own) becomes (total + bonus x dice) / classes less total / classes, the total as the game scales it
; for lost levels. Others kept.
con_share:
        test word [cs:rules], RULE_MULTI_HP
        jz .ret
        push bx
        push cx
        push dx
        push si
        push di
        push bp
        push es
        push fs
        push ax                 ; (the game's: one class keeps it)
        les bx, [CREATURES_PTR]
        imul ax, si, CREATURE_SIZE
        add bx, ax
        mov al, [es:bx + 0x1B]  ; CON
        mov [cs:mc_con_score], al
        les bx, [SHEETS_PTR]
        imul ax, si, SHEET_SIZE
        add bx, ax
        call mc_classes
        cmp ax, 1
        jbe .game
        mov bp, ax              ; BP the classes
        mov si, bx              ; ES:SI the sheet
        mov ax, ds
        sub ax, LEVEL_HP_FROM_DS
        mov fs, ax
        xor cx, cx              ; (the levels, and before any were lost)
        xor di, di
        xor bx, bx
.sum:   movzx ax, byte [es:si + bx + 0x1E]
        add cx, ax
        movzx ax, byte [es:si + bx + 0x39]
        add di, ax
        inc bx
        cmp bx, 3
        jb .sum
        mov ax, [es:si + 0x0A]
        or di, di
        jz .total
        mul cx                  ; (as the game: unsigned, its low word)
        xor dx, dx
        div di
.total: mov [cs:mc_total], ax
        xor cx, cx              ; CX the dice, DL 1 for a warrior's class
        xor dx, dx
        xor di, di
.class: movzx bx, byte [es:si + 0x1B]
        or bx, bx
        jz .next
        cmp bx, 32
        jae .next
        movzx bx, byte [fs:bx + 0x10]
        cmp bx, 4
        jae .next
        cmp bx, WARRIOR_GROUP
        jne .dice
        mov dl, 1
.dice:  shl bx, 2
        mov al, [fs:bx + 1]
        cmp al, [es:si + 0x1E]
        jbe .count
        mov al, [es:si + 0x1E]
.count: movzx ax, al
        add cx, ax
.next:  inc si                  ; (the next class)
        inc di
        cmp di, 3
        jb .class
        movzx bx, byte [cs:mc_con_score]
        cmp bx, 25
        jbe .con
        mov bx, 25
.con:   movsx ax, byte [fs:bx + LEVEL_HP_CON]
        or dl, dl
        jnz .bonus
        cmp ax, 2
        jle .bonus
        mov ax, 2
.bonus: imul cx                 ; (the bonus on every die)
        add ax, [cs:mc_total]
        cwd
        idiv bp
        mov cx, ax
        mov ax, [cs:mc_total]
        xor dx, dx
        div bp
        sub cx, ax
        mov ax, cx
        add sp, 2
        inc word [cs:mc_count]
        jmp .out
.game:  pop ax
.out:   pop fs
        pop es
        pop bp
        pop di
        pop si
        pop dx
        pop cx
        pop bx
.ret:   ret
mc_total dw 0
mc_count dw 0                           ; (the hit points shared so, for a look in play)
mc_con_score db 0
; MC_CLASSES: AX the classes the sheet at ES:BX shares its hit points between (the sequel's 9521Ah): 1
; for a human (+12h 1, who dual-classes), else its classes (+1Bh-1Dh not 0), at least 1. Others kept.
mc_classes:
        mov ax, 1
        cmp byte [es:bx + 0x12], 1
        je .ret
        xor ax, ax
        cmp byte [es:bx + 0x1B], 0
        je .two
        inc ax
.two:   cmp byte [es:bx + 0x1C], 0
        je .three
        inc ax
.three: cmp byte [es:bx + 0x1D], 0
        je .least
        inc ax
.least: or ax, ax
        jnz .ret
        inc ax
.ret:   ret

; SCORES AND HIT POINTS AS ROLLED: DSCLOG's RL_* (RULE_HI_ROLLED, the second rules word's 32:
; game.RULE_ROLLED), the sequel's creation screen SL's (its code 7D89h on, the data 6C0h back): a hit
; point click does nothing, and a score is raised only while the six add up to no more than the die
; gave (RL_POOL), lowering one freeing points for another; under CHR "SUM:100/102", the six's total and
; the die's; a click on CON moves the hit points as far as the most they may be (CON's bonus a level).
; The creature being made is DS:142Dh (scores from +19h), its sheet DS:1429h (hit points +8).
RULE_HI_ROLLED equ 32
RL_HP_MAX   equ 0x42D6              ; DS: the most hit points the classes could roll (SL's 4996h)
RL_BOX      equ 0x11F4              ; DS: the scores' box (x1, y1, x2, y2; SL's F62h)
RL_LABEL_X  equ 23                  ; "SUM:" this far left of the scores' x
RL_ROW_Y    equ 6 * 7 - 2           ; the line under CHR: 7 apart, from 2 above the box's top
RL_SHEET    equ 0x1429              ; DS: the sheet being made (SL's 119Ch)
RL_SCORES   equ 0x19                ; the creature's STR, then DEX ... CHA
; RL_TOTAL: DX the six scores of the creature being made added up. DS the game's; others kept.
rl_total:
        push es
        push ax
        push bx
        push cx
        les bx, [CR_CREATURE]
        xor ax, ax
        xor dx, dx
        mov cx, 6
.add:   mov al, [es:bx + RL_SCORES]
        add dx, ax
        inc bx
        loop .add
        pop cx
        pop bx
        pop ax
        pop es
        ret
; RL_SCORE (site 27, "rl_score"): "mov al,[bp-2]" (6D1DDh, SL's 655C6h), where a click sets a score
; (ES:BX the creature plus the score's number, [BP-2] the value the click gives). A raise is kept to
; the points to spare.
rl_score:
        push word [RL_HP_MAX]   ; (the most hit points before the click, for RL_CON)
        pop word [cs:rl_old_max]
        mov al, [bp - 2]
        test word [cs:rules_hi], RULE_HI_ROLLED
        jz .out
        cmp al, [es:bx + RL_SCORES]
        jbe .out                ; lowered: always
        push cx
        push dx
        mov cx, [cs:rl_pool]
        jcxz .done              ; (no roll seen)
        call rl_total
        sub cx, dx              ; the points to spare
        jg .some
        mov al, [es:bx + RL_SCORES] ; none: as it was
        inc word [cs:rl_count]
        jmp .done
.some:  add cl, [es:bx + RL_SCORES] ; the most it may be
        cmp al, cl
        jbe .done
        mov al, cl
        inc word [cs:rl_count]
.done:  pop dx
        pop cx
.out:   iret
; RL_HP (site 28, "rl_hp"): "add ax,[bp-2]" (6B7D2h, SL's 63A49h), a click's 1 or -1 on the hit
; points: with the rule nothing added (the hit points as rolled).
rl_hp:
        test word [cs:rules_hi], RULE_HI_ROLLED
        jnz .out
        add ax, [bp - 2]
.out:   iret
; RL_ROLL (site 29, "rl_roll_4", "rl_roll_6", "rl_roll_7"): "mov es:[bx+19h],al" in the die's three
; loops (6D55Ah, 6D593h, 6D5CCh; SL's 65944h...), SI the score, the byte [BP+6] 1 for a roll, 0 for
; the scores kept (raised to a new class's least): after CHR the six's total is the die's (a roll),
; or no less.
rl_roll:
        mov [es:bx + RL_SCORES], al
        cmp si, 5
        jne .out
        push dx
        call rl_total
        cmp byte [bp + 6], 0
        jne .set
        cmp dx, [cs:rl_pool]
        jbe .done
.set:   mov [cs:rl_pool], dx
.done:  pop dx
.out:   iret
; RL_CON (site 30, "rl_con"): "les bx,[1429h]" (6B6CFh, SL's 63946h) after a click on CON has had the
; game work out the hit points' least and most again: with the rule the sheet's hit points (+8) move
; as far as the most did (RL_SCORE kept it before the click); the game then keeps them in range.
rl_con:
        les bx, [RL_SHEET]
        test word [cs:rules_hi], RULE_HI_ROLLED
        jz .out
        push ax
        mov ax, [RL_HP_MAX]
        sub ax, [cs:rl_old_max]
        add [es:bx + 8], ax
        pop ax
.out:   iret
; RL_SUM (site 31, "rl_sum"): "add sp,4" (6CD98h, SL's 65185h) in the scores' redraw (6CD7Bh), after
; the game has put back what was under them (its box, RL_BOX, made a line taller and wider by
; ravager.py's "rl_sum_box"): with the rule and a roll seen, "SUM:" and the totals, the six's and the
; die's, in the game's lettering.
rl_sum:
        pop word [cs:rl_ip]
        pop word [cs:rl_cs]
        pop word [cs:rl_fl]
        add sp, 4               ; the replaced instruction
        test word [cs:rules_hi], RULE_HI_ROLLED
        jz .back
        cmp word [cs:rl_pool], 0
        je .back
        sti
        pushad
        push es
        mov ax, ds
        add ax, USE_TEXT_SEG
        mov [cs:c_draw + 2], ax
        mov word [cs:c_draw], USE_TEXT_OFF
        mov eax, [WIN_SHOWN]    ; the screen's window
        mov [cs:c_winptr], eax
        mov dx, [RL_BOX + 2]
        add dx, RL_ROW_Y
        mov ax, [RL_BOX]
        push dx
        push ax
        push cs
        push word rl_text
        push dx
        sub ax, RL_LABEL_X
        push ax
        push cs
        push word rl_label
        call c_draw_line
        call rl_total
        mov al, dl
        mov di, rl_text
        call c_itoa
        mov byte [cs:di], '/'
        inc di
        mov al, [cs:rl_pool]
        call c_itoa
        call c_draw_line
        inc word [cs:rl_drawn]
        pop es
        popad
.back:  push word [cs:rl_fl]
        push word [cs:rl_cs]
        push word [cs:rl_ip]
        iret
rl_old_max dw 0                 ; (RL_HP_MAX before a score's click)
rl_pool  dw 0                   ; the die's total, the most the six may add up to (0: none seen)
rl_count dw 0                   ; (raises cut, for a look in play)
rl_drawn dw 0                   ; (SUM lines drawn)
rl_ip    dw 0
rl_cs    dw 0
rl_fl    dw 0
rl_label db 'SUM:', 0
rl_text  db '000/000', 0, 0
; AD&D'S CLASS TABLES: DSCLOG's XP_NEED, PROBE_PRIEST_THAC0 and PROBE_ADND_SLOTS (RULE_HI_TABLES, the
; second rules word's 8), the sequel's tables to 20th level (tables.RAV_*). The game's own: its XP
; table (RESOURCE.GFF's DATA 1000, in hundreds) AD&D's but for the thief's, gladiator's and ranger's
; 2nd levels (1,200 and 2,200), the druid's from 11th (the cleric's), the gladiator's 16th and up
; (the fighter's) and the psionicist's 18th and 19th (1,400,000 and 1,700,000); priests' THAC0 2/3 a
; level; its own slot rule.
RULE_HI_TABLES equ 8
;
; XP_NEED (site 32, "xp_need_*"): "add sp,6 / imul eax,eax,64h" (7 bytes) after the game reads its XP
; table (5C8:20, a far call: the resource 3E8h, the row, the index), at the eight places that do
; (6C3E4h, 6C48Ah, 6C4CCh, 6FB8Bh, 958E3h, 95931h, 9597Ah, 95C84h): EAX the table's word, the three
; arguments still at the INT's SP (the row 0-7: cleric, druid, fighter, gladiator, preserver,
; psionicist, ranger, thief; the index the level, the next one's XP). EAX the game's x100, with the
; rule AD&D's where it differs (XP_FIXES); the arguments taken off, as the ADD did (the INT's frame
; moved up over them).
xp_need:
        push bp
        mov bp, sp                      ; +2 the way back, +4 CS, +6 flags; +8 3E8h, +0Ah the row,
        imul eax, eax, 100              ;   +0Ch the index
        cmp byte [cs:xp_top], 0
        jne .top
        cmp word [bp + 0x0C], RAV_GAME_XP
        jae .past
        test word [cs:rules_hi], RULE_HI_TABLES
        jz .drop
        push dx
        push si
        mov dl, [bp + 0x0A]
        mov dh, [bp + 0x0C]
        mov si, xp_fixes
.next:  cmp byte [cs:si], 0xFF
        je .done
        cmp dx, [cs:si]
        je .fix
        add si, 6
        jmp .next
.fix:   mov eax, [cs:si + 2]
        inc word [cs:xp_count]
.done:  pop si
        pop dx
        jmp .drop
.top:   mov byte [cs:xp_top], 0         ; (LV_CLAMP's: past the table, the most, so no hold)
.most:  or eax, -1
        jmp .drop
.past:  test word [cs:rules], RULE_LEVEL_10     ; (past the game's 20 entries, which run on into the next
        jz .drop                        ;   row: RAV_XP's to 30th, then the most)
        cmp word [bp + 0x0C], RAV_LEVELS
        jae .most
        cmp word [bp + 0x0A], 7
        ja .most
        push dx
        mov dl, [bp + 0x0A]
        mov dh, [bp + 0x0C]
        call rav_xp_at
        pop dx
        inc word [cs:xp_pasts]
.drop:  push ax
        mov ax, [bp + 6]
        mov [bp + 0x0C], ax
        mov ax, [bp + 4]
        mov [bp + 0x0A], ax
        mov ax, [bp + 2]
        mov [bp + 8], ax
        pop ax
        pop bp
        add sp, 6
        iret
%macro XP_FIX 3                         ; the row, the index, AD&D's XP
        db %1, %2
        dd %3
%endmacro
xp_fixes:
        XP_FIX 1, 10, 200000            ; druid (Dark Sun's)
        XP_FIX 1, 11, 300000
        XP_FIX 1, 12, 750000
        XP_FIX 1, 13, 1500000
        XP_FIX 1, 14, 3000000
        XP_FIX 1, 15, 3500000
        XP_FIX 1, 16, 4000000
        XP_FIX 1, 17, 4500000
        XP_FIX 1, 18, 5000000
        XP_FIX 1, 19, 5500000
        XP_FIX 3, 1, 2250               ; gladiator (Dark Sun's)
        XP_FIX 3, 15, 2400000
        XP_FIX 3, 16, 2700000
        XP_FIX 3, 17, 3000000
        XP_FIX 3, 18, 3300000
        XP_FIX 3, 19, 3600000
        XP_FIX 5, 17, 2400000           ; psionicist
        XP_FIX 5, 18, 2700000
        XP_FIX 6, 1, 2250               ; ranger
        XP_FIX 7, 1, 1250               ; thief
        db 0xFF
xp_count dw 0                           ; (AD&D's XP given, for a look in play)
xp_pasts dw 0                           ; (RAV_XP's past the game's table given, likewise)
;
; PRIEST_THAC0 (site 33, "priest_thac0"): "mov [bp-2],ax" (95391h; 3 bytes, SL's 876ABh) in the THAC0
; routine (9534Ch), AX what a class group takes off 20 at its level ((level - 1) x the group's
; factor / 12; CX the group 0-3: priest, warrior, wizard, rogue; the levels the bytes at [BP-0Ah] +
; CX x 2). With the rule a priest's AD&D's, 2 for every 3 levels. With RULE_LEVEL_10 (the owner's,
; 2026-11-26: High Level Campaigns' Table 39) no more than THAC0_MOST's for the group, so past 20th THAC0
; stops at a priest's 8, a warrior's 1, a wizard's 14 and a rogue's (a thief's or psionicist's) 11; the
; game keeps the best group's (the most taken off), so a character of several classes has the best of them.
priest_thac0:
        test word [cs:rules_hi], RULE_HI_TABLES
        jz .done
        or cx, cx
        jnz .done
        push bx
        push dx
        mov al, [bp - 0x0A]
        cbw
        dec ax
        jns .some
        xor ax, ax
.some:  xor dx, dx
        mov bx, 3
        div bx
        add ax, ax
        pop dx
        pop bx
.done:  test word [cs:rules], RULE_LEVEL_10
        jz .set
        cmp cx, 3
        ja .set
        push bx
        mov bx, cx
        movzx bx, byte [cs:bx + thac0_most]
        cmp ax, bx
        jle .kept
        mov ax, bx
        inc word [cs:thac0_cuts]
.kept:  pop bx
.set:   mov [bp - 2], ax
        iret
thac0_most db 12, 19, 6, 9              ; (20 less the group's best THAC0: priest 8, warrior 1, wizard 14, rogue 11)
thac0_cuts dw 0                         ; (THAC0 held at a group's best, for a look in play)
;
; SCHOLAR_THAC0 (site 248, "scholar_thac0"): "mov ax,14h / sub ax,si" (953A1h; 5 bytes, SL's 876BBh:
; DSCLOG's PROBE_THAC0) at the end of the THAC0 routine (SI the most any of the character's class groups
; takes off 20, PRIEST_THAC0's above; [BP+6] its sheet's number), which every write of a creature's
; THAC0 (+1Fh) uses: AX 20 less SI, and the kit's (kits.thac0): a Scholar's 1 worse, its kit awake.
scholar_thac0:
        mov ax, 20
        sub ax, si
        push bx
        push es
        push ax
        mov ax, [bp + 6]
        call kit_sheet_ax
        pop ax
        push dx
        xor dl, dl
        call kit_is_b
        db KIT_SCHOLAR
        jne .who
        inc ax
        inc word [cs:scholar_thac0s]
        inc dl
.who:   mov bx, ds              ; (the member on show, USE_WHO: on the creation screen the one being made,
        add bx, USE_WHO_SEG     ;  its creature's THAC0 now with the kit or not, for CR_KIT_THAC0)
        mov es, bx
        mov bx, [bp + 6]
        cmp bx, [es:USE_WHO_OFF]
        jne .out
        mov [cs:cr_thac0_scholar], dl
.out:   pop dx
        pop es
        pop bx
        iret
scholar_thac0s dw 0                     ; (Scholars' THAC0s made worse, for a look in play)
scholar_picks dw 0                      ; (Scholars' spells more at a level up: SCHOLAR_LEVEL_UP)
scholar_made dw 0                       ; (... and a new Scholar's: CR_SCHOLAR)
;
; ADND_SLOTS (site 34, "adnd_slots"): "nop / push cs / call 2A10h" (62893h; 5 bytes, SL's 5E240h),
; where the slot routine (62A10h) is asked one class's slots at a spell level: the arguments pushed
; (the class in the low byte, a near pointer in SS to its level and WIS, the spell level), AX the
; count from both (the level's rule and WIS's). With the rule, a cleric's, druid's or preserver's:
; AD&D's for the level (RAV_SLOTS) and the game's for its WIS alone (the routine called with level
; 0); the others', and all without the rule, the game's. Then the kits' (kits.slots, SL's PROBE_SLOTS,
; whatever the tables' rule): an Elementalist's a level behind, a Crusader's priest and a Battle Mage's
; wizard slots 1 fewer (SLOT_BEHIND, BEHIND_LEAST); a Seeker's, Justifier's and Shinobi's their own
; tables' (KIT_TABLE); then the Veiled Robe's (VEILED_SLOT).
SLOT_CALL   equ 0x62A10 - 0x62896       ; (the routine, from the INT's way back)
SLOT_LEVELS equ 30                      ; (class levels in RAV_SLOTS; more are the 30th's)
SLOT_SPELLS equ 9                       ; (spell levels in a row)
adnd_slots:
        push bp
        mov bp, sp                      ; +2 the way back, +4 CS, +6 flags; +8 the class, +0Ah the
        push bx                         ;   pointer, +0Ch the spell level
        push cx
        push si
        mov si, [bp + 0x0A]
        mov cx, [ss:si]                 ; (CL the level, CH WIS)
        mov [cs:sb_level], cl
        call slot_behind                ; (an Elementalist's a level behind, a Crusader's 1 fewer)
        mov [ss:si], cl
        test word [cs:rules_hi], RULE_HI_TABLES
        jz .game
        movzx bx, byte [bp + 8]
        cmp bx, 11
        je .wizard
        cmp bx, RANGER_FIRST
        jb .priest
        cmp bx, RANGER_LAST
        ja .game
        mov bx, 2 * SLOT_LEVELS * SLOT_SPELLS   ; (a ranger: the third)
        jmp .ours
.priest:
        cmp bx, 8
        ja .game
        or bx, bx
        jz .game
        cmp bx, DRUID_FIRST
        mov bx, 0                       ; (a priest: the first table)
        jb .ours
        mov byte [cs:slot_top], DRUID_SLOT_LEVELS   ; (a druid's: no more after 15th)
        jmp .ours
.wizard:
        mov bx, SLOT_LEVELS * SLOT_SPELLS
.ours:  mov byte [ss:si], 0             ; the game's for WIS alone
        call .call
        mov [ss:si], cl
        push ax
        movzx ax, cl                    ; and AD&D's for the level
        cmp al, [cs:slot_top]
        jbe .lv
        mov al, [cs:slot_top]
.lv:    mov byte [cs:slot_top], SLOT_LEVELS
        dec ax
        js .none
        imul ax, ax, SLOT_SPELLS
        add bx, ax
        mov ax, [bp + 0x0C]
        dec ax
        cmp ax, SLOT_SPELLS
        jae .none
        add bx, ax
        push fs
        call tail_fs
        mov al, [fs:bx + rav_slots]     ; (RAV_SLOTS: the tail's)
        pop fs
        mov ah, 0
        inc word [cs:slot_count]
        jmp .sum
.none:  xor ax, ax
.sum:   pop bx
        add ax, bx
        jmp .out
.game:  call .call
.out:   call behind_least
        call kit_table                  ; (a Seeker's, Justifier's or Shinobi's own table)
        call veiled_slot
        pop si
        pop cx
        pop bx
        pop bp
        iret
.call:  push bx                         ; (the routine, a far call in the game's segment: CS from
        push cx                         ;   the INT; it keeps only SI, DI and BP)
        push dx
        push word [bp + 0x0C]
        push word [bp + 0x0A]
        push word [bp + 8]
        push cs
        push word .back
        push word [bp + 4]
        mov ax, [bp + 2]
        add ax, SLOT_CALL
        push ax
        retf
.back:  add sp, 6
        pop dx
        pop cx
        pop bx
        ret
slot_count dw 0                         ; (AD&D's slots given, for a look in play)
; SLOT_BEHIND: (ADND_SLOTS's, its frame; at the site ES:BX the sheet + DI, DI the class's place) CL one less
; (0 kept) when class [BP+8] is a cleric's (1-4) with its slots a level behind (kits.slot_level): an
; Elementalist's kit class, awake; SB_BEHIND 1 then, else 0. SB_FEWER 1 when class [BP+8] is a priest's
; (1-8) and the sheet a Crusader's, awake, or the preserver's (11) and the sheet a Battle Mage's (kits.slots:
; its priest or wizard slots 1 fewer), else 0. SB_TABLE the kit's own slot table (KIT_TABLE) for the kit's
; own class: a Seeker's or Justifier's ranger class (13-16), a Shinobi's thief class (17), else 0. The kits'
; rule on. Others kept.
SBT_SEEKER    equ 1
SBT_JUSTIFIER equ 2
SBT_SHINOBI   equ 3
slot_behind:
        mov word [cs:sb_behind], 0      ; (and SB_FEWER)
        mov byte [cs:sb_table], 0
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        push ax
        push bx
        push si
        sub bx, di
        mov al, [bp + 8]
        cmp al, WIZARD_CLASS
        je .battle
        cmp al, THIEF_CLASS
        je .shinobi
        cmp al, RANGER_FIRST
        jb .priest
        cmp al, RANGER_LAST
        ja .out
        call kit_is_b
        db KIT_SEEKER
        jne .justifier
        mov ah, SBT_SEEKER
        jmp .own
.justifier:
        call kit_is_b
        db KIT_JUSTIFIER
        jne .out
        mov ah, SBT_JUSTIFIER
        jmp .own
.shinobi:
        call kit_is_b
        db KIT_SHINOBI
        jne .out
        mov ah, SBT_SHINOBI
.own:   mov si, [cs:kit_where]          ; (the kit's own class alone)
        cmp al, [es:bx + si + SH_CLASSES]
        jne .out
        mov [cs:sb_table], ah
        jmp .out
.battle:
        call kit_is_b
        db KIT_BATTLE_MAGE
        jne .out
        jmp .fewer
.priest:
        cmp al, 1
        jb .out
        cmp al, 8
        ja .out
        call kit_is_b
        db KIT_CRUSADER
        jne .elem
.fewer: mov byte [cs:sb_fewer], 1
.elem:  cmp byte [bp + 8], 4
        ja .out
        call kit_is_b
        db KIT_ELEMENTALIST
        jne .out
        mov si, [cs:kit_where]
        mov al, [es:bx + si + SH_CLASSES]
        cmp al, [bp + 8]
        jne .out
        mov byte [cs:sb_behind], 1
        or cl, cl
        jz .out
        dec cl
        inc word [cs:sb_count]
.out:   pop si
        pop bx
        pop ax
.ret:   ret
; KIT_TABLE: (ADND_SLOTS's, its frame) with SB_TABLE, AX (the slots of the class's level CL at spell level
; [BP+0Ch]) the kit's own table's, WIS's left out (kits.slots, SL's PROBE_SLOTS): a Seeker's priest slots
; at spell levels 1-4 from 6th level (SEEKER_SLOTS, the 16th's on), a Justifier's at 1-3 from 10th
; (JUSTIFIER_SLOTS: none at 8th and 9th, where the ranger's first slot would cast at level 0), a Shinobi's
; wizard slots the Seeker's by its thief level; none before the table's first level or past its spell
; levels. Others kept.
SEEKER_FIRST    equ 6
SEEKER_LAST     equ 16
JUSTIFIER_FIRST equ 10
JUSTIFIER_LAST  equ 16
kit_table:
        cmp byte [cs:sb_table], 0
        je .ret
        push bx
        push cx
        push si
        xor ax, ax
        movzx bx, byte [bp + 0x0C]
        dec bx
        cmp bx, 3
        ja .out                         ; (spell levels 1 to 4 only)
        mov si, seeker_slots
        mov ch, SEEKER_FIRST
        mov ah, SEEKER_LAST
        cmp byte [cs:sb_table], SBT_JUSTIFIER
        jne .row
        mov si, justifier_slots
        mov ch, JUSTIFIER_FIRST
        mov ah, JUSTIFIER_LAST
.row:   cmp cl, ch
        jb .none
        cmp cl, ah
        jbe .at
        mov cl, ah
.at:    sub cl, ch
        movzx cx, cl
        shl cx, 2
        add bx, cx
        movzx ax, byte [cs:bx + si]
        inc word [cs:kt_count]
        jmp .out
.none:  xor ax, ax
.out:   pop si
        pop cx
        pop bx
.ret:   ret
kt_count dw 0                           ; (slots from a kit's table, for a look in play)
; a Seeker's priest slots at spell levels 1 to 4, by level 6 to 16 (and on: kits.SEEKER_SLOTS, DSCLOG's
; seeker_slots; The Complete Ranger's Handbook's table, the owner's Table 51 past 13th), a Shinobi's (by
; thief level); a Justifier's at spell levels 1 to 3, by level 10 to 16 (and on: kits.JUSTIFIER_SLOTS, the
; owner's Table 46)
seeker_slots db 1, 0, 0, 0,  2, 0, 0, 0,  2, 1, 0, 0,  2, 2, 0, 0,  2, 2, 1, 0
             db 3, 2, 1, 0,  3, 2, 2, 0,  3, 3, 2, 1,  3, 3, 3, 1,  4, 4, 3, 1,  4, 4, 3, 2
justifier_slots db 1, 0, 0, 0,  2, 0, 0, 0,  2, 1, 0, 0,  2, 2, 0, 0,  2, 2, 1, 0,  2, 2, 2, 0,  3, 2, 2, 0
; BEHIND_LEAST: (ADND_SLOTS's, SI the level's pointer) with SB_FEWER, AX (the slots) 1 fewer (0 kept);
; with SB_BEHIND, the level put back (SB_LEVEL), and AX 1 where none and the class's own level reaches
; spell level [BP+0Ch]: 2 x it - 1, 14 for the 7th (a cleric's; a 6th-level one only with AD&D's
; tables, RULE_HI_TABLES). Others kept.
behind_least:
        cmp byte [cs:sb_fewer], 0
        je .behind
        or ax, ax
        jz .behind
        dec ax
        inc word [cs:sb_count]
.behind:
        cmp byte [cs:sb_behind], 0
        je .ret
        push cx
        mov cl, [cs:sb_level]
        mov [ss:si], cl
        or ax, ax
        jnz .out
        mov ch, [bp + 0x0C]
        cmp ch, 6
        jb .need
        test word [cs:rules_hi], RULE_HI_TABLES
        jz .out
.need:  add ch, ch
        dec ch
        cmp ch, 13
        jne .cmp
        inc ch
.cmp:   cmp cl, ch
        jb .out
        mov ax, 1
.out:   pop cx
.ret:   ret
sb_level  db 0
sb_behind db 0                          ; (a word with SB_FEWER, cleared together)
sb_fewer  db 0
sb_table  db 0                          ; (SBT_*: a kit's own table, KIT_TABLE)
sb_count  dw 0                          ; (slots counted a level behind or 1 fewer, for a look in play)
slot_top   db SLOT_LEVELS               ; (the class levels whose slots grow: a druid's DRUID_SLOT_LEVELS)
DRUID_FIRST equ 5                       ; (the druids' classes 5-8: the owner's table, 2026-11-25, the same
DRUID_SLOT_LEVELS equ 15                ;   as the cleric's to 15th, then 15th's, 6 6 6 6 4 2 1)
; VEILED_SLOT: (ADND_SLOTS's, its frame) AX the slots of class [BP+8] at spell level [BP+0Ch], the
; combatant at [BP-6] (the SI it pushed): the Veiled Robe (a robe of plus 2 on the chest, PROT_SCAN; SL's
; robes.slots) a preserver's slot more at spell levels 1 to 3 where it has any, a Shinobi's too. Others kept.
WIZARD_CLASS equ 11
veiled_slot:
        or ax, ax
        jz .ret
        cmp byte [bp + 8], WIZARD_CLASS
        je .robe
        cmp byte [cs:sb_table], SBT_SHINOBI     ; (a Shinobi's wizard slots too, as SL's PROBE_SLOTS)
        jne .ret
.robe:  cmp word [bp + 0x0C], 1
        jb .ret
        cmp word [bp + 0x0C], 3
        ja .ret
        push si
        mov si, [bp - 6]
        call prot_here
        pop si
        jc .ret
        cmp byte [cs:p_robe], 2
        jb .ret
        inc ax
        inc word [cs:veiled_count]
.ret:   ret
veiled_count dw 0
; by class level 1-30, the slots at spell levels 1-9 (tables.RAV_PRIEST_SLOTS, RAV_WIZARD_SLOTS,
; RAV_RANGER_SLOTS)

RANGER_LAST  equ 16
section tail
rav_slots:
        db 1, 0, 0, 0, 0, 0, 0, 0, 0    ; priests (clerics, druids): 1
        db 2, 0, 0, 0, 0, 0, 0, 0, 0
        db 2, 1, 0, 0, 0, 0, 0, 0, 0
        db 3, 2, 0, 0, 0, 0, 0, 0, 0
        db 3, 3, 1, 0, 0, 0, 0, 0, 0    ; 5
        db 3, 3, 2, 0, 0, 0, 0, 0, 0
        db 3, 3, 2, 1, 0, 0, 0, 0, 0
        db 3, 3, 3, 2, 0, 0, 0, 0, 0
        db 4, 4, 3, 2, 1, 0, 0, 0, 0
        db 4, 4, 3, 3, 2, 0, 0, 0, 0    ; 10
        db 5, 4, 4, 3, 2, 1, 0, 0, 0
        db 6, 5, 5, 3, 2, 2, 0, 0, 0
        db 6, 6, 6, 4, 2, 2, 0, 0, 0
        db 6, 6, 6, 5, 3, 2, 1, 0, 0
        db 6, 6, 6, 6, 4, 2, 1, 0, 0    ; 15
        db 7, 7, 7, 6, 4, 3, 1, 0, 0
        db 7, 7, 7, 7, 5, 3, 2, 0, 0
        db 8, 8, 8, 8, 6, 4, 2, 0, 0
        db 9, 9, 8, 8, 6, 4, 2, 0, 0
        db 9, 9, 9, 8, 7, 5, 2, 0, 0    ; 20
        db 9, 9, 9, 9, 8, 6, 2, 0, 0
        db 9, 9, 9, 9, 9, 6, 3, 0, 0
        db 9, 9, 9, 9, 9, 7, 3, 0, 0
        db 9, 9, 9, 9, 9, 8, 3, 0, 0
        db 9, 9, 9, 9, 9, 8, 4, 0, 0    ; 25
        db 9, 9, 9, 9, 9, 9, 4, 0, 0
        db 9, 9, 9, 9, 9, 9, 5, 0, 0
        db 9, 9, 9, 9, 9, 9, 6, 0, 0
        db 9, 9, 9, 9, 9, 9, 7, 0, 0
        db 9, 9, 9, 9, 9, 9, 8, 0, 0    ; 30
        db 1, 0, 0, 0, 0, 0, 0, 0, 0    ; wizards (preservers): 1
        db 2, 0, 0, 0, 0, 0, 0, 0, 0
        db 2, 1, 0, 0, 0, 0, 0, 0, 0
        db 3, 2, 0, 0, 0, 0, 0, 0, 0
        db 4, 2, 1, 0, 0, 0, 0, 0, 0    ; 5
        db 4, 2, 2, 0, 0, 0, 0, 0, 0
        db 4, 3, 2, 1, 0, 0, 0, 0, 0
        db 4, 3, 3, 2, 0, 0, 0, 0, 0
        db 4, 3, 3, 2, 1, 0, 0, 0, 0
        db 4, 4, 3, 2, 2, 0, 0, 0, 0    ; 10
        db 4, 4, 4, 3, 3, 0, 0, 0, 0
        db 4, 4, 4, 4, 4, 1, 0, 0, 0
        db 5, 5, 5, 4, 4, 2, 0, 0, 0
        db 5, 5, 5, 4, 4, 2, 1, 0, 0
        db 5, 5, 5, 5, 5, 2, 1, 0, 0    ; 15
        db 5, 5, 5, 5, 5, 3, 2, 1, 0
        db 5, 5, 5, 5, 5, 3, 3, 2, 0
        db 5, 5, 5, 5, 5, 3, 3, 2, 1
        db 5, 5, 5, 5, 5, 3, 3, 3, 1
        db 5, 5, 5, 5, 5, 4, 3, 3, 2    ; 20
        db 5, 5, 5, 5, 5, 4, 4, 4, 2
        db 5, 5, 5, 5, 5, 5, 4, 4, 3
        db 5, 5, 5, 5, 5, 5, 5, 5, 3
        db 5, 5, 5, 5, 5, 5, 5, 5, 4
        db 5, 5, 5, 5, 5, 5, 5, 5, 5    ; 25
        db 6, 6, 6, 6, 5, 5, 5, 5, 5
        db 6, 6, 6, 6, 6, 6, 6, 5, 5
        db 6, 6, 6, 6, 6, 6, 6, 6, 6
        db 7, 7, 7, 7, 6, 6, 6, 6, 6
        db 7, 7, 7, 7, 7, 7, 7, 6, 6    ; 30
        db 0, 0, 0, 0, 0, 0, 0, 0, 0    ; rangers (AD&D's; the game's formula gives 3 2 1 at 12th, 3 2 2 at 13th, 3 3 2 at 14th): 1
        db 0, 0, 0, 0, 0, 0, 0, 0, 0
        db 0, 0, 0, 0, 0, 0, 0, 0, 0
        db 0, 0, 0, 0, 0, 0, 0, 0, 0
        db 0, 0, 0, 0, 0, 0, 0, 0, 0    ; 5
        db 0, 0, 0, 0, 0, 0, 0, 0, 0
        db 0, 0, 0, 0, 0, 0, 0, 0, 0
        db 1, 0, 0, 0, 0, 0, 0, 0, 0
        db 2, 0, 0, 0, 0, 0, 0, 0, 0
        db 2, 1, 0, 0, 0, 0, 0, 0, 0    ; 10
        db 2, 2, 0, 0, 0, 0, 0, 0, 0
        db 2, 2, 1, 0, 0, 0, 0, 0, 0
        db 3, 2, 1, 0, 0, 0, 0, 0, 0
        db 3, 2, 2, 0, 0, 0, 0, 0, 0
        db 3, 3, 2, 0, 0, 0, 0, 0, 0    ; 15
        db 3, 3, 3, 0, 0, 0, 0, 0, 0
        db 3, 3, 3, 0, 0, 0, 0, 0, 0
        db 3, 3, 3, 0, 0, 0, 0, 0, 0
        db 3, 3, 3, 0, 0, 0, 0, 0, 0
        db 3, 3, 3, 0, 0, 0, 0, 0, 0    ; 20
        db 3, 3, 3, 0, 0, 0, 0, 0, 0
        db 3, 3, 3, 0, 0, 0, 0, 0, 0
        db 3, 3, 3, 0, 0, 0, 0, 0, 0
        db 3, 3, 3, 0, 0, 0, 0, 0, 0
        db 3, 3, 3, 0, 0, 0, 0, 0, 0    ; 25
        db 3, 3, 3, 0, 0, 0, 0, 0, 0
        db 3, 3, 3, 0, 0, 0, 0, 0, 0
        db 3, 3, 3, 0, 0, 0, 0, 0, 0
        db 3, 3, 3, 0, 0, 0, 0, 0, 0
        db 3, 3, 3, 0, 0, 0, 0, 0, 0    ; 30
section image
; CON AS IN AD&D: DSCLOG's REGEN_SITE and CON_SAVE (RULE_HI_CON, the second rules word's 1024), the
; sequel's routines SL's:
; - REGEN_SITE (site 35, "regen_rate"): "mov dx,cx / imul dx,dx,31h" (26599h; 5 bytes, SL's 228BFh)
;   in the regeneration routine (264BFh, SL's 227E5h: once more than 300 seconds of game time have
;   passed since the last, DS:19B8h; a hit point for each 300 to a member with CON 20 or more, what is
;   left over dropped), after its "div ebx" (EAX the 300s, EDX the rest; CX the member). With the
;   rule the seconds added to the member's own (REGEN_SECS, the rest kept for next time) and AX the
;   hit points from them, one for each (26 - CON) x 600 seconds (AD&D's one an hour at CON 20 to one
;   every 10 minutes at 25), at most 1000; a clock gone back (a game loaded) none.
; - CON_SAVE (site 36, "con_save"): "mov bx,ax / mov al,[bx+880h]" (1D36Bh; 6 bytes, SL's 5EAA1h) in
;   CON's save adjustment (1D35Bh, DS:880h by CON: +1 at 19 to +4 at 25), which the save modifiers
;   (83A81h) and the poison check (8E092h) add to a dwarf's or halfling's CON x 2 / 7. With the rule
;   0 for a dwarf or a halfling (the sheet's race +12h 2 or 6: the racial bonus alone); else the
;   table's. [BP+6] the thing (a combatant).
RULE_HI_CON equ 1024
regen_secs dd 0, 0, 0, 0
regen_count dw 0                        ; (hit points so given, for a look in play)
regen_site:
        test word [cs:rules_hi], RULE_HI_CON
        jz .game
        push ebx
        push si
        push es
        imul eax, eax, 300
        add eax, edx                    ; (the seconds since the last)
        mov si, cx
        shl si, 2
        add eax, [cs:regen_secs + si]
        js .back
        les bx, [CREATURES_PTR]
        imul dx, cx, CREATURE_SIZE
        add bx, dx
        movzx ebx, byte [es:bx + 0x1B]  ; (CON)
        cmp bl, 25
        jbe .con
        mov bl, 25
.con:   neg ebx
        add ebx, 26
        imul ebx, ebx, 600              ; (the seconds a hit point)
        xor edx, edx
        div ebx
        mov [cs:regen_secs + si], edx
        cmp eax, 1000
        jbe .out
        mov eax, 1000
        jmp .out
.back:  xor eax, eax
        mov [cs:regen_secs + si], eax
.out:   add [cs:regen_count], ax
        pop es
        pop si
        pop ebx
.game:  mov dx, cx
        imul dx, dx, CREATURE_SIZE
        iret
DWARF_RACE    equ 2
HALFLING_RACE equ 6
con_save_count dw 0                     ; (dwarves' and halflings' adjustments taken, for a look in play)
con_save:
        mov bx, ax
        mov al, [bx + 0x880]
        test word [cs:rules_hi], RULE_HI_CON
        jz .out
        push ax
        mov ax, [bp + 6]
        call fighter_creature
        jc .keep
        push es
        les bx, [CREATURES_PTR]         ; (its sheet: the creature's +4)
        imul ax, ax, CREATURE_SIZE
        add bx, ax
        mov ax, [es:bx + 4]
        imul ax, ax, SHEET_SIZE
        les bx, [SHEETS_PTR]
        add bx, ax
        mov bl, [es:bx + 0x12]          ; (the race)
        pop es
        pop ax
        cmp bl, DWARF_RACE
        je .none
        cmp bl, HALFLING_RACE
        jne .out
.none:  or al, al
        jz .out
        xor al, al
        inc word [cs:con_save_count]
        jmp .out
.keep:  pop ax
.out:   iret
; DUAL-CLASSING AS THE MANUAL HAS IT: DSCLOG's DUAL_LEVEL and DUAL_PRIMES (RULE_HI_DUAL, the second
; rules word's 2048), the sequel's code SL's with its records and unsigned jumps:
; - DUAL_LEVEL (site 37, "dual_level_menu", "dual_level_view", "dual_level_window"): the two portrait
;   menus' test for DUAL (7926Ch, 7948Bh) and the DUAL window's (94BCCh, in its class test), "cmp byte
;   [es:bx+1Eh],2" (5 bytes; ES:BX the sheet, +1Eh its first class's level, SL's +24h): 3 with the rule
;   ("at least third level in your current class", the manual). The flags are the game's next jump's.
; - DUAL_PRIMES (sites 38 and 39, "dual_old_prime", "dual_new_prime"): the DUAL window's class test (SI
;   the member, DI the class offered), "cmp byte [es:bx+19h],0Fh" (94B70h; ES:BX the creature plus the
;   old class's one prime requisite from the game's table) and "cmp byte [es:bx+19h],11h" (94BA5h, the
;   new class's), each with a "jc" (no) after: with the rule every prime requisite of the class
;   (DUAL_PRIMES_OF), the old class's (the sheet's +1Bh) at 15 or more, the new one's at 17 or more, on
;   the creature's scores (+19h on); else the game's compare.
RULE_HI_DUAL equ 2048
DUAL_LEAST_LEVEL equ 2          ; (the game's)
DUAL_OLD_LEAST equ 15
DUAL_NEW_LEAST equ 17
dual_count dw 0                 ; (the rule's tests made, for a look in play)
dual_level:
        pushad
        push es
        mov di, sp
        mov al, DUAL_LEAST_LEVEL
        test word [cs:rules_hi], RULE_HI_DUAL
        jz .cmp
        inc al                          ; (the manual's third)
        inc word [cs:dual_count]
.cmp:   cmp [es:bx + 0x1E], al
dual_flags:
        pushf
        pop ax
        and ax, 0x08D5
        and word [ss:di + 38], ~0x08D5
        or [ss:di + 38], ax
        pop es
        popad
        iret
dual_old:
        pushad
        push es
        mov di, sp
        mov dl, DUAL_OLD_LEAST
        xor cx, cx                      ; (the class from the sheet)
        jmp dual_primes
dual_new:
        pushad
        push es
        mov cx, di
        mov di, sp
        mov dl, DUAL_NEW_LEAST
dual_primes:
        test word [cs:rules_hi], RULE_HI_DUAL
        jnz .rule
        cmp [es:bx + 0x19], dl          ; (the game's)
        jmp dual_flags
.rule:  inc word [cs:dual_count]
        test cx, cx
        jnz .class
        les bx, [SHEETS_PTR]
        imul ax, si, SHEET_SIZE
        add bx, ax
        mov cl, [es:bx + 0x1B]
.class: les bx, [CREATURES_PTR]
        imul ax, si, CREATURE_SIZE
        lea si, [bx + 0x19]
        add si, ax                      ; (ES:SI the creature's STR)
        xor ax, ax
        cmp cx, DUAL_CLASSES
        jae .ok
        mov bx, cx
        mov al, [cs:dual_primes_of + bx]
.ok:    mov ah, dl                      ; (AH DL while every one passes, 0 once one doesn't)
.each:  shr al, 1
        jnc .next
        cmp [es:si], dl
        jae .next
        xor ah, ah
.next:  inc si
        test al, al
        jnz .each
        cmp ah, dl
        jmp dual_flags
; each class's prime requisites (bit 0 STR ... bit 5 CHA; tracker.PRIME_REQUISITES): clerics WIS,
; druids WIS and CHA, fighter and gladiator STR, preserver INT, psionicist CON and WIS, rangers STR,
; DEX and WIS, thief DEX; the sequel's 18 a wizard's (INT), 19 a priest's (WIS)
dual_primes_of db 0, 16, 16, 16, 16, 48, 48, 48, 48, 1, 1, 8, 20, 19, 19, 19, 19, 2, 8, 16
DUAL_CLASSES equ $ - dual_primes_of
manual_count dw 0                          ; (the sites above at work, counted for a look in play)
held_damage:
        mov ax, [bp - 4]
        test word [cs:rules_hi], RULE_HI_HELD
        jnz .out
        shl ax, 1
.out:   iret
held_now:                       ; CF with the rule on and the attack's target (TARGET) helpless. DS the game's
        test word [cs:rules_hi], RULE_HI_HELD   ; (TEST clears CF)
        jz .ret
        push ax
        push bx
        push cx
        push es
        mov ax, [TARGET]
        mov cl, HELD_EFFECT
        call has_effect
        je .yes
        cmp ax, 400
        jae .no
        imul bx, ax, 3
        mov cx, ds
        add cx, FIGHTERS_SEG
        mov es, cx
        cmp byte [es:bx + FIGHTERS_OFF], 2
        jne .no
        mov ax, [es:bx + FIGHTERS_OFF + 1]
        imul ax, ax, CREATURE_SIZE
        les bx, [CREATURES_PTR]
        add bx, ax
        cmp byte [es:bx + CREATURE_STATUS], HELD_OUT_COLD
        je .yes
.no:    clc
        jmp .out
.yes:   inc word [cs:held_count]
        stc
.out:   pop es
        pop cx
        pop bx
        pop ax
.ret:   ret
held_count dw 0                 ; (helpless targets hit so, for a look in play)

; TWO WEAPONS: DSCLOG's RULE_TWO_WEAPONS (AD&D's two weapons), the sequel's routines SL's:
; - PROBE_TWO: INT VEC_TWO replaces "neg ax / mov dx,ax / or dx,dx / jge +2 / xor dx,dx" (10 bytes, INT +
;   8 NOPs; 5DE7Ch, SL's 59634h) in the routine that gives an attack's to-hit adjustment with two weapons
;   ready (5DE34h, called by the attack at 5C78Ch), for a non-ranger: AX the attacker's DEX reaction
;   adjustment (the call before), [BP+0Ah] the attack's item, [BP-2] the attacker's creature. DX the
;   adjustment: the game's -AX, no less than 0; with the rule, -2 (the item in the right hand) or -4 (the
;   left) plus AX, no more than 0, and only with a melee weapon in the other hand (else 0: a shield, a
;   two-handed weapon, a sling or bow in the missile slot don't count). (SL's kits and cahulaks aren't
;   the sequel's.)
; - RG_TWO (site 78, SITE_RG_TWO): "test word es:[bx+10h],200h" (6 bytes: the site's INT, its number and 3
;   NOPs; 5DE67h, SL's RG_TWO at 5961Fh), the routine's test whether the attacker (sheet ES:BX, creature
;   [BP-2]) is a ranger, who has no penalty: its "jnz" after it kept. With the rule a ranger has none only
;   in light armour (ARMOUR_WORN with AW_HEAVY: not leather, and of a material); in other armour ZF is set,
;   as for anyone else, and PROBE_TWO gives AD&D's. A Justifier (KITS) has none in any armour.
; - OFF_HAND: INT VEC_OFF_HAND replaces "mov ah,0 / mov [bp-0Ah],ax" (5 bytes, INT + 3 NOPs; 5CEE8h, SL's
;   "cbw / mov [bp-8],ax" at 58892h, PROBE_ATTACKS' site), the attack routine's attacks a round (halves)
;   stored, AL: with the rule, no more than one a round (2 halves) with a melee weapon ([BP+16h] 1 or
;   less) in the off hand (the item [BP+12h] in slot LEFT_HAND); the extra attacks are the main hand's.
RULE_TWO_WEAPONS equ 4
RIGHT_HAND    equ 3
LEFT_HAND     equ 10
NO_ITEM       equ 9999
ITEM_NEXT     equ 0x04
ITEM_TYPE     equ 0x0A
ITEM_SLOT     equ 0x13
ITEM_TYPES_PTR equ 0x19CD           ; DS: far pointer to the item types, 0Fh bytes each
TYPE_SIZE     equ 0x0F
TYPE_MELEE    equ 0x06              ; (1 a melee weapon: SL's +0Ah)
probe_two:
        test word [cs:rules], RULE_TWO_WEAPONS
        jnz .rule
        neg ax
        mov dx, ax
        or dx, dx
        jge .done
        xor dx, dx
.done:  iret
.rule:  push ax
        push bx
        push es
        mov [cs:two_adjust], ax
        mov ax, [bp + 0x0A]
        call item_is_cahulaks
        jne .weapons
        mov word [cs:two_base], -2      ; (the cahulaks: the main head's base, as SL's)
        xor dx, dx
        call kit_two                    ; (a Ghetto Fighter's 2 better; a Twin-blade or Battle Dancer in light
        jc .out                         ;  armour none, as SL's PROBE_TWO has it for the cahulaks too)
        call cah_adjust                 ; (the cahulaks: the main head's here, the off head's more kept)
        jmp .counted
.weapons:
        xor dx, dx
        mov bx, [bp + 0x0A]
        cmp bx, NO_ITEM
        jae .out
        imul bx, bx, ITEM_SIZE
        mov ax, bx
        les bx, [ITEMS_PTR]
        add bx, ax
        mov al, [es:bx + ITEM_SLOT]     ; the attack's hand, and the other
        mov dx, -2
        mov ah, LEFT_HAND
        cmp al, RIGHT_HAND
        je .hand
        mov dx, -4
        mov ah, RIGHT_HAND
        cmp al, LEFT_HAND
        je .hand
        xor dx, dx
        jmp .out
.hand:  mov [cs:two_base], dx
        call kit_two                    ; (the kits': KITS)
        mov dx, 0
        jc .out
        mov al, ah
        mov bx, [bp - 2]
        call melee_in
        mov dx, 0
        jnc .out                        ; nothing to fight with in the other hand
        mov dx, [cs:two_base]
        add dx, [cs:two_adjust]
        jle .counted
        xor dx, dx
.counted:
        inc word [cs:two_count]
.out:   pop es
        pop bx
        pop ax
        iret
RANGER_FLAG   equ 0x200             ; (the sheet's +10h: a ranger; SL's +12h)
rg_two:
        pushad
        push es
        mov di, sp
        and word [ss:di + 38], ~0x40    ; (ZF clear: the game's jump to no penalty)
        test word [es:bx + 0x10], RANGER_FLAG
        jz .plain
        test word [cs:rules], RULE_TWO_WEAPONS
        jz .out
        call kit_is_b                   ; (a Justifier: none in any armour; kits.py)
        db KIT_JUSTIFIER
        je .out
        mov dx, [bp - 2]
        mov byte [cs:aw_heavy], 1
        call armour_worn
        mov byte [cs:aw_heavy], 0
        jnc .out
        inc word [cs:rg_heavy]
.plain: or word [ss:di + 38], 0x40      ; (ZF set: on to the penalty, PROBE_TWO's)
.out:   pop es
        popad
        iret
rg_heavy    dw 0                ; (rangers in armour not light given the penalty, for a look in play)
off_hand:
        mov ah, 0
        call kit_attacks                ; (the kits' to hit: KITS)
        call fine_hit                   ; (the Fine Bow's +1: POISON AND ARROWS)
        call spec_attacks               ; (weapon specialization: the skill's rate and THAC0)
        call kit_wild_more              ; (Wild Fighting passed: one more in melee)
        call cah_more                   ; (the cahulaks: the off head's one more a round)
        test word [cs:rules], RULE_TWO_WEAPONS
        jz .store
        cmp ax, 2
        jbe .store
        cmp word [bp + 0x16], 1
        jg .store
        cmp word [bp + 0x12], NO_ITEM
        jae .store
        push bx
        push es
        imul bx, [bp + 0x12], ITEM_SIZE
        push ax
        les ax, [ITEMS_PTR]
        add bx, ax
        pop ax
        cmp byte [es:bx + ITEM_SLOT], LEFT_HAND
        pop es
        pop bx
        jne .store
        mov ax, 2
        inc word [cs:off_count]
.store: mov [bp - 0x0A], ax
        iret
; MELEE_IN: CF if creature BX (DS the game's) has a melee weapon in slot AL, in any of its item lists
; (+8, +0Ah, +0Ch: each a thing, the combatants' table's kind 1 an item, the first of a list linked by
; +4). All registers kept.
melee_in:
        pusha
        push es
        mov [cs:mi_slot], al
        imul bx, bx, CREATURE_SIZE
        mov [cs:mi_creature], bx
        mov cx, 8
.list:  les bx, [CREATURES_PTR]
        add bx, [cs:mi_creature]
        add bx, cx
        mov dx, [es:bx]
        cmp dx, NO_ITEM                 ; (the party's lists are things 201h and up)
        jae .next
        imul bx, dx, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        cmp byte [es:bx + FIGHTERS_OFF], 1
        jne .next                       ; not an item
        mov dx, [es:bx + FIGHTERS_OFF + 1]
        mov si, 100                     ; (no more than 100 in a list)
.item:  cmp dx, NO_ITEM
        jae .next
        dec si
        js .next
        imul bx, dx, ITEM_SIZE
        les di, [ITEMS_PTR]
        add bx, di
        mov dx, [es:bx + ITEM_NEXT]
        mov al, [es:bx + ITEM_SLOT]
        cmp al, [cs:mi_slot]
        jne .item
        imul bx, [es:bx + ITEM_TYPE], TYPE_SIZE
        les di, [ITEM_TYPES_PTR]
        cmp byte [es:bx + di + TYPE_MELEE], 1
        jne .item
        pop es
        popa
        stc
        ret
.next:  add cx, 2
        cmp cx, 0x0E
        jb .list
        pop es
        popa
        clc
        ret
mi_slot     db 0
mi_creature dw 0
two_base    dw 0
two_adjust  dw 0
two_count   dw 0                ; (adjustments given so, for a look in play)
off_count   dw 0                ; (off-hand attacks cut so)

; WEAPON SPECIALIZATION: DSCLOG's RULE_SPECIALIZE (dsloader/specialize.py) in the sequel's weapon attack
; routine (5CE80h, SL's 58780h: the same code, its frame [BP+0Ah] the THAC0 the d20 is held against,
; [BP+10h] the attacker's sheet, [BP+12h] the weapon's item, [BP+14h] its type, [BP+16h] above 1 for a
; missile; its locals [BP-0Ah] the attacks a round in halves, [BP-10h] the damage dice, [BP-12h] their
; sides, [BP-14h] the damage bonus: SL's -8, -0Eh, -10h, -12h). The chosen kinds come over with the party
; (the transfer's sheet +42h..+44h, SL's +14h..+16h: SPEC_SLOTS); no one picks them in the sequel.
; - SPEC_ATTACKS, from OFF_HAND (5CEE8h, SL's PROBE_ATTACKS' site), before the off hand's cut: in melee
;   a warrior (more than 2 halves, the game's own specialist's rate for every fighter, gladiator and
;   ranger) with a weapon of a kind not chosen half an attack less, a grand master one more; a missile
;   a specialist's rate of fire (MISSILE_RATE); specialization +1 to hit, mastery +3 (the THAC0 less);
; - SPEC_DAMAGE (site 51 at 5CF6Dh, "add [bp-14h],ax", the strength bonus added; SL's 588F2h,
;   PROBE_SPEC_DAMAGE): specialization +2, mastery +3, grand mastery the dice the next greater die size
;   (NEXT_DIE), against a large target too (SIZE_DICE: SPEC_GRAND_DIE).
; The kits' parts (a Battle Mage's, Crusader's, Mind Warrior's expertise, a Justifier's, a Myrmidon's
; second kind, a Seeker's bow): SPEC_OF_SHEET and EXPERT_HALVES, with the kits' rules (KITS).
RULE_SPECIALIZE equ 4096
SPEC_SLOTS  equ 0x42            ; (the Loader's 48h sheet: SL's +14h..+16h there)
SPEC_COUNT  equ 4               ; (the four packed at SPEC_SLOTS: SL's)
SPEC_MORE   equ 0x45            ; slots 4-7 (SPEC_GET_MORE): +45h..+47h, 5 bits each (kind + 1), past SL's
SPEC_ALL    equ 8               ;   levels only (a gladiator's 5th-8th, the owner's 2026-11-26)
SPEC_PACKED equ 0x80
SPEC_V2     equ 0x40
SPEC_KINDS_MASK equ 0x1FFFF
V3_BASE equ 17 * 17 * 17 * 17  ; (DSCLOG's V3 layout: the Loader's game.packed_specs)
REST_SETS equ 1 + 22 + 231 + 1540
ROLL_SHIFT equ 17                ; (the starting roll in bits 17-21: SPEC_PACK's)
ROLL_UNKNOWN equ 31             ; (none kept: the Loader's game.ROLL_UNKNOWN)
KIND_COUNT equ 22
SHEETS_COUNT equ 17
SPEC_NONE   equ 0               ; (SPEC_OF's levels, DSCLOG's)
SPEC_PLAIN  equ 1
SPEC_EXPERT equ 2
SPEC_SPECIAL equ 3
SPEC_MASTER equ 4
SPEC_GRAND  equ 5
MASTERY     equ 5               ; (the fighter levels)
GRAND_MASTERY equ 9
BOW_KIND    equ 14              ; (the bow's kind + 1)
spec_attacks:                   ; AX the attacks a round (halves): made the skill's. Others kept.
        test word [cs:rules], RULE_SPECIALIZE
        jz .ret
        push dx
        call spec_of
        cmp word [bp + 0x16], 1
        jg .missile
        cmp ax, 2
        ja .warrior
        call expert_of          ; (not a warrior: the game's, or a kit's expertise, EXPERT_HALVES)
        jmp .hit
.warrior:
        cmp dl, SPEC_PLAIN
        jne .grand
        dec ax
        inc word [cs:spec_rates]
        jmp .hit
.grand: cmp dl, SPEC_GRAND
        jne .hit
        add ax, 2
        inc word [cs:spec_rates]
        jmp .hit
.missile:
        push bx
        push cx
        push si
        push es
        mov cx, ax
        call spec_sheet
        jc .kept
        mov si, [bp + 0x14]
        call missile_rate
        cmp ax, cx
        je .kept
        inc word [cs:spec_rates]
.kept:  pop es
        pop si
        pop cx
        pop bx
.hit:   cmp dl, SPEC_SPECIAL
        jb .done
        inc word [cs:spec_hits]
        cmp dl, SPEC_SPECIAL
        ja .three
        dec word [bp + 0x0A]
        jmp .done
.three: sub word [bp + 0x0A], 3
.done:  pop dx
.ret:   ret
spec_damage:                    ; (site 51) the strength bonus added, the kits' and the skill's
        add [bp - 0x14], ax
        call kit_damage
        test word [cs:rules], RULE_SPECIALIZE
        jz .ret
        push dx
        call spec_of
        cmp dl, SPEC_SPECIAL
        jb .out
        inc word [cs:spec_damages]
        cmp dl, SPEC_SPECIAL
        ja .three
        add word [bp - 0x14], 2
        jmp .out
.three: add word [bp - 0x14], 3
        cmp dl, SPEC_GRAND
        jne .out
        push ax
        mov ax, [bp - 0x12]
        call next_die
        mov [bp - 0x12], ax
        pop ax
.out:   pop dx
.ret:   iret
spec_grand_die:                 ; (SIZE_DICE's, its dice for a large target set) a grand master's sides
        test word [cs:rules], RULE_SPECIALIZE   ;   [BP-12h] the next greater die. All kept.
        jz .ret
        push ax
        push dx
        call spec_of
        cmp dl, SPEC_GRAND
        jne .out
        mov ax, [bp - 0x12]
        call next_die
        mov [bp - 0x12], ax
.out:   pop dx
        pop ax
.ret:   ret
spec_hits    dw 0               ; (attacks with specialization's to-hit, for a look in play)
spec_damages dw 0               ; (... its damage)
spec_rates   dw 0               ; (... and their attacks a round changed)

; SPEC_SHEET: ES:BX the sheet of the attack routine's attacker ([BP+10h]); CF set for none (past the
; table's 17). Others kept.
spec_sheet:
        push ax
        mov ax, [bp + 0x10]
        cmp ax, SHEETS_COUNT
        jae .none
        imul ax, ax, SHEET_SIZE
        les bx, [SHEETS_PTR]
        add bx, ax
        pop ax
        clc
        ret
.none:  pop ax
        stc
        ret

; SPEC_OF: DL the attacker's skill with the attack's weapon (SPEC_OF_SHEET, for the attack routine's
; [BP+10h] sheet and [BP+14h] item type). Others kept.
spec_of:
        push bx
        push si
        push es
        mov dl, SPEC_NONE
        call spec_sheet
        jc .out
        mov si, [bp + 0x14]
        call spec_of_sheet
.out:   pop es
        pop si
        pop bx
        ret

; SPEC_OF_SHEET: DL the skill with item type SI of the character whose sheet is at ES:BX (DSCLOG's, on
; the sequel's sheet: the race +12h, the classes +1Bh, their levels +1Eh): SPEC_NONE (no kinds chosen),
; SPEC_PLAIN (not this kind; a dual-classed warrior whose warrior class isn't back yet), SPEC_EXPERT (a
; ranger's, with no fighter or gladiator class; and every ranger's with the bow, chosen or not, but a
; Seeker's), SPEC_SPECIAL, SPEC_MASTER (a fighter's own kind, the first, from 5th level; a Myrmidon's
; second too), SPEC_GRAND (9th). With the kits (KITS): a Battle Mage's, Crusader's or Mind Warrior's
; chosen kind SPEC_EXPERT; a Justifier's expertise SPEC_SPECIAL. Others kept.
spec_of_sheet:
        push ax
        push cx
        push si
        mov dl, SPEC_NONE
        call spec_any
        jz .ret
        mov al, KIT_BATTLE_MAGE ; (a Battle Mage who has changed class: its weapon spec the kit's
        call kit_has            ; alone, nothing while it sleeps, expertise when awake)
        jne .kinds
        cmp word [es:bx + SH_CLASSES + 1], 0
        je .kinds
        call kit_is
        mov dl, SPEC_NONE
        jne .out
        mov dl, SPEC_PLAIN
        call spec_kind
        push ax
        push si
        xor si, si
        call spec_get
        cmp cl, al
        pop si
        pop ax
        jne .out
        mov dl, SPEC_EXPERT
        jmp .out
.kinds: mov dl, SPEC_PLAIN
        call spec_kind
        or cl, cl
        jz .ret
        xor si, si
.slot:  call spec_get
        cmp al, cl
        je .found
        inc si
        cmp si, SPEC_ALL
        jb .slot
        cmp cl, BOW_KIND        ; (not chosen: a ranger's bow all the same, but a Seeker's)
        jne .ret
        call kit_is_b
        db KIT_SEEKER
        je .ret
        xor si, si
.rbow:  mov al, [es:bx + si + SH_CLASSES]
        or si, si               ; (a human's earlier classes once the first's level has passed theirs)
        jz .ron
        cmp byte [es:bx + SH_RACE], CU_HUMAN
        jne .ron
        mov ah, [es:bx + si + SH_LEVELS]
        cmp ah, [es:bx + SH_LEVELS]
        jae .rnext
.ron:   cmp al, 13
        jb .rnext
        cmp al, 16
        ja .rnext
        mov dl, SPEC_EXPERT
        jmp .out                ; (expertise, a Justifier's too: its chosen weapon spec's alone
                                ;   becomes specialization)
.rnext: inc si
        cmp si, 3
        jb .rbow
        jmp .ret
.found: mov dl, SPEC_EXPERT
        mov [cs:spec_found], cl ; (the kind + 1: a Myrmidon's polearm)
        xor ax, ax              ; AH a fighter or gladiator, AL any warrior, CH the fighter level
        xor ch, ch
        push si
        xor si, si
.class: mov cl, [es:bx + si + SH_CLASSES]
        or si, si               ; a human's earlier classes (dual-classed) count only once the
        jz .on                  ; first's level has passed theirs
        cmp byte [es:bx + SH_RACE], CU_HUMAN
        jne .on
        push ax
        mov al, [es:bx + si + SH_LEVELS]
        cmp al, [es:bx + SH_LEVELS]
        pop ax
        jae .next
.on:    cmp cl, CU_FIGHTER
        jne .glad
        mov ax, 0x0101
        mov ch, [es:bx + si + SH_LEVELS]
.glad:  cmp cl, CU_GLADIATOR
        jne .ranger
        mov ax, 0x0101
.ranger:
        cmp cl, 13
        jb .next
        cmp cl, 16
        ja .next
        mov al, 1
.next:  inc si
        cmp si, 3
        jb .class
        pop si
        or al, al
        jnz .warrior
        mov dl, SPEC_PLAIN      ; (a warrior class not back yet)
        call kit_is_b           ; (a Battle Mage's expertise, a Crusader's, a Mind Warrior's)
        db KIT_BATTLE_MAGE
        je .expert
        call war_kit_is
        jne .ret
.expert:
        mov dl, SPEC_EXPERT
        jmp .ret
.warrior:
        or ah, ah
        jz .ret                 ; (a ranger's: expertise)
        mov dl, SPEC_SPECIAL
        or si, si
        jz .master              ; (a fighter's first kind goes on to mastery)
        or ch, ch
        jz .ret                 ; (a gladiator's: specialization)
        call kit_is_b           ; (a Myrmidon's polearm too, by its fighter level)
        db KIT_MYRMIDON
        jne .later
        cmp byte [cs:spec_found], MYRM_POLEARM + 1
        je .master
.later: sub ch, 12              ; (a fighter's other, its pick at 13th: mastery at 17th, grand mastery at
        jbe .ret                ;   21st, as the first's 1st, 5th, 9th; the owner's 2026-11-26)
.master:
        cmp ch, MASTERY
        jb .ret
        mov dl, SPEC_MASTER
        cmp ch, GRAND_MASTERY
        jb .ret
        mov dl, SPEC_GRAND
.ret:   cmp dl, SPEC_EXPERT     ; (a Justifier's expertise with its chosen weapon spec: specialization)
        jne .out
        call kit_is_b
        db KIT_JUSTIFIER
        jne .out
        mov dl, SPEC_SPECIAL
.out:   pop si
        pop cx
        pop ax
        ret

; SPEC_KIND: CL the kind + 1 that item type SI counts as for weapon specialization (0 none):
; KIND_OF_TYPE's, else SPEC_KINDS_OWN's (specialize.spec_kind_of with ravlog's layout:
; ravager.RAV_SPEC_KINDS). Others kept.
spec_kind:
        mov cl, [cs:spec_forced]        ; (EF_LINES_OF's: a kind itself, not an item type's)
        or cl, cl
        jnz .ret
        cmp si, KIND_TYPES
        jae .ret
        mov cl, [cs:si + kind_of_type]
        or cl, cl
        jnz .ret
        push ax
        push bx
        mov ax, si
        mov bx, spec_kinds_own
.own:   cmp byte [cs:bx], 0
        je .done
        cmp al, [cs:bx]
        je .got
        add bx, 2
        jmp .own
.got:   mov cl, [cs:bx + 1]
.done:  pop bx
        pop ax
.ret:   ret
; SPEC_KINDS_OWN: the sequel's weapons with no kind of SL's 22 (KIND_OF_TYPE's 0), and the kind + 1 each
; counts as for specialization alone, as SL's spell-made weapons do (CONJURED_KINDS): its type, the kind
; (the reasoning: DEVELOPMENT-RULES.md, Weapon specialization in Wake of the Ravager). Ends with type 0.
; (The Twohand Sword, Crystal sword, Lotulis, Double Spear, Trikal, Javelin and Darts have KIND_OF_TYPE's
; own kinds, SL's 17-22.)
spec_kinds_own:
        db 13, 1                ; Bloodletter (a 1d8 blade): long sword
        db 81, 5                ; Promere hammer: mace (a hammer, as Spiritual Hammer)
        db 68, 5                ; Jasmine (a mace's 1d6+1): mace
        db 90, 2                ; Shillelagh (the spell's): club
        db 95, 5                ; Spirit hammer (the spell's): mace
        db 87, 14               ; Rainbow (the spell's bow): bow
        db 0

; SPEC_GET: AX the spec in slot SI (kind + 1, 0 none; SL's 22 kinds, as KIND_OF_TYPE has them) of sheet
; ES:BX, in any of its layouts (DSCLOG's: a byte each; packed 5 bits each; SPEC_V2, base 17, or V3).
; SPEC_ANY: ZF clear when a spec is chosen. Others kept.
spec_get:
        cmp si, SPEC_COUNT
        jae spec_get_more
        test byte [es:bx + SPEC_SLOTS + 2], SPEC_PACKED
        jnz .packed
        movzx ax, byte [es:bx + si + SPEC_SLOTS]
        ret
.packed:
        test byte [es:bx + SPEC_SLOTS + 2], SPEC_V2
        jz .five
        call spec_unpack
        movzx ax, byte [cs:si + spec_digits]
        ret
.five:  push ecx
        push edx
        mov edx, [es:bx + SPEC_SLOTS]
        imul cx, si, 5
        shr edx, cl
        movzx ax, dl
        and al, 0x1F
        pop edx
        pop ecx
        ret
; SPEC_GET_MORE: AX the spec in slot SI (4-7: SPEC_ALL) of sheet ES:BX, from SPEC_MORE's three bytes, 5 bits
; a slot (kind + 1, 0 none): a gladiator's 5th to 8th (13th, 17th, 21st, 25th level) and a fighter's second
; (13th), past SL's levels (the owner's 2026-11-26; game.spec_more). Others kept.
spec_get_more:
        push ecx
        push edx
        mov edx, [es:bx + SPEC_MORE - 1]        ; (+44h..+47h: SPEC_MORE's three the top 24 bits)
        shr edx, 8
        lea cx, [si - SPEC_COUNT]
        imul cx, cx, 5
        shr edx, cl
        movzx ax, dl
        and al, 0x1F
        pop edx
        pop ecx
        ret
; SPEC_SET_MORE: AL (kind + 1) into slot SI (4-7) of sheet ES:BX (SPEC_SET's). All registers kept.
spec_set_more:
        push eax
        push ecx
        push edx
        movzx eax, al
        and al, 0x1F
        lea cx, [si - SPEC_COUNT]
        imul cx, cx, 5
        add cx, 8
        shl eax, cl
        mov edx, 0x1F
        shl edx, cl
        not edx
        and edx, [es:bx + SPEC_MORE - 1]
        or edx, eax
        mov [es:bx + SPEC_MORE - 1], edx
        pop edx
        pop ecx
        pop eax
        ret
; SPEC_UNPACK, SPEC_CHOOSE: DSCLOG's (a SPEC_V2 or V3 sheet's four specs in SPEC_DIGITS: the Loader
; writes V3, game.packed_specs).
        SHARED_spec_unpack
spec_rest_from dw 0, 1, 1 + 22, 1 + 22 + 231 ; (REST_SETS' sets of 0, 1, 2 and 3 before each size)
        SHARED_spec_choose
spec_found db 0                 ; (SPEC_OF_SHEET's kind + 1 found among the chosen)
spec_digits times SPEC_COUNT + 1 db 0  ; (one past: SPEC_UNPACK clears four from the second)

        SHARED_spec_any

; MISSILE_RATE: AX (the attacks a round in halves: the weapon type's, +7, as the game has a missile's)
; made a specialist's rate of fire when greater, for skill DL (SPEC_EXPERT or above) with item type SI
; (its kind SPEC_KIND's), the sheet at ES:BX, by the warrior's level (the highest fighter, gladiator or
; ranger level of the classes it has now: 1-6, 7-12, 13 on): DSCLOG's, the bow 3, 4, 5 a round, the
; sling, staff sling and chatkcha 3/2, 2, 5/2, the javelin 3/2, 2, 5/2 and darts 3, 4, 5 (MISSILE_RAV,
; kinds 21 and 22 after the staff sling's); a grand master one more; a kind not chosen (SPEC_PLAIN), from
; 7th level, the specialist's a band lower. Others kept.
MISSILE_KIND equ 13             ; (the chatkcha's kind + 1; then the bow, the sling, the staff sling)
MISSILE_RAV  equ 21             ; (the javelin's kind + 1; then the darts)
missile_halves db 3, 4, 5, 6, 8, 10, 3, 4, 5, 3, 4, 5, 3, 4, 5, 6, 8, 10
missile_rate:
        cmp dl, SPEC_PLAIN
        jb .ret
        push cx
        push dx
        push si
        call spec_kind
        movzx cx, cl
        sub cx, MISSILE_KIND
        jb .out
        cmp cx, 3
        jbe .kind
        sub cx, MISSILE_RAV - MISSILE_KIND - 4  ; (the javelin 4, the darts 5)
        cmp cx, 4
        jb .out
        cmp cx, 5
        ja .out
.kind:
        xor dx, dx              ; DL the specialist's level
        xor si, si
.class: push ax
        mov al, [es:bx + si + SH_CLASSES]
        mov ah, [es:bx + si + SH_LEVELS]
        or si, si               ; (a human's earlier classes once the first's level has passed theirs)
        jz .on
        cmp byte [es:bx + SH_RACE], CU_HUMAN
        jne .on
        cmp ah, [es:bx + SH_LEVELS]
        jae .next
.on:    cmp al, CU_FIGHTER
        je .warrior
        cmp al, CU_GLADIATOR
        je .warrior
        cmp al, 13              ; (a ranger, 13-16)
        jb .next
        cmp al, 16
        ja .next
.warrior:
        cmp ah, dl
        jbe .next
        mov dl, ah
.next:  pop ax
        inc si
        cmp si, 3
        jb .class
        imul cx, cx, 3
        cmp dl, 7
        jb .tier
        inc cx
        cmp dl, 13
        jb .tier
        inc cx
.tier:  mov si, sp
        cmp byte [ss:si + 2], SPEC_PLAIN  ; (the skill: DX, pushed before SI)
        jne .rate
        cmp dl, 7
        jb .out                 ; (a kind not chosen before 7th level: the weapon's own rate)
        dec cx                  ; (from 7th: a specialist's a band lower)
.rate:  mov si, cx
        movzx cx, byte [cs:si + missile_halves]
        cmp cx, ax
        jbe .grand
        mov ax, cx
.grand: mov si, sp
        cmp byte [ss:si + 2], SPEC_GRAND
        jne .out
        add ax, 2               ; (a grand master one more shot, as in melee)
.out:   pop si
        pop dx
        pop cx
.ret:   ret

; NEXT_DIE: AX a die's sides; AX the next greater die size (grand mastery's, Player's Option: Combat
; & Tactics: d2, d3, d4, d6, d8, d10, d12, d20; a die past d20 kept). Others kept.
        SHARED_next_die
die_sizes dw 2, 3, 4, 6, 8, 10, 12, 20
die_sizes_end:

; THE DAM LINES: SL's PROBE_DAM_LINE, PROBE_MISSILE_LINE and PROBE_VIEW_DAM as sites, so the inventory's
; and View Character's "DAM: 1.5x1D8+4" show what the attack does with weapon specialization (SPEC_ATTACKS,
; SPEC_DAMAGE), the cahulaks' off head (CAH_MORE) and the off hand's one a round (OFF_HAND). The sequel's
; line routine (7AF9Eh, SL's 7286Ah; its item DI, the type SI, the creature far at [BP-6], 0 for none)
; pushes the damage bonus, the dice's sides and their count, then the attacks a round (halves) it reads
; for the line's routine (7B1D9h): those three are under the site's return frame (+6 count, +8 sides, +0Ah
; bonus from SP at entry). The kits' as the attack has them: KIT_MELEE's damage and a kit's expertise
; (DAM_KIT_MELEE, DAM_EXPERT), and last Hasted and Slowed as the attack has them (FRAME_SPEED, SPEED_HALVES:
; the sequel's speed routine's effects). What SL's add and these don't: a thri-kreen's chatkcha (OWN_THROWS,
; not ported).
; DAM_LINE (site 70 at 7B19Eh, "mov al,es:[bx+24h]", SL's 72A77h): the melee branch, ES:BX the sheet; AL
; the attacks a round (the game's "mov ah,0" follows).
dam_line:
        mov al, [es:bx + 0x24]
        push bp
        mov bp, sp              ; BP+8 the count, +0Ah the sides, +0Ch the bonus
        push dx
        push ax
        call dam_kit_melee      ; (a Ravager's, a Brute's, a Ghetto Fighter's)
        add [bp + 0x0C], ax
        pop ax
        test word [cs:rules], RULE_SPECIALIZE
        jz .plain
        call spec_of_sheet
        cmp al, 2
        ja .warrior
        call dam_expert         ; (not a warrior: a kit's expertise)
        jmp .bonus
.warrior:
        cmp dl, SPEC_PLAIN
        jne .grand
        dec al
        jmp .bonus
.grand: cmp dl, SPEC_GRAND
        jne .bonus
        add al, 2
.bonus: lea bp, [bp + 0x0A]
        call dam_spec_bonus
.plain: pop dx
        pop bp
        push ax
        movzx ax, al
        call dam_hand
        call frame_speed        ; (Hasted twice, Slowed half: the game's attack's last step)
        mov [cs:dam_halves], al
        pop ax
        mov al, [cs:dam_halves]
        inc word [cs:dam_count]
        iret
; DAM_SPEC_BONUS: skill DL's damage on the line: [BP+2] (the bonus) 2 more for specialization, 3 for
; mastery, and for grand mastery [BP] (the sides) the next die. All registers kept.
dam_spec_bonus:
        cmp dl, SPEC_SPECIAL
        jb .ret
        ja .three
        add word [bp + 2], 2
        ret
.three: add word [bp + 2], 3
        cmp dl, SPEC_GRAND
        jne .ret
        push ax
        mov ax, [bp]
        call next_die
        mov [bp], ax
        pop ax
.ret:   ret
; DAM_HAND: AX the attacks a round (halves) with melee weapon item DI, as the attack has them after the
; skill's (OFF_HAND's order): the cahulaks 2 more (CAH_MORE's), then with RULE_TWO_WEAPONS one a round in
; the left hand. DS the game's; others kept.
dam_hand:
        push bx
        push es
        push ax
        mov ax, di
        call item_is_cahulaks
        pop ax
        jne .two
        add ax, 2
.two:   test word [cs:rules], RULE_TWO_WEAPONS
        jz .out
        cmp ax, 2
        jbe .out
        cmp di, NO_ITEM
        jae .out
        push ax
        imul bx, di, ITEM_SIZE
        les ax, [ITEMS_PTR]
        add bx, ax
        pop ax
        cmp byte [es:bx + ITEM_SLOT], LEFT_HAND
        jne .out
        mov ax, 2
.out:   pop es
        pop bx
        ret
; FRAME_SPEED (SL's): AX the attacks a round (halves) for the creature the line routine's [BP-6] points at
; (its record, far; 0 for none) as SPEED_HALVES gives them. DS the game's; others kept.
frame_speed:
        cmp dword [bp - 6], 0
        je .ret
        push bx
        push dx
        push ax
        mov ax, [bp - 6]
        sub ax, [CREATURES_PTR]
        xor dx, dx
        mov bx, CREATURE_SIZE
        div bx
        mov dx, ax              ; the creature (a party member's combatant number is its own)
        pop ax
        call speed_halves
        pop dx
        pop bx
.ret:   ret
; SPEED_HALVES: AX the attacks a round (halves) of thing DX as the attack has them after all the rest
; (5CF93h: the speed routine 628h:5Ch, 85899h, its 4 doubling them, its 1 halving them), the first of
; SPEED_TABLE's effects it has deciding: Paralyzed (69) and the effects 66 and 56 give speeds that change
; nothing, then Slowed (91) or Impeded (50) half, Hasted (42, 51) twice, the other Slowed (52) half (ravlog's
; SPEED_EFFECTS). DS the game's; others kept.
speed_halves:
        push bx
        push cx
        push si
        mov bx, ax
        mov si, speed_table
.next:  mov cx, [cs:si]         ; CL the effect, CH what it does: 0 nothing, 1 half, 2 twice
        add si, 2
        cmp cl, 0xFF
        je .out
        mov ax, dx
        call has_effect
        jne .next
        cmp ch, 1
        jb .out
        ja .twice
        shr bx, 1
        jmp short .out
.twice: shl bx, 1
.out:   mov ax, bx
        pop si
        pop cx
        pop bx
        ret
speed_table db 69, 0, 66, 0, 56, 0, 91, 1, 50, 1, 42, 2, 51, 2, 52, 1, 0xFF, 0
dam_halves db 0
dam_count  dw 0                 ; (the DAM lines made so, for a look in play)
; DAM_KIT_MELEE: AX what the kits of sheet ES:BX add to damage with item type SI on a DAM line, as the
; attack has it (KIT_DAMAGE's KIT_MELEE: SL's PROBE_DAM_LINE and PROBE_VIEW_DAM), with the kits' rule; else 0.
; Others kept.
dam_kit_melee:
        xor ax, ax
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        call kit_melee
        add [cs:dam_kits], ax
.ret:   ret
; DAM_EXPERT: AL the attacks a round (halves) of one who isn't a warrior, DL its skill, ES:BX its sheet: a
; kit's expertise (EXPERT_HALVES, as SPEC_ATTACKS' EXPERT_OF), the attack's own count of it kept. AH 0;
; others kept.
dam_expert:
        movzx ax, al
        push word [cs:kit_rates]
        push ax
        call expert_halves
        pop word [cs:dam_expert_was]
        cmp ax, [cs:dam_expert_was]
        je .same
        inc word [cs:dam_kits]
.same:  pop word [cs:kit_rates]
        ret
dam_expert_was dw 0
dam_kits   dw 0                 ; (the DAM lines a kit changed, for a look in play)
; MISSILE_LINE (site 71 at 7B124h, "mov al,es:[bx+7]", SL's 729FFh): the missile branch (and with no
; creature, an item box's, a melee weapon's too), ES:BX the type's record; AL the type's attacks a round.
; With a creature: a specialist's rate of fire (MISSILE_RATE) and the skill's damage, as SPEC_DAMAGE. With
; none, at least one a round (SL's: the line shows no rate, as the game's did before DAM_HALF).
missile_line:
        mov al, [es:bx + 7]
        cmp dword [bp - 6], 0
        jne .held
        cmp al, 2
        jae .ret
        mov al, 2
.ret:   iret
.held:  test word [cs:rules], RULE_SPECIALIZE
        jz .speed
        push bp
        mov bp, sp              ; BP+8 the count, +0Ah the sides, +0Ch the bonus
        push bx
        push dx
        push es
        movzx ax, al
        push ax
        mov bx, [bp]            ; (the line routine's BP: its creature)
        les bx, [ss:bx - 6]
        mov ax, [es:bx + 4]     ; its sheet
        cmp ax, SHEETS_COUNT
        jae .none
        imul ax, ax, SHEET_SIZE
        les bx, [SHEETS_PTR]
        add bx, ax
        call spec_of_sheet
        pop ax
        call missile_rate
        lea bp, [bp + 0x0A]
        call dam_spec_bonus
        inc word [cs:dam_count]
        jmp .out
.none:  pop ax
.out:   pop es
        pop dx
        pop bx
        pop bp
.speed: movzx ax, al
        call frame_speed        ; (Hasted twice, Slowed half, whatever the rules: the attack's last step)
        iret
; VIEW_DAM (site 72 at 6CAC9h, "mov [bp-0Eh],dx", SL's 64EB6h PROBE_VIEW_DAM): View Character's line, DX the
; damage bonus it stores; its [BP-6] the attacks a round (halves, the sheet's +24h), [BP-2] the dice's
; count, [BP-4] their sides, [BP-0Ah] the weapon's item; the character on show at USE_WHO_SEG:USE_WHO_OFF.
; A missile weapon (its type's +6 above 1) keeps the game's attacks (as SL's).
view_dam:
        mov [bp - 0x0E], dx
        pusha
        push es
        mov ax, [bp - 0x0A]     ; the item, its type
        cmp ax, NO_ITEM
        jae .out
        imul ax, ax, ITEM_SIZE
        les bx, [ITEMS_PTR]
        add bx, ax
        mov si, [es:bx + ITEM_TYPE]
        mov di, [bp - 0x0A]
        mov dl, SPEC_NONE
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov ax, [es:USE_WHO_OFF] ; the character on show, its sheet
        cmp ax, SHEETS_COUNT
        jae .out
        imul ax, ax, SHEET_SIZE
        les bx, [SHEETS_PTR]
        add bx, ax
        mov [cs:view_sheet], bx
        mov [cs:view_sheet + 2], es
        call dam_kit_melee      ; (a Ravager's, a Brute's, a Ghetto Fighter's)
        add [bp - 0x0E], ax
        test word [cs:rules], RULE_SPECIALIZE
        jz .kind
        call spec_of_sheet
.kind:  imul bx, si, TYPE_SIZE
        les ax, [ITEM_TYPES_PTR]
        add bx, ax
        cmp byte [es:bx + TYPE_MELEE], 1
        ja .bonus               ; (a missile weapon: its rate kept)
        mov ax, [bp - 6]
        cmp ax, 2
        ja .warrior
        les bx, [cs:view_sheet]
        call dam_expert         ; (not a warrior: a kit's expertise)
        jmp .hand
.warrior:
        cmp dl, SPEC_PLAIN
        jne .grand
        dec ax
        jmp .hand
.grand: cmp dl, SPEC_GRAND
        jne .hand
        add ax, 2
.hand:  call dam_hand
        mov [bp - 6], ax
.bonus: cmp dl, SPEC_SPECIAL
        jb .done
        ja .three
        add word [bp - 0x0E], 2
        jmp .done
.three: add word [bp - 0x0E], 3
        cmp dl, SPEC_GRAND
        jne .done
        mov ax, [bp - 4]
        call next_die
        mov [bp - 4], ax
.done:  call view_material      ; (a weak material's damage, as the game's attack and the inventory's line have it)
        mov ax, ds              ; (Hasted twice, Slowed half, as the attack: whatever the rules, a missile
        add ax, USE_WHO_SEG     ;  weapon too)
        mov es, ax
        mov dx, [es:USE_WHO_OFF]
        mov ax, [bp - 6]
        call speed_halves
        mov [bp - 6], ax
        inc word [cs:dam_count]
.out:   pop es
        popa
        iret
view_sheet dd 0

; VIEW_MATERIAL (SL's, in PROBE_VIEW_DAM): the damage bonus [BP-0Eh] less a weak material's, as the game's
; attack and the inventory's line have it and View Character's didn't (one more than both: an Obsidian
; Dagger's 1D4+4 beside the inventory's 1D4+3, 2026-11-28): a weapon with no plus (ITEM_PLUS; a power
; alone doesn't spare it) whose type isn't marked 80h (a club's, a staff's) nor 40h (no material) does 2
; less in wood and 1 less in bone, stone or obsidian (TYPE_KIND's low nibble). The item [BP-0Ah]. DS the
; game's; all kept.
view_material:
        push ax
        push bx
        push es
        mov ax, [bp - 0x0A]
        cmp ax, NO_ITEM
        jae .out
        imul ax, ax, ITEM_SIZE
        les bx, [ITEMS_PTR]
        add bx, ax
        cmp byte [es:bx + ITEM_PLUS], 0
        jne .out                ; (a plus: none)
        imul ax, [es:bx + ITEM_TYPE], TYPE_SIZE
        les bx, [ITEM_TYPES_PTR]
        add bx, ax
        mov al, [es:bx + TYPE_KIND]
        test al, 0x80 | 0x40
        jnz .out                ; (a club's, a staff's; 40h: no material)
        and al, 0x0F
        cmp al, 3
        ja .out                 ; (metal, leather)
        dec word [bp - 0x0E]
        or al, al
        jnz .out
        dec word [bp - 0x0E]    ; (wood: 2)
.out:   pop es
        pop bx
        pop ax
        ret

; ---- The Effects screen's lines: DSCLOG's PROBE_EF_ROWS and PROBE_EF_CLICK ----
; EF_ROWS (site 73 at 8AFA9h, "pop di / pop si / leave", SL's 7F13Eh): the end of the Effects screen's
; routine that puts the selected character's effects in their cells (8AC6Fh, SL's 7EDFAh: run when the
; screen opens and when another character is picked; [BP-4] the cells it has used, 23h at most). With the
; lower panel free (the game puts effects there only past EF_CELLS), the character's kits (with the kits'
; rule: RULE_HI_KITS) and weapon kinds (RULE_SPECIALIZE) are listed there, in the game's text as the USE
; screen's spell slots are (C_DRAW_LINE, at the same place): a line a kit, then a line for the skill and a
; line a kind. Then the routine's last three instructions, and on to its RETF. The character on show is
; USE_WHO's (370h:0B44h), the window WIN_SHOWN (the routine's own [1431h]).
; EF_CLICK (site 74 at 8AB1Ah, "mov si,[bp+8]", SL's 7EC9Eh): the Effects screen's handler for its cells
; (8AB13h; [BP+8] the cell's button, from EF_CELL_ID, [BP+0Ah] the event): a click on the lower panel while
; the lines take more than a page (EF_COUNT above EF_LINES) shows the next page (EF_NEXT): the window drawn
; again as the handler does after an effect's click (its "call 140:60Dh" at 8AC62h with [1431h]), the way
; back in a frame the overlay manager can fix up, and out of the handler (8AC6Ah). Else SI [BP+8].
; What SL's has and this doesn't: a Shinobi's read languages and the game's own party's lines (SL's).
EF_CELLS     equ 21                 ; (the upper panel's)
EF_LINES     equ 5
EF_CELL_ID   equ 0x2BCD
EF_CLICKED   equ 0x20               ; (the events: 2 the pointer onto a cell, 4 a button down, 20h a click)
EF_CLICK_OUT equ 0x8AC6A - 0x8AB1D  ; (the handler's way out, less the address after the site)
EF_REDRAW_CALL equ 0x8AC63 - 0x8AB1D ; (its "call 140:60Dh"'s operand, less that)
EF_PARTY     equ 4
ef_rows:
        sti
        pushad
        push es
        cmp word [bp - 4], EF_CELLS
        jg .pops
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov ax, [es:USE_WHO_OFF]
        cmp ax, EF_PARTY
        jae .pops
        mov dx, ds
        add dx, USE_TEXT_SEG
        mov [cs:c_draw + 2], dx
        mov word [cs:c_draw], USE_TEXT_OFF
        mov edx, [WIN_SHOWN]
        mov [cs:c_winptr], edx
        inc word [cs:ef_draws]
        call ef_draw
.pops:  pop es
        popad
        pop word [cs:ef_back]           ; the replaced "pop di / pop si / leave", under the frame
        pop word [cs:ef_back + 2]
        popf
        pop di
        pop si
        leave
        jmp far [cs:ef_back]            ; (the routine's RETF)
ef_click:
        mov si, [bp + 8]
        cmp word [bp + 0x0A], EF_CLICKED
        jne .iret
        cmp si, EF_CELL_ID + EF_CELLS
        jb .iret
        cmp word [cs:ef_count], EF_LINES
        ja .page
.iret:  iret
.page:  sti
        pushad
        push es
        mov bx, sp              ; the frame at BX+34: IP, CS, flags
        mov byte [cs:ef_next], 1
        push ds
        lds si, [ss:bx + 34]    ; (the window redraw's far address, in its call, as fixed up)
        mov eax, [si + EF_REDRAW_CALL]
        pop ds
        mov [cs:ef_far], eax
        push word [ss:bx + 36]
        mov ax, [ss:bx + 34]
        add ax, EF_CLICK_OUT
        push ax
        push bp
        mov bp, sp
        push dword [WIN_SHOWN]
        call far [cs:ef_far]
        add sp, 4
        pop bp
        pop ax                  ; (the way back, as the overlay manager has left it)
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
        pop es
        popad
        iret

; EF_DRAW: party member AX's lines (DS the game's): a line for each kit, the oldest class's first (EF_KIT_LINE,
; " (ASLEEP)" after a kit asleep), then its weapon kinds, the skill's line where it changes, then the kind's
; (EF_LINES_OF). The panel has room for EF_LINES: with more, a page at a time, EF_LINES - 1 of them and EF_MORE
; under them; a click on the panel (EF_CLICK) shows the next page, after the last the first again.
ef_draw:
        imul ax, ax, SHEET_SIZE
        les bx, [SHEETS_PTR]
        add bx, ax
        mov byte [cs:ef_drawing], 0     ; (counted first)
        mov word [cs:ef_index], 0
        call ef_lines_of
        mov cx, [cs:ef_index]           ; (CX the lines)
        xor ax, ax                      ; the page: the first, or the next if asked (EF_NEXT)
        cmp byte [cs:ef_next], 0
        je .page
        mov byte [cs:ef_next], 0
        mov ax, [cs:ef_after]           ; (the line after the last one shown)
        cmp ax, cx
        jb .page
        xor ax, ax
.page:  cmp cx, EF_LINES
        ja .set
        xor ax, ax
.set:   mov [cs:ef_first], ax
        mov [cs:ef_count], cx
        mov word [cs:ef_rows_n], EF_LINES
        cmp cx, EF_LINES
        jbe .draw
        dec word [cs:ef_rows_n]
.draw:  mov byte [cs:ef_drawing], 1
        mov word [cs:ef_index], 0
        mov word [cs:ef_used], 0
        mov word [cs:ef_y], USE_FIRST_Y
        call ef_lines_of
        cmp cx, EF_LINES
        jbe .ret
        mov word [cs:ef_y], USE_FIRST_Y + (EF_LINES - 1) * USE_STEP
        mov si, ef_more
        call ef_put
.ret:   ret

; EF_LINES_OF: EF_DRAW's lines of the character whose sheet is ES:BX, each through EF_LINE.
ef_lines_of:
        mov byte [cs:ef_last], 0xFF
        mov word [cs:ef_head], 0
        call kit_place       ; (a line for each kit, the oldest class's first; a human's kit
        jc .specs               ;   asleep until its class is passed, as the game's classes are)
.kit:   call kit_at
        jz .kit_next
        call ef_kit_line
        call ef_line
.kit_next:
        dec di
        jns .kit
.specs: test word [cs:rules], RULE_SPECIALIZE
        jz .ret
        xor di, di
.slot:  cmp di, SPEC_ALL
        jb .chosen
        mov si, BOW_KIND                ; (then the bow, a ranger's whether chosen or not, unless
        push di                         ;   it is among the chosen: SPEC_OF_SHEET's skill with it)
        xor di, di
.bow:   push si
        mov si, di
        call spec_get
        pop si
        cmp al, BOW_KIND
        je .bow_had
        inc di
        cmp di, SPEC_ALL
        jb .bow
        pop di
        jmp .kind_of
.bow_had:
        pop di
        jmp .ret
.chosen:
        mov si, di
        call spec_get
        mov si, ax
.kind_of:
        or si, si
        jz .next
        mov ax, si
        mov [cs:spec_forced], al        ; (SPEC_OF_SHEET's skill with that kind)
        dec si
        mov [cs:ef_kind], si
        call spec_of_sheet
        mov byte [cs:spec_forced], 0
        mov al, 3
        cmp dl, SPEC_EXPERT
        je .skill
        cmp dl, SPEC_SPECIAL
        jb .next                ; (a warrior class not back yet: none)
        mov al, dl
        sub al, SPEC_SPECIAL
.skill: cmp al, [cs:ef_last]
        je .kind
        mov [cs:ef_last], al
        movzx si, al
        shl si, 1
        mov si, [cs:si + ef_skills]
        mov byte [cs:ef_is_head], 1
        call ef_line
        mov byte [cs:ef_is_head], 0
.kind:  mov si, [cs:ef_kind]
        cmp si, KIND_COUNT
        jae .next
        shl si, 1
        mov si, [cs:si + ef_kinds]
        call ef_line
.next:  inc di
        cmp di, SPEC_ALL
        jbe .slot
.ret:   ret

; EF_LINE: CS:SI EF_DRAW's next line: counted (EF_INDEX), and put on the panel (EF_PUT) if drawing and on
; the page shown. All registers kept. (DSCLOG's.)
ef_line:
        push ax
        mov ax, [cs:ef_index]
        inc word [cs:ef_index]
        cmp byte [cs:ef_is_head], 0     ; (a skill's line: the kinds' under it, EF_HEAD)
        je .drawing
        mov [cs:ef_head], si
.drawing:
        cmp byte [cs:ef_drawing], 0
        je .out
        cmp ax, [cs:ef_first]
        jb .out
        push ax
        mov ax, [cs:ef_used]
        cmp ax, [cs:ef_rows_n]
        pop ax
        jae .out
        cmp word [cs:ef_used], 0        ; (the page's first line: a kind's, its skill's line over it)
        jne .put
        cmp ax, 0
        je .put
        cmp byte [cs:ef_is_head], 0
        jne .put
        cmp byte [cs:si], ' '
        jne .put
        cmp word [cs:ef_head], 0
        je .put
        push si
        mov si, [cs:ef_head]
        call ef_put
        pop si
        inc word [cs:ef_used]
.put:   cmp byte [cs:ef_is_head], 0      ; (a skill's line last on a page: on the next, with its kinds)
        je .shown
        push ax
        mov ax, [cs:ef_used]
        inc ax
        cmp ax, [cs:ef_rows_n]
        pop ax
        jb .shown
        cmp word [cs:ef_count], EF_LINES
        jbe .shown
        mov ax, [cs:ef_rows_n]
        mov [cs:ef_used], ax
        jmp .out
.shown: call ef_put
        inc word [cs:ef_used]
        inc ax
        mov [cs:ef_after], ax
.out:   pop ax
        ret
; EF_PUT: CS:SI on the panel's next line (all registers kept: the game's text routine changes ES)
        SHARED_ef_put

; THE KITS ON THE EFFECTS SCREEN: EF_LINES_OF's kit lines, by the KITS section's KIT_PLACE and KIT_AT (the
; sequel's sheet: the kit byte at +3Dh, the race +12h, the classes +1Bh, their levels +1Eh). The names are
; the tail's, as DSCLOG's (KIT_NAMES and KIT_SHORT, kit_names_table.inc, read through TAIL_FS).
; EF_KIT_LINE: CS:SI the line naming kit AL (EF_KIT_AT's, not 0: "KIT: RAVAGER"), a long name shorter
; (KIT_SHORT), " (ASLEEP)" after it if the kit of the class at place DI sleeps (a human's first class,
; until the class it has now is of a higher level). Others kept.
ef_kit_line:
        push ax
        push cx
        push di
        push fs
        call tail_fs
        mov si, kit_short
.short: cmp byte [fs:si], 0
        je .long
        cmp [fs:si], al
        je .found
.skip:  inc si
        cmp byte [fs:si], 0
        jne .skip
        inc si
        jmp .short
.found: inc si
        jmp .name
.long:  call kit_name_ptr
.name:  mov di, ef_kit_text + 5 ; (after "KIT: ")
.char:  fs lodsb
        mov [cs:di], al
        inc di
        or al, al
        jnz .char
        pop fs
        pop cx                  ; (the place)
        push cx
        jcxz .out               ; (asleep: a later place, its level not passed by the first's)
        push bx
        add bx, cx
        mov al, [es:bx + SH_LEVELS]
        pop bx
        cmp [es:bx + SH_LEVELS], al
        ja .out
        dec di
        mov si, ef_asleep
.copy:  cs lodsb
        mov [cs:di], al
        inc di
        or al, al
        jnz .copy
.out:   mov si, ef_kit_text
        pop di
        pop cx
        pop ax
        ret

; KIT_NAME_PTR: SI kit AL's name in KIT_NAMES (AL not 0), in the tail (TAIL_FS), as DSCLOG's. Others kept.
kit_name_ptr:
        push ax
        push cx
        push fs
        call tail_fs
        movzx cx, al            ; (the kit's place in KIT_NAMES, from 1: (class - 1) * 3 + kit)
        and cl, 3
        shr al, 2
        dec al
        mov ah, 3
        mul ah
        add cx, ax
        mov si, kit_names
.skip:  dec cx
        jz .out
.past:  fs lodsb
        or al, al
        jnz .past
        jmp .skip
.out:   pop fs
        pop cx
        pop ax
        ret
section tail                    ; (the kits' names: the tail's, as DSCLOG's, 2026-11-28's memory pass)
%include "kit_names_table.inc"
section image
ef_asleep    db ' (ASLEEP)', 0
ef_kit_text  db 'KIT: '
             times 24 db 0          ; (the longest name, 14, and " (ASLEEP)")
ef_more      db 'MORE: CLICK HERE', 0
ef_skills    dw .s0, .s1, .s2, .s3
.s0     db 'SPECIALIZED IN', 0
.s1     db 'MASTER OF', 0
.s2     db 'GRAND MASTER OF', 0
.s3     db 'EXPERT IN', 0
ef_kinds     dw .k0, .k1, .k2, .k3, .k4, .k5, .k6, .k7, .k8, .k9, .k10, .k11, .k12, .k13, .k14, .k15
             dw .k16, .k17, .k18, .k19, .k20, .k21
.k0     db '  LONG SWORD', 0
.k1     db '  CLUB', 0
.k2     db '  DAGGER', 0
.k3     db '  SHORT SWORD', 0
.k4     db '  MACE', 0
.k5     db '  AXE', 0
.k6     db '  GREAT AXE', 0
.k7     db '  PICK', 0
.k8     db '  QUARTERSTAFF', 0
.k9     db '  POLEARM', 0
.k10    db '  GYTHKA', 0
.k11    db '  CAHULAKS', 0
.k12    db '  CHATKCHA', 0
.k13    db '  BOW', 0
.k14    db '  SLING', 0
.k15    db '  STAFF SLING', 0
.k16    db '  TWO-HANDED SWORD', 0
.k17    db '  LOTULIS', 0
.k18    db '  DOUBLE SPEAR', 0
.k19    db '  TRIKAL', 0
.k20    db '  JAVELIN', 0
.k21    db '  DARTS', 0
spec_forced  db 0
ef_back      dd 0
ef_far       dd 0
ef_draws     dw 0               ; (EF_ROWS' draws, for a look in play)
ef_drawing   db 0
ef_index     dw 0
ef_first     dw 0
ef_rows_n    dw 0
ef_count     dw 0
ef_next      db 0
ef_after     dw 0
ef_used      dw 0
ef_head      dw 0
ef_is_head   db 0
ef_y         dw 0
ef_kind      dw 0
ef_last      db 0

; ---- KITS: DSCLOG's RULE_KITS (rules_hi bit 0: dsloader/kits.py, kitpages.py) in the sequel ----
; The transferred party keeps its kits (the transfer's sheet +3Dh, SL's +43h: KIT_BYTE, two bits for
; each class place, 40h OWN_BIT, 80h Friends known). Their rules, as DSCLOG's (DEVELOPMENT-KITS.md, Where
; each effect goes), at the sequel's sites:
; - AC (KIT_AC, from PROBE_AC: the AC function's end, 5D6E6h, SL's 58F8Dh; its [BP+6] the combatant);
; - to hit (KIT_ATTACKS, from OFF_HAND at the attacks' store, 5CEE8h, SL's PROBE_ATTACKS: KIT_TO_HIT,
;   WAR_HIT, KIT_EXTRA off the THAC0 [BP+0Ah]) and the attacks a round (EXPERT_HALVES from SPEC_ATTACKS;
;   Wild Fighting's one more, KIT_WILD_MORE); damage (KIT_DAMAGE, from SPEC_DAMAGE, site 51: SL's
;   PROBE_SPEC_DAMAGE's KIT_ATTACK_DAMAGE, KIT_EXTRA, WILD_PASSED; the bonus the sequel's [BP-14h]);
; - the weapon specs' kit parts (SPEC_OF_SHEET: a Battle Mage's, Crusader's, Mind Warrior's expertise,
;   a Justifier's made specialization, a Myrmidon's second kind on to mastery, a Seeker's bow none);
; - saves (KIT_SAVE, from PROT_SAVE, site 44: SL's PROBE_RING_SAVE's), thief skills (KIT_SKILL and a
;   Swashbuckler's bad luck, from BELT_SITE, site 20: SL's PROBE_BELT), from behind and backstab
;   (KIT_REAR, from MISSILE_REAR: SL's PROBE_STEALTH's), movement (KIT_MOVE, from CAH_MOVE: SL's
;   PROBE_MOVE), the two-weapon penalty (KIT_TWO, from PROBE_TWO), initiative (KIT_INIT, site 60 at
;   5B7E9h, SL's PROBE_INIT at 5750Eh); the Elementalist's second sphere (EL_SPHERE, sites 90-92);
; - spell slots (SL's PROBE_SLOTS and PROBE_SLOT_LEVEL, from ADND_SLOTS, site 34: SLOT_BEHIND, BEHIND_LEAST,
;   KIT_TABLE; a Shinobi's thief class asked its wizard slots, SHINOBI_MAGE, site 190); the Seeker's and
;   Justifier's casting level (RANGER_DROP, KIT_RANGER_CAST, site 61); the Shinobi's wizard spells
;   (THE SHINOBI'S SPELLS: its list, picks, scrolls and casting level, sites 90-92, 209-210);
; - PSP costs, a Mind Warrior's PSP, the level up's hit dice and a Battle Mage's casting after a hit (KIT PSP
;   COSTS, PSP, HIT DICE AND CASTING AFTER A HIT, sites 191-199), and a kit's hit die and PSP at creation
;   (sites 200, 201, and KIT_REROLL on the kit page).
; - a spell's level for its duration and damage (SL's PROBE_SPELL_LEVEL: KIT_CAST_LEVEL, site 205: the
;   Arcanist's, Spirit Caller's, Wasteland Seer's), the cures (PROBE_CURE: KIT_CURE, site 206; CELL_HEAL's
;   CELL_MORE), the Cause Wounds spells (AV_CAUSE: AVENGER_AREA, AVENGER_ONE, sites 207-208), the spells
;   known (EL_SPHERE's HEALER_COSMOS and KIT_BARS: the Healer's cosmos, the spells a kit never knows).
; The Loader's header bytes for them are DSCLOG's: KIT_OUTDOORS (+350), KIT_DANCE (+351), KIT_WILD
; (+355), BAD_LUCK (+1862); COSMOS_MORE (+2060) and the counters after it DSCLOG2's own. Not here (yet):
; poison, arrows, gear (KIT_FORBIDS, KIT_ALLOWS), the Effects lines.
RULE_HI_KITS equ 1
KIT_BYTE     equ 0x3D               ; (SL's +43h: ravager.sheet_field)
KIT_OPEN     equ 0xFF               ; (KIT_BYTE while the player has taken the kit back: none chosen)
SH_BASE_AC   equ 0x21               ; (SL's +27h)
CR_THAC0     equ 0x16               ; (a creature's THAC0: SL's +1Fh)
CR_STATUS    equ 0x14               ; (... its status, 0 New, 1 Okay: SL's +1Ch)
MULTI_FIRST  equ 9
KIT_HEALER   equ 6
KIT_CRUSADER equ 7
KIT_GROVE_WARDEN equ 9
KIT_WANDERER equ 11
KIT_MYRMIDON equ 13
KIT_SENTINEL equ 14
KIT_RAVAGER  equ 15
KIT_CHAMPION equ 17
KIT_TWIN_BLADE equ 18
KIT_BRUTE    equ 19
KIT_SCHOLAR  equ 21
KIT_BATTLE_MAGE equ 22
KIT_MIND_WARRIOR equ 26
KIT_STALKER  equ 29
KIT_JUSTIFIER equ 30
KIT_SEEKER   equ 31
KIT_SWASHBUCKLER equ 33
KIT_ASSASSIN equ 34
KIT_BATTLE_DANCER equ 37
KIT_SHADOWBLADE equ 41
KIT_SCOUT    equ 42
KIT_AVENGER  equ 45
KIT_RESCUER  equ 49
KIT_GHETTO   equ 53
KIT_WAYFINDER equ 54
KIT_WILD_FURY equ 77
KT_MISSILE   equ 0x02               ; (an item type's +0: a missile weapon; +0Bh 40h two-handed, TYPE_FLAGS)
DAGGER_KIND  equ 2

; KIT_IS: ZF set if sheet ES:BX has kit AL (the creation screen's class x 4 + the kit, kitpages.kit_ids)
; awake (KIT_AWAKE), KIT_WHERE then its class's place (KIT_LEVEL, KIT_CLASS_OF_SHEET); ZF clear if not.
; KIT_HAS: the same, asleep too. All registers kept. (DSCLOG's, the sequel's sheet.)
        SHARED_kit_is
        SHARED_kit_has
        SHARED_kit_find
kit_where dw 0

; OWN_RACE_B: AL the race of sheet ES:BX if the Loader marked it one of the sequel's own party (KIT_BYTE's
; OWN_BIT, kits.own_race: Gerakis, Thy'rokh, Terrannus, Ar'Anda), the kits' rule on; else 0, ZF set. OWN_HAS:
; ZF set if sheet ES:BX has class AL. Others kept.
OWN_BIT      equ 0x40
; KIT_OPEN_AT: ZF set if sheet ES:BX's kit byte is KIT_OPEN, a kit taken back on the creation screen: 0FFh
; on any sheet but a human's with three classes, whose 0FFh is its kits (each class's third), OWN_BIT and
; Friends known, which the kits can make (Terrannus could: game.kit_open, 2026-11-27's code audit). A sheet
; being made has one class, so its 0FFh is always KIT_OPEN. All registers kept.
kit_open_at:
        cmp byte [es:bx + KIT_BYTE], KIT_OPEN
        jne .out
        cmp byte [es:bx + SH_RACE], CU_HUMAN
        jne .yes
        cmp byte [es:bx + SH_CLASSES + 2], 0
        jne .out                ; (ZF clear: a third class)
.yes:   cmp al, al
.out:   ret
own_race_b:
        xor al, al
        test word [cs:rules_hi], RULE_HI_KITS
        jz .out
        call kit_open_at
        je .out
        test byte [es:bx + KIT_BYTE], OWN_BIT
        jz .out
        mov al, [es:bx + SHEET_RACE]
.out:   or al, al
        ret
own_has:
        cmp [es:bx + SH_CLASSES], al
        je .ret
        cmp [es:bx + SH_CLASSES + 1], al
        je .ret
        cmp [es:bx + SH_CLASSES + 2], al
.ret:   ret
; OWN_DRUID: AL Thy'rokh's druid level (a thri-kreen of the own party with no psionicist class: a Grove
; Warden's AC, kits.own_warden_level), else 0 (ZF set). Sheet ES:BX; others kept.
OWN_KREEN    equ 8
OWN_PSI      equ 12
own_druid:
        push si
        call own_race_b
        cmp al, OWN_KREEN
        jne .none
        mov al, OWN_PSI
        call own_has
        je .none
        xor si, si
.each:  mov al, [es:bx + si + SH_CLASSES]
        sub al, 5                       ; (the druids' classes 5-8)
        cmp al, 3
        jbe .found
        inc si
        cmp si, 3
        jb .each
.none:  xor al, al
        jmp .out
.found: mov al, [es:bx + si + SH_LEVELS]
.out:   pop si
        or al, al
        ret

; KIT_AT: AL the kit of the class at place DI (0-2) of sheet ES:BX, ZF clear; 0 and ZF set for none.
; Others kept.
kit_at:
        push cx
        push di
        xor cl, cl
        test word [cs:rules_hi], RULE_HI_KITS
        jz .out
        mov cx, di
        call kit_place
        jc .none
        xchg cx, di             ; (CX the oldest's place, DI the one asked for)
        sub cx, di
        jb .none
        shl cl, 1
        call kit_open_at
        je .none
        mov ch, [es:bx + KIT_BYTE]
        shr ch, cl
        and ch, 3
        jz .none
        dec ch
        push ax                 ; (two classes at once: their multiclass group's kit, one it has)
        call multi_group
        mov cl, al
        pop ax
        or cl, cl
        jz .class
        movzx di, cl
        cmp ch, [cs:di + multi_count - MULTI_FIRST]
        jae .none
        jmp .kit
.class: movzx di, byte [es:bx + di + SH_CLASSES]  ; (its class, 1-17)
        dec di
        cmp di, 16
        ja .none
        mov cl, [cs:di + kit_class_of]
.kit:   shl cl, 2
        add cl, ch
        inc cl
        jmp .out
.none:  xor cl, cl
.out:   mov al, cl
        pop di
        pop cx
        or al, al
        ret

; KIT_PLACE: DI the place (0-2) of the class sheet ES:BX's kit was chosen with: 0 for one class; a human
; who has changed class, its first (the last of its classes); 0 for a multiclass group's. CF set for
; more than one class otherwise. Others kept.
kit_place:
        xor di, di
        cmp word [es:bx + SH_CLASSES + 1], 0
        je .ok
        cmp byte [es:bx + SH_RACE], CU_HUMAN
        jne .multi
        inc di
        cmp byte [es:bx + SH_CLASSES + 2], 0
        je .ok
        inc di
.ok:    clc
        ret
.multi: push ax
        call multi_group
        or al, al
        pop ax
        jnz .ok
        stc
        ret

; KIT_AWAKE: CF set if the kit of sheet ES:BX, its class at place DI, sleeps (a human's first class
; until the class it has now is of a higher level). Others kept.
kit_awake:
        or di, di
        jz .yes
        push ax
        mov al, [es:bx + di + SH_LEVELS]
        cmp [es:bx + SH_LEVELS], al
        pop ax
        ja .yes
        stc
        ret
.yes:   clc
        ret

; KIT_LEVEL: AL the level of the class of the kit KIT_IS last found (KIT_WHERE) on sheet ES:BX.
kit_level:
        push di
        mov di, [cs:kit_where]
        mov al, [es:bx + di + SH_LEVELS]
        pop di
        ret

; MULTI_GROUP: AL the multiclass group (9-19, kitpages.MULTI) of sheet ES:BX: two or three classes at
; once, not a human's, its race and classes one of MULTI_TABLE's; else 0. MULTI_GROUP_CR the same for
; the sheet being made on the creation screen, its classes 1-8 (KIT PAGE). Others kept.
        SHARED_multi_group
        SHARED_multi_group_cr
multi_find:
        push cx
        push dx
        push di
        xor al, al
        xor dx, dx              ; DX the classes' bits (1 shl the creation class)
        cmp byte [es:bx + SH_RACE], CU_HUMAN
        je .out
        mov di, SH_CLASSES
.class: movzx cx, byte [es:bx + di]
        cmp di, SH_CLASSES + 2
        jne .any
        jcxz .classes           ; (two classes: no third)
.any:   dec cx
        cmp cx, 16
        ja .out                 ; (none: one class)
        push si
        add si, cx
        mov cl, [cs:si]
        pop si
        or cl, cl
        jz .out
        bts dx, cx
        inc di
        cmp di, SH_CLASSES + 3
        jb .class
.classes:
        mov ch, [es:bx + SH_RACE]
        mov si, multi_table
        mov al, MULTI_FIRST
.find:  cmp byte [cs:si], 0
        je .none
        cmp [cs:si], ch
        jne .skip
        cmp [cs:si + 1], dx
        je .out
.skip:  add si, 3
        inc al
        jmp .find
.none:  xor al, al
.out:   pop di
        pop dx
        pop cx
        pop si
        ret
; (race, the classes' bits) by group from 9 (DSCLOG's MULTI_TABLE); each group's kits, how many
multi_table db 3
            dw (1 << 1) | (1 << 3)      ; elf cleric/fighter: Battle Dancer
            db 4
            dw (1 << 3) | (1 << 8)      ; half-elf fighter/thief: Shadowblade, Military Scout
            db 4
            dw (1 << 2) | (1 << 3)      ; half-elf druid/fighter: Wilderness Avenger
            db 4
            dw (1 << 1) | (1 << 7)      ; half-elf cleric/ranger: Rescuer
            db 2
            dw (1 << 3) | (1 << 8)      ; dwarf fighter/thief: Ghetto Fighter, Wayfinder
            db 4
            dw (1 << 3) | (1 << 5)      ; half-elf fighter/preserver: Spellarcher
            db 5
            dw (1 << 3) | (1 << 6)      ; half-giant fighter/psionicist: Titan Mind
            db 6
            dw (1 << 3) | (1 << 8)      ; halfling fighter/thief: Poisoner
            db 6
            dw (1 << 1) | (1 << 6)      ; halfling cleric/psionicist: Spirit Caller
            db 8
            dw (1 << 2) | (1 << 3) | (1 << 6)   ; thri-kreen druid/fighter/psionicist: Wasteland Seer
            db 7
            dw (1 << 2) | (1 << 3)      ; mul druid/fighter: Wild Fury
            db 0
multi_count  db 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1
kit_class_of db 1, 1, 1, 1, 2, 2, 2, 2, 3, 4, 5, 6, 7, 7, 7, 7, 8   ; (a sheet's class, 1-17: the creation screen's)
multi_same   db 1, 2, 3, 4, 5, 6, 7, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0   ; (the sheet being made's classes, 1-8)

; KIT_SHEET: ES:BX the sheet of creature AX (its record's +4). KIT_SHEET_AX: of sheet number AX.
; All registers but ES:BX kept.
kit_sheet:
        push ax
        imul ax, ax, CREATURE_SIZE
        les bx, [CREATURES_PTR]
        add bx, ax
        mov ax, [es:bx + 4]
        jmp kit_sheet_n
kit_sheet_ax:
        push ax
kit_sheet_n:
        imul ax, ax, SHEET_SIZE
        les bx, [SHEETS_PTR]
        add bx, ax
        pop ax
        ret

; CR_IS: "call cr_is / db KIT_X": ZF set if creature AX has kit KIT_X awake (KIT_IS); KIT_IS_B the same
; for sheet ES:BX. All registers kept.
cr_is:
        push bx
        push es
        call kit_sheet
        call kit_is_b
        SHARED_cr_is_back
        SHARED_kit_is_b

; KIT_AC: AX (the AC the AC function has for combatant [BP+6]) with the creature's kits' (kits.ac): a
; Ravager's base AC by its level (RAVAGER_AC) where better than its sheet's; a Wanderer's 1 worse; a
; Sentinel's 2 better with a shield in a hand, an Arena Champion's 1; a Grove Warden's 1 better for every
; 3 druid levels, Thy'rokh's too (OWN_DRUID); a Battle Dancer's dance (KIT_DANCE); a Wild Fury fighting
; wild (KIT_WILD's bit N) 3 worse, no worse than 10. Others kept.
WILD_TO_HIT  equ 3
WILD_DAMAGE  equ 3
WILD_HALVES  equ 2
WILD_AC      equ 3
WILD_AC_MOST equ 10
kit_ac:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        push bx
        push cx
        push dx
        push es
        push ax
        mov cx, ax
        mov ax, [bp + 6]
        call fighter_creature
        jc .out
        cmp ax, 3               ; (fighting wild: 3 worse, no worse than 10)
        ja .sheet
        bt word [cs:kit_wild], ax
        jnc .sheet
        cmp cx, WILD_AC_MOST
        jge .sheet
        add cx, WILD_AC
        cmp cx, WILD_AC_MOST
        jle .sheet
        mov cx, WILD_AC_MOST
.sheet: call kit_sheet
        call kit_is_b
        db KIT_BATTLE_DANCER
        jne .wanderer
        cmp ax, 3
        ja .wanderer
        push si
        mov si, ax
        movsx si, byte [cs:si + kit_dance]
        sub cx, si
        pop si
.wanderer:
        call kit_is_b
        db KIT_WANDERER
        jne .ravager
        inc cx
.ravager:
        call kit_is_b
        db KIT_RAVAGER
        jne .warden
        call kit_level
        movzx ax, al
        dec ax
        jns .some               ; (level 0 as 1)
        xor ax, ax
.some:  cmp ax, RAVAGER_LEVELS - 1
        jbe .level
        mov ax, RAVAGER_LEVELS - 1
.level: push si
        mov si, ax
        movsx dx, byte [cs:si + ravager_ac]
        pop si
        movsx ax, byte [es:bx + SH_BASE_AC]
        sub ax, dx              ; (the sheet's base less the table's: what the table betters it by)
        jle .warden
        sub cx, ax
.warden:
        call kit_is_b
        db KIT_GROVE_WARDEN
        je .warden_level
        call own_druid                  ; (Thy'rokh: a Grove Warden's AC by his druid level)
        jz .sentinel
        jmp .warden_by
.warden_level:
        call kit_level
.warden_by:
        movzx ax, al
        mov dl, 3
        div dl
        movzx ax, al
        sub cx, ax
.sentinel:
        xor dx, dx              ; (a Sentinel's 2 with a shield, an Arena Champion's 1)
        call kit_is_b
        db KIT_SENTINEL
        jne .champion
        mov dl, 2
.champion:
        call kit_is_b
        db KIT_CHAMPION
        jne .shield
        inc dx
.shield:
        or dx, dx
        jz .done
        push si
        mov si, [bp + 6]
        call prot_here
        pop si
        jc .done
        test byte [cs:p_flags], P_SHIELD
        jz .done
        sub cx, dx
.done:  pop ax
        cmp ax, cx
        je .same
        inc word [cs:kit_acs]
.same:  mov ax, cx
        push ax
.out:   pop ax
        pop es
        pop dx
        pop cx
        pop bx
.ret:   ret
ravager_ac db 7, 7, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 1, 1, 0   ; (by level, 1-15, then 0: the owner's 2026-11-26)
RAVAGER_LEVELS equ $ - ravager_ac

; KIT_MELEE: AX what the kits of sheet ES:BX add to hit and to damage with item type SI unless it is a
; missile weapon's: a Ravager's 1; a Brute's 2 with a two-handed weapon; a Ghetto Fighter's 1 with a
; dagger (kits.melee). Others kept.
kit_melee:
        push bx
        push cx
        push es
        xor cx, cx
        call kit_is_b
        db KIT_RAVAGER
        jne .ghetto
        inc cx
.ghetto:
        call kit_is_b
        db KIT_GHETTO
        jne .brute
        cmp si, KIND_TYPES
        jae .brute
        cmp byte [cs:si + kind_of_type], DAGGER_KIND + 1
        jne .brute
        inc cx
.brute: call kit_is_b
        db KIT_BRUTE
        mov ax, 0
        jne .type
        mov al, 2
.type:  push ax
        les bx, [TYPES_PTR]
        imul ax, si, CU_TYPE_SIZE
        add bx, ax
        pop ax
        test byte [es:bx], KT_MISSILE
        jnz .none
        test byte [es:bx + TYPE_FLAGS], TYPE_TWO_HANDED
        jnz .sum
        xor ax, ax
.sum:   add ax, cx
        jmp .out
.none:  xor ax, ax
.out:   pop es
        pop cx
        pop bx
        ret

; KIT_ATTACKS (from OFF_HAND, before the skill's: SL's PROBE_ATTACKS' kit part): the THAC0 the d20 is
; held against ([BP+0Ah]) less what the attacker's kits add to hit (KIT_TO_HIT, WAR_HIT, KIT_EXTRA). The
; weapon attack routine's frame: [BP+0Eh] the attacker's creature, [BP+10h] its sheet, [BP+14h] the
; weapon's type, [BP+16h] above 1 a missile, [BP+18h] the attacker's combatant. All registers kept.
kit_attacks:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        push ax
        call kit_to_hit
        mov [cs:kit_hit_last], ax
        sub [bp + 0x0A], ax
        call war_hit
        add [cs:kit_hit_last], ax
        sub [bp + 0x0A], ax
        call kit_extra
        add [cs:kit_hit_last], ax
        sub [bp + 0x0A], ax
        cmp word [cs:kit_hit_last], 0
        je .none
        inc word [cs:kit_hits]
.none:  pop ax
.ret:   ret
; KIT_WILD_MORE (from OFF_HAND, after the skill's): AX (the attacks a round, halves) one more in melee
; for a Wild Fury whose Wild Fighting passed (WILD_PASSED). Others kept.
kit_wild_more:
        cmp word [bp + 0x16], 1
        jg .ret
        call wild_passed
        jnc .ret
        add ax, WILD_HALVES
        inc word [cs:kit_rates]
.ret:   ret

; KIT_TO_HIT: AX what the attacker's kits add to hit: in melee KIT_CHAMPION's and KIT_MELEE's; a missile
; a Military Scout's 1 with a bow, sling or staff sling under the open sky (KIT_OUTDOORS); either a
; Ghetto Fighter's -1 with anything but a dagger; Wild Fighting's -3 (WILD_TO_HIT). Others kept.
kit_to_hit:
        cmp word [bp + 0x16], 1
        jle .melee
        push si
        xor ax, ax
        mov si, [bp + 0x0E]
        cmp si, 3
        ja .missile             ; (not a party member)
        bt word [cs:kit_outdoors], si
        jnc .missile
        mov si, [bp + 0x14]
        cmp si, KIND_TYPES
        jae .missile
        cmp byte [cs:si + kind_of_type], BOW_KIND
        jb .missile             ; (the bow, sling and staff sling: kinds 13 to 15; not the javelin's
        cmp byte [cs:si + kind_of_type], BOW_KIND + 2   ;   and the darts' past them)
        ja .missile
        push ax
        mov ax, [bp + 0x0E]
        call cr_is
        db KIT_SCOUT
        pop ax
        jne .missile
        inc ax
.missile:
        pop si
        jmp .ghetto
.melee: call kit_champion
        push bx
        push dx
        push si
        push es
        mov dx, ax
        mov ax, [bp + 0x10]
        call kit_sheet_ax
        mov si, [bp + 0x14]
        call kit_melee
        add ax, dx
        pop es
        pop si
        pop dx
        pop bx
.ghetto:
        push bx
        push es
        push ax
        mov ax, [bp + 0x10]
        call kit_sheet_ax
        pop ax
        call kit_is_b           ; (a Ghetto Fighter 1 worse with anything but a dagger)
        db KIT_GHETTO
        jne .wild
        push si
        mov si, [bp + 0x14]
        cmp si, KIND_TYPES
        jae .worse
        cmp byte [cs:si + kind_of_type], DAGGER_KIND + 1
        je .dagger
.worse: dec ax
.dagger:
        pop si
.wild:  pop es
        pop bx
        push si                 ; (WILD_TO_HIT: a party member fighting wild, whatever its check)
        mov si, [bp + 0x0E]
        cmp si, 3
        ja .tame
        bt word [cs:kit_wild], si
        jnc .tame
        sub ax, WILD_TO_HIT
.tame:  pop si
        ret

; WILD_PASSED: CF set if the attacker ([BP+0Eh]) is a party member whose Wild Fighting passed this fight
; (KIT_WILD's bit N + 4). All registers kept.
wild_passed:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .no
        push si
        mov si, [bp + 0x0E]
        cmp si, 3
        ja .not
        add si, 4
        bt word [cs:kit_wild], si
        pop si
        ret
.not:   pop si
.no:    clc
        ret

; WAR_HIT: AX what a Swashbuckler's, Crusader's, Battle Mage's or Mind Warrior's warrior THAC0 adds to
; hit with a weapon of the kit's chosen weapon spec (one of its SPEC_SLOTS): its creature's THAC0 less
; a warrior's (21 less the kit's class level, 1 at best) where that is better, else 0 (kits.war_to_hit).
; Others kept.
war_hit:
        push bx
        push cx
        push si
        push es
        xor cx, cx
        mov si, [bp + 0x14]
        cmp si, KIND_TYPES
        jae .out
        movzx si, byte [cs:si + kind_of_type]   ; (the kind + 1; 0 none)
        or si, si
        jz .out
        mov ax, [bp + 0x10]
        call kit_sheet_ax
        call kit_is_b
        db KIT_SWASHBUCKLER
        je .kit
        call kit_is_b
        db KIT_BATTLE_MAGE
        je .kit
        call kit_is_b
        db KIT_CRUSADER
        je .kit
        call kit_is_b
        db KIT_MIND_WARRIOR
        jne .out
.kit:   mov cx, si              ; (CL the kind + 1, as the slots keep it)
        xor si, si
.slot:  call spec_get
        cmp al, cl
        je .chosen
        inc si
        cmp si, SPEC_ALL
        jb .slot
        xor cx, cx
        jmp .out
.chosen:
        call kit_level
        movzx cx, al
        neg cx
        add cx, 21
        cmp cx, 1
        jge .warrior
        mov cx, 1
.warrior:                       ; (CX a warrior's THAC0; the creature's own, less it)
        les bx, [CREATURES_PTR]
        imul ax, [bp + 0x0E], CREATURE_SIZE
        add bx, ax
        movsx ax, byte [es:bx + CR_THAC0]
        sub ax, cx
        mov cx, ax
        jg .out
        xor cx, cx
.out:   mov ax, cx
        pop es
        pop si
        pop cx
        pop bx
        ret

; KIT_EXTRA: AX what the attacker's kits add to hit and to damage, melee or missile (kits.extra): a
; Battle Dancer's dance (KIT_DANCE: +1 or -1); a Wilderness Avenger's 1. Others kept.
kit_extra:
        push bx
        push cx
        push si
        push es
        xor cx, cx
        mov ax, [bp + 0x0E]
        call kit_sheet
        call kit_is_b
        db KIT_BATTLE_DANCER
        jne .avenger
        cmp ax, 3
        ja .avenger
        mov si, ax
        movsx cx, byte [cs:si + kit_dance]
.avenger:
        call kit_is_b
        db KIT_AVENGER
        jne .out
        inc cx
.out:   mov ax, cx
        pop es
        pop si
        pop cx
        pop bx
        ret

; KIT_CHAMPION: AX 1 for an Arena Champion with a shield in a hand attacking in melee, -1 without one;
; a Sentinel -1 without a shield, 0 with one; else 0 (kits.champion; [BP+18h] the attacker's combatant,
; [BP+10h] its sheet). Others kept.
kit_champion:
        push bx
        push es
        mov ax, [bp + 0x10]
        call kit_sheet_ax
        mov byte [cs:champ_sentinel], 0
        call kit_is_b
        db KIT_CHAMPION
        je .kit
        call kit_is_b
        db KIT_SENTINEL
        jne .none
        mov byte [cs:champ_sentinel], 1
.kit:   pop es
        pop bx
        push si
        mov si, [bp + 0x18]
        mov ax, -1
        call prot_here
        jc .out
        test byte [cs:p_flags], P_SHIELD
        jz .out
        mov ax, 1
        cmp byte [cs:champ_sentinel], 0
        je .out
        xor ax, ax              ; (a Sentinel with a shield: nothing to hit)
.out:   pop si
        ret
.none:  pop es
        pop bx
        xor ax, ax
        ret
champ_sentinel db 0

; KIT_DAMAGE (from SPEC_DAMAGE): the weapon attack's damage bonus ([BP-14h]) with the attacker's kits'
; (SL's PROBE_SPEC_DAMAGE's): in melee an Arena Champion's 1 with a shield, KIT_MELEE's; melee or missile
; KIT_EXTRA's; Wild Fighting passed, 3 more. All registers kept.
kit_damage:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        push ax
        push word [bp - 0x14]
        cmp word [bp + 0x16], 1
        jg .any
        call kit_champion       ; (with a shield, +1 in melee)
        cmp ax, 1
        jne .kit
        inc word [bp - 0x14]
.kit:   push bx
        push si
        push es
        mov ax, [bp + 0x10]
        call kit_sheet_ax
        mov si, [bp + 0x14]
        call kit_melee
        add [bp - 0x14], ax
        pop es
        pop si
        pop bx
.any:   call kit_extra
        add [bp - 0x14], ax
        call wild_passed
        jnc .wild
        add word [bp - 0x14], WILD_DAMAGE
.wild:  pop ax
        cmp ax, [bp - 0x14]
        je .same
        inc word [cs:kit_damages]
.same:  pop ax
.ret:   ret

; EXPERT_OF: EXPERT_HALVES for the attack routine's attacker ([BP+10h] its sheet's number).
expert_of:
        push bx
        push es
        push ax
        mov ax, [bp + 0x10]
        call kit_sheet_ax
        pop ax
        call expert_halves
        pop es
        pop bx
        ret
; EXPERT_HALVES: AX the attacks a round (halves) of one who isn't a warrior (the game's 2), DL its skill
; (SPEC_OF_SHEET), ES:BX its sheet: with SPEC_EXPERT (a Battle Mage's, Crusader's or Mind Warrior's
; chosen weapon spec) 3/2 a round, 2 from the kit's class's 7th level, 5/2 from its 13th (a specialist's
; rate, as Combat & Tactics' expertise: the owner's 2026-11-26; specialize.expert_attacks). Others kept.
expert_halves:
        cmp dl, SPEC_EXPERT
        jne .ret
        cmp ax, 2
        ja .ret
        push cx
        call kit_level
        mov cl, al
        mov ax, 3
        cmp cl, 7
        jb .more
        inc ax
        cmp cl, 13
        jb .more
        inc ax
.more:  pop cx
        inc word [cs:kit_rates]
.ret:   ret

; WAR_KIT_IS: ZF set if sheet ES:BX is a Crusader's or a Mind Warrior's (kit awake). All kept.
        SHARED_war_kit_is

; KIT_SAVE (from PROT_SAVE: SI the one saving, a combatant; DI the modifier, the higher the better;
; [BP+14h] the spell): a Sentinel's -1 against a wizard's or priest's spell, a Myrmidon's -4 against a
; charm (KIT_CHARMS, the sequel's numbers), a Wanderer's +3 against fire and cold (WANDER_SPELLS: the
; sequel's spell records with +1Ah 2 or 4, as kits.save reads them). Others kept.
kit_save:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        push ax
        push bx
        push cx
        push di
        mov cx, [bp + 0x14]
        mov ax, si
        call fighter_creature
        jc .out
        call cr_is
        db KIT_SENTINEL
        jne .myrmidon
        cmp cx, PROT_SPELL_LAST
        ja .myrmidon
        dec di
.myrmidon:
        call cr_is
        db KIT_MYRMIDON
        jne .wanderer
        mov bx, kit_charms
        call kit_word_in
        jne .wanderer
        sub di, 4
.wanderer:
        call cr_is
        db KIT_WANDERER
        jne .out
        mov bx, wander_spells
        call kit_word_in
        jne .out
        add di, 3
.out:   pop ax                  ; (DI as it came in: counted if a kit changed it)
        cmp ax, di
        je .same
        inc word [cs:kit_saves]
.same:  pop cx
        pop bx
        pop ax
.ret:   ret
; KIT_WORD_IN: ZF set if CX is one of the words of the list at CS:BX (ended by -1). BX changed.
kit_word_in:
        cmp word [cs:bx], -1
        je .no
        cmp [cs:bx], cx
        je .ret
        add bx, 2
        jmp kit_word_in
.no:    or bx, bx               ; (ZF clear: BX is never 0 here)
.ret:   ret
; the charms (kits.CHARMS, the sequel's numbers: ravlog's layout): Charm Person, Charm Monster, Dominate,
; Mass Charm, Charm Mammal, the psionic Domination and Mass Domination
kit_charms dw 2, 39, 61, 94, 131, 255, 256, -1
; the spells all fire or cold (their records' +1Ah 2 or 4, RESOURCE.GFF's: ravlog.spell_table)
wander_spells dw 1, 3, 14, 27, 28, 33, 42, 54, 58, 83, 84, 93, 105, 109, 174, 180, 198, 207, 209, 222
              dw 269, 270, 278, 282, 291, 296, 297, 298, 309, -1

; KIT_SKILL (from BELT_SITE): AX (a thief skill's chance; DI the thief's combatant, the routine's [BP+8]
; the skill, 0-7) with the kits' (kits.thief_skill: KIT_SKILLS' row for each; a Military Scout's 10 to
; finding traps, moving silently, hiding and climbing under the open sky, 5 less under a roof) and a
; Swashbuckler's bad luck (0 to BAD_LUCK off each roll, from the game's seed: BAD_LUCK, BAD_LUCK_WHO for
; the dice log), no less than 0. Others kept.
BAD_LUCK     equ 25
SCOUT_SKILLS equ 0x5C           ; (bits: traps, move silently, hide, climb)
kit_skill:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        push bx
        push cx
        push dx
        push si
        push es
        mov dx, ax              ; DX the chance
        mov [cs:kit_skill_in], ax
        mov ax, di
        call fighter_creature
        jc .out
        mov cx, ax              ; CX the creature
        call kit_sheet
        mov si, [bp + 8]
        cmp si, 7
        ja .out
        push di
        mov di, kit_skills
.kit:   mov al, [cs:di]
        or al, al
        jz .scout
        call kit_is
        jne .next
        push bx
        mov bx, di
        movsx ax, byte [cs:bx + si + 1]
        pop bx
        add dx, ax
.next:  add di, 9
        jmp .kit
.scout: pop di
        mov al, KIT_SCOUT
        call kit_is
        jne .swash
        bt word [cs:scout_bits], si
        jnc .swash
        mov ax, -5
        cmp cx, 3
        ja .add
        bt word [cs:kit_outdoors], cx
        jnc .add
        mov ax, 10
.add:   add dx, ax
.swash: mov al, KIT_SWASHBUCKLER
        call kit_is
        jne .floor
        mov ax, BAD_LUCK + 1
        call game_die
        dec ax
        mov [cs:bad_luck], al
        mov [cs:bad_luck_who], cx
        sub dx, ax
.floor: or dx, dx
        jns .out
        xor dx, dx
.out:   mov ax, dx
        cmp ax, [cs:kit_skill_in]
        je .same
        inc word [cs:kit_skills_n]
.same:  pop es
        pop si
        pop dx
        pop cx
        pop bx
.ret:   ret
kit_skill_in dw 0
kit_skills db KIT_ASSASSIN, -15, -15, 0, 0, 0, 0, 0, 0     ; (pick pockets, open locks, traps,
           db KIT_SHADOWBLADE, -10, 0, 0, 5, 10, 0, 0, 0  ;  move silently, hide, hear noise, climb,
           db KIT_GHETTO, 5, 0, -5, 0, 5, 0, 0, 0         ;  read)
           db KIT_WAYFINDER, -10, 0, 0, 10, 10, 0, 0, 0
           db 0
scout_bits dw SCOUT_SKILLS

; KIT_REAR (from MISSILE_REAR, after the game's and the stealth rule's from behind and backstab; SI the
; attacker's combatant): a Military Scout's backstab taken back ([BP-21h] cleared, its 2 off THAC0 given
; back), a Rescuer's attack from behind 1 better to hit, not 2 (kits.backstabs, kits.REAR). All kept.
kit_rear:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        cmp si, 3
        ja .ret
        push ax
        mov ax, si
        call fighter_creature
        jc .out
        cmp byte [bp - 0x21], 0
        je .rescuer
        call cr_is
        db KIT_SCOUT
        jne .rescuer
        mov byte [bp - 0x21], 0
        add word [bp - 0x1E], 2
        inc word [cs:kit_rears]
.rescuer:
        cmp byte [bp - 0x19], 0
        je .out
        call cr_is
        db KIT_RESCUER
        jne .out
        inc word [bp - 0x1E]
        inc word [cs:kit_rears]
.out:   pop ax
.ret:   ret

; KIT_MOVE (from CAH_MOVE: AX a creature's movement for its turn, its Move x 10; SI the creature): a
; Stalker's or a Rescuer's 2 more. Others kept.
kit_move:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        push ax
        mov ax, si
        call cr_is
        db KIT_STALKER
        je .two
        call cr_is
        db KIT_RESCUER
.two:   pop ax
        jne .ret
        add ax, 20
        inc word [cs:kit_moves]
.ret:   ret

; KIT_TWO (from PROBE_TWO, the attack's hand found: TWO_BASE its -2 or -4; [BP-2] the creature): a
; Ghetto Fighter's 2 better (none in the main hand, -2 in the off hand); CF set for a Twin-blade or a
; Battle Dancer in armour that is light or none (no penalty, as a ranger's). All registers kept.
kit_two:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .no
        push ax
        mov ax, [bp - 2]
        call cr_is
        db KIT_GHETTO
        jne .twin
        add word [cs:two_base], 2
        inc word [cs:kit_twos]
.twin:  call cr_is
        db KIT_TWIN_BLADE
        je .light
        call cr_is
        db KIT_BATTLE_DANCER
        jne .not
.light: push dx
        mov dx, ax
        mov byte [cs:aw_heavy], 1
        call armour_worn
        mov byte [cs:aw_heavy], 0
        pop dx
        jc .not
        inc word [cs:kit_twos]
        pop ax
        stc
        ret
.not:   pop ax
.no:    clc
        ret

; KIT_INIT (site 60, "kit_initiative"): "add dx,14h" (5B7E9h, SL's PROBE_INIT site 5750Eh; 3 bytes) where
; a combatant's initiative for the round is made (DX the roll and its adjustments, SI the creature): the
; game's 20 added, then the kits' (kits.initiative): a Myrmidon's 2 less; a Wayfinder's own 2 more and,
; while a Wayfinder of the party is up (PATH_UP), each party member's 1 more; a Military Scout's 2 under
; the open sky (KIT_OUTDOORS). Others kept.
WAYFINDER_INIT equ 2
kit_init:
        add dx, 20
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        push ax
        push dx
        mov ax, si
        call cr_is
        db KIT_MYRMIDON
        jne .wayfinder
        sub dx, 2
.wayfinder:
        call cr_is
        db KIT_WAYFINDER
        jne .scout
        add dx, WAYFINDER_INIT
.scout: cmp si, 3
        ja .out                 ; (not a party member)
        call cr_is
        db KIT_SCOUT
        jne .path
        bt word [cs:kit_outdoors], si
        jnc .path
        add dx, 2
.path:  call path_up
        jne .out
        inc dx
.out:   pop ax                  ; (the game's: counted if a kit changed it)
        cmp ax, dx
        je .same
        inc word [cs:kit_inits]
.same:  pop ax
.ret:   iret
; PATH_UP: ZF set if a party member up (creatures 0-3, New or Okay) is a Wayfinder (kit awake). All kept.
path_up:
        push ax
        push bx
        push es
        xor ax, ax
.member:
        push ax
        les bx, [CREATURES_PTR]
        imul ax, ax, CREATURE_SIZE
        add bx, ax
        cmp byte [es:bx + CR_STATUS], 1
        pop ax
        ja .next
        call cr_is
        db KIT_WAYFINDER
        je .out
.next:  inc ax
        cmp ax, 4
        jb .member
        or ax, ax               ; (ZF clear: none)
.out:   pop es
        pop bx
        pop ax
        ret

; ---- KIT PSP COSTS, PSP, HIT DICE AND CASTING AFTER A HIT: DSCLOG's KIT_PSP, PROBE_PSP_*, PROBE_HIT_DIE,
; PROBE_MAX_PSP and PROBE_HIT_ROUND (RULE_KITS) in the sequel ----
; The power routines (61574h on: SL's 5C9xxh on, the same code) read a power's cost to use from its row of
; the powers' table (3D0h:7E0h, 3 bytes a power: SL's 8 at 408h:0; +1 the cost to use, +2 to keep up, 63h
; none), BX the power x 3; the powers are SL's 34 (psychokinesis 0-5, psychometabolism 6-19, telepathy
; 20-33), the combatants' and creatures' records as KIT_PSP has them (the combatant's creature at
; FIGHTERS_OFF + 1). The sites (kits.psp_cost):
; - PSP_USE (site 191, "psp_use"): "or di,di / jnl $+4 / xor di,di" (6178Eh; 6 bytes) where the routine
;   using a power (616D6h: SI the combatant, [BP+0Ah] the power) has its cost in DI, its table's or worked
;   out for Enhanced Strength and Domination: DI the kit's (KIT_PSP), no less than 0.
; - PSP_TABLE (site 192, "psp_can_use", "psp_failed"): "mov al,es:[bx+7E1h]" (6162Dh, the check whether a
;   power can be used, 6159Bh: SI the combatant; 6183Dh, half of it taken for a power that fails; 5 bytes):
;   AL the kit's; AH as it was (the game's "mov ah,0" after).
; - PSP_DEFENCE (site 193, "psp_defence"): "sub es:[bx+2],ax" (61FA1h; 4 bytes) where creature [BP-6]
;   pays AX for the psionic defence it raises (all telepathy): the kit's, then taken off.
; - PSP_KEEP (site 194, "psp_keep"): "mov al,es:[bx+7E2h]" (619DCh; 5 bytes) where a power's cost to keep it
;   up another round is taken (SI the combatant); PSP_KEEP_DX (site 195, "psp_can_keep"): the same at
;   616A8h, the check whether it can be kept up, the combatant in DX. AL the kit's, 63h (none) as it is.
; The level up's hit points (94F60h: [BP+6] the sheet's number, [BP+8] the class, [BP+0Ah] its new level,
; [BP-4] the sheet, far; the class's hit point group at 4D0h:0, 4 bytes: the die, its last level, the gain
; after; SL's 872xxh) and its most PSP (950xxh; SL's 873B2h):
; - KIT_HIT_DIE (site 196, "hit_die"): "mov al,es:[bx+0]" (95014h; 5 bytes), the die of a level up to the
;   group's last: a Battle Mage's a d6, an Arcanist's a d3 (the preserver's d4: kits.hit_die), for the
;   kit's own class (a human who has changed class rolls for the new one).
; - KIT_HIT_GAIN (site 197, "hit_gain"): "mov al,es:[bx+2]" (95000h; 5 bytes), the fixed gain of a level
;   past it (the preserver's 1 from 11th): a Battle Mage's 2, an Arcanist's 1 (kits.hit_gain; the owner's
;   choice, 2026-11-26), for the kit's own class likewise.
; - KIT_MAX_PSP (site 198, "max_psp"): "les bx,[bp-8]" (95172h; 3 bytes, an INT and a NOP) where the most PSP
;   the level gives is in SI, put in the sheet ([BP-8], far: +0Ch) when more than it was: a Mind Warrior's
;   SI a fifth less (kits.max_psp), its kit asleep or not (its psionicist levels are its PSP). First the
;   game's CON, INT and WIS bonuses are put right (PSP_SCORES, DSCLOG's): the sequel keeps SL's slip of
;   WIS read from the creation screen's record (95110h: DS:142Dh, SL's 11A0h) and its 8-long tables.
; A hit's mark (the creature's byte at 308h:0B2h + it, SL's 2E0h:0AFh), which keeps it from casting until
; the next round (the USE screen's refusal and a queued spell dropped: 97384h, 97A84h):
; - HIT_ROUND (site 199, "hit_round"): "mov byte es:[si+0B2h],1" (5CD76h; 6 bytes) where the routine taking
;   a hit's damage off (5CBE4h: SI the creature) marks it: a Battle Mage isn't marked (KITS.md).
; At creation (the creation overlay's rolls, 5C0h's: SL's CR_STUB's; DS's numbers, SL's in brackets) the
; game rolls the hit points and works out the PSP when a class is clicked, before a kit can be chosen: a
; kit's own are DSCLOG's PROBE_CR_DIE, PROBE_CR_PSP and KIT_REROLL:
; - CR_DIE (site 200, "cr_die"): "mov al,es:[bx+11Dh]" (6D28Fh; 5 bytes; SL's 65677h) where the creation hit
;   points' routine (6D1EDh, 5C0h:66h: SL's 655D6h) takes the class's die (360h:11Dh, by the creation class
;   BX) for the most hit points it can give, a level at a time: a Battle Mage's 6, an Arcanist's 3
;   (kits.hit_die). First a kit left over from the classes before a click on a class (KP_CLASS takes it
;   away only after the click) is taken away, from the party's sheet too (the routine copied the sheet
;   there, 6E6D8h, and rolls each level there: KIT_HIT_DIE), so the rolls go by the class's own die
;   (CR_KIT_STALE). The rolls themselves are KIT_HIT_DIE's (the level up's routine, 690h:20h).
; - CR_PSP (site 201, "cr_psp"): the end of the creation PSP routine (6D75Dh, 5C0h:6Bh: SL's 65B39h), which
;   has put the sheet being made's most PSP in its +0Ch: "les bx,[1429h] / add es:[bx+0Ch],ax / pop bp /
;   retf" (6D85Eh, 10 bytes: its WIS bonus, then the end) made the site, then "xor ax,ax / jmp short" back
;   to it (6D861h, which the WIS test's "jna" at 6D842h is made to go to: the bonus none, the site always
;   run for a psionicist) and the end kept at 6D866h (the routine's other way out, for no psionicist):
;   the WIS bonus added, a Mind Warrior's PSP a fifth fewer (kits.max_psp), then the routine's own end,
;   the INT's frame dropped, its flags put back first (the INT cleared IF: SL's note).
; - KIT_REROLL (no site of its own: KIT_ROW's, on the kit page, site 65): picking or taking back a Battle
;   Mage, an Arcanist or a Mind Warrior has the hit points rolled again and the PSP worked out again by the
;   game's routines, as a click on a class has them (6BBCCh: the hit points with the flag 1, kept within
;   the least and most the routine gave, put on the creature and shown again; the PSP, 6B749h), through the
;   far addresses of those calls in the panel's overlay (WP_CALLS).
KIT_ARCANIST     equ 23
KIT_MIND_BENDER  equ 25
KIT_KINETICIST   equ 27
KIT_TITAN_MIND   equ 61
KIT_WASTE_SEER   equ 73
KIT_SEER_ROOF    equ 0xFE           ; (PSI_KIT's: a Wasteland Seer under a roof)
PSP_PK_LAST      equ 5
PSP_TP_FIRST     equ 20
PSP_NO_UPKEEP    equ 0x63
MIND_PSP         equ 5              ; (a Mind Warrior's PSP a fifth fewer: kits.MIND_PSP)
BM_HIT_DIE       equ 6              ; (kits.hit_die)
ARC_HIT_DIE      equ 3
BM_HIT_GAIN      equ 2              ; (kits.hit_gain)
ARC_HIT_GAIN     equ 1
psp_use:
        push ax
        push bx
        mov ax, di
        mov bx, [bp + 0x0A]
        call kit_psp
        or ax, ax
        jge .set
        xor ax, ax
.set:   mov di, ax
        pop bx
        pop ax
        iret
psp_table:
        push bx
        push cx
        mov ch, ah
        movzx ax, byte [es:bx + 0x7E1]
        call psp_power
        call kit_psp
        mov ah, ch
        pop cx
        pop bx
        iret
psp_defence:
        push bx
        push cx
        mov cx, ax
        mov ax, [bp - 6]
        call psi_kit
        xchg ax, cx             ; (CL the kit, AX the cost)
        mov bx, PSP_TP_FIRST
        call kit_psp_of
        pop cx
        pop bx
        sub [es:bx + 2], ax
        iret
psp_keep_dx:
        push si
        mov si, dx
        call psp_keep_of
        pop si
        iret
psp_keep:
        call psp_keep_of
        iret
psp_keep_of:
        push bx
        push cx
        mov ch, ah
        movzx ax, byte [es:bx + 0x7E2]
        cmp al, PSP_NO_UPKEEP
        je .out
        call psp_power
        call kit_psp
.out:   mov ah, ch
        pop cx
        pop bx
        ret
; PSP_POWER: BX (a power's row in the table, the power x 3) the power. Others kept.
psp_power:
        push ax
        push dx
        mov ax, bx
        xor dx, dx
        mov bx, 3
        div bx
        mov bx, ax
        pop dx
        pop ax
        ret
; KIT_PSP: AX the PSP power BX (0-33) costs combatant SI to use, from the game's AX (kits.psp_cost): a Mind
; Bender's telepathy 2 less, its psychokinesis 2 more, a Kineticist's the other way about; a Titan Mind's
; psychometabolism 2 less, its telepathy 2 more; a Wasteland Seer's every power 2 less under the open sky,
; 1 more under a roof; never below 1 (a cost of 0 or less as it was). KIT_PSP_OF: the same for the kit in
; CL (PSI_KIT's). DS the game's; others kept.
kit_psp:
        push cx
        mov cx, ax
        call fighter_cr
        call psi_kit
        xchg ax, cx             ; (CL the kit, AX the cost)
        call kit_psp_of
        pop cx
        ret
; FIGHTER_CR: AX the creature of combatant SI (FIGHTERS_OFF + 1, as the game reads it, 388h:0C34h).
; Others kept.
fighter_cr:
        push bx
        push es
        imul bx, si, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        mov ax, [es:bx + FIGHTERS_OFF + 1]
        pop es
        pop bx
        ret
; PSI_KIT: AL the psionicist kit of creature AX that changes costs (KIT_MIND_BENDER, KIT_KINETICIST,
; KIT_TITAN_MIND; KIT_WASTE_SEER for a party member's under the open sky, its KIT_OUTDOORS bit, and
; KIT_SEER_ROOF under a roof; a thri-kreen of the games' own party with a psionicist class, SL's K'ratchek,
; as a Wasteland Seer: kits.OWN_FEATURES), awake, or 0. DS the game's; others but AH kept.
psi_kit:
        call cr_is
        db KIT_MIND_BENDER
        je .bender
        call cr_is
        db KIT_TITAN_MIND
        je .titan
        call cr_is
        db KIT_KINETICIST
        je .kinetic
        cmp ax, 3
        ja .none                ; (a Wasteland Seer, a party member: by where it stands)
        call cr_is
        db KIT_WASTE_SEER
        je .seer
        push ax
        push bx
        push es
        call kit_sheet
        call own_race_b
        cmp al, OWN_KREEN
        jne .not_own
        mov al, OWN_PSI
        call own_has
.not_own:
        pop es
        pop bx
        pop ax
        jne .none
.seer:  bt word [cs:kit_outdoors], ax
        mov al, KIT_WASTE_SEER
        jc .ret
        mov al, KIT_SEER_ROOF
        ret
.kinetic:
        mov al, KIT_KINETICIST
        ret
.none:  xor al, al
.ret:   ret
.bender:
        mov al, KIT_MIND_BENDER
        ret
.titan: mov al, KIT_TITAN_MIND
        ret
kit_psp_of:
        or ax, ax
        jle .ret
        push dx
        xor dx, dx              ; DX what the kit adds to telepathy (psychokinesis the opposite)
        cmp cl, KIT_TITAN_MIND
        jne .seer
        cmp bx, PSP_PK_LAST
        jbe .out                ; (a Titan Mind's psychokinesis: as it was)
        mov dx, -2              ; (its psychometabolism 2 less, its telepathy 2 more)
        cmp bx, PSP_TP_FIRST
        jb .add
        mov dx, 2
        jmp .add
.seer:  mov dx, -2              ; (a Wasteland Seer's every power: 2 less under the open sky,
        cmp cl, KIT_WASTE_SEER  ; 1 more under a roof)
        je .add
        mov dx, 1
        cmp cl, KIT_SEER_ROOF
        je .add
        xor dx, dx
        cmp cl, KIT_MIND_BENDER
        jne .kineticist
        mov dx, -2
        jmp .discipline
.kineticist:
        cmp cl, KIT_KINETICIST
        jne .out
        mov dx, 2
.discipline:
        cmp bx, PSP_TP_FIRST
        jae .add
        neg dx
        cmp bx, PSP_PK_LAST
        jbe .add
        xor dx, dx              ; (psychometabolism: as it was)
.add:   or dx, dx
        jz .out
        inc word [cs:kit_psps]
        add ax, dx
        cmp ax, 1
        jge .out
        mov ax, 1
.out:   pop dx
.ret:   ret
kit_hit_die:
        mov al, [es:bx]
        push cx
        mov cx, (ARC_HIT_DIE << 8) | BM_HIT_DIE
        jmp hit_kit
kit_hit_gain:
        mov al, [es:bx + 2]
        push cx
        mov cx, (ARC_HIT_GAIN << 8) | BM_HIT_GAIN
; HIT_KIT: (KIT_HIT_DIE's, KIT_HIT_GAIN's, CX pushed) AL CL for a Battle Mage, CH for an Arcanist, its kit
; awake and the class levelled ([BP+8]) its own; then CX popped and the INT's way back. Others kept.
hit_kit:
        push bx
        push si
        push es
        les bx, [bp - 4]
        call kit_is_b
        db KIT_BATTLE_MAGE
        je .own
        mov cl, ch
        call kit_is_b
        db KIT_ARCANIST
        jne .out
.own:   mov si, [cs:kit_where]
        push ax
        movzx ax, byte [es:bx + si + SH_CLASSES]
        cmp ax, [bp + 8]
        pop ax
        jne .out
        mov al, cl
        inc word [cs:kit_hds]
.out:   pop es
        pop si
        pop bx
        pop cx
        iret
kit_max_psp:
        call psp_scores
        les bx, [bp - 8]
        push ax
        mov al, KIT_MIND_WARRIOR
        call kit_has            ; (asleep too: its psionicist levels are the PSP's)
        jne .out
        push cx
        push dx
        mov ax, si
        xor dx, dx
        mov cx, MIND_PSP
        div cx
        sub si, ax
        inc word [cs:kit_psps]
        pop dx
        pop cx
.out:   pop ax
        iret

; PSP_SCORES (DSCLOG's, for KIT_MAX_PSP, its interrupt frame above the call's return): SI with the
; game's CON, INT and WIS bonuses taken off and the member's own added. The sequel's routine (95091h)
; is SL's (873B2h) with its own places: the creature's CON, INT, WIS at +1Bh-1Dh (SL's +24h-26h), the
; tables a byte for each score from 15 in the segment its "mov dx,seg" at 950F7h holds (the overlay
; manager's fix-up: read there), at CON EFh, INT F7h, WIS FFh + the score (SL's 11Ch, 124h, 12Ch: 8
; long, so INT 22 read 0 and a score past 22 the next table's bytes), and WIS read from the creation
; screen's record (DS:142Dh). Each is the member's own: CON and INT the score less 15, WIS twice the
; score less 10 (the game's own to 22, carried on to 25), nothing below 15.
PSP_SEG_BACK equ 0x95175 - 0x950F8   ; (the "mov dx,seg"'s word, back from the INT's way back)
PSP_CREATION equ 0x142D              ; DS: far pointer to the creation screen's creature record
PSP_CON     equ 0x1B                 ; (the creature's CON; INT, WIS the next)
PSP_CON_TAB equ 0xEF                 ; (the tables, + the score: CON's, INT's, WIS's)
PSP_INT_TAB equ 0xF7
PSP_WIS_TAB equ 0xFF
psp_scores:
        push ax
        push cx
        push dx
        push di
        push es
        push bx
        mov di, sp
        push ds
        lds di, [ss:di + 14]            ; (the INT's way back: past the six and the call's)
        mov cx, [di - PSP_SEG_BACK]     ; CX: the tables' segment
        pop ds
        les bx, [bp - 4]                ; the member's creature record
        mov al, [es:bx + PSP_CON]       ; CON
        mov dx, PSP_CON_TAB
        call .term
        mov al, [es:bx + PSP_CON + 1]   ; INT
        mov dx, PSP_INT_TAB
        call .term
        mov al, [es:bx + PSP_CON + 2]   ; WIS: the game's from the creation screen's record
        cmp al, 15
        jb .done
        cmp al, 25
        jbe .wis
        mov al, 25
.wis:   mov ah, 0
        add ax, ax
        sub ax, 10
        add si, ax
        les bx, [PSP_CREATION]
        movsx di, byte [es:bx + PSP_CON + 2] ; (signed, as the game takes it)
        push ds
        mov ds, cx
        movsx ax, byte [di + PSP_WIS_TAB]
        pop ds
        sub si, ax
.done:  pop bx
        pop es
        pop di
        pop dx
        pop cx
        pop ax
        ret
.term:  cmp al, 15                      ; (score AL, table DX: SI less the game's, plus the score's)
        jb .none
        movzx di, al
        add di, dx
        push ds
        mov ds, cx
        movsx di, byte [di]
        pop ds
        sub si, di
        cmp al, 25
        jbe .own
        mov al, 25
.own:   sub al, 15
        movzx di, al
        add si, di
.none:  ret
hit_round:
        mov [cs:hr_seg], es
        push ax
        mov ax, si
        call cr_is
        db KIT_BATTLE_MAGE
        je .bm
        mov byte [es:si + 0xB2], 1
        jmp .out
.bm:    inc word [cs:bm_hits]
.out:   pop ax
        iret
cr_die:
        push cx
        mov cl, [es:bx + 0x11D]
        call cr_kit_stale
        call kit_made
        cmp al, KIT_BATTLE_MAGE
        jne .arcanist
        mov cl, BM_HIT_DIE
.arcanist:
        cmp al, KIT_ARCANIST
        jne .out
        mov cl, ARC_HIT_DIE
.out:   mov al, cl
        pop cx
        iret
cr_psp:
        push bp
        mov bp, sp
        push word [bp + 6]      ; (the flags at the INT)
        popf
        pop bp
        add sp, 6
        les bx, [WP_CREATION]
        add [es:bx + 0x0C], ax  ; (the WIS bonus: none from the "jna")
        push ax
        call kit_made
        cmp al, KIT_MIND_WARRIOR
        jne .out
        push cx
        push dx
        mov ax, [es:bx + 0x0C]
        xor dx, dx
        mov cx, MIND_PSP
        div cx
        sub [es:bx + 0x0C], ax
        inc word [cs:cr_psps]
        pop dx
        pop cx
.out:   pop ax
        pop bp
        retf
; KIT_MADE: AL the kit (KIT_IS's numbers: the creation class x 4 + the kit) of the sheet being made, ZF
; clear; 0 and ZF set if none (the rule off, a multiclass group's or no class's, none chosen, or its
; classes changed since KP_CLASS last saw them: but before the screen's first look, an EDIT's own). DS
; the game's; others kept.
kit_made:
        push bx
        push es
        call kit_class
        cmp al, MULTI_FIRST
        jae .none
        or al, al
        jz .out
        les bx, [WP_CREATION]
        call cr_classes_seen
        jne .none
        mov bl, [es:bx + KIT_BYTE]
        cmp bl, KIT_OPEN
        je .none
        and bl, 3
        jz .none
        shl al, 2
        add al, bl
        jmp .out
.none:  xor al, al
.out:   pop es
        pop bx
        or al, al
        ret
; CR_CLASSES_SEEN: ZF set if the classes of the sheet at ES:BX are those KP_CLASS last saw, or it has
; seen none yet. All registers kept.
cr_classes_seen:
        push eax
        cmp dword [cs:wp_classes_seen], 0xFFFFFFFF
        je .out
        call sheet_classes_cr
        cmp eax, [cs:wp_classes_seen]
.out:   pop eax
        ret
; CR_KIT_STALE: (CR_DIE) a kit on the sheet being made while its classes are not those KP_CLASS last saw:
; taken away, from the party's sheet of the member being made (USE_WHO_SEG:USE_WHO_OFF) too. DS the
; game's; all registers kept.
cr_kit_stale:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        push ax
        push bx
        push es
        les bx, [WP_CREATION]
        call cr_classes_seen
        je .out
        cmp byte [es:bx + KIT_BYTE], 0
        je .out
        mov byte [es:bx + KIT_BYTE], 0
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov ax, [es:USE_WHO_OFF]
        call kit_sheet_ax
        mov byte [es:bx + KIT_BYTE], 0
        inc word [cs:cr_stales]
.out:   pop es
        pop bx
        pop ax
.ret:   ret
; KIT_ROLLS_DUE: (KIT_ROW) KIT_REROLL due if the sheet being made's kit now (KIT_MADE) is one with its own
; hit die or PSP: a Battle Mage, an Arcanist, a Mind Warrior. All registers kept.
kit_rolls_due:
        push ax
        call kit_made
        cmp al, KIT_BATTLE_MAGE
        je .due
        cmp al, KIT_ARCANIST
        je .due
        cmp al, KIT_MIND_WARRIOR
        jne .out
.due:   mov byte [cs:kit_reroll_due], 1
.out:   pop ax
        ret
; KIT_REROLL: (KIT_ROW, BP the kit page click's frame, the way back to the game's in it as the overlay
; manager needs it) the sheet being made's hit points rolled again and its PSP worked out again by the
; game's routines, as a click on a class has them (6BBCCh: the hit points' routine with the flag 1, the
; least and most it gives, DS:42D8h and RL_HP_MAX, and the sheet's +8; then kept within them, put on the
; creature and shown again; the PSP's routine, its +0Ch put on the creature and shown again), with its kit
; now, which the hit points' routine would leave none once taken back (KIT_OPEN): put back. DS the game's.
CR_HP_LEAST  equ 0x42D8             ; DS: the least hit points the classes could roll (SL's 4998h)
CR_HP_PLACE  equ 0x1224             ; DS: the hit points' number's place, x then y (SL's F92h)
CR_PSP_PLACE equ 0x122C             ; DS: the PSP's (SL's F9Ah)
CR_HP_BACK   equ 0x70               ; (the backdrop's words under the hit points, 368h:70h and 84h; SL's 3F0h)
CR_PSP_BACK  equ 0x72               ; (... under the PSP: SL's 3F2h)
CR_HP_SHOW   equ 0x3E               ; (WP_STUB's: the hit points shown, SL's 64C6Bh)
CR_PSP_SHOW  equ 0x43               ; (... the PSP)
kit_reroll:
        mov byte [cs:kit_reroll_due], 0
        inc word [cs:kit_rerolls]
        push word 1
        push word RL_HP_MAX
        push word CR_HP_LEAST
        les bx, [WP_CREATION]
        mov al, [es:bx + KIT_BYTE]
        mov [cs:kr_kit], al
        lea ax, [bx + 8]
        push es
        push ax
        call far [cs:cr_hp_fn]
        add sp, 10
        les bx, [WP_CREATION]
        mov al, [cs:kr_kit]     ; (the kit as chosen: the routine copies the sheet back from the party's
        mov [es:bx + KIT_BYTE], al ;  stand-in, 6EE5Eh, whose copy, 6E6D8h, made KIT_OPEN none)
        mov ax, [es:bx + 8]
        cmp ax, [RL_HP_MAX]
        jbe .not_over
        mov ax, [RL_HP_MAX]
.not_over:
        cmp ax, [CR_HP_LEAST]
        jae .not_under
        mov ax, [CR_HP_LEAST]
.not_under:
        mov [es:bx + 8], ax
        les bx, [CR_CREATURE]
        mov [es:bx], ax
        mov si, CR_HP_BACK
        mov di, CR_HP_PLACE
        mov ax, CR_HP_SHOW
        call cr_show
        call far [cs:cr_psp_fn]
        les bx, [WP_CREATION]
        mov ax, [es:bx + 0x0C]
        les bx, [CR_CREATURE]
        mov [es:bx + 2], ax
        mov si, CR_PSP_BACK
        mov di, CR_PSP_PLACE
        mov ax, CR_PSP_SHOW
; CR_SHOW: a number of the creation screen shown again, as the game does: its backdrop put back (the
; root's 0C8h:3B30h, WP_BACKDROP, with the words at 368h:SI and SI+14h), then the creation overlay's entry
; AX (WP_STUB's) with the number's place (DS:DI, x then y). DS the game's.
cr_show:
        push ax
        mov es, [cs:wp_stat_seg]
        push word [es:si]
        push word [es:si + 0x14]
        call far [cs:wp_backdrop]
        add sp, 4
        pop ax
        mov [cs:wp_far], ax
        mov ax, [di + 2]
        sub ax, 2
        push ax
        mov ax, [di]
        add ax, 0x15
        push ax
        push dword [CR_CREATURE]
        push dword [WP_CREATION]
        push dword [WIN_SHOWN]
        mov ax, ds
        add ax, WP_STUB
        mov [cs:wp_far + 2], ax
        call far [cs:wp_far]
        add sp, 16
        ret
kit_reroll_due db 0
kr_kit      db 0
kit_rerolls dw 0                ; (for a look in play: the rolls again on the kit page, the stale kits
cr_stales   dw 0                ;  taken away, the Mind Warriors' PSP cut at creation)
cr_psps     dw 0
kit_psps dw 0                   ; (PSP costs and most PSP a kit changed, for a look in play)
kit_hds  dw 0                   ; (hit dice and gains a kit changed)
bm_hits  dw 0                   ; (a Battle Mage hit and not marked)
hr_seg   dw 0                   ; (the marks' segment, the last hit's: for a look in play)

kit_hit_last dw 0               ; (the last attack's kits' to hit)
kit_acs      dw 0               ; (what the kits did, counted, for a look in play: ACs changed,
kit_hits     dw 0               ;  attacks given a kit's to hit, damage bonuses changed, attacks a
kit_damages  dw 0               ;  round, saves, thief skills, from behind and backstabs, moves, the
kit_rates    dw 0               ;  two-weapon penalties and initiatives)
kit_saves    dw 0
kit_skills_n dw 0
kit_rears    dw 0
kit_moves    dw 0
kit_twos     dw 0
kit_inits    dw 0

; PROBE_HELM_AC: INT VEC_HELM_AC replaces "mov al,es:[bx+0Eh] / cwde" (5 bytes: INT + 3 NOPs) at the
; two places the AC function reads a worn item's type's AC (5D663h, 5D67Bh; SL's PROBE_RING_AC's
; read at 58EBDh): ES:BX the type's record, CX the type, DI the worn list's index (the list at
; [BP-324h], 10 bytes an entry, the item at +0). PROBE_BOX_AC: INT VEC_BOX_AC replaces the same at the
; item box's "AC BONUS:" (9A4B7h; SL's 8C15Ah): SI the type, [BP+6] the item. AX the type's AC; with
; RULE_HELMS, 1 for a Helm of type 55 (HELM_TYPE: the leather helm's AC 0, which hats share: only an
; item named Helm, HELM_NAME, counts), and for the mod's Bone Helm (BONE_HELM_TYPE: the Loader's type for
; Shattered Lands' 117, ravager.mod_type, which only it has; SL's HELM_BONE). The sequel's other helm type
; (56, a Helm and the Helm of Domination) has AC 1 of its own already.
HELM_TYPE    equ 55
BONE_HELM_TYPE equ 104
HELM_NAME    equ 0x24           ; (an item's name, +14h: TEXT 1000's "Helm"; a hat's 27h)
HELM_LIST    equ -0x324         ; (the AC function's worn list, from its BP)
probe_helm_ac:
        movsx ax, byte [es:bx + 0x0E]
        cmp cx, BONE_HELM_TYPE
        je helm_rule_iret
        cmp cx, HELM_TYPE
        jne .done
        push di
        imul di, di, 10
        mov di, [ss:bp + di + HELM_LIST]
        call helm_named
        pop di
.done:  iret
probe_box_ac:
        movsx ax, byte [es:bx + 0x0E]
        cmp si, BONE_HELM_TYPE
        je helm_rule_iret
        cmp si, HELM_TYPE
        jne .done
        push di
        mov di, [bp + 6]
        call helm_named
        pop di
.done:  iret
helm_rule_iret:                 ; a Bone Helm: AX 1 if RULE_HELMS is on
        test word [cs:rules], RULE_HELMS
        jz .done
        mov ax, 1
.done:  iret
helm_named:                     ; DI an item of HELM_TYPE: AX 1 if it is a Helm and RULE_HELMS is on
        test word [cs:rules], RULE_HELMS
        jz .ret
        push bx
        push es
        imul di, di, ITEM_SIZE
        les bx, [ITEMS_PTR]
        cmp word [es:bx + di + 0x14], HELM_NAME
        pop es
        pop bx
        jne .ret
        mov ax, 1
.ret:   ret

; PROTECTION: SL's RULE_PROTECTION (always on), DSCLOG's PROBE_RING_AC, PROT_SCAN, RING_PLUS and
; ROBE_PLUS with the sequel's numbers, for the mod's items the party transfer brings (ravitems): a ring of
; protection is the sequel's Ring (PROT_RING, of no AC: +0Bh 0) with a plus; the cloak of protection,
; bracers of defense and the robes are the mod's types (ravager.mod_type), whose plus the sequel's AC
; function counts already (+0Bh 80h: the plus less the type's AC). As AD&D has it:
; - a ring of protection betters AC only without magical armour, and of two only the better (the left
;   hand's if they're equal); a cloak of protection only without magical or metal armour and without a
;   shield; bracers of defense only without armour (a helm too); a robe's plus, likewise, on top of the
;   rest, as a ring's (in [BP-6], after the Armor spell's armour value: SL's ROBE in PROBE_RING_AC);
; - on saves, the better ring's plus whatever the armour, the cloak's as for AC, the Veiled Robe +1 on
;   every save and the Ashen Robe +1 against a spell (DSCLOG's KIT_SAVE's robe part).
; PROT_AC (site 43, "protection_ac"): the AC function's "mov al,es:[bx+0Bh] / mov ah,0" (5D61Ah; 6
; bytes), whether a worn item counts for AC (AX bit 80h): ES:BX its type's record, CX the type, DX the
; item, SI the combatant, [BP-6] the function's other total (better the lower). PROT_SAVE (site 44,
; "protection_save"): the save modifiers' "mov si,[bp+6] / xor di,di" (8360Eh; 5 bytes; SL's 79D47h),
; SI the one saving, DI the modifier (the higher the better), [BP+14h] the spell.
PROT_RING      equ 45            ; (the sequel's Ring; its own carry a spell power, plus 0: OBJEX.GFF)
PROT_CLOAK     equ 103           ; (SL's 116, 123, 140: ravager.mod_type)
PROT_BRACERS   equ 110
PROT_ROBE      equ 127
FINGER_SLOT    equ 4             ; (an item's +13h while worn: the left hand's finger, the right's, the back;
FINGER2_SLOT   equ 11            ; SL's, which the transfer keeps)
CLOAK_SLOT     equ 12
P_MAGIC_ARMOUR equ 1             ; (PROT_SCAN's P_FLAGS: armour with a plus, armour of metal, a shield in a
P_METAL_ARMOUR equ 2             ; hand, any armour)
P_SHIELD       equ 4
P_ARMOUR       equ 8
PROT_SPELL_LAST equ 0xEA         ; (the sequel's spells: its psionic powers EBh on)
; BOOTS OF SPEED (DSCLOG's BOOTS_AC, BOOTS_MOVE): worn on the feet, the mod's type (SL's 145), AC 2 better
; in a fight unless Cannot Move, Paralyzed or Slowed (PROT_AC: in [BP-6]), and the movement for a turn in
; a fight doubled (BOOTS_MOVE, from CAH_MOVE). The sequel has two effects named Slowed (52 and 91).
PROT_BOOTS     equ 132
FOOT_SLOT      equ 13
SPEED_AC       equ 2
STUCK_FX       equ 66            ; (the sequel's effects: Cannot Move, Paralyzed, Slowed and Slowed)
PARALYZED_FX   equ 69
SLOWED_FX      equ 52
SLOWED_FX_2    equ 91
; BOOTS_MOVE: AX (a creature's movement for its turn in a fight; DI the combatant) doubled if it wears
; the Boots of Speed. All else kept.
boots_move:
        push si
        mov si, di
        call prot_here
        pop si
        jc .ret
        cmp byte [cs:p_boots], 0
        je .ret
        shl ax, 1
        inc word [cs:boots_count]
.ret:   ret
; THE GIRDLES AND THE AMULET (SL's worldgear.py; DSCLOG's ITEM_REAR, AMULET_MR), the mod's types in the sequel:
; - ITEM_REAR (from MISSILE_REAR, in the attack's set-up at 5C99Fh: DI the target, [BP-19h] from behind and
;   [BP-21h] the backstab, each 2 off the THAC0 [BP-1Eh]; [BP-4] the weapon's type, [BP+0Eh] 1 melee): a
;   target wearing the Girdle of Back Defense takes back the attack from behind and the backstab (their 2
;   each given back); the Golden Girdle of Urnst makes a sword's melee attack 3 worse (a long or short
;   sword kind, KIND_OF_TYPE). All registers kept.
; - AMULET_MR (site 45, "amulet_resistance"): the magic resistance routine's "cmp word [bp-2],0" (84B24h,
;   4 bytes; SL's 7A4FDh; [BP+6] the target, [BP-2] its resistance, Mind Bar's 75 added): an Amulet of
;   Magic Resistance at the neck adds AMULET_PERCENT, before Lower Resistance (LOWRES_SITE). The compare's
;   ZF handed back for the game's jne.
BACK_GIRDLE    equ 129           ; (SL's 142, 143, 144: ravager.mod_type)
URNST_GIRDLE   equ 130
MR_AMULET      equ 131
WAIST_SLOT     equ 5
NECK_SLOT      equ 8
URNST_AC       equ 3
AMULET_PERCENT equ 15
KIND_LONG_SWORD  equ 1
KIND_SHORT_SWORD equ 4
item_rear:
        push si
        mov si, di
        call prot_here
        pop si
        jc .ret
        cmp byte [cs:p_girdle], 1
        jne .urnst
        cmp byte [bp - 0x19], 0
        je .stab
        mov byte [bp - 0x19], 0
        add word [bp - 0x1E], 2
        inc word [cs:girdle_count]
.stab:  cmp byte [bp - 0x21], 0
        je .ret
        mov byte [bp - 0x21], 0
        add word [bp - 0x1E], 2
        inc word [cs:girdle_count]
        ret
.urnst: cmp byte [cs:p_girdle], 2
        jne .ret
        cmp word [bp + 0x0E], 1
        jne .ret
        push bx
        mov bx, [bp - 4]
        cmp bx, KIND_TYPES
        jae .not
        mov bl, [cs:kind_of_type + bx]
        cmp bl, KIND_LONG_SWORD
        je .sword
        cmp bl, KIND_SHORT_SWORD
        jne .not
.sword: add word [bp - 0x1E], URNST_AC
        inc word [cs:girdle_count]
.not:   pop bx
.ret:   ret
amulet_mr:
        push si
        mov si, [bp + 6]
        call prot_here
        pop si
        jc .test
        cmp byte [cs:p_amulet], 0
        je .test
        add word [bp - 2], AMULET_PERCENT
        inc word [cs:amulet_count]
.test:  push bx
        mov bx, sp                      ; ([ss:bx+2] the INT's IP, +4 CS, +6 FLAGS)
        or word [ss:bx + 6], 0x40
        cmp word [bp - 2], 0
        je .zero
        and word [ss:bx + 6], ~0x40
.zero:  pop bx
        iret
girdle_count dw 0
amulet_count dw 0
prot_ac:
        movzx ax, byte [es:bx + 0x0B]
        cmp cx, PROT_RING
        je .ring
        cmp cx, PROT_CLOAK
        je .cloak
        cmp cx, PROT_BRACERS
        je .bracers
        cmp cx, PROT_ROBE
        je .robe
        cmp cx, PROT_BOOTS
        je .boots
        iret
.boots: cmp byte [IN_COMBAT], 0         ; the Boots of Speed: AC 2 better in a fight, unless held
        je .out
        push ax
        push cx
        mov ax, si
        mov cl, STUCK_FX
        call has_effect
        je .held
        mov cl, PARALYZED_FX
        call has_effect
        je .held
        mov cl, SLOWED_FX
        call has_effect
        je .held
        mov cl, SLOWED_FX_2
        call has_effect
        je .held
        sub word [bp - 6], SPEED_AC
        inc word [cs:boots_count]
.held:  pop cx
        pop ax
        iret
.ring:  call prot_here
        jc .out
        test byte [cs:p_flags], P_MAGIC_ARMOUR
        jnz .out
        push bx
        push di
        push es
        les di, [ITEMS_PTR]
        imul bx, dx, ITEM_SIZE
        add bx, di
        mov byte [cs:p_counts], 0
        cmp byte [es:bx + ITEM_PLUS], 0
        jle .ringed                     ; (a plain or cursed ring: none)
        mov ah, [cs:p_ring]
        cmp byte [es:bx + ITEM_SLOT], FINGER_SLOT
        jne .right
        cmp ah, [cs:p_ring2]            ; the left hand's counts unless the other is better
        jl .ringed
        jmp .count
.right: cmp byte [es:bx + ITEM_SLOT], FINGER2_SLOT
        jne .ringed
        cmp [cs:p_ring2], ah            ; the right hand's only if better
        jle .ringed
.count: mov byte [cs:p_counts], 1
.ringed:
        pop es
        pop di
        pop bx
        mov ah, 0
        cmp byte [cs:p_counts], 0
        je .out
        or al, 0x80
        inc word [cs:prot_count]
.out:   iret
.cloak: call prot_here
        jc .out
        test byte [cs:p_flags], P_MAGIC_ARMOUR | P_METAL_ARMOUR | P_SHIELD
        jz .out
.off:   and al, 0x7F
        inc word [cs:prot_count]
        iret
.bracers:
        call prot_here
        jc .out
        test byte [cs:p_flags], P_ARMOUR
        jz .out
        jmp .off
.robe:  call prot_here               ; (a robe: as bracers, nothing over armour on the arms, legs or head)
        jc .out
        test byte [cs:p_flags], P_ARMOUR
        jnz .off
        push ax
        push bx
        push es
        les bx, [ITEMS_PTR]
        imul ax, dx, ITEM_SIZE
        add bx, ax
        movsx ax, byte [es:bx + ITEM_PLUS]
        sub [bp - 6], ax
        pop es
        pop bx
        pop ax
        jmp .off                        ; (and not as armour)
prot_save:
        mov si, [bp + 6]
        xor di, di
        call prot_here
        jc .out
        push ax
        movsx ax, byte [cs:p_ring]
        cmp al, [cs:p_ring2]
        jge .ring
        movsx ax, byte [cs:p_ring2]
.ring:  add di, ax
        test byte [cs:p_flags], P_MAGIC_ARMOUR | P_METAL_ARMOUR | P_SHIELD
        jnz .robe
        movsx ax, byte [cs:p_cloak]
        or ax, ax
        jle .robe
        add di, ax
.robe:  mov al, [cs:p_robe]
        cmp al, 2
        jae .one                        ; (the Veiled Robe, +2)
        cmp al, 1
        jne .done
        cmp word [bp + 0x14], PROT_SPELL_LAST
        ja .done
.one:   inc di
.done:  pop ax
        inc word [cs:prot_saves]
.out:   call kit_save                   ; (the kits': KITS)
        call ns_spook_save              ; (the new spells' Spook)
        iret
; PROT_HERE: PROT_SCAN for combatant SI (DS the game's); CF if it isn't a creature. All kept.
prot_here:
        pusha
        push es
        imul bx, si, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        cmp byte [es:bx + FIGHTERS_OFF], 2
        jne .not
        mov dx, [es:bx + FIGHTERS_OFF + 1]
        call prot_scan
        pop es
        popa
        clc
        ret
.not:   pop es
        popa
        stc
        ret
; PROT_SCAN: what creature DX (DS the game's) wears that the protection rules weigh, in any of its item
; lists (as ARMOUR_WORN reads them): P_FLAGS; P_RING, P_RING2 (the plus of a ring of protection on each
; hand's finger, 0 for none or less); P_CLOAK (a cloak of protection's plus, worn on the back); P_ROBE (a
; robe's plus, worn on the chest; 0 none); P_BOOTS (1 for the Boots of Speed on the feet); P_GIRDLE (1 the
; Girdle of Back Defense, 2 the Golden Girdle of Urnst, at the waist); P_AMULET (1 for the Amulet of Magic
; Resistance at the neck). All kept.
prot_scan:
        pusha
        push es
        xor ax, ax
        mov [cs:p_flags], al
        mov [cs:p_ring], ax             ; (and P_RING2)
        mov [cs:p_cloak], ax            ; (and P_ROBE)
        mov [cs:p_boots], al
        mov [cs:p_girdle], ax           ; (and P_AMULET)
        imul bx, dx, CREATURE_SIZE
        mov [cs:p_creature], bx
        mov cx, 8
.list:  les bx, [CREATURES_PTR]
        add bx, [cs:p_creature]
        add bx, cx
        mov dx, [es:bx]
        cmp dx, NO_ITEM
        jae .next
        imul bx, dx, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        cmp byte [es:bx + FIGHTERS_OFF], 1
        jne .next                       ; not an item
        mov dx, [es:bx + FIGHTERS_OFF + 1]
        mov si, 100                     ; (no more than 100 in a list)
.item:  cmp dx, NO_ITEM
        jae .next
        dec si
        js .next
        imul bx, dx, ITEM_SIZE
        les di, [ITEMS_PTR]
        add bx, di
        mov dx, [es:bx + ITEM_NEXT]
        mov al, [es:bx + ITEM_SLOT]
        mov ah, [es:bx + ITEM_PLUS]
        mov di, [es:bx + ITEM_TYPE]
        cmp di, PROT_RING
        jne .cloak
        cmp ah, 0
        jle .item
        cmp al, FINGER_SLOT
        jne .ring2
        mov [cs:p_ring], ah
        jmp .item
.ring2: cmp al, FINGER2_SLOT
        jne .item
        mov [cs:p_ring2], ah
        jmp .item
.cloak: cmp di, PROT_CLOAK
        jne .robe
        cmp al, CLOAK_SLOT
        jne .item
        mov [cs:p_cloak], ah
        jmp .item
.robe:  cmp di, PROT_ROBE
        jne .boots
        cmp al, CHEST_SLOT
        jne .item
        mov [cs:p_robe], ah
        jmp .item
.boots: cmp di, PROT_BOOTS
        jne .girdle
        cmp al, FOOT_SLOT
        jne .item
        mov byte [cs:p_boots], 1
        jmp .item
.girdle:
        cmp di, BACK_GIRDLE
        je .waist
        cmp di, URNST_GIRDLE
        jne .amulet
.waist: cmp al, WAIST_SLOT
        jne .item
        sub di, BACK_GIRDLE - 1         ; (1 back defense, 2 Urnst)
        mov ax, di
        mov [cs:p_girdle], al
        jmp .item
.amulet:
        cmp di, MR_AMULET
        jne .type
        cmp al, NECK_SLOT
        jne .item
        mov byte [cs:p_amulet], 1
        jmp .item
.type:  imul di, di, CU_TYPE_SIZE
        les bx, [ITEM_TYPES_PTR]
        add bx, di
        test byte [es:bx], 4            ; a shield (the flag the AC function reads for one)
        jz .body
        cmp al, RIGHT_HAND
        je .shield
        cmp al, LEFT_HAND
        jne .item
.shield:
        or byte [cs:p_flags], P_SHIELD
        jmp .item
.body:  cmp al, ARM_SLOT                ; armour: worn on the arms, legs, head or chest
        je .armour
        cmp al, LEG_SLOT
        je .armour
        cmp al, HEAD_SLOT
        je .armour
        cmp al, CHEST_SLOT
        jne .item
.armour:
        call armour_type
        jnc .item
        or byte [cs:p_flags], P_ARMOUR
        cmp ah, 0
        jle .metal
        or byte [cs:p_flags], P_MAGIC_ARMOUR
.metal: mov al, [es:bx + CU_MATERIAL]   ; (no material: 40h with 0)
        and al, 0x4F
        cmp al, MATERIAL_METAL
        jne .item
        or byte [cs:p_flags], P_METAL_ARMOUR
        jmp .item
.next:  add cx, 2
        cmp cx, 0x0E
        jb .list
        pop es
        popa
        ret
p_flags    db 0
p_counts   db 0
p_ring     db 0
p_ring2    db 0
p_cloak    db 0
p_robe     db 0
p_boots    db 0
p_girdle   db 0                 ; (1 the Girdle of Back Defense, 2 the Golden Girdle of Urnst, at the waist)
p_amulet   db 0                 ; (1 the Amulet of Magic Resistance at the neck)
boots_count dw 0                ; (the boots' AC and movement given, for a look in play)
p_creature dw 0
prot_count dw 0                 ; (AC counts changed so, and saves weighed, for a look in play)
prot_saves dw 0

; PROBE_HP_BEST: DSCLOG's. INT VEC_HP_BEST replaces "mov cx,ax" (2 bytes; 95025h, SL's 87319h) after
; the game's roll of a level's hit die (at creation too), AX the roll. With RULE_HP_BEST the game
; rolls it twice and keeps the better: the first time the roll is kept and the INT returns to the
; start of the game's roll (9500Ah, SL's 872FDh: the die from the class's table, then the call), so
; the dice log sees both rolls as the game's; the second time CX gets the better of the two.
HP_BEST_BACK equ 0x95027 - 0x9500A
        SHARED_probe_hp_best

hp_first dw 0
hp_again db 0

; ROLL_MAX_HP: a fix of the sequel's. INT VEC_ROLL_MAX replaces "add es:[bx+0Ah],cx" (4 bytes, INT + 2
; NOPs; 9506Ch) at the end of the routine rolling a level's hit die (94F60h; SL's 872xxh): [BP+6] the
; member, ES:BX its sheet, CX the roll, added to the rolled hit points (+0Ah). SL's routine then works out
; the most hit points again (SL's 874B0h, the sequel's 95193h, from the same segment) and raises the
; creature's by as much as they rose (SL's 87362h-87391h); the sequel's left that to the level-up
; (957E0h), so the creation screen's die rolled the dice and the new character kept the least the
; screen opened with (a 7th-level fighter 7/7 HP on View Character). Done here, as SL's: at a level-up
; the game's own (957E0h) then sets them again, the same.
MAX_HP_DELTA equ 0x95193 - 0x9506E      ; (the routine, from the INT's return)
roll_max_hp:
        add [es:bx + 0x0A], cx
        pusha
        push es
        mov di, sp
        mov ax, [ss:di + 18]            ; (the INT's IP and CS: the routine's segment is this one)
        add ax, MAX_HP_DELTA
        mov [cs:rm_target], ax
        mov ax, [ss:di + 20]
        mov [cs:rm_target + 2], ax
        mov si, [bp + 6]
        imul di, si, SHEET_SIZE
        les bx, [SHEETS_PTR]
        mov dx, [es:bx + di + 8]        ; (the most before)
        push dx
        push si
        call far [cs:rm_target]
        pop cx
        pop dx
        les bx, [SHEETS_PTR]
        mov [es:bx + di + 8], ax
        sub ax, dx
        jle .kept
        imul di, si, CREATURE_SIZE
        les bx, [CREATURES_PTR]
        add [es:bx + di], ax
        inc word [cs:rm_count]
.kept:  pop es
        popa
        iret
rm_target dw 0, 0
rm_count  dw 0                  ; (rises made so, for a look in play)

; HALF-GIANTS' HANDS: DSCLOG's RULE_HALF_GIANT (PROBE_TWO_HANDED), a half-giant holds a two-handed weapon
; in one hand. INT VEC_TWO_HANDED replaces "test byte es:[bx+0Bh],40h" (5 bytes: INT + 3 NOPs), the
; two-handed bit of an item type (ES:BX), where the inventory puts a weapon in a hand (the routine at
; 7761Bh, SL's 6F2xxh): the other hand's ("Two handed weapon in use", 77976h, SL's 6F33Fh) and the one
; going in ("Need two free hands", 77A0Dh, SL's 6F3CCh). ZF in the INT's frame: the game's test, or,
; with the rule, set ("not two-handed") for a half-giant, the character on show at
; (load + 3E71h):0B44h (the routine's own read, 77636h). The game's check that both hands don't hold
; heavy weapons (over 30 each) still stands; the sequel has no cahulaks to leave out.
RULE_HALF_GIANT equ 512
RACE_HALF_GIANT equ 5
TYPE_FLAGS    equ 0x0B
TYPE_TWO_HANDED equ 0x40
two_handed:
        push bp
        mov bp, sp                  ; ([BP+6] the INT's flags)
        or word [bp + 6], 0x40      ; ZF: not two-handed
        test byte [es:bx + TYPE_FLAGS], TYPE_TWO_HANDED
        jz .out
        test word [cs:rules], RULE_HALF_GIANT
        jz .two
        push ax
        push bx
        push es
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        imul ax, [es:USE_WHO_OFF], SHEET_SIZE
        les bx, [SHEETS_PTR]
        add bx, ax
        cmp byte [es:bx + SHEET_RACE], RACE_HALF_GIANT
        pop es
        pop bx
        pop ax
        jne .two
        inc word [cs:th_count]
        jmp .out
.two:   and word [bp + 6], ~0x40
.out:   pop bp
        iret
th_count  dw 0                  ; (half-giants let so, for a look in play)

; CAHULAKS: DSCLOG's (RULE_HI_CAHULAKS, Weapon traits, always on), a pair of four-bladed heads on a rope, one
; in each hand (Dark Sun's rules: the two-weapon rule, though one item; the sequel's Cahulaks, type 24, a
; plain weapon to it). With the rule:
; - the off head's one more attack a round (CAH_MORE, from OFF_HAND: AX the halves, [BP+12h] the item,
;   [BP+16h] the range 1 or less);
; - the two-weapon routine (5DE34h) asked for them as for two weapons ready: CAH_TWO replaces its "cmp
;   word [bp+6],1 / jle" (5DE6Fh, SL's 59627h; 6 bytes: INT + 4 NOPs), going on when [BP+6] is 2 or
;   more or the item [BP+0Ah] is the cahulaks, else to its "none" way (5DE86h);
; - PROBE_TWO then gives AD&D's main head -2 plus DEX's reaction adjustment, no better than 0, for every
;   swing (CAH_ADJUST), keeping how much worse the off head's -4 is (CAH_EXTRA) for attacker CX;
; - CAH_SWING replaces the attack's "mov word [bp-4],0" at each swing's start (5D052h, SL's 589B6h; 5
;   bytes: INT + 3 NOPs): the round's last swing with the cahulaks ([BP-16h] the swing, [BP-0Ah] the
;   round's swings, [BP+12h] the item, [BP+16h] the range, [BP+18h] the attacker), the off head's when
;   there are 2 or more, pays CAH_EXTRA more on [BP+0Ah] (what the d20 must reach, before the roll).
; The tangle: CAH_HIT, below. A ranger keeps the game's no penalty (the routine's own
; test, before CAH_TWO).
RULE_HI_CAHULAKS equ 0x2000
CAHULAKS_TYPE equ 24
CT_SKIP       equ 0x5DE86 - 0x5DE71   ; (the routine's "none" way, from after the INT)
item_is_cahulaks:               ; ZF if item AX (its number) is the cahulaks and the rule on. DS the
        test word [cs:rules_hi], RULE_HI_CAHULAKS   ;   game's; all kept
        jz .no
        cmp ax, NO_ITEM
        jae .no
        push es
        push bx
        push ax
        imul bx, ax, ITEM_SIZE
        les ax, [ITEMS_PTR]
        add bx, ax
        pop ax
        cmp word [es:bx + ITEM_TYPE], CAHULAKS_TYPE
        pop bx
        pop es
        ret
.no:    or sp, sp               ; (ZF clear)
        ret
cah_more:                       ; AX the attacks a round (halves) with item [BP+12h]: 2 more for the
        cmp word [bp + 0x16], 1 ;   cahulaks in melee. Others kept.
        jg .ret
        push ax
        mov ax, [bp + 0x12]
        call item_is_cahulaks
        pop ax
        jne .ret
        add ax, 2
        inc word [cs:cah_count]
.ret:   ret
cah_adjust:                     ; DX the main head's adjustment (TWO_BASE + TWO_ADJUST, no better than 0);
        push ax                 ;   CAH_EXTRA how much worse the off head's is (2 more), for attacker CX
        mov dx, [cs:two_base]
        add dx, [cs:two_adjust]
        jle .main
        xor dx, dx
.main:  mov ax, [cs:two_base]
        sub ax, 2
        add ax, [cs:two_adjust]
        jle .off
        xor ax, ax
.off:   neg ax
        add ax, dx
        mov [cs:cah_extra], ax
        mov [cs:cah_who], cx
        pop ax
        ret
cah_two:
        cmp word [bp + 6], 1
        jg .two
        push ax
        mov ax, [bp + 0x0A]
        call item_is_cahulaks
        pop ax
        je .two
        push bp
        mov bp, sp
        add word [bp + 2], CT_SKIP
        pop bp
.two:   iret
cah_swing:
        mov word [bp - 4], 0
        call size_dice                  ; (the creature size rule: a large target's dice, the call's first swing)
        call stink_swing                ; (the stinkpots: a nauseated attacker's -2, the stinkpot's 1d3)
        cmp word [bp + 0x16], 1
        jg .out
        call sf_swing                   ; (a lotulis or double spear specialist's last swing: a second foe)
        push ax
        mov ax, [bp + 0x12]
        call item_is_cahulaks
        jne .pop
        mov ax, [bp + 0x18]
        cmp ax, [cs:cah_who]
        jne .pop
        mov ax, [bp - 0x0A]
        cmp ax, 2
        jl .pop
        dec ax
        cmp ax, [bp - 0x16]
        jne .pop
        mov ax, [cs:cah_extra]
        add [bp + 0x0A], ax
        mov word [cs:cah_who], -1   ; (once)
        inc word [cs:cah_off]
.pop:   pop ax
.out:   iret
cah_extra dw 0
cah_who   dw -1
cah_count dw 0                  ; (rounds given the off head's attack, for a look in play)
cah_off   dw 0                  ; (off head's swings paying the more)

; CAH_HIT: the cahulaks' tangle (DSCLOG's CAH_HIT; RULE_HI_CAHULAKS). INT VEC_CAH_HIT replaces "mov byte
; [bp-19h],0" (5D1FEh, SL's "mov byte [bp-15h],0" at 58B54h; 4 bytes: INT + 2 NOPs), where a weapon's hit
; has done its damage (the item in SI, 0 or more). With the rule, a melee hit with the cahulaks ([BP+12h],
; [BP+16h] 1 or less) on a target (TARGET) still standing and man-sized or smaller (not a half-giant: its
; sheet's race, or large by the Loader's table: IS_LARGE) makes it save against petrification (its
; sheet's +33h, a d20 from the game's seed, as DSCLOG's GAME_DIE; a 20 always saves). A failure: it loses
; its next turn, at once if it has yet to act this round (SWEPT_NOW), else at its next turn's start
; (CAH_MOVE, from the bitmap TANGLED). Recorded for the dice log (KIND_MANUAL, MN_TANGLE: the target, the
; attacker [BP+18h], the d20, the save needed).
; CAH_MOVE: INT VEC_CAH_MOVE replaces "mov es:[bx+22Eh],ax" (5B838h, SL's PROBE_MOVE site 57566h; 5
; bytes: INT + 3 NOPs) where a creature's turn starts, AX its movement (DI the combatant, BX the creature
; x 2): a tangled one's turn taken (no movement, its initiative -1, as the game marks one that has
; acted). The bitmap is cleared at a fight's first round (ACID_ROUND). First the Boots of Speed's
; movement doubled (BOOTS_MOVE).
MN_TANGLE     equ 10
KIND_MANUAL   equ 14
IN_COMBAT     equ 0x13FA            ; DS byte: in a fight
WHOSE_TURN    equ 0x426D            ; DS word: the combatant whose turn it is
INIT_FROM_DS  equ 0x47E0 - 0x3C4F   ; (the creatures' initiative, (load + 3C4Fh):0DCh, 4 bytes each: -1
INIT_OFF      equ 0xDC              ;   once acted; their movement for the turn at +22Eh, 2 bytes each)
MOVE_OFF      equ 0x22E
SHEET_PETRIFY equ 0x33
TANGLE_MOST   equ 512               ; (the combatants the bitmap covers)
cah_hit:
        mov byte [bp - 0x19], 0
        cmp word [bp + 0x16], 1
        jg stink_hit                ; (a missile: the staff sling's stinkpot, STINKPOTS)
        mov word [cs:tg_how], MN_TANGLE << 8 | SHEET_PETRIFY
        push ax
        mov ax, [bp + 0x12]
        call item_is_cahulaks
        pop ax
        je .rule
        call trikal_trip            ; (THE TRIKAL: a specialist's hit trips)
        jnc .out
        mov word [cs:tg_how], MN_TRIP << 8 | SHEET_PARALYZE
.rule:  sti
        pushad
        push es
        mov bx, [TARGET]
        cmp bx, TANGLE_MOST
        jae .done
        mov ax, bx
        call fighter_creature
        jc .done
        imul si, ax, CREATURE_SIZE
        les di, [CREATURES_PTR]
        add di, si
        cmp word [es:di], 0
        jle .done                   ; (felled by the blow)
        mov ax, bx
        call is_large
        jc .done                    ; (too big to tangle: a half-giant, or large by the Loader's table)
        mov si, [es:di + 4]         ; (its sheet)
        imul si, si, SHEET_SIZE
        les di, [SHEETS_PTR]
        add di, si
        movzx si, byte [cs:tg_how]      ; (its save against petrification, or paralysis for a trip)
        add di, si
        movzx cx, byte [es:di]
        mov ax, 20
        call game_die
        mov [cs:mn_frame], bx
        mov dx, [bp + 0x18]
        mov [cs:mn_frame + 2], dx
        mov [cs:mn_frame + 4], ax
        mov [cs:mn_frame + 6], cx
        push ax
        push cx
        movzx ax, byte [cs:tg_how + 1]
        cmp al, MN_TRIP
        jne .rec
        inc word [cs:trip_saves]
.rec:   call mn_rec
        pop cx
        pop ax
        cmp ax, 20
        je .done                    ; (a natural 20 saves)
        cmp ax, cx
        jge .done                   ; (saved)
        cmp byte [cs:tg_how + 1], MN_TRIP
        jne .tangle
        inc word [cs:trips]
        jmp .lost
.tangle:
        inc word [cs:tangles]
.lost:
        call swept_now              ; (yet to act this round: this round's turn lost at once)
        jc .done
        mov si, bx
        call tangle_bit
        or [cs:tangled + si], al    ; (else its next turn's: CAH_MOVE)
.done:  pop es
        popad
.out:   iret
cah_move:
        call boots_move
        call kit_move                   ; (the kits': KITS)
        mov [es:bx + MOVE_OFF], ax
        cmp di, TANGLE_MOST
        jae .out
        pusha
        mov si, di
        call tangle_bit
        test [cs:tangled + si], al
        jz .kept
        not al
        and [cs:tangled + si], al
        mov word [es:bx + MOVE_OFF], 0
        shl bx, 1                   ; (the initiative's a creature x 4)
        mov word [es:bx + INIT_OFF], -1
        inc word [cs:tangle_turns]
.kept:  popa
.out:   iret
tangle_clear:                   ; (a fight's first round: no one tangled). All kept.
        push cx
        push di
        push es
        push cs
        pop es
        mov di, tangled
        mov cx, TANGLE_MOST / 8
        xor al, al
        rep stosb
        pop es
        pop di
        pop cx
        ret
; TANGLE_BIT: SI a combatant (under TANGLE_MOST): SI its byte in TANGLED, AL its bit. Others kept.
tangle_bit:
        push cx
        mov cx, si
        and cl, 7
        mov al, 1
        shl al, cl
        shr si, 3
        pop cx
        ret
; SWEPT_NOW: CF set when combatant BX, in a fight, has yet to act this round: not the one whose turn it
; is, its initiative not -1. Its turn is then taken at once, as CAH_MOVE takes a tangled one's. DS the
; game's; all kept.
swept_now:
        pushad
        push es
        cmp byte [IN_COMBAT], 0
        je .no
        mov ax, bx
        call fighter_creature
        jc .no
        mov di, ax
        mov ax, [WHOSE_TURN]
        call fighter_creature
        jc .no
        cmp ax, di
        je .no                      ; (its own turn: it acts now, and loses next round's)
        mov ax, ds
        sub ax, INIT_FROM_DS
        mov es, ax
        shl di, 2
        cmp word [es:di + INIT_OFF], -1
        je .no                      ; (it has acted: next round's)
        mov word [es:di + INIT_OFF], -1
        shr di, 1
        mov word [es:di + MOVE_OFF], 0
        inc word [cs:tangle_turns]
        pop es
        popad
        stc
        ret
.no:    pop es
        popad
        clc
        ret
; FIGHTER_CREATURE: AX a combatant: AX its creature, CF clear; CF set if it is none. DS the game's;
; others kept.
fighter_creature:
        cmp ax, 400
        jae .none
        push bx
        push es
        imul bx, ax, 3
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        cmp byte [es:bx + FIGHTERS_OFF], 2
        jne .no
        mov ax, [es:bx + FIGHTERS_OFF + 1]
        pop es
        pop bx
        clc
        ret
.no:    pop es
        pop bx
.none:  stc
        ret
; GAME_DIE: AX a roll of 1 to AX from the game's own seed (SEED), as its rand() steps it. Others kept.
game_die:
        push ebx
        push ecx
        push edx
        movzx ecx, ax
        mov eax, [SEED]
        imul eax, eax, 0x015A4E35
        inc eax
        mov [SEED], eax
        shr eax, 16
        and eax, 0x7FFF
        imul eax, ecx
        shr eax, 15
        inc eax
        pop edx
        pop ecx
        pop ebx
        ret
; MN_REC: a KIND_MANUAL entry, AX what (MN_*), the frame MN_FRAME's four words. CX, DX, SI, DI changed.
mn_rec:
        mov si, mn_frame
        mov cx, 4
        mov word [cs:kind], KIND_MANUAL
; REC_FRAME: DSCLOG's, an entry recorded (kind [CS:KIND], value AX) whose frame's +6 on are the CX words
; from CS:SI, as a far call's arguments (no return address: 0). CX, DX, SI, DI changed.
        SHARED_rec_frame
mn_frame  dw 0, 0, 0, 0
tangled   times TANGLE_MOST / 8 db 0
tangles   dw 0                  ; (tangles made, for a look in play)
tangle_turns dw 0               ; (turns taken so)

; THE TRIKAL AND THE TWO-HEADED WEAPONS: DSCLOG's (RULE_HI_CAHULAKS, the Loader's "Weapon traits", with the
; cahulaks' sites; the Dark Sun weapons guide's specialists), on the sequel's Lotulis (type 61), Double Spear
; (39) and Trikal (100) and any type KIND_OF_TYPE gives their kinds:
; - a trikal specialist's melee hit that does damage trips a man-sized or smaller target as the cahulaks
;   tangle one (CAH_HIT, TRIKAL_TRIP: its save against paralysis, the sheet's +31h, SHEET_PARALYZE; MN_TRIP);
;   the trikal reaches two squares as a polearm (REACH_HANDS);
; - a lotulis or double spear specialist's last swing of a round of two or more (SF_SWING, from CAH_SWING:
;   [BP-16h] the swing, [BP-0Ah] the round's) goes to a second foe beside it, when one is: a combatant on
;   the first target's side (SF_SIDE: the creature's +15h, the game's groups by its masks 71h and F80h,
;   23812h), standing and Okay (+14h 1, HP above 0), at the game's distance 1 from the attacker [BP+18h]
;   (1D40:35EFh, a call REACH leaves at 2); the first such in the combatants' order. TARGET is that foe
;   for the swing and the attack's AC ([BP+0Ch]) its own, from the game's AC routine (5D520h, in the
;   combat overlay: called at the INT's way back + SF_AC_GAP, its CS; the target, the attacker and the
;   behind flag [BP+20h], as the attack's set-up calls it at 5C9A7h); both put back as the swing ends
;   (SF_BACK, site 202 at the swing loop's "cmp ax,[bp-0Ah]", 5D308h, which every swing passes: SL's
;   AMMO_TURN's). The double spear's swing at it does 1 less damage, at least 1 (SF_LESS, from ENL_ROLL,
;   after the roll: STR in it). Recorded (MN_SECOND: +6 the second foe, +8 the attacker, +0Ah the first,
;   +0Ch 1 for the double spear).
MN_TRIP        equ 13
MN_SECOND      equ 14
SHEET_PARALYZE equ 0x31             ; (the sheet's save against paralysis/poison/death)
LOTULIS_KIND   equ 18               ; (KIND_OF_TYPE's lotulis, its kind + 1; the double spear's the next)
TRIKAL_KIND    equ 20               ; (... the trikal's)
DISTANCE_SEG   equ 0x1D40 - 0x47E0  ; (the distance routine's segment less DS)
SF_AC_GAP      equ 0x5D520 - 0x5D054  ; (the AC routine from CAH_SWING's way back)
CREATURE_SIDE  equ 0x15
SIDE_FRIENDS   equ 0x71             ; (the game's groups of +15h, by its bit)
SIDE_FOES      equ 0xF80
; TRIKAL_TRIP: CF if the melee hit is a trikal specialist's ([BP+12h] an item, [BP+14h] of the trikal's
; kind) and the rule on. All registers kept.
trikal_trip:
        test word [cs:rules_hi], RULE_HI_CAHULAKS
        jz .no
        cmp word [bp + 0x12], NO_ITEM
        jae .no
        push bx
        push dx
        mov bx, [bp + 0x14]
        cmp bx, KIND_TYPES
        jae .pop
        cmp byte [cs:bx + kind_of_type], TRIKAL_KIND
        jne .pop
        call spec_of
        cmp dl, SPEC_SPECIAL
        cmc                         ; (CF: specialized or better)
        pop dx
        pop bx
        ret
.pop:   pop dx
        pop bx
.no:    clc
        ret
; SF_SWING (CAH_SWING's, in melee; its INT's way back at [SP+2] here). All registers kept.
sf_swing:
        test word [cs:rules_hi], RULE_HI_CAHULAKS
        jz .ret
        pushad
        push es
        mov si, sp
        mov eax, [ss:si + 36]       ; (the INT's way back: the combat overlay's CS, and its IP)
        add ax, SF_AC_GAP
        mov [cs:sf_ac_at], eax
        cmp word [bp + 0x12], NO_ITEM
        jae .done
        mov bx, [bp + 0x14]
        cmp bx, KIND_TYPES
        jae .done
        movzx ax, byte [cs:bx + kind_of_type]
        sub ax, LOTULIS_KIND
        cmp ax, 1
        ja .done                    ; AX 0 the lotulis, 1 the double spear
        mov cx, [bp - 0x0A]
        dec cx
        jle .done                   ; (one swing)
        cmp cx, [bp - 0x16]
        jne .done                   ; (not the round's last)
        push ax
        call spec_of
        pop ax
        cmp dl, SPEC_SPECIAL
        jb .done
        mov [cs:mn_frame + 6], ax
        mov ax, [TARGET]
        mov [cs:mn_frame + 4], ax
        call sf_side
        jc .done
        mov di, ax                  ; DI the first target's side
        mov ax, ds
        add ax, DISTANCE_SEG
        mov [cs:sf_distance + 2], ax
        xor si, si
.each:  cmp si, [TARGET]
        je .next
        cmp si, [bp + 0x18]
        je .next
        mov ax, si
        call sf_side
        jc .next
        cmp ax, di
        jne .next
        push di
        push si
        push si
        push word [bp + 0x18]
        call far [cs:sf_distance]
        add sp, 4
        pop si
        pop di
        cmp ax, 1
        je .found
.next:  inc si
        cmp si, TANGLE_MOST
        jb .each
        jmp .done
.found: mov ax, [TARGET]
        mov [cs:sf_target], ax
        mov [TARGET], si
        mov [cs:mn_frame], si
        mov ax, [bp + 0x0C]
        mov [cs:sf_ac], ax
        movzx ax, byte [bp + 0x20]  ; (the attack's behind flag)
        mov dx, [bp + 0x18]
        mov bx, sp
        push word [ss:bx + 38]      ; (the INT's way back, in a frame the overlay manager can fix up)
        push word [ss:bx + 36]
        push bp
        mov bp, sp
        push ax
        push dx
        push si
        call far [cs:sf_ac_at]      ; (the game's AC routine: the foe's AC against the attacker)
        add sp, 6
        mov [cs:sf_ac_got], ax
        pop bp
        pop ax                      ; (the way back, as the overlay manager has left it)
        pop cx
        mov bx, sp
        mov [ss:bx + 36], ax
        mov [ss:bx + 38], cx
        mov ax, [cs:sf_ac_got]
        mov [bp + 0x0C], ax
        mov ax, [bp + 0x18]
        mov [cs:mn_frame + 2], ax
        mov ax, MN_SECOND
        call mn_rec
        inc word [cs:sf_swings]
.done:  pop es
        popad
.ret:   ret
; SF_SIDE: AX combatant AX's side (1 the game's friends, 2 its foes, else 100h + its own group), CF if
; it is no creature or isn't standing and Okay. BX, ES changed.
sf_side:
        call fighter_creature
        jc .ret
        imul bx, ax, CREATURE_SIZE
        les ax, [CREATURES_PTR]
        add bx, ax
        cmp word [es:bx], 0
        jle .no
        cmp byte [es:bx + CREATURE_STATUS], 1
        jne .no
        push cx
        mov cl, [es:bx + CREATURE_SIDE]
        mov ax, 1
        cmp cl, 15
        ja .own
        shl ax, cl
        test ax, SIDE_FRIENDS
        jnz .friend
        test ax, SIDE_FOES
        mov ax, 2
        jnz .side
.own:   movzx ax, cl
        or ah, 1
        jmp .side
.friend:
        mov ax, 1
.side:  pop cx
        clc
.ret:   ret
.no:    stc
        ret
; SF_BACK: the first target and its AC put back after a swing at a second foe. All kept.
sf_back:
        cmp word [cs:sf_target], -1
        je .ret
        push ax
        mov ax, -1
        xchg ax, [cs:sf_target]
        mov [TARGET], ax
        mov ax, [cs:sf_ac]
        mov [bp + 0x0C], ax
        inc word [cs:sf_backs]
        pop ax
.ret:   ret
; SF_SITE (site 202, "cmp ax,[bp-0Ah]" at 5D308h, the swing loop's test after each swing): SF_BACK, then
; the compare, its flags in the INT's frame.
sf_site:
        call sf_back
        push bx
        push ax
        cmp ax, [bp - 0x0A]
        pushf
        pop ax                      ; (the compare's flags)
        mov bx, sp
        and word [ss:bx + 8], ~0x08D5
        and ax, 0x08D5              ; (OF SF ZF AF PF CF)
        or [ss:bx + 8], ax
        pop ax
        pop bx
        iret
; SF_LESS (ENL_ROLL's, the hit's damage rolled, [BP-4]): the double spear's swing at a second foe 1 less,
; at least 1. All kept.
sf_less:
        cmp word [cs:sf_target], -1
        je .ret
        push bx
        mov bx, [bp + 0x14]
        cmp bx, KIND_TYPES
        jae .pop
        cmp byte [cs:bx + kind_of_type], LOTULIS_KIND + 1
        jne .pop
        cmp word [bp - 4], 1
        jle .pop
        dec word [bp - 4]
        inc word [cs:sf_lesses]
.pop:   pop bx
.ret:   ret
sf_distance dd 0x35EF
sf_ac_at    dd 0
sf_target   dw -1                   ; (the first target while a second foe is swung at; -1 none)
sf_ac       dw 0
sf_ac_got   dw 0
tg_how      dw 0                    ; (CAH_HIT: the save's offset, and above it the record's MN_)

; STINKPOTS: DSCLOG's (RULE_HI_CAHULAKS, the Loader's "Weapon traits"): the staff sling's shot is a
; stinkpot, a clay pot of burning sulphur (AD&D's Arms and Equipment Guide). Its damage is 1d3 against
; any size (STINK_SWING sets the call's sides, [BP-12h], on its first swing; the game's 1d4). A hit
; (STINK_HIT, from CAH_HIT for a missile: [BP+14h] the type, [BP+18h] the thrower, TARGET the target) on a
; target still standing, not undead (its sheet's race 9, as the sequel's own tests) and not immune to
; poison (the damage resistance routine 85052h, stub 628h:25h = the load + 475Ah: the share it takes of
; the poison kind, 1; 0 none), makes it save: the game's saving throw (66D26h, stub 598h:75h = the load +
; 46A7h; AL 0 failed) against Stinking Cloud (22: the sequel has no monster poison power as SL's 176). A
; failure: Nauseated (STINK_EFFECT, the sequel's empty effect 12, named and given Stinking Cloud's icon
; by the Loader's patch "nauseated_name") for 1d3+1 rounds, through the effect adder (7F9E6h, stub
; 608h:3Eh = the load + 473Bh), filed under Stinking Cloud. A nauseated attacker's swings are 2 worse
; (STINK_SWING, whatever the rules: only the rule puts it on). The far calls are made in a frame the
; overlay manager can fix up (the INT's way back in it, as ACID_ROUND's). Recorded: MN_STINK before the
; save (target, thrower, 0 a save follows, 1 undead, 2 immune to poison), MN_NAUSEA after it (target,
; thrower, the d3, the rounds; 0 and 0 saved).
STAFF_SLING_TYPE equ 98
STINK_SIDES  equ 3
STINK_EFFECT equ 12
STINK_SPELL  equ 22             ; (Stinking Cloud: the save's power and the effect's spell)
STINK_POISON equ 1              ; (the poison damage kind)
STINK_TO_HIT equ 2
STINK_UNDEAD equ 1              ; (MN_STINK's +0Ah)
STINK_IMMUNE equ 2
RACE_UNDEAD  equ 9
MN_STINK     equ 11
MN_NAUSEA    equ 12
SHARE_STUB   equ 0x475A - 0x47E0    ; (stubs, less DS)
SHARE_ENTRY  equ 0x25
SAVE_STUB    equ 0x46A7 - 0x47E0
SAVE_ENTRY   equ 0x75
ADD_STUB     equ 0x473B - 0x47E0
ADD_ENTRY    equ 0x3E
stink_swing:
        push ax
        push cx
        mov ax, [bp + 0x18]
        mov cl, STINK_EFFECT
        call has_effect
        jne .dice
        add word [bp + 0x0A], STINK_TO_HIT
        inc word [cs:nausea_swings]
.dice:  pop cx
        pop ax
        call ns_swing                   ; (the new spells' Fogbolt and Erdlu Claw)
        test word [cs:rules_hi], RULE_HI_CAHULAKS
        jz .ret
        cmp word [bp + 0x16], 1
        jle .ret
        cmp word [bp + 0x12], NO_ITEM
        jae .ret
        cmp word [bp + 0x14], STAFF_SLING_TYPE
        jne .ret
        push ax
        mov ax, [bp - 0x16]
        cmp ax, [bp - 0x0C]
        pop ax
        jne .ret                    ; (the call's first swing: the dice set once a call)
        mov word [bp - 0x12], STINK_SIDES
.ret:   ret
stink_hit:
        test word [cs:rules_hi], RULE_HI_CAHULAKS
        jz .out
        cmp word [bp + 0x12], NO_ITEM
        jae .out
        cmp word [bp + 0x14], STAFF_SLING_TYPE
        jne .out
        sti
        pushad
        push es
        mov bx, [TARGET]
        cmp bx, TANGLE_MOST
        jae .done
        mov ax, bx
        call fighter_creature
        jc .done
        imul si, ax, CREATURE_SIZE
        les di, [CREATURES_PTR]
        add di, si
        cmp word [es:di], 0
        jle .done                   ; (felled by the blow)
        mov [cs:mn_frame], bx
        mov ax, [bp + 0x18]
        mov [cs:mn_frame + 2], ax
        mov dword [cs:mn_frame + 4], 0
        mov si, [es:di + 4]
        imul si, si, SHEET_SIZE
        les di, [SHEETS_PTR]
        add di, si
        mov dx, STINK_UNDEAD
        cmp byte [es:di + SHEET_RACE], RACE_UNDEAD
        je .spared
        mov bx, sp
        push word [ss:bx + 36]      ; (the way back, in a frame the overlay manager can fix up)
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        push word STINK_POISON
        push cs
        push word stink_none        ; (its effects' bits: none count against poison)
        push word [cs:mn_frame]
        mov ax, SHARE_STUB
        mov dx, SHARE_ENTRY
        call stink_at
        call far [cs:stink_ptr]
        add sp, 8
        mov dx, STINK_IMMUNE
        or ax, ax
        jz .spared_back
        inc word [cs:stinks]
        mov ax, MN_STINK
        call mn_rec
        push word 0                 ; (the level)
        push word STINK_SPELL
        push word [cs:mn_frame + 2]
        push word [cs:mn_frame]
        mov ax, SAVE_STUB
        mov dx, SAVE_ENTRY
        call stink_at
        call far [cs:stink_ptr]
        add sp, 8
        or al, al
        jnz .saved
        mov ax, 3
        call game_die
        mov [cs:mn_frame + 4], ax
        inc ax
        mov [cs:mn_frame + 6], ax
        inc word [cs:nauseas]
        push word 0
        push word 0
        imul ax, ax, ROUND_SECONDS
        push ax
        push word STINK_EFFECT
        push word STINK_SPELL
        push word [cs:mn_frame + 2]
        push word [cs:mn_frame]
        mov ax, ADD_STUB
        mov dx, ADD_ENTRY
        call stink_at
        call far [cs:stink_ptr]
        add sp, 14
.saved: mov ax, MN_NAUSEA
        call mn_rec
        jmp .back
.spared_back:
        mov [cs:mn_frame + 4], dx
        mov ax, MN_STINK
        call mn_rec
.back:  pop bp
        pop ax                      ; (the way back, as the overlay manager has left it)
        pop cx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], cx
        jmp .done
.spared:
        mov [cs:mn_frame + 4], dx
        mov ax, MN_STINK
        call mn_rec
.done:  pop es
        popad
.out:   iret
; STINK_AT: STINK_PTR made the game's stub AX (less DS), entry DX, for a far call. DS the game's; BX kept.
stink_at:
        push bx
        mov bx, ds
        add ax, bx
        mov [cs:stink_ptr + 2], ax
        mov [cs:stink_ptr], dx
        pop bx
        ret
stink_ptr  dd 0
stink_none times 10 db 0
stinks     dw 0                 ; (stinkpot saves made, for a look in play)
nauseas    dw 0                 ; (Nauseated put on)
nausea_swings dw 0              ; (a nauseated attacker's swings)

; REACH: DSCLOG's (RULE_HI_CAHULAKS, the Loader's "Weapon traits"): a polearm reaches two squares. INT
; VEC_REACH replaces "mov ax,[bp-1Ch]" (25CDDh; 3 bytes: INT + NOP) at the end of the combatant distance
; routine (1D40:35EFh, 25BEFh; SL's 1A0A:2BA5h: [BP+6] the attacker, [BP+8] the target, both combatants;
; the least square distance between their footprints: 1 adjacent, diagonals too, 2 the square beyond).
; It does the MOV; then with the rule, for a distance of 2 asked by one of the game's melee tests
; (REACH_CALLER), an attacker whose hands hold a polearm and no other weapon (REACH_HANDS), and no wall
; on the line between the two (REACH_LINE), AX 1: the game then takes the target as adjacent. The melee
; tests, by their way back as a place in the program (the caller's CS less the load, x 16, + IP; each
; compares the distance with 1): the pointer's sword (20617h), the attack pointer's click (1EADCh), the
; walk arrow's click on a foe (1E2AAh), the walk to attack arriving (1FF39h and 260CBh), the step
; switch's case (2420Ah); and the computer's choice of an attack, in the combat overlay (5A920h on,
; loaded anywhere): its target's distance against its weapon's range (IP 14A2h, 5BDC2h) and the target
; it found in range (IP 1A72h, 5C392h), each told by its IP and the code around it (a far call to
; 35EFh before, its segment as the overlay loader made it; "add sp,4 / mov [bp-0Ah],ax" after). Every other caller (the spells', a missile's)
; keeps 2. The polearm: KIND_OF_TYPE's polearm (type 80).
REACH_AI_RANGE equ 0x14A2
ITEM_LISTS_MOST equ 520         ; (the things the combatants' table holds)
REACH_AI_FOUND equ 0x1A72
POLEARM_KIND equ 10
TYPE_WEAPON  equ 3              ; (a type's flags, +00h: 1 a melee weapon, 2 a missile weapon)
WALL_POS     equ 0x67C5         ; DS: the map things' feet (x, y), THING_SIZE a thing (sixteenths of a square)
REACH_LINE_SEG equ 0x0B0B - 0x47E0  ; (the line test's segment, 0B0Bh:00A4h (10354h), less DS)
reach_rets   dd 0x20617 - 0x5200, 0x1EADC - 0x5200, 0x1E2AA - 0x5200, 0x1FF39 - 0x5200
             dd 0x260CB - 0x5200, 0x2420A - 0x5200
REACH_RETS   equ ($ - reach_rets) / 4
reaches      dw 0               ; (distances of 2 made 1, for a look in play)
reach_site:
        mov ax, [bp - 0x1C]
        cmp ax, 2
        jne .out
        test word [cs:rules_hi], RULE_HI_CAHULAKS
        jz .out
        sti
        pushad
        push es
        call reach_caller
        jne .no
        mov ax, [bp + 6]
        call reach_hands
        jne .no
        call reach_line
        jne .no
        inc word [cs:reaches]
        pop es
        popad
        mov ax, 1
        iret
.no:    pop es
        popad
        mov ax, 2
.out:   iret

; REACH_CALLER: ZF if the distance routine's way back ([BP+2], [BP+4]) is one of REACH's melee tests.
; DS the game's; EAX, CX, EDX, SI, DI, ES changed.
reach_caller:
        movzx edx, word [bp + 4]
        mov ax, ds
        sub ax, DGROUP_GAP
        movzx eax, ax
        sub edx, eax                    ; (the caller's CS less the load)
        shl edx, 4
        movzx eax, word [bp + 2]
        add edx, eax
        mov si, reach_rets
        mov cx, REACH_RETS
.res:   cmp edx, [cs:si]
        je .ret
        add si, 4
        loop .res
        mov ax, [bp + 2]
        cmp ax, REACH_AI_RANGE
        je .code
        cmp ax, REACH_AI_FOUND
        jne .ret
.code:  mov es, [bp + 4]
        mov di, ax
        cmp word [es:di - 5], 0xEF9A    ; (call far 35EFh: its segment the overlay loader's)
        jne .ret
        cmp byte [es:di - 3], 0x35
        jne .ret
        cmp dword [es:di], 0x8904C483   ; (add sp,4 / mov [bp-0Ah],ax)
        jne .ret
        cmp word [es:di + 4], 0xF646
.ret:   ret

; REACH_HANDS: ZF if combatant AX holds a polearm in a hand (the right, RIGHT_HAND, or the left,
; LEFT_HAND) and no other weapon (a type with a melee or missile flag) in either. Its three item lists
; (the creature's +08h, +0Ah, +0Ch: things, kind 1, in the combatants' table), by each item's slot. DS
; the game's; AX, BX, CX, DX, SI, DI, ES changed.
reach_hands:
        call fighter_creature
        jc .none
        imul di, ax, CREATURE_SIZE
        xor dx, dx                      ; (DL the polearms in the hands, DH the other weapons)
        mov cx, 8
.list:  les bx, [CREATURES_PTR]
        add bx, di
        add bx, cx
        mov si, [es:bx]
        cmp si, ITEM_LISTS_MOST         ; (item lists are things 201h and on in the table)
        jae .next
        mov ax, ds
        add ax, FIGHTERS_SEG
        mov es, ax
        imul si, si, 3
        cmp byte [es:si + FIGHTERS_OFF], 1
        jne .next                       ; (not an item list)
        mov si, [es:si + FIGHTERS_OFF + 1]
        mov byte [cs:reach_left], 100
.item:  cmp si, NO_ITEM
        jae .next
        les bx, [ITEMS_PTR]
        imul ax, si, ITEM_SIZE
        add bx, ax
        mov al, [es:bx + ITEM_SLOT]
        cmp al, RIGHT_HAND
        je .hand
        cmp al, LEFT_HAND
        jne .on
.hand:  mov ax, [es:bx + ITEM_TYPE]
        cmp ax, KIND_TYPES
        jae .other
        push bx
        mov bx, ax
        cmp byte [cs:bx + kind_of_type], POLEARM_KIND
        je .pole
        cmp byte [cs:bx + kind_of_type], TRIKAL_KIND   ; (the trikal: a pole too, DSCLOG's)
.pole:  pop bx
        jne .other
        inc dl
        jmp .on
.other: push es
        push bx
        imul ax, ax, TYPE_SIZE
        les bx, [ITEM_TYPES_PTR]
        add bx, ax
        test byte [es:bx], TYPE_WEAPON
        pop bx
        pop es
        jz .on
        inc dh
.on:    mov si, [es:bx + ITEM_NEXT]
        dec byte [cs:reach_left]
        jnz .item
.next:  add cx, 2
        cmp cx, 0x0E
        jb .list
        cmp dx, 1                       ; (one polearm, no other weapon)
        ret
.none:  or sp, sp                       ; (no creature: ZF clear)
        ret
reach_left db 0

; REACH_LINE: ZF if no wall is on the line from attacker [BP+6]'s square to target [BP+8]'s, by the
; game's own test (0B0Bh:00A4h, 10354h: two squares, x, y and a height of 0 each; 0, or -1 blocked),
; the one the attack pointer's click makes (1EAA7h). DS the game's; AX, BX, CX, DX, ES changed.
reach_line:
        mov bx, [bp + 8]
        imul bx, bx, THING_SIZE
        push word 0
        mov ax, [bx + WALL_POS + 2]
        shr ax, 4
        push ax
        mov ax, [bx + WALL_POS]
        shr ax, 4
        push ax
        mov bx, [bp + 6]
        imul bx, bx, THING_SIZE
        push word 0
        mov ax, [bx + WALL_POS + 2]
        shr ax, 4
        push ax
        mov ax, [bx + WALL_POS]
        shr ax, 4
        push ax
        mov ax, ds
        add ax, REACH_LINE_SEG
        mov [cs:reach_line_at + 2], ax
        call far [cs:reach_line_at]
        add sp, 12
        or ax, ax
        ret
reach_line_at dw 0xA4, 0

; SIZE: DSCLOG's (RULE_HI_SIZE, always on), AD&D's creature sizes, which the game keeps none of. A
; combatant is large (IS_LARGE) when a half-giant (its sheet's race) or marked in LARGE_BITS (the
; Loader's, from dsloader/sizes.py's sequel table: large, huge or gargantuan; Enlarge isn't counted
; yet). Then:
; - a weapon's hit on it rolls AD&D's dice for large targets (SIZE_DICE, from CAH_SWING at the call's
;   first swing: the call's dice [BP-10h] the count, [BP-12h] the sides, [BP-14h] the bonus, SL's
;   -0Eh..-12h; [BP-0Ch] the call's first swing), by the weapon's kind (KIND_OF_TYPE: the sequel's
;   types of SL's kinds; its own weapons, the Twohand Sword, Trikal, Lotulis and the rest, keep the
;   game's dice), Spiritual Hammer (95) 1d4; and Shillelagh's (90) 2d4 1d6+1 on a smaller one;
; - Hold Person (30, the priests' 136) and Charm Person (2) don't take: SIZE_SPARED, from PROBE_SAVE,
;   makes the save's total 101 (the dice log: "too big for ... -> unaffected"; the game's compare a
;   save made).
RULE_HI_SIZE  equ 0x4000
SHILLELAGH_TYPE equ 90
HAMMER_TYPE   equ 95
is_large:                           ; CF if combatant AX is large (see SIZE). DS the game's; all kept.
        pusha
        push es
        mov dx, ax
        test word [cs:rules_hi], RULE_HI_SIZE
        jz .race
        cmp ax, LARGE_MOST
        jae .race
        mov si, ax
        call tangle_bit
        push fs
        call tail_fs
        test [fs:large_bits + si], al   ; (LARGE_BITS: the tail's)
        pop fs
        jnz .yes
.race:  mov ax, dx
        call fighter_creature
        jc .no
        imul si, ax, CREATURE_SIZE
        les di, [CREATURES_PTR]
        add di, si
        mov si, [es:di + 4]
        jmp .sheet
.no:    pop es
        popa
        clc
        ret
.sheet: imul si, si, SHEET_SIZE
        les di, [SHEETS_PTR]
        add di, si
        cmp byte [es:di + SHEET_RACE], RACE_HALF_GIANT
        jne .no
.yes:   pop es
        popa
        stc
        ret
size_dice:
        test word [cs:rules_hi], RULE_HI_SIZE
        jz .ret
        pusha
        mov ax, [bp - 0x16]
        cmp ax, [bp - 0x0C]
        jne .done                   ; (the call's first swing only: the dice set once a call)
        cmp word [bp + 0x12], NO_ITEM
        jae .done                   ; (a natural attack: its own damage)
        mov bx, [bp + 0x14]
        mov ax, [TARGET]
        call is_large
        jc .large
        cmp bx, SHILLELAGH_TYPE     ; (smaller: Shillelagh's 1d6+1 for the game's 2d4)
        jne .done
        mov word [bp - 0x10], 1
        mov word [bp - 0x12], 6
        inc word [bp - 0x14]
        jmp .done
.large: inc word [cs:large_hits]
        cmp bx, HAMMER_TYPE
        jne .kind
        dec word [bp - 0x14]        ; (Spiritual Hammer: 1d4)
        jmp .done
.kind:  mov si, rav_large                ; (the sequel's own weapons first: RAV_LARGE)
        or bh, bh
        jnz .table
.own:   cmp byte [cs:si], 0
        je .table
        cmp bl, [cs:si]
        je .found
        add si, 4
        jmp .own
.found: movzx ax, byte [cs:si + 1]
        or ax, ax
        jz .done                    ; (its dice the same on any size)
        mov [bp - 0x10], ax
        movzx ax, byte [cs:si + 2]
        mov [bp - 0x12], ax
        movsx ax, byte [cs:si + 3]
        add [bp - 0x14], ax
        call spec_grand_die         ; (a grand master's: the next greater die, as its own dice's at
        jmp .done                   ;   SPEC_DAMAGE, which these replace)
.table: cmp bx, KIND_TYPES
        jae .done
        movzx si, byte [cs:bx + kind_of_type]
        or si, si
        jz .done
        dec si
        imul si, si, 3
        push fs
        call tail_fs                ; (LARGE_DICE: the tail's)
        movzx ax, byte [fs:si + large_dice]
        pop fs
        or ax, ax
        jz .done
        mov [bp - 0x10], ax
        push fs
        call tail_fs
        movzx ax, byte [fs:si + large_dice + 1]
        mov [bp - 0x12], ax
        movsx ax, byte [fs:si + large_dice + 2]
        pop fs
        add [bp - 0x14], ax
        call spec_grand_die
.done:  popa
.ret:   ret
size_spared:                        ; (PROBE_SAVE's) a save's total 101 for Hold or Charm Person on a
        test word [cs:rules_hi], RULE_HI_SIZE   ;   large target ([BP+6]; the spell [BP+0Ah]). All kept.
        jz .ret
        cmp word [bp + 0x0A], 2
        je .spell
        cmp word [bp + 0x0A], 30
        je .spell
        cmp word [bp + 0x0A], 136
        jne .ret
.spell: push ax
        mov ax, [bp + 6]
        call is_large
        pop ax
        jnc .ret
        mov byte [bp - 2], 101
        inc word [cs:spared_count]
.ret:   ret
; SIZE_LINE (site 249 at 7B1CFh, "inc word [bp-2]", 3 bytes; DSCLOG's SIZE_LINE, SL's 72AA7h) in the
; routine writing a weapon's lines (7AF9Eh: an item box's, [BP-6] its creature 0; the inventory screen's and
; the Look box's, its creature's), its damage line just drawn from SS:[BP-2Eh] ("1D8+4"; SI the item type):
; an item box's line drawn again with the dice against a large target after it ("1D8+4/1D12+4", as
; Shattered Lands' box), when they differ (SZ_CHANGE: RAV_LARGE, then LARGE_DICE by KIND_OF_TYPE, as
; SIZE_DICE's; Shillelagh's 2D4, its line 1D6+1 by SIZE_PRE). Always, as SL's (the rule's on in both). The
; text routine's far address is the game's call's, before the site; the line's x, y and colours the
; call's ([BP+0Ch], [BP+10h], [BP+12h], [BP+14h]: the sequel's arguments 2 bytes on from SL's).
SZ_DRAW  equ 0x7B1C8 - 0x7B1D2      ; (the text routine's far address in that call, less the way back)
SZ_TEXT  equ 0x2E                   ; ([BP-2Eh]: the line)
size_line:
        inc word [bp - 2]
        cmp dword [bp - 6], 0
        jne .ret                    ; (an item box's only)
        sti                         ; (interrupts on while the game's text routine draws: the INT
        pushad                      ;   turned them off; IRET puts the caller's back)
        push es
        mov ax, 0x0402              ; (Shillelagh: 2D4, its line 1D6+1)
        mov dl, -1
        cmp si, SHILLELAGH_TYPE
        je .parse
        call sz_change
        jc .out
.parse: call sz_parse
        jc .out
        mov si, sp
        les bx, [ss:si + 34]        ; the way back (after ES and the PUSHAD)
        mov ecx, [es:bx + SZ_DRAW]
        mov [cs:sz_draw], ecx
        push ss                     ; "/1D12+4" after the line
        pop es
        lea di, [bp - SZ_TEXT]
.end:   cmp byte [es:di], 0
        je .slash
        inc di
        jmp .end
.slash: mov byte [es:di], '/'
        inc di
        call sz_write
        push word [bp + 0x14]
        push word [bp + 0x12]
        push word [bp + 0x10]
        push word [bp + 0x0C]
        push ss
        lea cx, [bp - SZ_TEXT]
        push cx
        push dword [bp + 6]         ; the window
        call far [cs:sz_draw]
        add sp, 16
        inc word [cs:sz_count]
.out:   pop es
        popad
.ret:   iret

; SZ_CHANGE: for item type SI, AL the count and AH the sides of its dice against a large target (0: its
; own) and DL its bonus's change (signed); CF if they are its own. As SIZE_DICE: the Spiritual Hammer 1 off
; its bonus; the sequel's own weapons by RAV_LARGE first (a count 0 there: the same on any size), else by
; kind (KIND_OF_TYPE, LARGE_DICE); not Shillelagh: its callers'. Others kept.
sz_change:
        push bx
        push cx
        xor ax, ax
        mov dl, -1
        cmp si, HAMMER_TYPE
        je .ok
        mov bx, rav_large
        mov cx, si
        or ch, ch
        jnz .table
.own:   cmp byte [cs:bx], 0
        je .table
        cmp cl, [cs:bx]
        je .found
        add bx, 4
        jmp .own
.found: mov al, [cs:bx + 1]
        or al, al
        jz .none                    ; (its dice the same on any size)
        mov ah, [cs:bx + 2]
        mov dl, [cs:bx + 3]
        jmp .ok
.table: cmp si, KIND_TYPES
        jae .none
        movzx bx, byte [cs:si + kind_of_type]
        or bx, bx
        jz .none
        dec bx
        imul bx, bx, 3
        push fs
        call tail_fs                ; (LARGE_DICE: the tail's)
        mov ax, [fs:bx + large_dice]
        mov dl, [fs:bx + large_dice + 2]
        pop fs
        or al, al
        jz .none
.ok:    pop cx
        pop bx
        clc
        ret
.none:  pop cx
        pop bx
        stc
        ret

; SZ_PARSE: SZ_DICE and SZ_BONUS from the line at SS:[BP-2Eh] ("1.5x1D8+7"): AL the count and AH the
; sides for its (0: the line's), its bonus DL (signed) more; DI the count's first digit. CF if the line
; has no D. BX, CX, DX lost. (DSCLOG's SL_PARSE.)
sz_parse:
        lea bx, [bp - SZ_TEXT]
        mov di, bx
.d:     mov cl, [ss:di]             ; the D
        or cl, cl
        jz .none
        cmp cl, 'D'
        je .back
        inc di
        jmp .d
.none:  stc
        ret
.back:  cmp di, bx                  ; the count's digits before it
        je .count
        mov cl, [ss:di - 1]
        sub cl, '0'
        cmp cl, 9
        ja .count
        dec di
        jmp .back
.count: mov bx, di
        push ax
        call sz_number
        pop ax
        or al, al
        jnz .c
        mov al, cl
.c:     inc bx                      ; (past the D)
        push ax
        call sz_number
        pop ax
        or ah, ah
        jnz .s
        mov ah, cl
.s:     movsx dx, dl
        mov cl, [ss:bx]
        inc bx
        cmp cl, '+'
        je .plus
        cmp cl, '-'
        jne .sum
        call sz_number
        sub dx, cx
        jmp .sum
.plus:  call sz_number
        add dx, cx
.sum:   mov [cs:sz_dice], ax
        mov [cs:sz_bonus], dx
        clc
        ret

; SIZE_PRE (site 250 at 7B1B2h, "push word [bp+14h]", 3 bytes; DSCLOG's SIZE_PRE, SL's 72A8Ah) in the same
; routine, its damage line made at SS:[BP-2Eh] and about to be drawn (SI the item type): Shillelagh's (the
; game's 2D4, AD&D's against a large target) made 1D6+1, AD&D's against a smaller one (SIZE_DICE's), the
; rate kept, in the item box, the inventory and the Look box; the box's then gets its "/2D4" (SIZE_LINE).
; Then the push, the interrupt's frame moved down a word for it.
size_pre:
        pushad
        push es
        cmp si, SHILLELAGH_TYPE
        jne .push
        mov ax, 0x0601              ; 1D6, its bonus 1 more
        mov dl, 1
        call sz_parse
        jc .push
        push ss
        pop es
        call sz_write               ; (over the count on: "1.5x1D6+1")
.push:  pop es
        popad
        sub sp, 2
        push bp
        push ax
        mov bp, sp
        mov ax, [bp + 6]
        mov [bp + 4], ax            ; IP
        mov ax, [bp + 8]
        mov [bp + 6], ax            ; CS
        mov ax, [bp + 10]
        mov [bp + 8], ax            ; flags
        mov bp, [bp + 2]            ; (the game's BP)
        mov ax, [bp + 0x14]
        mov bp, sp
        mov [bp + 10], ax           ; the word pushed
        pop ax
        pop bp
        iret

; SZ_NUMBER: CX the number at SS:BX (its digits; 0 if none), BX past them. Others kept.
sz_number:
        push ax
        xor cx, cx
.next:  mov al, [ss:bx]
        sub al, '0'
        cmp al, 9
        ja .out
        imul cx, cx, 10
        movzx ax, al
        add cx, ax
        inc bx
        jmp .next
.out:   pop ax
        ret

; SZ_WRITE: SZ_DICE and SZ_BONUS ("1D12+7"; no bonus at 0) at ES:DI, a NUL after. Others kept.
sz_write:
        pusha
        movzx ax, byte [cs:sz_dice]
        call sz_digits
        mov byte [es:di], 'D'
        inc di
        movzx ax, byte [cs:sz_dice + 1]
        call sz_digits
        mov ax, [cs:sz_bonus]
        or ax, ax
        jz .end
        mov byte [es:di], '+'
        jg .sign
        mov byte [es:di], '-'
        neg ax
.sign:  inc di
        call sz_digits
.end:   mov byte [es:di], 0
        popa
        ret

; SZ_DIGITS: AX (0-999) in decimal at ES:DI, DI past it. AX, BX, CX, DX lost.
sz_digits:
        mov bx, 10
        xor cx, cx
.div:   xor dx, dx
        div bx
        push dx
        inc cx
        or ax, ax
        jnz .div
.put:   pop dx
        add dl, '0'
        mov [es:di], dl
        inc di
        loop .put
        ret
sz_draw   dd 0
sz_dice   dw 0                      ; (the large dice: the count, then the sides)
sz_bonus  dw 0
sz_count  dw 0                      ; (the box lines drawn again, for a look in play)
; KIND_OF_TYPE: the sequel's item types' weapon kinds, as specialize.KINDS + 1 (0 none): long sword 1,
; club 2, dagger 3, short sword 4, mace 5, axe 6, great axe 7, pick 8, quarterstaff 9, polearm 10, gythka
; 11, cahulaks 12, chatkcha 13, bow 14, sling 15, staff sling 16, two-handed sword 17, lotulis 18, double
; spear 19, trikal 20, javelin 21, darts 22 (from OBJEX.GFF's items' names, dice and two-handed bit: the
; Longswords 16, 73, 97, Flameblade 47, Magma blade 69; Club 29, Toothed Club 89; Daggers 37, 72, 99;
; Maces 67, 74; Axes 8, 48; Great Axe 51; Pick 79; Quarterstaff 85; Polearm 80; Gythka 52; Cahulaks 24;
; Chatchka 25; Bow 18; Sling 93; Staff Sling 98; Twohand Sword 101 and Crystal sword 35 (two-handed
; 1d10); Lotulis 61; Double Spear 39; Trikal 100; Javelin 59; Darts 38, 43. Shillelagh, 90, has none).
; RAV_LARGE: the sequel's weapons whose game dice aren't those of SL's kind (KIND_OF_TYPE), or that have
; none: type, then AD&D's dice against a large target (count, sides, the bonus's change; count 0: the
; same dice on any size). By the AD&D weapon whose small and man-sized dice are the game's (the
; reasoning: DEVELOPMENT-RULES.md, Creature size, Wake of the Ravager's weapons). Ends with type 0.
rav_large:
        db 35, 3, 6, 0          ; Crystal sword, two-handed 1d10: the two-handed sword's 3d6
        db 38, 0, 0, 0          ; Darts 1d2: the same on any size
        db 39, 1, 8, 0          ; Double Spear 1d6: the spear's 1d8
        db 43, 1, 3, 0          ; Darts 1d4: 1d3 (the dart one die down)
        db 47, 0, 0, 0          ; Flameblade 1d4+4: the spell's, any size
        db 48, 1, 4, 0          ; Axe 1d6: the hand axe's 1d4
        db 59, 0, 0, 0          ; Javelin: the same on any size
        db 61, 2, 6, 0          ; Lotulis 2d4: the bardiche's 2d6 (Dark Sun's lotulis does more to the large)
        db 79, 1, 4, -1         ; Pick 1d4+1: the horseman's pick's 1d4
        db 81, 2, 6, 0          ; Promere hammer, two-handed 1d10: the halberd's 2d6
        db 89, 1, 6, 1          ; Toothed Club 1d8+2: the morning star's 1d6+1, its +2 kept
        db 100, 2, 6, 0         ; Trikal 1d10: the halberd's 2d6
        db 101, 3, 6, 0         ; Twohand Sword 1d10: the two-handed sword's 3d6
        db 0
kind_of_type:
        db 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 1   ; types 0-16
        db 0, 14, 0, 0, 0, 0, 0, 12, 13, 0, 0, 0, 2, 0, 0, 0, 0   ; types 17-33
        db 0, 17, 0, 3, 22, 19, 0, 0, 0, 22, 0, 0, 0, 1, 6, 0, 0   ; types 34-50
        db 7, 11, 0, 0, 0, 0, 0, 0, 21, 0, 18, 0, 0, 0, 0, 0, 5   ; types 51-67
        db 0, 1, 0, 0, 3, 1, 5, 0, 0, 0, 0, 8, 10, 0, 0, 0, 0   ; types 68-84
        db 9, 0, 0, 0, 2, 0, 0, 0, 15, 0, 0, 0, 1, 16, 3, 20, 17   ; types 85-101
        ; the mod's types (OBJEX2.GFF's 102-145, SL's 115-158: ravager.mod_type), SL's kinds
        ; (specialize.KIND_OF_TYPE): its short swords, axes, great axes, picks, polearms, cahulaks
        db 4, 0, 0, 4, 6, 4, 6, 4, 0, 3, 5, 7, 8, 10, 0, 0, 0   ; types 102-118
        db 0, 0, 0, 0, 3, 7, 7, 3, 0, 0, 0, 0, 0, 0, 12, 12      ; types 119-134
        ; the Ravager weapons backported: five plain ones' places (SL's 148-152, which go back as the
        ; sequel's own: ravager.sequel_weapon_type), SL's wooden darts (153), then the metal great sword, lotulis and javelin, the
        ; obsidian lotulis and the bone great sword (SL's 154-158), their material kept
        db 17, 18, 19, 20, 21, 22, 17, 18, 21, 18, 17            ; types 135-145
        ; Shattered Lands' own weapon types the sequel has none of its kind and material (ravager.SL_EXTRA_TYPES):
        ; its bone long sword
        db 1                                                     ; type 146
LARGE_MOST    equ 520
section tail                        ; (LARGE_DICE and LARGE_BITS: the tail's)
large_dice   db 1, 12, 0            ; long sword: 1d12 (DSCLOG's LARGE_DICE, sizes.LARGE_DICE)
             db 1, 3, 0             ; club: 1d3
             db 1, 3, 0             ; dagger: 1d3
             db 1, 8, 0             ; short sword: 1d8
             db 1, 6, -1            ; mace: 1d6 (the game's 1d6+1)
             db 1, 10, 0            ; axe: 1d10
             db 2, 8, 0             ; great axe: 2d8
             db 2, 4, -1            ; pick: 2d4
             db 0, 0, 0             ; quarterstaff: the same
             db 2, 6, 0             ; polearm: 2d6
             db 1, 10, 0            ; gythka: 1d10
             db 0, 0, 0             ; cahulaks: the same
             db 1, 4, 0             ; chatkcha: 1d4
             db 0, 0, 0             ; bow: the same
             db 0, 0, 0             ; sling: the same
             db 0, 0, 0             ; staff sling: the same
             db 3, 6, 0             ; two-handed sword: 3d6 (the sequel's own weapons: RAV_LARGE first)
             db 1, 12, 0            ; lotulis: 1d12
             db 0, 0, 0, 0, 0, 0, 0, 0, 0 ; double spear, trikal, javelin: the same
             db 1, 2, 0             ; darts: 1d2
section tailz
large_bits times LARGE_MOST / 8 + 1 db 0
section image
large_hits   dw 0               ; (hits on large targets, for a look in play)
spared_count dw 0               ; (Hold or Charm Person spared so)

; ---- KIT PAGE: DSCLOG's creation panel's KIT pages (kitpages.py) in the sequel ----
; With the kits' rule (RULE_HI_KITS), a character of one class (or of a multiclass group: kitpages.MULTI)
; takes a kit on the creation screen, on a page of its own in the panel as Shattered Lands' has it: the
; Loader's copy of RESOURCE.GFF (ravager.resources_fixed, kitpages.rav_chunks) has the kit pages (3026 on,
; by class or group), and the disciplines' and spheres' windows with KITS for their button (3022, 3023),
; made from the sequel's own (19504, 19505). The kit chosen is the creation sheet's KIT_BYTE (+3Dh: 0 none,
; 1-3 the class's kits, KIT_OPEN while taken back), which goes with the sheet when DONE copies it (NEW_SHEET
; makes KIT_OPEN none). The creation overlay is Shattered Lands' code at the sequel's addresses (its stub
; 46CCh, the same entries; DS's numbers below, SL's in brackets): the sites, as DSCLOG's probes,
; - KP_DISC_WIN (site 62, "push 4C30h", 6FA45h: SL's PROBE_WP_DISC_WIN), KP_SPHERE_WIN (site 63, "push
;   4C31h", 6BEC2h: PROBE_WP_SPHERE_WIN): the windows being opened, 3022 or 3023 in their place for a
;   class with kits (WP_IDS); the disciplines' opening (not on the way back to them, KIT_KEEP) a new
;   character's kit none, an EDIT's (CR_EDITING not -1) kept;
; - KP_DISC_CLICK (site 64, "mov bx,[bp+8]", 6C096h), KP_SPHERE_CLICK (site 65, 6C036h): those windows'
;   clicks, KITS opening the kit page, its rows and VIEW PSIONICS (WP_CLICK);
; - KP_SHOWN (site 66, "cmp ax,8", 6B10Ah: PROBE_WP_SHOWN): a class picked, the game asks whether the
;   spheres' window is up to close it: also for 3023 or a kit page;
; - KP_CLASS (site 67, "mov cl,1 / les bx,[1429h]", 6E026h: PROBE_WP_CLASS, SL's "mov cx,1"): after each
;   click on the screen: other classes than last seen, no kit; the panel made the one for the classes;
; - KP_RACE (site 68, "add sp,6", 6B191h: PROBE_RACE_PANEL): a new race or sex, the panel the right one;
; - KP_OPEN (site 69, "mov byte [1C96h],0FFh", 6D891h: SL's CR_OPEN's place): the screen opening.
; A kit's own hit die or PSP rolled again on its choice: KIT_ROW's KIT_REROLL (KIT PSP COSTS ... AND CASTING
; AFTER A HIT). Not here (DSCLOG's, for rules the sequel hasn't yet): the THAC0 shown again, the Elementalist's second sphere (EL_*), EDIT's kit given
; back after its classes are changed and changed back (ED_*), the age and weapon specs (CR_AGE,
; CR_WEAPONS).
KP_DISC_ID   equ 19504              ; (the game's windows: SL's 3012, 3013)
KP_SPHERE_ID equ 19505
KIT_DISC_ID  equ 3022
KIT_SPHERE_ID equ 3023
KIT_WIN_ID   equ 3026
KIT_GROUPS   equ 19                 ; (the classes' and the multiclass groups' pages)
KIT_ROW      equ 0x870
KIT_NONE     equ 0x888
KIT_VIEW     equ 0x889
MULTI_ROW    equ 0x88A
WP_BACK      equ 0x851              ; (a kit page's VIEW PSIONICS)
SPHERE_TOGGLE equ 0x7FF             ; (the spheres' VIEW PSIONICS)
WP_DISC      equ 0x1134             ; DS: the panel's windows (far; SL's EA2h, EA6h)
WP_SPHERE    equ 0x1138
WP_DISC_MASK equ 0x42C0             ; DS: the disciplines and spheres marked (SL's 4980h, 4982h)
WP_SPHERE_MASK equ 0x42C2
WP_CREATION  equ 0x1429             ; DS: the sheet being made (far; SL's 119Ch)
CR_EDITING   equ 0x112E             ; DS: -1 for a new member, else the party member edited (SL's 0E9Ch)
WP_STUB      equ 0x46CC - 0x47E0    ; the creation overlay's stub, less DS (SL's 421Dh)
WP_MARKED    equ 0x66               ; (6BC81h: the rows marked, as a mask)
WP_TO_DISC   equ 0x7A               ; (6BF3Fh: back to the disciplines)
WP_X         equ 0xD2
WP_Y         equ 0x58
WP_MARK_WIN  equ 0x11C4             ; DS: the window the marks are drawn through (far; SL's F32h)
WP_MARK_TABLE equ 0x17E             ; (the marks' table in its segment: SL's 1ABh)
WP_TITLE_FMT equ 0x109F             ; DS: "%C%C%C%s" (SL's E11h)
WP_INK       equ 0x2D16             ; DS: the panel's text colour (SL's 3270h)
CR_CLERIC    equ 1                  ; (classes at creation)
CR_DRUID     equ 2
CR_RANGER    equ 7
; The creation overlay's calls (9Ah) the click sites read the far addresses from, as the overlay
; manager has fixed them (file offsets): close 6BEAEh, open 6BEC5h, print 6BEF6h, text colour 6BF04h,
; the help line 6BF35h, set a button 6BFB6h, a row's mark 6BD4Bh; the segments "mov ax,360h" (the
; marks' table, 6BD39h) and "push 5B8h" (the spheres' routine's stub, 6BEB6h); the click sites'
; returns (the site + 3) and the routines' ends, where they go on
WP_CALL_CLOSE  equ 0x6BEAE
WP_CALL_OPEN   equ 0x6BEC5
WP_CALL_PRINT  equ 0x6BEF6
WP_CALL_COLOUR equ 0x6BF04
WP_CALL_HELP   equ 0x6BF35
WP_CALL_BUTTON equ 0x6BFB6
WP_CALL_MARK   equ 0x6BD4B
WP_MARK_SEG    equ 0x6BD39
WP_CALL_CR_HP  equ 0x6BBDF          ; (KIT_REROLL's: the creation rolls' hit points, 5C0h:66h, and PSP, 5C0h:6Bh;
WP_CALL_CR_PSP equ 0x6B749          ;  the backdrop put back under a number, 0C8h:3B30h; the backdrop's words'
WP_CALL_BACKDROP equ 0x6BC38        ;  segment, "mov ax,368h")
WP_STAT_SEG    equ 0x6BC24
WP_SPHERE_SEG  equ 0x6BEB6
WP_SPHERE_ENTRY equ 0x57
WP_SPHERE_RET  equ 0x6C039
WP_SPHERE_END  equ 0x6C068
WP_DISC_RET    equ 0x6C099
WP_DISC_END    equ 0x6C0C4
WP_SHOWN_CALL  equ 0x6B102          ; (140:C2Bh's call, and KP_SHOWN's return)
WP_SHOWN_RET   equ 0x6B10D
HEALER_SPHERE_MASK equ 0x10         ; (the spheres' marks: 80h air to 10h water)

; KP_IF_FRAME: interrupts as the INT's caller had them (DSCLOG's IF_FRAME: RETF 2 keeps the flags it sets)
kp_if_frame:
        pushf
        push bp
        mov bp, sp              ; [BP+2] the flags now, +4 the way back, +6 the INT's IP, +8 CS, +10 flags
        and byte [bp + 3], ~2
        test byte [bp + 11], 2
        jz .off
        or byte [bp + 3], 2
.off:   pop bp
        popf
        ret

; KP_OPEN (site 69): "mov byte [1C96h],0FFh" (6D891h) where the creation screen opens: its first
; disciplines' window (KP_DISC_WIN) is the screen's (KP_FIRST), the classes not seen yet.
kp_open:
        mov byte [0x1C96], 0xFF
        mov byte [cs:kp_first], 1
        mov byte [cs:kit_keep], 0
        mov dword [cs:wp_classes_seen], 0xFFFFFFFF
        mov byte [cs:cr_thac0_scholar], 0
        call psi_snap           ; (an EDIT's powers, for PSI_KEEP)
        iret

; KP_DISC_WIN (site 62) and KP_SPHERE_WIN (site 63): the window's id pushed under the INT's frame: the
; game's or the kits' (WP_IDS). The disciplines' opened but on the way back to them (KIT_KEEP): a new
; character's kit none, an EDIT's kept (its sheet the member's copy) when the screen opens; else none (a
; class picked: the game opens them again).
kp_disc_win:
        sub sp, 2               ; push the window's id: the frame down a word
        push bp
        mov bp, sp
        push ax
        mov ax, [bp + 4]
        mov [bp + 2], ax
        mov ax, [bp + 6]
        mov [bp + 4], ax
        mov ax, [bp + 8]
        mov [bp + 6], ax
        push dx
        call wp_ids
        mov [bp + 8], ax
        pop dx
        cmp byte [cs:kit_keep], 0
        jne .keep
        push es
        push bx
        push eax
        les bx, [WP_CREATION]
        call sheet_classes_cr
        mov [cs:wp_classes_seen], eax
        cmp byte [cs:kp_first], 0
        je .clear
        cmp word [CR_EDITING], -1
        jne .kept               ; (EDIT: the member's own)
.clear: mov byte [es:bx + KIT_BYTE], 0
.kept:  pop eax
        pop bx
        pop es
.keep:  mov byte [cs:kit_keep], 0
        mov byte [cs:kp_first], 0
        pop ax
        pop bp
        iret
kp_sphere_win:
        sub sp, 2
        push bp
        mov bp, sp
        push ax
        mov ax, [bp + 4]
        mov [bp + 2], ax
        mov ax, [bp + 6]
        mov [bp + 4], ax
        mov ax, [bp + 8]
        mov [bp + 6], ax
        push dx
        call wp_ids
        mov [bp + 8], dx
        pop dx
        pop ax
        pop bp
        iret

; SHEET_CLASSES_CR: EAX the classes of the sheet at ES:BX (its three class bytes).
sheet_classes_cr:
        mov eax, [es:bx + SH_CLASSES]
        and eax, 0x00FFFFFF
        ret

; WP_IDS: the windows the panel shows for the sheet being made (kitpages.panel_windows): AX the
; disciplines' (KP_DISC_ID; KIT_DISC_ID, KITS, for one of no sphere with kits to choose), DX the
; spheres' (KP_SPHERE_ID; KIT_SPHERE_ID for one with kits to choose). Others kept.
wp_ids:
        push bx
        push cx
        push es
        les bx, [WP_CREATION]
        xor ch, ch              ; CH a sphere: a cleric, druid or ranger class
        mov cl, 3
.class: mov al, [es:bx + SH_CLASSES]
        cmp al, CR_CLERIC
        je .sphere
        cmp al, CR_DRUID
        je .sphere
        cmp al, CR_RANGER
        jne .next
.sphere:
        mov ch, 1
.next:  inc bx
        dec cl
        jnz .class
        call kit_class
        mov bl, al
        mov ax, KP_DISC_ID
        mov dx, KP_SPHERE_ID
        or bl, bl
        jz .out
        mov dx, KIT_SPHERE_ID
        or ch, ch
        jnz .out
        mov ax, KIT_DISC_ID
.out:   pop es
        pop cx
        pop bx
        ret

; KIT_CLASS: AL the class of the sheet being made (1-8, as the creation screen numbers them) if it has
; kits to choose (the rule on, and one class), or its multiclass group (9-19: MULTI_GROUP_CR) for two or
; three classes at once, else 0. Others kept.
kit_class:
        push bx
        push es
        xor al, al
        test word [cs:rules_hi], RULE_HI_KITS
        jz .out
        les bx, [WP_CREATION]
        cmp word [es:bx + SH_CLASSES + 1], 0
        jne .multi
        mov al, [es:bx + SH_CLASSES]
        cmp al, 8
        jbe .out
        xor al, al
        jmp .out
.multi: call multi_group_cr
.out:   pop es
        pop bx
        ret

; KP_SHOWN (site 66): "cmp ax,8" (6B10Ah) after the game asked (140:C2Bh, the window's id pushed) whether
; the spheres' window is up, a new class picked, to close it: 8 too if the kits' spheres or a kit page
; is (WP_MINE). RETF 2 keeps the compare's flags.
kp_shown:
        call kp_if_frame
        cmp ax, 8
        je .ret
        push bp
        mov bp, sp
        push bx
        push cx
        push dx
        push es
        mov es, [bp + 4]        ; 140:C2Bh's far address, from the call just made
        mov bx, [bp + 2]
        add bx, (WP_SHOWN_CALL + 1 - WP_SHOWN_RET) & 0xFFFF
        mov ax, [es:bx]
        mov [cs:wp_far], ax
        mov ax, [es:bx + 2]
        mov [cs:wp_far + 2], ax
        mov bx, wp_mine
.one:   push word 0
        push word [cs:bx]
        call far [cs:wp_far]
        add sp, 4
        cmp ax, 8
        je .out
        add bx, 2
        cmp bx, wp_mine_end
        jb .one
.out:   pop es
        pop dx
        pop cx
        pop bx
        pop bp
.ret:   cmp ax, 8
        retf 2

; KP_CLASS (site 67): "mov cl,1 / les bx,[1429h]" (6E026h) at the start of the routine run after each
; click on the creation screen (it puts DONE in or out of use): other classes than last seen (but the
; first look after the screen opens), no kit; the disciplines' window up opened again if it isn't the
; one for the classes now (KITS or VIEW SPHERES); a kit page up marked again for the class now, the
; class's own opened for another, or back to the disciplines for one with no kits. Then the two
; instructions.
kp_class:
        sti
        pushad
        push es
        call cr_changed
        jz .drawn
        mov bx, sp              ; the frame at BX+34: IP, CS, flags
        push word [ss:bx + 36]  ; the way back, pushed as a far call's, with BP
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        call cr_draw            ; (another class: its picture, CR_DRAW)
        pop bp
        pop ax                  ; (the way back, as the overlay manager has left it)
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
.drawn: les bx, [CR_CREATURE]   ; (and the small figure, its outfit's: CR_SMALL_DRAW)
        call small_key
        cmp ax, [cs:small_seen]
        je .small
        mov [cs:small_seen], ax
        mov bx, sp
        push word [ss:bx + 36]
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        call cr_small_draw
        pop bp
        pop ax
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
.small: pop es
        popad
        push eax
        push es
        push bx
        les bx, [WP_CREATION]
        call sheet_classes_cr
        cmp eax, [cs:wp_classes_seen]
        je .same
        cmp dword [cs:wp_classes_seen], 0xFFFFFFFF
        mov [cs:wp_classes_seen], eax
        je .same                ; (the first look: as they are)
        mov byte [es:bx + KIT_BYTE], 0
.same:  pop bx
        pop es
        pop eax
        push ax
        push bx
        push es
        mov ax, [WP_DISC]       ; the disciplines up: the right window for the classes now?
        or ax, [WP_DISC + 2]
        jz .page
        push dx
        call wp_ids
        pop dx
        mov [cs:wp_button], ax
        les bx, [WP_DISC]
        mov ax, [es:bx + 8]
        cmp ax, [cs:wp_button]
        je .out
        sti
        pushad
        push es
        call wp_reopen_disc
        jmp .done
.page:  mov ax, [WP_SPHERE]     ; a kit page up: the window's id (+8)
        or ax, [WP_SPHERE + 2]
        jz .out
        les bx, [WP_SPHERE]
        mov ax, [es:bx + 8]
        sub ax, KIT_WIN_ID
        cmp ax, KIT_GROUPS
        jae .out
        sti
        pushad
        push es
        mov cl, al
        inc cl
        call kit_class
        or al, al
        jz .back
        cmp al, cl
        je .marks
        mov byte [cs:wp_from], 2
        call kit_open
        jmp .done
.back:  mov ax, WP_BACK
        call wp_page_button
        jmp .done
.marks: call kit_marks
.done:  pop es
        popad
.out:   pop es
        pop bx
        pop ax
        mov cl, 1
        les bx, [WP_CREATION]
        iret

; KP_RACE (site 68): "add sp,6" (6B191h) in the creation screen's routine for a new race or sex, after its
; call that gives the character its default class: the disciplines' window opened again if it isn't the
; one for the class now (KITS), as after a click on a class.
kp_race:
        pop word [cs:rp_ip]
        pop word [cs:rp_cs]
        pop word [cs:rp_fl]
        add sp, 6
        push word [cs:rp_fl]
        push word [cs:rp_cs]
        push word [cs:rp_ip]
        sti
        pushad
        push es
        mov ax, [WP_DISC]
        or ax, [WP_DISC + 2]
        jz .done
        call wp_ids
        les bx, [WP_DISC]
        cmp ax, [es:bx + 8]
        je .done
        call wp_reopen_disc
.done:  pop es
        popad
        iret
rp_ip   dw 0
rp_cs   dw 0
rp_fl   dw 0

; WP_REOPEN_DISC: the disciplines' window opened again by the game (6BF3Fh, through the stub), its marks
; kept as 6BE6Bh keeps them, and the kit (KIT_KEEP). DS the game's.
wp_reopen_disc:
        push word 0x7F8
        push word 0x7F6
        push dword [WP_DISC]
        call wp_marked
        add sp, 8
        mov [WP_DISC_MASK], ax
        mov byte [cs:kit_keep], 1
        mov ax, ds
        add ax, WP_STUB
        mov [cs:wp_far + 2], ax
        mov word [cs:wp_far], WP_TO_DISC
        call far [cs:wp_far]
        ret

; KP_DISC_CLICK (site 64), KP_SPHERE_CLICK (site 65): "mov bx,[bp+8]" (6C096h, 6C036h) in the disciplines'
; and spheres' click routines, [BP+8] the button: KITS opens the kit page; a kit page's buttons (shown with
; the spheres' routine: WP_SHOW) are its rows and VIEW PSIONICS; those go on at the routine's end (the
; redraw). Else BX [BP+8], the game's.
kp_disc_click:
        push bp
        mov bp, sp
        push ax
        mov word [cs:wp_ret_file], WP_DISC_RET & 0xFFFF
        mov word [cs:wp_end_file], WP_DISC_END & 0xFFFF
        mov byte [cs:wp_from], 0
        jmp wp_click
kp_sphere_click:
        push bp
        mov bp, sp
        push ax
        mov word [cs:wp_ret_file], WP_SPHERE_RET & 0xFFFF
        mov word [cs:wp_end_file], WP_SPHERE_END & 0xFFFF
        mov byte [cs:wp_from], 1
; (BP: the frame, [BP] the game's BP, [BP+2] the return; AX pushed)
wp_click:
        push bx
        mov bx, [bp]
        mov bx, [ss:bx + 8]     ; the button
        mov [cs:wp_button], bx
        cmp bx, SPHERE_TOGGLE   ; (VIEW PSIONICS: back to the disciplines, the kit kept)
        jne .which
        mov byte [cs:kit_keep], 1
.which: pop bx
        call wp_harvest
        mov ax, [cs:wp_button]
        cmp ax, KIT_VIEW
        je .kits
        cmp byte [cs:wp_from], 1    ; (a kit page's button, in the spheres' routine)
        jne .game
        cmp ax, WP_BACK
        jb .game
        cmp ax, MULTI_ROW + 3 * (KIT_GROUPS - MULTI_FIRST + 1)
        jae .game
        sti
        pushad
        push es
        call wp_page_button
        pop es
        popad
        jmp .end
.kits:  sti                     ; KITS: from the disciplines or the spheres
        pushad
        push es
        call kit_class          ; (no kit for the character now: back from the spheres, as VIEW
        or al, al               ;   PSIONICS goes)
        jnz .kit_class
        cmp byte [cs:wp_from], 0
        je .none
        mov ax, WP_BACK
        call wp_page_button
.none:  pop es
        popad
        jmp .end
.kit_class:
        call kit_open
        inc word [cs:kit_pages_shown]
        pop es
        popad
.end:   mov ax, [cs:wp_end_file]  ; go on at the routine's end
        sub ax, [cs:wp_ret_file]
        add [bp + 2], ax
.game:  pop ax
        pop bp
        mov bx, [cs:wp_button]
        iret

; WP_HARVEST: the window routines' far addresses from the overlay's calls (WP_CALLS), the probe's
; frame at BP.
        SHARED_wp_harvest

; WP_HELP_LINE: the panel's help line, as the game puts it under the spheres
wp_help_line:
        push dword 0x14A9D
        call far [cs:wp_help]
        add sp, 4
        ret

; KIT_OPEN: the kit page of the class being made in the panel, after closing what it shows (WP_FROM:
; 0 the disciplines, 1 the spheres, 2 a kit page), as 6BE6Bh opens the spheres. DS the game's.
        SHARED_kit_open

; WP_CLOSE_PANEL: what the panel shows (WP_FROM) closed, the disciplines' or spheres' marks kept as the
; game keeps them
        SHARED_wp_close_panel

; WP_SHOW: window AX in the panel, kept at WP_SPHERE, the spheres' own routine (5B8h:57h) answering its
; buttons (KP_SPHERE_CLICK), and its title CS:SI, as the spheres' (WP_TITLE_FMT)
wp_show:
        push word [cs:wp_sphere_seg]
        push word WP_SPHERE_ENTRY
        push word WP_Y
        push word WP_X
        push ax
        call far [cs:wp_open_fn]
        add sp, 10
        mov [WP_SPHERE], ax
        mov [WP_SPHERE + 2], dx
        push cs
        push si
        push dword 0xD90014
        push dword 0xFE00FE
        push dword 0xFF0000
        push ds
        push word WP_TITLE_FMT
        push dword 0x6000E
        push dx
        push ax
        call far [cs:wp_print]
        add sp, 0x1C
        push dword 0xF000FE
        call far [cs:wp_colour]
        add sp, 4
        push word [WP_INK]
        push word 0x14
        call far [cs:wp_colour]
        add sp, 4
        ret

; WP_MARKED: the game's 6BC81h through its stub (the window, the first and last row on the stack as for
; it): AX the rows marked.
wp_marked:
        push bp
        mov bp, sp
        push word [bp + 10]
        push word [bp + 8]
        push dword [bp + 4]
        mov ax, ds
        add ax, WP_STUB
        mov [cs:wp_far + 2], ax
        mov word [cs:wp_far], WP_MARKED
        call far [cs:wp_far]
        add sp, 8
        pop bp
        ret

; WP_BUTTON_OP: the game's 168:71Fh on button AX of the page (WP_SPHERE), with the operation pushed (0 in
; use, 1 out of use, 2 marked, 3 not marked); takes it off the stack. AX, BX, CX kept.
        SHARED_wp_button_op

; WP_MARK: the mark (pushed: 1) or none (0) at the page's row 4 - CX, as 6BD75h draws it; takes the
; flag off the stack. AX, BX, CX kept.
wp_mark:
        push bp
        mov bp, sp
        pusha
        push es
        push word [bp + 4]
        push dword [WP_MARK_WIN]
        push word 0
        mov bx, 4
        sub bx, cx
        shl bx, 1
        mov es, [cs:wp_mark_seg]
        mov ax, [es:bx + WP_MARK_TABLE]
        inc ax
        push ax
        push dword 0xDA0001
        call far [cs:wp_mark_fn]
        add sp, 0x0E
        pop es
        popa
        pop bp
        ret 2

; WP_PAGE_BUTTON: button AX of a kit page, clicked: a kit's row (KIT_ROW), VIEW PSIONICS back to the
; disciplines (6BF3Fh). DS the game's.
wp_page_button:
        cmp ax, KIT_ROW
        jae kit_row
        cmp ax, WP_BACK
        jne .ret
        push dword [WP_SPHERE]
        call far [cs:wp_close]
        add sp, 4
        mov dword [WP_SPHERE], 0
        mov byte [cs:kit_keep], 1
        mov ax, ds
        add ax, WP_STUB
        mov [cs:wp_far + 2], ax
        mov word [cs:wp_far], WP_TO_DISC
        call far [cs:wp_far]
.ret:   ret

; KIT_ROW: kit row AX of the kit page clicked (KIT_NONE: NO KIT), as the game's spheres: with none chosen
; (KIT_OPEN), the row's kit chosen; the one chosen, taken back (the rows all in use, the sheet KIT_OPEN);
; another, nothing. A Healer only with the water sphere marked (kits.HEALER_SPHERE). A Battle Mage, an
; Arcanist or a Mind Warrior chosen or taken back: its hit points and PSP rolled again (KIT_REROLL). DS the
; game's.
kit_row:
        les bx, [WP_CREATION]
        xor dl, dl
        cmp ax, KIT_NONE
        je .row
        mov cx, KIT_ROW
        cmp ax, MULTI_ROW
        jb .sub
        mov cx, MULTI_ROW       ; (a multiclass group's rows)
.sub:   sub ax, cx
        mov cl, 3
        div cl
        mov dl, ah
        inc dl
.row:   push eax                ; (the classes the kit goes with, as KP_CLASS keeps them)
        call sheet_classes_cr
        mov [cs:wp_classes_seen], eax
        pop eax
        mov dh, [es:bx + KIT_BYTE]
        cmp dh, KIT_OPEN        ; none chosen: this one (a Healer only with the water sphere)
        jne .chosen
        push ax
        call kit_class
        call healer_barred
        pop ax
        jc kit_marks
        jmp .put
.chosen:
        cmp dl, dh              ; another, while one is chosen: out of use (nothing)
        jne kit_marks
        mov dl, KIT_OPEN        ; the one chosen: taken back, the rest in use again
.put:   call kit_rolls_due      ; (a Battle Mage, an Arcanist or a Mind Warrior before or after: KIT_REROLL)
        mov [es:bx + KIT_BYTE], dl
        inc word [cs:kit_rows_taken]
        call kit_rolls_due
        call kit_marks
        cmp byte [cs:kit_reroll_due], 0
        je .ret
        call kit_reroll
.ret:   ret
; KIT_MARKS: the kit page's rows (NO KIT, then the class's three kits, or a multiclass group's one or
; two) marked as the creation sheet's kit, the rest not, as 6BD75h marks the spheres
kit_marks:
        push es
        push bx
        call kit_class
        or al, al
        jz .out
        les bx, [WP_CREATION]
        mov dl, [es:bx + KIT_BYTE]
        mov [cs:km_class], al
        movzx bx, al
        mov byte [cs:km_rows], 4
        cmp al, MULTI_FIRST
        jb .class
        mov cl, [cs:bx + multi_count - MULTI_FIRST]
        inc cl
        mov [cs:km_rows], cl
        imul bx, bx, 3
        add bx, MULTI_ROW - 3 * MULTI_FIRST - 1   ; (NO KIT first, then the group's)
        jmp .first
.class: imul bx, bx, 3
        add bx, KIT_ROW - 4     ; (NO KIT first, then the class's three)
.first: xor dh, dh              ; (the row's kit)
        mov cx, 4               ; (WP_MARK's row: 4 - CX)
.row:   mov ax, bx
        or dh, dh
        jnz .kit
        mov ax, KIT_NONE
.kit:   cmp dh, dl
        je .chosen
        push 3                  ; not chosen: greyed while another is, as the game's spheres
        call wp_button_op
        cmp dl, KIT_OPEN
        jne .grey
        push ax                 ; (a Healer's row greyed without the water sphere)
        mov al, [cs:km_class]
        xchg dl, dh
        call healer_barred
        xchg dl, dh
        pop ax
        jnc .open
.grey:  push 1
        jmp .op
.open:  push 0
.op:    call wp_button_op
        push 0
        jmp .next
.chosen:
        push 0
        call wp_button_op
        push 2
        call wp_button_op
        push 1
.next:  call wp_mark
        inc bx
        inc dh
        cmp dh, [cs:km_rows]    ; (a multiclass group's page: its one or two kits' rows)
        jae .out
        loop .row
.out:   pop bx
        pop es
        ret

; HEALER_BARRED: CF set if row DL (1-3) of creation class AL's kit page (KIT_CLASS's number) is the
; Healer's and the sphere marked (WP_SPHERE_MASK) isn't water's. Registers kept.
        SHARED_healer_barred

kit_title  db 'KITS', 0
kit_keep   db 0                 ; 1 while the panel goes back to the disciplines (the kit kept)
kp_first   db 0                 ; 1 from the screen's opening (KP_OPEN) to its first disciplines' window
wp_from    db 0
km_rows    db 4                 ; (KIT_MARKS: the page's rows)
km_class   db 0                 ; (KIT_MARKS: its class, KIT_CLASS's)
wp_classes_seen dd 0xFFFFFFFF   ; the classes being made, as KP_CLASS last saw them
wp_button  dw 0
wp_ret_file dw 0
wp_end_file dw 0
wp_far     dd 0
kit_pages_shown dw 0            ; (for a look in play: kit pages opened, rows taken)
kit_rows_taken dw 0
wp_mine    dw KIT_SPHERE_ID     ; (the kits' windows in the spheres' place: KP_SHOWN)
%assign kp_n 0
%rep KIT_GROUPS
           dw KIT_WIN_ID + kp_n
%assign kp_n kp_n + 1
%endrep
wp_mine_end:
wp_calls:                       ; each: the call's file offset (low word), then its far address
           dw WP_CALL_CLOSE & 0xFFFF
wp_close   dd 0
           dw WP_CALL_OPEN & 0xFFFF
wp_open_fn dd 0
           dw WP_CALL_PRINT & 0xFFFF
wp_print   dd 0
           dw WP_CALL_COLOUR & 0xFFFF
wp_colour  dd 0
           dw WP_CALL_HELP & 0xFFFF
wp_help    dd 0
           dw WP_CALL_BUTTON & 0xFFFF
wp_button_fn dd 0
           dw WP_CALL_MARK & 0xFFFF
wp_mark_fn dd 0
           dw WP_CALL_CR_HP & 0xFFFF
cr_hp_fn   dd 0
           dw WP_CALL_CR_PSP & 0xFFFF
cr_psp_fn  dd 0
           dw WP_CALL_BACKDROP & 0xFFFF
wp_backdrop dd 0
wp_calls_end:
wp_mark_seg dw 0
wp_stat_seg dw 0
wp_sphere_seg dw 0

; DUAL_KIT (site 76): "cmp word [bp+8],0Ch" (94A57h; 4 bytes: the site and a NOP; SL's PROBE_DUAL_KIT at
; 86D90h) in the routine that changes a human's class (9493Ch: SI the member, [BP+8] the new class, already
; first among its classes). With kits, the game's three-choice menu (the one a new cleric's sphere is asked
; on: its far call at 94878h, read from the code as the overlay manager has fixed it) asks for the new
; class's kit, "KIT: NONE" its title, the class's kits its rows, a kit barred left off (DK_BANNED: an empty
; row, which the menu leaves out); the one clicked goes in the kit byte's two bits for the new class
; (KIT_AT). A character keeps to one kit: one with a kit already (the byte's places, its low six bits, not 0;
; not KIT_OPEN) is asked none. The menu is overlay code of its own: the way back is put in a frame the
; overlay manager can fix up, as DSCLOG's. Then the compare, its flags back to the JNZ (RETF 2). Not here
; (DSCLOG's): an Elementalist's second sphere (DK_SECOND), a new warrior's weapon kinds (LV_CHECK), the DUAL
; window greying the classes a kit bars (DUAL_BANS' other use).
DK_MENU_CALL  equ 0x94879 - 0x94A5A     ; (the menu's far call's operand, less the address after the site)
DK_X       equ 0x5C
DK_Y       equ 0x47
KIT_PLACES_BITS equ 0x3F                ; (the kit byte's two bits for each of three places)
KIT_ELEMENTALIST equ 5
KIT_LIFEBINDER equ 10
KIT_SHINOBI  equ 35
HEALER_SPHERE_CLASS equ 4               ; (the water cleric)
dual_kit:
        call kp_if_frame        ; (interrupts as the caller had them: RETF 2 keeps these flags)
        pushad
        push es
        mov bx, sp              ; the interrupt frame at BX+34: IP, CS, flags
        push ds
        lds si, [ss:bx + 34]    ; (the menu's far address, in its call, as fixed up)
        mov eax, [si + DK_MENU_CALL]
        pop ds
        mov [cs:dk_far], eax
        push word [ss:bx + 36]
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        mov di, [bp]            ; (the routine's frame: [DI+8] the new class)
        mov ax, [ss:di + 8]
        mov si, [ss:di + 6]     ; (and [DI+6] the member)
        call dk_ask
        pop bp
        pop ax                  ; the way back, as the overlay manager has left it
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
        pop es
        popad
        cmp word [bp + 8], 0x0C
        retf 2

; DK_ASK: member SI (DS the game's), its new class AL first on its sheet: DUAL_KIT's menu. Registers changed.
dk_ask:
        cmp si, 4
        jae .ret
        les bx, [SHEETS_PTR]
        imul cx, si, SHEET_SIZE
        add bx, cx
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        cmp byte [es:bx + SH_RACE], CU_HUMAN
        jne .ret
        call kit_open_at
        je .none
        test byte [es:bx + KIT_BYTE], KIT_PLACES_BITS
        jnz .ret                ; (a kit already: one a character)
.none:  movzx di, al
        dec di
        cmp di, 16
        ja .ret
        mov ch, [cs:di + kit_class_of]
        shl ch, 2               ; (CH the kit numbers' base: the creation class x 4)
        mov di, dk_opts + 8     ; the rows, the last first
        mov cl, 3
.opt:   mov al, ch
        add al, cl
        mov dx, dk_blank
        call dk_banned
        mov [cs:di + 2], cs     ; (a blank row: the helper's; a kit's name: the tail's)
        jc .row
        push si
        call kit_name_ptr
        mov dx, si
        pop si
        push fs
        call tail_fs
        mov [cs:di + 2], fs
        pop fs
.row:   mov [cs:di], dx
        sub di, 4
        dec cl
        jnz .opt
        inc word [cs:dual_asks]
        mov dx, dk_title
        call dk_menu            ; (AX the row: 1-3 a kit)
        dec ax
        cmp ax, 2
        ja .ret
        mov dl, al
        add al, ch
        inc al
        call dk_banned
        jc .ret
        push di
        call kit_place          ; (DI the oldest class's place: the new one's bits above it)
        mov cx, di
        pop di
        jc .ret
        shl cl, 1
        inc dl
        movzx dx, dl
        shl dx, cl
        call kit_open_at
        mov cl, [es:bx + KIT_BYTE]
        jne .set
        xor cl, cl
.set:   or cl, dl
        mov [es:bx + KIT_BYTE], cl
        inc word [cs:dual_kits]
.ret:   ret

; DK_MENU: AX the row picked on the game's three-choice menu (DK_FAR), its title CS:DX, its rows DK_OPTS
; (far). ES:BX kept; others but CX, SI changed.
dk_menu:
        push bx
        push cx
        push si
        push es
        mov si, dk_opts + 8
.push:  push word [cs:si + 2]
        push word [cs:si]
        sub si, 4
        cmp si, dk_opts
        jae .push
        push 1                  ; (as the sphere's)
        push cs
        push dx
        push DK_Y
        push DK_X
        call far [cs:dk_far]
        add sp, 22
        pop es
        pop si
        pop cx
        pop bx
        ret

; DK_BANNED: CF set if kit AL may not go with the other classes of sheet ES:BX (its places from 1) or their
; kits (asleep too), or is a Healer for a cleric not of water (its new class, place 0): its DUAL_BANS hold one
; of the classes (KIT_BANS), or a kit's and its are a pair KIT_PAIRS bars (kits.dual_kit_banned). All
; registers kept.
dk_banned:
        pushad
        cmp al, KIT_HEALER      ; (the Healer: a water cleric's only)
        jne .bans
        cmp byte [es:bx + SH_CLASSES], HEALER_SPHERE_CLASS
        jne .no
.bans:  mov cl, al
        call kit_bans           ; (EDX the classes it bars)
        call kit_place
        jc .ok
.place: or di, di
        jz .ok
        movzx eax, byte [es:bx + di + SH_CLASSES]
        bt edx, eax
        jc .no
        call kit_at
        jz .next
        mov ah, cl
        call kit_pair
        jc .no
.next:  dec di
        jmp .place
.ok:    popad
        clc
        ret
.no:    popad
        stc
        ret

; KIT_PAIR: CF set if kits AL and AH may not go together (KIT_PAIRS, either way round). Others kept.
        SHARED_kit_pair
; Kits barred from going together (kits.KIT_PAIRS, DSCLOG's): 0 ends it.
kit_pairs  db KIT_CHAMPION, KIT_TWIN_BLADE,  KIT_CHAMPION, KIT_SHINOBI,  KIT_CHAMPION, KIT_RAVAGER
           db KIT_SENTINEL, KIT_TWIN_BLADE,  KIT_SENTINEL, KIT_SHINOBI,  KIT_SENTINEL, KIT_RAVAGER
           db KIT_TWIN_BLADE, KIT_HEALER,  KIT_BRUTE, KIT_SHINOBI,  KIT_BRUTE, KIT_LIFEBINDER
           db KIT_RAVAGER, KIT_GROVE_WARDEN
           db KIT_SWASHBUCKLER, KIT_CRUSADER,  KIT_SWASHBUCKLER, KIT_BATTLE_MAGE
           db KIT_SWASHBUCKLER, KIT_MIND_WARRIOR,  KIT_CRUSADER, KIT_BATTLE_MAGE
           db KIT_CRUSADER, KIT_MIND_WARRIOR,  KIT_BATTLE_MAGE, KIT_MIND_WARRIOR
           dw 0

; KIT_BANS: EDX the classes (bit n: class n, 1-17) kit AL bars a human from having as well (DUAL_BANS; 0 for
; none, or no kit). Others kept.
        SHARED_kit_bans
; By kit, the classes (bit n: class n, 1-17) a human with it may not change to (kits.DUAL_BANS, DSCLOG's)
DB_PRIEST   equ 0x1FE                   ; (clerics and druids, 1-8)
DB_WARRIOR  equ 0x1E600                 ; (fighter 9, gladiator 10, rangers 13-16)
DB_NO_SHIELD equ 0x1E0 | (1 << 11)      ; (druids 5-8, the preserver)
DB_NOT_WATER equ 0xE0EE                 ; (clerics 1-3, druids 5-7, rangers 13-15)
dual_bans   db KIT_SEEKER
            dd DB_PRIEST
            db KIT_JUSTIFIER
            dd DB_PRIEST
            db KIT_SHINOBI
            dd 1 << 11
            db KIT_SWASHBUCKLER
            dd DB_WARRIOR
            db KIT_CRUSADER
            dd DB_WARRIOR
            db KIT_BATTLE_MAGE
            dd DB_WARRIOR
            db KIT_MIND_WARRIOR
            dd DB_WARRIOR
            db KIT_CHAMPION
            dd DB_NO_SHIELD
            db KIT_SENTINEL
            dd DB_NO_SHIELD
            db KIT_BRUTE
            dd 1 << 12 | 1 << 1
            db KIT_STALKER
            dd 1 << 17
            db KIT_GROVE_WARDEN
            dd 1 << 10
            db KIT_HEALER
            dd DB_NOT_WATER
            db 0
dk_opts    times 3 dd 0
dk_far     dd 0
dk_title   db 'KIT: NONE', 0
dk_blank   db 0
dual_asks  dw 0                 ; (for a look in play: DUAL's kit menus shown, kits taken)
dual_kits  dw 0

; ---- a spell cast: DSCLOG's CAST_SITE, recording only ----
; INT VEC_CAST replaces "mov cx,[bp+6]" (80585h, 3 bytes: INT + NOP) at the start of the routine
; casting a spell or a power (80580h, SL's 772A5h): [BP+6] the caster, [BP+8] the target, [BP+0Ah] the
; spell. Recorded (kind KIND_CAST, the spell the entry's value: the Loader floats its name over the
; caster), then the move done.
KIND_CAST equ 8
probe_cast:
        push si
        mov si, sp
        sub si, 4               ; SS:SI+6 = our return address (as RECORD wants it)
        push ax
        mov word [cs:extra], 0
        mov ax, [bp + 0x0A]
        mov word [cs:kind], KIND_CAST
        call record
        call th_cast                    ; (TH_SITE's: armed for an attack roll)
        pop ax
        pop si
        mov cx, [bp + 6]
        iret

; ---- LABELS: DSCLOG's names floating over figures, on the sequel's map ----
; The Loader (labels.py) writes each label, two one-bit masks, into LBL_SLOTS (the header's +1834:+1838:
; here, in this resident part); this puts them over their figures' feet. The map is drawn straight
; into the screen on show, a rectangle at a time, so a label is put again after the game draws: from
; the timer, every other strike (LABEL_STAMP from PROBE_TICK), and from the main loop, which also
; places them (LABEL_TICK) and has where one was drawn again by the game's routine when it goes or
; moves (LABEL_ERASE). DSCLOG draws the whole view again when it scrolls; here the two places a label
; can be then (where it was, and where the game's copy of the screen moved it) are drawn again.
; (LBL_SLOTS, LBL_ROW, LBL_H_MOST, LBL_MASK, LBL_SIZE: at the tail's start, where LBL_SLOTS is)
LBL_TOP    equ 40               ; (screen rows above: the game's boxes, in a fight)
CAM_X      equ 0x1408           ; DS: the view's top left on the map (SL's 1178h)
CAM_Y      equ 0x140A
OBJ_LIST   equ 0x67B7           ; DS: far pointer to the things on the map, 8 bytes each, +6 which (SL's 6690h)
OBJ_COUNT  equ 0x264E           ;   and how many (SL's 1F72h)
MAP_THINGS equ 0x67BB           ; DS: each thing on the map, 25h bytes (SL's 6694h, 32), its feet +0Ah, +0Ch
THING_SIZE equ 0x25
THING_X    equ 0x0A
THING_Y    equ 0x0C
MAP_COUNT  equ 0x141
SCREEN_IS  equ 0x0DAB           ; DS: 1 on the map (SL's 0BC9h)
REDRAW_SEG equ 0x21E0           ; the game's routine drawing a rectangle of the view again (21E0:128Ch,
REDRAW_OFF equ 0x128C           ;   SL's 1DF3:142Fh), as its own call at 2CB06h (SL's 28185h)
DGROUP     equ 0x47E0
LS_SEEN  equ 0
LS_SHOWN equ 1
LS_W     equ 2
LS_H     equ 3
LS_X     equ 4
LS_Y     equ 6
lbl_state times LBL_SLOTS * 8 db 0
lbl_busy  db 0
lbl_cx    dw 0
lbl_cy    dw 0
lp_line   dw 0
lp_ink    db 0
lp_edge   db 0
pointer_ds dw 0                 ; the game's DS (PROBE_SCROLL's)
redraw_far dw REDRAW_OFF, 0
tick_count dw 0
dac_at    dw 0
dac_reads dw 0                  ; (for the tests and a look in play)
label_ticks dw 0
s_ip      dw 0
s_cs      dw 0
s_fl      dw 0
s_far     dw 0, 0

; ---- THE VIEW IN FIGHTS, THE WHOLE PARTY IN VIEW, STEADY PACE (DSCLOG's CAMERA, SPREAD, STEADY PACE) ----
; Ported from DSCLOG (gamepatch's camera_still, party_spread and party_gather, pace_pass and pace_draw),
; first written for the sequel on Codex's branch codex/ravager-map-controls (2026-11-26).
FS_SEG_GAP   equ DGROUP - 0x3C10        ; (DS less the fight state's segment: its +19h, a fight on)
SPREAD_STUB  equ DGROUP - 0x46BD        ; (DS less the overlay stubs' segment of the 5 and 6 keys)
GATHER_CODE  equ DGROUP - 0x18C9        ; (DS less the segment of the routine stepping a fight's figure)

; CAMERA_WALK (site 230): "mov bx,[426Dh]" (200B7h; 4 bytes: the INT, the site's number and a NOP) in the
; routine stepping a fight's figure (1FD6Bh, SL's 0AC0:C7B3), SI and DI the figure's feet on the map,
; just before the view's own moves after it: its "would the view centred on it pass the map's edge"
; (1C5F:01B2), the view centred at once when the figure is outside the middle of the screen (64 to 256
; across, 64 to 136 down), else stepped toward it (262C:0D80). In a fight (the fight state's +19h) with
; the feet on the screen the view stays: on to the routine's end (2019Bh), past both. Off the screen,
; or out of a fight, as the game has it. The displaced read done; others kept.
camera_walk:
        push bp
        mov bp, sp
        push ax
        push es
        mov ax, ds
        sub ax, FS_SEG_GAP
        mov es, ax
        cmp word [es:0x19], 0
        je .game                        ; (out of a fight: the game's)
        mov ax, si
        sub ax, [CAM_X]
        dec ax
        cmp ax, 319
        jae .game                       ; (off the screen across)
        mov ax, di
        sub ax, [CAM_Y]
        dec ax
        cmp ax, 199
        jae .game                       ; (off it up or down)
        add word [bp + 2], 0x2019B - 0x200BA  ; (the INT's way back, 200BAh: to the routine's end)
.game:  pop es
        pop ax
        pop bp
        mov bx, [WHOSE_TURN]            ; (the displaced read)
        iret

; PARTY_LOAD (site 231): "mov byte [13FAh],0" (70DA6h; 5 bytes) where loading a game finds the party in
; the leader's figure (SL's SPREAD_LOAD); PARTY_GATHER (site 232): the same store (6A823h) in the routine
; putting the party in one figure (46BD:0025's), the game's 6 key's and a fight's end's (SL's
; SPREAD_GATHER). Each does the store; a load, and a gather whose caller (the routine's own way back,
; [BP+2], [BP+4]) is one of the two at a fight's end (18C9:21C6h after 20051h, 18C9:31A9h after 21034h),
; set SPREAD_DUE; the 6 key's (18C9:0ED6h) clears it, so the party stays in one figure until the next
; fight or load. SPREAD_TICK does the spreading. All registers kept.
party_load:
        mov byte [IN_COMBAT], 0         ; (the displaced store)
        mov byte [cs:spread_due], 1
        iret

party_gather:
        mov byte [IN_COMBAT], 0         ; (the displaced store)
        push ax
        mov ax, ds
        sub ax, GATHER_CODE
        cmp ax, [bp + 4]
        pop ax
        jne .out                        ; (another caller: a script's)
        cmp word [bp + 2], 0x21C6       ; (a fight's end)
        je party_load
        cmp word [bp + 2], 0x31A9       ; (... the other)
        je party_load
        cmp word [bp + 2], 0x0ED6       ; (the 6 key)
        jne .out
        mov byte [cs:spread_due], 0
.out:   iret

; SPREAD_TICK: (PROBE_SCROLL's, DS the game's) with SPREAD_DUE set, on the map, out of a fight, and
; the party still in one figure (IN_COMBAT 0): the game's 5 key's routine (46BD:002A, 6A6D1h, its
; argument 1: the view drawn again) called, which spreads the members round the leader. All kept.
spread_tick:
        cmp byte [cs:spread_due], 0
        je .ret
        call on_map
        jne .ret
        pushad
        push ds
        push es
        mov ax, ds
        sub ax, FS_SEG_GAP
        mov es, ax
        cmp word [es:0x19], 0
        jne .out                        ; (a fight: after it)
        mov byte [cs:spread_due], 0
        cmp byte [IN_COMBAT], 0
        jne .out                        ; (spread already)
        mov ax, ds
        sub ax, SPREAD_STUB
        mov [cs:spread_call + 2], ax
        push word 1
        call far [cs:spread_call]
        add sp, 2
.out:   pop es
        pop ds
        popad
.ret:   ret
spread_due  db 0
spread_call dw 0x2A, 0

; STEADY PACE (SL's PROBE_PACE_PASS, PROBE_PACE_DRAW; DEVELOPMENT-SCREENS.md's Game speed). The map's
; frame (21A61h, SL's 1E8E4h) calls the step for everything (21E0:2BB9, which builds the list of what
; moved at 42A2h:0028h, 10 bytes each, and sets the frame's byte [BP-1], "something moved") and then
; the drawing of that list with the flip (21E0:1478). The step runs only when the timer (2A1AAh) has set
; DS:265Ah, at each tick of the game's clock (DS:145Eh, 96 a second): a tick passed while drawing is a
; step lost. PACE_PASS counts the steps run; PACE_DRAW, at each frame, adds the steps lost since the last
; to a debt in quarter ticks less PACE_ALLOW, and while the debt is above 0, out of a fight, leaves the
; drawing out and keeps the list (PACE_SAVED, PACE_KEPT entries); the next frame drawn gets it added
; after its own. Each site replaces the far call's offset (its INT and number: 3 bytes), the call's
; segment, as DOS relocated it, left in place and read from there.
PACE_LIST  equ 0x28                     ; the game's list of what moved (at 42A2h:0) ...
PACE_LSEG  equ DGROUP - 0x42A2          ; (... DS less its segment)
PACE_LMAX  equ 320                      ; ... and the most it holds
PACE_CLOCK equ 0x145E                   ; the game's clock: 96 ticks a second
PACE_STEP  equ 0x265A                   ; set by the game's timer each tick: the step is due
PACE_ALLOW equ 6                        ; steps a frame may lose, in quarter ticks (1.5 ticks)
PACE_AHEAD equ 4 * 4 * 4                ; (the most owed: 4 frames of 4 ticks, then as the game)
PACE_GAP   equ 24                       ; ticks since the last frame: a pause (a load, a talk), afresh
PACE_HOLD  equ 2                        ; ticks what moved is kept before a frame is drawn for it alone
PACE_KEPT  equ 64                       ; entries kept at most (more: the frame is drawn)

pace_far:                               ; (both sites': the way back and the game's routine's segment)
        pop word [cs:pace_ret]          ; (PACE_PASS's or PACE_DRAW's own way back)
        pop word [cs:pace_back]
        pop word [cs:pace_back + 2]
        popf                            ; (the caller's flags: interrupts as they were)
        push es
        push bx
        les bx, [cs:pace_back]
        mov bx, [es:bx]                 ; (the call's segment, as relocated)
        mov [cs:pace_call + 2], bx
        pop bx
        pop es
        add word [cs:pace_back], 2      ; (past it)
        jmp [cs:pace_ret]

pace_pass:
        call pace_far
        mov word [cs:pace_call], 0x2BB9
        cmp byte [PACE_STEP], 0
        je .call
        inc word [cs:pace_steps]        ; (a step due: it runs)
        inc word [cs:pace_ran]
.call:  call far [cs:pace_call]
        cmp word [cs:pace_kept], 0
        je .back
        push eax
        mov eax, [PACE_CLOCK]
        sub eax, [cs:pace_kept_at]
        cmp eax, PACE_HOLD
        pop eax
        jb .back                        ; (kept a moment: the next step draws it too)
        push bx
        mov bx, sp
        mov bx, [ss:bx + 2 + 6]         ; (the frame's "something moved", a byte: the call's 4th argument)
        mov byte [bx], 1
        pop bx
.back:  jmp far [cs:pace_back]

pace_draw:
        call pace_far
        mov word [cs:pace_call], 0x1478
        pusha
        push es
        mov bp, sp                      ; ([BP+24]: how many moved; PUSHA, ES, then x, y, 1)
        mov eax, [PACE_CLOCK]           ; the schedule
        mov edx, eax
        sub eax, [cs:pace_clock]
        mov [cs:pace_clock], edx
        xor dx, dx
        xchg dx, [cs:pace_steps]        ; (the steps run since the last frame)
        cmp eax, PACE_GAP
        jb .owed
        mov word [cs:pace_kept], 0      ; (a pause: what was kept is from before it)
        mov word [cs:pace_debt], 0
        jmp short .judge
.owed:  sub ax, dx                      ; the steps lost
        jge .lost
        xor ax, ax
.lost:  add [cs:pace_lost], ax
        shl ax, 2
        sub ax, PACE_ALLOW
        add ax, [cs:pace_debt]
        cmp ax, -PACE_ALLOW
        jge .low
        mov ax, -PACE_ALLOW             ; (a frame's allowance in hand at most)
.low:   cmp ax, PACE_AHEAD
        jle .high
        mov ax, PACE_AHEAD
.high:  mov [cs:pace_debt], ax
.judge: mov cx, [bp + 24]
        jcxz .draw                      ; (nothing new: drawn for what was kept)
        mov ax, ds
        sub ax, FS_SEG_GAP
        mov es, ax
        cmp word [es:0x19], 0
        jne .draw                       ; (a fight draws every frame)
        cmp word [cs:pace_debt], 0
        jle .draw
        mov ax, [cs:pace_kept]
        add ax, cx
        cmp ax, PACE_KEPT
        ja .draw
        mov di, [cs:pace_kept]          ; left undrawn: the list kept
        or di, di
        jnz .more
        mov edx, [PACE_CLOCK]
        mov [cs:pace_kept_at], edx
.more:  mov [cs:pace_kept], ax
        imul di, di, 10
        add di, pace_saved
        mov ax, cs
        add ax, TAIL_PARAS
        mov es, ax                      ; (PACE_SAVED: the tail's)
        push ds
        mov ax, ds
        sub ax, PACE_LSEG
        mov ds, ax
        mov si, PACE_LIST
        imul cx, cx, 5
        cld
        rep movsw
        pop ds
        inc word [cs:pace_skipped]
        pop es
        popa
        mov ax, 1                       ; (as drawn)
        jmp far [cs:pace_back]
.draw:  mov cx, [cs:pace_kept]          ; the list kept, after this frame's own
        jcxz .go
        mov word [cs:pace_kept], 0
        mov bx, [bp + 24]
        mov ax, bx
        add ax, cx
        cmp ax, PACE_LMAX
        ja .go                          ; (no room: it is dropped)
        mov [bp + 24], ax
        imul di, bx, 10
        add di, PACE_LIST
        mov ax, ds
        sub ax, PACE_LSEG
        mov es, ax
        push ds
        mov ax, cs
        add ax, TAIL_PARAS
        mov ds, ax                      ; (PACE_SAVED: the tail's)
        mov si, pace_saved
        imul cx, cx, 5
        cld
        rep movsw
        pop ds
.go:    cmp word [bp + 24], 0
        pop es
        popa
        je .none                        ; (nothing to draw at all)
        call far [cs:pace_call]
        jmp far [cs:pace_back]
.none:  mov ax, 1
        jmp far [cs:pace_back]

pace_ret     dw 0                       ; (PACE_FAR's own way back)
pace_back    dd 0                       ; (where the INT returns, past the call's segment)
pace_call    dd 0                       ; (the game's routine, its segment as relocated)
pace_clock   dd 0                       ; (the clock at the last frame)
pace_kept_at dd 0                       ; (the clock when the list was first kept)
pace_debt    dw 0                       ; steps lost past the allowance, in quarter ticks (signed)
pace_steps   dw 0                       ; steps run since the last frame
pace_ran     dw 0                       ; steps run (counted, for measuring)
pace_lost    dw 0                       ; steps lost (counted, for measuring)
pace_kept    dw 0                       ; entries kept (PACE_SAVED)
pace_skipped dw 0                       ; frames left undrawn (counted)
section tailz                           ; (PACE_SAVED: the tail's buffer)
pace_saved times PACE_KEPT * 10 db 0  ; (what moved in the frames left undrawn, 10 bytes each)
section image


; PROBE_SCROLL: INT VEC_SCROLL replaces the start of "call far 35B9:0034" (20230h: 9Ah 34h 00h, then
; the segment: A9h makes it a harmless "test ax,<segment>" the loader may relocate), the map's main
; loop asking where the pointer is (far pointers to x and y on the stack). The labels' pass done with
; interrupts off, then the call made as the game would (its segment read from the code, relocated),
; interrupts on again first if the caller had them on.
probe_scroll:
        pop word [cs:s_ip]
        pop word [cs:s_cs]
        pop word [cs:s_fl]
        push es
        push bx
        les bx, [cs:s_ip]
        mov bx, [es:bx + 1]             ; (the call's segment)
        mov [cs:s_far + 2], bx
        mov word [cs:s_far], 0x0034
        pop bx
        pop es
        add word [cs:s_ip], 3           ; (past the segment)
        mov [cs:pointer_ds], ds
        pusha
        push es
        mov byte [cs:va_done], 0
        inc word [cs:main_ticks]
        pushf
        cli                             ; (drawing)
        call panel_tick
        popf
        call label_tick
        call ring_tick
        call redraw_tick                ; (the view again for the Loader's squares and rings)
        call spread_tick                ; (the whole party in view: SPREAD_TICK)
        pushf
        cli                             ; (drawing: DUST_NUDGE)
        call dust_tick                  ; (the walkers' dust: DUST)
        popf
        call pan_tick                   ; (the view to the enemy chosen with Tab: the Loader's PAN)
        call save_tick                  ; (the Loader's quick save or quick load: QUICK SAVES)
        pop es
        popa
        test byte [cs:s_fl + 1], 2      ; (the caller's flags' IF)
        jz .call
        sti
.call:  call far [cs:s_far]
        call drag_mouse                 ; (a drag with the wheel pressed: the view moved, the pointer off the edges)
        call panel_mouse                ; (AX the buttons: a press on the panel kept from the game)
        call target_mouse               ; (... Enter's click on the chosen enemy: TARGETING)
        push word [cs:s_fl]
        push word [cs:s_cs]
        push word [cs:s_ip]
        iret

; SCROLLING (SCROLL_ON), DSCLOG's: pressing the mouse wheel and moving scrolls the map with the pointer,
; as if dragging it (the game has no use for that button). The game is told of the mouse's buttons by the
; driver calling its handler (INT 33h, 0Ch; the sequel's 35B9:00C0 sets it): INT33 puts MOUSE_EVENT in its
; place, which keeps the middle button from the game and starts and ends the drag, and forgets the game's
; handler when the game takes it away (0Ch with CX 0) or resets the driver (00h, 21h). The main loop's call
; for the pointer (PROBE_SCROLL, 20230h) is then followed by DRAG_MOUSE: while dragging, the view is
; centred where the drag puts it through the game's own routine (VIEW_AGAIN's CENTRE, as PAN_TICK), and the
; pointer the loop is told of is kept off the screen's edges (no scrolling of the game's own meanwhile).
; MOUSE_EVENT also keeps where the pointer was last seen (MP_X, MP_Y: MOUSE_SET), and takes a click that
; ends a message box's wait (MSG_SHOWN) from the game.
MIDDLE          equ 4           ; the middle button (pressing the wheel), in the buttons held
EVENT_MID_PRESS equ 0x20        ; the driver's events: it pressed, released
EVENT_MID_LEAVE equ 0x40
EVENT_PRESSES   equ 0x0A        ; (the left and right buttons pressed)
SCROLL_MIDDLE   equ 1           ; SCROLL_ON's bit: dragging with the wheel pressed
old33        dd 0
game_handler dd 0
game_mask    dw 0
drag         db 0               ; (2 while the wheel is held: dragging)
drag_new     db 0               ; (1: the drag's start not yet taken by DRAG_MOUSE)
drag_x       dw 0               ; (where the drag started, and the view then)
drag_y       dw 0
cam0_x       dw 0
cam0_y       dw 0
drag_moves   dw 0               ; (the view moved by a drag, counted: for a look in play)
int33:
        cmp ax, 0x0C
        jne .reset
        or cx, cx
        jz .gone                        ; (taking the handler away)
        mov [cs:game_handler], dx
        mov [cs:game_handler + 2], es
        mov [cs:game_mask], cx
        push es
        push dx
        push cx
        or cx, 0x7F                     ; (moves, and all three buttons)
        push cs
        pop es
        mov dx, mouse_event
        pushf
        call far [cs:old33]
        pop cx
        pop dx
        pop es
        iret
.reset: or ax, ax                       ; (the driver reset, or its software reset: no handler
        jz .gone                        ;   now, as the driver has it)
        cmp ax, 0x21
        jne .chain
.gone:  mov dword [cs:game_handler], 0
        mov word [cs:game_mask], 0
        mov byte [cs:drag], 0
.chain: jmp far [cs:old33]

mouse_event:                            ; AX = events, BX = buttons held, CX, DX = where
        mov [cs:mp_x], cx
        mov [cs:mp_y], dx
        cmp byte [cs:msg_waiting], 0    ; (a press ending a message box's wait: not the game's)
        je .drag
        test al, EVENT_PRESSES
        jz .drag
        mov byte [cs:msg_ended], 1
        and al, ~EVENT_PRESSES
.drag:  call panel_event               ; (a left press on the combat log's panel: not the game's)
        call page_mouse                 ; (... on PGUP or PGDN in the save or load window: the key)
        test byte [cs:scroll_on], SCROLL_MIDDLE
        jz .pass
        test al, EVENT_MID_PRESS        ; the wheel pressed: a drag at once
        jz .mheld
        cmp byte [cs:drag], 0
        jne .mheld
        mov byte [cs:drag], 2
        mov byte [cs:drag_new], 1
        mov [cs:drag_x], cx
        mov [cs:drag_y], dx
.mheld: test al, EVENT_MID_LEAVE
        jz .mdone
        mov byte [cs:drag], 0
.mdone: and bx, ~MIDDLE
        and al, ~(EVENT_MID_PRESS | EVENT_MID_LEAVE)
.pass:  and ax, [cs:game_mask]          ; the events the game asked for, to its handler
        jz .none
        cmp word [cs:game_handler + 2], 0
        je .none
        pusha
        push ds
        push es
        call far [cs:game_handler]
        pop es
        pop ds
        popa
.none:  retf

; DRAG_MOUSE: after the main loop's call for the pointer (AX the buttons; the far pointers to x and y at
; [SP+2], [SP+6] past this call's return; DS the game's): while dragging, on the map, the view centred
; where the drag puts it (the map moves with the pointer; while a label or the ring is drawn it waits a
; pass), and the pointer told the loop kept off the edges and the middle button left out. Keeps all but AX.
drag_mouse:
        cmp byte [cs:drag], 2
        jne .ret
        push bp
        mov bp, sp
        pusha
        push es
        les bx, [bp + 4]
        mov cx, [es:bx]
        les bx, [bp + 8]
        mov dx, [es:bx]
        call on_map
        jne .edges
        cmp byte [cs:drag_new], 0
        je .follow
        mov byte [cs:drag_new], 0
        mov ax, [CAM_X]
        mov [cs:cam0_x], ax
        mov ax, [CAM_Y]
        mov [cs:cam0_y], ax
.follow:
        cmp byte [cs:lbl_busy], 0
        jne .edges
        cmp byte [cs:vga_busy], 0
        jne .edges
        mov ax, [cs:cam0_x]             ; where the drag puts the view
        sub ax, cx
        add ax, [cs:drag_x]
        mov si, [cs:cam0_y]
        sub si, dx
        add si, [cs:drag_y]
        jns .yok
        xor si, si
.yok:   or ax, ax
        jns .xok
        xor ax, ax
.xok:   and ax, 0xFFF8                  ; (as the game keeps it)
        and si, 0xFFF8
        cmp ax, [CAM_X]
        jne .go
        cmp si, [CAM_Y]
        je .edges
.go:    push cx
        push dx
        mov bx, ds
        sub bx, DGROUP - CENTRE_SEG
        mov [cs:centre + 2], bx
        pushf
        cli                             ; (drawing)
        push word 1
        add si, 100
        push si
        add ax, 160
        push ax
        call far [cs:centre]
        add sp, 6
        popf
        pop dx
        pop cx
        inc word [cs:drag_moves]
.edges: cmp cx, 1                       ; (off the edges: no scrolling of the game's own)
        jge .x1
        mov cx, 1
.x1:    cmp cx, 0x13D
        jle .y0
        mov cx, 0x13D
.y0:    cmp dx, 1
        jge .y1
        mov dx, 1
.y1:    cmp dx, 0xC6
        jle .put
        mov dx, 0xC6
.put:   les bx, [bp + 4]
        mov [es:bx], cx
        les bx, [bp + 8]
        mov [es:bx], dx
        pop es
        popa
        pop bp
        and ax, ~MIDDLE
.ret:   ret

; MOUSE_INIT (site 170): "or ax,ax / jnz" (39F0Bh; 4 bytes, SL's 356F5h) as the game starts, just after it
; resets the mouse driver (AX 0: none): the pointer made to move as far up and down as across
; (MOUSE_RATIO), and the "jnz" made. DSCLOG's.
MI_SKIP      equ 0x39F1A - (0x39F0B + 3)
        SHARED_mouse_init

; MOUSE_SET (site 171): "mov word [0A103h],0" (2F110h; 6 bytes, SL's "mov word [0A12Dh],0" at 2A912h)
; just after the game gives the mouse its ranges (the screen's 320 by 200), as its screens start. A video
; mode set leaves the driver's pointer in the middle of its 640 across, which these ranges put at the right
; edge (318, 100): there it's put back where it was last seen (MP_X, MP_Y, the middle at first). The
; pointer moves as far up and down as across (MOUSE_RATIO). DSCLOG's.
mp_x       dw 160               ; (where the pointer was last seen, in the game's 320 by 200)
mp_y       dw 100
mouse_set:
        mov word [0xA103], 0
        call cine_hide
        pushad
        mov ax, 3
        int 0x33
        cmp cx, 318
        jb .ratio
        cmp dx, 100
        jne .ratio
        call mouse_mid
.ratio: call mouse_ratio
        popad
        iret
mouse_mid:
        mov ax, 4
        mov cx, [cs:mp_x]
        mov dx, [cs:mp_y]
        cmp cx, 319                     ; (one seen on a wider screen: the middle)
        jbe .put
        mov cx, 160
        mov dx, 100
.put:   int 0x33
        SHARED_mouse_ratio

; THE POINTER IN SCENES: DSCLOG's (SL's SCENE_POINTER, CINE_STEP and CINE_END), for the sequel's two kinds
; of scene. The game shows no pointer in them, and a click does nothing:
; - its FLI films (the logos and the intro before the title, 1.FLI and 2.FLI; the story's films from the
;   CD's CINE folder), played frame by frame by 831D4h in mode 13h (chained), where after each frame the
;   Shift keys' state (1E8h:11h, the BIOS's shift flags) ends the film (at once with [631Bh] set, else
;   after its 240th frame);
; - a narration over a picture (the opening's, after START GAME, and a map trigger's speech): the game
;   waits while the speech plays (69BDDh, 37B3h:51h's "still playing"), with no key or click to end it.
; Here the arrow is drawn where the driver has the pointer at each frame or pass of the wait (CINE_CHECK),
; and a button pressed since the last ends the film as Shift does (FLI_KEY)
; or the narration (SPEECH_WAIT: the speech stopped, 37B3h:3A5h, as the talk's own click stops it,
; 8850Ah). The arrow is SL's (POINTER.BIN: the game's own, from Shattered Lands' files, which the Loader
; writes; else a plain one), drawn in chained or planar (mode X) VGA memory, whichever the scene uses.
CP_MAX_ROWS  equ 16             ; (the room for the arrow: dsloader/scenepointer.py's)
CP_COLS      equ 11
CP_SHAPE_BYTES equ 88
CP_PIXELS    equ 76
SW_BACK      equ 0x69BE5 - 0x69BDD  ; (SPEECH_WAIT's "jnz" back to the test)
SPEECH_SEG   equ 0x3611         ; (37B3h at a load segment of 1A2h: the speech's routines' segment)
SPEECH_STOP  equ 0x03A5
cine_shown db 0                 ; (1 while a scene plays: the driver's ranges the screen's)
cp_drawn   db 0                 ; (1: the arrow on the screen, at CP_X, CP_Y, CP_PAGE in A000h,
cp_x       dw 0                 ;   in CP_MAP's colours, CP_UNDER what was under it)
cp_y       dw 0
cp_page    dw 0
cp_now     dw 0
cp_op      db 0
cp_chain   db 0                 ; (the sequencer's chain-4 bit: mode 13h's memory, not mode X's)
cp_last    dw 0                 ; (the BIOS tick at the last drawing)
cp_seq_i   db 0
cp_mask    db 0
cp_gc_i    db 0
cp_gc_ix   db 1, 3, 4, 5, 8     ; (the graphics controller's registers kept: set/reset enable,
cp_gc      times 5 db 0         ;   rotate, read plane, mode, bit mask)
cp_map     times CP_COLS db 0   ; (each colour's nearest in the palette, and how near)
cp_best    times CP_COLS db 0
cp_under   times CP_PIXELS db 0
cine_stop  dw SPEECH_STOP, 0
cine_skips dw 0                 ; (scenes ended by a click, counted: for a look in play)
; CP_DATA: the arrow, as POINTER.BIN has it (read over this as the helper loads): its rows, its colours,
; their red, green and blue (6 bits), then each row's pixels from its left (a colour's number from 1, or
; FFh for none), each row ending with 0. Without the file, a plain arrow of the helper's own.
cp_data:
cp_rows    db 11
cp_ncols   db 2
cp_rgb     db 0, 0, 0, 63, 63, 63
           times (CP_COLS - 2) * 3 db 0
        SHARED_cp_shape
CP_DATA_BYTES equ $ - cp_data
POINTER_FILE db "D:\POINTER.BIN", 0 ; (CP_DATA's file, read as the helper loads)

; SPEECH_WAIT (site 172): "or al,al / jnz 69BDDh" (69BE2h; 4 bytes) in the wait while a narration plays
; (AL 1: still playing): the arrow drawn, and a click stops the speech and ends the wait; else the "jnz".
speech_wait:
        sti
        or al, al
        jz .done
        mov byte [cs:cp_always], 0
        call cine_check
        jc .skip
        push bp
        mov bp, sp
        sub word [bp + 2], SW_BACK
        pop bp
        iret
.skip:  pusha
        push es
        inc word [cs:cine_skips]
        mov bx, ds
        sub bx, DGROUP - SPEECH_SEG
        mov [cs:cine_stop + 2], bx
        call far [cs:cine_stop]
        pop es
        popa
.done:  call cine_hide
        iret

; FLI_KEY (site 173): "test ax,3" (8335Ch; 3 bytes) after a FLI's frame, AX the shift flags (bits 0 and 1
; the Shift keys: the "jnz" after it ends the film): the arrow drawn, and a click since the last frame
; counts as Shift; the flags as the "test" leaves them.
fli_key:
        mov byte [cs:cp_always], 1
        call cine_check
        jnc .test
        or ax, 3
        inc word [cs:cine_skips]
.test:  push bp
        mov bp, sp
        test ax, 3
        jz .z
        and word [bp + 6], ~0x40        ; (ZF clear)
        pop bp
        iret
.z:     or word [bp + 6], 0x40
        pop bp
        iret

; FLI_END (site 174): "mov [bp-2],ax" (8324Dh; 3 bytes) as the FLI's frames are over, played or ended:
; the arrow wiped, then that.
fli_end:
        call cine_hide
        mov [bp - 2], ax
        iret

; CINE_CHECK: CF set if a button was pressed since the last check (a scene's first check takes the
; driver's ranges as the screen's and forgets the presses before it); else the arrow drawn again where
; the pointer is: with CP_ALWAYS (a film's frame, drawn over it) each time, else (a narration's wait,
; which asks a few hundred times a second) only when the pointer has moved or every CP_AGAIN BIOS ticks
; (a picture fading in), so the arrow is on the screen nearly all the time. Registers kept.
CP_AGAIN     equ 4
cp_always  db 0
cine_check:
        pusha
        cmp byte [cs:cine_shown], 0
        jne .ask
        mov byte [cs:cine_shown], 1
        call cine_mouse
        call cine_presses               ; (the presses before the scene let go)
        jmp .now
.ask:   call cine_presses               ; (ZF: none)
        jz .draw
        popa
        stc
        ret
.draw:  cmp byte [cs:cp_always], 0
        jne .now
        cmp byte [cs:cp_drawn], 0
        je .now
        mov ax, 3
        int 0x33
        cmp cx, [cs:cp_x]
        jne .now
        cmp dx, [cs:cp_y]
        jne .now
        push es
        xor ax, ax
        mov es, ax
        mov ax, [es:0x46C]
        pop es
        sub ax, [cs:cp_last]
        cmp ax, CP_AGAIN
        jb .kept
.now:   push es
        xor ax, ax
        mov es, ax
        mov ax, [es:0x46C]
        pop es
        mov [cs:cp_last], ax
        call cp_draw
.kept:  popa
        clc
        ret
        SHARED_cine_presses
cine_mouse:                             ; the driver's ranges the screen's, the pointer where last seen
        pusha
        mov ax, 7
        xor cx, cx
        mov dx, 319
        int 0x33
        mov ax, 8
        xor cx, cx
        mov dx, 199
        int 0x33
        mov ax, 4
        mov cx, [cs:mp_x]
        mov dx, [cs:mp_y]
        int 0x33
        popa
        ret
cine_where:                             ; CX, DX: the pointer (a video mode set puts the driver
        mov ax, 3                       ;   back to 640 across, in its middle: CINE_MOUSE again)
        int 0x33
        cmp cx, 319
        jbe .ok
        call cine_mouse
        mov cx, [cs:mp_x]
        mov dx, [cs:mp_y]
.ok:    cmp dx, 199
        jbe .in
        mov dx, 199
.in:    mov [cs:mp_x], cx
        mov [cs:mp_y], dx
        ret
cine_hide:                              ; the arrow wiped, the scene over
        mov byte [cs:cine_shown], 0
        jmp cp_erase

; CP_DRAW: the arrow wiped (CP_ERASE) and drawn again where the driver has the pointer, each colour as
; the palette's nearest, what it covers kept. CP_ERASE puts that back only where the arrow still is (a
; frame drawn over it since is left as it is).
cp_draw:
        pusha
        call cp_colours                 ; (the palette read first: the arrow off the screen only
        call cp_erase                   ;   while it moves)
        call cp_put
        popa
        ret
        SHARED_cp_put
        SHARED_cp_erase
        SHARED_cp_colours
cp_vga:                                 ; the VGA's registers the drawing changes kept and set;
        mov dx, 0x3C4                   ;   CP_NOW the page shown, CP_CHAIN the memory's kind
        in al, dx
        mov [cs:cp_seq_i], al
        mov al, 2
        out dx, al
        inc dx
        in al, dx
        mov [cs:cp_mask], al
        mov al, 0x0F
        out dx, al
        dec dx
        mov al, 4
        out dx, al
        inc dx
        in al, dx
        and al, 8
        mov [cs:cp_chain], al
        mov dx, 0x3CE
        in al, dx
        mov [cs:cp_gc_i], al
        xor bx, bx
.keep:  mov al, [cs:cp_gc_ix + bx]
        out dx, al
        inc dx
        in al, dx
        mov [cs:cp_gc + bx], al
        dec dx
        inc bx
        cmp bx, 5
        jb .keep
        mov ax, 0x0001
        out dx, ax
        mov ax, 0x0003
        out dx, ax
        mov ah, [cs:cp_gc + 3]
        and ah, 0x40
        mov al, 5
        out dx, ax
        mov ax, 0xFF08
        out dx, ax
        mov dx, 0x3D4
        in al, dx
        mov cl, al
        mov al, 0x0C
        out dx, al
        inc dx
        in al, dx
        mov ah, al
        dec dx
        mov al, 0x0D
        out dx, al
        inc dx
        in al, dx
        mov [cs:cp_now], ax
        dec dx
        mov al, cl
        out dx, al
        ret
        SHARED_cp_vga_back
        SHARED_cp_pass
cp_addr:                                ; DI: pixel CX, DX's (in mode X its plane read and written)
        push ax
        push cx
        push dx
        cmp byte [cs:cp_chain], 0
        je .planes
        imul di, dx, 320                ; (chained: a byte a pixel, from the page's start)
        add di, cx
        jmp .out
.planes:
        imul di, dx, 80
        mov ax, cx
        shr ax, 2
        add di, ax
        add di, [cs:cp_page]
        and cl, 3
        mov ah, 1
        shl ah, cl
        mov al, 2
        mov dx, 0x3C4
        out dx, ax
        mov ah, cl
        mov al, 4
        mov dx, 0x3CE
        out dx, ax
.out:   pop dx
        pop cx
        pop ax
        ret

; PROBE_TICK: INT VEC_TICK replaces "inc word cs:[0004h]" (5 bytes: INT + 3 NOPs; 3DA2Ch, SL's
; 3925Ch), the first instruction of the game's timer handler. Does that, and every other strike puts
; the labels again; every TICK_EVERY-th notes where the game was (the timer's own frame, just above this
; interrupt's: IP, CS, flags, SS, SP, BP, DS, ES) in TICKS, as DSCLOG's, for the Loader's freeze report.
; Interrupts stay off.
TICK_EVERY equ 32
TICK_SLOTS equ 16
TICK_SIZE  equ 16
        times -(TICK_SIZE != 16) db 0   ; (a negative count: the "shl bx,4" below takes a slot as 16 bytes)
probe_tick:
        push bp
        mov bp, sp                      ; BP+2 this interrupt's frame (in the handler), BP+8 the timer's
        push ds
        push ax
        push bx
        mov ds, [bp + 4]                ; the handler's CS
        inc word [4]                    ; the replaced instruction
        inc word [cs:tick_count]
        test byte [cs:tick_count], 1
        jnz .seen
        call label_stamp
.seen:  test byte [cs:tick_count], TICK_EVERY - 1
        jnz .out
        cmp word [cs:tail_seg], 0
        je .out                         ; (the tail not set yet)
        mov bx, [cs:tick_seq]
        and bx, TICK_SLOTS - 1
        shl bx, 4                       ; (TICK_SIZE)
        add bx, ticks
        mov ds, [cs:tail_seg]           ; (TICKS: the tail's)
        mov ax, [bp + 8]
        mov [bx], ax                    ; +0 IP
        mov ax, [bp + 10]
        mov [bx + 2], ax                ; +2 CS
        mov ax, [bp + 12]
        mov [bx + 4], ax                ; +4 flags
        mov [bx + 6], ss                ; +6 SS
        lea ax, [bp + 14]
        mov [bx + 8], ax                ; +8 SP
        mov ax, [bp]
        mov [bx + 10], ax               ; +10 BP
        mov ax, [bp - 2]
        mov [bx + 12], ax               ; +12 DS
        mov [bx + 14], es               ; +14 ES
        inc word [cs:tick_seq]
.out:   pop bx
        pop ax
        pop ds
        pop bp
        iret
section tailz
ticks      times TICK_SLOTS * TICK_SIZE db 0 ; (PROBE_TICK's, the Loader's to read: the header's +356)
section image

; ON_MAP: ZF set if the game is on the map (SCREEN_IS 1); registers kept
        SHARED_on_map

; DAC_TICK: the palette read into the far block's DAC about once a second (the Loader's labels'
; colours: combatlog.tsr_dac). DS the game's; keeps all.
dac_tick:
        pusha
        push es
        xor ax, ax
        mov es, ax
        mov ax, [es:0x46C]
        mov dx, ax
        sub dx, [cs:dac_at]
        cmp dx, 18
        jb .out
        mov [cs:dac_at], ax
        inc word [cs:dac_reads]
        mov es, [cs:far_seg]
        mov di, FAR_DAC
        mov dx, 0x3C7
        xor al, al
        out dx, al
        mov dx, 0x3C9
        mov cx, 768
        cld
        rep insb
        mov si, FAR_DAC                 ; (changed since the last read: counted, DAC_CHANGES)
        mov cx, 768
        xor bx, bx
        xor ax, ax
.sum:   mov al, [es:si]
        add bx, ax
        rol bx, 1
        inc si
        loop .sum
        cmp bx, [cs:dac_sum]
        je .out
        mov [cs:dac_sum], bx
        inc word [cs:dac_changes]
.out:   pop es
        popa
        ret
dac_sum dw 0

; LABEL_TICK: from the main loop (DS the game's): the labels placed, the old places of those gone or
; moved drawn again, then all put
label_tick:
        cmp byte [cs:lbl_busy], 0
        jne .ret
        inc word [cs:label_ticks]
        call dac_tick
        pushf
        cli
        mov ax, [CAM_X]
        mov bx, [CAM_Y]
        xchg ax, [cs:lbl_cx]
        xchg bx, [cs:lbl_cy]
        sub ax, [cs:lbl_cx]             ; (AX, BX: where the view's scroll moved what was on screen)
        sub bx, [cs:lbl_cy]
        mov cx, ax
        or cx, bx
        jz .slots
        mov si, lbl_state
.moved: cmp byte [cs:si + LS_SHOWN], 0
        je .nmoved
        call label_erase                ; (where it was)
        add [cs:si + LS_X], ax
        add [cs:si + LS_Y], bx
        call label_erase                ; (where the scroll's copy put it)
.nmoved:
        add si, 8
        cmp si, lbl_state + LBL_SLOTS * 8
        jb .moved
.slots: push fs
        call tail_fs                    ; (LBL_SLOTS: the tail's)
        mov si, lbl_state
        mov di, lbl_slots
.slot:  call label_where
        jc .off
        mov dl, [fs:di]
        cmp byte [cs:si + LS_SHOWN], 0
        je .new
        cmp dl, [cs:si + LS_SEEN]
        jne .move
        cmp ax, [cs:si + LS_X]
        jne .move
        cmp bx, [cs:si + LS_Y]
        je .next
.move:  call label_erase
.new:   call label_adopt
        jmp .next
.off:   cmp byte [cs:si + LS_SHOWN], 0
        je .next
        call label_erase
.next:  add di, LBL_SIZE
        add si, 8
        cmp si, lbl_state + LBL_SLOTS * 8
        jb .slot
        pop fs
        call label_stamp
        popf
.ret:   ret

; LABEL_ADOPT: label FS:DI (DL its number) shown from now at AX, BX (SI its state)
        SHARED_label_adopt

; LABEL_WHERE: CF clear and AX, BX the top left on screen of label DI (FS:DI, the Loader's slot) if it
; is to be shown: one, its size in bounds, on the map, its thing in OBJ_LIST; DS the game's (DSCLOG's,
; with the sequel's 25h-byte things); CX kept
label_where:
        cmp byte [fs:di], 0
        je .no
        cmp byte [fs:di + 1], LBL_ROW * 8
        ja .no
        cmp byte [fs:di + 2], LBL_H_MOST
        ja .no
        call on_map
        jne .no
        push ds
        mov ds, [cs:pointer_ds]
        push cx
        push es
        les bx, [OBJ_LIST]
        mov cx, [OBJ_COUNT]
        mov ax, [fs:di + 6]
        jcxz .none
.find:  cmp [es:bx + 6], ax
        je .got
        add bx, 8
        loop .find
.none:  pop es
        pop cx
        pop ds
.no:    stc
        ret
.got:   pop es
        pop cx
        cmp ax, MAP_COUNT
        jae .no_ds
        imul bx, ax, THING_SIZE
        movzx ax, byte [fs:di + 1]
        shr ax, 1
        neg ax
        add ax, [bx + MAP_THINGS + THING_X]  ; (its feet, on the map)
        sub ax, [CAM_X]
        jge .x0
        xor ax, ax
.x0:    push dx
        mov dx, 320
        sub dl, [fs:di + 1]
        sbb dh, 0
        cmp ax, dx
        jle .x1
        mov ax, dx
.x1:    mov bx, [bx + MAP_THINGS + THING_Y]
        sub bx, [CAM_Y]
        mov dx, bx                      ; (its feet, on screen)
        sub bl, [fs:di + 3]
        sbb bh, 0
        sub bl, [fs:di + 2]
        sbb bh, 0
        cmp bx, LBL_TOP
        jge .y1
        mov bx, dx                      ; (under its feet)
        add bx, 2
        or bx, bx
        jl .off
.y1:    mov dx, 200
        sub dl, [fs:di + 2]
        sbb dh, 0
        cmp bx, dx
        jle .y2
        mov bx, dx
.y2:    pop dx
        pop ds
        clc
        ret
.off:   pop dx
.no_ds: pop ds
        stc
        ret

; LABEL_ERASE: where label SI (its LBL_STATE) was drawn again by the game's routine for a rectangle of
; the view (REDRAW_SEG:REDRAW_OFF, page 1 and a flip, as the game's own call), widened to whole bytes
; of the planes; it is no longer shown. Nothing when it is all off the screen. Keeps all.
label_erase:
        mov byte [cs:lbl_busy], 1
        mov byte [cs:si + LS_SHOWN], 0
        pusha
        push ds
        push es
        mov ds, [cs:pointer_ds]
        movzx dx, byte [cs:si + LS_H]
        add dx, [cs:si + LS_Y]
        dec dx                          ; y1
        jl .out
        movzx cx, byte [cs:si + LS_W]
        add cx, [cs:si + LS_X]
        dec cx
        jl .out
        or cx, 3
        cmp cx, 319
        jle .x1
        mov cx, 319
.x1:    cmp dx, 199
        jle .y1
        mov dx, 199
.y1:    mov bx, [cs:si + LS_Y]          ; y0
        cmp bx, 199
        jg .out
        or bx, bx
        jge .y0
        xor bx, bx
.y0:    mov ax, [cs:si + LS_X]
        cmp ax, 319
        jg .out
        or ax, ax
        jge .x0
        xor ax, ax
.x0:    and ax, ~3                      ; x0
        push ax
        mov ax, ds
        sub ax, DGROUP - REDRAW_SEG
        mov [cs:redraw_far + 2], ax
        pop ax
        push word 1                     ; (the flip)
        push dx
        push cx
        push bx
        push ax
        push word 1                     ; (the page)
        push word [CAM_Y]
        push word [CAM_X]
        call far [cs:redraw_far]
        add sp, 16
.out:   pop es
        pop ds
        popa
        mov byte [cs:lbl_busy], 0
        ret

; LABEL_STAMP: the labels shown put on the screen on show (as the Loader has them: not one it is
; changing), on the map only, the view where LABEL_TICK last saw it. A new label is placed here too,
; as the main loop doesn't run while the game shows an attack or a spell. Any DS; keeps all.
label_stamp:
        cmp byte [cs:lbl_busy], 0
        jne .ret
        push fs
        call tail_fs                    ; (LBL_SLOTS: the tail's)
%assign slot 0
%rep LBL_SLOTS
        cmp byte [fs:lbl_slots + slot * LBL_SIZE], 0
        jne .some
%assign slot slot + 1
%endrep
.none:  pop fs
.ret:   ret                             ; (no label in any slot: nothing to put, nor to place)
.some:  cmp byte [cs:vga_busy], 0
        jne .none
        mov byte [cs:lbl_busy], 1
        pusha
        push ds
        push es
        call on_map
        jne .out
        mov ds, [cs:pointer_ds]
        mov ax, [CAM_X]
        cmp ax, [cs:lbl_cx]
        jne .out
        mov ax, [CAM_Y]
        cmp ax, [cs:lbl_cy]
        jne .out
        mov dx, 0x3D4                   ; the screen on show: where the VGA starts it, the CRTC's
        in al, dx                       ;   index kept
        mov ah, al
        mov al, 0x0C
        out dx, al
        inc dx
        in al, dx
        dec dx
        xchg al, ah
        out dx, al
        xor al, al
        shr ax, 4
        add ax, 0xA000
        mov es, ax
        call vga_save
        mov si, lbl_state
        mov di, lbl_slots
.slot:  mov dl, [fs:di]
        cmp byte [cs:si + LS_SHOWN], 0
        jne .shown
        push es
        call label_where
        pop es
        jc .next
        call label_adopt
.shown: cmp dl, [cs:si + LS_SEEN]
        jne .next
        call label_put
.next:  add di, LBL_SIZE
        add si, 8
        cmp si, lbl_state + LBL_SLOTS * 8
        jb .slot
        call vga_restore
.out:   pop es
        pop ds
        popa
        pop fs
        mov byte [cs:lbl_busy], 0
        ret

; LABEL_PUT: label DI (FS:DI; SI its state) into ES, the screen, a plane at a time; AX to DX not kept
label_put:
        push bp
        push di
        mov ax, [fs:di + 4]
        mov [cs:lp_ink], ax             ; (and LP_EDGE)
        add di, 8                       ; (DI: the ink's mask, a row of it)
        xor bp, bp                      ; (BP: the plane)
.plane: mov dx, 0x3C4
        mov cx, bp
        mov ax, 0x0102
        shl ah, cl
        out dx, ax
        mov bx, di
        mov ax, [cs:si + LS_Y]
        imul ax, ax, 80
        mov [cs:lp_line], ax
        xor dx, dx                      ; (DX: the row)
.row:   mov cx, bp
        sub cx, [cs:si + LS_X]
        and cx, 3                       ; (CX: the label's first x in this plane)
        push di
        mov di, [cs:si + LS_X]
        add di, cx
        shr di, 2
        add di, [cs:lp_line]
.px:    cmp cl, [cs:si + LS_W]
        jae .nrow
        bt word [fs:bx], cx
        mov al, [cs:lp_ink]
        jc .w
        bt word [fs:bx + LBL_MASK], cx
        jnc .npx
        mov al, [cs:lp_edge]
.w:     mov [es:di], al
.npx:   add cx, 4
        inc di
        jmp .px
.nrow:  pop di
        add bx, LBL_ROW
        add word [cs:lp_line], 80
        inc dx
        cmp dl, [cs:si + LS_H]
        jb .row
        inc bp
        cmp bp, 4
        jb .plane
        pop di
        pop bp
        ret

; the VGA's registers the labels change, kept and put back (DSCLOG's VGA_SAVE, VGA_RESTORE)
vga_busy db 0
sc_index db 0
sc_mask  db 0
gc_index db 0
gc_regs  db 1, 3, 4, 5, 8
gc_saved times 5 db 0
        SHARED_vga_save

        SHARED_vga_restore

; ---- PANEL: DSCLOG's combat log's panel over the map, on the sequel ----
; The Loader draws it (combatlog.py: the frame and the log's lines), PANEL_W x PANEL_H palette indices
; in the far block (FAR_PANEL; each row its planes in turn), and this puts that picture on screen,
; bottom right. The map is drawn straight into the screen on show, a rectangle at a time, so the
; picture is put again from the main loop (PANEL_TICK, from PROBE_SCROLL) when the Loader has a new one
; (PANEL_NEW), when the view scrolled (the game copies the screen, the panel too: the copy drawn over
; again), and about once a BIOS tick round the pointer; before the game's pointer is drawn over it
; (PROBE_POINTER), and on the new screen when the game flips its two (FLIP_SITE). PANEL_ON is the
; Loader's: set, the panel is shown; cleared, or the Loader silent for STATS_FRESH (its STATS_STAMP),
; the view under it is drawn again. DSCLOG's, but for the sequel's addresses and the view drawn again
; only under the panel (the game's rectangle routine), not whole.
PANEL_X0   equ 136              ; (x0 and the width a multiple of 4: whole bytes of the planes)
PANEL_Y0   equ 120
PANEL_W    equ 180
PANEL_H    equ 78
PANEL_H_MOST equ 130
PANEL_BYTES equ PANEL_W * PANEL_H_MOST
PAGES_SEG  equ 0x0BF3           ; the page routines' segment (less the load segment: SL's 0980h)
SHOWN_PAGE equ 0x118E           ; (in it) 1: A400h shown
STATS_FRESH equ 91              ; BIOS ticks (5 seconds) the Loader may be silent
L_FRESH    equ 2
panel_shown db 0
panel_pseg  dw 0
panel_page  dw 0
panel_drawn dw PANEL_Y0
panel_drawn_rows dw PANEL_H
panel_at   dw 0
panel_lx   dw 0
panel_ly   dw 0
panel_cx   dw 0
panel_cy   dw 0
map_tick   dw 0
panel_puts dw 0                 ; (counted: a look in play)

; LOADER_FRESH: ZF set if the Loader has passed within STATS_FRESH ticks; registers kept
loader_fresh:
        push es
        push ax
        xor ax, ax
        mov es, ax
        mov ax, [es:0x46C]
        sub ax, [cs:stats_stamp]
        cmp ax, STATS_FRESH
        jae .no
        xor ax, ax
        jmp .out
.no:    or ax, 1
.out:   pop ax
        pop es
        ret

; PANEL_TICK: from the main loop (DS the game's; AX to DI not kept)
panel_tick:
        xor ax, ax
        mov es, ax
        mov ax, [es:0x46C]
        mov [cs:map_tick], ax
        mov byte [cs:overhead], 0       ; (the map's main loop ran: no screen of MAP_KEY's up)
        cmp word [cs:panel_seg], 0
        je .ret
        call on_map
        jne .ret
        cmp word [cs:panel_on], 0
        je .off
        call loader_fresh
        je .on
.off:   cmp byte [cs:panel_shown], 0
        je .ret
        mov byte [cs:panel_shown], 0
        xor ax, ax
        xor bx, bx
        call panel_erase                ; (the view under it drawn again)
.ret:   ret
.on:    mov ax, [CAM_X]                 ; the view moved by the game's own scrolling: the screen
        xchg ax, [cs:panel_cx]          ;   copied, the panel too; that copy drawn over (AX, BX:
        sub ax, [cs:panel_cx]           ;   how far it moved), then the panel put again
        mov bx, [CAM_Y]
        xchg bx, [cs:panel_cy]
        sub bx, [cs:panel_cy]
        mov cx, ax
        or cx, bx
        jz .still
        cmp byte [cs:panel_shown], 0
        je .still
        call view_again                 ; (the view drawn again whole: the copies gone)
        jmp .draw
.still: cmp word [cs:panel_new], 0
        je .old
        mov word [cs:panel_new], 0
        cmp byte [cs:panel_shown], 0
        je .draw
        mov ax, [cs:panel_top]          ; smaller than it was: the view drawn again under it first
        cmp ax, [cs:panel_drawn]
        jbe .draw
        xor ax, ax
        xor bx, bx
        call panel_erase
        jmp .draw
.old:   cmp byte [cs:panel_shown], 0
        je .draw
        mov ax, [cs:map_tick]           ; put again at most once a BIOS tick
        sub ax, [cs:panel_at]
        cmp ax, 1
        jb .ret
        mov ax, [cs:panel_mx]           ; the pointer moved: put again, the pointer over it
        cmp ax, [cs:panel_lx]
        jne .draw
        mov ax, [cs:panel_my]
        cmp ax, [cs:panel_ly]
        jne .draw
        mov ax, [cs:map_tick]           ; and anyway, round the pointer
        mov [cs:panel_at], ax
        call panel_draw_around
        ret
.draw:  mov ax, [cs:map_tick]
        mov [cs:panel_at], ax
        mov byte [cs:panel_shown], 1
        mov ax, [cs:panel_mx]
        mov [cs:panel_lx], ax
        mov ax, [cs:panel_my]
        mov [cs:panel_ly], ax
        call panel_draw_pointer
        ret

; VIEW_AGAIN: DSCLOG's: the view drawn again, all of it, as the game does when the view is centred
; where it is (1C5F:01F3, 219E3h, SL's 191F:0281: centre on (x, y), 1 to draw it again); once a pass
; of the main loop (VA_DONE, cleared by PROBE_SCROLL). DS the game's; keeps all.
CENTRE_SEG equ 0x1C5F
CENTRE_OFF equ 0x01F3
view_again:
        cmp byte [cs:va_done], 0
        jne .ret
        mov byte [cs:va_done], 1
        pusha
        push es
        mov bx, ds
        sub bx, DGROUP - CENTRE_SEG
        mov [cs:centre + 2], bx
        push word 1
        mov ax, [CAM_Y]
        add ax, 100
        push ax
        mov ax, [CAM_X]
        add ax, 160
        push ax
        call far [cs:centre]
        add sp, 6
        pop es
        popa
.ret:   ret
va_done db 0
centre  dw CENTRE_OFF, 0

; PROBE_CENTRE: INT VEC_CENTRE replaces "mov byte [143Fh],0" (5 bytes: INT + 3 NOPs) at the end of the
; game's routine centring the view (1C5F:01F3, 219E3h; [BP+0Ah] 1 if it drew the view). The game's
; drawing of a moved view scrolls what is on the screen, the panel with it, and draws only what came
; into view: a copy of the panel left beside it. So a move while the panel is shown is drawn again at
; once (VIEW_MOVED; twice if the game's call did not draw it: the first draw scrolls). Then the
; replaced.
probe_centre:
        sti
        mov byte [0x143F], 0
        push ax
        mov al, 1
        cmp byte [bp + 0x0A], 1         ; (the routine's BP: the game drew the view?)
        je .drawn
        inc al
.drawn: call view_moved
        pop ax
        iret

; PROBE_FOLLOW: INT VEC_FOLLOW replaces "add sp,8" (3 bytes) after the game's call drawing the view
; moved by its following a figure (262C:06C4, its "push 1" a draw; at 1E3ECh, 20193h, 2143Eh: three
; routines moving the view by 262C:0D80, which writes CAM_X and CAM_Y): the move drawn again at once
; (VIEW_MOVED), then the caller's 8 bytes of arguments taken off (the frame moved up over them).
probe_follow:
        sti
        push ax
        mov al, 1
        call view_moved
        pop ax
        push bp
        mov bp, sp
        push ax
        mov ax, [bp + 6]                ; (flags, CS, IP and BP up by 8)
        mov [bp + 14], ax
        mov ax, [bp + 4]
        mov [bp + 12], ax
        mov ax, [bp + 2]
        mov [bp + 10], ax
        mov ax, [bp]
        mov [bp + 8], ax
        pop ax
        add sp, 8
        pop bp
        iret

; VIEW_MOVED: if the view has moved (CAM_X, CAM_Y not the panel's PANEL_CX, PANEL_CY) while the panel
; is shown on the map, it is drawn again AL times (VIEW_AGAIN); CENTRE_BUSY keeps those draws from
; coming here again. DS the game's; keeps all.
view_moved:
        cmp byte [cs:centre_busy], 0
        jne .ret
        cmp word [cs:panel_seg], 0
        je .ret
        cmp byte [cs:panel_shown], 0
        je .ret
        call on_map
        jne .ret
        push bx
        mov bx, [CAM_X]
        cmp bx, [cs:panel_cx]
        jne .moved
        mov bx, [CAM_Y]
        cmp bx, [cs:panel_cy]
        je .same
.moved: mov bx, [CAM_X]
        mov [cs:panel_cx], bx
        mov bx, [CAM_Y]
        mov [cs:panel_cy], bx
        mov byte [cs:centre_busy], 1
        push ax
.again: mov byte [cs:va_done], 0
        call view_again
        dec al
        jnz .again
        pop ax
        mov byte [cs:centre_busy], 0
        inc word [cs:centre_redraws]
.same:  pop bx
.ret:   ret
centre_busy    db 0
centre_redraws dw 0

; PANEL_ERASE: where the panel was last drawn, moved by AX, BX (a scroll's copy: 0, 0 for its own
; place), drawn again by the game's rectangle routine (REDRAW_RECT); DS the game's; keeps all
panel_erase:
        pusha
        mov si, ax
        mov di, bx
        mov ax, PANEL_X0
        add ax, si
        mov cx, PANEL_X0 + PANEL_W - 1
        add cx, si
        mov bx, [cs:panel_drawn]
        add bx, di
        mov dx, bx
        add dx, [cs:panel_drawn_rows]
        dec dx
        call redraw_rect
        popa
        ret

; REDRAW_RECT: the view's rectangle AX x0, BX y0, CX x1, DX y1 (on screen) drawn again by the game's
; routine (REDRAW_SEG:REDRAW_OFF, page 1 and a flip, as the game's own call), kept on the screen,
; widened to whole bytes of the planes; nothing if it is all off it. DS the game's; keeps all.
redraw_rect:
        pusha
        push es
        cmp cx, 0
        jl .out
        cmp dx, 0
        jl .out
        cmp ax, 319
        jg .out
        cmp bx, 199
        jg .out
        or ax, ax
        jge .x0
        xor ax, ax
.x0:    and ax, ~3
        or bx, bx
        jge .y0
        xor bx, bx
.y0:    or cx, 3
        cmp cx, 319
        jle .x1
        mov cx, 319
.x1:    cmp dx, 199
        jle .y1
        mov dx, 199
.y1:    push ax
        mov ax, ds
        sub ax, DGROUP - REDRAW_SEG
        mov [cs:redraw_far + 2], ax
        pop ax
        push word 1                     ; (the flip)
        push dx
        push cx
        push bx
        push ax
        push word 1                     ; (the page)
        push word [CAM_Y]
        push word [CAM_X]
        call far [cs:redraw_far]
        add sp, 16
.out:   pop es
        popa
        ret

; PANEL_LIVE: ZF set if the panel is on screen: shown, the page on show the one it was last drawn
; into, and the game on the map (for the pointer drawn over it)
        SHARED_panel_live

; PANEL_MOUSE: after the main loop's call for the pointer (AX the buttons; the far pointers to x and y
; at [SP+4], [SP+8] past this call's return): the pointer noted for the Loader; a left press on the
; panel, while it is shown, counted and kept from the game until released (the Loader scrolls the
; log: combatlog.py)
panel_mouse:
        push bp
        mov bp, sp
        push es
        push bx
        les bx, [bp + 4]
        mov cx, [es:bx]
        les bx, [bp + 8]
        mov dx, [es:bx]
        mov [cs:panel_mx], cx
        mov [cs:panel_my], dx
        cmp word [cs:panel_held], 0     ; (a press on the panel, PANEL_EVENT's: not the game's)
        je .out
        and al, ~1
.out:   pop bx
        pop es
        pop bp
        ret

; PANEL_EVENT: in MOUSE_EVENT (CX, DX where, AL the events, BX the buttons held), SL's PANEL_MOUSE: a left
; press on the panel while it is on the map (PANEL_HERE) counted with where it was (PANEL_HITS, PANEL_HX,
; PANEL_HY) and held (PANEL_HELD) till its release, both kept from the game. The main loop's call for the
; pointer (PANEL_MOUSE, above) saw a press only if the button was still down as it ran: a quick click
; was missed there and went to the game's own handler (the party walked to where the panel is).
panel_event:
        cmp word [cs:panel_held], 0
        jne .held
        test al, EVENT_LEFT_PRESS
        jz .ret
        call panel_here
        jne .ret
        push cx
        push dx
        sub cx, PANEL_X0
        cmp cx, PANEL_W
        jae .out
        sub dx, [cs:panel_top]
        cmp dx, [cs:panel_rows]
.out:   pop dx
        pop cx
        jae .ret
        mov word [cs:panel_held], 1
        mov [cs:panel_hx], cx
        mov [cs:panel_hy], dx
        inc word [cs:panel_hits]
.held:  test al, EVENT_LEFT_LEAVE
        jz .keep
        mov word [cs:panel_held], 0
.keep:  and al, ~(EVENT_LEFT_PRESS | EVENT_LEFT_LEAVE)
        and bx, ~1
.ret:   ret

; PANEL_HERE: ZF set if the panel is on screen over the map (PANEL_SHOWN, ON_MAP), for L and a press on it.
; Not SL's PANEL_LIVE page test (the page on show the one the panel was last drawn into): with a window
; ON_MAP is already clear, and on the map the test could only keep L and a click from a panel on screen
; (the owner's report in DOSBox-X: L didn't hide it, clicks went to the game). Registers kept.
panel_here:
        cmp byte [cs:panel_shown], 0
        je .no
        jmp on_map
.no:    cmp sp, 0                       ; (ZF clear)
        ret

; PANEL_DRAW: the picture into the page on show, a plane at a time (DS the game's; registers kept)
panel_draw:
        cmp word [cs:panel_seg], 0
        je .none
        pusha
        push ds
        push es
        cld
        inc word [cs:panel_puts]
        mov ax, ds
        sub ax, DGROUP - PAGES_SEG
        mov es, ax
        mov [cs:panel_pseg], ax
        mov ax, [es:SHOWN_PAGE]
        mov [cs:panel_page], ax
        mov ax, [cs:panel_top]
        mov [cs:panel_drawn], ax
        mov ax, [cs:panel_rows]
        mov [cs:panel_drawn_rows], ax
        call panel_staging
        mov ax, 0xA000
        cmp word [es:SHOWN_PAGE], 0
        je .seg
        mov ax, 0xA400
.seg:   call panel_blit
        mov ax, [cs:stage_seg]          ; (and into the screen the pointer is moved on)
        or ax, ax
        jz .done
        mov bl, 0
        xchg bl, [cs:pb_skip]
        push bx
        call panel_blit
        pop bx
        mov [cs:pb_skip], bl
.done:  pop es
        pop ds
        popa
.none:  ret

; PANEL_STAGING: DSCLOG's: in PANEL_DRAW (DS the game's, ES the page routines' segment), the screen the
; game moves its pointer on, when it does so ([3330h] set, the windows [33B6h] shown and [33B8h]
; apart: SL's 3C4Ah, 3CD0h, 3CD2h). STAGE_SEG its segment, or 0; AX, BX not kept.
PTR_STAGING  equ 0x3330
PTR_SHOWN_W  equ 0x33B6
PTR_STAGE_W  equ 0x33B8
WIN_SEGS     equ 4
panel_staging:
        mov word [cs:stage_seg], 0
        cmp word [PTR_STAGING], 0
        je .ret
        mov bx, [PTR_STAGE_W]
        cmp bx, [PTR_SHOWN_W]
        je .ret
        cmp bx, 1
        ja .ret
        shl bx, 1
        mov ax, [es:WIN_SEGS + bx]
        mov bx, 0xA000
        cmp word [es:SHOWN_PAGE], 0
        je .shown
        mov bx, 0xA400
.shown: cmp ax, bx
        je .ret
        cmp ax, 0xA000
        je .blit
        cmp ax, 0xA400
        jne .ret
.blit:  mov [cs:stage_seg], ax
.ret:   ret
stage_seg dw 0

; PANEL_DRAW_POINTER: PANEL_DRAW, then the game's pointer drawn again over it (2D72:0942, SL's
; 28D1:093D). DS the game's; registers kept.
POINTER_SEG  equ 0x2D72
POINTER_ON   equ 0x0942
panel_draw_pointer:
        pusha
        push es
        mov ax, ds
        sub ax, DGROUP - POINTER_SEG
        mov [cs:pointer_far + 2], ax
        mov word [cs:pointer_far], POINTER_ON
        call panel_draw
        mov byte [cs:pointer_busy], 1   ; (the panel just drawn: PROBE_POINTER leaves it)
        call far [cs:pointer_far]
        mov byte [cs:pointer_busy], 0
        pop es
        popa
        ret
pointer_far dw 0, 0
pointer_busy db 0

; PANEL_DRAW_AROUND: PANEL_DRAW with the box the pointer was last drawn in left as it is; if the game
; shows no pointer, PANEL_DRAW. DS the game's; registers kept. (SL's 3C46h, A13Fh, A17Fh)
POINTER_HIDE equ 0x332C
POINTER_XY   equ 0xA10D
POINTER_WAS  equ 0xA115
POINTER_KIND equ 0xA155
POINTER_MOST equ 32
        SHARED_panel_draw_around

; PROBE_POINTER: INT VEC_POINTER replaces "cmp [9Ch],sp" (4 bytes: INT + 2 NOPs; the stack check) in
; the game's routine that draws its pointer (3326Ah, 2D72:0942). The panel is put first if the pointer
; is to go over it. The stack check, with the routine's SP; RETF 2 keeps its flags. DS the game's.
probe_pointer:
        sti
        mov [cs:pointer_ds], ds
        call pp_disarm                  ; (PICK POCKETS: a pick put away once the pointer isn't the talk's)
        call pointer_panel
        push ax
        mov ax, sp
        add ax, 8               ; (the routine's SP: past this push and INT's IP, CS and flags)
        cmp [0x9C], ax
        pop ax
        retf 2

        SHARED_pointer_panel

; POINTER_OVER: ZF set if a pointer at DS:SI (x, y: top left) is over the panel; registers kept
pointer_over:
        push ax
        mov ax, [si]
        cmp ax, PANEL_X0 + PANEL_W
        jge .no
        add ax, POINTER_MOST
        cmp ax, PANEL_X0
        jle .no
        mov ax, [si + 2]
        add ax, POINTER_MOST
        cmp ax, [cs:panel_top]
        jle .no
        sub ax, POINTER_MOST
        sub ax, [cs:panel_top]
        cmp ax, [cs:panel_rows]
        jge .no
        cmp ax, ax
        pop ax
        ret
.no:    cmp sp, 0
        pop ax
        ret

; FLIP_SITE: INT VEC_FLIP replaces "mov ax,0A000h / cmp word [118Eh],0" (16974h; 8 bytes: INT + 6
; NOPs; SL's 14444h) in the game's flip of its two screens (0BF3:5814), the screen to be shown set
; ([118Eh], DS the routine's segment) and the VGA not yet told. If the panel is on the screen on show
; now, it is put on the new one first (FLIP_PUT). Then the two replaced: AX 0A000h, ZF from the compare.
flip_site:
        push bp
        mov bp, sp
        pushad
        push es
        push ds
        cld
        call flip_put
        pop ds
        pop es
        popad
        mov ax, 0xA000
        and word [bp + 6], ~0x40
        cmp word [SHOWN_PAGE], 0
        jne .nz
        or word [bp + 6], 0x40
.nz:    pop bp
        iret

flip_put:
        cmp word [cs:panel_seg], 0
        je .ret
        cmp byte [cs:panel_shown], 0
        je .ret
        call on_map
        jne .ret
        mov ax, [SHOWN_PAGE]
        mov bx, ax
        xor bx, 1
        cmp bx, [cs:panel_page]
        jne .ret
        mov [cs:panel_page], ax
        mov cx, 0xA000
        or ax, ax
        jz .seg
        mov cx, 0xA400
.seg:   mov ax, cx
        mov byte [cs:pb_skip], 0
        call panel_blit
.ret:   ret

; PANEL_BLIT: DSCLOG's: the picture into the screen at segment AX, a plane at a time (AX to DI, DS, ES
; not kept). Its top and height read once, the height kept within the screen.
panel_blit:
        mov es, ax
        mov ax, [cs:panel_top]
        cmp ax, 200
        jae .ret
        mov [cs:pb_top], ax
        mov cx, 200
        sub cx, ax
        mov ax, [cs:panel_rows]
        cmp ax, PANEL_H_MOST
        jbe .most
        mov ax, PANEL_H_MOST
.most:  cmp ax, cx
        jbe .rows
        mov ax, cx
.rows:  or ax, ax
        jz .ret
        mov [cs:pb_rows], ax
        mov ax, [cs:pb_sx0]
        sub ax, PANEL_X0 / 4
        call pb_clamp
        mov [cs:pb_left], ax
        mov ax, [cs:pb_sx1]
        sub ax, PANEL_X0 / 4
        call pb_clamp
        sub ax, [cs:pb_left]
        mov [cs:pb_mid], ax
        push bp
        call vga_save
        mov ds, [cs:panel_seg]
        xor bx, bx                      ; (BX: the plane)
.plane: mov dx, 0x3C4
        mov cl, bl
        mov ah, 1
        shl ah, cl
        mov al, 2
        out dx, ax
        mov ax, [cs:pb_top]
        mov dx, 80
        mul dx
        add ax, PANEL_X0 / 4
        mov di, ax
        mov ax, PANEL_W / 4
        mul bx
        mov si, ax
        add si, FAR_PANEL
        mov dx, [cs:pb_rows]
        mov bp, [cs:pb_top]
.row:   mov cx, PANEL_W / 4
        cmp byte [cs:pb_skip], 0
        je .pix
        cmp bp, [cs:pb_sy0]
        jl .pix
        cmp bp, [cs:pb_sy1]
        jge .pix
        mov cx, [cs:pb_left]
        rep movsb
        mov cx, [cs:pb_mid]
        add di, cx
        add si, cx
        mov cx, PANEL_W / 4
        sub cx, [cs:pb_left]
        sub cx, [cs:pb_mid]
.pix:   shr cx, 1
        rep movsw
        adc cx, cx
        rep movsb
        add di, 80 - PANEL_W / 4
        add si, 3 * PANEL_W / 4
        inc bp
        dec dx
        jnz .row
        inc bx
        cmp bx, 4
        jb .plane
        call vga_restore
        pop bp
.ret:   ret
pb_top  dw 0
pb_rows dw 0
pb_skip db 0
pb_sx0  dw 0
pb_sx1  dw 0
pb_sy0  dw 0
pb_sy1  dw 0
pb_left dw 0
pb_mid  dw 0

pb_clamp:
        cmp ax, 0
        jge .lo
        xor ax, ax
.lo:    cmp ax, PANEL_W / 4
        jle .hi
        mov ax, PANEL_W / 4
.hi:    ret

; INT16: DSCLOG's: the game reads keys through INT 16h; L on the map, the panel on it (or off, to open
; it: L_ON_MAP), counted for the Loader (PANEL_KEYS) and taken out of what the game sees; and, while the
; Loader has TARGET_ON (a party member's turn in a fight), Tab, Shift+Tab and, with an enemy chosen,
; Enter on the map (TARGETING, below)
KEY_L       equ 0x266C
KEY_SHIFT_L equ 0x264C
KEY_TAB     equ 0x0F09
KEY_BACKTAB equ 0x0F00
KEY_ENTER   equ 0x1C0D
KEY_PAD_ENTER equ 0xE00D
old16 dd 0
int16:
        cmp ah, 0x00
        je .read
        cmp ah, 0x10
        je .read
        cmp ah, 0x01
        je .peek
        cmp ah, 0x11
        je .peek
.chain: jmp far [cs:old16]
.peek:  push ax
        pushf
        call far [cs:old16]
        jz .none
        cmp byte [cs:msg_waiting], 0    ; (a key ending a message box's wait: read, not the game's)
        jne .msg
        mov byte [cs:mk_read], 0
        call map_key
        call our_key
        jc .took
        add sp, 2
        push bp
        mov bp, sp
        and word [bp + 6], ~0x40        ; ZF clear
        pop bp
        iret
.took:  pop ax
        push ax
        xor ah, ah
        pushf
        call far [cs:old16]
        pop ax
        jmp .peek
.msg:   xor ah, ah
        pushf
        call far [cs:old16]
        mov byte [cs:msg_ended], 1
.none:  pop ax
        push bp
        mov bp, sp
        or word [bp + 6], 0x40          ; ZF set: no key
        pop bp
        iret
.read:  push ax
.again: pop ax
        push ax
        pushf
        call far [cs:old16]
        mov byte [cs:mk_read], 1
        call map_key
        call our_key
        jc .again
        add sp, 2
        iret

our_key:                                ; AX a key: CF set (and counted) if it is one of ours
        call loot_key                   ; (T and S made Escape: LOOT AND SELL KEYS)
        call sell_key
        call qs_key                     ; (the Loader's quick save and quick load keys: QUICK SAVES)
        jnc .not_qs
        ret
.not_qs:
        cmp ax, KEY_L
        je .l
        cmp ax, KEY_SHIFT_L
        jne .tabs
.l:     call panel_here
        je .count
        call l_on_map
        jne .no
.count: inc word [cs:panel_keys]
        stc
        ret
.tabs:  cmp word [cs:target_on], 0      ; (DSCLOG's TARGETING: the Loader's, on a party member's turn)
        je .no
        call on_map                     ; (not with a window, a menu or a talk over the map)
        jne .no
        call loader_fresh               ; (nor with the Loader gone: TARGET_ON left as it was)
        jne .no
        cmp ax, KEY_TAB
        jne .back
        inc word [cs:tab_seq]
        stc
        ret
.back:  cmp ax, KEY_BACKTAB
        jne .enter
        inc word [cs:back_seq]
        stc
        ret
.enter: cmp word [cs:hit_target], 0xFFFF
        je .no
        cmp ax, KEY_ENTER
        je .go
        cmp ax, KEY_PAD_ENTER
        jne .no
.go:    inc word [cs:attack_seq]
        mov byte [cs:t_click], 1
        stc
        ret
.no:    clc
        ret

; L_ON_MAP: ZF set if L should open the panel: the panel there, not on screen, the map's main loop run
; within the last BIOS tick or two, on the map, and the Loader there; registers kept
l_on_map:
        push ax
        push es
        cmp word [cs:panel_seg], 0
        je .no
        cmp byte [cs:panel_shown], 0
        jne .no
        xor ax, ax
        mov es, ax
        mov ax, [es:0x46C]
        sub ax, [cs:map_tick]
        cmp ax, L_FRESH
        ja .no
        call on_map
        jne .no
        call loader_fresh
        jmp .out
.no:    or ax, 1
.out:   pop es
        pop ax
        ret

align 2




; ---- WALL SHADOWS: SL's shadows on the floor, cast by the sequel's walls ----
; Shattered Lands draws its walls' shadows into its floor tiles; the sequel has none. Here they are
; drawn into the floor as the game draws it, as DSCLOG's SHADOWS draws its figures' (dsclog.asm):
; the game draws a view of the map into a page of its planar (mode X) video memory, first the floor
; (DSUN.EXE 2B81Ch: all of the view, arguments page, camera x, y; 2B97Fh: a rectangle of it, page,
; x0, y0, x1 + 1, y1, camera x, y: SL's 2700Eh and 27162h, the same frames), then the walls and
; things standing on it and the figures. The two floor routines are hooked at their start
; (PROBE_FLOOR: INT + 4 NOPs for "push bp / mov bp,sp / sub sp,N"): their way back becomes
; FLOOR_POST, which darkens the shadows into the floor just drawn, clipped to it.
;
; The walls: the cells GMAP marks (DS:0538h, far, 98 rows of 128 bytes; a wall C0h, the cells
; beside walls and furniture 40h, which no one walks on). As SL's (its slave pens: floor 28,
; shadowed floor 26, the shadow's diagonal edge 70), each wall cell's square is swept a full cell
; along the light, from (0, 0) to (+16, +16) (the light from the upper left): in an open cell, the
; north-west wall's square covers all of it, the west wall's the pixels with x <= y, the north's
; those with x > y: full bands right of and below walls, with 45-degree ends, one span a row. DARK:
; each colour darkened evenly (Lab lightness x 0.73, a and b kept: SL's own tone, a + 11 and b x 0.82,
; read maroon on the sequel's grey cobbles; in the palette's 6-bit values about x 0.74 a channel,
; 51 for a grey 69), then the nearest of WS_FIRST to
; WS_LAST to that (the sequel cycles 1-31: water, flame, a turn's marker; the top, 240-255, is its grey ramp, the street's too), made from
; the palette when it changes (at most once a second, not while the screen is dark: a fade).
WS_FIRST    equ 32
WS_LAST     equ 255
GMAP_PTR    equ 0x0538              ; DS: the region's GMAP, far
FLOOR_ON    equ 0x29EA              ; DS: 0 when the floor routines draw nothing (SL's 2F44h)
DGROUP      equ 0x47E0              ; the game's DS, less its load segment
PAGES_SEG   equ 0x0BF3              ; the page routines' segment (less the load segment): its tables
WS_SPANS_MOST equ 256
WS_LIT      equ 4000                ; (the palette's 768 values add up to less in a fade)
WS_EVERY    equ 18                  ; (BIOS ticks between looks for a new palette to make DARK from)

        SHARED_probe_floor_all
        SHARED_probe_floor_rect
floor_enter:
        pop word [cs:resume]
        pop word [cs:resume + 2]
        popf
        cmp word [cs:wall_shadows], 0
        jne .want
        call fig_wanted                 ; (or the figures' shadows: FIGURE SHADOWS)
        jne .want
        cmp word [cs:dust_on], 0        ; (or the dust: DUST)
        jne .want
        call extras_wanted              ; (or a ring or the squares: RINGS, SQUARES)
        jnc .plain
.want:  cmp byte [cs:floor_busy], 0
        jne .plain
        cmp byte [FLOOR_ON], 0          ; (DS: the game's) the routine draws nothing without it
        je .plain
        mov byte [cs:floor_busy], 1
        push bp
        mov bp, sp
        push ax
        mov ax, [bp+2]                  ; the caller's way back, kept, and FLOOR_POST in its place
        mov [cs:floor_ret], ax
        mov ax, [bp+4]
        mov [cs:floor_ret + 2], ax
        mov word [bp+2], floor_post
        mov [bp+4], cs
        pop ax
        pop bp
.plain: push bp
        mov bp, sp
        sub sp, [cs:floor_frame]
        jmp far [cs:resume]

floor_post:
        pushf
        pushad
        push ds
        push es
        push fs
        mov bp, sp
        call wall_pass
        pop fs
        pop es
        pop ds
        popad
        popf
        mov byte [cs:floor_busy], 0
        jmp far [cs:floor_ret]
F_ARGS equ 40                   ; (FLOOR_POST's frame: FS, ES, DS, PUSHAD, flags, then the arguments)

; PAGE_SETUP: DSCLOG's, the sequel's page table (PAGES_SEG): page BX, its clip and its memory
page_setup:
        mov [cs:game_ds], ds
        mov ax, ds
        sub ax, DGROUP
        add ax, PAGES_SEG
        mov es, ax
        shl bx, 1
        mov ax, [es:bx + 0x404]
        mov [cs:clip_x0], ax
        mov ax, [es:bx + 0x604]
        mov [cs:clip_y0], ax
        mov ax, [es:bx + 0x804]
        mov [cs:clip_x1], ax
        mov ax, [es:bx + 0xA04]
        mov [cs:clip_y1], ax
.parent:
        test word [es:bx + 0xC04], 0x40
        jz .root
        mov bx, [es:bx + 4]
        jmp .parent
.root:  mov ax, [es:bx + 4]
        mov [cs:v_seg], ax
        mov ax, [es:bx + 0x604]
        mov [cs:v_y0], ax
        mov ax, [es:bx + 0x404]
        shr ax, 2
        mov [cs:v_x0], ax
        mov cx, [es:bx + 0x804]
        shr cx, 2
        sub cx, ax
        inc cx
        mov [cs:v_row], cx
        ret

wall_pass:
        cld
        mov bx, [bp + F_ARGS]           ; the page
        call page_setup
        cmp byte [cs:floor_kind], 0
        jne .rect
        mov ax, [bp + F_ARGS + 2]
        mov [cs:cam_x], ax
        mov ax, [bp + F_ARGS + 4]
        mov [cs:cam_y], ax
        jmp .clipped
.rect:  mov ax, [bp + F_ARGS + 10]
        mov [cs:cam_x], ax
        mov ax, [bp + F_ARGS + 12]
        mov [cs:cam_y], ax
        mov ax, [bp + F_ARGS + 2]       ; x0
        cmp ax, [cs:clip_x0]
        jle .rx1
        mov [cs:clip_x0], ax
.rx1:   mov ax, [bp + F_ARGS + 6]       ; x1 + 1
        dec ax
        cmp ax, [cs:clip_x1]
        jge .ry0
        mov [cs:clip_x1], ax
.ry0:   mov ax, [bp + F_ARGS + 4]       ; y0
        cmp ax, [cs:clip_y0]
        jle .ry1
        mov [cs:clip_y0], ax
.ry1:   mov ax, [bp + F_ARGS + 8]       ; y1
        cmp ax, [cs:clip_y1]
        jge .clipped
        mov [cs:clip_y1], ax
.clipped:
        mov fs, [cs:far_seg]
        cmp word [cs:wall_shadows], 0
        je .ring
        call dark_check
        cmp byte [cs:dark_ready], 0
        je .ring
        mov ds, [cs:game_ds]
        cmp dword [GMAP_PTR], 0
        je .ring
        inc word [cs:wall_passes]
        call vga_save
        ; the cells the clip covers: rows (cam_y + clip_y0) / 16 .. (cam_y + clip_y1) / 16
        mov ax, [cs:cam_y]
        add ax, [cs:clip_y0]
        sar ax, 4
        mov [cs:c_r0], ax
        mov ax, [cs:cam_y]
        add ax, [cs:clip_y1]
        sar ax, 4
        mov [cs:c_r1], ax
        mov ax, [cs:cam_x]
        add ax, [cs:clip_x0]
        sar ax, 4
        mov [cs:c_c0], ax
        mov ax, [cs:cam_x]
        add ax, [cs:clip_x1]
        sar ax, 4
        mov [cs:c_c1], ax
        mov si, [cs:c_r0]
.row:   cmp si, [cs:c_r1]
        jg .done
        mov di, [cs:c_c0]
.cell:  cmp di, [cs:c_c1]
        jg .nrow
        mov cx, di
        mov dx, si
        call is_wall                    ; (walls' own cells too, when wholly in shadow: the sequel's
        setc bh                         ;  walk map pads each wall a cell into the room, drawn as
        xor bl, bl                      ;  floor; the wall's art hides the rest)                      ; BL: bit 0 the west is a wall, 1 the north, 2 the north-west
        dec cx
        call is_wall
        adc bl, 0
        inc cx
        dec dx
        call is_wall
        jnc .nn
        or bl, 2
.nn:    dec cx
        call is_wall
        jnc .nnw
        or bl, 4
.nnw:   or bl, bl
        jz .ncell
        or bh, bh
        jz .open
        test bl, 4
        jnz .open
        mov al, bl
        and al, 3
        cmp al, 3
        jne .ncell
.open:
        mov [cs:c_bits], bl
        mov ax, di                      ; the cell's top left on the screen
        shl ax, 4
        sub ax, [cs:cam_x]
        mov [cs:c_sx], ax
        mov ax, si
        shl ax, 4
        sub ax, [cs:cam_y]
        mov [cs:c_sy], ax
        push si
        push di
        xor si, si                      ; SI: the row in the cell, one span a row (WS_SPAN)
.crow:  mov al, [cs:c_bits]
        test al, 4                      ; the north-west wall's square swept: all of the cell
        jnz .full
        and al, 3
        cmp al, 3                       ; the west's and the north's together: all of it too
        je .full
        cmp al, 1
        je .west
        ; the north's alone: x > y (x from y + 1 to 15)
        cmp si, 15
        je .cnext
        lea ax, [si + 1]
        mov cx, 15
        jmp .put
.west:  xor ax, ax                      ; the west's alone: x <= y
        mov cx, si
        jmp .put
.full:  xor ax, ax
        mov cx, 15
.put:   add ax, [cs:c_sx]
        add cx, [cs:c_sx]
        mov dx, ax
        mov di, cx
        mov bx, si
        add bx, [cs:c_sy]
        push si
        call ws_darken
        pop si
.cnext: inc si
        cmp si, 16
        jb .crow
        pop di
        pop si
.ncell: inc di
        jmp .cell
.nrow:  inc si
        jmp .row
.done:  call ws_flush
        call vga_restore
.ring:  call fig_pass                   ; (the figures' shadows: FIGURE SHADOWS)
        call dust_floor                 ; (the puffs of dust: DUST)
        call squares_pass               ; (the squares in reach over the shadows: SQUARES)
        call ring_pass                  ; (the rings over them: RINGS)
        ret

; IS_WALL: CF set if map cell CX (column), DX (row) is a wall (GMAP's C0h bits); DS the game's.
; All registers but flags kept.
is_wall:
        cmp cx, 128
        jae .no
        cmp dx, 98
        jae .no
        push bx
        push es
        les bx, [GMAP_PTR]
        push ax
        mov ax, dx
        shl ax, 7
        add bx, ax
        add bx, cx
        mov al, [es:bx]
        and al, 0xC0
        cmp al, 0xC0
        pop ax
        pop es
        pop bx
        jne .no
        stc
        ret
.no:    clc
        ret

; WS_RECT: the cell's (C_SX, C_SY) pixels AX..CX (x), BX..DX (rows) darkened, within the clip
ws_rect:
        add ax, [cs:c_sx]
        add cx, [cs:c_sx]
        add bx, [cs:c_sy]
        add dx, [cs:c_sy]
        mov [cs:r_x0], ax
        mov [cs:r_x1], cx
        mov [cs:r_y1], dx
.row:   cmp bx, [cs:r_y1]
        jg .ret
        push bx
        mov dx, [cs:r_x0]
        mov di, [cs:r_x1]
        call ws_darken
        pop bx
        inc bx
        jmp .row
.ret:   ret

; WS_DARKEN: DSCLOG's DARKEN: DX..DI on row BX noted (FS: the far block's FAR_SPANS)
ws_darken:
        cmp bx, [cs:clip_y0]
        jl .out
        cmp bx, [cs:clip_y1]
        jg .out
        cmp dx, [cs:clip_x0]
        jge .x1
        mov dx, [cs:clip_x0]
.x1:    cmp di, [cs:clip_x1]
        jle .span
        mov di, [cs:clip_x1]
.span:  cmp dx, di
        jg .out
        cmp word [cs:n_spans], WS_SPANS_MOST
        jb .room
        push dx
        push di
        push bx
        call ws_flush
        pop bx
        pop di
        pop dx
.room:  mov cx, dx
        mov ax, bx
        sub ax, [cs:v_y0]
        mul word [cs:v_row]
        sub ax, [cs:v_x0]
        imul bx, [cs:n_spans], 6
        mov [fs:FAR_SPANS + bx], ax
        mov [fs:FAR_SPANS + bx + 2], cx
        mov [fs:FAR_SPANS + bx + 4], di
        inc word [cs:n_spans]
.out:   ret

; WS_FLUSH: DSCLOG's SPANS_FLUSH: the noted runs darkened through DARK, a plane at a time
ws_flush:
        cmp word [cs:n_spans], 0
        je .ret
        push fs
        push ds
        push bp
        mov fs, [cs:far_seg]
        mov es, [cs:v_seg]
        imul bp, [cs:n_spans], 6
        add bp, FAR_SPANS
        push fs
        pop ds
        mov bx, FAR_DARK
        xor ah, ah
.plane: push ax
        mov cl, ah
        mov ax, 0x0102
        shl ah, cl
        mov dx, 0x3C4
        out dx, ax
        pop ax
        mov al, 4
        mov dx, 0x3CE
        out dx, ax
        mov si, FAR_SPANS
.span:  mov dl, ah
        sub dl, [fs:si + 2]
        and dx, 3
        add dx, [fs:si + 2]
        mov cx, [fs:si + 4]
        sub cx, dx
        jl .nspan
        shr cx, 2
        inc cx
        shr dx, 2
        add dx, [fs:si]
        mov di, dx
.pix:   mov al, [es:di]
        xlatb
        stosb
        loop .pix
.nspan: add si, 6
        cmp si, bp
        jb .span
        inc ah
        cmp ah, 4
        jb .plane
        mov word [cs:n_spans], 0
        pop bp
        pop ds
        pop fs
.ret:   ret

; ---- FIGURE SHADOWS: DSCLOG's SHADOWS (dsclog.asm), the figures' shadows on the sequel's floor ----
; Every living creature on the map (the party, the people, the monsters: a thing of kind 2 in the
; things table, the load + 3F49h:0C33h, 3 bytes a thing, whose creature, DS:19C9h far, 31h bytes, has a
; status at +14h neither dying 4, dead 7 nor gone 8) casts a see-through shadow on the floor, its
; outline laid down toward the lower right as the walls' fall: in the floor pass (FLOOR_POST, after
; the walls' shadows, before the squares and the rings), so the walls and the figures stand on it.
; SL's way: the runs of each row of the frame the figure is drawn with, from the feet up FS_ROWS
; rows, every other row (half as tall), each leaning right by 1.05 times as far as it is up,
; darkened once through the walls' DARK (WS_DARKEN, WS_FLUSH). The sequel draws a thing from the draw
; list (DS:67B7h far, 8 bytes an entry: x, y, height, flags, the thing; DS:264Eh of them) as SL does
; (its 26E96h on, SL's 2492Eh): flags bit 10h not drawn, 20h placed by the entry (x less the map
; thing's byte +7, y less its word +8 and the height: the shadow on the ground leaves the height out),
; else at the map thing's +3, +5; 80h mirrored; the map thing (DS:67BBh, 25h bytes) its flags +0
; (80h not drawn), its picture's slot +10h, the frame +12h. The picture is drawn only from the cache
; (PIC_REUSE's table: the slot's +6 its number, below 0 none; +0Ah the picture in memory, far; +0Eh bit
; 2 in memory), never loaded here (SL's lesson: in the middle of a drawing that can move a picture the
; game is about to draw). The sequel's figures are runs, as SL's (OBJEX.GFF: every picture of 8 frames
; or more); a planar one (FFh "PLNR" or "PLAN" after the size) casts none.
;
; A figure that moves is drawn again within a rectangle round where it was and where it is; its
; shadow reaches beyond its picture, so the two routines drawing rectangles again are made to reach
; further right and down by as far as a shadow does: the redraw of what moved (FIG_WIDE_ALL, site 160
; at 2868Ch, SL's PROBE_REDRAW_ALL) and of a rectangle (FIG_WIDE, site 161 at 2828Ch, SL's
; PROBE_REDRAW). The shadows are drawn only once one of them has run (FIG_SEEN): a copy of the game
; without them (RAV_SKIP=fig_wide_all,fig_wide, a control) has none, rather than shadows left behind.
FS_ROWS     equ 64              ; rows of a figure, up from its feet, that cast a shadow (SL's SHADOW_ROWS)
FS_RIGHT    equ 72              ; how far right a shadow reaches past its figure (SL's SHADOW_RIGHT) ...
FS_DOWN     equ 44              ; ... and down (SL's SHADOW_DOWN)
FS_MOST     equ 255             ; (the widest and tallest a figure that casts one may be: a kept frame's
                                ;   width and bottom row are bytes; 128 till 2026-11-28, when the
                                ;   Tarrasque's widest frames, 134 to 153, cast none, its shadow coming and
                                ;   going as it moved)
FS_LIST     equ 0x67B7          ; DS: the draw list, far ...
FS_COUNT    equ 0x264E          ; ... its entries
FS_THINGS_SEG equ 0x3F49        ; (less the load segment) the things table's segment ...
FS_THINGS   equ 0x0C33          ; ... and offset: kind (2 a creature), its creature (a word)
FS_CREATURES equ 0x19C9         ; DS: the creatures, far, FS_CR_SIZE bytes each
FS_CR_SIZE  equ 0x31
FS_CR_STATUS equ 0x14
FS_CR_MOST  equ 512
FS_LEAN_MOST equ FS_ROWS + (FS_ROWS + 10) / 20

; FIG_WIDE_ALL (site 160): "push word [bp+8] / push di" (4 bytes) where the redraw of what moved, its
; rectangle made (x0 [BP-0Ch], x1 [BP-0Eh], y0 [BP-10h], y1 [BP-12h]: 2863Ch on), starts drawing it
; (the floor's rectangle, 262C:04BF): x1 and y1 further by FS_RIGHT and FS_DOWN, kept on the screen;
; then the two pushes made.
fig_wide_all:
        pop word [cs:fw_ip]
        pop word [cs:fw_cs]
        pop word [cs:fw_fl]
        mov byte [cs:fig_seen], 1
        pusha
        call dust_union                 ; (the puffs' ground taken in: DUST)
        call ghost_union                ; (a figure turned solid or see-through: the whole view)
        popa
        cmp word [cs:fig_shadows], 0
        je .push
        inc word [cs:fig_wides]
        add word [bp - 0x0E], FS_RIGHT
        cmp word [bp - 0x0E], 0x13F     ; (the routine draws to x1 + 1)
        jle .x
        mov word [bp - 0x0E], 0x13F
.x:     add word [bp - 0x12], FS_DOWN
        cmp word [bp - 0x12], 0xC7
        jle .push
        mov word [bp - 0x12], 0xC7
.push:  push word [bp + 8]
        push di
        push word [cs:fw_fl]
        push word [cs:fw_cs]
        push word [cs:fw_ip]
        iret

; FIG_WIDE (site 161): "push bp / mov bp,sp / sub sp,8" (6 bytes) at the start of the routine drawing
; a rectangle of the view again (21E0:128C, 2828Ch; camera x, y, page, x0, y0, x1, y1, a flag; it keeps
; the rectangle on the screen itself): x1 and y1 further by FS_RIGHT and FS_DOWN; then the routine's
; start made, back to it past the site.
fig_wide:
        mov byte [cs:fig_seen], 1
        cmp word [cs:fig_shadows], 0
        je .go
        push bp
        mov bp, sp
        inc word [cs:fig_wides]
        add word [bp + 0x16], FS_RIGHT  ; x1 (after BP, the INT's IP, CS and flags, the caller's
        add word [bp + 0x18], FS_DOWN   ;   way back, camera x, y, the page, x0, y0); y1
        pop bp
.go:    pop word [cs:fw_ip]
        pop word [cs:fw_cs]
        popf
        push bp
        mov bp, sp
        sub sp, 8
        jmp far [cs:fw_ip]
fw_ip   dw 0
fw_cs   dw 0
fw_fl   dw 0
fig_seen db 0                   ; (1 once FIG_WIDE or FIG_WIDE_ALL has run: the shadows wanted)

; FIG_WANTED: ZF clear if the figures' shadows are to be drawn (FIG_SHADOWS, FIG_SEEN); keeps all
fig_wanted:
        cmp word [cs:fig_shadows], 0
        je .ret
        cmp byte [cs:fig_seen], 0
.ret:   ret

; FIG_PASS: (WALL_PASS's, the floor just drawn: PAGE_SETUP's page and clip, CAM_X/CAM_Y the floor
; routine's camera, FS the far block) the shadow of each living creature in the draw list
fig_pass:
        call fig_wanted
        je .ret
        cmp word [cs:wall_shadows], 0   ; (DARK made by the walls' pass: else here)
        jne .made
        call dark_check
.made:  cmp byte [cs:dark_ready], 0
        je .ret
        mov ds, [cs:game_ds]
        cmp dword [FS_LIST], 0
        je .ret
        inc word [cs:fig_passes]
        call vga_save
        les di, [FS_LIST]
        mov cx, [FS_COUNT]
        jcxz .done
.thing: mov bx, [es:di + 6]
        cmp bx, MAP_COUNT - 1           ; (below 0: a thing not made yet, unsigned above)
        ja .next
        test byte [es:di + 5], 0x10
        jnz .next
        push cx
        push di
        push es
        call fig_of
        pop es
        pop di
        pop cx
.next:  add di, 8
        loop .thing
.done:  call vga_restore
.ret:   ret

; FIG_ALIVE: CF set if thing BX is a living creature (FIGURE SHADOWS, above), or a part of one: the map
; thing's word +23h the thing it is part of (FFFFh none; the Tarrasque's front half, thing 252 in its fight,
; +23h 41 its back half, the creature; +21h on the creature names the part), which casts its own shadow
; (2026-11-28: the front half cast none, the back half's lay under the body, the beast standing on no
; shadow). DS the game's; keeps all.
fig_alive:
        push ax
        push si
        push es
        imul si, bx, THING_SIZE
        mov ax, [si + MAP_THINGS + 0x23]
        cmp ax, MAP_COUNT - 1
        jbe .whose
        mov ax, bx
.whose: imul si, ax, 3
        mov ax, ds
        sub ax, DGROUP - FS_THINGS_SEG
        mov es, ax
        cmp byte [es:si + FS_THINGS], 2
        jne .no
        mov ax, [es:si + FS_THINGS + 1]
        cmp ax, FS_CR_MOST
        jae .no
        les si, [FS_CREATURES]
        imul ax, ax, FS_CR_SIZE
        add si, ax
        mov al, [es:si + FS_CR_STATUS]
        cmp al, 4
        je .no
        cmp al, 7
        je .no
        cmp al, 8
        je .no
        stc
        jmp .out
.no:    clc
.out:   pop es
        pop si
        pop ax
        ret

; FIG_OF: the shadow of thing BX, its draw list entry ES:DI (DS the game's, FS the far block)
fig_of:
        call fig_alive
        jnc .no
        imul bx, bx, THING_SIZE
        add bx, MAP_THINGS
        test byte [bx], 0x80
        jnz .no                         ; (not drawn)
        mov si, [bx + 0x10]             ; its picture's slot
        cmp si, CACHE_MOST
        jae .no
        cmp si, [CACHE_LAST]
        jae .no
        mov al, [es:di + 5]
        mov [cs:fg_mirror], al
        test al, 0x20
        jz .fixed
        mov ax, [es:di]
        movzx dx, byte [bx + 7]
        sub ax, dx
        sub ax, [cs:cam_x]
        mov [cs:fg_x], ax
        mov ax, [es:di + 2]
        sub ax, [bx + 8]                ; (its height off the ground left out: the shadow is on it)
        sub ax, [cs:cam_y]
        mov [cs:fg_y], ax
        jmp .frame
.fixed: mov ax, [bx + 3]
        sub ax, [cs:cam_x]
        mov [cs:fg_x], ax
        mov ax, [bx + 5]
        sub ax, [cs:cam_y]
        mov [cs:fg_y], ax
.frame: movzx ax, byte [bx + 0x12]
        mov [cs:fg_frame], ax
        mov ax, [cs:fg_x]               ; (none of its shadow where the floor was drawn: nothing to do)
        cmp ax, [cs:clip_x1]
        jg .no
        add ax, FS_MOST + FS_RIGHT
        cmp ax, [cs:clip_x0]
        jl .no
        mov ax, [cs:fg_y]
        cmp ax, [cs:clip_y1]
        jg .no
        add ax, FS_MOST + FS_DOWN
        cmp ax, [cs:clip_y0]
        jl .no
        call fig_key                    ; (the picture's: its kept shadows' key)
        mov [cs:fk_key], eax
        mov ax, ds                      ; its picture, if in the cache and in memory
        sub ax, CACHE_GAP
        mov es, ax
        shl si, 4
        cmp dword [es:si + CACHE_BASE + 6], 0
        jl .no
        test byte [es:si + CACHE_BASE + 0x0E], 2
        jz .kept                        ; (out of memory: the shadow kept as the game last drew it)
        les si, [es:si + CACHE_BASE + 0x0A]
        mov ax, es
        or ax, si
        jz .no
        mov bx, [cs:fg_frame]
        cmp bx, [es:si + 4]
        jae .no
        shl bx, 2
        xor eax, eax                    ; (EAX: the frame's address, linear)
        mov ax, es
        shl eax, 4
        movzx ecx, si
        add eax, ecx
        add eax, [es:si + bx + 6]
        mov si, ax
        and si, 0x0F
        shr eax, 4
        mov es, ax
        mov ax, [es:si]                 ; the frame: width, height, then its rows
        mov [cs:fg_w], ax
        cmp ax, FS_MOST
        ja .no
        mov ax, [es:si + 2]
        cmp ax, FS_MOST
        ja .no
        dec ax
        js .no
        mov [cs:fg_bottom], ax
        cmp byte [es:si + 4], 0xFF      ; (none, or planar: FFh "PLNR" / "PLAN": the shadow kept as the
        je .kept                        ;   game drew it, PLANAR FIGURES)
        call feet_row                   ; (the feet on its lowest drawn row: FEET_ROW)
        cmp ax, [cs:fg_bottom]
        jae .feet
        mov [cs:fg_bottom], ax
.feet:  call fig_box
        jc .no
        add si, 4
.row:   mov al, [es:si]                 ; a row: its number (FFh: none left), then its runs
        inc si
        cmp al, 0xFF
        je .drawn
        xor ah, ah
        mov dx, [cs:fg_bottom]
        sub dx, ax                      ; DX: how far up from the feet
        jl .skip
        cmp dx, FS_ROWS
        jg .skip
        test dl, 1
        jnz .skip                       ; (every other row: the shadow half as tall)
        mov [cs:fg_up], dx
        shr dx, 1
        add dx, [cs:fg_feet]            ; the screen row it falls on
        cmp dx, [cs:clip_y0]
        jl .skip
        cmp dx, [cs:clip_y1]
        jg .skip
        mov [cs:fg_row], dx
.run:   mov ax, [es:si]                 ; a run: x (8000h: the row's last), its pixels, its bytes
        mov [cs:fg_rx], ax
        mov cl, [es:si + 2]
        mov [cs:fg_rn], cl
        movzx dx, byte [es:si + 3]
        add si, 4
        add si, dx
        mov ax, [cs:fg_up]
        mov bx, [cs:fg_row]
        push es
        push si
        call fig_cast
        pop si
        pop es
        test byte [cs:fg_rx + 1], 0x80
        jz .run
        jmp .row
.skip:  mov al, [es:si + 1]             ; (a row with no shadow: past its runs)
        movzx dx, byte [es:si + 3]
        add si, 4
        add si, dx
        test al, 0x80
        jz .skip
        jmp .row
.drawn: inc word [cs:fig_drawn]
        call ws_flush                   ; (its runs darkened)
.no:    ret
.kept:  mov al, [cs:fg_frame]           ; (FIG_KEEP's: this frame's, else another of the picture's)
        call sc_find
        jnc .found
        inc word [cs:fig_missed]
        ret
.found: mov al, [cs:fg_frame]
        cmp al, [fs:di + 4]
        je .same
        inc word [cs:fig_other]
.same:
        movzx ax, byte [fs:di + 5]
        mov [cs:fg_w], ax
        movzx ax, byte [fs:di + 6]
        mov [cs:fg_bottom], ax
        call fig_box
        jc .no
        movzx cx, byte [fs:di + 7]
        lea si, [di + 8]
.krun:  movzx ax, byte [fs:si]          ; a run: how far up, x, pixels
        mov bx, ax
        shr bx, 1
        add bx, [cs:fg_feet]            ; (the screen row, as above)
        cmp bx, [cs:clip_y0]
        jl .knext
        cmp bx, [cs:clip_y1]
        jg .knext
        movzx dx, byte [fs:si + 1]
        mov [cs:fg_rx], dx
        mov dl, [fs:si + 2]
        mov [cs:fg_rn], dl
        push cx
        push si
        call fig_cast
        pop si
        pop cx
.knext: add si, 3
        loop .krun
        inc word [cs:fig_from_kept]
        jmp .drawn

; FIG_KEY: EAX the key of the picture in cache slot SI (DS the game's): its number (the slot's word +0)
; and the low word of its place in the store (+6), so a slot reused for another picture has another
; key. Keeps the rest.
fig_key:
        push es
        push si
        mov ax, ds
        sub ax, CACHE_GAP
        mov es, ax
        shl si, 4
        mov ax, [es:si + CACHE_BASE + 6]
        shl eax, 16
        mov ax, [es:si + CACHE_BASE]
        pop si
        pop es
        ret

; KEPT SHADOWS (DSCLOG's SHADOW CACHE, SC_SEG, here the far block's FAR_SC): the sequel lets go of a
; picture from memory as soon as it wants the room (the slot's +0Eh bit 2 cleared; a figure's picture
; was out at most floor drawings in Tyr's street), so each frame's shadow is kept as the game draws the
; figure (FIG_KEEP, site 162, where the thing drawer calls the picture routine 1D40:3BEC with the picture
; in memory): SC_SLOTS slots of SC_SLOT bytes, the picture's key (FIG_KEY), the frame, its width, its
; bottom row, how many runs, then the runs that cast a shadow (how far up from the feet, x, pixels: a
; byte each, at most SC_RUNS), filled in turn (the oldest given up). A figure whose picture is out casts
; its frame's kept shadow, or another frame's of the same picture.
SC_RUNS  equ 48
SC_SLOT  equ 8 + 3 * SC_RUNS
SC_SLOTS equ 64
sc_next  dw 0                   ; the slot to fill next
fk_key   dd 0                   ; the picture's key (FIG_KEY)

; SC_FIND: FS:DI the slot with FK_KEY's frame AL, else one with another of its frames; CF if none
; (FS the far block; AX, BX, CX, DX not kept)
sc_find:
        mov ebx, [cs:fk_key]
        mov di, FAR_SC
        mov dx, 0xFFFF
        mov cx, SC_SLOTS
.slot:  cmp byte [fs:di + 7], 0
        je .next
        cmp [fs:di], ebx
        jne .next
        cmp [fs:di + 4], al
        je .hit
        mov dx, di
.next:  add di, SC_SLOT
        loop .slot
        cmp dx, 0xFFFF
        je .none
        mov di, dx
.hit:   clc
        ret
.none:  stc
        ret

; FIG_KEEP (site 162): "call far 1D40:3BEC" (9Ah, ECh, 3Bh, then the segment, which the program's load
; relocates: kept) where the thing drawer draws a thing's picture (2A347h; DI the thing, SI its cache
; slot; the call's arguments the page, x, y, mirrored, the picture (far) and the frame): a living
; creature's frame not kept yet is kept (FIG_RECORD); then the game's routine called as it was, and
; back past the segment.
fig_keep:
        pop word [cs:fk_ip]
        pop word [cs:fk_cs]
        pop word [cs:fk_fl]
        test byte [cs:fk_fl + 1], 2     ; (interrupts on again if the caller had them on: the figures are
        jz .masked                      ;   drawn every frame, as SL's PROBE_GHOST)
        sti
.masked:
        push fs
        push es
        pushad
        mov bp, sp
        call fig_record
        popad
        pop es
        pop fs
        push ds
        push si
        lds si, [cs:fk_ip]
        mov si, [si]                    ; (the routine's segment, as the load relocated it)
        mov [cs:fk_call + 2], si
        pop si
        pop ds
        add word [cs:fk_ip], 2
        call ghost_wanted               ; (a see-through figure: drawn here, SEE-THROUGH FIGURES)
        jnc .game
        call ghost_draw
        jmp .back
.game:  call far [cs:fk_call]
.back:
        push word [cs:fk_fl]
        push word [cs:fk_cs]
        push word [cs:fk_ip]
        iret
fk_ip   dw 0
fk_cs   dw 0
fk_fl   dw 0
fk_call dw 0x3BEC, 0
FK_ARGS equ 36                  ; (FIG_KEEP's frame: PUSHAD, ES, FS, then the call's arguments)

; FIG_RECORD: (FIG_KEEP's, DS the game's, BP its frame) thing DI's frame kept in FAR_SC, if a living
; creature's and not kept already
fig_record:
        cmp word [cs:fig_shadows], 0
        je .ret
        cmp word [cs:far_seg], 0
        je .ret
        cmp di, MAP_COUNT - 1
        ja .ret
        cmp si, CACHE_MOST
        jae .ret
        mov bx, di
        call fig_alive
        jnc .ret
        call fig_key
        mov [cs:fk_key], eax
        mov fs, [cs:far_seg]
        mov al, [bp + FK_ARGS + 12]     ; the frame
        mov [cs:fk_frame], al
        call sc_find
        jc .take
        cmp al, [fs:di + 4]
        je .ret                         ; (kept)
.take:  les si, [bp + FK_ARGS + 8]      ; the picture
        mov ax, es
        or ax, si
        jz .ret
        movzx bx, byte [cs:fk_frame]
        cmp bx, [es:si + 4]
        jae .ret
        shl bx, 2
        xor eax, eax                    ; (the frame's address, linear)
        mov ax, es
        shl eax, 4
        movzx ecx, si
        add eax, ecx
        add eax, [es:si + bx + 6]
        mov si, ax
        and si, 0x0F
        shr eax, 4
        mov es, ax
        mov ax, [es:si]
        cmp ax, FS_MOST
        ja .ret
        mov [cs:fk_w], al
        mov ax, [es:si + 2]
        cmp ax, FS_MOST
        ja .ret
        dec ax
        js .ret
        mov [cs:fk_bottom], al
        mov byte [cs:fk_planar], 0
        cmp byte [es:si + 4], 0xFF      ; (none, or planar)
        jne .runs
        cmp dword [es:si + 5], 'PLNR'   ; (a planar figure, the drakes' and the Tarrasque's: PL_FEET)
        jne .ret
        inc byte [cs:fk_planar]
        mov ax, pl_feet_far
        call pl_call
        cmp ax, 0xFFFF
        je .ret
        mov [cs:fk_bottom], al
        jmp .feet
.runs:  call feet_row                   ; (the feet on its lowest drawn row: FEET_ROW)
        cmp al, [cs:fk_bottom]
        jae .feet
        mov [cs:fk_bottom], al
.feet:
        mov ax, [cs:sc_next]
        inc word [cs:sc_next]
        cmp word [cs:sc_next], SC_SLOTS
        jb .slot
        mov word [cs:sc_next], 0
.slot:  imul di, ax, SC_SLOT
        add di, FAR_SC
        mov byte [fs:di + 7], 0         ; (not to be used till whole)
        mov eax, [cs:fk_key]
        mov [fs:di], eax
        mov al, [cs:fk_frame]
        mov [fs:di + 4], al
        mov al, [cs:fk_w]
        mov [fs:di + 5], al
        mov al, [cs:fk_bottom]
        mov [fs:di + 6], al
        xor cx, cx                      ; CX: the runs kept
        lea bx, [di + 8]
        cmp byte [cs:fk_planar], 0
        je .rows
        mov ax, pl_runs_far             ; (a planar frame's: PL_RUNS)
        call pl_call
        jmp .whole
.rows:  add si, 4
.row:   mov al, [es:si]                 ; a row: its number (FFh: none left), then its runs
        inc si
        cmp al, 0xFF
        je .whole
        xor ah, ah
        movzx dx, byte [cs:fk_bottom]
        sub dx, ax                      ; DX: how far up from the feet
        jl .skip
        cmp dx, FS_ROWS
        jg .skip
        test dl, 1
        jnz .skip
.run:   mov [fs:bx], dl                 ; (past SC_RUNS, round again over the first: the runs nearest
        mov al, [es:si]                 ;   the feet kept, the top of a big figure's shadow given up,
        mov [fs:bx + 1], al             ;   not its foot, which left it floating)
        mov al, [es:si + 2]
        mov [fs:bx + 2], al
        add bx, 3
        inc cx
        lea ax, [di + 8 + 3 * SC_RUNS]
        cmp bx, ax
        jb .past
        lea bx, [di + 8]
.past:  test byte [es:si + 1], 0x80        ; (past the run: its data's bytes)
        pushf
        movzx ax, byte [es:si + 3]
        add si, 4
        add si, ax
        popf
        jz .run
        jmp .row
.skip:  mov al, [es:si + 1]             ; (a row with no shadow: past its runs)
        movzx dx, byte [es:si + 3]
        add si, 4
        add si, dx
        test al, 0x80
        jz .skip
        jmp .row
.whole: cmp cx, SC_RUNS
        jbe .count
        mov cx, SC_RUNS
.count: mov [fs:di + 7], cl
        inc word [cs:fig_kept]
.ret:   ret
fk_frame  db 0
fk_w      db 0
fk_bottom db 0
fk_planar db 0

; PL_CALL: the tail's routine AX run (PLANAR FIGURES, in the tail): GS this segment there, as DSCLOG's
; TAIL_CALL. AX as it leaves it.
pl_call:
        push gs
        push cs
        pop gs
        push cs
        push word .back
        push word [cs:tail_seg]
        push ax
        retf
.back:  pop gs
        ret

section tail
; PLANAR FIGURES: the sequel's biggest creatures (the drakes, the Tarrasque: RESOURCE.GFF's 11001-11007) are
; drawn from planar pictures (FFh "PLNR" after the frame's width and height: the bits a code takes, then a
; colour for each code, then the codes, packed from each byte's top bit: a code not 0 a pixel of its colour;
; 0 then a count: not 0, the last pixel again count + 2 times; 0, a clear one; wotrart.decode_plnr), which
; cast no shadow before 2026-11-28, the drakes seeming to fly over the ground while all else stood on it. Such
; a frame's shadow is kept as it is drawn (FIG_KEEP), as a picture of runs is: PL_FEET finds its feet (the
; lowest row with a pixel not clear), PL_RUNS its rows' runs of pixels from there up, every other row, into
; the slot. A pixel is clear if its colour is 0. The frame is unpacked twice, once per frame kept. The work
; is in the tail (the segment has no room), run through PL_CALL: GS the segment, the tail's own variables CS.

; PL_FEET_FAR, PL_RUNS_FAR: PL_FEET's and PL_RUNS's way in from the segment (PL_CALL).
pl_feet_far:
        call pl_feet
        retf
pl_runs_far:
        call pl_runs
        retf

; PL_START: the codes of planar frame ES:SI read from the first (PL_CODE). AX, CX not kept.
pl_start:
        mov cl, [es:si + 9]
        mov [cs:pl_bits], cl
        mov ax, 1
        shl ax, cl
        dec ax
        mov [cs:pl_mask], ax
        lea ax, [si + 10]
        mov [cs:pl_cols], ax
        add ax, [cs:pl_mask]
        inc ax
        mov [cs:pl_ptr], ax
        mov word [cs:pl_acc], 0
        mov byte [cs:pl_n], 0
        mov byte [cs:pl_last], 0
        ret

; PL_CODE: AX the next code. CX, DX not kept.
pl_code:
        mov cl, [cs:pl_n]
        cmp cl, [cs:pl_bits]
        jae .take
        mov ax, [cs:pl_acc]
        shl ax, 8
        mov dx, si
        mov si, [cs:pl_ptr]
        mov al, [es:si]
        mov si, dx
        inc word [cs:pl_ptr]
        mov [cs:pl_acc], ax
        add byte [cs:pl_n], 8
        jmp pl_code
.take:  sub cl, [cs:pl_bits]
        mov [cs:pl_n], cl
        mov ax, [cs:pl_acc]
        shr ax, cl
        and ax, [cs:pl_mask]
        ret

; PL_SEG: the next pixels, CX of them alike, AL 1 if they are drawn (not clear), else 0. DX not kept.
pl_seg: call pl_code
        or ax, ax
        jz .esc
        mov [cs:pl_last], al
        mov cx, 1
        jmp .drawn
.esc:   call pl_code
        or ax, ax
        jz .clear
        add ax, 2
        mov cx, ax
        mov al, [cs:pl_last]
.drawn: or al, al
        jz .ret
        push bx
        movzx bx, al
        add bx, [cs:pl_cols]
        cmp byte [es:bx], 0
        pop bx
        setne al
.ret:   ret
.clear: mov byte [cs:pl_last], 0
        mov cx, 1
        xor al, al
        ret

; PL_FEET: AX the lowest row planar frame ES:SI draws a pixel on (FFFFh: none). Keeps all but AX.
pl_feet:
        push bx
        push cx
        push dx
        push di
        call pl_start
        mov ax, [es:si]
        mul word [es:si + 2]
        mov [cs:pl_total], ax           ; (its pixels: at most 255 x 255)
        xor bx, bx                      ; BX: the pixels unpacked
        mov di, 0xFFFF                  ; DI: the last drawn one, plus 1
.seg:   cmp bx, [cs:pl_total]
        jae .done
        call pl_seg
        add bx, cx
        cmp bx, [cs:pl_total]
        jbe .in
        mov bx, [cs:pl_total]
.in:    or al, al
        jz .seg
        mov di, bx
        jmp .seg
.done:  mov ax, 0xFFFF
        cmp di, 0xFFFF
        je .out
        lea ax, [di - 1]
        xor dx, dx
        div word [es:si]                ; (its row)
.out:   pop di
        pop dx
        pop cx
        pop bx
        ret

; PL_RUNS: (FIG_RECORD's: ES:SI the planar frame, FK_BOTTOM its feet, FS:DI the slot, FS:BX where its runs go,
; CX 0) the runs of its rows that cast a shadow kept, as FIG_RECORD keeps a picture of runs' (round again past
; SC_RUNS); CX how many. Keeps SI, DI.
pl_runs:
        push si
        call pl_start
        mov [cs:pl_out], bx
        mov word [cs:pl_count], 0
        xor ax, ax
        mov [cs:pl_x], ax
        mov [cs:pl_y], ax
        mov byte [cs:pl_in], 0
        call pl_row
.seg:   call pl_seg
        mov [cs:pl_op], al
.part:  jcxz .seg
        mov ax, [es:si]                 ; M: as many as are left of the row
        sub ax, [cs:pl_x]
        cmp ax, cx
        jbe .m
        mov ax, cx
.m:     sub cx, ax
        mov dx, ax
        cmp byte [cs:pl_op], 0
        je .clear
        cmp byte [cs:pl_up], 0xFF
        je .on
        cmp byte [cs:pl_in], 0
        jne .on
        mov ax, [cs:pl_x]
        mov [cs:pl_rx], ax
        mov byte [cs:pl_in], 1
        jmp .on
.clear: call pl_emit
.on:    add [cs:pl_x], dx
        mov ax, [cs:pl_x]
        cmp ax, [es:si]
        jb .part
        call pl_emit                    ; (the row's end)
        mov word [cs:pl_x], 0
        inc word [cs:pl_y]
        movzx ax, byte [gs:fk_bottom]
        cmp [cs:pl_y], ax
        ja .done
        call pl_row
        jmp .part
.done:  mov bx, [cs:pl_out]
        mov cx, [cs:pl_count]
        pop si
        ret

; PL_ROW: PL_UP how far row PL_Y is up from the feet if it casts a shadow (every other row, FS_ROWS of
; them), else FFh. AX not kept.
pl_row: mov byte [cs:pl_up], 0xFF
        movzx ax, byte [gs:fk_bottom]
        sub ax, [cs:pl_y]
        jl .ret
        cmp ax, FS_ROWS
        jg .ret
        test al, 1
        jnz .ret
        mov [cs:pl_up], al
.ret:   ret

; PL_EMIT: the run from PL_RX to PL_X kept in the slot (FS:DI), if one was going. AX, BX not kept.
pl_emit:
        cmp byte [cs:pl_in], 0
        je .ret
        mov byte [cs:pl_in], 0
        mov bx, [cs:pl_out]
        mov al, [cs:pl_up]
        mov [fs:bx], al
        mov ax, [cs:pl_rx]
        mov [fs:bx + 1], al
        neg al
        add al, [cs:pl_x]
        mov [fs:bx + 2], al
        add bx, 3
        lea ax, [di + 8 + 3 * SC_RUNS]
        cmp bx, ax
        jb .in
        lea bx, [di + 8]
.in:    mov [cs:pl_out], bx
        inc word [cs:pl_count]
.ret:   ret
pl_bits  db 0
pl_n     db 0
pl_last  db 0
pl_op    db 0
pl_in    db 0
pl_up    db 0
pl_mask  dw 0
pl_cols  dw 0
pl_ptr   dw 0
pl_acc   dw 0
pl_total dw 0
pl_x     dw 0
pl_y     dw 0
pl_rx    dw 0
pl_out   dw 0
pl_count dw 0
section image

; FEET_ROW: AX the lowest row frame ES:SI (width, height, then its rows of runs) draws anything on, its last
; (FFFFh: none): the figure's feet, which FIG_OF and FIG_RECORD take when higher than the frame's bottom edge
; (the redrawn figures' frames have a margin all round, ten rows under the party's and up to 22 under the big
; creatures', so their shadows fell that far below them, the figures floating). Keeps the rest.
        SHARED_feet_row

; FIG_BOX: CF set if none of the shadow of the frame (FG_W, FG_BOTTOM) at FG_X, FG_Y can be where the
; floor was drawn (the clip); FG_FEET the feet's row on the screen. Registers kept but AX.
fig_box:
        mov ax, [cs:fg_y]
        add ax, [cs:fg_bottom]
        mov [cs:fg_feet], ax
        cmp ax, [cs:clip_y1]
        jg .out
        add ax, FS_ROWS / 2
        cmp ax, [cs:clip_y0]
        jl .out
        mov ax, [cs:fg_x]
        cmp ax, [cs:clip_x1]
        jg .out
        add ax, [cs:fg_w]
        add ax, FS_LEAN_MOST - 1
        cmp ax, [cs:clip_x0]
        jl .out
        clc
        ret
.out:   stc
        ret

; FIG_CAST: the shadow of the run FG_RX, FG_RN, AX rows up from the feet, on screen row BX: its pixels
; leant right (SL's CAST_RUN) and noted (WS_DARKEN)
fig_cast:
        mov dx, [cs:fg_rx]
        and dx, 0x7FFF
        movzx cx, byte [cs:fg_rn]
        test byte [cs:fg_mirror], 0x80
        jz .lean
        mov di, [cs:fg_w]               ; (drawn mirrored: from the other side)
        sub di, dx
        sub di, cx
        mov dx, di
.lean:  add dx, [cs:fg_x]
        add dx, ax
        mov di, ax
        shr di, 1
        movzx ax, byte [cs:fg_lean + di]
        add dx, ax                      ; DX: its first x
        mov di, dx
        add di, cx
        dec di                          ; DI: its last
        jmp ws_darken

fg_lean:                                ; (AX + 10) / 20 for AX = 0, 2, ... FS_ROWS, by AX / 2
%assign up 0
%rep FS_ROWS / 2 + 1
        db (up + 10) / 20
%assign up up + 2
%endrep
fg_x      dw 0
fg_y      dw 0
fg_w      dw 0
fg_bottom dw 0
fg_feet   dw 0
fg_frame  dw 0
fg_up     dw 0
fg_row    dw 0
fg_rx     dw 0
fg_rn     db 0
fg_mirror db 0

; ---- DUST: DSCLOG's, on the sequel's map ----
; SL's DUST (dsclog.asm), the same code: a walker (FIGURE SHADOWS' casters: a living creature in the draw
; list) raises a puff behind its feet every DUST_STEP pixels (DUST_TICK, from the main loop's PROBE_SCROLL),
; the puffs drawn in the floor pass after the figures' shadows (DUST_PASS), lightening the ground through
; LIGHT (the far block's FAR_LIGHT, which the Loader makes from the palette: dust.light_table, only warm,
; middling colours: sand and dirt, not the street's grey stone), their ground taken into the redraw of
; what moved (DUST_UNION, from FIG_WIDE_ALL, site 160), or drawn again while no one walks (DUST_NUDGE).
; DUST_ON (header +1972) the Loader's: 1 once LIGHT is made. The sequel's own: the draw list's flag 10h
; (not drawn) passes a thing over; its things are MAP_COUNT (321); the walkers' places the draw list's
; x, y as SL's.
DUST_LIFE  equ 18               ; ticks of the BIOS clock (18.2 a second) a puff lasts
DUST_STEP  equ 6                ; pixels walked for each puff
JUMP_MOST  equ 40               ; a move further than this (across or up and down) is a jump, not a walk
DUST_EDGE  equ 16               ; (a walker further than this off the view raises none)
PUFFS      equ 24               ; puffs at most at once
PUFF_SIZE  equ 12               ; a puff: x, y (on the map), born (ticks), owner (thing), seed, live
BIOS_TICKS equ 0x46C

dust_tick:                      ; DS = the game's
        cmp word [cs:dust_on], 0
        jne .on
        ret
.on:    push es
        push bp
        push fs
        mov fs, [cs:far_seg]            ; (FS: the far block, the puffs')
        xor ax, ax
        mov es, ax
        mov ax, [es:BIOS_TICKS]
        mov [cs:d_now], ax
        cmp ax, [cs:d_last]
        je .walk
        mov [cs:d_last], ax
        mov si, FAR_PUFFS                   ; a tick on: each puff looks different, or is gone
        mov cx, PUFFS
.age:   cmp byte [fs:si + 10], 0
        je .anext
        call puff_dirty
        mov ax, [cs:d_now]
        sub ax, [fs:si + 4]
        cmp ax, DUST_LIFE
        jbe .anext
        mov byte [fs:si + 10], 0        ; (drawn once more, gone: now free)
.anext: add si, PUFF_SIZE
        loop .age
.walk:  les di, [FS_LIST]
        mov cx, [FS_COUNT]
        or cx, cx
        jz .done
.thing: mov bx, [es:di + 6]
        cmp bx, MAP_COUNT - 1
        ja .tnext
        test byte [es:di + 5], 0x10     ; (not drawn)
        jnz .tnext
        call fig_alive                  ; (a living creature: FIGURE SHADOWS' casters)
        jnc .tnext
        push cx
        mov [cs:dt_thing], bx
        mov ax, [es:di]
        mov [cs:dt_x], ax
        mov dx, [es:di + 2]
        mov [cs:dt_y], dx
        shl bx, 1
        push fs
        mov fs, [cs:far_seg]
        sub ax, [fs:FAR_LAST_X + bx]
        mov [cs:dt_dx], ax
        sub dx, [fs:FAR_LAST_Y + bx]
        mov [cs:dt_dy], dx
        mov ax, [cs:dt_x]
        mov [fs:FAR_LAST_X + bx], ax
        mov ax, [cs:dt_y]
        mov [fs:FAR_LAST_Y + bx], ax
        mov ax, [cs:dt_dx]               ; walked a little (not a jump: an area loaded, someone placed)
        call abs16
        cmp ax, JUMP_MOST
        jae .tpop
        mov cx, ax
        mov ax, [cs:dt_dy]
        call abs16
        cmp ax, JUMP_MOST
        jae .tpop
        add cx, ax                      ; CX: how far
        jz .tpop
        mov ax, [cs:dt_x]                ; (off the view: no dust, its place noted all the same)
        sub ax, [CAM_X]
        cmp ax, -DUST_EDGE
        jl .tpop
        cmp ax, 319 + DUST_EDGE
        jg .tpop
        mov ax, [cs:dt_y]
        sub ax, [CAM_Y]
        cmp ax, -DUST_EDGE
        jl .tpop
        cmp ax, 199 + DUST_EDGE
        jg .tpop
        mov ax, [cs:d_now]
        mov [cs:d_walked_at], ax
        mov bx, [cs:dt_thing]
        add [fs:FAR_WALKED + bx], cl    ; (FS still the far block)
        cmp byte [fs:FAR_WALKED + bx], DUST_STEP
        jb .tpop
        sub byte [fs:FAR_WALKED + bx], DUST_STEP
        cmp byte [fs:FAR_WALKED + bx], DUST_STEP
        jb .one
        mov byte [fs:FAR_WALKED + bx], 0    ; (one puff a tick at most)
.one:
        call puff_raise
.tpop:  pop fs
        pop cx
.tnext: add di, 8
        dec cx
        jnz .thing
.done:  call dust_nudge
        pop fs
        pop bp
        pop es
        ret

        SHARED_abs16

        SHARED_sgn16

puff_raise:                             ; behind T_THING's feet at (T_X, T_Y), walking (T_DX, T_DY)
        mov ax, [cs:d_next]             ; the next in turn (the oldest, if all are in use)
        inc word [cs:d_next]
        cmp word [cs:d_next], PUFFS
        jb .slot
        mov word [cs:d_next], 0
.slot:  imul si, ax, PUFF_SIZE
        add si, FAR_PUFFS
        cmp byte [fs:si + 10], 0
        je .free
        call puff_dirty                 ; (its ground drawn again without it)
.free:  xor byte [cs:d_side], 1         ; (the feet in turn: a little to one side, then the other)
        mov ax, [cs:dt_dx]
        call sgn16
        mov [cs:dt_sx], ax
        mov ax, [cs:dt_dy]
        call sgn16
        mov [cs:dt_sy], ax
        mov ax, [cs:dt_sx]               ; x: behind, and to the side across the way it goes
        imul ax, ax, -3
        add ax, [cs:dt_x]
        mov dx, [cs:dt_sy]
        shl dx, 1
        cmp byte [cs:d_side], 0
        je .x
        neg dx
.x:     add ax, dx
        mov [fs:si], ax
        mov ax, [cs:dt_sy]               ; y: behind, and to the side
        imul ax, ax, -2
        add ax, [cs:dt_y]
        mov dx, [cs:dt_sx]
        cmp byte [cs:d_side], 0
        jne .y
        neg dx
.y:     add ax, dx
        mov [fs:si + 2], ax
        mov ax, [cs:d_now]
        mov [fs:si + 4], ax
        mov ax, [cs:dt_thing]
        mov [fs:si + 6], ax
        inc word [cs:dust_puffs]
        imul ax, [cs:dust_puffs], 0x3D7
        mov [fs:si + 8], ax
        mov byte [fs:si + 10], 1
        call puff_dirty
        ret

        SHARED_puff_dirty

STILL_TICKS equ 3              ; how long no one has walked (nor the view moved) before DUST_NUDGE
NUDGE_TICKS equ 4               ; ... and between its drawings of the view

; DUST_NUDGE: with puffs to draw again while no one walks and the view stands still (when the
; game draws again round what moved anyway, DUST_UNION taking them in), their ground drawn again
; (D_X0 to D_Y1, as far as it is on screen: REDRAW_RECT) every NUDGE_TICKS, till they are gone
        SHARED_dust_nudge

; DUST_UNION: in FIG_WIDE_ALL (site 160: x0 [BP-0Ch], x1 [BP-0Eh], y0 [BP-10h], y1 [BP-12h]: on screen),
; the puffs' ground taken in, as far as it is on screen
dust_union:
        cmp byte [cs:d_dirty], 0
        je .ret
        mov byte [cs:d_dirty], 0
        mov ax, [cs:d_x0]
        sub ax, [CAM_X]
        mov cx, [cs:d_x1]
        sub cx, [CAM_X]
        mov dx, [cs:d_y0]
        sub dx, [CAM_Y]
        mov bx, [cs:d_y1]
        sub bx, [CAM_Y]
        cmp cx, 0                       ; (off screen: nothing)
        jl .ret
        cmp ax, 0x13F
        jg .ret
        cmp bx, 0
        jl .ret
        cmp dx, 0xC7
        jg .ret
        cmp ax, 0
        jge .ax
        xor ax, ax
.ax:    and ax, 0xFFFC
        cmp ax, [bp-0x0C]
        jge .cx
        mov [bp-0x0C], ax
.cx:    cmp cx, 0x13F
        jle .cx3
        mov cx, 0x13F
.cx3:   or cx, 3
        cmp cx, [bp-0x0E]
        jle .dx
        mov [bp-0x0E], cx
.dx:    cmp dx, 0
        jge .dx0
        xor dx, dx
.dx0:   cmp dx, [bp-0x10]
        jge .bx
        mov [bp-0x10], dx
.bx:    cmp bx, 0xC7
        jle .bx1
        mov bx, 0xC7
.bx1:   cmp bx, [bp-0x12]
        jle .ret
        mov [bp-0x12], bx
.ret:   ret

; DUST_PASS: in SHADOW_PASS (the VGA's registers kept; the clip, camera and page known), each puff
        SHARED_dust_pass

puff_draw:                              ; the puff at FS:SI (the far block)
        mov ax, [cs:d_now]
        sub ax, [fs:si + 4]
        cmp ax, DUST_LIFE
        jb .young
        ret
.young: mov bx, ax                      ; BX: its age
        shl bx, 1
        push word [cs:d_blocks + bx]    ; (its rows' thickness, DUST_BUILD's)
        pop word [cs:d_block]
        shr bx, 1
        shl ax, 3                       ; across: 3, growing to 11
        xor dx, dx
        mov cx, DUST_LIFE
        div cx
        add ax, 3
        mov [cs:d_rx], ax
        imul ax, ax, 9                  ; up and down: a little over half that
        add ax, 8
        shr ax, 4
        mov [cs:d_ry], ax
        imul ax, bx, 5                  ; rising, 5 pixels in all
        xor dx, dx
        div cx
        mov dx, [fs:si + 2]
        sub dx, ax
        mov [cs:d_wy], dx
        mov ax, [fs:si]
        mov [cs:d_wx], ax
        mov ax, [fs:si + 8]
        mov [cs:d_seed], ax
        ; (none of it where the floor was drawn: nothing to do)
        mov ax, [cs:d_wx]
        sub ax, [cs:cam_x]
        mov [cs:d_sx], ax               ; its middle on screen
        mov dx, ax
        sub dx, [cs:d_rx]
        cmp dx, [cs:clip_x1]
        jle .inx
        ret
.inx:   add ax, [cs:d_rx]
        cmp ax, [cs:clip_x0]
        jge .iny
        ret
.iny:   mov ax, [cs:d_wy]
        sub ax, [cs:cam_y]
        mov dx, ax
        sub dx, [cs:d_ry]
        cmp dx, [cs:clip_y1]
        jle .iny1
        ret
.iny1:  add ax, [cs:d_ry]
        cmp ax, [cs:clip_y0]
        jge .cols
        ret
.cols:  mov ax, [cs:clip_x0]            ; the columns within the clip
        sub ax, [cs:d_sx]
        mov dx, [cs:d_rx]
        neg dx
        cmp ax, dx
        jge .from
        mov ax, dx
.from:  mov [cs:d_xfrom], ax
        mov ax, [cs:clip_x1]
        sub ax, [cs:d_sx]
        cmp ax, [cs:d_rx]
        jle .to
        mov ax, [cs:d_rx]
.to:    mov [cs:d_xto], ax
        mov ax, [cs:d_rx]
        inc ax
        shl ax, 2
        mov [cs:d_stride], ax           ; (DUST_BUILD's rows: 2 RX + 2 words)
        mov ax, 11                      ; (and D_THRSYM's x 0 at its +22 whatever RX)
        sub ax, [cs:d_rx]
        shl ax, 1
        add ax, d_thrsym
        mov [cs:d_symat], ax
        mov ax, [cs:d_ry]
        neg ax
        mov [cs:d_yy], ax
        push bp
.row:   mov ax, [cs:d_yy]
        cmp ax, [cs:d_ry]
        jle .inrow
        pop bp
        ret
.inrow: mov bx, [cs:d_wy]
        add bx, ax
        mov [cs:d_wrow], bx
        sub bx, [cs:cam_y]
        cmp bx, [cs:clip_y0]
        jl .nrow
        cmp bx, [cs:clip_y1]
        jg .nrow
        mov ax, bx                      ; the row's place in the page
        sub ax, [cs:v_y0]
        mul word [cs:v_row]
        sub ax, [cs:v_x0]
        mov [cs:d_row_at], ax
        mov ax, [cs:d_yy]               ; for each |x| on this row: how thick (0: outside), and
        or ax, ax                       ;   whether in the core, and the widest |x| inside: the
        jns .absy                       ;   row of DUST_BUILD's table for its age and |y|
        neg ax
.absy:  imul ax, [cs:d_stride]
        add ax, [cs:d_block]
        push ds
        push es
        mov si, ax
        mov ds, [cs:far_seg]
        push cs
        pop es
        lodsw
        mov [cs:d_xmax], ax
        mov di, [cs:d_symat]
        mov cx, [cs:d_rx]
        shl cx, 1
        inc cx
        rep movsw
        pop es
        pop ds
        mov ax, [cs:d_xmax]             ; the row's columns: within the clip and the ellipse
        or ax, ax
        js .nrow
        mov dx, [cs:d_xto]
        cmp dx, ax
        jle .rto
        mov dx, ax
.rto:   mov [cs:d_rto], dx
        neg ax
        mov dx, [cs:d_xfrom]
        cmp dx, ax
        jge .rfrom
        mov dx, ax
.rfrom: mov [cs:d_rfrom], dx
        cmp dx, [cs:d_rto]
        jg .nrow
        mov ax, [cs:d_wrow]             ; the pattern, fixed to the map: the row's part
        imul ax, ax, 0x3B1
        mov [cs:d_rowhash], ax
        mov es, [cs:v_seg]
        mov word [cs:d_plane], 0        ; a plane at a time (the VGA's registers set once for each)
.plane: mov ax, [cs:d_sx]
        add ax, [cs:d_rfrom]
        mov si, [cs:d_plane]
        sub si, ax
        and si, 3
        add si, [cs:d_rfrom]            ; SI: the first column on this plane
        cmp si, [cs:d_rto]
        jg .nplane
        mov cx, [cs:d_plane]
        mov dx, 0x3C4                   ; write to this plane, read from it
        mov al, 2
        mov ah, 1
        shl ah, cl
        out dx, ax
        mov dx, 0x3CE
        mov al, 4
        mov ah, cl
        out dx, ax
        mov di, [cs:d_wx]               ; DI: the column's part of the pattern
        add di, si
        imul di, di, 0x9E5
        mov bp, [cs:d_sx]               ; BP: where it is in the page
        add bp, si
        shr bp, 2
        add bp, [cs:d_row_at]
.px:    mov bx, si
        shl bx, 1
        mov cx, [cs:d_thrsym + 22 + bx] ; CL: how thick, CH: whether in the core
        mov ax, di
        xor ax, [cs:d_rowhash]
        add ax, [cs:d_seed]
        mov dx, ax
        shr dx, 7
        xor ax, dx
        imul ax, ax, 0x2C5
        shr ax, 4
        cmp al, cl
        jae .npx
        xor bh, bh                      ; lightened (twice in the core)
        mov bl, [es:bp]
        mov al, [fs:FAR_LIGHT + bx]     ; (FS: the far block, SHADOW_PASS's)
        or al, al
        jz .npx
        or ch, ch
        jz .put
        mov bl, al
        mov ah, [fs:FAR_LIGHT + bx]
        or ah, ah
        jz .put
        mov al, ah
.put:   mov [es:bp], al
.npx:   add si, 4
        add di, 4 * 0x9E5
        inc bp
        cmp si, [cs:d_rto]
        jle .px
.nplane:
        inc word [cs:d_plane]
        cmp word [cs:d_plane], 4
        jb .plane
.nrow:  inc word [cs:d_yy]
        jmp .row

; DUST_BUILD: the far block's FAR_DUST, once: for each age of a puff, and each row of it from its
; middle out (|y| from 0 to RY), the widest |x| inside and, for each |x| from 0 to RX, how thick the
; dust is there (0: outside the ellipse) and (high byte) whether in its core, as PUFF_DRAW had them
; worked out for each row it drew; D_BLOCKS: where each age's rows start
        SHARED_dust_build
; (the table's size: as DUST_BUILD fills it)
%assign dbytes 0
%assign age 0
%rep DUST_LIFE
%assign drx 3 + age * 8 / DUST_LIFE
%assign dry (drx * 9 + 8) / 16
%assign dbytes dbytes + (dry + 1) * (2 * drx + 2) * 2
%assign age age + 1
%endrep
DUST_BYTES equ dbytes
d_built    db 0
d_blocks   times DUST_LIFE dw 0
d_block    dw 0
d_stride   dw 0
d_symat    dw 0
d_thrsym   times 23 dw 0        ; the row being drawn, by x from -11 to 11 (D_THRCORE's, both ways)

dust_dens  db 255, 255, 255, 255, 247, 238, 229, 219, 209, 198, 187, 174, 161, 147, 132, 114, 93, 66   ; how thick, by age (of 256)
dust_core  db 140, 132, 125, 117, 109, 101, 93, 86, 78, 70, 62, 54, 46, 39, 31, 23, 15, 7   ; the core (twice as light), by age
d_now      dw 0
d_nudged   dw 0
d_cam_x    dw 0
d_cam_y    dw 0
d_owner    dw 0
d_walked_at dw 0                ; when someone last took a step
d_last     dw 0
d_next     dw 0
d_side     db 0
d_dirty    db 0
d_x0       dw 0
d_x1       dw 0
d_y0       dw 0
d_y1       dw 0
d_rx       dw 0
d_ry       dw 0
d_dens     dw 0
d_core     dw 0
d_wx       dw 0
d_wy       dw 0
d_seed     dw 0
d_yy       dw 0
d_wrow     dw 0
d_ey       dw 0
d_sx       dw 0
d_xfrom    dw 0
d_xto      dw 0
d_plane    dw 0
d_extab    times 12 dw 0         ; (x / rx)^2 of 256, by |x| (rx at most 11)
d_thrcore  times 12 dw 0         ; on the row being drawn, by |x|: how thick (0: outside), and
                                ;   (high byte) whether in the core
d_xmax     dw 0
d_rfrom    dw 0
d_rto      dw 0
d_rowhash  dw 0
d_row_at   dw 0
dt_thing    dw 0
dt_x        dw 0
dt_y        dw 0
dt_dx       dw 0
dt_dy       dw 0
dt_sx       dw 0
dt_sy       dw 0

; DUST_FLOOR: (WALL_PASS's, after FIG_PASS) the puffs drawn, the VGA's registers kept
dust_floor:
        cmp word [cs:dust_on], 0
        je .ret
        call vga_save
        call dust_pass
        call vga_restore
.ret:   ret

; (VGA_SAVE, VGA_RESTORE: the labels', above)

; DARK_CHECK: at most every WS_EVERY ticks, the palette read; when it differs from the one DARK was
; made from and isn't a fade's dark, DARK made from it (DSCLOG's BUILD_DARK: the nearest at 3/4,
; keeping the hue). FS: the far block.
dark_check:
        push ds
        xor ax, ax
        mov ds, ax
        mov ax, [0x046C]                ; (BIOS ticks)
        pop ds
        mov dx, ax
        sub dx, [cs:dark_tried]
        cmp byte [cs:dark_ready], 0
        je .look
        cmp dx, WS_EVERY
        jb .ret
.look:  mov [cs:dark_tried], ax
        mov dx, 0x3C7
        xor al, al
        out dx, al
        mov dx, 0x3C9
        mov di, FAR_WS_DAC
        mov cx, 768
        xor ebx, ebx                    ; (EBX: a checksum; SI: how bright in all)
        xor si, si
.read:  in al, dx
        mov [fs:di], al
        movzx eax, al
        add si, ax
        cmp cx, 768 - 1*3               ; (the sum leaves out the cycled colours, 1-31:
        ja .sum                         ;  they change every frame)
        cmp cx, 768 - WS_FIRST*3
        ja .skip
.sum:
        rol ebx, 3
        xor ebx, eax
.skip:  inc di
        loop .read
        cmp si, WS_LIT
        jb .ret                         ; (a fade: kept as it was)
        cmp ebx, [cs:ws_dac_sum]
        jne .make
        cmp byte [cs:dark_ready], 0
        jne .ret
.make:  mov [cs:ws_dac_sum], ebx
        call ws_build
        inc word [cs:dark_builds]
        mov byte [cs:dark_ready], 1
.ret:   ret

ws_build:
        push ds
        push cs
        pop ds
        xor bx, bx
.colour:
        mov si, bx
        imul si, si, 3
        add si, FAR_WS_DAC
        xor di, di
.chan:  movzx ax, byte [fs:si]          ; the shadowed colour: (gain x c + offset) / 256, in 0..63
        inc si
        push bx
        mov bx, di
        shl bx, 1
        imul ax, [cs:ws_gain + bx]
        add ax, [cs:ws_offset + bx]
        pop bx
        sar ax, 8
        jns .pos
        xor ax, ax
.pos:   cmp ax, 63
        jbe .keep
        mov ax, 63
.keep:  mov [want + di], al
        inc di
        cmp di, 3
        jb .chan
        mov si, bx
        imul si, si, 3
        add si, FAR_WS_DAC
        xor ax, ax
        xor dx, dx
        mov di, 3
.own:   mov al, [fs:si]
        inc si
        add dx, ax
        dec di
        jnz .own
        imul dx, dx, 7
        shr dx, 3
        mov [lit_most], dx
        mov dword [best_d], 0xFFFFFFFF
        mov [best_c], bl
        cmp bx, 1                       ; (the cycled colours, 1-31, stay as they are)
        jb .find
        cmp bx, WS_FIRST
        jb .store
.find:
        mov cx, WS_FIRST
.cand:  mov word [lit_sum], 0
        mov si, cx
        imul si, si, 3
        add si, FAR_WS_DAC
        xor di, di
.diff:  mov al, [fs:si]
        inc si
        mov ah, 0
        add [lit_sum], ax
        sub al, [want + di]
        cbw
        mov [diffs + di], al
        inc di
        cmp di, 3
        jb .diff
        mov ax, [lit_sum]
        cmp ax, [lit_most]
        jae .worse
        xor edx, edx
        xor di, di
.sq:    movsx eax, byte [diffs + di]
        imul eax, eax
        add edx, eax
        inc di
        cmp di, 3
        jb .sq
        movsx eax, byte [diffs]
        movsx edi, byte [diffs + 1]
        sub eax, edi
        imul eax, eax
        shl eax, 2
        add edx, eax
        movsx eax, byte [diffs + 1]
        movsx edi, byte [diffs + 2]
        sub eax, edi
        imul eax, eax
        shl eax, 2
        add edx, eax
        cmp edx, [best_d]
        jae .worse
        mov [best_d], edx
        mov [best_c], cl
.worse: inc cx
        cmp cx, WS_LAST
        jbe .cand
.store: mov al, [best_c]
        mov [fs:FAR_DARK + bx], al
        inc bx
        cmp bx, 256
        jb .colour
        pop ds
        ret

ws_gain    dw 189, 189, 189          ; (lightness x 0.73, x 256: red, green, blue; SL's warm
ws_offset  dw 0, 0, 0                 ;  tone was 187, 180, 188 and 1393, -469, -72)
resume     dd 0
floor_ret  dd 0
floor_frame dw 0
floor_kind db 0
floor_busy db 0
game_ds    dw 0
clip_x0    dw 0
clip_y0    dw 0
clip_x1    dw 0
clip_y1    dw 0
v_seg      dw 0
v_y0       dw 0
v_x0       dw 0
v_row      dw 0
cam_x      dw 0
cam_y      dw 0
c_r0       dw 0
c_r1       dw 0
c_c0       dw 0
c_c1       dw 0
c_sx       dw 0
c_sy       dw 0
c_bits     db 0
r_x0       dw 0
r_x1       dw 0
r_y1       dw 0
n_spans    dw 0
dark_ready db 0
dark_tried dw 0
ws_dac_sum    dd 0
want       db 0, 0, 0
diffs      db 0, 0, 0
lit_most   dw 0
lit_sum    dw 0
best_d     dd 0
best_c     db 0

; ---- TARGETING and RINGS: choosing an enemy with Tab, Enter attacking it, a red ring under it ----
; DSCLOG's (dsclog.asm: TARGETING, PROBE_HIT, RINGS), on the sequel. While the Loader has TARGET_ON (a
; party member's turn in a fight), INT16 takes Tab and Shift+Tab from the game and counts them; the
; Loader steps through the enemies, the nearest first, and puts the chosen one in HIT_TARGET
; (dsloader/targeting.py). Enter then (INT16: T_CLICK) has the main loop's next pass (TARGET_MOUSE, from
; PROBE_SCROLL) put the pointer a little above the enemy's feet and give the game's own mouse handler a
; left click there. For HIT_PASSES passes
; from it the routine finding what is under the pointer (29DBDh, SL's 25B52h: PROBE_HIT, site 77)
; answers with the chosen enemy whatever stands in front of it. The ring (RINGS_ON) is drawn into the
; floor as the game draws it (FLOOR_POST, after the walls' shadows), the floor's colours reddened
; three times through RED (the Loader's, from the palette: rings.red_table); RING_TICK draws the view
; again where it was and where it is when the chosen enemy changes or walks.
HIT_PASSES  equ 600             ; passes of the main loop the finder answers with the chosen enemy, from
                                ;   the click (SL's: the walk to it never stalls on a figure in front)
T_ABOVE     equ 8               ; (the click a little above the feet, on the figure)
RING_W      equ 16              ; (the ring's room round the feet, drawn again when it moves: wide ...
RING_H      equ 9               ;   ... and high)
hit_until  dw 0
hit_forced db 0
t_click    db 0                 ; (INT16's: Enter pressed on the chosen enemy)
t_x        dw 0
t_y        dw 0
h_resume   dd 0

; TARGET_MOUSE: after PANEL_MOUSE (DS the game's): Enter's click (T_CLICK): the pointer put a little
; above the chosen enemy's feet (INT 33h 4) and the game's own mouse handler called there with a left
; press and a letting go, as the mouse driver calls it (the game reads clicks from the handler it set
; with INT 33h 0Ch, not from its main loop's call for the pointer: that handler found by INT 33h 14h,
; given back at once). Registers kept.
EVENT_LEFT_PRESS equ 2
EVENT_LEFT_LEAVE equ 4
target_mouse:
        cmp byte [cs:t_click], 0
        je .ret
        mov byte [cs:t_click], 0
        pusha
        push ds
        push es
        mov ds, [cs:pointer_ds]
        mov bx, [cs:hit_target]
        cmp bx, MAP_COUNT - 1
        ja .out
        call on_map
        jne .out
        imul bx, bx, THING_SIZE
        mov cx, [bx + MAP_THINGS + THING_X]
        mov dx, [bx + MAP_THINGS + THING_Y]
        sub cx, [CAM_X]
        sub dx, [CAM_Y]
        sub dx, T_ABOVE
        cmp cx, 1                       ; (on the screen: else nothing, as SL's)
        jl .out
        cmp cx, 318
        jg .out
        cmp dx, 1
        jl .out
        cmp dx, 198
        jg .out
        mov [cs:t_x], cx
        mov [cs:t_y], dx
        mov ax, 0x14                    ; the game's handler: swapped for none, then given back
        xor cx, cx
        push cs
        pop es
        mov dx, t_none
        int 0x33
        mov [cs:t_handler], dx
        mov [cs:t_handler + 2], es
        mov [cs:t_mask], cx
        mov ax, 0x14
        int 0x33                        ; (CX, ES:DX: the game's again)
        cmp word [cs:t_handler + 2], 0
        je .out
        mov ax, [cs:main_ticks]
        add ax, HIT_PASSES
        mov [cs:hit_until], ax
        mov byte [cs:hit_forced], 1
        inc word [cs:attack_clicks]
        mov ax, 4                       ; the pointer there
        mov cx, [cs:t_x]
        mov dx, [cs:t_y]
        int 0x33
        pushf                           ; (the handler as the driver calls it: interrupts off)
        cli
        mov ax, EVENT_LEFT_PRESS
        mov bx, 1
        call t_event
        mov ax, EVENT_LEFT_LEAVE
        xor bx, bx
        call t_event
        popf
.out:   pop es
        pop ds
        popa
.ret:   ret
t_event:                                ; the game's handler called with event AX, buttons BX at T_X, T_Y
        pusha
        push ds
        push es
        mov cx, [cs:t_x]
        mov dx, [cs:t_y]
        xor si, si
        xor di, di
        call far [cs:t_handler]
        pop es
        pop ds
        popa
        ret
t_none: retf                            ; (the handler for the moment of the swap)
t_handler dd 0
t_mask    dw 0

; PAN_TICK: (PROBE_SCROLL's, DS the game's) DSCLOG's PAN: the Loader adds to PAN_X and PAN_Y (wrapping)
; the pixels the view is to scroll by (targeting.py: to the enemy chosen with Tab, when it is off the
; screen, so Enter's click has it to click on), and the next pass on the map moves the view by what was
; added since the last (PAN_X_DONE, PAN_Y_DONE) through the game's own routine centring it (1C5F:01F3,
; VIEW_AGAIN's CENTRE: it keeps the view inside the map's limits, DS:14D7h to 14DDh, and draws it again;
; PROBE_CENTRE then draws the panel's view again too). Off the map what was added is dropped; while a
; label or the ring is being drawn it waits a pass. Keeps all.
pan_tick:
        pusha
        mov ax, [cs:pan_x]
        sub ax, [cs:pan_x_done]
        mov si, [cs:pan_y]
        sub si, [cs:pan_y_done]
        mov di, ax
        or di, si
        jz .out
        call on_map
        jne .drop
        cmp byte [cs:lbl_busy], 0
        jne .out
        cmp byte [cs:vga_busy], 0
        jne .out
        add [cs:pan_x_done], ax
        add [cs:pan_y_done], si
        add ax, [CAM_X]
        add si, [CAM_Y]
        and ax, 0xFFF8                  ; (as the game keeps it)
        and si, 0xFFF8
        cmp ax, [CAM_X]
        jne .go
        cmp si, [CAM_Y]
        je .out
.go:    mov bx, ds
        sub bx, DGROUP - CENTRE_SEG
        mov [cs:centre + 2], bx
        pushf
        cli                             ; (drawing)
        push word 1
        add si, 100
        push si
        add ax, 160
        push ax
        call far [cs:centre]
        add sp, 6
        popf
        inc word [cs:pan_moves]
        jmp .out
.drop:  add [cs:pan_x_done], ax
        add [cs:pan_y_done], si
.out:   popa
        ret
pan_x_done dw 0
pan_y_done dw 0
pan_moves  dw 0                 ; (the view moved by PAN, counted: ravtab.py)

; PROBE_HIT (site 77): "push bp / mov bp,sp / sub sp,0Eh" (6 bytes: the site and 3 NOPs) at the start of
; the routine that finds the thing under the pointer (29DBDh: camera x, y, pointer x, y; the thing, or
; FFFFh): for HIT_PASSES passes after TARGET_MOUSE's click, the chosen enemy, wherever the pointer is.
probe_hit:
        pop word [cs:h_resume]
        pop word [cs:h_resume + 2]
        popf
        cmp byte [cs:hit_forced], 0
        je .plain
        cmp word [cs:hit_target], 0xFFFF
        je .over                        ; (none chosen any more: a new turn, the click done)
        push ax
        mov ax, [cs:main_ticks]
        sub ax, [cs:hit_until]
        pop ax
        jns .over
        inc word [cs:hit_answers]
        mov ax, [cs:hit_target]
        retf                            ; (back to the finder's caller, the enemy its answer)
.over:  mov byte [cs:hit_forced], 0
.plain: push bp
        mov bp, sp
        sub sp, 0x0E
        jmp far [cs:h_resume]

; RING_WANTED: CF set if a ring is to be drawn: RINGS_ON, an enemy chosen and the Loader there.
; Registers kept.
ring_wanted:
        cmp word [cs:rings_on], 0
        je .no
        cmp word [cs:hit_target], MAP_COUNT - 1
        ja .no
        call loader_fresh               ; (the Loader gone: none, HIT_TARGET left as it was)
        jne .no
        stc
        ret
.no:    clc
        ret

; RING_TICK: (PROBE_SCROLL's, DS the game's) on the map, when the ring to show isn't the one drawn (the
; chosen enemy changed or walked, the rings switched): the view drawn again round where it was and
; where it is now (RING_REDRAW), the floor pass drawing the new one. Keeps all.
ring_tick:
        pusha
        mov bx, 0xFFFF
        call ring_wanted
        jnc .which
        mov bx, [cs:hit_target]
.which: xor cx, cx
        xor dx, dx
        cmp bx, 0xFFFF
        je .same
        mov si, bx
        imul si, si, THING_SIZE
        mov cx, [si + MAP_THINGS + THING_X]
        mov dx, [si + MAP_THINGS + THING_Y]
.same:  cmp bx, [cs:r_thing]
        jne .moved
        cmp cx, [cs:r_mx]
        jne .moved
        cmp dx, [cs:r_my]
        je .out
.moved: call on_map
        jne .out
        cmp byte [cs:lbl_busy], 0
        jne .out
        cmp byte [cs:vga_busy], 0
        jne .out
        push bx
        push cx
        push dx
        cmp word [cs:r_thing], 0xFFFF
        je .new
        mov cx, [cs:r_mx]
        mov dx, [cs:r_my]
        call ring_redraw
.new:   pop dx
        pop cx
        pop bx
        mov [cs:r_thing], bx
        mov [cs:r_mx], cx
        mov [cs:r_my], dx
        cmp bx, 0xFFFF
        je .out
        call ring_redraw
.out:   popa
        ret
r_thing dw 0xFFFF               ; (the ring last drawn: its thing and its feet on the map)
r_mx    dw 0
r_my    dw 0

; RING_REDRAW: the view drawn again (the game's routine for a rectangle of it, as LABEL_ERASE) round
; map point CX, DX (a ring's feet). Nothing when it is off the screen. DS the game's; keeps all.
ring_redraw:
        pusha
        push es
        mov byte [cs:lbl_busy], 1
        sub cx, [CAM_X]
        sub dx, [CAM_Y]
        mov ax, cx
        sub ax, RING_W
        add cx, RING_W
        mov bx, dx
        sub bx, RING_H
        add dx, RING_H
        cmp cx, 0
        jl .out
        cmp dx, 0
        jl .out
        cmp ax, 319
        jg .out
        cmp bx, 199
        jg .out
        or ax, ax
        jge .x1
        xor ax, ax
.x1:    or bx, bx
        jge .x2
        xor bx, bx
.x2:    or cx, 3
        cmp cx, 319
        jle .y1
        mov cx, 319
.y1:    cmp dx, 199
        jle .go
        mov dx, 199
.go:    and ax, ~3
        push ax
        mov ax, ds
        sub ax, DGROUP - REDRAW_SEG
        mov [cs:redraw_far + 2], ax
        pop ax
        push word 1                     ; (the flip)
        push dx
        push cx
        push bx
        push ax
        push word 1                     ; (the page)
        push word [CAM_Y]
        push word [CAM_X]
        call far [cs:redraw_far]
        add sp, 16
.out:   mov byte [cs:lbl_busy], 0
        pop es
        popa
        ret

; RING_PASS: (WALL_PASS's, the floor just drawn: PAGE_SETUP's page and clip, CAM_X/CAM_Y the floor
; routine's camera, FS the far block) the chosen enemy's ring round its feet, three rings of points
; (DSCLOG's RING_OUTER, RING_INNER, RING_EXTRA), each pixel reddened three times through RED; then a
; ring under each thing RING_TAB marks (DSCLOG's: kind 1 two rings of points, tinted twice through RED,
; which the Loader makes golden for them: usable.py), with RINGS_ON and the Loader there.
ring_pass:
        cmp word [cs:rings_on], 0
        je .ret
        call loader_fresh
        jne .ret
        call vga_save
        mov es, [cs:v_seg]
        mov word [cs:r_tab], FAR_RED
        mov bx, [cs:hit_target]
        cmp bx, MAP_COUNT - 1
        ja .marks
        mov word [cs:r_times], 3
        mov al, 2
        call ring_at
        jnc .marks
        inc word [cs:ring_draws]
.marks: mov word [cs:r_times], 2
        xor bx, bx
.mark:  cmp byte [fs:FAR_RING_TAB + bx], 0
        jne .one
.mnext: inc bx
        cmp bx, MAP_COUNT
        jb .mark
        call vga_restore
.ret:   ret
.one:   push bx
        mov al, [fs:FAR_RING_TAB + bx]
        call ring_at
        jnc .unseen
        inc word [cs:mark_draws]
.unseen:
        pop bx
        jmp .mnext

; RING_AT: a ring of kind AL (1: outer and inner, 2: the extra too) round thing BX's feet, unless wholly
; outside the clip (CF clear then; set when drawn). ES the page; R_TAB and R_TIMES the tint.
ring_at:
        mov [cs:r_kind], al
        push ds
        mov ds, [cs:game_ds]
        imul bx, bx, THING_SIZE
        mov ax, [bx + MAP_THINGS + THING_X]
        sub ax, [cs:cam_x]
        mov [cs:r_fx], ax
        mov ax, [bx + MAP_THINGS + THING_Y]
        sub ax, [cs:cam_y]
        mov [cs:r_fy], ax
        pop ds
        mov ax, [cs:r_fx]               ; (wholly outside the clip: nothing)
        add ax, RING_W
        cmp ax, [cs:clip_x0]
        jl .no
        sub ax, 2 * RING_W
        cmp ax, [cs:clip_x1]
        jg .no
        mov ax, [cs:r_fy]
        add ax, RING_H
        cmp ax, [cs:clip_y0]
        jl .no
        sub ax, 2 * RING_H
        cmp ax, [cs:clip_y1]
        jg .no
        mov si, ring_outer
        mov cx, RING_OUTER
        call ring_points
        mov si, ring_inner
        mov cx, RING_INNER
        call ring_points
        cmp byte [cs:r_kind], 2
        jb .done
        mov si, ring_extra
        mov cx, RING_EXTRA
        call ring_points
.done:  stc
        ret
.no:    clc
        ret

        SHARED_ring_points

ring_dot:                               ; the point (R_QX, R_QY) round (R_FX, R_FY) reddened, if in
        mov bx, [cs:r_qx]               ;   the clip; SI kept
        add bx, [cs:r_fx]
        mov ax, [cs:r_qy]
        add ax, [cs:r_fy]
        cmp ax, [cs:clip_y0]
        jl .skip
        cmp ax, [cs:clip_y1]
        jg .skip
        cmp bx, [cs:clip_x0]
        jl .skip
        cmp bx, [cs:clip_x1]
        jg .skip
        sub ax, [cs:v_y0]               ; the row's place in the page
        mul word [cs:v_row]
        sub ax, [cs:v_x0]
        mov di, ax
        mov cx, bx                      ; the pixel's plane, read and written
        and cx, 3
        mov dx, 0x3C4
        mov al, 2
        mov ah, 1
        shl ah, cl
        out dx, ax
        mov dx, 0x3CE
        mov al, 4
        mov ah, cl
        out dx, ax
        shr bx, 2
        add di, bx
        movzx bx, byte [es:di]          ; its colour, tinted R_TIMES times through R_TAB (as far as
        push si                         ;   it goes: RED, or SQUARES' LIGHT)
        mov si, [cs:r_tab]
        mov cx, [cs:r_times]
.again: mov al, [fs:si + bx]
        or al, al
        jz .none
        mov bl, al
        loop .again
        jmp .put
.none:  cmp cx, [cs:r_times]            ; no colour that way. At the first look, where LIGHT has
        jne .put                        ;   none (a colour that isn't the ground's: stone), the
        cmp si, FAR_LIGHT               ;   mark is darkened through the walls' shadows' DARK
        jne .put                        ;   instead, as many times (DSCLOG's RING_PX)
        mov si, FAR_DARK
        jmp .again
.put:   mov [es:di], bl
        pop si
.skip:  ret

RING_OUTER equ 20                ; (a quarter of each ring, DSCLOG's: RING_POINTS mirrors them)
RING_INNER equ 18
RING_EXTRA equ 22
ring_outer db 0 << 3 | 6, 1 << 3 | 6, 2 << 3 | 6, 3 << 3 | 6, 4 << 3 | 6, 5 << 3 | 5, 5 << 3 | 6, 6 << 3 | 5, 7 << 3 | 5, 8 << 3 | 5, 9 << 3 | 4, 9 << 3 | 5, 10 << 3 | 4, 11 << 3 | 3, 11 << 3 | 4, 12 << 3 | 2, 12 << 3 | 3, 13 << 3 | 0, 13 << 3 | 1, 13 << 3 | 2
ring_inner db 0 << 3 | 5, 1 << 3 | 5, 2 << 3 | 5, 3 << 3 | 5, 4 << 3 | 5, 5 << 3 | 4, 5 << 3 | 5, 6 << 3 | 4, 7 << 3 | 4, 8 << 3 | 4, 9 << 3 | 3, 9 << 3 | 4, 10 << 3 | 2, 10 << 3 | 3, 11 << 3 | 1, 11 << 3 | 2, 12 << 3 | 0, 12 << 3 | 1
ring_extra db 0 << 3 | 7, 1 << 3 | 7, 2 << 3 | 7, 3 << 3 | 7, 4 << 3 | 7, 5 << 3 | 6, 5 << 3 | 7, 6 << 3 | 6, 7 << 3 | 6, 8 << 3 | 6, 9 << 3 | 5, 9 << 3 | 6, 10 << 3 | 5, 11 << 3 | 4, 11 << 3 | 5, 12 << 3 | 3, 12 << 3 | 4, 13 << 3 | 2, 13 << 3 | 3, 14 << 3 | 0, 14 << 3 | 1, 14 << 3 | 2
r_fx       dw 0
r_fy       dw 0
r_qx       dw 0
r_qy       dw 0
r_kind     db 0
r_tab      dw FAR_RED           ; (the far block's table RING_DOT tints a colour through ...
r_times    dw 3                 ;   ... and how many times)

; EXTRAS_WANTED: CF set if the floor pass has something of the Loader's to draw: the chosen enemy's ring
; (RING_WANTED), the rings RING_TAB marks (RINGS_ON) or the squares in reach (SQUARES_ON), the Loader
; there. Registers kept.
extras_wanted:
        call ring_wanted
        jc .ret
        cmp word [cs:rings_on], 0
        jne .fresh
        cmp word [cs:squares_on], 0
        je .no
.fresh: call loader_fresh
        jne .no
        stc
.ret:   ret
.no:    clc
        ret

; SQUARES (SQUARES_ON): DSCLOG's, a small light cross (two pixels each way) on the floor in the middle
; of each of the walk map's squares the Loader marks in SQ_MAP (where the party member whose turn it is
; in a fight can still walk, squares.py), drawn in the floor pass after the walls' shadows and before
; the rings, by the rings' routines (RING_POINTS, RING_DOT), the ground lightened four times through
; LIGHT (the dust's table in Shattered Lands: dust.light_table, made by the Loader from the palette)
; and what isn't ground (a stone floor) darkened four times through the walls' shadows' DARK. SQ_MAP is
; the Loader's: the column and the row (a byte each) of the walk map's square its first bit is for, then
; SQ_SIDE rows of SQ_SIDE bits, the leftmost square a row's bit 0. It lies in this helper's own PSP (CS -
; 10h), in the room DOS keeps there for a program's two FCBs and its command line (5Ch to FFh): kept
; with the helper, of no use to DOS once it has stayed resident, so the map costs no upper memory.
SQ_SIDE    equ 32               ; SQ_MAP: its origin's column and row, then SQ_SIDE x SQ_SIDE bits
SQ_MAP     equ 0x5C             ; ... its offset in the PSP (squares.py's SQ_MAP_PSP)
SQ_MAP_BYTES equ 2 + SQ_SIDE * SQ_SIDE / 8
        times -(SQ_MAP + SQ_MAP_BYTES > 0x100) db 0 ; (a negative count: past the PSP's end)
SQ_REACH   equ 2                ; how far the cross reaches from the square's middle
SQ_DOTS    equ 5                ; (a quarter of the cross, as the rings': RING_POINTS mirrors it)
sq_dots    db 0 << 3 | 0, 1 << 3 | 0, 2 << 3 | 0, 0 << 3 | 1, 0 << 3 | 2
squares_pass:
        cmp word [cs:squares_on], 0
        je .ret
        call loader_fresh
        jne .ret
        inc word [cs:square_draws]
        call vga_save
        mov es, [cs:v_seg]
        mov word [cs:r_tab], FAR_LIGHT
        mov word [cs:r_times], 4
        push ds
        mov ax, cs
        sub ax, 0x10
        mov ds, ax                      ; (the PSP)
        xor di, di                      ; the row
.row:   movzx ax, byte [SQ_MAP + 1]
        add ax, di
        shl ax, 4
        add ax, 8
        sub ax, [cs:cam_y]              ; its squares' middle, on the screen
        mov [cs:r_fy], ax
        add ax, SQ_REACH
        cmp ax, [cs:clip_y0]            ; (a row or a square whose cross is all outside what is
        jl .rnext                       ;   being drawn is passed over: a walker's rectangle is
        sub ax, 2 * SQ_REACH            ;   small, and RING_DOT would test every pixel)
        cmp ax, [cs:clip_y1]
        jg .rnext
        mov bx, di
        shl bx, 2
        mov edx, [bx + SQ_MAP + 2]      ; the row's bits
        movzx si, byte [SQ_MAP]
        shl si, 4
        add si, 8
        sub si, [cs:cam_x]              ; the middle of the row's first square
.col:   shr edx, 1
        jnc .next
        lea ax, [si + SQ_REACH]
        cmp ax, [cs:clip_x0]
        jl .next
        lea ax, [si - SQ_REACH]
        cmp ax, [cs:clip_x1]
        jg .next
        mov [cs:r_fx], si
        push edx
        push si
        push di
        mov si, sq_dots
        mov cx, SQ_DOTS
        call ring_points
        pop di
        pop si
        pop edx
.next:  add si, 16
        or edx, edx
        jnz .col
.rnext: inc di
        cmp di, SQ_SIDE
        jb .row
        pop ds
        mov word [cs:r_tab], FAR_RED
        call vga_restore
.ret:   ret

; REDRAW_TICK: (PROBE_SCROLL's, DS the game's) on the map, the view drawn again, all of it (VIEW_AGAIN),
; when the Loader asks (VIEW_REDRAW: its squares or rings changed) or the squares or RING_TAB's rings
; come or go by the Loader's coming or going (its LOADER_FRESH stamp), so none are left drawn; while a
; label or a ring is being drawn it waits a pass. Keeps all.
redraw_tick:
        pusha
        xor al, al
        call loader_fresh
        jne .state
        cmp word [cs:squares_on], 0
        je .rings
        or al, 1
.rings: cmp word [cs:rings_on], 0
        je .state
        or al, 2
.state: cmp word [cs:view_redraw], 0
        jne .go
        cmp al, [cs:x_state]
        je .out
.go:    call on_map
        jne .drop
        cmp byte [cs:lbl_busy], 0
        jne .out
        cmp byte [cs:vga_busy], 0
        jne .out
        mov [cs:x_state], al
        mov word [cs:view_redraw], 0
        pushf
        cli                             ; (drawing)
        call view_again
        popf
        inc word [cs:x_redraws]
        jmp .out
.drop:  mov [cs:x_state], al            ; (off the map: its next drawing is whole)
        mov word [cs:view_redraw], 0
.out:   popa
        ret
x_state    db 0
x_redraws  dw 0                 ; (the view drawn again so, counted)

; F10_PIN (site 100, SITE_F10_PIN): DSCLOG's, "mov ah,0 / or ax,ax / jz 1EC3Fh" (1EC36h; 6 bytes: the
; INT, the site's number and 3 NOPs), the F10 key's last test (1EC05h, SL's 1B83Ah, with a fight on and
; a party member's turn): AL 1F3FCh's (SL's 1BF9Dh), 0 if the member stands still, and the jump to the
; move taken back (the member put on the turn's first square, DS:425Ch and 425Ah, its points the turn's
; own, DS:4258h), past the "jmp 1F08Ch" (the key's end) after it. The jump is made, back to 1EC3Fh, only
; for AL 0 and the member on its turn (WHOSE_TURN) holding neither Paralyzed (69) nor Cannot Move (66),
; the effects that pin (826F6h, SL's 786A9h: their landing clears the member's "can walk"): a pinned
; member is left where it is, with its points. Else back to the NOPs and the JMP. AX (AH 0) and every
; other register kept.
F10_TO_MOVE equ 0x1EC3F - 0x1EC39   ; (the move, less the address after the site's number)
F10_HELD   equ 69               ; (the sequel's Paralyzed ...
F10_STUCK  equ 66               ;   ... and Cannot Move)
f10_pin:
        mov ah, 0
        or ax, ax
        jnz .out                        ; (walking: the game's end)
        push bp
        push cx
        mov ax, [WHOSE_TURN]
        mov cl, F10_HELD
        call has_effect
        je .kept
        mov cl, F10_STUCK
        call has_effect
        je .kept
        mov bp, sp                      ; ([BP+4] the INT's IP)
        add word [bp + 4], F10_TO_MOVE
        inc word [cs:f10_moves]
        jmp .done
.kept:  inc word [cs:f10_kept]
.done:  xor ax, ax
        pop cx
        pop bp
.out:   iret

; ---- Psionic Blast's imagined wounds (DSCLOG's PROBE_WORN's blast and knock-out cases, always on) ----
; - BLAST_LOSS (site 79, SITE_BLAST_LOSS): "mov [bp-16h],dx" (3 bytes: the site; 6662Dh) in the effect
;   routine's Psionic Blast case (6660Ah, SL's case 169 at 796CBh), DX the hit points a target that
;   failed its save loses (down to a fifth of its most), DI the target (a combatant): stored, and for a
;   party member (0-3) a loss over 0 added to BLAST_HP, for the Loader to give back as the fight ends
;   (psiblast.py). The sequel deals the damage in a tail shared with other cases (656FAh: SL's "or byte
;   [si],1" after it, PROBE_WORN's site, is there "or byte [bx],1", not the blast's alone), so the loss is
;   taken here, before the damage is dealt: the same amount.
; - BLAST_KO (site 80, SITE_BLAST_KO): "add ax,0Ah" (3 bytes: the site; 5CC51h, SL's 58608h) before the
;   damage routine's death test "cmp ax,dx / jg" (5CC54h, SL's blast_knockout at 5860Bh), AX the
;   creature's hit points, DX the damage, DI the combatant: while a party member has hit points of Psionic
;   Blast's still to come back (BLAST_HP), a blow that would kill it (DX at AX + 10 or more) knocks it out
;   instead (AX made DX + 1: the "jg" goes to the Out Cold case, which reads only DX and BX), as the
;   blast's wounds are imagined; Disintegrate's (DX 10000 and up) still kills.
BLAST_UNMADE equ 10000                  ; (the damage routine's Disintegrate: status 8)
blast_loss:
        mov [bp - 0x16], dx             ; (the game's)
        cmp di, 3
        ja .out
        or dx, dx
        jle .out
        push bx
        mov bx, di
        add bx, bx
        add [cs:bx + blast_hp], dx
        pop bx
        inc word [cs:blast_seen]
.out:   iret
blast_ko:
        add ax, 0x0A                    ; (the game's)
        cmp di, 3
        ja .out
        cmp dx, BLAST_UNMADE
        jge .out
        push bx
        mov bx, di
        add bx, bx
        cmp word [cs:bx + blast_hp], 0
        pop bx
        jle .out
        cmp ax, dx
        jg .out
        mov ax, dx
        inc ax                          ; ("greater": knocked out, not killed)
        inc word [cs:blast_kos]
.out:   iret
blast_seen dw 0                         ; (blasts on party members counted, for a look in play)
blast_kos  dw 0                         ; (deaths made knock-outs, the same)

; RL_TRY (site 81, SITE_RL_TRY): "add ax,[42DAh]" (4 bytes: the site and a NOP; 6C585h, SL's RL_TRY at
; 6498Bh), where an ability's roll (6C504h, the ability at [BP+8], DI the try, 0-3) adds the race's
; adjustment + 4 to a 4d4 (AX): the 4d4 kept in RL_TRIES, and RL_SEQ counted, for the dice log (the
; die tumbles faster than the ring is read); whatever the rule.
rl_try:
        push bx
        mov bx, [bp + 8]
        cmp bx, 5
        ja .add
        cmp di, 3
        ja .add
        shl bx, 2
        mov [cs:rl_tries + bx + di], al
        inc word [cs:rl_seq]
.add:   pop bx
        add ax, [0x42DA]                ; (the game's)
        iret

; ---- QUICK SAVES: DSCLOG's quick save, quick load and autosave (quicksave.py), on the sequel's routines ----
; The Loader's two keys (QS_KEYS, F5 and F9 with its switch on) are counted (QS_SEQ) and taken from the game
; when the map's main loop has run within a tick or two, on the map, with the Loader there (QS_KEY, from
; INT16's OUR_KEY). For a save the Loader writes the file and the name into SAVE_TEXT, the number of its
; GREQ chunk into SAVE_GREQ, and sets SAVE_REQ 1; for a load it makes the quick saves' page the window's
; (the letter Q in the game's two file names, DS:2088h "SAVE??.SAV" and DS:20B9h "SAVE%.2d.SAV"), chooses
; the row (the window's word at 2F8h:0, the load + 3C4Ch) and sets 2. SAVE_TICK, from the top of the map's
; main loop (PROBE_SCROLL, DS the game's), does it once: the routine the SAVE window's wrapper (7D6FFh on)
; calls, save(far file, far name) (overlay stub 46EFh:0084h, its selector 5D8h; AL 0 if it failed), unless a
; fight is on (3C10h:19h, as F1's "CAN'T SAVE DURING COMBAT", 79AFDh); or the LOAD window, as F2 opens it
; (4736h:0020h, selector 600h; 79B74h). SAVE_REQ is 0 while it runs, then what came of it.
;
; The sequel's wrapper also keeps the map's limits (DS:14D7h-14DEh, set by a script, the whole map again
; at an area change; the view's centring keeps inside them) and DS:4459h as a GREQ chunk numbered by the
; slot in the roster file (DS:144Ah, opened by 46E9h:0052h), not in the save, and its load reads that
; chunk back. A quick save's GREQ is written the same way by GREQ_WRITE with the Loader's number (100 and
; the slot), and a load from the quick saves' page reads that one (GREQ_LOAD, site 84), so a quick save
; never takes a slot's limits from the save of the same number on the game's own page.
QS_DGROUP     equ 0x47E0            ; the game's DS, less its load segment
QS_SAVE_SEG   equ 0x46EF            ; (less the load segment) the save routine's overlay stub ...
QS_SAVE_ENTRY equ 0x0084            ;   ... and its entry: save(far file, far name), AL 0 if it failed
QS_LOAD_SEG   equ 0x4736            ; the save window's stub: its entry 20h opens it to load (F2's)
QS_LOAD_ENTRY equ 0x0020
QS_FIGHT_SEG  equ 0x3C10            ; the fight's state: a word at +19h, not 0 in a fight
QS_FILE_SEG   equ 0x46E9            ; the roster file opened (52h; its handle DS:144Ah) and closed (57h)
QS_OPEN       equ 0x0052
QS_CLOSE      equ 0x0057
QS_CHECK_SEG  equ 0x27ED            ; (27EDh:64h(handle): not 0, nothing written: the wrapper's test)
QS_CHECK      equ 0x0064
QS_GFF_SEG    equ 0x27FC            ; the open GFF's chunks: 5C5h(type, number) taken out, E8h(far data,
QS_DELETE     equ 0x05C5            ;   length, type, number) written
QS_WRITE      equ 0x00E8
QS_HANDLE     equ 0x144A            ; DS: the roster file's handle (a dword)
QS_LIMITS     equ 0x14D7            ; DS: the map's limits, four words ...
QS_LIMIT_MORE equ 0x4459            ; ... and a byte, then the byte at 4458h (the wrapper's 10 bytes, of which
GREQ_LENGTH   equ 9                 ;   it writes 9)
GREQ_PAGE     equ 100               ; (a quick save's GREQ number: this and its slot, the Loader's)
QS_LETTER     equ 0x2088            ; DS: the page's letter in "SAVE??.SAV" (the window's list) ...
QS_NAME_SAVE  equ 0x20B9            ; ... and in "SAVE%.2d.SAV" (the file a save writes)
QS_PAGE_GAME  equ 'E'               ; (the game's own page's letter)
QS_PAGE_QUICK equ 'Q'               ; (the QUICK page's: SAVQnn.SAV)
SAVE_FILE     equ 64                ; (SAVE_TEXT: the file's bytes, then the name's, SAVE_NAME)
SAVE_NAME     equ 48

; QS_KEY: (OUR_KEY's) AX a key: CF set, and counted in its word of QS_SEQ, if it is the Loader's quick save
; or quick load key with the map's main loop run within the last BIOS tick or two (no window, talk or
; menu waiting on keys), the map on show and the Loader there; else CF clear. Registers kept.
qs_key:
        push bx
        xor bx, bx
        cmp ax, 0xFFFF
        je .no
        cmp ax, [cs:qs_keys]
        je .ours
        mov bl, 2
        cmp ax, [cs:qs_keys + 2]
        jne .no
.ours:  push ax
        push es
        xor ax, ax
        mov es, ax
        mov ax, [es:0x46C]
        sub ax, [cs:map_tick]
        pop es
        cmp ax, L_FRESH
        pop ax
        ja .no
        call on_map
        jne .no
        call loader_fresh
        jne .no
        inc word [cs:qs_seq + bx]
        pop bx
        stc
        ret
.no:    pop bx
        clc
        ret

; SAVE_TICK: from PROBE_SCROLL (DS the game's, interrupts off): what the Loader asked in SAVE_REQ, once,
; with interrupts on again if the game's loop had them on. PROBE_SCROLL's way back (S_IP, S_CS, S_FL, S_FAR)
; kept on the stack meanwhile, in case the game's routine runs a pass of its loop. AX to DI, ES changed.
save_tick:
        cmp word [cs:save_req], 2       ; (no quick load waiting: the page the game's own, PAGE_BACK)
        je .req
        cmp word [SCREEN_IS], 1         ; (nor a window up: F9's LOAD window, its own passes of the main
        jne .req                        ;   loop coming here, has the screen word 2)
        cmp byte [QS_LETTER], QS_PAGE_GAME
        je .req
        mov al, QS_PAGE_GAME            ; (QUICK, or a page PgDn turned to: every window opens on the first)
        call qs_page
        push es
        mov ax, ds
        add ax, PG_LIST
        mov es, ax
        mov dword [es:0], 0             ; (and on its first row: the one chosen there may be empty here)
        pop es
        inc word [cs:pages_back]
.req:   mov ax, [cs:save_req]
        dec ax
        cmp ax, 1
        ja .ret                         ; (none, or an answer the Loader hasn't read yet)
        push word [cs:s_ip]
        push word [cs:s_cs]
        push word [cs:s_fl]
        push word [cs:s_far]
        push word [cs:s_far + 2]
        pushf
        test byte [cs:s_fl + 1], 2      ; (the caller's flags' IF)
        jz .work
        sti
.work:  call save_work
        popf
        pop word [cs:s_far + 2]
        pop word [cs:s_far]
        pop word [cs:s_fl]
        pop word [cs:s_cs]
        pop word [cs:s_ip]
.ret:   ret

save_work:
        mov ax, [cs:save_req]
        mov word [cs:save_req], 0
        cmp ax, 2
        je .load
        mov ax, ds
        sub ax, QS_DGROUP - QS_FIGHT_SEG
        mov es, ax
        mov ax, 5
        cmp word [es:0x19], 0
        jne .set                        ; (a fight: the game saves none)
        mov ax, QS_SAVE_SEG
        mov bx, QS_SAVE_ENTRY
        call qs_far
        mov ax, cs                      ; save(file, name): SAVE_TEXT, the tail's
        add ax, TAIL_PARAS
        push ax
        push word save_text + SAVE_FILE
        push ax
        push word save_text
        call far [cs:qs_call]
        add sp, 8
        or al, al
        mov ax, 4
        jz .set
        inc word [cs:quick_saves]
        call greq_write
        mov ax, 3
        jmp .set
.load:  mov al, QS_PAGE_QUICK            ; (the QUICK page for the window, and only for it: PAGE_BACK)
        call qs_page
        mov ax, QS_LOAD_SEG
        mov bx, QS_LOAD_ENTRY
        call qs_far
        call far [cs:qs_call]           ; (it returns with the window up: the main loop runs it, and
        inc word [cs:quick_loads]       ;   SAVE_TICK puts E back once it is shut and the map is the screen)
        mov ax, 3
.set:   mov [cs:save_req], ax
        ret

; QS_PAGE: AL the page's letter put in the game's two save file names (QS_LETTER, QS_NAME_SAVE; DS the
; game's). PAGE_BACK: the sequel's one page is the game's E; the QUICK page (Q) is only for F9's LOAD window,
; put there by SAVE_WORK as it opens it and taken off by SAVE_TICK whenever the main loop runs on the map
; (SCREEN_IS 1) with no quick load waiting (the Loader writes Q before asking): so F1's SAVE window (or F2's
; LOAD) can never open on Q, where a save by hand would go to SAVQnn.SAV (its slots written over in turn).
; The window's routine returns with the window up (seen in play: SAVE_REQ 3 0.4 s after F9, the window
; still open) and the main loop runs it, with the screen word 2: Q is kept until it shuts. (The Loader's
; own page-back, SL's, is off in the sequel: ravlog.QUICK_LAYOUT's page_back.)
qs_page:
        mov [QS_LETTER], al
        mov [QS_NAME_SAVE], al
        ret

; QS_FAR: QS_CALL made the game's routine at AX (less the load segment):BX (DS the game's)
qs_far:
        mov [cs:qs_call], bx
        mov bx, ds
        add ax, bx
        sub ax, QS_DGROUP
        mov [cs:qs_call + 2], ax
        ret

; GREQ_WRITE: after a quick save, its GREQ chunk (SAVE_GREQ, the Loader's number; 0 none) written as the
; SAVE window's wrapper writes a slot's (7D85Fh-7D8D9h, its PREF chunk left out): the roster file opened,
; the wrapper's test, the chunk taken out and written again (GREQ_LENGTH bytes: the map's limits and the
; byte after them), the file closed.
greq_write:
        cmp word [cs:save_greq], 0
        je .ret
        mov si, QS_LIMITS
        mov di, greq_data
        mov ax, [si]
        mov [cs:di], ax
        mov ax, [si + 2]
        mov [cs:di + 2], ax
        mov ax, [si + 4]
        mov [cs:di + 4], ax
        mov ax, [si + 6]
        mov [cs:di + 6], ax
        mov al, [QS_LIMIT_MORE]
        mov [cs:di + 8], al
        mov al, [QS_LIMIT_MORE - 1]
        mov [cs:di + 9], al
        mov ax, QS_FILE_SEG
        mov bx, QS_OPEN
        call qs_far
        call far [cs:qs_call]
        push word [QS_HANDLE + 2]
        push word [QS_HANDLE]
        mov ax, QS_CHECK_SEG
        mov bx, QS_CHECK
        call qs_far
        call far [cs:qs_call]
        add sp, 4
        or ax, ax
        jnz .close
        push word 0                     ; (the chunk's number, a dword)
        push word [cs:save_greq]
        push word 'EQ'                  ; (its type, "GREQ")
        push word 'GR'
        mov ax, QS_GFF_SEG
        mov bx, QS_DELETE
        call qs_far
        call far [cs:qs_call]
        add sp, 8
        push word 0
        push word [cs:save_greq]
        push word 'EQ'
        push word 'GR'
        push word 0                     ; (its length, a dword)
        push word GREQ_LENGTH
        push cs
        push word greq_data
        mov ax, QS_GFF_SEG
        mov bx, QS_WRITE
        call qs_far
        call far [cs:qs_call]
        add sp, 16
        inc word [cs:greq_saves]
.close: mov ax, QS_FILE_SEG
        mov bx, QS_CLOSE
        call qs_far
        call far [cs:qs_call]
.ret:   ret

; GREQ_LOAD (site 84, SITE_GREQ_LOAD): "mov ax,es:[2]" (7DA30h: 4 bytes, the site's INT, its number, a NOP)
; in the load's wrapper, the window's first row (ES its data, 2F8h) the GREQ chunk's number is made from
; (it, the row and 1): GREQ_PAGE more on the quick saves' page, whose saves GREQ_WRITE numbered so.
greq_load:
        push bx
        call page_base
        mov ax, [es:2]
        add ax, bx
        or bx, bx
        jz .r
        inc word [cs:greq_loads]
.r:     pop bx
        iret

; ---- MORE SAVES: SL's PROBE_SAVE_PAGE (savepages.py's pages) on the sequel's save and load window ----
; The window shows ten saves, on five pages, each a letter of the game's two save file names (QS_PAGE):
; the game's own (SAVE01.SAV to SAVE10.SAV), then SAVB, SAVC and SAVD01.SAV to 10.SAV, and in the load
; window the quick saves' (SAVQ: QUICK SAVES), in that order. PgDn shows the next page, PgUp the one before
; (PAGE_KEY); the window's own routines (in its overlay, reached from the site's way back: what they call
; is resident, so it stays put) search the folder again and draw the rows, the load window chooses the
; page's first save (passing by pages with none), the row chosen is shown so, and the window is drawn
; again with the page's name under EXIT (PAGE_LABEL; also as the window opens, PAGE_OPEN). Each page's
; saves keep their map limits in GREQ chunks of their own (PAGE_BASE: GREQ_SAVE, GREQ_LOAD), as the quick
; saves' (GREQ_WRITE). The sequel's RESOURCE.GFF has no PAGE buttons to add (no WIND 3009 or EXIT icon of
; SL's), so the keys alone turn the pages. Every window opens on the game's own page (SAVE_TICK's
; page-back once the map is the screen again).
PG_BACK    equ 0x7DABF                  ; (DSUN.EXE: PAGE_KEY's way back, past the INT and site byte at 7DABCh)
PG_IGNORE  equ 0x7E00F - PG_BACK        ; the routine's end, for a key it has no use for
PG_DONE    equ 0x7DBD7 - PG_BACK        ; ... after Up or Down: the screen updated, then the end
PG_SCAN    equ 0x7D3F2 - PG_BACK        ; the overlay's routines: the folder searched (how many),
PG_ROW     equ 0x7E058 - PG_BACK        ;   a row drawn (its number),
PG_PICK    equ 0x7E0F4 - PG_BACK        ;   a row shown as chosen, its name below
PG_KEY     equ 0x12                     ; (the key, at the routine's BP+12h)
PG_LIST    equ 0x3C4C - QS_DGROUP       ; (less DS) the list's words: +0 the row chosen, +2 the first shown
PG_WINDOW  equ 0x40AF - QS_DGROUP       ; (less DS) +0 the window (far), +4 1 for the load window
PG_SAVES   equ 0x6278                   ; DS: the saves (far), 7Dh bytes each, +0 the file's name
PG_SAVE_SIZE equ 0x7D
PG_ROW_ID  equ 0x4780                   ; the rows' buttons
PG_BTN_SEG equ 0x2EBE - QS_DGROUP       ; (resident) a button's state (window, id, state) ...
PG_BTN_OFF equ 0x071F
PG_WIN_SEG equ 0x2A8E - QS_DGROUP       ; ... and a window brought to the front and drawn (window)
PG_WIN_OFF equ 0x060D
PAGE_COUNT equ 5
PAGE_QUICK equ 4                        ; (the QUICK page: the load window's only)
KEY_PGUP   equ 0x4900
KEY_PGDN   equ 0x5100
PG_LABEL_X equ 228                      ; (the window's coordinates, its top 32 lines down: under EXIT)
PG_LABEL_Y equ 64
page_key:
        push bp
        mov bp, sp
        sti
        pushad
        push es
        mov si, [bp]                    ; (the routine's BP)
        mov ax, [ss:si + PG_KEY]
        cmp al, 0xE0
        jne .keys
        xor al, al                      ; (the grey keys: as the number pad's)
.keys:  mov dl, -1
        cmp ax, KEY_PGUP
        je .step
        mov dl, 1
        cmp ax, KEY_PGDN
        jne .skip
.step:  mov [cs:pg_dir], dl
        mov ax, [bp + 4]                ; (the overlay's routines: from the way back)
        mov [cs:pg_call + 2], ax
        mov ax, [bp + 2]
        mov [cs:pg_ip], ax
        call page_now
        mov [cs:pg_was], bl
.next:  add bl, [cs:pg_dir]
        cmp bl, PAGE_COUNT
        jae .none                       ; (no page before the first, or after the last)
        call pg_es_window
        cmp bl, PAGE_QUICK
        jne .page
        cmp byte [es:4], 0
        je .none                        ; (QUICK: not for the save window)
.page:  call pg_page
        call pg_es_window
        xor di, di                      ; (the save window: its first row)
        cmp byte [es:4], 0
        je .rows
.first: les bx, [PG_SAVES]              ; (the load window: the page's first save)
        imul ax, di, PG_SAVE_SIZE
        add bx, ax
        cmp byte [es:bx], 0
        jne .found
        inc di
        cmp di, 10
        jb .first
        call page_now                   ; (none: the next page that way)
        jmp .next
.none:  call page_now
        cmp bl, [cs:pg_was]
        je .skip                        ; (where it was: nothing to do)
        mov bl, [cs:pg_was]             ; (back to the page there was)
        call pg_page
        jmp .skip
.found:
.rows:  xor cx, cx
.row:   push cx
        push cx
        mov ax, PG_ROW
        call pg_overlay
        add sp, 2
        pop cx
        inc cx
        cmp cx, 10
        jb .row
        mov ax, ds
        add ax, PG_LIST
        mov es, ax
        push word 5                     ; (the row chosen before: as the others ...)
        mov ax, [es:0]
        call pg_button
        mov ax, ds
        add ax, PG_LIST
        mov es, ax
        mov [es:0], di
        mov word [es:2], 0
        push word 4                     ; (... and the one chosen now)
        mov ax, di
        call pg_button
        push di
        mov ax, PG_PICK
        call pg_overlay
        add sp, 2
        call page_label
        inc word [cs:page_turns]
        add word [bp + 2], PG_DONE
        jmp .out
.skip:  add word [bp + 2], PG_IGNORE
.out:   pop es
        popad
        pop bp
        iret

; PAGE_OPEN (site 216, "save_page_open"): "add sp,4" (7D691h, 3 bytes) after the window's opening routine
; draws it (the far call before it is fixed up as the overlay loads, so no site there): the page's label put in
; (PAGE_LABEL), then the routine's own "add sp,4" done under the way back. AX to DI, ES kept.
page_open:
        inc word [cs:pg_opens]
        push ax
        mov ax, ds
        add ax, PG_WINDOW
        mov [cs:pg_win_seg], ax         ; (PAGE_MOUSE's test of the window)
        pop ax
        pushad
        push es
        call page_label
        pop es
        popad
        pop word [cs:pg_near]           ; (the way back, IP, CS and flags, put 4 bytes higher)
        pop word [cs:pg_far]
        pop word [cs:pg_far + 2]
        add sp, 4
        push word [cs:pg_far + 2]
        push word [cs:pg_far]
        push word [cs:pg_near]
        iret

; PAGE_MOUSE: (MOUSE_EVENT's: CX, DX where, in the game's pixels, AL the events) a left press on "PGUP" or
; "PGDN" under EXIT, with the save or load window up (its far pointer, PG_WIN_SEG:0, cleared as it shuts), is
; posted to the game as that key (PAGE_KEY then turns the page), and not the game's. The game's keyboard
; handler (39E35h) posts each key it reads as an event (1, 0Ah, 0, the key, the shift keys) through
; PG_POST_SEG:0230h; a key put in the BIOS's buffer instead waits for the next key pressed. AX's press bit
; cleared for one; others kept.
PG_HIT_Y0  equ 79                       ; (the screen's pixels: the "PGUP PGDN" line, a little more)
PG_HIT_Y1  equ 93
PG_UP_X0   equ 226                      ; PGUP's ...
PG_DN_X0   equ 254                      ; ... and PGDN's
PG_DN_X1   equ 282
PG_POST_SEG equ 0x3464 - QS_DGROUP      ; (resident: an event posted, its far pointer pushed)
PG_POST_OFF equ 0x0230
page_mouse:
        test al, EVENT_LEFT_PRESS
        jz .ret
        cmp word [cs:pg_win_seg], 0
        je .ret
        cmp dx, PG_HIT_Y0
        jb .ret
        cmp dx, PG_HIT_Y1
        jae .ret
        cmp cx, PG_UP_X0
        jb .ret
        cmp cx, PG_DN_X1
        jae .ret
        push ds
        mov ds, [cs:pg_win_seg]
        cmp dword [0], 0
        pop ds
        je .ret                         ; (no window up)
        pusha
        push ds
        push es
        mov word [cs:pg_event + 6], KEY_PGUP
        cmp cx, PG_DN_X0
        jb .post
        mov word [cs:pg_event + 6], KEY_PGDN
.post:  mov ax, [cs:pg_win_seg]
        sub ax, PG_WINDOW               ; (the game's DS)
        mov ds, ax
        add ax, PG_POST_SEG
        mov [cs:pg_post + 2], ax
        mov word [cs:pg_post], PG_POST_OFF
        pushf
        cli
        push cs
        push word pg_event
        call far [cs:pg_post]
        add sp, 4
        popf
        inc word [cs:pg_clicks]
        pop es
        pop ds
        popa
        and al, ~EVENT_LEFT_PRESS
.ret:   ret
pg_event     dw 1, 0x0A, 0, 0, 0        ; (the key's event, as the game's keyboard handler posts it)
pg_post      dd 0                       ; (its own: the mouse's handler may come in the middle of PG_FAR's use)

; PAGE_NOW: BL the page shown (0 to 4, by the letter in QS_LETTER: PAGE_LETTERS; another as the first).
page_now:
        push ax
        mov al, [QS_LETTER]
        xor bx, bx
.find:  cmp al, [cs:page_letters + bx]
        je .ret
        inc bx
        cmp bx, PAGE_COUNT
        jb .find
        xor bx, bx
.ret:   pop ax
        ret

; PAGE_BASE: BX the page's GREQ chunks' base (its saves' are this and the slot): the game's own 0, QUICK
; GREQ_PAGE (GREQ_WRITE's), the others 200, 300, 400. DS the game's; keeps the rest.
page_base:
        push ax
        call page_now
        mov al, [cs:page_bases + bx]
        mov bl, 100
        mul bl
        mov bx, ax
        pop ax
        ret

; PG_PAGE: page BL's letter put in the names (QS_PAGE), and the folder searched again (PG_SCAN).
pg_page:
        movzx bx, bl
        mov al, [cs:page_letters + bx]
        call qs_page
        push word 10
        mov ax, PG_SCAN
        call pg_overlay
        add sp, 2
        ret

; PG_OVERLAY: a far call to the window's overlay at AX from PAGE_KEY's way back (PG_CALL's segment set),
; its arguments pushed; the game's routines keep neither BX nor ES.
pg_overlay:
        add ax, [cs:pg_ip]              ; (offsets from the way back)
        mov [cs:pg_call], ax
        pop word [cs:pg_near]           ; (the near way back, kept while the far call runs)
        call far [cs:pg_call]
        jmp [cs:pg_near]

; PG_BUTTON: row AX's button set to the state pushed (taken off: PG_BTN_SEG's routine, as the game does).
pg_button:
        pop word [cs:pg_near2]
        add ax, PG_ROW_ID
        movzx edx, ax
        call pg_es_window
        pop cx                          ; (the state)
        push cx
        push edx
        push dword [es:0]
        mov ax, ds
        add ax, PG_BTN_SEG
        mov [cs:pg_far + 2], ax
        mov word [cs:pg_far], PG_BTN_OFF
        call far [cs:pg_far]
        add sp, 10
        jmp [cs:pg_near2]

pg_es_window:                           ; ES the window's words (PG_WINDOW)
        mov ax, ds
        add ax, PG_WINDOW
        mov es, ax
        ret

; PAGE_LABEL: the page's name ("PAGE 2", "QUICK") and "PGUP PGDN" under EXIT in the window, which is then
; drawn again (PG_WIN_SEG's routine). DS the game's; changes all but DS and BP.
page_label:
        call pg_es_window
        mov eax, [es:0]
        or eax, eax
        jz .ret
        mov [cs:c_winptr], eax
        inc word [cs:pg_labels]
        mov ax, ds
        add ax, USE_TEXT_SEG
        mov [cs:c_draw + 2], ax
        mov word [cs:c_draw], USE_TEXT_OFF
        call page_now
        mov al, '1'
        add al, bl
        mov [cs:pg_text + 5], al
        mov si, pg_text
        cmp bl, PAGE_QUICK
        jne .win
        mov si, pg_quick
.win:   push si
        call pg_es_window
        push dword [es:0]
        mov ax, ds
        add ax, PG_WIN_SEG
        mov [cs:pg_far + 2], ax
        mov word [cs:pg_far], PG_WIN_OFF
        call far [cs:pg_far]
        add sp, 4
        pop si
.draw:  push word PG_LABEL_Y
        push word PG_LABEL_X
        push cs
        push si
        call c_draw_line
        push word PG_LABEL_Y + 9
        push word PG_LABEL_X
        push cs
        push word pg_keys
        call c_draw_line
.ret:   ret

page_letters db QS_PAGE_GAME, 'B', 'C', 'D', QS_PAGE_QUICK
page_bases   db 0, 2, 3, 4, GREQ_PAGE / 100
pg_text      db 'PAGE 1', 0
pg_quick     db 'QUICK', 0
pg_keys      db 'PGUP PGDN', 0
pg_was       db 0
pg_dir       db 0
pg_ip        dw 0
pg_call      dd 0
pg_far       dd 0
pg_near      dw 0
pg_near2     dw 0
page_turns   dw 0               ; (pages turned, for a look in play)
pg_opens     dw 0               ; (windows opened: PAGE_OPEN)
pg_win_seg   dw 0               ; (the window's words, as PAGE_OPEN saw them: PAGE_MOUSE)
pg_clicks    dw 0               ; (PGUP and PGDN clicked: PAGE_MOUSE)
pg_labels    dw 0               ; (labels drawn: PAGE_LABEL)

; GREQ_SAVE (site 239, "greq_save"): "mov ax,si / inc ax" (7D8A1h, 7D8BAh; 3 bytes) where the SAVE window's
; wrapper numbers the GREQ chunk it takes out and writes again (the row and 1): the page's base more
; (PAGE_BASE), so each page keeps its saves' map limits apart. Others kept.
greq_save:
        push bx
        call page_base
        lea ax, [bx + si + 1]
        pop bx
        iret

; ---- LOOT AND SELL KEYS, M, U and I: DSCLOG's LOOT_KEY, SELL_KEY, MAP_KEY and SHOP_LOOP on the sequel ----
; (The Loader's dsloader/loot.py and sell.py do the item moves once the window or the shop is shut, as in
; Shattered Lands, on the sequel's addresses: ravlog.RAV_ITEMS.) The header's fields are DSCLOG's, at its
; offsets (+1846 to +1859). What differs from DSCLOG's: the game's DS is PROBE_SCROLL's (POINTER_DS), the
; container whose window is open DS:05D6h (SL's 05E6h), the shop's merchant DS:1A30h (SL's 179Ch), the
; party member on show at selector 370h:0B44h (SL's 3931h:25Bh), and the shop's loop "while byte [143Dh]
; is 1" (88D52h; SL's word [11B2h], 7DDE4h).

; LOOT_KEY: (OUR_KEY's first) T or Shift+T with a container's window open (LOOT_OPEN its map thing, 9999
; none) is made Escape, which closes the window, and, when the key is read (MK_READ; a peek only looks),
; counted in LOOT_SEQ with the container (LOOT_THING) and T's mode or Shift+T's (LOOT_MODE: Shift held,
; from the BIOS keyboard flags, whatever Caps Lock does to the letter). Other keys, and these with no
; window, or with no Loader passing (LOADER_FRESH: unlike DSCLOG, DSCLOG2 runs whenever the sequel does, the
; Loader or not), as they were. AX the key (Escape now, for one of these); others kept.
KEY_T        equ 0x1474
KEY_SHIFT_T  equ 0x1454
KEY_ESCAPE   equ 0x011B
LOOT_OPEN    equ 0x05D6             ; (the game's DS) the container whose window is open
LOOT_NONE    equ 9999
loot_key:
        cmp ax, KEY_T
        je .t
        cmp ax, KEY_SHIFT_T
        jne .ret
.t:     push ds
        push bx
        call loader_fresh               ; (no Loader to do the move: T the game's key, the window kept)
        jne .out
        mov bx, [cs:pointer_ds]
        or bx, bx
        jz .out
        mov ds, bx
        mov bx, [LOOT_OPEN]
        cmp bx, LOOT_NONE
        je .out
        cmp word [cs:loot_thing], 0xFFFF ; (the last T not yet taken by the Loader: this one left as
        jne .out                        ;   the game's key, the window kept open, to be pressed again)
        cmp byte [cs:mk_read], 0
        je .esc                         ; (peeked: told it is Escape, counted when read)
        mov [cs:loot_thing], bx
        mov word [cs:loot_mode], 0
        xor bx, bx
        mov ds, bx
        test byte [0x417], 3            ; (either Shift)
        jz .count
        mov word [cs:loot_mode], 1
.count: inc word [cs:loot_seq]
.esc:   mov ax, KEY_ESCAPE
.out:   pop bx
        pop ds
.ret:   ret

; SELL_KEY: (OUR_KEY's) S or Shift+S on a shop's screen (its loop, SHOP_LOOP, run within the last
; SHOP_FRESH BIOS ticks) is made Escape, which shuts the shop, and, when the key is read (MK_READ),
; counted in SELL_SEQ with the party member on show (SELL_MEMBER) and the shop's merchant (SELL_MERCHANT):
; the Loader sells that member's plain gear (dsloader/sell.py) once the shop is shut (with no Loader
; passing, LOADER_FRESH, S the game's). AX the key (Escape now, for one of these); others kept.
KEY_S        equ 0x1F73
KEY_SHIFT_S  equ 0x1F53
SHOP_FRESH   equ 2
SHOP_SCREEN  equ 0x143D             ; (the game's DS) a byte, 1 while a merchant's shop is open (7BCA6h)
SELL_WHO_SEG equ 0x3E71 - 0x47E0    ; (selector 370h's segment less the game's DS) ...
SELL_WHO_OFF equ 0x0B44             ; ... the character on show
sell_key:
        cmp ax, KEY_S
        je .s
        cmp ax, KEY_SHIFT_S
        jne .ret
.s:     push ds
        push bx
        push ax
        call loader_fresh               ; (no Loader to sell: S the game's key, the shop kept)
        jne .out
        mov bx, [cs:pointer_ds]
        or bx, bx
        jz .out
        cmp word [cs:shop_at], 0
        je .out
        xor ax, ax
        mov ds, ax
        mov ax, [0x46C]
        sub ax, [cs:shop_at]
        cmp ax, SHOP_FRESH
        ja .out
        cmp byte [cs:mk_read], 0
        je .esc                         ; (peeked: told it is Escape, counted when read)
        mov ds, bx
        mov ax, [SHOP_MERCHANT]
        mov [cs:sell_merchant], ax
        add bx, SELL_WHO_SEG
        mov ds, bx
        mov ax, [SELL_WHO_OFF]
        mov [cs:sell_member], ax
        inc word [cs:sell_seq]
        mov byte [cs:sell_wait], 1      ; (SHOP_LOOP waits for the Loader's sale as the shop shuts)
        mov word [cs:shop_at], 0        ; (shut: the next S is a key of the game's)
.esc:   pop ax
        mov ax, KEY_ESCAPE
        push ax
.out:   pop ax
        pop bx
        pop ds
.ret:   ret

; SHOP_LOOP (site 82, "shop_loop"): "cmp byte [143Dh],1" (88D99h; 5 bytes: the site's INT, its number and
; 2 NOPs), the test of the shop's own loop (88D52h, run while a merchant's shop is open): the BIOS tick
; kept in SHOP_AT while it is open (SELL_KEY), and the test made, its flags given back. DS the game's.
; The shop shut by S (SELL_WAIT): held here till the Loader has sold (SELL_DONE is SELL_SEQ) or SELL_HOLD
; ticks have passed. The merchant's script reads the party's money as the shop returns to it, against
; what it was before (Notaku's, GPL 153 at 3EFh-400h: "Thank you, your business is appreciated." when
; it moved, "Sometimes the wisest purchase is none at all, yes?" when not), so the Loader's pay must
; be in by then, as the game's own SELL's is.
SELL_HOLD equ 55                ; BIOS ticks (3 seconds) at most
shop_loop:
        push bp
        mov bp, sp
        push ax
        cmp byte [SHOP_SCREEN], 1
        je .open
        cmp byte [cs:sell_wait], 0
        je .test
        mov byte [cs:sell_wait], 0
        push es
        push bx
        xor ax, ax
        mov es, ax
        mov bx, [es:0x46C]              ; (the hold's start)
        sti                             ; (the BIOS clock and the Loader's passes go on meanwhile)
.hold:  mov ax, [cs:sell_done]
        cmp ax, [cs:sell_seq]
        je .held
        mov ax, [es:0x46C]
        sub ax, bx
        cmp ax, SELL_HOLD
        jae .held
        hlt
        jmp .hold
.held:  cli
        pop bx
        pop es
        jmp .test
.open:
        push es
        xor ax, ax
        mov es, ax
        mov ax, [es:0x46C]
        mov [cs:shop_at], ax
        pop es
        inc word [cs:shop_passes]
        push bp
        call shine_turn                 ; (the magic items' shine, as the map's loop turns it)
        pop bp
.test:  cmp byte [SHOP_SCREEN], 1
        lahf
        mov [bp + 6], ah                ; (the flags' low byte: ZF for the loop's JE)
        pop ax
        pop bp
        iret
shop_passes dw 0                ; (the shop's loop's passes, for a look in play)

; SEE-THROUGH FIGURES (DSCLOG's GHOST, on the sequel): a party member hidden in shadows and unheard
; (STEALTH's bit), and a creature the Loader marks in GHOST_TAB (invisible, the sequel's effect 53, while no
; party member detects it, 25: ghost.py), are drawn half see-through, each pixel the colour halfway between
; the figure's and what is under it. Drawn in FIG_KEEP's place of the thing drawer's picture call (site 162,
; 2A347h: DI the thing, the call's arguments the page, x, y, mirrored, the picture and the frame, SL's).
; **Smaller than SL's block**: the tables the Loader makes (BLEND, 8 KB: for each of the figure's REP_COUNT
; colours a row of 256, the colour halfway between it and each of the palette's; REP; GHOST_TAB) are in the
; far block (FAR_GH_BLEND on: the HMA in a GOG start), only the figure's pixels and spans (5,632 bytes) in
; GHOST's block of upper memory (GHOST_SEG, made at the start if there's room).
REP_COUNT   equ 32
GH_PIX      equ 0                       ; (GHOST's block: the figure's pixels, as REP numbers (GHOST_DRAW) ...
GH_PIX_MOST equ 4096
GH_SPANS    equ GH_PIX + GH_PIX_MOST    ; ... its runs on the screen, 8 bytes each: the row's place in the
GH_SPANS_MOST equ 192                   ;   page, first x, last x, its first pixel)
GHOST_PARAS equ (GH_SPANS + GH_SPANS_MOST * 8 + 15) / 16
gh_shown    dw 0                        ; (party members drawn see-through while hidden: a bit each)

; GHOST_WANTED: CF if thing DI is drawn see-through (GHOST_ON, the block, and its STEALTH bit, a party
; member's, or its GHOST_TAB bit). Registers kept.
ghost_wanted:
        cmp word [cs:ghost_on], 0
        je .no
        cmp word [cs:ghost_seg], 0
        je .no
        cmp word [cs:far_seg], 0
        je .no
        cmp di, MAP_COUNT - 1
        ja .no
        cmp di, 3
        ja .tab
        bt [cs:stealth], di
        jnc .tab
        bts [cs:gh_shown], di           ; (drawn see-through while hidden: GHOST_UNION)
        stc
        ret
.tab:   push fs
        mov fs, [cs:far_seg]
        bt [fs:FAR_GH_TAB], di
        pop fs
        ret
.no:    clc
        ret

; GHOST_DRAW: FIG_KEEP's call's frame drawn see-through (its arguments at [BP+4] on). The frame's runs
; decoded into GH_PIX as REP numbers, each run within the page noted (GH_SPANS: the pixel at its first x; a
; mirrored frame's pixels are read from the other end), then a plane at a time each pixel there made BLEND's
; of its REP number and the colour under it. DS, SI, DI kept. (SL's, GS the block, FS the far block.)
GD_SPANS equ -2
GD_W     equ -4
GD_X     equ -6
GD_N     equ -8
GD_STEP  equ -10
ghost_draw:
        push bp
        mov bp, sp                      ; [bp+4] page, +6 x, +8 y, +10 mirrored, +12 picture, +16 frame
        push ds
        push si
        push di
        push fs
        push gs
        sub sp, 12
        inc word [cs:ghost_draws]
        mov ax, 4
        test byte [bp + 10], 1
        jz .step
        neg ax
.step:  mov [bp + GD_STEP - 12], ax
        mov bx, [bp + 4]
        call page_setup
        mov fs, [cs:far_seg]
        mov gs, [cs:ghost_seg]
        les si, [bp + 12]               ; the picture: its frames' places from +6
        mov ax, es
        or ax, si
        jz .out
        mov bx, [bp + 16]
        cmp bx, [es:si + 4]
        jae .out
        shl bx, 2
        xor eax, eax
        mov ax, es
        shl eax, 4
        movzx ecx, si
        add eax, ecx
        add eax, [es:si + bx + 6]
        mov si, ax
        and si, 0x0F
        shr eax, 4
        mov ds, ax                      ; DS:SI the frame: width, height, then its rows
        cld
        lodsw
        mov [bp + GD_W - 12], ax
        lodsw
        push gs
        pop es
        mov di, GH_PIX
        mov word [bp + GD_SPANS - 12], GH_SPANS
.row:   lodsb
        cmp al, 0xFF
        je .flush
        movzx dx, al
        add dx, [bp + 8]                ; DX its row on the screen
.run:   lodsw
        push ax                         ; x (8000h: the row's last)
        and ah, 0x7F
        movzx cx, byte [si]             ; its pixels
        mov [bp + GD_N - 12], cx
        test byte [bp + 10], 1
        jz .fwd
        neg ax                          ; (mirrored: from the right)
        sub ax, cx
        add ax, [bp + GD_W - 12]
.fwd:   add ax, [bp + 6]
        mov [bp + GD_X - 12], ax
        movzx ax, byte [si + 1]
        add si, 2
        add ax, si
        push ax                         ; (past its data)
        mov ax, di
        add ax, cx
        jc .full
        cmp ax, GH_SPANS
        ja .full                        ; (no room: what is decoded drawn)
        push di                         ; (its first pixel)
        jcxz .noted
        push dx
        mov dx, cx                      ; DX: the pixels left
        mov bx, FAR_GH_REP              ; (FS:BX: REP, for XLAT)
.data:  lodsb                           ; a control byte: bit 0 clear, (b >> 1) + 1 bytes to copy;
        movzx cx, al                    ;   set, one byte (b >> 1) + 1 times (each a REP number)
        shr cx, 1
        inc cx
        sub dx, cx
        test al, 1
        jz .copy
        lodsb
        fs xlatb
        rep stosb
        jmp .took
.copy:  lodsb
        fs xlatb
        stosb
        loop .copy
.took:  or dx, dx
        jg .data
        pop dx
.noted: pop bx                          ; BX its first pixel
        pop si
        cmp dx, [cs:clip_y0]            ; the run within the page: noted
        jl .next
        cmp dx, [cs:clip_y1]
        jg .next
        mov ax, [bp + GD_X - 12]        ; AX its first x, CX its last, BX the pixel there
        mov cx, ax
        add cx, [bp + GD_N - 12]
        dec cx
        test byte [bp + 10], 1
        jz .clip
        add bx, [bp + GD_N - 12]
        dec bx
.clip:  push dx
        mov dx, [cs:clip_x0]
        sub dx, ax
        jle .x1
        add ax, dx
        cmp word [bp + GD_STEP - 12], 0
        jg .ahead
        neg dx
.ahead: add bx, dx
.x1:    pop dx
        cmp cx, [cs:clip_x1]
        jle .span
        mov cx, [cs:clip_x1]
.span:  cmp ax, cx
        jg .next
        cmp word [bp + GD_SPANS - 12], GH_SPANS + GH_SPANS_MOST * 8
        jae .spans_full                 ; (no room for its span: what is noted drawn)
        push di
        mov di, [bp + GD_SPANS - 12]
        mov [es:di + 2], ax
        mov [es:di + 4], cx
        mov [es:di + 6], bx
        mov ax, dx                      ; the row's place in the page
        sub ax, [cs:v_y0]
        push dx
        mul word [cs:v_row]
        pop dx
        sub ax, [cs:v_x0]
        stosw
        add word [bp + GD_SPANS - 12], 8
        pop di
.next:  pop ax
        test ah, 0x80
        jz .run
        jmp .row
.full:  pop ax
.spans_full:
        pop ax
.flush: call vga_save
        mov es, [cs:v_seg]
        xor cx, cx                      ; the plane
.plane: mov dx, 0x3C4                   ; write to this plane, read from it
        mov al, 2
        mov ah, 1
        shl ah, cl
        out dx, ax
        mov dx, 0x3CE
        mov al, 4
        mov ah, cl
        out dx, ax
        mov si, GH_SPANS
.gspan: cmp si, [bp + GD_SPANS - 12]
        jae .nplane
        mov ax, cx
        sub ax, [gs:si + 2]
        and ax, 3                       ; how far on its first pixel on this plane is
        mov bx, [gs:si + 6]
        cmp word [bp + GD_STEP - 12], 0
        jg .on
        sub bx, ax
        sub bx, ax
.on:    add bx, ax
        add ax, [gs:si + 2]
        mov dx, [gs:si + 4]
        sub dx, ax
        jl .nspan
        shr dx, 2
        inc dx                          ; DX: how many
        shr ax, 2
        add ax, [gs:si]
        mov di, ax
        push si
        mov si, bx
.pix:   mov bl, [es:di]                 ; what is under it, and the figure's: BLEND's
        mov bh, [gs:si]
        mov al, [fs:bx + FAR_GH_BLEND]
        stosb
        add si, [bp + GD_STEP - 12]
        dec dx
        jnz .pix
        pop si
.nspan: add si, 8
        jmp .gspan
.nplane:
        inc cx
        cmp cx, 4
        jb .plane
        call vga_restore
.out:   add sp, 12
        pop gs
        pop fs
        pop di
        pop si
        pop ds
        pop bp
        ret

; GHOST_UNION: in FIG_WIDE_ALL, after DUST_UNION (the rectangle at [BP-0Ch] x0, [BP-0Eh] x1, [BP-10h] y0,
; [BP-12h] y1): a party member drawn see-through while hidden (GH_SHOWN) and hidden no longer (its STEALTH
; bit cleared) has the whole view drawn, so it is solid at the next step of anyone's; the same once the
; Loader has written GHOST_TAB anew (GH_CHANGED). AX, ES not kept.
ghost_union:
        cmp word [cs:ghost_on], 0
        je .hidden
        cmp word [cs:far_seg], 0
        je .hidden
        push es
        mov es, [cs:far_seg]
        xor al, al
        xchg al, [es:FAR_GH_CHANGED]    ; (read and cleared at once: a Loader write between kept)
        pop es
        test al, al
        jnz .whole
.hidden:
        mov ax, [cs:stealth]
        not ax
        test ax, [cs:gh_shown]
        jz .ret
        not ax
        and [cs:gh_shown], ax
.whole: xor ax, ax
        mov [bp - 0x0C], ax
        mov [bp - 0x10], ax
        mov word [bp - 0x0E], 0x13F
        mov word [bp - 0x12], 0xC7
.ret:   ret

; SHOP_SHINE (site 163), SHINE_TURN: a shop's magic items shine (DSCLOG's, on the sequel). The map's main
; loop turns the palette's colour cycles (the magic items' shine) when the timer has asked for it (1CF0Eh:
; "cmp byte [1424h],0 / jz / call far 2796:047C / mov byte [1424h],0"); a shop runs its own loop (SHOP_LOOP)
; and, as the pointer stands on some things, waits in the game's wait for an event: neither turned them,
; so its magic items stood still. Both now do as the main loop while a shop is open.
; SHOP_SHINE: "or di,di / jz 084Fh-like" (2F7BEh, "0B FF 74 B5"; 4 bytes: the INT, the number and a NOP),
; the test that ends the wait (DI not 0: an event came); with DI 0 the jump made (the way back moved
; SHINE_BACK before the NOP the INT returns to) and the cycles turned.
SHINE_DUE    equ 0x1424             ; (the game's DS) a byte: the timer asks for the colour cycles' turn
SHINE_CALL   equ 0x047C             ; the cycler (2CFDCh: 2796h:047Ch) ...
CYCLER_FROM_DS equ 0x47E0 - 0x2796  ; ... its segment below the game's DS
SHINE_BACK   equ 0x4A               ; (the jz's distance back from the NOP after the site's byte: 4Bh less 1)
shop_shine:
        or di, di
        jnz .out
        push bp
        mov bp, sp
        sub word [bp + 2], SHINE_BACK
        push ds
        push ax
        mov ax, [cs:pointer_ds]
        or ax, ax
        jz .no
        mov ds, ax
        call shine_turn
.no:    pop ax
        pop ds
        pop bp
.out:   iret

; SHINE_TURN: the colour cycles turned if the timer asked and a shop is open. DS the game's; AX, BP and
; the flags not kept.
shine_turn:
        cmp byte [SHOP_SCREEN], 1
        jne .out
        cmp byte [SHINE_DUE], 0
        je .out
        mov ax, ds
        sub ax, CYCLER_FROM_DS
        push ax
        push word SHINE_CALL
        mov bp, sp
        sti
        call far [ss:bp]
        cli
        add sp, 4
        mov byte [SHINE_DUE], 0
        inc word [cs:shine_turns]
.out:   ret
sell_wait db 0                  ; (1 from S's count (SELL_KEY) till the shop's loop has held its way out)

; MAP_KEY: (DSCLOG's) M on the map (its main loop run within the last tick or two, the map the screen on
; show) made O, the game's key for its overhead map; U and I there left as they are, the game's keys for
; the USE and inventory screens (each switches to the other on its own too); OVERHEAD then the key's
; letter. The same key again with the map's loop not run since (that screen up; PANEL_TICK clears
; OVERHEAD) made Escape, the key that closes it; U or I on the other screen of the two, left as it is,
; moves OVERHEAD to it, and any other key there clears it (V's screen, typing...): AX the key, changed or
; kept; others kept. (A peek and the read after it give the same: OVERHEAD changes only on the read,
; MK_READ 1.)
KEY_M       equ 0x326D
KEY_SHIFT_M equ 0x324D
KEY_U       equ 0x1675
KEY_SHIFT_U equ 0x1655
KEY_I       equ 0x1769
KEY_SHIFT_I equ 0x1749
KEY_O       equ 0x186F
        SHARED_map_key
mk_read db 0                    ; (1 when MAP_KEY's key is being read, 0 when peeked at)
overhead db 0                   ; ('m', 'u' or 'i': the screen its key opened, 0 none)

qs_call     dd 0
quick_saves dw 0                ; (saves and loads made, for a look in play)
quick_loads dw 0
pages_back  dw 0                ; (the QUICK page taken off by SAVE_TICK, for a look in play)
greq_data   times 10 db 0
section tailz
save_text   times SAVE_FILE + SAVE_NAME db 0 ; (the Loader's: SAVE_TICK's file and name, +1914: the tail's)
section image

; ---- STORE AND RECALL: DSCLOG's PROBE_RS_CLICK on the sequel's creation screen (rollstore.py) ----
; RS_CLICK (site 83, "roll_store"): "mov cx,16h" (6DE85h, SL's 6625Dh) where the screen's click routine (its
; overlay 6D090h, stub 46DDh) looks the button ([BP+8]) up among its own; STORE and RECALL are the Loader's
; buttons in its window 19503 (rollstore.rav_chunks). STORE keeps the roll on screen (RS_FIELDS: the sheet's
; race, sex, classes and kit, then its hit points, hit points rolled and most PSP; the creature's hit points,
; PSP and six scores; the hit points' most and least, DS:42D6h; the die's total, RL_POOL), RECALL puts it back.
; A stored roll is forgotten at the first button pressed after the race, sex, classes or kit have changed
; (RS_SAME), and RECALL then does nothing. Either way the routine goes on as for a button not its own
; (RS_DONE). After a recall the scores are shown again (the creation overlay's routine for it, WP_STUB's
; entry RS_SCORES, 6CD7Bh, which RL_SUM follows with the totals), then the rest as the die shows a roll: its
; routine (6D3CEh) from where it has rolled the hit points (RS_TAIL, 6D5F1h, with its frame and its byte
; argument 1, a roll), which shows them and the PSP (worked out again from the same scores: no dice), the AC,
; damage and THAC0; each call with the way back in a frame the overlay manager can fix up (RS_FRAMED).
RS_STORE  equ 0x8B0
RS_RECALL equ 0x8B1
RS_DONE   equ 0x6DF97 - 0x6DE88    ; (the routine's way on for another button, less the site's return)
RS_TAIL   equ 0x6D5F1 - 0x6D090    ; (in the die's routine: the overlay's from 6D090h)
RS_SCORES equ 0xB6                 ; (WP_STUB's entry: SL's 0BBh)
RS_HP_MOST equ 0x42D6              ; DS: the hit points' most and least (RL_HP_MAX's; SL's 4996h)
rs_click:
        mov cx, 0x16
        cmp byte [cs:rs_have], 0
        je .which
        call rs_same                        ; (race, sex, classes or kit changed: the roll forgotten)
        je .which
        mov byte [cs:rs_have], 0
.which: cmp word [bp + 8], RS_STORE
        je .ours
        cmp word [bp + 8], RS_RECALL
        jne .out
.ours:  sti
        pushad
        push es
        mov si, sp
        add word [ss:si + 34], RS_DONE      ; (on as for another button)
        xor dl, dl
        cmp word [bp + 8], RS_STORE
        je .xfer
        cmp byte [cs:rs_have], 0
        je .done
        inc dl
.xfer:  call rs_xfer
        or dl, dl
        jz .stored
        inc word [cs:rs_recalls]
        mov byte [cs:cr_age_hold], 1        ; (the stored age shown, not rolled again: CR_AGE)
        mov word [cs:wp_far], RS_SCORES
        mov ax, ds
        add ax, WP_STUB
        mov [cs:wp_far + 2], ax
        call rs_framed                      ; (the scores' routine: another overlay's)
        mov word [cs:wp_far], .tail
        mov [cs:wp_far + 2], cs
        call rs_framed                      ; (the die's routine from where it rolled the hit points)
        mov byte [cs:cr_age_hold], 0
        jmp .done
.tail:  mov [cs:rs_tail + 2], dx            ; (DX: the overlay's segment, the site's way back)
        push word 1                         ; (its byte argument: a roll)
        push cs
        push word .back
        push bp                             ; (the die's frame, as its routine makes it)
        mov bp, sp
        sub sp, 2
        push si
        jmp far [cs:rs_tail]
.back:  add sp, 2
        retf
.stored:
        mov byte [cs:rs_have], 1
        inc word [cs:rs_stores]
.done:  pop es
        popad
.out:   iret

; RS_FRAMED: a far call to WP_FAR with the site's way back (RS_CLICK's, past ES and PUSHAD: SP+2 on entry,
; +36 and +38) in a frame the overlay manager can fix up, as DSCLOG's: the call may load another overlay over
; the click routine's or move it, which leaves the way back where the manager has put it (DX its segment, for
; RS_TAIL). Keeps BX, SI, DI.
        SHARED_rs_framed

; RS_SAME: ZF set if the sheet being made (DS:[1429h]) has the stored roll's race, sex, classes and kit
; (RS_BUF's first 6 bytes, in RS_FIELDS' order: the sheet's +12h, +13h, +1Bh..+1Dh, +3Dh). DS the game's;
; keeps all but flags.
rs_same:
        push es
        push bx
        push ax
        les bx, [WP_CREATION]
        mov al, [es:bx + 0x12]
        cmp al, [cs:rs_buf]
        jne .out
        mov al, [es:bx + 0x13]
        cmp al, [cs:rs_buf + 1]
        jne .out
        mov ax, [es:bx + 0x1B]
        cmp ax, [cs:rs_buf + 2]
        jne .out
        mov al, [es:bx + 0x1D]
        cmp al, [cs:rs_buf + 4]
        jne .out
        mov al, [es:bx + 0x3D]
        cmp al, [cs:rs_buf + 5]
.out:   pop ax
        pop bx
        pop es
        ret

; RS_XFER: the roll's fields (RS_FIELDS, then the hit points' most and least and RL_POOL) into RS_BUF (DL 0)
; or back (DL 1). DS the game's; keeps DL.
rs_xfer:
        push es
        mov si, rs_fields
        mov di, rs_buf
.field: mov al, [cs:si]
        cmp al, 0xFF
        je .rest
        les bx, [WP_CREATION]
        or al, al
        jz .got
        les bx, [CR_CREATURE]
.got:   movzx ax, byte [cs:si + 1]
        add bx, ax
        movzx cx, byte [cs:si + 2]
        call rs_bytes
        add si, 3
        jmp .field
.rest:  push ds
        pop es
        mov bx, RS_HP_MOST
        mov cx, 4
        call rs_bytes
        push cs
        pop es
        mov bx, rl_pool
        mov cx, 2
        call rs_bytes
        pop es
        ret
        SHARED_rs_bytes
; (sheet 0 / creature 1, offset, bytes): the sheet's race, sex, classes, kit (the key), hit points, rolled
; and most PSP; the creature's hit points and PSP, and its six scores
rs_fields db 0, 0x12, 1, 0, 0x13, 1, 0, 0x1B, 3, 0, 0x3D, 1
          db 0, 0x08, 6, 1, 0x00, 4, 1, 0x19, 6, 0, SHEET_AGE, 1, 0xFF
rs_buf    times 6 + 6 + 4 + 6 + 1 + 4 + 2 db 0
rs_have   db 0
rs_tail   dw RS_TAIL, 0
rs_stores  dw 0                 ; (STOREs and RECALLs taken, for a look in play)
rs_recalls dw 0

; ---- FULLER STARTING GEAR: DSCLOG's GEAR_DUE and GEAR_HOLD on the sequel's DONE (startgear.py) ----
; GEAR_DONE (site 85, "gear_done"): "pop cx / push si / nop" (6E2F2h, SL's 666DFh, CR_WEAPONS' place) in the
; creation screen's DONE, between its calls for the new character SI (its sheet index) that give it the game's
; starting gear (6F197h, SL's 67401h) and write it to the roster (6E4D6h, SL's 668C3h, CHARSAVE.GFF's CHAR
; chunk, from memory). The two instructions are done on the stack under the site's way back (the word popped
; into CX is SI, pushed before the call: SI put back). Then, with the Loader there (LOADER_BEAT under
; LOADER_FRESH old), GEAR_DUE set for SI (GEAR_WHO) and the Loader's pass waited for (GEAR_DUE cleared), at
; most GEAR_HOLD_TICKS: its fuller starting gear (startgear.fill, the sequel's items: ravlog's) is then in the
; roster's copy and in View Character's first drawing, which come after (so DSCLOG's GEAR_WAIT, its redraw of
; View Character when the gear came after it, isn't needed here). On a timeout GEAR_DUE stays set: the Loader
; gives the gear at its next pass, the roster's copy without it. All registers kept but CX (the game's).
GEAR_HOLD_TICKS equ 182         ; (about ten seconds, at most)
LOADER_FRESH    equ 91          ; (about five seconds)
gear_done:
        push bp
        mov bp, sp
        mov cx, [bp + 8]                ; (pop cx: the word under the way back)
        mov [bp + 8], si                ; (push si: in its place)
        pop bp
        sti
        push ax
        push bx
        push es
        xor ax, ax
        mov es, ax
        mov bx, [es:0x46C]              ; (the BIOS timer: the wait's start)
        mov ax, bx
        sub ax, [cs:loader_beat]
        cmp ax, LOADER_FRESH
        jae .out                        ; (no Loader: the game's gear, as ever)
        mov ax, si
        mov [cs:gear_who], al
        mov byte [cs:gear_given], 0
        mov byte [cs:gear_due], 1
        inc word [cs:gear_holds]
.wait:  cmp byte [cs:gear_due], 0
        je .out
        mov ax, [es:0x46C]
        sub ax, bx
        cmp ax, GEAR_HOLD_TICKS
        jb .wait
        inc word [cs:gear_timeouts]     ; (the Loader slow: GEAR_DUE left for its next pass)
.out:   pop es
        pop bx
        pop ax
        iret
gear_holds    dw 0              ; (DONEs held for the Loader, and those it was too slow for: for a look in play)
gear_timeouts dw 0

; FIRST SPELLS AND POWERS (SL's PROBE_CR_SPELLS and PSI_GRANT, PSI_ASK, PSI_LIST, PSI_CYCLE: always on).
; The creation screen's DONE (6E0B9h, 5C0:57h) saves the new member (SI) and calls, among others, the
; routine that gives its psionic powers (6E906h, 5C0:2Ah) and then the one that gives a preserver its
; spells (6EA10h, 5C0:2Fh). The sequel's grants are its own (not SL's Grease and Magic Missile): a preserver
; whose level isn't the one the screen opened with (selector 360h's word 0: 0 for a new member) has its 115
; wizard spells' bits cleared (selector 320h, KNOWN_OFF + 15 a member) and is given Wall of Fog at 1st
; level; from 2nd Fireball, Haste, Detect Invisible, Magic Missile, Wall of Fog and four spells drawn by
; rand() from fours (two 1st-level, two 2nd), and at 7th Ice Storm too. The powers: everyone's disciplines
; from the panel's choice (DS:42C0h, into selector 370h's A55h + the member), its 34 powers cleared
; (580:3Eh) and given from selector 360h's table (580:39h): a psionicist's 20 entries at +15h, anyone
; else's five of its discipline at +6 + 5 x the discipline, -1 none; the power's byte at selector 370h's
; 9CDh + 22h a member (bits 1-7 its number, none unknown).
; - PSI_GRANT (site 88): "cmp dx,-1" (6E9C9h the psionicist's loop, 6E9F7h the others'; 3 bytes, the JZ
;   kept): Mind Blank (30) and Detonate (0, which the psionicists' pop-up never lists) given as the game
;   gives them; any other power, once, a pick due (PSI_DUE) and a default (PSI_DEFS), not given. EDIT on a
;   member that keeps its psionicist class and disciplines (PSI_SNAP, at the screen's opening: KP_OPEN)
;   gives none and asks none (PSI_KEEP): its powers are put back.
; - CR_PICKS (site 87): "cmp byte [bp-6],0" (6ED55h; 4 bytes) at the spells' routine's end: for a new
;   member ([CR_EDITING] -1) given spells ([BP-5]), the spells given are taken back and as many picked on
;   the game's CHOOSE A SPELL (688:66h, the level up's), level by level from 1st, each with the pages up
;   to that level (CR_CAP: PICK_ANY, PICK_PAGE and PICK_TOP heed it); then the psionicists' pop-up (688:61h,
;   the level up's) for PSI_DUE picks (PSI_MODE: PSI_COUNT, PSI_LIST, PSI_CYCLE, PSI_CLICK). EXIT on
;   either leaves the rest to the game's own, in spell or table order, less any known (CR_FILL, PSI_FILL).
;   The windows are overlay code of their own: the way back is put in a frame the overlay manager can fix
;   up, as DUAL_KIT's. Then the compare, its flags back (RETF 2).
CR_STUB        equ 0x47B0 - 0x47E0  ; (688h's stub segment less DS's)
CR_SPELL_ENTRY equ 0x66             ; (CHOOSE A SPELL, 93160h)
CR_PSI_ENTRY   equ 0x61             ; (the psionicists' pop-up, 93B62h)
POW_SEG        equ USE_WHO_SEG      ; (selector 370h's segment: the powers, the disciplines)
POW_OFF        equ 0x9CD
POW_SIZE       equ 0x22
POWER_COUNT    equ 34
DISC_OFF       equ 0xA55
PSI_SHOWN      equ 0x9D7B           ; DS: the discipline the pop-up shows, a byte a member
MIND_BLANK     equ 30
PSI_CLASS      equ 0x0C
cr_picks:
        call kp_if_frame        ; (interrupts as the caller had them: RETF 2 keeps these flags)
        pushad
        push es
        mov bx, sp              ; the interrupt frame at BX+34: IP, CS, flags
        push word [ss:bx + 36]
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        mov di, [bp]            ; (the routine's frame: [DI+6] the member, [DI-5] spells given)
        mov si, [ss:di + 6]
        cmp si, 4
        jae .back
        cmp byte [ss:di - 5], 0
        je .shinobi
        cmp word [CR_EDITING], -1
        jne .psi
        call cr_spells
        jmp .psi
.shinobi:
        call sh_first_spells    ; (a new Shinobi of 6th thief level on: THE SHINOBI'S SPELLS)
.psi:   call psi_ask
.back:  mov byte [cs:psi_due], 0
        mov byte [cs:psi_keep], 0
        pop bp
        pop ax                  ; the way back, as the overlay manager has left it
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
        pop es
        popad
        cmp byte [bp - 6], 0
        retf 2

; CR_SPELLS: member SI (DS the game's) given wizard spells by the game: those taken back (CR_DEFS, CR_DUE
; by level) and as many picked on CHOOSE A SPELL; on EXIT the rest from CR_DEFS (CR_FILL). Registers changed.
cr_spells:
        call known_bits         ; (ES:BX the member's bits)
        xor di, di
.clear: mov byte [cs:cr_due + di], 0
        inc di
        cmp di, WIZ_LEVELS
        jb .clear
        xor di, di              ; (DI the spells given)
        xor al, al
.each:  cmp al, [SPELL_STARTS + WIZ_LEVELS]
        jae .got
        call bit_known
        jz .next
        push fs
        call tail_fs
        mov [fs:cr_defs + di], al   ; (CR_DEFS: the tail's)
        pop fs
        inc di
        call wiz_level          ; (DL its level)
        movzx dx, dl
        push bx
        mov bx, dx
        inc byte [cs:cr_due + bx - 1]
        pop bx
        call bit_clear
.next:  inc al
        jmp .each
.got:   mov [cs:cr_n], di
        mov [cs:cr_left], di
        or di, di
        jz .ret
        call cr_scholar         ; (a new Scholar: one more for each preserver level)
        inc word [cs:cr_members]
        mov cl, 1               ; (CL the level, CH its picks)
.level: movzx di, cl
        mov ch, [cs:cr_due + di - 1]
.one:   or ch, ch
        jz .up
        mov [cs:cr_cap], cl
        call cr_one
        jc .fill
        dec word [cs:cr_left]
        inc word [cs:cr_picked]
        movzx di, cl
        dec byte [cs:cr_due + di - 1]   ; (CR_DUE: those still due at each level, for CR_FILL)
        dec ch
        jmp .one
.up:    inc cl
        cmp cl, WIZ_LEVELS
        jbe .level
        jmp .done
.fill:  call cr_fill
.done:  mov byte [cs:cr_cap], 0
.ret:   ret

; CR_SCHOLAR: (CR_SPELLS', the spells given counted) a new member SI with the Scholar kit awake picks one
; more 1st-level spell for each of its preserver levels (SL's PROBE_CR_SPELLS: KIT_MADE's CL), CR_DUE's and
; CR_LEFT's. Counted (SCHOLAR_MADE). All registers kept.
cr_scholar:
        push ax
        push bx
        push es
        mov ax, si
        call kit_sheet_ax
        call kit_is_b
        db KIT_SCHOLAR
        jne .out
        call kit_level
        movzx ax, al
        add [cs:cr_due], al
        add [cs:cr_left], ax
        add [cs:scholar_made], ax
.out:   pop es
        pop bx
        pop ax
        ret

; CR_ONE: CHOOSE A SPELL for member SI; CF set if it was left with no spell learnt. CX kept; DS the game's.
cr_one:
        push cx
        call wiz_count
        push ax
        mov ax, ds
        add ax, CR_STUB
        mov [cs:cr_far + 2], ax
        mov word [cs:cr_far], CR_SPELL_ENTRY
        push si
        call far [cs:cr_far]
        add sp, 2
        inc word [cs:cr_windows]
        call wiz_count
        pop cx
        cmp ax, cx
        je .none
        pop cx
        clc
        ret
.none:  pop cx
        stc
        ret

; CR_FILL: member SI given CR_LEFT more of CR_DEFS, less any known: first those of a level with picks
; still due there (CR_DUE), in their order; then any still left, in their order. Registers changed.
cr_fill:
        call known_bits
        xor di, di
.level: cmp word [cs:cr_left], 0
        je .ret
        cmp di, [cs:cr_n]
        jae .rest
        push fs
        call tail_fs
        mov al, [fs:cr_defs + di]
        pop fs
        inc di
        call bit_known
        jnz .level
        call wiz_level
        movzx dx, dl
        push bx
        mov bx, dx
        cmp byte [cs:cr_due + bx - 1], 0
        je .later
        dec byte [cs:cr_due + bx - 1]
        pop bx
        call bit_set
        dec word [cs:cr_left]
        inc word [cs:cr_filled]
        jmp .level
.later: pop bx
        jmp .level
.rest:  xor di, di
.each:  cmp word [cs:cr_left], 0
        je .ret
        cmp di, [cs:cr_n]
        jae .ret
        push fs
        call tail_fs
        mov al, [fs:cr_defs + di]
        pop fs
        inc di
        call bit_known
        jnz .each
        call bit_set
        dec word [cs:cr_left]
        inc word [cs:cr_filled]
        jmp .each
.ret:   ret

; WIZ_COUNT: AX the wizard spells member SI knows (KNOWN_BITS). DS the game's; others kept.
wiz_count:
        push bx
        push dx
        push es
        call known_bits
        xor dx, dx
        xor al, al
.each:  cmp al, [SPELL_STARTS + WIZ_LEVELS]
        jae .out
        call bit_known
        jz .next
        inc dx
.next:  inc al
        jmp .each
.out:   push cx                 ; (and the new spells known: NEW SPELLS)
        mov byte [cs:ns_want], 1
        mov cl, 1
.levels:
        call ns_level_new
        add dx, ax
        inc cl
        cmp cl, 2
        jbe .levels
        pop cx
        mov ax, dx
        pop es
        pop dx
        pop bx
        ret

; WIZ_LEVEL: DL wizard spell AL's level (SPELL_STARTS). DS the game's; others kept.
wiz_level:
        push bx
        mov bx, 1
.each:  cmp al, [SPELL_STARTS + bx]
        jb .out
        inc bx
        cmp bx, WIZ_LEVELS
        jb .each
.out:   mov dl, bl
        pop bx
        ret

; BIT_SET, BIT_CLEAR: spell AL's bit in ES:BX's (KNOWN_BITS) set, cleared. All registers kept.
bit_set:
        push ax
        push bx
        push cx
        call bit_place
        or [es:bx], al
        pop cx
        pop bx
        pop ax
        ret
bit_clear:
        push ax
        push bx
        push cx
        call bit_place
        not al
        and [es:bx], al
        pop cx
        pop bx
        pop ax
        ret
bit_place:                      ; (BX the byte, AL the bit's mask; CX changed)
        mov cl, al
        and cl, 7
        movzx ax, al
        shr ax, 3
        add bx, ax
        mov al, 1
        shl al, cl
        ret

; PSI_ASK: member SI (DS the game's): PSI_KEEP's powers put back, or PSI_DUE picked on the psionicists'
; pop-up (the discipline shown its own for one not a psionicist, the first for a psionicist), the rest on
; EXIT from PSI_DEFS (PSI_FILL). Registers changed.
psi_ask:
        mov ax, ds
        add ax, POW_SEG
        mov es, ax
        imul bx, si, POW_SIZE
        add bx, POW_OFF
        cmp byte [cs:psi_keep], 0
        je .ask
        xor di, di
.back:  mov al, [cs:psi_saved + di]
        mov [es:bx + di], al
        inc di
        cmp di, POWER_COUNT
        jb .back
        inc word [cs:psi_kept]
        ret
.ask:   cmp byte [cs:psi_due], 0
        je .ret
        xor al, al
        cmp byte [cs:psi_isp], 0
        jne .shown
        mov al, [cs:psi_disc]
.shown: mov [PSI_SHOWN + si], al
        inc word [cs:psi_asks]
        mov byte [cs:psi_mode], 1
        mov ax, ds
        add ax, CR_STUB
        mov [cs:cr_far + 2], ax
        mov word [cs:cr_far], CR_PSI_ENTRY
        push si
        call far [cs:cr_far]
        add sp, 2
        mov byte [cs:psi_mode], 0
        movzx cx, byte [PICK_SHOWN]     ; (the picks left: none, or EXIT's)
        cmp cl, [cs:psi_due]
        jbe .fill
        movzx cx, byte [cs:psi_due]
.fill:  mov ax, ds
        add ax, POW_SEG
        mov es, ax
        imul bx, si, POW_SIZE
        add bx, POW_OFF
        xor di, di
.each:  jcxz .ret
        cmp di, [cs:psi_n]
        jae .ret
        movzx ax, byte [cs:psi_defs + di]
        inc di
        push bx
        add bx, ax
        test byte [es:bx], 0xFE
        jnz .known
        and byte [es:bx], 1     ; (as 580:39h gives one)
        or byte [es:bx], 2
        inc word [cs:psi_filled]
        dec cx
.known: pop bx
        jmp .each
.ret:   ret

; PSI_GRANT (site 88): "cmp dx,-1" in the powers' routine (DX the power, DI the member, SI the entry,
; [BP-5] 1 a psionicist, [BP-4] the discipline): ZF set (none given) for -1, a pick (PSI_DUE) or PSI_KEEP.
psi_grant:
        push ax
        push bx
        or si, si
        jnz .which
        call psi_start
.which: cmp dx, -1
        je .none
        cmp di, 4
        jae .give
        cmp byte [cs:psi_keep], 0
        jne .none
        cmp dx, MIND_BLANK
        je .give
        or dx, dx
        jz .give
        xor bx, bx
.seen:  cmp bx, [cs:psi_n]
        jae .new
        cmp [cs:psi_defs + bx], dl
        je .none
        inc bx
        jmp .seen
.new:   cmp bx, POWER_COUNT
        jae .none
        mov [cs:psi_defs + bx], dl
        inc word [cs:psi_n]
        inc byte [cs:psi_due]
.none:  mov bx, sp
        or word [ss:bx + 8], 0x40       ; (ZF: the JZ past the grant)
        jmp .out
.give:  mov bx, sp
        and word [ss:bx + 8], ~0x40
.out:   pop bx
        pop ax
        iret
; PSI_START: the routine's first entry: the picks none, PSI_ISP and PSI_DISC its, PSI_KEEP for an EDIT of
; PSI_SNAP's member with the same psionicist class and disciplines (selector 370h's A55h, set by now).
psi_start:
        mov byte [cs:psi_due], 0
        mov word [cs:psi_n], 0
        mov byte [cs:psi_keep], 0
        mov al, [bp - 5]
        mov [cs:psi_isp], al
        mov al, [bp - 4]
        mov [cs:psi_disc], al
        cmp word [CR_EDITING], -1
        je .ret
        cmp byte [cs:psi_snap_ok], 0
        je .ret
        mov ax, di
        cmp al, [cs:psi_snap_who]
        jne .ret
        mov al, [bp - 5]
        cmp al, [cs:psi_snap_isp]
        jne .ret
        push es
        push bx
        mov ax, ds
        add ax, POW_SEG
        mov es, ax
        mov al, [es:DISC_OFF + di]
        and al, 7
        pop bx
        pop es
        cmp al, [cs:psi_snap_disc]
        jne .ret
        mov byte [cs:psi_keep], 1
.ret:   ret

; PSI_SNAP: from KP_OPEN, an EDIT's member ([CR_EDITING], 0-3): its powers, disciplines and whether a
; psionicist (its sheet's classes), for PSI_KEEP. DS the game's; all registers kept.
psi_snap:
        pusha
        push es
        mov byte [cs:psi_snap_ok], 0
        mov si, [CR_EDITING]
        cmp si, 4
        jae .out
        mov ax, si
        mov [cs:psi_snap_who], al
        les bx, [SHEETS_PTR]
        imul ax, si, SHEET_SIZE
        add bx, ax
        xor al, al
        mov cx, 3
.class: cmp byte [es:bx + SH_CLASSES], PSI_CLASS
        jne .other
        mov al, 1
.other: inc bx
        loop .class
        mov [cs:psi_snap_isp], al
        mov ax, ds
        add ax, POW_SEG
        mov es, ax
        mov al, [es:DISC_OFF + si]
        and al, 7
        mov [cs:psi_snap_disc], al
        imul bx, si, POW_SIZE
        add bx, POW_OFF
        xor di, di
.copy:  mov al, [es:bx + di]
        mov [cs:psi_saved + di], al
        inc di
        cmp di, POWER_COUNT
        jb .copy
        mov byte [cs:psi_snap_ok], 1
.out:   pop es
        popa
        ret

; (SITE's way back is the byte after the site's number: the NOP of a 4-byte site, so a jump's target is counted
; from there.)
; PSI_COUNT (site 95): "or dx,dx / jz" (93B95h; 4 bytes) in the pop-up's opening (DX the psionicist's
; level, 0 none: the window not opened): in PSI_MODE the picks left (DS:43ECh) PSI_DUE's, in WEAPON PICKS'
; LV_MODE LV_LEFT's, the window opened.
psi_count:
        push ax
        mov al, [cs:lv_left]            ; (WEAPON PICKS' weapon mode: its picks left)
        cmp byte [cs:lv_mode], 0
        jne .shown
        mov al, [cs:psi_due]
        cmp byte [cs:psi_mode], 0
        je .pop
.shown: mov [PICK_SHOWN], al
        pop ax
        iret
.pop:   pop ax
.game:  or dx, dx
        jnz .out
        push bp
        mov bp, sp
        add word [bp + 2], 0x93BD3 - 0x93B98
        pop bp
.out:   iret

; PSI_LIST (site 96): "or ax,ax / jz" (93E1Bh; 4 bytes) in the list of the discipline shown (AX 1 when the
; member has power SI): listed when not; a known one listed too (to raise its number) but in PSI_MODE.
psi_list:
        push bp
        mov bp, sp
        or ax, ax
        jz .list
        cmp byte [cs:psi_mode], 0
        je .out
        add word [bp + 2], 0x93E4A - 0x93E1E
        jmp .out
.list:  add word [bp + 2], 0x93E41 - 0x93E1E
.out:   pop bp
        iret

; PSI_CYCLE (site 97): "inc byte [bx-6285h]" (93FF1h; the discipline button): the next discipline, but in
; PSI_MODE for one not a psionicist (its own only).
psi_cycle:
        cmp byte [cs:psi_mode], 0
        je .inc
        cmp byte [cs:psi_isp], 0
        je .out
.inc:   inc byte [bx + PSI_SHOWN - 0x10000]
.out:   iret

; PSI_CLICK (site 98): "or al,al / jz" (94245h; 4 bytes) where a power's button is clicked (AL 1 when the
; member has it: the game raises its number): in PSI_MODE a known one does nothing.
psi_click:
        push bp
        mov bp, sp
        or al, al
        jz .give
        cmp byte [cs:psi_mode], 0
        je .out
        add word [bp + 2], 0x94389 - 0x94248
        jmp .out
.give:  add word [bp + 2], 0x94269 - 0x94248
.out:   pop bp
        iret

; PICK_TOP (site 99): "cmp ax,[bp-2]" (93831h; 3 bytes) where CHOOSE A SPELL's level button goes on a page
; (AX the next, [BP-2] the highest the reader casts): no higher than PICK_MOST. Its flags back.
; PICK_MOST: AL the highest spell level CHOOSE A SPELL offers: CR_CAP while set (creation's picks), else
; WIZ_PICK_MOST with RULE_LEVEL_10 (the owner's, 2026-11-26: no 10th-level wizard slots, so a preserver's
; level up from 20th, where the game opens on level / 2, never offers the sequel's four 10th-level spells,
; 111-114, Dome of Invulnerability, Magical Plague, Rift, Wall of Ash: monsters' only), else 0 (none).
; Others kept.
WIZ_PICK_MOST equ 9
pick_most:
        mov al, [cs:cr_cap]
        or al, al
        jnz .ret
        test word [cs:rules], RULE_LEVEL_10
        jz .ret
        mov al, WIZ_PICK_MOST
.ret:   ret
pick_top:
        push cx
        mov cx, [bp - 2]
        push ax
        call pick_most
        or al, al
        jz .most
        cmp cl, al
        jbe .most
        movzx cx, al
.most:  pop ax
        call sh_page_top        ; (a Shinobi's: its own levels, THE SHINOBI'S SPELLS)
.cmp:   push bp
        mov bp, sp              ; ([BP+2] CX, +4 IP, +6 CS, +8 the flags)
        cmp ax, cx
        pushf
        pop cx
        and cx, 0x08D5
        and word [bp + 8], ~0x08D5
        or [bp + 8], cx
        pop bp
        pop cx
        iret

cr_far     dd 0
cr_cap     db 0                 ; (the spell levels on offer up to this one: 0 none set)
cr_due     times WIZ_LEVELS db 0
section tailz
cr_defs    times 128 db 0
section image
cr_n       dw 0
cr_left    dw 0
psi_defs   times POWER_COUNT db 0
psi_n      dw 0
psi_due    db 0
psi_mode   db 0
psi_isp    db 0
psi_disc   db 0
psi_keep   db 0
psi_snap_ok db 0
psi_snap_who db 0
psi_snap_isp db 0
psi_snap_disc db 0
psi_saved  times POWER_COUNT db 0
cr_members dw 0                 ; (counts, for a look in play)
cr_windows dw 0
cr_picked  dw 0
cr_filled  dw 0
psi_asks   dw 0
psi_filled dw 0
psi_kept   dw 0

; LEVEL CAP BY XP: DSCLOG's PROBE_LEVEL, LEVEL_ROOM, PROBE_XP_NEXT, PROBE_HD_ROLL and PROBE_HD_CON (RULE_LEVEL_10,
; always on) with the owner's cap (2026-11-25): a class goes up a level while its next level needs no more
; than its share of RAV_XP_CAP, 5,625,000 (the whole for one class, an equal share for several, a human's
; what its old classes' levels left), past the game's cap of 15 to RAV_XP's 30th level (the owner's, 2026-11-25:
; no stop at 20th). Most characters of three classes reach 15th, of one or two higher, one class 20th to 30th
; (ravager.level_most). The sites:
; - LV_UP (site 110, "level_cap_up"): "cmp byte es:[bx+1Eh],0Fh" (959A5h; 5 bytes) in the level up
;   (95860h on; SI the member, DI the class's place, ES:BX the sheet + DI), then "jb" to the new level.
; - LV_VIEW (site 111, "level_cap_view"): the same compare (6FB51h) on View Character, its copy of the sheet
;   (classes as the XP table's rows, 1-8; SI the place), then "je" past the next level's XP: none at the cap.
; - LV_CLAMP (site 112, "level_clamp"): "add ax,3" (958BDh; 3 bytes) where the level up holds the sheet's XP
;   to the XP of 3 levels on (entry level + 3, then its read at 958E3h): past RAV_XP's last (29) the game
;   would read on into the next class's row, so from 27th no hold (XP_TOP: XP_NEED's answer the most, so
;   the game's "jae" passes the hold by); XP_HOLD holds it at the share. XP_NEED answers RAV_XP's for an
;   index past the game's 20 entries (all eight reads: the level up's, View Character's).
; - XP_SUFFIX (site 117, "xp_suffix"): View Character's "push 1386h", the ")" after the next level's XP: for
;   a character of more than one class (not a human) the class whose next level it is, as SL's (" F)").
; Levels 16-30 need no other change: hit points (the fixed gains past 9th or 10th) and THAC0 are the game's
; formulas (a byte, read signed: a warrior's -9 at 30th), the slots RAV_SLOTS (to 30th), the saves
; SAVE_BASE's table (its last row on), the thief skills THIEF_TABLE (to 17th, then flat), a ranger's casting
; level RANGER_MOST (9); the game's one psionic power a level stops when none is left to learn. New characters start at 6th to 8th (6C3A4h-6C4E7h), far
; below any share.
RULE_LEVEL_10 equ 128
RAV_XP_CAP    equ 5625000
RAV_LEVELS    equ 30                    ; (RAV_XP's entries, 0-29: the next level's XP; the owner's, 2026-11-25)
RAV_GAME_XP   equ 20                    ; (the game's table's: past it XP_NEED answers RAV_XP's)
LV_CAP_GAME   equ 15                    ; (the game's cap)
lv_up:
        pushad
        push es
        mov di, sp
        test word [cs:rules], RULE_LEVEL_10
        jz lv_game
        mov dx, [ss:di + 2]             ; (the place: the game's DI)
        mov al, 1                       ; (the sheet's classes, 1-17)
        jmp lv_room
lv_view:
        pushad
        push es
        mov di, sp
        test word [cs:rules], RULE_LEVEL_10
        jz lv_game
        mov dx, si
        xor al, al                      ; (the screen's copy: rows)
lv_room:
        sub bx, dx
        call level_room
        jc .below
        inc word [cs:lv_tops]
        cmp al, al                      ; (at the cap: "cmp 15,15")
        jmp dual_flags
.below: inc word [cs:lv_rooms]
        mov al, 0
        cmp al, 1                       ; (below it: "cmp 0,1")
        jmp dual_flags
lv_game:
        cmp byte [es:bx + 0x1E], LV_CAP_GAME
        jmp dual_flags
lv_rooms dw 0                           ; (answers below the cap and at it, for a look in play)
lv_tops  dw 0
;
; LV_CLAMP: AX the level (+ 3 here); past RAV_LEVELS - 1 that, and XP_TOP for XP_NEED's next answer.
lv_clamp:
        add ax, 3
        test word [cs:rules], RULE_LEVEL_10
        jz .out
        cmp ax, RAV_LEVELS - 1
        jbe .share
        mov ax, RAV_LEVELS - 1
        mov byte [cs:xp_top], 1
.share: call xp_hold
.out:   iret
xp_top db 0                             ; (XP_NEED's next answer the most: no hold)
; XP_HOLD (the owner's, 2026-11-25: XP stops growing at the cap): the sheet's XP (+0, a dword) no more than
; its share (LR_SHARE), ES:BX the sheet + DI (the class's place) as the level up has them at LV_CLAMP's
; site. The game's hold after it may take it lower. All registers kept.
xp_hold:
        pushad
        sub bx, di
        mov byte [cs:lr_classes], 1
        call lr_share
        cmp [es:bx], eax
        jbe .ret
        mov [es:bx], eax
        inc word [cs:xp_holds]
.ret:   popad
        ret
xp_holds dw 0                           ; (XP held at the share, for a look in play)
;
; LEVEL_ROOM: CF set if the class in place DX (0-2) of sheet ES:BX may go up a level under RAV_XP_CAP: its
; next level's XP (RAV_XP_AT at its level) no more than its share, and its level below RAV_LEVELS. AL 1: the
; sheet's classes (1-17, CLASS_ROWS), 0: rows (1-8, View Character's copy). One class: the whole cap.
; Several (not a human): an equal share each, as the game shares out XP. A human (the race, +12h, 1) who
; changed class: what is left after the XP its old classes' levels needed (places 1 and 2: the change of
; class, 9493Ch, puts the new class first at 1st level and the sheet's XP at 0). All registers kept.
level_room:
        pushad
        mov [cs:lr_classes], al
        call lr_share
        mov edi, eax
        mov si, sp
        mov si, [ss:si + 20]            ; (the place: DX as it came, from PUSHAD's)
        movzx cx, byte [es:bx + si + 0x1E]
        call lr_need
        jc .no
        cmp eax, edi
        ja .no
        popad
        stc
        ret
.no:    popad
        clc
        ret
; LR_SHARE: EAX the XP sheet ES:BX's classes may gather under RAV_XP_CAP (LEVEL_ROOM's share; LR_CLASSES
; as it says). Others kept.
lr_share:
        push ecx
        push edx
        push si
        mov eax, RAV_XP_CAP
        cmp byte [es:bx + 0x12], 1
        je .human
        xor cx, cx                      ; (how many classes)
        xor si, si
.count: cmp byte [es:bx + si + 0x1B], 0
        je .counted
        inc cx
.counted:
        inc si
        cmp si, 3
        jb .count
        xor edx, edx
        movzx ecx, cx
        jecxz .out
        div ecx
        jmp .out
.human: push edi
        mov edi, eax
        mov si, 1                       ; (the old classes: places 1 and 2)
.old:   movzx cx, byte [es:bx + si + 0x1E]
        jcxz .next_old
        dec cx                          ; (the XP its level needed: the entry before it)
        call lr_need
        jc .next_old
        sub edi, eax
        jnc .next_old
        xor edi, edi
.next_old:
        inc si
        cmp si, 3
        jb .old
        mov eax, edi
        pop edi
.out:   pop si
        pop edx
        pop ecx
        ret
; LR_NEED: EAX the XP the class in place SI of sheet ES:BX needs at index CX; CF set for none (no class,
; past the table). Others kept.
lr_need:
        push bx
        push dx
        push si
        movzx si, byte [es:bx + si + 0x1B]
        cmp byte [cs:lr_classes], 0
        je .row
        cmp si, CLASS_ROW_LAST
        ja .none
        movzx si, byte [cs:si + class_rows]
.row:   or si, si
        jz .none
        cmp si, 8
        ja .none
        cmp cx, RAV_LEVELS - 1
        ja .none
        mov dx, si
        dec dx
        mov dh, cl
        call rav_xp_at
        pop si
        pop dx
        pop bx
        clc
        ret
.none:  pop si
        pop dx
        pop bx
        stc
        ret
lr_classes db 0
; the sheet's classes 1-17 to the XP table's rows 1-8 (the game's map at 360h:9Dh: ravager.CLASS_ROWS)
CLASS_ROW_LAST equ 17
class_rows db 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 4, 5, 6, 7, 7, 7, 7, 8
;
; RAV_XP_AT: EAX the XP the class of row DL (0-7) needs at index DH (0-29): RAV_XP's, tables.RAV_XP, AD&D's
; (RULE_HI_TABLES's; XP_FIXES' among them), whatever the rules. Others kept.
rav_xp_at:
        push bx
        movzx bx, dl
        imul bx, bx, RAV_LEVELS
        add bl, dh
        adc bh, 0
        shl bx, 2
        push fs
        call tail_fs
        mov eax, [fs:bx + rav_xp]       ; (RAV_XP: the tail's)
        pop fs
        pop bx
        ret
; tables.RAV_XP, a row a class, the XP of levels 1-30 (past the game's table, 20 entries, the owner's AD&D
; tables, 2026-11-25)
section tail
rav_xp:
        dd 0, 1500, 3000, 6000, 13000, 27500, 55000, 110000, 225000, 450000, 675000, 900000, 1125000, 1350000, 1575000, 1800000, 2025000, 2250000, 2475000, 2700000, 2925000, 3150000, 3375000, 3600000, 3825000, 4050000, 4275000, 4500000, 4725000, 4950000 ; cleric
        dd 0, 2000, 4000, 7500, 12500, 20000, 35000, 60000, 90000, 125000, 200000, 300000, 750000, 1500000, 3000000, 3500000, 4000000, 4500000, 5000000, 5500000, 6000000, 6500000, 7000000, 7500000, 8000000, 8500000, 9000000, 9500000, 10000000, 10500000 ; druid
        dd 0, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 250000, 500000, 750000, 1000000, 1250000, 1500000, 1750000, 2000000, 2250000, 2500000, 2750000, 3000000, 3250000, 3500000, 3750000, 4000000, 4250000, 4500000, 4750000, 5000000, 5250000, 5500000 ; fighter
        dd 0, 2250, 4500, 9000, 18000, 36000, 75000, 150000, 300000, 600000, 900000, 1200000, 1500000, 1800000, 2100000, 2400000, 2700000, 3000000, 3300000, 3600000, 3900000, 4200000, 4500000, 4800000, 5100000, 5400000, 5700000, 6000000, 6300000, 6600000 ; gladiator
        dd 0, 2500, 5000, 10000, 20000, 40000, 60000, 90000, 135000, 250000, 375000, 750000, 1125000, 1500000, 1875000, 2250000, 2625000, 3000000, 3375000, 3750000, 4125000, 4500000, 4875000, 5250000, 5625000, 6000000, 6375000, 6750000, 7125000, 7500000 ; preserver
        dd 0, 2200, 4400, 8800, 16500, 30000, 55000, 100000, 200000, 400000, 600000, 800000, 1000000, 1200000, 1500000, 1800000, 2100000, 2400000, 2700000, 3000000, 3300000, 3600000, 4000000, 4400000, 4800000, 5200000, 5600000, 6000000, 6500000, 7000000 ; psionicist
        dd 0, 2250, 4500, 9000, 18000, 36000, 75000, 150000, 300000, 600000, 900000, 1200000, 1500000, 1800000, 2100000, 2400000, 2700000, 3000000, 3300000, 3600000, 3900000, 4200000, 4500000, 4800000, 5100000, 5400000, 5700000, 6000000, 6300000, 6600000 ; ranger
        dd 0, 1250, 2500, 5000, 10000, 20000, 40000, 70000, 110000, 160000, 220000, 440000, 660000, 880000, 1100000, 1320000, 1540000, 1760000, 1980000, 2200000, 2420000, 2640000, 2860000, 3080000, 3300000, 3520000, 3740000, 3960000, 4180000, 4400000 ; thief
section image
;
; LV_ORDINAL (site 118, "level_ordinal"): "mov ax,2B7Eh" (959D3h; 3 bytes) in the level up's message ("%Fs is
; %d%s level %Fs", DS:2B68h), AX the new level when it is above 3: the game pushes "th" (DS:2B7Eh, used nowhere
; else) for all of them, so past 20th "21th". DS:2B7Eh made English's ending for AX ("st", "nd", "rd", "th":
; 11th to 13th "th") and AX it. Others kept.
LV_TH equ 0x2B7E
lv_ordinal:
        push bx
        push cx
        push dx
        xor dx, dx
        mov cx, 100
        div cx                          ; (DX the level's last two digits)
        mov ax, dx
        mov bx, 'th'
        cmp ax, 11
        jb .ones
        cmp ax, 13
        jbe .put
.ones:  mov cl, 10
        div cl                          ; (AH the last digit)
        cmp ah, 1
        jne .two
        mov bx, 'st'
        jmp .put
.two:   cmp ah, 2
        jne .three
        mov bx, 'nd'
        jmp .put
.three: cmp ah, 3
        jne .put
        mov bx, 'rd'
.put:   mov [LV_TH], bx
        mov ax, LV_TH
        pop dx
        pop cx
        pop bx
        iret
;
; XP_SUFFIX: replaces "push 1386h" (6FC08h; 3 bytes) in View Character's "EXP:10301 (16000)", where the game
; pushes ")" (DS:1386h) after the next level's XP: the least of its classes' ([BP-6], a dword, never 0 here),
; the routine's character ([BP+0Ah], far) the screen's copy (classes as rows 1-8, +12h the race). For a
; character of more than one class (not a human), DSCLOG2's text instead (the game's DS, pushed before,
; becomes CS): the class whose next level that is, then ")": " F)", " Pr/T)" if two are due at once.
XP_CLOSE equ 0x1386
xp_suffix_site:
        pop word [cs:x_ip]
        pop word [cs:x_cs]
        pop word [cs:x_fl]
        pushad
        push es
        mov byte [cs:xp_ours], 0
        test word [cs:rules], RULE_LEVEL_10
        jz .out
        les bx, [bp + 0x0A]
        cmp byte [es:bx + 0x12], 1
        je .out                         ; (a human: the game's ")")
        cmp byte [es:bx + 0x1C], 0
        je .out                         ; (one class: the game's ")")
        mov di, xp_suffix + 1
        xor dx, dx
.slot:  push bx
        add bx, dx
        movzx si, byte [es:bx + 0x1B]   ; the class (a row)
        movzx cx, byte [es:bx + 0x1E]   ; its level
        pop bx
        or si, si
        jz .next
        cmp si, 8
        ja .next
        xor al, al
        call level_room                 ; (at the cap: none)
        jnc .next
        push dx
        mov dx, si
        dec dx
        mov dh, cl
        call rav_xp_at
        pop dx
        cmp eax, [bp - 6]
        jne .next
        cmp di, xp_suffix + 1
        je .letters
        mov byte [cs:di], '/'
        inc di
.letters:
        add si, si
        mov ax, [cs:si + class_letters]
        mov [cs:di], al
        inc di
        or ah, ah
        jz .one
        mov [cs:di], ah
        inc di
.one:   mov byte [cs:xp_ours], 1
.next:  inc dx
        cmp dx, 3
        jb .slot
        mov word [cs:di], ')'           ; (and its NUL)
.out:   pop es
        popad
        cmp byte [cs:xp_ours], 0
        je .game
        add sp, 2                       ; the game's DS
        push cs
        push xp_suffix
        jmp .back
.game:  push XP_CLOSE
.back:  push word [cs:x_fl]
        push word [cs:x_cs]
        push word [cs:x_ip]
        iret
x_ip    dw 0
x_cs    dw 0
x_fl    dw 0
xp_ours db 0
xp_suffix db ' ', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
; by row, 1-8
class_letters db 0, 0, 'C', 0, 'D', 0, 'F', 0, 'G', 0, 'P', 'r', 'P', 's', 'R', 0, 'T', 0
;
; A THIEF'S HIT DICE (SL's PROBE_HD_ROLL and PROBE_HD_CON, RULE_LEVEL_10): the game keeps one "dice up to this
; level" for thieves and psionicists together (the rogues' group, 9: then +2 a level); AD&D's thief rolls a d6
; to 10th, its psionicist to 9th (the owner's table, 2026-11-25). A thief's goes to 10, the psionicist's stays
; 9, in the three places it counts:
; - HD_ROLL (site 113, "thief_hd_roll"): "mov al,es:[bx+1]" (94FECh; 5 bytes) where a new level's hit points
;   are a roll or the fixed gain (94F60h: ES:BX the class's group, [BP+8] the class).
; - HD_CON (site 114, "thief_hd_con"): "cmp al,es:[bx+1]" (95460h; 5 bytes, then "jle") where the most hit
;   points (9535Ch on) count the levels CON's bonus and the dice apply to: AL a group's level, ES:BX the
;   group, [BP-4] the sheet (far) and CX which of its classes.
; - HD_CLAMP (site 115, "thief_hd_clamp"): "mov al,es:[bx+1]" (95471h; 5 bytes) after it, the levels kept.
hd_roll:
        mov al, [es:bx + 1]
        test word [cs:rules], RULE_LEVEL_10
        jz .done
        cmp al, 9
        jne .done
        cmp word [bp + 8], THIEF_CLASS
        jne .done
        inc al
        inc word [cs:hd_tens]
.done:  iret
hd_con:
        pushad
        push es
        mov di, sp
        mov dl, [es:bx + 1]
        call hd_thief
        cmp al, dl
        jmp dual_flags
hd_clamp:
        push dx
        mov dl, [es:bx + 1]
        call hd_thief
        mov al, dl
        pop dx
        iret
; HD_THIEF: DL a group's dice levels: 10 for 9 when the class in place CX of sheet [BP-4] is a thief.
hd_thief:
        test word [cs:rules], RULE_LEVEL_10
        jz .ret
        cmp dl, 9
        jne .ret
        push es
        push bx
        les bx, [bp - 4]
        add bx, cx
        cmp byte [es:bx + 0x1B], THIEF_CLASS
        pop bx
        pop es
        jne .ret
        inc dl
.ret:   ret
hd_tens dw 0                            ; (thieves' 10th-level dice, for a look in play)
;
; SAVING THROWS AS IN AD&D (RULE_HI_TABLES, AD&D's class tables; save_bands.inc, DSCLOG's the same): the
; game's saves (954D2h: for each class group 0-3, priest, warrior, wizard, rogue, at the best level of its
; classes in it, and each of the five saves) are the group's 1st-level save less (level - 1) x a rate / 100,
; but no more than the table's third byte (4D0h:6Ch + group x 15 + save x 3), AD&D's best save and not the
; most a save improves: a warrior stays at 11/11/11/13/11 from 10th level (SL's 877EBh the same); and
; psionicists are thieves. SAVE_BASE (site 116, "save_table"): "mov al,es:[bx+6Ch]" (955DFh; 5 bytes)
; before "cbw / sub ax,[bp-2]". The sheets: SHEETS_PTR, SHEET_SIZE, classes +1Bh, levels +1Eh. The bands
; are the tail's (SAVE_BASE reads them through TAIL_SEG: in the segment they read the tail's bytes at the
; segment's offsets, and every save a level up or the creation screen worked out was nonsense, a new 7th-level
; fighter's 81/2/235/0/208, 2026-11-28).
        SAVE_BASE_CODE SHEETS_PTR, SHEET_SIZE, 0x1B, 0x1E
section tail
        SAVE_BANDS_DATA
section image
; ---- WEAPON PICKS: DSCLOG's CR_WEAPONS, LV_CHECK and PROBE_PK_* on the sequel's creation screen ----
; With weapon specialization (RULE_SPECIALIZE), a new character that is a fighter, gladiator or ranger (or a
; Battle Mage, Crusader, Mind Warrior or Swashbuckler: LV_DUE) picks its weapon specs after DONE, as in
; Shattered Lands: on the level up's psionicists' pop-up (688:61h, 93B62h; FIRST SPELLS AND POWERS' CR_PSI_ENTRY)
; in weapon mode (LV_MODE), which shows the Loader's weapon window (RESOURC2.GFF's 3021: weaponpages.rav_chunks,
; four rows of six slots, a picture of each of the 22 kinds) in place of the powers' and takes its clicks. The
; picks go in the 48h sheet's +42h..+44h (SPEC_SET, the V3 layout game.packed_specs reads); EXIT leaves the rest
; to WP_FILL (the long sword, else the club, a thri-kreen's chatkcha first, else the first it may). EDIT asks
; only for picks it is still due (its own kept: the creation screen copies 42h bytes, +42h..+47h left as
; they were), so an EDIT that keeps its classes asks none. The sites:
; - CR_WEAPONS (site 120): "push si / nop / push cs" (6E2ECh; 3 bytes) in DONE (6E0B9h) before its call for
;   the game's starting gear (6F197h): the screen's windows closed and their pictures let go by then (SL's
;   CR_WEAPONS' place, just before its own); the spells and powers (CR_PICKS) are picked before it. The way
;   back is put in a frame the overlay manager can fix up, as CR_PICKS'; then the two pushes, under the frame.
; - PK_WIN (site 121): "push 445Dh" (93C94h; 3 bytes) in the pop-up's window routine (93BE4h): the weapon
;   window, centred (the place pushed before it: "push 2B0050h").
; - PK_TITLE (site 122): "push ds / push 2ACCh" (93D63h; 4 bytes), "PICK A PSIONIC POWER,": no lines in
;   weapon mode (PK_HOVER puts the title under the slots), the game's own put back otherwise.
; - PK_FILL (site 123): "xor di,di / mov si,di" (93DECh; 4 bytes) at the start of the powers' list (93DE4h):
;   in weapon mode none, the slots of the kinds it can't pick out of use (168:71Fh, read from 93D09h).
; - PK_CLICK (site 124): "mov ax,[bp+8]" (93FABh; 3 bytes) in the window's click handler (93F8Dh): a slot it
;   can pick taken (WP_TAKE), the window closed (94047h) once none are left, else left up (9403Eh).
; - PK_HOVER (site 125): "or ax,ax / jnz 93BD3h" (93BBAh; 4 bytes) in the pop-up's event loop: the slot under
;   the pointer named in the window's two lines (93930h, the powers' own), "SPECIALIZE IN" or "EXPERT IN" and
;   the kind, the title when on none.
; - PSI_COUNT (site 95, FIRST SPELLS AND POWERS'): the picks left shown, LV_LEFT.
; Not here (DSCLOG's): a kit's own weapon as a default pick, KIT_ALLOWS' and KIT_FORBIDS' kinds (the sequel's
; kits have none yet), the picks after DUAL, the starting weapon of the kind picked first (startgear).
WP_STUB_CALL   equ 0x47B0 - 0x47E0  ; (688h's stub segment less DS's: CR_STUB)
WP_PSI_ENTRY   equ 0x61             ; (the psionicists' pop-up, 93B62h)
PICK_WIN       equ 0xBCD            ; (weaponpages.PICKER: 3021)
PICK_FIRST     equ 0x8C0            ; (weaponpages.PICK_FIRST: its slots)
PICK_COUNT_BUTTON equ 0x2C37
PK_WINDOW      equ 0x1431           ; DS: the pop-up's window (far)
PK_CREATION    equ 0x1429           ; DS: the sheet being made and its creature (far: the pop-up sets them)
PK_FILL_BACK   equ 0x93DEC + 3      ; (PK_FILL's way back: the NOP after the site's number)
PK_FILL_DONE   equ 0x93F7E - PK_FILL_BACK ; (the list's end: "xor ax,ax / pop di")
PK_OP_CALL     equ 0x93D09 - PK_FILL_BACK ; (168:71Fh's far address in its call at 93D08h: a button in use or not)
PK_LABEL_CALL  equ 0x93CF4 - PK_FILL_BACK ; (168:7FFh's at 93CF3h: a button's text)
PK_CLICK_BACK  equ 0x93FAB + 3
PK_STAY        equ 0x9403E - PK_CLICK_BACK ; (the click handler's way out, and its close's)
PK_CLOSE       equ 0x94047 - PK_CLICK_BACK
PK_TITLE_BACK  equ 0x93D63 + 3
PK_TITLE_SECOND equ 0x93D6B - PK_TITLE_BACK ; ("push 0E700FEh"'s colour byte, "push 0E3009Fh"'s width and
PK_TITLE_WIDTH equ 0x93D6F - PK_TITLE_BACK  ;   ink, "push 46h"'s place, after PK_TITLE's site)
PK_TITLE_INK   equ 0x93D71 - PK_TITLE_BACK
PK_TITLE_Y     equ 0x93D74 - PK_TITLE_BACK
PK_GAME_SECOND equ 0xE7             ; (the game's)
PK_GAME_INK    equ 0xE3
PK_GAME_WIDTH  equ 0x9F
PK_GAME_Y      equ 0x46
PK_PICK_WIDTH  equ 214              ; (weaponpages.PICK_WIDTH, PICK_TITLE_Y: the lines under the slots)
PK_PICK_Y      equ 7 + 4 * 34 + 3
PK_FIRST_Y     equ 0x7F             ; (PK_TITLE's: the game's "push 46h" takes a byte; no lines drawn there)
PK_PICK_X      equ (320 - 214) / 2  ; (the window's place, centred: weaponpages.PICK_HEIGHT 182)
PK_PICK_TOP    equ (200 - 182) / 2
PK_HOVER_BACK  equ 0x93BBA + 3
PK_LINES       equ 0x93930 - PK_HOVER_BACK ; (the window's two lines, rubbed out and drawn)
PK_NO_EVENT    equ 0x93BD3 - PK_HOVER_BACK
PK_SLOTS_X     equ PK_PICK_X + (214 - 6 * 34 + 2) / 2 ; (the first slot's corner on the screen)
PK_SLOTS_Y     equ PK_PICK_TOP + 7
PK_PITCH       equ 34
PK_SLOT        equ 32
PK_NAME        equ 0x21             ; (a creature's name)
PK_UNDRAWN     equ 0xFE             ; (LV_HOVERED: neither a slot's lines nor the title drawn yet)
SH_CLASS_FLAGS equ 0x10             ; (the sheet's classes as bits: 200h a ranger)
RANGER_FLAG    equ 0x200
CU_TYPE_CLASSES equ 0x0C            ; (an item type's classes as bits)
WP_THRI_KREEN  equ 8                ; (the sheet's race)
KIT_SPELLARCHER equ 57
KIT_POISONER   equ 65
KIT_KREEN_KINDS equ 0x1000          ; (the chatkcha)
KIT_BM_KINDS   equ 0x00BF           ; a Battle Mage's: long sword, club, dagger, short sword, mace, axe, pick
KIT_MELEE_KINDS equ 0xF0FFF         ; (not the chatkcha, bow, sling, staff sling, javelin or darts)
KIT_POISON_KINDS equ 0x000C         ; a Poisoner's: dagger, short sword
SWASH_KINDS    equ 0x000D           ; a Swashbuckler's: long sword, dagger, short sword
MYRM_POLEARM   equ 9                ; (the polearm's kind, less 1: a Myrmidon's own second weapon spec)
CHATKCHA_KIND  equ 12               ; (less 1)

cr_weapons:
        call kp_if_frame        ; (interrupts as the caller had them: the pop-up needs them)
        pushad
        push es
        mov bx, sp              ; the interrupt frame at BX+34: IP, CS, flags
        push word [ss:bx + 36]
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        call wp_ask             ; (SI the member, as the game has it)
        pop bp
        pop ax                  ; the way back, as the overlay manager has left it
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
        pop es
        popad
        sub sp, 4               ; "push si / push cs" under the frame: it two words down
        push bp
        mov bp, sp              ; ([BP+6] the way back, +8 its CS, +10 the flags)
        push ax
        mov ax, [bp + 6]
        mov [bp + 2], ax
        mov ax, [bp + 8]
        mov [bp + 4], ax        ; (and [BP+8] CS still: the "push cs")
        mov ax, [bp + 10]
        mov [bp + 6], ax
        mov [bp + 10], si
        pop ax
        pop bp
        iret

; LV_WEAPONS (site 150): "cmp word [bp+8],0Ch" (957BEh; 4 bytes: the site and a NOP) in the routine that
; raises a character a level in a class (its frame [BP+8] the class, SI the member; the preserver's spell
; pick just before it, the psionicist's power pick after it: DSCLOG's PROBE_LV_PICK's place, its LV_CHECK):
; a warrior (or a Battle Mage, Crusader, Mind Warrior or Swashbuckler) with fewer weapon specs than it is due
; (LV_DUE: a gladiator's 3rd at 6th and 4th at 9th, and past SL's levels a gladiator's 5th to 8th at 13th, 17th,
; 21st and 25th and a fighter's second at 13th, the owner's 2026-11-26) picks the rest on the weapon window
; (WP_ASK, as at creation); one with them all is asked nothing. The pop-up is overlay code: the way back is put
; in a frame the overlay manager can fix up, as CR_WEAPONS'. Then the compare, its flags back to the JNZ
; (RETF 2), as DUAL_KIT's.
lv_weapons:
        call kp_if_frame        ; (interrupts as the caller had them: RETF 2 keeps these flags)
        pushad
        push es
        mov bx, sp              ; the interrupt frame at BX+34: IP, CS, flags
        push word [ss:bx + 36]
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        inc word [cs:lv_weapon_calls]
        call wp_ask             ; (SI the member, as the game has it)
        pop bp
        pop ax                  ; the way back, as the overlay manager has left it
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
        pop es
        popad
        cmp word [bp + 8], 0x0C
        retf 2
lv_weapon_calls dw 0            ; (for a look in play)

; WP_ASK: member SI (DS the game's) asked for the weapon specs it is due (LV_DUE) and hasn't, from those its
; classes and kit allow (WP_KINDS), on the pop-up in weapon mode; on EXIT the rest from WP_FILL; a
; Myrmidon's polearm. Registers changed.
wp_ask:
        test word [cs:rules], RULE_SPECIALIZE
        jz .ret
        cmp si, 4
        jae .ret
        les bx, [SHEETS_PTR]
        imul ax, si, SHEET_SIZE
        add bx, ax
        call lv_due
        jcxz .ret
        call spec_count         ; (DX those it has)
        cmp dx, cx
        jae .ret
        sub cl, dl
        call wp_kinds
        call wp_less_mine
        or eax, eax
        jz .ret
        call wp_bits            ; (DL how many: no more than there are to pick)
        cmp dl, cl
        jae .left
        mov cl, dl
.left:  mov [cs:lv_left], cl
        mov [cs:lv_avail], eax
        mov [cs:lv_member], si
        inc word [cs:wp_asks]
        push dword [PK_CREATION]        ; (the pop-up sets the sheet being made and its creature: put back)
        push dword [PK_CREATION + 4]
        mov byte [cs:lv_mode], 1
        mov ax, ds
        add ax, WP_STUB_CALL
        mov [cs:cr_far + 2], ax
        mov word [cs:cr_far], WP_PSI_ENTRY
        push si
        call far [cs:cr_far]
        add sp, 2
        mov byte [cs:lv_mode], 0
        pop dword [PK_CREATION + 4]
        pop dword [PK_CREATION]
        les bx, [SHEETS_PTR]
        imul ax, si, SHEET_SIZE
        add bx, ax
        call wp_fill
        call myrm_polearm
.ret:   ret

; SPEC_COUNT: DX the weapon specs sheet ES:BX has. Others kept.
spec_count:
        push ax
        push si
        xor dx, dx
        xor si, si
.each:  call spec_get
        or ax, ax
        jz .next
        inc dx
.next:  inc si
        cmp si, SPEC_ALL
        jb .each
        pop si
        pop ax
        ret

; WP_LESS_MINE: EAX less the kinds sheet ES:BX has. Others kept.
wp_less_mine:
        push cx
        push si
        xor si, si
.each:  push eax
        call spec_get
        mov cx, ax
        pop eax
        jcxz .next
        dec cx
        btr eax, ecx
.next:  inc si
        cmp si, SPEC_ALL
        jb .each
        pop si
        pop cx
        ret

; WP_BITS: DL the bits set in EAX (of the KIND_COUNT). Others kept.
wp_bits:
        push di
        xor dx, dx
        xor di, di
.each:  bt eax, edi
        adc dl, 0
        inc di
        cmp di, KIND_COUNT
        jb .each
        pop di
        ret

; WP_FILL: sheet ES:BX given LV_LEFT more of LV_AVAIL (none left when every pick was made): a thri-kreen's
; chatkcha, the long sword, the club, else the first it may (SL's weaponchoice.kinds_for, less the kits'
; own weapons). Others kept.
wp_fill:
        pushad
.each:  cmp byte [cs:lv_left], 0
        je .out
        mov eax, [cs:lv_avail]
        or eax, eax
        jz .out
        cmp byte [es:bx + SH_RACE], WP_THRI_KREEN
        jne .sword
        mov cx, CHATKCHA_KIND
        bt eax, ecx
        jc .take
.sword: xor cx, cx
        bt eax, ecx
        jc .take
        inc cx
        bt eax, ecx
        jc .take
        bsf ecx, eax
.take:  btr dword [cs:lv_avail], ecx
        mov ax, cx
        call wp_put
        dec byte [cs:lv_left]
        inc word [cs:wp_filled]
        jmp .each
.out:   popad
        ret

; WP_PUT: kind AX into sheet ES:BX's first empty slot (SPEC_SET). All registers kept.
wp_put:
        push ax
        push si
        xor si, si
.slot:  push ax
        call spec_get
        or ax, ax
        pop ax
        je .put
        inc si
        cmp si, SPEC_ALL
        jb .slot
        jmp .out
.put:   inc al
        call spec_set
.out:   pop si
        pop ax
        ret

; MYRM_POLEARM: sheet ES:BX, a Myrmidon's, the polearm in its second slot when that is empty and the first
; holds its pick (DSCLOG's). All registers kept.
myrm_polearm:
        pusha
        call kit_is_b
        db KIT_MYRMIDON
        jne .out
        xor si, si
        call spec_get
        or ax, ax
        jz .out
        inc si
        call spec_get
        or ax, ax
        jnz .out
        mov al, MYRM_POLEARM + 1
        call spec_set
.out:   popa
        ret

; LV_DUE: CX the weapon specs the character whose sheet is ES:BX is due (DSCLOG's, the sequel's sheet): a
; gladiator 2, 3 from 6th level, 4 from 9th, and one more at 13th, 17th, 21st and 25th (8: the owner's
; 2026-11-26); a fighter 1, 2 from 13th (a Myrmidon's polearm, MYRM_POLEARM, given it: 3 from 13th); a ranger
; 1; a Battle Mage, Crusader, Mind Warrior or Swashbuckler 1; 0 for others. A human's earlier
; classes (dual-classed) count only once its first class's level has passed theirs. Others kept.
lv_due:
        push ax
        push si
        xor cx, cx
        xor si, si
.class: mov al, [es:bx + si + SH_CLASSES]
        mov ah, [es:bx + si + SH_LEVELS]
        or si, si
        jz .on
        cmp byte [es:bx + SH_RACE], CU_HUMAN
        jne .on
        cmp ah, [es:bx + SH_LEVELS]
        jae .next
.on:    cmp al, CU_GLADIATOR
        jne .warrior
        mov al, 2
        cmp ah, 6
        jb .most
        inc al
        cmp ah, 9
        jb .most
        inc al
        sub ah, 9               ; (then one each 4 levels: 13th, 17th, 21st, 25th)
        shr ah, 2
        add al, ah
        cmp al, SPEC_ALL
        jbe .most
        mov al, SPEC_ALL
        jmp .most
.warrior:
        cmp al, CU_FIGHTER
        jne .ranger
        mov al, 1
        cmp ah, 13
        jb .most
        inc al                  ; (a second at 13th)
        call kit_is_b
        db KIT_MYRMIDON
        jne .most
        inc al                  ; (a Myrmidon's polearm besides)
        jmp .most
.ranger:
        cmp al, 13
        jb .next
        cmp al, 16
        ja .next
.one:   mov al, 1
.most:  cmp cl, al
        jae .next
        mov cl, al
.next:  inc si
        cmp si, 3
        jb .class
        or cl, cl               ; (a Battle Mage, Crusader, Mind Warrior or Swashbuckler: one)
        jnz .out
        call kit_is_b
        db KIT_BATTLE_MAGE
        je .one_kit
        call kit_is_b
        db KIT_SWASHBUCKLER
        je .one_kit
        call war_kit_is
        jne .out
.one_kit:
        mov cl, 1
.out:   pop si
        pop ax
        ret

; WP_KINDS: EAX the kinds (bit 0 the long sword) the character whose sheet is at ES:BX can choose (DSCLOG's
; KINDS_ALLOWED on the sequel's item types: KIND_OF_TYPE): those with an item type its classes may use (the
; type's +0Ch and the sheet's +10h) and CLASS_FORBIDS doesn't keep it from; not the bow for a ranger (it has
; expertise already) but a Seeker; a Battle Mage its one-handed melee kinds, a Spellarcher the bow, a Poisoner
; the dagger and short sword, a Swashbuckler the long sword, dagger and short sword; a Myrmidon any but the
; polearm; a Crusader or Mind Warrior melee kinds (a thri-kreen Mind Warrior the chatkcha too). DS the game's.
wp_kinds:
        push cx
        push dx
        push si
        push edi
        mov edi, KIT_BM_KINDS
        call kit_is_b
        db KIT_BATTLE_MAGE
        je .all
        mov edi, 1 << (BOW_KIND - 1)
        call kit_is_b
        db KIT_SPELLARCHER
        je .all
        mov edi, KIT_POISON_KINDS
        call kit_is_b
        db KIT_POISONER
        je .all
        mov edi, SWASH_KINDS
        call kit_is_b
        db KIT_SWASHBUCKLER
        je .all
        xor dx, dx              ; DX each item type of a kind, CX its kind
        xor edi, edi
.type:  mov si, dx
        movzx cx, byte [cs:si + kind_of_type]
        sub cx, 1
        jc .no
        bt edi, ecx
        jc .no                  ; (one of its types already let in)
        push es
        push bx
        imul ax, dx, TYPE_SIZE
        les bx, [ITEM_TYPES_PTR]
        add bx, ax
        mov ax, [es:bx + CU_TYPE_CLASSES]
        pop bx
        pop es
        and ax, [es:bx + SH_CLASS_FLAGS]
        jz .no
        call class_forbids
        jc .no
        bts edi, ecx
.no:    inc dx
        cmp dx, KIND_TYPES
        jb .type
        call kit_is_b
        db KIT_MYRMIDON
        jne .war
        btr edi, MYRM_POLEARM
.war:   call war_kit_is
        jne .ranger
        mov eax, edi
        and edi, KIT_MELEE_KINDS
        cmp byte [es:bx + SH_RACE], WP_THRI_KREEN
        jne .ranger
        call kit_is_b
        db KIT_MIND_WARRIOR
        jne .ranger
        and eax, KIT_KREEN_KINDS
        or edi, eax
.ranger:
        test word [es:bx + SH_CLASS_FLAGS], RANGER_FLAG
        jz .all
        call kit_is_b
        db KIT_SEEKER
        je .all
        btr edi, BOW_KIND - 1
.all:   mov eax, edi
        pop edi
        pop si
        pop dx
        pop cx
        ret

; SPEC_PACK, SPEC_SET, SPEC_REPACK: DSCLOG's, on the sequel's sheet (+42h..+44h; +45h spare, kept): a sheet put
; in the SPEC_V2 layout (its specs as they were, no roll kept), a spec AL (kind + 1) into slot SI, the
; sheet made V3 (game.packed_specs). Each takes the sheet at ES:BX and keeps the rest.
spec_pack:
        test byte [es:bx + SPEC_SLOTS + 2], SPEC_V2
        jnz .ret
        push eax
        push edx
        push si
        xor si, si
.each:  call spec_get
        cmp al, 16
        jbe .keep
        xor al, al                      ; (no such kind: none)
.keep:  mov [cs:si + spec_digits], al
        inc si
        cmp si, SPEC_COUNT
        jb .each
        mov edx, [es:bx + SPEC_SLOTS]
        and edx, 0xFF000000             ; (+45h kept)
        or edx, (SPEC_PACKED | SPEC_V2) << 16 | ROLL_UNKNOWN << ROLL_SHIFT
        mov [es:bx + SPEC_SLOTS], edx
        call spec_repack
        pop si
        pop edx
        pop eax
.ret:   ret
spec_set:
        cmp si, SPEC_COUNT
        jae spec_set_more
        push ax
        push si
        push di
        mov di, si
        xor si, si
.read:  push ax
        call spec_get
        mov [cs:si + spec_kept], al
        pop ax
        inc si
        cmp si, SPEC_COUNT
        jb .read
        mov [cs:di + spec_kept], al
        call spec_pack
        mov si, SPEC_COUNT - 1
.copy:  mov al, [cs:si + spec_kept]
        mov [cs:si + spec_digits], al
        dec si
        jns .copy
        call spec_repack
        pop di
        pop si
        pop ax
        ret
        SHARED_spec_repack

; PK_FRAME_DOWN: the interrupt frame a word down (DSCLOG's FRAME_DOWN), its last word free.
pk_frame_down:
        push ax                 ; (room for the way back, a word below)
        push bp
        mov bp, sp              ; [bp+4] the way back, [bp+6] IP, [bp+8] CS, [bp+10] flags
        push ax
        mov ax, [bp + 4]
        mov [bp + 2], ax
        mov ax, [bp + 6]
        mov [bp + 4], ax
        mov ax, [bp + 8]
        mov [bp + 6], ax
        mov ax, [bp + 10]
        mov [bp + 8], ax
        pop ax
        pop bp
        ret

; PK_WIN (site 121): the window's id pushed: the game's, or the weapon window, centred.
pk_win:
        call pk_frame_down
        push bp
        mov bp, sp
        mov word [bp + 8], 0x445D
        cmp byte [cs:lv_mode], 0
        je .out
        mov word [bp + 8], PICK_WIN
        mov word [bp + 10], PK_PICK_X
        mov word [bp + 12], PK_PICK_TOP
.out:   pop bp
        iret

; PK_TITLE (site 122): the title's far text pushed: the game's (its colours, width and place put back in the
; pushes after), or in weapon mode none and none for the name pushed before (the place past a byte's reach).
pk_title:
        call pk_frame_down
        call pk_frame_down
        push bp
        mov bp, sp
        mov [bp + 10], ds
        mov word [bp + 8], 0x2ACC
        push ds
        push bx
        lds bx, [bp + 2]        ; (the code after the site: the next pushes)
        mov byte [bx + PK_TITLE_SECOND], PK_GAME_SECOND
        mov byte [bx + PK_TITLE_INK], PK_GAME_INK
        mov byte [bx + PK_TITLE_WIDTH], PK_GAME_WIDTH
        mov byte [bx + PK_TITLE_Y], PK_GAME_Y
        cmp byte [cs:lv_mode], 0
        je .out
        mov byte [bx + PK_TITLE_WIDTH], PK_PICK_WIDTH
        mov byte [bx + PK_TITLE_Y], PK_FIRST_Y
        mov [bp + 10], cs
        mov word [bp + 8], pk_no_title
        mov [bp + 14], cs
        mov word [bp + 12], pk_no_title
.out:   pop bx
        pop ds
        pop bp
        iret

; PK_FILL (site 123): the powers' list, or in weapon mode none: its end, and the slots in use or not.
pk_fill:
        call kp_if_frame        ; (it calls the game: interrupts as the caller had them)
        xor di, di
        mov si, di
        cmp byte [cs:lv_mode], 0
        je .out
        push bp
        mov bp, sp
        push ds
        push bx
        push eax
        lds bx, [bp + 2]        ; the code after the site: the far calls' addresses, as fixed up
        mov eax, [bx + PK_OP_CALL]
        mov [cs:lv_op_call], eax
        mov eax, [bx + PK_LABEL_CALL]
        mov [cs:lv_label_call], eax
        pop eax
        pop bx
        pop ds
        add word [bp + 2], PK_FILL_DONE
        pop bp
        mov byte [cs:lv_hovered], PK_UNDRAWN ; (no title yet: PK_HOVER draws it, at once)
        call pk_ops
.out:   iret

; PK_OPS: every slot in use if its kind is in LV_AVAIL, out of use if not (DS the game's).
        SHARED_pk_ops

; PK_CLICK (site 124): the button clicked ([BP+8] of the handler's frame, into AX): in weapon mode a slot it
; can pick taken, then the window closed once none are left, else left up.
pk_click:
        push bp
        mov bp, sp              ; ([BP]: the click handler's BP)
        push bx
        mov bx, [bp]
        mov ax, [ss:bx + 8]
        cmp byte [cs:lv_mode], 0
        je .out
        sub ax, PICK_FIRST
        cmp ax, KIND_COUNT
        jae .back
        bt [cs:lv_avail], ax
        jnc .back
        btr [cs:lv_avail], ax
        call wp_take
        dec byte [cs:lv_left]
        mov ax, PK_STAY
        jnz .go
        mov ax, PK_CLOSE
.go:    add [bp + 2], ax
        jmp .out
.back:  add ax, PICK_FIRST
.out:   pop bx
        pop bp
        iret

; WP_TAKE: kind AX into LV_MEMBER's sheet (WP_PUT), its slot out of use, the number shown one less (DS the
; game's). All registers kept.
wp_take:
        pusha
        push es
        mov dx, ax
        les bx, [SHEETS_PTR]
        imul ax, [cs:lv_member], SHEET_SIZE
        add bx, ax
        mov ax, dx
        call wp_put
        inc word [cs:wp_picked]
        push word 1
        push word 0
        add dx, PICK_FIRST
        push dx
        push dword [PK_WINDOW]
        call far [cs:lv_op_call]
        add sp, 10
        mov al, [cs:lv_left]
        dec al
        mov [PICK_SHOWN], al
        add al, '0'
        mov [cs:lv_count_text + 2], al
        push cs
        push word lv_count_text
        push dword PICK_COUNT_BUTTON
        push dword [PK_WINDOW]
        call far [cs:lv_label_call]
        add sp, 12
        pop es
        popa
        ret

; PK_HOVER (site 125): "or ax,ax / jnz" in the pop-up's event loop (AX 0 when there is an event): on round
; the loop as the JNZ for none; in weapon mode the slot under the pointer (INT 33h) named in the window's two
; lines, or the title on none, drawn only when that changes.
pk_hover:
        pushad
        push es
        mov di, sp
        mov ax, [ss:di + 34]    ; (the way back: the overlay's code, before the JNZ's target is put there)
        add ax, PK_LINES
        mov [cs:lv_lines_call], ax
        mov ax, [ss:di + 36]
        mov [cs:lv_lines_call + 2], ax
        mov bx, [ss:di + 30]    ; (AX as it was)
        or bx, bx
        jz .mode
        add word [ss:di + 34], PK_NO_EVENT
.mode:  cmp byte [cs:lv_mode], 0
        je .out
        mov ax, 3
        int 0x33                ; CX, DX: the pointer, on the screen
        mov al, 0xFF
        sub cx, PK_SLOTS_X
        jb .got
        sub dx, PK_SLOTS_Y
        jb .got
        xchg ax, cx             ; (AX the x, CL 0FFh)
        mov bl, PK_PITCH
        div bl
        cmp ah, PK_SLOT
        jae .none
        cmp al, 6
        jae .none
        mov ch, al              ; the column
        mov ax, dx
        div bl
        cmp ah, PK_SLOT
        jae .none
        mov ah, 6
        mul ah
        add al, ch
        cmp ax, KIND_COUNT
        jb .got
.none:  mov al, 0xFF
.got:   cmp al, [cs:lv_hovered]
        je .out
        mov [cs:lv_hovered], al
        cmp al, 0xFF
        jne .slot
        imul ax, [cs:lv_member], CREATURE_SIZE
        add ax, [CREATURES_PTR]
        add ax, PK_NAME
        push word [CREATURES_PTR + 2]
        push ax
        push cs
        call lv_title_of
        push ax
        jmp .draw
.slot:  push cs
        xor ah, ah
        call pk_word
        mov si, ax
        add si, si
        mov si, [cs:si + ef_kinds]
        lea ax, [si + 2]        ; (the kinds' names begin with two spaces)
        push ax
        push cs
        push dx
.draw:  push dword (PK_GAME_SECOND << 16) | 0xFE
        push dword (PK_GAME_INK << 16) | PK_PICK_WIDTH
        push word PK_PICK_Y
        push dword [PK_WINDOW]
        call far [cs:lv_lines_call]
        add sp, 0x16
.out:   pop es
        popad
        iret

; LV_TITLE_OF: AX the title for LV_MEMBER: "PICK A WEAPON OF EXPERTISE," when it would have expertise with
; the first kind (PK_WORD: a ranger, a Battle Mage, a Crusader, a Mind Warrior), else "PICK A WEAPON SPECIALTY,".
lv_title_of:
        push dx
        xor ax, ax
        call pk_word
        mov ax, lv_title
        cmp dx, lv_expert
        jne .ret
        mov ax, lv_title_x
.ret:   pop dx
        ret

; PK_WORD: DX the first line for kind AX: "EXPERT IN" when LV_MEMBER would have expertise with it once picked,
; else "SPECIALIZE IN" (the kind put in the sheet's first empty slot for SPEC_OF_SHEET to judge, SPEC_FORCED
; its kind, then taken out again). DS the game's; others kept.
pk_word:
        push ax
        push bx
        push si
        push es
        mov dx, lv_hover
        les bx, [SHEETS_PTR]
        push ax
        imul ax, [cs:lv_member], SHEET_SIZE
        add bx, ax
        pop ax
        xor si, si
.slot:  push ax
        call spec_get
        or ax, ax
        pop ax
        je .put
        inc si
        cmp si, SPEC_ALL
        jb .slot
        jmp .ret
.put:   push dword [es:bx + SPEC_SLOTS]  ; (put back after: a kind pointed at changes nothing)
        push dword [es:bx + SPEC_MORE - 1]
        push si
        inc al
        call spec_set
        mov [cs:spec_forced], al
        push dx
        call spec_of_sheet
        mov al, dl
        pop dx
        mov byte [cs:spec_forced], 0
        pop si
        pop dword [es:bx + SPEC_MORE - 1]
        pop dword [es:bx + SPEC_SLOTS]
        cmp al, SPEC_EXPERT
        jne .ret
        mov dx, lv_expert
.ret:   pop es
        pop si
        pop bx
        pop ax
        ret

lv_op_call dd 0                 ; 168:71Fh, a button's state (0 in use, 1 out of use)
lv_label_call dd 0              ; 168:7FFh, a button's text
lv_lines_call dd 0              ; 93930h, the window's two lines (as PK_HOVER finds it)
pk_no_title db 0                ; (PK_TITLE's lines in weapon mode: none)
lv_hovered db 0FFh              ; the slot PK_HOVER last named (0FFh none: the title)
lv_hover  db 'SPECIALIZE IN', 0
lv_expert db 'EXPERT IN', 0
lv_mode   db 0                  ; 1 while WP_ASK has the pop-up up for weapons
lv_left   db 0
lv_avail  dd 0
lv_member dw 0
lv_count_text db '  0', 0
lv_title  db 'PICK A WEAPON SPECIALTY,', 0
lv_title_x db 'PICK A WEAPON OF EXPERTISE,', 0
spec_sorted times SPEC_COUNT db 0
spec_kept times SPEC_COUNT db 0
wp_asks    dw 0                 ; (counts, for a look in play: windows, slots clicked, picks filled after EXIT)
wp_picked  dw 0
wp_filled  dw 0

; ---- PICK POCKETS: DSCLOG's (PICK_BUTTON; pickpocket.py), on the sequel's USE screen and talk ----
; A character with thief levels, outside a fight, has a button of their own on the USE screen where a
; priest's Turn Undead is: a purse (PP_ICON, ICON 3048 in the Loader's RESOURC2.GFF: icons.rav_pick_icon).
; Let go of, the screen closes as for Turn Undead, no spell is readied, and the pointer is the one for
; talking; the next someone it is clicked on has their pocket tried by that thief instead of a talk (the
; Loader answers PICK_SEQ: PICK_TEXT shown in the dialogue window). The pointer turned to another mode puts
; the pick away (PROBE_POINTER's PP_DISARM). The sequel's routines are SL's at other addresses: the button
; shown 97AC8h (SL's 89959h), its handler 9756Eh (894E2h), the screen's closing 9654Dh (884B3h), the talk
; 630F0h (5ECD0h). Not ported: a cleric/thief's purse beside Turn Undead (SL's PP_EXTRAS: a cleric/thief
; keeps Turn Undead alone), the purse's own description on a right click (none shown: PP_INFO), the XP for
; SL's three weapons and the purse's sound.
; - PP_SHOW (site 180): "cmp word [9C1Ch],0" (97AF4h; 5 bytes), the priest's element of the character on
;   show (the sheet at [1429h], its +10h; 0 no button): for a thief with no element, outside a fight, past
;   the elements' cases (PP_ELEMENT) and its icon (PP_ICON). The game loads the icon once a screen
;   (TU_CACHE, let go of as it closes): one of another number is let go of now (1D0h:92h), so the
;   button's own is loaded. The compare's flags into the INT's.
; - PP_CLICK (site 181): "cmp byte [9D76h],0" (97623h; 5 bytes) in the handler as the button is let go of:
;   set when pressed (the game's press doesn't reach it outside a fight); the thief's always (ZF clear),
;   what the screen's closing sets for a spell kept (PP_KEEP).
; - PP_LIT (site 182): "mov ax,[9D77h]" (9767Bh; 3 bytes), the icon the menu button shows lit: the thief's
;   as it was (READY_ICON).
; - PP_ARM (site 183): "push dword 132FFFFh" (97699h; 6 bytes), Turn Undead (306) readied: the thief's
;   readies nothing (on to the handler's end, ARM_OUT) but the pick, the readied kind put back (PP_RESTORE).
; - PP_TEXT (site 184): "push ds / push 2D08h" (975CBh, 97702h; 4 bytes), "TURN UNDEAD" under the screen:
;   the thief's PP_NAME.
; - PP_INFO (site 185): "mov ax,[9D77h]" (97716h; 3 bytes), a right click, the description box of the
;   element's icon less 0BE4h plus 149h: none for the purse (INFO_SKIP past the box's call).
; - PP_HAND (site 186): "mov si,[bp+6]" (630F8h; 3 bytes) at the start of the routine of a click on the map
;   with the pointer for talking ([BP+6] the thing under it): with a pick readied, PICK_SEQ asked; answered
;   (PICK_TAKEN), PICK_TEXT shown and on to the routine's end (HAND_DONE), else the talk as ever.
PP_ICON      equ 3048
PP_ELEMENT   equ 9                  ; (past the switch's 1-8: the icon kept)
PICK_BUTTON  equ 2                  ; (PICK_ON's bit, DSCLOG's)
PICK_SIZE    equ 240
PICK_WAIT    equ 9                  ; timer ticks the Loader has to answer (DSCLOG's)
TU_ELEMENT   equ 0x9C1C             ; DS: the Turn Undead button's element (0: none)
TU_ICON      equ 0x9D77             ; DS: its icon
TU_PRESSED   equ 0x9D76             ; DS: a button pressed (a byte)
TU_CACHE     equ 0x2B9A             ; DS: the icon loaded (far)
TU_SHEET     equ 0x1429             ; DS: the sheet of the character on show (far)
TU_NAME      equ 0x2D08             ; DS: "TURN UNDEAD"
POINTER_MODE equ 0x1440             ; DS: the pointer's mode: 1 walk, 2 talk, 4 attack (SL's 11B8h)
TALK_MODE    equ 2
READY_WHO    equ 0x4264             ; DS: the character readying (SL's 4970h) ...
READY_KIND   equ 0x4265             ; ... each one's readied kind, a word (4971h) ...
READY_ICON   equ 0x445A             ; ... the icon the menu button shows (4AF9h)
PP_FREE_SEG  equ 0x344C             ; (less the load segment) 1D0h:92h, which lets go of memory (far)
PP_FREE_OFF  equ 0x0092
PP_DGROUP    equ 0x47E0             ; the game's DS, less its load segment
ARM_OUT      equ 0x9772B - (0x97699 + 3)  ; (the handler's end, less the way back)
INFO_SKIP    equ 0x97726 - (0x97716 + 3)  ; (past the description box's call)
HAND_DONE    equ 0x6373F - (0x630F8 + 3)  ; (the talk routine's end)
PP_SI        equ 6                  ; (SI in PUSHAD's frame under ES)
PP_FLAGS     equ 0x08D5             ; (OF, SF, ZF, AF, PF, CF)
pp_show:
        call kp_if_frame                ; (it calls the game: interrupts as the caller had them)
        push bp
        mov bp, sp                      ; [BP+6] the INT's flags
        pushad
        push es
        mov byte [cs:pp_shown], 0
        mov dword [cs:pp_extra], 0
        call pp_fighting
        jne .icon
        mov di, -1                      ; (DI: where the next goes: -1 Turn Undead's place while no
        cmp word [TU_ELEMENT], 0        ;   priest's element has it, then the slots beside it: PP_PUT)
        je .kinds
        xor di, di
.kinds: test byte [cs:pick_on], PICK_BUTTON
        jz .arrows
        cmp di, -1
        jne .arrows                     ; (a cleric/thief: Turn Undead's, no purse)
        les bx, [TU_SHEET]
        mov si, SHEET_CLASSES
.cls:   cmp byte [es:bx + si], THIEF_CLASS
        je .thief
        inc si
        cmp si, SHEET_CLASSES + 3
        jb .cls
        jmp .arrows
.thief: mov al, 1                       ; the thief's purse
        call pp_put
        inc word [cs:pick_shown]
.arrows:
        cmp word [cs:arrows_on], 0
        je .icon
        mov cx, 1                       ; a Spellarcher's arrows, a button for each touch spell it knows
.arrow: call arrow_knows                ;   (ARROW_SPELLS' first, Burning Hands, never: spellarrows.RETIRED)
        jnc .anext
        mov al, cl
        add al, PP_ARROWS
        call pp_put
        inc word [cs:arrows_shown]
.anext: inc cx
        cmp cx, 4
        jb .arrow
.icon:  mov ax, [TU_ICON]               ; the icon to be shown: the element's, or as it is
        mov bx, [TU_ELEMENT]
        cmp bx, PP_ELEMENT
        je .want
        mov si, pp_icons
.elem:  cmp bx, [cs:si]
        je .found
        add si, 4
        cmp si, pp_icons_end
        jb .elem
        jmp .want
.found: mov ax, [cs:si + 2]
.want:  or bx, bx
        jz .flags                       ; (no button)
        cmp dword [TU_CACHE], 0
        je .keep                        ; (none loaded: the game loads it)
        cmp ax, [cs:pp_loaded]
        je .keep
        push ax                         ; another's loaded: let go of it
        push dword [TU_CACHE]
        mov ax, ds
        sub ax, PP_DGROUP - PP_FREE_SEG
        mov [cs:pp_call + 2], ax
        mov word [cs:pp_call], PP_FREE_OFF
        call far [cs:pp_call]
        add sp, 4
        mov [TU_CACHE], ax
        mov [TU_CACHE + 2], dx
        pop ax
.keep:  mov [cs:pp_loaded], ax
.flags: cmp word [TU_ELEMENT], 0
        pushf
        pop ax
        and ax, PP_FLAGS
        and word [bp + 6], ~PP_FLAGS
        or [bp + 6], ax
        mov eax, [cs:pp_extra]
        or eax, [cs:pp_extra_on]
        jz .out                         ; (no button beside it, shown or to show)
        push word [bp + 4]              ; the buttons beside it shown, or taken off: the game's routines,
        push word [bp + 2]              ;   which may load overlays, called in a frame the overlay manager
        push word [bp]                  ;   can fix up (the way back, and the game's BP)
        mov bp, sp
        call pp_extras
        pop ax                          ; (the game's BP)
        pop ax                          ; the way back, as the overlay manager has left it
        pop dx
        mov bp, sp
        add bp, 34                      ; (past ES and PUSHAD: this routine's BP)
        mov [bp + 2], ax
        mov [bp + 4], dx
.out:   pop es
        popad
        pop bp
        iret

; PP_PUT: a button of kind AL wanted: in Turn Undead's place while DI is -1 (PP_SHOWN, its element
; and icon: PP_ICON - 1 + the kind), else in the slot DI beside it (PP_EXTRA; none past EXTRA_MOST);
; DI the next. AX lost.
        SHARED_pp_put

; PP_MINE: AL the kind of the button whose handler's frame is BX (its +8 the button): Turn Undead's
; place's (PP_SHOWN: 0 the game's), or one beside it (PP_EXTRA). All else kept.
        SHARED_pp_mine

pp_click:
        push bx
        push ax
        mov bx, bp                      ; (the handler's frame: its +8 the button)
        call pp_mine
        push bp
        mov bp, sp                      ; [BP+10] the INT's flags
        mov [cs:pp_arming], al
        or al, al
        jz .game
        call pp_keep                    ; (what closing the screen sets for a spell readied)
        or bp, bp                       ; (ZF clear: on as pressed)
        jmp .flags
.game:  cmp byte [TU_PRESSED], 0
.flags: pushf
        pop ax
        and ax, PP_FLAGS
        and word [bp + 10], ~PP_FLAGS
        or [bp + 10], ax
        pop bp
        pop ax
        pop bx
        iret

pp_lit:
        mov ax, [TU_ICON]               ; (the replaced instruction)
        cmp byte [cs:pp_arming], 0
        je .ret
        mov ax, [READY_ICON]            ; (the thief's: as it was)
.ret:   iret

pp_arm:
        cmp byte [cs:pp_arming], 0
        jne .pick
        call pk_frame_down              ; the game's push: the INT's frame moved down over it
        call pk_frame_down
        push bp
        mov bp, sp
        mov word [bp + 8], 0xFFFF
        mov word [bp + 10], 0x0132
        pop bp
        iret
.pick:  cmp byte [cs:pp_arming], PP_ARROWS
        jae arrows_arm                  ; (a Spellarcher's arrows: SPELL ARROWS)
        mov byte [cs:pp_arming], 0
        push bp
        mov bp, sp
        add word [bp + 2], ARM_OUT
        call pp_restore                 ; (no spell readied: as before the screen was closed)
        push ax
        push es
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov al, [es:USE_WHO_OFF]        ; the thief: the character on show
        mov [cs:pp_who], al
        mov byte [cs:pp_armed], 1
        mov word [POINTER_MODE], TALK_MODE
        inc word [cs:pick_armed]
        pop es
        pop ax
        pop bp
        iret

pp_text:
        call pk_frame_down              ; the game's two pushes: the INT's frame moved down over them
        call pk_frame_down
        push bp
        mov bp, sp
        push ax
        push bx
        mov word [bp + 8], TU_NAME
        mov [bp + 10], ds
        mov bx, [bp]                    ; (the handler's frame)
        call pp_mine
        or al, al
        jz .out
        mov word [bp + 8], pp_name
        sub al, PP_ARROWS
        jb .cs
        movzx bx, al
        shl bx, 1
        mov ax, [cs:bx + arrows_names]
        mov [bp + 8], ax
.cs:    mov [bp + 10], cs
.out:   pop bx
        pop ax
        pop bp
        iret

pp_info:
        push bx
        mov bx, bp                      ; (the handler's frame)
        call pp_mine
        pop bx
        cmp al, 0
        mov ax, [TU_ICON]               ; (the replaced instruction)
        je .ret
        push bp
        mov bp, sp
        add word [bp + 2], INFO_SKIP    ; (the purse, the arrows: no description box)
        pop bp
.ret:   iret

pp_hand:
        sti
        pushad
        push es
        mov bx, sp                      ; the interrupt frame at BX+34: IP, CS, flags
        mov si, [bp + 6]                ; the replaced "mov si,[bp+6]" (BP the game's), into the frame
        mov [ss:bx + PP_SI], si
        cmp byte [cs:pp_armed], 0
        je .out
        cmp word [POINTER_MODE], TALK_MODE
        jne .out
        mov byte [cs:pp_armed], 0
        test byte [cs:pick_on], PICK_BUTTON
        jz .out
        call pp_fighting
        jne .out
        call loader_fresh
        jne .out                        ; (no Loader: the talk)
        mov [cs:pick_who], si
        movzx ax, byte [cs:pp_who]
        mov [cs:pick_thief], ax
        mov word [cs:pick_taken], 0
        inc word [cs:pick_seq]
        xor ax, ax
        mov es, ax
        mov cx, [es:0x46C]              ; the BIOS timer
        call rtc_begin
.wait:  mov ax, [cs:pick_reply]
        cmp ax, [cs:pick_seq]
        je .ready
        mov ax, [es:0x46C]
        sub ax, cx
        cmp ax, PICK_WAIT
        jae .late
        call rtc_waited                 ; (the BIOS clock can stand still: at most 2 s by the real-time clock)
        jnc .wait
.late:  mov ax, [cs:pick_seq]           ; no answer: marked answered, so a late one isn't carried out
        mov [cs:pick_reply], ax         ;   unseen (the Loader looks again before it moves anything)
        inc word [cs:pick_late]
        jmp .out
.ready: cmp word [cs:pick_taken], 0
        je .out
        add word [ss:bx + 34], HAND_DONE
        cmp byte [cs:pick_text], 0
        je .out
        cmp byte [cs:showing], 0
        jne .out
        mov word [cs:show_text], pick_text
        push word [ss:bx + 36]          ; the way back, pushed as a far call's, with BP (the dialogue
        push word [ss:bx + 34]          ;   window may load other overlays over the talk's)
        push bp
        mov bp, sp
        call show_window
        pop bp
        pop ax                          ; (the way back, as the overlay manager has left it)
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
.out:   pop es
        popad
        iret

; PP_KEEP: what the screen's closing (9654Dh) sets for a spell readied (READY_WHO; the character's
; READY_KIND, 3 for a spell; READY_ICON), kept for PP_RESTORE to put back. DS the game's; registers kept.
        SHARED_pp_keep
        SHARED_pp_restore
pp_shown_member:                        ; BX: the character on show, times 2 (ES lost)
        mov bx, ds
        add bx, USE_WHO_SEG
        mov es, bx
        movzx bx, byte [es:USE_WHO_OFF]
        shl bx, 1
        ret

; PP_FIGHTING: ZF clear in a fight (the fight's state, QS_FIGHT_SEG's +19h). DS the game's; registers kept.
pp_fighting:
        push es
        push ax
        mov ax, ds
        sub ax, PP_DGROUP - QS_FIGHT_SEG
        mov es, ax
        cmp word [es:0x19], 0
        pop ax
        pop es
        ret

; PP_DISARM: (PROBE_POINTER) the pick put away once the pointer is in another mode than talking
        SHARED_pp_disarm

; ---- SPELL ARROWS: DSCLOG's PP_EXTRAS, ARROWS_ARM, ARROWS_ASK and ARROW_KNOWS on the sequel's USE screen ----
; (spellarrows.py; site 240 and PICK POCKETS' 180-185, the header's +2098 to +2113.) A Spellarcher (KIT_SPELLARCHER awake)
; on show, outside a fight, has a button for each touch spell it knows (ARROW_KNOWS: the sequel's known
; bits, selector 320h, KNOWN_BITS; ARROW_SPELLS by WC_ARROWS: Chill Touch 3, Shocking Grasp 10, Vampiric
; Touch 38), with ARROWS_ON set: the first in Turn Undead's place unless a thief's purse or a priest's
; element has it (PP_PUT), the rest in the panel's empty places to its right (APFM 2BE7h-2BEAh of the USE
; screen's window, WIND 11500, as Shattered Lands': PP_EXTRAS). Kind PP_ARROWS + the spell's place (3-5),
; its icon PP_ICON - 1 + the kind (ICON 3050-3052 in the Loader's RESOURC2.GFF: icons.rav_arrow_icons),
; its name CHILL ARROWS and so on (PP_TEXT), no description box (PP_INFO). Let go of, the screen closes as
; for Turn Undead, nothing is readied, and ARROWS_ASK has the Loader make one (ARROWS_SEQ: the member, the
; spell's place; a slot used, the arrow on its stack, ravlog's _answer_arrows); refused, its words
; (PICK_TEXT) are shown in the dialogue window. The sequel's routines are SL's at other addresses: a
; button's handler set 5B0h:4Dh (the load + 46BDh; SL's 530h:43h), a button drawn 698h:6Bh (97743h; SL's
; 630h:4Dh), Turn Undead's handler 698h:66h (9756Eh), a chunk loaded 128h:4ABh (SL's 100h:4A4h), the
; screen's window at 4D8h:0 (the load + 45C9h), the buttons' frame at 370h:2Fh (the load + 3E71h).
; - PP_CLOSE (site 240): "cmp dword [2B9Ah],0" (9659Eh; 6 bytes) where the USE screen, closing (9654Dh),
;   lets go of Turn Undead's icon: the buttons beside it let go of too, its flags given back.
EXTRA_MOST   equ 4                  ; (the slots beside Turn Undead's)
PP_ARROWS    equ 2                  ; (a button's kind: 0 the game's, 1 the purse, PP_ARROWS + N the arrows
                                    ;   of ARROW_SPELLS' Nth)
SECOND_ID    equ 0x2BE7             ; (the empty places right of Turn Undead's: 2BCDh + 1Ah on)
SECOND_INDEX equ SECOND_ID - 0x2BCD
USE_STUB_SEG equ 0x47C1             ; (less the load segment) selector 698h: the USE screen's overlay's stub
DRAW_OFF     equ 0x006B             ;   97743h, a button drawn
HANDLER_OFF  equ 0x0066             ;   9756Eh, Turn Undead's handler
REG_SEG      equ 0x46BD             ; selector 5B0h: a button's handler and events set (its stub's 4Dh)
REG_OFF      equ 0x004D
LOAD_SEG     equ 0x28FF             ; selector 128h: a chunk loaded (its tag, its number, where to), 4ABh
LOAD_OFF     equ 0x04AB
WIN_LIST_SEG equ 0x45C9             ; selector 4D8h: the USE screen's window, far at this segment:0
FRAME_SEG    equ 0x3E71             ; selector 370h: the buttons' frame picture, far at this segment:2Fh
        SHARED_pp_extras

pp_extra_draw:                          ; slot SI, kind AL
        mov bx, si
        shl bx, 2
        add bx, pp_icons2               ; (BX: its icon's far pointer)
        cmp al, [cs:si + pp_icon_kind]
        je .load
        mov [cs:si + pp_icon_kind], al
        call pp_free_icon               ; (another kind's: let go of)
.load:  cmp dword [cs:bx], 0
        jne .reg
        push cs
        push bx
        movzx eax, byte [cs:si + pp_icon_kind]
        add ax, PP_ICON - 1
        push eax
        push dword 0x4E4F4349           ; ("ICON")
        mov ax, LOAD_SEG
        mov dx, LOAD_OFF
        call pp_aim
        call far [cs:pp_call]
        add sp, 12
.reg:   push word 0x66                  ; (its events, as the game's)
        mov ax, ds
        sub ax, PP_DGROUP - USE_STUB_SEG
        push ax
        push word HANDLER_OFF
        call pp_list_push               ; (its slot and the window)
        mov ax, REG_SEG
        mov dx, REG_OFF
        call pp_aim
        call far [cs:pp_call]
        add sp, 12
        mov byte [cs:si + pp_extra_on], 1
        inc word [cs:extras_drawn]
        push dword 2                    ; its frame, as the game draws Turn Undead's
        lea ax, [si + SECOND_INDEX]
        push ax
        mov ax, ds
        sub ax, PP_DGROUP - FRAME_SEG
        mov es, ax
        push dword [es:0x2F]
        push word 0
        call pp_draw
        mov bx, si
        shl bx, 2
        cmp dword [cs:bx + pp_icons2], 0
        je .ret
        push dword 0                    ; and its icon
        lea ax, [si + SECOND_INDEX]
        push ax
        push dword [cs:bx + pp_icons2]
        push word 1
        call pp_draw
.ret:   ret

pp_draw:                                ; the game's button drawing (698h:6Bh), its 12 bytes under the way back
        pop word [cs:pp_ret]
        mov ax, USE_STUB_SEG
        mov dx, DRAW_OFF
        call pp_aim
        call far [cs:pp_call]
        add sp, 12
        jmp word [cs:pp_ret]

pp_extra_hide:                          ; slot SI
        push word 0
        push dword 0
        call pp_list_push
        mov ax, REG_SEG
        mov dx, REG_OFF
        call pp_aim
        call far [cs:pp_call]
        add sp, 12
        mov byte [cs:si + pp_extra_on], 0
        ret

pp_list_push:                           ; pushes slot SI's button, then the window (far), under the way back
        pop word [cs:pp_ret]
        lea ax, [si + SECOND_ID]
        push ax
        mov ax, ds
        sub ax, PP_DGROUP - WIN_LIST_SEG
        mov es, ax
        push dword [es:0]
        jmp word [cs:pp_ret]

pp_free_icon:                           ; the icon at CS:BX let go of, if loaded (1D0h:92h); AX, CX, DX lost
        cmp dword [cs:bx], 0
        je .ret
        push bx                         ; (the game's far calls lose BX and ES)
        push es
        push dword [cs:bx]
        mov ax, PP_FREE_SEG
        mov dx, PP_FREE_OFF
        call pp_aim
        call far [cs:pp_call]
        add sp, 4
        pop es
        pop bx
        mov [cs:bx], ax
        mov [cs:bx + 2], dx
.ret:   ret

pp_aim:                                 ; PP_CALL aimed at the game's segment AX (less the load segment):DX
        mov [cs:pp_call], dx
        push bx
        mov bx, ds
        sub bx, PP_DGROUP
        add ax, bx
        pop bx
        mov [cs:pp_call + 2], ax
        ret

pp_close:
        call kp_if_frame                ; (it calls the game: interrupts as the caller had them)
        push bp
        mov bp, sp
        pushad
        push es
        mov bx, pp_icons2
.free:  call pp_free_icon
        add bx, 4
        cmp bx, pp_icons2 + 4 * EXTRA_MOST
        jb .free
        mov dword [cs:pp_extra_on], 0
        mov dword [cs:pp_icon_kind], 0
        cmp dword [TU_CACHE], 0
        pushf
        pop ax
        and ax, PP_FLAGS
        and word [bp + 6], ~PP_FLAGS
        or [bp + 6], ax
        pop es
        popad
        pop bp
        iret

; ARROWS_ARM: PP_ARM for a Spellarcher's arrows button (let go of, the USE screen closed): nothing
; readied, and ARROWS_ASK, in a frame the overlay manager can fix up (pushed as a far call's, with the
; game's BP: the dialogue window may load overlays).
arrows_arm:
        push ax
        mov al, [cs:pp_arming]
        sub al, PP_ARROWS
        mov [cs:arrows_which], al
        pop ax
        mov byte [cs:pp_arming], 0
        push bp
        mov bp, sp
        add word [bp + 2], ARM_OUT
        call pp_restore                 ; (no spell readied: as before the screen was closed)
        sti                             ; (the wait for the Loader counts the BIOS's ticks)
        pushad
        push es
        push word [bp + 4]
        push word [bp + 2]
        push word [bp]
        mov bp, sp
        call arrows_ask
        pop ax                          ; (the game's BP)
        pop ax                          ; the way back, as the overlay manager has left it
        pop dx
        mov bx, sp
        mov [ss:bx + 36], ax
        mov [ss:bx + 38], dx
        pop es
        popad
        pop bp
        iret

; ARROWS_ASK: the Spellarcher on show asks for an arrow of ARROWS_WHICH's touch spell (ARROWS_SEQ, its
; ARROWS_WHO and ARROWS_ROW), PICK_WAIT ticks at most; refused, the Loader's words (PICK_TEXT) shown. DS
; the game's; registers changed.
arrows_ask:
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        movzx di, byte [es:USE_WHO_OFF]
        cmp di, 4
        jae .done
        call loader_fresh
        jne .done                       ; (no Loader: nothing made)
        mov [cs:arrows_who], di
        movzx ax, byte [cs:arrows_which]
        mov [cs:arrows_row], ax
        mov byte [cs:pick_text], 0
        inc word [cs:arrows_seq]
        xor ax, ax
        mov es, ax
        mov cx, [es:0x46C]              ; the BIOS timer
        call rtc_begin
.wait:  mov ax, [cs:arrows_reply]
        cmp ax, [cs:arrows_seq]
        je .ready
        mov ax, [es:0x46C]
        sub ax, cx
        cmp ax, PICK_WAIT
        jae .late
        call rtc_waited
        jnc .wait
.late:  mov ax, [cs:arrows_seq]         ; (no answer: marked answered, so no arrow is made later unseen)
        mov [cs:arrows_reply], ax
        inc word [cs:arrows_late]
        ret
.ready: cmp byte [cs:pick_text], 0
        je .made                        ; (made: nothing to say)
        cmp byte [cs:showing], 0
        jne .done
        mov word [cs:show_text], pick_text
        call show_window
.done:  ret
.made:  mov ax, ds                      ; (the cast sound, as SL's plays the spell's own: ARROWS_SOUND)
        sub ax, DGROUP_GAP - SOUND_SEG
        mov [cs:sound_far + 2], ax
        push word ARROWS_SOUND
        call far [cs:sound_far]
        add sp, 2
        inc word [cs:arrows_sounds]
        ret
; The game's sound routine (B8h:0A22h, resident: the load + 1C5Fh; a byte, the sound, FFh none: the turn
; sounds' and the spells' own, [BP+6]). As an arrow is made SL plays its touch spell's cast sound (the
; record's +0Fh: Chill Touch's 4Eh, Shocking Grasp's 51h, Vampiric Touch's 6Eh); the sequel's records have
; one for Vampiric Touch alone (6Eh; Chill Touch's and Shocking Grasp's FFh), so that one for each.
SOUND_SEG    equ 0x1C5F
ARROWS_SOUND equ 0x6E
sound_far dw 0x0A22, 0

; ARROW_KNOWS: CF set if the party member on show (USE_WHO, its sheet [TU_SHEET]) is a Spellarcher who
; knows ARROW_SPELLS' CXth touch spell (1-3: WC_ARROWS' CX - 1). DS the game's; all registers kept.
arrow_knows:
        pusha
        push es
        les bx, [TU_SHEET]
        call kit_is_b
        db KIT_SPELLARCHER
        jne .no
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        movzx si, byte [es:USE_WHO_OFF]
        cmp si, 4
        jae .no
        mov di, cx
        call known_bits                 ; (ES:BX member SI's known wizard spells)
        mov al, [cs:di + wc_arrows - 1]
        call bit_known
        jz .no
        pop es
        popa
        stc
        ret
.no:    pop es
        popa
        clc
        ret

arrows_which db 0
arrows_names dw arrows_n1, arrows_n1, arrows_n2, arrows_n3 ; (the first, Burning Arrows, never shown)
arrows_n1    db "CHILL ARROWS", 0
arrows_n2    db "SHOCKING ARROWS", 0
arrows_n3    db "VAMPIRIC ARROWS", 0
pp_extra     times EXTRA_MOST db 0      ; (the kinds wanted beside Turn Undead's, PP_PUT's) ...
pp_extra_on  times EXTRA_MOST db 0      ; ... those with a handler set (PP_EXTRA_DRAW) ...
pp_icon_kind times EXTRA_MOST db 0      ; ... and the kind each one's icon is of
pp_icons2    times EXTRA_MOST dd 0      ; (their icons, loaded: far)
pp_ret       dw 0

pp_name   db "PICK POCKETS", 0
pp_icons  dw 1, 0x0BE4, 2, 0x0BE5, 4, 0x0BE6, 8, 0x0BE7 ; (the elements' Turn Undead icons)
pp_icons_end:
pp_shown  db 0                          ; the kind of the button in Turn Undead's place (PP_PUT: 0 the game's)
pp_arming db 0                          ; its kind, from its letting go to PP_ARM
pp_armed  db 0                          ; 1 while the next talk is a pick
pp_who    db 0                          ; (the thief)
pp_loaded dw 0                          ; the icon the game has loaded (TU_CACHE)
pp_call   dd 0
pp_kept_who  db 0                       ; (PP_KEEP's)
pp_kept_kind dw 0
pp_kept_icon dw 0
pick_text times PICK_SIZE db 0          ; (PICK_OFF's)

; ---- POISON AND ARROWS: the Poisoner's poison, the Spellarcher's arrows' plus, the Fine Bow ----
; (DSCLOG's PROBE_POISON, PROBE_ARROW's ARROW_PLUS_NOW and FINE_HIT on the sequel's weapon attack routine,
; 5CE80h; sites 214-215, the header's +2088 to +2095; kits.py, spellarrows.py)
; - POISON_HIT (site 214): "cmp word [es:bx+10h],0" (5D20Dh; 5 bytes) after a weapon's hit (CAH_HIT's
;   5D1FEh before it), where the attack asks whether the weapon (item [BP+12h], ES:BX) casts a spell (its
;   +10h, the spell + 1) and, with none and nothing in the quiver's (308h:[7]), leaves (5D2F5h). A
;   Poisoner's (KIT_POISONER awake, RULE_HI_KITS) first melee hit in a fight ([BP+16h] 1: not a shot or a
;   throw) with each hand's weapon (POISON_USED: bit N party member N's main hand, N + 4 its off hand, the
;   item's slot +13h POISON_OFF_SLOT; cleared at a fight's first round, ACID_ROUND, as a dose is used up)
;   with a weapon of no spell of its own (one with a spell casts that, as it does: no dose used) is
;   answered "a spell" (ZF clear) and PZ_ARMED set: PLAIN_ARROW (5D248h) then makes the hit's spell the
;   monsters' poison, RAV_POISON_POWER (273, the sequel's "poison (10 damage)", SL's power 176 by its
;   record), and the game casts it on the target as a weapon's spell (608h:89h, WEAPON_CAST's level 6 and
;   no roll to hit): its save (paralysis/poison/death) and its 10 damage the game's. POISON_DOSES counts.
; - ARROW_PLUS (site 215): "mov es:[0009h],al" (5D456h; 4 bytes) in the routine finding a missile
;   weapon's ammunition (5D3BAh; [BP+0Ch] the weapon's type, DI the ammunition's item, ES 308h), where it
;   keeps the ammunition's plus (AL) for the shot's damage (5D021h) and its magic (the better of the
;   weapon's and the ammunition's, 5C7B5h): SL's PROBE_ARROW. Spell arrows (named AP_ARROW_NAME to +3, the
;   Loader's names: ravager.mod_name of spellarrows' entries) shot from a bow by a Spellarcher whose turn
;   it is (WHOSE_TURN's combatant, KIT_SPELLARCHER awake), or by anyone not in the party, are +1 from its
;   SPELL_ARROW_PLUS1st level, +2 from its 2nd, +3 from its 3rd (AP_LEVEL: a party member's preserver
;   level, anyone else's highest), where better than their own; other arrows as they are. ARROW_PLUSES counts.
; - FINE_HIT (from OFF_HAND, whatever the rules, as DSCLOG's): the THAC0 ([BP+0Ah]) 1 better for an attack
;   with the Fine Bow (item [BP+12h] named RAV_FINE_NAME: the Spellarcher's starting bow, kept so by the
;   party transfer; a bow of fine make, not magic). FINE_HITS counts.
RAV_POISON_POWER  equ 273
POISON_OFF_SLOT   equ 10            ; (an item's slot, +13h: the left hand)
ITEM_SLOT         equ 0x13
ITEM_NAME_W       equ 0x14
AP_ARROW_NAME     equ 256 + 42      ; (ravager.mod_name(0x16C): Burning, Chill, Shocking, Vampiric Arrows)
RAV_FINE_NAME     equ 256 + 49      ; (ravager.mod_name(0x173): the Fine Bow)
SPELL_ARROW_PLUS1 equ 5             ; (the preserver levels: kits.SPELL_ARROW_LEVELS)
SPELL_ARROW_PLUS2 equ 9
SPELL_ARROW_PLUS3 equ 13
poison_hit:
        pushad
        push es
        cmp word [es:bx + 0x10], 0
        jne .flags                      ; (the weapon's own spell: cast as it is)
        test word [cs:rules_hi], RULE_HI_KITS
        jz .none
        cmp word [bp + 0x16], 1
        jne .none                       ; (a shot or a throw)
        mov ax, [bp + 0x0E]
        cmp ax, 3
        ja .none                        ; (not a party member)
        call cr_is
        db KIT_POISONER
        jne .none
        mov cx, ax
        cmp byte [es:bx + ITEM_SLOT], POISON_OFF_SLOT
        jne .hand
        add cx, 4
.hand:  bt word [cs:poison_used], cx
        jc .none                        ; (that weapon's dose used this fight)
        bts word [cs:poison_used], cx
        mov byte [cs:pz_armed], 1
        inc word [cs:poison_doses]
        or ax, 1                        ; (ZF clear: "a spell")
        jmp .flags
.none:  cmp word [es:bx + 0x10], 0
.flags: pushf
        pop ax
        jmp acid_flags
pz_armed db 0                           ; (1 from POISON_HIT to PLAIN_ARROW: this hit's spell the poison)

arrow_plus:
        push bx
        push cx
        push si
        push ax
        test word [cs:rules_hi], RULE_HI_KITS
        jz .store
        mov si, [bp + 0x0C]
        cmp si, KIND_TYPES
        jae .store
        cmp byte [cs:si + kind_of_type], BOW_KIND
        jne .store                      ; (not a bow: sling stones as they are)
        push es
        imul bx, di, ITEM_SIZE
        les si, [ITEMS_PTR]
        add bx, si
        mov si, [es:bx + ITEM_NAME_W]
        pop es
        sub si, AP_ARROW_NAME
        cmp si, 4
        jae .store                      ; (not a spell arrow)
        mov ax, [WHOSE_TURN]
        call fighter_creature
        jc .store
        call ap_level
        jc .store                       ; (a party member who isn't a Spellarcher: as they are)
        mov ah, al
        xor cl, cl
        cmp ah, SPELL_ARROW_PLUS1       ; (each "sbb cl, -1" adds 1 when AH is at least the level)
        sbb cl, -1
        cmp ah, SPELL_ARROW_PLUS2
        sbb cl, -1
        cmp ah, SPELL_ARROW_PLUS3
        sbb cl, -1
        pop ax
        cmp al, cl
        jge .own
        mov al, cl
        inc word [cs:arrow_pluses]
.own:   push ax
.store: pop ax
        mov [es:0x9], al
        pop si
        pop cx
        pop bx
        iret

; AP_LEVEL: AL the level spell arrows' archer, creature AX, shoots them at (their plus): a party member's
; (a Spellarcher's: CF set for any other) preserver level (class PRESERVER_CLASS or WIZARD_NEW_CLASS among
; its sheet's classes), anyone else's highest (spellarrows.archer_level). DS the game's; others but AX kept.
ap_level:
        push bx
        push cx
        push si
        push es
        mov si, ax
        cmp si, 3
        ja .sheet
        call cr_is
        db KIT_SPELLARCHER
        jne .no
.sheet: call kit_sheet                  ; (ES:BX the sheet)
        xor ax, ax
        mov cx, 3
.cls:   mov ah, [es:bx + SHEET_LEVELS]
        cmp si, 3
        ja .any
        cmp byte [es:bx + SHEET_CLASSES], PRESERVER_CLASS
        je .take
        cmp byte [es:bx + SHEET_CLASSES], WIZARD_NEW_CLASS
        je .take
        jmp .next
.any:   cmp ah, al
        jbe .next
.take:  mov al, ah
.next:  inc bx
        loop .cls
        xor ah, ah
        clc
        jmp .out
.no:    stc
.out:   pop es
        pop si
        pop cx
        pop bx
        ret

fine_hit:
        push ax
        push bx
        push es
        mov bx, [bp + 0x12]
        cmp bx, NO_ITEM
        jae .out                        ; (no weapon)
        imul bx, bx, ITEM_SIZE
        les ax, [ITEMS_PTR]
        add bx, ax
        cmp word [es:bx + ITEM_NAME_W], RAV_FINE_NAME
        jne .out
        dec word [bp + 0x0A]            ; (+1 to hit)
        inc word [cs:fine_hits]
.out:   pop es
        pop bx
        pop ax
        ret

; LOCK_SITE (site 241, RULE_THIEF_TABLE: Thieves as in AD&D, always on; DSCLOG's LOCK_SITE on the sequel's
; addresses): "mov [bp-2],ax" (8C7E6h; SL's 803D3h, the same routine at 8C7CBh: character [BP+6], skill [BP+8],
; bonus [BP+0Ch], a d100 under [BP-2] succeeds) in the game's thief skill check. Does the MOV; then for open
; locks by a party member, a lock that member failed at the thief level it has now (PO: Skills & Powers:
; "If a thief fails to open a lock, he cannot attempt to open that lock again until advancing a level") is
; out of reach: [BP-2] LOCK_NEVER, which no roll is under (the dice log names it). The lock is the thing the
; running script was started on (the load + 3C13h at 365h, SL's 3781h) in the region the party is in
; (DS:140Ch, SL's 117Ch); the Loader keeps LOCK_BARRED (the tail's, FS: dsloader/locks.py): for each member
; 0-3, LOCK_MAX (region, thing) word pairs, FFFFh for none.
LOCK_SKILL   equ 1                ; (open locks: game.THIEF_SKILLS' second)
LOCK_NEVER   equ -2000
LOCK_MAX     equ 4
LOCK_REGION  equ 0x140C           ; DS: the region the party is in
LOCK_TALK_GAP equ 0x47E0 - 0x3C13 ; (DS less the talk's segment) and the thing the running script
LOCK_TALK    equ 0x365            ;   was started on there
lock_site:
        mov [bp - 2], ax
        cmp word [bp + 8], LOCK_SKILL
        jne .out
        cmp word [bp + 6], 4
        jae .out
        pusha
        push es
        push fs
        call tail_fs
        mov ax, ds
        sub ax, LOCK_TALK_GAP
        mov es, ax
        mov dx, [es:LOCK_TALK]
        mov ax, [LOCK_REGION]
        mov bx, [bp + 6]
        shl bx, 4                       ; (LOCK_MAX x 4 bytes a member)
        add bx, lock_barred
        mov cx, LOCK_MAX
.each:  cmp [fs:bx], ax
        jne .next
        cmp [fs:bx + 2], dx
        jne .next
        mov word [bp - 2], LOCK_NEVER
        inc word [cs:lock_bars]
        jmp .done
.next:  add bx, 4
        loop .each
.done:  pop fs
        pop es
        popa
.out:   iret
section tail
lock_barred times 4 * LOCK_MAX dw 0xFFFF, 0xFFFF
section image

; GL_ARMOUR (site 242, always on: SL's PROBE_WORN at its AC test, a fix of the game's own): the AC routine's
; "test word es:[bx+10h],40h" (5D6B3h, SL's 58F86h; ES:BX the sheet of thing SI, the sequel's 40h a gladiator)
; gave the gladiator's armour optimisation (1 a 5 levels) with no armour on, where Dark Sun gives it to armour
; worn. ZF clear only for a gladiator who wears armour on its arms, legs, head or chest (ARMOUR_WORN: not a
; shield, bracers or a robe); RETF 2 keeps the flags for the game's "jz".
gl_armour:
        test word [es:bx + 0x10], 0x40
        jz .out                         ; not a gladiator (ZF set)
        push es
        push bx
        push dx
        mov dx, ds
        add dx, FIGHTERS_SEG
        mov es, dx
        imul bx, si, 3
        mov dx, [es:bx + FIGHTERS_OFF + 1] ; its creature (a thing of kind 2 here)
        call armour_worn
        pop dx
        pop bx
        pop es
        jc .armour
        inc word [cs:gl_bare]
        cmp al, al                      ; none: ZF set, no bonus
        jmp short .out
.armour: or sp, sp                      ; ZF and CF clear: the bonus
.out:   retf 2

; AI_WALL (site 243, "ai_wall"; DSCLOG's NS_WALL): the four pushes of the two points the computer's cast is
; aimed at (5EE6Bh, 28h bytes: "mov ax,[bp-4] / shl ax,4 / add ax,8 / push ax", then [bp-2]'s, twice; [BP-2],
; [BP-4] the cell chosen), in the AI's casting (5EE00h, SL's 5A31Fh: the caster SI, the spell DI). The game
; gave both points the cell's middle, so a wall, as long as its points are apart, was a single point. A wall
; (WALL_SPELLS: the sequel's records with +0Ch 2) now runs across the line from the caster (its place,
; sixteenths of a cell, at the map thing's DS:67C5h + SI x 25h, SL's 669Dh + SI x 20h) to the cell:
; WALL_HALF either way, along an axis, or the diagonal, whichever is nearest square to the line; anything
; else at the middle, as before. The four words go under the INT's frame, where the pushes left them
; (point 1 on top: x, y). The second copy of the pushes (5F6D1h) is SL's 5AA05h, which DSCLOG leaves too.
WALL_HALF  equ 32               ; (two cells: a wall four long)
WALL_DIAG  equ 23               ; (WALL_HALF / sqrt(2))
WALL_POS   equ 0x67C5
WALL_THING equ 0x25
ai_wall:
        sub sp, 8
        push bp
        mov bp, sp
        push ax
        mov ax, [bp + 10]       ; (the frame, 8 lower)
        mov [bp + 2], ax
        mov ax, [bp + 12]
        mov [bp + 4], ax
        mov ax, [bp + 14]
        mov [bp + 6], ax
        pusha
        mov bx, wall_spells
        mov cx, di              ; (the spell)
        call kit_word_in
        lahf
        imul bx, si, WALL_THING ; (the caster)
        mov si, [bp]            ; (the game's BP)
        mov cx, [ss:si - 2]
        shl cx, 4
        add cx, 8               ; (CX, DX the middle)
        mov dx, [ss:si - 4]
        shl dx, 4
        add dx, 8
        xor si, si              ; (SI, DI the half-wall, none)
        xor di, di
        sahf
        jne .put
        inc word [cs:ai_walls]
        mov ax, cx
        sub ax, [bx + WALL_POS] ; (AX, BX the line: the middle less the caster's place)
        mov bx, [bx + WALL_POS + 2]
        neg bx
        add bx, dx
        push ax
        push bx
        or ax, ax
        jns .xa
        neg ax
.xa:    or bx, bx
        jns .ya
        neg bx
.ya:    mov di, bx              ; (|dy|)
        shl di, 1
        cmp ax, di
        jbe .notx
        pop bx                  ; mostly across: the wall up and down
        pop ax
        xor si, si
        mov di, WALL_HALF
        jmp short .put
.notx:  shl ax, 1
        shr di, 1
        cmp di, ax
        jbe .diag
        pop bx                  ; mostly up or down: the wall across
        pop ax
        mov si, WALL_HALF
        xor di, di
        jmp short .put
.diag:  pop bx                  ; slanting: the other diagonal
        pop ax
        mov si, WALL_DIAG
        mov di, WALL_DIAG
        xor ax, bx              ; (the same signs: down to the left and up to the right)
        js .put
        neg si
.put:   mov ax, cx
        add ax, si
        mov [bp + 8], ax        ; point 1: the middle plus the half
        mov ax, dx
        add ax, di
        mov [bp + 10], ax
        mov ax, cx
        sub ax, si
        mov [bp + 12], ax       ; point 2: less it
        mov ax, dx
        sub ax, di
        mov [bp + 14], ax
        popa
        pop ax
        pop bp
        iret
; the wall spells (their records' +0Ch 2, a wall's target: RESOURCE.GFF's, ravlog.spell_table)
wall_spells dw 11, 54, 55, 66, 67, 70, 75, 100, 114, 154, 161, 206, 207, 208, 214, 222, -1

; KREEN_CLAWS (site 244, "kreen_claws"; the thri-kreen's part of DSCLOG's NS_FIST): "cmp word [bp-0Ch],0"
; (5C86Dh, SL's 58226h; 4 bytes) in the melee attack routine (5C5E1h, SL's 58019h: SI the attacker; [BP-2]
; the weapon's item, -1 for a natural attack; [BP-0Ch] its magic; [BP-12h] the attacker's sheet; [BP-14h]
; the hit's damage kinds, the game's crushing (8) for any natural attack). A thri-kreen of the party's
; claws and bite cut: a natural attack of one is slashing, not crushing (monsters' own as the game has
; them), so a creature crushing weapons can't hurt is no longer safe from them. Then that compare, its
; flags kept (RETF 2).
DMG_CRUSHING equ 0x08
DMG_SLASHING equ 0x10
kreen_claws:
        cmp word [bp - 2], -1
        jne .test
        cmp si, 4                       ; (the party's combatants: 0-3)
        jae .test
        push es
        push bx
        push ax
        imul ax, [bp - 0x12], SHEET_SIZE
        les bx, [SHEETS_PTR]
        add bx, ax
        cmp byte [es:bx + SH_RACE], WP_THRI_KREEN
        pop ax
        pop bx
        pop es
        jne .test
        test word [bp - 0x14], DMG_CRUSHING
        jz .test
        and word [bp - 0x14], ~DMG_CRUSHING
        or word [bp - 0x14], DMG_SLASHING
        inc word [cs:kreen_cuts]
.test:  cmp word [bp - 0x0C], 0
        retf 2

; BERSERK (sites 245, 246; SL's NS_SIDE, a fix of the game's own): a berserk creature's side (its creature's
; +15h) is rolled anew, a d2, on each of its turns the computer runs (the AI's routine, 0618h:000Eh, 81770h;
; SL's 8053:000Eh), and when Berserk (effect 7) ended nothing put it back: the end routine (0618h:1017h)
; has cases for Controlled and Confused (20, 21: 120Dh, the side from the effect record's +9, which the add's
; own cases put there, 0D2Dh: the side the creature had) and the clamp of Tenser's Transformation (102, the
; sequel's other "Berserk", 106Dh), none for 7: so a party member could stay on a side the d2 gave it.
; - BERSERK_ADD (site 245) replaces "jmp 0F1Eh" (822A1h; 3 bytes), the add's check routine (0618h:0AF9h:
;   [BP+6] the thing, SI too, [BP+0Ah] the effect, [BP+0Ch] a far pointer to the record's +9 to come) where
;   the effect has no case of its own: for Berserk the side kept there, as Confused's case keeps it; a
;   Berserk the thing already has gives its kept side (the side now is a rolled one). Then 0F1Eh.
; - BERSERK_END (site 246) replaces "jmp 12E9h" (827D6h; 3 bytes) in the end routine ([BP+8] the effect, DX
;   its record): Berserk to Controlled's case (120Dh, the side given back), any other on to 12E9h.
BZ_BERSERK  equ 7
BZ_SIDE     equ 0x15                    ; (the creature's side)
BZ_EXTRA    equ 9                       ; (an effect record's +9: the side kept)
BZ_ADD_TAIL equ 0x0F1E - 0x0B34         ; (less the way back: past the INT and the site's number)
BZ_END_CASE equ 0x120D - 0x1069
BZ_END_TAIL equ 0x12E9 - 0x1069
berserk_add:
        cmp word [bp + 0x0A], BZ_BERSERK
        jne .out
        pusha
        push es
        mov ax, ds
        sub ax, EFFECTS_GAP
        mov es, ax
        mov bx, EFFECTS_BASE
        mov cx, [EFFECTS_COUNT]
        cmp cx, 400
        ja .now
        jcxz .now
.find:  cmp [es:bx], si                 ; (a Berserk of this thing's already: its kept side)
        jne .next
        cmp byte [es:bx + 6], BZ_BERSERK
        jne .next
        mov al, [es:bx + BZ_EXTRA]
        jmp short .put
.next:  add bx, 10
        loop .find
.now:   mov ax, ds                      ; (else the side it has now)
        add ax, FIGHTERS_SEG
        mov es, ax
        imul bx, si, 3
        mov ax, [es:bx + FIGHTERS_OFF + 1]
        imul ax, ax, CREATURE_SIZE
        les bx, [CREATURES_PTR]
        add bx, ax
        mov al, [es:bx + BZ_SIDE]
.put:   mov ah, 0
        les bx, [bp + 0x0C]
        mov [es:bx], ax
        inc word [cs:berserk_sides]
        pop es
        popa
.out:   push bp
        mov bp, sp
        add word [bp + 2], BZ_ADD_TAIL
        pop bp
        iret
berserk_end:
        push bx
        mov bx, BZ_END_TAIL
        cmp word [bp + 8], BZ_BERSERK
        jne .go
        mov bx, BZ_END_CASE
        inc word [cs:berserk_ends]
.go:    push bp
        mov bp, sp
        add [bp + 4], bx                ; (the way back: past BX and BP)
        pop bp
        pop bx
        iret

; ---- THE EFFECTS SCREEN'S CHARGES: DSCLOG's EF_CHARGES (its charges part), with SL's fix ----
; The Effects screen's handler for its cells (8AB13h) names the effect under the pointer (event 2, [BP+0Ah]) on
; the line under the cells: the effect's record (selector 318h, 31 bytes each: its name, 29, then its icon; the
; push of 318h:effect x 31 at 8ABB9h), "push 2C06h / push dword [1431h]" (the line, the window), then the
; name's call (5F0h:61h). SL's EF_CHARGES names it with its charges, "Armor (3 charges)", where the effect
; has some left (the active effect's +8: Armor's hits, Mirror Image's images, Stoneskin's blows...) and they
; mean something: a spell lasting a number of uses (its record's time negative, not -9999: EC_USES), or an
; effect with a timer (an "effect ends" event, kind 7, for this thing and handle, in the game's queue: DS:2A63h
; far, its count DS:2A6Bh, 11h bytes each, SL's 2FBEh and 2FC6h). Not an item's power, cast for -9999 with
; no timer, whose +8 is a stray 15 (9999's low byte): Shadowseeker's Detect Invisible said "(15 CHARGES)" in
; SL before its fix (GAME-BUGS.md), and so here.
; - EF_CHARGES (site 247) replaces those two pushes (8ABBDh; 8 bytes, the INT, the site's number and 6 NOPs):
;   it makes them, under the INT's frame (the frame moved down 6 bytes), and with charges to show puts the
;   name's far pointer, already pushed, on EC_TEXT (the tail's), the record's name and its charges; the way
;   back past the NOPs (8ABC5h, the call). Only for the effect's push: the segment pushed the one the code's
;   "push 318h" has (its word as the overlay manager fixed it up, 6 bytes back from the way back), and the
;   offset a whole record. The character on show is USE_WHO's (370h:0B44h), as EF_ROWS's.
; - SL's other parts (EC_MOD, from the Loader's EF_STATS as SL's from its STATS): a party member's Enlarge named
;   with its melee damage instead, "Enlarged (+90% dice)" ("damage" without RULE_HI_ENLARGE), from the level
;   the Loader puts there (the game's 608h:52h sum, ENL_SITE's), and Barkskin, Flesh Armor and Magical Vestments
;   with the AC they give, "Barkskin (AC 4)" (the AC routine's 85BA7h: 6 - level/4, 10 - level, 5 less 1 for
;   each 3 levels past 5, SL's 7C557h the same); only with the Loader there (LOADER_FRESH). Mirror Images
;   from Reflected Image (the record's spell 323) named "Reflected Image" (EC_REFLECT), with its charges.
;   Not ported: Reflected Image's own icon (the cells' icons are drawn elsewhere).
EC_PAST       equ 0x8ABC5 - 0x8ABC0     ; (the bytes replaced past the way back)
EC_SEG_BACK   equ 0x8ABC0 - 0x8ABBA     ; ("push 318h"'s word, back from the way back)
EC_LINE       equ 0x2C06                ; (the line's id, the game's push)
EC_RECORD     equ 31
EC_NAME_MOST  equ 29
EC_EFFECTS    equ 120                   ; (the effect bits: 0-119)
EVENT_QUEUE   equ 0x2A63                ; DS: the game's timed events (far), and their count
EVENT_COUNT   equ 0x2A6B
EVENT_SIZE    equ 0x11                  ; (+4 the kind, +5 the thing, +7 the effect's handle)
EVENT_EFFECT_ENDS equ 7
ef_charges:
        sub sp, 6                       ; (room for the game's three pushes)
        push bp
        mov bp, sp                      ; [bp+8] IP, [bp+10] CS, [bp+12] FLAGS, [bp+14] the name pushed, far
        pushad
        push es
        push fs
        les si, [bp + 8]
        mov dx, [es:si - EC_SEG_BACK]   ; (DX the effects' segment, as fixed up)
        lea ax, [si + EC_PAST]
        mov [bp + 2], ax                ; the frame moved down: IP past the NOPs, CS, FLAGS
        mov ax, [bp + 10]
        mov [bp + 4], ax
        mov ax, [bp + 12]
        mov [bp + 6], ax
        mov eax, [WIN_SHOWN]            ; (the game's "push dword [1431h]", then "push 2C06h" above it)
        mov [bp + 8], eax
        mov word [bp + 12], EC_LINE
        cmp [bp + 16], dx
        jne .out                        ; (another line's text: the lower panel's, a button's)
        mov ax, [bp + 14]
        xor dx, dx
        mov cx, EC_RECORD
        div cx
        or dx, dx
        jnz .out
        cmp ax, EC_EFFECTS
        jae .out
        mov cl, al                      ; (CL the effect)
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov ax, [es:USE_WHO_OFF]        ; (AX the character on show)
        call ec_counted                 ; (BL its charges, or CF clear; DX the spell)
        setc ch                         ; (CH 1: charges to name)
        mov bh, 0                       ; (BH 1: the line made here)
        call tail_fs
        mov di, ec_text
        push ax                         ; (the character)
        cmp cl, MIRROR_EFFECT
        jne .own
        cmp dx, EC_REFLECT_SPELL
        jne .own
        mov si, ec_reflect              ; (Reflected Image's Mirror Images: its own name)
        mov bh, 1
.rname: mov al, [fs:si]
        or al, al
        jz .named
        mov [fs:di], al
        inc si
        inc di
        jmp .rname
.own:   push ds
        lds si, [bp + 14]               ; (the record's name)
        push cx
        mov cx, EC_NAME_MOST
.name:  lodsb
        or al, al
        jz .end
        mov [fs:di], al
        inc di
        loop .name
.end:   pop cx
        pop ds
.named: pop ax
        call ec_mod                     ; (Enlarge's damage or an armour spell's AC after it, CF set)
        jc .modded
        or ch, ch
        jz .plain
        mov word [fs:di], ' ('
        add di, 2
        mov al, bl
        call ec_itoa
        mov si, ec_word
.word:  mov al, [cs:si]
        mov [fs:di], al
        inc si
        inc di
        or al, al
        jnz .word
        dec di
        cmp bl, 1
        je .shut
        mov byte [fs:di], 's'
        inc di
.shut:  mov word [fs:di], ')'
        inc word [cs:ef_charge_lines]
        or bh, bh
        jnz .modded                     ; (Reflected Image's: both counted)
        jmp .set
.plain: or bh, bh
        jz .out
        mov byte [fs:di], 0
.modded:
        inc word [cs:ef_mod_lines]
.set:   mov word [bp + 14], ec_text
        mov [bp + 16], fs
.out:   pop fs
        pop es
        popad
        pop bp
        iret
ec_word db ' charge', 0

; EC_COUNTED: CF set, BL the charges, if thing AX's effect CL has charges that mean something (EF_CHARGES);
; DX the spell that made it (FFFFh: thing AX hasn't it). DS the game's; BX, DX, SI, ES changed.
ec_counted:
        push cx
        mov dx, ds
        sub dx, EFFECTS_GAP
        mov es, dx
        mov si, EFFECTS_BASE
        mov dx, [EFFECTS_COUNT]
        cmp dx, 400
        ja .no
.find:  or dx, dx
        jz .no
        cmp [es:si], ax
        jne .next
        cmp [es:si + 6], cl
        je .found
.next:  add si, 10
        dec dx
        jmp .find
.found: mov bx, [es:si + 7]             ; (BH the charges, BL the handle)
        mov dx, [es:si + 4]             ; (the spell that made it)
        or bh, bh
        jz .none
        push fs
        call tail_fs
        mov si, ec_uses
.uses:  cmp word [fs:si], -1
        je .timer
        cmp [fs:si], dx
        je .yes_fs
        add si, 2
        jmp .uses
.timer: pop fs
        les si, [EVENT_QUEUE]           ; (else only if timed: an item's power, cast for -9999, and a
        mov cx, [EVENT_COUNT]           ;  permanent effect have none, and +8 a stray)
        cmp cx, 1000
        ja .none
.event: jcxz .none
        cmp byte [es:si + 4], EVENT_EFFECT_ENDS
        jne .on
        cmp [es:si + 5], ax
        jne .on
        cmp [es:si + 7], bl
        je .yes
.on:    add si, EVENT_SIZE
        dec cx
        jmp .event
.yes_fs:
        pop fs
.yes:   mov bl, bh
        pop cx
        stc
        ret
.no:    mov dx, 0xFFFF
.none:  pop cx
        clc
        ret

; EC_MOD: (EF_CHARGES) CF set and the line's end at FS:DI (DI past it) made SL's mod line where party member AX's
; effect CL is Enlarge, " (+90% dice)", or an armour spell, " (AC 4)", and the Loader's EF_STATS (FS's tail)
; has a level or an AC for it; CF clear, nothing written, else. AX and DI changed only with CF set.
EC_ENLARGE   equ 32                     ; (the sequel's effects: Enlarged, and the armour spells in EF_STATS' order)
EC_BARKSKIN  equ 6
EC_FLESH     equ 40
EC_VESTMENTS equ 104
EC_REFLECT_SPELL equ 323
EF_STATS_SIZE equ 4                     ; (+0 Enlarge's level, 0 none; +1 to +3 the ACs, signed, EC_NO_AC none)
EC_NO_AC     equ 0x80
ec_mod:
        cmp ax, 4
        jae .no
        call loader_fresh
        jnz .no
        push bx
        push si
        mov si, ax
        shl si, 2
        add si, ef_stats                ; (the member's row)
        cmp cl, EC_ENLARGE
        je .enlarge
        mov bx, 1
        cmp cl, EC_BARKSKIN
        je .ac
        inc bx
        cmp cl, EC_FLESH
        je .ac
        inc bx
        cmp cl, EC_VESTMENTS
        jne .not
.ac:    mov al, [fs:si + bx]
        cmp al, EC_NO_AC
        je .not
        mov dword [fs:di], ' (AC'
        mov byte [fs:di + 4], ' '
        add di, 5
        or al, al
        jns .acn
        mov byte [fs:di], '-'
        inc di
        neg al
.acn:   call ec_itoa
        mov si, ec_shut
        jmp .tail
.enlarge:
        mov al, [fs:si]
        or al, al
        jz .not
        mov word [fs:di], ' ('
        mov byte [fs:di + 2], '+'
        add di, 3
        call ec_itoa                    ; (the level, then a 0: 10% a level)
        mov si, ec_dice
        test word [cs:rules_hi], RULE_HI_ENLARGE
        jnz .tail
        mov si, ec_damage
.tail:  mov al, [cs:si]
        mov [fs:di], al
        inc si
        inc di
        or al, al
        jnz .tail
        dec di
        pop si
        pop bx
        stc
        ret
.not:   pop si
        pop bx
.no:    clc
        ret
ec_dice   db '0% dice)', 0
ec_damage db '0% damage)', 0
ec_shut   db ')', 0

; EC_ITOA: AL (unsigned) in decimal at FS:DI, DI past it. Others kept.
ec_itoa:
        push ax
        push cx
        xor ah, ah
        mov cl, 100
        div cl                          ; (AL the hundreds, AH the rest)
        or al, al
        jz .tens
        add al, '0'
        mov [fs:di], al
        inc di
.tens:  mov ch, al                      ; (nonzero once a digit is written)
        mov al, ah
        xor ah, ah
        mov cl, 10
        div cl
        or ch, ch
        jnz .ten
        or al, al
        jz .ones
.ten:   add al, '0'
        mov [fs:di], al
        inc di
.ones:  add ah, '0'
        mov [fs:di], ah
        inc di
        pop cx
        pop ax
        ret
section tail
; the spells that last a number of uses (their records' time, +7, -1: RESOURCE.GFF's, ravlog.spell_table; and
; Reflected Image, 323, Mirror Image's record), ended by -1
ec_uses dw 0, 17, 19, 46, 52, 86, 104, 120, 153, 167, 168, 179, 200, 225, 285, 301, 323, -1
ec_reflect db 'Reflected Image', 0      ; (EC_REFLECT: its Mirror Images' name)
ef_stats times 4 db 0, EC_NO_AC, EC_NO_AC, EC_NO_AC   ; (EF_STATS: the Loader's, a row a party member)
section tailz
ec_text times 48 db 0                   ; (EF_CHARGES' line: the name, then " (255 charges)" at most)
section image

; THE QUIVER'S LAST ARROW (always on: SL's AMMO_CAP, AMMO_TURN and AMMO_OKAY, a fix of the game's own; the
; sequel's weapon attack routine, 5CF??h, is SL's 5883Ah with the round's attacks in [BP-0Ah], SL's [BP-8]).
; The routine cuts a shot's attacks to the arrows (or stones) left, "Out of ammo" with none, and once its
; attacks are made marks the attacker's attacks for the round spent (selector 308h +184h 63h at 5D339h, "cmp
; ax,[bp-0Ah] / jl" at 5D32Ch), which ends the turn: so a party member whose quiver ran dry lost the turn with
; shots still due, and could ready no more arrows for them.
; - AMMO_CAP (site 217): "mov ax,[bp-8] / mov [bp-0Ah],ax" (5D031h; 6 bytes: the cut, [BP-8] the arrows),
;   the round's attacks before it kept (AMMO_REAL), then cut as before, so no shot is made without an arrow.
; - AMMO_TURN (site 218): "cmp ax,[bp-0Ah]" (5D32Ch; 3 bytes; the "jl" after it kept), the attacks made
;   against the round's: for a party member (the attacker, [BP+0Eh], 0-3) whose shots were cut, against the
;   round's attacks before the cut, so the turn stays its own while attacks are left (AMMO_OUT that member);
;   for the others, and every attack not cut, against [BP-0Ah] as the game has it.
; - AMMO_OKAY (site 219): "cmp byte es:[bx+14h],1" (5CA92h, 5CAF7h, 5CB64h; 5 bytes each, their jumps NEW
;   AS OKAY's jbe/ja), the attack command's (SL's 58019h) tests of its target still Okay after the attacks:
;   Okay, the command ends the turn. For the AMMO_OUT member (the command's attacker, [BP-0Eh]) the target
;   answers as fallen, so the turn goes on as after a kill (arrows readied from the pack, the shots left
;   made, or a walk). The target itself is as it was. Others: the game's compare.
; Each keeps every register; AMMO_TURN's and AMMO_OKAY's flags are their compare's (RETF 2).
ammo_cap:
        push word [bp - 0x0A]
        pop word [cs:ammo_real]
        mov ax, [bp - 8]
        mov [bp - 0x0A], ax
        iret
ammo_turn:
        push bx
        mov bx, -1
        xchg bx, [cs:ammo_real]         ; (one shot's: never the next attack's)
        mov word [cs:ammo_out], -1
        cmp bx, -1
        je .plain
        cmp word [bp + 0x0E], 3
        ja .plain                       ; (not a party member: the game's way)
        cmp ax, bx
        jge .cmp                        ; (the round spent)
        push word [bp + 0x0E]
        pop word [cs:ammo_out]          ; (cut, with attacks left: AMMO_OKAY's)
        jmp short .cmp
.plain: mov bx, [bp - 0x0A]
.cmp:   cmp ax, bx
        pop bx
        retf 2
ammo_okay:
        push ax
        mov ax, [bp - 0x0E]
        cmp ax, [cs:ammo_out]
        jne .game
        mov al, 2                       ; (fallen, to the tests: above Okay)
        cmp al, 1
        pop ax
        retf 2
.game:  pop ax
        cmp byte [es:bx + 0x14], 1
        retf 2
ammo_real dw -1                         ; (AMMO_CAP's: the round's attacks before the cut; -1 none)
ammo_out  dw -1                         ; (AMMO_TURN's: the party member whose shots were cut, attacks left)

; A NATURAL 20 AND "CAN'T SAVE" (always on: SL's SAVE_SUM, gamepatch "save_natural"): the saving throw (the
; sequel's 66D??h, SL's 79A71h, the same code) took a natural 20 as saved before it added the modifiers
; (66E4Ah: its "jnz" made "jmp", so it goes on with them), so a creature that can't save (the modifiers'
; -100: Chaos's, Cloudkill's, Scare's below 6th level, Color Spray's) saved on a 20.
; - SAVE_SUM (site 220): "mov dl,[bp-2] / add dl,al / mov [bp-2],dl" (66E86h; 8 bytes: [BP-2] the d20, AL
;   the modifiers): the sum, kept between -SAVE_MOST and SAVE_MOST so that it stays in its byte with the
;   bonus that follows (66EA3h: -8 to +7), DL it as the game's; SV_NAT whether the d20 was a natural 20.
; - SAVE_NAT (site 221): that bonus's "add [bp-2],al" (66EA3h; 3 bytes): after it, a natural 20 makes the
;   total at least the number needed ([BP-1]), unless the total is under SAVE_CANT (the -100's). Then the
;   dice log's PROBE_SAVE (the size rule's 101 there) and the signed compare (save_signed).
SAVE_MOST equ 110
SAVE_CANT equ -50
save_sum:
        push ax
        cbw
        mov dx, ax
        movsx ax, byte [bp - 2]
        cmp ax, 20                      ; (never doubled: no_double)
        sete [cs:sv_nat]
        add ax, dx
        cmp ax, SAVE_MOST
        jle .low
        mov ax, SAVE_MOST
.low:   cmp ax, -SAVE_MOST
        jge .set
        mov ax, -SAVE_MOST
.set:   mov [bp - 2], al
        mov dl, al
        pop ax
        iret
        SHARED_save_nat
sv_nat  db 0

resident_end:
align 16
image_end:
RESIDENT_PARAS equ (resident_end - hdr + 15) / 16   ; (the segment to here: what stays of it)

; ---- the far block (FAR_INIT): the ring ----
FAR_RING   equ 0x10
FAR_END    equ FAR_RING + NENT * ESIZE
FAR_DAC    equ FAR_END                         ; the palette (DAC_TICK), 768 bytes
FAR_PANEL  equ FAR_DAC + 768                   ; the combat log's panel's picture (PANEL_BLIT)
FAR_SPANS  equ FAR_PANEL + PANEL_BYTES         ; WALL SHADOWS' spans, 6 bytes each
FAR_WS_DAC equ FAR_SPANS + WS_SPANS_MOST * 6   ; ... the palette DARK was made from
FAR_DARK   equ FAR_WS_DAC + 768                ; ... DARK (XLAT)
FAR_RED    equ FAR_DARK + 256                 ; RINGS' RED (XLAT), the Loader's
FAR_TBUF   equ FAR_RED + 256                  ; the text buffer (TEXT: PROBE_TEXT, PROBE_MSG), TSIZE bytes
FAR_LIGHT  equ FAR_TBUF + TSIZE               ; SQUARES' LIGHT (XLAT), the Loader's (dust.light_table)
FAR_RING_TAB equ FAR_LIGHT + 256               ; RINGS' RING_TAB, the Loader's: a byte a thing (THINGS)
RING_TAB_BYTES equ 520                          ; (the Loader's table: game.THINGS; MAP_COUNT of it read)
FAR_SC     equ FAR_RING_TAB + RING_TAB_BYTES     ; FIGURE SHADOWS' kept shadows (FIG_KEEP), SC_SLOTS x SC_SLOT
FAR_PUFFS  equ FAR_SC + SC_SLOTS * SC_SLOT     ; DUST's puffs (DUST_TICK, PUFF_RAISE, DUST_PASS)
FAR_DUST   equ FAR_PUFFS + PUFFS * PUFF_SIZE    ; ... their thickness by age, row and column (DUST_BUILD)
FAR_LAST_X equ FAR_DUST + DUST_BYTES             ; ... each thing's place as last seen
FAR_LAST_Y equ FAR_LAST_X + MAP_COUNT * 2
FAR_WALKED equ FAR_LAST_Y + MAP_COUNT * 2        ; ... how far each has walked since its last puff
FAR_GH_BLEND equ (FAR_WALKED + MAP_COUNT + 15) & ~15  ; SEE-THROUGH FIGURES' BLEND (GHOST_DRAW: REP_COUNT x 256)
FAR_GH_REP equ FAR_GH_BLEND + REP_COUNT * 256  ; ... REP, each of the palette's colours to one of REP_COUNT
FAR_GH_TAB equ FAR_GH_REP + 256                ; ... GHOST_TAB, a bit for each thing (the Loader's) ...
FAR_GH_CHANGED equ FAR_GH_TAB + 79             ; ... 1 once the Loader has written it anew (GHOST_UNION)
FAR_TOP    equ FAR_GH_TAB + 80
%if FAR_TOP > 0x10000
%error "the far block past the HMA's 64 KB"
%endif
FAR_PARAS  equ (FAR_TOP - FAR_RING + 15) / 16 + 1

; ---- install (not kept): its own segment, INSTALL_PARAS paragraphs into the image ----
; CS the install's (its variables and ALL_VECTORS are cs:), DS the segment's (what stays: the
; header's fields, the handlers' offsets), the PSP's paragraphs below it.
section install
install:                        ; DS = ES = PSP, CS = the install's
        mov [cs:psp], es
        mov ax, es
        add ax, 0x10
        mov ds, ax              ; (DS the segment: the image, past the PSP)
        mov si, all_vectors     ; the vectors must be free (DSCLOG's check)
        mov cx, VECTORS
.check:
        cs lodsb
        inc si
        inc si
        mov ah, 35h
        int 21h
        mov dx, es
        or dx, bx
        jz .free
        mov dx, busy
        call say
        mov ax, 4C01h
        int 21h
.free:
        loop .check
        mov ax, 3D00h           ; the game's own arrow for the scenes (CP_DATA), if the
        mov dx, POINTER_FILE    ;   Loader has written it
        int 21h
        jc .no_pointer
        mov bx, ax
        mov ah, 3Fh
        mov cx, CP_DATA_BYTES
        mov dx, cp_data
        int 21h
        mov ah, 3Eh
        int 21h
.no_pointer:
        mov es, [cs:psp]
        mov es, [es:0x2C]       ; free our copy of the environment
        mov ah, 49h
        int 21h
        mov dx, msg
        call say
        call far_init
        jnc .far
        mov dx, no_far
        call say
        mov ax, 4C01h
        int 21h
.far:
        mov si, all_vectors
        mov cx, VECTORS
.vec:   cs lodsb
        mov ah, 25h
        mov dx, [cs:si]
        inc si
        inc si
        int 21h
        loop .vec
        mov ax, 3521h           ; DOS last (PROBE_DOS_OPEN)
        int 21h
        mov [old21], bx
        mov [old21 + 2], es
        mov ax, 2521h
        mov dx, probe_dos_open
        int 21h
        mov ax, 3516h           ; the keyboard (INT16: L for the panel)
        int 21h
        mov [old16], bx
        mov [old16 + 2], es
        mov ax, 2516h
        mov dx, int16
        int 21h
        mov ax, 3533h           ; the mouse driver's (SCROLLING), if there is one
        int 21h
        mov ax, es
        or ax, bx
        jz .no_mouse
        mov [old33], bx
        mov [old33 + 2], es
        mov ax, 2533h
        mov dx, int33
        int 21h
.no_mouse:
        mov byte [hooked], 1
        mov ax, [far_seg]
        mov [ring_seg], ax
        mov [panel_seg], ax     ; (the panel's picture: in the far block)
        mov [tbuf_seg], ax      ; (the text buffer: in the far block)
        mov ax, ds
        add ax, TAIL_PARAS
        mov [tail_seg], ax      ; (the tail: the labels' slots, the item names, ...)
        mov es, [cs:psp]        ; our block cut down to the PSP, the segment and the tail, then kept
        mov bx, 0x10 + KEPT_PARAS
        mov ah, 4Ah
        int 21h
        push bx
        mov bx, GHOST_PARAS     ; the see-through figures' pixels and spans (GHOST_DRAW), if upper memory
        call umb_alloc          ;   has the room (their tables are the far block's)
        jc .no_ghost
        mov [ghost_seg], ax
.no_ghost:
        pop bx
        mov dx, bx
        mov ax, 3100h
        int 21h

; SAY: DOS's 09h, the install's text CS:DX. AX changed.
say:
        push ds
        push cs
        pop ds
        mov ah, 9
        int 21h
        pop ds
        ret

; FAR_INIT: DSCLOG's: FAR_SEG (DS:, the segment's) set and its FAR_RING to FAR_END cleared; CF if there
; was no room.
; The HMA when it is ours (XMS's, or unused: all zero), else a block of upper memory, else of
; conventional memory (FAR_SEG a paragraph below it). XMS 01h's 90h (no HMA, as DOSBox 0.74 says)
; tries the HMA if all zero; 91h (in use: DOS=HIGH, DOSBox-X's DOS in the HMA) and 92h go straight
; to a block. An HMA given but unusable (A20 refused, or still wrapping) is handed back. Kept for
; good (a TSR): A20 and the HMA never released (tests/test_far_init.py).
far_init:
        mov ax, 4300h
        int 2Fh
        cmp al, 80h
        jne .block
        mov ax, 4310h
        int 2Fh
        mov [cs:xms], bx
        mov [cs:xms + 2], es
        mov ah, 1
        mov dx, 0xFFFF
        call far [cs:xms]
        mov [cs:hma_given], al
        or ax, ax
        jnz .a20
        cmp bl, 90h
        jne .block
.a20:   mov ah, 3               ; A20 on, for good (global: the HMA's owner's, XMS's spec)
        call far [cs:xms]
        or ax, ax
        jz .drop
        push ds
        xor ax, ax
        mov ds, ax
        mov ax, 0xFFFF
        mov es, ax
        cli
        mov ax, [ds:0]
        not word [es:0x10]
        cmp ax, [ds:0]
        not word [es:0x10]
        sti
        pop ds
        jne .drop
        cmp byte [cs:hma_given], 0
        jne .hma
        mov di, FAR_RING
        mov cx, (FAR_TOP - FAR_RING) / 2
        xor ax, ax
        cld
        repe scasw
        jne .block
.hma:   mov word [far_seg], 0xFFFF
        jmp .clear
.drop:  cmp byte [cs:hma_given], 0  ; given but unusable (A20 won't come on): back to XMS (02h),
        je .block               ;   for whoever asks next
        mov byte [cs:hma_given], 0
        mov ah, 2
        call far [cs:xms]
.block: mov bx, FAR_PARAS
        call umb_alloc
        jnc .got
        mov ah, 48h
        mov bx, FAR_PARAS
        int 21h
        jc .ret
.got:   dec ax
        mov [far_seg], ax
.clear: mov es, [far_seg]
        mov di, FAR_RING
        mov cx, (FAR_TOP - FAR_RING) / 2
        xor ax, ax
        cld
        rep stosw
        clc
.ret:   ret

; UMB_ALLOC: DSCLOG's: BX paragraphs of upper memory (DOS's link and strategy as they were after);
; AX its segment, or CF.
umb_alloc:
        push bx
        mov ax, 5802h
        int 21h
        mov [cs:ua_link], al
        mov ax, 5800h
        int 21h
        mov [cs:ua_strat], ax
        mov ax, 5803h
        mov bx, 1
        int 21h
        mov ax, 5801h
        mov bx, 42h             ; (upper memory only)
        int 21h
        pop bx
        mov ah, 48h
        int 21h
        pushf
        push ax
        mov ax, 5801h
        mov bx, [cs:ua_strat]
        int 21h
        mov ax, 5803h
        xor bh, bh
        mov bl, [cs:ua_link]
        int 21h
        pop ax
        popf
        ret

ua_link   db 0
ua_strat  dw 0
xms       dd 0
hma_given db 0
psp       dw 0
msg     db 'DSCLOG2 loaded (Wake of the Ravager).', 13, 10, '$'
busy    db 'DSCLOG2: interrupts 60h-61h in use (already loaded?). Not loaded.', 13, 10, '$'
no_far  db 'DSCLOG2: no memory for its ring. Not loaded.', 13, 10, '$'

%macro vector 2
        db %1
        dw %2
%endmacro
all_vectors:
        vector VEC_RAND, int_rand
        vector VEC_SAVE, probe_save
        vector VEC_AC, probe_ac
        vector VEC_PIC_FULL, pic_full
        vector VEC_PIC_PLACE, pic_place
        vector VEC_PIC_COUNT, pic_count
        vector VEC_PIC_FAIL, pic_fail
        vector VEC_REAR, missile_rear
        vector VEC_REST_POISON, rest_poison
        vector VEC_NPP, npp_save
        vector VEC_ACID_ROUNDS, acid_rounds
        vector VEC_ACID_BURN, acid_burn
        vector VEC_ACID_ONCE, acid_once
        vector VEC_ACID_USE, acid_use
        vector VEC_ACID_ROUND, acid_round
        vector VEC_IMAGE, image_spell
        vector VEC_BLOW, image_blow
        vector VEC_USE, probe_use
        vector VEC_WIN, probe_win
        vector VEC_ITEM_BOX, probe_item_box
        vector VEC_CHAR, probe_char
        vector VEC_CAST, probe_cast
        vector VEC_SCROLL, probe_scroll
        vector VEC_TICK, probe_tick
        vector VEC_FLIP, flip_site
        vector VEC_POINTER, probe_pointer
        vector VEC_CENTRE, probe_centre
        vector VEC_FOLLOW, probe_follow
        vector VEC_VIEW, probe_view
        vector VEC_LOOK, probe_look
        vector VEC_CR_HP, probe_cr_hp
        vector VEC_HP_BEST, probe_hp_best
        vector VEC_HELM_AC, probe_helm_ac
        vector VEC_BOX_AC, probe_box_ac
        vector VEC_HELD_HIT, held_hit
        vector VEC_HELD_DAMAGE, held_damage
        vector VEC_TWO, probe_two
        vector VEC_OFF_HAND, off_hand
        vector VEC_ROLL_MAX, roll_max_hp
        vector VEC_TWO_HANDED, two_handed
        vector VEC_CAH_TWO, cah_two
        vector VEC_CAH_SWING, cah_swing
        vector VEC_CAH_HIT, cah_hit
        vector VEC_CAH_MOVE, cah_move
        vector VEC_REACH, reach_site
        vector VEC_RANGER_LEVEL, ranger_level
        vector VEC_ENL_ROLL, enl_roll
        vector VEC_ENL_SITE, enl_site
        vector VEC_SCROLL_LEARN, scroll_learn
        vector VEC_LEARN_SAID, learn_said
        vector VEC_LEARN_REFUSED, learn_refused
        vector VEC_PICK_ANY, pick_any
        vector VEC_PICK_LIST, pick_list
        vector VEC_PICK_PAGE, pick_page
        vector VEC_BLUR_SAVE, blur_save
        vector VEC_FSHIELD_SAVE, fshield_save
        vector VEC_SITE, site_int
VECTORS equ ($ - all_vectors) / 3

; ---- THE IMAGE'S PARTS: the segment (to IMAGE_END), the tail, the install; each a whole number of
; paragraphs, so that each starts where the paragraphs before it end ----
align 16
install_end:
section tail
align 16
tail_mid:
section tailz
align 16
tail_end:
section install
TAIL_PARAS    equ (image_end - hdr) / 16                ; the tail's paragraph in the image
TAIL_LEN      equ ((tail_mid - tail_start) + (tail_end - tailz_start)) / 16
KEPT_PARAS    equ TAIL_PARAS + TAIL_LEN                 ; what stays: the segment and the tail
INSTALL_PARAS equ KEPT_PARAS                            ; the install's paragraph, after them
image_len equ (INSTALL_PARAS * 16) + (install_end - install)
LOAD_EXTRA equ (STACK + 15) / 16

; UPPER MEMORY (the audit's R3, measured 2026-11-27 with UMBPLUS.COM, as the Loader starts the sequel):
; one block, CA00h-EFFFh, its first 9 paragraphs a free scrap ahead of the helper's MCB at CA0Ah; the
; game puts nothing there (no overlay or music buffer, unlike Shattered Lands'), the far block is in
; the HMA. The build fails if the helper outgrows the block without UMBPLUS.COM (D000h on, as
; DSCLOG's UMB_ROOM): loaded (its PSP, the image with the install and the stack) or kept (its PSP, the
; segment and the tail, then the see-through figures' block), each with its MCB. In 2026-11 the kept
; helper took 4,505 of the 9,718 paragraphs there are with UMBPLUS.COM.
UMB_ROOM equ 0xF000 - 0xD00A
UMB_NEED equ 1 + 0x10 + (image_len + STACK + 15) / 16
UMB_KEPT equ (1 + 0x10 + KEPT_PARAS) + (1 + GHOST_PARAS)
        times -(UMB_NEED > UMB_ROOM) db 0   ; (a negative count: the helper no longer loads into upper memory)
        times -(UMB_KEPT > UMB_ROOM) db 0   ; (a negative count: the helper and the see-through block don't fit)
file_len equ 32 + image_len
