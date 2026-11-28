"""DSCLOG2's TEXT in Wake of the Ravager: Shattered Lands' PROBE_TEXT and PROBE_MSG ported (sites 93 and 94),
what the game shows as text copied into the text buffer (the far block's FAR_TBUF, its header's +126 to +138
as DSCLOG's) for the Loader's Dialogue and Journal tabs and the dice log's "Message:" lines; and the Loader's
side (ravlog.RavDiceLog): the sequel's portraits kept apart from SL's (RAV_PORTRAITS), its journal a chain of
its own. The probes run in an emulated CPU: needs nasm and unicorn, else those tests are skipped."""

import os
import shutil
import struct
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dsloader import game, journal, ravager, ravlog, textlog  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_16
    from unicorn import x86_const as r
except ImportError:
    Uc = None

ASM = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dos", "dsclog2.asm")
TSR, GAME_DS, SS, FAR = 0x1000, 0x5000, 0x4000, 0x7000
SP, BP = 0x7F0, 0x600


@unittest.skipIf(Uc is None or not shutil.which("nasm"), "needs unicorn and nasm")
class TextProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from test_dsclog_drawing import build
        exe, cls.sym = build(ASM)
        cls.image = exe[struct.unpack_from("<H", exe, 8)[0] * 16:]
        cls.hdr = cls.image.index(b"DSCLOGR1")

    def machine(self):
        mu = Uc(UC_ARCH_X86, UC_MODE_16)
        mu.mem_map(0, 0x100000)
        mu.mem_write(TSR * 16, self.image)
        mu.mem_write(TSR * 16 + 0xFFF0, bytes((0xF4,)))
        mu.mem_write(TSR * 16 + self.sym["far_seg"], struct.pack("<H", FAR))
        mu.mem_write(TSR * 16 + self.sym["tbuf_seg"], struct.pack("<H", FAR))
        return mu

    def call(self, mu, site, args: bytes):
        """SITE as the game's INT reaches it at a routine's start: the IRET frame (to a HLT), the routine's own
        far way back (1111h:2222h), then its arguments."""
        mu.mem_write(SS * 16 + SP, struct.pack("<HHHHH", 0xFFF0, TSR, 0x2, 0x2222, 0x1111) + args)
        for name, value in dict(cs=TSR, ds=GAME_DS, ss=SS, esp=SP, ebp=BP, eflags=0x2, eax=0xA1, ebx=0xB2,
                                ecx=0xC3, edx=0xD4, esi=0xE5).items():
            mu.reg_write(getattr(r, "UC_X86_REG_" + name.upper()), value)
        mu.emu_start(TSR * 16 + self.sym[site], TSR * 16 + 0xFFF0, count=100000)
        # the replaced "push bp / mov bp,sp" done for the routine, every other register as it was
        self.assertEqual((mu.reg_read(r.UC_X86_REG_SP), mu.reg_read(r.UC_X86_REG_BP)), (SP + 4, SP + 4))
        self.assertEqual(struct.unpack("<H", mu.mem_read(SS * 16 + SP + 4, 2))[0], BP)
        self.assertEqual([mu.reg_read(getattr(r, "UC_X86_REG_" + n)) for n in ("AX", "BX", "CX", "DX", "SI", "DS")],
                         [0xA1, 0xB2, 0xC3, 0xD4, 0xE5, GAME_DS])

    def records(self, mu):
        """What the Loader's TextBuffer reads from the emulated memory (the header's +126 to +138)."""
        def read(addr, size):
            return bytes(mu.mem_read(addr, size))
        buf = textlog.TextBuffer(read, TSR * 16 + self.hdr)
        buf.pos = 0
        return buf.poll()

    def test_header(self):
        """The header's text fields at DSCLOG's places: TSIZE, FAR_TBUF in the far block, the probes."""
        tpos, off, size, text, msg = struct.unpack_from("<HHHHH", self.image, self.hdr + 126)
        self.assertEqual((tpos, off, size), (0, self.sym["FAR_TBUF"], 2048))
        self.assertEqual((text, msg), (self.sym["probe_text"], self.sym["probe_msg"]))
        self.assertLessEqual(self.sym["FAR_TBUF"] + 2048, 0xFFF0)  # (the far block may be the HMA)

    def test_site_table(self):
        """Sites 93 and 94 are PROBE_TEXT and PROBE_MSG, as ravager's patches "text" and "message" name them,
        on the routines' "push bp / mov bp,sp"."""
        table = self.sym["site_table"]
        for number, name in ((93, "probe_text"), (94, "probe_msg")):
            self.assertEqual(struct.unpack_from("<H", self.image, table + 2 * number)[0], self.sym[name])
        patches = {p.name: p for p in ravager.PATCHES}
        for name, number, at in (("text", 93, 0x87BA0), ("message", 94, 0x59A0B)):
            self.assertEqual((patches[name].offset, patches[name].original, patches[name].replacement),
                             (at, bytes.fromhex("558bec"), bytes((0xCD, ravager.VEC_SITE, number))))

    def test_dialogue_records(self):
        """A portrait, a text, a reply and the replies shown: each a record, the texts copied."""
        mu = self.machine()
        mu.mem_write(GAME_DS * 16 + 0x100, b"Greetings, traveller.\0")
        mu.mem_write(GAME_DS * 16 + 0x200, b"Who are you?\0")
        self.call(mu, "probe_text", struct.pack("<HIH", 1, 0, 12))
        self.call(mu, "probe_text", struct.pack("<HHHH", 2, 0x100, GAME_DS, 0))
        self.call(mu, "probe_text", struct.pack("<HHHH", 0, 0x200, GAME_DS, 0))
        self.call(mu, "probe_text", struct.pack("<HIH", 3, 0, 0))
        got = [(rec.kind, rec.value, rec.text) for rec in self.records(mu)]
        self.assertEqual(got, [(1, 12, ""), (2, 0, "Greetings, traveller."), (0, 0, "Who are you?"), (3, 0, "")])
        self.assertEqual(struct.unpack("<H", mu.mem_read(TSR * 16 + self.sym["text_records"], 2))[0], 4)

    def test_message_box(self):
        """The message box's far text, kind 16; a text longer than 400 bytes cut there."""
        mu = self.machine()
        mu.mem_write(GAME_DS * 16 + 0x300, b"YOU LEARN THE SPELL\0")
        mu.mem_write(GAME_DS * 16 + 0x400, b"x" * 500 + b"\0")
        self.call(mu, "probe_msg", struct.pack("<HH", 0x300, GAME_DS))
        self.call(mu, "probe_msg", struct.pack("<HH", 0x400, GAME_DS))
        got = self.records(mu)
        self.assertEqual([(rec.kind, rec.text) for rec in got], [(16, "YOU LEARN THE SPELL"), (16, "x" * 400)])
        self.assertEqual(struct.unpack("<H", mu.mem_read(TSR * 16 + self.sym["msg_records"], 2))[0], 2)

    def test_buffer_wraps(self):
        """The position wraps at TSIZE: the Loader reads a record cut by the end from both ends."""
        mu = self.machine()
        mu.mem_write(TSR * 16 + self.hdr + 126, struct.pack("<H", 2040))
        mu.mem_write(GAME_DS * 16 + 0x100, b"Across the end\0")
        self.call(mu, "probe_text", struct.pack("<HHHH", 2, 0x100, GAME_DS, 0))
        def read(addr, size):
            return bytes(mu.mem_read(addr, size))
        buf = textlog.TextBuffer(read, TSR * 16 + self.hdr)
        buf.pos = 2040
        self.assertEqual([rec.text for rec in buf.poll()], ["Across the end"])


