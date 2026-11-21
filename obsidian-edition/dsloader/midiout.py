"""The music device: where DOSBox sends the game's General MIDI music.

GOG's DOSBox 0.74 has no synthesizer of its own: its `[midi]` section (`mididevice=default`,
`midiconfig=` empty) opens Windows' MIDI Mapper, which plays through the Microsoft GS Wavetable
Synth unless the player has set another. `midiconfig=N` opens the Nth MIDI output device instead
(DOSBox's midi_win32.h: `midiOutOpen` with that number, counted from 0 as `midiOutGetDevCaps`
counts them), which is how a soft synth with a soundfont, or an MT-32 driver, the player installed
is chosen. A number with no device behind it leaves the game without music (DOSBox opens nothing
and says nothing), so the Loader shows the devices' names where it can read them: on Windows,
through winmm with ctypes. A Linux DOSBox (0.74-3: ALSA) takes a sequencer port there,
"client:port" as `aconnect -o` lists them.

The choice is `midi_device` in settings.json: "default" (or missing), a device number, or an ALSA
port "128:0"; anything else is taken as the default. It applies the next time the game is started
(launch.write_conf)."""

import ctypes
import re
from typing import List, Optional, Union

DEFAULT = "default"
SETTING = "midi_device"
MOST = 255  # (a device number: Windows' are small; DOSBox reads an unsigned one)
_PORT = re.compile(r"(\d{1,3}):(\d{1,3})$")  # (an ALSA port; DOSBox keeps 9 characters of it)

Device = Union[str, int]


def parse(value: object) -> Optional[Device]:
    """VALUE as a music device: "default" (also for nothing at all), a device number, or an ALSA
    port "client:port"; None when it is none of these."""
    if value is None:
        return DEFAULT
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if 0 <= value <= MOST else None
    if not isinstance(value, str):
        return None
    text = value.strip()
    if text.lower() in ("", DEFAULT):
        return DEFAULT
    if text.isascii() and text.isdigit():
        return int(text) if int(text) <= MOST else None
    port = _PORT.match(text) if text.isascii() else None
    return f"{int(port.group(1))}:{int(port.group(2))}" if port else None


def setting(settings: dict) -> Device:
    """The music device the settings ask for; "default" when they don't, or ask for none there is."""
    device = parse(settings.get(SETTING))
    return DEFAULT if device is None else device


def conf_lines(settings: dict) -> List[str]:
    """DOSBox's music device, over GOG's settings: nothing for the default (GOG's own `[midi]`),
    else `midiconfig` naming the device."""
    device = setting(settings)
    return [] if device == DEFAULT else ["[midi]", f"midiconfig={device}", ""]


class _Caps(ctypes.Structure):
    """Windows' MIDIOUTCAPSW (84 bytes; the name 32 UTF-16 units, ending at a zero)."""
    _fields_ = [("wMid", ctypes.c_ushort), ("wPid", ctypes.c_ushort), ("vDriverVersion", ctypes.c_uint),
                ("szPname", ctypes.c_uint16 * 32), ("wTechnology", ctypes.c_ushort), ("wVoices", ctypes.c_ushort),
                ("wNotes", ctypes.c_ushort), ("wChannelMask", ctypes.c_ushort), ("dwSupport", ctypes.c_uint)]


def _name(caps: _Caps) -> str:
    units = list(caps.szPname)
    units = units[:units.index(0)] if 0 in units else units
    return b"".join(u.to_bytes(2, "little") for u in units).decode("utf-16-le", errors="replace").strip()


def _winmm():
    """Windows' multimedia library, or None where there is none (not Windows)."""
    try:
        return ctypes.WinDLL("winmm")  # type: ignore[attr-defined]
    except (AttributeError, OSError):
        return None


def devices(winmm=None) -> Optional[List[str]]:
    """The names of Windows' MIDI output devices, in the order DOSBox numbers them (the first is
    0); None where they can't be read (not Windows: the player types the number or the port). A
    device that won't tell its name is listed by its number alone."""
    winmm = _winmm() if winmm is None else winmm
    if winmm is None:
        return None
    try:
        count = int(winmm.midiOutGetNumDevs())
        names = []
        for number in range(min(count, MOST + 1)):
            caps = _Caps()
            failed = winmm.midiOutGetDevCapsW(ctypes.c_size_t(number), ctypes.byref(caps), ctypes.sizeof(caps))
            names.append("" if failed else _name(caps))
        return names
    except (AttributeError, OSError, ValueError, ctypes.ArgumentError):
        return None


DEFAULT_LABEL = "Windows' default"


def label(device: Device, names: Optional[List[str]]) -> str:
    """How the Loader's list shows DEVICE: the default, or "2: its name" (a number with no device
    behind it now says so)."""
    if device == DEFAULT:
        return DEFAULT_LABEL
    if isinstance(device, int) and names is not None:
        if device < len(names):
            return f"{device}: {names[device]}" if names[device] else str(device)
        return f"{device}: (no such device now: no music)"
    return str(device)


def labels(names: List[str], chosen: Device = DEFAULT) -> List[str]:
    """The Loader's list: the default, each device, and the chosen one if it is none of them."""
    out = [DEFAULT_LABEL] + [label(number, names) for number in range(len(names))]
    mine = label(chosen, names)
    return out if mine in out else out + [mine]


def from_label(text: str) -> Optional[Device]:
    """The device a line of the list (or what the player typed) stands for; None if none."""
    text = text.strip()
    if text == DEFAULT_LABEL:
        return DEFAULT
    return parse(text.split(": ", 1)[0] if ": " in text else text)
