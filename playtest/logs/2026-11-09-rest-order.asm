; Rest pass 2 reordered: the free cures before the effect bitset is read (80765h-807ECh)
bits 16
org 0x0765            ; low word of file offset 80765h (the 8 0000h base cancels in rel jumps)
        jmp near X07ED              ; after the bitset read: on to the mode-1 / Acid / HP part
CASTS:
        cmp word [bp-10h],5         ; best cleric 5th+
        jl .druid
        mov al,[bp-10h]
        push ax
        push word [bp-16h]
        push si
        push byte 60h               ; Cure Disease
        push cs
        call X09A2
        add sp,8
        mov al,[bp-10h]
        push ax
        push word [bp-16h]
        push si
        push byte 67h               ; Remove Curse
        push cs
        call X09A2
        add sp,8
        mov al,[bp-10h]
        push ax
        push word [bp-16h]
        push si
        push byte 69h               ; Remove Paralysis
        push cs
        call X09A2
        add sp,8
.druid: cmp word [bp-12h],5
        jl .np
        mov al,[bp-12h]
        push ax
        push di
        push si
        push byte 60h
        push cs
        call X09A2
        add sp,8
        mov al,[bp-12h]
        push ax
        push di
        push si
        push byte 67h
        push cs
        call X09A2
        add sp,8
        mov al,[bp-12h]
        push ax
        push di
        push si
        push byte 69h
        push cs
        call X09A2
        add sp,8
.np:    cmp word [bp-12h],7
        jl .read
        mov al,[bp-12h]
        push ax
        push di
        push si
        push byte 76h               ; Neutralize Poison
        push cs
        call X09A2
        add sp,8
.read:  jmp near X0758              ; now take the effect bitset
        nop
END:
X0758 equ 0x0758
X07ED equ 0x07ED
X09A2 equ 0x09A2
