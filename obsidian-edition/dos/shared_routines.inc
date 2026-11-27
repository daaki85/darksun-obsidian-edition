; shared_routines.inc: the routines DSCLOG (Shattered Lands') and DSCLOG2 (Wake of the Ravager's)
; have the same, line for line, each a macro that its helper expands where the routine belongs
; (SHARED name). A fix here reaches both helpers; the rebuild checks prove the bytes unchanged.
; What each routine does is said where it is expanded.

%macro SHARED_abs16 0
abs16:  or ax, ax
        jns .pos
        neg ax
.pos:   ret
%endmacro

%macro SHARED_c_cells 0
c_cells:
        push es
        push si
        push di
        xor si, si
.cell:  push cx
        push bx
        push word [cs:bx + 2]   ; y
        push word [cs:bx]       ; x
        push cs
        push word [cs:bx + 4]   ; the label
        call c_draw_line
        pop bx
        push bx
        mov al, [cs:c_vals + si]
        mov di, c_num
        or si, si
        jnz .unsigned
        cmp byte [cs:c_signed], 0
        je .unsigned
        call c_itoa_s           ; the first cell of THAC0 and the saves
        jmp .number
.unsigned:
        call c_itoa
.number:
        push word [cs:bx + 2]
        push word [cs:bx + 6]   ; the value's x
        push cs
        push word c_num
        call c_draw_line
        pop bx
        pop cx
        add bx, 8
        inc si
        loop .cell
        pop di
        pop si
        pop es
        ret
%endmacro

%macro SHARED_c_cells_top 0
c_cells_top:
        dw 0xEC, 0x0D, l_thac0, 0x111
        dw 0xEC, 0x14, l_ppd, 0x103,  0x113, 0x14, l_rsw, 0x12A
        dw 0xEC, 0x1B, l_pp, 0x103,   0x113, 0x1B, l_bw, 0x12A
        dw 0xEC, 0x22, l_sp, 0x103
%endmacro

%macro SHARED_c_itoa 0
c_itoa:                         ; AL (unsigned) -> decimal at CS:DI, NUL-terminated; keeps BX, CX
        push bx
        push cx
        xor ah, ah
        mov bl, 10
        xor cx, cx
.div:   div bl
        push ax                 ; AH = a digit
        inc cx
        xor ah, ah
        or al, al
        jnz .div
.put:   pop ax
        add ah, '0'
        mov [cs:di], ah
        inc di
        loop .put
        mov byte [cs:di], 0
        pop cx
        pop bx
        ret
%endmacro

%macro SHARED_c_itoa_s 0
c_itoa_s:                       ; AL (signed) -> decimal at CS:DI, with "-" below 0; keeps BX, CX
        test al, al
        jns c_itoa
        mov byte [cs:di], '-'
        inc di
        neg al
        jmp c_itoa
%endmacro

%macro SHARED_cr_is_back 0
cr_is_back:
        pop es
        pop bx
        ret
%endmacro

%macro SHARED_dust_build 0
dust_build:
        pusha
        push es
        mov es, [cs:far_seg]
        mov di, FAR_DUST
        xor bx, bx                      ; BX: the age
.age:   mov si, bx
        shl si, 1
        mov [cs:d_blocks + si], di
        mov ax, bx                      ; across, and up and down (as PUFF_DRAW)
        shl ax, 3
        xor dx, dx
        mov cx, DUST_LIFE
        div cx
        add ax, 3
        mov [cs:d_rx], ax
        imul ax, ax, 9
        add ax, 8
        shr ax, 4
        mov [cs:d_ry], ax
        mov al, [cs:dust_dens + bx]
        xor ah, ah
        mov [cs:d_dens], ax
        mov al, [cs:dust_core + bx]
        mov [cs:d_core], ax
        push bx
        mov cx, [cs:d_rx]               ; how far out it is across, (x / rx)^2 of 256, by |x|
        imul cx, cx
        xor si, si
.tab:   mov ax, si
        imul ax, ax
        shl ax, 8
        xor dx, dx
        div cx
        mov bx, si
        shl bx, 1
        mov [cs:d_extab + bx], ax
        inc si
        cmp si, [cs:d_rx]
        jbe .tab
        mov word [cs:d_yy], 0
.row:   mov ax, [cs:d_yy]               ; how far out it is, up and down: (y / ry)^2, of 256
        imul ax, ax
        shl ax, 8
        mov cx, [cs:d_ry]
        imul cx, cx
        xor dx, dx
        div cx
        mov [cs:d_ey], ax
        mov word [cs:d_xmax], -1        ; (the widest |x| inside, on this row)
        xor si, si
