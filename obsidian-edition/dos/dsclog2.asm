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
copied    dw 0                  ; +146 bits: 1 the Loader's RESOURCE.GFF copy opened, 2 its GPLDATA.GFF
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
        times 238 - ($ - hdr) db 0  ; (DSCLOG's fields +172 to +237: none of them here yet, zero)
dac_off  dw FAR_DAC             ; +238 offset of DAC in the far block: the palette as last read (DAC_TICK),
                                ;      768 values 0-63, for the colours of the Loader's labels and panel
dac_changes dw 0                ; +240 (DSCLOG2's own) counted up when DAC_TICK finds the palette changed:
                                ;      the Loader draws its panel again in it (DSCLOG's DARK count)
        times 268 - ($ - hdr) db 0  ; (DSCLOG's fields +242 to +267: none of them here yet, zero)
ring_seg dw 0                   ; +268 the ring's segment: the far block's (FAR_SEG), as DSCLOG's
rules_hi   dw 0                 ; +270 the rules' second word, as DSCLOG's (none ported yet)
        times 326 - ($ - hdr) db 0  ; (DSCLOG's fields +272 to +325: none of them here yet, zero)
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
        times 1834 - ($ - hdr) db 0 ; (DSCLOG's fields +350 to +1833: none of them here yet, zero)
tail_seg dw 0                   ; +1834 DSCLOG's tail's segment: here this helper's own (LBL_SLOTS is
tail_paras dw 0                 ; +1836   in its resident part), set as it loads
lbl_off  dw lbl_slots           ; +1838 offset of LBL_SLOTS there: the Loader's names over figures (labels.py)
big_off  dw 0                   ; +1840 (DSCLOG's BIG, the cahulaks' too-big list: none here, the Loader's LARGE_BITS serve)
large_off dw large_bits         ; +1842 offset of LARGE_BITS there: the Loader's, a bit per combatant large or bigger
                                ;      (sizes.Large, by name and race: the creature size rule, IS_LARGE)
        times HDR_SIZE - ($ - hdr) db 0  ; (the rest of DSCLOG's header, to its last field: zero, so
                                ;   whatever the Loader reads of it is a defined 0, never this helper's code)
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
; aren't ported yet), and left in AX as the game's code would.
probe_ac:
        sti
        push si
        mov si, sp
        sub si, 4               ; SS:SI+6 = our return address (as RECORD wants it)
        mov word [cs:extra], 0
        mov ax, [bp-4]
        add ax, [bp-6]
        mov word [cs:kind], 2
        call record
        pop si
        retf 2

; ---- MISSILE_REAR: DSCLOG's, at the sequel's attack set-up ----
; The routine setting up an attack makes it one from behind by the target's facing alone, at any distance:
; "from behind" (the byte [BP-19h]: +2 to hit, 2 off THAC0 [BP-1Eh], and the AC function leaves out the
; target's DEX and shield), so a missile from across a room counted so too. Only melee ([BP+0Eh] 1) is
; from behind: a missile's taken back. INT VEC_REAR replaces "mov al,[bp-19h]" (5C99Fh: "push ax"
; after it kept), so it ends with AL as the game's. (DSCLOG's hidden archer's shot, the stealth rule's,
; isn't ported.) All registers but AL kept.
missile_rear:
        cmp word [bp + 0x0E], 1
        je .out
        cmp byte [bp - 0x19], 0
        je .out
        mov byte [bp - 0x19], 0
        add word [bp - 0x1E], 2
        inc word [cs:rear_taken]
.out:   mov al, [bp - 0x19]
        iret
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
; ACID_ONCE has its damage put no effect on. (DSCLOG's, without Lower Resistance's level, Sunstroke's
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
; in seconds made rounds as charges (at least 1, at most 127); then the compare made, its flags returned.
acid_rounds:
        pushad
        push es
        cmp byte [bp + 0x0C], ACID_EFFECT
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
; (bit 1), GPLDATA.GFF D:\GPLDAT2.GFF (bit 2). With no copy there, the game's own. Everything else goes
; on to DOS.
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
        db 0
res_copy db 'D:\RESOURC2.GFF', 0
gpl_copy db 'D:\GPLDAT2.GFF', 0

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
; (the Loader's STATS, with equipment and effects, the age and a ranger's stealth aren't ported).
IV_DRAW     equ -0x99           ; (from the patch) "lcall SEG:OFF" operand: the text routine
IV_WHO      equ -0x8B           ; (from the patch) "mov ax,0370h" operand: the character number's selector
WHO_OFF     equ 0x0B44
SHEETS_PTR  equ 0x19C5
SHEET_SIZE  equ 0x42
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
.react: mov al, [cs:c_react]      ; right of SP in the saves: "REAC +4"
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
; The tangle (SL's CAH_HIT) isn't ported yet. A ranger keeps the game's no penalty (the routine's own
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
; acted). The bitmap is cleared at a fight's first round (ACID_ROUND).
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
        jg .out
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
KIND_TYPES    equ 102
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
.kind:  cmp bx, KIND_TYPES
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
kind_of_type:
        db 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 1   ; types 0-16
        db 0, 14, 0, 0, 0, 0, 0, 12, 13, 0, 0, 0, 2, 0, 0, 0, 0   ; types 17-33
        db 0, 1, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 6, 0, 0   ; types 34-50
        db 7, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5   ; types 51-67
        db 0, 1, 0, 0, 3, 1, 5, 0, 0, 0, 0, 8, 10, 0, 0, 0, 0   ; types 68-84
        db 9, 0, 0, 0, 2, 0, 0, 0, 15, 0, 0, 0, 1, 16, 3, 0, 0   ; types 85-101
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


resident_end:
align 16
RESIDENT_PARAS equ (resident_end - hdr + 15) / 16   ; (the image to here: what stays)

; ---- the far block (FAR_INIT): the ring ----
FAR_RING   equ 0x10
FAR_END    equ FAR_RING + NENT * ESIZE
FAR_DAC    equ FAR_END                         ; the palette (DAC_TICK), 768 bytes
FAR_PANEL  equ FAR_DAC + 768                   ; the combat log's panel's picture (PANEL_BLIT)
FAR_TOP    equ FAR_PANEL + PANEL_BYTES
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
VECTORS equ ($ - all_vectors) / 3

align 16
image_len equ $ - $$
LOAD_EXTRA equ (STACK + 15) / 16
file_len equ 32 + image_len
