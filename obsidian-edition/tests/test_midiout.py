"""The music device (midiout.py): the stored choice read (the default, a device number, an ALSA
port; anything else the default), DOSBox's `[midi]` lines for it, Windows' device names read
through winmm (a stand-in for it here), and the Loader's list of them."""

import ctypes
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsloader import midiout  # noqa: E402


class Winmm:
    """A stand-in for Windows' winmm: NAMES are its MIDI output devices (None: one that fails)."""

    def __init__(self, names):
        self.names = names
        self.asked = []

    def midiOutGetNumDevs(self):
        return len(self.names)

    def midiOutGetDevCapsW(self, number, caps, size):
        self.asked.append((number.value, size))
        if self.names[number.value] is None:
            return 2  # (MMSYSERR_BADDEVICEID)
        for at, unit in enumerate(self.names[number.value].encode("utf-16-le")[::2]):  # (plain letters)
            caps._obj.szPname[at] = unit
        return 0


class MidiOutTests(unittest.TestCase):
    def test_the_stored_choice(self):
        for value, device in ((None, "default"), ("default", "default"), ("", "default"), (" Default ", "default"),
                              (0, 0), (2, 2), ("2", 2), (" 7 ", 7), (255, 255), ("128:0", "128:0"),
                              ("014:01", "14:1")):
            self.assertEqual(midiout.parse(value), device, value)
        for value in (-1, 256, "256", True, False, 1.5, "two", "2;exit", "1:2:3", "128:", ":0", "1 2", "٣",
                      "128:0\nexit", [2], {"n": 2}, "1000:0"):
            self.assertIsNone(midiout.parse(value), value)
            self.assertEqual(midiout.setting({"midi_device": value}), "default", value)
        self.assertEqual(midiout.setting({}), "default")
        self.assertEqual(midiout.setting({"midi_device": "3"}), 3)

    def test_dosbox_lines(self):
        """Nothing for the default (GOG's own [midi] section stays); else the device as DOSBox's
        `midiconfig`, which its Windows MIDI handler reads as the device's number."""
        self.assertEqual(midiout.conf_lines({}), [])
        self.assertEqual(midiout.conf_lines({"midi_device": "default"}), [])
        self.assertEqual(midiout.conf_lines({"midi_device": "nonsense"}), [])
        self.assertEqual(midiout.conf_lines({"midi_device": 0}), ["[midi]", "midiconfig=0", ""])
        self.assertEqual(midiout.conf_lines({"midi_device": "4"}), ["[midi]", "midiconfig=4", ""])
        self.assertEqual(midiout.conf_lines({"midi_device": "128:0"}), ["[midi]", "midiconfig=128:0", ""])

    def test_windows_device_names(self):
        winmm = Winmm(["Microsoft GS Wavetable Synth", "VirtualMIDISynth #1", None, " MT-32 Synth Emulator "])
        self.assertEqual(midiout.devices(winmm), ["Microsoft GS Wavetable Synth", "VirtualMIDISynth #1", "",
                                                  "MT-32 Synth Emulator"])
        self.assertEqual([number for number, _ in winmm.asked], [0, 1, 2, 3])
        self.assertEqual({size for _, size in winmm.asked}, {84})  # (MIDIOUTCAPSW's size)
        self.assertEqual(ctypes.sizeof(midiout._Caps), 84)
        self.assertEqual(midiout.devices(Winmm([])), [])
        self.assertIsNone(midiout.devices(object()))  # (a library without the calls)
        if os.name != "nt":
            self.assertIsNone(midiout.devices())  # (no winmm here: the player types the number)

    def test_the_loaders_list(self):
        names = ["Microsoft GS Wavetable Synth", "", "MT-32 Synth Emulator"]
        self.assertEqual(midiout.labels(names), ["Windows' default", "0: Microsoft GS Wavetable Synth", "1",
                                                 "2: MT-32 Synth Emulator"])
        self.assertEqual(midiout.labels(names, 2), midiout.labels(names))
        gone = midiout.labels(names, 5)  # (a device chosen once and not there now: shown, and why it is silent)
        self.assertEqual(gone[-1], "5: (no such device now: no music)")
        self.assertEqual(len(gone), 5)
        for device in ("default", 0, 1, 2, 5, "128:0"):
            self.assertEqual(midiout.from_label(midiout.label(device, names)), device, device)
            self.assertEqual(midiout.from_label(midiout.label(device, None)), device, device)
        self.assertEqual(midiout.from_label(""), "default")
        self.assertEqual(midiout.from_label(" 3 "), 3)
        self.assertIsNone(midiout.from_label("the loud one"))


if __name__ == "__main__":
    unittest.main()
