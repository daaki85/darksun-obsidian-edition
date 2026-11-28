; kit_names_table.inc: the kits' names, the same in DSCLOG (Shattered Lands') and DSCLOG2 (Wake of the
; Ravager's), each helper's tail's (KIT_NAME_PTR finds a name; the memory pass of 2026-11-28 moved the
; sequel's out of its segment). A kit is the creation screen's class x 4 + the kit (kitpages.kit_ids).
; Each class's kits (kitpages.KITS), the creation screen's classes in order, three each
kit_names    db 'ELEMENTALIST', 0, 'HEALER', 0, 'CRUSADER', 0
             db 'GROVE WARDEN', 0, 'LIFEBINDER', 0, 'WANDERER', 0
             db 'MYRMIDON', 0, 'SENTINEL', 0, 'RAVAGER', 0
             db 'ARENA CHAMPION', 0, 'TWIN-BLADE', 0, 'BRUTE', 0
             db 'SCHOLAR', 0, 'BATTLE MAGE', 0, 'ARCANIST', 0
             db 'MIND BENDER', 0, 'MIND WARRIOR', 0, 'KINETICIST', 0
             db 'STALKER', 0, 'JUSTIFIER', 0, 'SEEKER', 0
             db 'SWASHBUCKLER', 0, 'ASSASSIN', 0, 'SHINOBI', 0
             db 'BATTLE DANCER', 0, 0, 0                ; (the multiclass groups', three to each)
             db 'SHADOWBLADE', 0, 'MILITARY SCOUT', 0, 0
             db 'WILDERNESS AVENGER', 0, 0, 0
             db 'RESCUER', 0, 0, 0
             db 'GHETTO FIGHTER', 0, 'WAYFINDER', 0, 0
             db 'SPELLARCHER', 0, 0, 0
             db 'TITAN MIND', 0, 0, 0
             db 'POISONER', 0, 0, 0
             db 'SPIRIT CALLER', 0, 0, 0
             db 'WASTELAND SEER', 0, 0, 0
             db 'WILD FURY', 0, 0, 0
; Shorter names for the Effects screen's line (kitpages.SHORT): the kit, the name. 0 ends it.
kit_short    db 17, 'CHAMPION', 0, 33, 'SWASHBUCK', 0, 5, 'ELEMENTAL', 0
             db 9, 'WARDEN', 0, 22, 'BATTLMAGE', 0, 25, 'M-BENDER', 0
             db 26, 'M-WARRIOR', 0, 37, 'B-DANCER', 0, 41, 'SHADOWBLD', 0
             db 42, 'M-SCOUT', 0, 45, 'W-AVENGER', 0, 53, 'G-FIGHTER', 0
             db 57, 'SPELLARCH', 0, 69, 'S-CALLER', 0, 73, 'WASTE SEER', 0, 0
