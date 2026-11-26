# add_dosbox_x.py ZIP TOP: puts DOSBox-X for Windows in the mod's zip, as a release gives it (used by
# release.yml and test-package.yml, so a test download is the release's package).
#
# The 64-bit Windows build of DOSBOX_X_VERSION, unchanged, from DOSBox-X's own release, goes in ZIP's
# TOP/dosbox-x/ folder (dosbox-x.exe, beside the Loader's dsloader folder: dsloader/dosboxx.py's
# BUNDLED_DIR) with its licence (COPYING.txt, GPL 2), its README.txt and SOURCE.txt, which says where
# its source is. DOSBox-X's own archive of the same tag is saved as dosbox-x-source-VERSION.tar.gz in
# the current folder, for the workflow to offer beside the zip (GPL 2, section 3). DOSBOX_X_SHA256,
# when set, is checked against the download (each run prints what it got). The environment's
# DOSBOX_X_VERSION is the version; GITHUB_ENV, when set, gets DBX_SOURCE (the source file's name).
import hashlib, io, os, sys, urllib.request, zipfile

BASE = "https://github.com/joncampbell123/dosbox-x"
TAKE = {"bin/x64/Release SDL2/dosbox-x.exe": "dosbox-x.exe", "COPYING": "COPYING.txt",
        "bin/x64/Release SDL2/README.txt": "README.txt"}


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=300) as r:
        return r.read()


def source_text(version: str, tag: str) -> str:
    return (f"DOSBox-X {version}, the 64-bit Windows build (dosbox-x.exe), as DOSBox-X's own release gives it,\r\n"
            f"unchanged. DOSBox-X is free software under the GNU General Public License, version 2\r\n"
            f"(COPYING.txt). Its source code for this version:\r\n\r\n"
            f"  {BASE}/tree/{tag}\r\n\r\n"
            f"and a copy of it beside this mod's download (dosbox-x-source-{version}.tar.gz on the same\r\n"
            f"page). DOSBox-X's site: https://dosbox-x.com/\r\n\r\n"
            f"The Obsidian Edition's Loader starts it with its own configuration (obsidian.conf, written\r\n"
            f"here at each start). To play in GOG's DOSBox instead, choose it on the Loader's Options tab\r\n"
            f"(Engine).\r\n")


def main() -> None:
    zip_path, top = sys.argv[1], sys.argv[2]
    version = os.environ["DOSBOX_X_VERSION"]
    tag = "dosbox-x-v" + version
    build = fetch(f"{BASE}/releases/download/{tag}/dosbox-x-vsbuild-win64-{version}-portable.zip")
    got = hashlib.sha256(build).hexdigest()
    print(f"DOSBox-X {version} for Windows: sha256 {got}")
    want = os.environ.get("DOSBOX_X_SHA256", "")
    if want and got != want:
        sys.exit(f"expected {want}")
    source = f"dosbox-x-source-{version}.tar.gz"
    with open(source, "wb") as f:
        f.write(fetch(f"{BASE}/archive/refs/tags/{tag}.tar.gz"))
    with zipfile.ZipFile(io.BytesIO(build)) as src, zipfile.ZipFile(zip_path, "a", zipfile.ZIP_DEFLATED) as out:
        names = set(src.namelist())
        for name, to in TAKE.items():
            if name not in names:
                sys.exit(f"DOSBox-X's zip has no {name}")
            out.writestr(f"{top}/dosbox-x/{to}", src.read(name))
        out.writestr(f"{top}/dosbox-x/SOURCE.txt", source_text(version, tag))
    if os.environ.get("GITHUB_ENV"):
        with open(os.environ["GITHUB_ENV"], "a") as f:
            f.write(f"DBX_SOURCE={source}\n")


if __name__ == "__main__":
    main()
