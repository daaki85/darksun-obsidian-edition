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
  ; S3 unlock
  mov ax,4838h
  out dx,ax
  mov ax,0A539h
  out dx,ax
  mov ax,0A000h
  mov es,ax
  ; bank 0: vertical stripes (colour = x/4/5+32 per byte, all planes)
  mov dx,3C4h
  mov ax,0F02h
  out dx,ax
  xor di,di
  mov cx,64000
b0: mov ax,di
  xor dx,dx
  mov bx,80
  div bx          ; dx = column byte
  mov ax,dx
  mov bl,5
  div bl
  add al,32
  stosb
  loop b0
  ; bank 1: horizontal bands (colour by row)
  mov dx,3D4h
  mov ax,016Ah
  out dx,ax
  xor di,di
  mov cx,64000
b1: mov ax,di
  xor dx,dx
  mov bx,80
  div bx          ; ax = row
  shr ax,3
  add al,40
  stosb
  loop b1
  mov dx,3D4h
  mov ax,006Ah
  out dx,ax
  call key
  ; step 1: display start = 64K (CR69 bit 0 = start addr bit 16)
  mov dx,3D4h
  mov ax,0169h
  out dx,ax
  call key
  ; step 2: back to 0, widen to 640 (pitch 160 bytes)
  mov ax,0069h
  out dx,ax
  mov ax,0E11h      ; unprotect CR0-7
  out dx,ax
  mov ax,0C300h
  out dx,ax
  mov ax,9F01h
  out dx,ax
  mov ax,0A002h
  out dx,ax
  mov ax,8203h
  out dx,ax
  mov ax,0A804h
  out dx,ax
  mov ax,0005h
  out dx,ax
  mov ax,5013h
  out dx,ax
  call key
  mov ax,3
  int 10h
  int 20h
key: xor ax,ax
  int 16h
  ret