class _Inner:
    def __init__(self, records):
        self.records, self.size = records, 2048

    def poll(self):
        out, self.records = self.records, []
        return out


class LoaderSideTests(unittest.TestCase):
    def test_portraits_apart(self):
        """The sequel's portraits as RAV_PORTRAITS + its number (0, narration, kept); its names never SL's."""
        recs = [textlog.TextRecord(textlog.KIND_PORTRAIT, 0, 12, ""), textlog.TextRecord(textlog.KIND_PORTRAIT, 0, 0, ""),
                textlog.TextRecord(textlog.KIND_TEXT, 0, 0, "Hello")]
        got = ravlog.SequelText(_Inner(recs)).poll()
        self.assertEqual([r.value for r in got], [ravlog.RAV_PORTRAITS + 12, 0, 0])
        log = ravlog.RavDiceLog.__new__(ravlog.RavDiceLog)
        log.speaker_names, log.learned_speakers = {}, {}
        sl_face = next(iter(game.SPEAKERS))
        self.assertEqual(log.speaker(ravlog.RAV_PORTRAITS + sl_face), f"Portrait {sl_face}")
        self.assertEqual(log.speaker(0), "Narration")
        log.learned_speakers[ravlog.RAV_PORTRAITS + 12] = "Uhubito"
        self.assertEqual(log.speaker(ravlog.RAV_PORTRAITS + 12), "Uhubito")

    def test_journal_follows_the_saves(self):
        """The sequel's journal keeps its head in the game's global numbers (DS:15F6h's, the last two of 200,
        saved as SAVE 31) as SL's: written past the read-only view as entries are added, and a game loaded
        with another head shows that head's chain."""
        import tempfile

        class Raw:
            def __init__(self):
                self.mem = bytearray(0x80000)

            def read(self, addr, size):
                return bytes(self.mem[addr:addr + size])

            def write(self, addr, data):
                self.mem[addr:addr + len(data)] = data

        class Game:
            ds = 0x1000

            def game_time(self):
                return 3600

        with tempfile.TemporaryDirectory() as tmp:
            raw = Raw()
            log = ravlog.RavDiceLog.__new__(ravlog.RavDiceLog)
            log.guest = ravlog.ReadOnlyGuest(raw)
            log.journal, log.game = journal.Journal(os.path.join(tmp, "j.jsonl")), Game()
            self.assertIsNone(log._journal_head())  # (no numbers in memory yet)
            self.assertFalse(log._journal_write(5))
            struct.pack_into("<HH", raw.mem, Game.ds * 16 + ravlog.RAV_NUMBERS_PTR, 0x0004, 0x6D8A)
            numbers = 0x6D8A * 16 + 4
            for _ in range(journal.STEADY):
                log._journal_sync()
            log.journal.add(journal.TALK, "Welcome to Tyr.", 3600, 0x32)
            log._journal_sync()
            first = log.journal.head
            self.assertTrue(first)
            self.assertEqual(struct.unpack_from("<I", raw.mem, numbers + 198 * 2)[0], first)
            self.assertEqual(sum(raw.mem[numbers:numbers + 198 * 2]), 0)  # (no other number touched)
            log.journal.add(journal.MESSAGE, "YOU LEARN THE SPELL", 3700, 0x32)
            log._journal_sync()
            self.assertEqual(len(log.journal.chain()), 2)
            struct.pack_into("<I", raw.mem, numbers + 198 * 2, first)  # (a save made after the first, loaded)
            for _ in range(journal.STEADY + 1):
                log._journal_sync()
            self.assertEqual([e.text for e in log.journal.chain()], ["Welcome to Tyr."])

    def test_layout(self):
        """The dialogue's replies and the one talked to at the sequel's addresses; the journal's regions its own
        while it is attached."""
        layout = ravlog.layout()
        self.assertEqual((layout["REPLY_CHOSEN"], layout["REPLY_SCROLL"], layout["REPLY_TEXTS"], layout["TALK_SEG"]),
                         (0x25BA, 0x6321, 0x6356, 0x3C13))
        ravlog.apply_layout()
        try:
            self.assertEqual(journal.region_name(0x32), "Tyr")
        finally:
            ravlog.restore_layout()
        self.assertNotEqual(journal.region_name(0x32), "Tyr")


if __name__ == "__main__":
    unittest.main()
