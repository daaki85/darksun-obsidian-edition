"""The single garment underneath each approved half-elf multiclass drawing."""


def garment(role):
    parts = role.split("/")
    if len(parts) == 1:
        return role
    if role == "Druid/Thief" or len(parts) == 3 and "Thief" in parts and role != "Fighter/Psionicist/Thief":
        # These outfits borrow just the Thief's crown and nape.
        parts.remove("Thief")
    return next(name for name in ("Thief", "Cleric", "Druid", "Preserver", "Ranger", "Fighter")
                if name in parts)


CLOAKED = frozenset(("Thief", "Druid", "Preserver", "Ranger"))
