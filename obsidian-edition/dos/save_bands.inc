; SAVE_BANDS: the saving throws as in AD&D for DSCLOG's and DSCLOG2's SAVE_BASE (tables.RAV_SAVE_BANDS):
; the Player's Handbook's Table 60 by class group (priests, warriors, wizards, rogues) and Dark Sun's
; Table 8 for psionicists (SAVE_PSI_SET), a band each: its first level, then paralysis, poison and death;
; rod, staff and wand; petrification and polymorph; breath; spell. Each set's begin with level 1.
; Included by both before their code: SAVE_BASE_CODE (in the segment) and SAVE_BANDS_DATA (DSCLOG's in its
; tail, DSCLOG2's in its segment: each reached through TAIL_SEG, DSCLOG2's its own segment).
SAVE_BAND       equ 6                   ; (a band: its first level, then the five saves)
SAVE_ROGUES     equ 3                   ; (the game's group of thieves and psionicists)
SAVE_PSI_SET    equ 4                   ; (SAVE_BANDS' psionicists' set)
SAVE_THIEF      equ 17                  ; (the class numbers)
SAVE_PSIONICIST equ 12

; SAVE_BASE: the site over "mov al,es:[bx+6Ch]" in the game's save routine (SL's 877EBh, the sequel's
; 954D2h, run at a level up: for each class group CX 0-3, at the best level of its classes in it,
; [BP-0Ah] + CX x 2, and each save SI 0-4, the group's 1st-level save less (level - 1) x a rate / 100, but
; no more than its table's third byte, AD&D's last save, taken off in "cbw / sub ax,[bp-2]", [BP-2]
; that improvement plus a dwarf's or halfling's CON bonus; DI the creature). With RULE_HI_TABLES, AL
; the Handbook's save plus the game's improvement worked out again, so the game's sum is the
; Handbook's less the race's bonus; for the rogues, the better of a thief's save at its thief level and
; a psionicist's (Dark Sun's table) at its psionicist level, from the sheet (the game lumps the two at
; the best level of either). The best of the groups is the game's (its "jle" keeps the lowest). The
; rule off, the game's byte. Others kept.
; %1 the sheets' far pointer (in the game's DS), %2 a sheet's size, %3 its classes, %4 its levels.
%macro SAVE_BASE_CODE 4
save_base:
        mov al, [es:bx + 0x6C]
        test word [cs:rules_hi], RULE_HI_TABLES
        jz .out
        push bx
        push cx
        push dx
        push si
        push di
        push ds
        push es
        push di                         ; (the creature)
        mov di, cx
        add di, di
        movsx di, byte [bp + di - 0x0A] ; (the group's level)
        mov ax, di                      ; the game's improvement, which it takes off:
        dec ax                          ;   (level - 1) x rate / 100, the third byte at most
        movsx dx, byte [es:bx + 0x6D]
        imul dx
        cwd
        push si
        mov si, 100
        idiv si
        pop si
        movsx dx, byte [es:bx + 0x6E]
        cmp ax, dx
        jle .imp
        mov ax, dx
.imp:   xchg dx, ax                     ; (DX the improvement)
        pop ax                          ; (the creature)
        mov bx, cx
        cmp cx, SAVE_ROGUES
        jne .group
        imul ax, ax, %2                 ; the rogues: the sheet's thief and psionicist levels
        les bx, [%1]
        add bx, ax
        xor ax, ax                      ; (AL the thief's, AH the psionicist's)
        mov cx, 3
.cls:   cmp byte [es:bx + %3], SAVE_THIEF
        jne .psi
        cmp al, [es:bx + %4]
        jae .next
        mov al, [es:bx + %4]
        jmp .next
.psi:   cmp byte [es:bx + %3], SAVE_PSIONICIST
        jne .next
        cmp ah, [es:bx + %4]
        jae .next
        mov ah, [es:bx + %4]
.next:  inc bx
        loop .cls
        or ax, ax
        jnz .some
        mov ax, di                      ; (neither: the group's level, as a thief)
.some:  mov ds, [cs:tail_seg]
        mov cl, 0x7F
        or al, al
        jz .psis
        push ax
        movzx di, al
        mov bx, SAVE_ROGUES
        call band_save
        mov cl, al
        pop ax
.psis:  or ah, ah
        jz .sum
        movzx di, ah
        mov bx, SAVE_PSI_SET
        call band_save
        cmp al, cl
        jge .sum
        mov cl, al
        jmp .sum
.group: mov ds, [cs:tail_seg]
        call band_save
        mov cl, al
.sum:   mov al, cl                      ; the Handbook's, and the game's improvement
        add al, dl
        inc word [cs:save_count]
        pop es
        pop ds
        pop di
        pop si
        pop dx
        pop cx
        pop bx
.out:   iret
save_count dw 0                         ; (saves worked out with the tables, for a look in play)
; BAND_SAVE: AL save SI of SAVE_BANDS' set BX (0-4) at level DI (DS:save_bands): the last band whose
; first level is DI's or below. BX lost; others kept.
band_save:
        push cx
        mov cx, bx
        inc cx
        mov bx, save_bands - SAVE_BAND
.set:   add bx, SAVE_BAND               ; (to set BX's first band: each set's begins with level 1)
        cmp byte [bx], 1
        jne .set
        loop .set
.band:  mov al, [bx + si + 1]
        add bx, SAVE_BAND
        cmp bx, save_bands_end
        jae .got
        movzx cx, byte [bx]
        cmp cx, 1
        je .got                         ; (the next set's)
        cmp di, cx
        jge .band
.got:   pop cx
        ret
%endmacro

%macro SAVE_BANDS_DATA 0
save_bands:
        db 1, 10, 14, 13, 16, 15,  4, 9, 13, 12, 15, 14,  7, 7, 11, 10, 13, 12,  10, 6, 10, 9, 12, 11  ; priests
        db 13, 5, 9, 8, 11, 10,  16, 4, 8, 7, 10, 9,  19, 2, 6, 5, 8, 7
        db 1, 14, 16, 15, 17, 17,  3, 13, 15, 14, 16, 16,  5, 11, 13, 12, 13, 14,  7, 10, 12, 11, 12, 13  ; warriors
        db 9, 8, 10, 9, 9, 11,  11, 7, 9, 8, 8, 10,  13, 5, 7, 6, 5, 8,  15, 4, 6, 5, 4, 7,  17, 3, 5, 4, 4, 6
        db 1, 14, 11, 13, 15, 12,  6, 13, 9, 11, 13, 10,  11, 11, 7, 9, 11, 8,  16, 10, 5, 7, 9, 6  ; wizards
        db 21, 8, 3, 5, 7, 4
        db 1, 13, 14, 12, 16, 15,  5, 12, 12, 11, 15, 13,  9, 11, 10, 10, 14, 11,  13, 10, 8, 9, 13, 9  ; thieves
        db 17, 9, 6, 8, 12, 7,  21, 8, 4, 7, 11, 5
        db 1, 13, 15, 10, 16, 15,  5, 12, 13, 9, 15, 14,  9, 11, 11, 8, 13, 12,  13, 10, 9, 7, 12, 11  ; psionicists
        db 17, 9, 7, 6, 11, 9,  21, 8, 5, 5, 9, 7
save_bands_end:
%endmacro
