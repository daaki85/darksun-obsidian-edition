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
TSIZE   equ 2048        ; (the text buffer: none yet, its size kept for the header's readers)
STACK   equ 256         ; bytes of stack while installing
HDR_SIZE equ 1872       ; DSCLOG's header to its last field (dicelog.py's TSR_ offsets end at +1867)

; ---- MZ header: no relocations, and only as much memory as the image needs (as DSCLOG's) ----
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
        dw install                              ; IP
        dw 0                                    ; CS (relative to the image)
        dw 0x1C                                 ; relocation table offset
        dw 0                                    ; overlay
        align 32, db 0

section image follows=mz vstart=0

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
glob     dw TARGET, 0, 0, 0     ; +24  DS offsets of 4 game words to capture (0 = none): the attack's
                                ;      target first, as the Loader's dice log has DSCLOG's (TARGET_GLOBAL)
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
tpos     dw 0                   ; +126 (no text buffer yet)
tbuf_off dw 0                   ; +128
tsize    dw TSIZE               ; +130
probe_text_off dw 0             ; +132
probe_msg_off dw 0              ; +134
probe_char_off dw 0             ; +136
tbuf_seg  dw 0                  ; +138
panel_off dw FAR_PANEL          ; +140 the panel's picture's offset in the far block (PANEL_BLIT)
far_seg   dw 0                  ; +142 the far block's segment (FAR_INIT): its buffers from FAR_RING on
vec_table dw all_vectors        ; +144 where ALL_VECTORS is in the image
copied    dw 0                  ; +146 bits: 1 the Loader's RESOURCE.GFF copy opened, 2 its GPLDATA.GFF, 4 its OBJEX.GFF
slots_off dw slots_text         ; +148 offset of SLOTS_TEXT: 4 x SLOTS_SIZE bytes, one a party member,
                                ;      written by the Loader (DSCLOG's: dicelog.DiceLog._write_slots)
look_seq   dw 0                 ; +150 monsters looked at in a fight (PROBE_LOOK counts them)
look_reply dw 0                 ; +152 the Loader sets this to LOOK_SEQ once LOOK_TEXT is ready
look_who   dw 0                 ; +154 the combatant looked at
look_off   dw look_text         ; +156 offset of LOOK_TEXT: up to 3 short lines for the Look box, "|"
                                ;      between them (a first byte 1: beside LEVEL), written by the Loader
look_full_off dw 0              ; +158 (DSCLOG's whole description for the dialogue window: none here yet)
look_on    dw 0                 ; +160 the Loader sets 1 to have monsters described
        times 164 - ($ - hdr) db 0  ; (DSCLOG's fields +162 to +163: none of them here yet, zero)
stats_stamp dw 0                ; +164 the BIOS timer when the Loader last passed (RavDiceLog): older
                                ;      than STATS_FRESH, the panel is taken off
        times 170 - ($ - hdr) db 0  ; (DSCLOG's fields +166 to +169: none of them here yet, zero)
rules      dw 0                 ; +170 the rule changes the Loader turns on, as DSCLOG's (RULE_HP_BEST, ...;
                                ;      the Loader writes only the ported ones: ravager.RULES_PORTED)
        times 196 - ($ - hdr) db 0  ; (DSCLOG's fields +172 to +195: none of them here yet, zero)
names_off  dw item_names        ; +196 offset of ITEM_NAMES in this segment: the item names past the
names_count dw NAMES_ROOM       ; +198   game's 256 (as DSCLOG's EXTRA_NAMES), NAME_KEPT bytes each,
                                ;        written by the Loader (dsloader/ravager.item_names)
        times 204 - ($ - hdr) db 0  ; (DSCLOG's fields +200 to +203: none of them here yet, zero)
stealth    dw 0                 ; +204 the Loader sets bit N when party member N is hidden and unheard
                                ;      (RULE_STEALTH, stealth.py): their next attack is from behind
stealth_used dw 0               ; +206 counted up each time one is (the bit cleared: MISSILE_REAR)
        times 238 - ($ - hdr) db 0  ; (DSCLOG's fields +208 to +237: none of them here yet, zero)
dac_off  dw FAR_DAC             ; +238 offset of DAC in the far block: the palette as last read (DAC_TICK),
                                ;      768 values 0-63, for the colours of the Loader's labels and panel
dac_changes dw 0                ; +240 (DSCLOG2's own) counted up when DAC_TICK finds the palette changed:
                                ;      the Loader draws its panel again in it (DSCLOG's DARK count)
        times 268 - ($ - hdr) db 0  ; (DSCLOG's fields +242 to +267: none of them here yet, zero)
ring_seg dw 0                   ; +268 the ring's segment: the far block's (FAR_SEG), as DSCLOG's
rules_hi   dw 0                 ; +270 the rules' second word, as DSCLOG's
learn_seq  dw 0                 ; +272 a wizard's try at a scroll's spell (INT_LEARN), counted ...
learn_who  db 0                 ; +274 ... the party member ...
learn_spell db 0                ; +275 ... the spell ...
learn_int  db 0                 ; +276 ... its INT ...
learn_chance db 0               ; +277 ... the chance to learn (%) ...
learn_roll db 0                 ; +278 ... the d100 (LEARN_FULL: the spells of that level known) ...
learn_result db 0               ; +279 ... and LEARN_LEARNT, LEARN_FAILED or LEARN_FULL (DSCLOG's)
        times 326 - ($ - hdr) db 0  ; (DSCLOG's fields +280 to +325: none of them here yet, zero)
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
        times 1834 - ($ - hdr) db 0 ; (DSCLOG's fields +356 to +1833: none of them here yet, zero)
tail_seg dw 0                   ; +1834 DSCLOG's tail's segment: here this helper's own (LBL_SLOTS is
tail_paras dw 0                 ; +1836   in its resident part), set as it loads
lbl_off  dw lbl_slots           ; +1838 offset of LBL_SLOTS there: the Loader's names over figures (labels.py)
big_off  dw 0                   ; +1840 (DSCLOG's BIG, the cahulaks' too-big list: none here, the Loader's LARGE_BITS serve)
large_off dw large_bits         ; +1842 offset of LARGE_BITS there: the Loader's, a bit per combatant large or bigger
                                ;      (sizes.Large, by name and race: the creature size rule, IS_LARGE)
        times 1862 - ($ - hdr) db 0 ; (DSCLOG's fields +1844 to +1861: none of them here yet, zero)
bad_luck db 0                   ; +1862 a Swashbuckler's bad luck as KIT_SKILL last rolled it (0-25) ...
bad_luck_who dw 0               ; +1863 ... and whose (the creature), for the dice log (kits.TSR_BAD_LUCK)
        times HDR_SIZE - ($ - hdr) db 0  ; (the rest of DSCLOG's header, to its last field: zero, so
                                ;   whatever the Loader reads of it is a defined 0, never this helper's code)
wall_shadows dw 1               ; +1872 (DSCLOG2's own, past DSCLOG's header) 1: the walls cast shadows on
                                ;      the floor (WALL SHADOWS)
wall_passes  dw 0               ; +1874 floor passes shadowed (counted)
dark_builds  dw 0               ; +1876 times DARK was made
align 16
kind     dw 0                   ; the entry kind RECORD writes (0: a rand() call)
extra    dw 0                   ; RECORD's +186 (none yet)
old21    dd 0                   ; DOS, as it was

; ---- rand(): DSCLOG's INT_RAND and STUB, but its seed's address and the psionic range filter ----
; The patched rand() starts with INT VEC_RAND. Drop the interrupt frame (restoring the caller's
; flags) and be rand(): the same numbers (seed = seed * 015A4E35h + 1, (seed >> 16) & 7FFFh),
; and each call whose calling code matches a filter recorded.
int_rand:
        add sp, 4
        popf
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
        mov bx, [cs:glob+bx]
        xor cx, cx
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
; before, the compare's flags into the INT's frame. (Reflected Image's 50 waits for the new spells.)
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
        mov dx, IMAGE_CHANCE
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
        cmp dx, IMAGE_CHANCE
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
pf_mark:                                ; BX a slot (any word): its bit in PF_USED
        cmp bx, CACHE_MOST
        jae .out
        bts word [cs:pf_used], bx
.out:   ret

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
; (bit 1), GPLDATA.GFF D:\GPLDAT2.GFF (bit 2), OBJEX.GFF D:\OBJEX2.GFF (bit 4: the mod's item types).
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
        db 0
res_copy db 'D:\RESOURC2.GFF', 0
gpl_copy db 'D:\GPLDAT2.GFF', 0
obj_copy db 'D:\OBJEX2.GFF', 0

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

use_draw:                       ; the selected character's slots in the USE screen's panel
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov bx, [es:USE_WHO_OFF] ; the character on show
        cmp bx, 3
        ja .done
        imul si, bx, SLOTS_SIZE
        add si, slots_text
        cmp byte [cs:si], 0
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
.find:  cmp [cs:si], bl         ; the line keyed BL from SI drawn at y DX, carry clear; carry set
        je .line                ; if none
.next:  mov al, [cs:si]
        inc si
        cmp al, '|'
        je .find
        or al, al
        jnz .next
        stc
        ret
.line:  inc si                  ; (past its key)
        mov di, u_line          ; copy the line (up to "|" or the end) and draw it
.copy:  mov al, [cs:si]
        cmp al, '|'
        je .cut
        cmp al, 0
        je .cut
        mov [cs:di], al
        inc si
        inc di
        cmp di, u_line + SLOTS_SIZE - 1
        jb .copy
.cut:   mov byte [cs:di], 0
        push bx
        push dx
        push dx                 ; y
        push word USE_X         ; x
        push cs
        push word u_line
        call c_draw_line
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
u_line   times SLOTS_SIZE db 0
slots_text times 4 * SLOTS_SIZE db 0


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
; effects).
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
.skill: movsx ax, byte [gs:bx]  ; base
        movzx cx, dl
        add ax, cx
        movsx cx, byte [gs:bx + di]  ; race
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
c_cells:
        push es
        push si
        push di
        xor si, si
.cell:  push cx
        push bx
        push word [cs:bx + 2]   ; y
        push word [cs:bx]       ; x
        push cs
        push word [cs:bx + 4]   ; the label
        call c_draw_line
        pop bx
        push bx
        mov al, [cs:c_vals + si]
        mov di, c_num
        or si, si
        jnz .unsigned
        cmp byte [cs:c_signed], 0
        je .unsigned
        call c_itoa_s           ; the first cell of THAC0 and the saves
        jmp .number
.unsigned:
        call c_itoa
.number:
        push word [cs:bx + 2]
        push word [cs:bx + 6]   ; the value's x
        push cs
        push word c_num
        call c_draw_line
        pop bx
        pop cx
        add bx, 8
        inc si
        loop .cell
        pop di
        pop si
        pop es
        ret

c_itoa:                         ; AL (unsigned) -> decimal at CS:DI, NUL-terminated; keeps BX, CX
        push bx
        push cx
        xor ah, ah
        mov bl, 10
        xor cx, cx
.div:   div bl
        push ax                 ; AH = a digit
        inc cx
        xor ah, ah
        or al, al
        jnz .div
.put:   pop ax
        add ah, '0'
        mov [cs:di], ah
        inc di
        loop .put
        mov byte [cs:di], 0
        pop cx
        pop bx
        ret

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

c_itoa_s:                       ; AL (signed) -> decimal at CS:DI, with "-" below 0; keeps BX, CX
        test al, al
        jns c_itoa
        mov byte [cs:di], '-'
        inc di
        neg al
        jmp c_itoa

; cells: x, y, label, value's x (window coordinates, as DSCLOG's: the stats' labels at x 0ECh)
c_cells_top:
        dw 0xEC, 0x0D, l_thac0, 0x111
        dw 0xEC, 0x14, l_ppd, 0x103,  0x113, 0x14, l_rsw, 0x12A
        dw 0xEC, 0x1B, l_pp, 0x103,   0x113, 0x1B, l_bw, 0x12A
        dw 0xEC, 0x22, l_sp, 0x103
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
; patch (SL's -22h), the box's colours F3h, AFh (SL's 1Fh, 11h). DSCLOG's whole description in the
; dialogue window as the box closes (PROBE_UNLOOK) isn't ported.
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
.ready: mov es, [ss:si + 36]
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

; ---- ITEM NAMES: the mod's items' names, past the game's 256 ----
; The game's item names are RESOURCE.GFF's TEXT 1000, a name a line, read into a table of 256 far
; pointers at DS:56F3h (line k is name k + 1, name 0 the first line too): more lines run past the
; table and break the game (playtest/logs/2026-11-22-ravager-item-types.md). An item names its entry by
; a word (+14h), and the game's 7 reads of the table, "push dword [bx+56F3h]" with BX the number x4
; (59296h, 716A3h, 75E36h, 75E81h, 93AAAh, 95027h, 95052h: the inventory, the item box, the shops...),
; are SITE_NAME: name 256 on is ITEM_NAMES' (the Loader's, from the party transfer), an empty name past them.
NAMES_TABLE equ 0x56F3
NAMES_GAME  equ 256
NAMES_ROOM  equ 160
NAME_KEPT   equ 16                  ; (each: 15 letters at most and a NUL, as DSCLOG's EXTRA_NAMES)
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
item_names times NAMES_ROOM * NAME_KEPT db 0

; RTC_BEGIN, RTC_WAITED: DSCLOG's: a wait for the Loader ends after its BIOS ticks, or, as the BIOS
; clock can stand still in fights, once the real-time clock's second has changed twice (1 to 2 s)
rtc_begin:
        push ax
        call rtc_second
        mov [cs:w_sec], al
        mov byte [cs:w_flips], 0
        pop ax
        ret
rtc_waited:                             ; CF set: the wait is over
        push ax
        call rtc_second
        cmp al, [cs:w_sec]
        je .no
        mov [cs:w_sec], al
        inc byte [cs:w_flips]
        cmp byte [cs:w_flips], 2
        jb .no
        pop ax
        stc
        ret
.no:    pop ax
        clc
        ret
rtc_second:                             ; AL = the real-time clock's seconds (CMOS register 0)
        pushf
        cli
        mov al, 0
        out 0x70, al
        in al, 0x71
        popf
        ret
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

; ---- THE CREATION SCREEN'S THAC0: DSCLOG's CR_HP and CR_THAC0_DRAW, no kits ----
; INT VEC_CR_HP replaces "add sp,10h" (3 bytes: INT + NOP) after the creation screen draws its hit
; points again (6B84Ch, a click on them; 6BC62h; SL's 63AC3h, 63EDAh) and after it draws PSP, which
; follows the hit points (6D6AEh at the die, a choice and the screen opening; 6B79Ch at a click on
; CON; SL's 65A89h, 63A13h, its CR_AGE's sites). "THAC0: M18 R19" right of the hit points, on their
; line: the creature's THAC0 (it follows the classes chosen as they change) less STR's to-hit
; adjustment (M, melee) and less DEX's missile adjustment (R, ranged), none below 0, as the
; inventory's THAC0 with no weapon. The hit points' box (the 7th, DS:1224h) widened to x 243 (DONE's
; left 244: ravager.py's "cr_thac0_box"), so its saved background clears it. What differs from
; DSCLOG's: the sequel's records (the creature being made at DS:142Dh, 31h bytes: THAC0 +16h, STR
; +19h, DEX +1Ah; the STR to-hit table at DS:0832h, SL's 7C2h) and no kits (the THAC0 is the game's).
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
        les bx, [CR_CREATURE]
        mov cl, [es:bx + CREATURE_THAC0]
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
        pop es
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
held_hit:
        push ax
        push bx
        mov bx, sp                  ; ([BX+8] the INT's flags)
        and word [ss:bx + 8], ~0x40
        cmp word [bp - 6], 20
        je .hit
        call held_now
        jnc .out
.hit:   or word [ss:bx + 8], 0x40   ; (ZF: the game's JE to the hit)
.out:   pop bx
        pop ax
        iret
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
        ja .out                 ; (not a ranger)
        call ranger_drop
        sub al, cl
        jnc .out
        xor al, al
.out:   pop cx
        iret
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
        pop bx
        iret
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
;   once; else the game's. (No backstab dice in the sequel: SL's STAB_TIMES isn't ported.)
RULE_HI_ENLARGE equ 512
enl_dice  dw 0
enl_known db 0
enl_roll:
        push bx
        push ax
        sub ax, [bp - 0x14]
        mov [cs:enl_dice], ax
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
lm_ip dw 0
lm_cs dw 0
lm_fl dw 0
learn_said:
        pop word [cs:lm_ip]
        pop word [cs:lm_cs]
        pop word [cs:lm_fl]
        cmp byte [cs:learn_msg], LEARN_FAILED
        jne .game
        push es
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
        push learn_failed_text
        jmp learn_back
.game:  push ds
        push 0x2E97
learn_back:
        push word [cs:lm_fl]
        push word [cs:lm_cs]
        push word [cs:lm_ip]
        iret
learn_refused:
        pop word [cs:lm_ip]
        pop word [cs:lm_cs]
        pop word [cs:lm_fl]
        cmp byte [cs:learn_msg], LEARN_FULL
        jne .game
        mov byte [cs:learn_msg], 0
        push cs
        push learn_full_text
        jmp learn_back
.game:  push ds
        push 0x2EAB
        jmp learn_back
; PICK_ANY: INT VEC_PICK_ANY replaces "mov [bp-2],ax / or ax,ax" (9317Fh; 5 bytes: INT + 3 NOPs) in the
; routine a preserver's level up calls (688h:66h, 93160h; SI the member, AX its preserver level), which
; goes on (the JG after) to ask the game's list (94C7Ch) for a spell to learn at each spell level from
; [BP-2] down, and opens CHOOSE A SPELL (93378h) if one is found. With the rule: [BP-2] and AX the
; highest spell level it casts (as 698h:39h works it out: (level + 1) / 2 below 10th, level / 2 from it,
; WIZ_LEVELS the most; the game's own counted from the class level, past the wizard spells' rows), or 0
; (the window not opened) when no level up to it has a spell it doesn't know and room for one more
; (PICK_ROOM). Flags as "or ax,ax".
pick_any:
        mov [bp - 2], ax
        test word [cs:rules_hi], RULE_HI_INT
        jz .flags
        cmp ax, 0
        jle .flags
        cmp si, 3
        ja .flags
        push cx
        cmp ax, 10
        jae .half
        inc ax
.half:  shr ax, 1
        cmp ax, WIZ_LEVELS
        jbe .top
        mov ax, WIZ_LEVELS
.top:   mov cl, al
.level: call pick_room
        jc .found
        dec cl
        jnz .level
.found: movzx ax, cl                        ; (0: none)
        mov [bp - 2], ax
        pop cx
        inc word [cs:pick_asks]
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
        test word [cs:rules_hi], RULE_HI_INT
        jz .ret
        push ax
        push cx
        push si
        push es
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov si, [es:USE_WHO_OFF]
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
        test word [cs:rules_hi], RULE_HI_INT
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
        jae .none
        call bit_known
        jz .yes
        inc al
        jmp .each
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
.done:  cmp ch, dh                          ; (CF while fewer)
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
        mov bx, [cs:site_table + bx]
        mov [cs:site_jump], bx
        pop bx
        pop bp
        jmp [cs:site_jump]
site_jump dw 0
site_none:
        iret
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
        times 60 - ($ - site_table) / 2 dw site_none ; (52-59: none yet, another port's to take)
        dw kit_init                         ; 60 SITE_KIT_INIT (a combatant's initiative: the kits')
        dw kit_ranger_cast                  ; 61 SITE_KIT_RANGER_CAST (a ranger's caster level: a Seeker's, a Justifier's)
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
; The dice pushed under the INT's frame (its IP, CS and flags moved down 4 bytes). The sequel's classes
; SL's 1-17, then 18 (a wizard's) and 19 (a priest's); the sheet's classes at +1Bh.
STRENGTH_SPELL equ 23
STR_SIDES:              ; classes 1-19: Strength's sides
        db 6, 6, 6, 6, 6, 6, 6, 6       ; (clerics, druids)
        db 8, 8, 4, 6, 8, 8, 8, 8       ; (fighter, gladiator, preserver, psionicist, rangers)
        db 6, 4, 6                      ; (thief; the sequel's 18, a wizard's, and 19, a priest's)
strength_dice:
        sub sp, 4                       ; (room for the dice)
        push bp
        mov bp, sp                      ; ([BP+2] the room, [BP+6] the INT's IP, CS and flags)
        pusha
        push es
        mov cx, 6
        mov si, [bp]                    ; (the game's BP)
        cmp word [ss:si + 0x0E], STRENGTH_SPELL
        jne .put
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
        mov al, [cs:STR_SIDES + di]
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
.put:   mov ax, [bp + 6]
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
; Poison's and the rest's) and the healing after it; its record's cure of disease is the game's own.
; Recorded (MN_CELL: the target, the user, the healing; no kit's more, the sequel has no kits).
MN_CELL   equ 3
CELL_BACK equ 0x66545 - (0x664C5 + 3)
cell_heal:
        push bp
        mov bp, sp
        add word [bp + 2], CELL_BACK
        mov ax, 4
        call game_die
        pusha
        mov [cs:mn_frame], di
        mov bx, [ss:bp]                 ; (the game's BP)
        mov bx, [ss:bx + 8]
        mov [cs:mn_frame + 2], bx
        mov [cs:mn_frame + 4], ax
        mov word [cs:mn_frame + 6], 0
        mov ax, MN_CELL
        call mn_rec
        popa
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
        test [cs:tu_failed + si], al
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
        or [cs:tu_failed + si], al
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
        push cs
        pop es
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
tu_cell:
        mov ah, 4
        cmp al, 1
        jbe .row
        mov ah, 2
        cmp al, 2
        je .row
        dec ah
        cmp al, 4
        jbe .row
        dec ah
        cmp al, 5
        je .row
        cmp al, 11
        jb .many
        mov al, 11
.many:  mov ah, 4
        sub ah, al                      ; (6 to 11 hit dice: -2 to -7)
.row:   mov al, cl
        cmp al, 10
        jb .col
        sub al, 10
        shr al, 1
        cmp al, 2
        jbe .high
        mov al, 2
.high:  add al, 10
.col:   add al, ah                      ; (the run's place, from 1)
        jle .none
        cmp al, 12
        jb .run
        mov ax, TU_DSTAR
        ret
.run:   movzx bx, al
        mov al, [cs:bx + tu_cells - 1]
        mov ah, 0
        ret
.none:  xor ax, ax
        ret
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
tu_failed times TU_MOST db 0 ; (a byte a target: the priests, 0-7, who failed against it this fight)
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
        add di, GAME_SHEET_SIZE
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
rp_choose:
        mov [cs:rp_wound], ax
        mov bx, RP_CURES_END - 4
.down:  mov ax, [cs:bx + 2]
        cmp ax, [cs:rp_wound]
        jg .lower
        mov ax, [cs:bx]
        mov [cs:rp_spell], ax
        call rp_find
        jnc .ok
.lower: sub bx, 4
        cmp bx, rp_cures
        jae .down
        mov bx, rp_cures
.up:    mov ax, [cs:bx]
        mov [cs:rp_spell], ax
        call rp_find
        jnc .ok
        add bx, 4
        cmp bx, RP_CURES_END
        jb .up
        stc
.ok:    ret
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
; classes +1Bh, levels +1Eh. The mod's bracers, robes and Cloak of Protection (its types 102-134 in
; OBJEX2.GFF, with the party transfer) aren't armour (ARMOUR_TYPE). Not in the sequel, so not here:
; the mod's kits, weapon specs, the Spellarcher's arrows.
; - CU_SITE (site 19) replaces "mov [bp-1],al" (775FDh) at the end of the sequel's "may this character
;   equip this item" (77525h on; SL's 6EE5xh, the same tests but its answer a byte): AL 1 if the item
;   type's classes include one of the character's, DX the type, [BP+0Ah] the sheet (far). An item the
;   game allows that the classes' limits forbid (CLASS_FORBIDS) is refused, the game then saying it can't
;   use it, as SL's.
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
;   or ranger (CLASS_AND_WARRIOR): SL's PROBE_NO_CAST.
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
PSI_KINDS   equ 0x701E          ; bits by kind: club, dagger, short sword, mace, chatkcha, bow, sling
SPHERE_EARTH equ 0x1D           ; bits by material: wood, stone, obsidian, metal
SPHERE_FIRE equ 0x08            ; obsidian
SPHERE_WATER equ 0x03           ; wood, bone
CU_BOW_KIND equ 14              ; (KIND_OF_TYPE's bow)
CU_FIGHTER  equ 9
CU_GLADIATOR equ 10
KIND_TYPES  equ 135             ; (KIND_OF_TYPE's types: the sequel's 102 and the mod's 33)
ARM_SLOT    equ 0               ; (an item's +13h while worn: arms, legs, head, chest)
LEG_SLOT    equ 6
HEAD_SLOT   equ 7
CHEST_SLOT  equ 9
cu_site:
        test word [cs:rules], RULE_RESTRICT
        jz .out
        or al, al
        jz .out
        push bx
        push es
        les bx, [bp + 0x0A]
        call class_forbids
        pop es
        pop bx
        jnc .out
        xor al, al
        inc word [cs:restrict_count]
.out:   mov [bp - 1], al
        iret
belt_site:
        sti
        mov ax, si
        call kit_skill                  ; (the kits': KITS)
        test word [cs:rules], RULE_RESTRICT
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
        call armour_worn
        jnc .done
        xor ax, ax
        inc word [cs:restrict_count]
.done:  pop es
        pop dx
        pop bx
.out:   iret
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
        mov cl, dl
        mov dx, 1
        shl dx, cl
        pop cx
        test dx, PSI_KINDS
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
        pop si
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
; shield (+0 4), nor of these the mod's types bring (OBJEX2.GFF's 102-134): bracers of defense (worn on
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
shield_not_leather:
        test byte [cs:cu_flags], 4
        jz .ok
        cmp byte [cs:cu_mat], LEATHER
        je .ok
        stc
        ret
.ok:    clc
        ret
; SPHERE_ALLOWS: carry clear if sphere AL (0 air, 1 earth, 2 fire, 3 water) allows the weapon:
; air, missile and thrown weapons, daggers and the cahulaks; the others by material (SL's).
sphere_allows:
        push cx
        or al, al
        jnz .mat
        test byte [cs:cu_flags], 0x12
        jnz .yes
        cmp byte [cs:cu_kind], 2        ; (a dagger)
        je .yes
        cmp byte [cs:cu_kind], 11       ; (the cahulaks)
        je .yes
        jmp .no
.mat:   mov ah, SPHERE_EARTH
        cmp al, 1
        je .test
        mov ah, SPHERE_FIRE
        cmp al, 2
        je .test
        mov ah, SPHERE_WATER
.test:  mov cl, [cs:cu_mat]
        cmp cl, 8
        jae .no
        mov ch, 1
        shl ch, cl
        test ah, ch
        jnz .yes
.no:    pop cx
        stc
        ret
.yes:   pop cx
        clc
        ret
cu_flags   db 0
cu_mat     db 0
cu_armour  db 0
cu_kind    db 0
cu_dual    db 0
cu_others  dw 0
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
;
; PRIEST_THAC0 (site 33, "priest_thac0"): "mov [bp-2],ax" (95391h; 3 bytes, SL's 876ABh) in the THAC0
; routine (9534Ch), AX what a class group takes off 20 at its level ((level - 1) x the group's
; factor / 12; CX the group 0-3: priest, warrior, wizard, rogue; the levels the bytes at [BP-0Ah] +
; CX x 2). With the rule a priest's AD&D's, 2 for every 3 levels.
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
.done:  mov [bp - 2], ax
        iret
;
; ADND_SLOTS (site 34, "adnd_slots"): "nop / push cs / call 2A10h" (62893h; 5 bytes, SL's 5E240h),
; where the slot routine (62A10h) is asked one class's slots at a spell level: the arguments pushed
; (the class in the low byte, a near pointer in SS to its level and WIS, the spell level), AX the
; count from both (the level's rule and WIS's). With the rule, a cleric's, druid's or preserver's:
; AD&D's for the level (RAV_SLOTS) and the game's for its WIS alone (the routine called with level
; 0); the others', and all without the rule, the game's.
SLOT_CALL   equ 0x62A10 - 0x62896       ; (the routine, from the INT's way back)
SLOT_LEVELS equ 20                      ; (class levels in RAV_SLOTS; more are the 20th's)
SLOT_SPELLS equ 9                       ; (spell levels in a row)
adnd_slots:
        push bp
        mov bp, sp                      ; +2 the way back, +4 CS, +6 flags; +8 the class, +0Ah the
        push bx                         ;   pointer, +0Ch the spell level
        push cx
        push si
        mov si, [bp + 0x0A]
        mov cx, [ss:si]                 ; (CL the level, CH WIS)
        test word [cs:rules_hi], RULE_HI_TABLES
        jz .game
        movzx bx, byte [bp + 8]
        cmp bx, 11
        je .wizard
        cmp bx, 8
        ja .game
        or bx, bx
        jz .game
        xor bx, bx                      ; (a priest: the first table)
        jmp .ours
.wizard:
        mov bx, SLOT_LEVELS * SLOT_SPELLS
.ours:  mov byte [ss:si], 0             ; the game's for WIS alone
        call .call
        mov [ss:si], cl
        push ax
        movzx ax, cl                    ; and AD&D's for the level
        cmp al, SLOT_LEVELS
        jbe .lv
        mov al, SLOT_LEVELS
.lv:    dec ax
        js .none
        imul ax, ax, SLOT_SPELLS
        add bx, ax
        mov ax, [bp + 0x0C]
        dec ax
        cmp ax, SLOT_SPELLS
        jae .none
        add bx, ax
        mov al, [cs:bx + rav_slots]
        mov ah, 0
        inc word [cs:slot_count]
        jmp .sum
.none:  xor ax, ax
.sum:   pop bx
        add ax, bx
        jmp .out
.game:  call .call
.out:   call veiled_slot
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
; VEILED_SLOT: (ADND_SLOTS's, its frame) AX the slots of class [BP+8] at spell level [BP+0Ch], the
; combatant at [BP-6] (the SI it pushed): the Veiled Robe (a robe of plus 2 on the chest, PROT_SCAN; SL's
; robes.slots) a preserver's slot more at spell levels 1 to 3 where it has any. Others kept.
WIZARD_CLASS equ 11
veiled_slot:
        or ax, ax
        jz .ret
        cmp byte [bp + 8], WIZARD_CLASS
        jne .ret
        cmp word [bp + 0x0C], 1
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
; by class level 1-20, the slots at spell levels 1-9 (tables.RAV_PRIEST_SLOTS, RAV_WIZARD_SLOTS)
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
;   the sequel's; a ranger keeps the game's no penalty, in any armour.)
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
off_hand:
        mov ah, 0
        call kit_attacks                ; (the kits' to hit: KITS)
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
SPEC_SLOTS  equ 0x42            ; (the Loader's 48h sheet: SL's +14h..+16h there, +45h spare, 0)
SPEC_COUNT  equ 4
SPEC_PACKED equ 0x80
SPEC_V2     equ 0x40
SPEC_KINDS_MASK equ 0x1FFFF
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
        cmp si, SPEC_COUNT
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
        cmp si, 1               ; (a Myrmidon's second kind too)
        jne .ret
        call kit_is_b
        db KIT_MYRMIDON
        jne .ret
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
        xor cl, cl
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
; SPEC_KINDS_OWN: the sequel's weapons with no kind of SL's (KIND_OF_TYPE's 0), and the kind + 1 each
; counts as for specialization alone, as SL's spell-made weapons do (CONJURED_KINDS): its type, the kind
; (the reasoning: DEVELOPMENT-RULES.md, Weapon specialization in Wake of the Ravager). Ends with type 0.
spec_kinds_own:
        db 13, 1                ; Bloodletter (a 1d8 blade): long sword
        db 101, 1               ; Twohand Sword: long sword (SL's swords' one kind)
        db 61, 11               ; Lotulis (a blade at each end of a shaft): gythka
        db 39, 10               ; Double Spear: polearm
        db 100, 10              ; Trikal (a bladed polearm): polearm
        db 81, 5                ; Promere hammer: mace (a hammer, as Spiritual Hammer)
        db 68, 5                ; Jasmine (a mace's 1d6+1): mace
        db 38, 13               ; Darts: chatkcha (SL's thrown weapon)
        db 43, 13               ; Darts
        db 59, 13               ; Javelin
        db 90, 2                ; Shillelagh (the spell's): club
        db 95, 5                ; Spirit hammer (the spell's): mace
        db 87, 14               ; Rainbow (the spell's bow): bow
        db 0

; SPEC_GET: AX the spec in slot SI (kind + 1, 0 none) of sheet ES:BX, in any of its layouts (DSCLOG's:
; a byte each; packed 5 bits each; SPEC_V2, base 17). SPEC_ANY: ZF clear when a spec is chosen.
; Others kept.
spec_get:
        test byte [es:bx + SPEC_SLOTS + 2], SPEC_PACKED
        jnz .packed
        movzx ax, byte [es:bx + si + SPEC_SLOTS]
        ret
.packed:
        push ecx
        push edx
        push eax
        mov edx, [es:bx + SPEC_SLOTS]
        test edx, SPEC_V2 << 16
        jz .five
        mov eax, edx
        and eax, SPEC_KINDS_MASK
        mov ecx, 17
        push si
.digit: xor edx, edx            ; (digit SI: the remainder of the (SI + 1)th division)
        div ecx
        dec si
        jns .digit
        pop si
        jmp .got
.five:  imul cx, si, 5
        shr edx, cl
        and dl, 0x1F
.got:   pop eax
        movzx ax, dl
        pop edx
        pop ecx
        ret
spec_any:
        push eax
        mov eax, [es:bx + SPEC_SLOTS]
        test byte [es:bx + SPEC_SLOTS + 2], SPEC_PACKED
        jz .test                        ; (the old layout: any of the four bytes)
        test byte [es:bx + SPEC_SLOTS + 2], SPEC_V2
        jz .five
        and eax, SPEC_KINDS_MASK
        jmp .test
.five:  and eax, 0x000FFFFF
.test:  test eax, eax
        pop eax
        ret

; MISSILE_RATE: AX (the attacks a round in halves: the weapon type's, +7, as the game has a missile's)
; made a specialist's rate of fire when greater, for skill DL (SPEC_EXPERT or above) with item type SI
; (its kind SPEC_KIND's: the sequel's darts and javelins as the chatkcha), the sheet at ES:BX, by the
; warrior's level (the highest fighter, gladiator or ranger level of the classes it has now: 1-6, 7-12,
; 13 on): DSCLOG's, the bow 3, 4, 5 a round, the sling, staff sling and chatkcha 3/2, 2, 5/2; a grand
; master one more; a kind not chosen (SPEC_PLAIN), from 7th level, the specialist's a band lower.
; Others kept.
MISSILE_KIND equ 13             ; (the chatkcha's kind + 1; then the bow, the sling, the staff sling)
missile_halves db 3, 4, 5, 6, 8, 10, 3, 4, 5, 3, 4, 5
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
        ja .out
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
next_die:
        push si
        mov si, die_sizes
.next:  cmp ax, [cs:si]
        jb .got
        add si, 2
        cmp si, die_sizes_end
        jb .next
        pop si
        ret
.got:   mov ax, [cs:si]
        pop si
        ret
die_sizes dw 2, 3, 4, 6, 8, 10, 12, 20
die_sizes_end:

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
;   5B7E9h, SL's PROBE_INIT at 5750Eh).
; The Loader's header bytes for them are DSCLOG's: KIT_OUTDOORS (+350), KIT_DANCE (+351), KIT_WILD
; (+355), BAD_LUCK (+1862). Not here (yet): spell slots, casting levels, PSP costs, cures, a spell's
; damage, spells known, poison, arrows, gear (KIT_FORBIDS, KIT_ALLOWS), hit dice, the Effects lines.
RULE_HI_KITS equ 1
KIT_BYTE     equ 0x3D               ; (SL's +43h: ravager.sheet_field)
KIT_OPEN     equ 0xFF
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
kit_is:
        push si
        mov si, 1
        jmp kit_find
kit_has:
        push si
        xor si, si
kit_find:
        push di
        push cx
        mov ch, al
        call kit_place          ; (DI the oldest class's place)
        jc .no
.place: call kit_at
        cmp al, ch
        jne .next
        or si, si
        jz .yes
        call kit_awake
        jnc .yes
.next:  dec di
        jns .place
.no:    mov al, ch
        or ch, 1                ; (ZF clear)
        jmp .out
.yes:   mov [cs:kit_where], di
        cmp al, al              ; (ZF set)
.out:   pop cx
        pop di
        pop si
        ret
kit_where dw 0

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
        mov ch, [es:bx + KIT_BYTE]
        cmp ch, KIT_OPEN
        je .none
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
; once, not a human's, its race and classes one of MULTI_TABLE's; else 0. Others kept.
multi_group:
        push cx
        push dx
        push si
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
        mov si, cx
        mov cl, [cs:si + kit_class_of]
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
        pop si
        pop dx
        pop cx
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
cr_is_back:
        pop es
        pop bx
        ret
kit_is_b:
        push bp
        mov bp, sp
        push si
        push ax
        mov si, [bp + 2]
        cmp si, cr_is_back      ; (from CR_IS: the byte after the call to it)
        jne .byte
        mov si, [bp + 8]
        inc word [bp + 8]
        jmp .is
.byte:  inc word [bp + 2]
.is:    mov al, [cs:si]
        call kit_is
        pop ax
        pop si
        pop bp
        ret

; KIT_AC: AX (the AC the AC function has for combatant [BP+6]) with the creature's kits' (kits.ac): a
; Ravager's base AC by its level (RAVAGER_AC) where better than its sheet's; a Wanderer's 1 worse; a
; Sentinel's 2 better with a shield in a hand, an Arena Champion's 1; a Grove Warden's 1 better for every
; 3 druid levels; a Battle Dancer's dance (KIT_DANCE); a Wild Fury fighting wild (KIT_WILD's bit N) 3
; worse, no worse than 10. Others kept.
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
        jne .sentinel
        call kit_level
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
ravager_ac db 7, 7, 6, 6, 5, 5, 4, 4, 3, 3   ; (by level, 1-10)
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
        jb .missile             ; (the bow, sling and staff sling: kinds 13 to 15)
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
        cmp si, SPEC_COUNT
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
; chosen weapon spec) 3/2 a round, 2 from the kit's class's 7th level (specialize.expert_attacks).
; Others kept.
expert_halves:
        cmp dl, SPEC_EXPERT
        jne .ret
        cmp ax, 2
        ja .ret
        push ax
        call kit_level
        cmp al, 7
        pop ax
        mov ax, 3
        jb .more
        inc ax
.more:  inc word [cs:kit_rates]
.ret:   ret

; WAR_KIT_IS: ZF set if sheet ES:BX is a Crusader's or a Mind Warrior's (kit awake). All kept.
war_kit_is:
        call kit_is_b
        db KIT_CRUSADER
        je .ret
        call kit_is_b
        db KIT_MIND_WARRIOR
.ret:   ret

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
; item named Helm, HELM_NAME, counts). The sequel's other helm type (56, a Helm and the Helm of
; Domination) has AC 1 of its own already.
HELM_TYPE    equ 55
HELM_NAME    equ 0x24           ; (an item's name, +14h: TEXT 1000's "Helm"; a hat's 27h)
HELM_LIST    equ -0x324         ; (the AC function's worn list, from its BP)
probe_helm_ac:
        movsx ax, byte [es:bx + 0x0E]
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
        cmp si, HELM_TYPE
        jne .done
        push di
        mov di, [bp + 6]
        call helm_named
        pop di
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
probe_hp_best:
        test word [cs:rules], RULE_HP_BEST
        jz .game
        cmp byte [cs:hp_again], 0
        jne .second
        mov [cs:hp_first], ax
        mov byte [cs:hp_again], 1
        push bp
        mov bp, sp
        sub word [bp + 2], HP_BEST_BACK ; (the INT's return IP)
        pop bp
        iret
.second:
        mov byte [cs:hp_again], 0
        cmp ax, [cs:hp_first]
        jge .game
        mov ax, [cs:hp_first]
.game:  mov cx, ax
        iret

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
cah_adjust:                     ; DX the main head's adjustment (-2 + TWO_ADJUST, no better than 0);
        push ax                 ;   CAH_EXTRA how much worse the off head's is, for attacker CX
        mov dx, -2
        add dx, [cs:two_adjust]
        jle .main
        xor dx, dx
.main:  mov ax, -4
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
        push ax
        mov ax, [bp + 0x12]
        call item_is_cahulaks
        pop ax
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
        mov ax, bx
        call is_large
        jc .done                    ; (too big to tangle: a half-giant, or large by the Loader's table)
        mov si, [es:di + 4]         ; (its sheet)
        imul si, si, SHEET_SIZE
        les di, [SHEETS_PTR]
        add di, si
        movzx cx, byte [es:di + SHEET_PETRIFY]
        mov ax, 20
        call game_die
        mov [cs:mn_frame], bx
        mov dx, [bp + 0x18]
        mov [cs:mn_frame + 2], dx
        mov [cs:mn_frame + 4], ax
        mov [cs:mn_frame + 6], cx
        push ax
        push cx
        mov ax, MN_TANGLE
        call mn_rec
        pop cx
        pop ax
        cmp ax, 20
        je .done                    ; (a natural 20 saves)
        cmp ax, cx
        jge .done                   ; (saved)
        inc word [cs:tangles]
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
rec_frame:
        pop dx                          ; (the way back)
        mov di, sp
        add si, cx
        add si, cx
.push:  sub si, 2
        push word [cs:si]
        loop .push
        push dword 0
        push bp
        mov bp, sp
        mov si, bp
        sub si, 4                       ; (SS:SI+6: the frame's return address, none)
        call record
        pop bp
        mov sp, di
        jmp dx
mn_frame  dw 0, 0, 0, 0
tangled   times TANGLE_MOST / 8 db 0
tangles   dw 0                  ; (tangles made, for a look in play)
tangle_turns dw 0               ; (turns taken so)

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
        pop bx
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
        test [cs:large_bits + si], al
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
        movzx ax, byte [cs:si + large_dice]
        or ax, ax
        jz .done
        mov [bp - 0x10], ax
        movzx ax, byte [cs:si + large_dice + 1]
        mov [bp - 0x12], ax
        movsx ax, byte [cs:si + large_dice + 2]
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
; KIND_OF_TYPE: the sequel's item types' weapon kinds, as specialize.KINDS + 1 (0 none): long sword 1,
; club 2, dagger 3, short sword 4, mace 5, axe 6, great axe 7, pick 8, quarterstaff 9, polearm 10, gythka
; 11, cahulaks 12, chatkcha 13, bow 14, sling 15, staff sling 16 (from OBJEX.GFF's items' names: the
; Longswords 16, 73, 97, Crystal sword 35, Flameblade 47, Magma blade 69; Club 29, Toothed Club 89;
; Daggers 37, 72, 99; Maces 67, 74; Axes 8, 48; Great Axe 51; Pick 79; Quarterstaff 85; Polearm 80;
; Gythka 52; Cahulaks 24; Chatchka 25; Bow 18; Sling 93; Staff Sling 98. Shillelagh, 90, has none).
; RAV_LARGE: the sequel's weapons whose game dice aren't those of SL's kind (KIND_OF_TYPE), or that have
; none: type, then AD&D's dice against a large target (count, sides, the bonus's change; count 0: the
; same dice on any size). By the AD&D weapon whose small and man-sized dice are the game's (the
; reasoning: DEVELOPMENT-RULES.md, Creature size, Wake of the Ravager's weapons). Ends with type 0.
rav_large:
        db 35, 3, 6, 0          ; Crystal sword, two-handed 1d10: the two-handed sword's 3d6
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
        db 0, 1, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 6, 0, 0   ; types 34-50
        db 7, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5   ; types 51-67
        db 0, 1, 0, 0, 3, 1, 5, 0, 0, 0, 0, 8, 10, 0, 0, 0, 0   ; types 68-84
        db 9, 0, 0, 0, 2, 0, 0, 0, 15, 0, 0, 0, 1, 16, 3, 0, 0   ; types 85-101
        ; the mod's types (OBJEX2.GFF's 102-134, SL's 115-147: ravager.mod_type), SL's kinds
        ; (specialize.KIND_OF_TYPE): its short swords, axes, great axes, picks, polearms, cahulaks
        db 4, 0, 0, 4, 6, 4, 6, 4, 0, 3, 5, 7, 8, 10, 0, 0, 0   ; types 102-118
        db 0, 0, 0, 0, 3, 7, 7, 3, 0, 0, 0, 0, 0, 0, 12, 12      ; types 119-134
LARGE_MOST    equ 520
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
large_bits times LARGE_MOST / 8 + 1 db 0
large_hits   dw 0               ; (hits on large targets, for a look in play)
spared_count dw 0               ; (Hold or Charm Person spared so)

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
LBL_SLOTS  equ 4
LBL_ROW    equ 16
LBL_H_MOST equ 11
LBL_MASK   equ LBL_ROW * LBL_H_MOST
LBL_SIZE   equ 8 + 2 * LBL_MASK
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
        pushf
        cli                             ; (drawing)
        call panel_tick
        popf
        call label_tick
        pop es
        popa
        test byte [cs:s_fl + 1], 2      ; (the caller's flags' IF)
        jz .call
        sti
.call:  call far [cs:s_far]
        call panel_mouse                ; (AX the buttons: a press on the panel kept from the game)
        push word [cs:s_fl]
        push word [cs:s_cs]
        push word [cs:s_ip]
        iret

; PROBE_TICK: INT VEC_TICK replaces "inc word cs:[0004h]" (5 bytes: INT + 3 NOPs; 3DA2Ch, SL's
; 3925Ch), the first instruction of the game's timer handler. Does that, and every other strike puts
; the labels again. Interrupts stay off.
probe_tick:
        push bp
        mov bp, sp
        push ds
        mov ds, [bp + 4]                ; the handler's CS
        inc word [4]                    ; the replaced instruction
        pop ds
        pop bp
        inc word [cs:tick_count]
        test byte [cs:tick_count], 1
        jnz .out
        call label_stamp
.out:   iret

; ON_MAP: ZF set if the game is on the map (SCREEN_IS 1); registers kept
on_map:
        push es
        push ax
        mov ax, [cs:pointer_ds]
        cmp ax, 1                       ; (not known yet: ZF clear)
        jb .out
        mov es, ax
        cmp word [es:SCREEN_IS], 1
.out:   pop ax
        pop es
        ret

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
        push cs
        pop fs
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
label_adopt:
        mov [cs:si + LS_SEEN], dl
        mov [cs:si + LS_X], ax
        mov [cs:si + LS_Y], bx
        mov ax, [fs:di + 1]
        mov [cs:si + LS_W], ax          ; (and LS_H)
        mov byte [cs:si + LS_SHOWN], 1
        ret

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
%assign slot 0
%rep LBL_SLOTS
        cmp byte [cs:lbl_slots + slot * LBL_SIZE], 0
        jne .some
%assign slot slot + 1
%endrep
.ret:   ret                             ; (no label in any slot: nothing to put, nor to place)
.some:  cmp byte [cs:vga_busy], 0
        jne .ret
        mov byte [cs:lbl_busy], 1
        push fs
        pusha
        push ds
        push es
        push cs
        pop fs
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
vga_save:
        mov byte [cs:vga_busy], 1
        mov dx, 0x3C4
        in al, dx
        mov [cs:sc_index], al
        mov al, 2
        out dx, al
        inc dx
        in al, dx
        mov [cs:sc_mask], al
        mov dx, 0x3CE
        in al, dx
        mov [cs:gc_index], al
        xor bx, bx
.save:  mov al, [cs:gc_regs + bx]
        out dx, al
        inc dx
        in al, dx
        dec dx
        mov [cs:gc_saved + bx], al
        inc bx
        cmp bx, 5
        jb .save
        mov ax, 0x0001                  ; no set/reset, no rotation, all bits, write mode 0
        out dx, ax
        mov ax, 0x0003
        out dx, ax
        mov ah, [cs:gc_saved + 3]
        and ah, 0xF4
        mov al, 5
        out dx, ax
        mov ax, 0xFF08
        out dx, ax
        ret

vga_restore:
        mov dx, 0x3CE
        xor bx, bx
.put:   mov al, [cs:gc_regs + bx]
        mov ah, [cs:gc_saved + bx]
        out dx, ax
        inc bx
        cmp bx, 5
        jb .put
        mov al, [cs:gc_index]
        out dx, al
        mov dx, 0x3C4
        mov al, 2
        mov ah, [cs:sc_mask]
        out dx, ax
        mov al, [cs:sc_index]
        out dx, al
        mov byte [cs:vga_busy], 0
        ret

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
; into, and the game on the map
panel_live:
        cmp byte [cs:panel_shown], 0
        je .no
        push es
        push ax
        mov es, [cs:panel_pseg]
        mov ax, [es:SHOWN_PAGE]
        cmp ax, [cs:panel_page]
        pop ax
        pop es
        jne .ret
        call on_map
.ret:   ret
.no:    cmp sp, 0                       ; (ZF clear)
        ret

; PANEL_MOUSE: after the main loop's call for the pointer (AX the buttons; the far pointers to x and y
; at [SP+4], [SP+8] past this call's return): the pointer noted for the Loader; a left press on the
; panel, while it is shown, counted and kept from the game until released (the Loader scrolls the
; log: combatlog.py)
panel_mouse:
        push bp
        mov bp, sp
        push es
        push bx
        push cx
        push dx
        les bx, [bp + 4]
        mov cx, [es:bx]
        les bx, [bp + 8]
        mov dx, [es:bx]
        mov [cs:panel_mx], cx
        mov [cs:panel_my], dx
        test al, 1
        jz .up
        cmp word [cs:panel_held], 0
        jne .keep
        call panel_live
        jne .out
        push cx
        push dx
        sub cx, PANEL_X0
        cmp cx, PANEL_W
        jae .off
        sub dx, [cs:panel_top]
        cmp dx, [cs:panel_rows]
.off:   pop dx
        pop cx
        jae .out
        mov word [cs:panel_held], 1
        mov [cs:panel_hx], cx
        mov [cs:panel_hy], dx
        inc word [cs:panel_hits]
.keep:  and al, ~1
        jmp .out
.up:    mov word [cs:panel_held], 0
.out:   pop dx
        pop cx
        pop bx
        pop es
        pop bp
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
panel_draw_around:
        cmp word [POINTER_HIDE], 0
        jne .whole
        cmp word [POINTER_KIND], -1
        je .whole
        push ax
        mov ax, [POINTER_WAS]
        sar ax, 2
        mov [cs:pb_sx0], ax
        add ax, POINTER_MOST / 4 + 1
        mov [cs:pb_sx1], ax
        mov ax, [POINTER_WAS + 2]
        mov [cs:pb_sy0], ax
        add ax, POINTER_MOST
        mov [cs:pb_sy1], ax
        pop ax
        mov byte [cs:pb_skip], 1
        call panel_draw
        mov byte [cs:pb_skip], 0
        ret
.whole: jmp panel_draw

; PROBE_POINTER: INT VEC_POINTER replaces "cmp [9Ch],sp" (4 bytes: INT + 2 NOPs; the stack check) in
; the game's routine that draws its pointer (3326Ah, 2D72:0942). The panel is put first if the pointer
; is to go over it. The stack check, with the routine's SP; RETF 2 keeps its flags. DS the game's.
probe_pointer:
        sti
        mov [cs:pointer_ds], ds
        call pointer_panel
        push ax
        mov ax, sp
        add ax, 8               ; (the routine's SP: past this push and INT's IP, CS and flags)
        cmp [0x9C], ax
        pop ax
        retf 2

pointer_panel:
        cmp byte [cs:pointer_busy], 0
        jne .ret
        cmp word [POINTER_HIDE], 0
        jne .ret
        call panel_live
        jne .ret
        push si
        mov si, POINTER_XY
        call pointer_over
        je .draw
        mov si, POINTER_WAS
        call pointer_over
        jne .out
.draw:  call panel_draw
.out:   pop si
.ret:   ret

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
; it: L_ON_MAP), counted for the Loader (PANEL_KEYS) and taken out of what the game sees
KEY_L       equ 0x266C
KEY_SHIFT_L equ 0x264C
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
        call our_key
        jc .again
        add sp, 2
        iret

our_key:                                ; AX a key: CF set (and counted) if it is L for the panel
        cmp ax, KEY_L
        je .l
        cmp ax, KEY_SHIFT_L
        jne .no
.l:     call panel_live
        je .count
        call l_on_map
        jne .no
.count: inc word [cs:panel_keys]
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
lbl_slots times LBL_SLOTS * LBL_SIZE db 0 ; (the Loader's: LABELS, the header's +1834:+1838)



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

probe_floor_all:
        mov word [cs:floor_frame], 0x1C
        mov byte [cs:floor_kind], 0
        jmp floor_enter
probe_floor_rect:
        mov word [cs:floor_frame], 0x1E
        mov byte [cs:floor_kind], 1
floor_enter:
        pop word [cs:resume]
        pop word [cs:resume + 2]
        popf
        cmp word [cs:wall_shadows], 0
        je .plain
        cmp byte [cs:floor_busy], 0
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
        call dark_check
        cmp byte [cs:dark_ready], 0
        je .out
        mov ds, [cs:game_ds]
        cmp dword [GMAP_PTR], 0
        je .out
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
.out:   ret

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

resident_end:
align 16
RESIDENT_PARAS equ (resident_end - hdr + 15) / 16   ; (the image to here: what stays)

; ---- the far block (FAR_INIT): the ring ----
FAR_RING   equ 0x10
FAR_END    equ FAR_RING + NENT * ESIZE
FAR_DAC    equ FAR_END                         ; the palette (DAC_TICK), 768 bytes
FAR_PANEL  equ FAR_DAC + 768                   ; the combat log's panel's picture (PANEL_BLIT)
FAR_SPANS  equ FAR_PANEL + PANEL_BYTES         ; WALL SHADOWS' spans, 6 bytes each
FAR_WS_DAC equ FAR_SPANS + WS_SPANS_MOST * 6   ; ... the palette DARK was made from
FAR_DARK   equ FAR_WS_DAC + 768                ; ... DARK (XLAT)
FAR_TOP    equ FAR_DARK + 256
FAR_PARAS  equ (FAR_TOP - FAR_RING + 15) / 16 + 1

; ---- install (not kept) ----
install:                        ; DS = ES = PSP, CS = the image
        mov [cs:psp], es
        push cs
        pop ds
        mov si, all_vectors     ; the vectors must be free (DSCLOG's check)
        mov cx, VECTORS
.check:
        lodsb
        inc si
        inc si
        mov ah, 35h
        int 21h
        mov dx, es
        or dx, bx
        jz .free
        mov dx, busy
        mov ah, 9
        int 21h
        mov ax, 4C01h
        int 21h
.free:
        loop .check
        mov es, [cs:psp]
        mov es, [es:0x2C]       ; free our copy of the environment
        mov ah, 49h
        int 21h
        mov dx, msg
        mov ah, 9
        int 21h
        call far_init
        jnc .far
        mov dx, no_far
        mov ah, 9
        int 21h
        mov ax, 4C01h
        int 21h
.far:
        mov si, all_vectors
        mov cx, VECTORS
.vec:   lodsb
        mov ah, 25h
        mov dx, [si]
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
        mov byte [hooked], 1
        mov ax, [cs:far_seg]
        mov [cs:ring_seg], ax
        mov [cs:tail_seg], cs   ; (the labels' slots: in this segment)
        mov [cs:panel_seg], ax  ; (the panel's picture: in the far block)
        mov es, [cs:psp]        ; our block cut down to the PSP and what stays, then kept
        mov bx, 0x10 + RESIDENT_PARAS
        mov ah, 4Ah
        int 21h
        mov dx, bx
        mov ax, 3100h
        int 21h

; FAR_INIT: DSCLOG's: FAR_SEG set and its FAR_RING to FAR_END cleared; CF if there was no room.
; The HMA when it is ours (XMS's, or unused: all zero), else a block of upper memory, else of
; conventional memory (FAR_SEG a paragraph below it).
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
.a20:   mov ah, 3
        call far [cs:xms]
        or ax, ax
        jz .block
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
        jne .block
        cmp byte [cs:hma_given], 0
        jne .hma
        mov di, FAR_RING
        mov cx, (FAR_TOP - FAR_RING) / 2
        xor ax, ax
        cld
        repe scasw
        jne .block
.hma:   mov word [cs:far_seg], 0xFFFF
        jmp .clear
.block: mov bx, FAR_PARAS
        call umb_alloc
        jnc .got
        mov ah, 48h
        mov bx, FAR_PARAS
        int 21h
        jc .ret
.got:   dec ax
        mov [cs:far_seg], ax
.clear: mov es, [cs:far_seg]
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

align 16
image_len equ $ - $$
LOAD_EXTRA equ (STACK + 15) / 16
file_len equ 32 + image_len
