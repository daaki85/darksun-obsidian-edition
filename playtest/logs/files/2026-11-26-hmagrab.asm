; HMAGRAB.COM: a test stand-in for "something else has the HMA": asks XMS for it (01h), prints the
; answer, turns A20 on (03h) and writes a marker at FFFF:0010 (as a DOS kernel or TSR there would).
        org 100h
        mov ax, 4300h
        int 2Fh
        cmp al, 80h
        jne none
        mov ax, 4310h
        int 2Fh
        mov [xms], bx
        mov [xms+2], es
        mov ah, 1
        mov dx, 0FFFFh
        call far [xms]
        mov [r01], ax
        mov [r01+2], bl
        mov ah, 3
        call far [xms]
        mov [r03], ax
        mov ax, 0FFFFh
        mov es, ax
        mov di, 10h
        mov si, mark
        mov cx, 16
        cld
        rep movsb
        mov al, [r01]
        call hex
        mov [o1], ax
        mov al, [r01+2]
        call hex
        mov [o2], ax
        mov al, [r03]
        call hex
        mov [o3], ax
        mov dx, msg
        mov ah, 9
        int 21h
        mov ax, 4C00h
        int 21h
none:   mov dx, nox
        mov ah, 9
        int 21h
        mov ax, 4C01h
        int 21h
hex:    mov ah, al
        shr al, 4
        and ah, 0Fh
        add al, '0'
        cmp al, '9'
        jbe .a
        add al, 7
.a:     add ah, '0'
        cmp ah, '9'
        jbe .b
        add ah, 7
.b:     ret
xms     dd 0
r01     dw 0
        db 0
r03     dw 0
mark    db 'HMA TAKEN (TEST)'
msg     db 'HMAGRAB: XMS 01h AX='
o1      dw 0
        db ' BL='
o2      dw 0
        db ', 03h AX='
o3      dw 0
        db 13, 10, '$'
nox     db 'HMAGRAB: no XMS', 13, 10, '$'
