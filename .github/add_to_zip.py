"""add_to_zip.py ZIP NAME FILE: FILE added to ZIP as NAME (the release workflow's: the patch notes'
web page, made at the repository's root, put in the release zip's folder)."""
import sys
import zipfile

zip_path, name, source = sys.argv[1:4]
with zipfile.ZipFile(zip_path, "a", zipfile.ZIP_DEFLATED) as z:
    if name in z.namelist():
        sys.exit(f"{name} is in {zip_path} already")
    z.write(source, name)
print(f"{source} added to {zip_path} as {name}")
