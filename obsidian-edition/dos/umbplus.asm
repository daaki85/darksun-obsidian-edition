; UMBPLUS.COM: 28 KB more upper memory in DOSBox 0.74, run before the helper is loaded high.
;
; DOSBox 0.74 (GOG's) makes its upper memory block at D000h-EFFFh (umb=true, ems=false), but the
; RAM below it, C800h-CFFFh, is ordinary memory too: only C000h-C7FFh is ROM (the video BIOS)
; (its src/hardware/memory.cpp). DOSBox keeps its own small tables there (DOS_PRIVATE_SEGMENT, from
; C800h up: DOS_GetMemory, src/dos/dos_tables.cpp), to about C8B1h once the shell is up, a few
; paragraphs more when a program asks for more file handles (the game does, once: INT 21h AH=67h at
; DSUN.EXE 54F3h). So the block can start at C900h: the system MCB at 9FFFh that covers the video
; memory and the ROM is cut to end there, and a free block's MCB goes at C900h, reaching F000h as
; the old one did.
;
; Done only if the chain is exactly DOSBox 0.74's, untouched (the system MCB at 9FFFh, 'M', owner
; 8, "SC", to D000h; at D000h one free block, 'Z', to F000h), and C900h-CFFFh is all zero (DOSBox
; clears its memory: nothing has used it) and holds what is written there (RAM, not ROM or a hole).
; Anything else (another DOSBox, EMS's page frame, the helper already loaded): left as it is.
; Exit code 0 if the block was moved, 1 if not. Says nothing either way.

        org 100h
COVER   equ 9FFFh               ; the system MCB DOSBox puts before upper memory
OLD_UMB equ 0D000h              ; its free block's MCB
NEW_UMB equ 0C900h
UMB_END equ 0F000h

start:  cld
        mov ax, COVER
        mov es, ax
        cmp byte [es:0], 'M'
        jne no
        cmp word [es:1], 8
        jne no
        cmp word [es:3], OLD_UMB - COVER - 1
        jne no
        cmp word [es:8], 'SC'
        jne no
        mov ax, OLD_UMB
        mov es, ax
        cmp byte [es:0], 'Z'
        jne no
        cmp word [es:1], 0
        jne no
        cmp word [es:3], UMB_END - OLD_UMB - 1
        jne no

        mov ax, NEW_UMB         ; C900h-CFFFh: all zero ...
        mov es, ax
        xor di, di
        mov cx, (OLD_UMB - NEW_UMB) * 16
        xor al, al
        repe scasb
        jne no
        mov bx, NEW_UMB         ; ... and RAM: each 4 KB page keeps a word written to it
.page:  mov es, bx
        mov word [es:0], 0A55Ah
        cmp word [es:0], 0A55Ah
        mov word [es:0], 0
        jne no
        add bx, 100h
        cmp bx, OLD_UMB
        jb .page

        mov ax, NEW_UMB         ; the free block from C900h, the system MCB cut to meet it
        mov es, ax
        mov byte [es:0], 'Z'
        mov word [es:1], 0
        mov word [es:3], UMB_END - NEW_UMB - 1
        mov ax, COVER
        mov es, ax
        mov word [es:3], NEW_UMB - COVER - 1
        mov ax, OLD_UMB         ; (the old MCB, now inside the block, cleared)
        mov es, ax
        xor di, di
        mov cx, 8
        xor ax, ax
        rep stosw
        mov ax, 4C00h
        int 21h
no:     mov ax, 4C01h
        int 21h
