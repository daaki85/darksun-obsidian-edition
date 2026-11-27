org 100h
  mov ax,13h
  int 10h
  ; mode X: unchain
  mov dx,3C4h
  mov ax,0604h
  out dx,ax
  mov dx,3D4h
  mov ax,0014h
  out dx,ax
  mov ax,0E317h
  out dx,ax
  mov ax,0A000h
  mov es,ax
  ; draw 320x200: colour = stripe x/20 + 32 ; white line each 25 rows, black every 50th col
  xor bx,bx            ; y
yl: xor cx,cx          ; x
xl: mov ax,cx
  push cx
  mov dl,20
  div dl
  add al,32
  mov ah,al
  mov ax,bx
  mov dl,25
  div dl
  or ah,ah
  jnz .n1
  mov ah,15
  jmp .put
.n1: mov ax,cx
  mov dl,20
  div dl
  add al,32
  mov ah,al
  ; diagonal mark
  mov ax,cx
  sub ax,bx
  jnz .n2
  mov ah,4
  jmp .put
.n2: mov ax,cx
  mov dl,20
  div dl
  add al,32
  mov ah,al
.put:
  pop cx
  push ax
  mov al,1
  push cx
  and cl,3
  shl al,cl
  pop cx
  mov dx,3C4h
  mov ah,al
  mov al,2
  out dx,ax
  ; addr = y*80 + x/4
  mov ax,bx
  mov dx,80
  mul dx
  mov di,cx
  shr di,2
  add di,ax
  pop ax
  mov [es:di],ah
  inc cx
  cmp cx,320
  jb xl
  inc bx
  cmp bx,200
  jb yl
  call key
  ; step 1: vertical x2 (max scan line 1 -> 3)
  mov dx,3D4h
  mov ax,4309h
  out dx,ax
  call key
  ; step 2: horizontal x2 (sequencer clocking mode bit 3)
  mov dx,3C4h
  mov ax,0100h
  out dx,ax
  mov al,1
  out dx,al
  inc dx
  in al,dx
  or al,8
  out dx,al
  dec dx
  mov ax,0300h
  out dx,ax
  call key
  ; step 3: pan: start address = 50 rows down + 40 pixels right = 50*80+10
  mov dx,3D4h
  mov bx,50*80+10
  mov al,0Ch
  mov ah,bh
  out dx,ax
  mov al,0Dh
  mov ah,bl
  out dx,ax
  call key
  mov ax,3
  int 10h
  int 20h
key: xor ax,ax
  int 16h
  ret
