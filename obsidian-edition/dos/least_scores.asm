; DSUN.EXE 67399h (104 bytes, overlay code): the least a score may be at creation, for ability
; [BP+8] (0 STR .. 5 CHA) of a character whose first [BP+6] classes are the creation sheet's
; (+21h, 1-8: cleric, druid, fighter, gladiator, preserver, psionicist, ranger, thief): the
; highest of its classes' requirements in the manual, 3 for none. The game's raised a class's
; one prime requisite to 17 and every other score to one number a class (its table at 338h:180h,
; which the change of class still reads). The two "mov dx,338h" stay where the game has them
; (+1Eh, +42h): the overlay manager fixes up their segment as it loads the code.
bits 16
        push bp
        mov bp, sp
        push si
        mov cl, [bp+8]
        shl cl, 2               ; the ability's nibble
        mov ch, 3               ; the least so far: 3, none
        mov bp, [bp+6]          ; the classes (the caller's BP comes back below)
        call .here
.here:  pop si                  ; (where the code runs)
.next:  dec bp
        js .done
        les bx, [0x119C]
        add bx, bp
        times 0x1E - ($ - $$) nop
        mov dx, 0x338           ; (the game's, kept: its segment is fixed up as the overlay loads)
        mov al, [es:bx+0x21]    ; the class, 1-8
        cbw
        imul bx, ax, 3
        mov eax, [cs:bx+si+table-3-.here]
        shr eax, cl
        and al, 0x0F
        cmp al, ch
        jbe .next
        mov ch, al
        jmp short .next
.done:  mov al, ch
        cbw
        pop si
        pop bp
        retf
        times 0x42 - ($ - $$) nop
        mov dx, 0x338           ; (the game's second, kept; never run)
table:                          ; classes 1-8, three bytes each: six nibbles (STR first), the least (0 none)
%include "least_scores_table.inc"
        times 0x68 - ($ - $$) nop
