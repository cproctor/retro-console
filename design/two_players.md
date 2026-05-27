# Two-player support

I want to extend retro-console to support two players. 

## Updated input device to key mapping

The new key mapping from the joystick and buttons to keystrokes is as follows:

- Player 1:
  - joystick:
    - right: d
    - up: w
    - left: a
    - down: s
  - Row 1 buttons: 
    - red: space
    - yellow: g
    - green: h
    - blue: j
  - Row 2 buttons:
    - red: t
    - yellow: y
    - green: u
    - blue: i
- Player 2:
  - joystick:
    - right: 6
    - up: 8
    - left: 4
    - down: 2
  - Row 1 buttons: 
    - red: enter
    - yellow: k
    - green: l
    - blue: ;
  - Row 2 buttons:
    - red: o
    - yellow: p
    - green: [
    - blue: ]

This needs to be updated in several locations: 
- in the antimicrox configuration file (will we need to reload the systemd unit?)
- in the default settings for games 
- in existing games which hard-code keystroke values
- in the docs

## Updated game metadata 

Games will need to specify one or both of:

- tool.retro.single_player = true
- tool.retro.two_player = true

The default for each is false; if neither is specified validation should fail, 
as the game is unplayable. The detail pane for the game select screen should also indicate 
whether the game can be played by one player, two players, or both. The console ui
will not handle any kind of selection on whether the game should be played by one or two, nor
pass any such value to the game; that logic is up to the game. 

Update existing games to have `tool.retro.single_player = true`.

## Updated docs

Update all of the above changes in the docs. Include a new section in the docs under 
Console Manager explaining step-by-step how to add new games to the console. Focus on the
use case of a teacher who has student-authored games (which may have validation issues)
wanting to add them to the console.
the 
