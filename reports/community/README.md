# Notes for other Dark Sun projects

Reports written for the other public Dark Sun projects that read this repository. Their own
cross-reads of this repository pick these notes up, and each one can also be posted as an issue.

- [OpenDS](https://github.com/VirInvictus/opends) (MIT): a toolkit, bugfix patches (darkfix) and
  reverse-engineering notes for both games. It reads this repository and darksun-recompiled
  (its `docs/reports/daaki85-crossread-2026-11-23.md`).
- [yuan-ti](https://github.com/CalvinRodo/yuan-ti) (MIT, Calvin Rodo): an engine project whose
  script repairs this mod uses. Its `.github/instructions/ref_notes_from_obsidian.md` relays our
  findings.

**Rules for what goes in.** Facts, file offsets and observations only, in our own words. No game data,
nothing from the private installation-files repository, no personal details. A note says which game
release it was checked against (GOG 1.10 unless it says otherwise).

Each note is a file named `YYYY-MM-DD-<project>-<subject>.md`, with a status line saying whether it
has been posted anywhere.

## Notes

| Date | For | Subject | Status |
|---|---|---|---|
| 2026-11-24 | OpenDS | [Cure Critical Wounds' dice and the GF123 flag (Alhena)](2026-11-24-opends-cure-and-alhena.md) | not posted |

Older drafts for OpenDS, from before this folder: [the exchange draft](../opends-exchange-draft-2026-11-17.md)
and [six issue texts](../opends-issues-draft-2026-11-18.md).

## What else would help them (ideas, 2026-11-24)

Most useful first:

1. **Runtime QA for OpenDS's darkfix betas.** darkfix-ds1 0.2.0-beta.4 ships ten fixes switched off
   until someone plays them (their issue #18; `docs/qa/qa-packet-ds1-script-repairs-beta.md` asks for
   reports as `beta QA: <site> <pass/fail>`). Our DOSBox play rig (`playtest/`) and saves can run
   those checks, and several of the same repairs are already in our Loader. A pass/fail list with
   what was seen is the one thing they can't produce themselves yet.
2. **An update to our October notes for yuan-ti.** yuan-ti carries our notes of 20 October
   (`.github/instructions/ref_notes_from_obsidian.md`, at their commit 9c1952b). Some of it has
   changed since: its section 1.3 says Hold Undead holds the living, which we later found is not so
   (the area code's sifting at 7A897h drops a living target first; DEVELOPMENT-CONTENT.md). An errata
   list plus what we have found since (thief skills, the dice log, rules) keeps them from building on
   the old claim.
3. **Things in our files that are not in OpenDS's.** The script buffer's size (our exchange draft,
   item 3; their detour repairs grow scripts), and a fresh comparison of GAME-BUGS.md and
   DEVELOPMENT-*.md against their known-bugs.md since their 23 November cross-read.
4. **Wake of the Ravager.** The Ravager port's findings (the party transfer, CHARSAVE.GFF for the
   active party, the rules of the second game) feed their DS2 work, whose headline is the mines
   elevator bug (their roadmap phase 7).
5. **The dice-log replay.** Their cross-read names the missing pieces (seed capture at DS:4124h, a
   replay, a diff). Whatever we build for it, described as facts, helps both.
