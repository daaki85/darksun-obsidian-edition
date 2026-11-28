"""sfxvolume: the sound effects' starting volume in both games, and a loaded game's in the roster."""
import os
import tempfile
import unittest

from dsloader import gamepatch, gff, ravager, sfxvolume
from test_core import build_gff

SL_PREF = bytes.fromhex("0100643f64010001000100")  # (Shattered Lands' roster as the game saves it)
RAV_PREF = bytes.fromhex("0000ff3fff01010001")  # (the sequel's CHARSAVE.GFF as GOG installs it)


def roster(pref: bytes) -> bytes:
    return build_gff({("CHAR", 15): b"x" * 8, ("PREF", 100): pref, ("TEXT", 0): b"t"})


class SfxVolumeTests(unittest.TestCase):
    def folder(self, pref: bytes, cloud: bytes = b"") -> str:
        d = tempfile.mkdtemp()
        self.addCleanup(__import__("shutil").rmtree, d)
        with open(os.path.join(d, "CHARSAVE.GFF"), "wb") as f:
            f.write(roster(pref))
        if cloud:
            os.mkdir(os.path.join(d, "cloud_saves"))
            with open(os.path.join(d, "cloud_saves", "charsave.gff"), "wb") as f:
                f.write(roster(cloud))
        return d

    def pref(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return gff.read_gff(f.read())[("PREF", 100)]

    def test_the_patches_start_where_the_levels_say(self):
        """The data the patches write is the levels the roster gets: the sequel's full, Shattered
        Lands' in DOSBox-X 79; both games start at the game's 100 and 63."""
        rav = {p.name: p for p in ravager.PATCHES}["sfx_volume_full"]
        sl = {p.name: p for p in gamepatch.PATCHES}["sfx_volume_dosbox_x"]
        self.assertEqual((rav.original, rav.replacement), (bytes(sfxvolume.GAME), bytes(sfxvolume.FULL)))
        self.assertEqual((sl.original, sl.replacement), (bytes(sfxvolume.GAME), bytes(sfxvolume.SL_DOSBOX_X)))
        self.assertEqual(sfxvolume.SL_DOSBOX_X[0] >> 1, sfxvolume.SL_DOSBOX_X[1])  # (the menu's own slider for it)
        self.assertEqual(gamepatch.SFX_VOLUME_DBX, (sl.name,))

    def test_the_sequels_roster_made_full(self):
        d = self.folder(RAV_PREF)
        self.assertEqual(sfxvolume.set_roster(d, *sfxvolume.ravager_level()), [os.path.join(d, "CHARSAVE.GFF")])
        pref = self.pref(os.path.join(d, "CHARSAVE.GFF"))
        self.assertEqual(pref, bytes.fromhex("0000ff7fff01010001"))  # (the rest as it was)
        self.assertEqual(sfxvolume.set_roster(d, *sfxvolume.ravager_level()), [])  # (once)

    def test_a_volume_the_player_chose_stays(self):
        chosen = bytes.fromhex("0000502801")  # (slider 80, volume 40)
        d = self.folder(chosen + RAV_PREF[5:])
        self.assertEqual(sfxvolume.set_roster(d, *sfxvolume.ravager_level()), [])
        self.assertEqual(sfxvolume.set_roster(d, *sfxvolume.sl_level(True)), [])

    def test_shattered_lands_follows_the_engine_both_ways(self):
        d = self.folder(SL_PREF, cloud=SL_PREF)
        paths = [os.path.join(d, "CHARSAVE.GFF"), os.path.join(d, "cloud_saves", "charsave.gff")]
        self.assertEqual(sfxvolume.set_roster(d, *sfxvolume.sl_level(True)), paths)  # (GOG's cloud_saves too)
        for path in paths:
            self.assertEqual(sfxvolume.level(open(path, "rb").read()), sfxvolume.SL_DOSBOX_X)
        self.assertEqual(sfxvolume.set_roster(d, *sfxvolume.sl_level(False)), paths)  # (back for GOG's DOSBox)
        for path in paths:
            self.assertEqual(self.pref(path), SL_PREF)

    def test_the_loader_sets_shattered_lands_roster_for_its_engine(self):
        """prepare_patched_game sets the roster for the engine the game starts in, before the copy."""
        from dsloader import dosboxx, launch
        d = self.folder(SL_PREF)
        open(os.path.join(d, "DSUN.EXE"), "wb").close()
        saved = gamepatch.write_patched
        self.addCleanup(setattr, gamepatch, "write_patched", saved)

        def write_patched(*args, **kwargs):
            raise gamepatch.PatchError("not in a test")
        gamepatch.write_patched = write_patched
        path = os.path.join(d, "CHARSAVE.GFF")
        launch.prepare_patched_game(d, {dosboxx.SETTING: dosboxx.DOSBOX_X})
        self.assertEqual(sfxvolume.level(open(path, "rb").read()), sfxvolume.SL_DOSBOX_X)
        launch.prepare_patched_game(d, {dosboxx.SETTING: dosboxx.GOG})
        self.assertEqual(sfxvolume.level(open(path, "rb").read()), sfxvolume.GAME)

    def test_no_roster_or_no_pref_changes_nothing(self):
        d = tempfile.mkdtemp()
        self.addCleanup(os.rmdir, d)
        self.assertEqual(sfxvolume.set_roster(d, *sfxvolume.ravager_level()), [])
        self.assertIsNone(sfxvolume.level(build_gff({("CHAR", 15): b"x"})))
        self.assertIsNone(sfxvolume.level(build_gff({("PREF", 100): b"\0\0\x64"})))  # (too short)
        with open(os.path.join(d, "CHARSAVE.GFF"), "wb") as f:
            f.write(b"not a gff")
        self.addCleanup(os.remove, os.path.join(d, "CHARSAVE.GFF"))
        self.assertEqual(sfxvolume.set_roster(d, *sfxvolume.ravager_level()), [])


if __name__ == "__main__":
    unittest.main()
