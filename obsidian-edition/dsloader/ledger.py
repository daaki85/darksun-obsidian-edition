"""The dice log's lines laid out for reading (the window's "G" layout): an outcome first on each
event's line, the roll and HP in columns at its right, the working on dim lines under it.

The dice log's own lines (DiceLog.lines) stay as they are: the panel in the game, the saved logs and
the find box read them. Ledger turns each into what the window shows: whole lines (Row), each a run
of pieces in a role (a colour) and a kind (event, detail, rule, turn, plain), and fills (Fill): a
piece put later into a slot an earlier row left (a hit's damage, which its own line gives after the
attack's; the HP the target is left with, which comes later still).

    ● Seneca hits Arena Guard for 11 - backstab, Bone Hayneedle +1   19/30 (-11)   d20 15 vs 4+ (85%) · AC 8
        to hit: THAC0 19, +2 from behind ... = 12; vs AC 8 needs 4+; d20 15 -> HIT (would hit AC -3)
        damage: Bone Hayneedle +1 (1d4+1): 1d4 = [3] +1 weapon +4 STR 18 ...

A party member's line has a filled pip, a monster's a hollow one. The outcome's colour is the
party's view of it: good (a party hit, a monster's failed save), bad (a monster's hit, a party
member's failed save), dim (a miss, a monster's save). The names are coloured by the window, as on
any line."""

import re
from typing import Callable, Dict, List, NamedTuple, Optional, Tuple, Union

# the pieces' roles (the window's colours: palette.LEDGER_COLOURS)
BODY, GOOD, BAD, DIM, NOTE, RULE = "body", "good", "bad", "dim", "note", "rule"
# the rows' kinds
EVENT, DETAIL, ROUND, TURN, PLAIN, SUMMARY = "event", "detail", "round", "turn", "plain", "summary"
TAB = "\t"  # (an event row's columns: its text, then the HP, then the roll)
PARTY_PIP, MONSTER_PIP, NO_PIP = "● ", "○ ", "  "
DASH = " — "
DOT = " · "
ARROW = "→"
MINUS = "−"
RULE_TAIL = 24  # (the round's rule after its text, in characters)
KEEP = 40  # rows a slot waits for its fill before it is given up


class Piece(NamedTuple):
    text: str
    role: str = BODY
    slot: Optional[str] = None  # a slot: empty now, a Fill later (its id)


class Row(NamedTuple):
    kind: str
    pieces: Tuple[Piece, ...]
    plain_kind: str = ""  # a plain row: the classic log's kind (combatlog.line_kind), for its colour


class Fill(NamedTuple):
    slot: str
    pieces: Tuple[Piece, ...]


Op = Union[Row, Fill]

ATTACK = re.compile(r"(?P<who>.+?) attacks (?P<target>.+?)(?P<how> from behind| BACKSTAB| unseen)?"
                    r"(?: with (?P<weapon>.+?))?: d20 = (?P<d20>\d+)(?P<natural> \(natural \d+\))?, "
                    r"(?P<needs>needs -?\d+\+|only a 20 hits|hits on anything but a 1)(?: \((?P<pct>\d+)%\))?"
                    r"(?:, hits AC (?P<hit_ac>-?\d+))?(?:, target AC (?P<ac>-?\d+))? -> (?P<result>HIT|miss)$")
# a spell's attack roll (dicelog's _spell_to_hit): its working in brackets (nested ones in it), the AC last
SPELL_ATTACK = re.compile(r"(?P<who>.+?)'s (?P<spell>.+?) at (?P<target>.+?): (?P<touch>touch )?attack "
                          r"d20 = (?P<d20>\d+)(?P<natural> \(natural \d+\))?, "
                          r"(?P<needs>needs -?\d+\+|only a 20 hits|hits on anything but a 1)(?: \((?P<pct>\d+)%\))?"
                          r"(?: \((?P<how>.*); target AC (?P<ac>-?\d+)\))? -> (?P<result>HIT|MISS)(?:: (?P<tail>.*))?$")
TAKES = re.compile(r"  (?P<who>.+?) takes (?P<n>\d+) from (?P<what>.+?)(?: \(.*?\))?(?: and \d+ from the hit)?"
                   r"(?:, now (?P<hp>-?\d+)(?:/(?P<most>\d+))? HP)?$")
