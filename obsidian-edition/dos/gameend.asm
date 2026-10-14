; GAMEEND.COM: run after the game. If the game stopped with an error (a message such as "Null
; pointer assignment" left on the screen, a non-zero return code, or the screen left in graphics
; mode), the screen's text and the code are saved to GAMEEND.TXT next to this file (for the
; Loader's crash report) and the message stays on screen until a key is pressed (in text mode, if
; the game left the screen in graphics, where it couldn't be read); otherwise
; nothing (DOSBox closes as before).
; Build: nasm -f bin -o dos/GAMEEND.COM dos/gameend.asm

COLS    equ 80
ROWS    equ 25

        org 100h
        mov ah, 4Dh                     ; the last program's (the game's) return code
        int 21h
        mov [code], al
        mov ah, 0Fh                     ; the video mode
        int 10h
        mov [mode], al
        mov word [screen], 0B800h
        cmp al, 7
        jne .colour
        mov word [screen], 0B000h
        jmp .scan
.colour:
        cmp al, 3
        ja .error                       ; still in graphics: no text to read
.scan:
        push ds
        mov ds, [screen]
        xor si, si
        mov cx, COLS * ROWS
.char:
        lodsw
        cmp al, ' '
        ja .found
        loop .char
        pop ds
        cmp byte [code], 0
        jne .error
        mov ax, 4C00h                   ; ended as usual
        int 21h
.found:
        pop ds
        mov byte [text], 1
.error:
        call save
        cmp byte [mode], 7              ; still in graphics: back to text, for the message to be read
        je .text
        cmp byte [mode], 3
        jbe .text
        mov ax, 0003h
        int 10h
.text:
        mov ah, 09h
        mov dx, said
        int 21h
        xor ah, ah                      ; wait for a key
        int 16h
        mov ax, 4C01h
        int 21h

; GAMEEND.TXT, beside this program (D:, the Loader's dos folder): the code, the mode, then the
; screen's rows (trailing spaces trimmed, blank rows at the end left out)
save:
        mov ah, 3Ch
        xor cx, cx
        mov dx, fname
        int 21h
        jc .done
        mov [handle], ax
        mov al, [code]
        mov di, head_code
        call hex2
        mov al, [mode]
        mov di, head_mode
        call hex2
        mov dx, head
        mov cx, head_end - head
        call write
        cmp byte [text], 0
        je .close
        mov bx, ROWS                    ; the last row with text
.last:
        dec bx
        mov ax, bx
        call row_len
        or cx, cx
        jz .last
        inc bx
        mov [rows], bx
        xor bx, bx
.row:
        mov ax, bx
        call row_len                    ; CX characters, from row BX
        mov di, line
        jcxz .end
        push ds
        mov ds, [cs:screen]
        mov ax, bx
        mov dx, COLS * 2
        mul dx
        mov si, ax
        push cx
.copy:
        lodsw
        stosb
        loop .copy
        pop cx
        pop ds
.end:
        mov ax, 0A0Dh
        stosw
        add cx, 2
        mov dx, line
        call write
        inc bx
        cmp bx, [rows]
        jb .row
.close:
        mov bx, [handle]
        mov ah, 3Eh
        int 21h
.done:
        ret

; CX = row AX's length without trailing spaces
row_len:
        push ds
        push si
        mov ds, [cs:screen]
        mov dx, COLS * 2
        mul dx
        mov si, ax
        add si, COLS * 2 - 2
        mov cx, COLS
.back:
        cmp byte [si], ' '
        ja .got
        sub si, 2
        loop .back
.got:
        pop si
        pop ds
        ret

; write CX bytes at DS:DX to the file
write:
        push bx
        mov bx, [handle]
        mov ah, 40h
        int 21h
        pop bx
        ret

; AL as two hex digits at DI
hex2:
        mov ah, al
        shr al, 4
        call .digit
        mov al, ah
        and al, 0Fh
.digit:
        add al, '0'
        cmp al, '9'
        jbe .put
        add al, 'A' - '9' - 1
.put:
        stosb
        ret

said    db 13, 10, "The game stopped with an error. The Loader saves what is on the screen", 13, 10
        db "in its crash report. Press a key to close DOSBox.$"
fname   db "D:\GAMEEND.TXT", 0
head    db "Return code "
head_code db "00h, video mode "
head_mode db "00h", 13, 10
head_end:
code    db 0
mode    db 0
text    db 0
screen  dw 0
handle  dw 0
rows    dw 0
line    times COLS + 2 db 0