.thr:   mov bx, si
        shl bx, 1
        mov ax, [cs:d_extab + bx]       ; and across
        add ax, [cs:d_ey]
        mov word [cs:d_thrcore + bx], 0
        cmp ax, 256
        ja .nthr
        mov [cs:d_xmax], si
        cmp ax, [cs:d_core]
        setb byte [cs:d_thrcore + bx + 1]
        imul ax, ax, 154                ; thinner toward the edge
        shr ax, 8
        neg ax
        add ax, 256
        mul word [cs:d_dens]
        shr ax, 8
        mov [cs:d_thrcore + bx], al
.nthr:  inc si
        cmp si, [cs:d_rx]
        jbe .thr
        mov ax, [cs:d_xmax]             ; the row: the widest |x|, then x from -RX to RX
        stosw
        mov si, [cs:d_rx]
        neg si
.put:   mov bx, si
        or bx, bx
        jns .abs
        neg bx
.abs:   shl bx, 1
        mov ax, [cs:d_thrcore + bx]
        stosw
        inc si
        cmp si, [cs:d_rx]
        jle .put
        inc word [cs:d_yy]
        mov ax, [cs:d_yy]
        cmp ax, [cs:d_ry]
        jbe .row
        pop bx
        inc bx
        cmp bx, DUST_LIFE
        jb .age
        mov byte [cs:d_built], 1
        pop es
        popa
        ret
%endmacro

%macro SHARED_dust_nudge 0
dust_nudge:
        mov ax, [CAM_X]                 ; (the view: when it last moved)
        cmp ax, [cs:d_cam_x]
        jne .cam
        mov ax, [CAM_Y]
        cmp ax, [cs:d_cam_y]
        je .still
.cam:   mov ax, [CAM_X]
        mov [cs:d_cam_x], ax
        mov ax, [CAM_Y]
        mov [cs:d_cam_y], ax
        mov ax, [cs:d_now]
        mov [cs:d_walked_at], ax
        ret
.still: cmp byte [cs:d_dirty], 0
        je .ret
        mov ax, [cs:d_now]
        sub ax, [cs:d_walked_at]
        cmp ax, STILL_TICKS
        jb .ret
        mov ax, [cs:d_now]
        sub ax, [cs:d_nudged]
        cmp ax, NUDGE_TICKS
        jb .ret
        mov ax, [cs:d_now]
        mov [cs:d_nudged], ax
        mov byte [cs:d_dirty], 0
        mov ax, [cs:d_x0]
        sub ax, [CAM_X]
        mov cx, [cs:d_x1]
        sub cx, [CAM_X]
        mov bx, [cs:d_y0]
        sub bx, [CAM_Y]
        mov dx, [cs:d_y1]
        sub dx, [CAM_Y]
        cmp cx, 0                       ; (off screen: nothing)
        jl .ret
        cmp ax, 0x13F
        jg .ret
        cmp dx, 0
        jl .ret
        cmp bx, 0xC7
        jg .ret
        or ax, ax
        jge .x0
        xor ax, ax
.x0:    and ax, 0xFFFC                  ; (whole bytes of the planes, as LABEL_ERASE)
        cmp cx, 0x13F
        jle .x1
        mov cx, 0x13F
.x1:    or cx, 3
        or bx, bx
        jge .y1
        xor bx, bx
.y1:    cmp dx, 0xC7
        jle .rect
        mov dx, 0xC7
.rect:  call redraw_rect
.ret:   ret
%endmacro

%macro SHARED_dust_pass 0
dust_pass:
        cmp word [cs:dust_on], 0
        je .ret
        push ds
        xor ax, ax
        mov ds, ax
        mov ax, [BIOS_TICKS]
        pop ds
        mov [cs:d_now], ax
        cmp byte [cs:d_built], 0
        jne .built
        call dust_build
.built: mov si, FAR_PUFFS
        mov cx, PUFFS
.puff:  cmp byte [fs:si + 10], 0
        je .next
        push cx
        push si
        call puff_draw
        pop si
        pop cx
.next:  add si, PUFF_SIZE
        loop .puff
.ret:   ret
%endmacro

%macro SHARED_ef_put 0
ef_put:
        pusha
        push es
        cmp word [cs:ef_y], USE_FIRST_Y + (EF_LINES - 1) * USE_STEP
        ja .out
        push word [cs:ef_y]
        push word USE_X
        push cs
        push si
        call c_draw_line
.out:   add word [cs:ef_y], USE_STEP
        pop es
        popa
        ret
%endmacro

%macro SHARED_healer_barred 0
healer_barred:
        push ax
        shl al, 2
        add al, dl
        cmp al, KIT_HEALER
        pop ax
        jne .ok
        cmp word [WP_SPHERE_MASK], HEALER_SPHERE_MASK
        je .ok
        stc
        ret
.ok:    clc
        ret
%endmacro

