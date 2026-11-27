org 100h
  mov ax,13h
  int 10h
  mov dx,3C4h
  mov ax,0604h
  out dx,ax
  mov dx,3D4h
  mov ax,0014h
  out dx,ax
  mov ax,0E317h
  out dx,ax
  mov ax,4838h
  out dx,ax
  mov ax,0A539h
  out dx,ax
  mov ax,0A000h
  mov es,ax
  mov byte [base],32
  call draw            ; planar picture, vertical stripes
  call key
  ; step 1: S3 enhanced 8bpp display: CR31 bit3, CR3A bit4, pitch 320 bytes
  mov dx,3D4h
  mov al,31h
  out dx,al
  inc dx
  in al,dx
  or al,08h
  out dx,al
  dec dx
  mov al,3Ah
  out dx,al
  inc dx
  in al,dx
  or al,10h
  out dx,al
  dec dx
  mov ax,2813h          ; offset 40 -> 320 bytes (x8)
  out dx,ax
  call key
  ; step 2: planar-style draw again (different colours) while in enhanced
  mov byte [base],48
  call draw
  call key
  ; step 3: bank 4 (256K), write a chunky band block; then show from 256K
  mov dx,3D4h
  mov ax,046Ah
  out dx,ax
  xor di,di
  mov cx,64000
f:mov ax,di
  xor dx,dx
  mov bx,320
  div bx
  shr ax,3
  add al,40
  stosb
  loop f
  mov dx,3D4h
  mov ax,006Ah
  out dx,ax
  ; display start = 256K bytes: in dword units? set CR69 = 1 (bit16 of start addr)
  mov ax,0169h
  out dx,ax
  call key
  mov ax,3
  int 10h
  int 20h
draw:                    ; planar: x 0..319, y 0..199
  xor bx,bx
.y: xor cx,cx
.x: mov ax,cx
  mov dl,20
  div dl
  add al,[base]
  mov si,ax
  mov ax,bx
  mov dl,25
  div dl
  or ah,ah
  jnz .a
  mov si,15
.a: cmp cx,bx
  jne .b
  mov si,4
.b: mov ah,1
  push cx
  and cl,3
  shl ah,cl
  pop cx
  mov al,2
  mov dx,3C4h
  out dx,ax
  mov ax,bx
  mov dx,80
  mul dx
  mov di,cx
  shr di,2
  add di,ax
  mov ax,si
  mov [es:di],al
  inc cx
  cmp cx,320
  jb .x
  inc bx
  cmp bx,200
  jb .y
  ret
key: xor ax,ax
  int 16h
  ret
base db 0
