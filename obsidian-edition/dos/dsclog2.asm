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
; and DOS's file opens, so the game reads the Loader's copy of RESOURCE.GFF (D:\RESOURC2.GFF, with
; the spell records' fixes: dsloader/ravager.py) in place of its own.
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
panel_off dw 0                  ; +140
far_seg   dw 0                  ; +142 the far block's segment (FAR_INIT): its buffers from FAR_RING on
vec_table dw all_vectors        ; +144 where ALL_VECTORS is in the image
copied    dw 0                  ; +146 1 once the game has opened the Loader's RESOURCE.GFF copy
        times 268 - ($ - hdr) db 0  ; (DSCLOG's fields +148 to +267: none of them here yet, zero)
ring_seg dw 0                   ; +268 the ring's segment: the far block's (FAR_SEG), as DSCLOG's
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

; ---- DOS's file opens: DSCLOG's PROBE_DOS_OPEN, for RESOURCE.GFF only ----
; Opening a file (AH=3Dh) whose name is RESOURCE.GFF (the whole path, or after a \, : or /, in any
; case) opens the Loader's copy, D:\RESOURC2.GFF, instead (with the same mode), and notes it
; (COPIED); with no copy there, the game's own. Everything else goes on to DOS.
probe_dos_open:
        cmp ah, 3Dh
        jne .chain
        push ax
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
        cmp cx, RES_LEN
        jb .no
        sub si, RES_LEN         ; where the name would start
        cmp cx, RES_LEN
        je .compare             ; (the path is just the name)
        mov al, [si - 1]
        cmp al, '\'
        je .compare
        cmp al, ':'
        je .compare
        cmp al, '/'
        jne .no
.compare:
        mov di, res_name
        mov cx, RES_LEN
.cmp:   mov al, [si]
        cmp al, 'a'
        jb .upper
        cmp al, 'z'
        ja .upper
        sub al, 20h
.upper: cmp al, [cs:di]
        jne .no
        inc si
        inc di
        loop .cmp
        pop di
        pop si
        pop cx
        pop ax
        sti
        push ax                 ; (the game's AX, for its own file if there's no copy)
        push ds
        push dx
        push cs
        pop ds
        mov dx, copy_path
        pushf
        call far [cs:old21]
        pop dx
        pop ds
        jc .own
        add sp, 2               ; (CF clear, AX the handle)
        mov word [cs:copied], 1
        retf 2
.own:   pop ax
        jmp .chain
.no:    pop di
        pop si
        pop cx
        pop ax
.chain: jmp far [cs:old21]

res_name  db 'RESOURCE.GFF'
RES_LEN   equ $ - res_name
copy_path db 'D:\RESOURC2.GFF', 0

resident_end:
align 16
RESIDENT_PARAS equ (resident_end - hdr + 15) / 16   ; (the image to here: what stays)

; ---- the far block (FAR_INIT): the ring ----
FAR_RING   equ 0x10
FAR_END    equ FAR_RING + NENT * ESIZE
FAR_PARAS  equ (FAR_END - FAR_RING + 15) / 16 + 1

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
        mov byte [hooked], 1
        mov ax, [cs:far_seg]
        mov [cs:ring_seg], ax
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
        mov cx, (FAR_END - FAR_RING) / 2
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
        mov cx, (FAR_END - FAR_RING) / 2
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
VECTORS equ ($ - all_vectors) / 3

align 16
image_len equ $ - $$
LOAD_EXTRA equ (STACK + 15) / 16
file_len equ 32 + image_len