%macro SHARED_held_hit 0
held_hit:
        push ax
        push bx
        mov bx, sp                  ; ([BX+8] the INT's flags)
        and word [ss:bx + 8], ~0x40
        cmp word [bp - 6], 20
        je .hit
        call held_now
        jnc .out
.hit:   or word [ss:bx + 8], 0x40   ; (ZF: the game's JE to the hit)
.out:   pop bx
        pop ax
        iret
%endmacro

%macro SHARED_int_rand 0
int_rand:
        add sp, 4
        popf
%endmacro

%macro SHARED_kit_bans 0
kit_bans:
        push si
        xor edx, edx
        or al, al
        jz .out
        mov si, dual_bans
.next:  cmp byte [cs:si], 0
        je .out
        cmp [cs:si], al
        je .kit
        add si, 5
        jmp .next
.kit:   mov edx, [cs:si + 1]
.out:   pop si
        ret
%endmacro

%macro SHARED_kit_find 0
kit_find:
        push di
        push cx
        mov ch, al
        call kit_place          ; (DI the oldest class's place)
        jc .no
.place: call kit_at
        cmp al, ch
        jne .next
        or si, si
        jz .yes
        call kit_awake
        jnc .yes
.next:  dec di
        jns .place
.no:    mov al, ch
        or ch, 1                ; (ZF clear)
        jmp .out
.yes:   mov [cs:kit_where], di
        cmp al, al              ; (ZF set)
.out:   pop cx
        pop di
        pop si
        ret
%endmacro

%macro SHARED_kit_has 0
kit_has:
        push si
        xor si, si
%endmacro

%macro SHARED_kit_is 0
kit_is:
        push si
        mov si, 1
        jmp kit_find
%endmacro

%macro SHARED_kit_is_b 0
kit_is_b:
        push bp
        mov bp, sp
        push si
        push ax
        mov si, [bp + 2]
        cmp si, cr_is_back      ; (from CR_IS: the byte after the call to it)
        jne .byte
        mov si, [bp + 8]
        inc word [bp + 8]
        jmp .is
.byte:  inc word [bp + 2]
.is:    mov al, [cs:si]
        call kit_is
        pop ax
        pop si
        pop bp
        ret
%endmacro

%macro SHARED_kit_open 0
kit_open:
        call wp_close_panel
        call kit_class
        movzx ax, al
        add ax, KIT_WIN_ID - 1
        mov si, kit_title
        call wp_show
        call kit_marks
        jmp wp_help_line
%endmacro

%macro SHARED_kit_pair 0
kit_pair:
        push dx
        push si
        mov dx, ax
        xchg dl, dh
        mov si, kit_pairs
.next:  cmp word [cs:si], 0
        je .free
        cmp [cs:si], ax
        je .barred
        cmp [cs:si], dx
        je .barred
        add si, 2
        jmp .next
.free:  clc
        jmp .out
.barred:
        stc
.out:   pop si
        pop dx
        ret
%endmacro

%macro SHARED_label_adopt 0
label_adopt:
        mov [cs:si + LS_SEEN], dl
        mov [cs:si + LS_X], ax
        mov [cs:si + LS_Y], bx
        mov ax, [fs:di + 1]
        mov [cs:si + LS_W], ax          ; (and LS_H)
        mov byte [cs:si + LS_SHOWN], 1
        ret
%endmacro

%macro SHARED_learn_back 0
learn_back:
        push word [cs:lm_fl]
        push word [cs:lm_cs]
        push word [cs:lm_ip]
        iret
%endmacro

%macro SHARED_map_key 0
map_key:
        push bx
        mov bl, 'm'
        cmp ax, KEY_M
        je .key
        cmp ax, KEY_SHIFT_M
        je .key
        mov bl, 'u'
        cmp ax, KEY_U
        je .key
        cmp ax, KEY_SHIFT_U
        je .key
        mov bl, 'i'
        cmp ax, KEY_I
        je .key
        cmp ax, KEY_SHIFT_I
        je .key
        cmp byte [cs:overhead], 'm'     ; another key: the overhead map's are its own
        je .ret
        cmp byte [cs:mk_read], 0
        je .ret
        mov byte [cs:overhead], 0
        jmp .ret
.key:   push ax
        push es
        xor ax, ax
        mov es, ax
        mov ax, [es:0x46C]
        sub ax, [cs:map_tick]
        pop es
        cmp ax, L_FRESH
        pop ax
        ja .up
        call on_map
        jne .ret
        cmp byte [cs:mk_read], 0
        je .fresh
        mov [cs:overhead], bl
.fresh: cmp bl, 'm'
        jne .ret
        mov ax, KEY_O
        jmp .ret
.up:    cmp [cs:overhead], bl
        jne .other
        mov ax, KEY_ESCAPE
        jmp .ret
.other: cmp bl, 'm'
        je .ret
        cmp byte [cs:overhead], 'u'     ; (U on the inventory, I on USE: the game switches)
        je .move
        cmp byte [cs:overhead], 'i'
        jne .ret
.move:  cmp byte [cs:mk_read], 0
        je .ret
        mov [cs:overhead], bl
.ret:   pop bx
        ret
%endmacro

%macro SHARED_multi_group 0
multi_group:
        push si
        mov si, kit_class_of
        jmp multi_find
%endmacro

%macro SHARED_multi_group_cr 0
multi_group_cr:
        push si
        mov si, multi_same
%endmacro

%macro SHARED_next_die 0
next_die:
        push si
        mov si, die_sizes
.next:  cmp ax, [cs:si]
        jb .got
        add si, 2
        cmp si, die_sizes_end
        jb .next
        pop si
        ret
.got:   mov ax, [cs:si]
        pop si
        ret
%endmacro

%macro SHARED_on_map 0
on_map:
        push es
        push ax
        mov ax, [cs:pointer_ds]
        cmp ax, 1                       ; (not known yet: ZF clear)
        jb .out
        mov es, ax
        cmp word [es:SCREEN_IS], 1
.out:   pop ax
        pop es
        ret
%endmacro

%macro SHARED_panel_draw_around 0
panel_draw_around:
        cmp word [POINTER_HIDE], 0
        jne .whole
        cmp word [POINTER_KIND], -1
        je .whole
        push ax
        mov ax, [POINTER_WAS]
        sar ax, 2
        mov [cs:pb_sx0], ax
        add ax, POINTER_MOST / 4 + 1
        mov [cs:pb_sx1], ax
        mov ax, [POINTER_WAS + 2]
        mov [cs:pb_sy0], ax
        add ax, POINTER_MOST
        mov [cs:pb_sy1], ax
        pop ax
        mov byte [cs:pb_skip], 1
        call panel_draw
        mov byte [cs:pb_skip], 0
        ret
.whole: jmp panel_draw
%endmacro

%macro SHARED_panel_live 0
panel_live:
        cmp byte [cs:panel_shown], 0
        je .no
        push es
        push ax
        mov es, [cs:panel_pseg]
        mov ax, [es:SHOWN_PAGE]
        cmp ax, [cs:panel_page]
        pop ax
        pop es
        jne .ret
        call on_map
.ret:   ret
.no:    cmp sp, 0                       ; (ZF clear)
        ret
%endmacro

%macro SHARED_pf_mark 0
pf_mark:                                ; BX a slot (any word): its bit in PF_USED
        cmp bx, CACHE_MOST
        jae .out
        bts word [cs:pf_used], bx
.out:   ret
%endmacro

%macro SHARED_pk_ops 0
pk_ops:
        pusha
        push es
        xor si, si
.row:   xor ax, ax
        bt [cs:lv_avail], si
        jc .op
        inc ax
.op:    push ax
        push word 0
        lea bx, [si + PICK_FIRST]
        push bx
        push dword [PK_WINDOW]
        call far [cs:lv_op_call]
        add sp, 10
        inc si
        cmp si, KIND_COUNT
        jb .row
        pop es
        popa
        ret
%endmacro

%macro SHARED_pointer_panel 0
pointer_panel:
        cmp byte [cs:pointer_busy], 0
        jne .ret
        cmp word [POINTER_HIDE], 0
        jne .ret
        call panel_live
        jne .ret
        push si
        mov si, POINTER_XY
        call pointer_over
        je .draw
        mov si, POINTER_WAS
        call pointer_over
        jne .out
.draw:  call panel_draw
.out:   pop si
.ret:   ret
%endmacro

%macro SHARED_pp_disarm 0
pp_disarm:
        cmp byte [cs:pp_armed], 0
        je .ret
        cmp word [POINTER_MODE], TALK_MODE
        je .ret
        mov byte [cs:pp_armed], 0
.ret:   ret
%endmacro

%macro SHARED_pp_extras 0
pp_extras:
        xor si, si
.slot:  mov al, [cs:si + pp_extra]
        or al, al
        jz .hide
        call pp_extra_draw
        jmp .next
.hide:  cmp byte [cs:si + pp_extra_on], 0
        je .next
        call pp_extra_hide
.next:  inc si
        cmp si, EXTRA_MOST
        jb .slot
        ret
%endmacro

%macro SHARED_pp_keep 0
pp_keep:
        push ax
        push bx
        push es
        mov al, [READY_WHO]
        mov [cs:pp_kept_who], al
        mov ax, [READY_ICON]
        mov [cs:pp_kept_icon], ax
        call pp_shown_member
        mov ax, [bx + READY_KIND]
        mov [cs:pp_kept_kind], ax
        pop es
        pop bx
        pop ax
        ret
%endmacro

%macro SHARED_pp_mine 0
pp_mine:
        mov al, [cs:pp_shown]
        push si
        mov si, [ss:bx + 8]
        sub si, SECOND_ID
        cmp si, EXTRA_MOST
        jae .ret
        mov al, [cs:si + pp_extra]
.ret:   pop si
        ret
%endmacro

%macro SHARED_pp_put 0
pp_put:
        cmp di, -1
        jne .extra
        mov [cs:pp_shown], al
        mov word [TU_ELEMENT], PP_ELEMENT
        movzx ax, al
        add ax, PP_ICON - 1
        mov [TU_ICON], ax
        xor di, di
        ret
.extra: cmp di, EXTRA_MOST
        jae .ret
        mov [cs:di + pp_extra], al
        inc di
.ret:   ret
%endmacro

%macro SHARED_pp_restore 0
pp_restore:
        push ax
        push bx
        push es
        mov al, [cs:pp_kept_who]
        mov [READY_WHO], al
        mov ax, [cs:pp_kept_icon]
        mov [READY_ICON], ax
        call pp_shown_member
        mov ax, [cs:pp_kept_kind]
        mov [bx + READY_KIND], ax
        pop es
        pop bx
        pop ax
        ret
%endmacro

%macro SHARED_probe_floor_all 0
probe_floor_all:
        mov word [cs:floor_frame], 0x1C
        mov byte [cs:floor_kind], 0
        jmp floor_enter
%endmacro

%macro SHARED_probe_floor_rect 0
probe_floor_rect:
        mov word [cs:floor_frame], 0x1E
        mov byte [cs:floor_kind], 1
%endmacro

%macro SHARED_probe_hp_best 0
probe_hp_best:
        test word [cs:rules], RULE_HP_BEST
        jz .game
        cmp byte [cs:hp_again], 0
        jne .second
        mov [cs:hp_first], ax
        mov byte [cs:hp_again], 1
        push bp
        mov bp, sp
        sub word [bp + 2], HP_BEST_BACK ; (the INT's return IP)
        pop bp
        iret
.second:
        mov byte [cs:hp_again], 0
        cmp ax, [cs:hp_first]
        jge .game
        mov ax, [cs:hp_first]
.game:  mov cx, ax
        iret
%endmacro

%macro SHARED_puff_dirty 0
puff_dirty:                             ; the puff at FS:SI: its ground to be drawn again (DS = the game's)
        mov ax, [fs:si]
        sub ax, 12
        mov dx, [fs:si + 2]
        sub dx, 12
        cmp byte [cs:d_dirty], 0
        je .first
        cmp ax, [cs:d_x0]
        jge .x1
.first: mov [cs:d_x0], ax
.x1:    add ax, 24
        cmp byte [cs:d_dirty], 0
        je .fx1
        cmp ax, [cs:d_x1]
        jle .y0
.fx1:   mov [cs:d_x1], ax
.y0:    cmp byte [cs:d_dirty], 0
        je .fy0
        cmp dx, [cs:d_y0]
        jge .y1
.fy0:   mov [cs:d_y0], dx
.y1:    add dx, 19
        cmp byte [cs:d_dirty], 0
        je .fy1
        cmp dx, [cs:d_y1]
        jle .mark
.fy1:   mov [cs:d_y1], dx
.mark:  mov byte [cs:d_dirty], 1
        mov ax, [fs:si + 6]
        mov [cs:d_owner], ax
        ret
%endmacro

%macro SHARED_rec_frame 0
rec_frame:
        pop dx                          ; (the way back)
        mov di, sp
        add si, cx
        add si, cx
.push:  sub si, 2
        push word [cs:si]
        loop .push
        push dword 0
        push bp
        mov bp, sp
        mov si, bp
        sub si, 4                       ; (SS:SI+6: the frame's return address, none)
        call record
        pop bp
        mov sp, di
        jmp dx
%endmacro

%macro SHARED_ring_points 0
ring_points:                            ; CX points at CS:SI round (R_FX, R_FY): each a quarter's
.pt:    push cx                         ;   (x << 3 | y, x and y not negative), with its mirror
        mov al, [cs:si]                 ;   images (x and y each negated, if not 0)
        inc si
        movzx bx, al
        shr bx, 3
        and ax, 7
        mov [cs:r_qx], bx
        mov [cs:r_qy], ax
        call ring_dot                   ; (x, y)
        neg word [cs:r_qx]
        jz .neg_y
        call ring_dot                   ; (-x, y)
.neg_y: neg word [cs:r_qy]
        jz .next
        call ring_dot                   ; (-x, -y), or (0, -y)
        neg word [cs:r_qx]
        jz .next
        call ring_dot                   ; (x, -y)
.next:  pop cx
        loop .pt
        ret
%endmacro

%macro SHARED_rp_choose 0
rp_choose:
        mov [cs:rp_wound], ax
        mov bx, RP_CURES_END - 4
.down:  mov ax, [cs:bx + 2]
        cmp ax, [cs:rp_wound]
        jg .lower
        mov ax, [cs:bx]
        mov [cs:rp_spell], ax
        call rp_find
        jnc .ok
.lower: sub bx, 4
        cmp bx, rp_cures
        jae .down
        mov bx, rp_cures
.up:    mov ax, [cs:bx]
        mov [cs:rp_spell], ax
        call rp_find
        jnc .ok
        add bx, 4
        cmp bx, RP_CURES_END
        jb .up
        stc
.ok:    ret
%endmacro

%macro SHARED_rs_bytes 0
rs_bytes:                       ; CX bytes ES:BX <-> CS:DI (DL 0: into CS:DI)
        mov al, [es:bx]
        or dl, dl
        jz .keep
        mov al, [cs:di]
        mov [es:bx], al
.keep:  mov [cs:di], al
        inc bx
        inc di
        loop rs_bytes
        ret
%endmacro

%macro SHARED_rs_framed 0
rs_framed:
        push bx
        mov bx, sp
        push word [ss:bx + 40]
        push word [ss:bx + 38]
        push bp
        mov bp, sp
        mov dx, [ss:bx + 40]
        call far [cs:wp_far]
        pop bp
        pop ax                  ; the way back, as the overlay manager has left it
        pop dx
        mov bx, sp
        mov [ss:bx + 38], ax
        mov [ss:bx + 40], dx
        pop bx
        ret
%endmacro

%macro SHARED_rtc_begin 0
rtc_begin:
        push ax
        call rtc_second
        mov [cs:w_sec], al
        mov byte [cs:w_flips], 0
        pop ax
        ret
%endmacro

%macro SHARED_rtc_second 0
rtc_second:                             ; AL = the real-time clock's seconds (CMOS register 0)
        pushf
        cli
        mov al, 0
        out 0x70, al
        in al, 0x71
        popf
        ret
%endmacro

%macro SHARED_rtc_waited 0
rtc_waited:                             ; CF set: the wait is over
        push ax
        call rtc_second
        cmp al, [cs:w_sec]
        je .no
        mov [cs:w_sec], al
        inc byte [cs:w_flips]
        cmp byte [cs:w_flips], 2
        jb .no
        pop ax
        stc
        ret
.no:    pop ax
        clc
        ret
%endmacro

%macro SHARED_sgn16 0
sgn16:  or ax, ax                       ; AX -> -1, 0 or 1
        jz .z
        mov ax, 1
        jg .z
        neg ax
.z:     ret
%endmacro

%macro SHARED_shield_not_leather 0
shield_not_leather:
        test byte [cs:cu_flags], 4
        jz .ok
        cmp byte [cs:cu_mat], LEATHER
        je .ok
        stc
        ret
.ok:    clc
        ret
%endmacro

%macro SHARED_spec_any 0
spec_any:
        push eax
        mov eax, [es:bx + SPEC_SLOTS]
        test byte [es:bx + SPEC_SLOTS + 2], SPEC_PACKED
        jz .test                        ; (the old layout: any of the four bytes)
        test byte [es:bx + SPEC_SLOTS + 2], SPEC_V2
        jz .five
        and eax, SPEC_KINDS_MASK
        cmp eax, V3_BASE
        jb .test                        ; (V2's number: none, 0; V3's from V3_BASE, none V3_BASE)
        sub eax, V3_BASE
        jmp .test
.five:  and eax, 0x000FFFFF
.test:  test eax, eax
        pop eax
        ret
%endmacro

%macro SHARED_spec_choose 0
spec_choose:
        push eax
        push ecx
        push si
        mov eax, 1
        movzx ecx, ch
        inc si                          ; (K: SI + 1; the product's steps, C(N, J) * (N - J) / (J + 1))
        xor edx, edx
        push bx
        xor bx, bx
.step:  cmp bx, si
        jae .done
        push edx
        mov edx, ecx
        sub dx, bx
        jbe .zero                       ; (N under K: none)
        imul eax, edx
        pop edx
        push ecx
        movzx ecx, bx
        inc ecx
        xor edx, edx
        div ecx
        pop ecx
        inc bx
        jmp .step
.zero:  pop edx
        xor eax, eax
.done:  pop bx
        mov edx, eax
        pop si
        pop ecx
        pop eax
        ret
%endmacro

%macro SHARED_spec_repack 0
spec_repack:
        push eax
        push ecx
        push edx
        push si
        push di
        mov dword [cs:spec_sorted], 0   ; SPEC_SORTED: the kinds in order, none and a second of one
        xor di, di                      ;   left out (DI how many)
        xor si, si
.copy:  mov al, [cs:si + spec_digits]
        or al, al
        jz .next
        cmp al, KIND_COUNT
        ja .next
        mov cx, di
        jcxz .keep
.dup:   push si
        mov si, cx
        cmp al, [cs:si + spec_sorted - 1]
        pop si
        je .next
        loop .dup
.keep:  mov [cs:di + spec_sorted], al
        inc di
.next:  inc si
        cmp si, SPEC_COUNT
        jb .copy
        xor eax, eax
        or di, di
        jz .put                         ; (none: V3_BASE alone)
        mov cx, 2                       ; the others ascending (three at most: a bubble twice)
.pass:  mov si, 1
.swap:  lea dx, [si + 1]
        cmp dx, di
        jae .passed
        mov al, [cs:si + spec_sorted]
        mov ah, [cs:si + spec_sorted + 1]
        cmp al, ah
        jbe .ok
        mov [cs:si + spec_sorted], ah
        mov [cs:si + spec_sorted + 1], al
.ok:    inc si
        jmp .swap
.passed:
        loop .pass
        movzx eax, byte [cs:spec_sorted] ; the first times REST_SETS, the others' rank: the sets of
        imul eax, eax, REST_SETS        ;   fewer, and C(other - 1, I + 1) for each, I from 0
        dec di
        mov si, di
        add si, si
        movzx edx, word [cs:si + spec_rest_from]
        add eax, edx
        mov si, di
        dec si
        js .put
.rank:  mov ch, [cs:si + spec_sorted + 1]
        dec ch
        call spec_choose
        add eax, edx
        dec si
        jns .rank
.put:   add eax, V3_BASE
        mov edx, [es:bx + SPEC_SLOTS]
        and edx, ~SPEC_KINDS_MASK
        or edx, eax
        mov [es:bx + SPEC_SLOTS], edx
        pop di
        pop si
        pop edx
        pop ecx
        pop eax
        ret
%endmacro

%macro SHARED_spec_unpack 0
spec_unpack:
        push eax
        push ecx
        push edx
        push si
        mov eax, [es:bx + SPEC_SLOTS]
        and eax, SPEC_KINDS_MASK
        cmp eax, V3_BASE
        jae .v3
        mov ecx, 17
        xor si, si
.digit: xor edx, edx
        div ecx
        mov [cs:si + spec_digits], dl
        inc si
        cmp si, SPEC_COUNT
        jb .digit
        jmp .out
.v3:    sub eax, V3_BASE                ; (the first, and the others' rank: SPEC_REPACK's undone)
        xor edx, edx
        mov ecx, REST_SETS
        div ecx
        mov [cs:spec_digits], al
        mov eax, edx
        mov si, 3                       ; (how many others: the sets of fewer come first)
.size:  push si
        add si, si
        movzx ecx, word [cs:si + spec_rest_from]
        pop si
        cmp eax, ecx
        jae .sized
        dec si
        jmp .size
.sized: sub eax, ecx
        mov dword [cs:spec_digits + 1], 0  ; (one past: SPEC_SORTED's room)
        dec si
        js .out
.place: mov cl, KIND_COUNT - 1          ; (the greatest C(CL, SI + 1) under the rank left: the
.try:   mov ch, cl                      ;   other in slot SI + 1 is CL + 1)
        call spec_choose
        cmp edx, eax
        jbe .found
        dec cl
        jmp .try
.found: sub eax, edx
        inc cl
        mov [cs:si + spec_digits + 1], cl
        dec si
        jns .place
.out:   pop si
        pop edx
        pop ecx
        pop eax
        ret
%endmacro

%macro SHARED_sphere_allows 0
sphere_allows:
        push cx
        or al, al
        jnz .mat
        test byte [cs:cu_flags], 0x12
        jnz .yes
        cmp byte [cs:cu_kind], 2        ; (a dagger)
        je .yes
        cmp byte [cs:cu_kind], 11       ; (the cahulaks)
        je .yes
        jmp .no
.mat:   mov ah, SPHERE_EARTH
        cmp al, 1
        je .test
        mov ah, SPHERE_FIRE
        cmp al, 2
        je .test
        mov ah, SPHERE_WATER
.test:  mov cl, [cs:cu_mat]
        cmp cl, 8
        jae .no
        mov ch, 1
        shl ch, cl
        test ah, ch
        jnz .yes
.no:    pop cx
        stc
        ret
.yes:   pop cx
        clc
        ret
%endmacro

%macro SHARED_tputw 0
tputw:
        call tput
        mov al, ah
        jmp tput
%endmacro

%macro SHARED_tu_cell 0
tu_cell:
        mov ah, 4
        cmp al, 1
        jbe .row
        mov ah, 2
        cmp al, 2
        je .row
        dec ah
        cmp al, 4
        jbe .row
        dec ah
        cmp al, 5
        je .row
        cmp al, 11
        jb .many
        mov al, 11
.many:  mov ah, 4
        sub ah, al                      ; (6 to 11 hit dice: -2 to -7)
.row:   mov al, cl
        cmp al, 10
        jb .col
        sub al, 10
        shr al, 1
        cmp al, 2
        jbe .high
        mov al, 2
.high:  add al, 10
.col:   add al, ah                      ; (the run's place, from 1)
        jle .none
        cmp al, 12
        jb .run
        mov ax, TU_DSTAR
        ret
.run:   movzx bx, al
        mov al, [cs:bx + tu_cells - 1]
        mov ah, 0
        ret
.none:  xor ax, ax
        ret
%endmacro

%macro SHARED_vga_restore 0
vga_restore:
        mov dx, 0x3CE
        xor bx, bx
.put:   mov al, [cs:gc_regs + bx]
        mov ah, [cs:gc_saved + bx]
        out dx, ax
        inc bx
        cmp bx, 5
        jb .put
        mov al, [cs:gc_index]
        out dx, al
        mov dx, 0x3C4
        mov al, 2
        mov ah, [cs:sc_mask]
        out dx, ax
        mov al, [cs:sc_index]
        out dx, al
        mov byte [cs:vga_busy], 0
        ret
%endmacro

%macro SHARED_vga_save 0
vga_save:
        mov byte [cs:vga_busy], 1
        mov dx, 0x3C4
        in al, dx
        mov [cs:sc_index], al
        mov al, 2
        out dx, al
        inc dx
        in al, dx
        mov [cs:sc_mask], al
        mov dx, 0x3CE
        in al, dx
        mov [cs:gc_index], al
        xor bx, bx
.save:  mov al, [cs:gc_regs + bx]
        out dx, al
        inc dx
        in al, dx
        dec dx
        mov [cs:gc_saved + bx], al
        inc bx
        cmp bx, 5
        jb .save
        mov ax, 0x0001                  ; no set/reset, no rotation, all bits, write mode 0
        out dx, ax
        mov ax, 0x0003
        out dx, ax
        mov ah, [cs:gc_saved + 3]
        and ah, 0xF4
        mov al, 5
        out dx, ax
        mov ax, 0xFF08
        out dx, ax
        ret
%endmacro

%macro SHARED_war_kit_is 0
war_kit_is:
        call kit_is_b
        db KIT_CRUSADER
        je .ret
        call kit_is_b
        db KIT_MIND_WARRIOR
.ret:   ret
%endmacro

%macro SHARED_wp_button_op 0
wp_button_op:
        push bp
        mov bp, sp
        pusha
        push word [bp + 4]
        push word 0
        push ax
        push dword [WP_SPHERE]
        call far [cs:wp_button_fn]
        add sp, 10
        popa
        pop bp
        ret 2
%endmacro

%macro SHARED_wp_close_panel 0
wp_close_panel:
        cmp byte [cs:wp_from], 0
        jne .sphere
        push word 0x7F8
        push word 0x7F6
        push dword [WP_DISC]
        call wp_marked
        add sp, 8
        mov [WP_DISC_MASK], ax
        push dword [WP_DISC]
        call far [cs:wp_close]
        add sp, 4
        mov dword [WP_DISC], 0
        ret
.sphere:
        cmp byte [cs:wp_from], 1
        jne .page
        push word 0x7FD
        push word 0x7FA
        push dword [WP_SPHERE]
        call wp_marked
        add sp, 8
        mov [WP_SPHERE_MASK], ax
.page:  mov ax, [WP_SPHERE]
        or ax, [WP_SPHERE + 2]
        jz .ret
        push dword [WP_SPHERE]
        call far [cs:wp_close]
        add sp, 4
        mov dword [WP_SPHERE], 0
.ret:   ret
%endmacro

%macro SHARED_wp_harvest 0
wp_harvest:
        push ax
        push bx
        push cx
        push si
        push es
        mov es, [bp + 4]
        mov si, wp_calls
        mov bx, (WP_MARK_SEG + 1) & 0xFFFF
        sub bx, [cs:wp_ret_file]
        add bx, [bp + 2]
        mov ax, [es:bx]
        mov [cs:wp_mark_seg], ax
        mov bx, (WP_SPHERE_SEG + 1) & 0xFFFF
        sub bx, [cs:wp_ret_file]
        add bx, [bp + 2]
        mov ax, [es:bx]
        mov [cs:wp_sphere_seg], ax
        mov bx, (WP_STAT_SEG + 1) & 0xFFFF
        sub bx, [cs:wp_ret_file]
        add bx, [bp + 2]
        mov ax, [es:bx]
        mov [cs:wp_stat_seg], ax
        mov cx, (wp_calls_end - wp_calls) / 6
.one:   mov bx, [cs:si]         ; a call's file offset (low word), less the return's
        sub bx, [cs:wp_ret_file]
        add bx, [bp + 2]
        mov ax, [es:bx + 1]
        mov [cs:si + 2], ax
        mov ax, [es:bx + 3]
        mov [cs:si + 4], ax
        add si, 6
        loop .one
        pop es
        pop si
        pop cx
        pop bx
        pop ax
        ret
%endmacro

%macro SHARED_feet_row 0
feet_row:
        push si
        push dx
        mov dx, -1
        add si, 4
.row:   mov al, [es:si]                 ; a row: its number (FFh: none left), then its runs
        inc si
        cmp al, 0xFF
        je .done
        movzx dx, al                    ; (the rows top down: the last the lowest)
.run:   test byte [es:si + 1], 0x80     ; (past the run: its data's bytes)
        pushf
        movzx ax, byte [es:si + 3]
        add si, 4
        add si, ax
        popf
        jz .run
        jmp .row
.done:  mov ax, dx
        pop dx
        pop si
        ret
%endmacro
