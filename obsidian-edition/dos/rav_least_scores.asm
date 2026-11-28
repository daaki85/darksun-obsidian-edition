; Wake of the Ravager's DSUN.EXE 6F12Dh (106 bytes, overlay code): Shattered Lands' least_scores.asm at the
; sequel's addresses. The same routine (ability [BP+8], the creation sheet's first [BP+6] classes, 1-8 as
; Shattered Lands'), its sheet at far DS:1429h with the classes at +1Bh, the game's table at 360h:153h; the
; game's two "mov dx,360h" at +1Fh and +44h (its "mov ah,0" a byte longer than SL's "cbw").
%define SHEET_PTR 0x1429
%define CLASS_AT 0x1B
%define GAME_SEG 0x360
%define FIX_1 0x1F
%define FIX_2 0x44
%define SIZE 0x6A
%include "least_scores.asm"
