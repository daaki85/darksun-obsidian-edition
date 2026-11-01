# Notes for Claude

- **Before any in-game test** (anything run in DOSBox: seeing a fix work, a screenshot, a play
  check), read `playtest/PLAYTESTING.md` in full and follow it. Its tools are in `playtest/`.
  When a test turns up a new kind of stall, add it there and commit and push, so it isn't lost
  with the container (an earlier version of the guide was).
- `playtest/` is outside `obsidian-edition/`, so it never ships in a release zip (the zip is that
  folder alone). Keep it that way.
