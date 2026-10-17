; DSCLOG.EXE - dice log helper for the Dark Sun companion.
;
; A tiny TSR that stays resident (load it high with LH) and holds a ring
; buffer plus a replacement for the game's Borland rand(). The Loader runs a
; patched copy of the game (DSUNLOG.EXE) whose rand() and a few "probe" places
; start with INT instructions; this TSR answers those interrupts
; (VEC_RAND, VEC_SAVE, VEC_AC, VEC_TEXT, VEC_MSG) and the Loader reads the ring buffer
; from DOSBox's memory. VEC_CHAR adds THAC0, the saving throws and thief skills to the
; game's inventory screen. VEC_RING_AC and VEC_RING_SAVE make a ring with a plus (the
; companion's Ring +1) better the AC and saving throws of whoever wears it.
;
; STUB produces exactly the numbers the original rand() would
; (seed = seed * 0x015A4E35 + 1, result = (seed >> 16) & 0x7FFF), so the game
; plays the same. For every call it also records who called and the caller's
; stack frame, which holds the dice size, THAC0, target AC and so on.
;
; It is a small .EXE rather than a .COM so that LH can load it into upper
; memory: a .COM asks DOS for a whole 64 KB block, more than DOSBox's UMB has.
;
; Build: nasm -f bin -o DSCLOG.EXE dsclog.asm

BITS 16
CPU 386

VEC_RAND equ 0x60     ; rand() (DSUNLOG.EXE: INT 60h at the start of rand())
VEC_SAVE equ 0x61     ; PROBE_SAVE
VEC_AC   equ 0x62     ; PROBE_AC
VEC_TEXT equ 0x63     ; PROBE_TEXT
VEC_MSG  equ 0x64     ; PROBE_MSG
VEC_CHAR equ 0x65     ; PROBE_CHAR
VEC_USE  equ 0xF2     ; PROBE_USE
VEC_VIEW equ 0xF3     ; PROBE_VIEW
VEC_WIN  equ 0xF4     ; PROBE_WIN
VEC_LOOK equ 0xF5     ; PROBE_LOOK
VEC_UNLOOK equ 0xF6   ; PROBE_UNLOOK
VEC_RING_AC equ 0xF8  ; PROBE_RING_AC
VEC_RING_SAVE equ 0xF9  ; PROBE_RING_SAVE
VEC_WEAPON equ 0xFA   ; PROBE_WEAPON
VEC_MOVE   equ 0xFB   ; PROBE_MOVE
VEC_MISSILE_LINE equ 0xFC ; PROBE_MISSILE_LINE
VEC_USE_ITEM equ 0xFD ; PROBE_USE_ITEM
VEC_TWO    equ 0xFE   ; PROBE_TWO
VEC_DOUBLE equ 0xF0   ; PROBE_DOUBLE
VEC_GRACE_CAST equ 0xED    ; PROBE_GRACE_CAST
VEC_GRACE_EFFECT equ 0xEE  ; PROBE_GRACE_EFFECT
VEC_GRACE_ABILITY equ 0xEF ; PROBE_GRACE_ABILITY
VEC_NAMES_SIZE equ 0xEC    ; PROBE_NAMES_SIZE
VEC_NAMES_FILL equ 0xEB    ; PROBE_NAMES_FILL
VEC_STEALTH equ 0xEA       ; PROBE_STEALTH
VEC_TYPES_SIZE equ 0xE9    ; PROBE_TYPES_SIZE
VEC_TYPES_FILL equ 0xE8    ; PROBE_TYPES_FILL
VEC_LEVEL equ 0xE7         ; PROBE_LEVEL
VEC_HD_ROLL equ 0xE6       ; PROBE_HD_ROLL
VEC_HD_CON equ 0xE5        ; PROBE_HD_CON
VEC_THIEF_SKILL equ 0xE4   ; PROBE_THIEF_SKILL
VEC_TWO_HANDED equ 0xE3    ; PROBE_TWO_HANDED
VEC_SPELL_TEXT equ 0xE2    ; PROBE_SPELL_TEXT
VEC_CHUNK_ID equ 0xE1      ; PROBE_CHUNK_ID
VEC_FLOOR_ALL equ 0xE0     ; PROBE_FLOOR (the whole view's floor)
VEC_FLOOR_RECT equ 0xDF    ; PROBE_FLOOR (a rectangle's floor)
VEC_REDRAW equ 0xDE        ; PROBE_REDRAW
VEC_REDRAW_ALL equ 0xDD    ; PROBE_REDRAW_ALL
VEC_SCROLL equ 0xDC        ; PROBE_SCROLL
VEC_HIT    equ 0xDB        ; PROBE_HIT
VEC_ITEM_BOX equ 0xDA      ; PROBE_ITEM_BOX
VEC_BELT equ 0xD9          ; PROBE_BELT
VEC_SAVE_PAGE equ 0xD8     ; PROBE_SAVE_PAGE
VEC_SAVE_CLICK equ 0xD7    ; PROBE_SAVE_CLICK
VEC_ITEM_WEAPON equ 0xD6   ; PROBE_ITEM_WEAPON
VEC_ITEM_SKIP equ 0xD5     ; PROBE_ITEM_SKIP
VEC_ITEM_ARMOUR equ 0xD4   ; PROBE_ITEM_ARMOUR
VEC_SCRIPT_RAND equ 0xD3   ; PROBE_SCRIPT_RAND
VEC_XP_NEXT equ 0xD2       ; PROBE_XP_NEXT
VEC_ATTACKS equ 0xD1       ; PROBE_ATTACKS
VEC_SPEC_DAMAGE equ 0xD0   ; PROBE_SPEC_DAMAGE
VEC_DAM_LINE equ 0xCF      ; PROBE_DAM_LINE
VEC_VIEW_DAM equ 0xCE      ; PROBE_VIEW_DAM
VEC_CAN_USE equ 0xCD       ; PROBE_CAN_USE
VEC_NO_CAST equ 0xCC       ; PROBE_NO_CAST
VEC_MC_CON equ 0xCA        ; PROBE_MC_CON
VEC_MC_UNCON equ 0xC9      ; PROBE_MC_UNCON
VEC_WP_DISC_WIN equ 0xC8   ; PROBE_WP_DISC_WIN
VEC_WP_SPHERE_WIN equ 0xC7 ; PROBE_WP_SPHERE_WIN
VEC_WP_DISC_CLICK equ 0xC6 ; PROBE_WP_DISC_CLICK
VEC_WP_SPHERE_CLICK equ 0xC5 ; PROBE_WP_SPHERE_CLICK
VEC_WP_SHOWN equ 0xC4      ; PROBE_WP_SHOWN
VEC_WP_CLASS equ 0xC3      ; PROBE_WP_CLASS
VEC_LV_PICK equ 0xC2       ; PROBE_LV_PICK
VEC_PK_COUNT equ 0xC1      ; PROBE_PK_COUNT
VEC_PK_WIN equ 0xC0        ; PROBE_PK_WIN
VEC_PK_LEFT equ 0xBF       ; PROBE_PK_LEFT
VEC_PK_TITLE equ 0xBE      ; PROBE_PK_TITLE
VEC_PK_FILL equ 0xBD       ; PROBE_PK_FILL
VEC_PK_CLICK equ 0xBC      ; PROBE_PK_CLICK
VEC_EF_ROWS equ 0xBB       ; PROBE_EF_ROWS
VEC_HP_BEST equ 0xBA       ; PROBE_HP_BEST
VEC_TOME equ 0xB9          ; PROBE_TOME
VEC_INIT equ 0xB8          ; PROBE_INIT
VEC_THAC0 equ 0xB7         ; PROBE_THAC0
VEC_SLOTS equ 0xB6         ; PROBE_SLOTS
VEC_SLOT_LEVEL equ 0xB5    ; PROBE_SLOT_LEVEL
VEC_PSP_USE equ 0xB4       ; PROBE_PSP_USE
VEC_PSP_TABLE equ 0xB3     ; PROBE_PSP_TABLE
VEC_PSP_DEFENCE equ 0xB2   ; PROBE_PSP_DEFENCE
VEC_CURE equ 0xB1          ; PROBE_CURE
VEC_PSP_KEEP equ 0xB0      ; PROBE_PSP_KEEP
VEC_RANGER_CAST equ 0xAF   ; PROBE_RANGER_CAST
VEC_PSP_KEEP_DX equ 0xAE   ; PROBE_PSP_KEEP_DX
VEC_HIT_ROUND equ 0xAD     ; PROBE_HIT_ROUND
VEC_CAST_LEVEL equ 0xAC    ; PROBE_CAST_LEVEL
VEC_PICK_LEVEL equ 0xAB    ; PROBE_PICK_LEVEL
VEC_PICK_LIST equ 0xAA     ; PROBE_PICK_LIST
VEC_SCROLL_LEARN equ 0xA9  ; PROBE_SCROLL_LEARN
VEC_SPELL_LEVEL equ 0xA8   ; PROBE_SPELL_LEVEL
VEC_PICK_ANY equ 0xA7      ; PROBE_PICK_ANY
VEC_RANGER_LEVEL equ 0xA6  ; PROBE_RANGER_LEVEL
VEC_HIT_DIE equ 0xA5       ; PROBE_HIT_DIE
VEC_MAX_PSP equ 0xA4       ; PROBE_MAX_PSP
VEC_CR_DIE equ 0xA3        ; PROBE_CR_DIE
VEC_CR_PSP equ 0xA2        ; PROBE_CR_PSP
VEC_EL_GRANT equ 0xA1      ; PROBE_EL_GRANT
VEC_EL_CAST equ 0xA0       ; PROBE_EL_CAST
VEC_EL_LEVEL equ 0x9F      ; PROBE_EL_LEVEL
VEC_EL_KNOW equ 0x9E       ; PROBE_EL_KNOW
VEC_DUAL_BAN equ 0x9D      ; PROBE_DUAL_BAN
VEC_DUAL_SPELLS equ 0x9C   ; PROBE_DUAL_SPELLS
VEC_SOUND_42 equ 0x9B      ; PROBE_SOUND_42
VEC_SOUND_44 equ 0x9A      ; PROBE_SOUND_44
VEC_DUAL_KIT equ 0x99      ; PROBE_DUAL_KIT
VEC_CR_SPELLS equ 0x98     ; PROBE_CR_SPELLS
VEC_EF_CLICK equ 0x97      ; PROBE_EF_CLICK
VEC_CAST_MARK equ 0x96     ; PROBE_CAST_MARK
VEC_ROUND_MARK equ 0x95    ; PROBE_ROUND_MARK
VEC_CAST_DONE equ 0x94     ; PROBE_CAST_DONE
VEC_END_TURN equ 0x93      ; PROBE_END_TURN
VEC_LEARN_SAID equ 0x92    ; PROBE_LEARN_SAID
VEC_LEARN_REFUSED equ 0x91 ; PROBE_LEARN_REFUSED
VEC_XP equ 0x90            ; PROBE_XP
VEC_PRIEST_THAC0 equ 0x8F  ; PROBE_PRIEST_THAC0
VEC_ADND_SLOTS equ 0x8E    ; PROBE_ADND_SLOTS
VEC_POINTER equ 0xF1       ; PROBE_POINTER
VEC_STRIP equ 0xF7         ; PROBE_STRIP
VEC_PALETTE equ 0x8B       ; PROBE_PALETTE
VEC_COLOURS equ 0xCB       ; PROBE_COLOURS
VEC_PRICE equ 0x8D         ; PROBE_PRICE
VEC_PRICE_EAX equ 0x8C     ; PROBE_PRICE_EAX
VEC_RS_CLICK equ 0x8A      ; PROBE_RS_CLICK
VEC_RACE_PANEL equ 0x89    ; PROBE_RACE_PANEL
VEC_BOX_AC equ 0x88        ; PROBE_BOX_AC
VEC_TICK equ 0x87          ; PROBE_TICK
VEC_POISON equ 0x86        ; PROBE_POISON
VEC_ARROW equ 0x85         ; PROBE_ARROW
TSIZE    equ 4096     ; bytes in the text buffer (a power of two)

NENT    equ 74          ; entries in the ring (74: the helper and it fit in upper memory)
ESIZE   equ 192         ; bytes per entry (see ENTRY LAYOUT)
STACK   equ 256         ; bytes of stack while installing

; ---- MZ header: no relocations, and only as much memory as the image needs ----
section mz start=0
        db 'MZ'
        dw file_len % 512                       ; bytes in the last page
        dw (file_len + 511) / 512               ; pages
        dw 0                                    ; relocations
        dw 2                                    ; header size in paragraphs
        dw LOAD_EXTRA                           ; min extra paragraphs: the ring's end past the image
        dw LOAD_EXTRA                           ; max extra paragraphs (so the whole fits in upper memory)
        dw 0                                    ; SS (relative to the image)
        dw image_len + STACK                    ; SP
        dw 0                                    ; checksum
        dw install                              ; IP
        dw 0                                    ; CS (relative to the image)
        dw 0x1C                                 ; relocation table offset
        dw 0                                    ; overlay
        align 32, db 0

section image follows=mz vstart=0

; ---- header, found by the Loader via SIG (16-byte aligned) ----
hdr:
sig      db 'DSCLOGvZ'          ; +0
seq      dw 0                   ; +8   entries written so far (wraps at 65536)
widx     dw 0                   ; +10  ring slot the next entry goes to
nent     dw NENT                ; +12
esize    dw ESIZE               ; +14
ring_off dw 0                   ; +16  offset of the ring in RING_SEG's segment
stub_off dw stub                ; +18  offset of STUB in this segment
hdr_off  dw hdr                 ; +20  offset of this header in this segment
seed_off dw 0x4122              ; +22  DS offset of the game's 32-bit rand seed
glob     dw 0, 0, 0, 0          ; +24  DS offsets of 4 game words to capture (0 = none)
nfilt    dw NFILT               ; +32  number of filters in use (0 = record every call)
filt:                           ; +34  up to 8 filters: a length (1-8), then that many bytes the
                                ;      calling code must start with to be recorded. By default,
                                ;      "rand()*N/32768" rolls (movsx eax,ax, then N) and the
                                ;      percentile check, so bursts of other randomness
                                ;      (animations) don't crowd out the rolls that matter
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
vectors  db VEC_RAND, VEC_SAVE, VEC_AC, VEC_TEXT, VEC_MSG  ; +112 the interrupts the patched game uses
hooked   db 0                   ; +117 1 once the vectors are ours
int_rand_off dw int_rand        ; +118 offset of INT_RAND (VEC_RAND's handler) in this segment
gpl_hook_off dw gpl_hook        ; +120 offset of GPL_HOOK in this segment
gpl_chain dd 0                  ; +122 the game's own hook, which GPL_HOOK passes on to
tpos     dw 0                   ; +126 bytes written to the text buffer so far (wraps at 65536)
tbuf_off dw tbuf                ; +128 offset of the text buffer in this segment
tsize    dw TSIZE               ; +130 its size (a power of two)
probe_text_off dw probe_text    ; +132 offset of PROBE_TEXT in this segment
probe_msg_off dw probe_msg      ; +134 offset of PROBE_MSG in this segment
probe_char_off dw probe_char    ; +136 offset of PROBE_CHAR in this segment
          times 4 dw 0          ; +138 (unused: the turn summaries' pop-up, gone for the combat log)
ended     dw 0                  ; +146 the combatant whose turn just ended
slots_off dw slots_text         ; +148 offset of SLOTS_TEXT: 4 x SLOTS_SIZE bytes, one per party
                                ;      member, lines separated by "|", NUL-terminated (the Loader
                                ;      keeps them up to date); PROBE_USE draws them
look_seq   dw 0                 ; +150 monsters looked at in a fight (PROBE_LOOK counts them)
look_reply dw 0                 ; +152 the Loader sets this to LOOK_SEQ once LOOK_TEXT is ready
look_who   dw 0                 ; +154 the combatant looked at
look_off   dw look_text         ; +156 offset of LOOK_TEXT: up to 3 short lines for the Look box,
                                ;      separated by "|", NUL-terminated
look_full_off dw look_full      ; +158 offset of LOOK_FULL: the whole description, shown in the
                                ;      dialogue window afterwards (empty: none)
look_on    dw 0                 ; +160 the Loader sets 1 to have monsters described
stats_off  dw stats             ; +162 offset of STATS: for each party member, the THAC0 and
                                ;      saves as they stand now (see STATS)
stats_stamp dw 0                ; +164 the BIOS timer when the Loader last wrote STATS: older
                                ;      than STATS_FRESH, the screens show the game's own numbers
stats_req  dw 0                 ; +166 counted up when a screen is about to show STATS ...
stats_reply dw 0                ; +168 ... and set to it by the Loader once STATS are up to date
rules      dw 0                 ; +170 rule changes the Loader turns on (RULE_HELMS, ...)
           dw 0, 0              ; +172 (unused: once P in a conversation)
pick_off   dw pick_text         ; +176 offset of PICK_TEXT: what came of it, NUL-terminated (empty:
                                ;      nothing to show)
pick_on    dw 0                 ; +178 the Loader sets bit 0 for the thieving tools on someone to pick
                                ;      their pocket
use_seq    dw 0                 ; +180 an item used on something on the map (PROBE_USE_ITEM counts) ...
use_reply  dw 0                 ; +182 ... and set to it by the Loader once it has had its say
use_who    dw 0                 ; +184 the object it was used on
use_taken  dw 0                 ; +186 the Loader sets 1 when it was one of its own (the thieving
                                ;      tools): the game then does nothing more, and PICK_TEXT is shown;
                                ;      2 when it is used up as well (the cooked vulture, eaten)
use_item   dw 0                 ; +188 the item used (FFFFh: none)
swap_on    dw 0                 ; +190 the Loader sets 1 to have the next dialogue text that
                                ;      starts with SWAP_MATCH shown as SWAP_TEXT instead (once)
swap_seq   dw 0                 ; +192 counted up when it has been
swap_off   dw swap_match        ; +194 offset of SWAP_MATCH (SWAP_SIZE bytes, NUL-terminated),
                                ;      then SWAP_TEXT (TSIZE_SWAP bytes)
names_off  dw extra_names       ; +196 offset of EXTRA_NAMES: the names past the game's own (NAMES_EXTRA
                                ;      of NAME_SIZE bytes), copied into the game's table each time it loads
names_count dw NAMES_EXTRA      ; +198 how many
names_ptr  dd 0                 ; +200 the game's name table, as last loaded with them (0: not yet)
stealth    dw 0                 ; +204 the Loader sets bit N when party member N is hidden and
                                ;      unheard (RULE_STEALTH): their next attack is from behind
stealth_used dw 0               ; +206 counted up each time one is (the bit cleared)
types_off  dw extra_types       ; +208 offset of EXTRA_TYPES: item types past the game's own
                                ;      (TYPES_EXTRA of TYPE_SIZE bytes), copied in as it loads them
types_count dw TYPES_EXTRA      ; +210 how many
types_first dw 0                ; +212 the number the first of them gets (the game's own count)
types_ptr  dd 0                 ; +214 the game's item type table, as last loaded with them
objects_on dw 0                 ; +218 1 once the game has opened the Loader's copy of
                                ;      SEGOBJEX.GFF (its icons: see PROBE_DOS_OPEN)
shadows_on dw 0                 ; +220 the Loader sets 1 to have figures cast shadows (SHADOWS)
shadow_tab_off dw shadow_tab    ; +222 offset of SHADOW_TAB: a byte for each of the game's 520 things,
                                ;      1 for those that cast a shadow (the Loader keeps it)
dark_build dw 0                 ; +224 the Loader sets 1 to have DARK made again from the palette
                                ;      (after the area, so the palette, changes); 0 once it is
shadow_passes dw 0              ; +226 shadow passes drawn (counted)
scroll_on  dw 0                 ; +228 the Loader sets SCROLL_MIDDLE and/or SCROLL_RIGHT to have
                                ;      a drag with that button scroll the map (SCROLLING)
pan_x      dw 0                 ; +230 the Loader adds to these (wrapping) to scroll the map by
pan_y      dw 0                 ; +232   as many pixels (to a chosen enemy: TARGETING)
dust_on    dw 0                 ; +234 the Loader sets 1 once LIGHT is made, to have walkers raise
                                ;      dust (DUST)
light_off  dw light             ; +236 offset of LIGHT: each colour's lighter one (0: none, not ground
                                ;      dust shows on), the Loader makes it from DAC
dac_off    dw dac               ; +238 offset of DAC: the palette as DARK was last made from it
dust_puffs dw 0                 ; +240 puffs of dust raised (counted)
view_redraw dw 0                ; +242 the Loader sets 1 to have the view drawn again (all of it, from
                                ;      the main loop: VIEW_AGAIN), as it is once it has been
rings_on   dw 0                 ; +244 the Loader sets 1 to have rings drawn under the things RING_TAB
                                ;      marks (RINGS), once RED is made
ring_tab_off dw ring_tab        ; +246 offset of RING_TAB: a byte for each of the game's 520 things: 1 a
                                ;      ring, 2 the chosen one's (brighter, thicker)
red_off    dw red               ; +248 offset of RED: each colour's reddened one (0: none), as LIGHT
target_on  dw 0                 ; +250 the Loader sets 1 while Tab chooses an enemy (TARGETING)
tab_seq    dw 0                 ; +252 Tab pressed (counted) ...
back_seq   dw 0                 ; +254 ... and Shift+Tab
hit_target dw 0xFFFF            ; +256 the enemy chosen (the Loader sets it; FFFFh: none)
attack_seq dw 0                 ; +258 Enter pressed on it (counted)
main_ticks dw 0                 ; +260 the map's main loop run (counted: not while a talk, menu or
                                ;      shop is open)
xp_who     dw 0xFFFF            ; +262 the Loader sets the party member to be given XP_AMOUNT
                                ;      with PICK_TEXT (GIVE_XP: the game's own routine, and the
                                ;      quest's sound; FFFFh: none), DSCLOG sets it back once given
xp_amount  dw 0                 ; +264
skills_on  dw 0                 ; +266 the Loader sets SKILLS_STEALTH to have an item's box name a
                                ;      cloak's and boots' bonus to hiding and moving silently
                                ;      (PROBE_ITEM_BOX), SKILLS_BELT for a worn belt's to picking
                                ;      pockets and opening locks (PROBE_BELT, and its box's line),
                                ;      SKILLS_ELVEN the Cloak and Boots of Elvenkind's chances
ring_seg   dw 0                 ; +268 the ring's segment: a memory block of its own (upper memory
                                ;      if any has room, else conventional), so the ring takes none
                                ;      of the helper's 64 KB (set when installed; RING_OFF its offset)
rules_hi   dw 0                 ; +270 more rule changes the Loader turns on (RULE_HI_KITS)
learn_seq  dw 0                 ; +272 a preserver's try at a scroll's spell (INT_LEARN), counted ...
learn_who  db 0                 ; +274 ... the party member ...
learn_spell db 0                ; +275 ... the spell ...
learn_int  db 0                 ; +276 ... its INT ...
learn_chance db 0               ; +277 ... the chance to learn (%) ...
learn_roll db 0                 ; +278 ... the d100 (LEARN_FULL: the spells of that level known) ...
learn_result db 0               ; +279 ... and LEARN_LEARNT, LEARN_FAILED or LEARN_FULL
rl_seq     dw 0                 ; +280 an ability's 4d4 rolled on the creation screen (RL_TRY), counted
rl_tries   times 24 db 0        ; +282 the last four 4d4 of each ability, STR to CHA (the dice log's,
                                ;      as the die tumbles faster than its ring is read)
seg_moved  db 0                 ; +306 1 once SEG_MOVE has made the new spells' records' room
           db 0                 ; +307
sold_seq   dw 0                 ; +308 a magical item sold to a merchant and kept (SELL_KEEP), counted:
sold_q     times 4 * 2 dw 0     ; +310 the last SOLD_SLOTS of them: the thing holding it, then
                                ;      the merchant (the shop's DS:179Ch), for the Loader to put in
                                ;      the merchant's pack (buyback.py)
panel_on   dw 0                 ; +326 the Loader sets 1 to have the combat log's panel drawn
                                ;      over the map (PANEL), 0 to have it gone (the view drawn again)
panel_seg  dw 0                 ; +328 the panel's picture: PANEL_W x PANEL_H palette indices, row
                                ;      by row, each row its four planes' bytes in turn (PANEL_BLIT),
                                ;      the Loader's to draw (combatlog.py); its own
                                ;      memory block (0: none could be had, no panel)
panel_new  dw 0                 ; +330 the Loader sets 1 once it has put a new picture there;
                                ;      DSCLOG draws it and sets it back to 0
panel_mx   dw 0                 ; +332 the pointer, as the mouse driver last said (game pixels): x,
panel_my   dw 0                 ; +334   y (MOUSE_EVENT)
panel_held dw 0                 ; +336 1 while the left button pressed on the panel is held (the
                                ;      press and its release kept from the game: PANEL_MOUSE)
panel_hits dw 0                 ; +338 the presses on the panel, counted, and where the last was:
panel_hx   dw 0                 ; +340   x,
panel_hy   dw 0                 ; +342   y
panel_top  dw PANEL_Y0          ; +344 the Loader's: where the panel's top is on the screen,
panel_rows dw PANEL_H           ; +346   and its height (at most PANEL_H_MOST), set before PANEL_NEW
panel_keys dw 0                 ; +348 L pressed on the map with the panel shown, counted (the
                                ;      companion collapses or opens it), or out of a fight with the
                                ;      panel off (it opens it); the key kept from the game
kit_outdoors db 0               ; +350 the Loader sets bit N while party member N stands under the
                                ;      open sky (stealth.daylight: the Military Scout's skills, the
                                ;      Rescuer's cures)
kit_dance  times 4 db 0         ; +351 each party member's Battle Dancer's dance, the Loader's (it
                                ;      rolls it as a fight starts and counts its rounds): +1 danced
                                ;      well, -1 stumbled, 0 none; to hit, to damage and on AC (KIT_EXTRA)
kit_wild   db 0                 ; +355 Wild Fighting, the Loader's (wild.py: it rolls each Wild Fury's
                                ;      check as a fight starts, clears it as the fight ends): bit N
                                ;      party member N's check failed (3 worse to hit, AC 3 worse), bit
                                ;      N + 4 it passed (1 more attack a round in melee, 3 more damage)
tick_off   dw ticks             ; +356 offset of TICKS: where the game was as its timer struck
                                ;      (PROBE_TICK), TICK_SLOTS records of TICK_SIZE bytes, for the
                                ;      Loader's freeze report
tick_seq   dw 0                 ; +358 records taken, counted: the newest in slot (TICK_SEQ - 1)
                                ;      mod TICK_SLOTS
kit_poisoned db 0               ; +360 bit N set once party member N, a Poisoner, has poisoned a
                                ;      foe this fight (PROBE_POISON); the Loader clears it as a fight
                                ;      starts
           db 0                 ; +361

; TEXT BUFFER: what the game sends to its dialogue window, as records of
;   byte 0FEh, byte kind (the dialogue window's: 0 = a reply to choose, the
;   first of a list being its title; 1 = a portrait; 2 = text; 3 = show the
;   replies; 4 = clear. 16 = a message box),
;   dword first argument (the text's far pointer, for 0, 2 and 16), word second
;   argument, word length, then that many bytes of text (for kinds 0, 2 and 16).
; A record is complete once TPOS counts it.

; ENTRY LAYOUT (ESIZE bytes, all words little-endian)
;   +0  seq of this entry (0xFFFF while being written)
;   +2  caller IP        +4  caller CS
;   +6  rand() result    +8  caller BP     +10 SS    +12 DS
;   +14 parent BP (word at SS:BP, the caller's caller's frame)
;   +16 32 bytes from SS:BP+2   (the caller's return address, then its arguments)
;   +48 32 bytes from SS:parentBP+2 (the same for the caller's caller)
;   +80 the 4 captured game words (glob)
;   +88 16 bytes from SS:BP-10h (the caller's last local variables)
;   +104 24 bytes of code at the caller's return address (overlays move, so
;       the code is copied now rather than read later)
;   +128 16 bytes of code at the return address stored at SS:BP+2 (the
;       caller's own caller)
;   +144 40 bytes from SS:parentBP-28h (the caller's caller's local variables)
;   +184 kind: 0 = a rand() call, 1 = PROBE_SAVE (+6 = total, save value),
;        2 = PROBE_AC (+6 = the AC)
;   +186 PROBE_SAVE: the segment of the game's spell table (0 otherwise)
;
; An entry is complete once the header's seq has counted it: the entry's own
; seq is written before the header's.

; The patched rand() starts with INT VEC_RAND. Drop the interrupt frame (restoring
; the caller's flags, so interrupts are enabled again) and be rand().
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
        pop cx                  ; POP leaves the flags alone
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


; RECORD: add an entry to the ring.
;   SS:SI+6 = the return address of the call being logged (IP, then CS)
;   BP      = the frame of the code that made that call
;   AX      = the value to store at +6;  [kind] = the entry kind
; Keeps every register except the flags.
record:
        push bx
        push cx
        push di
        push es
        mov es, [cs:ring_seg]
        mov di, [cs:widx]
        imul di, di, ESIZE
        mov word [es:di], 0xFFFF
        mov cx, [cs:kind]
        mov [es:di+184], cx
        mov cx, [cs:extra]
        mov [es:di+186], cx
        mov word [cs:extra], 0
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
        push ds                 ; DI is at +72: the caller's locals
        push si
        push ss
        pop ds
        lea si, [bp-16]
        mov cx, 8
        rep movsw
        pop si
        pop ds

        push ds                 ; DI is at +88: the calling code
        push si
        lds si, [ss:si+6]       ; the return address of this rand() call
        mov cx, 12
        rep movsw
        pop si
        push si
        lds si, [ss:bp+2]       ; the return address in the caller's frame
        mov cx, 8
        rep movsw
        push ss                 ; DI is at +128: the caller's caller's locals
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

; PROBE_SAVE: INT VEC_SAVE replaces "mov al,[bp-2] / cmp al,[bp-1]" (6 bytes:
; INT + 4 NOPs) at the end of the saving-throw function, where [bp-2] is the
; final total (d20 + modifiers) and [bp-1] the save value it must reach.
; Records both, then does the replaced instructions; RETF 2 keeps their flags. (Spook's save is
; worse for its caster's levels first: SPOOK_SAVE.)
probe_save:
        sti
        call spook_save
        push si
        mov si, sp
        sub si, 4               ; SS:SI+6 = our return address
        push ax
        push ds
        push bx
        lds bx, [ss:si+6]       ; our return address, 2 bytes after the patch
        mov ax, [bx-SPELL_SEG]  ; the saving throw's "mov ax,<spell table>"
        mov [cs:extra], ax
        pop bx
        pop ds
        mov ax, [bp-2]          ; AL = total, AH = save value
        mov word [cs:kind], 1
        call record
        pop ax
        pop si
        mov al, [bp-2]
        cmp al, [bp-1]
        retf 2

; PROBE_AC: INT VEC_AC replaces "mov ax,[bp-6] / add ax,si" (5 bytes: INT + 3
; NOPs) at the end of the AC function. Does the replaced instructions and
; records the result: the AC the game uses for this attack.
probe_ac:
        sti
        push si                 ; the game's SI is part of the AC
        mov ax, [bp-6]
        add ax, si
        call kit_ac
        mov si, sp
        sub si, 4
        mov word [cs:kind], 2
        call record
        pop si
        retf 2

; GPL_HOOK: the game's script interpreter calls the far pointer at DS:00ACh with
; each command's number before running it. The Loader points it here and
; puts the game's own hook in GPL_CHAIN. Records the command (kind 3), then
; passes on to the game's hook.
gpl_hook:
        push si
        mov si, sp
        sub si, 4               ; SS:SI+6 = our return address
        push ax
        mov ax, [ss:si+10]      ; the command number
        mov word [cs:kind], 3
        call record
        pop ax
        pop si
        jmp far [cs:gpl_chain]

; PROBE_TEXT: INT VEC_TEXT replaces "push bp / mov bp,sp" (3 bytes: INT + NOP) at
; the start of the game's routine that feeds its dialogue window
; (kind, dword, word). Copies what it's given to the text buffer, then does the
; replaced instructions for the routine.
probe_text:
        call text_enter         ; SS:BP+16 = the routine's arguments
        cmp word [cs:swap_on], 0
        je .record
        cmp byte [bp+16], 2     ; text for the window
        jne .record
        lds si, [bp+18]
        mov ax, ds
        or ax, si
        jz .record
        mov bx, swap_match
.same:  mov al, [cs:bx]
        or al, al
        jz .swap                ; all of SWAP_MATCH matched
        cmp al, [si]
        jne .record
        inc si
        inc bx
        jmp .same
.swap:  mov word [bp+18], swap_text  ; the routine is given ours instead
        mov [bp+20], cs
        mov word [cs:swap_on], 0
        inc word [cs:swap_seq]
.record:
        mov cl, [bp+16]
        lds si, [bp+18]
        mov dx, [bp+22]
        jmp text_leave

SWAP_SIZE equ 64
swap_match times SWAP_SIZE db 0
swap_text  times 240 db 0

; PROBE_MSG: the same for the game's message box routine (far pointer to the
; message), recorded as kind 16.
probe_msg:
        call text_enter
        mov cl, 16
        lds si, [bp+16]
        xor dx, dx
        jmp text_leave

text_enter:                     ; take the interrupt frame off, save registers, BP = SP
        pop word [cs:t_ret]
        pop word [cs:t_ip]      ; the routine's stack is underneath the interrupt frame
        pop word [cs:t_cs]
        pop word [cs:t_fl]
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
        jmp [cs:t_ret]

text_leave:                     ; record CL = kind, DS:SI = dword, DX = word, then return
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
        push word [cs:t_fl]
        push word [cs:t_cs]
        push word [cs:t_ip]
        iret

; PROBE_INV: INT VEC_CHAR replaces "add sp,0Eh" (3 bytes: INT + NOP) in the inventory
; screen's routine for its right-hand panel, straight after the weapon lines (AX = how many
; lines they took). Does the add, then adds in the game's own lettering: THAC0 and the five
; saving throws above STR, and for a thief the eight skills in a column right of the
; abilities (below the weapons, three of which reach the buttons, there'd be no room).
; The routine's code holds the (relocated) far address of the game's text routine at a
; fixed distance before the patch: it is read from there.
IV_PATCH  equ 0x6F6BF           ; DSUN.EXE offsets
IV_DRAW   equ 0x6F626           ; "lcall 0150h:016Dh" operand: the text routine
IV_WHO    equ 0x6F634           ; "mov ax,0348h" operand: segment of the character number (+25Bh)
THIEF_CLASS equ 17
THIEF_TABLE equ 0x3FAA - 0x4356 ; the thief tables' segment, relative to DS
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
        mov eax, [es:di + IV_DRAW - IV_PATCH]
        mov [cs:c_draw], eax
        mov fs, [es:di + IV_WHO - IV_PATCH]
        mov eax, [0x11A4]       ; the panel's window
        mov [cs:c_winptr], eax
        mov bx, [fs:0x25B]      ; the character on show
        mov [cs:c_who], bx
        imul ax, bx, 0x47
        les si, [0x1661]
        add si, ax              ; ES:SI = the character sheet
        cmp word [es:si + 0x10], 0
        je .done                ; an empty slot
        imul bx, bx, 0x3A
        lfs di, [0x1665]
        add di, bx              ; FS:DI = the creature record
        ; THAC0 and the saves
        mov al, [fs:di + 0x1F]
        mov bx, c_cells_top
        call c_cells_saves
        ; the DEX reaction adjustment (the game's table for initiative holds the same numbers),
        ; worked out now, so a change of DEX shows the next time the panel is drawn
        mov byte [cs:c_react], NO_REACT
        movzx bx, byte [fs:di + 0x23]
        cmp bx, 26
        jae .thieves
        mov al, [bx + DEX_REACTION]
        mov [cs:c_react], al
        mov al, [bx + DEX_DEFENCE]   ; and the defensive adjustment (on AC; on saves against
        mov [cs:c_defence], al       ; what can be dodged, the other way round)
.thieves:
        ; thief skills, for a character with thief levels
        xor cx, cx
        mov bx, 0x21
.cls:   cmp byte [es:si + bx], THIEF_CLASS
        je .thief
        inc bx
        inc cx
        cmp cx, 3
        jb .cls
        ; no thief levels: a ranger's move silently and hide in shadows (the Loader's
        ; stealth rule), in the thief's places, when the Loader sends them
        mov bx, [cs:c_who]
        call stats_for
        jc .react
        cmp byte [cs:bx + 17], STATS_RANGER
        jne .react
        mov ax, [cs:bx + 18 + 3]
        mov [cs:c_vals], ax
        mov bx, c_cells_thief + 3 * 8
        mov cx, 2
        mov byte [cs:c_signed], 0
        call c_cells
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

; PROBE_VIEW: INT VEC_VIEW replaces "push dword 000B0140h" (6 bytes: INT + 4 NOPs) near the
; end of the View Character screen's routine for its panels, once the game has drawn its own
; lines. Adds the five saves under the item icons, each with its label, and MOVE and THAC0 in the
; lower panel right of HP and PSI (as DAM is right of AC), then does the push.
; The routine's code holds, at fixed distances before the patch, the (relocated) far address
; of the text routine, the segment of the panel's window handle and the segment of the
; selected character's number: they are read from there.
CH_PATCH  equ 0x8A471           ; DSUN.EXE offsets
CH_DRAW   equ 0x8A2C8           ; "lcall 0150h:016Dh" operand: the text routine
CH_WIN    equ 0x8A2BD           ; "mov ax,0430h" operand: segment of the window's far pointer
CH_WHO    equ 0x8A2D6           ; "mov ax,0348h" operand: segment of the character number (+25Bh)
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
        mov eax, [es:di + CH_DRAW - CH_PATCH]
        mov [cs:c_draw], eax
        mov fs, [es:di + CH_WIN - CH_PATCH]
        mov eax, [fs:0]         ; the panel's window
        mov [cs:c_winptr], eax
        mov fs, [es:di + CH_WHO - CH_PATCH]
        mov bx, [fs:0x25B]      ; the character on show
        cmp bx, 3
        ja .done
        mov [cs:c_who], bx
        imul ax, bx, 0x47
        les si, [0x1661]
        add si, ax              ; ES:SI = the character sheet
        cmp word [es:si + 0x10], 0
        je .done                ; an empty slot
        imul bx, bx, 0x3A
        lfs di, [0x1665]
        mov cl, [fs:di + bx + 0x1B]  ; movement
        mov [cs:v_move_val], cl
        mov al, [fs:di + bx + 0x1F]  ; THAC0
        call c_load_stats       ; (or the Loader's, as they stand now)
        mov di, v_thac0 + 7
        mov al, [cs:c_vals]
        call c_itoa_s
        mov di, v_move + 7
        mov al, [cs:v_move_val]
        call c_itoa_s
        xor si, si              ; the saves, each with its label (V_SAVES)
.save:  mov bx, si
        shl bx, 2
        mov di, [cs:v_saves + bx]
        add di, 4
        mov al, [cs:c_vals + 1 + si]
        call v_two
        push word [cs:v_saves + bx + 2]  ; (its place: y, then x)
        mov ax, si
        and ax, 1
        imul ax, ax, V_SAVE_GAP
        add ax, V_SAVE_X
        push ax
        push cs
        push word [cs:v_saves + bx]
        call c_draw_line
        inc si
        cmp si, 5
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

v_two:                          ; AL (0-99) -> two digits (a space for a leading 0) and a space
        push bx                 ; at CS:DI; DI moves on
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
; the saves under the item icons, two to a row (PPD and RSW, PP and BW, SP), with the short
; labels the inventory panel gives them: each its text and its row's y
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

; THAC0 (AL) and the saves (sheet +37h..+3Bh at ES:SI), or the Loader's numbers as they
; stand now, as the cells at CS:BX say
c_cells_saves:
        call c_load_stats
        mov byte [cs:c_signed], 1  ; (THAC0 can be below 0)
        mov cx, 6
        jmp c_cells

; the eight thief skills of the character (sheet ES:SI, creature FS:DI, thief level AL):
; base + 4 a level + the race's adjustment + DEX, from the game's tables (before equipment and
; effects); the Loader's numbers instead, which count those too, while it keeps STATS
c_thief:
        push si
        mov dl, al
        shl dl, 2               ; 4 a level
        mov ax, ds
        add ax, THIEF_TABLE
        mov gs, ax
        mov dh, [fs:di + 0x23]  ; DEX
        movzx di, byte [es:si + 0x18]  ; race
        shl di, 3
        add di, 8               ; +8 + race * 8
        xor bx, bx
.skill: movsx ax, byte [gs:bx]  ; base
        movzx cx, dl
        add ax, cx
        movsx cx, byte [gs:bx + di]  ; race
        add ax, cx
        push dx                 ; DEX: -5 a point below LOW, +5 a point above HIGH, -3 above TOP
        movzx dx, dh
        movzx cx, byte [gs:bx + 0x90]
        sub cx, dx
        jle .nolow
        imul cx, cx, 5
        sub ax, cx
.nolow: mov cx, dx
        push dx
        movzx dx, byte [gs:bx + 0x98]
        sub cx, dx
        pop dx
        jle .nohigh
        imul cx, cx, 5
        add ax, cx
.nohigh:
        mov cx, dx
        push dx
        movzx dx, byte [gs:bx + 0xA0]
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
        mov al, [cs:c_vals + 6] ; pick pockets, open locks, find traps, move silently and hide in
        mov [cs:c_vals + 5], al ; shadows (which the Loader rolls: for picking pockets
                                ; and its stealth rule), and climb walls; not hear noise (one
                                ; script check in the game) or read languages (none)
        mov bx, [cs:c_who]      ; the Loader's, with equipment and effects, if it keeps them
        call stats_for
        jc .ours
        cmp byte [cs:bx + 17], 0
        je .ours
        mov eax, [cs:bx + 18]
        mov [cs:c_vals], eax
        mov ax, [cs:bx + 22]
        mov [cs:c_vals + 4], ax
.ours:  mov bx, c_cells_thief
        mov cx, 6
        mov byte [cs:c_signed], 0
        ; fall through

; CX cells at CS:BX: each x, y, label offset, value's x (words); the values are C_VALS in
; order. Keeps ES, SI, DI.
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

c_draw_line:                    ; stack: text far pointer, x, y (near return address first)
        push bp
        mov bp, sp
        push dword [bp + 4]     ; the text, for the format's %s
        push word [0x3270]      ; the colours, as the game sets them for its AC line
        push word 0x14
        push word [0x326E]
        push dword 0x00FE00FF
        push word 0
        push ds
        push word 0x0E11        ; the format: "%C%C%C%s"
        push dword [bp + 8]     ; x, y
        push dword [cs:c_winptr]  ; the window
        call far [cs:c_draw]
        add sp, 0x1C
        pop bp
        ret 8

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

; cells: x, y, label, value's x (window coordinates: the stats' labels are at x 0ECh, their
; values at 104h, STR at y 35h, lines 7 apart)
c_cells_top:
        dw 0xEC, 0x10, l_thac0, 0x111
        dw 0xEC, 0x17, l_ppd, 0x103,  0x113, 0x17, l_rsw, 0x12A
        dw 0xEC, 0x1E, l_pp, 0x103,   0x113, 0x1E, l_bw, 0x12A
        dw 0xEC, 0x25, l_sp, 0x103
c_cells_thief:                  ; right of the abilities (whose values end by 10Eh), in the
        dw 0x113, 0x35, l_pick, 0x12D  ; saves' second column, level with STR..CHA
        dw 0x113, 0x3C, l_lock, 0x12D
        dw 0x113, 0x43, l_trap, 0x12D
        dw 0x113, 0x4A, l_move, 0x12D  ; (move silently)
        dw 0x113, 0x51, l_hide, 0x12D  ; (hide in shadows)
        dw 0x113, 0x58, l_clmb, 0x12D
l_thac0 db 'THAC0:', 0
l_ppd   db 'PPD', 0
l_rsw   db 'RSW', 0
l_pp    db 'PP', 0
l_bw    db 'BW', 0
l_sp    db 'SP', 0
l_pick  db 'PICK', 0
l_lock  db 'LOCK', 0
l_trap  db 'TRAP', 0
l_move  db 'MOVE', 0
l_hide  db 'HIDE', 0
l_clmb  db 'CLMB', 0
l_react db 'REAC', 0
l_defence db 'DEF', 0
c_react db 0
c_defence db 0
DEX_DEFENCE equ 0x07F6          ; DS: the DEX defensive adjustment (bytes, by score: on AC)
DEF_Y   equ 0x72                ; the AC line's y
DEF_VALUE_X equ 0x12D           ; (under the thief skills' values, as REAC's)
NO_REACT equ 0x80
DEX_REACTION equ 0x07DC         ; DS: the DEX reaction adjustment (bytes, by score)
REACT_Y equ 0x25                ; the saves' last row, right of SP (where BW and RSW are above)
REACT_VALUE_X equ 0x130         ; (a little right of the thief skills' values: REAC is the longer label)
c_vals  times 8 db 0
c_num   db 0, 0, 0, 0
c_draw  dd 0
c_winptr dd 0


; The game's dialogue window (SHOW_WINDOW): its routines are reached through the game's overlay
; stub for them, whose segment is a fixed distance from the game's data segment.
DLG_STUB  equ 0x42CA - 0x4356   ; the stub's segment (DSUN.EXE: 42CAh) less the data segment's
DLG_FEED  equ 0x25              ; the window's input: (kind, far text, word), see the text buffer
DLG_WAIT  equ 0x34              ; wait for a reply to be clicked
S_PRESS   equ 0x15E8            ; DS: "Press continue"
S_CONT    equ 0x15F7            ; DS: "Continue"
S_CLOSE   equ 0x1F11            ; DS: "CLOSE"
TURN_WAIT equ 7                 ; timer ticks (55 ms each) the Loader has to answer

PICK_WAIT equ 9                 ; timer ticks the Loader has to answer (PROBE_USE_ITEM)
PICK_SIZE equ 240
pick_text times PICK_SIZE db 0

; GIVE_XP: the XP the Loader asked for with PICK_TEXT (XP_WHO, XP_AMOUNT), given by the routine
; the game's scripts give one person XP with (GPL 21h; it sees to a level gained), and the sound
; of a quest done that they play with it ("... receives N experience points!" is in PICK_TEXT);
; DS = the game's. Called in the frame PROBE_USE_ITEM makes for the overlay manager.
XP_SEG    equ 0x4251            ; (DSUN.EXE segments, less the load segment) an overlay's entry:
XP_OFF    equ 0x005C            ;   (who, how many)
give_xp:
        cmp word [cs:xp_who], 0xFFFF
        je .ret
        mov ax, ds
        sub ax, DGROUP_SEG - XP_SEG
        mov [cs:xp_call + 2], ax
        push word [cs:xp_amount]
        push word [cs:xp_who]
        call far [cs:xp_call]
        add sp, 4
        mov ax, ds
        sub ax, DGROUP_SEG - DROP_SEG
        mov [cs:sound_call + 2], ax
        push word QUEST_SOUND
        call far [cs:sound_call]
        add sp, 2
        mov word [cs:xp_who], 0xFFFF
.ret:   ret

xp_call dw XP_OFF, 0
drop_call dw DROP_OFF, 0
sound_call dw SOUND_OFF, 0

; PROBE_USE_ITEM: INT VEC_USE_ITEM replaces "cmp si,-1 / jne +3" (5 bytes: INT + 3 NOPs) in the
; routine that uses the item on the pointer on whatever is under it on the map (SI: that
; object, -1 for none). When the Loader wants picked pockets: count it, wait a moment for
; the Loader to see whether the item is its thieving tools and the object someone to rob
; (USE_TAKEN), and if so show what came of it (PICK_TEXT) and skip the game's own handling (the
; routine's end). Otherwise on as the compare and the JNE would have gone. Overlay code: the
; way back is put in a frame the overlay manager can fix up (pushed as a far call's, with BP).
USE_NONE  equ 0x7361A - 0x73617 ; (DSUN.EXE) SI = -1: "jmp", less the address after the INT
USE_SOME  equ 0x7361D - 0x73617 ; the JNE's target
USE_DONE  equ 0x7371D - 0x73617 ; the routine's end
USE_HELD_SEG equ 0x73A15 - 0x73617 ; the routine's "mov dx,<segment>" for the pointer's items,
                                ;   whose operand the game fixes up when it loads the code
HELD      equ 0x17A0            ; DS: the pointer's item (in that segment at HELD * 10 + 44h)
HELD_LIST equ 0x179E            ; DS: the object whose item list is the pointer's
DGROUP_SEG equ 0x4356           ; the game's DS, less its load segment
DROP_SEG  equ 0x1A0A            ; and the resident routine (21134h in DSUN.EXE) that empties an
DROP_OFF  equ 0x1C94            ;   object's item list, putting the items back on the free list
SOUND_OFF equ 0x0663            ; the resident routine there that plays a sound (GPL's 5Dh)
QUEST_SOUND equ 53              ; the sound of a quest done (the game's scripts, with their XP)
probe_use_item:
        sti
        pushad
        push es
        mov bx, sp              ; the interrupt frame at BX+34: IP, CS, flags
        mov dx, USE_NONE
        cmp si, -1
        je .go
        mov dx, USE_SOME
        cmp word [cs:pick_on], 0
        je .go
        mov [cs:use_who], si
        mov word [cs:use_taken], 0
        mov word [cs:use_item], 0xFFFF
        mov di, [HELD]          ; (DS: the game's)
        cmp di, -1
        je .asked
        imul di, di, 10
        push ds
        push si
        lds si, [ss:bx + 34]    ; DS:SI: the code after the INT
        mov ds, [si + USE_HELD_SEG]  ; the pointer's items' segment, as fixed up
        mov ax, [di + 0x44]
        pop si
        pop ds
        mov [cs:use_item], ax
.asked:
        inc word [cs:use_seq]
        xor ax, ax
        mov es, ax
        mov cx, [es:0x46C]      ; the BIOS timer
        call rtc_begin
.wait:  mov ax, [cs:use_reply]
        cmp ax, [cs:use_seq]
        je .ready
        mov ax, [es:0x46C]
        sub ax, cx
        cmp ax, PICK_WAIT
        jae .late_use_reply
        call rtc_waited         ; (the BIOS clock can stand still: the game's timer
        jnc .wait               ;   doesn't always pass its ticks on; at most 2 s by the real-time clock)
.late_use_reply:
        jmp .go                 ; no answer: the Loader isn't reading
.ready: cmp word [cs:use_taken], 0
        je .go
        cmp word [cs:use_taken], 2
        jne .kept
        ; 2: the item is used up (the cooked vulture, eaten): let go of the pointer's items the
        ; way the game does once it has counted coins picked up, and hold nothing
        push bx
        mov ax, ds
        sub ax, DGROUP_SEG - DROP_SEG
        mov [cs:drop_call + 2], ax
        push word [HELD_LIST]
        call far [cs:drop_call]
        add sp, 2
        mov word [HELD], -1
        mov ax, ds              ; (the drop routine's AX is its own)
        sub ax, DGROUP_SEG - DROP_SEG
        mov [cs:sound_call + 2], ax  ; and the sound the game plays when a quest is done (with
        push word QUEST_SOUND   ;   "... receives N experience points!": its 5Dh command)
        call far [cs:sound_call]
        add sp, 2
        pop bx
.kept:
        mov dx, USE_DONE
        add [ss:bx + 34], dx
        cmp byte [cs:pick_text], 0
        je .out
        push word [ss:bx + 36]
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        call give_xp
        mov word [cs:show_text], pick_text
        call show_window
        pop bp
        pop ax                  ; the way back, as the overlay manager has left it
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
        jmp .out
.go:    add [ss:bx + 34], dx
.out:   pop es
        popad
        iret

; the text at CS:[SHOW_TEXT] in the game's dialogue window, with "Continue" to click;
; DS = the game's
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
        push word 0             ; the text
        push cs
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
dlg     dd 0                    ; the dialogue window routine being called
showing db 0                    ; 1 while SHOW_WINDOW has its window up

; PROBE_USE: INT VEC_USE replaces "add sp,0Ch" (3 bytes: INT + NOP) in the USE (cast spells)
; screen's routine that labels its LEVEL button, which runs whenever the screen is drawn
; or the level changes. Draws the selected character's spell slots (SLOTS_TEXT, from the
; companion) in the empty panel under the spells, with the game's own text routine.
USE_TEXT_SEG equ 0x2B7A - 0x4356 ; the text routine's segment (DSUN.EXE: 2B7Ah) less DS's
USE_TEXT_OFF equ 0x16D
USE_WHO_SEG  equ 0x3931 - 0x4356 ; the selected character's number is at this segment:25Bh
SLOTS_SIZE   equ 96
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
        mov eax, [0x11A4]       ; the USE screen is up: PROBE_WIN may redraw on this window
        mov [cs:use_win], eax
        call use_draw
        pop fs
        pop es
        popad
        iret

; PROBE_WIN: INT VEC_WIN replaces "xor ax,ax / pop si" (3 bytes: INT + NOP) at the end of the
; game's routine that brings a window to the front and redraws it (its window far pointer the
; argument, at the routine's BP+6), which repaints the USE screen's panels when a character or
; spell level is picked, after the LEVEL button's label (where PROBE_USE draws). For the USE
; screen's window, once PROBE_USE has drawn on it (not while the screen opens), the slots are
; drawn again. Everything is kept on the stack: drawing may run the routine again.
WIN_USE_SEG equ 0x40BC - 0x4356 ; the USE screen's window pointer is at this segment:0
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
        call save_label         ; (the save/load window: which saves it shows)
        cmp eax, [cs:use_win]
        jne .done               ; not a USE screen PROBE_USE has drawn on
        cmp eax, [0x11A4]
        jne .done               ; not the window on show
        mov bx, ds
        add bx, WIN_USE_SEG
        mov es, bx
        cmp eax, [es:0]
        jne .done               ; not the USE screen
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

use_win dd 0                    ; the USE screen's window, as PROBE_USE last saw it

; PROBE_SAVE_PAGE: INT VEC_SAVE_PAGE replaces "jmp <the end>" (3 bytes: INT + NOP; DSUN.EXE 74901h),
; where the save/load window's event routine (74 8CAh; BP its frame) leaves a key it has no use
; for. The window shows ten saves, on four pages: the game's own (SAVE01.SAV to SAVE10.SAV), then
; SAVB, SAVC and SAVD01.SAV to 10.SAV. PgDn shows the next page, PgUp the one before; the PAGE 1
; to PAGE 4 buttons theirs (PROBE_SAVE_CLICK). The page is one letter of the game's two save
; names, the folder search's ("SAVE??.SAV") and the name a save is written to ("SAVE%.2d.SAV"):
; loading takes the name the search found. (The other pages' names don't match the game's
; search, so the game without the Loader never sees them: its list has room for ten, and a
; SAVE11.SAV would run past it.) For the new page, the window's own routines (in its overlay, at
; CS: nothing they call is an overlay, so it stays put) search the folder again and draw the
; rows, the selected row stays (in the load window, the first save: PgUp and PgDn pass by pages
; with none; a button's page with none is shown, its first row chosen, and SAVE_LABEL greys
; LOAD while the row chosen has no save; Enter, which the game's key table no longer has, comes
; here too and goes on to LOAD only on a row with a save), and the window is drawn again (SAVE_LABEL greys the
; page's button); then on as the routine goes on after Up or Down.
SP_IGNORE  equ 0x74DEC - 0x74903 ; (DSUN.EXE, from the way back: the NOP after the INT) the routine's end
SP_DONE    equ 0x74A21 - 0x74903 ; ... after Up or Down: the screen updated, then the end
SP_KEY     equ 0x12             ; the key, at the routine's BP+12h
SP_SCAN    equ 0x743E2 - 0x74300 ; the overlay's routines (offsets in its segment): search the folder,
SP_ROW     equ 0x74E36 - 0x74300 ;   draw a row,
SP_PICK    equ 0x74ECD - 0x74300 ;   show a row as chosen (and its description below)
SAVE_SEG   equ 0x3BA7 - 0x4356  ; the window's data (DS-relative): the saves, 7Dh bytes each from +2
SAVE_SIZE  equ 0x7D             ;   (+2 the file's name, +52h the description), +4E4h the chosen
SAVE_CHOSEN equ 0x4E4           ;   row, +4E6h the window, +4EAh 1: the load window
SAVE_WIN   equ 0x4E6
SAVE_LOADING equ 0x4EA
BTN_SEG    equ 0x2A1D - 0x4356  ; (resident) a button's state: (window, id, state)
BTN_OFF    equ 0x71A
WIN_SEG    equ 0x25EC - 0x4356  ; (resident) bring a window to the front and draw it (PROBE_WIN's)
WIN_OFF    equ 0x618
NAME_FIND  equ 0x1DCF + 3       ; DS: "SAVE??.SAV": the letter that is the page
NAME_SAVE  equ 0x1DDA + 3       ; DS: "SAVE%.2d.SAV"
KEY_ENTER  equ 0x1C0D           ; (taken out of the window's key table: gamepatch.py's save_enter)
SP_ENTER   equ 0x74C68 - 0x74903 ; ... where the window's routine takes it: LOAD (or SAVE)
KEY_PGUP   equ 0x4900
KEY_PGDN   equ 0x5100
ROW_ID     equ 0x80B            ; the rows' buttons: 80Bh on
LOAD_ID    equ 0x809            ; LOAD (in the save window, SAVE)
probe_save_page:
        push bp
        mov bp, sp              ; BP+2 the way back, BP+4 its segment
        sti
        pushad
        push es
        mov word [cs:sp_done], SP_DONE
        mov word [cs:sp_ignore], SP_IGNORE
        mov byte [cs:sp_zero], 0
        mov si, [bp]            ; the routine's BP
        mov ax, [ss:si + SP_KEY]
        cmp al, 0xE0
        jne .scan
        xor al, al              ; (the grey keys': as the number pad's)
.scan:  cmp ax, KEY_ENTER
        jne .pages
        call sp_es              ; Enter: LOAD, as the game's own, but not on a row with no save
        cmp word [es:SAVE_LOADING], 0
        je .enter
        imul bx, [es:SAVE_CHOSEN], SAVE_SIZE
        cmp byte [es:bx + 2], 0
        je sp_skip
.enter: add word [bp + 2], SP_ENTER
        pop es
        popad
        pop bp
        iret
.pages: mov dl, -1              ; (the page before)
        cmp ax, KEY_PGUP
        je .step
        mov dl, 1               ; (the next)
        cmp ax, KEY_PGDN
        jne sp_skip
.step:  mov [cs:sp_step], dl
        call sp_now
        add al, dl
        mov bl, al
        jmp sp_want

; PROBE_SAVE_CLICK: INT VEC_SAVE_CLICK replaces "jmp <the end>" (3 bytes: INT + NOP; DSUN.EXE
; 74B9Fh), where the window's event routine leaves a click on a button it doesn't know: PAGE 1 to
; PAGE 4 (savepages.py) show that page (then the routine's end returns 0, as for the game's own
; buttons).
SC_DONE    equ 0x74A21 - 0x74BA1 ; (DSUN.EXE, from the way back) the screen updated, then the end
SC_IGNORE  equ 0x74DE5 - 0x74BA1 ; the end for the game's buttons
SC_ID      equ 8                ; the button, at the routine's BP+8
PAGE1_ID   equ 0x815            ; (PAGE 1 to PAGE 4: 815h to 818h)
PAGES      equ 4
probe_save_click:
        push bp
        mov bp, sp
        sti
        pushad
        push es
        mov word [cs:sp_done], SC_DONE
        mov word [cs:sp_ignore], SC_IGNORE
        mov byte [cs:sp_zero], 1
        mov si, [bp]
        mov ax, [ss:si + SC_ID]
        sub ax, PAGE1_ID
        cmp ax, PAGES
        jae sp_skip
        mov bl, al
        mov byte [cs:sp_step], 0  ; (that page or none)

sp_want:                        ; BL the page wanted (0 to 3), SP_STEP: where to look on from it
        cmp bl, PAGES           ;   if the load window has no saves on it (-1, 1; 0: nowhere)
        jae sp_skip             ; (no page before the first, or after the last)
        call sp_now
        cmp bl, al
        je sp_skip              ; (on that page already)
        mov [cs:sp_target], bl
        mov al, [NAME_FIND]
        mov [cs:sp_was], al     ; the page now, if no page wanted has anything to load
        mov ax, [bp + 4]
        mov [cs:sp_call + 2], ax
        call sp_es
        mov di, [es:SAVE_CHOSEN]
.try:   movzx bx, byte [cs:sp_target]
        mov bl, [cs:sp_letters + bx]
        call sp_page
        cmp word [es:SAVE_LOADING], 0
        je .rows
        xor di, di              ; loading: the first save on the page
.first: imul bx, di, SAVE_SIZE
        cmp byte [es:bx + 2], 0
        jne .rows
        inc di
        cmp di, 10
        jb .first
        mov al, [cs:sp_step]    ; none: the next page that way, if there is one
        add [cs:sp_target], al
        xor di, di              ; (a button's page: shown empty, its first row chosen)
        or al, al
        jz .rows
        cmp byte [cs:sp_target], PAGES
        jb .try
.none:  mov bl, [cs:sp_was]     ; none at all: back to the page there was
        call sp_page
        jmp sp_skip
.rows:  xor cx, cx
.row:   push cx
        push cx
        mov word [cs:sp_call], SP_ROW
        call far [cs:sp_call]
        add sp, 2
        pop cx
        inc cx
        cmp cx, 10
        jb .row
        call sp_es
        push word 5             ; the row chosen before: as the others
        mov ax, [es:SAVE_CHOSEN]
        call sp_button
        mov [es:SAVE_CHOSEN], di
        push word 4             ; ... and the one chosen now
        mov ax, di
        call sp_button
        push di
        mov word [cs:sp_call], SP_PICK
        call far [cs:sp_call]
        add sp, 2
        call sp_es
        push dword [es:SAVE_WIN]
        mov ax, ds
        add ax, WIN_SEG
        mov [cs:sp_call + 2], ax
        mov word [cs:sp_call], WIN_OFF
        call far [cs:sp_call]
        add sp, 4
        mov ax, [cs:sp_done]
        add [bp + 2], ax
        pop es
        popad
        cmp byte [cs:sp_zero], 0
        je .back
        xor si, si              ; (a click: the routine returns 0, as for its own buttons)
.back:  pop bp
        iret
sp_skip:
        mov ax, [cs:sp_ignore]
        add [bp + 2], ax
        pop es
        popad
        pop bp
        iret

sp_now:                         ; AL the page shown (0 to 3: the game's names' letter in SP_LETTERS)
        push bx
        mov al, [NAME_FIND]
        xor bx, bx
.find:  cmp al, [cs:sp_letters + bx]
        je .found
        inc bx
        cmp bx, PAGES
        jb .find
        xor bx, bx              ; (not one of them: as the first)
.found: mov al, bl
        pop bx
        ret

sp_page:                        ; BL the page's letter: the names, then the folder searched again
        mov [NAME_FIND], bl     ;   (ES the window's data again after)
        mov [NAME_SAVE], bl
        push word 10
        mov word [cs:sp_call], SP_SCAN
        call far [cs:sp_call]
        add sp, 2
sp_es:  mov ax, ds              ; ES: the window's data (the game's routines keep neither BX nor ES)
        add ax, SAVE_SEG
        mov es, ax
        ret

sp_button:                      ; AX a row, the state pushed (taken off): its button's state
        add ax, ROW_ID
sp_button_id:                   ; (AX the button)
        push bp
        mov bp, sp
        push word [bp + 4]      ; the state
        movsx eax, ax
        push eax
        push dword [es:SAVE_WIN]
        mov ax, ds
        add ax, BTN_SEG
        mov [cs:sp_btn + 2], ax
        call far [cs:sp_btn]
        add sp, 10
        call sp_es
        pop bp
        ret 2

sp_btn  dw BTN_OFF, 0           ; the game's routine for a button's state
sp_call dd 0
sp_was  db 0
sp_letters db 'EBCD'            ; the pages' letters (SAVE??.SAV, SAVB, SAVC, SAVD)
sp_target db 0
sp_step   db 0
sp_done   dw 0                  ; where the event routine goes on: after the page changes,
sp_ignore dw 0                  ;   or not (from the way back)
sp_zero   db 0                  ; 1: a click (the routine to return 0)

; SAVE_LABEL: (PROBE_WIN; EAX the window drawn, DS the game's) on the save/load window, the
; button of the page shown (PAGE 1 to PAGE 4, savepages.py) out of use: so it shows which; and in
; the load window, LOAD out of use while the row chosen has no save (an empty page's).
save_label:
        pushad
        push es
        cmp byte [cs:sl_busy], 0
        jne .out                ; (setting a button's state may draw the window again)
        mov bx, ds
        add bx, SAVE_SEG
        mov es, bx
        cmp eax, [es:SAVE_WIN]
        jne .out
        mov byte [cs:sl_busy], 1
        call sp_now
        mov [cs:sl_page], al
        xor si, si
.button:
        xor cx, cx              ; (states: 1 out of use, 0 in use)
        mov ax, si
        cmp al, [cs:sl_page]
        jne .state
        inc cx
.state: push cx
        lea ax, [si + PAGE1_ID]
        call sp_button_id
        inc si
        cmp si, PAGES
        jb .button
        cmp word [es:SAVE_LOADING], 0
        je .done
        imul bx, [es:SAVE_CHOSEN], SAVE_SIZE
        xor cx, cx
        cmp byte [es:bx + 2], 0
        jne .load
        inc cx                  ; (no save there)
.load:  push cx
        mov ax, LOAD_ID
        call sp_button_id
.done:  mov byte [cs:sl_busy], 0
.out:   pop es
        popad
        ret

sl_busy    db 0
sl_page    db 0

use_draw:                       ; the selected character's slots in the USE screen's panel
        mov ax, ds
        add ax, USE_WHO_SEG
        mov es, ax
        mov bx, [es:0x25B]      ; the character on show
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
        mov eax, [0x11A4]       ; the screen's window
        mov [cs:c_winptr], eax
        mov dx, USE_FIRST_Y
.line:  mov di, u_line          ; copy one line (up to "|" or the end) and draw it
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
        push si
        push dx
        push dx                 ; y
        push word USE_X         ; x
        push cs
        push word u_line
        call c_draw_line
        pop dx
        pop si
        add dx, USE_STEP
        cmp byte [cs:si], '|'
        jne .done
        inc si
        cmp dx, USE_LAST_Y
        jbe .line
.done:  ret
; PROBE_LOOK: INT VEC_LOOK replaces "mov si,ax / xor di,di" (4 bytes: INT + 2 NOPs) in the
; routine that fills the Look box (right-click to Look, then a monster in a fight), where the
; first of its four status rows have been drawn and AX says how many. Asks the Loader
; for up to three short lines about the monster (LOOK_TEXT), prints them in the rows left
; with the game's text routine, as the box prints the monster's level, and moves the game's
; row count past them, so its own status lines follow in any row still free. If the
; companion also gave the whole description (LOOK_FULL), PROBE_UNLOOK shows it in the dialogue
; window as the box closes.
LOOK_PATCH equ 0x5FCDA          ; DSUN.EXE offsets
LOOK_DRAW  equ 0x5FCB8          ; "lcall 0090h:0A40h" operand: the text routine
LOOK_ROWS  equ 4                ; the box's status rows: y = (row + 2) * 7 + 10h
LOOK_SIDE  equ 1                ; a line starting with this goes on LEVEL's row (row -1), to its right
LOOK_SIDE_X equ 60              ;   at this x (past LEVEL: 10)
probe_look:
        sti
        pushad
        push es
        mov si, sp              ; SS:SI: ES, then EDI, ESI, EBP, ESP, EBX, EDX, ECX, EAX, IP, CS, flags
        mov ax, [ss:si + 30]
        mov [cs:l_row], ax      ; the rows the game has used
        cmp word [cs:look_on], 0
        je .done
        mov bx, [bp + 0xA]      ; the combatant (BP: the Look routine's frame)
        mov [cs:look_who], bx
        mov byte [cs:look_text], 0
        mov byte [cs:look_full], 0
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
        cmp ax, TURN_WAIT
        jae .late_look_reply
        call rtc_waited         ; (the BIOS clock can stand still: the game's timer
        jnc .wait               ;   doesn't always pass its ticks on; at most 2 s by the real-time clock)
.late_look_reply:
        jmp .done               ; no answer: the Loader isn't reading
.ready: mov es, [ss:si + 36]
        mov di, [ss:si + 34]
        sub di, 2               ; ES:DI = the patch
        mov eax, [es:di + LOOK_DRAW - LOOK_PATCH]
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
        jae .full
        cmp byte [cs:di], 0
        je .full
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
        push word 0x11          ; as the box prints LEVEL
        push word 0x1F
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
.full:  cmp byte [cs:look_full], 0
        je .done
        mov byte [cs:look_pending], 1
.done:  mov si, sp              ; the replaced code: SI = the rows used, DI = 0
        mov ax, [cs:l_row]
        mov [ss:si + 6], ax
        mov dword [ss:si + 2], 0
        pop es
        popad
        iret

; PROBE_TICK: INT VEC_TICK replaces "inc word cs:[0004h]" (5 bytes: INT + 3 NOPs; DSUN.EXE
; 3925Ch), the first instruction of the game's timer handler (IRQ 0, the timer its own: the
; game's timers run from it). Does that, and every TICK_EVERY strikes notes where the game was
; (what the timer interrupted) in TICKS, for the Loader's freeze report: its CS:IP, flags, SS,
; SP (before the interrupt), BP, DS and ES, and the strikes counted. Interrupts stay off.
TICK_EVERY equ 16
TICK_SLOTS equ 32
TICK_SIZE  equ 16
probe_tick:
        push bp
        mov bp, sp              ; BP+2 this interrupt's frame (in the handler), BP+8 the timer's
        push ds
        push ax
        push bx
        mov ds, [bp + 4]        ; the handler's CS
        inc word [4]            ; the replaced instruction
        inc word [cs:tick_count]
        test byte [cs:tick_count], TICK_EVERY - 1
        jnz .out
        mov bx, [cs:tick_seq]
        and bx, TICK_SLOTS - 1
        shl bx, 4               ; (TICK_SIZE)
        add bx, ticks
        mov ax, [bp + 8]
        mov [cs:bx], ax         ; +0 IP
        mov ax, [bp + 10]
        mov [cs:bx + 2], ax     ; +2 CS
        mov ax, [bp + 12]
        mov [cs:bx + 4], ax     ; +4 flags
        mov [cs:bx + 6], ss     ; +6 SS
        lea ax, [bp + 14]
        mov [cs:bx + 8], ax     ; +8 SP
        mov ax, [bp]
        mov [cs:bx + 10], ax    ; +10 BP
        mov ax, [bp - 2]
        mov [cs:bx + 12], ax    ; +12 DS
        mov [cs:bx + 14], es    ; +14 ES
        inc word [cs:tick_seq]
.out:   pop bx
        pop ax
        pop ds
        pop bp
        iret
tick_count dw 0
ticks   times TICK_SLOTS * TICK_SIZE db 0

; PROBE_POISON: INT VEC_POISON replaces "jmp 7A7C5h" (3 bytes: INT + NOP; DSUN.EXE 7A6DDh) in the
; routine giving a hit's special effects (DI the attacker's combatant, SI the target's; the
; attacker's creature at its [BP-6]), where a person who isn't a thri-kreen has none and goes on to
; the end. A Poisoner's first hit in a fight (KIT_POISONED's bit for it clear) queues the monsters'
; poison on the target as a monster's poisoned hit does (the routine at 790D2h: the target, the
; attacker, power 176, "poison (10 damage)", its save the game's, and the attacker's level from
; 508:2Ah, whose far call is at 7A7ACh), and marks it used. Then on to the end, as the jump went.
POISON_POWER  equ 176
PZ_TO_END     equ 0x7A7C5 - 0x7A6DF   ; (from the INT's way back)
PZ_TO_QUEUE   equ 0x790D2 - 0x7A6DF
PZ_TO_LEVEL   equ 0x7A7AD - 0x7A6DF   ; (the far call's address)
probe_poison:
        push bp
        mov bp, sp              ; BP+2 the INT's way back, [BP] the routine's BP
        pushad
        push es
        mov bx, [bp]
        mov ax, [ss:bx - 6]     ; (the attacker's creature)
        cmp ax, 3
        ja .out                 ; (not a party member)
        call cr_is
        db KIT_POISONER
        jne .out
        bts word [cs:kit_poisoned], ax
        jc .out                 ; (its poison used this fight)
        mov es, [bp + 4]
        mov bx, [bp + 2]
        mov eax, [es:bx + PZ_TO_LEVEL]
        mov [cs:pz_far], eax
        push di
        call far [cs:pz_far]    ; (the attacker's level)
        add sp, 2
        xor ah, ah
        push ax
        push word POISON_POWER
        push di
        push si
        mov ax, [bp + 2]
        add ax, PZ_TO_QUEUE
        mov [cs:pz_far], ax
        mov ax, [bp + 4]
        mov [cs:pz_far + 2], ax
        call far [cs:pz_far]
        add sp, 8
.out:   add word [bp + 2], PZ_TO_END
        pop es
        popad
        pop bp
        iret
pz_far  dd 0

; PROBE_ARROW: INT VEC_ARROW replaces "mov es:[0006h],al" (4 bytes: INT + 2 NOPs; DSUN.EXE 58D27h)
; in the routine that finds a missile weapon's ammunition (58C8Fh; [BP+0Ch] the weapon's item
; type), where it keeps the ammunition's plus (AL) for the shot's damage and magic (the game takes
; the better of the weapon's and the ammunition's plus for the hit's +1/+2/+3 damage kinds). For a
; Spellarcher whose turn it is (WHOSE_TURN's combatant; kits.arrow_plus), arrows shot from a bow
; are 1 better and at least +1.
probe_arrow:
        push bx
        push si
        mov si, [bp + 0x0C]
        cmp si, KIND_TYPES
        jae .store
        cmp byte [cs:si + kind_of_type], BOW_KIND
        jne .store              ; (not a bow: sling stones as they are)
        push ax
        push es
        mov ax, ds
        add ax, THINGS_SEG
        mov es, ax
        imul bx, [WHOSE_TURN], 3
        mov ax, [es:bx + COMBATANT_CREATURE]
        pop es
        cmp ax, 3
        ja .not                 ; (not a party member)
        call cr_is
        db KIT_SPELLARCHER
.not:   pop ax
        jne .store
        cmp al, 0
        jge .plus
        xor al, al              ; (a cursed arrow: +1 all the same)
.plus:  inc al
.store: mov [es:0x6], al
        pop si
        pop bx
        iret

; PROBE_UNLOOK: INT VEC_UNLOOK replaces "mov word [0844h],270Fh" (6 bytes: INT + 4 NOPs) at the
; end of the routine that closes the Look box (the game forgets whom it was looking at). Does
; that, then shows the monster's whole description (LOOK_FULL) in the dialogue window.
probe_unlook:
        mov word [0x844], 0x270F  ; the replaced instruction (DS = the game's)
        sti
        pushad
        push es
        cmp byte [cs:look_pending], 0
        je .out
        cmp byte [cs:showing], 0
        jne .out
        mov byte [cs:look_pending], 0
        mov word [cs:show_text], look_full
        mov bx, sp              ; the interrupt frame at BX+34: IP, CS, flags
        push word [ss:bx + 36]  ; the way back in a frame the overlay manager can fix up (pushed
        push word [ss:bx + 34]  ;   as a far call's, with BP): the dialogue window may load other
        push bp                 ;   overlays over this routine's while it waits for Continue
        mov bp, sp
        call show_window
        pop bp
        pop ax                  ; the way back, as the overlay manager has left it
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
.out:   pop es
        popad
        iret

; STATS: STATS_SIZE bytes for each party member, kept by the Loader: +0 1 if in use, +1 THAC0
; with the main weapon (signed), +2 the five saves as the d20 needed now, +8 three words: the
; item numbers of the weapons ready, +14 three bytes: the THAC0 with each (signed), +17 1 for a
; thief (2 for a ranger: of the six, only move silently and hide in shadows count), +18 the six
; thief skills the panel shows, as they stand (equipment and effects too)
STATS_SIZE  equ 24
STATS_RANGER equ 2
STATS_FRESH equ 91              ; timer ticks (5 seconds)
STATS_WAIT  equ 9               ; ... (half a second): the longest a screen waits for fresh STATS
stats   times 4 * STATS_SIZE db 0

; A screen is being drawn: while the Loader is keeping STATS, have it bring them up to date
; (an item just put on, say) and wait for that, once for all the screen's lines (not again
; within 2 timer ticks). The game stands still meanwhile, so its state is what's drawn.
stats_sync:
        push ax
        push dx
        push es
        xor ax, ax
        mov es, ax
        mov dx, [es:0x46C]
        mov ax, dx
        sub ax, [cs:sync_at]
        cmp ax, 2
        jb .out                 ; this screen's already
        mov ax, dx
        sub ax, [cs:stats_stamp]
        cmp ax, STATS_FRESH
        jae .out                ; the Loader isn't running
        inc word [cs:stats_req]
        call rtc_begin
.wait:  mov ax, [cs:stats_reply]
        cmp ax, [cs:stats_req]
        je .done
        mov ax, [es:0x46C]
        sub ax, dx
        cmp ax, STATS_WAIT
        jae .done
        call rtc_waited         ; (as the waits for the Loader: the BIOS clock can stand still)
        jnc .wait
.done:  mov ax, [es:0x46C]
        mov [cs:sync_at], ax
.out:   pop es
        pop dx
        pop ax
        ret

sync_at dw 0

; RTC_BEGIN, RTC_WAITED: a wait for the Loader ends after its BIOS ticks, or, as the BIOS clock
; stands still while the game's timer handler keeps its ticks to itself (as in some fights), once
; the real-time clock's second has changed twice (1 to 2 seconds): never a hang.
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

; BX = a party member (0-3): CF clear and CS:BX = their STATS entry if the Loader keeps it
; current, CF set if not
stats_for:
        cmp bx, 3
        ja .no
        push ax
        push es
        xor ax, ax
        mov es, ax
        mov ax, [es:0x46C]
        sub ax, [cs:stats_stamp]
        cmp ax, STATS_FRESH
        pop es
        pop ax
        jae .no
        imul bx, bx, STATS_SIZE
        add bx, stats
        cmp byte [cs:bx], 0
        je .no
        clc
        ret
.no:    stc
        ret

; THAC0 (AL) and the saves (sheet +37h..+3Bh at ES:SI) into C_VALS, or the Loader's numbers
; for the character in C_WHO instead. Keeps ES, SI, DI.
c_load_stats:
        push bx
        mov [cs:c_vals], al
        mov eax, [es:si + 0x37]
        mov [cs:c_vals + 1], eax
        mov al, [es:si + 0x3B]
        mov [cs:c_vals + 5], al
        mov bx, [cs:c_who]
        call stats_sync
        call stats_for
        jc .own
        mov al, [cs:bx + 1]
        mov [cs:c_vals], al
        mov eax, [cs:bx + 2]
        mov [cs:c_vals + 1], eax
        mov al, [cs:bx + 6]
        mov [cs:c_vals + 5], al
.own:   pop bx
        ret

c_itoa_s:                       ; AL (signed) -> decimal at CS:DI, with "-" below 0; keeps BX, CX
        test al, al
        jns c_itoa
        mov byte [cs:di], '-'
        inc di
        neg al
        jmp c_itoa

; PROBE_WEAPON: INT VEC_WEAPON replaces "add sp,10h" (3 bytes: INT + NOP) straight after the
; routine that lists a creature's weapons (on the inventory screen, and in the Look box) has
; drawn one: its name, then its damage, AX lines from y = [BP+0Eh]. Does the add, then puts
; the THAC0 the Loader worked out for that weapon at the right of its last line.
W_PATCH equ 0x7276E             ; DSUN.EXE offsets
W_DRAW  equ 0x72851             ; "lcall 0090h:0A40h" operand: the routine that draws the lines
W_X     equ 0x12A               ; (window coordinates: the lines start at 0ECh)
probe_weapon:
        pop word [cs:w_ip]
        pop word [cs:w_cs]
        pop word [cs:w_fl]
        add sp, 0x10            ; the replaced instruction
        sti
        pushad
        push es
        or ax, ax
        jz .done
        mov [cs:w_lines], ax
        mov bx, [bp + 0x0A]     ; the creature (its object number: the party's are 0-3)
        cmp bx, 3
        ja .done
        call stats_sync
        call stats_for
        jc .done
        mov si, [bp - 2]        ; the entry of the item list the weapon came from
        imul si, si, 10
        mov dx, [bp + si - 0x330]  ; its item number
        xor cx, cx
.find:  mov di, cx
        shl di, 1
        cmp [cs:bx + di + 8], dx
        je .found
        inc cx
        cmp cx, 3
        jb .find
        mov ax, AMMO_SLOT       ; (the game lists the ammunition a missile weapon shoots, its
        call w_slot             ;   arrows: the THAC0 is the missile weapon's)
        jne .done
        xor cx, cx
.missile:
        mov di, cx
        shl di, 1
        mov dx, [cs:bx + di + 8]
        mov ax, MISSILE_SLOT_W
        call w_slot
        je .found
        inc cx
        cmp cx, 3
        jb .missile
        jmp .done
.found: mov di, cx
        mov al, [cs:bx + di + 14]
        mov di, w_text + 1
        call c_itoa_s
        mov es, [cs:w_cs]
        mov di, [cs:w_ip]
        mov eax, [es:di + W_DRAW - W_PATCH - 2]
        mov [cs:w_draw], eax
        mov ax, [cs:w_lines]
        dec ax
        imul ax, ax, 7
        add ax, [bp + 0x0E]     ; the weapon's last line
        push word [bp + 0x12]   ; the colours, as the routine draws its lines
        push word [bp + 0x10]
        push ax
        push word W_X
        push cs
        push word w_text
        push dword [bp + 6]     ; the window
        call far [cs:w_draw]
        add sp, 0x10
.done:  pop es
        popad
        push word [cs:w_fl]
        push word [cs:w_cs]
        push word [cs:w_ip]
        iret

; W_SLOT: ZF set if item DX (0270Fh and above: none) is in slot AX (its +11h). DS the game's;
; registers kept.
AMMO_SLOT      equ 1
MISSILE_SLOT_W equ 2
w_slot:
        cmp dx, 0x270F
        jae .no
        push bx
        push es
        push ax
        imul bx, dx, 0x15
        les ax, [0x165D]
        add bx, ax
        pop ax
        cmp [es:bx + 0x11], al
        pop es
        pop bx
        ret
.no:    cmp sp, 0               ; (ZF clear)
        ret

w_ip    dw 0
w_cs    dw 0
w_fl    dw 0
w_lines dw 0
w_draw  dd 0
w_text  db 'T', 0, 0, 0, 0
c_who   dw 0
c_signed db 0

; RINGS: the game has rings (item type RING_TYPE, a plain "Ring") but nothing that makes
; one better AC or saves. The Loader can put a Ring +1 in the arena; these two make its
; plus count, as a ring of protection's would.
RING_TYPE  equ 102
HELM_LEATHER equ 5              ; the helm item types: Helm, Dapartea's Helm; Helm of
HELM_METAL   equ 89             ; Contemplation; and a leather one no object uses (Helm of
HELM_OTHER   equ 109            ; Might, made by a script)
HELM_BONE    equ 117            ; (and the Loader's bone helm, of TYPES)
FINGER     equ 4                ; the item's slot byte while worn on a finger (the left
FINGER2    equ 11               ; hand's, then the right's)
CLOAK      equ 12               ; ... and on the back
THINGS     equ 0xC36            ; the things table (3 bytes each: kind, index) in its segment
NO_THING   equ 0x270F
CREATURES  equ 0x1665           ; DS: far pointer to the creature records (3Ah bytes each)
ITEMS      equ 0x165D           ; DS: far pointer to the item records (15h bytes each)
ITEM_TYPES equ 0x1669           ; DS: far pointer to the item types (14h bytes each; +0Ah: 1 melee)
WS_MELEE   equ 0xFFFE           ; WS_TYPE: any melee weapon

; PROBE_RING_AC: INT VEC_RING_AC replaces "mov al,es:[bx+0Fh] / cbw" (5 bytes: INT + 3 NOPs)
; in the AC function, where ES:BX is a worn item's type, CX its number, DX the item and DI the
; creature's thing; bit 80h of AX says the type counts for AC (the plus less the type's AC).
; Does that, counting rings too. With RULE_PROTECTION, AD&D's: a ring of protection betters
; AC only without magical armour, and of two rings only the better (the left hand's if they're
; equal); a cloak of protection (the second of TYPES) counts only without magical or metal
; armour and without a shield (PROT_SCAN).
probe_ring_ac:
        mov al, [es:bx+0x0F]
        cbw
        cmp cx, RING_TYPE
        jne .cloak
        or al, 0x80
        test word [cs:rules], RULE_PROTECTION
        jz .done
        call prot_here
        jc .done
        test byte [cs:p_flags], P_MAGIC_ARMOUR
        jnz .off
        push ax
        push bx
        push es
        les bx, [ITEMS]
        mov ax, dx
        imul ax, ax, 0x15
        add bx, ax
        mov al, [es:bx+0x11]    ; the slot this ring is worn in
        mov ah, [cs:p_ring]
        cmp al, FINGER
        je .first
        cmp [cs:p_ring2], ah    ; (the other hand's) counts if better than the left's
        jmp .which
.first: cmp ah, [cs:p_ring2]    ; the left hand's counts unless the other is better
.which: pop es
        pop bx
        pop ax
        jg .done                ; (the better: counts)
        je .tie
        jmp .off
.tie:   push ax                 ; equal: the left hand's
        push bx
        push es
        les bx, [ITEMS]
        mov ax, dx
        imul ax, ax, 0x15
        add bx, ax
        cmp byte [es:bx+0x11], FINGER
        pop es
        pop bx
        pop ax
        je .done
.off:   and al, 0x7F
.done:  iret
.cloak: push ax
        mov ax, [cs:types_first]
        or ax, ax
        jz .other
        inc ax
        cmp cx, ax
        jne .other
        pop ax
        test word [cs:rules], RULE_PROTECTION
        jz .done
        call prot_here
        jc .done
        test byte [cs:p_flags], P_MAGIC_ARMOUR | P_METAL_ARMOUR | P_SHIELD
        jnz .off
        iret
.other: pop ax
        push ax                 ; bracers of defense: their plus counts, but not over armour
        mov ax, cx              ; on the arms, legs, head or chest (AD&D's; a shield, rings and
        call bracers_ax         ; cloaks go with them)
        pop ax
        jne .helm
        call prot_here
        jc .done
        test byte [cs:p_flags], P_ARMOUR
        jnz .off
        iret
.helm:  cmp cx, HELM_LEATHER    ; a helm: AC 1 with RULE_HELMS (the game's are all 0), 0 without
        je .is
        cmp cx, HELM_METAL
        je .is
        cmp cx, HELM_OTHER
        je .is
        cmp cx, HELM_BONE
        je .is
        iret
.is:    push ax
        xor al, al
        test byte [cs:rules], RULE_HELMS
        jz .set
        inc al
.set:   mov [es:bx+0x12], al    ; (the type's AC, read next)
        pop ax
        iret

; PROBE_BOX_AC: INT VEC_BOX_AC replaces "mov al,es:[bx+12h]" (4 bytes: INT + 2 NOPs; DSUN.EXE 8C15Ah)
; in the item box's routine, the type's AC for its "AC BONUS:", ES:BX the type's record, SI the
; type: a helm's set first as PROBE_RING_AC sets it (1 with RULE_HELMS, else 0), so a helm not
; yet worn shows it too.
probe_box_ac:
        cmp si, HELM_LEATHER
        je .is
        cmp si, HELM_METAL
        je .is
        cmp si, HELM_OTHER
        je .is
        cmp si, HELM_BONE
        jne .read
.is:    xor al, al
        test byte [cs:rules], RULE_HELMS
        jz .set
        inc al
.set:   mov [es:bx + 0x12], al
.read:  mov al, [es:bx + 0x12]
        iret

; PROBE_RING_SAVE: INT VEC_RING_SAVE replaces "xor si,si" (2 bytes) at the start of the
; function that adds up a saving throw's modifiers into SI, DI being the one saving. Starts
; SI at the plus of the rings they wear instead of 0.
probe_ring_save:
        push bp
        mov bp, sp              ; SS:BP+2 = our return address
        push ax
        push bx
        push cx
        push dx
        push es
        xor si, si
        les bx, [bp+2]
        mov ax, [es:bx+6]       ; the things table's segment: the code after the patch is
        call ring_plus          ; "mov bx,di / imul bx,bx,3 / mov ax,<segment>"
        mov bx, [bp]            ; (the routine's frame: [BP+14h] the spell)
        mov ax, [ss:bx + 0x14]
        call kit_save
        pop es
        pop dx
        pop cx
        pop bx
        pop ax
        pop bp
        iret

ring_plus:                      ; DS = the game's, AX = the things table's segment, DI = a
        mov [cs:r_things], ax   ; creature's thing: SI += the pluses of the rings it wears
        test word [cs:rules], RULE_PROTECTION
        jnz .rules
        mov es, ax
        mov bx, di
        imul bx, bx, 3
        cmp byte [es:bx+THINGS], 2
        jne .done               ; not a creature
        mov ax, [es:bx+THINGS+1]
        mov [cs:r_who], ax
        mov word [cs:ws_slot], FINGER
        mov word [cs:ws_type], RING_TYPE
        call worn_scan
        add si, [cs:ws_plus]
        mov ax, [cs:r_who]
        mov word [cs:ws_slot], FINGER2
        call worn_scan
        add si, [cs:ws_plus]
.cloak: mov ax, [cs:types_first]  ; and a cloak of protection's (the second of TYPES), worn
        or ax, ax
        jz .done
        inc ax
        mov [cs:ws_type], ax
        mov word [cs:ws_slot], CLOAK
        mov ax, [cs:r_who]
        call worn_scan
        add si, [cs:ws_plus]
.done:  ret
.rules: call prot_scan          ; RULE_PROTECTION: the better ring only, whatever the armour;
        jc .done                ; the cloak only without magical or metal armour or a shield
        mov al, [cs:p_ring]
        cmp al, [cs:p_ring2]
        jge .ring
        mov al, [cs:p_ring2]
.ring:  cbw
        add si, ax
        test byte [cs:p_flags], P_MAGIC_ARMOUR | P_METAL_ARMOUR | P_SHIELD
        jnz .done
        mov es, [cs:r_things]
        mov bx, di
        imul bx, bx, 3
        mov ax, [es:bx+THINGS+1]
        mov [cs:r_who], ax
        jmp .cloak

; PROT_HERE: (called from PROBE_RING_AC, its INT's return address at SP+2) PROT_SCAN for the
; AC routine's creature DI, the things table's segment being in its "mov ax,<segment>" A8h
; bytes on (DSUN.EXE 58F66h).
prot_here:
        push bp
        mov bp, sp
        push es
        push bx
        les bx, [bp+4]
        mov bx, [es:bx+0xA8]
        mov [cs:r_things], bx
        pop bx
        pop es
        pop bp
        ; (on into PROT_SCAN)

; PROT_SCAN: what creature thing DI wears (DS = the game's, R_THINGS the things table's
; segment) that the protection rules weigh: P_FLAGS (P_MAGIC_ARMOUR: a worn armour piece,
; chest, arm, leg or helm, with a plus; P_METAL_ARMOUR: one of metal; P_SHIELD: a shield in a hand),
; P_RING and P_RING2 (the plus of the ring on each hand's finger, 0 for none or less). CF set
; if DI isn't a creature. Keeps every register.
prot_scan:
        pushad
        push es
        mov es, [cs:r_things]
        mov bx, di
        imul bx, bx, 3
        cmp byte [es:bx+THINGS], 2
        jne .not
        mov ax, [es:bx+THINGS+1]
        imul ax, ax, 0x3A
        mov [cs:r_creature], ax
        mov byte [cs:p_flags], 0
        mov word [cs:p_ring], 0         ; (and P_RING2)
        mov cx, 8                       ; its item lists, each a thing: +8, +0Ah, +0Ch
.list:  les bx, [CREATURES]
        add bx, [cs:r_creature]
        add bx, cx
        mov dx, [es:bx]
        cmp dx, NO_THING
        jae .next
        mov es, [cs:r_things]
        mov bx, dx
        imul bx, bx, 3
        cmp byte [es:bx+THINGS], 1
        jne .next                       ; not an item
        mov dx, [es:bx+THINGS+1]
        mov byte [cs:r_left], 100
.item:  cmp dx, NO_THING
        jae .next
        les bx, [ITEMS]
        mov ax, dx
        imul ax, ax, 0x15
        add bx, ax
        mov dx, [es:bx+4]               ; (the next)
        mov si, [es:bx+0x0A]            ; the type
        mov al, [es:bx+0x11]            ; the slot
        mov ah, [es:bx+0x14]            ; the plus
        cmp si, RING_TYPE
        jne .type
        cmp ah, 0
        jle .on
        cmp al, FINGER
        jne .ring2
        mov [cs:p_ring], ah
        jmp .on
.ring2: cmp al, FINGER2
        jne .on
        mov [cs:p_ring2], ah
        jmp .on
.type:  push ax
        mov ax, si
        call bracers_ax                 ; (bracers aren't armour)
        pop ax
        je .on
        les bx, [ITEM_TYPES]
        imul si, si, 0x14
        add bx, si
        test byte [es:bx], 4            ; a shield (the flag the game's AC reads for one)
        jz .body
        cmp al, HAND_RIGHT
        je .shield
        cmp al, HAND_LEFT
        jne .on
.shield: or byte [cs:p_flags], P_SHIELD
        jmp .on
.body:  cmp al, ARM_SLOT                ; armour: worn on the arms, legs, head or chest, and
        je .armour                      ; counting for AC
        cmp al, LEG_SLOT
        je .armour
        cmp al, HEAD_SLOT
        je .armour
        cmp al, CHEST_SLOT
        jne .on
.armour: test byte [es:bx+0x0F], 0x80
        jz .on
        or byte [cs:p_flags], P_ARMOUR  ; (a helm too, to bracers)
        cmp ah, 0
        jle .metal
        or byte [cs:p_flags], P_MAGIC_ARMOUR
.metal: mov al, [es:bx+8]               ; its material (no material: 40h with 0)
        and al, 0x4F
        cmp al, MATERIAL_METAL
        jne .on
        or byte [cs:p_flags], P_METAL_ARMOUR
.on:    dec byte [cs:r_left]
        jnz .item
.next:  add cx, 2
        cmp cx, 0x0E
        jb .list
        clc
        jmp .out
.not:   stc
.out:   pop es
        popad
        ret

; Weapon specialization (RULE_SPECIALIZE; dsloader/specialize.py). A character's chosen weapon
; kinds are in its sheet's +14h..+17h (SPEC_SLOTS: the kind + 1 each, 0 none); a character with
; none there (monsters, and those who have not chosen) fights as the game has it. Two probes in
; the routine that makes a weapon attack (its [BP+0Ah] the THAC0 the d20 is held against, [BP+10h]
; the attacker's sheet, [BP+14h] the weapon's item type, [BP+16h] above 1 for a missile; its
; locals [BP-8] the attacks a round in halves, [BP-0Eh] the damage dice and [BP-10h] their
; sides, [BP-12h] the damage bonus):
; PROBE_ATTACKS: INT VEC_ATTACKS replaces "cbw / mov [bp-8],ax" (4 bytes: INT + 2 NOPs; DSUN.EXE
; 58892h), the attacks a round stored. The game gives every fighter, gladiator and ranger AD&D's
; specialist's rate (3/2, then 2 from 7th level, 5/2 from 13th); in melee a warrior (more than 2
; halves) with a weapon of a kind not chosen has AD&D's plain rate, half an attack less, and a
; grand master one more. A Crusader or Mind Warrior has a warrior's extra attacks in melee
; (WAR_KIT_OF), whatever RULE_SPECIALIZE. Specialization +1 to hit, mastery +3 (the THAC0 less).
; PROBE_SPEC_DAMAGE: INT VEC_SPEC_DAMAGE replaces "add [bp-12h],ax" (3 bytes: INT + NOP; 588F2h),
; the strength bonus added to the damage bonus: specialization +2, mastery +3, and grand mastery
; the damage dice one size larger (2 more sides: d8 to d10, 2d4 to 2d6).
SPEC_SLOTS equ 0x14
SPEC_COUNT equ 4
FIGHTER_CLASS equ 9
GLADIATOR_CLASS equ 10
MASTERY equ 5                   ; (the fighter levels)
GRAND_MASTERY equ 9
SPEC_NONE equ 0                 ; (SPEC_OF's levels)
SPEC_PLAIN equ 1
SPEC_EXPERT equ 2
SPEC_SPECIAL equ 3
SPEC_MASTER equ 4
SPEC_GRAND equ 5
probe_attacks:
        cbw
        push ax
        call kit_to_hit         ; (a Ravager's, a Brute's, an Arena Champion's)
        sub [bp + 0x0A], ax
        call kit_extra          ; (a Battle Dancer's dance, a Wilderness Avenger's against undead)
        sub [bp + 0x0A], ax
        pop ax
        test word [cs:rules], RULE_SPECIALIZE
        jz .store
        push dx
        call spec_of
        cmp word [bp + 0x16], 1
        jg .missile
        cmp ax, 2
        ja .warrior
        call expert_of          ; (not a warrior: a Battle Mage's expertise)
        jmp .hit
.warrior:
        cmp dl, SPEC_PLAIN
        jne .grand
        dec ax
        jmp .hit
.grand: cmp dl, SPEC_GRAND
        jne .hit
        add ax, 2
.hit:   cmp dl, SPEC_SPECIAL
        jb .done
        ja .three
        dec word [bp + 0x0A]
        jmp .done
.three: sub word [bp + 0x0A], 3
.done:  pop dx
.store: call war_kit_of        ; (a Crusader's or Mind Warrior's extra attacks, in melee)
        cmp word [bp + 0x16], 1
        jle .melee_kit
        call own_throws         ; (K'ratchek's chatkcha: one more a round)
        jmp .kept
.melee_kit:
        call wild_passed        ; (Wild Fighting, its check passed: 1 more a round in melee)
        jnc .tame
        add ax, WILD_HALVES
.tame:  push bx
        mov bx, [bp + 0x12]     ; (the weapon's item)
        call off_hand_halves    ; (RULE_TWO_WEAPONS: the off hand's one a round)
        pop bx
.kept:  mov [bp - 8], ax
        iret
.missile:                       ; (a specialist's rate of fire, else the game's)
        push bx
        push si
        push es
        mov si, [bp + 0x10]
        imul si, si, 0x47
        les bx, [0x1661]
        add bx, si
        mov si, [bp + 0x14]
        call missile_rate
        pop es
        pop si
        pop bx
        jmp .hit

; OWN_THROWS: AX (the attacks a round in halves) one more a round (OWN_THROWS_MORE) for a missile
; attack ([BP+16h] above 1) with a chatkcha (item type [BP+14h]) by K'ratchek, the game's own
; party's thri-kreen (OWN_RACE_B; sheet number [BP+10h]): her chatkcha comes back as if she had
; several (kits.OWN_THROWS). DS the game's; others kept.
OWN_THROWS_MORE equ 2
own_throws:
        push bx
        push si
        push es
        mov si, [bp + 0x10]
        imul si, si, 0x47
        les bx, [0x1661]
        add bx, si
        push ax
        call own_race_b
        cmp al, THRI_KREEN_RACE
        pop ax
        jne .out
        mov si, [bp + 0x14]
        cmp si, KIND_TYPES
        jae .out
        cmp byte [cs:si + kind_of_type], MISSILE_KIND
        jne .out
        add ax, OWN_THROWS_MORE
.out:   pop es
        pop si
        pop bx
        ret

; OWN_RACE_B: AL the race of sheet ES:BX if it is one of the game's own party given a feature of
; its own (KIT_BYTE's OWN_BIT, set by the Loader as a new game starts: defaultparty.py), with the
; kits on (RULE_HI_KITS): Gerakis (half-giant) Wild Fighting (the Loader's, KIT_WILD), K'ratchek
; (thri-kreen) a Wasteland Seer's casting (SKY_LEVEL) and OWN_THROWS, Cilla (elf) the Elven
; Wanderer's hiding (the Loader's); else 0, ZF set. CR_OWN_RACE the same for creature AX (DS the
; game's). Others kept.
OWN_BIT equ 0x40
own_race_b:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .none
        mov al, [es:bx + KIT_BYTE]
        cmp al, KIT_OPEN
        je .none
        test al, OWN_BIT
        jz .none
        mov al, [es:bx + 0x18]
        or al, al
        ret
.none:  xor al, al
        ret
cr_own_race:
        push bx
        push es
        call creature_sheet
        call own_race_b
        pop es
        pop bx
        ret

; MISSILE_RATE: AX (the attacks a round in halves: the weapon type's, +0Bh, as the game has a
; missile's) made a specialist's rate of fire when greater, for skill DL (SPEC_EXPERT or above: a
; fighter's or gladiator's chosen kind, a ranger's, a ranger's bow) with item type SI, the sheet at
; ES:BX, by the warrior's level (the highest fighter, gladiator or ranger level of the classes it
; has now: 1-6, 7-12, 13 on): AD&D's
; for the sling, 3/2, 2, 5/2 a round; the bow, staff sling and chatkcha a step above AD&D's, the bow
; 3, 4, 5, the staff sling and chatkcha 3/2, 2, 5/2; a grand master one more. A warrior's weapon of
; a kind not chosen (SPEC_PLAIN), from 7th level: the specialist's rate a band lower, as in melee
; (a bow 3 at 7-12, a sling 3/2).
MISSILE_KIND equ 13             ; (the chatkcha's kind + 1; then the bow, the sling, the staff sling)
missile_halves db 3, 4, 5, 6, 8, 10, 3, 4, 5, 3, 4, 5
missile_rate:
        cmp dl, SPEC_PLAIN
        jb .ret
        cmp si, KIND_TYPES
        jae .ret
        push cx
        push dx
        push si
        movzx cx, byte [cs:si + kind_of_type]
        sub cx, MISSILE_KIND
        jb .out
        cmp cx, 3
        ja .out
        xor dx, dx              ; DL the specialist's level
        xor si, si
.class: push ax
        mov al, [es:bx + si + 0x21]
        mov ah, [es:bx + si + 0x24]
        or si, si               ; (a human's earlier classes once the first's level has passed theirs)
        jz .on
        cmp byte [es:bx + 0x18], 1
        jne .on
        cmp ah, [es:bx + 0x24]
        jae .next
.on:    cmp al, FIGHTER_CLASS
        je .warrior
        cmp al, GLADIATOR_CLASS
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
.grand: pop si                  ; (DX, pushed after it: the skill back in DL)
        pop dx
        push dx
        push si
        cmp dl, SPEC_GRAND
        jne .out
        add ax, 2               ; (a grand master one more shot, as in melee)
.out:   pop si
        pop dx
        pop cx
.ret:   ret

; EXPERT_OF: EXPERT_HALVES for the attack routine's attacker ([BP+10h] its sheet's number).
expert_of:
        push bx
        push es
        push ax
        mov ax, [bp + 0x10]
        imul ax, ax, 0x47
        les bx, [0x1661]
        add bx, ax
        pop ax
        call expert_halves
        pop es
        pop bx
        ret

; EXPERT_HALVES: AX the attacks a round (halves) of a character who isn't a warrior (the game's 2:
; 1 a round), DL its skill with the weapon (SPEC_OF_SHEET), ES:BX its sheet: with SPEC_EXPERT (a
; Battle Mage's chosen weapon spec, kits.py; no warrior has fewer than 3 halves) the expertise
; rate, 3/2 a round, 2 from 7th level (specialize.expert_attacks). Others kept.
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
        jb .ret
        inc ax
.ret:   ret

; OFF_HAND_HALVES: AX the attacks a round (halves) with item BX, a melee weapon: with RULE_TWO_WEAPONS
; (AD&D's two weapons), no more than one a round (2 halves) in the off hand (its slot OFF_HAND_SLOT),
; whoever wields it; the extra attacks are the main hand's. DS the game's; others kept.
OFF_HAND_SLOT equ 10
off_hand_halves:
        test byte [cs:rules], RULE_TWO_WEAPONS
        jz .ret
        cmp ax, 2
        jbe .ret
        cmp bx, 0x270F
        jae .ret
        push es
        push bx
        push ax
        imul bx, bx, 0x15
        les ax, [0x165D]
        add bx, ax
        cmp byte [es:bx + 0x11], OFF_HAND_SLOT
        pop ax
        pop bx
        pop es
        jne .ret
        mov ax, 2
.ret:   ret

; WAR_KIT_OF: AX the attacks a round (halves) of PROBE_ATTACKS's attacker ([BP+10h]) made a
; Crusader's or Mind Warrior's (WAR_KIT_HALVES) for a melee attack ([BP+16h] 1 or less). Others kept.
war_kit_of:
        cmp word [bp + 0x16], 1
        jg .ret
        push bx
        push es
        push ax
        mov ax, [bp + 0x10]
        imul ax, ax, 0x47
        les bx, [0x1661]
        add bx, ax
        pop ax
        call war_kit_halves
        pop es
        pop bx
.ret:   ret

; WAR_KIT_HALVES: AX the melee attacks a round (halves) of a character who isn't a warrior (2 or
; fewer), ES:BX its sheet: a Crusader's or Mind Warrior's (kit awake) the warrior's extra attacks,
; 3/2 a round from 7th level of the kit's class, 2 from 13th, the better of the two kits' for a
; human with both (kits.warrior_attacks). Others kept.
war_kit_halves:
        cmp ax, 2
        ja .ret
        push dx
        mov dx, ax
        call kit_is_b
        db KIT_CRUSADER
        jne .mind
        call .by_level
.mind:  call kit_is_b
        db KIT_MIND_WARRIOR
        jne .back
        call .by_level
.back:  mov ax, dx
        pop dx
.ret:   ret
.by_level:                      ; (DL the more of itself and the level's, KIT_WHERE's level)
        push ax
        call kit_level
        mov ah, 3
        cmp al, 13
        jb .early
        inc ah
.early: cmp al, 7
        jb .no
        cmp dl, ah
        jae .no
        mov dl, ah
.no:    pop ax
        ret

probe_spec_damage:
        add [bp - 0x12], ax
        call kit_attack_damage
        push ax
        call kit_extra
        add [bp - 0x12], ax
        call wild_passed        ; (Wild Fighting, its check passed: 3 more)
        jnc .wild
        add word [bp - 0x12], WILD_DAMAGE
.wild:  pop ax
        test word [cs:rules], RULE_SPECIALIZE
        jz .done
        push dx
        call spec_of
        cmp dl, SPEC_SPECIAL
        jb .out
        ja .three
        add word [bp - 0x12], 2
        jmp .out
.three: add word [bp - 0x12], 3
        cmp dl, SPEC_GRAND
        jne .out
        add word [bp - 0x10], 2
.out:   pop dx
.done:  iret

; PROBE_DAM_LINE: INT VEC_DAM_LINE replaces "mov al,es:[bx+2Ah]" (4 bytes: INT + 2 NOPs; DSUN.EXE
; 72A77h) in the routine that writes a melee weapon's "DAM: 1.5x1D8+4" (View Character, the
; inventory screen), ES:BX the sheet, SI the weapon's item type, the damage bonus, the dice's sides
; and their count pushed (under the INT's return, in that order up). With RULE_SPECIALIZE, the
; attacks as PROBE_ATTACKS gives them, and the bonus and sides as PROBE_SPEC_DAMAGE does; a
; Crusader's or Mind Warrior's extra attacks (WAR_KIT_HALVES) either way.
probe_dam_line:
        push bp
        mov bp, sp              ; BP+8 the count, +0Ah the sides, +0Ch the bonus
        push ax
        call kit_melee          ; (a Ravager's, a Brute's)
        add [bp + 0x0C], ax
        pop ax
        pop bp
        mov al, [es:bx + 0x2a]
        test word [cs:rules], RULE_SPECIALIZE
        jz .done
        push bp
        mov bp, sp
        push dx
        call spec_of_sheet
        cmp al, 2
        ja .warrior
        push cx                 ; (not a warrior: a Battle Mage's expertise; AH kept)
        mov ch, ah
        xor ah, ah
        call expert_halves
        mov ah, ch
        pop cx
        jmp .bonus
.warrior:
        cmp dl, SPEC_PLAIN
        jne .grand
        dec al
        jmp .bonus
.grand: cmp dl, SPEC_GRAND
        jne .bonus
        add al, 2
.bonus: cmp dl, SPEC_SPECIAL
        jb .out
        ja .three
        add word [bp + 0x0C], 2
        jmp .out
.three: add word [bp + 0x0C], 3
        cmp dl, SPEC_GRAND
        jne .out
        add word [bp + 0x0A], 2
.out:   pop dx
        pop bp
.done:  push cx                 ; (a Crusader's or Mind Warrior's extra attacks; the off hand's
        mov ch, ah              ;  one a round, the item DI; AH kept)
        xor ah, ah
        call war_kit_halves
        push bx
        mov bx, di
        call off_hand_halves
        pop bx
        mov ah, ch
        pop cx
        iret

; PROBE_MISSILE_LINE: INT VEC_MISSILE_LINE replaces "mov al,es:[bx+0Bh]" (4 bytes: INT + 2 NOPs;
; DSUN.EXE 729FFh) in the same routine's branch for a missile weapon (the inventory screen's
; "1D4"), ES:BX its item type's record, SI the type, the routine's [BP-6] the creature (0 for
; none), the damage bonus, the dice's sides and their count pushed as for PROBE_DAM_LINE. AL: the
; weapon's attacks a round (halves). With RULE_SPECIALIZE, the rate of fire as PROBE_ATTACKS gives
; it (MISSILE_RATE), and the bonus and sides as PROBE_SPEC_DAMAGE does; K'ratchek's chatkcha one
; more a round, as OWN_THROWS (with the kits on, whatever the specialization rule).
probe_missile_line:
        mov al, [es:bx + 0x0B]
        cmp dword [bp - 6], 0
        je .ret
        push di
        mov di, sp              ; DI+8 the count, +0Ah the sides, +0Ch the bonus
        push bx
        push dx
        push es
        cbw
        push ax
        les bx, [bp - 6]        ; the creature, its sheet
        mov ax, [es:bx + 4]
        imul ax, ax, 0x47
        les bx, [0x1661]
        add bx, ax
        pop ax
        test word [cs:rules], RULE_SPECIALIZE
        jz .own
        push ax
        call spec_of_sheet
        pop ax
        call missile_rate
        cmp dl, SPEC_SPECIAL
        jb .own
        ja .three
        add word [ss:di + 0x0C], 2
        jmp .own
.three: add word [ss:di + 0x0C], 3
        cmp dl, SPEC_GRAND
        jne .own
        add word [ss:di + 0x0A], 2
.own:   push ax                 ; (K'ratchek's chatkcha: one more a round, as OWN_THROWS)
        call own_race_b
        cmp al, THRI_KREEN_RACE
        pop ax
        jne .out
        cmp si, KIND_TYPES
        jae .out
        cmp byte [cs:si + kind_of_type], MISSILE_KIND
        jne .out
        add ax, OWN_THROWS_MORE
.out:   pop es
        pop dx
        pop bx
        pop di
.ret:   iret

; PROBE_VIEW_DAM: INT VEC_VIEW_DAM replaces "mov [bp-0Eh],dx" (3 bytes: INT + NOP; DSUN.EXE 64EB6h)
; in View Character's routine for its "DAM: 1.5x1D8+4": DX the damage bonus it stores, its [BP-6]
; the attacks a round (halves), [BP-2] the dice's count, [BP-4] their sides, [BP-0Ah] the weapon's
; item. A Crusader's or Mind Warrior's extra attacks (WAR_KIT_HALVES, not with a missile weapon).
; With RULE_SPECIALIZE, the attacks (not a missile weapon's), the bonus and the sides as the
; attack has them (PROBE_ATTACKS, PROBE_SPEC_DAMAGE), for the character on show: its number in
; the segment the routine's "mov ax,seg" at 64E33h holds, +25Bh (as PROBE_VIEW's CH_WHO).
VIEW_DAM_WHO equ 0x84           ; that operand, back from the INT's return
probe_view_dam:
        mov [bp - 0x0E], dx
        call wp_rules
        jz .done
        push ax
        push bx
        push dx
        push si
        push di
        push es
        mov ax, [bp - 0x0A]     ; the item, its type
        imul ax, ax, 0x15
        les bx, [0x165D]
        add bx, ax
        mov si, [es:bx + 0x0A]
        mov di, sp
        mov bx, [ss:di + 12]    ; (the INT's return, past the six pushes)
        mov es, [ss:di + 14]
        mov es, [es:bx - VIEW_DAM_WHO]
        mov ax, [es:0x25B]      ; the character on show, its sheet
        imul ax, ax, 0x47
        les bx, [0x1661]
        add bx, ax
        push ax
        call kit_melee          ; (a Ravager's, a Brute's: the rule for kits being on)
        add [bp - 0x0E], ax
        pop ax
        mov dl, SPEC_NONE
        test word [cs:rules], RULE_SPECIALIZE
        jz .bonus
        call spec_of_sheet
        mov ax, si              ; a missile weapon (the type's +0, 2) keeps its rate
        imul ax, ax, 0x14
        push es
        push bx
        les bx, [0x1669]
        add bx, ax
        test byte [es:bx], 2
        pop bx
        pop es
        jnz .bonus
        cmp word [bp - 6], 2
        ja .warrior
        push ax                 ; (not a warrior: a Battle Mage's expertise)
        mov ax, [bp - 6]
        call expert_halves
        mov [bp - 6], ax
        pop ax
        jmp .bonus
.warrior:
        cmp dl, SPEC_PLAIN
        jne .grand
        dec word [bp - 6]
        jmp .bonus
.grand: cmp dl, SPEC_GRAND
        jne .bonus
        add word [bp - 6], 2
.bonus: cmp dl, SPEC_SPECIAL
        jb .out
        ja .three
        add word [bp - 0x0E], 2
        jmp .out
.three: add word [bp - 0x0E], 3
        cmp dl, SPEC_GRAND
        jne .out
        add word [bp - 4], 2
.out:   mov ax, si              ; (a Crusader's or Mind Warrior's extra attacks, not a missile
        imul ax, ax, 0x14       ; weapon's)
        push es
        push bx
        les bx, [0x1669]
        add bx, ax
        test byte [es:bx], 2
        pop bx
        pop es
        jnz .gone
        mov ax, [bp - 6]
        call war_kit_halves
        mov bx, [bp - 0x0A]             ; (the item: the off hand's one a round)
        call off_hand_halves
        mov [bp - 6], ax
.gone:  pop es
        pop di
        pop si
        pop dx
        pop bx
        pop ax
.done:  iret

; PROBE_CAN_USE: INT VEC_CAN_USE replaces "and ax,[es:bx+12h]" (4 bytes: INT + 2 NOPs; DSUN.EXE
; 6EF34h) in the routine that says whether a character may equip an item (its "Cannot use this
; item" when not; its only caller, the equip routine): AX the item type's mask of the classes that
; may use it, ES:BX the character's sheet, its +12h a bit for each of its classes, DX the item
; type. With RULE_RESTRICT, an item the game allows that the character's classes keep it from
; (CLASS_FORBIDS) is not allowed either. The kit's own (KIT_ALLOWS) are allowed whatever the
; game's lists and the restrictions; the kit's limits (KIT_FORBIDS) hold over everything.
probe_can_use:
        and ax, [es:bx + 0x12]
        jnz .game
        call kit_allows         ; (the game's lists say no: the kit's own, all the same)
        jnc .done
        inc ax
.game:  mov byte [cs:kf_spec], 0
        push si
        mov si, [bp]            ; (the equip routine's frame: its [BP+8] the slot, 14 the off hand)
        cmp word [ss:si + 8], EQUIP_OFF_HAND
        pop si
        sete [cs:kf_off_hand]
        call kit_forbids
        mov byte [cs:kf_off_hand], 0
        jc .no
        test word [cs:rules], RULE_RESTRICT
        jz .done
        call kit_allows         ; (the kit's own: whatever the classes' restrictions)
        jc .done
        call class_forbids
        jnc .done
.no:    xor ax, ax
.done:  iret

; KIT_FORBIDS: carry set if the kit of the character whose sheet is at ES:BX keeps it from item
; type DX (kits.forbids): a Ravager a shield, a missile or thrown weapon, and armour that isn't
; light; a Twin-blade a shield, and a two-handed weapon (but a half-giant's,
; with RULE_HALF_GIANT); a Brute a one-handed melee weapon, and a shield (but a half-giant's,
; with the rule), and with KF_SPEC set (a weapon spec chosen) a missile weapon; a Stalker armour
; that isn't light (leather, or of no material); an Assassin, Shinobi, Shadowblade, Poisoner or
; Spellarcher the same, asleep too (KIT_LIGHT); a Grove Warden a metal weapon; a Lifebinder a
; weapon of a kind not blunt (KIT_BLUNT); a Shinobi a shield, armour that isn't light, and a
; weapon not of its kinds (KIT_SHINOBI); a Seeker a weapon its sphere doesn't allow (as a
; cleric's: SPHERE_ALLOWS), but the bow. A weapon of a kind the character specialized in (its
; SPEC_SLOTS, while they count: SPECS_AWAKE; but choosing one, KF_SPEC) none, but for the off
; hand's. DS the game's; all registers kept.
KT_MELEE   equ 0x01             ; (the item type's +0 flags, +0Fh kind flags)
KT_MISSILE equ 0x02
KT_SHIELD  equ 0x04
KT_THROWN  equ 0x10
KT_ARMOUR  equ 0x80
KT_TWO_HANDED equ 0x40
KIT_BLUNT  equ 0xC112           ; bits by kind: club, mace, quarterstaff, sling, staff sling
HALF_GIANT equ 5
kit_forbids:
        push ax
        push cx
        push di
        call kit_place          ; (each of its kits awake: KIT_AT, KIT_AWAKE)
        jc .ok
.place: call kit_at
        jz .next
        call kit_light          ; (the light-armour kits, asleep too)
        jc .out
        call kit_awake
        jc .next
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
; KIT_LIGHT: carry set if kit AL keeps its character to light armour whether awake or asleep (an
; Assassin, Shinobi, Shadowblade, Poisoner or Spellarcher: kits.LIGHT_KITS, a thief's own limit
; kept after dual-classing) and item type DX is armour that isn't light (leather, or of no
; material; not a shield). All registers kept.
kit_light:
        push ax
        push bx
        push si
        push es
        mov si, light_kits
.kit:   cmp byte [cs:si], 0
        je .no
        cmp [cs:si], al
        je .type
        inc si
        jmp .kit
.type:  les bx, [ITEM_TYPES]
        imul ax, dx, 0x14
        add bx, ax
        test byte [es:bx + 0x0F], KT_ARMOUR
        jz .no
        test byte [es:bx], KT_SHIELD
        jnz .no
        mov al, [es:bx + 8]
        and al, 0x4F
        cmp al, LEATHER
        je .no
        cmp al, 0x40
        je .no
        stc
        jmp .out
.no:    clc
.out:   pop es
        pop si
        pop bx
        pop ax
        ret
light_kits db KIT_ASSASSIN, KIT_SHINOBI, KIT_SHADOWBLADE, KIT_POISONER, KIT_SPELLARCHER, 0

kit_forbids_one:                ; (AL the kit, KIT_WHERE its class's place)
        push ax
        push bx
        push cx
        push si
        push es
        mov cl, al              ; CL the kit, CH 1 for a half-giant with RULE_HALF_GIANT
        xor ch, ch
        cmp byte [es:bx + 0x18], HALF_GIANT
        jne .type
        test word [cs:rules], RULE_HALF_GIANT
        jz .type
        inc ch
.type:  call kit_class_of_sheet     ; (a ranger's sphere, for a Seeker: its class less 13)
        sub al, 13
        mov [cs:kf_sphere], al
        mov byte [cs:kf_chosen], 0      ; (a weapon of a kind it specialized in: the kit keeps
        cmp byte [cs:kf_spec], 0        ; it from none, but for the off hand's rules)
        jne .forbids
        call specs_awake                ; (its weapon specs counting: their class or kit awake)
        jc .forbids
        cmp dx, KIND_TYPES
        jae .forbids
        push si
        mov si, dx
        mov al, [cs:si + kind_of_type]
        pop si
        or al, al
        jz .forbids
        cmp [es:bx + SPEC_SLOTS], al
        je .chosen
        cmp [es:bx + SPEC_SLOTS + 1], al
        je .chosen
        cmp [es:bx + SPEC_SLOTS + 2], al
        je .chosen
        cmp [es:bx + SPEC_SLOTS + 3], al
        jne .forbids
.chosen:
        mov byte [cs:kf_chosen], 1
.forbids:
        les bx, [ITEM_TYPES]
        imul ax, dx, 0x14
        add bx, ax
        mov al, [es:bx]         ; AL the flags, AH the kind flags
        mov ah, [es:bx + 0x0F]
        cmp byte [cs:kf_off_hand], 0    ; the off hand: nothing for a Battle Mage, no weapon for a Healer
        je .ravager
        cmp cl, KIT_BATTLE_MAGE
        je .no
        cmp cl, KIT_HEALER
        jne .ravager
        test al, KT_MELEE | KT_MISSILE | KT_THROWN
        jnz .no
.ravager:
        cmp byte [cs:kf_chosen], 0
        jne .ok
        cmp cl, KIT_SHADOWBLADE ; a Shadowblade or Ghetto Fighter: no shield
        je .unshielded
        cmp cl, KIT_GHETTO
        jne .ravager_kit
.unshielded:
        test al, KT_SHIELD
        jnz .no
        jmp .ok
.ravager_kit:
        cmp cl, KIT_RAVAGER     ; a Ravager: no shield, no missile or thrown weapon, light armour only
        jne .twin
        test al, KT_SHIELD
        jnz .no
        test al, KT_MISSILE | KT_THROWN
        jnz .no
        jmp .light
.twin:  cmp cl, KIT_TWIN_BLADE
        jne .brute
        test al, KT_SHIELD
        jnz .no
        test al, KT_MELEE | KT_MISSILE
        jz .ok
        test ah, KT_TWO_HANDED
        jz .ok
        or ch, ch
        jnz .ok
        jmp .no
.brute: cmp cl, KIT_BRUTE
        jne .stalker
        test al, KT_SHIELD
        jz .melee
        or ch, ch
        jnz .ok
        jmp .no
.melee: test al, KT_MELEE
        jz .missile
        test ah, KT_TWO_HANDED
        jz .no
        jmp .ok
.missile:
        test al, KT_MISSILE
        jz .ok
        cmp byte [cs:kf_spec], 0
        jne .no
        jmp .ok
.stalker:
        cmp cl, KIT_STALKER
        jne .warden
.light: test ah, KT_ARMOUR
        jz .ok
        test al, KT_SHIELD
        jnz .ok
        mov al, [es:bx + 8]     ; (the material: leather, or none)
        and al, 0x4F
        cmp al, LEATHER
        je .ok
        cmp al, 0x40
        je .ok
        jmp .no
.warden:
        cmp cl, KIT_GROVE_WARDEN
        jne .lifebinder
        test al, KT_MELEE | KT_MISSILE
        jz .ok
        mov al, [es:bx + 8]
        and al, 0x4F
        cmp al, MATERIAL_METAL
        je .no
        jmp .ok
.lifebinder:
        cmp cl, KIT_SEEKER      ; a Seeker: its sphere's weapons (SPHERE_ALLOWS), but the bow
        jne .blunt
        test al, KT_MELEE | KT_MISSILE
        jz .ok
        cmp dx, KIND_TYPES
        jae .ok
        mov si, dx
        mov ah, [cs:si + kind_of_type]
        sub ah, 1
        jc .ok                  ; (no kind: as the game has it)
        cmp ah, BOW_KIND - 1
        je .ok
        mov [cs:cu_kind], ah
        mov [cs:cu_flags], al
        mov al, [es:bx + 8]     ; (the material, as CLASS_FORBIDS keeps it)
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
.blunt: mov si, kit_blunt
        cmp cl, KIT_LIFEBINDER
        je .kind
        mov si, kit_dancer      ; a Battle Dancer: the long sword and the bow only
        cmp cl, KIT_BATTLE_DANCER
        je .kind
        cmp cl, KIT_SHINOBI
        jne .ok
        test al, KT_SHIELD      ; a Shinobi: no shield, light armour, its own weapons
        jnz .no
        test ah, KT_ARMOUR
        jz .weapon
        mov al, [es:bx + 8]
        and al, 0x4F
        cmp al, LEATHER
        je .ok
        cmp al, 0x40
        je .ok
        jmp .no
.weapon:
        mov si, kit_shinobi
.kind:  cmp dx, KIND_TYPES      ; a weapon's kind in the mask at CS:SI (no kind: as the game has it)
        jae .ok
        push si
        mov si, dx
        movzx ax, byte [cs:si + kind_of_type]
        pop si
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
; KIT_ALLOWS: carry set if the kit of the character whose sheet is at ES:BX lets it use item type
; DX whatever its classes' lists and restrictions (kits.allows): a Battle Mage the weapons of its
; chosen weapon spec (SPEC_SLOTS' first, with RULE_SPECIALIZE) and light armour (leather, or of no
; material; not a shield); a Battle Dancer long swords and bows (kit_dancer), whatever its cleric's
; sphere. DS the game's; all registers kept.
kit_allows:
        push ax
        push bx
        push cx
        push si
        push es
        call kit_is_b
        db KIT_BATTLE_DANCER
        jne .mage
        cmp dx, KIND_TYPES
        jae .no
        mov si, dx
        movzx cx, byte [cs:si + kind_of_type]
        jcxz .no                ; (not a weapon of a kind)
        dec cx
        mov ax, [cs:kit_dancer]
        shr ax, cl
        test al, 1
        jnz .yes
        jmp .no
.mage:  call kit_is_b
        db KIT_BATTLE_MAGE
        jne .no
        mov cl, [es:bx + SPEC_SLOTS]
        les bx, [ITEM_TYPES]
        imul ax, dx, 0x14
        add bx, ax
        test byte [es:bx + 0x0F], KT_ARMOUR
        jz .weapon
        test byte [es:bx], KT_SHIELD
        jnz .no
        mov al, [es:bx + 8]
        and al, 0x4F
        cmp al, LEATHER
        je .yes
        cmp al, 0x40
        je .yes
        jmp .no
.weapon:
        test word [cs:rules], RULE_SPECIALIZE
        jz .no
        cmp dx, KIND_TYPES
        jae .no
        mov si, dx
        mov al, [cs:si + kind_of_type]
        or al, al
        jz .no
        cmp al, cl
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

kit_blunt  dw KIT_BLUNT
kit_dancer dw 0x2001           ; bits by kind: the long sword, the bow (a Battle Dancer's)
kit_shinobi dw 0xF10C           ; bits by kind: dagger, short sword, quarterstaff, chatkcha, bow, sling,
                                ;   staff sling
kf_spec    db 0
kf_off_hand db 0               ; (KIT_FORBIDS: the item going to the off hand)
kf_sphere  db 0                 ; (KIT_FORBIDS: a ranger's sphere, 0 air to 3 water)
kf_chosen  db 0                 ; (KIT_FORBIDS: a weapon of a kind it specialized in)
EQUIP_OFF_HAND equ 14          ; the equip routine's slot for the off (left) hand

; CLASS_FORBIDS: carry set if the classes of the character whose sheet is at ES:BX keep it from
; item type DX (dsloader/restrict.py, which says why): a psionicist, a thief (light armour, but
; a multiclass one, or a human thief once a warrior, as its other class allows: CU_DUAL; a
; multiclass one its shields too), a preserver of that class alone (or a human once a warrior),
; a druid, a cleric. A human's first class alone holds it (the one it has now, if it has changed
; class); another race's every class. All registers kept.
RESTRICT_TYPE equ 0x14          ; (the item type record's size)
NO_MATERIAL equ 0xFF            ; (CU_MAT: none)
LEATHER equ 5
THIEF_BIT equ 0x400
PSI_KINDS equ 0x701E            ; bits by kind: club, dagger, short sword, mace, chatkcha, bow, sling
SPHERE_EARTH equ 0x1D           ; bits by material: stone, obsidian, metal, wood
SPHERE_FIRE equ 0x08            ; obsidian
SPHERE_WATER equ 0x03           ; bone, wood
class_forbids:
        push ax
        push bx
        push cx
        push dx
        push si
        push di
        push ds
        mov ax, dx
        imul ax, ax, RESTRICT_TYPE
        lds si, [0x1669]
        add si, ax
        mov al, [si]                    ; the flags: 1 melee, 2 missile, 4 shield, 10h thrown
        mov [cs:cu_flags], al
        mov al, [si + 8]                ; the material (its low nibble; 40h and 0 none)
        mov ah, al
        and al, 0x0F
        jnz .mat
        test ah, 0x40
        jz .mat
        mov al, NO_MATERIAL
.mat:   mov [cs:cu_mat], al
        xor al, al                      ; armour: +0Fh 80h, and not a shield (nor bracers, nor
        push ax                         ;   a cloak of protection: worn as a cloak, +09h 8)
        mov ax, dx
        call bracers_ax
        pop ax
        je .armour
        cmp byte [si + 9], 8
        je .armour
        test byte [si + 0x0F], 0x80
        jz .armour
        test byte [cs:cu_flags], 4
        jnz .armour
        inc ax
.armour:
        mov [cs:cu_armour], al
        mov ax, [si + 0x10]             ; the classes but thief that may use it
        and ax, [es:bx + 0x12]
        and ax, 0xFFFF - THIEF_BIT
        mov [cs:cu_others], ax
        mov byte [cs:cu_kind], 0xFF     ; a weapon's kind (0FFh none)
        test byte [cs:cu_flags], 3
        jz .kind
        cmp dx, KIND_TYPES
        jae .kind
        mov si, dx
        mov al, [cs:si + kind_of_type]
        dec al
        mov [cs:cu_kind], al
.kind:  pop ds
        call specialized_back   ; (a dual-classed warrior's own kinds: as the game has them)
        jnc .holds0
        mov byte [cs:cu_kind], 0xFF
.holds0:
        call dual_warrior       ; (CU_DUAL: a human thief or preserver now, a warrior before)
        mov cx, 3                       ; CL the classes that hold, CH more than one (not human)
        cmp byte [es:bx + 0x18], 1
        jne .multi
        mov cl, 1
        jmp .holds
.multi: cmp byte [es:bx + 0x22], 0
        je .holds
        inc ch
.holds: xor di, di
.each:  mov al, [es:bx + di + 0x21]
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
.out:   pop di
        pop si
        pop dx
        pop cx
        pop bx
        pop ax
        ret

; SPECS_AWAKE: CF clear if the weapon specs of the character (sheet ES:BX) count: one class, or not
; a human; a human's warrior class (fighter, gladiator, ranger) now, or before and passed by the
; class it has now; a Battle Mage's kit awake (KIT_IS). Set while the class or kit that gave them
; sleeps. All registers kept.
specs_awake:
        pusha
        cmp byte [es:bx + 0x22], 0
        je .yes
        cmp byte [es:bx + 0x18], 1
        jne .yes
        xor si, si
.class: mov al, [es:bx + si + 0x21]
        cmp al, FIGHTER_CLASS
        je .warrior
        cmp al, GLADIATOR_CLASS
        je .warrior
        cmp al, 13
        jb .next
        cmp al, 16
        ja .next
.warrior:
        or si, si
        jz .yes
        mov al, [es:bx + si + 0x24]
        cmp al, [es:bx + 0x24]
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

; SPECIALIZED_BACK: carry set if CU_KIND is a kind the character (sheet ES:BX) specialized in as a
; fighter, gladiator or ranger, a human who has dual-classed and whose new class's level has
; passed the old; or the bow, for a ranger (a multiclass one always, a human while a ranger or
; once its new class's level has passed its ranger level): restrict.specialized_back. All
; registers kept.
specialized_back:
        pusha
        mov al, [cs:cu_kind]
        cmp al, 0xFF
        je .no
        cmp al, BOW_KIND - 1
        jne .spec
        xor si, si                      ; (the bow: a ranger's own)
.rclass:
        mov al, [es:bx + si + 0x21]
        cmp al, 13
        jb .rnext
        cmp al, 16
        ja .rnext
        cmp byte [es:bx + 0x18], 1      ; (not human: multiclass, always)
        jne .yes
        or si, si                       ; (a human ranger now)
        jz .yes
        mov al, [es:bx + si + 0x24]
        cmp al, [es:bx + 0x24]
        jb .yes
.rnext: inc si
        cmp si, 3
        jb .rclass
        mov al, [cs:cu_kind]
.spec:  cmp byte [es:bx + 0x18], 1
        jne .no
        inc al
        cmp [es:bx + SPEC_SLOTS], al
        je .kind
        cmp [es:bx + SPEC_SLOTS + 1], al
        je .kind
        cmp [es:bx + SPEC_SLOTS + 2], al
        je .kind
        cmp [es:bx + SPEC_SLOTS + 3], al
        jne .no
.kind:  mov si, 1
.class: mov al, [es:bx + si + 0x21]
        cmp al, FIGHTER_CLASS
        je .warrior
        cmp al, GLADIATOR_CLASS
        je .warrior
        cmp al, 13
        jb .next
        cmp al, 16
        ja .next
.warrior:
        mov al, [es:bx + si + 0x24]
        cmp al, [es:bx + 0x24]
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
        call heavy
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
.thief: cmp al, 17
        jne .pres
        call heavy                      ; (a thief: light armour only, but a multiclass one, or a
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
.pres:  cmp al, 11
        jne .druid
        or ch, ch
        jnz .ok
        cmp byte [cs:cu_dual], 0        ; (a human once a warrior: as a multiclass one, no spells
        jne .ok                         ;   in armour: PROBE_NO_CAST)
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
        mov al, [es:bx + si + 0x21]     ; a cleric's or ranger's sphere: its class less 1 (13 a ranger's), mod 4
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
        call el_second          ; (an Elementalist's second sphere's too)
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
        cmp byte [es:bx + 0x18], 1
        jne .out
        mov cl, [es:bx + 0x21]
        cmp cl, 17
        je .was
        cmp cl, 11
        jne .out
.was:   mov al, [es:bx + 0x22]
        call .before
        jc .yes
        mov al, [es:bx + 0x23]
        call .before
        jnc .out
.yes:   mov byte [cs:cu_dual], 1
.out:   pop cx
        pop ax
        ret
.before:                        ; (carry set: class AL a warrior, or a cleric for a thief, CL, now)
        call warrior_al
        jc .ret
        cmp cl, 17
        jne .no
        cmp al, 1
        jb .no
        cmp al, 4
        ja .no
        stc
        ret
.no:    clc
.ret:   ret
cu_dual db 0

; WARRIOR_AL: carry set if class AL is a fighter, gladiator or ranger. All registers kept.
warrior_al:
        cmp al, FIGHTER_CLASS
        je .yes
        cmp al, GLADIATOR_CLASS
        je .yes
        cmp al, 13
        jb .no
        cmp al, 16
        ja .no
.yes:   stc
        ret
.no:    clc
        ret

; CLASS_AND_WARRIOR: carry set if the character (sheet ES:BX) has class AL and a warrior class
; (WARRIOR_AL) among its classes. All registers kept.
class_and_warrior:
        push si
        push cx
        xor cx, cx                      ; CL class AL found, CH a warrior
        xor si, si
.each:  cmp [es:bx + si + 0x21], al
        jne .war
        mov cl, 1
.war:   push ax
        mov al, [es:bx + si + 0x21]
        call warrior_al
        pop ax
        jnc .next
        mov ch, 1
.next:  inc si
        cmp si, 3
        jb .each
        and cl, ch
        cmp cl, 1                       ; (CF set if CL < 1)
        cmc
        pop cx
        pop si
        ret

; HEAVY: carry set for armour not light (not leather, and of a material)
heavy:  cmp byte [cs:cu_armour], 0
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
; air, missile and thrown weapons and daggers; the others by material.
sphere_allows:
        push cx
        or al, al
        jnz .mat
        test byte [cs:cu_flags], 0x12
        jnz .yes
        cmp byte [cs:cu_kind], 2        ; (a dagger)
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

; BRACERS_AX: ZF set if AX is the bracers of defense's type (TYPES_FIRST + BRACERS, once the
; types are in) or the robes' (+ ROBE): worn where armour is, their plus counting for AC, but
; not armour. All registers kept.
bracers_ax:
        push bx
        mov bx, [cs:types_first]
        or bx, bx
        jz .no
        add bx, BRACERS
        cmp ax, bx
        je .yes
        add bx, ROBE - BRACERS
        cmp ax, bx
.yes:   pop bx
        ret
.no:    inc bx                  ; (ZF clear)
        pop bx
        ret

; ROBE_PLUS: AX the plus of the robe creature AX wears (on the chest: TYPES_FIRST + ROBE), 0 for
; none: 1 the Ashen Robe, 2 the Veiled Robe (dsloader/robes.py). DS the game's; others kept.
robe_plus:
        push bx
        push cx
        push dx
        push si
        push di
        push es
        mov bx, ds
        add bx, THINGS_SEG
        mov [cs:r_things], bx
        mov bx, [cs:types_first]
        or bx, bx
        jz .none
        add bx, ROBE
        mov [cs:ws_type], bx
        mov word [cs:ws_slot], CHEST_SLOT
        call worn_scan
        mov ax, [cs:ws_plus]
        cmp word [cs:ws_count], 0
        jne .out
.none:  xor ax, ax
.out:   pop es
        pop di
        pop si
        pop dx
        pop cx
        pop bx
        ret
cu_kind    db 0
cu_others  dw 0

; PROBE_NO_CAST: INT VEC_NO_CAST replaces "add sp,4" (3 bytes: INT + NOP; DSUN.EXE 89B84h) at the
; end of the game's test of whether a character can't cast spells, which the USE screen asks
; before it shows a spell as one to cast and before it casts one, wizard or priest (not a
; psionic power), and so does a spell queued in a fight: the character the test's first argument
; (the "push dx" before its call, under the interrupt frame: DX itself is the test's to change,
; and was, so the check once looked at someone else), AX not 0 if it can't (its "No spell use"
; effect). With RULE_RESTRICT, a multiclass preserver can't either while it wears armour, a helm
; too (ARMOUR_WORN; a shield doesn't count); nor can a human who has been a preserver and a
; fighter, gladiator or ranger, in either order (CLASS_AND_WARRIOR).
PRESERVER_CLASS equ 11
probe_no_cast:
        push bp                 ; the replaced "add sp,4": move the interrupt frame (and BP)
        mov bp, sp              ; up over the 4 bytes, so IRET returns with them gone
        push ax
        mov ax, [bp + 8]        ; (the test's first argument: the character)
        mov [cs:nc_who], ax
        mov ax, [bp + 6]
        mov [bp + 10], ax       ; flags
        mov ax, [bp + 4]
        mov [bp + 8], ax        ; CS
        mov ax, [bp + 2]
        mov [bp + 6], ax        ; IP
        mov ax, [bp]
        mov [bp + 4], ax        ; BP
        pop ax
        mov sp, bp
        add sp, 4
        pop bp
        or ax, ax
        jnz .done
        test word [cs:rules], RULE_RESTRICT
        jz .done
        push bx
        push cx
        push dx
        push es
        mov dx, [cs:nc_who]
        mov bx, dx
        imul bx, bx, 0x47
        les cx, [0x1661]
        add bx, cx
        cmp byte [es:bx + 0x18], 1      ; a human: a preserver and a warrior, dual-classed
        jne .multi
        mov al, PRESERVER_CLASS
        call class_and_warrior
        mov ax, 0
        jc .pres
        jmp .out
.multi: cmp byte [es:bx + 0x22], 0      ; one class: none
        je .out
        cmp byte [es:bx + 0x21], PRESERVER_CLASS
        je .pres
        cmp byte [es:bx + 0x22], PRESERVER_CLASS
        je .pres
        cmp byte [es:bx + 0x23], PRESERVER_CLASS
        jne .out
.pres:  call armour_worn
        adc ax, 0                       ; (AX was 0)
.out:   pop es
        pop dx
        pop cx
        pop bx
.done:  iret
nc_who  dw 0                            ; (the character the test was asked about)

; ARMOUR_WORN: carry set if creature DX (DS = the game's) wears armour, a helm too: an item of
; a type the game marks armour (+0Fh 80h), not a shield, on its arms, legs, head or chest.
; HEAVY_WORN: the same for armour that isn't light (not leather, and of a material, as KIT_ALLOWS
; has it). All registers kept.
heavy_worn:
        mov byte [cs:aw_heavy], 1
        call armour_worn
        mov byte [cs:aw_heavy], 0
        ret
aw_heavy db 0
armour_worn:
        pushad
        push es
        mov ax, ds
        add ax, THINGS_SEG
        mov [cs:r_things], ax
        imul ax, dx, 0x3A
        mov [cs:r_creature], ax
        mov cx, 8               ; its item lists, each a thing: +8, +0Ah, +0Ch
.list:  les bx, [CREATURES]
        add bx, [cs:r_creature]
        add bx, cx
        mov dx, [es:bx]
        cmp dx, NO_THING
        jae .next
        mov es, [cs:r_things]
        mov bx, dx
        imul bx, bx, 3
        cmp byte [es:bx+THINGS], 1
        jne .next               ; not an item
        mov dx, [es:bx+THINGS+1]
        mov byte [cs:r_left], 100
.item:  cmp dx, NO_THING
        jae .next
        les bx, [ITEMS]
        imul ax, dx, 0x15
        add bx, ax
        mov dx, [es:bx+4]       ; (the next)
        mov al, [es:bx+0x11]    ; the slot
        cmp al, ARM_SLOT
        je .slot
        cmp al, LEG_SLOT
        je .slot
        cmp al, HEAD_SLOT
        je .slot
        cmp al, CHEST_SLOT
        jne .on
.slot:  mov si, [es:bx+0x0A]
        push ax
        mov ax, si
        call bracers_ax                 ; (bracers aren't armour)
        pop ax
        je .on
        imul si, si, 0x14
        les bx, [ITEM_TYPES]
        add bx, si
        test byte [es:bx], 4    ; a shield
        jnz .on
        test byte [es:bx+0x0F], 0x80
        jz .on
        cmp byte [cs:aw_heavy], 0
        je .worn
        mov al, [es:bx+8]       ; (light: leather, or of no material)
        and al, 0x4F
        cmp al, LEATHER
        je .on
        cmp al, 0x40
        je .on
.worn:  pop es
        popad
        stc
        ret
.on:    dec byte [cs:r_left]
        jnz .item
.next:  add cx, 2
        cmp cx, 0x0E
        jb .list
        pop es
        popad
        clc
        ret

; Weapon pages in the character creation panel (RULE_SPECIALIZE; dsloader/weaponpages.py, which
; puts the windows and their pictures in the Loader's RESOURCE.GFF). The panel shows the psionic
; disciplines' window (3012, DS:EA2h its window) or the clerical spheres' (3013, DS:EA6h), which
; the game swaps through its routines at DSUN.EXE 640E4h (to the spheres) and 641B9h (back). For a
; fighter, gladiator or ranger it gets windows with WEAPON SPEC for its button (3018 for the
; disciplines if it has no sphere, 3019 for the spheres), and that opens the four weapon pages
; (3014-3017; kept at DS:EA6h, as the spheres' window is, so that the game closes it as one),
; each four kinds (specialize.KINDS), MORE SPECS to the next, the last's VIEW PSIONICS back.
; The kind marked is the creation sheet's (DS:119Ch) first SPEC_SLOTS byte, which goes with the
; sheet when DONE is pressed (the Loader puts in the long sword for a warrior who marks none).
; PROBE_WP_DISC_WIN: INT replaces "push 0BC4h" (3 bytes: INT + NOP; 67BFBh), the disciplines'
; window being opened: pushes 3018's id instead for a warrior with no sphere.
; PROBE_WP_SPHERE_WIN: INT replaces "push 0BC5h" (6413Bh), the spheres' window being opened:
; 3019's id instead for a warrior.
; PROBE_WP_SHOWN: INT replaces "cmp ax,8" (3 bytes: INT + NOP; 6337Ah) where a new class has been
; picked and the game asks whether the spheres' window is up (AX 8 if it is, from the routine it
; has just called, 118:C36h, with the window's id) to close it: 8 too if a warrior's spheres or a
; weapon page is up. RETF 2 keeps the compare's flags.
; PROBE_WP_DISC_CLICK, PROBE_WP_SPHERE_CLICK: INT replaces "mov bx,[bp+8]" (3 bytes: INT + NOP;
; 64311h, 642B0h) in those windows' click routines, [BP+8] the button: WEAPON SPEC opens the
; first page, and the routine goes on at its end (6433Fh, 642E2h: the redraw). Both read
; the far addresses of the game's window routines from the calls in their own overlay, as the
; loader has fixed them (WP_CALLS), for WP_HANDLER to call.
WP_DISC_ID   equ 0xBC4              ; (windows' ids: 3012, 3013, 3014-3017, 3018, 3019)
WP_SPHERE_ID equ 0xBC5
WP_PAGE_ID   equ 0xBC6
WP_WDISC_ID  equ 0xBCA
WP_WSPHERE_ID equ 0xBCB
WP_ROW       equ 0x840              ; (buttons: the kinds' rows, MORE SPECS, VIEW PSIONICS, WEAPON SPEC)
WP_MORE      equ 0x850
WP_BACK      equ 0x851
WP_VIEW      equ 0x852
WP_PAGES     equ 4
SPHERE_TOGGLE equ 0x7FF             ; (the spheres' VIEW PSIONICS)
; Kits (RULE_HI_KITS; kitpages.py): one class's three, or none, chosen on a page of their own
; (3026-3033, by class, kept at DS:EA6h as the weapon pages are), its rows NO KIT and the
; class's kits (KIT_ROW + 3 * (class - 1) + kit - 1), its button VIEW PSIONICS back. KITS opens it:
; the button of the disciplines' window (3022) for a class with no sphere, of the spheres' (3023)
; for a cleric's, druid's or ranger's, of the fourth weapon page (3025) for a warrior choosing
; weapons. The kit marked is the creation sheet's KIT_BYTE (0 none, 1-3), which goes with the
; sheet when DONE is pressed. The game keeps that sheet from one character to
; the next: the disciplines' window opened other than on the way back to it (KIT_KEEP), for a
; new character or another class, puts the kit back to none.
KIT_DISC_ID  equ 3022
KIT_SPHERE_ID equ 3023
KIT_PAGE4_ID equ 3025
KIT_WIN_ID   equ 3026
KIT_ROW      equ 0x870
KIT_NONE     equ 0x888
KIT_VIEW     equ 0x889
KIT_BYTE     equ 0x43
KIT_OPEN     equ 0xFF               ; (KIT_BYTE while the player has taken the kit back: none chosen)
; The kits as KIT_IS numbers them (the creation screen's class x 4 + the kit)
KIT_ELEMENTALIST equ 5
KIT_HEALER   equ 6
KIT_CRUSADER equ 7
KIT_GROVE_WARDEN equ 9
KIT_LIFEBINDER equ 10
KIT_WANDERER equ 11
KIT_MYRMIDON equ 13
KIT_SENTINEL equ 14
KIT_RAVAGER  equ 15
KIT_CHAMPION equ 17
KIT_TWIN_BLADE equ 18
KIT_BRUTE    equ 19
KIT_SCHOLAR  equ 21
KIT_BATTLE_MAGE equ 22
KIT_ARCANIST equ 23
KIT_MIND_BENDER equ 25
KIT_MIND_WARRIOR equ 26
KIT_KINETICIST equ 27
KIT_STALKER  equ 29
KIT_JUSTIFIER equ 30
KIT_SEEKER   equ 31
KIT_SWASHBUCKLER equ 33
KIT_ASSASSIN equ 34
KIT_SHINOBI  equ 35
; the multiclass kits (kitpages.MULTI): their groups, 9-13, numbered on from the classes, and the kits
; (KIT_IS's numbers) as a class's
MULTI_FIRST  equ 9
KIT_GROUPS   equ 19             ; (the classes' and the multiclass groups' pages)
MULTI_ROW    equ 0x88A          ; (a group's rows: + 3 * (group - 9) + kit - 1)
KIT_BATTLE_DANCER equ 37
KIT_SHADOWBLADE equ 41
KIT_SCOUT    equ 42
KIT_AVENGER  equ 45
KIT_RESCUER  equ 49
KIT_GHETTO   equ 53
KIT_WAYFINDER equ 54
KIT_SPELLARCHER equ 57
KIT_TITAN_MIND equ 61
KIT_POISONER equ 65
KIT_SPIRIT_CALLER equ 69
KIT_WASTE_SEER equ 73
KIT_WILD_FURY equ 77
WP_DISC      equ 0xEA2              ; DS: the panel's windows (far)
WP_SPHERE    equ 0xEA6
WP_DISC_MASK equ 0x4980             ; DS: the disciplines and spheres marked, kept while hidden
WP_SPHERE_MASK equ 0x4982
WP_CREATION  equ 0x119C             ; DS: the sheet being made (far; its classes numbered 1-8)
WP_STUB      equ 0x421D - 0x4356    ; the creation overlay's stub, less DS: its entries
WP_MARKED    equ 0x66               ; (63EFAh: the rows marked, as a mask)
WP_TO_DISC   equ 0x7A               ; (641B9h: back to the disciplines)
WP_X         equ 0xD2               ; (the panel's place)
WP_Y         equ 0x58
CR_CLERIC    equ 1                  ; (classes at creation)
CR_DRUID     equ 2
CR_FIGHTER   equ 3
CR_GLADIATOR equ 4
CR_RANGER    equ 7
; WP_CALLS: the routines' far calls (9Ah) in the overlay, back from the click probes' return
; (the overlay's 642B3h and 64314h; the calls at 64127h close, 6413Eh open, 6416Fh print,
; 6417Dh set the text colour, 641AFh the panel's help line, 6422Fh set a button, 642E2h redraw)
WP_CALL_CLOSE  equ 0x64127
WP_CALL_OPEN   equ 0x6413E
WP_CALL_PRINT  equ 0x6416F
WP_CALL_COLOUR equ 0x6417D
WP_CALL_HELP   equ 0x641AF
WP_CALL_BUTTON equ 0x6422F
WP_CALL_REDRAW equ 0x642E2
WP_CALL_MARK   equ 0x63FC4          ; (the row's mark: A0:3180h, as 63FEEh draws it)
WP_CALL_BACKDROP equ 0x639E9        ; (a number's backdrop put back: A0:30C3h, as 639D5h shows the PSP)
WP_STAT_SEG    equ 0x639D5          ; ("mov ax,340h": the backdrops' words' segment)
WP_MARK_SEG    equ 0x63FB2          ; ("mov ax,338h": the marks' table's segment, +1ABh)
WP_MARK_WIN    equ 0xF32            ; DS: the window the marks are drawn through (far)
WP_SPHERE_SEG  equ 0x6412F          ; ("push 538h": the spheres' routine's stub segment, as fixed)
WP_SPHERE_ENTRY equ 0x57            ; (its entry there)
WP_SPHERE_RET  equ 0x642B2          ; (the click probes' return, and where they go on to)
WP_SPHERE_END  equ 0x642E2
WP_DISC_RET    equ 0x64313
WP_DISC_END    equ 0x6433F
WP_SHOWN_CALL  equ 0x63372          ; (118:C36h's call, and PROBE_WP_SHOWN's return)
WP_SHOWN_RET   equ 0x6337C

probe_wp_disc_win:
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
        cmp byte [cs:kit_keep], 0   ; (opened for a new character, or another class: no kit, and
        jne .keep                   ;   no weapon spec until one is chosen: WP_MARKS's default)
        push es
        push bx
        les bx, [WP_CREATION]
        mov byte [es:bx + KIT_BYTE], 0
        mov dword [es:bx + SPEC_SLOTS], 0
        pop bx
        pop es
.keep:  mov byte [cs:kit_keep], 0
        pop ax
        pop bp
        iret

probe_wp_sphere_win:
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

; WP_IDS: the windows the panel shows for the sheet being made (kitpages.panel_windows): AX the
; disciplines' (3012, its button VIEW SPHERES; 3018, WEAPON SPEC, for a warrior with no sphere
; and weapon specialization; 3022, KITS, for one of no sphere with kits to choose), DX the
; spheres' (3013, VIEW PSIONICS; 3019, WEAPON SPEC, for a warrior and weapon specialization;
; 3023, KITS, for one with kits to choose). Others kept.
wp_ids:
        push bx
        push cx
        call wp_classes
        mov cx, ax              ; CL a warrior, CH a sphere
        call kit_class
        mov bl, al
        mov ax, WP_DISC_ID
        mov dx, WP_SPHERE_ID
        test word [cs:rules], RULE_SPECIALIZE
        jz .kits
        or cl, cl
        jz .kits
        mov dx, WP_WSPHERE_ID
        or ch, ch
        jnz .out
        mov ax, WP_WDISC_ID
        jmp .out
.kits:  or bl, bl
        jz .out
        mov dx, KIT_SPHERE_ID
        or ch, ch
        jnz .out
        mov ax, KIT_DISC_ID
.out:   pop cx
        pop bx
        ret

; KIT_CLASS: AL the class of the sheet being made (1-8, as the creation screen numbers them) if it
; has kits to choose (the rule on, and one class), or its multiclass group (9-13: MULTI_GROUP_CR) for
; two classes at once, else 0. Others kept.
kit_class:
        push bx
        push es
        xor al, al
        test word [cs:rules_hi], RULE_HI_KITS
        jz .out
        les bx, [WP_CREATION]
        cmp word [es:bx + 0x22], 0
        jne .multi
        mov al, [es:bx + 0x21]
        cmp al, 8
        jbe .out
        xor al, al
        jmp .out
.multi: call multi_group_cr
.out:   pop es
        pop bx
        ret

; MULTI_GROUP: AL the multiclass group (9-13, kitpages.MULTI) of sheet ES:BX, its classes 1-17
; (KIT_CLASS_OF); MULTI_GROUP_CR the same for the sheet being made, its classes 1-8: two classes at
; once (none at +23h), not a human's, its race and their pair one of MULTI_TABLE's; 0 for none.
; Others kept.
multi_group:
        push si
        mov si, kit_class_of
        jmp multi_find
multi_group_cr:
        push si
        mov si, multi_same
multi_find:
        push cx
        push dx
        push di
        xor al, al
        xor dx, dx              ; DX the pair's bits (1 shl the creation class)
        cmp byte [es:bx + 0x18], 1
        je .out
        cmp byte [es:bx + 0x23], 0
        jne .out
        mov di, 0x21
.class: movzx cx, byte [es:bx + di]
        dec cx
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
        cmp di, 0x23
        jb .class
        mov ch, [es:bx + 0x18]
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
; (race, the pair's bits) by group from 9; then each group's kits, how many
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
            dw (1 << 2) | (1 << 3)      ; thri-kreen druid/fighter: Wasteland Seer
            db 7
            dw (1 << 2) | (1 << 3)      ; mul druid/fighter: Wild Fury
            db 0
multi_count db 1, 2, 1, 1, 2, 1, 1, 1, 1, 1, 1
km_rows     db 4                ; (KIT_MARKS: the page's rows)
multi_same  db 1, 2, 3, 4, 5, 6, 7, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0   ; (the sheet being made's classes)

; WP_RULES: ZF clear if weapon specialization or kits are on (the panel's own windows wanted).
; All registers kept.
wp_rules:
        test word [cs:rules], RULE_SPECIALIZE
        jnz .ret
        test word [cs:rules_hi], RULE_HI_KITS
.ret:   ret

; WP_ALLOWED: AX the kinds (bit 0 the long sword) the sheet being made can choose: those whose
; plain weapon (WP_PLAIN) the game's class lists and CLASS_FORBIDS let it use, its classes as the
; sheet numbers them (a cleric's or ranger's by the sphere marked). restrict.allowed_kinds.
wp_allowed:
        push bx
        push cx
        push dx
        push si
        push di
        push es
        les bx, [WP_CREATION]
        push ds
        push cs
        pop ds
        mov di, wp_sheet
        mov cx, 0x47 / 2 + 1
        xor ax, ax
.zero:  mov [di], ax
        add di, 2
        loop .zero
        pop ds
        mov al, [es:bx + 0x18]
        mov [cs:wp_sheet + 0x18], al
        xor si, si
        xor dx, dx              ; DX the class flags
.class: mov al, [es:bx + si + 0x24]
        mov [cs:wp_sheet + si + 0x24], al
        movzx di, byte [es:bx + si + 0x21]
        cmp di, 8
        ja .next
        shl di, 2
        mov al, [cs:di + wp_class_map]
        mov cx, [cs:di + wp_class_map + 2]
        cmp byte [cs:di + wp_class_map + 1], 0  ; (a sphere to add: 0-3 by the mark)
        je .put
        mov ah, 0x80
.sphere:
        test [WP_SPHERE_MASK], ah
        jnz .put
        inc al
        shl cx, 1
        shr ah, 1
        cmp ah, 0x08
        ja .sphere
        sub al, 4               ; (none marked: the first)
        shr cx, 4
.put:   mov [cs:wp_sheet + si + 0x21], al
        cmp byte [cs:di + wp_class_map + 1], 2  ; (a ranger's sphere doesn't change its flag)
        jne .flag
        mov cx, 0x200
.flag:  or dx, cx
.next:  inc si
        cmp si, 3
        jb .class
        mov [cs:wp_sheet + 0x12], dx
        mov al, [es:bx + KIT_BYTE]          ; (its kit: what it keeps the sheet from)
        mov [cs:wp_sheet + KIT_BYTE], al
        mov al, [es:bx + SPHERE2]           ; (an Elementalist's second sphere)
        mov [cs:wp_sheet + SPHERE2], al
        push cs
        pop es
        mov bx, wp_sheet
        call kinds_allowed
        pop es
        pop di
        pop si
        pop dx
        pop cx
        pop bx
        ret

; KINDS_ALLOWED: AX the kinds (bit 0 the long sword) the character whose sheet is at ES:BX can
; choose: those with an item type (KIND_OF_TYPE) the game's class lists and CLASS_FORBIDS let it
; use (a fire cleric's long sword the obsidian one, not the plain bone one); not the bow for a
; ranger (its class flags, +12h: 200h), who has expertise with it already; a Battle Mage the
; one-handed melee kinds (KIT_BM_KINDS), not thrown, whatever its class lets it use; a Spellarcher
; the bow only; a kind KIT_ALLOWS lets it use whatever its classes (a Battle Dancer's long sword).
; DS = the game's. Others kept.
KIT_BM_KINDS equ 0x00BF         ; a Battle Mage's: long sword, club, dagger, short sword, mace, axe, pick
kinds_allowed:
        push cx
        push dx
        push si
        push di
        call kit_is_b             ; (a Battle Mage: its own, whatever its class)
        db KIT_BATTLE_MAGE
        jne .archer
        mov di, KIT_BM_KINDS
        jmp .all
.archer:
        call kit_is_b             ; (a Spellarcher: the bow only)
        db KIT_SPELLARCHER
        jne .types
        mov di, 1 << (BOW_KIND - 1)
        jmp .all
.types: xor dx, dx              ; DX each item type of a kind, CL its kind
        xor di, di
.type:  mov si, dx
        mov cl, [cs:si + kind_of_type]
        sub cl, 1
        jc .no
        bt di, cx
        jc .no                  ; (one of its types already let in)
        call kit_allows         ; (a Battle Dancer's long sword, whatever its cleric's sphere)
        jc .let
        push es
        push bx
        imul ax, dx, 0x14
        les bx, [0x1669]
        add bx, ax
        mov ax, [es:bx + 0x10]
        pop bx
        pop es
        and ax, [es:bx + 0x12]
        jz .no
        call class_forbids
        jc .no
        mov byte [cs:kf_spec], 1
        call kit_forbids
        jc .no
.let:   movzx cx, cl
        bts di, cx
.no:    inc dx
        cmp dx, KIND_TYPES
        jb .type
        test word [es:bx + 0x12], 0x200
        jz .all                 ; (a ranger)
        btr di, BOW_KIND - 1
.all:   mov ax, di
        pop di
        pop si
        pop dx
        pop cx
        ret

; PROBE_LV_PICK: INT VEC_LV_PICK replaces "cmp word [bp+8],0Bh" (4 bytes: INT + 2 NOPs, then the
; game's "jnz +7"; DSUN.EXE 87A9Bh) in the routine that raises a character a level in a class
; ([BP+8] the class, SI the character), where it goes on to have a preserver pick a new spell and a
; psionicist a new power. With weapon specialization, a fighter, gladiator or ranger with fewer
; weapon kinds than it is due (LV_DUE: a gladiator two, a third at 6th level and a fourth at 9th;
; a fighter or ranger one) picks the rest the way a psionicist picks a power: the game's own
; routine for that (its far call a little further on, 620:57h) is called in weapon mode (LV_MODE),
; in which the PROBE_PK_* probes in it show the weapon window (weaponpages.PICKER) in place of the
; powers' and take its clicks. Then on as the compare and the JNZ would have gone. The level-up
; routine is overlay code: the way back is put in a frame the overlay manager can fix up, as for
; PROBE_USE_ITEM.
LV_SHEETS   equ 0x1661          ; DS: the sheets (far, 47h bytes each) and creatures (3Ah each)
LV_PARTY    equ 4
LV_PSI_CALL equ 0x87AB0 - 0x87A9D  ; the psionicists' pop-up's far call's address, less the INT's
LV_SPELL_CALL equ 0x87AA3 - 0x87A9D ; the preservers' CHOOSE A SPELL's (620:5Ch), as that
LV_THIEF    equ 17
probe_lv_pick:
        sti
        pushad
        push es
        mov bx, sp              ; the interrupt frame at BX+34: IP, CS, flags
        push ds
        push si
        lds si, [ss:bx + 34]
        mov eax, [si + LV_PSI_CALL]
        mov [cs:lv_psi], eax
        mov eax, [si + LV_SPELL_CALL]
        mov [cs:lv_spell], eax
        pop si
        pop ds
        mov ax, [ss:bx + 34]
        add ax, 4               ; past the NOPs and the JNZ for a preserver (and a Shinobi) ...
        mov byte [cs:lv_class], 0x0B
        cmp word [bp + 8], 0x0B
        je .frame
        mov byte [cs:lv_class], 0
        cmp word [bp + 8], LV_THIEF
        jne .other
        call lv_shinobi
        je .frame
.other: add ax, 7               ; ... and to its target for any other class
.frame: push word [ss:bx + 36]
        push ax
        push bp
        mov bp, sp
        call lv_check
        cmp byte [cs:lv_class], 0x0B
        jne .scholar_done
        call lv_scholar
.scholar_done:
        pop bp
        pop ax                  ; the way back, as the overlay manager has left it
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
        pop es
        popad
        iret

; Character SI (DS the game's) asked for weapon kinds while it has fewer than it is due
lv_check:
        test word [cs:rules], RULE_SPECIALIZE
        jz .ret
        cmp si, LV_PARTY
        jae .ret
        cmp byte [cs:showing], 0
        jne .ret
        les bx, [LV_SHEETS]
        imul ax, si, 0x47
        add bx, ax
        call lv_due
        xor dx, dx              ; DX the kinds it has, DI the first slot empty
        mov di, SPEC_COUNT
        push si
        mov si, SPEC_COUNT - 1
.have:  movzx ax, byte [es:bx + si + SPEC_SLOTS]
        or ax, ax
        jnz .has
        mov di, si
        jmp .next
.has:   inc dx
.next:  dec si
        jns .have
        pop si
        cmp dx, cx
        jae .ret
        cmp di, SPEC_COUNT
        jae .ret
        mov [cs:lv_have], dl
        sub cl, dl              ; (the kinds due less those it has: those left)
        mov [cs:lv_left], cl
        call kinds_allowed
        push si
        xor si, si              ; less those it has
.mine:  movzx cx, byte [es:bx + si + SPEC_SLOTS]
        jcxz .mine_next
        dec cx
        btr ax, cx
.mine_next:
        inc si
        cmp si, SPEC_COUNT
        jb .mine
        pop si
        or ax, ax
        jz .ret
        mov cl, [cs:lv_left]    ; (no more than there are to pick)
        xor dx, dx
        xor di, di
.count: bt ax, di
        adc dl, 0
        inc di
        cmp di, 16
        jb .count
        cmp dl, cl
        jae .left
        mov cl, dl
.left:  mov [cs:lv_left], cl
        call lv_ask
.ret:   ret

; LV_SHINOBI: ZF set if character SI, gone up a level as a thief, is a Shinobi of SHINOBI_FIRST or
; more, who learns a spell of its own (as a preserver: CHOOSE A SPELL, with PROBE_PICK_LEVEL and
; PROBE_PICK_LIST). All registers kept.
lv_shinobi:
        push ax
        push bx
        push es
        cmp si, LV_PARTY
        jae .no
        les bx, [LV_SHEETS]
        imul ax, si, 0x47
        add bx, ax
        call kit_is_b
        db KIT_SHINOBI
        jne .out                ; (none: ZF clear)
        call kit_level
        cmp al, SHINOBI_FIRST
        jb .no
        cmp al, al              ; (ZF set)
        jmp .out
.no:    or al, 1
.out:   pop es
        pop bx
        pop ax
        ret

; LV_SCHOLAR: for character SI gone up a level as a preserver, a Scholar's spell more: the game's
; CHOOSE A SPELL (LV_SPELL) once before the game's own. All registers kept.
lv_scholar:
        pusha
        push es
        cmp si, LV_PARTY
        jae .out
        les bx, [LV_SHEETS]
        imul ax, si, 0x47
        add bx, ax
        call kit_is_b
        db KIT_SCHOLAR
        jne .out
        push si
        call far [cs:lv_spell]
        add sp, 2
.out:   pop es
        popa
        ret

; LV_DUE: CX the weapon kinds the character whose sheet is ES:BX is due: a gladiator 2, 3 from 6th
; level, 4 from 9th; a fighter or ranger 1; 0 for others. A human's earlier classes (dual-classed)
; count only once its first class's level has passed theirs. Others kept.
lv_due:
        push ax
        push si
        xor cx, cx
        xor si, si
.class: mov al, [es:bx + si + 0x21]
        mov ah, [es:bx + si + 0x24]
        or si, si
        jz .on
        cmp byte [es:bx + 0x18], 1
        jne .on
        cmp ah, [es:bx + 0x24]
        jae .next
.on:    cmp al, GLADIATOR_CLASS
        jne .warrior
        mov al, 2
        cmp ah, 6
        jb .most
        inc al
        cmp ah, 9
        jb .most
        inc al
        jmp .most
.warrior:
        cmp al, FIGHTER_CLASS
        je .one
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
        or cl, cl               ; (a Battle Mage: one)
        jnz .out
        call kit_is_b
        db KIT_BATTLE_MAGE
        jne .out
        mov cl, 1
.out:   pop si
        pop ax
        ret

; LV_ASK: the psionicists' pop-up (LV_PSI) in weapon mode for character SI (DS the game's): the
; kinds AX to pick from, LV_LEFT of them to pick. Each kind clicked goes in the sheet's first empty
; SPEC_SLOTS byte (PK_TAKE); the window closes once LV_LEFT are picked, or with EXIT.
lv_ask:
        pusha
        push es
        mov [cs:lv_avail], ax
        mov [cs:lv_member], si
        mov byte [cs:lv_mode], 1
        mov byte [cs:showing], 1
        push si
        call far [cs:lv_psi]
        add sp, 2
        mov byte [cs:lv_mode], 0
        mov byte [cs:showing], 0
        pop es
        popa
        ret

; The PROBE_PK_* probes, in the psionicists' pop-up (DSUN.EXE 85EECh, its window routine 85F6Eh,
; the window's drawing 86107h and clicks 862B6h); outside weapon mode each does what it replaced.
; PROBE_PK_COUNT: "mov dx,ax / or dx,dx" (85F01h; 4 bytes), the powers it has to pick: some.
; PROBE_PK_WIN: "push 445Dh" (85FF4h; 3 bytes), the window: the weapon window, centred.
; PROBE_PK_LEFT: "mov al,[4AECh]" (8602Dh; 3 bytes), the number shown: the kinds left to pick.
; PROBE_PK_TITLE: "push ds / push 3026h" (860C3h; 4 bytes), "PICK A PSIONIC POWER,": the weapons',
;   and its colours near-white on black (the next pushes' bytes; the game's own put back otherwise).
; PROBE_PK_FILL: "xor di,di / mov si,di" (8610Fh; 4 bytes), at the start of the powers' pictures
;   put in: none; the rows of the kinds it can't pick out of use (the routine's end, 862A7h).
; PROBE_PK_CLICK: "mov ax,[bp+8]" (862D4h; 3 bytes), a button clicked: a row it can pick taken
;   (PK_TAKE), then the window closed (as for a close, 86370h) once none are left to pick, or left up
;   (86367h).
PICK_WIN      equ 0xBCD             ; (weaponpages.PICKER: 3021)
PICK_FIRST    equ 0x860             ; (weaponpages.PICK_FIRST: its rows)
PICK_COUNT_BUTTON equ 0x2C37
PK_FILL_DONE  equ 0x862A7 - 0x86111 ; (the drawing routine's end, less the address after the INT)
PK_STAY       equ 0x86367 - 0x862D6 ; (the click handler's way out, and its close's)
PK_CLOSE      equ 0x86370 - 0x862D6
PK_OP_CALL    equ 0x86069 - 0x86111 ; (140:71Ah's far address, in a call, less the address after
PK_LABEL_CALL equ 0x86054 - 0x86111 ;   PROBE_PK_FILL's INT; and 140:7FAh's)
PK_WINDOW     equ 0x11A4            ; DS: the window up (far)
PK_TITLE_SECOND equ 0x860CB - 0x860C5 ; ("push 0D000FEh" and "push 0D3009Fh", after PROBE_PK_TITLE's
PK_TITLE_INK  equ 0x860D1 - 0x860C5 ;   INT: their colour bytes, less the address after it)
PK_TITLE_WIDTH equ 0x860CF - 0x860C5 ; ("push 0D3009Fh"'s width, 9Fh, the lines centred in it, and
PK_TITLE_Y    equ 0x860D4 - 0x860C5 ;   "push 46h": the lines' place)
PK_GAME_WIDTH equ 0x9F
PK_GAME_Y     equ 0x46
PK_PICK_WIDTH equ 214               ; (weaponpages.PICK_WIDTH, PICK_TITLE_Y: the lines under the slots)
PK_PICK_Y     equ 7 + 3 * 34 + 3
PK_PICK_X     equ (320 - 214) / 2   ; (the window's place, "push 2B0050h" before PROBE_PK_WIN: centred,
PK_PICK_TOP   equ (200 - 156) / 2   ;   weaponpages.PICK_HEIGHT 156)
PK_GAME_SECOND equ 0xD0
PK_GAME_INK   equ 0xD3              ; (dark grey)
PK_PICK_SECOND equ 0xD0             ; (as the game has it)
PK_PICK_INK   equ 0xD9              ; (near-white: 234, 234, 234)
probe_pk_count:
        mov dx, ax
        cmp byte [cs:lv_mode], 0
        je .flags
        mov dx, 2               ; (2: [4AECh] 1, as the routine counts; PROBE_PK_LEFT shows ours)
.flags: push bp
        mov bp, sp
        push ax
        or dx, dx
        pushf
        pop ax
        and ax, 0x08D5
        and word [bp + 6], 0xFFFF - 0x08D5
        or [bp + 6], ax
        pop ax
        pop bp
        iret

probe_pk_win:
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
        mov word [bp + 8], 0x445D
        cmp byte [cs:lv_mode], 0
        je .out
        mov word [bp + 8], PICK_WIN
        mov word [bp + 10], PK_PICK_X   ; (and its place, centred: the game's, 50h and 2Bh, centre
        mov word [bp + 12], PK_PICK_TOP ;   the psionicists' 159 by 113)
.out:   pop ax
        pop bp
        iret

probe_pk_left:
        mov al, [0x4AEC]
        cmp byte [cs:lv_mode], 0
        je .out
        mov al, [cs:lv_left]
.out:   iret

probe_pk_title:
        sub sp, 4               ; push a far pointer: the frame down two words
        push bp
        mov bp, sp
        push ax
        mov ax, [bp + 6]
        mov [bp + 2], ax
        mov ax, [bp + 8]
        mov [bp + 4], ax
        mov ax, [bp + 10]
        mov [bp + 6], ax
        mov [bp + 10], ds
        mov word [bp + 8], 0x3026
        push ds
        push bx
        lds bx, [bp + 2]        ; the line's colours, in the pushes that come next: the game's ...
        mov byte [bx + PK_TITLE_SECOND], PK_GAME_SECOND
        mov byte [bx + PK_TITLE_INK], PK_GAME_INK
        mov byte [bx + PK_TITLE_WIDTH], PK_GAME_WIDTH
        mov byte [bx + PK_TITLE_Y], PK_GAME_Y
        cmp byte [cs:lv_mode], 0
        je .out
        mov byte [bx + PK_TITLE_SECOND], PK_PICK_SECOND  ; ... or near-white on black, under the
        mov byte [bx + PK_TITLE_INK], PK_PICK_INK         ;   slots, centred in the wider window
        mov byte [bx + PK_TITLE_WIDTH], PK_PICK_WIDTH
        mov byte [bx + PK_TITLE_Y], PK_PICK_Y
        mov [bp + 10], cs
        mov word [bp + 8], lv_title
.out:   pop bx
        pop ds
        pop ax
        pop bp
        iret

probe_pk_fill:
        xor di, di
        mov si, di
        cmp byte [cs:lv_mode], 0
        je .out
        push bp
        mov bp, sp
        push ds
        push bx
        lds bx, [bp + 2]        ; the code after the INT: the far calls' addresses, as fixed up
        mov eax, [bx + PK_OP_CALL]
        mov [cs:lv_op_call], eax
        mov eax, [bx + PK_LABEL_CALL]
        mov [cs:lv_label_call], eax
        pop bx
        pop ds
        add word [bp + 2], PK_FILL_DONE
        pop bp
        mov byte [cs:lv_hovered], 0xFF ; (the title, as the window is drawn)
        call pk_ops
.out:   iret

; every row in use if its kind is in LV_AVAIL, out of use if not (DS the game's)
pk_ops:
        pusha
        push es
        xor si, si
.row:   xor ax, ax
        bt [cs:lv_avail], si
        jc .op
        inc ax
.op:    push ax
        push word 0
        lea bx, [si + PICK_FIRST]
        push bx
        push dword [PK_WINDOW]
        call far [cs:lv_op_call]
        add sp, 10
        inc si
        cmp si, 16
        jb .row
        pop es
        popa
        ret

probe_pk_click:
        push bp
        mov bp, sp              ; ([BP]: the click handler's BP)
        push bx
        mov bx, [bp]
        mov ax, [ss:bx + 8]     ; the replaced "mov ax,[bp+8]": the button
        cmp byte [cs:lv_mode], 0
        je .out
        sub ax, PICK_FIRST
        cmp ax, 16
        jae .back
        bt [cs:lv_avail], ax
        jnc .back
        btr [cs:lv_avail], ax
        call pk_take
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

; PK_TAKE: kind AX into the sheet of LV_MEMBER (its first empty SPEC_SLOTS byte), its row out of
; use, and the number shown one less (DS the game's)
pk_take:
        pusha
        push es
        mov dx, ax
        les bx, [LV_SHEETS]
        imul ax, [cs:lv_member], 0x47
        add bx, ax
        xor si, si
.slot:  cmp byte [es:bx + si + SPEC_SLOTS], 0
        je .put
        inc si
        cmp si, SPEC_COUNT
        jb .slot
        jmp .shown
.put:   mov al, dl
        inc al
        mov [es:bx + si + SPEC_SLOTS], al
.shown: push word 1
        push word 0
        add dx, PICK_FIRST
        push dx
        push dword [PK_WINDOW]
        call far [cs:lv_op_call]
        add sp, 10
        mov al, [cs:lv_left]
        dec al
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

lv_psi    dd 0                  ; the psionicists' pop-up (620:57h, as fixed up)
lv_spell  dd 0                  ; the preservers' CHOOSE A SPELL (620:5Ch, as fixed up)
lv_class  db 0                  ; 0Bh while PROBE_LV_PICK has a preserver gone up a level
lv_op_call dd 0                 ; 140:71Ah, a button's state (0 in use, 1 out of use)
lv_label_call dd 0              ; 140:7FAh, a button's text
lv_lines_call dd 0              ; 85CC9h, the window's two lines (as PK_HOVER finds it)
lv_hovered db 0FFh              ; the slot PK_HOVER last named (0FFh none: the title)
lv_hover  db 'SPECIALIZE IN', 0
lv_expert db 'EXPERT IN', 0
lv_mode   db 0                  ; 1 while LV_ASK has the pop-up up for weapons
lv_left   db 0
lv_have   db 0
lv_avail  dw 0
lv_member dw 0
lv_count_text db '  0', 0
lv_title  db 'PICK A WEAPON SPECIALTY,', 0

; PROBE_EF_ROWS: INT VEC_EF_ROWS replaces "pop di / pop si" (2 bytes; DSUN.EXE 7F13Eh) at the end of
; the Effects screen's routine that puts the selected character's effects in their cells (7EDFAh,
; run when the screen opens and when another character is picked; [BP-4] the cells it has used).
; With weapon specialization, and the lower panel free (the game puts effects there only past 21),
; the character's weapon kinds are listed there, in the game's text as the USE screen's spell slots
; are (C_DRAW_LINE, at the same place): a line for the skill, then a line a kind. Then the pops,
; from under the interrupt frame.
EF_SEL_SEG   equ 0x7EE07 - 0x7F140  ; ("mov ax,348h": the selected character's number's segment,
EF_SELECTED  equ 0x25B              ;   at +25Bh there; less the address after the INT)
EF_CELLS     equ 21                 ; (the upper panel's)
EF_LINES     equ 5
probe_ef_rows:
        sti
        pushad
        push es
        call wp_rules
        jz .pops
        cmp word [bp - 4], EF_CELLS
        jg .pops
        mov bx, sp
        les di, [ss:bx + 34]    ; the code after the INT
        mov es, [es:di + EF_SEL_SEG]
        mov ax, [es:EF_SELECTED]
        cmp ax, LV_PARTY
        jae .pops
        mov dx, ds
        add dx, USE_TEXT_SEG
        mov [cs:c_draw + 2], dx
        mov word [cs:c_draw], USE_TEXT_OFF
        mov edx, [PK_WINDOW]
        mov [cs:c_winptr], edx
        call ef_draw
.pops:  pop es
        popad
        push bp                 ; the replaced pops: DI and SI from under the interrupt frame,
        mov bp, sp              ;   the frame (and BP) moved up over them
        push ax
        mov di, [bp + 8]
        mov si, [bp + 10]
        mov ax, [bp + 6]
        mov [bp + 10], ax       ; flags
        mov ax, [bp + 4]
        mov [bp + 8], ax        ; CS
        mov ax, [bp + 2]
        mov [bp + 6], ax        ; IP
        mov ax, [bp]
        mov [bp + 4], ax        ; BP
        pop ax
        mov sp, bp
        add sp, 4
        pop bp
        iret

; EF_DRAW: party member AX's lines (DS the game's): a line for each kit, the oldest class's first
; (KIT_OF_SHEET, "(ASLEEP)" after a kit asleep), then its weapon kinds, the skill's line where it
; changes, then the kind's (EF_LINES_OF). The panel has room for EF_LINES: with more, a page at a
; time, EF_LINES - 1 of them and EF_MORE under them; a click on the panel (PROBE_EF_CLICK) shows the
; next page, after the last the first again.
ef_draw:
        les bx, [LV_SHEETS]
        mov dx, ax
        imul ax, ax, 0x47
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
        mov word [cs:ef_rows], EF_LINES
        cmp cx, EF_LINES
        jbe .draw
        dec word [cs:ef_rows]
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
        call kit_place          ; (a line for each kit, the oldest class's first; a human's kit
        jc .specs               ; asleep until its class is passed, as the game's classes are)
.kit:   call kit_at
        jz .kit_next
        call kit_of_sheet
        call kit_awake
        jnc .line
        call kit_line_asleep
.line:  call ef_line
.kit_next:
        dec di
        jns .kit
.specs: call own_race_b         ; (the game's own party's features: a line each, OWN_LINES)
        jz .spec_rule
        mov si, own_lines
.own:   cmp byte [cs:si], 0
        je .spec_rule
        cmp [cs:si], al
        lea si, [si + 1]
        jne .own_skip
        call ef_line
.own_skip:
        cmp byte [cs:si], 0
        lea si, [si + 1]
        jne .own_skip
        jmp .own
.spec_rule:
        test word [cs:rules], RULE_SPECIALIZE
        jz .ret
        xor di, di
.slot:  cmp di, SPEC_COUNT
        jb .chosen
        mov si, BOW_KIND                ; (then the bow, a ranger's whether chosen or not, unless
        push di                         ;   it is among the chosen: SPEC_OF_SHEET's skill with it)
        xor di, di
.bow:   cmp byte [es:bx + di + SPEC_SLOTS], BOW_KIND
        je .bow_had
        inc di
        cmp di, SPEC_COUNT
        jb .bow
        pop di
        jmp .kind_of
.bow_had:
        pop di
        jmp .ret
.chosen:
        movzx si, byte [es:bx + di + SPEC_SLOTS]
.kind_of:
        or si, si
        jz .next
        dec si
        mov [cs:ef_kind], si
        shl si, 1
        mov si, [cs:si + wp_plain]  ; (its plain weapon's type: SPEC_OF_SHEET's skill with it)
        call spec_of_sheet
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
        shl si, 1
        mov si, [cs:si + ef_kinds]
        call ef_line
.next:  inc di
        cmp di, SPEC_COUNT
        jbe .slot
.ret:   ret

; KIT_OF_SHEET: CS:SI the line naming kit AL (KIT_AT's, not 0: "KIT: RAVAGER", in KIT_LINE), a long
; name shorter (KIT_SHORT). KIT_LINE_ASLEEP: " (ASLEEP)" after it. Others kept.
kit_line_asleep:
        push ax
        push di
        mov si, kit_line
.end:   cs lodsb
        or al, al
        jnz .end
        lea di, [si - 1]
        mov si, kit_asleep
.copy:  cs lodsb
        mov [cs:di], al
        inc di
        or al, al
        jnz .copy
        mov si, kit_line
        pop di
        pop ax
        ret
kit_of_sheet:
        push ax
        push cx
        push di
        mov si, kit_short
.short: cmp byte [cs:si], 0
        je .long
        cmp [cs:si], al
        je .found
.skip:  inc si
        cmp byte [cs:si], 0
        jne .skip
        inc si
        jmp .short
.found: inc si
        jmp .name
.long:  call kit_name_ptr
.name:  mov di, kit_line + 5    ; (after "KIT: ")
.char:  cs lodsb
        mov [cs:di], al
        inc di
        or al, al
        jnz .char
        mov si, kit_line
        or di, di               ; (ZF clear)
.out:   pop di
        pop cx
        pop ax
        ret

; KIT_NAME_PTR: CS:SI kit AL's name in KIT_NAMES (AL not 0). Others kept.
kit_name_ptr:
        push ax
        push cx
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
.past:  cs lodsb
        or al, al
        jnz .past
        jmp .skip
.out:   pop cx
        pop ax
        ret

; KIT_IS: ZF set if sheet ES:BX has kit AL (KIT_RAVAGER...: the creation screen's class x 4 + the
; kit, kitpages.kit_ids) awake (KIT_AWAKE), KIT_WHERE then the place of its class (KIT_LEVEL and
; KIT_CLASS_OF go by it); ZF clear if not (the rule off, more than one class but for a human, not
; chosen, or asleep). KIT_HAS: the same, asleep too. A human may have a kit for each of its classes
; (KIT_AT). All registers kept.
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

; KIT_AT: AL the kit (as KIT_IS numbers them) of the class at place DI (0-2) of sheet ES:BX, asleep
; or not, ZF clear; 0 and ZF set for none. KIT_BYTE has two bits for each class with a kit (0 none,
; 1-3), the first class's lowest, the next class taken (DUAL) the next two: the place of the class
; a pair is for counts back from the oldest's (KIT_PLACE). Others kept.
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
.class: movzx di, byte [es:bx + di + 0x21]  ; (its class, 1-17: the creation screen's)
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

; KIT_PLACE: DI the place (0-2) among sheet ES:BX's classes of the class its kit was chosen with:
; 0 for one class; for a human who has changed class (DUAL: the classes move down, the new one
; first), its first class, the last of its classes; 0 for two classes at once with a multiclass
; group (MULTI_GROUP). CF set for more than one class otherwise (no kit). Others kept.
kit_place:
        xor di, di
        cmp word [es:bx + 0x22], 0
        je .ok
        cmp byte [es:bx + 0x18], 1
        jne .multi
        inc di
        cmp byte [es:bx + 0x23], 0
        je .ok
        inc di
.ok:    clc
        ret
.multi: push ax                 ; (two classes at once: place 0, with a multiclass group)
        call multi_group
        or al, al
        pop ax
        jnz .ok
        stc
        ret

; KIT_AWAKE: CF set if the kit of sheet ES:BX, its class at place DI (KIT_PLACE), sleeps: a human's
; first class, until the class it has now is of a higher level (as the game counts its earlier
; classes). Others kept.
kit_awake:
        or di, di
        jz .yes
        push ax
        mov al, [es:bx + di + 0x24]
        cmp [es:bx + 0x24], al
        pop ax
        ja .yes
        stc
        ret
.yes:   clc
        ret

; KIT_LEVEL: AL the level of the class of the kit KIT_IS (or KIT_HAS) last found (KIT_WHERE) on
; sheet ES:BX, the kit's levels (a Ravager's AC, a Seeker's slots). KIT_CLASS_OF: AL that class.
; Others kept.
kit_level:
        push di
        mov di, [cs:kit_where]
        mov al, [es:bx + di + 0x24]
        pop di
        ret
kit_class_of_sheet:
        push di
        mov di, [cs:kit_where]
        mov al, [es:bx + di + 0x21]
        pop di
        ret

; CREATURE_SHEET: ES:BX the sheet of creature AX (its record's number). DS the game's; others kept.
creature_sheet:
        push ax
        les bx, [CREATURES]
        imul ax, ax, 0x3A
        add bx, ax
        mov ax, [es:bx + 4]     ; (its sheet's number)
        les bx, [0x1661]
        imul ax, ax, 0x47
        add bx, ax
        pop ax
        ret

; CR_IS: "call cr_is / db KIT_X": ZF set if creature AX (DS the game's) has kit KIT_X awake (KIT_IS,
; KIT_WHERE set), KIT_IS_B the same for sheet ES:BX. All registers kept.
cr_is:
        push bx
        push es
        call creature_sheet
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

; KIT_AC: AX (the AC the game's AC routine has for its creature, whose thing is its [BP+6]) with
; the creature's kit's (kits.ac): a Ravager's base AC by its level (RAVAGER_AC) where it is better
; than its sheet's (+27h), its armour improving it as before; a Wanderer's 1 worse; a Sentinel's 2
; better with a shield in a hand, an Arena Champion's 1; a Grove Warden's 1 better for every 3 druid levels. DS the game's;
; a Wild Fury whose Wild Fighting check failed (KIT_WILD) 3 worse, no worse than 10.
; others kept.
kit_ac:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        push bx
        push cx
        push dx
        push es
        mov cx, ax
        mov ax, ds
        add ax, THINGS_SEG
        mov es, ax
        mov bx, [bp + 6]
        imul bx, bx, 3
        cmp byte [es:bx + THINGS], 2
        jne .out                ; (not a creature)
        mov ax, [es:bx + THINGS + 1]
        cmp ax, 3               ; (Wild Fighting failed: 3 worse, no worse than 10)
        ja .sheet
        bt word [cs:kit_wild], ax
        jnc .sheet
        cmp cx, WILD_AC_MOST
        jge .sheet
        add cx, WILD_AC
        cmp cx, WILD_AC_MOST
        jle .sheet
        mov cx, WILD_AC_MOST
.sheet: call creature_sheet     ; (each of its kits' awake: a human may have two or three)
        call kit_is_b           ; (a Battle Dancer's dance: 1 better, or 1 worse, KIT_DANCE)
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
        cmp ax, RAVAGER_LEVELS - 1
        jbe .level
        mov ax, RAVAGER_LEVELS - 1
.level: push si
        mov si, ax
        movsx dx, byte [cs:si + ravager_ac]
        pop si
        movsx ax, byte [es:bx + 0x27]
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
        jz .out
        push di
        mov di, [bp + 6]
        mov ax, ds
        add ax, THINGS_SEG
        mov es, ax
        mov [cs:r_things], ax
        call prot_scan
        pop di
        jc .out
        test byte [cs:p_flags], P_SHIELD
        jz .out
        sub cx, dx
.out:   mov ax, cx
        pop es
        pop dx
        pop cx
        pop bx
.ret:   ret
ravager_ac db 7, 7, 6, 6, 5, 5, 4, 4, 3, 3   ; (by level, 1-10: the highest the game goes)
RAVAGER_LEVELS equ $ - ravager_ac

; KIT_MELEE: AX what the kit of sheet ES:BX adds to hit and to damage with item type SI unless it
; is a missile weapon's (its type's +0, bit 2): a Ravager's 1; a Brute's 2 with a two-handed weapon
; (+0Fh, 40h); a Ghetto Fighter's 1 with a dagger; else 0 (kits.melee). DS the game's; others kept.
DAGGER_KIND equ 2
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
        les bx, [ITEM_TYPES]
        imul ax, si, 0x14
        add bx, ax
        pop ax
        test byte [es:bx], KT_MISSILE
        jnz .none
        test byte [es:bx + 0x0F], KT_TWO_HANDED
        jnz .sum
        xor ax, ax
.sum:   add ax, cx
        jmp .out
.none:  xor ax, ax
.out:   pop es
        pop cx
        pop bx
        ret

; KIT_TO_HIT: AX what the attacker's kit adds to hit in the weapon attack routine (the attacker
; its [BP+0Eh], the sheet its [BP+10h], the item type [BP+14h], [BP+16h] above 1 for a missile):
; for a melee attack KIT_CHAMPION's and KIT_MELEE's; for a missile a Military Scout's 1 with a bow,
; sling or staff sling under the open sky (its KIT_OUTDOORS bit; kits.missile_to_hit); and either
; way a Poisoner's -1 (kits.POISONER_TO_HIT). Others kept.
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
        jmp .poisoner
.melee:
        call kit_champion
        push bx
        push dx
        push si
        push es
        mov dx, ax
        les bx, [0x1661]
        imul ax, [bp + 0x10], 0x47
        add bx, ax
        mov si, [bp + 0x14]
        call kit_melee
        add ax, dx
        pop es
        pop si
        pop dx
        pop bx
.poisoner:                      ; (a Poisoner 1 worse, melee or missile)
        push bx
        push es
        push ax
        les bx, [0x1661]
        imul ax, [bp + 0x10], 0x47
        add bx, ax
        pop ax
        call kit_is_b
        db KIT_POISONER
        jne .ghetto
        dec ax
.ghetto:
        call kit_is_b           ; (a Ghetto Fighter 1 worse with anything but a dagger)
        db KIT_GHETTO
        jne .ret
        push si
        mov si, [bp + 0x14]
        cmp si, KIND_TYPES
        jae .worse
        cmp byte [cs:si + kind_of_type], DAGGER_KIND + 1
        je .dagger
.worse: dec ax
.dagger:
        pop si
.ret:   pop es
        pop bx
        jmp wild_to_hit

; WILD_TO_HIT: AX (what the attacker's kit adds to hit) 3 less if the attacker in the weapon attack
; routine ([BP+0Eh]) is a party member whose Wild Fighting check failed (KIT_WILD: kits.WILD_TO_HIT).
; Others kept.
WILD_TO_HIT  equ 3
WILD_DAMAGE  equ 3
WILD_HALVES  equ 2              ; (1 more attack a round)
WILD_AC      equ 3              ; (AC that much worse, but no worse than WILD_AC_MOST)
WILD_AC_MOST equ 10
wild_to_hit:
        push si
        mov si, [bp + 0x0E]
        cmp si, 3
        ja .ret
        bt word [cs:kit_wild], si
        jnc .ret
        sub ax, WILD_TO_HIT
.ret:   pop si
        ret

; WILD_PASSED: CF set if the attacker in the weapon attack routine ([BP+0Eh]) is a party member
; whose Wild Fighting check passed this fight (KIT_WILD's bit N + 4). All registers kept.
wild_passed:
        push si
        mov si, [bp + 0x0E]
        cmp si, 3
        ja .no
        add si, 4
        bt word [cs:kit_wild], si
        pop si
        ret
.no:    pop si
        clc
        ret

; KIT_ATTACK_DAMAGE: the weapon attack's damage bonus ([BP-12h]) with the attacker's kit's
; (KIT_MELEE, for a melee attack: [BP+16h] 1 or less; the sheet [BP+10h], the item type
; [BP+14h]). All registers kept.
kit_attack_damage:
        cmp word [bp + 0x16], 1
        jg .ret
        push ax
        call kit_champion       ; (with a shield, +1 in melee)
        cmp ax, 1
        jne .kit
        inc word [bp - 0x12]
.kit:   pop ax
        push ax
        push bx
        push si
        push es
        les bx, [0x1661]
        imul ax, [bp + 0x10], 0x47
        add bx, ax
        mov si, [bp + 0x14]
        call kit_melee
        add [bp - 0x12], ax
        pop es
        pop si
        pop bx
        pop ax
.ret:   ret

; KIT_EXTRA: AX what the attacker's kit adds to hit and to damage in the weapon attack routine,
; melee or missile (the attacker its [BP+0Eh], the target's combatant the game's DS:494Ah)
; (kits.extra): a Battle Dancer's dance (KIT_DANCE, the Loader's: +1 or -1); a Wilderness
; Avenger's 1 against undead (race 9). DS the game's; others kept.
TARGET_COMBATANT equ 0x494A
UNDEAD_RACE equ 9
kit_extra:
        push bx
        push cx
        push si
        push es
        xor cx, cx
        mov ax, [bp + 0x0E]
        call creature_sheet
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
        mov ax, ds
        add ax, THINGS_SEG
        mov es, ax
        imul bx, [TARGET_COMBATANT], 3
        cmp byte [es:bx + THINGS], 2
        jne .out                ; (not a creature)
        mov ax, [es:bx + THINGS + 1]
        call creature_sheet
        cmp byte [es:bx + 0x18], UNDEAD_RACE
        jne .out
        inc cx
.out:   mov ax, cx
        pop es
        pop si
        pop cx
        pop bx
        ret

; KIT_CHAMPION: AX 1 if the attacker in the weapon attack routine (its thing [BP+18h], its sheet
; [BP+10h]) is an Arena Champion with a shield in a hand, -1 if one without, else 0 (kits.champion:
; in melee, with one +1 to hit and damage, without one -1 to hit). DS the game's; others kept.
kit_champion:
        push bx
        push es
        les bx, [0x1661]
        imul ax, [bp + 0x10], 0x47
        add bx, ax
        call kit_is_b
        db KIT_CHAMPION
        pop es
        pop bx
        mov ax, 0
        jne .ret
        push di
        mov ax, ds
        add ax, THINGS_SEG
        mov [cs:r_things], ax
        mov di, [bp + 0x18]
        mov ax, -1
        call prot_scan
        jc .out
        test byte [cs:p_flags], P_SHIELD
        jz .out
        mov ax, 1
.out:   pop di
.ret:   ret

; PROBE_INIT: INT VEC_INIT replaces "add dx,14h" (3 bytes: INT + NOP; DSUN.EXE 5750Eh) where a
; combatant's initiative for the round is made (DX the 0-9 roll and its adjustments, SI the
; creature): the game's 20 added, and a Sentinel's 2 more, a Military Scout's 2 under the open sky
; (its KIT_OUTDOORS bit), and 1 for each party member while a Wayfinder of the party is up
; (PATH_UP; kits.initiative).
probe_init:
        add dx, 20
        push ax
        mov ax, si
        call cr_is
        db KIT_SENTINEL
        jne .scout
        add dx, 2
.scout: cmp si, 3
        ja .out                 ; (not a party member)
        call cr_is
        db KIT_SCOUT
        jne .path
        bt word [cs:kit_outdoors], si
        jnc .path
        add dx, 2
.path:  call path_up
        jne .down
        inc dx
        jmp .out
.down:  call path_down          ; (a Wayfinder down, none up: 1 less)
        jne .out
        dec dx
.out:   pop ax
        iret

; PROBE_THAC0: INT VEC_THAC0 replaces "mov ax,14h / sub ax,si" (5 bytes: INT + 3 NOPs; DSUN.EXE
; 876BBh) at the end of the game's THAC0 routine (SI the most any of the character's classes
; takes off 20, [BP+6] its sheet's number), which every write of a creature's THAC0 (+1Fh) uses:
; AX 20 less SI, and the kit's (kits.thac0): a Swashbuckler's, Crusader's, Battle Mage's or Mind
; Warrior's a warrior's (21 less its level) where that is better, a Scholar's 1 worse.
probe_thac0:
        push bx
        push cx
        push es
        mov cx, 20
        sub cx, si
        les bx, [0x1661]
        imul ax, [bp + 6], 0x47
        add bx, ax
        call kit_is_b           ; (each kit it has awake: the best warrior THAC0 of them)
        db KIT_SWASHBUCKLER
        call .warrior
        call kit_is_b
        db KIT_CRUSADER
        call .warrior
        call kit_is_b
        db KIT_BATTLE_MAGE
        call .warrior
        call kit_is_b
        db KIT_MIND_WARRIOR
        call .warrior
        call kit_is_b
        db KIT_SCHOLAR
        jne .out
        inc cx
.out:   mov ax, cx
        pop es
        pop cx
        pop bx
        iret
.warrior:                       ; (ZF set: CX the warrior THAC0 by the kit's level where better)
        jne .ret
        push ax
        call kit_level
        movzx ax, al
        neg ax
        add ax, 21
        cmp ax, 1
        jge .best
        mov ax, 1
.best:  cmp ax, cx
        jge .kept
        mov cx, ax
.kept:  pop ax
.ret:   ret

; PROBE_SLOTS: INT VEC_SLOTS replaces "mov ax,[bp-2]" (3 bytes: INT + NOP; DSUN.EXE 5E255h) at the
; end of the game's spell slot routine (the slots a combatant has at a spell level, on resting
; and wherever the most is wanted: [BP+6] the combatant, [BP+8] the kind of magic, 1 wizard and 2
; priest, [BP+0Ah] the spell level; [BP-2] the slots its classes give): AX the slots, with the
; kit's (kits.slots): an Arcanist's wizard slots 1 more at each spell level it has any, a Battle
; Mage's 1 fewer, a Crusader's priest slots 1 fewer; a Seeker's and a Justifier's priest slots
; their own tables' (SEEKER_SLOTS), by ranger level; a Shinobi's wizard slots the Seeker's, by
; thief level.
SLOT_WIZARD  equ 1
SLOT_PRIEST  equ 2
probe_slots:
        push bx
        push cx
        push es
        mov cx, [bp - 2]
        mov ax, ds
        add ax, THINGS_SEG
        mov es, ax
        imul bx, [bp + 6], 3
        mov ax, [es:bx + COMBATANT_CREATURE]
        call creature_sheet     ; (each kit it has awake)
        call kit_is_b
        db KIT_ARCANIST
        jne .battle
        cmp byte [bp + 8], SLOT_WIZARD
        jne .battle
        jcxz .battle
        inc cx
.battle:
        call kit_is_b
        db KIT_BATTLE_MAGE
        jne .crusader
        cmp byte [bp + 8], SLOT_WIZARD
        jne .crusader
        jcxz .crusader
        dec cx
.crusader:
        call kit_is_b           ; (a Crusader's, a Wilderness Avenger's priest slots 1 fewer)
        db KIT_CRUSADER
        je .priest
        call kit_is_b
        db KIT_AVENGER
        jne .tables
.priest:
        cmp byte [bp + 8], SLOT_PRIEST
        jne .tables
        jcxz .tables
        dec cx
.tables:
        push dx
        mov dl, KIT_SEEKER      ; (a Shinobi's wizard slots: the Seeker's table, by thief level)
        call kit_is_b
        db KIT_SHINOBI
        jne .ranger
        cmp byte [bp + 8], SLOT_WIZARD
        je .levels
.ranger:
        cmp byte [bp + 8], SLOT_PRIEST
        jne .table_out
        call kit_is_b
        db KIT_SEEKER
        je .levels
        mov dl, KIT_JUSTIFIER
        call kit_is_b
        db KIT_JUSTIFIER
        jne .table_out
.levels:
        call kit_level                  ; (the ranger level)
        movzx ax, al
        xor cx, cx
        movzx bx, byte [bp + 0x0A]
        dec bx
        cmp bx, 2
        ja .table_out           ; (spell levels 1 to 3 only)
        cmp dl, KIT_JUSTIFIER
        jne .seeker_level
        cmp ax, 10
        jb .table_out
        or bx, bx
        jnz .table_out
        inc cx                  ; (one 1st-level slot from 10th level)
        jmp .table_out
.seeker_level:
        cmp ax, 6
        jb .table_out
        cmp ax, 10
        jbe .row
        mov ax, 10
.row:   sub ax, 6
        imul ax, ax, 3
        add bx, ax
        mov cl, [cs:bx + seeker_slots]
.table_out:
        pop dx
        cmp byte [bp + 8], SLOT_WIZARD  ; the Veiled Robe (dsloader/robes.py): a wizard slot more
        jne .out                        ; at spell levels 1 to 3 where it has any
        jcxz .out
        cmp byte [bp + 0x0A], 3
        ja .out
        imul bx, [bp + 6], 3
        mov ax, ds
        add ax, THINGS_SEG
        mov es, ax
        mov ax, [es:bx + COMBATANT_CREATURE]
        call robe_plus
        cmp ax, 2
        jb .out
        inc cx
.out:   mov ax, cx
        pop es
        pop cx
        pop bx
        iret
; a Seeker's priest slots at spell levels 1, 2 and 3, by ranger level 6 to 10 (and on: kits.SEEKER_SLOTS)
seeker_slots db 1, 0, 0,  2, 0, 0,  2, 1, 0,  2, 2, 0,  2, 2, 1

; PROBE_SLOT_LEVEL: INT VEC_SLOT_LEVEL replaces "mov al,es:[bx+24h]" (4 bytes: INT + 2 NOPs;
; DSUN.EXE 5E1F6h) in the game's spell slot routine, where it takes a class's level (ES:BX the
; sheet + DI, the class's place): AL that level, an Elementalist's 1 less (kits.slot_level: its
; slots a level behind), for its kit's own class (KIT_PLACE). Others kept.
probe_slot_level:
        push bx
        push cx
        push dx
        mov ch, ah
        mov dx, di
        sub bx, di
        call kit_at             ; (the kit of the class at place DI, awake)
        mov cl, al
        jz .own
        call kit_awake
        jnc .own
        xor cl, cl
.own:   add bx, di
        mov al, [es:bx + 0x24]
        cmp cl, KIT_ELEMENTALIST
        jne .out
        or al, al
        jz .out
        dec al
.out:   mov ah, ch
        pop dx
        pop cx
        pop bx
        iret

; KIT_PSP: AX the PSP a power (BX, 0-33: psychokinesis to 5, psychometabolism to 19, telepathy
; from 20) costs combatant SI to use, from the game's AX (kits.psp_cost): a Mind Bender's telepathy
; 2 less, its psychokinesis 2 more, a Kineticist's the other way about; a Titan Mind's
; psychometabolism 2 less, its telepathy 2 more; never below 1 (a cost of 0 or less as it was). KIT_PSP_OF: the same for the kit in CL. DS the game's; others kept.
PSP_PK_LAST  equ 5
WHOSE_TURN   equ 0x4979         ; DS: the combatant whose turn it is in a fight
PSP_TP_FIRST equ 20
kit_psp:
        push cx
        push es
        mov cx, ax
        mov ax, ds
        add ax, THINGS_SEG
        mov es, ax
        push bx
        imul bx, si, 3
        mov ax, [es:bx + COMBATANT_CREATURE]
        pop bx
        call psi_kit
        xchg ax, cx             ; (CL the kit, AX the cost)
        call kit_psp_of
        pop es
        pop cx
        ret
; PSI_KIT: AL the psionicist kit of creature AX that changes costs (KIT_MIND_BENDER, KIT_KINETICIST,
; KIT_TITAN_MIND), awake, or 0. DS the game's; others but AH kept.
psi_kit:
        call cr_is
        db KIT_MIND_BENDER
        je .bender
        call cr_is
        db KIT_TITAN_MIND
        je .titan
        call cr_is
        db KIT_KINETICIST
        mov al, KIT_KINETICIST
        je .ret
        xor al, al
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
        jne .bender
        cmp bx, PSP_PK_LAST
        jbe .out                ; (a Titan Mind's psychokinesis: as it was)
        mov dx, -2              ; (its psychometabolism 2 less, its telepathy 2 more)
        cmp bx, PSP_TP_FIRST
        jb .add
        mov dx, 2
        jmp .add
.bender:
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
.add:   add ax, dx
        cmp ax, 1
        jge .out
        mov ax, 1
.out:   pop dx
.ret:   ret

; PROBE_PSP_USE: INT VEC_PSP_USE replaces "or di,di / jge $+4 / xor di,di" (6 bytes: INT + 4
; NOPs; DSUN.EXE 5CBE7h) where the routine using a power has its cost in DI (SI the combatant,
; [BP+0Ah] the power: its table's, or worked out for Enhanced Strength and Domination): DI the
; kit's (KIT_PSP), no less than 0.
probe_psp_use:
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

; PROBE_PSP_TABLE: INT VEC_PSP_TABLE replaces "mov al,es:[bx+1]" (5 bytes: INT + 3 NOPs) where the
; game reads a power's cost from its table (ES:BX the power's row, 8 bytes a power; SI the
; combatant): in the check whether a power can be used (DSUN.EXE 5CAA3h) and where half of it is
; taken for a power that fails (5CCA2h). AL the kit's (KIT_PSP); AH as it was.
probe_psp_table:
        push bx
        push cx
        mov ch, ah
        movzx ax, byte [es:bx + 1]
        shr bx, 3
        call kit_psp
        mov ah, ch
        pop cx
        pop bx
        iret

; PROBE_PSP_DEFENCE: INT VEC_PSP_DEFENCE replaces "sub es:[bx+2],ax" (4 bytes: INT + 2 NOPs;
; DSUN.EXE 5D820h) where a creature (ES:BX its record, [BP-6] its number) pays AX for the psionic
; defence it raises: the kit's (KIT_PSP_OF; the defences are all telepathy), then taken off.
probe_psp_defence:
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

; GAME_DIE: AX a roll of 1 to AX from the game's own rand() seed (as its "rand()*N/32768 + 1"),
; not recorded in the ring. DS the game's; others kept (EAX's upper half too).
game_die:
        push ebx
        push ecx
        push edx
        movzx ecx, ax
        push eax
        mov bx, [cs:seed_off]
        mov eax, [bx]
        imul eax, eax, 0x015A4E35
        inc eax
        mov [bx], eax
        shr eax, 16
        and eax, 0x7FFF
        imul eax, ecx
        shr eax, 15
        inc eax
        mov cx, ax
        pop eax
        mov ax, cx
        pop edx
        pop ecx
        pop ebx
        ret

; PROBE_CURE: INT VEC_CURE replaces "nop / push cs" (2 bytes; DSUN.EXE 79619h) in the handler for
; spells with rules of their own, where the healing it has rolled (the word pushed last but one;
; DI the target, the game's [BP+8] the caster, [BP+0Eh] the spell) goes to the routine that heals:
; the caster's kit's (kits.cure): a Healer's Cure Light, Serious and Critical Wounds 1 more a die,
; a Lifebinder's those and Blood Flow a die more (CURE_DICE). Then CS pushed, as the code was.
CURE_SPELLS: ; spell, dice, sides (kits.CURE_DICE)
        db 71, 1, 8,  112, 2, 8,  127, 3, 8,  108, 2, 6
CURE_SPELLS_END:
probe_cure:
        sub sp, 2
        push bp
        mov bp, sp              ; [BP+4] the INT's IP, CS, flags; [BP+0Ah] DI pushed, [BP+0Ch] the healing
        pusha
        mov ax, [bp + 4]
        mov [bp + 2], ax
        mov ax, [bp + 6]
        mov [bp + 4], ax
        mov ax, [bp + 8]
        mov [bp + 6], ax
        mov ax, [bp + 4]
        mov [bp + 8], ax        ; (the CS the code pushed)
        mov di, [bp]            ; the game's BP
        mov ax, [ss:di + 0x0E]
        mov bx, CURE_SPELLS
.find:  cmp [cs:bx], al
        je .spell
        add bx, 3
        cmp bx, CURE_SPELLS_END
        jb .find
        jmp .out
.spell: or ah, ah
        jnz .out
        push bx
        push es
        mov ax, ds
        add ax, THINGS_SEG
        mov es, ax
        imul bx, [ss:di + 8], 3
        mov ax, [es:bx + COMBATANT_CREATURE]
        pop es
        pop bx
        mov dx, ax              ; (DX the creature)
        call cr_is
        db KIT_HEALER
        jne .lifebinder
        cmp byte [cs:bx], 108   ; (Blood Flow: not a cure)
        je .lifebinder
        movzx ax, byte [cs:bx + 1]
        add [bp + 0x0C], ax
.lifebinder:
        mov ax, dx
        call cr_is
        db KIT_LIFEBINDER
        jne .rescuer
        movzx ax, byte [cs:bx + 2]
        call game_die
        add [bp + 0x0C], ax
.rescuer:                       ; (a Rescuer under the open sky: 1 more a die of the cures)
        mov ax, dx
        call cr_is
        db KIT_RESCUER
        jne .out
        cmp byte [cs:bx], 108
        je .out
        cmp dx, 3
        ja .out
        bt word [cs:kit_outdoors], dx
        jnc .out
        movzx ax, byte [cs:bx + 1]
        add [bp + 0x0C], ax
.out:   popa
        pop bp
        iret

; PROBE_PSP_KEEP: INT VEC_PSP_KEEP replaces "mov al,es:[bx+2]" (5 bytes: INT + 3 NOPs; DSUN.EXE
; 5CE49h) where the game takes a power's cost to keep it up another round from its table (ES:BX
; the power's row; SI the combatant): AL the kit's (KIT_PSP), but 63h (none to keep up) as it is;
; AH as it was. PROBE_PSP_KEEP_DX: the same with the combatant in DX (5CB02h, the check whether it
; can be kept up).
PSP_NO_UPKEEP equ 0x63
probe_psp_keep_dx:
        push si
        mov si, dx
        call psp_keep
        pop si
        iret
probe_psp_keep:
        call psp_keep
        iret
psp_keep:
        push bx
        push cx
        mov ch, ah
        movzx ax, byte [es:bx + 2]
        cmp al, PSP_NO_UPKEEP
        je .out
        shr bx, 3
        call kit_psp
.out:   mov ah, ch
        pop cx
        pop bx
        ret

; PROBE_HIT_ROUND: INT VEC_HIT_ROUND replaces "mov byte es:[si+0AFh],1" (6 bytes: INT + 4 NOPs;
; DSUN.EXE 58733h) where the routine taking a hit's damage off marks creature SI hit this round
; (ES the segment of those marks), which keeps it from casting a spell until the next round (the
; USE screen's refusal, 892F3h; a queued spell dropped, 8991Bh): a Battle Mage isn't marked.
probe_hit_round:
        push ax
        mov ax, si
        call cr_is
        db KIT_BATTLE_MAGE
        je .out
        mov byte [es:si + 0xAF], 1
.out:   pop ax
        iret

; The Arcanist's second preserver spell in a turn. In a fight, a spell cast ends the caster's turn,
; through the fight's routine that sets a combatant's actions (59256h; with 0, none: the turn is
; over), called from the routine finishing any use of what the USE screen armed (a spell from a
; slot, an item's charge: 720F4h, which takes the slot or charge) and from the routines that cast;
; the routine casting a spell aimed on the map also marks the caster (the mark of a hit, +0AFh in
; the fight's table), and a marked character is offered no spell. An Arcanist's first preserver
; spell of its turn (DS:[54FBh] 0: from its wizard slots; DS:[54FCh] the party member) does
; neither: ARC_CASTS counts them, and ARC_HOLD keeps the turn from ending till the game's main loop
; runs again (PROBE_SCROLL), so it can cast a second; a hit still marks it.
; PROBE_CAST_MARK: INT VEC_CAST_MARK replaces "mov byte es:[bx+0AFh],1" (6 bytes: INT + 4 NOPs;
; DSUN.EXE 845F0h), the caster BX marked. PROBE_CAST_DONE: INT VEC_CAST_DONE replaces the finishing
; routine's "cmp word es:[19h],0" (6 bytes; 722AFh; ES the segment of the fight's state, not 0 in a
; fight): counts, sets ARC_HOLD (the party member + 1) for the first, and gives the JE after it
; the game's flags. PROBE_END_TURN: INT VEC_END_TURN replaces "mov si,[bp+8]" (3 bytes: INT + NOP;
; 59256h, [BP+6] the combatant, [BP+8] the actions) and returns at once, leaving the actions be,
; when ending ARC_HOLD's turn from another of the game's code segments (the fight's own routines,
; a turn ended from the combat menu among them, call it from its own). PROBE_ROUND_MARK: INT
; VEC_ROUND_MARK replaces "mov byte es:[si+0AFh],0" (6 bytes; 57621h) where creature SI's turn
; starts and its mark is cleared: its count too.
ARM_KIND equ 0x54FB             ; (the armed thing's kind: 0 a wizard spell from a slot, 1 a priest's, 3 an item)
ARM_WHO  equ 0x54FC             ; (the party member using it)
END_TURN_OUT equ 0x592AF - 0x5925F  ; (the routine's "pop si / leave / retf", from the INT's return: its NOP)
arc_casts db 0, 0, 0, 0         ; (party members 0-3: an Arcanist's preserver spells this turn)
arc_hold  db 0                  ; (the party member + 1 whose turn a cast doesn't end; 0 none)
probe_cast_mark:
        cmp bx, 4
        jae .mark
        cmp byte [ARM_KIND], 0
        jne .mark
        cmp byte [cs:arc_casts + bx], 0
        jne .mark
        push ax
        mov ax, bx
        call cr_is
        db KIT_ARCANIST
        pop ax
        jne .mark
        iret
.mark:  mov byte [es:bx + 0xAF], 1
        iret

probe_cast_done:
        sti
        push ax
        push bx
        mov byte [cs:arc_hold], 0
        cmp word [es:0x19], 0
        je .flags                       ; (not in a fight)
        cmp byte [ARM_KIND], 0
        jne .game
        movzx bx, byte [ARM_WHO]
        cmp bx, 4
        jae .game
        mov ax, bx
        call cr_is
        db KIT_ARCANIST
        jne .game
        inc byte [cs:arc_casts + bx]
        cmp byte [cs:arc_casts + bx], 1
        jne .game
        inc bx
        mov [cs:arc_hold], bl
.game:  cmp word [es:0x19], 0           ; (the game's flags)
.flags: pop bx
        pop ax
        retf 2

probe_end_turn:
        mov si, [bp + 8]
        or si, si
        jnz .ret                        ; (actions left: not the turn's end)
        push ax
        push bp
        movzx ax, byte [cs:arc_hold]
        dec ax
        js .ends                        ; (none held)
        cmp ax, [bp + 6]
        jne .ends
        mov ax, [bp + 4]                ; the caller's code segment ...
        mov bp, sp
        cmp ax, [bp + 6]                ; ... and the routine's own (the INT's return, past AX and BP)
        je .ends
        add word [bp + 4], END_TURN_OUT ; (held: return at once)
.ends:  pop bp
        pop ax
.ret:   iret

probe_round_mark:
        mov byte [es:si + 0xAF], 0
        mov byte [cs:arc_hold], 0
        cmp si, 4
        jae .ret
        mov byte [cs:arc_casts + si], 0
.ret:   iret

; The Shinobi's spells (kits.SHINOBI_SPELLS): spell, spell level. Wizard spells are 0 to WIZARD_LAST;
; Fogbolt, Reflected Image, Spook and Friends, new spells, count only with RULE_NEW_SPELLS (SHINOBI_KNOWS).
SHINOBI_SPELLS:
        db 6, 1,  2, 1,  9, 1,  4, 1,  11, 1           ; Gaze Reflection, Charm Person, Shield, Color Spray, Wall of Fog
        db FOG_SPELL, 1,  REFLECT_SPELL, 1,  SPOOK_SPELL, 1,  FRIENDS_SPELL, 1 ; Fogbolt, Reflected Image, Spook, Friends
        db 17, 2,  19, 2,  12, 2,  13, 2,  15, 2       ; Invisibility, Mirror Image, Blur, Detect Invisibility, Fog Cloud
        db 25, 3,  29, 3,  36, 3,  30, 3               ; Blink, Haste, Protection from Normal Missiles, Hold Person
SHINOBI_SPELLS_END:
WIZARD_LAST  equ 68
SHINOBI_FIRST equ 6             ; (the thief level its spells start at; it casts at that less 5)
KNOWN_FROM_DS equ 0x4356 - 0x3800  ; the spells each party member knows: DS less this, from KNOWN_OFF,
KNOWN_OFF    equ 0x168          ;   8Ah bytes a member, a byte a spell (not 0: known)
KNOWN_SIZE   equ 0x8A

; SHINOBI_CAST: AX the level a Shinobi of thief level AX casts at (less SHINOBI_FIRST - 1, no less
; than 0). Others kept.
shinobi_cast:
        sub ax, SHINOBI_FIRST - 1
        jns .ret
        xor ax, ax
.ret:   ret

; PROBE_CAST_LEVEL: INT VEC_CAST_LEVEL replaces "mov ax,[bp-2]" (3 bytes: INT + NOP; DSUN.EXE 81C06h)
; at the end of the caster level routine (its [BP+6] the combatant, [BP+8] the spell; [BP-2] the
; level its classes give, a ranger's 7 less: PROBE_RANGER_CAST), which sets the spell levels a
; caster may cast (half it rounded up: 81664h asks for spell 0) and weighs a spell against Dispel
; Magic: AX that, a Shinobi's for a wizard spell its thief level less 5 where more (SHINOBI_LEVEL).
probe_cast_level:
        mov ax, [bp - 2]
        jmp shinobi_wizard

; PROBE_SPELL_LEVEL: INT VEC_SPELL_LEVEL replaces "mov ax,di" (2 bytes; DSUN.EXE 5E3D1h) at the end of
; the routine giving the level a spell is cast at, for its duration and damage (5E25Ch; the same
; arguments; DI the best level of the caster's classes that cast it, PROBE_RANGER_LEVEL's for a
; ranger): AX that, for a wizard spell a Shinobi's as PROBE_CAST_LEVEL's; for a priest spell a
; Spirit Caller's or Wasteland Seer's (or K'ratchek's: OWN_RACE_B) 2 more under the open sky (its KIT_OUTDOORS bit), 1 less
; under a roof, no less than 1 (SKY_LEVEL; kits.sky_level).
probe_spell_level:
        mov ax, di
        call sky_level
        jmp shinobi_wizard

; SKY_LEVEL: AX (the level priest spell [BP+8] is cast at by combatant [BP+6]) with a Spirit
; Caller's or Wasteland Seer's: 2 more under the open sky, 1 less under a roof (no less than 1).
; DS the game's; others kept.
SKY_MORE equ 2
sky_level:
        cmp word [bp + 8], WIZARD_LAST
        jbe .ret
        cmp word [bp + 8], KIT_SPELL_LAST
        ja .ret                 ; (not a priest spell)
        push bx
        push cx
        push es
        mov cx, ax
        mov ax, ds
        add ax, THINGS_SEG
        mov es, ax
        imul bx, [bp + 6], 3
        mov ax, [es:bx + COMBATANT_CREATURE]
        cmp ax, 3
        ja .out                 ; (not a party member)
        call cr_is
        db KIT_SPIRIT_CALLER
        je .sky
        call cr_is
        db KIT_WASTE_SEER
        je .sky
        push ax                 ; (K'ratchek, as a Wasteland Seer: OWN_RACE_B)
        call cr_own_race
        cmp al, THRI_KREEN_RACE
        pop ax
        jne .out
.sky:   bt word [cs:kit_outdoors], ax
        jnc .roof
        add cx, SKY_MORE
        jmp .out
.roof:  cmp cx, 1
        jle .out
        dec cx
.out:   mov ax, cx
        pop es
        pop cx
        pop bx
.ret:   ret

; PROBE_RANGER_LEVEL: INT VEC_RANGER_LEVEL replaces "mov al,es:[bx+24h]" (4 bytes: INT + 2 NOPs;
; DSUN.EXE 5E3B8h) where that routine takes the level of a class of the caster's that casts the
; spell (ES:BX the sheet + the class's place; the combatant its [BP+6]), whole for a ranger (the
; caster level routine counts it 7 less: PROBE_RANGER_CAST): AL that, a ranger's 7 less with
; RULE_HI_RANGER, a Seeker's 5 less and a Justifier's 9 whatever the rule (no less than 0;
; kits.spell_class_level).
probe_ranger_level:
        mov al, [es:bx + 0x24]
        push cx
        mov cl, [es:bx + 0x21]
        sub cl, 13
        cmp cl, 3
        ja .out                 ; (not a ranger: classes 13-16)
        push ax
        push bx
        mov cl, 5
        call cb_is
        db KIT_SEEKER
        je .take
        mov cl, 9
        call cb_is
        db KIT_JUSTIFIER
        je .take
        mov cl, 7
        test word [cs:rules_hi], RULE_HI_RANGER
        jnz .take
        xor cl, cl
.take:  pop bx
        pop ax
        sub al, cl
        jnc .out
        xor al, al
.out:   pop cx
        iret

; SHINOBI_WIZARD: AX (a level), for wizard spell [BP+8] (or a new spell) the level a Shinobi (combatant [BP+6])
; casts it at where more; then IRET.
shinobi_wizard:
        cmp word [bp + 8], WIZARD_LAST
        jbe .wizard
        cmp word [bp + 8], NS_FIRST     ; (or a new spell: NEW SPELLS)
        jb .ret
        cmp word [bp + 8], NS_LAST
        ja .ret
.wizard:
        push cx
        mov cx, ax
        call shinobi_level
        cmp ax, cx
        jge .out
        mov ax, cx
.out:   pop cx
.ret:   iret

; CB_IS: "call cb_is / db KIT_X": ZF set if combatant [BP+6] has kit KIT_X awake (KIT_IS, KIT_WHERE
; set), BX its creature. DS the game's; others kept.
cb_is:
        push es
        push ax
        push si
        push di
        mov di, sp
        mov si, [ss:di + 8]     ; (the byte after the call)
        inc word [ss:di + 8]
        mov ax, ds
        add ax, THINGS_SEG
        mov es, ax
        imul bx, [bp + 6], 3
        mov ax, [es:bx + COMBATANT_CREATURE]
        push ax
        call creature_sheet
        mov al, [cs:si]
        call kit_is
        pop bx
        pop di
        pop si
        pop ax
        pop es
        ret

; SHINOBI_LEVEL: AX the level a Shinobi casts at (SHINOBI_CAST) if combatant [BP+6] is one, else 0.
; DS the game's; others kept.
shinobi_level:
        push bx
        push es
        call cb_is
        db KIT_SHINOBI
        mov ax, 0
        jne .out
        mov ax, bx
        les bx, [CREATURES]
        imul ax, ax, 0x3A
        add bx, ax
        mov ax, [es:bx + 4]
        les bx, [0x1661]
        imul ax, ax, 0x47
        add bx, ax
        call kit_level
        movzx ax, al
        call shinobi_cast
.out:   pop es
        pop bx
        ret

; PROBE_PICK_ANY: INT VEC_PICK_ANY replaces "mov [bp-2],ax / or ax,ax" (5 bytes: INT + 3 NOPs;
; DSUN.EXE 85580h) in the routine a level up calls for a preserver's spell (620:5Ch, 85560h; SI the
; character, AX its preserver level), which goes on (the JG after) only for a level, and then opens
; CHOOSE A SPELL (85771h) if the game's list (500:2Ah) has a spell to learn. A Shinobi has no
; preserver level and nothing on that list: for one, CHOOSE A SPELL (DI 1, on at PICK_OPEN) if one
; of its spells (SHINOBI_SPELLS) up to the spell level it casts is unknown (SHINOBI_UNKNOWN), else
; nothing (AX 0). Flags as "or ax,ax".
PICK_OPEN equ 0x855CB - 0x85582   ; ("or di,di", then "push si / call 5771h")
probe_pick_any:
        mov [bp - 2], ax
        push bp
        mov bp, sp              ; (the INT's frame: [BP+2] IP, [BP+6] flags)
        push bx
        push cx
        push es
        mov cx, ax
        les bx, [0x1661]
        imul ax, si, 0x47
        add bx, ax
        call kit_is_b
        db KIT_SHINOBI
        mov ax, cx
        jne .int
        call kit_level
        movzx ax, al
        call shinobi_cast
        inc ax
        shr ax, 1
        mov cl, al              ; (CL the highest spell level it casts)
        xor ax, ax
        call shinobi_unknown
        jnc .flags
        mov di, 1
        add word [bp + 2], PICK_OPEN
        jmp .flags
.int:   call pick_int_any               ; (RULE_HI_INT: a spell left to learn, its level not full)
.flags: or ax, ax
        pushf
        pop cx
        and cx, 0x08D5          ; (OF, SF, ZF, AF, PF, CF)
        and word [bp + 6], ~0x08D5
        or [bp + 6], cx
        pop es
        pop cx
        pop bx
        pop bp
        iret

; SHINOBI_UNKNOWN: CF set if character SI doesn't know one of the Shinobi's spells (SHINOBI_SPELLS)
; of spell level CL or less (SHINOBI_KNOWS). DS the game's; all registers kept.
shinobi_unknown:
        push ax
        push bx
        push si
        mov bx, si
        mov si, SHINOBI_SPELLS
.spell: cmp [cs:si + 1], cl
        ja .next
        movzx ax, byte [cs:si]
        call shinobi_knows
        jc .next
        stc
        jmp .out
.next:  add si, 2
        cmp si, SHINOBI_SPELLS_END
        jb .spell
        clc
.out:   pop si
        pop bx
        pop ax
        ret

; SHINOBI_KNOWS: CF set if party member BX knows spell AX: the game's byte for it (KNOWN_OFF's), or
; for a new spell its sheet's bit (NS_KNOWS); a new spell counts as known while RULE_NEW_SPELLS is
; off, or its record has no room yet (NS_NEW: so it isn't offered). DS the game's; all registers kept.
shinobi_knows:
        cmp ax, NS_FIRST
        jae .new
        push bx
        push ds
        push ax
        imul bx, bx, KNOWN_SIZE
        add bx, KNOWN_OFF
        add bx, ax
        mov ax, ds
        sub ax, KNOWN_FROM_DS
        mov ds, ax
        pop ax
        cmp byte [bx], 0
        pop ds
        pop bx
        jne .yes
        clc
        ret
.new:   push ax
        call ns_new             ; (off, or no room for its record yet: as known, not offered)
        pop ax
        jnc .yes
        push ax
        push cx
        mov cl, al
        sub cl, NS_FIRST
        mov ax, bx
        call ns_knows
        pop cx
        pop ax
        ret
.yes:   stc
        ret

; PROBE_PICK_LEVEL: INT VEC_PICK_LEVEL replaces "inc al" (2 bytes; DSUN.EXE 85861h) in the CHOOSE A
; SPELL window, where AL is the character's preserver level and the spell levels on offer are up to
; (AL + 1) / 2 (DS:[119Ch] its sheet, far): a Shinobi's its casting level (SHINOBI_CAST); no more
; than PICK_CAP's spell level while PICK_SPELLS sets one. Then AL + 1, as the code was.
PICK_SHEET   equ 0x119C
probe_pick_level:
        push bx
        push es
        les bx, [PICK_SHEET]
        push ax
        call kit_is_b
        db KIT_SHINOBI
        pop ax
        jne .out
        call kit_level
        movzx ax, al
        call shinobi_cast
.out:   cmp byte [cs:pick_cap], 0   ; (PICK_SPELLS's: spell levels up to PICK_CAP)
        je .inc
        push cx
        mov cl, [cs:pick_cap]
        shl cl, 1
        dec cl
        cmp al, cl
        jbe .capped
        mov al, cl
.capped:
        pop cx
.inc:   inc al
        pop es
        pop bx
        iret

; PICK_SPELLS: member SI picks its preserver spells on the game's CHOOSE A SPELL (620:5Ch, through
; its stub, PICK_STUB from DS; the routine a preserver's level up calls), CL of them with the
; spell levels on offer up to 1st, then CH up to 2nd (PICK_CAP, for PROBE_PICK_LEVEL). DS the
; game's, interrupts on; all registers kept. From code of another overlay than CHOOSE A SPELL's
; (85560h on: the DUAL window's), only with the way back in a frame the overlay manager can fix
; up (PROBE_CR_SPELLS): its loading may take that code's place. EXIT on the window (its "YOU
; HAVEN'T CHOSEN", then EXIT) leaves it with no spell learnt: the picks are over, and those left
; are the game's own starting spells (PICK_FILL), as it gives them without the mod.
PICK_STUB  equ 0x430A - 0x4356          ; (the stub's segment, less DS's, as WP_STUB)
PICK_ENTRY equ 0x5C
PICK_WIZARD equ 0x45                    ; (the preserver spells: 0-44h)
pick_spells:
        pusha
        push es
        mov byte [cs:pick_cap], 1
.first: or cl, cl
        jz .second
        call .one
        jc .exited
        dec cl
        jmp .first
.second:
        mov byte [cs:pick_cap], 2
.more:  or ch, ch
        jz .done
        call .one
        jc .exited
        dec ch
        jmp .more
.exited:
        call pick_fill
.done:  mov byte [cs:pick_cap], 0
        pop es
        popa
        ret
.one:   push cx                 ; (CF set if the window was left with no spell learnt)
        call pick_known
        push ax
        mov ax, ds
        add ax, PICK_STUB
        mov [cs:pick_far + 2], ax
        mov word [cs:pick_far], PICK_ENTRY
        push si
        call far [cs:pick_far]
        add sp, 2
        call pick_known
        pop cx
        cmp si, 4               ; (only the party's four have KNOWN_OFF's table; creation's
        jae .chose              ;   and DUAL's are among them)
        cmp ax, cx
        je .none
.chose: pop cx
        clc
        ret
.none:  pop cx
        stc
        ret
pick_far   dd 0
pick_cap   db 0

; PICK_KNOWN: AX the preserver spells member SI knows (KNOWN_OFF's bytes, the low four bits set
; when known, as the game's learning, 500:43h, sets them). DS the game's; others kept.
pick_known:
        push bx
        push cx
        push ds
        imul bx, si, KNOWN_SIZE
        add bx, KNOWN_OFF
        mov ax, ds
        sub ax, KNOWN_FROM_DS
        mov ds, ax
        xor ax, ax
        mov cx, PICK_WIZARD
.spell: test byte [bx], 0x0F
        jz .next
        inc ax
.next:  inc bx
        loop .spell
        pop ds
        push ax
        xor cl, cl
        call ns_count_of        ; (and the new spells: NS_SHEET's bits)
        pop cx
        add ax, cx
        pop cx
        pop bx
        ret

; PICK_FILL: member SI learns the game's own starting spells it doesn't know yet, CL of 1st level
; (Grease, Magic Missile, Shield, Wall of Fog, as the game gives them) and CH of 2nd (Fog Cloud,
; Mirror Image), for the picks EXIT left (fewer if the lists run out). DS the game's; all kept.
pick_fill:
        pusha
        push ds
        imul bx, si, KNOWN_SIZE
        add bx, KNOWN_OFF
        mov ax, ds
        sub ax, KNOWN_FROM_DS
        mov ds, ax
        mov di, fill_first
        call .list
        mov cl, ch
        mov di, fill_second
        call .list
        pop ds
        popa
        ret
.list:  or cl, cl               ; (CL of the spells at CS:DI, to a 0)
        jz .out
        movzx ax, byte [cs:di]
        or ax, ax
        jz .out
        inc di
        push bx
        add bx, ax
        test byte [bx], 0x0F
        jnz .known
        and byte [bx], 0xF0
        or byte [bx], 1
        dec cl
.known: pop bx
        jmp .list
.out:   ret
fill_first  db 7, 8, 0x0B, 9, 0
fill_second db 0x0F, 0x16, 0

; PROBE_DUAL_SPELLS: INT VEC_DUAL_SPELLS replaces "push 8 / push si / call 500:43h / add sp,4 /
; push 7 / push si / call 500:43h / add sp,4" (22 bytes: INT + 20 NOPs; DSUN.EXE 86DE4h) in the
; routine that changes a human's class (86C80h), where the game, its wizard spells taken away,
; makes a new preserver (member SI) know Grease and Magic Missile: it picks two 1st-level spells
; of its own instead on CHOOSE A SPELL (PICK_SPELLS), as a preserver does at a level up.
probe_dual_spells:
        sti
        push bx
        push cx
        push es
        mov cx, 2
        les bx, [LV_SHEETS]
        push ax
        imul ax, si, 0x47
        add bx, ax
        pop ax
        call kit_is_b           ; (the Scholar kit taken for the new preserver class: one more, as
                                ; at its level ups)
        db KIT_SCHOLAR
        jne .pick
        inc cx
.pick:  call ns_forget_all       ; (the new spells too: the game took its own)
        call pick_spells
        pop es
        pop cx
        pop bx
        iret

; PROBE_DUAL_KIT: INT VEC_DUAL_KIT replaces "cmp word [bp+8],0Ch" (4 bytes: INT + 2 NOPs; DSUN.EXE
; 86D90h) in the routine that changes a human's class (86C80h; SI the member, [BP+8] the new class,
; already first among its classes, as for the sphere a cleric's menu chose before). With kits, the
; game's three-choice menu (4D0:25h, the sphere's: DK_STUB) asks for the new class's kit, "KIT:
; NONE" its first row, the class's kits below it, a kit barred left off (DK_BANNED: an empty row,
; which the menu leaves out); the one
; clicked goes in the kit byte's two bits for the new class (KIT_AT). An Elementalist picks its
; second sphere the same way. Then, with weapon specialization, a new warrior (or Battle Mage) picks
; the weapon kinds it is due as at a level up (LV_CHECK, through the psionicists' pop-up, 620:57h:
; DK_PSI). The menu is overlay code of its own: the way back is put in a frame the overlay manager
; can fix up, as for PROBE_LV_PICK. Then the compare, its flags back to the JNZ (RETF 2).
DK_STUB    equ 0x41B4 - 0x4356          ; (the menu's stub segment, less DS: as PICK_STUB)
DK_MENU    equ 0x25
DK_PSI     equ 0x57                     ; (in PICK_STUB's: the psionicists' pop-up)
DK_X       equ 0x5C
DK_Y       equ 0x47
probe_dual_kit:
        sti
        pushad
        push es
        mov bx, sp              ; the interrupt frame at BX+34: IP, CS, flags
        test word [cs:rules_hi], RULE_HI_KITS
        jnz .ask
        test word [cs:rules], RULE_SPECIALIZE
        jz .done
.ask:   push word [ss:bx + 36]
        push word [ss:bx + 34]
        push bp
        mov bp, sp
        mov di, [bp]            ; (the routine's frame: [DI+8] the new class)
        mov ax, [ss:di + 8]
        call dk_ask
        pop bp
        pop ax                  ; the way back, as the overlay manager has left it
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
.done:  pop es
        popad
        cmp word [bp + 8], 0x0C
        retf 2

; DK_ASK: member SI (DS the game's), its new class AL first on its sheet: PROBE_DUAL_KIT's menus and
; weapon kinds. Registers changed.
dk_ask:
        les bx, [LV_SHEETS]
        imul cx, si, 0x47
        add bx, cx
        test word [cs:rules_hi], RULE_HI_KITS
        jz .specs
        movzx di, al
        dec di
        cmp di, 16
        ja .specs
        mov ch, [cs:di + kit_class_of]
        shl ch, 2               ; (CH the kit numbers' base: the creation class x 4)
        mov di, dk_opts + 8     ; the rows, the last first
        mov cl, 3
.opt:   mov al, ch
        add al, cl
        mov dx, dk_blank
        call dk_banned
        jc .row
        push si
        call kit_name_ptr
        mov dx, si
        pop si
.row:   mov [cs:di], dx
        mov [cs:di + 2], cs
        sub di, 4
        dec cl
        jnz .opt
        mov dx, dk_title
        call dk_menu            ; (AX the row: 1-3 a kit)
        dec ax
        cmp ax, 2
        ja .specs
        mov dl, al
        add al, ch
        inc al
        call dk_banned
        jc .specs
        push di
        call kit_place          ; (DI the oldest class's place: the new one's bits above it)
        mov cx, di
        pop di
        shl cl, 1
        inc dl
        movzx dx, dl
        shl dx, cl
        mov cl, [es:bx + KIT_BYTE]
        cmp cl, KIT_OPEN
        jne .set
        xor cl, cl
.set:   or cl, dl
        mov [es:bx + KIT_BYTE], cl
        cmp al, KIT_ELEMENTALIST
        jne .specs
        call dk_second
.specs: mov ax, ds
        add ax, PICK_STUB
        mov word [cs:lv_psi], DK_PSI
        mov [cs:lv_psi + 2], ax
        call lv_check
        ret

; DK_SECOND: a new Elementalist (sheet ES:BX, its cleric class first) picks its second sphere on
; the menu: the three that aren't its own; SPHERE2 that sphere + 1. Registers changed.
dk_second:
        and byte [es:bx + SPHERE2], ~SPHERE2_MASK   ; (the new spells known, above it, kept)
        movzx cx, byte [es:bx + 0x21]
        dec cx                  ; (CX its own sphere, 0-3: the cleric's class less 1)
        mov di, dk_opts
        xor dx, dx
.sphere:
        cmp dx, cx
        je .next
        push dx
        imul dx, dx, 6
        add dx, dk_spheres
        mov [cs:di], dx
        mov [cs:di + 2], cs
        pop dx
        add di, 4
.next:  inc dx
        cmp dx, 4
        jb .sphere
        mov dx, dk_title2
        call dk_menu
        dec ax
        cmp ax, 2
        ja .ret
        cmp ax, cx              ; (the rows skip its own)
        jb .take
        inc ax
.take:  inc ax
        or [es:bx + SPHERE2], al
.ret:   ret

; DK_MENU: AX the row picked on the game's three-choice menu (DK_STUB), its title CS:DX, its rows
; DK_OPTS (far). ES:BX kept; others but CX, SI changed.
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
        mov ax, ds
        add ax, DK_STUB
        mov word [cs:dk_far], DK_MENU
        mov [cs:dk_far + 2], ax
        call far [cs:dk_far]
        add sp, 22
        pop es
        pop si
        pop cx
        pop bx
        ret

; DK_BANNED: CF set if kit AL may not go with the other classes of sheet ES:BX (its places from 1)
; or their kits (asleep too): its DUAL_BANS hold one of the classes (KIT_BANS), or a kit's and its
; are a pair KIT_PAIRS bars (kits.dual_kit_banned). All registers kept.
dk_banned:
        pushad
        mov cl, al
        call kit_bans           ; (EDX the classes it bars)
        call kit_place
        jc .ok
.place: or di, di
        jz .ok
        movzx eax, byte [es:bx + di + 0x21]
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
kit_pair:
        push dx
        push si
        mov dx, ax
        xchg dl, dh
        mov si, kit_pairs
.next:  cmp word [cs:si], 0
        je .free
        cmp [cs:si], ax
        je .barred
        cmp [cs:si], dx
        je .barred
        add si, 2
        jmp .next
.free:  clc
        jmp .out
.barred:
        stc
.out:   pop si
        pop dx
        ret
; Kits barred from going together (kits.KIT_PAIRS): one needing a shield and one forbidding it
; (Arena Champion, Sentinel; Twin-blade, Shinobi, Ravager); two-weapon fighting and the off hand
; free of weapons (Twin-blade, Healer); a two-handed weapon and weapons it can't be (Brute;
; Shinobi, Lifebinder); two ACs that grow by level, one on the other (Ravager, Grove Warden); a
; warrior's THAC0 twice over (Swashbuckler, Crusader, Battle Mage, Mind Warrior). 0 ends it.
kit_pairs  db KIT_CHAMPION, KIT_TWIN_BLADE,  KIT_CHAMPION, KIT_SHINOBI,  KIT_CHAMPION, KIT_RAVAGER
           db KIT_SENTINEL, KIT_TWIN_BLADE,  KIT_SENTINEL, KIT_SHINOBI,  KIT_SENTINEL, KIT_RAVAGER
           db KIT_TWIN_BLADE, KIT_HEALER,  KIT_BRUTE, KIT_SHINOBI,  KIT_BRUTE, KIT_LIFEBINDER
           db KIT_RAVAGER, KIT_GROVE_WARDEN     ; (two ACs of their own by level, one on the other)
           db KIT_SWASHBUCKLER, KIT_CRUSADER,  KIT_SWASHBUCKLER, KIT_BATTLE_MAGE  ; (a warrior's THAC0
           db KIT_SWASHBUCKLER, KIT_MIND_WARRIOR,  KIT_CRUSADER, KIT_BATTLE_MAGE  ;   twice over)
           db KIT_CRUSADER, KIT_MIND_WARRIOR,  KIT_BATTLE_MAGE, KIT_MIND_WARRIOR
           dw 0
dk_opts    times 3 dd 0
dk_far     dd 0
dk_title   db 'KIT: NONE', 0
dk_title2  db 'SPHERE 2: NONE', 0
dk_blank   db 0
dk_spheres db 'AIR', 0, 0, 0, 'EARTH', 0, 'FIRE', 0, 0, 'WATER', 0

; PROBE_CR_SPELLS: INT VEC_CR_SPELLS replaces "mov ax,[bp-2]" (3 bytes: INT + NOP; DSUN.EXE 66F2Dh) in
; the creation screen's DONE (overlay 65480h), where the game makes a new preserver (SI, its
; preserver level [BP-2]) know spells of its choosing: Grease and Magic Missile at 1st level,
; Shield and Wall of Fog too at 2nd, Fog Cloud and Mirror Image too at 3rd. It picks as many on
; CHOOSE A SPELL instead (PICK_SPELLS: 2, 4, or 4 and two of 2nd level), a Scholar one more for
; each level (KIT_MADE), then on past the game's (CR_SPELLS_PAST). CHOOSE A SPELL is overlay code
; of its own: the way back is put in a frame the overlay manager can fix up, as for PROBE_LV_PICK
; (without it the game's code is lost). Another level, or the grants run for the game's own
; party (START GAME with no party made calls them from 65480h+6FBh, not DONE's 66556h): AX [BP-2],
; on as before. (The creature's status can't tell the two: a character being made reads Okay
; here too, as the game's party does.)
CR_SPELLS_PAST equ 0x66F83 - 0x66F2F    ; (past the game's grants, less the address after the INT)
CR_FROM_DONE  equ 0x66F2F - 0x66556    ; (the grants' way back into DONE, less the INT's)
probe_cr_spells:
        push bp
        mov bp, sp
        push ds
        push bx
        lds bx, [bp + 2]
        mov bl, [bx]            ; the byte after the INT: its NOP, or another site's number (RL_*)
        mov [cs:rl_site], bl
        cmp bl, 0x90
        je .own
        inc word [bp + 2]       ; (past the site's number)
.own:   pop bx
        pop ds
        pop bp
        cmp byte [cs:rl_site], 0x90
        jne rl_sites
        mov ax, [bp - 2]
        or ax, ax
        jz .iret
        cmp ax, 3
        ja .iret
        push bx                 ; only a character made on the creation screen picks (the grants
        mov bx, sp              ;   called by DONE, in the same overlay as the INT, [BP+2] and
        push ax                 ;   [BP+4]): the game's own party keeps the game's spells
        mov ax, [ss:bx + 2]
        sub ax, CR_FROM_DONE
        cmp ax, [bp + 2]
        jne .from
        mov ax, [ss:bx + 4]
        cmp ax, [bp + 4]
.from:  pop ax
        pop bx
        je .pick
.iret:  iret
.pick:  sti
        pushad
        push es
        push ax                 ; (a new character knows none of the new spells: NS_SHEET)
        mov ax, si
        call creature_sheet
        call ns_forget_all
        pop ax
        mov bx, sp              ; the interrupt frame at BX+34: IP, CS, flags
        mov cx, 2               ; (CL 1st-level picks, CH 2nd-level)
        cmp al, 1
        je .scholar
        mov cl, 4
        cmp al, 3
        jne .scholar
        mov ch, 2
.scholar:
        push ax
        call kit_made
        cmp al, KIT_SCHOLAR
        pop ax
        jne .frame
        add cl, al
.frame: push word [ss:bx + 36]
        mov ax, [ss:bx + 34]
        add ax, CR_SPELLS_PAST
        push ax
        push bp
        mov bp, sp
        call pick_spells
        pop bp
        pop ax                  ; the way back, as the overlay manager has left it
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
        pop es
        popad
        iret

; Creation's scores and hit points as rolled (RULE_HI_ROLLED; game.RULE_ROLLED). The game lets
; a click raise any score to its most and set the hit points anywhere from the least to the most
; the classes could roll. With the rule, a hit point click does nothing, and a score is raised
; only while the six add up to no more than the die gave (RL_POOL): lowering one frees points
; for another. Under CHR the screen shows the six's total and the die's: "SUM:100/102". A click
; on CON moves the hit points as far as it moves the most they may be (CON's bonus for each level,
; as the game counts it), where the game alone keeps them between the least and most.
; No vectors are left: these sites share VEC_CR_SPELLS, the INT followed by the site's number
; (PROBE_CR_SPELLS's own has its NOP), which the return address is moved past.
RL_SCORE equ 1                  ; DSUN.EXE 655C6h, in the score click (65480h)
RL_HP    equ 2                  ; 63A49h, in the hit point click (63A24h)
RL_ROLL  equ 3                  ; 65944h, 65979h, 659AEh: the die's three loops (657BBh)
RL_SUM   equ 4                  ; 65185h, in the scores' redraw (65168h)
RL_CON   equ 5                  ; 63946h, in the score click's CON case (63915h)
RL_TRY   equ 6                  ; 6498Bh, in an ability's roll (6490Dh): each 4d4, whatever the rule
PK_HOVER equ 7                  ; 85F44h, the weapon window's event loop: the slot under the pointer
RG_TWO   equ 8                  ; 5961Fh, the two-weapon adjustment's test for a ranger
RL_HP_MAX equ 0x4996            ; DS: the most hit points the classes could roll (655D6h's)
RL_BOX   equ 0x0F62             ; DS: the screen's boxes (x1, y1, x2, y2), the scores' first
RL_LABEL_X equ 23               ; "SUM:" this far left of the scores' x
RL_ROW_Y equ 6 * 7 - 2          ; the line under CHR: 7 apart, from 2 above the box's top
rl_sites:
        cmp byte [cs:rl_site], RL_SCORE
        je rl_score
        cmp byte [cs:rl_site], RL_HP
        je rl_hp
        cmp byte [cs:rl_site], RL_ROLL
        je rl_roll
        cmp byte [cs:rl_site], RL_SUM
        je rl_sum
        cmp byte [cs:rl_site], RL_CON
        je rl_con
        cmp byte [cs:rl_site], RL_TRY
        je rl_try
        cmp byte [cs:rl_site], PK_HOVER
        je pk_hover
        cmp byte [cs:rl_site], RG_TWO
        je rg_two
        cmp byte [cs:rl_site], NS_SITE
        jae ns_sites
        iret

; RG_TWO: "test word es:[bx+12h],200h" (5961Fh; 6 bytes: the site's number and 3 NOPs after the
; INT), where the routine giving an attack's to-hit adjustment for two weapons ready (595ECh)
; asks whether the attacker (sheet ES:BX, creature [BP-2]) is a ranger, who has none: its "jnz"
; after it kept. With RULE_TWO_WEAPONS a ranger (its kits too, but a Justifier) has none only in
; light armour (HEAVY_WORN): in other armour ZF is set, as for anyone else, and PROBE_TWO gives
; AD&D's. A Justifier has none in any armour.
rg_two:
        pushad
        push es
        mov di, sp
        and word [ss:di + 38], ~0x40
        test word [es:bx + 0x12], 0x200
        jz .plain
        test byte [cs:rules], RULE_TWO_WEAPONS
        jz .out
        call kit_is_b           ; (a Justifier: none in any armour; kits.py)
        db KIT_JUSTIFIER
        je .out
        mov dx, [bp - 2]
        call heavy_worn
        jnc .out
.plain: or word [ss:di + 38], 0x40
.out:   pop es
        popad
        iret

; PK_HOVER: "or ax,ax / jnz 85F5Dh" (85F44h; 4 bytes: the site's number and a NOP after the INT),
; in the pop-up's event loop (85F2Ch), each time round: AX 0 when 110:965h has an event to deal
; with. In weapon mode, the slot the pointer is on (INT 33h; the window where PROBE_PK_WIN puts it,
; the slots where weaponpages has them) named in the window's two lines, "SPECIALIZE IN" (or
; "EXPERT IN", PK_WORD) and the kind, as the powers' handler names a power (864B9h, with the
; routine that rubs out the old lines, 85CC9h), and the title put back once it is on none; drawn
; only when that changes. (A slot is a button, and a button the pointer is on takes the pointer:
; the powers' cells' handler never hears of it.)
PK_HOVER_PAST equ 0x85F47           ; (the address after the site's number)
PK_LINES      equ 0x85CC9 - PK_HOVER_PAST
PK_NO_EVENT   equ 0x85F5D - PK_HOVER_PAST
PK_SEL_SEG    equ 0x85F75 - PK_HOVER_PAST ; ("mov ax,348h" at 85F74h: the character's number's
PK_SELECTED   equ 0x25B             ;   segment, as fixed up; its name at [1665h] + 3Ah each, +28h)
PK_NAMES      equ 0x1665
PK_SLOTS_X    equ PK_PICK_X + (214 - 6 * 34 + 2) / 2 ; (the first slot's corner on the screen:
PK_SLOTS_Y    equ PK_PICK_TOP + 7                    ;   weaponpages' left and PICK_TOP)
PK_PITCH      equ 34
PK_SLOT       equ 32
pk_hover:
        pushad
        push es
        mov di, sp
        push word [ss:di + 38]  ; (the loop's own flags)
        popf
        mov bx, [ss:di + 30]    ; (AX as it was)
        or bx, bx
        jz .flags
        add word [ss:di + 34], PK_NO_EVENT ; (no event: on round the loop, as the JNZ)
.flags: cmp byte [cs:lv_mode], 0
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
        cmp ax, 16
        jb .got
.none:  mov al, 0xFF
.got:   cmp al, [cs:lv_hovered]
        je .out
        mov [cs:lv_hovered], al
        les bx, [ss:di + 34]    ; (the overlay's code, at the INT's way back)
        cmp al, 0xFF
        jne .slot
        mov ax, [es:bx + PK_SEL_SEG]
        push es
        mov es, ax
        mov ax, [es:PK_SELECTED]
        pop es
        imul ax, ax, 0x3A
        add ax, [PK_NAMES]
        add ax, 0x28
        push word [PK_NAMES + 2]
        push ax
        push cs
        push word lv_title
        jmp .draw
.slot:  push cs
        xor ah, ah
        call pk_word
        mov si, ax
        add si, si
        mov ax, [cs:ef_kinds + si]
        inc ax                  ; (the kinds' names begin with two spaces)
        inc ax
        push ax
        push cs
        push dx
.draw:  push dword (PK_PICK_SECOND << 16) | 0xFE
        push dword (PK_PICK_INK << 16) | PK_PICK_WIDTH
        push word PK_PICK_Y
        push dword [PK_WINDOW]
        lea ax, [bx + PK_LINES]
        mov [cs:lv_lines_call], ax
        mov [cs:lv_lines_call + 2], es
        call far [cs:lv_lines_call]
        add sp, 0x16
.out:   pop es
        popad
        iret

; PK_WORD: DX the first line for kind AX: "EXPERT IN" when LV_MEMBER would have expertise with it
; once picked, else "SPECIALIZE IN" (the kind put in the sheet's first empty SPEC_SLOTS byte for
; SPEC_OF_SHEET to judge, its plain weapon's, and taken out again). DS the game's; others kept.
pk_word:
        push ax
        push bx
        push si
        push es
        mov dx, lv_hover
        les bx, [LV_SHEETS]
        push ax
        imul ax, [cs:lv_member], 0x47
        add bx, ax
        pop ax
        xor si, si
.slot:  cmp byte [es:bx + si + SPEC_SLOTS], 0
        je .put
        inc si
        cmp si, SPEC_COUNT
        jb .slot
        jmp .ret
.put:   push si
        inc al
        mov [es:bx + si + SPEC_SLOTS], al
        dec al
        mov si, ax
        shl si, 1
        mov si, [cs:si + wp_plain]
        push dx
        call spec_of_sheet
        mov al, dl
        pop dx
        pop si
        mov byte [es:bx + si + SPEC_SLOTS], 0
        cmp al, SPEC_EXPERT
        jne .ret
        mov dx, lv_expert
.ret:   pop es
        pop si
        pop bx
        pop ax
        ret

; CR_TOTAL: DX the six scores of the creature being made (DS:[11A0h], from +22h) added up.
; DS the game's; others kept.
rl_total:
        push es
        push ax
        push bx
        push cx
        les bx, [0x11A0]
        xor ax, ax
        xor dx, dx
        mov cx, 6
.add:   mov al, [es:bx + 0x22]
        add dx, ax
        inc bx
        loop .add
        pop cx
        pop bx
        pop ax
        pop es
        ret

; RL_SCORE replaces "mov al,[bp-2]" (DSUN.EXE 655C6h), where a click sets a score (ES:BX the
; creature plus the score's number, [BP-2] the value the click gives: one more or one less, or
; round from the most to the least or back). A raise is kept to the points to spare.
rl_score:
        push word [RL_HP_MAX]   ; (the most hit points before the click, for RL_CON)
        pop word [cs:rl_old_max]
        mov al, [bp - 2]
        test word [cs:rules_hi], RULE_HI_ROLLED
        jz .out
        cmp al, [es:bx + 0x22]
        jbe .out                ; lowered: always
        push cx
        push dx
        mov cx, [cs:rl_pool]
        jcxz .done              ; (no roll seen)
        call rl_total
        sub cx, dx              ; the points to spare
        jg .some
        mov al, [es:bx + 0x22]  ; none: as it was
        jmp .done
.some:  add cl, [es:bx + 0x22]  ; the most it may be
        cmp al, cl
        jbe .done
        mov al, cl
.done:  pop dx
        pop cx
.out:   iret

; RL_HP replaces "add ax,[bp-2]" (63A49h), where a click adds 1 or -1 (BP-2) to the hit points.
rl_hp:
        test word [cs:rules_hi], RULE_HI_ROLLED
        jnz .out
        add ax, [bp - 2]
.out:   iret

; RL_CON replaces "les bx,[119Ch]" (+ NOP; 63946h) after a click on CON has had the game work out
; the hit points' least and most again (655D6h, not rolling): the sheet's hit points (+8) move as
; far as the most did (RL_SCORE kept it before the click), so a CON raised adds its bonus and one
; lowered takes it off; the game then keeps them between the least and most, as before.
rl_con:
        les bx, [0x119C]
        test word [cs:rules_hi], RULE_HI_ROLLED
        jz .out
        push ax
        mov ax, [RL_HP_MAX]
        sub ax, [cs:rl_old_max]
        add [es:bx + 8], ax
        pop ax
.out:   iret

; RL_TRY replaces "add ax,[499Ah]" (+ NOP; 6498Bh), where an ability's roll (6490Dh, the ability at
; [BP+8], DI the try, 0-3) adds the race's adjustment + 4 to a 4d4 (AX): the 4d4 kept in RL_TRIES,
; and RL_SEQ counted, for the dice log.
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
        add ax, [0x499A]
        iret

; RL_ROLL replaces "mov es:[bx+22h],al" (+ NOP) in the die's three loops (one for each kind of
; class), SI the score: after CHR, the six's total is the die's (DI 1, a roll), or no less
; (DI 0: the scores kept, raised to a new class's least).
rl_roll:
        mov [es:bx + 0x22], al
        cmp si, 5
        jne .out
        push dx
        call rl_total
        or di, di
        jnz .set
        cmp dx, [cs:rl_pool]
        jbe .done
.set:   mov [cs:rl_pool], dx
.done:  pop dx
.out:   iret

; RL_SUM replaces "add sp,4" (65185h) in the scores' redraw, after the game has put back what
; was under them (its box, RL_BOX, the line under CHR and to x 77 too: gamepatch.py's
; "cr_sum_box"): "SUM:" and the totals, the six's and the die's, in the game's lettering.
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
        mov eax, [0x11A4]       ; the screen's window
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
        pop es
        popad
.back:  push word [cs:rl_fl]
        push word [cs:rl_cs]
        push word [cs:rl_ip]
        iret

rl_site  db 0
rl_old_max dw 0                 ; (RL_HP_MAX before a score's click)
rl_pool  dw 0                   ; (RL_POOL) the die's total, the most the six may add up to (0: none seen)
rl_ip    dw 0
rl_cs    dw 0
rl_fl    dw 0
rl_label db 'SUM:', 0
rl_text  db '000/000', 0

; PROBE_EF_CLICK: INT VEC_EF_CLICK replaces "mov si,[bp+8]" (3 bytes: INT + NOP; DSUN.EXE 7EC9Eh) in the
; Effects screen's handler for its cells (7EC97h; [BP+8] the cell's button, from 2BCDh, [BP+0Ah] the
; event, EF_CLICKED a click), cells from EF_CELLS on being the lower panel's: a click there while EF_DRAW's
; lines take more than a page (EF_COUNT) shows the next page (EF_NEXT): the window drawn again as
; the handler does after a cell's label (118:618h, DS:[11A4h] the window: its background, then its
; contents, 7E620h, and EF_DRAW in them), the way back in a frame the overlay manager can fix up (as
; PROBE_LV_PICK), and out of the handler (7EDF5h). Else SI [BP+8].
EF_CELL_ID   equ 0x2BCD
EF_CLICKED   equ 0x20                   ; (the events: 2 the pointer onto a cell, 40h a button down,
                                        ;   20h up again: a click)
EF_CLICK_OUT equ 0x7EDF5 - 0x7ECA0      ; (the handler's way out, less the address after the INT)
EF_REDRAW_CALL equ 0x7EDEE - 0x7ECA0    ; (its "call 118:618h", the window drawn again, less that)
probe_ef_click:
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
        mov bx, sp              ; the interrupt frame at BX+34: IP, CS, flags
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
        push dword [PK_WINDOW]
        call far [cs:ef_far]
        add sp, 4
        pop bp
        pop ax                  ; the way back, as the overlay manager has left it
        pop dx
        mov bx, sp
        mov [ss:bx + 34], ax
        mov [ss:bx + 36], dx
        pop es
        popad
        iret

; PROBE_SOUND_42 / PROBE_SOUND_44: INT VEC_SOUND_42 replaces "mov dx,[es:bx+42h]" (4 bytes: INT + 2
; NOPs; DSUN.EXE 78FDAh) and INT VEC_SOUND_44 "mov ax,[es:bx+44h]" (81DE3h): two sound numbers on
; the character sheet (ES:BX), read as words by the game, though the bytes above them are the
; kit (KIT_BYTE, 43h) and the second sphere (SPHERE2, 45h); the low byte alone (0 above it in every one of
; the game's sheets), so a kit or a sphere doesn't play another sound.
probe_sound_42:
        movzx dx, byte [es:bx+0x42]
        iret
probe_sound_44:
        movzx ax, byte [es:bx+0x44]
        iret

; PROBE_PICK_LIST: INT VEC_PICK_LIST replaces "mov di,ax" (2 bytes; DSUN.EXE 8563Fh) in the CHOOSE A
; SPELL window, after the game's routine put the spells the character may learn in the list (the
; segment of "mov ax,348h" before, PICK_LIST_SEG, at 7, a word each; AX how many; the character at
; that segment's 25Bh; the highest spell level DS:[4AECh]): for a Shinobi, its own spells
; (SHINOBI_SPELLS) up to that level that it doesn't know yet. DI how many, as the code had it.
PICK_LIST_SEG equ 0x8562E - 0x85641   ; (the segment's word in "mov ax,348h", less the INT's way back)
PICK_LIST    equ 7
PICK_WHO     equ 0x25B
PICK_MOST    equ 0x4AEC
probe_pick_list:
        mov di, ax
        push ax
        push bx
        push cx
        push dx
        push si
        push es
        push bp
        les bx, [PICK_SHEET]
        call kit_is_b
        db KIT_SHINOBI
        jne .int
        mov bp, sp
        les si, [ss:bp + 14]    ; (the INT's way back: CS:IP)
        mov es, [es:si + PICK_LIST_SEG]
        mov cx, [es:PICK_WHO]   ; (CX the character)
        mov dl, [PICK_MOST]     ; (DL the highest spell level on offer)
        xor di, di              ; (the list's length)
        mov si, SHINOBI_SPELLS
.spell: cmp [cs:si + 1], dl
        ja .next
        movzx ax, byte [cs:si]
        mov bx, cx
        call shinobi_knows
        jc .next                ; (known)
        mov [es:PICK_LIST + di], ax
        add di, 2
.next:  add si, 2
        cmp si, SHINOBI_SPELLS_END
        jb .spell
        shr di, 1
        jmp .out
.int:   test word [cs:rules_hi], RULE_HI_INT    ; (a preserver: the list without the spells of a
        jz .out                                 ; level it knows its INT's most of)
        call is_preserver
        jnc .out
        mov bp, sp
        les si, [ss:bp + 14]
        mov es, [es:si + PICK_LIST_SEG]
        mov si, [es:PICK_WHO]
        mov dx, di              ; (DX the game's count)
        xor di, di
        xor bx, bx
.each:  cmp bx, dx
        jae .counted
        push bx
        shl bx, 1
        mov ax, [es:PICK_LIST + bx]
        pop bx
        call spell_level_of
        push ax
        call level_full
        pop ax
        jc .skip
        push di
        shl di, 1
        mov [es:PICK_LIST + di], ax
        pop di
        inc di
.skip:  inc bx
        jmp .each
.counted:
.out:   pop bp
        pop es
        pop si
        pop dx
        pop cx
        pop bx
        pop ax
        iret

; PICK_INT_ANY: (PROBE_PICK_ANY, not a Shinobi: SI the character, ES:BX its sheet, AX its
; preserver level) with RULE_HI_INT, AX 0 (CHOOSE A SPELL not opened) when no wizard spell it
; doesn't know is left at a spell level on offer (up to (AX + 1) / 2, no more than PICK_CAP's) that
; isn't full (LEVEL_FULL). DS the game's; others kept.
pick_int_any:
        test word [cs:rules_hi], RULE_HI_INT
        jz .ret
        cmp ax, 0
        jle .ret
        call is_preserver
        jnc .ret
        push ax
        push bx
        push cx
        push dx
        inc ax
        shr ax, 1
        mov dl, al              ; (DL the highest spell level on offer)
        mov al, [cs:pick_cap]
        or al, al
        jz .capped
        cmp dl, al
        jbe .capped
        mov dl, al
.capped:
        imul bx, si, KNOWN_SIZE
        add bx, KNOWN_OFF
        mov al, 1
.spell: push ds
        push ax
        mov ax, ds
        sub ax, KNOWN_FROM_DS
        mov ds, ax
        pop ax
        push bx
        movzx cx, al
        add bx, cx
        test byte [bx], 0x0F
        pop bx
        pop ds
        jnz .next               ; (known)
        call spell_level_of
        cmp cl, dl
        ja .next
        push ax
        call level_full
        pop ax
        jnc .found
.next:  inc al
        cmp al, WIZARD_LAST
        jbe .spell
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .none
        call ns_setup
        mov al, NS_FIRST        ; (and the new spells: NS_KNOWS; those with room for their records)
.new:   push ax
        call ns_new
        pop ax
        jnc .new_next
        push ax
        push cx
        mov cl, al
        sub cl, NS_FIRST
        mov ax, si
        call ns_knows
        pop cx
        pop ax
        jc .new_next
        call spell_level_of
        cmp cl, dl
        ja .new_next
        push ax
        call level_full
        pop ax
        jnc .found
.new_next:
        inc al
        cmp al, NS_LAST
        jbe .new
.none:  pop dx
        pop cx
        pop bx
        pop ax
        xor ax, ax              ; (nothing to learn)
        ret
.found: pop dx
        pop cx
        pop bx
        pop ax
.ret:   ret

; PROBE_SCROLL_LEARN: INT VEC_SCROLL_LEARN replaces "or ax,ax" (2 bytes; DSUN.EXE 8B6D3h, then the
; game's "jz", to "YOU ALREADY KNOW THIS SPELL") after the game's check whether the character on
; show (the segment of "mov ax,348h" before, its 25Bh) may learn a scroll's spell ([BP-3] of the
; game's frame; the game's only check is that it doesn't know it yet): none for a Shinobi, who
; learns only at a level up; with RULE_HI_INT, a preserver's try at a wizard spell as INT_LEARN has
; it. ZF as "or ax,ax" leaves it.
SCROLL_WHO_SEG equ 0x8B6C2 - 0x8B6D5
probe_scroll_learn:
        or ax, ax
        jz .flags
        push bx
        push si
        push es
        push bp
        mov bp, sp
        les si, [ss:bp + 8]     ; (the INT's way back)
        mov es, [es:si + SCROLL_WHO_SEG]
        mov si, [es:PICK_WHO]   ; (SI the reader)
        imul bx, si, 0x47
        push si
        les si, [0x1661]
        add bx, si
        pop si
        call kit_is_b
        db KIT_SHINOBI
        jne .int
        xor ax, ax
        jmp .keep
.int:   push dx
        mov bp, [ss:bp]         ; (the game's frame: [BP-3] the spell)
        mov dl, [bp - 3]
        call int_learn
        pop dx
.keep:  pop bp
        pop es
        pop si
        pop bx
.flags: push bp                 ; (ZF in the flags IRET gives back)
        mov bp, sp
        and word [bp + 6], ~0x40
        or ax, ax
        jnz .done
        or word [bp + 6], 0x40
.done:  pop bp
        iret

; INT_LEARN (RULE_HI_INT; dsloader/intlearn.py): party member SI, its sheet ES:BX, tries to learn
; wizard spell DL from a scroll, AX not 0 (the game would teach it). A preserver's INT (the creature
; record's) gives, as AD&D's table, the chance to learn a spell (INT_CHANCE) and the most spells of a
; spell level it may know (INT_MOST): knowing that many of the spell's level, it can't (AX 0, and
; PROBE_LEARN_REFUSED's message, LEARN_FULL_TEXT: the scroll is kept); else a d100 above the chance
; and it fails (AX kept: the game teaches it and uses the scroll up, PROBE_LEARN_SAID takes the
; spell back and says so). The try is told to the Loader (LEARN_SEQ...). DS the game's; others kept.
INT_FIRST    equ 9                      ; (the rows' first INT; a preserver's least)
INT_ROWS     equ 17                     ; (9 to 25)
INT_ALL      equ 255                    ; (no most)
int_chance   db 35, 40, 45, 50, 55, 60, 65, 70, 75, 85, 95, 96, 97, 98, 99, 100, 100
int_most     db 6, 7, 7, 7, 9, 9, 11, 11, 14, 18, INT_ALL, INT_ALL, INT_ALL, INT_ALL, INT_ALL, INT_ALL, INT_ALL
LEARN_LEARNT equ 0
LEARN_FAILED equ 1
LEARN_FULL   equ 2
SPELL_LEVELS_SEG equ 0x3FB9 - 0x4356    ; the spells' table (7 bytes a spell): its segment less DS's ...
SPELL_LEVELS equ 0x19C                  ; ... and each spell's level there
learn_msg    db 0                       ; (LEARN_FAILED or LEARN_FULL: the game's message to change)
int_learn:
        or ax, ax
        jz .ret
        test word [cs:rules_hi], RULE_HI_INT
        jz .ret
        cmp dl, WIZARD_LAST
        jbe .wizard
        push ax                         ; (or a new spell: NEW SPELLS)
        movzx ax, dl
        call ns_new
        pop ax
        jnc .ret
.wizard:
        call is_preserver
        jnc .ret
        push ax
        push bx
        push cx
        mov ax, si
        mov [cs:learn_who], al
        mov [cs:learn_spell], dl
        call int_row                    ; (BX the INT's row, AL the INT)
        mov [cs:learn_int], al
        mov al, [cs:int_chance + bx]
        mov [cs:learn_chance], al
        mov al, dl
        call spell_level_of             ; (CL the spell's level)
        call level_full                 ; (AL the spells of that level known)
        jnc .roll
        mov [cs:learn_roll], al
        mov byte [cs:learn_result], LEARN_FULL
        mov byte [cs:learn_msg], LEARN_FULL
        pop cx
        pop bx
        pop ax
        xor ax, ax
        jmp .told
.roll:  call d100
        mov [cs:learn_roll], al
        mov byte [cs:learn_result], LEARN_LEARNT
        cmp al, [cs:learn_chance]
        jbe .out
        mov byte [cs:learn_result], LEARN_FAILED
        mov byte [cs:learn_msg], LEARN_FAILED
.out:   pop cx
        pop bx
        pop ax
.told:  inc word [cs:learn_seq]
.ret:   ret

; IS_PRESERVER: CF set if sheet ES:BX has the preserver class among its classes. All kept.
is_preserver:
        cmp byte [es:bx + 0x21], PRESERVER_CLASS
        je .yes
        cmp byte [es:bx + 0x22], PRESERVER_CLASS
        je .yes
        cmp byte [es:bx + 0x23], PRESERVER_CLASS
        je .yes
        clc
        ret
.yes:   stc
        ret

; INT_ROW: BX the row of INT_CHANCE and INT_MOST for party member SI's INT (its creature record's,
; 9 or less the first row, 25 or more the last), AL the INT. DS the game's; others kept.
int_row:
        push es
        les bx, [CREATURES]
        push ax
        imul ax, si, 0x3A
        add bx, ax
        pop ax
        mov al, [es:bx + 0x25]          ; (the abilities from +22h: STR, DEX, CON, INT)
        movzx bx, al
        sub bx, INT_FIRST
        jge .high
        xor bx, bx
.high:  cmp bx, INT_ROWS - 1
        jbe .row
        mov bx, INT_ROWS - 1
.row:   pop es
        ret

; SPELL_LEVEL_OF: CL the spell level of spell AL. DS the game's; others kept.
spell_level_of:
        push ax
        push bx
        push es
        mov bx, ds
        add bx, SPELL_LEVELS_SEG
        mov es, bx
        movzx bx, al
        imul bx, bx, 7
        mov cl, [es:bx + SPELL_LEVELS]
        pop es
        pop bx
        pop ax
        ret

; LEVEL_FULL: CF set if party member SI knows as many wizard spells of spell level CL as its INT
; lets it (INT_MOST; RULE_HI_INT), AL how many it knows. DS the game's; others kept.
level_full:
        push bx
        push dx
        push si
        push ds
        mov dl, cl
        call int_row
        mov dh, [cs:int_most + bx]      ; (DH the most)
        mov cl, dl
        call ns_count_of                ; (the new spells of that level it knows: NS_SHEET)
        push ax
        imul bx, si, KNOWN_SIZE
        add bx, KNOWN_OFF
        mov si, ds
        mov ax, ds
        sub ax, KNOWN_FROM_DS
        mov ds, ax
        pop ax
        mov ah, al                      ; (AH the count)
        mov al, 1                       ; (AL the spell)
.spell: test byte [bx + 1], 0x0F        ; (known: the game's low four bits)
        jz .next
        push ds
        mov ds, si
        call spell_level_of
        pop ds
        cmp cl, dl
        jne .next
        inc ah
.next:  mov cl, dl
        inc bx
        inc al
        cmp al, WIZARD_LAST
        jbe .spell
        mov al, ah
        cmp al, dh                      ; (CF set while fewer)
        cmc
        pop ds
        pop si
        pop dx
        pop bx
        ret

; D100: AL 1 to 100, from the helper's own generator (stirred by the BIOS's timer ticks). Others kept.
d100_seed dw 0x1234
d100:
        push dx
        push es
        push cx
        mov ax, 0x40
        mov es, ax
        mov ax, [es:0x6C]
        add ax, [cs:d100_seed]
        mov cx, 25173
        mul cx
        add ax, 13849
        mov [cs:d100_seed], ax
        mov al, ah                      ; (the high byte: the better half of such a generator)
        xor ah, ah
        mul word [cs:d100_hundred]
        mov al, ah
        inc al                          ; (0-255 scaled to 1-100)
        pop cx
        pop es
        pop dx
        ret
d100_hundred dw 100

; PROBE_LEARN_SAID: INT VEC_LEARN_SAID replaces "push ds / push 33F1h" (4 bytes: INT + 2 NOPs;
; DSUN.EXE 8B712h), the scroll's spell taught and the scroll used up, its message ("YOU LEARN THE
; SPELL"): after INT_LEARN's failed d100, the spell taken back (the known spells' table, DS less
; KNOWN_FROM_DS) and LEARN_FAILED_TEXT pushed in its place. PROBE_LEARN_REFUSED: INT
; VEC_LEARN_REFUSED replaces "push ds / push 3405h" (8B719h, "YOU ALREADY KNOW THIS SPELL"): after
; INT_LEARN found the spell's level full, LEARN_FULL_TEXT.
learn_failed_text db 'YOU FAIL TO LEARN THE SPELL', 0
learn_full_text   db 'TOO MANY SPELLS OF THAT LEVEL', 0
lm_ip dw 0
lm_cs dw 0
lm_fl dw 0
probe_learn_said:
        cmp byte [cs:learn_msg], LEARN_FAILED
        jne .game
        push ax
        push bx
        push ds
        movzx ax, byte [cs:learn_spell]
        call ns_new
        jnc .table
        push cx                 ; (a new spell: its bit in the sheet, NS_SHEET_FORGET)
        push es
        mov cl, al
        movzx ax, byte [cs:learn_who]
        call thing_sheet
        call ns_sheet_forget
        pop es
        pop cx
        jmp .taken
.table: movzx bx, byte [cs:learn_who]
        imul bx, bx, KNOWN_SIZE
        add bx, KNOWN_OFF
        add bx, ax
        mov ax, ds
        sub ax, KNOWN_FROM_DS
        mov ds, ax
        and byte [bx], 0xF0
.taken: pop ds
        pop bx
        pop ax
        mov byte [cs:learn_msg], 0
        pop word [cs:lm_ip]
        pop word [cs:lm_cs]
        pop word [cs:lm_fl]
        push cs
        push learn_failed_text
        jmp learn_back
.game:  pop word [cs:lm_ip]
        pop word [cs:lm_cs]
        pop word [cs:lm_fl]
        push ds
        push 0x33F1
learn_back:
        push word [cs:lm_fl]
        push word [cs:lm_cs]
        push word [cs:lm_ip]
        iret

probe_learn_refused:
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
        push 0x3405
        jmp learn_back

; PROBE_RANGER_CAST: INT VEC_RANGER_CAST replaces "sub dx,7" (3 bytes: INT + NOP; DSUN.EXE 81B6Ah)
; in the game's caster level routine (its [BP+6] the combatant, [BP+8] the spell), where a ranger's
; level counts 7 less: DX that much less, a Seeker's 5, a Justifier's 9 (kits.ranger_cast_drop),
; which also sets the spell levels it may cast (half the caster level, rounded up). Others kept.
probe_ranger_cast:
        push ax
        push bx
        push es
        push dx
        mov ax, ds
        add ax, THINGS_SEG
        mov es, ax
        imul bx, [bp + 6], 3
        mov ax, [es:bx + COMBATANT_CREATURE]
        pop dx
        mov bx, 7
        call cr_is
        db KIT_SEEKER
        jne .justifier
        mov bx, 5
.justifier:
        call cr_is
        db KIT_JUSTIFIER
        jne .take
        mov bx, 9
.take:  sub dx, bx
        pop es
        pop bx
        pop ax
        iret

; KIT_SAVE: SI (a saving throw's modifiers) with the kit's of the one saving (thing DI) against
; spell AX: a Sentinel's -1 against a wizard's or priest's spell (0-137, not a psionic power or a
; monster's), a Myrmidon's -4 against a charm (KIT_CHARMS), a Wanderer's +3 against fire and cold
; (kits.save). DS the game's; others kept.
KIT_SPELL_LAST equ 137
KIT_SPELLS equ 256              ; (the spell records: DS - SPELLS_FROM_DS, +40h, 20h each)
SPELLS_FROM_DS equ 0x4356 - 0x3CB4
kit_save:
        push ax
        push bx
        push cx
        push es
        mov cx, ax
        mov ax, ds
        add ax, THINGS_SEG
        mov es, ax
        mov bx, di
        imul bx, bx, 3
        cmp byte [es:bx + THINGS], 2
        jne .out                ; (not a creature)
        mov ax, [es:bx + THINGS + 1]
        push ax                 ; a robe's (dsloader/robes.py): the Veiled Robe +1 on every
        call robe_plus          ; save, the Ashen Robe +1 against a wizard's or priest's spell
        cmp ax, 2
        jae .robe
        dec ax
        jnz .no_robe
        cmp cx, KIT_SPELL_LAST
        ja .no_robe
.robe:  inc si
.no_robe:
        pop ax
        call cr_is              ; (each kit it has awake)
        db KIT_SENTINEL
        jne .myrmidon
        cmp cx, KIT_SPELL_LAST
        ja .myrmidon
        dec si
.myrmidon:
        call cr_is
        db KIT_MYRMIDON
        jne .wanderer
        mov bx, kit_charms
.charm: cmp [cs:bx], cx
        je .charmed
        add bx, 2
        cmp bx, kit_charms_end
        jb .charm
        jmp .wanderer
.charmed:
        sub si, 4
.wanderer:
        call cr_is
        db KIT_WANDERER    ; +3 against a fire or cold spell (its record's +1Ah: 2 fire, 4 cold),
        jne .out                ;   as the game's Resist Fire and Resist Cold
        cmp cx, KIT_SPELLS
        jae .out
        push ds
        mov ax, ds
        sub ax, SPELLS_FROM_DS
        mov ds, ax
        mov bx, cx
        shl bx, 5
        test byte [bx + 0x40 + 0x1A], 0x06
        pop ds
        jz .out
        add si, 3
.out:   pop es
        pop cx
        pop bx
        pop ax
        ret
; the charms (kits.CHARMS): Charm Person, Charm Monster, Domination, Charm Person or Mammal, and
; the psionic Domination and Mass Domination
kit_charms dw 2, 40, 61, 82, 158, 159
kit_charms_end:

; KIT_MOVE: AX (a creature's movement for its turn in a fight, its Move x 10; SI the creature)
; with its kit's: a Stalker's 2 more. Others kept.
kit_move:
        push ax
        mov ax, si
        call cr_is
        db KIT_STALKER
        pop ax
        jne .path
        add ax, 20
.path:  cmp si, 3               ; (a party member, while a Wayfinder of the party is up: 1 more;
        ja .ret                 ;   while one is down and none up, 1 less: PATH_DOWN)
        call path_up
        jne .down
        add ax, 10
        ret
.down:  call path_down
        jne .ret
        sub ax, 10
.ret:   ret

; PATH_UP: ZF set if a party member up (creatures 0-3, status New or Okay) is a Wayfinder (kit
; awake): Path-finder, the party's 1 more Move in a fight and 1 more initiative (kits.path_finder).
; DS the game's; all registers kept.
path_up:
        push ax
        push bx
        push es
        xor ax, ax
.member:
        push ax
        les bx, [CREATURES]
        imul ax, ax, 0x3A
        add bx, ax
        cmp byte [es:bx + 0x1C], 1      ; (New or Okay)
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

; PATH_DOWN: ZF set if no party member up is a Wayfinder (PATH_UP) and one not up (status 2-7:
; stunned to petrified; not Gone) is: Path-finder lost, the party's 1 less Move in a fight and 1
; less initiative (kits.path_finder). DS the game's; all registers kept.
path_down:
        call path_up
        jne .scan
        or sp, sp               ; (ZF clear: one is up)
        ret
.scan:
        push ax
        push bx
        push es
        xor ax, ax
.member:
        push ax
        les bx, [CREATURES]
        imul ax, ax, 0x3A
        add bx, ax
        mov ah, [es:bx + 0x1C]
        sub ah, 2               ; (not New or Okay, and not Gone: 2 to 7)
        cmp ah, 7 - 2
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

; EF_LINE: CS:SI EF_DRAW's next line: counted (EF_INDEX), and put on the panel (EF_PUT) if drawing
; and on the page shown. All registers kept.
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
        cmp ax, [cs:ef_rows]
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
        cmp ax, [cs:ef_rows]
        pop ax
        jb .shown
        cmp word [cs:ef_count], EF_LINES
        jbe .shown
        mov ax, [cs:ef_rows]
        mov [cs:ef_used], ax
        jmp .out
.shown: call ef_put
        inc word [cs:ef_used]
        inc ax
        mov [cs:ef_after], ax
.out:   pop ax
        ret
; EF_PUT: CS:SI on the panel's next line (all registers kept: the game's text routine changes ES)
ef_put:
        pusha
        push es
        cmp word [cs:ef_y], USE_FIRST_Y + (EF_LINES - 1) * USE_STEP
        ja .out
        push word [cs:ef_y]
        push word USE_X
        push cs
        push si
        call c_draw_line
.out:   add word [cs:ef_y], USE_STEP
        pop es
        popa
        ret

; Each class's kits (kitpages.KITS), the creation screen's classes in order, three each
kit_names    db 'ELEMENTALIST', 0, 'HEALER', 0, 'CRUSADER', 0
             db 'GROVE WARDEN', 0, 'LIFEBINDER', 0, 'WANDERER', 0
             db 'MYRMIDON', 0, 'SENTINEL', 0, 'RAVAGER', 0
             db 'ARENA CHAMPION', 0, 'TWIN-BLADE', 0, 'BRUTE', 0
             db 'SCHOLAR', 0, 'BATTLE MAGE', 0, 'ARCANIST', 0
             db 'MIND BENDER', 0, 'MIND WARRIOR', 0, 'KINETICIST', 0
             db 'STALKER', 0, 'JUSTIFIER', 0, 'SEEKER', 0
             db 'SWASHBUCKLER', 0, 'ASSASSIN', 0, 'SHINOBI', 0
             db 'BATTLE DANCER', 0, 0, 0                ; (the multiclass groups', three to each)
             db 'SHADOWBLADE', 0, 'MILITARY SCOUT', 0, 0
             db 'WILDERNESS AVENGER', 0, 0, 0
             db 'RESCUER', 0, 0, 0
             db 'GHETTO FIGHTER', 0, 'WAYFINDER', 0, 0
             db 'SPELLARCHER', 0, 0, 0
             db 'TITAN MIND', 0, 0, 0
             db 'POISONER', 0, 0, 0
             db 'SPIRIT CALLER', 0, 0, 0
             db 'WASTELAND SEER', 0, 0, 0
             db 'WILD FURY', 0, 0, 0
kit_class_of db 1, 1, 1, 1, 2, 2, 2, 2, 3, 4, 5, 6, 7, 7, 7, 7, 8   ; (a sheet's class, 1-17: the screen's)
kit_asleep   db ' (ASLEEP)', 0
; Shorter names for the Effects screen's line (kitpages.SHORT): the kit, the name. 0 ends it.
kit_short    db KIT_CHAMPION, 'CHAMPION', 0, KIT_SWASHBUCKLER, 'SWASHBUCK', 0, KIT_ELEMENTALIST, 'ELEMENTAL', 0
             db KIT_GROVE_WARDEN, 'WARDEN', 0, KIT_BATTLE_MAGE, 'BATTLMAGE', 0, KIT_MIND_BENDER, 'M-BENDER', 0
             db KIT_MIND_WARRIOR, 'M-WARRIOR', 0, KIT_BATTLE_DANCER, 'B-DANCER', 0, KIT_SHADOWBLADE, 'SHADOWBLD', 0
             db KIT_SCOUT, 'M-SCOUT', 0, KIT_AVENGER, 'W-AVENGER', 0, KIT_GHETTO, 'G-FIGHTER', 0
             db KIT_SPELLARCHER, 'SPELLARCH', 0, KIT_SPIRIT_CALLER, 'S-CALLER', 0, KIT_WASTE_SEER, 'WASTE SEER', 0, 0
ef_more      db 'MORE: CLICK HERE', 0
; The game's own party's features on the Effects screen (OWN_RACE_B): the race, the line. 0 ends it.
own_lines    db 5, 'WILD FIGHTING', 0, 8, 'OPEN SKY SPELLS', 0, 8, 'CHATKCHA 2/ROUND', 0
             db 3, 'KIT: E-WANDERER', 0, 0
ef_drawing   db 0
ef_index     dw 0
ef_first     dw 0
ef_rows      dw 0
ef_count     dw 0
ef_next      db 0
ef_after     dw 0
ef_used      dw 0
ef_head      dw 0
ef_is_head   db 0
ef_far       dd 0
kit_line     db 'KIT: '
             times 24 db 0          ; (the longest name, 14, and " (ASLEEP)")
ef_y         dw 0
ef_kind      dw 0
ef_last      db 0
ef_skills    dw .s0, .s1, .s2, .s3
.s0     db 'SPECIALIZED IN', 0
.s1     db 'MASTER OF', 0
.s2     db 'GRAND MASTER OF', 0
.s3     db 'EXPERT IN', 0
ef_kinds     dw .k0, .k1, .k2, .k3, .k4, .k5, .k6, .k7, .k8, .k9, .k10, .k11, .k12, .k13, .k14, .k15
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

; By class as the creation screen numbers it (0-8): the sheet's number (the first of four, by
; sphere), 1 if a sphere is added (2 for a ranger, whose flag is one), the class's flag
wp_class_map db 0, 0
             dw 0
             db 1, 1
             dw 0x01            ; cleric (air, earth, fire, water: flags 1, 2, 4, 8)
             db 5, 0
             dw 0x10            ; druid
             db 9, 0
             dw 0x20            ; fighter
             db 10, 0
             dw 0x40            ; gladiator
             db 11, 0
             dw 0x80            ; preserver
             db 12, 0
             dw 0x100           ; psionicist
             db 13, 2
             dw 0x200           ; ranger
             db 17, 0
             dw 0x400           ; thief
wp_plain   dw 81, 18, 17, 115, 20, 22, 2, 112, 3, 19, 44, 21, 48, 1, 64, 0   ; (weaponchoice.PLAIN's types, by kind)
wp_ok      dw 0
wp_sheet   times 0x48 db 0

; WP_GLADIATOR: ZF clear if the sheet being made (ES:BX) is a gladiator's (two kinds to choose).
; All registers kept.
wp_gladiator:
        cmp byte [es:bx + 0x21], CR_GLADIATOR
        je .yes
        cmp byte [es:bx + 0x22], CR_GLADIATOR
        je .yes
        cmp byte [es:bx + 0x23], CR_GLADIATOR
        je .yes
        cmp al, al              ; (ZF set)
        ret
.yes:   push ax
        or al, 1                ; (ZF clear)
        pop ax
        ret

; WP_TWO: ZF clear if the sheet being made (ES:BX) chooses two kinds: a gladiator, or a Myrmidon
; (a fighter of one class, its kit the first; kits.py). All registers kept.
wp_two:
        call wp_gladiator
        jnz .ret
        push ax
        call kit_class
        cmp al, CR_FIGHTER
        jne .no
        cmp byte [es:bx + KIT_BYTE], 1
        jne .no
        or al, 1                ; (ZF clear)
        pop ax
        ret
.no:    cmp al, al              ; (ZF set)
        pop ax
.ret:   ret

; WP_CLASSES: AL 1 if the sheet being made has a fighter, gladiator or ranger class, AH 1 if a
; cleric, druid or ranger one (a sphere). Others kept.
wp_classes:
        push bx
        push cx
        push es
        les bx, [WP_CREATION]
        xor ax, ax
        mov cx, 3
.class: mov ch, [es:bx + 0x21]
        cmp ch, CR_FIGHTER
        je .warrior
        cmp ch, CR_GLADIATOR
        je .warrior
        cmp ch, CR_RANGER
        jne .sphere
        mov ax, 0x0101
        jmp .next
.warrior:
        mov al, 1
        jmp .next
.sphere:
        cmp ch, CR_CLERIC
        je .has
        cmp ch, CR_DRUID
        jne .next
.has:   mov ah, 1
.next:  inc bx
        dec cl
        jnz .class
        or al, al               ; (a Battle Mage, with weapon specialization: a warrior here)
        jnz .out
        test word [cs:rules], RULE_SPECIALIZE
        jz .out
        push ax
        call kit_made
        cmp al, KIT_BATTLE_MAGE
        pop ax
        jne .out
        mov al, 1
.out:   pop es
        pop cx
        pop bx
        ret

probe_wp_shown:
        sti
        cmp ax, 8
        je .ret
        call wp_rules
        jz .ret
        push bp
        mov bp, sp
        push bx
        push cx
        push dx
        push es
        mov es, [bp + 4]        ; 118:C36h's far address, from the call just made
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

; PROBE_WP_CLASS: INT replaces "mov cx,1" (3 bytes: INT + NOP; 66406h) at the start of the routine
; that runs after each click on a class (it puts DONE in or out of use): the disciplines' window
; up is opened again if it is the other one for the class now (WEAPON SPEC or VIEW SPHERES); a
; weapon page up is marked again for the class now (a gladiator's two), or, for one with no
; weapon to choose, goes back to the disciplines.
probe_wp_class:
        mov cx, 1
        call wp_rules
        jz .ret
        push eax                ; (the classes changed: their defaults, until a kind is clicked;
        push es                 ;   the routine runs after every click on the screen)
        push bx
        les bx, [WP_CREATION]
        mov eax, [es:bx + 0x21]
        and eax, 0x00FFFFFF
        cmp eax, [cs:wp_classes_seen]
        je .same
        mov [cs:wp_classes_seen], eax
        mov byte [cs:wp_touched], 0
        mov byte [es:bx + KIT_BYTE], 0
        mov dword [es:bx + SPEC_SLOTS], 0  ; (the weapon specs too: the game keeps the sheet from one
.same:  pop bx                          ;   character to the next, so the last one's were kept)
        pop es
        pop eax
        push ax
        push bx
        push es
        mov ax, [WP_DISC]       ; the disciplines up: the right window for the class now?
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
        push word 0x7F8         ; (its marks kept, as 640E4h keeps them)
        push word 0x7F6
        push dword [WP_DISC]
        call wp_marked
        add sp, 8
        mov [WP_DISC_MASK], ax
        mov byte [cs:kit_keep], 1
        mov ax, ds              ; and the game opens it again (641B9h), as for the class now
        add ax, WP_STUB
        mov [cs:wp_far + 2], ax
        mov word [cs:wp_far], WP_TO_DISC
        call far [cs:wp_far]
        jmp .done
.page:  mov ax, [WP_SPHERE]     ; a weapon page up: the window's id (+8)
        or ax, [WP_SPHERE + 2]
        jz .out
        les bx, [WP_SPHERE]
        mov ax, [es:bx + 8]
        cmp ax, KIT_SPHERE_ID   ; (the spheres: an Elementalist's marked again, EL_MARKS)
        je .spheres
        cmp ax, GAME_SPHERES_ID
        je .spheres
        sub ax, KIT_WIN_ID
        cmp ax, KIT_GROUPS
        jb .kit
        add ax, KIT_WIN_ID - WP_PAGE_ID
        cmp ax, KIT_PAGE4_ID - WP_PAGE_ID
        jne .weapons
        mov al, WP_PAGES - 1    ; (the last page, its button KITS)
.weapons:
        cmp ax, WP_PAGES
        jae .out
        mov [cs:wp_page], al
        sti
        pushad
        push es
        call wp_classes
        or al, al
        jz .back
        cmp byte [cs:wp_page], WP_PAGES - 1     ; the last page: its button KITS only while the
        jne .marks                              ;   character can take a kit (opened again if not)
        call kit_class
        les bx, [WP_SPHERE]
        mov dx, [es:bx + 8]
        or al, al
        jz .no_kit
        cmp dx, KIT_PAGE4_ID
        je .marks
        jmp .reopen
.no_kit:
        cmp dx, KIT_PAGE4_ID
        jne .marks
.reopen:
        mov byte [cs:wp_from], 2
        mov al, WP_PAGES - 1
        call wp_open
        jmp .done
.marks: call wp_marks
        jmp .done
.back:  mov ax, WP_BACK
        call wp_page_button
        jmp .done
.kit:   sti                     ; a kit page up: marked again if its class is still the one made,
        pushad                  ;   the class's own opened if another is, else back
        push es
        mov cl, al
        inc cl
        call kit_class
        or al, al
        jz .back
        cmp al, cl
        je .kit_marks
        mov byte [cs:wp_from], 2
        call kit_open
        jmp .done
.kit_marks:
        call kit_marks
        jmp .done
.spheres:
        sti
        pushad
        push es
        call el_remark
.done:  pop es
        popad
.out:   pop es
        pop bx
        pop ax
.ret:   iret

; PROBE_RACE_PANEL: INT VEC_RACE_PANEL replaces "add sp,6" (3 bytes: INT; DSUN.EXE 63403h) in the
; creation screen's routine for a new race or sex, after its call (63C95h) that gives the
; character its default class. The routine empties the classes first, and the panel is opened
; again for a character of no class (the game's disciplines, VIEW SPHERES), then the class put
; in with no click to have the panel follow it: the disciplines' window is opened again here if
; it isn't the one for the class now (WEAPON SPEC, KITS), as after a click on a class.
probe_race_panel:
        pop word [cs:rp_ip]
        pop word [cs:rp_cs]
        pop word [cs:rp_fl]
        add sp, 6
        push word [cs:rp_fl]
        push word [cs:rp_cs]
        push word [cs:rp_ip]
        call wp_rules
        jz .ret
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
        push word 0x7F8         ; (its marks kept, as PROBE_WP_CLASS keeps them)
        push word 0x7F6
        push dword [WP_DISC]
        call wp_marked
        add sp, 8
        mov [WP_DISC_MASK], ax
        mov byte [cs:kit_keep], 1
        mov ax, ds              ; the game opens it again (641B9h), as for the class now
        add ax, WP_STUB
        mov [cs:wp_far + 2], ax
        mov word [cs:wp_far], WP_TO_DISC
        call far [cs:wp_far]
.done:  pop es
        popad
.ret:   iret

rp_ip   dw 0
rp_cs   dw 0
rp_fl   dw 0

probe_wp_disc_click:
        push bp
        mov bp, sp
        push ax
        mov word [cs:wp_ret_file], WP_DISC_RET & 0xFFFF
        mov word [cs:wp_end_file], WP_DISC_END & 0xFFFF
        mov byte [cs:wp_from], 0
        jmp wp_click

probe_wp_sphere_click:
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
        call wp_rules
        jz .game
        call wp_harvest
        mov ax, [cs:wp_button]
        cmp ax, WP_VIEW
        je .view
        cmp ax, KIT_VIEW
        je .kits
        cmp byte [cs:wp_from], 1    ; (a weapon or kit page's button, in the spheres' routine)
        jne .game
        cmp ax, WP_ROW
        jb .sphere
        cmp ax, MULTI_ROW + 3 * (KIT_GROUPS - MULTI_FIRST + 1)
        jae .game               ; (the multiclass groups' rows come after KITS: theirs too)
        sti
        pushad
        push es
        call wp_page_button
        pop es
        popad
        jmp .end
.view:  sti
        pushad
        push es
        xor al, al
        call wp_open
        pop es
        popad
        jmp .end
.kits:  sti                     ; KITS: from the disciplines, the spheres or the last weapon page
        pushad
        push es
        call kit_class          ; (no kit for the character now, as after another class is added:
        or al, al               ;   back from the spheres or a weapon page, as VIEW PSIONICS goes)
        jnz .kit_class
        cmp byte [cs:wp_from], 0
        je .kit_none
        mov ax, WP_BACK
        call wp_page_button
        pop es
        popad
        jmp .end
.kit_none:
        pop es
        popad
        jmp .sphere
.kit_class:
        cmp byte [cs:wp_from], 0
        je .kit_open
        les bx, [WP_SPHERE]
        cmp word [es:bx + 8], KIT_SPHERE_ID
        je .kit_open
        mov byte [cs:wp_from], 2
.kit_open:
        call kit_open
        pop es
        popad
.sphere:                        ; a sphere's row: an Elementalist's second (EL_CLICK)
        cmp ax, EL_ROW
        jb .game
        cmp ax, EL_ROW + 3
        ja .game
        sti
        pushad
        push es
        call el_click
        pop es
        popad
        jnc .game
.end:
        mov ax, [cs:wp_end_file]  ; go on at the routine's end
        sub ax, [cs:wp_ret_file]
        add [bp + 2], ax
        cmp byte [cs:kit_reroll_due], 0
        je .game
        sti
        pushad
        push es
        call kit_reroll
        pop es
        popad
.game:  pop ax
        pop bp
        mov bx, [cs:wp_button]
        iret

; WP_HARVEST: the window routines' far addresses from the overlay's calls (WP_CALLS), the
; probe's frame at BP.
wp_harvest:
        push ax
        push bx
        push cx
        push si
        push es
        mov es, [bp + 4]
        mov si, wp_calls
        mov bx, (WP_MARK_SEG + 1) & 0xFFFF
        sub bx, [cs:wp_ret_file]
        add bx, [bp + 2]
        mov ax, [es:bx]
        mov [cs:wp_mark_seg], ax
        mov bx, (WP_SPHERE_SEG + 1) & 0xFFFF
        sub bx, [cs:wp_ret_file]
        add bx, [bp + 2]
        mov ax, [es:bx]
        mov [cs:wp_sphere_seg], ax
        mov bx, (WP_STAT_SEG + 1) & 0xFFFF
        sub bx, [cs:wp_ret_file]
        add bx, [bp + 2]
        mov ax, [es:bx]
        mov [cs:wp_stat_seg], ax
        mov cx, (wp_calls_end - wp_calls) / 6
.one:   mov bx, [cs:si]         ; a call's file offset (low word), less the return's
        sub bx, [cs:wp_ret_file]
        add bx, [bp + 2]
        mov ax, [es:bx + 1]
        mov [cs:si + 2], ax
        mov ax, [es:bx + 3]
        mov [cs:si + 4], ax
        add si, 6
        loop .one
        pop es
        pop si
        pop cx
        pop bx
        pop ax
        ret

; WP_OPEN: page AL of the weapons in the panel, after closing what it shows (WP_FROM: 0 the
; disciplines, 1 the spheres, 2 a weapon or kit page), as 640E4h opens the spheres. DS = the
; game's.
wp_open:
        mov [cs:wp_page], al
        call wp_close_panel
        movzx si, byte [cs:wp_page]
        lea ax, [si + WP_PAGE_ID]
        imul si, si, WP_TITLE_SIZE
        add si, wp_titles
        cmp ax, WP_PAGE_ID + WP_PAGES - 1
        jne .show
        push ax
        call kit_class
        or al, al
        pop ax
        jz .show
        mov ax, KIT_PAGE4_ID    ; (the last, its button KITS)
.show:  call wp_show
        call wp_marks
wp_help_line:
        push dword 0x11771
        call far [cs:wp_help]
        add sp, 4
        ret

; KIT_OPEN: the kit page of the class being made in the panel, after closing what it shows
; (WP_FROM as for WP_OPEN). DS = the game's.
kit_open:
        call wp_close_panel
        call kit_class
        movzx ax, al
        add ax, KIT_WIN_ID - 1
        mov si, kit_title
        call wp_show
        call kit_marks
        jmp wp_help_line

; WP_CLOSE_PANEL: what the panel shows (WP_FROM) closed, the disciplines' or spheres' marks kept
; as the game keeps them
wp_close_panel:
        cmp byte [cs:wp_from], 0
        jne .sphere
        push word 0x7F8
        push word 0x7F6
        push dword [WP_DISC]
        call wp_marked
        add sp, 8
        mov [WP_DISC_MASK], ax
        push dword [WP_DISC]
        call far [cs:wp_close]
        add sp, 4
        mov dword [WP_DISC], 0
        ret
.sphere:
        cmp byte [cs:wp_from], 1
        jne .page
        push word 0x7FD
        push word 0x7FA
        push dword [WP_SPHERE]
        call wp_marked
        add sp, 8
        mov [WP_SPHERE_MASK], ax
.page:  mov ax, [WP_SPHERE]
        or ax, [WP_SPHERE + 2]
        jz .ret
        push dword [WP_SPHERE]
        call far [cs:wp_close]
        add sp, 4
        mov dword [WP_SPHERE], 0
.ret:   ret

; WP_SHOW: window AX in the panel, kept at DS:EA6h, the spheres' own routine (538h:57h) answering
; its buttons (PROBE_WP_SPHERE_CLICK), and its title CS:SI, as the spheres' ("%C%C%C%s" at
; DS:E11h)
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
        push dword 0x3C0014
        push dword 0xFE00FE
        push dword 0xFF0000
        push ds
        push word 0xE11
        push dword 0x6000E
        push dx
        push ax
        call far [cs:wp_print]
        add sp, 0x1C
        push dword 0x3400FE
        call far [cs:wp_colour]
        add sp, 4
        push word [0x3270]
        push word 0x14
        call far [cs:wp_colour]
        add sp, 4
        ret

; WP_MARKED: the game's 63EFAh through its stub (the window, the first and last row on the stack
; as for it): AX the rows marked.
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

CHATKCHA_KIND equ 12             ; (specialize.KINDS' number, less 1 than SPEC_SLOTS')
THRI_KREEN_RACE equ 8
; WP_MARKS: the page's rows, the kinds marked (the creation sheet's: a gladiator's two, anyone
; else's one; none yet: the long sword (a thri-kreen's the chatkcha, if allowed), and a gladiator's club, put in) chosen and the rest not,
; as 63FEEh marks the spheres.
wp_marks:
        push es
        push bx
        call wp_allowed
        mov [cs:wp_ok], ax
        les bx, [WP_CREATION]
        movzx cx, byte [es:bx + SPEC_SLOTS]     ; none yet, or one its classes don't allow: the
        jcxz .none                              ; long sword, or else the first allowed (unless
        dec cx                                  ; the player has taken it back: WP_TOUCHED)
        bt ax, cx
        jc .first
        mov word [es:bx + SPEC_SLOTS], 0
.none:  cmp byte [cs:wp_touched], 0
        jne .first
        mov cx, CHATKCHA_KIND           ; (a thri-kreen: the chatkcha, if its classes allow it)
        cmp byte [es:bx + 0x18], THRI_KREEN_RACE
        jne .sword
        bt ax, cx
        jc .put
.sword: xor cx, cx
        bt ax, 0
        jc .put
        bsf cx, ax
        jnz .put
        mov cx, -1                              ; (none at all)
.put:   inc cx
        mov [es:bx + SPEC_SLOTS], cl
.first: mov word [es:bx + SPEC_SLOTS + 2], 0
        call wp_two
        jz .one
        call wp_gladiator                       ; (a Myrmidon's second: none put in)
        jz .marked
        cmp byte [es:bx + SPEC_SLOTS + 1], 0
        jne .marked
        cmp byte [cs:wp_touched], 0
        jne .marked
        mov al, 2                               ; (the club; or the long sword, if the club is first)
        cmp byte [es:bx + SPEC_SLOTS], al
        jne .second
        dec al
.second:
        mov [es:bx + SPEC_SLOTS + 1], al
        jmp .marked
.one:   mov byte [es:bx + SPEC_SLOTS + 1], 0
.marked:
        mov ax, [es:bx + SPEC_SLOTS]
        mov [cs:wp_kind], ax
        mov byte [cs:wp_full], 0                ; all its picks made (a gladiator's two, another's
        or al, al                               ;   one): the other kinds out of use until one is
        jz .count                               ;   taken back, as the game's classes and disciplines
        call wp_two
        jz .full
        or ah, ah
        jz .count
.full:  mov byte [cs:wp_full], 1
.count:
        movzx bx, byte [cs:wp_page]
        shl bx, 2               ; (four to a page)
        mov cx, 4
.row:   inc bx                  ; (the kind + 1)
        lea ax, [bx + WP_ROW - 1]
        lea dx, [bx - 1]
        bt [cs:wp_ok], dx
        jc .open
        push 3                  ; a kind its other class doesn't allow: out of use
        call wp_button_op
        push 1
        call wp_button_op
        push 0
        jmp .next
.open:  cmp bl, [cs:wp_kind]
        je .chosen
        cmp bl, [cs:wp_kind + 1]
        je .chosen
        push 3                  ; one not chosen: in use, or greyed once all are picked
        call wp_button_op
        movzx dx, byte [cs:wp_full]
        push dx
        call wp_button_op
        push 0
        jmp .next
.chosen:
        push 0
        call wp_button_op
        push 2
        call wp_button_op
        push 1
.next:  call wp_mark
        loop .row
        pop bx
        pop es
        ret

; WP_BUTTON_OP: the game's 140:71Ah on button AX of the page (DS:EA6h), with the operation pushed
; (0 in use, 1 out of use, 2 marked, 3 not marked); takes it off the stack. AX, BX, CX kept.
wp_button_op:
        push bp
        mov bp, sp
        pusha
        push word [bp + 4]
        push word 0
        push ax
        push dword [WP_SPHERE]
        call far [cs:wp_button_fn]
        add sp, 10
        popa
        pop bp
        ret 2

; WP_MARK: the mark (pushed: 1) or none (0) at the page's row 4 - CX, as 63FEEh draws it; takes
; the flag off the stack. AX, BX, CX kept.
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
        mov ax, [es:bx + 0x1AB]
        inc ax
        push ax
        push dword 0xDA0001
        call far [cs:wp_mark_fn]
        add sp, 0x0E
        pop es
        popa
        pop bp
        ret 2

; WP_PAGE_BUTTON: button AX of a weapon page, clicked: a kind's row marked (on the creation sheet),
; MORE SPECS the next page, VIEW PSIONICS back to the disciplines (641B9h). DS = the game's.
wp_page_button:
        cmp ax, KIT_ROW
        jae kit_row
        cmp ax, WP_MORE
        je .more
        cmp ax, WP_BACK
        je .back
        sub ax, WP_ROW
        cmp ax, 16
        jae .ret
        bt [cs:wp_ok], ax       ; (one its classes don't allow: nothing)
        jnc .ret
        inc ax
        mov byte [cs:wp_touched], 1
        les bx, [WP_CREATION]
        cmp al, [es:bx + SPEC_SLOTS]            ; a kind chosen: taken back (a gladiator's second
        je .first_off                           ;   moving up), as the game's classes are
        cmp al, [es:bx + SPEC_SLOTS + 1]
        je .second_off
        cmp byte [es:bx + SPEC_SLOTS], 0        ; another: chosen, where a pick is free
        je .put_first
        call wp_two
        jz .ret
        cmp byte [es:bx + SPEC_SLOTS + 1], 0
        jne .ret
        mov [es:bx + SPEC_SLOTS + 1], al
        jmp wp_marks
.put_first:
        mov [es:bx + SPEC_SLOTS], al
        jmp wp_marks
.first_off:
        mov al, [es:bx + SPEC_SLOTS + 1]
        mov [es:bx + SPEC_SLOTS], al
.second_off:
        mov byte [es:bx + SPEC_SLOTS + 1], 0
        jmp wp_marks
.more:  mov byte [cs:wp_from], 2
        mov al, [cs:wp_page]
        inc al
        cmp al, WP_PAGES
        jb .open
        xor al, al
.open:  jmp wp_open
.back:  push dword [WP_SPHERE]
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

; KIT_ROW: kit row AX of the kit page clicked (KIT_NONE: NO KIT), as the game's spheres: with
; none chosen, the row's kit chosen; the one chosen, taken back (KIT_OPEN: the rows all in use,
; the sheet with no kit); another, nothing. DS = the game's.
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
.row:   push eax                ; (the classes the kit goes with, as PROBE_WP_CLASS keeps them: a
        mov eax, [es:bx + 0x21] ;   new character's default class is never clicked, and a kit with
        and eax, 0x00FFFFFF     ;   classes not seen is taken as stale, KIT_STALE, when the die
        mov [cs:wp_classes_seen], eax ; rolls the hit points again)
        pop eax
        mov dh, [es:bx + KIT_BYTE]
        cmp dh, KIT_OPEN        ; none chosen: this one
        je .put
        cmp dl, dh              ; another, while one is chosen: out of use (nothing)
        jne kit_marks
        mov dl, KIT_OPEN        ; the one chosen: taken back, the rest in use again
.put:   call kit_made           ; (a Battle Mage or Mind Warrior before or after: rolls again)
        call kit_rolls
        mov [es:bx + KIT_BYTE], dl
        call kit_made
        call kit_rolls
        call wp_allowed         ; (a Spellarcher, the bow its only kind: its weapon spec the bow,
        cmp ax, 1 << (BOW_KIND - 1) ;   whatever was chosen)
        jne .dagger
        mov byte [es:bx + SPEC_SLOTS], BOW_KIND
.dagger:                        ; (a Ghetto Fighter's or Poisoner's the dagger, a Battle Dancer's
        cmp byte [cs:wp_touched], 0 ;   the long sword, if the player left the weapon page's
        jne .two                ;   default: kits.default_kind)
        push cx
        mov cx, ax              ; (the kinds its classes and kit allow)
        call kit_made
        mov ah, DAGGER_KIND
        cmp al, KIT_GHETTO
        je .kind
        cmp al, KIT_POISONER
        je .kind
        mov ah, 0               ; (the long sword)
        cmp al, KIT_BATTLE_DANCER
        jne .kept
.kind:  movzx ax, ah
        bt cx, ax
        jnc .kept
        inc al
        mov [es:bx + SPEC_SLOTS], al
.kept:  mov ax, cx
        pop cx
.two:   call wp_two             ; (no Myrmidon now: its second kind gone)
        jnz kit_marks
        mov byte [es:bx + SPEC_SLOTS + 1], 0
; KIT_MARKS: the kit page's rows (NO KIT, then the class's three kits, or a multiclass group's one
; or two) marked as the creation sheet's kit, the rest not, as WP_MARKS marks a weapon page's
kit_marks:
        push es
        push bx
        call kit_class
        or al, al
        jz .out
        les bx, [WP_CREATION]
        mov dl, [es:bx + KIT_BYTE]
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
        je .open
        push 1
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

; KIT_ROLLS: kit AL one with its own hit die or PSP (a Battle Mage, a Mind Warrior, an Arcanist):
; KIT_REROLL due.
kit_rolls:
        cmp al, KIT_BATTLE_MAGE
        je .due
        cmp al, KIT_MIND_WARRIOR
        je .due
        cmp al, KIT_ARCANIST
        jne .ret
.due:   mov byte [cs:kit_reroll_due], 1
.ret:   ret

; KIT_REROLL: (WP_CLICK, at its end, BP the probe's frame, the way back to the game's in it as the
; overlay manager needs it) the sheet being made's hit points rolled again and its PSP worked out
; again, by the game's own routines for a click on a class (655D6h, flag 1, and 65B39h through the
; creation overlay's stub, as 63E44h and 639C0h call them), with its kit now: the hit points kept
; within the range 655D6h gives, as 63E5Fh keeps them, and both put on the creature and shown
; again (the game's 64C6Bh and 64CEDh, as 63E9Ch and 639D5h). DS the game's.
CR_STUB      equ 0x422E - 0x4356    ; the creation rolls' overlay's stub, less DS: its entries
CR_HP        equ 0x66               ; (655D6h: the hit points, rolled with a flag)
CR_PSP       equ 0x6B               ; (65B39h: the most PSP)
CR_HP_MIN    equ 0x4998             ; DS: the least and most hit points 655D6h works out
CR_HP_MAX    equ 0x4996
CR_CREATURE  equ 0x11A0             ; DS: the creature being made (far)
CR_PORTRAIT  equ 0x11A4             ; DS: (far; 64C6Bh's first)
CR_HP_SHOW   equ 0x3E               ; (64C6Bh, through WP_STUB: a number shown)
CR_PSP_SHOW  equ 0x43               ; (64CEDh)
kit_reroll:
        mov byte [cs:kit_reroll_due], 0
        push word 1
        push word CR_HP_MAX
        push word CR_HP_MIN
        les bx, [WP_CREATION]
        lea ax, [bx + 8]
        push es
        push ax
        mov ax, CR_HP
        call cr_far
        call far [cs:wp_far]
        add sp, 10
        les bx, [WP_CREATION]
        mov ax, [es:bx + 8]
        cmp ax, [CR_HP_MAX]
        jle .not_over
        mov ax, [CR_HP_MAX]
.not_over:
        cmp ax, [CR_HP_MIN]
        jge .not_under
        mov ax, [CR_HP_MIN]
.not_under:
        mov [es:bx + 8], ax
        les bx, [CR_CREATURE]
        mov [es:bx], ax
        mov si, 0x3F0           ; (the backdrop's words, 340h:3F0h and 404h)
        mov di, 0xF92           ; (the number's place, DS: x then y)
        mov ax, CR_HP_SHOW
        call cr_show
        mov ax, CR_PSP
        call cr_far
        call far [cs:wp_far]
        les bx, [WP_CREATION]
        mov ax, [es:bx + 0x0C]
        les bx, [CR_CREATURE]
        mov [es:bx + 2], ax
        mov si, 0x3F2
        mov di, 0xF9A
        mov ax, CR_PSP_SHOW
        jmp cr_show

; CR_FAR: WP_FAR the creation rolls' overlay's entry AX. DS the game's.
cr_far:
        mov [cs:wp_far], ax
        mov ax, ds
        add ax, CR_STUB
        mov [cs:wp_far + 2], ax
        ret

; CR_SHOW: a number of the creation screen shown again, as the game does: its backdrop put back
; (WP_BACKDROP, with the words at 340h:SI and SI+14h), then the creation overlay's entry AX with the
; number's place (DS:DI, x then y).
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
        push dword [CR_PORTRAIT]
        mov ax, ds
        add ax, WP_STUB
        mov [cs:wp_far + 2], ax
        call far [cs:wp_far]
        add sp, 16
        ret

kit_reroll_due db 0

; The Elementalist (kits.py): a cleric with a second sphere, its spells and its weapons. The sheet's
; SPHERE2 (+45h): 0 none, 1-4 the sphere (air, earth, fire, water) + 1. On the creation panel's
; spheres (the game's, mask-driven: WP_SPHERE_MASK its own sphere's row, 80h air to 10h water), an
; Elementalist with its own sphere chosen clicks another for its second (EL_CLICK), the rows kept in
; use and both marked (EL_MARKS, after every click: PROBE_WP_CLASS); its own taken back, the
; second goes too.
SPHERE2    equ 0x45
EL_ROW     equ 0x7FA                ; (the spheres' rows: AIR, EARTH, FIRE, WATER)
GAME_SPHERES_ID equ 3013
; EL_SECOND: AL the second sphere (0-3) of the Elementalist whose sheet is at ES:BX, ZF clear; ZF
; set if none (not one, or none chosen). Others kept.
el_second:
        push cx
        mov cl, [es:bx + SPHERE2]
        and cl, SPHERE2_MASK    ; (NS_SHEET's bits above it)
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

; EL_CLICK: sphere row AX clicked on the creation panel (DS the game's): carry set if it was an
; Elementalist's second (taken, or taken back) and the game is to do nothing; its own taken back
; (the game's), the second cleared too.
el_click:
        mov si, ax
        sub si, EL_ROW
        call kit_made
        cmp al, KIT_ELEMENTALIST
        jne .game
        les bx, [WP_CREATION]
        mov ax, [WP_SPHERE_MASK]
        mov cx, si
        mov dx, 0x80
        shr dx, cl
        or ax, ax
        jz .own                 ; (none chosen: the game's, its own)
        test ax, dx
        jnz .own                ; (its own: taken back)
        inc si
        mov ax, si
        mov ah, [es:bx + SPHERE2]
        and ah, SPHERE2_MASK
        cmp ah, al
        jne .put
        xor al, al              ; (the second again: taken back)
.put:   and byte [es:bx + SPHERE2], ~SPHERE2_MASK
        or [es:bx + SPHERE2], al
        call el_marks
        stc
        ret
.own:   and byte [es:bx + SPHERE2], ~SPHERE2_MASK
.game:  clc
        ret

; EL_REMARK: for an Elementalist with its own sphere chosen, the spheres' rows as EL_MARKS has
; them. DS the game's.
el_remark:
        cmp word [cs:wp_button_fn + 2], 0   ; (the window routines not yet read from the overlay)
        je .ret
        call kit_made
        cmp al, KIT_ELEMENTALIST
        jne .ret
        cmp word [WP_SPHERE_MASK], 0
        jne el_marks
.ret:   ret

; EL_MARKS: the spheres' rows (the page at DS:EA6h) all in use, its own sphere's and its second's
; marked, the others not.
el_marks:
        les bx, [WP_CREATION]
        mov dx, [WP_SPHERE_MASK]
        mov cl, [es:bx + SPHERE2]
        and cl, SPHERE2_MASK
        jz .draw
        dec cl
        mov ax, 0x80
        shr ax, cl
        or dx, ax
.draw:  mov bx, EL_ROW
        mov si, 0x80
        mov cx, 4
.row:   mov ax, bx
        push 0
        call wp_button_op
        test dx, si
        jz .open
        push 2
        call wp_button_op
        push 1
        jmp .mark
.open:  push 3
        call wp_button_op
        push 0
.mark:  call wp_mark
        inc bx
        shr si, 1
        loop .row
        ret

; The Elementalist's spells. The game gives each class a mask (the load segment + 3800h, +118h, a
; dword a class: 1 wizard, 2 priest, then a bit a class, 4 the air cleric to 20h the water cleric)
; and each spell one (+3FB9h:19Dh, 7 bytes a spell): a class casts the spells whose masks meet its.
; PROBE_EL_GRANT: INT VEC_EL_GRANT replaces "xor si,si" (2 bytes; DSUN.EXE 5E489h) in the routine
; that gives a priest the spells of its spheres (5E401h; [BP+6] the character, [BP-6] the mask of
; its priest classes, then every spell meeting it that it may cast learnt): an Elementalist's
; second sphere's cleric bit added. PROBE_EL_CAST: INT VEC_EL_CAST replaces "mov edx,es:[si+19Dh]"
; (6 bytes; 81B42h) in the caster level routine (81B16h, [BP+6] the caster), and PROBE_EL_LEVEL
; "mov ebx,es:[bx+19Dh]" (6 bytes; 5E375h) in the effect level routine (5E25Ch, [BP+6] too), where
; the spell's mask is read: for an Elementalist, a spell of its second sphere counts as its own
; sphere's (its cleric bit added; kits.spell_spheres).
probe_el_grant:
        xor si, si
        push ax
        push bx
        push cx
        push es
        call el_caster
        jz .out
        mov bx, 4
        xchg cl, al             ; (CL the second sphere)
        shl bx, cl
        xchg cl, al
        or [bp - 6], bx
.out:   pop es
        pop cx
        pop bx
        pop ax
        iret

probe_el_cast:
        mov edx, [es:si + 0x19D]
        push eax
        mov eax, edx
        call el_spheres
        mov edx, eax
        pop eax
        iret

probe_el_level:
        mov ebx, [es:bx + 0x19D]
        push eax
        mov eax, ebx
        call el_spheres
        mov ebx, eax
        pop eax
        iret

; PROBE_EL_KNOW: INT VEC_EL_KNOW replaces "test dword es:[bx+19Dh],eax" (6 bytes; DSUN.EXE 66FC9h,
; on making a character, and 86E56h, when a human changes class) in the loops that mark each priest spell
; (45h-89h) known or not for party member SI by its mask (ES:BX the spell's place in the table)
; meeting the class's bit (EAX): for an Elementalist, its second sphere's cleric bit too
; (as kits.spell_spheres). The flags of the test go back to the JZ after (RETF 2: the interrupt's own
; dropped), interrupts on again.
probe_el_know:
        sti
        push eax
        push ecx
        push bx
        push es
        mov ecx, eax            ; (ECX the class's bit)
        imul ax, si, 0x3A
        les bx, [CREATURES]
        add bx, ax
        mov ax, [es:bx + 4]
        les bx, [0x1661]
        imul ax, ax, 0x47
        add bx, ax
        call el_second
        jz .test
        movzx eax, al           ; (the second sphere's cleric bit: 4 the air cleric's)
        add al, 2
        bts ecx, eax
.test:  pop es
        pop bx
        test [es:bx + 0x19D], ecx
        pop ecx
        pop eax
        retf 2

; PROBE_DUAL_BAN: INT VEC_DUAL_BAN replaces "or ax,ax" (2 bytes; DSUN.EXE 866FFh) after the test
; whether a human may change to a class (86E94h: AX 1 if so), made for each class (SI, 1-17) as
; the DUAL window (866C7h, for member [BP+6]) greys those it can't: AX 0 for a class one of its
; kits bars (KIT_AT, asleep too; KIT_BANS, kits.DUAL_BANS). The test's flags back to the JZ (RETF 2).
probe_dual_ban:
        sti
        or ax, ax
        jz .out
        push bx
        push ecx
        push si
        push es
        push di
        push edx
        les bx, [0x1661]
        imul ax, [bp + 6], 0x47
        add bx, ax
        movzx ecx, si           ; (ECX the class)
        mov ax, 1
        call kit_place          ; (each of its kits, asleep too)
        jc .back
.place: push ax
        call kit_at
        call kit_bans
        pop ax
        bt edx, ecx
        jnc .next
        xor ax, ax
.next:  dec di
        jns .place
.back:  pop edx
        pop di
        pop es
        pop si
        pop ecx
        pop bx
.out:   or ax, ax
        retf 2

; KIT_BANS: EDX the classes (bit n: class n, 1-17) kit AL bars a human from having as well
; (DUAL_BANS; 0 for none, or no kit). Others kept.
kit_bans:
        push si
        xor edx, edx
        or al, al
        jz .out
        mov si, dual_bans
.next:  cmp byte [cs:si], 0
        je .out
        cmp [cs:si], al
        je .kit
        add si, 5
        jmp .next
.kit:   mov edx, [cs:si + 1]
.out:   pop si
        ret
; By kit (KIT_IS's number), the classes (bit n: class n, 1-17) a human with it may not change to
; (kits.DUAL_BANS): slot tables of its own that would take the new class's place (a Seeker's or
; Justifier's priest slots, a Shinobi's wizard ones); a warrior's THAC0 (a warrior class instead);
; a shield it needs (a class with none: druid, preserver); a two-handed melee weapon it needs (a
; class with none: psionicist, air cleric); a Stalker's hiding on a thief's own (the thief); a
; Grove Warden's AC on a gladiator's own (the gladiator). 0 ends it.
DB_PRIEST   equ 0x1FE                   ; (clerics and druids, 1-8)
DB_WARRIOR  equ 0x1E600                 ; (fighter 9, gladiator 10, rangers 13-16)
DB_NO_SHIELD equ 0x1E0 | (1 << 11)      ; (druids 5-8, the preserver)
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
            dd (1 << 12) | (1 << 1)     ; (the psionicist, the air cleric)
            db KIT_STALKER
            dd 1 << 17                  ; (the thief: its own hiding, the Stalker's on top)
            db KIT_GROVE_WARDEN
            dd 1 << 10                  ; (the gladiator: its own AC by level, the Warden's on top)
            db 0

; EL_SPHERES: EAX a spell's mask, for caster [BP+6]: an Elementalist's second sphere's spells its
; own sphere's too. Others kept.
el_spheres:
        push bx
        push cx
        push edx
        push es
        mov edx, eax
        call el_caster          ; AL the second sphere, CL the cleric class (1-4)
        jz .out
        push cx
        mov cl, al
        mov eax, 4
        shl eax, cl
        pop cx
        test edx, eax
        jz .out
        mov eax, 2
        shl eax, cl
        or edx, eax
.out:   mov eax, edx
        pop es
        pop edx
        pop cx
        pop bx
        ret

; EL_CASTER: for combatant [BP+6]: AL its second sphere (EL_SECOND), CL its class, ZF clear if an
; Elementalist with one; ZF set if not. ES, BX changed.
el_caster:
        call cb_is
        db KIT_ELEMENTALIST
        jne .no
        mov ax, bx
        les bx, [CREATURES]
        imul ax, ax, 0x3A
        add bx, ax
        mov ax, [es:bx + 4]
        les bx, [0x1661]
        imul ax, ax, 0x47
        add bx, ax
        push ax
        call kit_class_of_sheet
        mov cl, al
        pop ax
        jmp el_second
.no:    cmp al, al
        ret
kit_title  db 'KITS', 0
kit_keep   db 0                 ; 1 while the panel goes back to the disciplines (the kit kept)
WP_TITLE_SIZE equ 16
wp_titles  db 'WEAPONS 1 OF 4', 0, 0
           db 'WEAPONS 2 OF 4', 0, 0
           db 'WEAPONS 3 OF 4', 0, 0
           db 'WEAPONS 4 OF 4', 0, 0
wp_page    db 0
wp_from    db 0
wp_kind    db 0, 0
wp_full    db 0
wp_touched db 0                 ; 1 once the player has clicked a kind (no defaults put back after)
wp_classes_seen dd 0xFFFFFFFF   ; the classes being made, when WP_TOUCHED was last cleared
wp_button  dw 0
wp_ret_file dw 0
wp_end_file dw 0
wp_far     dd 0
wp_mine    dw WP_WSPHERE_ID, WP_PAGE_ID, WP_PAGE_ID + 1, WP_PAGE_ID + 2, WP_PAGE_ID + 3
           dw KIT_SPHERE_ID, KIT_PAGE4_ID, KIT_WIN_ID, KIT_WIN_ID + 1, KIT_WIN_ID + 2
           dw KIT_WIN_ID + 3, KIT_WIN_ID + 4, KIT_WIN_ID + 5, KIT_WIN_ID + 6, KIT_WIN_ID + 7
           dw KIT_WIN_ID + 8, KIT_WIN_ID + 9, KIT_WIN_ID + 10, KIT_WIN_ID + 11, KIT_WIN_ID + 12
wp_mine_end:
wp_calls:                   ; each: the call's file offset (low word), then its far address
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
           dw WP_CALL_REDRAW & 0xFFFF
wp_redraw  dd 0
           dw WP_CALL_MARK & 0xFFFF
wp_mark_fn dd 0
           dw WP_CALL_BACKDROP & 0xFFFF
wp_backdrop dd 0
wp_calls_end:
wp_stat_seg dw 0
wp_mark_seg dw 0
wp_sphere_seg dw 0

; SPEC_OF: DL the attacker's skill with the attack's weapon (SPEC_OF_SHEET, for the attack
; routine's [BP+10h] sheet and [BP+14h] item type).
spec_of:
        push bx
        push si
        push es
        mov si, [bp + 0x10]
        imul si, si, 0x47
        les bx, [0x1661]
        add bx, si
        mov si, [bp + 0x14]
        call spec_of_sheet
        pop es
        pop si
        pop bx
        ret

; SPEC_OF_SHEET: DL the skill with item type SI of the character whose sheet is at ES:BX:
; SPEC_NONE (it has chosen no kinds), SPEC_PLAIN (not this kind), SPEC_EXPERT (a ranger's: no
; fighter or gladiator class; and every ranger's with the bow, chosen or not), SPEC_SPECIAL,
; SPEC_MASTER (a fighter's own kind, the first, from 5th level; a Myrmidon's second too),
; SPEC_GRAND (9th). A Battle Mage's chosen kind SPEC_EXPERT; a Justifier's expertise (its chosen
; kind and the bow) SPEC_SPECIAL.
BOW_KIND equ 14                 ; (the bow's kind + 1)
spec_of_sheet:
        push ax
        push cx
        push si
        mov dl, SPEC_NONE
        mov al, [es:bx + SPEC_SLOTS]
        or al, [es:bx + SPEC_SLOTS + 1]
        or al, [es:bx + SPEC_SLOTS + 2]
        or al, [es:bx + SPEC_SLOTS + 3]
        jz .ret
        mov al, KIT_BATTLE_MAGE ; (a Battle Mage who has changed class: its weapon spec the kit's
        call kit_has            ; alone, nothing while it sleeps, expertise when awake)
        jne .kinds
        cmp word [es:bx + 0x22], 0
        je .kinds
        call kit_is
        mov dl, SPEC_NONE
        jne .out
        mov dl, SPEC_PLAIN
        cmp si, KIND_TYPES
        jae .out
        mov al, [cs:si + kind_of_type]
        cmp al, [es:bx + SPEC_SLOTS]
        jne .out
        mov dl, SPEC_EXPERT
        jmp .out
.kinds: mov dl, SPEC_PLAIN
        cmp si, KIND_TYPES
        jae .ret
        mov cl, [cs:si + kind_of_type]
        or cl, cl
        jz .ret
        xor si, si
.slot:  cmp [es:bx + si + SPEC_SLOTS], cl
        je .found
        inc si
        cmp si, SPEC_COUNT
        jb .slot
        cmp cl, BOW_KIND        ; (not chosen: a ranger's bow all the same)
        jne .ret
        xor si, si
.rbow:  mov al, [es:bx + si + 0x21]
        or si, si               ; (a human's earlier classes once the first's level has passed theirs)
        jz .ron
        cmp byte [es:bx + 0x18], 1
        jne .ron
        mov ah, [es:bx + si + 0x24]
        cmp ah, [es:bx + 0x24]
        jae .rnext
.ron:   cmp al, 13
        jb .rnext
        cmp al, 16
        ja .rnext
        mov dl, SPEC_EXPERT
        jmp .ret
.rnext: inc si
        cmp si, 3
        jb .rbow
        jmp .ret
.found: mov dl, SPEC_EXPERT
        xor ax, ax              ; AH a fighter or gladiator, AL any warrior, CH the fighter level
        xor ch, ch
        push si
        xor si, si
.class: mov cl, [es:bx + si + 0x21]
        or si, si               ; a human's earlier classes (dual-classed) count only once the
        jz .on                  ; first's level has passed theirs
        cmp byte [es:bx + 0x18], 1
        jne .on
        push ax
        mov al, [es:bx + si + 0x24]
        cmp al, [es:bx + 0x24]
        pop ax
        jae .next
.on:    cmp cl, FIGHTER_CLASS
        jne .glad
        mov ax, 0x0101
        mov ch, [es:bx + si + 0x24]
.glad:  cmp cl, GLADIATOR_CLASS
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
        call kit_is_b           ; (a Battle Mage's expertise)
        db KIT_BATTLE_MAGE
        jne .ret
        mov dl, SPEC_EXPERT
        jmp .ret
.warrior:
        or ah, ah
        jz .ret
        mov dl, SPEC_SPECIAL
        or si, si
        jz .master
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
.ret:   cmp dl, SPEC_EXPERT     ; (a Justifier's expertise, the bow's too: specialization)
        jne .out
        call kit_is_b
        db KIT_JUSTIFIER
        jne .out
        mov dl, SPEC_SPECIAL
.out:   pop si
        pop cx
        pop ax
        ret

; By item type (the game's 115, then the Loader's own: 115 its short sword), the weapon kind
; + 1 (dsloader/specialize.py's KIND_OF_TYPE; 0 none)
KIND_TYPES equ 140
kind_of_type  db 16, 14, 7, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 2, 10, 5, 12, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0
              db 0, 3, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 11, 1, 5, 1, 13, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1
              db 15, 0, 0, 0, 0, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 1, 0, 0, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0
              db 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 8, 0, 0, 4, 0, 0, 4, 6, 4, 6, 4, 0, 3, 5, 7, 8
              db 10, 0, 0, 0, 0, 0, 0, 0, 3   ; (136: the air clerics' metal dagger, Galefang's)
              db 7, 7, 3                      ; (137, 138: the bone and obsidian great axes; 139 the bone dagger)

; AD&D's class tables (RULE_HI_TABLES): the XP each class needs, priests' THAC0, and clerics',
; druids' and preservers' spell slots by level, as AD&D's Player's Handbook and Dark Sun have them
; (tables.py). The game's own: a gladiator on the fighter's XP, ranger's and thief's 2nd levels
; (2,250 and 1,250) out of reach of its table in hundreds, priests' THAC0 2/3 a level (19 at
; 3rd), its own slot tables.
;
; XP_NEED: EAX the XP class row SI (1-8: cleric, druid, fighter, gladiator, preserver,
; psionicist, ranger, thief, as the game's XP table and View Character's copy number them) needs
; at level index CX (the entry the game reads: the level the character has), EAX coming in as the
; game's table word: the game's x100, or with RULE_HI_TABLES AD&D's (levels 0-10). Others kept.
xp_need:
        test word [cs:rules_hi], RULE_HI_TABLES
        jz .game
        cmp si, 8
        ja .game
        or si, si
        jz .game
        cmp cx, 10
        ja .game
        push bx
        imul bx, si, 11 * 4
        add bx, cx
        add bx, cx
        add bx, cx
        add bx, cx
        mov eax, [cs:bx + adnd_xp - 11 * 4]
        pop bx
        ret
.game:  imul eax, eax, 100
        ret
; by class row (1-8), the XP needed at each level 0-10 (the next level's: AD&D's, levels 1-11)
adnd_xp dd 0, 1500, 3000, 6000, 13000, 27500, 55000, 110000, 225000, 450000, 675000       ; cleric
        dd 0, 2000, 4000, 7500, 12500, 20000, 35000, 60000, 90000, 125000, 200000        ; druid
        dd 0, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 250000, 500000, 750000      ; fighter
        dd 0, 2250, 4500, 9000, 18000, 36000, 75000, 150000, 300000, 600000, 900000      ; gladiator
        dd 0, 2500, 5000, 10000, 20000, 40000, 60000, 90000, 135000, 250000, 375000      ; preserver
        dd 0, 2200, 4400, 8800, 16500, 30000, 55000, 100000, 200000, 400000, 600000      ; psionicist
        dd 0, 2250, 4500, 9000, 18000, 36000, 75000, 150000, 300000, 600000, 900000      ; ranger
        dd 0, 1250, 2500, 5000, 10000, 20000, 40000, 70000, 110000, 160000, 220000       ; thief

; PROBE_XP: INT VEC_XP replaces "imul eax,eax,64h" (4 bytes: INT + 2 NOPs) where the game takes the
; XP for the next level from its table, at a level up (DSUN.EXE 87BBBh) and on View Character
; (67D41h): EAX the table's word, BX its place (the class row x 40 + the level x 2). XP_NEED.
probe_xp:
        push si
        push cx
        push dx
        mov ax, bx
        xor dx, dx
        mov si, 40
        div si
        mov cx, dx
        shr cx, 1
        xchg si, ax             ; (SI the row, AX 40)
        movzx eax, word [es:bx + 0x27C]
        call xp_need
        pop dx
        pop cx
        pop si
        iret

; PROBE_PRIEST_THAC0: INT VEC_PRIEST_THAC0 replaces "mov [bp-2],ax" (3 bytes: INT + NOP; DSUN.EXE
; 876ABh) in the game's THAC0 routine, AX what a class group takes off 20 at its level: (level - 1)
; x the group's factor / 12, the groups (CX 0-3) priest (8), warrior (12), wizard (4), rogue (6),
; their levels the bytes at [BP-0Ah] + CX x 2. With RULE_HI_TABLES a priest's is AD&D's, 2 for
; every 3 levels (20, 20, 20, 18, 18, 18, 16...); the others are AD&D's already.
probe_priest_thac0:
        test word [cs:rules_hi], RULE_HI_TABLES
        jz .done
        or cx, cx
        jnz .done
        push bx
        push dx
        push si
        mov si, cx
        add si, si
        mov al, [bp + si - 0x0A]
        pop si
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

; PROBE_ADND_SLOTS: INT VEC_ADND_SLOTS replaces "nop / push cs / call 5E4C2h" (5 bytes: INT + 3
; NOPs; DSUN.EXE 5E240h) where the game's slot routine asks one class's slots at a spell level:
; the arguments pushed (the class, a near pointer in SS to its level and WIS, the spell level),
; and the routine's AX its count from both (level and WIS rules). With RULE_HI_TABLES, for a
; cleric, druid or preserver, AD&D's slots for its level (ADND_SLOTS) and the game's for its WIS
; alone (the routine called with the level 0); the others', and with the rule off, the game's.
SLOT_CALL equ 0x5E4C2 - 0x5E242   ; the routine, from the INT's return
probe_adnd_slots:
        push bp
        mov bp, sp              ; +2 the INT's IP, +4 CS, +6 flags; +8 the class, +0Ah the
        push bx                 ; pointer, +0Ch the spell level
        push cx
        push si
        mov si, [bp + 0x0A]
        mov cx, [ss:si]         ; (CL the level, CH WIS)
        mov bx, [bp + 8]
        test word [cs:rules_hi], RULE_HI_TABLES
        jz .game
        cmp bx, 11
        je .wizard
        cmp bx, 8
        ja .game
        or bx, bx
        jz .game
        xor bx, bx              ; (a priest: the first table)
        jmp .ours
.wizard:
        mov bx, 1
.ours:  mov byte [ss:si], 0     ; the game's for WIS alone
        call .call
        mov [ss:si], cl
        push ax
        mov al, cl              ; and AD&D's for the level
        cmp al, 10
        jbe .lv
        mov al, 10
.lv:    mov ah, 0
        imul bx, bx, 10 * 5
        dec ax
        js .none
        imul ax, ax, 5
        add bx, ax
        mov ax, [bp + 0x0C]
        dec ax
        cmp ax, 5
        jae .none
        add bx, ax
        mov al, [cs:bx + adnd_slots]
        mov ah, 0
        jmp .sum
.none:  xor ax, ax
.sum:   pop bx
        add ax, bx
        jmp .out
.game:  call .call
.out:   pop si
        pop cx
        pop bx
        pop bp
        iret
.call:  push bx                 ; (the routine, a far call in the game's segment: CS from the INT;
        push cx                 ; it keeps only SI, DI and BP)
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
; AD&D's spell slots by level 1-10, spell levels 1-5: priests (clerics and druids), then wizards
adnd_slots db 1,0,0,0,0, 2,0,0,0,0, 2,1,0,0,0, 3,2,0,0,0, 3,3,1,0,0, 3,3,2,0,0, 3,3,2,1,0, 3,3,3,2,0, 4,4,3,2,1, 4,4,3,3,2
           db 1,0,0,0,0, 2,0,0,0,0, 2,1,0,0,0, 3,2,0,0,0, 4,2,1,0,0, 4,2,2,0,0, 4,3,2,1,0, 4,3,3,2,0, 4,3,3,2,1, 4,4,3,2,2

; The leader's CHA and shop prices (RULE_HI_CHA_PRICES; prices.py):
; buying costs 5% less at CHA 18 and 5% more for each point above, to 40% at 25. The leader
; is the party member whose turn it is outside a fight (DS:4979h). Selling is as the game has it.
;
; CHA_PRICE: CX an item's price (the word at its +6), lowered for the leader's CHA (never below
; 1; the game's 9999, "not for sale", kept). DS the game's; others kept.
CHA_PRICE_FIRST equ 18          ; (prices.CHA_FIRST)
CHA_PRICE_STEPS equ 8           ; (to CHA 25)
cha_price:
        test word [cs:rules_hi], RULE_HI_CHA_PRICES
        jz .out
        cmp cx, 9999
        je .out
        jcxz .out
        push ax
        push bx
        push dx
        push es
        mov bx, [WHOSE_TURN]
        cmp bx, 3
        ja .done
        les ax, [CREATURES]
        imul bx, bx, 0x3A
        add bx, ax
        mov al, [es:bx + 0x27]          ; (the abilities from +22h: STR, DEX, CON, INT, WIS, CHA)
        sub al, CHA_PRICE_FIRST - 1
        jle .done
        cmp al, CHA_PRICE_STEPS
        jbe .pct
        mov al, CHA_PRICE_STEPS
.pct:   mov ah, 5
        mul ah                          ; AX the discount in %
        mov bx, 100
        sub bx, ax
        mov ax, cx
        mul bx                          ; DX:AX the price x (100 - discount)
        mov bx, 100
        div bx
        or ax, ax
        jnz .set
        inc ax
.set:   mov cx, ax
.done:  pop es
        pop dx
        pop bx
        pop ax
.out:   ret

; PROBE_PRICE: INT VEC_PRICE replaces "mov cx,es:[bx+6]" (4 bytes: INT + 2 NOPs) where a shop
; reads an item's price to charge it (DSUN.EXE 8384Bh) and to show it under the item (83BB1h).
probe_price:
        mov cx, [es:bx + 6]
        call cha_price
        iret

; PROBE_PRICE_EAX: INT VEC_PRICE_EAX replaces "movsx eax,word es:[bx+6]" (6 bytes: INT + 4 NOPs)
; where a shop's list greys an item the party can't afford (8310Ch).
probe_price_eax:
        push cx
        mov cx, [es:bx + 6]
        call cha_price
        movsx eax, cx
        pop cx
        iret

; PROBE_XP_NEXT: INT VEC_XP_NEXT replaces "push 10F4h" (3 bytes: INT + NOP; DSUN.EXE 67DBEh) in
; View Character's line "EXP:10301 (16000)", where the game adds ")" (DS:10F4h) after the XP the
; next level needs: the least of its classes' ([BP-6], a dword, never 0 here), each class's from
; its table (a word, x100, at the class x 40 + its level x 2 + 27Ch, in the segment the game's
; "mov ax,seg" at 67D35h holds) unless it is at the level cap. The routine's character ([BP+0Ah])
; is the screen's copy of the sheet, its classes numbered 1-8 as at character creation (cleric,
; druid, fighter, gladiator, preserver, psionicist, ranger, thief), not the sheet's 1-17; its +18h
; is the race. For a character of more than one class (a second one in the second slot; not a
; human, who dual-classes and whose first class alone the game counts here), it pushes DSCLOG's
; XP_SUFFIX instead (the game's DS, pushed before, becomes CS): the class whose next level that
; is, then ")": " F)", " Pr/T)" if two are due at once. Preserver and psionicist are "Pr" and
; "Ps", the rest a letter (CLASS_LETTERS).
XP_SEG_BACK equ 0x8A            ; the "mov ax,seg"'s immediate, back from the INT's return
XP_CLOSE equ 0x10F4             ; DS: the game's ")"
probe_xp_next:
        pop word [cs:x_ip]
        pop word [cs:x_cs]
        pop word [cs:x_fl]
        push ax
        push bx
        push cx
        push dx
        push si
        push di
        push es
        push gs
        mov byte [cs:xp_ours], 0
        les bx, [bp + 0x0A]     ; the screen's copy of the sheet
        cmp byte [es:bx + 0x18], 1
        je .out                 ; (a human: the game's ")")
        cmp byte [es:bx + 0x22], 0
        je .out                 ; (one class: the game's ")")
        mov si, [cs:x_ip]
        mov gs, [cs:x_cs]
        mov ax, [gs:si - XP_SEG_BACK]
        mov gs, ax
        mov di, xp_suffix + 1
        mov cl, 9               ; the level cap (as PROBE_LEVEL)
        test byte [cs:rules], RULE_LEVEL_10
        jz .slots
        inc cl
.slots: xor dx, dx
.slot:  push bx
        add bx, dx
        movzx si, byte [es:bx + 0x21]   ; the class
        mov al, [es:bx + 0x24]          ; its level
        pop bx
        or si, si
        jz .next
        cmp si, 8
        ja .next
        cmp al, cl
        je .next
        mov ch, al
        imul ax, si, 40
        push si
        movzx si, ch
        add si, si
        add si, ax
        movzx eax, word [gs:si + 0x27C]
        pop si
        push cx
        movzx cx, ch
        call xp_need            ; (AD&D's, with RULE_HI_TABLES)
        pop cx
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
        mov word [cs:di], ')'   ; (and its NUL)
.out:   pop gs
        pop es
        pop di
        pop si
        pop dx
        pop cx
        pop bx
        pop ax
        cmp byte [cs:xp_ours], 0
        je .game
        add sp, 2               ; the game's DS
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
; by class, 1-8 (CREATION_CLASS_NAMES in dsloader/game.py)
class_letters db 0, 0, 'C', 0, 'D', 0, 'F', 0, 'G', 0, 'P', 'r', 'P', 's', 'R', 0, 'T', 0

; STORE and RECALL on the creation screen (rollstore.py: the buttons, in its window), as Baldur's
; Gate has them. PROBE_RS_CLICK: INT VEC_RS_CLICK replaces "mov cx,16h" (3 bytes: INT + NOP;
; DSUN.EXE 6625Dh) where the screen's click routine (its overlay from 65480h) looks the button
; ([BP+8]) up among its own: STORE keeps the roll on screen (RS_FIELDS: the sheet's race, sex,
; classes and kit, then its hit points, hit points rolled and most PSP; the creature's hit
; points, PSP and six scores; the hit points' least and most; the die's total, RL_POOL), RECALL
; puts it back. A stored roll is forgotten at the first button pressed after the race, sex,
; classes or kit have changed (RS_SAME), and RECALL then does nothing. Either way the
; routine goes on as for a button not its own (RS_DONE: nothing more). After a recall the scores
; are shown again (the screen's routine for it, WP_STUB's entry RS_SCORES, which RL_SUM follows
; with the totals), then the rest as the die shows a roll: its routine from where it has rolled
; the hit points (RS_TAIL, with its frame and DI 1), which shows them and the PSP (worked out
; again from the same scores: no dice), then the AC and damage.
RS_STORE  equ 0x8B0
RS_RECALL equ 0x8B1
RS_DONE   equ 0x66377 - 0x6625F    ; (the routine's way on for another button, less the INT's return)
RS_TAIL   equ 0x659D0 - 0x65480    ; (in the die's routine, 657BBh: the overlay's from 65480h)
RS_SCORES equ 0xBB
RS_KEY    equ 6                    ; (RS_BUF's first bytes: race, sex, classes, kit)
probe_rs_click:
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
        mov word [cs:wp_far], RS_SCORES
        mov ax, ds
        add ax, WP_STUB
        mov [cs:wp_far + 2], ax
        call far [cs:wp_far]
        mov si, sp
        mov ax, [ss:si + 36]                ; (the overlay's segment: the INT's return)
        mov [cs:rs_tail + 2], ax
        push cs
        push word .done
        push bp                             ; (the die's frame, as its routine makes it)
        mov bp, sp
        sub sp, 2
        push si
        push di
        mov di, 1
        jmp far [cs:rs_tail]
.stored:
        mov byte [cs:rs_have], 1
.done:  pop es
        popad
.out:   iret

; RS_SAME: ZF set if the sheet being made (DS:[119Ch]) has the stored roll's race, sex, classes
; and kit (RS_BUF's first RS_KEY bytes, in RS_FIELDS' order). DS the game's; keeps all but flags.
rs_same:
        push es
        push bx
        push ax
        les bx, [0x119C]
        mov al, [es:bx + 0x18]
        cmp al, [cs:rs_buf]
        jne .out
        mov al, [es:bx + 0x19]
        cmp al, [cs:rs_buf + 1]
        jne .out
        mov ax, [es:bx + 0x21]
        cmp ax, [cs:rs_buf + 2]
        jne .out
        mov al, [es:bx + 0x23]
        cmp al, [cs:rs_buf + 4]
        jne .out
        mov al, [es:bx + 0x43]
        cmp al, [cs:rs_buf + 5]
.out:   pop ax
        pop bx
        pop es
        ret

; RS_XFER: the roll's fields (RS_FIELDS, then the hit points' least and most and RL_POOL) into
; RS_BUF (DL 0) or back (DL 1). DS the game's; keeps DL, ES.
rs_xfer:
        push es
        mov si, rs_fields
        mov di, rs_buf
.field: mov al, [cs:si]
        cmp al, 0xFF
        je .rest
        les bx, [0x119C]
        or al, al
        jz .got
        les bx, [0x11A0]
.got:   movzx ax, byte [cs:si + 1]
        add bx, ax
        movzx cx, byte [cs:si + 2]
        call rs_bytes
        add si, 3
        jmp .field
.rest:  push ds
        pop es
        mov bx, 0x4996
        mov cx, 4
        call rs_bytes
        push cs
        pop es
        mov bx, rl_pool
        mov cx, 2
        call rs_bytes
        pop es
        ret
rs_bytes:                       ; CX bytes ES:BX <-> CS:DI (DL 0: into CS:DI)
        mov al, [es:bx]
        or dl, dl
        jz .keep
        mov al, [cs:di]
        mov [es:bx], al
.keep:  mov [cs:di], al
        inc bx
        inc di
        loop rs_bytes
        ret
rs_fields db 0, 0x18, 1, 0, 0x19, 1, 0, 0x21, 3, 0, 0x43, 1   ; (RS_KEY: race, sex, classes, kit)
          db 0, 0x08, 6, 1, 0x00, 4, 1, 0x22, 6, 0xFF
rs_buf    times 6 + 6 + 4 + 6 + 4 + 2 db 0
rs_have   db 0
rs_tail   dw RS_TAIL, 0

; PROBE_SCRIPT_RAND: INT VEC_SCRIPT_RAND replaces "inc eax / mov edx,eax" (5 bytes: INT + 3 NOPs;
; DSUN.EXE B300h) in the scripts' random command (0 to N, each as likely: rand() * (N + 1) /
; 32768), EAX its N, the rand() on the stack under the INT's return. Does the two instructions
; and records the command (kind KIND_SCRIPT): AL the result, AH N (its low byte), EXTRA where
; the script is (the running script's position, past the command's number: what dsloader's
; searches.py knows the junk, haystack and wardrobe searches by), and the frame's BP+2, +4 and
; +6 the searches' counts (the scripts' variables 135,21 to 23: junk and hay finds, wardrobe
; searches; words in the table DS:1356h points to).
KIND_SCRIPT equ 5
SCRIPT_DATA equ 0x3781 - 0x4356 ; (DS-relative) the interpreter's: +192h the running script's slot,
SCRIPT_SLOT equ 0x192           ;   +295h each slot's position (words)
SCRIPT_POS equ 0x295
SCRIPT_COUNTS equ 0x1356        ; DS: far pointer to the scripts' variables 135 (words)
SEARCH_FIRST equ 21             ; (junk, hay, wardrobe: 21 to 23)
probe_script_rand:
        sti
        inc eax
        mov edx, eax
        push bp
        mov bp, sp              ; BP+2 the INT's return, BP+8 the rand() pushed
        pushad
        push es
        movsx ebx, word [bp + 8]
        imul ebx, eax
        sar ebx, 15             ; (the game's: / 32768, the product never negative)
        mov ax, dx
        dec ax
        mov ah, al              ; N
        mov al, bl              ; the result
        mov bx, ds
        add bx, SCRIPT_DATA
        mov es, bx
        movsx bx, byte [es:SCRIPT_SLOT]
        add bx, bx
        mov cx, [es:bx + SCRIPT_POS]
        mov [cs:extra], cx
        les bx, [SCRIPT_COUNTS]
        push word [es:bx + (SEARCH_FIRST + 2) * 2]
        push word [es:bx + (SEARCH_FIRST + 1) * 2]
        push word [es:bx + SEARCH_FIRST * 2]
        push bp
        mov bp, sp              ; BP+2, +4, +6: the counts
        mov word [cs:kind], KIND_SCRIPT
        lea si, [bp + 38]       ; (SS:SI+6: the INT's return address, past ES, PUSHAD's and BP)
        call record
        pop bp
        add sp, 6
        pop es
        popad
        pop bp
        iret

; ITEM SAVES. The game's acid and corroding touch (its special attacks 178, 186 and 187, the
; Rampager's and the Babau's hits, after a failed save) can destroy an item (DSUN.EXE 7AA5Ah,
; the first melee weapon held; 7ABC4h, the first worn arm, leg or chest piece that fails):
; a weapon on a d20 under 8 less its plus; armour with no magical power (the item's +0Fh, as
; the game's weapon breaking reads it) at once, without a roll, else on a d20 under 10 less
; that byte. With RULE_ITEM_SAVES the item needs the lower (the easier) of the game's number
; and AD&D's save against acid for its material (the DMG's table: wood 8, bone 11, metal 13,
; leather 10, cloth 12; glass's 5 for stone and obsidian), less its plus, and 1 less again
; for a magical power. Each check is recorded (kind KIND_ITEM: the d20 in the low byte, the
; number needed in the high, 0 for none rolled; EXTRA the item, 8000h for armour).
KIND_ITEM equ 4
ITEM_ARMOUR equ 0x8000

; PROBE_ITEM_WEAPON: INT VEC_ITEM_WEAPON replaces "mov dx,8 / sub dx,[bp-2]" (6 bytes: INT + 4
; NOPs; DSUN.EXE 7AABCh), AX the d20, [BP-2] the weapon's plus, SI its entry in the list at
; BP-324h (the item at BP-320h + SI*0Ah). DX: the number needed (a roll under it corrodes).
probe_item_weapon:
        push si
        push ax
        push bx
        push cx
        push di
        mov dx, 8
        sub dx, [bp-2]
        mov di, si
        imul di, di, 0x0A
        mov bx, [bp+di-0x320]
        test word [cs:rules], RULE_ITEM_SAVES
        jz .log
        call adnd_needed
        cmp cx, dx
        jge .log
        mov dx, cx
.log:   xor cx, cx                      ; (a weapon)
        jmp item_record

; PROBE_ITEM_SKIP: INT VEC_ITEM_SKIP replaces "cmp word [bp-2],0" (4 bytes: INT + 2 NOPs;
; 7AC45h) before the game's "jz <destroyed>": [BP-2] the armour's magical power, SI its entry
; in the list at BP-322h (the item at BP-31Eh + SI*0Ah). ZF as the game's (destroyed without a
; roll, recorded so), or with RULE_ITEM_SAVES clear: it rolls.
probe_item_skip:
        push bp
        mov bp, sp
        and word [bp+6], ~0x40          ; (the flags IRET takes back)
        pop bp
        test word [cs:rules], RULE_ITEM_SAVES
        jnz .roll
        cmp word [bp-2], 0
        jne .roll
        push bp
        mov bp, sp
        or word [bp+6], 0x40
        pop bp
        push si
        push ax
        push bx
        push cx
        push di
        mov di, si
        imul di, di, 0x0A
        mov bx, [bp+di-0x31E]
        xor ax, ax                      ; no roll
        mov dx, 21                      ; (any d20 is under it)
        mov cx, ITEM_ARMOUR
        jmp item_record
.roll:  iret

; PROBE_ITEM_ARMOUR: INT VEC_ITEM_ARMOUR replaces "mov dx,0Ah / sub dx,[bp-2]" (6 bytes: INT
; + 4 NOPs; 7AC59h), AX the d20, [BP-2] the armour's magical power, SI as for PROBE_ITEM_SKIP.
; DX: the number needed.
probe_item_armour:
        push si
        push ax
        push bx
        push cx
        push di
        mov dx, 10
        sub dx, [bp-2]
        cmp word [bp-2], 0
        jne .game
        mov dx, 21                      ; (no power: the game's, destroyed whatever the roll)
.game:  mov di, si
        imul di, di, 0x0A
        mov bx, [bp+di-0x31E]
        test word [cs:rules], RULE_ITEM_SAVES
        jz .log
        call adnd_needed
        cmp cx, dx
        jge .log
        mov dx, cx
.log:   mov cx, ITEM_ARMOUR
        ; (on into ITEM_RECORD)

; ITEM_RECORD: (jumped to with SI, AX, BX, CX, DI pushed, in that order, on the INT's return
; address) records the check: AL the d20 (0: none), DL the number needed, BX the item, CX
; ITEM_ARMOUR or 0; then IRETs with those registers back and DX as given.
item_record:
        or cx, bx
        mov [cs:extra], cx
        mov ah, dl
        mov si, sp
        add si, 4                       ; (SS:SI+6: the INT's return address)
        mov word [cs:kind], KIND_ITEM
        call record
        pop di
        pop cx
        pop bx
        pop ax
        pop si
        iret

; ADND_NEEDED: CX = AD&D's save against acid for item BX (DS the game's): its material's
; number, less its plus, less 1 for a magical power. Keeps every other register.
adnd_needed:
        push ax
        push bx
        push di
        push es
        mov di, bx
        les bx, [ITEMS]
        imul ax, di, 0x15
        add bx, ax
        mov al, [es:bx+0x14]            ; its plus
        cbw
        mov cx, ax
        cmp byte [es:bx+0x0F], 0
        je .type
        inc cx                          ; a magical power: one plus more
.type:  mov ax, [es:bx+0x0A]
        les bx, [ITEM_TYPES]
        imul ax, ax, 0x14
        add bx, ax
        mov al, [es:bx+8]               ; its material (40h with 0: none, cloth)
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
        mov al, [cs:acid_saves+bx]
        sub ax, cx
        mov cx, ax
        pop es
        pop di
        pop bx
        pop ax
        ret

MATERIAL_CLOTH equ 6
acid_saves db 8, 11, 5, 5, 13, 10, 12   ; wood, bone, stone, obsidian, metal, leather; cloth

P_MAGIC_ARMOUR equ 1
P_METAL_ARMOUR equ 2
P_SHIELD       equ 4
P_ARMOUR       equ 8                    ; any armour on the arms, legs, head or chest
ARM_SLOT       equ 0                    ; the item slots of armour (the game's: arm, legs,
LEG_SLOT       equ 6                    ; head, chest)
HEAD_SLOT      equ 7
CHEST_SLOT     equ 9
HAND_RIGHT     equ 3
HAND_LEFT      equ 10
MATERIAL_METAL equ 4
p_flags    db 0
p_ring     db 0
p_ring2    db 0

; The items creature AX (DS = the game's, R_THINGS the things table's segment) wears in slot
; WS_SLOT, of type WS_TYPE (0FFFFh: any): WS_COUNT of them, their positive pluses adding up to
; WS_PLUS. Keeps SI, DI, BP.
worn_scan:
        push cx
        imul ax, ax, 0x3A
        mov [cs:r_creature], ax
        mov word [cs:ws_count], 0
        mov word [cs:ws_plus], 0
        mov cx, 8               ; its item lists, each a thing: +8, +0Ah, +0Ch
.list:  les bx, [CREATURES]
        add bx, [cs:r_creature]
        add bx, cx
        mov dx, [es:bx]
        cmp dx, NO_THING
        jae .next
        mov es, [cs:r_things]
        mov bx, dx
        imul bx, bx, 3
        cmp byte [es:bx+THINGS], 1
        jne .next               ; not an item
        mov dx, [es:bx+THINGS+1]
        mov byte [cs:r_left], 100
.item:  cmp dx, NO_THING
        jae .next
        les bx, [ITEMS]
        mov ax, dx
        imul ax, ax, 0x15
        add bx, ax
        mov al, [es:bx+0x11]
        cmp al, [cs:ws_slot]
        jne .on
        mov ax, [cs:ws_type]
        cmp ax, 0xFFFF
        je .match
        cmp ax, WS_MELEE
        je .melee
        cmp [es:bx+0x0A], ax
        jne .on
        jmp .match
.melee: push es               ; WS_MELEE: a melee weapon (its type's class 1)
        push bx
        mov ax, [es:bx+0x0A]
        imul ax, ax, 0x14
        les bx, [ITEM_TYPES]
        add bx, ax
        cmp byte [es:bx+0x0A], 1
        pop bx
        pop es
        jne .on
.match: inc word [cs:ws_count]
        mov al, [es:bx+0x14]    ; the plus
        cbw
        or ax, ax
        jle .on
        add [cs:ws_plus], ax
.on:    mov dx, [es:bx+4]       ; the next item in the list
        dec byte [cs:r_left]
        jnz .item
.next:  add cx, 2
        cmp cx, 0x0E
        jb .list
        pop cx
        ret

r_things   dw 0
r_creature dw 0
r_left     db 0
r_who      dw 0
ws_slot    dw 0
ws_type    dw 0
ws_count   dw 0
ws_plus    dw 0

; RULES (set by the Loader, from its Options): a helm counts AC 1, ... (2, once boots'
; movement in a fight, is unused)
RULE_HELMS equ 1
RULE_TWO_WEAPONS equ 4
RULE_SPELL_SAVE equ 8           ; (the Loader writes the game's save table for this one)
RULE_NO_DOUBLE equ 16
RULE_NEW_SPELLS equ 32          ; three new wizard spells: Cat's Grace, Erdlu Claw, Fogbolt (NEW SPELLS)
RULE_STEALTH equ 64             ; (the Loader rolls the hiding and moving silently, and sets STEALTH)
RULE_LEVEL_10 equ 128          ; class levels go up to 10, not 9
RULE_THIEF_TABLE equ 256        ; thief skills from AD&D's table and Dark Sun's DEX adjustments
RULE_HALF_GIANT equ 512         ; half-giants wield two-handed weapons in one hand
RULE_PROTECTION equ 1024        ; AD&D's rings and cloaks of protection (PROBE_RING_AC, RING_PLUS)
RULE_ITEM_SAVES equ 2048        ; items save against acid as in AD&D where better (PROBE_ITEM_*)
RULE_SPECIALIZE equ 4096        ; weapon specialization (PROBE_ATTACKS, PROBE_SPEC_DAMAGE)
RULE_RESTRICT equ 8192          ; class restrictions on armour, shields and weapons (PROBE_CAN_USE)
RULE_MULTI_HP equ 16384         ; multiclass hit points as in AD&D (PROBE_MC_*)
RULE_HP_BEST equ 32768          ; a hit die rolled twice, the better kept (PROBE_HP_BEST)
RULE_HI_KITS equ 1              ; (RULES_HI) kits, chosen on the creation panel's KIT page (KIT_*)
RULE_HI_CHA_PRICES equ 16      ; (RULES_HI) the leader's CHA lowers what shops ask (CHA_PRICE)
RULE_HI_ROLLED equ 32           ; (RULES_HI) creation's scores and hit points as rolled (RL_SCORE, RL_HP)
RULE_HI_TABLES equ 8            ; (RULES_HI) AD&D's class tables: XP, priests' THAC0, spell slots (XP_NEED, PROBE_*)
RULE_HI_INT    equ 4            ; (RULES_HI) INT's chance to learn a scroll's spell and most spells a level (INT_LEARN)
RULE_HI_RANGER equ 2            ; (RULES_HI) a ranger's spells' durations and damage at its level less 7 (PROBE_RANGER_LEVEL)
RULE_HI_BUYBACK equ 64          ; (RULES_HI) magical items sold to a merchant kept to buy back (SELL_KEEP)
THINGS_SEG equ 0x3972 - 0x4356  ; the things table's segment, relative to DS

; PROBE_MOVE: INT VEC_MOVE replaces "mov es:[bx+22Bh],ax" (5 bytes: INT + 3 NOPs) where a
; creature's turn in a fight starts: AX = its movement for the turn (its Move x 10), SI the
; creature. Does the move, with a kit's more (KIT_MOVE: the Stalker's).
probe_move:
        call kit_move
.store: mov [es:bx+0x22B], ax
        iret

; PROBE_TWO: INT VEC_TWO replaces "neg ax / mov dx,ax / or dx,dx / jge +2 / xor dx,dx" (10
; bytes: INT + 8 NOPs) in the routine that gives an attack's to-hit adjustment for two weapons
; ready, after the call that reads the attacker's DEX in the game's initiative table (AX), for
; a non-ranger; [BP+0Ah] is the attack's item, CX the attacker's object. Leaves the
; adjustment in DX: the game's, -AX and no less than 0; with RULE_TWO_WEAPONS, AD&D's: -2 (the
; item in the right hand) or -4 (in the left) plus AX (the same numbers as the reaction
; adjustment), no more than 0, and only with a melee weapon in the other hand too (else 0:
; a two-handed weapon, a shield, a sling or bow in the missile slot don't count).
RIGHT_HAND equ 3
LEFT_HAND  equ 10
probe_two:
        test byte [cs:rules], RULE_TWO_WEAPONS
        jnz .rule
        neg ax
        mov dx, ax
        or dx, dx
        jge .done
        xor dx, dx
.done:  iret
.rule:  push bx
        push es
        push cx
        mov [cs:t_adjust], ax
        xor dx, dx
        mov bx, [bp+0x0A]
        cmp bx, NO_THING
        jae .out
        imul bx, bx, 0x15
        mov ax, bx
        les bx, [ITEMS]
        add bx, ax
        mov al, [es:bx+0x11]    ; the attack's hand, and the other
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
.hand:  mov [cs:t_base], dx
        mov [cs:ws_slot], ah
        mov byte [cs:ws_slot+1], 0
        mov word [cs:ws_type], WS_MELEE
        mov ax, ds
        add ax, THINGS_SEG
        mov [cs:r_things], ax
        mov es, ax
        mov bx, cx
        imul bx, bx, 3
        xor dx, dx
        cmp byte [es:bx+THINGS], 2
        jne .out                ; not a creature
        mov ax, [es:bx+THINGS+1]
        call cr_is              ; (a Ghetto Fighter: none in the main hand, -2 in the off hand)
        db KIT_GHETTO
        jne .twin
        add word [cs:t_base], 2
.twin:  push ax                 ; (a Twin-blade or Battle Dancer in light armour: none, as a ranger; kits.py)
        call cr_is
        db KIT_TWIN_BLADE
        je .light
        call cr_is
        db KIT_BATTLE_DANCER
.light: pop ax
        jne .scan
        push dx
        mov dx, ax
        call heavy_worn
        pop dx
        jnc .out
.scan:  call worn_scan
        xor dx, dx
        cmp word [cs:ws_count], 0
        je .out                 ; nothing to fight with in the other hand
        mov dx, [cs:t_base]
        add dx, [cs:t_adjust]
        jle .out
        xor dx, dx
.out:   pop cx
        pop es
        pop bx
        iret
t_base   dw 0
t_adjust dw 0

; PROBE_DOUBLE: INT VEC_DOUBLE replaces "shl al,1" (2 bytes), where the saving throw doubles
; its d20 against fire, cold and electricity spells; not with RULE_NO_DOUBLE.
probe_double:
        test byte [cs:rules], RULE_NO_DOUBLE
        jnz .done
        shl al, 1
.done:  iret

; PROBE_LEVEL: INT VEC_LEVEL replaces "cmp byte es:[bx+24h],9" (5 bytes: INT + 3 NOPs) in the
; two places the game holds a class level (ES:BX+24h, a sheet's) against its cap of 9: where a
; character goes up a level (only while below it) and where View Character shows the XP for the
; next level (not at it). With RULE_LEVEL_10 the cap is 10: the game's XP tables, hit points,
; THAC0, saves, spell slots and thief skills all go on past 9 (the tables have 20 levels, the
; rest are formulas). RETF 2 keeps the compare's flags.
probe_level:
        sti
        push ax
        mov al, 9
        test byte [cs:rules], RULE_LEVEL_10
        jz .cmp
        inc al
.cmp:   cmp [es:bx+0x24], al
        pop ax
        retf 2

; A thief's hit dice. The game keeps one "dice up to this level" for thieves and psionicists
; together (9: after it, +2 a level), but an AD&D thief rolls a d6 up to 10th (a psionicist
; stops at 9th). With RULE_LEVEL_10 a thief's goes to 10, in the two places it counts.
THIEF_CLASS equ 17
; PROBE_HD_ROLL: INT VEC_HD_ROLL replaces "mov al,es:[bx+1]" (5 bytes: INT + 3 NOPs) where a new
; level's hit points are a roll or the fixed gain: ES:BX the class's hit point group, the
; game's [BP+8] the class.
probe_hd_roll:
        mov al, [es:bx+1]
        test byte [cs:rules], RULE_LEVEL_10
        jz .done
        cmp al, 9
        jne .done
        cmp word [bp+8], THIEF_CLASS
        jne .done
        inc al
.done:  iret

; PROBE_HD_CON: INT VEC_HD_CON replaces "cmp al,es:[bx+1]" (5 bytes: INT + 3 NOPs) where the game
; counts the levels CON's hit point bonus applies to: AL a class's level, ES:BX its group, the
; game's [BP-4] the sheet (far) and CX which of its classes. RETF 2 keeps the compare's flags.
probe_hd_con:
        sti
        push dx
        mov dl, [es:bx+1]
        test byte [cs:rules], RULE_LEVEL_10
        jz .cmp
        cmp dl, 9
        jne .cmp
        push es
        push bx
        les bx, [bp-4]
        add bx, cx
        cmp byte [es:bx+0x21], THIEF_CLASS
        pop bx
        pop es
        jne .cmp
        inc dl
.cmp:   cmp al, dl
        pop dx
        retf 2

; Multiclass hit points as in AD&D (RULE_MULTI_HP). The game adds each new level's die (or fixed
; gain) to a sheet's base (+0Ah), and a character's most hit points are that base divided by its
; number of classes (a human's, who dual-classes, counts one), plus CON's bonus for its levels:
; the warrior's full bonus, the rest's up to +2, undivided. With the rule, of a character of more
; than one class (not a human) each level's die counts its share, at least 1 (the base gains
; that times the classes, which the game divides again), and CON's bonus is shared out too.
; PROBE_HIT_DIE: INT VEC_HIT_DIE replaces "mov al,es:[bx+0]" (5 bytes: INT + 3 NOPs; DSUN.EXE 87308h)
; where a new level's hit die is taken from its class's hit point group (ES:BX; the routine's
; [BP-4] the sheet, far), at a level up and at creation: AL that, a Battle Mage's a d6 (a
; preserver's d4), a Mind Warrior's a d8 (a psionicist's d6), an Arcanist's a d3 (kits.hit_die),
; for the kit's class (one class: a human who has changed class rolls for its new one).
probe_hit_die:
        mov al, [es:bx]
        push bx
        push cx
        push es
        mov cl, al
        les bx, [bp - 4]
        cmp word [es:bx + 0x22], 0      ; (a human who has changed class rolls for the new one)
        jne .out
        call kit_is_b
        db KIT_BATTLE_MAGE
        jne .warrior
        mov cl, 6
.warrior:
        call kit_is_b
        db KIT_MIND_WARRIOR
        jne .arcanist
        mov cl, 8
.arcanist:
        call kit_is_b
        db KIT_ARCANIST
        jne .out
        mov cl, 3
.out:   mov al, cl
        pop es
        pop cx
        pop bx
        iret

; PROBE_MAX_PSP: INT VEC_MAX_PSP replaces "les bx,[bp-8]" (3 bytes: INT + NOP; DSUN.EXE 8748Fh) where
; the level-up routine has a character's most PSP worked out (SI) and puts it in the sheet ([BP-8],
; far: its +0Ch) when more than it was, the gain on the creature's PSP too: ES:BX the sheet, and a
; Mind Warrior's SI a tenth less (kits.max_psp), its kit asleep or not (KIT_HAS).
probe_max_psp:
        les bx, [bp - 8]
        push ax
        mov al, KIT_MIND_WARRIOR
        call kit_has            ; (asleep too: its psionicist levels are the PSP's)
        jne .out
        push cx
        push dx
        mov ax, si
        xor dx, dx
        mov cx, 10
        div cx
        sub si, ax
        pop dx
        pop cx
.out:   pop ax
        iret

; At creation the game rolls a character's hit points and works out its PSP when a class is
; clicked, before a kit can be chosen; picking or taking back a Battle Mage, a Mind Warrior or an
; Arcanist on the kit page has KIT_REROLL roll them again (KIT_ROW). The sheet being made has its
; classes numbered 1-8; the game copies it to the party's sheet (66AC4h, which numbers them 1-17)
; before the rolls.
; PROBE_CR_DIE: INT VEC_CR_DIE replaces "mov al,es:[bx+14Ah]" (5 bytes: INT + 3 NOPs; DSUN.EXE
; 65677h) where the creation hit points' routine (655D6h) takes the class's die for the most hit
; points it can give (ES:BX the table, by class): AL that, a Battle Mage's 6, a Mind Warrior's 8,
; an Arcanist's 3 (kits.hit_die). A kit left from the classes before a click on a class
; (PROBE_WP_CLASS takes it away only after the rolls) is taken away first, from the party's sheet
; too, so the rolls go by the class's own die. It also sets the text colour (DS:326Eh, CR_INK) the
; creation screen prints in: the screen never sets it, so it kept the last screen's (a character
; screen's yellow, 2Fh) and the scores and lines below them came out yellow.
CR_MEMBER_SEG equ 0x65689 - 0x65679   ; ("mov ax,348h": the member's number's segment, +25Bh)
CR_MEMBER     equ 0x25B
TEXT_INK      equ 0x326E              ; DS: the colour the game's screens print in (34h, 2Fh, 27h)
CR_INK        equ 0x34                ; (the creation screen's white)
probe_cr_die:
        mov word [TEXT_INK], CR_INK
        push cx
        mov cl, [es:bx + 0x14A]
        call kit_stale
        call kit_made
        cmp al, KIT_BATTLE_MAGE
        jne .warrior
        mov cl, 6
.warrior:
        cmp al, KIT_MIND_WARRIOR
        jne .arcanist
        mov cl, 8
.arcanist:
        cmp al, KIT_ARCANIST
        jne .out
        mov cl, 3
.out:   mov al, cl
        pop cx
        iret

; KIT_STALE: (PROBE_CR_DIE, its interrupt frame at SP+6) a kit on the sheet being made while its
; classes are not those PROBE_WP_CLASS last saw: taken away, from the party's sheet too. DS the
; game's; all registers kept.
kit_stale:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        push eax
        push bx
        push es
        les bx, [WP_CREATION]
        mov eax, [es:bx + 0x21]
        and eax, 0x00FFFFFF
        cmp eax, [cs:wp_classes_seen]
        je .out
        mov byte [es:bx + KIT_BYTE], 0
        mov bx, sp
        les bx, [ss:bx + 12]            ; (the INT's return, in the overlay, past CX and the call)
        mov ax, [es:bx + CR_MEMBER_SEG]
        mov es, ax
        imul ax, [es:CR_MEMBER], 0x47
        les bx, [0x1661]
        add bx, ax
        mov byte [es:bx + KIT_BYTE], 0
.out:   pop es
        pop bx
        pop eax
.ret:   ret

; KIT_MADE: AL the kit (KIT_IS's numbers) of the sheet being made, ZF clear; 0 and ZF set if none
; (the rule off, more than one class, none chosen, or its classes changed since PROBE_WP_CLASS last
; saw them). DS the game's; others kept.
kit_made:
        push bx
        push es
        call kit_class
        or al, al
        jz .out
        les bx, [WP_CREATION]
        push eax
        mov eax, [es:bx + 0x21]
        and eax, 0x00FFFFFF
        cmp eax, [cs:wp_classes_seen]
        pop eax
        jne .none
        mov bl, [es:bx + KIT_BYTE]
        dec bl
        cmp bl, 2
        ja .none
        shl al, 2
        add al, bl
        inc al
        jmp .out
.none:  xor al, al
.out:   pop es
        pop bx
        or al, al
        ret

; PROBE_CR_PSP: INT VEC_CR_PSP replaces "pop bp; retf" (2 bytes; DSUN.EXE 65C3Dh), the end of the
; creation PSP routine (65B39h), which has put the sheet being made's most PSP in its +0Ch: a Mind
; Warrior's a tenth fewer, rounded down (kits.max_psp). Then the routine's own end, the interrupt
; frame dropped, its flags put back first: the INT cleared IF, and a click on a score reaches the
; routine with nothing after to set it again (the game's clock stopped, and the game with it).
probe_cr_psp:
        push bp
        mov bp, sp
        push word [bp + 6]      ; (the flags at the INT)
        popf
        pop bp
        add sp, 6
        push ax
        call kit_made
        cmp al, KIT_MIND_WARRIOR
        jne .out
        push bx
        push cx
        push dx
        push es
        les bx, [WP_CREATION]
        mov ax, [es:bx + 0x0C]
        xor dx, dx
        mov cx, 10
        div cx
        sub [es:bx + 0x0C], ax
        pop es
        pop dx
        pop cx
        pop bx
.out:   pop ax
        pop bp
        retf

; PROBE_MC_CON: INT VEC_MC_CON replaces "add di,ax" (2 bytes; 87523h) where the most hit points
; get CON's bonus: AX the bonus, SI the sheet's number.
; PROBE_MC_UNCON: INT VEC_MC_UNCON replaces "sub dx,ax" (2 bytes; 877DAh) where the game takes
; CON's bonus off the hit points to work back to the base (when CON changes): AX, SI as above.
; PROBE_HP_BEST: INT VEC_HP_BEST replaces "mov cx,ax" (2 bytes; DSUN.EXE 87319h) after the game's
; roll of a level's hit die (at creation too), AX the roll. With RULE_HP_BEST the game rolls it
; twice and keeps the better: the first time the roll is kept and the INT returns to the start of
; the game's roll (872FDh: the die from the class's table, then the call), so the dice log sees
; both rolls as the game's; the second time CX gets the better of the two.
HP_BEST_BACK equ 0x8731B - 0x872FD
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

; PROBE_TOME: INT VEC_TOME replaces "push ds / push 3440h" (4 bytes: INT + 2 NOPs; DSUN.EXE
; 8B80Ch) in the routine run when a scroll's icon is clicked in its box, where a scroll of the
; game's (object 1400-1499) whose spell byte, less one ([BP-3]), is 172 to 195 has the game show
; its message 3440h ("CANNOT LEARN FROM THIS ITEM") and keep the scroll. The Tome of Understanding (dsloader/tome.py) is such
; a scroll, of TOME_SPELL: the one whose scroll it is (the character on show, at 25Bh of the
; segment the game names in its "mov ax,348h" at 8B7E3h) gains a point of WIS, in the sheet
; (+1Fh) and the creature record (+26h), at most TOME_MOST, and the game goes on as for a psionic
; power taught (8B7E2h): it uses the scroll up and shows the message in its buffer at [BP-54h],
; here "<name> reads the tome: WIS <n>." At TOME_MOST already, only the message ("... can grow no
; wiser."), shown as the game shows its own (8B810h), and the tome is kept. Any other scroll: the
; game's message.
TOME_SPELL   equ 0xB0             ; (172-195: the game lets the icon be clicked for below 196)
TOME_MOST    equ 25
TOME_WHO     equ 0x8B7E4 - 0x8B80E   ; (the segment in that "mov ax", less the INT's way back)
TOME_USE     equ 0x8B7E2 - 0x8B80E
TOME_SHOW    equ 0x8B810 - 0x8B80E
probe_tome:
        cmp byte [bp - 3], TOME_SPELL
        je .tome
        pop word [cs:tm_ip]
        pop word [cs:tm_cs]
        pop word [cs:tm_fl]
        push ds
        push 0x3440
        jmp .show
.tome:  pushad
        push es
        push fs
        mov si, sp
        mov es, [ss:si + 38]            ; (the INT's CS:IP, above FS, ES and PUSHAD's 32 bytes)
        mov di, [ss:si + 36]
        mov fs, [es:di + TOME_WHO]
        mov bx, [fs:0x25B]              ; the reader
        mov byte [cs:tm_used], 0
        les di, [0x1661]
        imul ax, bx, 0x47
        add di, ax                      ; ES:DI: their sheet
        lfs si, [0x1665]
        imul ax, bx, 0x3A
        add si, ax                      ; FS:SI: their creature record
        mov al, [es:di + 0x1F]
        cmp al, TOME_MOST
        jae .text
        inc al
        mov [es:di + 0x1F], al
        mov byte [cs:tm_used], 1
        cmp byte [fs:si + 0x26], TOME_MOST
        jae .text
        inc byte [fs:si + 0x26]
.text:  mov [cs:tm_wis], al
        push ss
        pop es
        lea di, [bp - 0x54]             ; ES:DI: the game's message buffer
        mov cx, 16
.name:  mov al, [fs:si + 0x28]
        or al, al
        jz .named
        stosb
        inc si
        loop .name
.named: push ds
        push cs
        pop ds
        mov si, tm_reads
        cmp byte [cs:tm_used], 0
        jne .copy
        mov si, tm_wiser
.copy:  lodsb
        stosb
        or al, al
        jnz .copy
        pop ds
        cmp byte [cs:tm_used], 0
        je .kept
        dec di                          ; (the number, after "WIS ")
        mov al, [cs:tm_wis]
        aam                             ; AH tens, AL ones
        or ax, 0x3030
        cmp ah, 0x30
        je .ones
        mov [es:di], ah
        inc di
.ones:  mov [es:di], al
        mov word [es:di + 1], '.'
        mov si, sp
        add word [ss:si + 36], TOME_USE ; on as for a power taught: the tome used up, the message
        pop fs
        pop es
        popad
        iret
.kept:  pop fs
        pop es
        popad
        pop word [cs:tm_ip]
        pop word [cs:tm_cs]
        pop word [cs:tm_fl]
        mov [cs:tm_ax], ax
        lea ax, [bp - 0x54]
        push ss
        push ax
        mov ax, [cs:tm_ax]
.show:  push word [cs:tm_fl]
        push word [cs:tm_cs]
        mov [cs:tm_ax], ax
        mov ax, [cs:tm_ip]
        add ax, TOME_SHOW
        push ax
        mov ax, [cs:tm_ax]
        iret

tm_ip    dw 0
tm_cs    dw 0
tm_fl    dw 0
tm_ax    dw 0
tm_wis   db 0
tm_used  db 0
tm_reads db " reads the tome: WIS ", 0
tm_wiser db " can grow no wiser.", 0

probe_mc_con:
        call con_share
        add di, ax
        iret

probe_mc_uncon:
        call con_share
        sub dx, ax
        iret

; CON_SHARE: with RULE_MULTI_HP, for a character of more than one class (CLASS_SHARE; SI the sheet's
; number), CON's hit points as Demihuman Deities (TSR 1998) has a multiclassed character's: each hit
; die so far with CON's bonus on it, all in the total the game keeps (the sheet's +0Ah, which the
; game already adds each new die to and divides by the classes), the total divided by the classes.
; The bonus is a warrior's (LEVEL_HP_CON + CON) on every die if any class is a warrior's, else at
; most +2; the dice, each class's levels up to its group's last that rolls one. AX (the game's own
; CON hit points, by its highest class's levels) becomes (total + bonus x dice) / classes less
; total / classes, the total as the game scales it for lost levels (87500h). Others kept.
LEVEL_HP_FROM_DS equ 0x4356 - 0x40B1    ; the game's hit point table: +group x 4 (die, its last
LEVEL_HP_CON equ 0x52                   ;   level, then a fixed gain), +10h + class: its group
WARRIOR_GROUP equ 1
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
        les bx, [0x1665]
        imul ax, si, 0x3A
        add bx, ax
        mov al, [es:bx + 0x24]  ; CON
        mov [cs:mc_con], al
        les bx, [0x1661]
        imul ax, si, 0x47
        add bx, ax
        call class_share
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
.sum:   movzx ax, byte [es:si + bx + 0x24]
        add cx, ax
        movzx ax, byte [es:si + bx + 0x3F]
        add di, ax
        inc bx
        cmp bx, 3
        jb .sum
        mov ax, [es:si + 0x0A]
        or di, di
        jz .total
        imul cx
        idiv di
.total: mov [cs:mc_total], ax
        xor cx, cx              ; CX the dice, DL 1 for a warrior's class
        xor dx, dx
        xor di, di
.class: movzx bx, byte [es:si + 0x21]
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
        cmp al, [es:si + 0x24]
        jbe .count
        mov al, [es:si + 0x24]
.count: movzx ax, al
        add cx, ax
.next:  inc si                  ; (the next class)
        inc di
        cmp di, 3
        jb .class
        movzx bx, byte [cs:mc_con]
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
        cwd
        idiv bp
        sub cx, ax
        mov ax, cx
        add sp, 2
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
mc_con   db 0

; CLASS_SHARE: AX the number of classes of the sheet at ES:BX, 1 for a human's. Others kept.
class_share:
        mov ax, 1
        cmp byte [es:bx + 0x18], 1
        je .ret
        cmp byte [es:bx + 0x22], 0
        je .ret
        inc ax
        cmp byte [es:bx + 0x23], 0
        je .ret
        inc ax
.ret:   ret

; PROBE_THIEF_SKILL: INT VEC_THIEF_SKILL, then "jc" past the game's DEX formula, replaces
; "mov ax,si / shl ax,2 / add dx,ax / mov si,dx" (9 bytes) in the game's thief skill routine,
; where DX is the skill's base plus the race's adjustment, SI the thief level, ES:0 the game's
; thief tables (the base at +skill), and the game's [BP+8] the skill, [BP-0Ch] DEX. Without
; RULE_THIEF_TABLE (or a thief level), the game's sum (SI = DX + 4 a level), CF clear: on to
; the game's DEX formula. With it, SI = AD&D's average for the level (THIEF_TABLE, levels past
; 10 as 10) + the race's adjustment + Dark Sun's DEX adjustment (DEX_TABLE, DEX 9-22), CF set:
; past the game's DEX formula, to its armour and effects (dsloader/game.py does the same sums).
probe_thief_skill:
        sti
        test word [cs:rules], RULE_THIEF_TABLE
        jz .game
        cmp si, 1
        jl .game
        push ax
        push bx
        mov bx, [bp+8]
        and bx, 7
        mov al, [es:bx]         ; the game's base, out
        cbw
        sub dx, ax
        mov ax, si
        cmp ax, 10
        jbe .level
        mov ax, 10
.level: dec ax
        imul bx, bx, 10
        add bx, ax
        mov al, [cs:thief_table+bx]
        mov ah, 0
        add dx, ax
        mov bx, [bp+8]
        and bx, 7
        cmp bx, 5               ; DEX adjusts the first five
        jae .done
        mov ax, [bp-0Ch]
        cmp ax, 9
        jge .low
        mov ax, 9
.low:   cmp ax, 22
        jle .high
        mov ax, 22
.high:  sub ax, 9
        imul ax, ax, 5
        add bx, ax
        mov al, [cs:dex_table+bx]
        cbw
        add dx, ax
.done:  mov si, dx
        pop bx
        pop ax
        push bp
        mov bp, sp
        or word [bp+6], 1       ; CF in the flags IRET restores: past the game's DEX formula
        pop bp
        iret
.game:  shl si, 2
        add si, dx
        push bp
        mov bp, sp
        and word [bp+6], 0FFFEh
        pop bp
        iret
; PROBE_TWO_HANDED: INT VEC_TWO_HANDED replaces "test byte es:[bx+0Fh],40h" (5 bytes: INT + 3
; NOPs), the two-handed bit of an item type (ES:BX), where the inventory screen puts a weapon in
; a hand: of the other hand's ("Two handed weapon in use") and of the one going in ("Need two
; free hands"). With RULE_HALF_GIANT, for a half-giant on show the answer is "not two-handed"
; (ZF set); otherwise the game's test. RETF 2 keeps the flags. (The game's own check that both
; hands don't hold heavy weapons, over 30 each, still stands.)
WHO_SEG equ USE_WHO_SEG          ; the segment of the character on show's number (+25Bh), from DS
                                ; (the overlay's code says 0348h, which its loader relocates there)
HALF_GIANT equ 5
probe_two_handed:
        sti
        test word [cs:rules], RULE_HALF_GIANT
        jz .test
        push ax
        push es
        push bx
        mov ax, ds
        add ax, WHO_SEG
        mov es, ax
        imul ax, [es:0x25B], 0x47
        les bx, [0x1661]
        add bx, ax              ; ES:BX = the sheet of the character on show
        cmp byte [es:bx + 0x18], HALF_GIANT
        pop bx
        pop es
        pop ax
        jne .test
        cmp ax, ax              ; ZF: not two-handed, for a half-giant
        retf 2
.test:  test byte [es:bx + 0x0F], 0x40
        retf 2

; PROBE_SPELL_TEXT: INT VEC_SPELL_TEXT replaces "add sp,0Ch" (3 bytes: INT + NOP) after the game
; reads a spell's description (RESOURCE.GFF's SPIN chunk DI, the spell's number + 1) into the
; buffer at the game's [BP-8] (far), AX its length or FFFFh. With RULE_NEW_SPELLS, the new spells'
; (NEW SPELLS: SPIN 197 to 199, which the game hasn't, so AX is FFFFh) are NS_TEXTS', in the
; game's words for its own.
probe_spell_text:
        pop word [cs:n_ip]
        pop word [cs:n_cs]
        pop word [cs:n_fl]
        add sp, 0x0C
        push word [cs:n_fl]
        push word [cs:n_cs]
        push word [cs:n_ip]
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .out
        cmp di, NS_FIRST + 1
        jb .out
        cmp di, NS_LAST + 1
        ja .out
        push cx
        push si
        push di
        push ds
        push es
        mov si, ns_texts
        sub di, NS_FIRST + 1
        jz .found
.skip:  cmp byte [cs:si], 0     ; (past the texts before it, each ended by a NUL)
        lea si, [si + 1]
        jne .skip
        dec di
        jnz .skip
.found: push dx
        mov dx, si
        les di, [bp-8]
        push cs
        pop ds
        cld
.copy:  lodsb
        stosb
        or al, al
        jnz .copy
        sub si, dx
        lea ax, [si - 1]        ; (its length, the NUL not counted, as the game's read gives it)
        pop dx
        pop es
        pop ds
        pop di
        pop si
        pop cx
.out:   iret
ns_texts:
        db "CAT'S GRACE:  Raises the target's dexterity by 1 to 6 pts. Maximum dexterity is 24.", 13, 10, 0
        db "ERDLU CLAW:  Erdlu talons: unarmed attacks do 1d6+1 (or +1 to Body Weaponry's or "
        db "Animal Affinity's dice), +1 to hit, as a +1 weapon. Lasts 5 rounds per level.", 13, 10, 0
        db "FOGBOLT:  A bolt of fog clings to one creature: -3 to hit and Armor Class 2 worse for "
        db "2 to 8 rounds. A saving throw negates it.", 13, 10, 0
        db "REFLECTED IMAGE:  An image of the caster moves with it: an attack may strike the "
        db "image instead, which then vanishes. Mirror Image takes its place.", 13, 10, 0
        db "SPOOK:  One creature flees in fear for 3 rounds. Its saving throw is 1 worse for each "
        db "2 caster levels (up to 6). Undead are not affected.", 13, 10, 0
        db "FRIENDS:  The caster's charisma rises by 2d4 (to 25 at most) for 1d4 rounds and 1 "
        db "per level.", 13, 10, 0

; PROBE_CHUNK_ID: INT VEC_CHUNK_ID replaces "cmp [9Ch],sp" (4 bytes: INT + 2 NOPs; the stack
; check) at the start of the game's two routines that load a GFF chunk, whose [BP+6] is the
; chunk's type and [BP+0Ah] its number (dwords). (It once asked for Cat's Grace's icon in Flaming
; Sphere's place; the new spells' icons are their own numbers, 21000 + the spell, in the
; companion's copy of RESOURCE.GFF.) The stack check, with the routine's SP; RETF 2 keeps its flags.
probe_chunk_id:
        sti                     ; (RETF 2 keeps these flags: interrupts on, as the game had them)
        push ax
        mov ax, sp
        add ax, 8               ; (the routine's SP: past this push and INT's IP, CS and flags)
        cmp [0x9C], ax
        pop ax
        retf 2

; AD&D's average thief skills, levels 1-10, a row per skill (game.AD_D_THIEF)
thief_table:
        db 30, 35, 40, 45, 50, 55, 60, 65, 70, 80     ; pick pockets
        db 25, 29, 33, 37, 42, 47, 52, 57, 62, 67     ; open locks
        db 20, 25, 30, 35, 40, 45, 50, 55, 60, 65     ; find/remove traps
        db 15, 21, 27, 33, 40, 47, 55, 62, 70, 78     ; move silently
        db 10, 15, 20, 25, 31, 37, 43, 49, 56, 63     ; hide in shadows
        db 10, 10, 15, 15, 20, 20, 25, 25, 30, 30     ; hear noise
        db 85, 86, 87, 88, 90, 92, 94, 96, 98, 99     ; climb walls
        db 0, 0, 0, 20, 25, 30, 35, 40, 45, 50        ; read languages
; Dark Sun's DEX adjustments, DEX 9-22, a row per DEX: pick, open, traps, move, hide (game.DEX_ADJUST)
dex_table:
        db -15, -10, -10, -20, -10
        db -10, -5, -10, -15, -5
        db -5, 0, -5, -10, 0
        db 0, 0, 0, -5, 0
        db 0, 0, 0, 0, 0
        db 0, 0, 0, 0, 0
        db 0, 0, 0, 0, 0
        db 0, 5, 0, 0, 0
        db 5, 10, 0, 5, 5
        db 10, 15, 5, 10, 10
        db 15, 20, 10, 15, 15
        db 20, 25, 12, 20, 17
        db 25, 27, 15, 25, 20
        db 27, 30, 17, 30, 22

; PROBE_DOS_OPEN: the DOS services (INT 21h), hooked. Opening a file (AH=3Dh) whose name ends in
; one of COPIES' (SEGOBJEX.GFF, the game's objects and their pictures; RESOURCE.GFF, its screens'
; pictures and texts; GPLDATA.GFF, its scripts; RGN29.GFF, the slave pens; RGN1C.GFF, RGN1E.GFF,
; RGN08.GFF and RGN28.GFF, the Upper Castle, the Undermountain, the Gemfields and the warrens, a
; person or thing there with an object of its own for a new item) opens the Loader's
; copy instead (D:\..., which the launcher writes with
; the Loader's icons added; the game folder is never changed), and notes that it has; with no
; copy there, the game's own. Everything else goes on to DOS.
OBJ_NAME_LEN equ 12
probe_dos_open:
        cmp ah, 40h
        je dos_write
        cmp ah, 4Ch
        je dos_quit
        cmp ah, 3Dh
        jne .chain
        call seg_move
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
;
; Each copy's name (its length first) is matched against the end of the path, where it starts the
; path or follows a \, : or /.
.at_end:
        mov ax, si
        sub ax, dx              ; AX: the path's length
        mov bx, copies
.file:  mov cl, [cs:bx]         ; this copy's name length (0: no more)
        xor ch, ch
        jcxz .no
        cmp ax, cx
        jb .next
        push ax
        push si
        sub si, cx              ; where the name would start
        cmp ax, cx
        je .compare             ; (the path is just the name)
        mov al, [si - 1]
        cmp al, '\'
        je .compare
        cmp al, ':'
        je .compare
        cmp al, '/'
        jne .differ
.compare:
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
        pop si
        pop ax
        jmp .found
.differ:
        pop si
        pop ax
.next:  add bx, COPY_SIZE
        jmp .file
.found: mov [cs:copy_at], bx
        pop di
        pop si
        pop cx
        pop bx
        pop ax
        sti                     ; (RETF 2 keeps these flags: interrupts on, as the game had them)
        push ax                 ; (the game's AX, for its own file if there's no copy)
        push ds
        push dx
        push cs
        pop ds
        mov dx, [cs:copy_at]
        add dx, 1 + OBJ_NAME_LEN  ; its copy's path
        pushf
        call far [cs:old21]
        pop dx
        pop ds
        jc .own
        pop word [cs:obj_scratch]  ; (POP keeps the flags: CF clear, AX the handle)
        push bx
        mov bx, [cs:copy_at]
        mov bx, [cs:bx + 1 + OBJ_NAME_LEN + COPY_PATH]  ; (its flag: set to 1)
        mov word [cs:bx], 1
        pop bx
        retf 2
.own:   pop ax
        jmp .chain
.no:    pop di
        pop si
        pop cx
        pop bx
        pop ax
.chain: jmp far [cs:old21]
old21       dd 0

; DOS_WRITE (INT 21h AH=40h): what the game writes to the screen (handles 1 and 2: stdout,
; stderr) kept, its last MSG_BYTES in MSG_RING, then on to DOS. The game prints its fatal errors
; ("Mel Fatal Error", "ABEND: VMDelHeap() ...") while the screen is still in graphics, and puts
; it back in text mode, clearing it, on its way out: GAMEEND.COM found nothing to read.
MSG_BYTES   equ 256
dos_write:
        cmp bx, 2
        ja .chain
        cmp bx, 1
        jb .chain
        push ax
        push cx
        push si
        push di
        mov si, dx
        jcxz .done
.byte:  mov al, [si]
        inc si
        mov di, [cs:msg_at]
        mov [cs:msg_ring + di], al
        inc di
        and di, MSG_BYTES - 1
        mov [cs:msg_at], di
        cmp word [cs:msg_len], MSG_BYTES
        jae .full
        inc word [cs:msg_len]
.full:  loop .byte
.done:  pop di
        pop si
        pop cx
        pop ax
.chain: jmp far [cs:old21]

; DOS_QUIT (INT 21h AH=4Ch): a program ending with a code other than 0, the first time (the
; game: GAMEEND.COM, after it, also ends with 1), saves D:\GAMEMSG.BIN for the Loader's crash
; report (launch.game_message): "GMSG", the code, the game's load segment, SS, SP, the stack's
; first STACK_BYTES there (the ways back of the calls that led to the exit), the length of the
; text kept and the text (DOS_WRITE). Then on to DOS.
STACK_BYTES equ 256
dos_quit:
        or al, al
        jz .chain
        cmp byte [cs:quit_saved], 0
        jne .chain
        mov byte [cs:quit_saved], 1
        pusha
        push ds
        push es
        mov [cs:qm_code], al
        mov [cs:qm_ss], ss
        mov [cs:qm_sp], sp
        add word [cs:qm_sp], 20         ; (the INT's way back: past PUSHA, DS and ES)
        mov ah, 62h
        pushf
        call far [cs:old21]
        add bx, 10h
        mov [cs:qm_load], bx
        push ss                         ; the stack, copied
        pop ds
        mov si, [cs:qm_sp]
        push cs
        pop es
        mov di, qm_stack
        mov cx, STACK_BYTES / 2
        cld
        rep movsw
        mov ax, [cs:msg_len]
        mov [cs:qm_len], ax
        push cs
        pop ds
        mov ah, 3Ch
        xor cx, cx
        mov dx, qm_name
        pushf
        call far [cs:old21]
        jc .out
        mov bx, ax
        mov ah, 40h
        mov cx, qm_end - qm_head
        mov dx, qm_head
        pushf
        call far [cs:old21]
        mov si, [msg_at]                ; the text, oldest first: from its start to the ring's
        sub si, [msg_len]               ;   end, then from the ring's start
        and si, MSG_BYTES - 1
        mov cx, MSG_BYTES
        sub cx, si
        cmp cx, [msg_len]
        jbe .first
        mov cx, [msg_len]
.first: lea dx, [msg_ring + si]
        push cx
        mov ah, 40h
        pushf
        call far [cs:old21]
        pop ax
        mov cx, [msg_len]
        sub cx, ax
        jcxz .close
        mov dx, msg_ring
        mov ah, 40h
        pushf
        call far [cs:old21]
.close: mov ah, 3Eh
        pushf
        call far [cs:old21]
.out:   pop es
        pop ds
        popa
.chain: jmp far [cs:old21]
quit_saved  db 0
msg_at      dw 0
msg_len     dw 0
qm_name     db "D:\GAMEMSG.BIN", 0
qm_head     db "GMSG"
qm_code     db 0
qm_load     dw 0
qm_ss       dw 0
qm_sp       dw 0
qm_stack    times STACK_BYTES db 0
qm_len      dw 0
qm_end:
msg_ring    times MSG_BYTES db 0

; SEG_MOVE: once, at a file open (AH=3Dh) of the game's (DSUNLOG.EXE the program running, its
; segment table where it should be, SEGTAB_AT), before any of its overlays is in: the game's segments
; 3E3Fh (a small stack, selector 3B8h) and 3E45h (the monster kinds' table, 3C0h), the 200h bytes
; after the spell records, moved here (SEG_SPACE: each overlay's code is given the table's segment
; as it is read in), so that the new spells from 196 on have their records' room there (NEW
; SPELLS: 196-198 had been over the stack). All registers kept.
SEGTAB_AT    equ 0x4137          ; the segment table (8 bytes a selector: the segment, the length)
SEL_RECORDS  equ 0x3B0           ;   from the load segment, and its selectors: the spell records',
SEL_STACK    equ 0x3B8           ;   the stack's and the monster kinds'
SEL_KINDS    equ 0x3C0
SEG_RECORDS  equ 0x3CB4
SEG_STACK    equ 0x3E3F
SEG_KINDS    equ 0x3E45
SEG_BYTES    equ 0x200
seg_move:
        cmp byte [cs:seg_moved], 0
        jne .ret
        pusha
        push ds
        push es
        mov ah, 62h
        pushf
        call far [cs:old21]     ; (BX the program's PSP)
        lea dx, [bx + 0x10]     ; (DX its load segment)
        lea ax, [bx + 0x10 + SEGTAB_AT]
        mov es, ax
        lea ax, [bx + 0x10 + SEG_RECORDS]
        cmp [es:SEL_RECORDS], ax
        jne .out
        cmp word [es:SEL_RECORDS + 2], 0x18B0
        jne .out
        lea ax, [bx + 0x10 + SEG_STACK]
        cmp [es:SEL_STACK], ax
        jne .out
        lea ax, [bx + 0x10 + SEG_KINDS]
        cmp [es:SEL_KINDS], ax
        jne .out
        cmp word [es:SEL_KINDS + 2], 0x192
        jne .out
        mov ds, [es:SEL_STACK]  ; (the 200h bytes, here)
        xor si, si
        mov ax, cs
        add ax, (seg_space - hdr) / 16
        mov [es:SEL_STACK], ax
        add ax, (SEG_KINDS - SEG_STACK)
        mov [es:SEL_KINDS], ax
        push es
        mov ax, cs
        mov es, ax
        mov di, seg_space
        mov cx, SEG_BYTES / 2
        cld
        rep movsw
        pop es
        mov byte [cs:seg_moved], 1
.out:   pop es
        pop ds
        popa
.ret:   ret
obj_scratch dw 0
copy_at     dw 0
resources_on dw 0               ; 1 once the game has opened D:\RESOURCE.GFF (PROBE_CHUNK_ID)
scripts_on dw 0                 ; 1 once the game has opened D:\GPLDATA.GFF (Kalzith's conversation)
region_on dw 0                  ; 1 once the game has opened D:\RGN29.GFF (Kalzith in the pens)
others_on dw 0                  ; 1 once it has opened one of the other regions' copies
; the files with copies: the name's length, the game's name (up to 12 letters), the copy's path,
; the flag set when opened
COPY_PATH equ 16
COPY_SIZE equ 1 + OBJ_NAME_LEN + COPY_PATH + 2
%macro COPY 3
        db %strlen(%1), %1
        times OBJ_NAME_LEN - %strlen(%1) db 0
        db %2
        times COPY_PATH - %strlen(%2) db 0
        dw %3
%endmacro
copies:
        COPY 'SEGOBJEX.GFF', 'D:\SEGOBJEX.GFF', objects_on
        COPY 'RESOURCE.GFF', 'D:\RESOURCE.GFF', resources_on
        COPY 'GPLDATA.GFF', 'D:\GPLDATA.GFF', scripts_on
        COPY 'RGN29.GFF', 'D:\RGN29.GFF', region_on
        COPY 'RGN1C.GFF', 'D:\RGN1C.GFF', others_on   ; (a Castle Guard of its own: worldgear.py)
        COPY 'RGN1E.GFF', 'D:\RGN1E.GFF', others_on   ; (an Undermountain miner of its own)
        COPY 'RGN08.GFF', 'D:\RGN08.GFF', others_on   ; (a Magera of their own, Drakejaw's)
        COPY 'RGN28.GFF', 'D:\RGN28.GFF', others_on   ; (a skeleton of its own, Gutterward's)
        db 0

; NEW SPELLS (RULE_NEW_SPELLS): three wizard spells past the game's 196 (0-68 wizard, 69-137 priest,
; 138-171 psionic powers, 172-195 monsters' powers): Cat's Grace (196, 2nd level), Erdlu Claw (197,
; 1st) and Fogbolt (198, 1st). Their records are the three after the game's, a block of 96 bytes the
; game zeroes and never uses (its segment 3E3Fh; from 199 on is live data), and their rows in the
; table of spell levels (7 bytes each) are past its own too. NS_SETUP fills those in while the rule
; is on (and empties them while it's off): a row with the level and a wizard's mask, a record from
; another spell's (Strength's, Enlarge's, Charm Person's), and each one's effect's name and icon.
; The game's lists of spells run to 8Ah; three bytes in gamepatch.py take them to NS_LAST, and the
; places where the game tells a wizard's or priest's spell (below 8Ah) from a psionic power or a
; monster's (and a priest's from a wizard's, below 45h) see a new spell as a wizard's: NS_CMP, at
; the sites in NS_SITES. A party member knows them by bits of its sheet's +45h (NS_SHEET, above the
; Elementalist's second sphere, SPHERE2's low four bits), which saves keep: the game's own table
; has 8Ah bytes a member, so NS_KNOWN hands the game a byte of its own for the bit (NS_SCRATCH) and
; NS_LEARN puts a learnt spell's in the sheet. Their names (NS_NAME), descriptions (PROBE_SPELL_TEXT)
; and icons (21000 + the spell, in the Loader's copy of RESOURCE.GFF) are the helper's.
; Cat's Grace works as Strength does but for DEX: its own effect (54, a number the game leaves
; unused) holds the 1d6, which the routine that works out a creature's abilities adds to DEX,
; keeping it between 3 and 24. Erdlu Claw, a spell without a handler of its own, puts its effect
; (6, unused too) on the creature, and each of its natural attacks does 1d6+1 where that is
; better than its own (NS_CLAW). Fogbolt puts its (27)
; on a creature that fails its save: -3 to hit, and +2 to hit it (NS_HIT).
NS_FIRST     equ 0xC4
NS_COUNT     equ 6
NS_LAST      equ NS_FIRST + NS_COUNT - 1
GRACE_SPELL  equ NS_FIRST
CLAW_SPELL   equ NS_FIRST + 1
FOG_SPELL    equ NS_FIRST + 2
REFLECT_SPELL equ NS_FIRST + 3
SPOOK_SPELL  equ NS_FIRST + 4
FRIENDS_SPELL equ NS_FIRST + 5
STRENGTH_SPELL equ 23
ENLARGE_SPELL equ 5
CHARM_SPELL  equ 2
MIRROR_SPELL equ 19
GRACE_EFFECT equ 54
CLAW_EFFECT  equ 6
FOG_EFFECT   equ 27
MIRROR_EFFECT equ 25            ; (the game's Mirror Images: Reflected Image's too)
AFRAID_EFFECT equ 17            ; (the game's Afraid: Spook's)
FRIENDS_EFFECT equ 74           ; (unused by the game, as 6, 27 and 54)
FRIENDS_MOST equ 25
SPOOK_MOST   equ 6              ; Spook's save: 1 worse for each 2 caster levels, up to 6
ADRENALIN    equ 0x94           ; the psionic Adrenalin Control, which Strength's code also serves
NS_ICON      equ 21000          ; a spell's icon: ICON 21000 + its number (RESOURCE.GFF)
NS_SHEET     equ 0x45           ; the sheet's byte with most of the bits that say it knows them
SPHERE2_MASK equ 0x07           ;   (its low three bits the Elementalist's second sphere, 0-4)
SPELL_RECS   equ 0x30           ; the spell records (DS - SPELLS_FROM_DS: 20h each from here)
FLIGHTS      equ 0              ; before them the 16 flights a record's +10h names (3 bytes each:
MISSILE_FLIGHT equ 4            ;   the object flying, a byte): Magic Missile's, and place 15,
FOG_FLIGHT   equ 15             ;   which no record names, Fogbolt's (object FOG_BOLT, in the
FLIGHT15_OBJECT equ 8116        ;   companion's copy of SEGOBJEX.GFF: icons.py), else the game's
FLIGHT15_BYTE equ 16
FOG_BOLT     equ 8118
FOG_CAST_SOUND equ 82           ; a record's +0Fh: the sound with its cast glow (+0Dh), +13h as
FOG_HIT_SOUND equ 98            ;   it flies, +16h as it lands (BVOC chunks of RESOURCE.GFF)
NS_OBJECTS   equ 0x80           ; NS_STATE's bits: the copy open (OBJECTS_ON), and the records'
NS_MOVED     equ 0x40           ;   room made (SEG_MOVED)
EFFECT_TABLE_FROM_DS equ 0x4356 - 0x3F8D ; the effects' table (6 bytes each from effect 1: its
EFFECT_NO_NAME equ 0x1FF0       ;   name, far, and icon); DS: the empty name of an unnamed one
EFFECTS_FROM_DS equ 0x4356 - 0x3BF6 ; the active effects (10 bytes each from EFFECTS_OFF: the
EFFECTS_OFF  equ 0x106          ;   thing it is on, ..., its number at +6), and how many (DS)
EFFECTS_COUNT equ 0x1E24

; PROBE_GRACE_CAST: INT VEC_GRACE_CAST replaces "mov ax,[bp+0Eh] / mov [bp-1Ah],ax" (6 bytes:
; INT + 4 NOPs) where the code for spells with handlers of their own picks the handler by the
; spell's number: Cat's Grace goes to Strength's.
probe_grace_cast:
        mov ax, [bp+0x0E]
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .store
        cmp ax, GRACE_SPELL
        je .strength
        cmp ax, FRIENDS_SPELL   ; (Friends too)
        jne .store
.strength:
        mov ax, STRENGTH_SPELL
.store: mov [bp-0x1A], ax
        iret

; PROBE_GRACE_EFFECT: INT VEC_GRACE_EFFECT replaces Strength's handler choosing its effect
; (19 bytes: INT + 17 NOPs): Adrenalin Control 42h, Strength 43h, and Cat's Grace and Friends
; their own; Friends rolls 2d4 (FRIENDS_DICE) where the others roll 1d6.
FRIENDS_DICE equ 0x00040002     ; (the dice routine's count, then sides: 2d4)
FRIENDS_PUSH equ 0x79489 - 0x79472 ; (past the INT's 17 NOPs and "push dword 60001h", 79483h)
probe_grace_effect:
        mov word [bp-0x14], 0x43
        cmp word [bp+0x0E], ADRENALIN
        jne .grace
        mov word [bp-0x14], 0x42
        iret
.grace: test byte [cs:rules], RULE_NEW_SPELLS
        jz .out
        cmp word [bp+0x0E], GRACE_SPELL
        jne .friends
        mov word [bp-0x14], GRACE_EFFECT
.friends:
        cmp word [bp+0x0E], FRIENDS_SPELL
        jne .out
        mov word [bp-0x14], FRIENDS_EFFECT
        push bx                 ; Friends' 2d4, not Strength's 1d6: the handler's next "push
        mov bx, sp              ;   60001h" (6 bytes: the dice, count and sides) done here with
        sub sp, 4               ;   FRIENDS_DICE, and the INT's return moved past it
        mov bx, sp              ; (SS:BX: BX and the frame 4 lower; the old ones from +4)
        push ax
        mov ax, [ss:bx + 4]     ; BX
        mov [ss:bx], ax
        mov ax, [ss:bx + 6]     ; IP, past the push
        add ax, FRIENDS_PUSH
        mov [ss:bx + 2], ax
        mov ax, [ss:bx + 8]     ; CS
        mov [ss:bx + 4], ax
        mov ax, [ss:bx + 10]    ; flags
        mov [ss:bx + 6], ax
        mov word [ss:bx + 8], FRIENDS_DICE & 0xFFFF
        mov word [ss:bx + 10], FRIENDS_DICE >> 16
        pop ax
        pop bx
.out:   iret

; PROBE_GRACE_ABILITY: INT VEC_GRACE_ABILITY replaces "mov [bp-0Ah],ax / mov cx,7" (6 bytes:
; INT + 4 NOPs) in the routine that works out a creature's abilities, as it looks at one of its
; effects (AX its number; ES:BX the effect, its amount at +10Fh): Cat's Grace adds the amount
; to DEX in its sums (words from [BP-342h], STR first), as Strength's adds to STR; Friends adds
; its amount (2d4) to CHA, up to FRIENDS_MOST.
probe_grace_ability:
        mov [bp-0x0A], ax
        mov cx, 7
        cmp ax, FRIENDS_EFFECT
        jne .grace
        push ax
        mov al, [es:bx+0x10F]
        cbw
        add ax, [bp-0x338]
        cmp ax, FRIENDS_MOST
        jle .cha
        mov ax, FRIENDS_MOST
.cha:   cmp ax, [bp-0x338]      ; (never lower: a CHA above it already kept)
        jl .kept
        mov [bp-0x338], ax
.kept:  pop ax
        iret
.grace: cmp ax, GRACE_EFFECT
        jne .out
        push ax
        mov al, [es:bx+0x10F]
        cbw
        add ax, [bp-0x340]
        cmp ax, 24
        jle .low
        mov ax, 24
.low:   cmp ax, 3
        jge .set
        mov ax, 3
.set:   mov [bp-0x340], ax
        pop ax
.out:   iret

; NS_SETUP: once the rule has changed (NS_STATE), the new spells' rows, records and effects as it
; has them now (see NEW SPELLS), and flight 15 Fogbolt's grey bolt once the game has the objects'
; copy open (FLIGHTS). DS the game's; all registers kept.
ns_state     db 0xFF            ; RULE_NEW_SPELLS and NS_OBJECTS as last set up (0FFh: not yet)
ns_levels    db 2, 1, 1, 1, 1, 1 ; each one's spell level ...
ns_templates db STRENGTH_SPELL, ENLARGE_SPELL, CHARM_SPELL, MIRROR_SPELL, CHARM_SPELL, STRENGTH_SPELL
                                ; ... the spell whose record it takes ...
ns_effects   db GRACE_EFFECT, CLAW_EFFECT, FOG_EFFECT, MIRROR_EFFECT, AFRAID_EFFECT, FRIENDS_EFFECT
                                ; ... its effect ...
ns_effect_how db 2, 1, 1, 0, 3, 2 ; ... put in the record and named by the helper (1), put in
                                ;   the record, the game's own (3), the template's (0), or by the
                                ;   handler (PROBE_GRACE_EFFECT) and named by the helper (2) ...
ns_landing   db 96, 77, FOG_HIT_SOUND, 0, 0, 0 ; ... the sound as it lands (+16h): Haste's, Shocking
                                ;   Grasp's, Fog Cloud's (0: the template's) ...
ns_known_at  db NS_SHEET, NS_SHEET, NS_SHEET, NS_SHEET, NS_SHEET, KIT_BYTE ; ... and the sheet's
ns_known_bit db 0x10, 0x20, 0x40, 0x08, 0x80, 0x80 ;   byte and bit that say a member knows it
                                ;   (KIT_BYTE's 0FFh, KIT_OPEN, none: NS_BIT_AT)
; NS_PATCHES: the records' changes from their templates': the new spell (0 to NS_COUNT - 1), the
; place, 1 (a byte) or 2 (a word), the value; 0FFh ends them.
%macro NS_PATCH 4
        db %1 - NS_FIRST, %2, %3
        dw %4
%endmacro
ns_patches:
        NS_PATCH FOG_SPELL, 4, 1, 0x42          ; Fogbolt: 2d4 rounds (+4: the dice, sides x 16 + count;
        NS_PATCH FOG_SPELL, 5, 2, 0             ;   +5 a level's more; +7 the time each counts), not
        NS_PATCH FOG_SPELL, 7, 2, 60            ;   Charm Person's for ever ...
        NS_PATCH FOG_SPELL, 0x11, 2, 0x4000     ;   ... nor mind-affecting; Fog Cloud's sound as it's
        NS_PATCH FOG_SPELL, 0x0F, 1, FOG_CAST_SOUND ; cast (Charm Person's, 75, as it flies)
        NS_PATCH REFLECT_SPELL, 4, 1, 0x11      ; Reflected Image: one image (Mirror Image's are its
        NS_PATCH REFLECT_SPELL, 5, 2, 0         ;   "rounds", 1d4 + a level's third, counted down)
        NS_PATCH SPOOK_SPELL, 4, 1, 0x13        ; Spook: 3 rounds, not Charm Person's for ever ...
        NS_PATCH SPOOK_SPELL, 5, 2, 0
        NS_PATCH SPOOK_SPELL, 7, 2, 60          ;   (nothing flies to it, as Charm Person)
        NS_PATCH FRIENDS_SPELL, 4, 1, 0x41      ; Friends: 1d4 rounds and 1 a level, not Strength's hour
        NS_PATCH FRIENDS_SPELL, 5, 2, 1         ;   a level (+1Dh's low bits: the levels a "level"
        NS_PATCH FRIENDS_SPELL, 7, 2, 60        ;   counts, 1) ...
        NS_PATCH FRIENDS_SPELL, 0x1D, 1, 1
        NS_PATCH FRIENDS_SPELL, 1, 2, 0xFFFF    ; ... on the caster alone, as Mirror Image
        NS_PATCH FRIENDS_SPELL, 0x0C, 1, 7
        db 0xFF
ns_name_at   dw ns_name_grace, ns_name_claw, ns_name_fog, ns_name_reflect, ns_name_spook, ns_name_friends
ns_name_grace db "CAT'S GRACE", 0
ns_name_claw db "ERDLU CLAW", 0
ns_name_fog  db "FOGBOLT", 0
ns_name_reflect db "REFLECTED IMAGE", 0
ns_name_spook db "SPOOK", 0
ns_name_friends db "FRIENDS", 0
ns_setup:
        push ax
        mov al, [cs:rules]
        and al, RULE_NEW_SPELLS
        cmp word [cs:objects_on], 1
        jne .moved
        or al, NS_OBJECTS
.moved: cmp byte [cs:seg_moved], 0
        je .state
        or al, NS_MOVED
.state: cmp al, [cs:ns_state]
        jne .do
        pop ax
        ret
.do:    mov [cs:ns_state], al
        pusha
        push es
        cld
        mov dl, al              ; (DL not 0 while the rule is on)
        and dl, RULE_NEW_SPELLS
        xor si, si              ; (SI each new spell, 0 to NS_COUNT - 1)
.spell: cmp si, REFLECT_SPELL - NS_FIRST
        jb .row
        cmp byte [cs:seg_moved], 0
        je .next                ; (no room for its record: SEG_MOVE)
.row:   mov ax, ds              ; its row: the level and a wizard's mask (spell 0's), or nothing
        add ax, SPELL_LEVELS_SEG
        mov es, ax
        imul di, si, 7
        add di, SPELL_LEVELS + NS_FIRST * 7
        push di
        xor ax, ax
        mov cx, 7
        rep stosb
        pop di
        or dl, dl
        jz .record
        mov al, [cs:si + ns_levels]
        mov [es:di], al
        mov eax, [es:SPELL_LEVELS + 1]
        mov [es:di + 1], eax
.record:
        mov ax, ds              ; its record: its template's, changed, or nothing
        sub ax, SPELLS_FROM_DS
        mov es, ax
        imul di, si, 0x20
        add di, SPELL_RECS + NS_FIRST * 0x20
        push di
        xor ax, ax
        mov cx, 0x10
        rep stosw
        pop di
        or dl, dl
        jz .effect
        movzx bx, byte [cs:si + ns_templates]
        shl bx, 5
        add bx, SPELL_RECS
        push di
        mov cx, 0x10
.copy:  mov ax, [es:bx]
        stosw
        add bx, 2
        loop .copy
        pop di
        mov al, [cs:si + ns_landing]
        or al, al
        jz .own_landing
        mov [es:di + 0x16], al
.own_landing:
        test byte [cs:si + ns_effect_how], 1
        jz .patches             ; (Cat's Grace, Friends: Strength's, the effect PROBE_GRACE_EFFECT's)
        mov al, [cs:si + ns_effects]
        mov [es:di + 0x19], al
.patches:
        mov bx, ns_patches      ; (and NS_PATCHES' changes for it)
.patch: movzx ax, byte [cs:bx]
        cmp al, 0xFF
        je .flight
        cmp ax, si
        jne .skip
        movzx cx, byte [cs:bx + 1]
        push di
        add di, cx
        mov ax, [cs:bx + 3]
        cmp byte [cs:bx + 2], 1
        jne .word
        mov [es:di], al
        jmp .put
.word:  mov [es:di], ax
.put:   pop di
.skip:  add bx, 5
        jmp .patch
.flight:
        cmp si, FOG_SPELL - NS_FIRST
        jne .effect
        test byte [cs:ns_state], NS_OBJECTS
        jz .effect
        mov byte [es:di + 0x10], FOG_FLIGHT ; (Fogbolt's grey bolt flies, where the copy has it)
.effect:
        mov al, [cs:si + ns_effect_how]
        or al, al
        jz .next                ; (the game's effect: its name and icon its own)
        cmp al, 3
        je .next
        mov ax, ds              ; its effect: the name and icon, or none
        sub ax, EFFECT_TABLE_FROM_DS
        mov es, ax
        movzx di, byte [cs:si + ns_effects]
        dec di
        imul di, di, 6
        mov word [es:di], EFFECT_NO_NAME
        mov [es:di + 2], ds
        mov word [es:di + 4], 0
        or dl, dl
        jz .next
        mov bx, si
        shl bx, 1
        mov ax, [cs:bx + ns_name_at]
        mov [es:di], ax
        mov [es:di + 2], cs
        lea ax, [si + NS_ICON + NS_FIRST]
        mov [es:di + 4], ax
.next:  inc si
        cmp si, NS_COUNT
        jb .spell
        mov ax, ds              ; Reflected Image's entry (NS_ENTRY), or nothing
        sub ax, EFFECT_TABLE_FROM_DS
        mov es, ax
        xor ax, ax
        mov [es:REFLECT_ENTRY], ax
        mov [es:REFLECT_ENTRY + 2], ax
        mov [es:REFLECT_ENTRY + 4], ax
        or dl, dl
        jz .flights
        test byte [cs:ns_state], NS_MOVED
        jz .flights
        mov word [es:REFLECT_ENTRY], ns_name_reflect
        mov [es:REFLECT_ENTRY + 2], cs
        mov word [es:REFLECT_ENTRY + 4], NS_ICON + REFLECT_SPELL
.flights:
        mov ax, ds              ; flight 15: Fogbolt's grey bolt, as fast as Magic Missile's; else the game's
        sub ax, SPELLS_FROM_DS
        mov es, ax
        mov word [es:FLIGHTS + FOG_FLIGHT * 3], FLIGHT15_OBJECT
        mov byte [es:FLIGHTS + FOG_FLIGHT * 3 + 2], FLIGHT15_BYTE
        or dl, dl
        jz .done
        test byte [cs:ns_state], NS_OBJECTS
        jz .done
        mov word [es:FLIGHTS + FOG_FLIGHT * 3], FOG_BOLT
        mov al, [es:FLIGHTS + MISSILE_FLIGHT * 3 + 2]
        mov [es:FLIGHTS + FOG_FLIGHT * 3 + 2], al
.done:  pop es
        popa
        pop ax
        ret

; NS_NEW: CF set if spell AX is a new one and the rule is on, AX then its place (0 to NS_COUNT - 1);
; else AX kept. Those from REFLECT_SPELL on only once their records have room (SEG_MOVED). Others
; kept.
ns_new:
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .no
        cmp ax, NS_FIRST
        jb .no
        cmp ax, NS_LAST
        ja .no
        cmp ax, REFLECT_SPELL
        jb .yes
        cmp byte [cs:seg_moved], 0
        je .no
.yes:   sub ax, NS_FIRST
        stc
        ret
.no:    clc
        ret

; NS_FLAGS: the arithmetic flags of AX (OF, SF, ZF, AF, PF, CF) into the interrupt frame of a site
; (PUSHAD, then ES: its flags at SS:DI+38). All registers and flags kept.
ns_flags:
        pushf
        push ax
        and ax, 0x08D5
        and word [ss:di + 38], ~0x08D5
        or [ss:di + 38], ax
        pop ax
        popf
        ret

; NS_KNOWS: CF set if party member AX (its thing) knows new spell CL (0 to NS_COUNT - 1): its
; sheet's bit (NS_SHEET_KNOWS). DS the game's; all registers kept.
ns_knows:
        push bx
        push es
        call thing_sheet
        call ns_sheet_knows
        pop es
        pop bx
        ret

; NS_BIT: DI the sheet's byte that says a member knows new spell CL (0 to NS_COUNT - 1: NS_KNOWN_AT),
; AL its bit (NS_KNOWN_BIT). Others kept.
ns_bit:
        push bx
        movzx bx, cl
        movzx di, byte [cs:bx + ns_known_at]
        mov al, [cs:bx + ns_known_bit]
        pop bx
        ret

; NS_SHEET_KNOWS: CF set if sheet ES:BX says it knows new spell CL (KIT_BYTE's KIT_OPEN: none
; chosen, and no spell known). All registers kept.
ns_sheet_knows:
        push ax
        push di
        call ns_bit
        cmp di, KIT_BYTE
        jne .test
        cmp byte [es:bx + di], KIT_OPEN
        je .no
.test:  test [es:bx + di], al
        jz .no
        pop di
        pop ax
        stc
        ret
.no:    pop di
        pop ax
        clc
        ret

; NS_SHEET_LEARN: sheet ES:BX knows new spell CL (a KIT_OPEN kit byte made 0, no kit, first);
; NS_SHEET_FORGET: no longer; NS_FORGET_ALL: none of them. All registers kept.
ns_sheet_learn:
        push ax
        push di
        call ns_bit
        cmp di, KIT_BYTE
        jne .set
        cmp byte [es:bx + di], KIT_OPEN
        jne .set
        mov byte [es:bx + di], 0
.set:   or [es:bx + di], al
        pop di
        pop ax
        ret
ns_sheet_forget:
        push ax
        push di
        call ns_bit
        cmp di, KIT_BYTE
        jne .clear
        cmp byte [es:bx + di], KIT_OPEN
        je .out
.clear: not al
        and [es:bx + di], al
.out:   pop di
        pop ax
        ret
ns_forget_all:
        push cx
        xor cx, cx
.each:  call ns_sheet_forget
        inc cx
        cmp cx, NS_COUNT
        jb .each
        pop cx
        ret

; SPOOK_SAVE: in the saving throw (its [BP+6] the target, [BP+8] the caster, [BP+0Ah] the spell,
; SI too; [BP-2] the total, a byte), Spook's total 1 less for each 2 of the caster's wizard levels
; (NS_CASTER_LEVEL), no more than SPOOK_MOST, no less than 0. All registers kept.
spook_save:
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .ret
        cmp si, SPOOK_SPELL
        jne .ret
        push ax
        mov ax, [bp + 8]
        call ns_caster_level
        shr ax, 1
        cmp ax, SPOOK_MOST
        jbe .less
        mov ax, SPOOK_MOST
.less:  sub [bp - 2], al
        jns .kept
        mov byte [bp - 2], 0
.kept:  pop ax
.ret:   ret

; NS_CASTER_LEVEL: AX the wizard level combatant AX casts a new spell at: the level of a preserver
; class of its, or a Shinobi's casting level (SHINOBI_CAST), the more. DS the game's; others kept.
ns_caster_level:
        push bx
        push cx
        push dx
        push si
        push es
        mov dx, ds
        add dx, THINGS_SEG
        mov es, dx
        imul bx, ax, 3
        mov ax, [es:bx + COMBATANT_CREATURE]
        call creature_sheet
        xor dx, dx
        xor si, si
.class: cmp byte [es:bx + si + 0x21], PRESERVER_CLASS
        jne .next
        movzx ax, byte [es:bx + si + 0x24]
        cmp ax, dx
        jbe .next
        mov dx, ax
.next:  inc si
        cmp si, 3
        jb .class
        call kit_is_b
        db KIT_SHINOBI
        jne .out
        call kit_level
        movzx ax, al
        call shinobi_cast
        cmp ax, dx
        jbe .out
        mov dx, ax
.out:   mov ax, dx
        pop es
        pop si
        pop dx
        pop cx
        pop bx
        ret

; NS_COUNT_OF: AX how many of the new spells party member SI knows (none while the rule is off),
; of spell level CL only if CL isn't 0. DS the game's; others kept.
ns_count_of:
        push bx
        push cx
        push dx
        push es
        xor dx, dx
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .out
        mov dh, cl
        xor cx, cx
.each:  mov ax, si
        call ns_knows
        jnc .next
        or dh, dh
        jz .count
        mov bx, cx
        cmp [cs:ns_levels + bx], dh
        jne .next
.count: inc dl
.next:  inc cx
        cmp cx, NS_COUNT
        jb .each
.out:   movzx ax, dl
        pop es
        pop dx
        pop cx
        pop bx
        ret

; THING_SHEET: ES:BX the sheet of thing AX (a creature's: its entry in the things table). DS the
; game's; others kept.
thing_sheet:
        push ax
        mov bx, ds
        add bx, THINGS_SEG
        mov es, bx
        imul bx, ax, 3
        mov ax, [es:bx + THINGS + 1]
        call creature_sheet
        pop ax
        ret

; NS_SITES (RULE_NEW_SPELLS): the INT VEC_CR_SPELLS sites from NS_SITE (their numbers' order).
; Each of NS_CMP's is a "cmp" the game makes of a spell's number (one of the NS_K_* operands) with
; a number (8Ah, the first psionic power; 45h, the first priest spell; 0ACh, the first monster's
; power; 0C4h, the end): the site is the INT, its number and NOPs over it, and NS_CMP makes the
; compare with a new spell's number as 0's, a wizard's, its flags in the INT's frame.
NS_K_R16  equ 0                 ; a register: its place in the frame (NS_SI, NS_DX, NS_AX)
NS_K_R8   equ 1                 ; ... its low byte (NS_CL)
NS_K_BP16 equ 2                 ; a word at [BP + the number]
NS_K_BP8  equ 3                 ; a byte there
NS_K_DS16 equ 4                 ; a word at DS:the number
NS_K_ESBX equ 6                 ; a word at ES:[BX + the number]
NS_SI equ 6                     ; (the registers' places in the frame: PUSHAD, then ES)
NS_DX equ 22
NS_CL equ 26
NS_AX equ 30
NS_SITE   equ 9                 ; the first site's number (PROBE_CR_SPELLS's RL_* and others below)
NS_KNOWN  equ NS_SITE           ; 5DD04h, the start of the routine that finds a spell's known byte
NS_LEARN  equ NS_SITE + 1       ; 5E3F7h, where the routine that teaches a spell sets it
NS_NAME   equ NS_SITE + 2       ; 5E560h, in the routine that gives a spell's name
NS_CLAW   equ NS_SITE + 3       ; 7B70Ah, a natural attack's dice
NS_HIT    equ NS_SITE + 4       ; 7C430h, an attack's to-hit adjustments
NS_CMP    equ NS_SITE + 5       ; NS_CMP_SITES' from here
ns_cmp_sites:                   ; (kind, the operand, the number compared with)
        db NS_K_R16
        dw NS_SI, 0x8A          ; 5585Ch the USE screen's spells, drawn (and 55865h: 45h)
        db NS_K_R16
        dw NS_SI, 0x45
        db NS_K_BP8
        dw -1, 0x8A             ; 55AECh the USE screen's click on a spell (and 55AF2h: 45h)
        db NS_K_BP8
        dw -1, 0x45
        db NS_K_R16
        dw NS_SI, 0x8A          ; 55FECh the USE screen's spells, which can be cast (and 55FF5h)
        db NS_K_R16
        dw NS_SI, 0x45
        db NS_K_DS16
        dw 0x4AF5, 0x8A         ; 6CC93h the spell cast in a fight, shown (and 6CCBEh: 0C4h)
        db NS_K_DS16
        dw 0x4AF5, 0xC4
        db NS_K_DS16
        dw 0x54F9, 0x8A         ; 72051h the readied spell's icon
        db NS_K_ESBX
        dw 0x10A, 0x8A          ; 76883h, 76C00h an effect's spell: not a psionic power's
        db NS_K_ESBX
        dw 0x10A, 0x8A
        db NS_K_R16
        dw NS_DX, 0xC4          ; 772BBh the cast (and 772C7h: 0ACh, 772ECh: 8Ah)
        db NS_K_R16
        dw NS_DX, 0xAC
        db NS_K_R16
        dw NS_DX, 0x8A
        db NS_K_R16
        dw NS_SI, 0x8A          ; 7A258h a spell's effect on its target
        db NS_K_R16
        dw NS_SI, 0x8A          ; 7BDA7h, 7BDB1h, 7BDCBh: a spell of the 1st to 3rd level (Minor
        db NS_K_R16             ;   Globe of Invulnerability)
        dw NS_SI, 0x8A
        db NS_K_R16
        dw NS_SI, 0x8A
        db NS_K_BP16
        dw 8, 0x8A              ; 81B23h the caster level
        db NS_K_R16
        dw NS_SI, 0x8A          ; 84C76h, 851BBh the level a spell is cast at
        db NS_K_R16
        dw NS_SI, 0x8A
        db NS_K_DS16
        dw 0x4AF5, 0x8A         ; 88DE0h the spell cast, shown (and 88DFFh: 0C4h)
        db NS_K_DS16
        dw 0x4AF5, 0xC4
        db NS_K_BP8
        dw -3, 0xC4             ; 8B491h a scroll used: its spell (8B6B5h: 8Ah, learnt; 8B875h: its
        db NS_K_BP8             ;   icon; 8B8AAh, 8BA37h, 8BA70h: 0C4h)
        dw -3, 0x8A
        db NS_K_BP16
        dw -2, 0x8A
        db NS_K_BP8
        dw -3, 0xC4
        db NS_K_BP8
        dw -3, 0xC4
        db NS_K_BP8
        dw -3, 0xC4
        db NS_K_BP8
        dw -1, 0xC4             ; 6F827h an item's spell used (and 6F8D8h: its cast, DX)
        db NS_K_R16
        dw NS_DX, 0xC4
        db NS_K_R16
        dw NS_DX, 0x8A          ; 720D3h, 8C457h an item's spell's icon (a scroll's in its box)
        db NS_K_R16
        dw NS_DX, 0x8A
        db NS_K_R16
        dw NS_SI, 0x8A          ; 8C64Eh the spell info box's icon
        db NS_K_R8
        dw NS_CL, 0xC4          ; 8B0FAh a scroll's spell, read (and 58B7Eh: a weapon's, on a hit)
        db NS_K_R8
        dw NS_CL, 0xC4
NS_CMP_COUNT equ ($ - ns_cmp_sites) / 5
NS_FIST   equ NS_CMP + NS_CMP_COUNT ; 58226h, a melee hit's magic (after NS_CMP's)
NS_IMAGE  equ NS_FIST + 1       ; 7A5CDh, an image taking a weapon's blow
NS_ENTRY_EF equ NS_IMAGE + 1    ; 7ED37h, 7EEC9h, 7EF34h: an effect's entry, the Effects screen's
NS_ENTRY_LOOK equ NS_IMAGE + 2  ; 5FD1Ch: the Look box's
NS_ENTRY_STATUS equ NS_IMAGE + 3 ; 71DF5h: the status under a portrait
SELL_KEEP equ NS_IMAGE + 4      ; 83D9Eh: a shop freeing an item sold
SELL_PRICE equ NS_IMAGE + 5     ; 83CCAh: what a shop pays for an item
ns_sites:                       ; (the game's registers kept for each: NS_CMP takes its site from RL_SITE)
        cmp byte [cs:rl_site], NS_KNOWN
        je ns_known
        cmp byte [cs:rl_site], NS_LEARN
        je ns_learn
        cmp byte [cs:rl_site], NS_NAME
        je ns_name
        cmp byte [cs:rl_site], NS_CLAW
        je ns_claw
        cmp byte [cs:rl_site], NS_HIT
        je ns_hit
        cmp byte [cs:rl_site], NS_FIST
        je ns_fist
        cmp byte [cs:rl_site], NS_IMAGE
        je ns_image
        cmp byte [cs:rl_site], SELL_KEEP
        je sell_keep
        cmp byte [cs:rl_site], SELL_PRICE
        je sell_price
        cmp byte [cs:rl_site], NS_ENTRY_EF
        jb .cmp
        cmp byte [cs:rl_site], NS_ENTRY_STATUS
        jbe ns_entry
.cmp:
        cmp byte [cs:rl_site], NS_CMP + NS_CMP_COUNT
        jb ns_cmp
        iret

; NS_CMP: the compare of site RL_SITE (of NS_CMP_SITES), its flags into the INT's frame.
ns_cmp:
        pushad
        push es
        mov di, sp
        call ns_setup
        movzx si, byte [cs:rl_site]
        sub si, NS_CMP
        imul si, si, 5
        add si, ns_cmp_sites
        mov cl, [cs:si]
        mov bx, [cs:si + 1]
        cmp cl, NS_K_R16
        jne .r8
        mov ax, [ss:di + bx]
        jmp .got
.r8:    cmp cl, NS_K_R8
        jne .bp16
        movzx ax, byte [ss:di + bx]
        jmp .got
.bp16:  push si
        mov si, bx              ; (BP's: [BP + SI])
        cmp cl, NS_K_BP16
        jne .bp8
        mov ax, [ss:bp + si]
        pop si
        jmp .got
.bp8:   cmp cl, NS_K_BP8
        jne .ds16
        movzx ax, byte [ss:bp + si]
        pop si
        jmp .got
.ds16:  pop si
        cmp cl, NS_K_DS16
        jne .esbx
        mov ax, [bx]
        jmp .got
.esbx:  add bx, [ss:di + 18]    ; (the game's BX)
        mov ax, [es:bx]
.got:   push ax
        call ns_new
        pop ax
        jnc .cmp
        xor ax, ax              ; (a new spell: as a wizard's)
.cmp:   mov dx, [cs:si + 3]
        test cl, 1
        jz .word
        cmp al, dl
        jmp .flags
.word:  cmp ax, dx
.flags: pushf
        pop ax
        call ns_flags
        pop es
        popad
        iret

; NS_KNOWN: "cmp si,4" (5DD04h; 3 bytes: the site's number after the INT) at the start of the
; routine (500:48h) giving the far address of thing SI's byte for spell DX (low four bits not 0:
; known; 0 for a party member's at 2F8h:168h, 8Ah bytes each). For a party member's new spell,
; NS_SCRATCH's byte for it, 1 if its sheet says known (NS_KNOWS), on to the routine's end with it.
NS_KNOWN_PAST equ 0x5DD6D - 0x5DD07
ns_scratch times 4 * NS_COUNT db 0
ns_known:
        pushad
        push es
        mov di, sp
        call ns_setup
        mov si, [ss:di + NS_SI]
        cmp si, 4
        pushf
        pop ax
        call ns_flags
        jge .out
        mov ax, [ss:di + NS_DX]
        call ns_new
        jnc .out
        mov cl, al
        mov ax, si
        call ns_knows
        setc al
        imul bx, si, NS_COUNT
        movzx cx, cl
        add bx, cx
        add bx, ns_scratch
        mov [cs:bx], al
        mov [ss:di + NS_AX], bx
        mov [ss:di + NS_DX], cs
        add word [ss:di + 34], NS_KNOWN_PAST
.out:   pop es
        popad
        iret

; NS_LEARN: "and byte es:[bx],0F0h / or byte es:[bx],1" (5E3F7h; 8 bytes: the site's number and 5
; NOPs after the INT), where the routine teaching a spell (500:43h) marks its byte (NS_KNOWN's) known:
; that, and for a new spell's byte in NS_SCRATCH, its bit in the member's sheet.
ns_learn:
        pushad
        push es
        and byte [es:bx], 0xF0
        or byte [es:bx], 1
        mov ax, es
        mov cx, cs
        cmp ax, cx
        jne .out
        sub bx, ns_scratch
        jb .out
        cmp bx, 4 * NS_COUNT
        jae .out
        mov ax, bx
        mov cl, NS_COUNT
        div cl                  ; (AL the member, AH the new spell)
        mov cl, ah
        movzx ax, al
        call thing_sheet
        call ns_sheet_learn
.out:   pop es
        popad
        iret

; NS_NAME: "cmp ax,8Ah" (5E560h; 3 bytes) in the routine giving spell AX's name (500:61h: DX:AX far,
; its row's +5 in DS): a new spell's is the helper's (NS_NAME_AT), on to the routine's end with it.
NS_NAME_PAST equ 0x5E57C - 0x5E563
ns_name:
        pushad
        push es
        mov di, sp
        mov ax, [ss:di + NS_AX]
        call ns_new
        jnc .game
        mov bx, ax
        shl bx, 1
        mov ax, [cs:bx + ns_name_at]
        mov [ss:di + NS_AX], ax
        mov [ss:di + NS_DX], cs
        add word [ss:di + 34], NS_NAME_PAST
        jmp .out
.game:  cmp ax, 0x8A
        pushf
        pop ax
        call ns_flags
.out:   pop es
        popad
        iret

; NS_CLAW: "or dx,dx / jne 7B755h" (7B70Ah; 4 bytes: the site's number and a NOP after the INT) in
; the routine giving natural attack DX of thing SI (7B66Ch; its dice's number to the far word at
; [BP+0Eh], their sides to [BP+12h], its bonus to [BP+16h], all set by now), where the game goes on
; to its effects only for the first (Body Weaponry's 2d4, Animal Affinity's 1d10). With Erdlu
; Claw's effect on it (NS_HAS), each natural attack is 1d6+1 where that is better on average than
; its own; then the game's way on.
NS_CLAW_PAST equ 0x7B755 - 0x7B70D
ns_claw:
        pushad
        push es
        mov di, sp
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .on
        mov ax, si
        mov cl, CLAW_EFFECT
        call ns_has
        jne .on
        les bx, [bp + 0x0E]     ; (its average, twice over: dice x (sides + 1) + 2 x bonus)
        mov ax, [es:bx]
        les bx, [bp + 0x12]
        mov cx, [es:bx]
        inc cx
        imul ax, cx
        les bx, [bp + 0x16]
        add ax, [es:bx]
        add ax, [es:bx]
        cmp ax, 9               ; (1d6+1's: 4.5)
        jge .on
        mov word [es:bx], 1
        les bx, [bp + 0x0E]
        mov word [es:bx], 1
        les bx, [bp + 0x12]
        mov word [es:bx], 6
.on:    cmp word [ss:di + NS_DX], 0
        je .out
        add word [ss:di + 34], NS_CLAW_PAST
.out:   pop es
        popad
        iret

; NS_IMAGE: "cmp ax,4Bh" (7A5CDh; 3 bytes) where a weapon's blow at thing SI with Mirror Images
; (25) on it strikes an image instead on a d100 (AX) of 75 or less: 50 or less for one of Reflected
; Image (the effect's spell, NS_EFFECT_SPELL), its flags into the INT's frame.
IMAGE_CHANCE equ 75
REFLECT_CHANCE equ 50
ns_image:
        pushad
        push es
        mov di, sp
        mov dx, IMAGE_CHANCE
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .cmp
        mov ax, [ss:di + NS_SI]
        mov cl, MIRROR_EFFECT
        call ns_effect_spell
        cmp ax, REFLECT_SPELL
        jne .cmp
        mov dx, REFLECT_CHANCE
.cmp:   mov ax, [ss:di + NS_AX]
        cmp ax, dx
        pushf
        pop ax
        call ns_flags
        pop es
        popad
        iret

; NS_ENTRY: "imul ax,ax,6" or "imul bx,bx,6" (3 bytes) where the Effects screen (its icons and
; names: AX the effect, on the character on show), the Look box (BX, on thing [BP+0Ah]) and the
; status under a portrait (BX, on party member DI) find an effect's entry in the effects' table
; (6 bytes each from effect 1: the name, far, then the icon) by its number times 6: Mirror Images
; put there by Reflected Image (NS_EFFECT_SPELL) is REFLECT_ENTRY's instead, its name and icon,
; which NS_SETUP keeps past the spell rows (as an entry of the table's segment).
NS_DI equ 2
NS_BX equ 18
EF_SHOWN_FROM_DS equ 0x4356 - 0x3931 ; the character on show on the Effects screen (348h:25Bh)
EF_SHOWN     equ 0x25B
REFLECT_ENTRY equ (SPELL_LEVELS_SEG + 0x4356 - 0x3F8D) * 16 + SPELL_LEVELS + (NS_FIRST + 16) * 7
ns_entry:
        pushad
        push es
        mov di, sp
        mov bx, NS_AX           ; (the frame's register: AX on the Effects screen, else BX)
        cmp byte [cs:rl_site], NS_ENTRY_EF
        je .ef
        mov bx, NS_BX
        mov ax, [ss:di + NS_DI]
        cmp byte [cs:rl_site], NS_ENTRY_STATUS
        je .thing
        mov ax, [bp + 0x0A]
        jmp .thing
.ef:    mov ax, ds
        sub ax, EF_SHOWN_FROM_DS
        mov es, ax
        mov ax, [es:EF_SHOWN]
.thing: mov dx, [ss:di + bx]    ; (DX the effect)
        cmp dx, MIRROR_EFFECT
        jne .times
        call ns_setup           ; (its entry as the rule has it now)
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .times
        cmp byte [cs:seg_moved], 0
        je .times
        mov cl, MIRROR_EFFECT
        call ns_effect_spell
        cmp ax, REFLECT_SPELL
        jne .times
        mov word [ss:di + bx], REFLECT_ENTRY + 6
        jmp .out
.times: imul dx, dx, 6
        mov [ss:di + bx], dx
.out:   pop es
        popad
        iret

; SELL_PRICE: "mov si,es:[bx+6]" (83CCAh; 4 bytes: the site's number and a NOP after the INT) where
; a shop takes the price it pays for the item the party sells (ES:BX the item; shown in its offer,
; then paid, times the count for a stack). With RULE_HI_CHA_PRICES, SELL_PERCENT of it (rounded
; down, never below 1): the leader's CHA takes at most 40% off buying (rounded down too), so
; nothing bought can be sold for more than it cost (prices.sell_price).
SELL_PERCENT equ 60
sell_price:
        pushad
        push es
        mov di, sp
        mov ax, [es:bx + 6]
        test word [cs:rules_hi], RULE_HI_CHA_PRICES
        jz .set
        cmp ax, 9999
        je .set
        cmp ax, 1
        jbe .set
        mov cx, SELL_PERCENT
        mul cx                  ; (DX:AX the price x 60)
        mov cx, 100
        div cx
        or ax, ax
        jnz .set
        inc ax
.set:   mov [ss:di + NS_SI], ax
        pop es
        popad
        iret

; SELL_KEEP: "push word [179Eh]" (83D9Eh; 4 bytes: the site's number and a NOP after the INT) where
; a shop has paid for the item the party sold and empties the item list of the thing holding it,
; the pointer's (0A0h:1C94h, which does nothing for 270Fh). With RULE_HI_BUYBACK and a magical item (a plus, +14h, or a power,
; +0Fh: rings, wands, scrolls...), 270Fh is pushed in its place and the thing and the merchant
; (DS:179Ch) queued (SOLD_Q, SOLD_SEQ) for the Loader, which puts the item in the merchant's pack,
; where the shop lists it; any other item is pushed and freed as the game does. The push: the
; registers kept and the interrupt's frame moved down a word, the word under them.
SOLD_SLOTS   equ 4              ; (SOLD_Q's room: 4 entries in the header)
SOLD_THING   equ 0x179E         ; DS: the thing holding the item sold ...
SHOP_MERCHANT equ 0x179C        ; ... and the shop's merchant
ITEM_PLUS_AT equ 0x14
ITEM_POWER_AT equ 0x0F
sell_keep:
        push ax
        push bx
        push cx
        push es
        mov cx, [SOLD_THING]
        test word [cs:rules_hi], RULE_HI_BUYBACK
        jz .push
        cmp cx, NO_THING
        jae .push
        mov bx, ds
        add bx, THINGS_SEG
        mov es, bx
        imul bx, cx, 3
        cmp byte [es:bx + THINGS], 1    ; (a list of items ...
        jne .push
        mov ax, [es:bx + THINGS + 1]    ;   ... its first)
        cmp ax, NO_THING
        jae .push
        les bx, [ITEMS]
        imul ax, ax, 0x15
        add bx, ax
        cmp byte [es:bx + ITEM_PLUS_AT], 0
        jg .keep
        cmp byte [es:bx + ITEM_POWER_AT], 0
        je .push
.keep:  mov bx, [cs:sold_seq]
        and bx, SOLD_SLOTS - 1
        shl bx, 2
        mov [cs:bx + sold_q], cx
        mov ax, [SHOP_MERCHANT]
        mov [cs:bx + sold_q + 2], ax
        inc word [cs:sold_seq]
        mov cx, NO_THING
.push:  mov bx, sp              ; (SS:BX: ES, CX, BX, AX, then the frame: IP, CS, flags)
        sub sp, 2
        mov ax, [ss:bx]
        mov [ss:bx - 2], ax
        mov ax, [ss:bx + 2]
        mov [ss:bx], ax
        mov ax, [ss:bx + 4]
        mov [ss:bx + 2], ax
        mov ax, [ss:bx + 6]
        mov [ss:bx + 4], ax
        mov ax, [ss:bx + 8]
        mov [ss:bx + 6], ax
        mov ax, [ss:bx + 10]
        mov [ss:bx + 8], ax
        mov ax, [ss:bx + 12]
        mov [ss:bx + 10], ax
        mov [ss:bx + 12], cx    ; (the word pushed)
        pop es
        pop cx
        pop bx
        pop ax
        iret

; NS_EFFECT_SPELL: AX the spell that put effect CL on thing AX (the game's table of active effects:
; the spell at +4), FFFFh if none. DS the game's; others kept.
ns_effect_spell:
        push bx
        push dx
        push es
        mov dx, ds
        sub dx, EFFECTS_FROM_DS
        mov es, dx
        mov dx, [EFFECTS_COUNT]
        mov bx, EFFECTS_OFF
.each:  or dx, dx
        jz .none
        cmp [es:bx], ax
        jne .next
        cmp [es:bx + 6], cl
        jne .next
        mov ax, [es:bx + 4]
        jmp .out
.next:  add bx, 10
        dec dx
        jmp .each
.none:  mov ax, 0xFFFF
.out:   pop es
        pop dx
        pop bx
        ret

; NS_HAS: ZF set if thing AX has effect CL (the game's table of active effects). DS the game's; all
; registers kept.
ns_has:
        push bx
        push dx
        push es
        mov dx, ds
        sub dx, EFFECTS_FROM_DS
        mov es, dx
        mov dx, [EFFECTS_COUNT]
        mov bx, EFFECTS_OFF
.each:  or dx, dx
        jz .none
        cmp [es:bx], ax
        jne .next
        cmp [es:bx + 6], cl
        je .out
.next:  add bx, 10
        dec dx
        jmp .each
.none:  or dx, 1
.out:   pop es
        pop dx
        pop bx
        ret

; NS_HIT: "test byte [bp-8],80h" (7C430h; 4 bytes: the site's number and a NOP after the INT) in the
; routine adding up an attack's to-hit adjustments from effects (7C3E9h: SI the sum; the attacker's
; bits at [BP-18h], the target's at [BP-0Eh]), where the target's Blur takes 2: Fogbolt's 3 off for
; a fogged attacker and 2 on against a fogged target (its AC 2 worse), then that test.
ns_hit:
        pushad
        push es
        mov di, sp
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .test
        test byte [bp - 0x18 + FOG_EFFECT / 8], 1 << (FOG_EFFECT % 8)
        jz .target
        sub word [ss:di + NS_SI], 3
.target:
        test byte [bp - 0x0E + FOG_EFFECT / 8], 1 << (FOG_EFFECT % 8)
        jz .test
        add word [ss:di + NS_SI], 2
.test:  test byte [bp - 8], 0x80
        pushf
        pop ax
        call ns_flags
        pop es
        popad
        iret

; NS_FIST: "cmp word [bp-0Ch],0" (58226h; 4 bytes: the site's number and a NOP after the INT) in the
; melee attack routine (58019h: SI the attacker; [BP-2] the weapon's item, -1 for none: a natural
; attack; [BP-8] its to-hit plus, taken off the THAC0; [BP-0Ch] its magic, which the hit's damage
; kinds then get as PLUS1..PLUS3). With Erdlu Claw's effect on the attacker, a natural attack is
; +1 to hit and at least a +1 weapon; then that compare.
ns_fist:
        pushad
        push es
        mov di, sp
        test byte [cs:rules], RULE_NEW_SPELLS
        jz .test
        cmp word [bp - 2], -1
        jne .test
        mov ax, si
        mov cl, CLAW_EFFECT
        call ns_has
        jne .test
        inc word [bp - 8]
        cmp word [bp - 0x0C], 1
        jge .test
        mov word [bp - 0x0C], 1
.test:  cmp word [bp - 0x0C], 0
        pushf
        pop ax
        call ns_flags
        pop es
        popad
        iret

; NAMES: the game's name table (GPLDATA's NAME chunk: 322 names of 25 bytes, which items name
; by number) gets NAMES_EXTRA more, for the Loader's own items (the Ring of Protection, the
; Thieves' Tools...). Where the game reserves memory for the chunk (as it starts, and as a game
; is loaded) PROBE_NAMES_SIZE makes the room for them; once it has read the chunk in,
; PROBE_NAMES_FILL copies EXTRA_NAMES after the game's own. Nothing in the game limits the
; numbers to its own 322.
NAMES_OWN    equ 0x142
NAME_SIZE    equ 25
NAMES_EXTRA  equ 35
NAMES_PTR    equ 0x166D         ; DS: far pointer to the name table

; PROBE_NAMES_SIZE: INT VEC_NAMES_SIZE replaces "push dword 1" (3 bytes: INT + NOP) just before
; the game reserves memory for the NAME chunk, its size the dword at [BP-4]: adds the room,
; then does the push (under the interrupt's return frame).
probe_names_size:
        add word [bp-4], NAMES_EXTRA * NAME_SIZE
        adc word [bp-2], 0
        pop word [cs:n_ip]
        pop word [cs:n_cs]
        pop word [cs:n_fl]
        push dword 1
        push word [cs:n_fl]
        push word [cs:n_cs]
        push word [cs:n_ip]
        iret

; PROBE_NAMES_FILL: INT VEC_NAMES_FILL replaces "add sp,0Ch" (3 bytes: INT + NOP) after the call
; that reads the NAME chunk into the table (AX 0: read). Does the add, then, if it was read,
; copies EXTRA_NAMES after the game's names and notes the table in NAMES_PTR.
probe_names_fill:
        pop word [cs:n_ip]
        pop word [cs:n_cs]
        pop word [cs:n_fl]
        add sp, 0x0C
        push word [cs:n_fl]
        push word [cs:n_cs]
        push word [cs:n_ip]
        or ax, ax
        jnz .out
        push cx
        push si
        push di
        push ds
        push es
        les di, [NAMES_PTR]
        mov [cs:names_ptr], di
        mov [cs:names_ptr+2], es
        add di, NAMES_OWN * NAME_SIZE
        push cs
        pop ds
        mov si, extra_names
        mov cx, NAMES_EXTRA * NAME_SIZE
        cld
        rep movsb
        pop es
        pop ds
        pop di
        pop si
        pop cx
.out:   iret
n_ip    dw 0
n_cs    dw 0
n_fl    dw 0

; TYPES: the game's item types (GPLDATA's IT1R chunk, 20 bytes each, which items name by
; number), read in just before the names, get TYPES_EXTRA more in the same way: for the
; companion's own items that no type of the game's fits (a metal short sword, a cloak of
; protection). Nothing in the game limits the numbers to its own.
TYPE_SIZE   equ 20
TYPES_EXTRA equ 27
TYPES_PTR   equ 0x1669          ; DS: far pointer to the item types
BRACERS     equ 8               ; (the bracers of defense: the ninth of them)
ROBE        equ 25              ; (the robes: dsloader/robes.py)
ELVEN_CLOAK equ 19              ; (the Cloak and Boots of Elvenkind)
ELVEN_BOOTS equ 20
GREYS_ARMS  equ 54              ; Grey's Scale's arm and leg armour: the game's AC 2 each, made 3
GREYS_LEGS  equ 24              ; (PROBE_TYPES_FILL)
AIR_CLERIC  equ 1               ; a type's +10h (the classes that may use it): the air cleric's bit

; PROBE_TYPES_SIZE: INT VEC_TYPES_SIZE replaces "push dword 1" (3 bytes: INT + NOP) before the
; game reserves memory for the IT1R chunk, its size the dword at [BP-4]: adds the room.
probe_types_size:
        add word [bp-4], TYPES_EXTRA * TYPE_SIZE
        adc word [bp-2], 0
        pop word [cs:n_ip]
        pop word [cs:n_cs]
        pop word [cs:n_fl]
        push dword 1
        push word [cs:n_fl]
        push word [cs:n_cs]
        push word [cs:n_ip]
        iret

; PROBE_TYPES_FILL: INT VEC_TYPES_FILL replaces "add sp,0Ch" (3 bytes: INT + NOP) after the
; call that reads the chunk in (AX 0: read). Does the add, then, if it was read, copies
; EXTRA_TYPES after the game's own (the room made, [BP-4], less theirs) and notes where;
; raises Grey's Scale's AC (its arm and leg armour, the game's own types) to 3; and lets air
; clerics use the game's daggers (17, 33, 84, 94: none had their bit; their sphere's weapons
; are daggers and missile and thrown ones).
probe_types_fill:
        pop word [cs:n_ip]
        pop word [cs:n_cs]
        pop word [cs:n_fl]
        add sp, 0x0C
        push word [cs:n_fl]
        push word [cs:n_cs]
        push word [cs:n_ip]
        or ax, ax
        jnz .out
        push ax
        push cx
        push dx
        push si
        push di
        push ds
        push es
        les di, [TYPES_PTR]
        mov [cs:types_ptr], di
        mov [cs:types_ptr+2], es
        mov byte [es:di+GREYS_ARMS*TYPE_SIZE+0x12], 3
        mov byte [es:di+GREYS_LEGS*TYPE_SIZE+0x12], 3
        or byte [es:di+17*TYPE_SIZE+0x10], AIR_CLERIC
        or byte [es:di+33*TYPE_SIZE+0x10], AIR_CLERIC
        or byte [es:di+84*TYPE_SIZE+0x10], AIR_CLERIC
        or byte [es:di+94*TYPE_SIZE+0x10], AIR_CLERIC
        mov ax, [bp-4]
        sub ax, TYPES_EXTRA * TYPE_SIZE
        add di, ax              ; after the game's own
        xor dx, dx
        mov cx, TYPE_SIZE
        div cx
        mov [cs:types_first], ax
        push cs
        pop ds
        mov si, extra_types
        mov cx, TYPES_EXTRA * TYPE_SIZE
        cld
        rep movsb
        pop es
        pop ds
        pop di
        pop si
        pop dx
        pop cx
        pop ax
.out:   iret
; the types, numbered from the game's count (115): the Loader's (the same as TYPES in
; dsloader/npcitems.py), the rest unused
extra_types:
        ; a metal short sword: the metal long sword's type (63), 1d6
        db 0x01, 0x00, 0x30, 0x00, 0x1E, 0x00, 0xFA, 0x00, 0x04, 0x05, 0x01, 0x01
        db 0x06, 0x01, 0x00, 0x00, 0x72, 0x16, 0x00, 0x01
        ; a cloak of protection: the Cloak's type (65), no material shown, its plus counting
        ; for AC (bit 80h of +0Fh, as armour's) with an AC of its own of 0
        db 0x00, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x0A, 0x00, 0x40, 0x08, 0x00, 0x00
        db 0x00, 0x00, 0x00, 0x80, 0xFF, 0x1F, 0x00, 0x01
        ; a bone helm: the Helm's type (5), of bone (to go with the bone scale armour), and like
        ; it for the classes that can wear it (+10h: no thieves, where the Helm allows them)
        db 0x00, 0x00, 0x00, 0x00, 0x0F, 0x00, 0xFA, 0x00, 0x01, 0x06, 0x00, 0x00
        db 0x00, 0x00, 0x00, 0x80, 0x6F, 0x12, 0x00, 0x00
        ; a bone short sword (a new warrior's, weaponchoice.py): the short sword's, of bone (+8),
        ; half its weight (+4), for the classes of the bone long sword and psionicists (+10h)
        db 0x01, 0x00, 0x30, 0x00, 0x0F, 0x00, 0xFA, 0x00, 0x01, 0x05, 0x01, 0x01
        db 0x06, 0x01, 0x00, 0x00, 0x78, 0x17, 0x00, 0x01
        ; a bone axe: the Axe's (22), of bone, for the bone weapons' classes (a water cleric's,
        ; not an earth cleric's); weighing 30 (+4), not HEAVY (over 30: the game's 70), as the
        ; obsidian one: light enough for the off hand
        db 0x01, 0x00, 0x10, 0x00, 0x1E, 0x00, 0xFA, 0x00, 0x01, 0x05, 0x01, 0x01
        db 0x08, 0x01, 0x00, 0x00, 0x78, 0x17, 0x00, 0x01
        ; an obsidian short sword: the short sword's, of obsidian, for the obsidian long sword's
        ; classes and psionicists
        db 0x01, 0x00, 0x30, 0x00, 0x1E, 0x00, 0xFA, 0x00, 0x03, 0x05, 0x01, 0x01
        db 0x06, 0x01, 0x00, 0x00, 0x7E, 0x17, 0x00, 0x01
        ; an obsidian axe: the Axe's, of obsidian, for the obsidian weapons' classes; weighing 30
        db 0x01, 0x00, 0x10, 0x00, 0x1E, 0x00, 0xFA, 0x00, 0x03, 0x05, 0x01, 0x01
        db 0x08, 0x01, 0x00, 0x00, 0x7E, 0x17, 0x00, 0x01
        ; a plain metal short sword: the first's (Kurzak's, which is his alone: Shadowseeker)
        db 0x01, 0x00, 0x30, 0x00, 0x1E, 0x00, 0xFA, 0x00, 0x04, 0x05, 0x01, 0x01
        db 0x06, 0x01, 0x00, 0x00, 0x72, 0x16, 0x00, 0x01
        ; bracers of defense (BRACERS): the cloak of protection's, worn on the arms (+9: 3, the
        ; arm armour's slot), their plus counting for AC; not armour to anything else here
        db 0x00, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x0A, 0x00, 0x40, 0x03, 0x00, 0x00
        db 0x00, 0x00, 0x00, 0x80, 0xFF, 0x1F, 0x00, 0x01
        ; metal versions of the game's plain weapons that have none (dsloader/worldgear.py):
        ; each its type of metal (+8: 4), for the metal long sword's clerics (+10h's low nibble:
        ; 2, earth's): the Dagger's (33), an air cleric's too (3), as every dagger
        db 0x01, 0x00, 0x20, 0x00, 0x0A, 0x00, 0xFA, 0x00, 0x04, 0x05, 0x01, 0x01
        db 0x04, 0x01, 0x00, 0x00, 0xF3, 0x1F, 0x00, 0x00
        ; the Mace's (20)
        db 0x01, 0x00, 0x08, 0x00, 0x64, 0x00, 0xFA, 0x00, 0x04, 0x05, 0x01, 0x01
        db 0x06, 0x01, 0x01, 0x00, 0x72, 0x16, 0x00, 0x01
        ; the Great Axe's (2)
        db 0x01, 0x00, 0x10, 0x00, 0x46, 0x00, 0xFA, 0x00, 0x04, 0x05, 0x01, 0x01
        db 0x0A, 0x01, 0x00, 0x40, 0x62, 0x16, 0x00, 0x02
        ; the pick's (112)
        db 0x01, 0x00, 0x20, 0x00, 0x28, 0x00, 0xFA, 0x00, 0x04, 0x05, 0x01, 0x01
        db 0x04, 0x01, 0x01, 0x00, 0x72, 0x17, 0x00, 0x00
        ; the Polearm's (19)
        db 0x01, 0x00, 0x30, 0x00, 0x96, 0x00, 0xFA, 0x00, 0x04, 0x05, 0x01, 0x01
        db 0x0A, 0x01, 0x00, 0x40, 0x72, 0x16, 0x00, 0x06
        ; a circlet and a crown (dsloader/worldgear.py): worn on the head (+9: 6), as the
        ; Necklace's (36) of no material, not armour (+0Fh: no 80h), for every class
        db 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0xFA, 0x00, 0x40, 0x06, 0x00, 0x00
        db 0x00, 0x00, 0x00, 0x00, 0xFF, 0x1F, 0x00, 0x00
        db 0x00, 0x00, 0x00, 0x00, 0x05, 0x00, 0xFA, 0x00, 0x40, 0x06, 0x00, 0x00
        db 0x00, 0x00, 0x00, 0x00, 0xFF, 0x1F, 0x00, 0x00
        ; plate mail (the Warden's Plate, dsloader/worldgear.py): the Chain's chest, arm and
        ; leg armour (57, 58, 59), heavier (+4: 250, 75, 75), AC 3, 2, 2 (+12h; chain's 2, 2, 1)
        db 0x00, 0x00, 0x00, 0x00, 0xFA, 0x00, 0xFA, 0x00, 0x04, 0x01, 0x00, 0x00
        db 0x00, 0x00, 0x00, 0x80, 0x6F, 0x12, 0x03, 0x01
        db 0x00, 0x00, 0x00, 0x00, 0x4B, 0x00, 0xFA, 0x00, 0x04, 0x03, 0x00, 0x00
        db 0x00, 0x00, 0x00, 0x80, 0x6F, 0x12, 0x02, 0x00
        db 0x00, 0x00, 0x00, 0x00, 0x4B, 0x00, 0xFA, 0x00, 0x04, 0x0A, 0x00, 0x00
        db 0x00, 0x00, 0x00, 0x80, 0x6F, 0x12, 0x02, 0x00
        ; the Cloak and Boots of Elvenkind (ELVEN_CLOAK, ELVEN_BOOTS: dsloader/worldgear.py,
        ; their stealth stealth.py): the Cloak's (65) and the Boots' (68), for thieves and rangers
        ; only (+10h: 600h, their class bits; a multiclass with either may wear them)
        db 0x00, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x0A, 0x00, 0x05, 0x08, 0x00, 0x00
        db 0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x00, 0x01
        db 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x0A, 0x00, 0x85, 0x04, 0x00, 0x00
        db 0x00, 0x00, 0x00, 0x00, 0x00, 0x06, 0x00, 0x00
        ; Galefang's (dsloader/worldgear.py): the metal Dagger's, air clerics' too (+10h: 1FF3h;
        ; fire and water clerics not); the type its own, as it was made when no other dagger was
        ; an air cleric's
        db 0x01, 0x00, 0x20, 0x00, 0x0A, 0x00, 0xFA, 0x00, 0x04, 0x05, 0x01, 0x01
        db 0x04, 0x01, 0x00, 0x00, 0xF3, 0x1F, 0x00, 0x00
        ; bone and obsidian great axes (dsloader/weaponchoice.py, worldgear.py): the metal one's,
        ; of bone (+8: 1; lighter, +4: 50, still too heavy to backstab with; water clerics, 1668h)
        ; and of obsidian (+8: 3; earth, fire and water clerics, 166Eh)
        db 0x01, 0x00, 0x10, 0x00, 0x32, 0x00, 0xFA, 0x00, 0x01, 0x05, 0x01, 0x01
        db 0x0A, 0x01, 0x00, 0x40, 0x68, 0x16, 0x00, 0x02
        db 0x01, 0x00, 0x10, 0x00, 0x46, 0x00, 0xFA, 0x00, 0x03, 0x05, 0x01, 0x01
        db 0x0A, 0x01, 0x00, 0x40, 0x6E, 0x16, 0x00, 0x02
        ; a bone dagger (dsloader/weaponchoice.py, worldgear.py): the obsidian Dagger's (17), of
        ; bone (+8: 1), for water and air clerics and not fire ones (+10h: 1FFBh; the game's
        ; obsidian daggers 1FF6h, an air cleric's bit added: PROBE_TYPES_FILL)
        db 0x01, 0x00, 0x20, 0x00, 0x0A, 0x00, 0xFA, 0x00, 0x01, 0x05, 0x01, 0x01
        db 0x04, 0x01, 0x00, 0x00, 0xFB, 0x1F, 0x00, 0x00
        ; a robe (ROBE: the Ashen Robe +1 and the Veiled Robe +2, dsloader/robes.py): the cloak
        ; of protection's, worn on the chest (+9: 1, the chest armour's slot), its plus counting
        ; for AC, not armour (as the bracers: BRACERS_AX), for preservers, psionicists and
        ; druids (+10h: 190h)
        db 0x00, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x0A, 0x00, 0x40, 0x01, 0x00, 0x00
        db 0x00, 0x00, 0x00, 0x80, 0x90, 0x01, 0x00, 0x01
        ; a metal shield (Ironbulwark +3, dsloader/worldgear.py): the game's leather Shield's
        ; (4), of metal (+8: 4), for the classes of its wooden one and its chain armour (+10h:
        ; 126Fh, no thieves); the game has no metal shield
        db 0x04, 0x00, 0x00, 0x00, 0x32, 0x00, 0xFA, 0x00, 0x04, 0x05, 0x00, 0x00
        db 0x00, 0x00, 0x00, 0x80, 0x6F, 0x12, 0x01, 0x00
; the names, numbered from NAMES_OWN (322): the Loader's items' (the same as the Loader's
; NAMES in dsloader/names.py), the rest blank until it writes more
extra_names:
        db "Ring/Protection"
        times NAME_SIZE - 15 db 0
        db "Thieves' Tools"
        times NAME_SIZE - 14 db 0
        db "Short Sword"                ; (Kurzak's, of type TYPES' first)
        times NAME_SIZE - 11 db 0
        db "Cloak/Protectn"             ; (Pehtucl's, the game's way of shortening)
        times NAME_SIZE - 14 db 0
        db "Ring/Protection"            ; (Pehtucl's ring: the arena's is the first; their icons differ)
        times NAME_SIZE - 15 db 0
        db "Shadowseeker"               ; (Kurzak's Short Sword made +1: MAGIC_ARMS)
        times NAME_SIZE - 12 db 0
        db "Kreenfang"                  ; (the arena's Bone Gythka made +1)
        times NAME_SIZE - 9 db 0
        db "Bracers/Defense"            ; (bracers of defense: BRACERS, dsloader/worldgear.py)
        times NAME_SIZE - 15 db 0
        db "Gutterknot"                 ; (the magic weapons of dsloader/worldgear.py: a club +1,
        times NAME_SIZE - 10 db 0
        db "Deepbiter"                  ; a stone pick +1,
        times NAME_SIZE - 9 db 0
        db "Windlash"                   ; a staff sling +1,
        times NAME_SIZE - 8 db 0
        db "Greenbright"                ; a metal short sword +2)
        times NAME_SIZE - 11 db 0
        db "Arrowbane"                  ; (the circlet and the crown of dsloader/worldgear.py)
        times NAME_SIZE - 9 db 0
        db "Sunking Crown"
        times NAME_SIZE - 13 db 0
        db "Warden's Chest"             ; (the Warden's Plate of dsloader/worldgear.py)
        times NAME_SIZE - 14 db 0
        db "Warden's Arms"
        times NAME_SIZE - 13 db 0
        db "Warden's Legs"
        times NAME_SIZE - 13 db 0
        db "Warden's Helm"
        times NAME_SIZE - 13 db 0
        db "Cloak/Elvenkind"            ; (the Cloak and Boots of Elvenkind)
        times NAME_SIZE - 15 db 0
        db "Boots/Elvenkind"
        times NAME_SIZE - 15 db 0
        db "Flame Blade"                ; (an obsidian long sword +1, Focus Heat on what it hits)
        times NAME_SIZE - 11 db 0
        db "Tome/Understand"            ; (the Tome of Understanding: dsloader/tome.py)
        times NAME_SIZE - 15 db 0
        db "Inixhide"                   ; (Legcrusher's Leather Chest Armor +1: dsloader/npcitems.py)
        times NAME_SIZE - 8 db 0
        db "Drakejaw"                   ; (the magic axes of dsloader/worldgear.py: a bone axe +1,
        times NAME_SIZE - 8 db 0
        db "Glasshewer"                 ; an obsidian axe +2,
        times NAME_SIZE - 10 db 0
        db "Headsman"                   ; a metal great axe +2)
        times NAME_SIZE - 8 db 0
        db "Galefang"                   ; (more magic weapons of dsloader/worldgear.py: an air
        times NAME_SIZE - 8 db 0        ; cleric's dagger +2,
        db "Mindshard"                  ; an obsidian short sword +1,
        times NAME_SIZE - 9 db 0
        db "Stillwater"                 ; a bone short sword +1,
        times NAME_SIZE - 10 db 0
        db "Linebreaker"                ; a metal polearm +2,
        times NAME_SIZE - 11 db 0
        db "Thornwall"                  ; a bone polearm +1)
        times NAME_SIZE - 9 db 0
        db "Ashen Robe"                 ; (the robes: dsloader/robes.py)
        times NAME_SIZE - 10 db 0
        db "Veiled Robe"
        times NAME_SIZE - 11 db 0
        db "Gutterward"                 ; (the magic shields of dsloader/worldgear.py: a wooden
        times NAME_SIZE - 10 db 0       ; shield +1,
        db "Ironbulwark"                ; a metal shield +3)
        times NAME_SIZE - 11 db 0
        times (NAMES_EXTRA - 35) * NAME_SIZE db 0

; STEALTH (RULE_STEALTH): a thief who starts a turn with no enemy next to them may hide in
; shadows and move silently up to someone; the Loader rolls both and, when both succeed,
; sets the thief's bit in STEALTH. Their next attack then counts as one from behind, and so
; as a backstab when the game's own conditions for one hold; the bit is cleared (attacking
; gives the thief away).
;
; PROBE_STEALTH: INT VEC_STEALTH replaces "push word [bp-1Ah]" (3 bytes: INT + NOP) in the
; routine that sets up an attack, straight after it has worked out whether the attacker (SI)
; is behind the target (DI) and whether that makes a backstab: [BP-1Ah] from behind (+2 to
; hit, the target's DEX and shield don't count), [BP-24h] a backstab (+2 more, and the damage
; multiplied), [BP-20h] the THAC0 they lower; [BP-1Ch] set when the target is an object, which
; has no back. Does the push (under the interrupt's return frame).
probe_stealth:
        pop word [cs:s_ip]
        pop word [cs:s_cs]
        pop word [cs:s_fl]
        test byte [cs:rules], RULE_STEALTH
        jz .push
        cmp si, 3
        ja .push
        btr word [cs:stealth], si
        jnc .push
        inc word [cs:stealth_used]
        cmp word [bp-0x1C], 0
        jne .push
        push ax
        push bx
        push es
        cmp word [bp-0x1A], 0
        jne .stab
        mov word [bp-0x1A], 1
        sub word [bp-0x20], 2
.stab:  cmp word [bp-0x24], 0
        jne .done
        ; the game's own conditions: a thief (the sheet's word +12h, bit 400h), in melee
        ; ([BP+0Eh] 1), with a weapon whose type weighs 40 or less (the type's word +4)
        mov ax, [bp-0x12]
        imul ax, ax, 0x47
        les bx, [0x1661]
        add bx, ax
        test word [es:bx+0x12], 0x400
        jz .done
        cmp word [bp+0x0E], 1
        jne .done
        mov ax, [bp-4]
        imul ax, ax, 0x14
        les bx, [0x1669]
        add bx, ax
        cmp word [es:bx+4], 0x28
        jg .done
        sub word [bp-0x20], 2
        mov word [bp-0x24], 1
.done:  pop es
        pop bx
        pop ax
.push:  call thief_rear
        call kit_rear
        push word [bp-0x1A]
        push word [cs:s_fl]
        push word [cs:s_cs]
        push word [cs:s_ip]
        iret
s_ip    dw 0
s_cs    dw 0
s_fl    dw 0

; KIT_REAR: in PROBE_STEALTH (SI the attacker, a creature; DS the game's), with kits on, after the
; game's (and the stealth rule's) from behind and backstab: a Military Scout's backstab taken back
; ([BP-24h] cleared, the 2 to hit it gave with it; kits.backstabs), a Rescuer's attack from behind
; 1 better to hit, not 2 (kits.REAR). All registers kept.
kit_rear:
        test word [cs:rules_hi], RULE_HI_KITS
        jz .ret
        cmp si, 3
        ja .ret
        push ax
        mov ax, si
        cmp word [bp-0x24], 0
        je .rescuer
        call cr_is
        db KIT_SCOUT
        jne .rescuer
        mov word [bp-0x24], 0
        add word [bp-0x20], 2
.rescuer:
        cmp word [bp-0x1A], 0
        je .out
        call cr_is
        db KIT_RESCUER
        jne .out
        inc word [bp-0x20]
.out:   pop ax
.ret:   ret

; THIEF_REAR: in PROBE_STEALTH (SI the attacker), a thief in armour that isn't light
; (THIEF_HEAVY) backstabs no more: [BP-24h] cleared, the 2 to hit it gave with it. All kept.
thief_rear:
        cmp si, 3
        ja .ret
        cmp word [bp-0x24], 0
        je .ret
        push ax
        mov ax, si
        call thief_heavy
        pop ax
        jnc .ret
        mov word [bp-0x24], 0
        add word [bp-0x20], 2
.ret:   ret

L_LINE_SIZE equ 24
LOOK_SIZE   equ 80
LOOK_FULL_SIZE equ 700
l_row   dw 0
l_draw  dd 0
l_win   dd 0
l_line  times L_LINE_SIZE db 0
l_side  db 0                    ; the line being drawn goes beside LEVEL (LOOK_SIDE)
look_pending db 0
look_text times LOOK_SIZE db 0
look_full times LOOK_FULL_SIZE db 0

USE_X      equ 0x96             ; the panel under the spells (window coordinates): its top,
USE_FIRST_Y equ 0x6C            ; three lines above where the icons of usable items (fruit,
USE_STEP   equ 7                ; wands...) go, along the panel's bottom from 0x81
USE_LAST_Y equ 0x7A
u_line  times SLOTS_SIZE db 0
slots_text times 4 * SLOTS_SIZE db 0

tput:                           ; AL -> text buffer at position BX
        push bx
        and bx, TSIZE - 1
        mov [cs:tbuf+bx], al
        pop bx
        inc bx
        ret

tputw:
        call tput
        mov al, ah
        jmp tput

t_ret   dw 0
t_ip    dw 0
t_cs    dw 0
t_fl    dw 0
kind    dw 0
extra   dw 0
SPELL_SEG equ 2 + 0x79BB7 - 0x79A85  ; return address - (DSUN.EXE offsets: patch, mov ax's operand)

; SHADOWS (SHADOWS_ON): every figure the Loader marks (SHADOW_TAB) casts a see-through shadow
; on the floor, its outline laid down toward the lower right (the light on Athas's maps comes from
; the upper left, as the walls' and bones' shadows show), drawn after the floor and before anything else, so
; walls and figures, its own and everyone else's, stand on it.
;
; The game draws a view of the map into a page of its planar (mode X) video memory: first the floor
; (DSUN.EXE 2700Eh: all of the view; 27162h: a rectangle of it), then, row by row, the walls and
; things standing on it and the figures (1DBD:0002). The floor routines are hooked at their start
; (PROBE_FLOOR): their way back is pointed at FLOOR_POST, which draws the shadows over the floor
; they have just drawn, clipped to it, then goes back (not when the routine draws nothing: then
; whatever is there was shadowed already). Each pixel of a shadow is darkened once, by DARK (each
; colour's nearest darker one, at 3/4 strength, among the colours the game doesn't animate). A
; figure's outline is its picture's: the runs of each row of the frame it is drawn with (no colours
; needed), its picture loaded into the cache first if it isn't in memory (as drawing it is about to;
; in a fight most aren't till then).
;
; A figure that moves is drawn again within a rectangle round where it was and where it is; its
; shadow reaches beyond its picture, so the routines redrawing rectangles (PROBE_REDRAW: 2475Fh, a
; rectangle; PROBE_REDRAW_ALL: 24B18h, the one round everything that moved) make theirs bigger by
; as far as a shadow reaches (SHADOW_RIGHT, SHADOW_DOWN), or the old shadow would be left behind.

SHADOW_ROWS  equ 64             ; rows of a figure, up from its feet, that cast a shadow
SHADOW_RIGHT equ 72             ; how far right a shadow reaches past its figure (SHADOW_ROWS * 1.05,
                                ;   and a step of 4: rectangles are kept to whole bytes)
SHADOW_DOWN  equ 44             ; and how far down (SHADOW_ROWS / 2, and a figure's height off the
                                ;   ground)
PAGES_SEG    equ 0x0980         ; (DSUN.EXE segments, less the load segment) the page routines',
                                ;   whose code segment holds the pages' table
CACHE_SEG    equ 0x3E60         ; the picture cache's table: 16 bytes a slot
OBJ_LIST     equ 0x6690         ; DS: far pointer to the things on the map, 8 bytes each (x, y,
OBJ_COUNT    equ 0x1F72         ;   height, flags, which thing), and how many
MAP_THINGS   equ 0x6694         ; DS: each thing on the map, 32 bytes (sprites.py)
MAP_COUNT    equ 520            ; how many things the game has
CACHE_LAST   equ 0x1F84         ; DS: the last slot of the picture cache
FLOOR_ON     equ 0x2F44         ; DS: 0 when the floor routines draw nothing
LOADER_SEG   equ 0x1DF3         ; (DSUN.EXE 25D6Ah) the routine that loads a picture into the cache
LOADER_OFF   equ 0x2A3A         ;   (slot, 0), as drawing one does when it isn't in memory
FIGURE_MOST  equ 128            ; (the widest and tallest a figure's picture may be, for the test of
                                ;   whether its shadow can be where the floor was drawn)

; PROBE_REDRAW: INT VEC_REDRAW replaces "push bp / mov bp,sp / sub sp,8" (6 bytes: INT + 4 NOPs)
; at the start of the routine that draws a rectangle of the view again (camera x, y, page, x0,
; y0, x1, y1, a flag: then shown by a flip of the screens and copied to the other): with shadows
; on, the rectangle reaches further right and down. With the combat log's panel on screen, a
; rectangle over it is drawn as the parts of it around the panel (REDRAW_PARTS), so nothing the
; game draws there covers it; the routine itself is then left out, its caller's way back kept in a
; frame of the routine's own shape (BP, the way back, the arguments), which the overlay manager
; can fix up. The parts come back through here (RP_BUSY): as they are.
REDRAW_SEG equ 0x1DF3           ; (DSUN.EXE 2475Fh: 1DF3:142F, the routine's own address)
REDRAW_OFF equ 0x142F
probe_redraw:
        cmp byte [cs:rp_busy], 0
        jne .go
        push bp
        mov bp, sp
        cmp word [cs:shadows_on], 0
        jne .wide
        cmp word [cs:rings_on], 0
        je .wided
.wide:
        add word [bp+22], SHADOW_RIGHT  ; x1 (after BP, the interrupt's IP, CS and flags, and the
        add word [bp+24], SHADOW_DOWN   ;   caller's way back); y1 (the routine keeps both on screen)
.wided: pop bp
.go:    pop word [cs:resume]
        pop word [cs:resume + 2]
        popf
        cmp byte [cs:rp_busy], 0
        jne .plain
        push bp                         ; (the routine's frame: x0 [BP+0Ch], y0, x1, y1, flag)
        mov bp, sp
        push ax
        push bx
        push cx
        push dx
        mov ax, [bp+0x0C]
        mov bx, [bp+0x0E]
        mov cx, [bp+0x10]
        mov dx, [bp+0x12]
        call clip_check
        jnc .whole
        mov ax, [bp+6]
        mov [cs:rp_camx], ax
        mov ax, [bp+8]
        mov [cs:rp_camy], ax
        mov ax, [bp+0x0A]
        mov [cs:rp_page], ax
        mov ax, [bp+0x14]
        mov [cs:rp_flag], ax
        call redraw_parts
        pop dx
        pop cx
        pop bx
        pop ax
        mov ax, 1                       ; (drawn, as the routine says)
        pop bp
        retf                            ; (to the caller, which takes its arguments off)
.whole: pop dx
        pop cx
        pop bx
        pop ax
        pop bp
.plain: push bp
        mov bp, sp
        sub sp, 8
        jmp far [cs:resume]

; CLIP_CHECK: CF set if the rectangle (AX x0, BX y0, CX x1, DX y1) is to be drawn in parts round
; the panel: the panel on screen and the rectangle over it (on screen, in whole bytes of the planes,
; as the routine draws it). Its bounds then in RP_X0 to RP_Y1. Keeps all.
clip_check:
        cmp word [cs:panel_on], 0
        je .no
        call panel_live
        jne .no
        push ax
        push bx
        push cx
        push dx
        or ax, ax
        jge .x0
        xor ax, ax
.x0:    or bx, bx
        jge .y0
        xor bx, bx
.y0:    cmp cx, 0x13F
        jle .x1
        mov cx, 0x13F
.x1:    cmp dx, 0xC7
        jle .y1
        mov dx, 0xC7
.y1:    and ax, 0xFFFC
        or cx, 3
        cmp cx, PANEL_X0
        jl .out
        cmp ax, PANEL_X0 + PANEL_W - 1
        jg .out
        cmp dx, [cs:panel_top]
        jl .out
        push si
        mov si, [cs:panel_top]
        add si, [cs:panel_rows]
        dec si
        cmp bx, si
        pop si
        jg .out
        mov [cs:rp_x0], ax
        mov [cs:rp_y0], bx
        mov [cs:rp_x1], cx
        mov [cs:rp_y1], dx
        pop dx
        pop cx
        pop bx
        pop ax
        stc
        ret
.out:   pop dx
        pop cx
        pop bx
        pop ax
.no:    clc
        ret

; REDRAW_PARTS: the rectangle RP_X0 to RP_Y1 drawn by the routine (RP_CAMX, RP_CAMY, RP_PAGE,
; RP_FLAG as given) as up to four parts round the panel: above it, below it, and to its left and
; right. With the flag (the screens flipped, the parts copied to the other), the panel is put on
; the other screen first, so whichever is shown has it. DS the game's; BP kept (the caller's frame,
; for the overlay manager); keeps all.
redraw_parts:
        pusha
        push es
        mov byte [cs:rp_busy], 1
        mov ax, ds
        sub ax, DGROUP_SEG - REDRAW_SEG
        mov [cs:redraw_far + 2], ax
        cmp word [cs:rp_flag], 0
        je .parts
        call panel_draw_other
.parts: mov si, [cs:panel_top]          ; SI the panel's top, DI its bottom row
        mov di, si
        add di, [cs:panel_rows]
        dec di
        mov bx, [cs:rp_y0]              ; above it
        cmp bx, si
        jge .below
        mov dx, si
        dec dx
        cmp dx, [cs:rp_y1]
        jle .a
        mov dx, [cs:rp_y1]
.a:     mov ax, [cs:rp_x0]
        mov cx, [cs:rp_x1]
        call rp_call
.below: mov dx, [cs:rp_y1]
        cmp dx, di
        jle .mid
        mov bx, di
        inc bx
        cmp bx, [cs:rp_y0]
        jge .b
        mov bx, [cs:rp_y0]
.b:     mov ax, [cs:rp_x0]
        mov cx, [cs:rp_x1]
        call rp_call
.mid:   mov bx, [cs:rp_y0]              ; its rows: to the left and right of it
        cmp bx, si
        jge .m0
        mov bx, si
.m0:    mov dx, [cs:rp_y1]
        cmp dx, di
        jle .m1
        mov dx, di
.m1:    mov [cs:rp_ym0], bx
        mov [cs:rp_ym1], dx
        mov ax, [cs:rp_x0]
        cmp ax, PANEL_X0
        jge .right
        mov cx, PANEL_X0 - 1
        call rp_call
.right: mov cx, [cs:rp_x1]
        cmp cx, PANEL_X0 + PANEL_W - 1
        jle .done
        mov ax, PANEL_X0 + PANEL_W
        mov bx, [cs:rp_ym0]
        mov dx, [cs:rp_ym1]
        call rp_call
.done:  cmp word [cs:rp_flag], 0        ; (flipped: the screen shown now the one it is drawn into)
        je .out
        call panel_live
        je .out
        call panel_draw_pointer         ; (the parts drew the pointer again: kept over the panel)
.out:   mov byte [cs:rp_busy], 0
        pop es
        popa
        ret

; RP_CALL: the routine for the part AX x0, BX y0, CX x1, DX y1 (AX to DX and ES not kept)
rp_call:
        push word [cs:rp_flag]
        push dx
        push cx
        push bx
        push ax
        push word [cs:rp_page]
        push word [cs:rp_camy]
        push word [cs:rp_camx]
        call far [cs:redraw_far]
        add sp, 16
        ret
redraw_far dw REDRAW_OFF, 0
rp_busy  db 0
rp_camx  dw 0
rp_camy  dw 0
rp_page  dw 0
rp_flag  dw 0
rp_x0    dw 0
rp_y0    dw 0
rp_x1    dw 0
rp_y1    dw 0
rp_ym0   dw 0
rp_ym1   dw 0

; PROBE_REDRAW_ALL: INT VEC_REDRAW_ALL replaces "push word [bp+8] / push word [bp+6]" (6 bytes:
; INT + 4 NOPs) where the routine drawing again what moved, having made the rectangle round it all
; (x0 at [BP-8], x1 [BP-0Ah], y0 [BP-0Ch], y1 [BP-0Eh]), starts to draw: with shadows on, it
; reaches further right and down; over the combat log's panel, it is drawn in parts round it by
; the routine PROBE_REDRAW is in (REDRAW_PARTS), and this one goes on at its end (24C65h).
REDRAW_ALL_AT  equ 0x24B1A      ; (DSUN.EXE: the way back of the INT)
REDRAW_ALL_END equ 0x24C65      ; ("mov ax,1", then its return)
probe_redraw_all:
        pop word [cs:resume]
        pop word [cs:resume + 2]
        pop word [cs:resume_fl]
        cmp word [cs:shadows_on], 0
        jne .wide
        cmp word [cs:rings_on], 0
        je .dust
.wide:  add word [bp-0x0A], SHADOW_RIGHT
        cmp word [bp-0x0A], 0x13F       ; (the routine draws to x1 + 1: kept on screen)
        jle .x
        mov word [bp-0x0A], 0x13F
.x:     add word [bp-0x0E], SHADOW_DOWN
        cmp word [bp-0x0E], 0xC7
        jle .dust
        mov word [bp-0x0E], 0xC7
.dust:  call dust_union
        push ax                         ; (over the combat log's panel: drawn in parts round it,
        push bx                         ;   the routine's own drawing left out: on at its end)
        push cx
        push dx
        mov ax, [bp-8]
        mov bx, [bp-0x0C]
        mov cx, [bp-0x0A]
        mov dx, [bp-0x0E]
        call clip_check
        jnc .whole
        mov ax, [bp+6]
        mov [cs:rp_camx], ax
        mov ax, [bp+8]
        mov [cs:rp_camy], ax
        mov ax, [bp+0x0A]
        mov [cs:rp_page], ax
        mov ax, [bp+0x0E]
        mov [cs:rp_flag], ax
        push word [cs:resume_fl]        ; (the way back kept: the parts' routine, and the floor's
        push word [cs:resume + 2]       ;   within it, come through probes that use RESUME too)
        push word [cs:resume]
        call redraw_parts
        pop word [cs:resume]
        pop word [cs:resume + 2]
        pop word [cs:resume_fl]
        pop dx
        pop cx
        pop bx
        pop ax
        add word [cs:resume], REDRAW_ALL_END - REDRAW_ALL_AT
        push word [cs:resume_fl]
        push word [cs:resume + 2]
        push word [cs:resume]
        iret
.whole: pop dx
        pop cx
        pop bx
        pop ax
.go:    push word [bp+8]
        push word [bp+6]
        push word [cs:resume_fl]
        push word [cs:resume + 2]
        push word [cs:resume]
        iret

; PROBE_FLOOR: INT VEC_FLOOR_ALL and INT VEC_FLOOR_RECT replace "push bp / mov bp,sp / sub sp,N"
; (6 bytes: INT + 4 NOPs) at the start of the routines drawing the floor of the view (page, camera
; x, y) and of a rectangle of it (page, x0, y0, x1 + 1, y1, camera x, y). With shadows on, their
; way back is FLOOR_POST.
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
        cmp word [cs:panel_on], 0       ; (the floor drawn over the panel, maybe: drawn again)
        je .shade
        mov byte [cs:panel_dirty], 1
.shade:
        cmp word [cs:shadows_on], 0
        jne .on
        cmp word [cs:dust_on], 0
        jne .on
        cmp word [cs:rings_on], 0
        je .plain
.on:    cmp byte [cs:floor_busy], 0
        jne .plain
        cmp word [FLOOR_ON], 0          ; (DS: the game's) the routine draws nothing without it
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

; the floor drawn: the shadows on it, then back to the caller (its arguments still on the stack)
floor_post:
        pushf
        pushad
        push ds
        push es
        mov bp, sp
        call shadow_pass
        pop es
        pop ds
        popad
        popf
        mov byte [cs:floor_busy], 0
        jmp far [cs:floor_ret]

F_ARGS equ 38                   ; (FLOOR_POST's frame: ES, DS, PUSHAD, flags, then the arguments)

shadow_pass:
        cld
        inc word [cs:shadow_passes]
        mov [cs:game_ds], ds
        mov ax, ds
        sub ax, DGROUP_SEG
        mov [cs:load_seg], ax
        ; the page: where it is (its bounds, the clip), and the page it is part of (its memory)
        add ax, PAGES_SEG
        mov es, ax
        mov bx, [bp + F_ARGS]
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
        ; the camera, and for a rectangle's floor the rectangle
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
        cmp word [cs:dark_build], 0
        je .dark
        call build_dark
        jc .dark                        ; (not yet: the screen is fading)
        mov word [cs:dark_build], 0
.dark:  call vga_save
        cmp word [cs:shadows_on], 0
        je .dust
        cmp byte [cs:dark_ready], 0
        je .dust                        ; (no colours to darken with yet)
        mov ds, [cs:game_ds]
        les di, [OBJ_LIST]
        mov cx, [OBJ_COUNT]
        jcxz .done
.thing: push cx
        push di
        push es
        call shadow_of
        pop es
        pop di
        pop cx
        add di, 8
        loop .thing
.dust:  call ring_pass
        call dust_pass
.done:  call vga_restore
        ret

; SHADOW_GONE: CF set if thing BX (DS the game's) is a creature dying or dead (its +1Ch, 4 or 5): the
; companion's SHADOW_TAB is made afresh only every half second, and a creature's death changes its
; pictures, which SHADOW_OF would load from the floor routine, in the middle of the game's drawing.
; All registers kept.
SH_DYING     equ 4
SH_DEAD      equ 5
shadow_gone:
        push ax
        push si
        push es
        mov ax, ds
        add ax, THINGS_SEG
        mov es, ax
        imul si, bx, 3
        cmp byte [es:si + THINGS], 2
        jne .alive                      ; (not a creature)
        mov ax, [es:si + THINGS + 1]
        les si, [CREATURES]
        imul ax, ax, 0x3A
        add si, ax
        mov al, [es:si + 0x1C]
        cmp al, SH_DYING
        je .gone
        cmp al, SH_DEAD
        je .gone
.alive: clc
        jmp .out
.gone:  stc
.out:   pop es
        pop si
        pop ax
        ret

; the shadow of the thing at ES:DI (DS = the game's), if it casts one
shadow_of:
        mov bx, [es:di + 6]
        cmp bx, MAP_COUNT - 1
        ja .no                          ; (none)
        cmp byte [cs:shadow_tab + bx], 0
        je .no
        call shadow_gone                ; (a creature dying or dead since SHADOW_TAB was made: none,
        jc .no                          ;   nor its new pictures loaded in the middle of a drawing)
        shl bx, 5
        add bx, MAP_THINGS
        test byte [bx], 0x80
        jnz .no                         ; (not drawn)
        mov si, [bx + 0x0F]             ; its picture's place in the cache
        cmp si, 0xFFFF
        je .no
        cmp si, [CACHE_LAST]
        ja .no
        ; where its picture is drawn (as the game works it out), on the ground
        mov al, [es:di + 5]
        mov [cs:mirror], al
        xor dx, dx
        test al, 0x20
        jz .fixed
        mov ax, [es:di]
        mov dl, [bx + 7]
        sub ax, dx
        sub ax, [cs:cam_x]
        mov [cs:fig_x], ax
        mov ax, [es:di + 2]
        mov dl, [bx + 8]
        sub ax, dx                      ; (its height off the ground left out: the shadow is on it)
        sub ax, [cs:cam_y]
        mov [cs:fig_y], ax
        jmp .frame
.fixed: mov ax, [bx + 3]
        sub ax, [cs:cam_x]
        mov [cs:fig_x], ax
        mov ax, [bx + 5]
        sub ax, [cs:cam_y]
        mov [cs:fig_y], ax
.frame: mov al, [bx + 0x11]
        xor ah, ah
        mov [cs:frame], ax
        ; (none of its shadow where the floor was drawn: nothing to do)
        mov ax, [cs:fig_x]
        cmp ax, [cs:clip_x1]
        jg .no
        add ax, FIGURE_MOST + SHADOW_RIGHT
        cmp ax, [cs:clip_x0]
        jl .no
        mov ax, [cs:fig_y]
        cmp ax, [cs:clip_y1]
        jg .no
        add ax, FIGURE_MOST + SHADOW_DOWN
        cmp ax, [cs:clip_y0]
        jl .no
        ; its picture, if in the cache
        mov ax, [cs:load_seg]
        add ax, CACHE_SEG
        mov es, ax
        shl si, 4
        cmp dword [es:si + 6], 0
        jl .no
        test byte [es:si + 0x0E], 2
        jnz .loaded
        shr si, 4                       ; (not in memory: loaded, as drawing it is about to)
        push si
        mov ax, [cs:load_seg]
        add ax, LOADER_SEG
        mov [cs:loader + 2], ax
        push word 0
        push si
        call far [cs:loader]
        add sp, 4
        pop si
        or ax, ax
        jz .no
        mov ax, [cs:load_seg]
        add ax, CACHE_SEG
        mov es, ax
        shl si, 4
.loaded:
        les si, [es:si + 0x0A]
        mov bx, [cs:frame]
        cmp bx, [es:si + 4]
        jae .no
        shl bx, 2
        movzx eax, word [cs:zero]       ; (EAX: the frame's address, linear)
        mov ax, es
        shl eax, 4
        movzx ecx, si
        add eax, ecx
        add eax, [es:si + bx + 6]
        mov si, ax
        and si, 0x0F
        shr eax, 4
        mov es, ax
        ; the frame: width, height, then its rows
        mov ax, [es:si]
        mov [cs:f_w], ax
        mov ax, [es:si + 2]
        dec ax
        mov [cs:f_bottom], ax
        add si, 4
.row:   mov al, [es:si]
        inc si
        cmp al, 0xFF
        je .drawn
        xor ah, ah
        mov [cs:f_y], ax
.run:   mov ax, [es:si]                 ; a run: x (8000h: the row's last), its pixels, its data
        mov [cs:r_x], ax
        mov cl, [es:si + 2]
        mov [cs:r_n], cl
        mov dl, [es:si + 3]
        xor dh, dh
        add si, 4
        add si, dx
        mov ax, [cs:f_bottom]
        sub ax, [cs:f_y]                ; how far up from the feet
        jl .next
        cmp ax, SHADOW_ROWS
        jg .next
        test al, 1
        jnz .next                       ; (every other row: the shadow is half as tall)
        push es
        push si
        call cast_run
        pop si
        pop es
.next:  test byte [cs:r_x + 1], 0x80
        jz .run
        jmp .row
.drawn: push es                         ; (its runs: drawn)
        call spans_flush
        pop es
.no:    ret

; the shadow of the current run, AX rows up from the feet
cast_run:
        mov bx, ax
        shr bx, 1
        add bx, [cs:f_bottom]
        add bx, [cs:fig_y]              ; BX: the screen row it falls on
        mov dx, [cs:r_x]
        and dx, 0x7FFF
        xor ch, ch
        mov cl, [cs:r_n]
        test byte [cs:mirror], 0x80
        jz .lean
        mov di, [cs:f_w]                ; (drawn mirrored: from the other side)
        sub di, dx
        sub di, cx
        mov dx, di
.lean:  add dx, [cs:fig_x]
        mov di, ax                      ; leaning right by 1.05 times as far as it is up
        add ax, 10
        push dx
        xor dx, dx
        push bx
        mov bx, 20
        div bx
        pop bx
        pop dx
        add di, ax
        add dx, di                      ; DX: its first x
        mov di, dx
        add di, cx
        dec di                          ; DI: its last
        call darken
        ret

; darken DX..DI on row BX (screen), within the clip: noted (SPANS), and drawn with the figure's
; others a plane at a time (SPANS_FLUSH: the VGA's registers set once a plane, not once a run; a
; figure's runs never overlap, so the order makes no difference)
SPANS_MOST equ 256
darken: cmp bx, [cs:clip_y0]
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
        cmp word [cs:n_spans], SPANS_MOST
        jb .room
        push dx
        push di
        push bx
        call spans_flush                ; (full: those so far drawn first)
        pop bx
        pop di
        pop dx
.room:  push dx
        mov ax, bx                      ; the row's place in the page
        sub ax, [cs:v_y0]
        mul word [cs:v_row]
        sub ax, [cs:v_x0]
        pop dx
        mov bx, [cs:n_spans]
        imul bx, bx, 6
        mov [cs:spans + bx], ax
        mov [cs:spans + bx + 2], dx
        mov [cs:spans + bx + 4], di
        inc word [cs:n_spans]
.out:   ret

spans_flush:                            ; the noted runs darkened, a plane at a time
        cmp word [cs:n_spans], 0
        je .ret
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
        xor si, si
.span:  mov ax, cx
        sub ax, [cs:spans + si + 2]
        and ax, 3
        add ax, [cs:spans + si + 2]     ; the first x on this plane
        mov dx, [cs:spans + si + 4]
        sub dx, ax
        jl .nspan
        shr dx, 2
        inc dx                          ; DX: how many
        shr ax, 2
        add ax, [cs:spans + si]
        mov di, ax
        xor bh, bh
.pix:   mov bl, [es:di]
        mov bl, [cs:dark + bx]
        mov [es:di], bl
        inc di
        dec dx
        jnz .pix
.nspan: add si, 6
        mov ax, [cs:n_spans]
        imul ax, ax, 6
        cmp si, ax
        jb .span
        inc cx
        cmp cx, 4
        jb .plane
        mov word [cs:n_spans], 0
.ret:   ret

n_spans dw 0
spans   times SPANS_MOST * 6 db 0       ; (row's place in the page, first x, last x)

; the VGA's registers the shadows change, kept and put back
vga_save:
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
        ret

; DARK: for each colour of the palette as it is now, the nearest to it at 3/4 strength among the
; colours the game doesn't animate (DARK_FIRST-DARK_LAST: 11-15 and 224-255 cycle, for fire and
; water); made again when the area, so the palette, changes
DARK_FIRST equ 16
DARK_LAST  equ 223
DARK_PARTS equ 3                ; (a shadow's strength: 3/4, as the walls' own shadows on the floor)
DARK_WHOLE equ 4
DARK_HUE   equ 4                ; (how much a change of hue counts against a colour)
DARK_LIT   equ 4000             ; (the palette's 768 values, out of 63 each, add up to less in a fade)
build_dark:
        push ds
        push cs
        pop ds
        mov dx, 0x3C7
        xor al, al
        out dx, al
        mov dx, 0x3C9
        mov di, dac
        mov cx, 768
        xor bx, bx                      ; (BX: how bright it is in all)
.read:  in al, dx
        mov [di], al
        xor ah, ah
        add bx, ax
        inc di
        loop .read
        cmp bx, DARK_LIT
        jae .lit
        pop ds                          ; (nearly black: a fade, not the area's colours)
        stc
        ret
.lit:
        xor bx, bx                      ; the colour
.colour:
        mov si, bx
        imul si, si, 3
        add si, dac
        xor di, di                      ; its darker self
.chan:  lodsb
        mov ah, DARK_PARTS
        mul ah
        mov dl, DARK_WHOLE
        div dl
        mov [want + di], al
        inc di
        cmp di, 3
        jb .chan
        mov si, bx                      ; (only clearly darker ones: brightness under 7/8 of its own)
        imul si, si, 3
        add si, dac
        xor ax, ax
        xor dx, dx
        mov di, 3
.own:   lodsb
        add dx, ax
        dec di
        jnz .own
        imul dx, dx, 7
        shr dx, 3
        mov [lit_most], dx
        mov dword [best_d], 0xFFFFFFFF
        mov [best_c], bl
        mov cx, DARK_FIRST
.cand:  mov word [lit_sum], 0
        mov si, cx                      ; how far a colour is from the one wanted: the differences
        imul si, si, 3                  ;   squared, and those between them weighted (DARK_HUE),
        add si, dac                     ;   so that it keeps its hue (sand stays sand, not pink)
        xor di, di
.diff:  lodsb
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
        jae .worse                      ; (not darker enough)
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
        imul eax, eax, DARK_HUE
        add edx, eax
        movsx eax, byte [diffs + 1]
        movsx edi, byte [diffs + 2]
        sub eax, edi
        imul eax, eax
        imul eax, eax, DARK_HUE
        add edx, eax
        cmp edx, [best_d]
        jae .worse
        mov [best_d], edx
        mov [best_c], cl
.worse: inc cx
        cmp cx, DARK_LAST
        jbe .cand
        mov al, [best_c]
        mov [dark + bx], al
        inc bx
        cmp bx, 256
        jb .colour
        mov byte [dark_ready], 1
        pop ds
        clc
        ret

; SCROLLING (SCROLL_ON): holding the right mouse button and moving scrolls the map with the pointer,
; as if dragging it; a right click (released before the pointer has moved DRAG_START pixels) is
; still the game's (it changes what the pointer does: walk, use, look).
;
; The game is told of the mouse's buttons by the mouse driver calling its handler (INT 33h, 0Ch).
; INT33 puts MOUSE_EVENT in its place, which keeps the right button from the game while it is
; held: if it was a click, the game gets the press and the release when it is let go; if it was a
; drag, nothing. The game's main loop reads where the pointer is (DSUN.EXE 1CAACh, the call to the
; driver's 03h), to scroll the map when it is at the screen's edge; PROBE_SCROLL makes that call
; itself and, while dragging, has the game centre its view where the drag puts it (191F:0281h, as
; clicking on the overview map does: the view is then drawn again), and the pointer is kept off
; the edges. It also scrolls by what the Loader adds to PAN_X and PAN_Y.

DRAG_START  equ 4               ; pixels the pointer moves before a right click is a drag
CAM_X       equ 0x1178          ; DS: the view's top left on the map
CAM_Y       equ 0x117A
CAM_X_MOST  equ 0x6C0           ; (as far as the game lets it go: the map less the view)
CAM_Y_MOST  equ 0x558
CENTRE_SEG  equ 0x191F          ; (DSUN.EXE 1E871h) centre the view on (x, y, 1: draw it again)
CENTRE_OFF  equ 0x0281
EVENT_PRESS equ 8               ; the driver's events: right button pressed, released
EVENT_LEAVE equ 16
RIGHT       equ 2               ; the right button, in the buttons held
MIDDLE      equ 4               ; the middle one (pressing the wheel)
EVENT_MID_PRESS equ 0x20
EVENT_MID_LEAVE equ 0x40
SCROLL_MIDDLE equ 1             ; SCROLL_ON's bits: dragging with the wheel pressed,
SCROLL_RIGHT  equ 2             ;   with the right button held

int33:
        cmp ax, 0x0C
        jne .chain
        or cx, cx
        jz .chain                       ; (taking the handler away)
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
.chain: jmp far [cs:old33]

mouse_event:                            ; AX = events, BX = buttons held, CX, DX = where
        call panel_mouse
        cmp word [cs:scroll_on], 0
        je .pass
        test byte [cs:scroll_on], SCROLL_MIDDLE
        jz .right
        test al, EVENT_MID_PRESS        ; the wheel pressed: a drag at once (the game has no use
        jz .mheld                       ;   for that button)
        cmp byte [cs:drag], 0
        jne .mheld
        mov byte [cs:drag], 2
        mov byte [cs:drag_mid], 1
        mov byte [cs:drag_new], 1
        mov [cs:drag_x], cx
        mov [cs:drag_y], dx
.mheld: cmp byte [cs:drag_mid], 0
        je .right
        and bx, ~MIDDLE
        test al, EVENT_MID_LEAVE
        jz .mdone
        mov byte [cs:drag], 0
        mov byte [cs:drag_mid], 0
.mdone: and al, ~(EVENT_MID_PRESS | EVENT_MID_LEAVE)
        jmp .pass
.right: test byte [cs:scroll_on], SCROLL_RIGHT
        jz .pass
        test al, EVENT_PRESS
        jz .held
        cmp byte [cs:drag], 0
        jne .held
        mov byte [cs:drag], 1
        mov [cs:drag_x], cx
        mov [cs:drag_y], dx
        and al, ~EVENT_PRESS
.held:  cmp byte [cs:drag], 0
        je .pass
        and bx, ~RIGHT
        cmp byte [cs:drag], 1
        jne .leave
        push ax                         ; moved far enough to be a drag?
        mov ax, cx
        sub ax, [cs:drag_x]
        call .apart
        jnc .y
        mov ax, dx
        sub ax, [cs:drag_y]
        call .apart
        jc .near
.y:     mov byte [cs:drag], 2
        mov byte [cs:drag_new], 1
.near:  pop ax
.leave: test al, EVENT_LEAVE
        jz .pass
        and al, ~EVENT_LEAVE
        cmp byte [cs:drag], 1
        mov byte [cs:drag], 0
        jne .pass                       ; (a drag: the game never knows)
        pusha                           ; a click: pressed and released, where it was pressed
        or bx, RIGHT
        mov cx, [cs:drag_x]
        mov dx, [cs:drag_y]
        mov ax, EVENT_PRESS
        call .give
        popa
        pusha
        mov ax, EVENT_LEAVE
        call .give
        popa
.pass:  call .give
        retf
.give:  and ax, [cs:game_mask]          ; the events the game asked for, to its handler
        jz .none
        pusha
        push ds
        push es
        call far [cs:game_handler]
        pop es
        pop ds
        popa
.none:  ret
.apart: or ax, ax                       ; CF clear when |AX| >= DRAG_START
        jns .pos
        neg ax
.pos:   cmp ax, DRAG_START
        ret

; PROBE_SCROLL: INT VEC_SCROLL replaces the start of "call far 3118:002E" (9Ah 2Eh 00h, then the
; segment: A9h makes it a harmless "test ax,<segment>" the loader may relocate), the game's main
; loop asking where the pointer is (its arguments, far pointers to x and y, on the stack).
probe_scroll:
        pop word [cs:s_resume]
        pop word [cs:s_resume + 2]
        pop word [cs:s_resume_fl]
        add word [cs:s_resume], 3       ; (past the segment)
        push bp
        mov bp, sp
        push es
        push bx
        push cx
        push dx
        push si
        push di
        inc word [cs:main_ticks]
        mov byte [cs:arc_hold], 0       ; (an Arcanist's cast is over: PROBE_END_TURN)
        call dust_tick
        call target_click
        cmp word [cs:view_redraw], 0
        je .panel
        mov word [cs:view_redraw], 0
        call view_again
.panel: call panel_tick
.read:  mov ax, 3
        int 0x33                        ; BX = buttons, CX, DX = where
        cmp word [cs:scroll_on], 0
        je .wheel                       ; (the Loader's scrolling, as for a chosen enemy, anyway)
        cmp byte [cs:drag], 2
        jne .wheel
        cmp byte [cs:drag_new], 0
        je .follow
        mov byte [cs:drag_new], 0
        mov ax, [CAM_X]
        mov [cs:cam0_x], ax
        mov ax, [CAM_Y]
        mov [cs:cam0_y], ax
.follow:
        mov ax, [cs:cam0_x]             ; where the drag puts the view: the map moves with it
        sub ax, cx
        add ax, [cs:drag_x]
        mov si, [cs:cam0_y]
        sub si, dx
        add si, [cs:drag_y]
        call pan_to
.wheel: mov ax, [cs:pan_x]              ; the Loader's
        sub ax, [cs:pan_x_done]
        mov si, [cs:pan_y]
        sub si, [cs:pan_y_done]
        mov di, ax
        or di, si
        jz .report
        add [cs:pan_x_done], ax
        add [cs:pan_y_done], si
        add [cs:cam0_x], ax             ; (a drag under way goes on from there)
        add [cs:cam0_y], si
        add ax, [CAM_X]
        add si, [CAM_Y]
        call pan_to
.report:
        cmp byte [cs:drag], 0
        je .put
        and bx, ~(RIGHT | MIDDLE)
        cmp cx, 1                       ; (off the edges: no scrolling of the game's own)
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
.put:   les di, [bp + 2]
        mov [es:di], cx
        les di, [bp + 6]
        mov [es:di], dx
        mov ax, bx
        pop di
        pop si
        pop dx
        pop cx
        pop bx
        pop es
        pop bp
        push word [cs:s_resume_fl]
        push word [cs:s_resume + 2]
        push word [cs:s_resume]
        iret

pan_to:                                 ; the view's top left to (AX, SI) as far as the map goes;
        cmp ax, 0                       ;   keeps CX, DX
        jge .x1
        xor ax, ax
.x1:    cmp ax, CAM_X_MOST
        jle .y0
        mov ax, CAM_X_MOST
.y0:    cmp si, 0
        jge .y1
        xor si, si
.y1:    cmp si, CAM_Y_MOST
        jle .snap
        mov si, CAM_Y_MOST
.snap:  and ax, 0xFFF8                  ; (as the game keeps it)
        and si, 0xFFF8
        cmp ax, [CAM_X]
        jne .go
        cmp si, [CAM_Y]
        je .done
.go:    call centre_on
.done:  ret

centre_on:                              ; the view's top left to (AX, SI), drawn again; keeps CX, DX
        push cx
        push dx
        push bx
        mov bx, ds
        sub bx, DGROUP_SEG - CENTRE_SEG
        mov [cs:centre + 2], bx
        push 1
        add si, 100
        push si
        add ax, 160
        push ax
        call far [cs:centre]
        add sp, 6
        pop bx
        pop dx
        pop cx
        ret

; DUST (DUST_ON): a figure walking raises puffs of dust behind it, which spread, rise a little and
; fade away in about a second (DUST_LIFE ticks of the BIOS clock). Each is drawn on the floor as the
; shadows are (DUST_PASS: before the walls and figures, which stand in it), lightening the ground's
; colours through LIGHT (made by the Loader from the palette: 0 for colours that aren't ground
; dust shows on, so only sand and dirt take it), dithered thinner toward its edge and as it fades,
; by a pattern fixed to the map (so a puff looks the same however much of it is drawn again).
;
; DUST_TICK, from the main loop (PROBE_SCROLL), notes how far each figure that casts a shadow
; (SHADOW_TAB) has walked, and raises a puff behind its feet every DUST_STEP pixels. While puffs
; change (each tick of the clock), their ground is to be drawn again: the rectangle the game draws
; again round what moved takes them in (DUST_UNION, from PROBE_REDRAW_ALL), and when no one is
; walking, DUST_NUDGE has the game draw the view again. Nothing of the game's is changed (marking a
; figure changed to have it drawn again can set one in a fight walking again).

DUST_LIFE  equ 18               ; ticks of the BIOS clock (18.2 a second) a puff lasts
DUST_STEP  equ 6                ; pixels walked for each puff
JUMP_MOST  equ 40               ; a move further than this (across or up and down) is a jump, not a walk
PUFFS      equ 24               ; puffs at most at once
PUFF_SIZE  equ 12               ; a puff: x, y (on the map), born (ticks), owner (thing), seed, live
BIOS_TICKS equ 0x46C

dust_tick:                      ; DS = the game's
        cmp word [cs:dust_on], 0
        jne .on
        ret
.on:    push es
        push bp
        xor ax, ax
        mov es, ax
        mov ax, [es:BIOS_TICKS]
        mov [cs:d_now], ax
        cmp ax, [cs:d_last]
        je .walk
        mov [cs:d_last], ax
        mov si, puffs                   ; a tick on: each puff looks different, or is gone
        mov cx, PUFFS
.age:   cmp byte [cs:si + 10], 0
        je .anext
        call puff_dirty
        mov ax, [cs:d_now]
        sub ax, [cs:si + 4]
        cmp ax, DUST_LIFE
        jbe .anext
        mov byte [cs:si + 10], 0        ; (drawn once more, gone: now free)
.anext: add si, PUFF_SIZE
        loop .age
.walk:  les di, [OBJ_LIST]
        mov cx, [OBJ_COUNT]
        or cx, cx
        jz .done
.thing: push cx
        mov bx, [es:di + 6]
        cmp bx, MAP_COUNT - 1
        ja .tnext
        cmp byte [cs:shadow_tab + bx], 0
        je .tnext
        mov [cs:t_thing], bx
        mov ax, [es:di]
        mov [cs:t_x], ax
        mov dx, [es:di + 2]
        mov [cs:t_y], dx
        shl bx, 1
        sub ax, [cs:last_x + bx]
        mov [cs:t_dx], ax
        sub dx, [cs:last_y + bx]
        mov [cs:t_dy], dx
        mov ax, [cs:t_x]
        mov [cs:last_x + bx], ax
        mov ax, [cs:t_y]
        mov [cs:last_y + bx], ax
        mov ax, [cs:t_dx]               ; walked a little (not a jump: an area loaded, someone placed)
        call abs16
        cmp ax, JUMP_MOST
        jae .tnext
        mov cx, ax
        mov ax, [cs:t_dy]
        call abs16
        cmp ax, JUMP_MOST
        jae .tnext
        add ax, cx
        jz .tnext
        mov ax, [cs:d_now]
        mov [cs:d_walked_at], ax
        mov bx, [cs:t_thing]
        add [cs:walked + bx], al
        cmp byte [cs:walked + bx], DUST_STEP
        jb .tnext
        sub byte [cs:walked + bx], DUST_STEP
        cmp byte [cs:walked + bx], DUST_STEP
        jb .one
        mov byte [cs:walked + bx], 0        ; (one puff a tick at most)
.one:
        call puff_raise
.tnext: pop cx
        add di, 8
        dec cx
        jnz .thing
.done:  call dust_nudge
        pop bp
        pop es
        ret

abs16:  or ax, ax
        jns .pos
        neg ax
.pos:   ret

sgn16:  or ax, ax                       ; AX -> -1, 0 or 1
        jz .z
        mov ax, 1
        jg .z
        neg ax
.z:     ret

puff_raise:                             ; behind T_THING's feet at (T_X, T_Y), walking (T_DX, T_DY)
        mov ax, [cs:d_next]             ; the next in turn (the oldest, if all are in use)
        inc word [cs:d_next]
        cmp word [cs:d_next], PUFFS
        jb .slot
        mov word [cs:d_next], 0
.slot:  imul si, ax, PUFF_SIZE
        add si, puffs
        cmp byte [cs:si + 10], 0
        je .free
        call puff_dirty                 ; (its ground drawn again without it)
.free:  xor byte [cs:d_side], 1         ; (the feet in turn: a little to one side, then the other)
        mov ax, [cs:t_dx]
        call sgn16
        mov [cs:t_sx], ax
        mov ax, [cs:t_dy]
        call sgn16
        mov [cs:t_sy], ax
        mov ax, [cs:t_sx]               ; x: behind, and to the side across the way it goes
        imul ax, ax, -3
        add ax, [cs:t_x]
        mov dx, [cs:t_sy]
        shl dx, 1
        cmp byte [cs:d_side], 0
        je .x
        neg dx
.x:     add ax, dx
        mov [cs:si], ax
        mov ax, [cs:t_sy]               ; y: behind, and to the side
        imul ax, ax, -2
        add ax, [cs:t_y]
        mov dx, [cs:t_sx]
        cmp byte [cs:d_side], 0
        jne .y
        neg dx
.y:     add ax, dx
        mov [cs:si + 2], ax
        mov ax, [cs:d_now]
        mov [cs:si + 4], ax
        mov ax, [cs:t_thing]
        mov [cs:si + 6], ax
        inc word [cs:dust_puffs]
        imul ax, [cs:dust_puffs], 0x3D7
        mov [cs:si + 8], ax
        mov byte [cs:si + 10], 1
        call puff_dirty
        ret

puff_dirty:                             ; the puff at CS:SI: its ground to be drawn again (DS = the game's)
        mov ax, [cs:si]
        sub ax, 12
        mov dx, [cs:si + 2]
        sub dx, 12
        cmp byte [cs:d_dirty], 0
        je .first
        cmp ax, [cs:d_x0]
        jge .x1
.first: mov [cs:d_x0], ax
.x1:    add ax, 24
        cmp byte [cs:d_dirty], 0
        je .fx1
        cmp ax, [cs:d_x1]
        jle .y0
.fx1:   mov [cs:d_x1], ax
.y0:    cmp byte [cs:d_dirty], 0
        je .fy0
        cmp dx, [cs:d_y0]
        jge .y1
.fy0:   mov [cs:d_y0], dx
.y1:    add dx, 19
        cmp byte [cs:d_dirty], 0
        je .fy1
        cmp dx, [cs:d_y1]
        jle .mark
.fy1:   mov [cs:d_y1], dx
.mark:  mov byte [cs:d_dirty], 1
        mov ax, [cs:si + 6]
        mov [cs:d_owner], ax
        ret

STILL_TICKS equ 3              ; how long no one has walked (nor the view moved) before DUST_NUDGE
NUDGE_TICKS equ 4               ; ... and between its drawings of the view

; DUST_NUDGE: with puffs to draw again while no one walks and the view stands still (when the
; game draws again round what moved anyway, DUST_UNION taking them in), the view drawn again
; (VIEW_AGAIN) every NUDGE_TICKS, till they are gone
dust_nudge:
        mov ax, [CAM_X]                 ; (the view: when it last moved)
        cmp ax, [cs:d_cam_x]
        jne .cam
        mov ax, [CAM_Y]
        cmp ax, [cs:d_cam_y]
        je .still
.cam:   mov ax, [CAM_X]
        mov [cs:d_cam_x], ax
        mov ax, [CAM_Y]
        mov [cs:d_cam_y], ax
        mov ax, [cs:d_now]
        mov [cs:d_walked_at], ax
        ret
.still: cmp byte [cs:d_dirty], 0
        je .ret
        mov ax, [cs:d_now]
        sub ax, [cs:d_walked_at]
        cmp ax, STILL_TICKS
        jb .ret
        mov ax, [cs:d_now]
        sub ax, [cs:d_nudged]
        cmp ax, NUDGE_TICKS
        jb .ret
        mov ax, [cs:d_now]
        mov [cs:d_nudged], ax
        mov byte [cs:d_dirty], 0
        call view_again
.ret:   ret

; VIEW_AGAIN: the view drawn again, all of it, as the game does when the view is centred where it
; is (DS = the game's). The figures are never marked changed to have them drawn again: in a fight
; that can set one walking again.
view_again:
        push ax
        push bx
        push cx
        push dx
        push si
        mov si, [CAM_Y]
        mov ax, [CAM_X]
        call centre_on
        pop si
        pop dx
        pop cx
        pop bx
        pop ax
        ret

; PANEL: the combat log's panel over the map, bottom right. The Loader draws it (combatlog.py:
; its frame and, in time, the log's lines), PANEL_W x PANEL_H palette indices in PANEL_SEG (each
; row its planes in turn), and this puts that picture on screen. The map is drawn straight into the screen on show (no page flip on
; the map), a rectangle at a time, so the picture is put again from the main loop (PANEL_TICK, from
; PROBE_SCROLL) whenever the floor has been drawn since (FLOOR_ENTER marks it) or the Loader has
; a new one (PANEL_NEW), and at the end of each redrawn rectangle (REDRAW_POST), into the page on
; show (0980:118E: A400h when 1, else A000h). PANEL_ON is the Loader's: set, the panel is shown;
; cleared, or the Loader silent for STATS_FRESH (its STATS_STAMP), the view is drawn again
; without it. The game's windows over the map (a figure's menu, a question) are shown on the other
; screen, the view drawn there again without the panel: it is back when they close.
PANEL_X0   equ 136              ; (x0 and the width a multiple of 4: whole bytes of the planes)
PANEL_Y0   equ 120
PANEL_W    equ 180
PANEL_H    equ 78                ; (as it starts: the Loader's PANEL_TOP and PANEL_ROWS)
PANEL_H_MOST equ 130
PANEL_BYTES equ PANEL_W * PANEL_H_MOST
SHOWN_PAGE equ 0x118E           ; (in the page routines' segment, PAGES_SEG) 1: A400h shown
panel_shown db 0
panel_dirty db 0
panel_pseg  dw 0                ; the page routines' segment, and the page on show when the panel
panel_page  dw 0                ;   was last drawn (PANEL_DRAW), and its top then
panel_drawn dw PANEL_Y0

panel_tick:
        push es                         ; (the map's main loop ran: L_ON_MAP)
        xor ax, ax
        mov es, ax
        mov ax, [es:0x46C]
        pop es
        mov [cs:map_tick], ax
        cmp word [cs:panel_on], 0
        je .off
        push es                         ; (the Loader gone: off, as if it had said so)
        xor ax, ax
        mov es, ax
        mov ax, [es:0x46C]
        pop es
        sub ax, [cs:stats_stamp]
        cmp ax, STATS_FRESH
        jb .on
.off:   cmp byte [cs:strip_on], 0       ; (the strip: kept empty, in the palette of the moment)
        je .off2
        dec word [cs:strip_wait]
        jnz .off2
        mov word [cs:strip_wait], STRIP_EVERY
        call strip_clear
.off2:  cmp byte [cs:panel_shown], 0
        je .ret
        mov byte [cs:panel_shown], 0
        cmp byte [cs:strip_on], 0
        jne .unstrip
        call view_again                 ; (the view under it drawn again)
.ret:   ret
.unstrip:
        call strip_clear                ; (the strip: emptied)
        ret
.on:    cmp byte [cs:strip_on], 0
        jne .strip
        mov ax, [CAM_X]                 ; the view moved by the game's own scrolling (at the edge,
        xchg ax, [cs:panel_cx]          ;   following who walks): that copies the screen as it is,
        cmp ax, [cs:panel_cx]           ;   the panel too, and draws only what comes into view, so
        mov ax, [CAM_Y]                 ;   copies of the panel stayed on the map. The view drawn
        xchg ax, [cs:panel_cy]          ;   again whole, round the panel, then the panel
        jne .cam
        cmp ax, [cs:panel_cy]
        je .still
.cam:   cmp byte [cs:panel_shown], 0
        je .still
        call view_again
        jmp .draw
.still: cmp word [cs:panel_new], 0
        je .old
        mov word [cs:panel_new], 0
        cmp byte [cs:panel_shown], 0
        je .draw
        mov ax, [cs:panel_top]          ; smaller than it was: the view drawn again under it first
        cmp ax, [cs:panel_drawn]
        jbe .draw
        call view_again
        jmp .draw
.old:   cmp byte [cs:panel_shown], 0
        je .draw
        cmp byte [cs:panel_dirty], 0
        jne .draw
        mov ax, [cs:map_tick]           ; put again at most once a BIOS tick (PANEL_TICKS: a pass
        sub ax, [cs:panel_at]           ;   at a time it was most of what the game's CPU did)
        cmp ax, PANEL_TICKS
        jb .ret
        mov ax, [cs:panel_mx]           ; the pointer moved: the game may have drawn the view
        cmp ax, [cs:panel_lx]           ;   under it again in ways not hooked (in a fight, what
        jne .draw                       ;   the pointer is over, later in the pass too): put
        mov ax, [cs:panel_my]           ;   again, the pointer over it
        cmp ax, [cs:panel_ly]
        jne .draw
        mov ax, [cs:map_tick]           ; and anyway (round the pointer: PANEL_DRAW_AROUND, the
        mov [cs:panel_at], ax           ;   panel itself unchanged)
        call panel_draw_around
        ret
.draw:  mov ax, [cs:map_tick]
        mov [cs:panel_at], ax
        mov byte [cs:panel_dirty], 0
        mov byte [cs:panel_shown], 1
        mov ax, [cs:panel_mx]
        mov [cs:panel_lx], ax
        mov ax, [cs:panel_my]
        mov [cs:panel_ly], ax
        call panel_draw_pointer
        ret
.strip: cmp word [cs:panel_new], 0      ; the strip below the map: put when new, and now and
        jne .sput                       ;   then (nothing of the game's goes there; the game's
        cmp byte [cs:panel_shown], 0    ;   mode setting clears it)
        je .sput
        mov ax, [cs:map_tick]
        sub ax, [cs:panel_at]
        cmp ax, STRIP_TICKS
        jb .ret
.sput:  mov word [cs:panel_new], 0
        mov ax, [cs:map_tick]
        mov [cs:panel_at], ax
        mov byte [cs:panel_shown], 1
        mov byte [cs:strip_mode], 0
        call strip_sum                  ; (the colours it is in: STRIP_SAME)
        mov [cs:strip_shown_sum], ax
        call panel_draw
        ret
PANEL_TICKS equ 1               ; (BIOS ticks, 18.2 a second, between puts with nothing new)
STRIP_TICKS equ 9
panel_at   dw 0                 ; (the BIOS tick of the last put: PANEL_TICK)
STRIP_EVERY equ 512             ; (passes between the strip's emptying again, the log off)
strip_wait dw 1
panel_lx   dw 0
panel_ly   dw 0
panel_cx   dw 0                 ; (the view's top left at the last pass: PANEL_TICK)
panel_cy   dw 0

; PANEL_LIVE: ZF set if the panel is on screen: shown, the page on show the one it was last drawn
; into (not while the game shows the other screen: a window over the map, the panel not on it), and
; the game on the map (SCREEN_IS 1: not a full screen, USE or the inventory, drawn on that page over
; the map, which would else be drawn round the panel and its clicks kept from it)
panel_live:
        cmp byte [cs:strip_on], 0       ; (in the strip: never over the map)
        jne .no
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
        call strip_on_map
.ret:   ret
.no:    cmp sp, 0                       ; (ZF clear)
        ret

; PANEL_MOUSE: in MOUSE_EVENT (AX the events, BX the buttons held, CX, DX where): the pointer
; noted for the Loader; a left press on the panel, while it is shown, counted and kept from the
; game with its release (the Loader scrolls the log: combatlog.py)
panel_mouse:
        mov [cs:panel_mx], cx
        mov [cs:panel_my], dx
        cmp word [cs:panel_held], 0
        jne .held
        cmp byte [cs:panel_shown], 0
        je .ret
        test al, EVENT_LEFT_PRESS
        jz .ret
        call panel_live
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
        and bx, ~LEFT
.ret:   ret

; PANEL_DRAW: the picture into the page on show, a plane at a time (registers kept)
panel_draw:
        cmp word [cs:panel_seg], 0
        je .none
        cmp byte [cs:strip_on], 0
        jne strip_draw
        pusha
        push ds
        push es
        cld
        mov ax, ds
        sub ax, DGROUP_SEG
        add ax, PAGES_SEG
        mov es, ax
        mov [cs:panel_pseg], ax         ; (where the page on show is said, and which it was:
        mov ax, [es:SHOWN_PAGE]         ;   PANEL_LIVE)
        mov [cs:panel_page], ax
        mov ax, [cs:panel_top]          ; (and where its top was: PANEL_TICK)
        mov [cs:panel_drawn], ax
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
        xchg bl, [cs:pb_skip]           ;   (whole: no pointer is left there)
        push bx
        call panel_blit
        pop bx
        mov [cs:pb_skip], bl
.done:  pop es
        pop ds
        popa
.none:  ret

; PANEL_STAGING: in PANEL_DRAW (DS the game's, ES the page routines' segment): the picture also
; into the screen the game moves its pointer on, when it does so (28D1:0B7F, 28D1:1360: set
; [3C4Ah] and windows [3CD0h], shown, and [3CD2h] apart). There the pointer is drawn, the box round
; its old and new places copied from that screen to the one on show, and it is taken off again,
; so without the picture there the map came back over the panel wherever the pointer went (and
; stayed under a still one: PANEL_DRAW_AROUND leaves its box). Drawn whole: no pointer is left
; there. STAGE_SEG: that screen's segment, or 0; AX, BX not kept.
PTR_STAGING  equ 0x3C4A         ; (the game's DS) set: the pointer moved on another screen
PTR_SHOWN_W  equ 0x3CD0         ;   the window shown, and the one it is moved on
PTR_STAGE_W  equ 0x3CD2
WIN_SEGS     equ 4              ; (the page routines' segment) each window's segment, a word each
panel_staging:
        mov word [cs:stage_seg], 0
        cmp word [PTR_STAGING], 0
        je .ret
        mov bx, [PTR_STAGE_W]
        cmp bx, [PTR_SHOWN_W]
        je .ret
        cmp bx, 1                       ; (the two screens' windows: 0 and 1)
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

; PANEL_DRAW_POINTER: PANEL_DRAW, then the game's pointer drawn again over it (28D1:093D, as the
; game draws it). Not taken off first: what the game keeps under its pointer, to put back when it
; moves, is the map without the panel (taken off, it showed as a patch of map until put again).
; DS the game's; registers kept.
POINTER_SEG  equ 0x28D1         ; (DSUN.EXE 2E8E0h: the pointer's routines' segment)
POINTER_ON   equ 0x093D         ; put it on (what is under it kept first)
panel_draw_pointer:
        pusha
        push es
        mov ax, ds
        sub ax, DGROUP_SEG - POINTER_SEG
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

; PANEL_DRAW_AROUND: PANEL_DRAW with the box the pointer was last drawn in left as it is, the
; pointer kept on screen (PANEL_TICK's put now and then, the panel unchanged); if the game shows
; no pointer, PANEL_DRAW. DS the game's; registers kept.
POINTER_HIDE equ 0x3C46         ; (set: the game draws no pointer)
POINTER_XY   equ 0xA137         ; where it is to be drawn, top left (x, y)
POINTER_WAS  equ 0xA13F         ; where it was last drawn (x, y)
POINTER_KIND equ 0xA17F         ; and its kind then (-1: none)
POINTER_MOST equ 32             ; (the widest and tallest a pointer may be)
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

; PROBE_POINTER: INT VEC_POINTER replaces "cmp [9Ch],sp" (4 bytes: INT + 2 NOPs; the stack check)
; in the game's routine that draws its pointer (28D1:093D). The panel is put first if the pointer
; is to go over it: the game takes its pointer off by putting back the map that was under it, over
; the panel. The stack check, with the routine's SP; RETF 2 keeps its flags. DS the game's.
probe_pointer:
        sti                     ; (RETF 2 keeps these flags: interrupts on, as the game had them)
        mov [cs:strip_ds], ds
        call strip_mind
        call pointer_panel
        push ax
        mov ax, sp
        add ax, 8               ; (the routine's SP: past this push and INT's IP, CS and flags)
        cmp [0x9C], ax
        pop ax
        retf 2

; POINTER_PANEL: the panel put (PANEL_DRAW) if it is on screen and the pointer about to be drawn
; over it, or last drawn over it; registers kept
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
        cmp ax, ax                      ; (ZF set)
        pop ax
        ret
.no:    cmp sp, 0                       ; (ZF clear)
        pop ax
        ret

; PANEL_DRAW_OTHER: the picture into the screen not on show (a redraw about to flip to it: the
; game's map on both); registers kept
panel_draw_other:
        cmp word [cs:panel_seg], 0
        je .none
        pusha
        push ds
        push es
        cld
        mov ax, ds
        sub ax, DGROUP_SEG
        add ax, PAGES_SEG
        mov es, ax
        mov ax, 0xA400
        cmp word [es:SHOWN_PAGE], 0
        je .seg
        mov ax, 0xA000
.seg:   call panel_blit
        pop es
        pop ds
        popa
.none:  ret

; PANEL_BLIT: the picture into the screen at segment AX, a plane at a time (AX to DI, DS, ES not
; kept). Its top and height read once, the height kept within the screen (never past row 199).
panel_blit:
        mov es, ax
        mov word [cs:pb_x4], PANEL_X0 / 4 ; (the panel over the map; STRIP_BLIT sets the strip's)
        mov word [cs:pb_w4], PANEL_W / 4
        mov word [cs:pb_end], 200
pb_go:  mov ax, [cs:panel_top]
        cmp ax, [cs:pb_end]
        jae .ret
        mov [cs:pb_top], ax
        mov cx, [cs:pb_end]
        sub cx, ax
        mov ax, [cs:panel_rows]
        cmp ax, cx
        jbe .rows
        mov ax, cx
.rows:  or ax, ax
        jz .ret
        mov [cs:pb_rows], ax
        mov ax, [cs:pb_sx0]             ; (the pointer's box, in bytes of the panel's rows: those
        sub ax, [cs:pb_x4]              ;   left of it, and its own)
        call pb_clamp
        mov [cs:pb_left], ax
        mov ax, [cs:pb_sx1]
        sub ax, [cs:pb_x4]
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
        mov ax, [cs:pb_top]             ; the screen's byte for the picture's first row ...
        sub ax, [cs:pb_row0]
        mov dx, 80
        mul dx
        add ax, [cs:pb_x4]
        mov di, ax
        mov ax, [cs:pb_w4]              ; ... and this plane's bytes of it (each of the picture's
        mul bx                          ;   rows its four planes' bytes in turn: combatlog.py
        mov si, ax                      ;   PLANAR), copied whole
        mov dx, [cs:pb_rows]
        mov bp, [cs:pb_top]             ; (BP: the row on screen)
.row:   mov cx, [cs:pb_w4]
        cmp byte [cs:pb_skip], 0
        je .pix
        cmp bp, [cs:pb_sy0]
        jl .pix
        cmp bp, [cs:pb_sy1]
        jge .pix
        mov cx, [cs:pb_left]            ; the pointer's row: the bytes left of its box, its box
        rep movsb                       ;   left as it is, then the bytes right of it
        mov cx, [cs:pb_mid]
        add di, cx
        add si, cx
        mov cx, [cs:pb_w4]
        sub cx, [cs:pb_left]
        sub cx, [cs:pb_mid]
.pix:   shr cx, 1
        rep movsw
        adc cx, cx
        rep movsb
        add di, 80
        sub di, [cs:pb_w4]
        mov ax, [cs:pb_w4]              ; (past the other planes' bytes of the row)
        add si, ax
        add si, ax
        add si, ax
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
pb_x4   dw PANEL_X0 / 4         ; where the picture goes, its width (bytes of a plane's row), and
pb_w4   dw PANEL_W / 4          ;   the screen's rows (the panel: 200; the strip: 240)
pb_end  dw 200
pb_row0 dw 0                    ; (the screen row at the memory's first: the strip's 200)
pb_skip db 0                    ; set: the box PB_SX0 to PB_SX1 (bytes of a row, the last not in
pb_sx0  dw 0                    ;   it), PB_SY0 to PB_SY1 (rows, the last not in it) left as it is
pb_sx1  dw 0
pb_sy0  dw 0
pb_sy1  dw 0
pb_left dw 0
pb_mid  dw 0

; PB_CLAMP: AX kept within 0 to PB_W4
pb_clamp:
        cmp ax, 0
        jge .lo
        xor ax, ax
.lo:    cmp ax, [cs:pb_w4]
        jle .hi
        mov ax, [cs:pb_w4]
.hi:    ret

; STRIP: with the Options tab's "combat log below the map" the game's screen is 320 x 222 (its
; mode X set up as ever, then 22 rows more in the same timing: PROBE_STRIP), and the game, which
; knows nothing of it, draws its 200 rows as before. Below row 200 the VGA's split screen (its line
; compare) shows video memory from its start whichever screen is up: the strip, 22 rows of 80 bytes
; a plane (1760), the game's two screens moved up past it (A070h, A460h: each at a multiple of 256
; bytes, as the game's page flip sets only the high byte of where the screen starts; gamepatch's
; STRIP). The strip is the
; combat log's: the Loader's picture, STRIP_W x STRIP_H, put there (STRIP_DRAW); the panel's top
; and height are the Loader's as ever (200, 40). The pointer never goes there.
STRIP_W   equ 320
STRIP_ROWS equ 222
strip_on  db 0                  ; set once the game's screen is 320 x 222

; PROBE_STRIP: INT VEC_STRIP replaces "mov al,2 / mov ah,1 / out dx,ax" (5 bytes: INT + 3 NOPs) at
; the end of the game's mode X set up (0980:2A40h, DSUN.EXE 11640h; DX 3C4h): that, then the
; screen 222 rows in the game's own timing (70 a second, 449 scan lines a frame, each row drawn
; twice: the speed and shape as ever): the picture to scan line 443 (12h: 1BBh), the blanking from
; 444 (15h, to 16h: 3Fh, the frame's end) and the sync at 445 to 447 (10h, 11h, keeping registers
; 0-7 locked), and the split after scan line 399 (the line compare, 18h: 18Fh; its bit 9, in 09h,
; cleared). Their bit 8s are in the overflow (07h, 1Fh: set) as the game has it. Keeps all.
probe_strip:
        push ax
        push dx
        push si
        push cx
        mov dx, 0x3D4
        mov si, strip_crtc
        mov cx, STRIP_CRTC_N
.crtc:  mov ax, [cs:si]
        out dx, ax
        add si, 2
        loop .crtc
        pop cx
        pop si
        mov byte [cs:strip_on], 1
        mov dx, 0x3C4
        mov ax, 0x0102                  ; (as the game: all planes off but the first)
        out dx, ax
        pop dx
        pop ax
        iret
strip_crtc dw 0x0109, 0xBB12, 0xBC15, 0x3F16, 0xBD10, 0x8F11, 0x8F18
STRIP_CRTC_N equ ($ - strip_crtc) / 2

; PROBE_PALETTE: INT VEC_PALETTE replaces "sti / pop di" (2 bytes) at the end of the game's
; routine that sets the whole palette (0980:58F5h, DSUN.EXE 144F5h: a new screen or area): those,
; then STRIP_NEW_PALETTE. Keeps all.
probe_palette:
        push bp
        mov bp, sp
        mov di, [bp + 8]                ; (pop di: the word under INT's IP, CS and flags)
        push word [bp + 6]              ; (the frame moved up over it, interrupts on: sti)
        push word [bp + 4]
        push word [bp + 2]
        pop word [bp + 4]
        pop word [bp + 6]
        pop word [bp + 8]
        or word [bp + 8], 0x200
        pop bp
        add sp, 2
        call strip_new_palette
        iret

; PROBE_COLOURS: INT VEC_COLOURS replaces "pop dx / pop cx" (2 bytes) at the end of the game's
; routine that sets a run of colours (DSUN.EXE 288BAh: BX the first, CX how many; the title's,
; and each step of a fade): those, then as PROBE_PALETTE if the run reaches below the colours
; the game animates (DARK_LAST). Keeps all but DX and CX, as the routine leaves them.
probe_colours:
        push bp
        mov bp, sp
        cmp bx, DARK_LAST
        mov dx, [bp + 8]                ; (pop dx / pop cx: the words under INT's IP, CS, flags)
        mov cx, [bp + 10]
        push word [bp + 6]              ; (the frame moved up over them; the flags as they were)
        push word [bp + 4]
        push word [bp + 2]
        pop word [bp + 6]
        pop word [bp + 8]
        pop word [bp + 10]
        pop bp
        lea sp, [esp + 4]               ; (keeps the flags: the CMP's above)
        ja .ret
        call strip_new_palette
.ret:   iret

; STRIP_NEW_PALETTE: the strip in the new palette: emptied (STRIP_CLEAR) unless the log's picture
; is in it and the colours it was put in are still those on screen (STRIP_SAME: a window over the
; map); else it is put again when the map's main loop runs again;
; registers kept
strip_new_palette:
        cmp byte [cs:strip_on], 0
        je .ret
        cmp byte [cs:panel_shown], 0
        je .clear
        call strip_same
        je .ret
        mov byte [cs:panel_shown], 0
.clear: call strip_clear
.ret:   ret

; STRIP_SUM: AX a sum of the VGA's colours DARK_FIRST to DARK_LAST (STRIP_SAME's); BX, CX, DX not kept
strip_sum:
        mov dx, 0x3C7
        mov al, DARK_FIRST
        out dx, al
        mov dx, 0x3C9
        mov cx, (DARK_LAST - DARK_FIRST + 1) * 3
        xor bx, bx
        xor ah, ah
.next:  in al, dx
        rol bx, 1
        add bx, ax
        loop .next
        mov ax, bx
        ret

; STRIP_SAME: ZF set if the VGA's colours are still those the log's picture was put in (STRIP_SUM as
; the main loop last put it: STRIP_SHOWN_SUM); registers kept
strip_same:
        pusha
        call strip_sum
        cmp ax, [cs:strip_shown_sum]
        popa
        ret
strip_shown_sum dw 0

; STRIP_MIND: from the game's pointer (on every screen; DS the game's): on the map, or with the
; log's picture still in the strip (a talk over the map), a new picture of the log put at once (the map's main loop doesn't run while the game plays a scene out, the
; arena's opening show); else the empty strip filled again when the screen calls for another look
; (STRIP_WANT), in the colours STRIP_COLOURS found last (no palette read here: the pointer may be
; drawn while the game sets colours); registers kept
strip_mind:
        cmp byte [cs:strip_on], 0
        je .ret
        push ax
        cmp word [cs:panel_new], 0
        je .empty
        cmp word [cs:panel_on], 0
        je .empty
        cmp byte [cs:panel_shown], 0    ; (the log's picture still there: its colours too, a
        jne .put                        ;   talk over the map)
        call strip_on_map
        jne .empty
.put:   mov word [cs:panel_new], 0
        mov byte [cs:panel_shown], 1
        mov byte [cs:strip_mode], 0
        call panel_draw
        jmp .out
.empty: cmp byte [cs:panel_shown], 0
        jne .out
        call strip_want
        cmp al, [cs:strip_mode]
        je .out
        mov [cs:strip_mode], al
        call strip_fill
.out:   pop ax
.ret:   ret

; SCREEN_IS: the game's DS:0BC9h, 1 on the map, 2 with a character's screen or a talk over it,
; 0 on the title, the menus and in character creation
SCREEN_IS  equ 0x0BC9

; STRIP_ON_MAP: ZF set if the game is on the map (SCREEN_IS 1); registers kept
strip_on_map:
        push es
        push ax
        mov ax, [cs:strip_ds]
        cmp ax, 1                       ; (not known yet: ZF clear)
        jb .out
        mov es, ax
        cmp word [es:SCREEN_IS], 1
.out:   pop ax
        pop es
        ret

; STRIP_WANT: AL the look of the empty strip: STRIP_STONE (the panel's blue-grey) in a game (the
; map, or a character's screen over it), else STRIP_BLACK (the title, the menus, character creation)
STRIP_BLACK equ 1
STRIP_STONE equ 2
strip_want:
        push es
        mov al, STRIP_BLACK
        cmp word [cs:strip_ds], 0
        je .out
        mov es, [cs:strip_ds]
        cmp word [es:SCREEN_IS], 0
        je .out
        mov al, STRIP_STONE
.out:   pop es
        ret

strip_ds    dw 0                ; the game's DS (PROBE_POINTER's)
strip_mode  db 0                ; the strip now: 0 the log's picture (or not yet filled), else STRIP_WANT's

; STRIP_DRAW: the picture into the strip (PANEL_DRAW, in the strip: PANEL_BLIT at the strip's
; place and width, video memory's first rows showing screen rows 200 on; registers kept)
strip_draw:
        pusha
        push ds
        push es
        cld
        mov ax, 0xA000
        mov es, ax
        mov word [cs:pb_x4], 0
        mov word [cs:pb_w4], STRIP_W / 4
        mov word [cs:pb_end], STRIP_ROWS
        mov word [cs:pb_row0], 200
        mov byte [cs:pb_skip], 0
        call pb_go
        mov word [cs:pb_x4], PANEL_X0 / 4
        mov word [cs:pb_w4], PANEL_W / 4
        mov word [cs:pb_end], 200
        mov word [cs:pb_row0], 0
        pop es
        pop ds
        popa
        ret

; STRIP_COLOURS: from the VGA's palette (from the main loop or after the game has set colours), the
; empty strip's colours: STRIP_DARKEST the darkest of all 256 (the title's black is among the
; last), STRIP_EDGE and STRIP_DEEP the colours nearest the panel's outline and its well (combatlog.py
; COLOURS: palette.SHADOW #202038, palette.DEEP #30304D) among those the game doesn't animate
; (AX, BX, CX, DX, SI not kept)
strip_colours:
        mov dx, 0x3C7
        xor al, al
        out dx, al
        mov dx, 0x3C9
        xor bx, bx
        mov word [cs:sc_dark], 0xFFFF
        mov word [cs:sc_edge], 0xFFFF
        mov word [cs:sc_deep], 0xFFFF
.next:  in al, dx
        mov [cs:sc_rgb], al
        in al, dx
        mov [cs:sc_rgb + 1], al
        in al, dx
        mov [cs:sc_rgb + 2], al
        xor ah, ah                      ; the darkest: the least red, green and blue (a byte)
        mov al, [cs:sc_rgb]
        add al, [cs:sc_rgb + 1]
        add al, [cs:sc_rgb + 2]
        cmp ax, [cs:sc_dark]
        jae .lit
        mov [cs:sc_dark], ax
        mov [cs:strip_darkest], bl
.lit:   cmp bx, DARK_FIRST
        jb .skip
        cmp bx, DARK_LAST
        ja .skip
        mov si, sc_deep_rgb
        call sc_distance
        cmp ax, [cs:sc_deep]
        jae .edge
        mov [cs:sc_deep], ax
        mov [cs:strip_deep], bl
.edge:  mov si, sc_edge_rgb
        call sc_distance
        cmp ax, [cs:sc_edge]
        jae .skip
        mov [cs:sc_edge], ax
        mov [cs:strip_edge], bl
.skip:  inc bx
        cmp bx, 255
        jbe .next
        ret

; SC_DISTANCE: AX the square of the distance between SC_RGB and the colour at CS:SI (0-63 a
; channel); registers but AX kept
sc_distance:
        push cx
        push si
        push di
        push bx
        xor di, di
        mov bx, sc_rgb
        mov cx, 3
.ch:    mov al, [cs:bx]
        sub al, [cs:si]
        cbw
        imul ax, ax
        add di, ax
        inc bx
        inc si
        loop .ch
        mov ax, di
        pop bx
        pop di
        pop si
        pop cx
        ret

sc_rgb      db 0, 0, 0
sc_deep_rgb db 0x30 / 4, 0x30 / 4, 0x4D / 4     ; (palette.DEEP)
sc_edge_rgb db 0x20 / 4, 0x20 / 4, 0x38 / 4     ; (palette.SHADOW)
sc_dark     dw 0
sc_deep     dw 0
sc_edge     dw 0
strip_darkest db 0
strip_deep  db 0
strip_edge  db 0

; STRIP_FILL: the strip emptied as STRIP_MODE has it: all STRIP_DARKEST (STRIP_BLACK), or the
; panel's look without its lines (STRIP_STONE: its top line STRIP_EDGE, the rest STRIP_DEEP);
; registers kept
strip_fill:
        pusha
        push es
        call vga_save
        mov dx, 0x3C4
        mov ax, 0x0F02                  ; (all four planes)
        out dx, ax
        cld
        mov bx, 0xA000
        mov es, bx
        xor di, di
        mov al, [cs:strip_darkest]
        mov ah, al
        mov cx, (STRIP_ROWS - 200) * 80 / 2
        cmp byte [cs:strip_mode], STRIP_STONE
        jne .fill
        mov al, [cs:strip_edge]
        mov ah, al
        mov cx, 80 / 2
        rep stosw
        mov al, [cs:strip_deep]
        mov ah, al
        mov cx, (STRIP_ROWS - 201) * 80 / 2
.fill:  rep stosw
        call vga_restore
        pop es
        popa
        ret

; STRIP_CLEAR: the strip emptied (the log not in it), in the palette of the moment (STRIP_COLOURS),
; as the screen calls for (STRIP_WANT); registers kept
strip_clear:
        pusha
        call strip_colours
        call strip_want
        mov [cs:strip_mode], al
        call strip_fill
        popa
        ret

; DUST_UNION: in PROBE_REDRAW_ALL (x0 [BP-8], x1 [BP-0Ah], y0 [BP-0Ch], y1 [BP-0Eh]: on screen),
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
        cmp ax, [bp-8]
        jge .cx
        mov [bp-8], ax
.cx:    cmp cx, 0x13F
        jle .cx3
        mov cx, 0x13F
.cx3:   or cx, 3
        cmp cx, [bp-0x0A]
        jle .dx
        mov [bp-0x0A], cx
.dx:    cmp dx, 0
        jge .dx0
        xor dx, dx
.dx0:   cmp dx, [bp-0x0C]
        jge .bx
        mov [bp-0x0C], dx
.bx:    cmp bx, 0xC7
        jle .bx1
        mov bx, 0xC7
.bx1:   cmp bx, [bp-0x0E]
        jle .ret
        mov [bp-0x0E], bx
.ret:   ret

; DUST_PASS: in SHADOW_PASS (the VGA's registers kept; the clip, camera and page known), each puff
dust_pass:
        cmp word [cs:dust_on], 0
        je .ret
        push ds
        xor ax, ax
        mov ds, ax
        mov ax, [BIOS_TICKS]
        pop ds
        mov [cs:d_now], ax
        mov si, puffs
        mov cx, PUFFS
.puff:  cmp byte [cs:si + 10], 0
        je .next
        push cx
        push si
        call puff_draw
        pop si
        pop cx
.next:  add si, PUFF_SIZE
        loop .puff
.ret:   ret

puff_draw:                              ; the puff at CS:SI
        mov ax, [cs:d_now]
        sub ax, [cs:si + 4]
        cmp ax, DUST_LIFE
        jb .young
        ret
.young: mov bx, ax                      ; BX: its age
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
        mov al, [cs:dust_dens + bx]
        xor ah, ah
        mov [cs:d_dens], ax
        mov al, [cs:dust_core + bx]
        mov [cs:d_core], ax
        imul ax, bx, 5                  ; rising, 5 pixels in all
        xor dx, dx
        div cx
        mov dx, [cs:si + 2]
        sub dx, ax
        mov [cs:d_wy], dx
        mov ax, [cs:si]
        mov [cs:d_wx], ax
        mov ax, [cs:si + 8]
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
        mov cx, [cs:d_rx]               ; how far out it is across, (x / rx)^2 of 256, by |x|
        imul cx, cx
        xor si, si
.tab:   mov ax, si
        imul ax, ax
        shl ax, 8
        xor dx, dx
        div cx
        mov bx, si
        shl bx, 1
        mov [cs:d_extab + bx], ax
        inc si
        cmp si, [cs:d_rx]
        jbe .tab
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
        mov [cs:row_at], ax
        mov ax, [cs:d_yy]               ; how far out it is, up and down: (y / ry)^2, of 256
        imul ax, ax
        shl ax, 8
        mov cx, [cs:d_ry]
        imul cx, cx
        xor dx, dx
        div cx
        mov [cs:d_ey], ax
        mov word [cs:d_xmax], -1        ; (the widest |x| inside, on this row)
        xor si, si                      ; for each |x| on this row: how thick (0: outside), and
.thr:   mov bx, si                      ;   whether in the core
        shl bx, 1
        mov ax, [cs:d_extab + bx]       ; and across
        add ax, [cs:d_ey]
        mov bx, si
        shl bx, 1
        mov word [cs:d_thrcore + bx], 0
        cmp ax, 256
        ja .nthr
        mov [cs:d_xmax], si
        cmp ax, [cs:d_core]
        setb byte [cs:d_thrcore + bx + 1]
        imul ax, ax, 154                ; thinner toward the edge
        shr ax, 8
        neg ax
        add ax, 256
        mul word [cs:d_dens]
        shr ax, 8
        mov [cs:d_thrcore + bx], al
.nthr:  inc si
        cmp si, [cs:d_rx]
        jbe .thr
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
        add bp, [cs:row_at]
.px:    mov bx, si
        or bx, bx
        jns .abs
        neg bx
.abs:   shl bx, 1
        mov cx, [cs:d_thrcore + bx]     ; CL: how thick, CH: whether in the core
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
        mov al, [cs:light + bx]
        or al, al
        jz .npx
        or ch, ch
        jz .put
        mov bl, al
        mov ah, [cs:light + bx]
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
d_xx       dw 0
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
t_thing    dw 0
t_x        dw 0
t_y        dw 0
t_dx       dw 0
t_dy       dw 0
t_sx       dw 0
t_sy       dw 0
puffs      times PUFFS * PUFF_SIZE db 0
last_x     times MAP_COUNT dw 0
last_y     times MAP_COUNT dw 0
walked     times MAP_COUNT db 0
light      times 256 db 0

; RINGS (RINGS_ON): a ring on the ground under each thing RING_TAB marks (the Loader marks the
; enemies in a fight, and the one chosen with Tab), drawn in the floor pass as the shadows are, so
; the figures stand in it, the ground's colours reddened through RED (made by the Loader from the
; palette): two pixels thick, the chosen one's three, and redder.
ring_pass:
        cmp word [cs:rings_on], 0
        je .ret
        mov ds, [cs:game_ds]
        les di, [OBJ_LIST]
        mov cx, [OBJ_COUNT]
        or cx, cx
        jz .ret
.thing: push cx
        push di
        push es
        mov bx, [es:di + 6]
        cmp bx, MAP_COUNT - 1
        ja .next
        mov al, [cs:ring_tab + bx]
        or al, al
        jz .next
        mov [cs:r_kind], al
        mov ax, [es:di]
        sub ax, [cs:cam_x]
        mov [cs:r_fx], ax
        mov ax, [es:di + 2]
        sub ax, [cs:cam_y]
        mov [cs:r_fy], ax
        mov si, ring_outer
        mov cx, RING_OUTER
        call ring_points
        mov si, ring_inner
        mov cx, RING_INNER
        call ring_points
        cmp byte [cs:r_kind], 2
        jne .next
        mov si, ring_extra
        mov cx, RING_EXTRA
        call ring_points
.next:  pop es
        pop di
        pop cx
        add di, 8
        loop .thing
.ret:   ret

ring_points:                            ; CX points (dx, dy bytes) at CS:SI, round (R_FX, R_FY)
.pt:    push cx
        mov al, [cs:si]
        cbw
        add ax, [cs:r_fx]
        mov bx, ax
        mov al, [cs:si + 1]
        cbw
        add ax, [cs:r_fy]
        add si, 2
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
        mov [cs:row_at], ax
        push si
        call ring_px
        pop si
.skip:  pop cx
        loop .pt
        ret

ring_px:                                ; redden screen x BX on the row at ROW_AT (twice for the chosen)
        mov cx, bx
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
        add bx, [cs:row_at]
        mov es, [cs:v_seg]
        xor ax, ax
        mov al, [es:bx]
        mov cl, [cs:r_kind]
        inc cl                          ; (reddened twice, the chosen one three times)
.again: mov di, ax
        mov ah, [cs:red + di]
        or ah, ah
        jz .put
        mov al, ah
        xor ah, ah
        dec cl
        jnz .again
.put:   mov [es:bx], al
        ret

RING_OUTER equ 76
RING_INNER equ 68
RING_EXTRA equ 84
ring_outer db 13, 0, 13, 1, 13, 2, 12, 2, 12, 3, 11, 3, 11, 4, 10, 4, 9, 4, 9, 5, 8, 5, 7, 5, 6, 5, 5, 5, 5, 6, 4, 6, 3, 6, 2, 6, 1, 6, 0, 6, 255, 6, 254, 6, 253, 6, 252, 6, 251, 6, 251, 5, 250, 5, 249, 5, 248, 5, 247, 5, 247, 4, 246, 4, 245, 4, 245, 3, 244, 3, 244, 2, 243, 2, 243, 1, 243, 0, 243, 255, 243, 254, 244, 254, 244, 253, 245, 253, 245, 252, 246, 252, 247, 252, 247, 251, 248, 251, 249, 251, 250, 251, 251, 251, 251, 250, 252, 250, 253, 250, 254, 250, 255, 250, 0, 250, 1, 250, 2, 250, 3, 250, 4, 250, 5, 250, 5, 251, 6, 251, 7, 251, 8, 251, 9, 251, 9, 252, 10, 252, 11, 252, 11, 253, 12, 253, 12, 254, 13, 254, 13, 255
ring_inner db 12, 0, 12, 1, 11, 1, 11, 2, 10, 2, 10, 3, 9, 3, 9, 4, 8, 4, 7, 4, 6, 4, 5, 4, 5, 5, 4, 5, 3, 5, 2, 5, 1, 5, 0, 5, 255, 5, 254, 5, 253, 5, 252, 5, 251, 5, 251, 4, 250, 4, 249, 4, 248, 4, 247, 4, 247, 3, 246, 3, 246, 2, 245, 2, 245, 1, 244, 1, 244, 0, 244, 255, 245, 255, 245, 254, 246, 254, 246, 253, 247, 253, 247, 252, 248, 252, 249, 252, 250, 252, 251, 252, 251, 251, 252, 251, 253, 251, 254, 251, 255, 251, 0, 251, 1, 251, 2, 251, 3, 251, 4, 251, 5, 251, 5, 252, 6, 252, 7, 252, 8, 252, 9, 252, 9, 253, 10, 253, 10, 254, 11, 254, 11, 255, 12, 255
ring_extra db 14, 0, 14, 1, 14, 2, 13, 2, 13, 3, 12, 3, 12, 4, 11, 4, 11, 5, 10, 5, 9, 5, 9, 6, 8, 6, 7, 6, 6, 6, 5, 6, 5, 7, 4, 7, 3, 7, 2, 7, 1, 7, 0, 7, 255, 7, 254, 7, 253, 7, 252, 7, 251, 7, 251, 6, 250, 6, 249, 6, 248, 6, 247, 6, 247, 5, 246, 5, 245, 5, 245, 4, 244, 4, 244, 3, 243, 3, 243, 2, 242, 2, 242, 1, 242, 0, 242, 255, 242, 254, 243, 254, 243, 253, 244, 253, 244, 252, 245, 252, 245, 251, 246, 251, 247, 251, 247, 250, 248, 250, 249, 250, 250, 250, 251, 250, 251, 249, 252, 249, 253, 249, 254, 249, 255, 249, 0, 249, 1, 249, 2, 249, 3, 249, 4, 249, 5, 249, 5, 250, 6, 250, 7, 250, 8, 250, 9, 250, 9, 251, 10, 251, 11, 251, 11, 252, 12, 252, 12, 253, 13, 253, 13, 254, 14, 254, 14, 255
r_kind     db 0
r_fx       dw 0
r_fy       dw 0
ring_tab   times MAP_COUNT db 0
red        times 256 db 0

; TARGETING (TARGET_ON): Tab and Shift+Tab, counted for the Loader, choose an enemy in a fight
; (its ring brighter: RINGS); Enter attacks it, as a click on it does, even where another figure
; stands in front of it. The game reads keys through INT 16h: INT16 takes Tab, Shift+Tab and (with
; an enemy chosen) Enter out of what it sees. For Enter, the main loop (TARGET_CLICK, from
; PROBE_SCROLL) puts the pointer at the enemy's feet and gives the game a left click there, while
; the routine that finds what is under the pointer (PROBE_HIT, DSUN.EXE 25B52h) answers with the
; chosen enemy for a moment (HIT_PASSES), whatever is in front of it.

KEY_TAB     equ 0x0F09
KEY_BACKTAB equ 0x0F00
KEY_ENTER   equ 0x1C0D
KEY_PAD_ENTER equ 0xE00D
KEY_L       equ 0x266C
KEY_SHIFT_L equ 0x264C
HIT_PASSES  equ 600             ; passes of the map's main loop the hit is the chosen enemy, from the
                                ;   click (not BIOS ticks: the BIOS clock can stand still in a fight,
                                ;   and the hit stayed the enemy, the walk to it stalling)
EVENT_LEFT_PRESS equ 2
EVENT_LEFT_LEAVE equ 4
LEFT        equ 1

int16:
        cmp word [cs:target_on], 0
        jne .on
        cmp byte [cs:panel_shown], 0    ; (L for the combat log's panel)
        jne .on
        cmp word [cs:panel_seg], 0      ; (... or to open it, over the map)
        je .chain
        cmp byte [cs:strip_on], 0
        jne .chain
.on:
        cmp ah, 0x00
        je .read
        cmp ah, 0x10
        je .read
        cmp ah, 0x01
        je .peek
        cmp ah, 0x11
        je .peek
.chain: jmp far [cs:old16]
.peek:  push ax                         ; a key waiting: if it is ours, take it and say none is
        pushf
        call far [cs:old16]
        jz .none
        call our_key
        jc .took
        add sp, 2                       ; (not ours: as the BIOS said)
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
.read:  push ax                         ; reading: ours are taken out and the next one read
.again: pop ax
        push ax
        pushf
        call far [cs:old16]
        call our_key
        jc .again
        add sp, 2
        iret

; L_ON_MAP: ZF set if L should open the panel over the map: the panel there (not the strip), not
; on screen, the map's main loop run within the last BIOS tick or two (no game window, save name
; or menu waiting on keys) and the Loader there; registers kept
L_FRESH    equ 2
l_on_map:
        push ax
        push es
        cmp word [cs:panel_seg], 0
        je .no
        cmp byte [cs:strip_on], 0
        jne .no
        cmp byte [cs:panel_shown], 0
        jne .no
        xor ax, ax
        mov es, ax
        mov ax, [es:0x46C]
        sub ax, [cs:map_tick]
        cmp ax, L_FRESH
        ja .no
        mov ax, [es:0x46C]
        sub ax, [cs:stats_stamp]
        cmp ax, STATS_FRESH
        jae .no
        xor ax, ax                      ; (ZF set)
        jmp .out
.no:    or ax, 1                        ; (ZF clear)
.out:   pop es
        pop ax
        ret
map_tick   dw 0

our_key:                                ; AX a key: CF set (and counted) if it is one of ours
        cmp ax, KEY_L
        je .l
        cmp ax, KEY_SHIFT_L
        jne .tabs
.l:     call panel_live                 ; L on the map, the panel on it: the Loader's
        je .count
        call l_on_map                   ; ... or the panel off, to open it
        jne .no
.count: inc word [cs:panel_keys]
        stc
        ret
.tabs:  cmp word [cs:target_on], 0
        je .no
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

; TARGET_CLICK: (in PROBE_SCROLL, DS = the game's) Enter on the chosen enemy: a left click at its feet
target_click:
        cmp byte [cs:t_click], 0
        je .ret
        mov byte [cs:t_click], 0
        cmp word [cs:game_mask], 0
        je .ret
        mov bx, [cs:hit_target]
        cmp bx, MAP_COUNT - 1
        ja .ret
        shl bx, 5
        mov cx, [bx + MAP_THINGS + 9]   ; its feet, on the map
        mov dx, [bx + MAP_THINGS + 11]
        sub cx, [CAM_X]
        sub dx, [CAM_Y]
        sub dx, 8                       ; (a little above them)
        cmp cx, 1
        jl .ret
        cmp cx, 0x13E
        jg .ret
        cmp dx, 1
        jl .ret
        cmp dx, 0xC6
        jg .ret
        mov [cs:t_x], cx
        mov [cs:t_y], dx
        mov ax, [cs:main_ticks]
        add ax, HIT_PASSES
        mov [cs:hit_until], ax
        mov byte [cs:hit_forced], 1
        mov ax, 4                       ; the pointer there
        mov cx, [cs:t_x]
        mov dx, [cs:t_y]
        int 0x33
        pusha                           ; and a click
        push ds
        push es
        mov ax, EVENT_LEFT_PRESS
        mov bx, LEFT
        mov cx, [cs:t_x]
        mov dx, [cs:t_y]
        xor si, si
        xor di, di
        call far [cs:game_handler]
        pop es
        pop ds
        popa
        pusha
        push ds
        push es
        mov ax, EVENT_LEFT_LEAVE
        xor bx, bx
        mov cx, [cs:t_x]
        mov dx, [cs:t_y]
        xor si, si
        xor di, di
        call far [cs:game_handler]
        pop es
        pop ds
        popa
.ret:   ret

; PROBE_HIT: INT VEC_HIT replaces "push bp / mov bp,sp / sub sp,10h" (6 bytes: INT + 4 NOPs) at the
; start of the routine that finds the thing under the pointer (camera x, y, x, y on screen; the
; thing, or FFFFh): for a moment after TARGET_CLICK, the chosen enemy, wherever the pointer is.
probe_hit:
        cmp byte [cs:hit_forced], 0
        je .plain
        cmp word [cs:hit_target], 0xFFFF
        je .over                        ; (no enemy chosen any more: a new turn, the click's done)
        push ax
        mov ax, [cs:main_ticks]
        sub ax, [cs:hit_until]
        pop ax
        jns .over
        push bp                         ; (the caller's flags back: the INT turned interrupts off,
        mov bp, sp                      ;   and a RETF leaves them so; the game then ran on without
        push word [bp + 6]              ;   its timer, a walk to the enemy frozen till something
        popf                            ;   turned them on again)
        pop bp
        add sp, 6                       ; (the interrupt's frame: back to the caller, the enemy)
        mov ax, [cs:hit_target]
        retf
.over:  mov byte [cs:hit_forced], 0
.plain: pop word [cs:h_resume]
        pop word [cs:h_resume + 2]
        popf
        push bp
        mov bp, sp
        sub sp, 0x10
        jmp far [cs:h_resume]

; PROBE_ITEM_BOX: INT VEC_ITEM_BOX replaces "push 0" (2 bytes) at the end of the routine that fills
; an item's box (right-click an item: its picture, price, name, damage, HEAVY, AC BONUS; DSUN.EXE
; 8C1A1h), its lines drawn (SI: the item's type, DI: the row after them, but for AC BONUS's).
; With SKILLS_ON's bits, a cloak's or boots' bonus to hiding in shadows or moving silently (the
; Loader's rule: stealth.py), or a belt's to picking pockets and opening locks (PROBE_BELT), in the
; next row, with the routine's own text routine, as it draws AC BONUS; an item that casts a spell
; with charges (a wand, a ring, a necklace: its spell byte, +0Fh, a spell's + 1 below ITEM_SPECIAL;
; its charges, +0Eh, not 0; not fruit, eaten whole; not scenery, a door) its charges left there
; ("Charges: 50"; the item [BP+6]); then the push, as the code would have.
IB_DRAW   equ 0x8C19A - 0x8C1A3 ; (DSUN.EXE) the text routine's far address in the call before,
                                ;   less the way back
TYPES_PTR equ 0x1669            ; DS: far pointer to the item types, 20 bytes each
TYPE_WORN equ 9                 ; in one: where it is worn (8: as a cloak, 4: on the feet, 2: as a belt)
SKILLS_STEALTH equ 1            ; (SKILLS_ON's bits)
SKILLS_BELT equ 2
SKILLS_ELVEN equ 4              ; (the Cloak and Boots of Elvenkind's: the stealth rule on)
TYPE_ARMOUR equ 0x0F            ; ... 80h: armour (AC BONUS drawn)
ITEM_CHARGES equ 0x0E          ; (an item's charges left and its spell + 1)
ITEM_SPELL   equ 0x0F
ITEM_SPECIAL equ 0xF9           ; (spell bytes from here are the game's own effects: a belt's STR...)
TYPE_FRUIT   equ 60
TYPE_SCENERY equ 0x60          ; (a type's +08h: doors, haystacks, walls...)
probe_item_box:
        pushad
        push es
        cmp si, 0x270F
        jae .push
        les bx, [TYPES_PTR]             ; (DS: the game's)
        imul ax, si, 20
        add bx, ax
        call ib_charges                 ; (DX the line, or 0)
        or dx, dx
        jnz .draw
        cmp word [cs:skills_on], 0
        je .push
        mov ax, si                      ; the Cloak and Boots of Elvenkind: their own lines
        sub ax, [cs:types_first]
        mov cl, SKILLS_ELVEN
        mov dx, ib_elf_hide
        cmp ax, ELVEN_CLOAK
        je .want
        mov dx, ib_elf_quiet
        cmp ax, ELVEN_BOOTS
        je .want
        mov al, [es:bx + TYPE_WORN]
        mov cl, SKILLS_STEALTH
        mov dx, ib_hide
        cmp al, 8
        je .want
        mov dx, ib_quiet
        cmp al, 4
        je .want
        mov cl, SKILLS_BELT
        mov dx, ib_belt
        cmp al, 2
        jne .push
.want:  test [cs:skills_on], cl
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
        push dword 0x00960081           ; (as the box draws its lines)
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

; IB_CHARGES: DX IB_CHARGES_TEXT with the charges of PROBE_ITEM_BOX's item ([BP+6]; SI its
; type, ES:BX its type's record) if it casts a spell with charges, else 0. Not for scenery (doors,
; walls: their +0Eh and +0Fh hold something else). DS the game's; others kept.
ib_charges:
        xor dx, dx
        cmp si, TYPE_FRUIT
        je .ret
        push ax
        push bx
        push es
        mov al, [es:bx + 8]
        and al, TYPE_SCENERY
        cmp al, TYPE_SCENERY
        je .none
        les bx, [0x165D]                ; (the items, 15h bytes each)
        imul ax, [bp + 6], 0x15
        add bx, ax
        mov al, [es:bx + ITEM_SPELL]
        or al, al
        jz .none
        cmp al, ITEM_SPECIAL
        jae .none
        movzx ax, byte [es:bx + ITEM_CHARGES]
        or ax, ax
        jz .none
        mov bl, 10                      ; (up to 255: three digits at most)
        mov dx, ib_charges_num
        push di
        mov di, dx
        div bl                          ; AL tens and hundreds, AH ones
        mov dh, ah
        xor ah, ah
        div bl                          ; AL hundreds, AH tens
        or al, al
        jz .tens
        add al, '0'
        mov [cs:di], al
        inc di
        jmp .tens_always
.tens:  or ah, ah
        jz .ones
.tens_always:
        add ah, '0'
        mov [cs:di], ah
        inc di
.ones:  add dh, '0'
        mov [cs:di], dh
        mov byte [cs:di + 1], 0
        pop di
        mov dx, ib_charges_text
        jmp .out
.none:  xor dx, dx
.out:   pop es
        pop bx
        pop ax
.ret:   ret

ib_draw    dd 0
ib_charges_text db 'Charges: '
ib_charges_num  db '000', 0
ib_hide    db 'Hide +10', 0     ; (the skills' short names, as the inventory screen's thief rows
ib_quiet   db 'Move +10', 0     ;   have them: HIDE, MOVE, PICK, LOCK; mixed case, as item names)
ib_belt    db 'Pick +5, Lock +5', 0
ib_elf_hide  db 'Hide 90-95%', 0    ; (the Cloak of Elvenkind's chance: stealth.py)
ib_elf_quiet db 'Move 95%', 0

; PROBE_BELT: INT VEC_BELT replaces "mov ax,si" (2 bytes) at the end of the game's thief skill
; routine (DSUN.EXE 803B2h: SI the chance, armour and effects counted; DI the thief's object; the
; game's [BP+8] the skill, a dword). With SKILLS_BELT, a thief wearing a belt (the waist slot)
; gets BELT_BONUS more to pick pockets (0) and open locks (1); then the kit's (KIT_SKILL), no less
; than 0, as the Loader counts them (game.py's thief_skills_now); 0 for a thief in armour that
; isn't light (THIEF_HEAVY); then AX = the chance, as the code would have.
WAIST      equ 5                ; the item's slot byte while worn as a belt
BELT_BONUS equ 5
COMBATANT_CREATURE equ 0xC37    ; in the things table: an object's creature (3 bytes an object)
probe_belt:
        sti
        mov ax, si
        cmp word [bp + 0x0A], 0
        jne .out
        push bx
        push cx
        push dx
        push es
        mov dx, si              ; DX the chance
        mov ax, ds
        add ax, THINGS_SEG
        mov [cs:r_things], ax
        mov es, ax
        imul bx, di, 3
        mov ax, [es:bx + COMBATANT_CREATURE]
        mov cx, ax
        cmp word [bp + 8], 1
        ja .kit                 ; (the belt: pick pockets and open locks only)
        test byte [cs:skills_on], SKILLS_BELT
        jz .kit
        mov word [cs:ws_slot], WAIST
        mov word [cs:ws_type], 0xFFFF
        push dx
        call worn_scan
        pop dx
        cmp word [cs:ws_count], 0
        je .kit
        add dx, BELT_BONUS
.kit:   mov ax, cx              ; the kit's (kits.thief_skill), no less than 0
        push si
        mov si, [bp + 8]
        call kit_skill
        pop si
        or ax, ax
        jz .done
        add dx, ax
        jns .done
        xor dx, dx
.done:  mov ax, cx
        call thief_heavy
        jnc .chance
        xor dx, dx
.chance:
        mov ax, dx
        pop es
        pop dx
        pop cx
        pop bx
.out:   iret

; THIEF_HEAVY: carry set if, with RULE_RESTRICT, creature AX (DS the game's) has a thief class and
; wears armour that isn't light (HEAVY_WORN): a multiclass thief, or a human thief once a warrior
; (or a warrior once a thief), may wear it, but loses its thief skills and backstab in it
; (restrict.thief_heavy). All registers kept.
thief_heavy:
        test word [cs:rules], RULE_RESTRICT
        jz .no
        pusha
        push es
        call creature_sheet
        mov cx, 3
        xor si, si
.class: cmp byte [es:bx + si + 0x21], THIEF_CLASS
        je .thief
        inc si
        loop .class
        pop es
        popa
.no:    clc
        ret
.thief: mov dx, ax
        call heavy_worn
        pop es
        popa
        ret

; KIT_SKILL: AX what the kit of creature AX adds to thief skill SI (0-7: game.THIEF_SKILLS' order)
; (kits.thief_skill): KIT_SKILLS' row for each of its kits; a Military Scout's 10 to finding traps,
; moving silently, hiding and climbing while under the open sky (KIT_OUTDOORS), 5 less under a roof.
; DS the game's; others kept.
kit_skills db KIT_SWASHBUCKLER, -10, -10, -10, -10, -10, -10, -10, -10  ; (pick pockets, open locks,
           db KIT_ASSASSIN, -15, -15, 0, 0, 0, 0, 0, 0                  ;  traps, move silently, hide,
           db KIT_SHADOWBLADE, -10, 0, 0, 5, 10, 0, 0, 0                ;  hear noise, climb, read)
           db KIT_GHETTO, 5, 0, -5, 0, 5, 0, 0, 0
           db KIT_WAYFINDER, -10, 0, 0, 10, 10, 0, 0, 0
           db 0
SCOUT_SKILLS equ 0x5C           ; (bits: traps, move silently, hide, climb)
kit_skill:
        push bx
        push cx
        push dx
        push di
        push es
        mov cx, ax
        call creature_sheet
        xor dx, dx
        cmp si, 7
        ja .out
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
.scout: mov al, KIT_SCOUT
        call kit_is
        jne .out
        bt word [cs:scout_bits], si
        jnc .out
        mov ax, -5
        cmp cx, 3
        ja .add
        bt word [cs:kit_outdoors], cx
        jnc .add
        mov ax, 10
.add:   add dx, ax
.out:   mov ax, dx
        pop es
        pop di
        pop dx
        pop cx
        pop bx
        ret
scout_bits dw SCOUT_SKILLS

old16      dd 0
t_click    db 0
hit_forced db 0
hit_until  dw 0
h_resume   dd 0

old33        dd 0
game_handler dd 0
game_mask    dw 0
centre       dw CENTRE_OFF, 0
s_resume     dd 0
s_resume_fl  dw 0
drag         db 0               ; 0: no drag; 1: the right button held, not moved yet; 2: dragging
drag_mid     db 0               ; 1: dragging with the wheel pressed
drag_new     db 0
drag_x       dw 0               ; where it was pressed
drag_y       dw 0
cam0_x       dw 0               ; the view's top left then
cam0_y       dw 0
pan_x_done   dw 0
pan_y_done   dw 0

loader     dw LOADER_OFF, 0
resume     dd 0
resume_fl  dw 0
floor_ret  dd 0
floor_frame dw 0
floor_kind db 0
floor_busy db 0
dark_ready db 0
mirror     db 0
r_n        db 0
sc_index   db 0
sc_mask    db 0
gc_index   db 0
gc_regs    db 1, 3, 4, 5, 8
gc_saved   times 5 db 0
zero       dw 0
game_ds    dw 0
%ifdef CAMTRACE
; (a test build's only: INT 3 put over "push bp" at the start of the game's routine that centres
; the view on a creature, by hand: each caller's return address kept, 16 of them, then "push bp")
cam_trace:
        push bp
        mov bp, sp
        push ax
        push bx
        mov bx, [cs:cam_n]
        and bx, 0x3C
        mov ax, [bp + 8]
        mov [cs:cam_log + bx], ax
        mov ax, [bp + 10]
        mov [cs:cam_log + bx + 2], ax
        add word [cs:cam_n], 4
        mov ax, [bp]
        mov bx, [bp + 2]
        mov [bp], bx
        mov bx, [bp + 4]
        mov [bp + 2], bx
        mov bx, [bp + 6]
        mov [bp + 4], bx
        mov [bp + 6], ax
        pop bx
        pop ax
        mov bp, [bp + 6]
        iret
        db "CAMTRACE"
cam_n   dw 0
cam_log times 64 db 0
%endif
load_seg   dw 0
clip_x0    dw 0
clip_y0    dw 0
clip_x1    dw 0
clip_y1    dw 0
v_seg      dw 0
v_x0       dw 0
v_y0       dw 0
v_row      dw 0
cam_x      dw 0
cam_y      dw 0
fig_x      dw 0
fig_y      dw 0
frame      dw 0
f_w        dw 0
f_bottom   dw 0
f_y        dw 0
r_x        dw 0
row_at     dw 0
best_d     dd 0
diffs      times 3 db 0
lit_sum    dw 0
lit_most   dw 0
best_c     db 0
want       times 3 db 0
shadow_tab times MAP_COUNT db 0
dark       times 256 db 0
dac        times 768 db 0

tbuf:   times TSIZE db 0

; KEEP: the last of installing, from here, as the ring is where the install code was: clear the
; ring and stay resident, the ring with the image (DX the paragraphs). The stack goes to the PSP's
; command tail first, out of the ring's way.
keep:   mov ax, [cs:psp]
        mov ss, ax
        mov sp, 0x100
        mov es, [cs:ring_seg]
        xor di, di
        xor ax, ax
        mov cx, RING_BYTES / 2
        cld
        rep stosw
        mov ax, 3100h
        int 21h

align 16
seg_space times SEG_BYTES db 0   ; (SEG_MOVE's: the stack's 60h bytes, then the monster kinds')
resident_end:                   ; (the ring follows, in a segment of its own)
RING_BYTES equ NENT * ESIZE

install:                        ; DS = ES = PSP, CS = the image
        mov [cs:psp], es
        push cs
        pop ds
        mov si, all_vectors     ; the vectors must be free
        mov cx, all_vectors_end - all_vectors
.check:
        lodsb
        mov ah, 35h
        int 21h                 ; ES:BX = the vector
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

        mov ax, 2500h + VEC_RAND
        mov dx, int_rand
        int 21h
        mov ax, 2500h + VEC_SAVE
        mov dx, probe_save
        int 21h
        mov ax, 2500h + VEC_AC
        mov dx, probe_ac
        int 21h
        mov ax, 2500h + VEC_TEXT
        mov dx, probe_text
        int 21h
        mov ax, 2500h + VEC_MSG
        mov dx, probe_msg
        int 21h
        mov ax, 2500h + VEC_CHAR
        mov dx, probe_char
        int 21h
        mov ax, 2500h + VEC_USE
        mov dx, probe_use
        int 21h
        mov ax, 2500h + VEC_VIEW
        mov dx, probe_view
        int 21h
        mov ax, 2500h + VEC_WIN
        mov dx, probe_win
        int 21h
        mov ax, 2500h + VEC_LOOK
        mov dx, probe_look
        int 21h
        mov ax, 2500h + VEC_UNLOOK
        mov dx, probe_unlook
        int 21h
        mov ax, 2500h + VEC_RING_AC
        mov dx, probe_ring_ac
        int 21h
        mov ax, 2500h + VEC_RING_SAVE
        mov dx, probe_ring_save
        int 21h
        mov ax, 2500h + VEC_WEAPON
        mov dx, probe_weapon
        int 21h
        mov ax, 2500h + VEC_MOVE
        mov dx, probe_move
        int 21h
        mov ax, 2500h + VEC_USE_ITEM
        mov dx, probe_use_item
        int 21h
        mov ax, 2500h + VEC_MISSILE_LINE
        mov dx, probe_missile_line
        int 21h
        mov ax, 2500h + VEC_RACE_PANEL
        mov dx, probe_race_panel
        int 21h
        mov ax, 2500h + VEC_BOX_AC
        mov dx, probe_box_ac
        int 21h
        mov ax, 2500h + VEC_TICK
        mov dx, probe_tick
        int 21h
        mov ax, 2500h + VEC_POISON
        mov dx, probe_poison
        int 21h
        mov ax, 2500h + VEC_ARROW
        mov dx, probe_arrow
        int 21h
        mov ax, 2500h + VEC_TWO
        mov dx, probe_two
        int 21h
        mov ax, 2500h + VEC_DOUBLE
        mov dx, probe_double
        int 21h
        mov ax, 2500h + VEC_GRACE_CAST
        mov dx, probe_grace_cast
        int 21h
        mov ax, 2500h + VEC_GRACE_EFFECT
        mov dx, probe_grace_effect
        int 21h
        mov ax, 2500h + VEC_GRACE_ABILITY
        mov dx, probe_grace_ability
        int 21h
        mov ax, 2500h + VEC_NAMES_SIZE
        mov dx, probe_names_size
        int 21h
        mov ax, 2500h + VEC_NAMES_FILL
        mov dx, probe_names_fill
        int 21h
        mov ax, 2500h + VEC_STEALTH
        mov dx, probe_stealth
        int 21h
        mov ax, 2500h + VEC_TYPES_SIZE
        mov dx, probe_types_size
        int 21h
        mov ax, 2500h + VEC_TYPES_FILL
        mov dx, probe_types_fill
        int 21h
        mov ax, 2500h + VEC_LEVEL
        mov dx, probe_level
        int 21h
        mov ax, 2500h + VEC_HD_ROLL
        mov dx, probe_hd_roll
        int 21h
        mov ax, 2500h + VEC_HD_CON
        mov dx, probe_hd_con
        int 21h
        mov ax, 2500h + VEC_THIEF_SKILL
        mov dx, probe_thief_skill
        int 21h
        mov ax, 2500h + VEC_TWO_HANDED
        mov dx, probe_two_handed
        int 21h
        mov ax, 2500h + VEC_SPELL_TEXT
        mov dx, probe_spell_text
        int 21h
        mov ax, 2500h + VEC_CHUNK_ID
        mov dx, probe_chunk_id
        int 21h
        mov ax, 2500h + VEC_FLOOR_ALL
        mov dx, probe_floor_all
        int 21h
        mov ax, 2500h + VEC_FLOOR_RECT
        mov dx, probe_floor_rect
        int 21h
        mov ax, 2500h + VEC_REDRAW
        mov dx, probe_redraw
        int 21h
        mov ax, 2500h + VEC_REDRAW_ALL
        mov dx, probe_redraw_all
        int 21h
        mov ax, 2500h + VEC_POINTER
        mov dx, probe_pointer
        int 21h
        mov ax, 2500h + VEC_STRIP
        mov dx, probe_strip
        int 21h
%ifdef CAMTRACE
        mov ax, 2503h
        mov dx, cam_trace
        int 21h
%endif
        mov ax, 2500h + VEC_PALETTE
        mov dx, probe_palette
        int 21h
        mov ax, 2500h + VEC_COLOURS
        mov dx, probe_colours
        int 21h
        mov ax, 2500h + VEC_SCROLL
        mov dx, probe_scroll
        int 21h
        mov ax, 2500h + VEC_HIT
        mov dx, probe_hit
        int 21h
        mov ax, 2500h + VEC_ITEM_BOX
        mov dx, probe_item_box
        int 21h
        mov ax, 2500h + VEC_BELT
        mov dx, probe_belt
        int 21h
        mov ax, 2500h + VEC_SAVE_PAGE
        mov dx, probe_save_page
        int 21h
        mov ax, 2500h + VEC_SAVE_CLICK
        mov dx, probe_save_click
        int 21h
        mov ax, 2500h + VEC_ITEM_WEAPON
        mov dx, probe_item_weapon
        int 21h
        mov ax, 2500h + VEC_ITEM_SKIP
        mov dx, probe_item_skip
        int 21h
        mov ax, 2500h + VEC_ITEM_ARMOUR
        mov dx, probe_item_armour
        int 21h
        mov ax, 2500h + VEC_SCRIPT_RAND
        mov dx, probe_script_rand
        int 21h
        mov ax, 2500h + VEC_XP_NEXT
        mov dx, probe_xp_next
        int 21h
        mov ax, 2500h + VEC_ATTACKS
        mov dx, probe_attacks
        int 21h
        mov ax, 2500h + VEC_SPEC_DAMAGE
        mov dx, probe_spec_damage
        int 21h
        mov ax, 2500h + VEC_DAM_LINE
        mov dx, probe_dam_line
        int 21h
        mov ax, 2500h + VEC_VIEW_DAM
        mov dx, probe_view_dam
        int 21h
        mov ax, 2500h + VEC_CAN_USE
        mov dx, probe_can_use
        int 21h
        mov ax, 2500h + VEC_NO_CAST
        mov dx, probe_no_cast
        int 21h
        mov ax, 2500h + VEC_MC_CON
        mov dx, probe_mc_con
        int 21h
        mov ax, 2500h + VEC_MC_UNCON
        mov dx, probe_mc_uncon
        int 21h
        mov ax, 2500h + VEC_WP_DISC_WIN
        mov dx, probe_wp_disc_win
        int 21h
        mov ax, 2500h + VEC_WP_SPHERE_WIN
        mov dx, probe_wp_sphere_win
        int 21h
        mov ax, 2500h + VEC_WP_DISC_CLICK
        mov dx, probe_wp_disc_click
        int 21h
        mov ax, 2500h + VEC_WP_SPHERE_CLICK
        mov dx, probe_wp_sphere_click
        int 21h
        mov ax, 2500h + VEC_WP_SHOWN
        mov dx, probe_wp_shown
        int 21h
        mov ax, 2500h + VEC_WP_CLASS
        mov dx, probe_wp_class
        int 21h
        mov ax, 2500h + VEC_LV_PICK
        mov dx, probe_lv_pick
        int 21h
        mov ax, 2500h + VEC_PK_COUNT
        mov dx, probe_pk_count
        int 21h
        mov ax, 2500h + VEC_PK_WIN
        mov dx, probe_pk_win
        int 21h
        mov ax, 2500h + VEC_PK_LEFT
        mov dx, probe_pk_left
        int 21h
        mov ax, 2500h + VEC_PK_TITLE
        mov dx, probe_pk_title
        int 21h
        mov ax, 2500h + VEC_PK_FILL
        mov dx, probe_pk_fill
        int 21h
        mov ax, 2500h + VEC_PK_CLICK
        mov dx, probe_pk_click
        int 21h
        mov ax, 2500h + VEC_HP_BEST
        mov dx, probe_hp_best
        int 21h
        mov ax, 2500h + VEC_TOME
        mov dx, probe_tome
        int 21h
        mov ax, 2500h + VEC_EF_ROWS
        mov dx, probe_ef_rows
        int 21h
        mov ax, 2500h + VEC_INIT
        mov dx, probe_init
        int 21h
        mov ax, 2500h + VEC_THAC0
        mov dx, probe_thac0
        int 21h
        mov ax, 2500h + VEC_SLOTS
        mov dx, probe_slots
        int 21h
        mov ax, 2500h + VEC_SLOT_LEVEL
        mov dx, probe_slot_level
        int 21h
        mov ax, 2500h + VEC_PSP_USE
        mov dx, probe_psp_use
        int 21h
        mov ax, 2500h + VEC_PSP_TABLE
        mov dx, probe_psp_table
        int 21h
        mov ax, 2500h + VEC_PSP_DEFENCE
        mov dx, probe_psp_defence
        int 21h
        mov ax, 2500h + VEC_CURE
        mov dx, probe_cure
        int 21h
        mov ax, 2500h + VEC_PSP_KEEP
        mov dx, probe_psp_keep
        int 21h
        mov ax, 2500h + VEC_PSP_KEEP_DX
        mov dx, probe_psp_keep_dx
        int 21h
        mov ax, 2500h + VEC_HIT_ROUND
        mov dx, probe_hit_round
        int 21h
        mov ax, 2500h + VEC_CAST_LEVEL
        mov dx, probe_cast_level
        int 21h
        mov ax, 2500h + VEC_SPELL_LEVEL
        mov dx, probe_spell_level
        int 21h
        mov ax, 2500h + VEC_PICK_ANY
        mov dx, probe_pick_any
        int 21h
        mov ax, 2500h + VEC_RANGER_LEVEL
        mov dx, probe_ranger_level
        int 21h
        mov ax, 2500h + VEC_HIT_DIE
        mov dx, probe_hit_die
        int 21h
        mov ax, 2500h + VEC_MAX_PSP
        mov dx, probe_max_psp
        int 21h
        mov ax, 2500h + VEC_CR_DIE
        mov dx, probe_cr_die
        int 21h
        mov ax, 2500h + VEC_CR_PSP
        mov dx, probe_cr_psp
        int 21h
        mov ax, 2500h + VEC_EL_GRANT
        mov dx, probe_el_grant
        int 21h
        mov ax, 2500h + VEC_EL_CAST
        mov dx, probe_el_cast
        int 21h
        mov ax, 2500h + VEC_EL_LEVEL
        mov dx, probe_el_level
        int 21h
        mov ax, 2500h + VEC_EL_KNOW
        mov dx, probe_el_know
        int 21h
        mov ax, 2500h + VEC_DUAL_BAN
        mov dx, probe_dual_ban
        int 21h
        mov ax, 2500h + VEC_DUAL_SPELLS
        mov dx, probe_dual_spells
        int 21h
        mov ax, 2500h + VEC_SOUND_42
        mov dx, probe_sound_42
        int 21h
        mov ax, 2500h + VEC_SOUND_44
        mov dx, probe_sound_44
        int 21h
        mov ax, 2500h + VEC_DUAL_KIT
        mov dx, probe_dual_kit
        int 21h
        mov ax, 2500h + VEC_CR_SPELLS
        mov dx, probe_cr_spells
        int 21h
        mov ax, 2500h + VEC_EF_CLICK
        mov dx, probe_ef_click
        int 21h
        mov ax, 2500h + VEC_CAST_MARK
        mov dx, probe_cast_mark
        int 21h
        mov ax, 2500h + VEC_ROUND_MARK
        mov dx, probe_round_mark
        int 21h
        mov ax, 2500h + VEC_CAST_DONE
        mov dx, probe_cast_done
        int 21h
        mov ax, 2500h + VEC_END_TURN
        mov dx, probe_end_turn
        int 21h
        mov ax, 2500h + VEC_LEARN_SAID
        mov dx, probe_learn_said
        int 21h
        mov ax, 2500h + VEC_LEARN_REFUSED
        mov dx, probe_learn_refused
        int 21h
        mov ax, 2500h + VEC_XP
        mov dx, probe_xp
        int 21h
        mov ax, 2500h + VEC_PRIEST_THAC0
        mov dx, probe_priest_thac0
        int 21h
        mov ax, 2500h + VEC_ADND_SLOTS
        mov dx, probe_adnd_slots
        int 21h
        mov ax, 2500h + VEC_PRICE
        mov dx, probe_price
        int 21h
        mov ax, 2500h + VEC_PRICE_EAX
        mov dx, probe_price_eax
        int 21h
        mov ax, 2500h + VEC_RS_CLICK
        mov dx, probe_rs_click
        int 21h
        mov ax, 2500h + VEC_PICK_LEVEL
        mov dx, probe_pick_level
        int 21h
        mov ax, 2500h + VEC_PICK_LIST
        mov dx, probe_pick_list
        int 21h
        mov ax, 2500h + VEC_SCROLL_LEARN
        mov dx, probe_scroll_learn
        int 21h
        mov ax, 2500h + VEC_RANGER_CAST
        mov dx, probe_ranger_cast
        int 21h
        mov ax, 3516h           ; the keyboard's (TARGETING)
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
        mov ax, 3521h           ; DOS itself last: opening the objects file (PROBE_DOS_OPEN)
        int 21h
        mov [old21], bx
        mov [old21 + 2], es
        mov ax, 2521h
        mov dx, probe_dos_open
        int 21h
        mov byte [hooked], 1

        mov es, [cs:psp]
        mov es, [es:0x2C]       ; free our copy of the environment
        mov ah, 49h
        int 21h
        mov dx, msg
        mov ah, 9
        int 21h
        mov bx, (RING_BYTES + 15) / 16  ; the ring, in a block of its own: upper memory, else any
        call umb_alloc
        jnc .ring
        mov ah, 48h
        mov bx, (RING_BYTES + 15) / 16
        int 21h
        jnc .ring
        mov ax, cs                      ; (none: the paragraphs after the resident image, which
        add ax, (resident_end - hdr) / 16   ;  the load's size leaves room for)
        mov [cs:ring_seg], ax
        mov bx, (PANEL_BYTES + 15) / 16
        call umb_alloc
        jc .nopan1
        mov [cs:panel_seg], ax
.nopan1:
        mov dx, 0x10 + (resident_end - hdr) / 16 + RING_BYTES / 16  ; PSP, image and ring, in paragraphs
        jmp keep
.ring:  mov [cs:ring_seg], ax
        mov bx, (PANEL_BYTES + 15) / 16 ; the combat log's picture: upper memory only (else no panel)
        call umb_alloc
        jc .nopan2
        mov [cs:panel_seg], ax
.nopan2:
        mov dx, 0x10 + (resident_end - hdr) / 16    ; PSP and image, in paragraphs
        jmp keep

; UMB_ALLOC: BX paragraphs in upper memory (the upper blocks linked in, high only, best fit, for the
; moment), AX the segment; CF set if none has room. The DOS's own settings put back.
umb_alloc:
        push bx
        mov ax, 5802h                   ; (the link and the strategy as they were)
        int 21h
        mov [cs:ua_link], al
        mov ax, 5800h
        int 21h
        mov [cs:ua_strat], ax
        mov ax, 5803h
        mov bx, 1
        int 21h
        mov ax, 5801h
        mov bx, 41h                     ; (best fit, upper memory only)
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
ua_link  db 0
ua_strat dw 0

msg     db 'Dark Sun companion dice log helper loaded.', 13, 10, '$'
psp     dw 0
busy    db 'DSCLOG: interrupts 60h-65h or 8Ch-FEh are in use (already loaded?). Not loaded.', 13, 10, '$'
all_vectors db VEC_RAND, VEC_SAVE, VEC_AC, VEC_TEXT, VEC_MSG, VEC_CHAR, VEC_USE, VEC_VIEW, VEC_WIN, VEC_LOOK, VEC_UNLOOK, VEC_RING_AC, VEC_RING_SAVE, VEC_WEAPON, VEC_MOVE, VEC_MISSILE_LINE, VEC_USE_ITEM, VEC_TWO, VEC_DOUBLE, VEC_GRACE_CAST, VEC_GRACE_EFFECT, VEC_GRACE_ABILITY, VEC_NAMES_SIZE, VEC_NAMES_FILL, VEC_STEALTH, VEC_TYPES_SIZE, VEC_TYPES_FILL, VEC_LEVEL, VEC_HD_ROLL, VEC_HD_CON, VEC_THIEF_SKILL, VEC_TWO_HANDED, VEC_SPELL_TEXT, VEC_CHUNK_ID, VEC_FLOOR_ALL, VEC_FLOOR_RECT, VEC_REDRAW, VEC_REDRAW_ALL, VEC_SCROLL, VEC_HIT, VEC_ITEM_BOX, VEC_BELT, VEC_SAVE_PAGE, VEC_SAVE_CLICK, VEC_ITEM_WEAPON, VEC_ITEM_SKIP, VEC_ITEM_ARMOUR, VEC_SCRIPT_RAND, VEC_XP_NEXT, VEC_ATTACKS, VEC_SPEC_DAMAGE, VEC_DAM_LINE, VEC_VIEW_DAM, VEC_CAN_USE, VEC_NO_CAST, VEC_MC_CON, VEC_MC_UNCON, VEC_WP_DISC_WIN, VEC_WP_SPHERE_WIN, VEC_WP_DISC_CLICK, VEC_WP_SPHERE_CLICK, VEC_WP_SHOWN, VEC_WP_CLASS, VEC_LV_PICK, VEC_PK_COUNT, VEC_PK_WIN, VEC_PK_LEFT, VEC_PK_TITLE, VEC_PK_FILL, VEC_PK_CLICK, VEC_EF_ROWS, VEC_HP_BEST, VEC_TOME, VEC_INIT, VEC_THAC0, VEC_SLOTS, VEC_SLOT_LEVEL
            db VEC_PSP_USE, VEC_PSP_TABLE, VEC_PSP_DEFENCE, VEC_CURE, VEC_PSP_KEEP, VEC_RANGER_CAST, VEC_PSP_KEEP_DX
            db VEC_HIT_ROUND, VEC_CAST_LEVEL, VEC_PICK_LEVEL, VEC_PICK_LIST, VEC_SCROLL_LEARN, VEC_SPELL_LEVEL, VEC_PICK_ANY, VEC_RANGER_LEVEL, VEC_HIT_DIE, VEC_MAX_PSP, VEC_CR_DIE, VEC_CR_PSP, VEC_EL_GRANT, VEC_EL_CAST, VEC_EL_LEVEL, VEC_EL_KNOW, VEC_DUAL_BAN, VEC_DUAL_SPELLS, VEC_SOUND_42, VEC_SOUND_44, VEC_DUAL_KIT, VEC_CR_SPELLS, VEC_EF_CLICK, VEC_CAST_MARK, VEC_ROUND_MARK, VEC_CAST_DONE, VEC_END_TURN, VEC_LEARN_SAID, VEC_LEARN_REFUSED, VEC_XP, VEC_PRIEST_THAC0, VEC_ADND_SLOTS, VEC_POINTER, VEC_STRIP, VEC_PALETTE, VEC_COLOURS, VEC_PRICE, VEC_PRICE_EAX, VEC_RS_CLICK, VEC_RACE_PANEL, VEC_BOX_AC, VEC_TICK, VEC_POISON, VEC_ARROW
all_vectors_end:

        align 16, db 0
image_len equ $ - $$
file_len  equ image_len + 32
; the memory past the image to load in: up to the ring's end (the ring follows the resident part,
; over the install code), and the install's stack beyond it (resident_end + RING_BYTES is the
; larger: the install code and its stack are smaller than the ring)
LOAD_EXTRA equ (resident_end - hdr + RING_BYTES - image_len + STACK + 15) / 16
