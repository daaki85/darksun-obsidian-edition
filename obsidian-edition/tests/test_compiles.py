"""Every module of the Loader compiles (the window's too, which no other test imports: it
needs tkinter)."""

import glob
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CompileTests(unittest.TestCase):
    def test_every_module(self):
        files = sorted(glob.glob(os.path.join(ROOT, "dsloader", "*.py")))
        self.assertTrue(files)
        for path in files:
            with self.subTest(module=os.path.basename(path)):
                with open(path, encoding="utf-8") as f:
                    compile(f.read(), path, "exec")


if __name__ == "__main__":
    unittest.main()