WEAPON = re.compile(r"(?P<name>.+?)(?: \((?P<dice>[^()]*)\))?$")
HIT_FOR = re.compile(r"  (?P<who>.+?) hits (?P<target>.+?) for (?P<n>\d+): (?P<rest>.*)$")
NOW_HP = re.compile(r"  (?P<who>.+?) now (?P<hp>-?\d+)/(?P<most>\d+) HP \((?P<delta>[+-]\d+)(?::\s*(?P<why>.*))?\)$")
SAVE = re.compile(r"(?P<who>.+?)'s saving throw vs (?P<what>.+?): d20 = (?P<d20>\d+)(?P<natural> \(natural \d+\))?"
                  r"(?P<mods>.*?), needs (?P<need>-?\d+)(?: \((?P<pct>\d+)% to save\))? -> (?P<result>.+)$")
CHECK = re.compile(r"(?P<ind>\s*)(?P<what>[^:]+?): (?P<die>d\d+|\d+-\d+) = (?P<roll>-?\d+), "
                   r"needs (?P<need>-?\d+)(?P<why_in> \([^)]*\))? or less(?P<why> \(.*?\))?(?P<more>[^>]*?) -> (?P<result>.+)$")
ROUND_LINE = re.compile(r"Round (?P<n>\d+)(?::\s*(?P<order>.*))?$")
TURN_LINE = re.compile(r"(?P<who>.+)'s turn$")
KILLED = re.compile(r"(?P<who>.+) is killed$")
GOOD_WORDS = ("success", "hidden", "unheard", "resisted", "saved", "sent away", "dispelled", "it works")
BAD_WORDS = ("fail", "stumbles", "caught", "not resisted", "seen", "heard", "BREAKS", "DESTROYED")


SAVE_KIND_TAIL = re.compile(r" \((?P<kind>[a-z/ ]+)\)$")


def save_source(what: str) -> Tuple[str, Optional[str], Optional[str]]:
    """A saving throw's "vs" part (dicelog's _save_line: "SPELL[ from CASTER][ (KIND)]"): the spell,
    who cast it (None when unnamed: its target's own, a cloud on the ground) and the kind of save.
    The caster is after the last " from " that isn't a spell's own ("Protection from Evil")."""
    kind = None
    m = SAVE_KIND_TAIL.search(what)
    if m:
        kind, what = m.group("kind"), what[:m.start()]
    at = len(what)
    while True:
        at = what.rfind(" from ", 0, at)
        if at < 0:
            return what, None, kind
        if not what[:at].endswith("Protection"):
            return what[:at], what[at + len(" from "):], kind


def _signed(text: str) -> str:
    return text.replace("-", MINUS) if text.startswith("-") else text


