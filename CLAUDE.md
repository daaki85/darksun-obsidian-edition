# Notes for Claude

- **Before any in-game test** (anything run in DOSBox: seeing a fix work, a screenshot, a play
  check), read `playtest/PLAYTESTING.md` in full and follow it. Its tools are in `playtest/`.
  After every play, add everything learned to it (controls, screens, routes, timings, script
  details, tool changes, stalls) and commit and push, so it isn't lost with the container (an
  earlier version of the guide was).
- `playtest/` is outside `obsidian-edition/`, so it never ships in a release zip (the zip is that
  folder alone). Keep it that way.
