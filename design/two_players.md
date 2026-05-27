# Two-player support

I want to extend retro-console to support two players. 

## Updated input device to key mapping

`KEY_MAPPING` in `settings.py` is a flat dict with keys prefixed by `P1_` or `P2_`, using
the logical button names below. Env vars injected into game subprocesses follow the same
naming convention (e.g. `RETRO_KEY_P1_UP`, `RETRO_KEY_P2_A`).

- Player 1:
  - joystick: up=w (P1_UP), down=s (P1_DOWN), left=a (P1_LEFT), right=d (P1_RIGHT)
  - Row 1: red=space (P1_A), yellow=g (P1_B), green=h (P1_C), blue=j (P1_D)
  - Row 2: red=t (P1_E), yellow=y (P1_F), green=u (P1_G), blue=i (P1_H)
- Player 2:
  - joystick: up=8 (P2_UP), down=2 (P2_DOWN), left=4 (P2_LEFT), right=6 (P2_RIGHT)
  - Row 1: red=enter (P2_A), yellow=k (P2_B), green=l (P2_C), blue=; (P2_D)
  - Row 2: red=o (P2_E), yellow=p (P2_F), green=[ (P2_G), blue=] (P2_H)

This needs to be updated in several locations:
- in the antimicrox configuration file
- in `settings.py`
- in existing games which hard-code keystroke values or env var names (old `RETRO_KEY_UP` → new `RETRO_KEY_P1_UP`, etc.)
- in the docs

The console UI listens to both players' inputs and responds to them identically (e.g.
`P1_UP` and `P2_UP` both scroll up in the game select screen). The only exception is the
high-score screen — see below.

## Updated game metadata 

Games will need to specify one or both of:

- tool.retro.single_player = true
- tool.retro.two_player = true

If neither is specified, `single_player = true` is assumed and a warning is logged. The
detail pane for the game select screen should indicate whether the game can be played by one
player, two players, or both. The console UI will not handle selection of player count nor
pass any such value to the game; that logic is up to the game.

Update existing games to have `tool.retro.single_player = true`.

### Two-player game result contract

When a two-player game ends, `result.json` may optionally include a `"winner"` key with
value `1` or `2`. When present and valid, only the corresponding player's input is active on
the high-score screen. When absent or invalid, player 1 has control. Document this in the
docs under Game Developer.

## Updated docs

Update all of the above changes in the docs. Include a new section in the docs under Console
Manager explaining step-by-step how to add new games to the console as regular files in the
repo. Focus on the use case of a teacher who has student-authored games (which may have
validation issues) wanting to add them to the console.

At startup, retro-console should detect whether the installed antimicrox profile
(`/opt/retro-console/config/gamecontroller.amgp`) is newer than antimicrox's last restart
(obtainable via `systemctl --user show antimicrox --property=ActiveEnterTimestamp`). If so,
automatically run `systemctl --user restart antimicrox` and log that this happened. Add a
note to the console manager docs explaining the key-mapping → antimicrox relationship, so
operators understand why this restart occurs.