class Ledger:
    """Feed it the dice log's lines (feed); it gives what the window shows of each (rows and fills).
    IS_PARTY tells a party member's name from anyone else's."""

    def __init__(self, is_party: Callable[[str], bool]):
        self.is_party = is_party
        self._attack: Optional[dict] = None  # (the last attack, for its THAC0 line and its damage)
        self._slots: Dict[Tuple[str, str], Tuple[str, int]] = {}  # (kind, name) -> (slot id, row made at)
        self._rows = 0
        self._next = 0
        self._summary = False  # (in a fight's summary: its members' lines shown with it, not as working)

    # ---------------------------------------------------------------------------------------------

    def feed(self, line: str) -> List[Op]:
        ops = self._line(line)
        self._rows += sum(1 for op in ops if isinstance(op, Row))
        stale = [key for key, (_, at) in self._slots.items() if self._rows - at > KEEP]
        for key in stale:
            del self._slots[key]
        return ops

    def _slot(self, kind: str, name: str) -> Piece:
        self._next += 1
        sid = f"{kind}{self._next}"
        self._slots[(kind, name)] = (sid, self._rows)
        return Piece("", BODY, sid)

    def _take(self, kind: str, name: str) -> Optional[str]:
        found = self._slots.pop((kind, name), None)
        return found[0] if found else None

    def _pip(self, name: str) -> Piece:
        return Piece(PARTY_PIP if self.is_party(name) else MONSTER_PIP, BODY)

    def _actor(self, text: str) -> Optional[str]:
        """The name a line starts with, if it is a party member's (else None)."""
        words = text.split()
        for n in range(len(words), 0, -1):
            name = " ".join(words[:n])
            if self.is_party(name):
                return name
        return None

    # ---------------------------------------------------------------------------------------------

    def _line(self, line: str) -> List[Op]:
        text = line.strip()
        if line.startswith("Fight over: "):
            self._summary = True
            self._slots.clear()
            return [Row(SUMMARY, (Piece("Fight over", NOTE), Piece(": " + line[len("Fight over: "):], BODY)))]
        if self._summary and line.startswith("    "):
            return [Row(SUMMARY, (Piece("  " + text, BODY),))]
        self._summary = False
        if self._attack is not None and self._attack.get("thac0_due") and line.startswith("    THAC0 "):
            return [self._to_hit(text)]
        if self._attack is not None:
            self._attack["thac0_due"] = False
        m = ROUND_LINE.match(line)
        if m:
            self._slots.clear()
            head = f"── Round {m.group('n')}"
            order = m.group("order")
            pieces = [Piece(head, RULE)]
            if order:
                pieces.append(Piece(DOT + order, BODY))
            pieces.append(Piece(" " + "─" * RULE_TAIL, RULE))
            return [Row(ROUND, tuple(pieces))]
        m = TURN_LINE.match(line)
        if m and not line.startswith(" "):
            return [Row(TURN, (Piece("▸ " + m.group("who"), DIM),))]
        m = ATTACK.match(line)
        if m:
            return [self._attack_row(m)]
        m = SPELL_ATTACK.match(line)
        if m:
            return self._spell_row(m)
        m = TAKES.match(line)
        if m and ("spell", f"{m.group('what')}>{m.group('who')}") in self._slots:
            return self._spell_damage(m, line)
        m = HIT_FOR.match(line)
        if m:
            return self._damage(m, line)
        m = NOW_HP.match(line)
        if m:
            return self._hp(m, line)
        m = SAVE.match(line)
        if m:
            return self._save(m, line)
        m = KILLED.match(line)
        if m and not line.startswith(" "):
            return [Row(EVENT, (Piece(NO_PIP), Piece(m.group("who"), BODY), Piece(" is killed", NOTE)))]
        m = CHECK.match(line)
        if m and "attacks" not in line:
            return self._check(m)
        if line.startswith("    "):
            return [Row(DETAIL, (Piece(line, DIM),))]
        return [Row(PLAIN, (Piece(line, BODY),))]

    def _attack_row(self, m: "re.Match") -> Row:
        who, target, hit = m.group("who"), m.group("target"), m.group("result") == "HIT"
        party = self.is_party(who)
        weapon = WEAPON.match(m.group("weapon")) if m.group("weapon") else None
        self._attack = dict(who=who, target=target, hit=hit, d20=m.group("d20"), needs=m.group("needs"),
                            hit_ac=m.group("hit_ac"), ac=m.group("ac"), thac0_due=True,
                            weapon=m.group("weapon"))
        role = (GOOD if party else BAD) if hit else DIM
        extras = []
        how = (m.group("how") or "").strip()
        if how:
            extras.append("backstab" if how == "BACKSTAB" else how)
        if weapon:
            extras.append(weapon.group("name"))
        pieces = [self._pip(who), Piece(who, BODY if hit else DIM), Piece(" "),
                  Piece("hits" if hit else "misses", role), Piece(" "), Piece(target, BODY if hit else DIM)]
        if hit:
            pieces.append(self._slot("damage", f"{who}>{target}"))
        if extras:
            pieces.append(Piece(DASH + ", ".join(extras), BODY if hit else DIM))
        pieces.append(Piece(TAB))
        pieces.append(self._slot("hp", target) if hit else Piece(""))
        needs = m.group("needs")
        need = needs[len("needs "):] if needs.startswith("needs ") else "2+" if "anything" in needs else "20"
        roll = f"d20 {m.group('d20')}{' (natural)' if m.group('natural') else ''} vs {_signed(need)}"
        if m.group("pct"):
            roll += f" ({m.group('pct')}%)"
        if m.group("ac") is not None:
            roll += f"{DOT}AC {_signed(m.group('ac'))}"
        pieces += [Piece(TAB), Piece(roll, DIM)]
        return Row(EVENT, tuple(pieces))

    def _spell_row(self, m: "re.Match") -> List[Op]:
        """A spell's attack roll as an attack's event row ("Lex's Acid Arrow hits Templar [for 3] ...
        d20 12 vs 4+ (85%) · AC 4"), its working under it; its damage and the HP after it filled by
        its "takes" line."""
        who, spell, target, hit = m.group("who"), m.group("spell"), m.group("target"), m.group("result") == "HIT"
        self._attack = None  # (no weapon's THAC0 line follows a spell's)
        role = (GOOD if self.is_party(who) else BAD) if hit else DIM
        pieces = [self._pip(who), Piece(who, BODY if hit else DIM), Piece(f"'s {spell} ", BODY if hit else DIM),
                  Piece("hits" if hit else "misses", role), Piece(" "), Piece(target, BODY if hit else DIM)]
        if hit:
            pieces.append(self._slot("spell", f"{spell}>{target}"))
        elif m.group("tail"):
            pieces.append(Piece(DASH + m.group("tail").replace("the spell does nothing, ", ""), DIM))
        pieces.append(Piece(TAB))
        pieces.append(self._slot("hp", target) if hit else Piece(""))
        needs = m.group("needs")
        need = needs[len("needs "):] if needs.startswith("needs ") else "2+" if "anything" in needs else "20"
        roll = f"d20 {m.group('d20')}{' (natural)' if m.group('natural') else ''} vs {_signed(need)}"
        if m.group("pct"):
            roll += f" ({m.group('pct')}%)"
        if m.group("ac") is not None:
            roll += f"{DOT}AC {_signed(m.group('ac'))}"
        pieces += [Piece(TAB), Piece(roll, DIM)]
        rows: List[Op] = [Row(EVENT, tuple(pieces))]
        if m.group("how"):
            detail = f"    {m.group('touch') or ''}to hit: {m.group('how')}"
            if m.group("ac") is not None:
                detail += f"; vs AC {_signed(m.group('ac'))} {needs}"
            detail += f"; d20 {m.group('d20')} {ARROW} {m.group('result')}"
            rows.append(Row(DETAIL, (Piece(detail, DIM),)))
        return rows

    def _spell_damage(self, m: "re.Match", line: str) -> List[Op]:
        """A spell's damage after its attack roll hit: into the attack's row (and the HP left)."""
        who, n = m.group("who"), m.group("n")
        sid = self._take("spell", f"{m.group('what')}>{who}")
        party = self.is_party(who)
        ops: List[Op] = [Fill(sid, (Piece(" for ", BODY), Piece(n, BAD if party else GOOD)))]
        hp_sid = self._take("hp", who)
        if hp_sid is not None and m.group("hp") is not None:
            hp = int(m.group("hp"))
            most = int(m.group("most")) if m.group("most") else None
            low = party and most is not None and hp * 3 <= most
            text = f"{'! ' if low else ''}{hp}{f'/{most}' if most is not None else ''} ({MINUS}{n})"
            ops.append(Fill(hp_sid, (Piece(text, BAD if party else BODY),)))
        ops.append(Row(DETAIL, (Piece("    " + line.strip(), DIM),)))
        return ops

    def _to_hit(self, thac0: str) -> Row:
        a = self._attack
        a["thac0_due"] = False
        text = f"    to hit: {thac0}"
        if a["ac"] is not None:
            text += f"; vs AC {_signed(a['ac'])} {a['needs']}"
        text += f"; d20 {a['d20']} {ARROW} {'HIT' if a['hit'] else 'miss'}"
        if a["hit_ac"] is not None:
            text += f" (would hit AC {_signed(a['hit_ac'])})"
        return Row(DETAIL, (Piece(text, DIM),))

    def _damage(self, m: "re.Match", line: str) -> List[Op]:
        who, target, n = m.group("who"), m.group("target"), m.group("n")
        sid = self._take("damage", f"{who}>{target}")
        if sid is None:
            return [Row(PLAIN, (Piece(line, BODY),), "damage")]
        role = GOOD if self.is_party(who) else BAD
        weapon = self._attack["weapon"] if self._attack and self._attack["who"] == who else None
        detail = f"    damage: {weapon + ': ' if weapon else ''}{m.group('rest')}"
        return [Fill(sid, (Piece(" for ", BODY), Piece(n, role))), Row(DETAIL, (Piece(detail, DIM),))]

    def _hp(self, m: "re.Match", line: str) -> List[Op]:
        who = m.group("who")
        sid = self._take("hp", who)
        hp, most, delta = int(m.group("hp")), int(m.group("most")), m.group("delta")
        party = self.is_party(who)
        low = party and hp * 3 <= most
        role = BAD if low else (BAD if party and delta.startswith("-") else BODY)
        text = f"{'! ' if low else ''}{hp}/{most} ({_signed(delta)})"
        if sid is None:
            return [Row(EVENT, (Piece(NO_PIP), Piece(f"{who} now "), Piece(text, role)) +
                        ((Piece(f": {m.group('why')}", DIM),) if m.group("why") else ()))]
        ops: List[Op] = [Fill(sid, (Piece(text, role),))]
        if m.group("why"):
            ops.append(Row(DETAIL, (Piece(f"    {who}: {m.group('why')}", DIM),)))
        return ops

    def _save(self, m: "re.Match", line: str) -> List[Op]:
        who, result = m.group("who"), m.group("result")
        party = self.is_party(who)
        saved = result.startswith("saved")
        spell, _, kind = save_source(m.group("what"))  # (who cast it: in the detail line)
        what = spell if not kind or "/" in kind else f"{spell} ({kind})"
        tail = result.split(":", 1)[1].strip() if ":" in result else ""
        role = (GOOD if saved else BAD) if party else (DIM if saved else GOOD)
        pieces = [Piece(NO_PIP), Piece(who, BODY), Piece(" "), Piece("saves" if saved else "fails", role),
                  Piece(f" vs {what}", BODY if not (saved and not party) else DIM)]
        if tail:
            pieces.append(Piece(DASH + tail, BODY))
        total = re.findall(r"= (-?\d+)", m.group("mods") or "")
        roll = f"d20 {m.group('d20')}" + (f" = {total[-1]}" if total else "") + f" vs {_signed(m.group('need'))}+"
        if m.group("pct"):
            roll += f" ({m.group('pct')}%)"
        # (the HP after it: a hit's slot for this creature, still empty, takes it first)
        hp = Piece("") if ("hp", who) in self._slots else self._slot("hp", who)
        pieces += [Piece(TAB), hp, Piece(TAB), Piece(roll, DIM)]
        return [Row(EVENT, tuple(pieces)), Row(DETAIL, (Piece("    " + line.strip(), DIM),))]

    def _check(self, m: "re.Match") -> List[Op]:
        what, result = m.group("what").strip(), m.group("result")
        actor = self._actor(what)
        low = result.lower()
        good = any(w.lower() in low for w in GOOD_WORDS) and not low.startswith(("fail", "not "))
        bad = not good and any(w.lower() in low for w in BAD_WORDS)
        role = BODY if not (good or bad) else (GOOD if good else BAD) if actor else (BAD if good else GOOD)
        indent = m.group("ind") or ""
        pip = Piece(PARTY_PIP if actor else NO_PIP) if not indent else Piece(indent)
        roll = f"{m.group('die')} {m.group('roll')} vs {_signed(m.group('need'))} or less"
        why = (m.group("why") or m.group("why_in") or "").strip()
        detail = f"    {what}: {m.group('die')} = {m.group('roll')}, needs {m.group('need')} or less" + \
                 (f" {why}" if why else "") + (m.group("more") or "") + f" {ARROW} {result}"
        return [Row(EVENT, (pip, Piece(what, BODY), Piece(DASH), Piece(result, role), Piece(TAB), Piece(""),
                            Piece(TAB), Piece(roll, DIM))),
                Row(DETAIL, (Piece(detail, DIM),))]
