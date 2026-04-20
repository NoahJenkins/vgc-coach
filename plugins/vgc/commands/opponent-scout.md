---
description: Scout likely opponent shells, techs, and prep risks from public information.
---

# VGC Opponent Scout

Use `$vgc-opponent-scout` immediately for this request.

If "$ARGUMENTS" is non-empty, treat it as the user's scouting request and start there.
If "$ARGUMENTS" is empty, ask only for the missing player, archetype, public team info, or matchup context needed to proceed.

Preserve the skill's contract:

- separate confirmed public info from extrapolation
- build the scout around the few tendencies that materially change prep
- keep low-confidence reads broad and say so directly
- do not imply private scouting access or exact closed-team certainty

Recommended start:

`Use $vgc-opponent-scout to scout this Pokemon Champions opponent, archetype, or public team trail and turn it into prep notes. $ARGUMENTS`
