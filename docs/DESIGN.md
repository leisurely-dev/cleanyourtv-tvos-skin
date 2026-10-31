# What the patch touches

17 files, all under `launcher/`. Nothing outside it, no manifest change, no new dependency.

The point of this page is so you can read the diff without reverse-engineering my intent from 580 lines of
Java.

## The shelf

**`AppAdapter.java`** is where the bottom shelf comes from. Upstream decides "is this tile in the dock" by
its position in the list (`position < COLUMNS`). That only works while the dock is the first row. The
patch swaps every one of those checks for a membership test against the dock list, which is correct no
matter where the dock sits, and then orders the rows so the dock comes last. The row above it fades at its
bottom edge so you can tell there is more to scroll to.

**`DockDecoration.java`** follows the shelf instead of the old top row. Two lines, but without them the
highlight lands in the wrong place.

**`glass_panel.xml`** is the band the shelf sits on: a rounded rectangle with a slightly brighter top
edge, drawn under the tiles rather than behind each one.

## The glass

**`GlassPlateDrawable.java`** (new, the biggest single addition) is the renderer. For a given tile it
takes the wallpaper bitmap, samples the region the tile covers, averages and lifts it a step in lightness,
and draws that colour back at low alpha with a one-pixel lighter border and a rounded corner. Re-sampled
when the wallpaper changes or the shelf moves.

No blur. A blur on a 1 GB TV is a frame budget you do not have, and it also does not look like glass. It
looks like frosted plastic. Sampling keeps the actual picture visible through the plate, which is the
whole effect.

**`GlassView.java`** wires it up: which views get a plate, when to re-sample, and what to fall back to if
the wallpaper is not available.

## The header

**`activity_main.xml`** changes the clock and date typography, and makes room in the top bar for a third
button.

- Clock goes 52sp to 48sp, letter spacing loosens slightly, tabular figures on so the digits do not jitter
  as the minute changes, and a soft shadow so it survives a bright wallpaper.
- Date drops to 13sp and loses most of its letter spacing. It reads as a caption under the clock instead
  of a label shouting next to it.
- The top bar gets the library button, between Wi-Fi and Settings. Settings stays rightmost always.

**`item_app.xml`** adds the same shadow to app labels, at higher alpha, because labels over a bright part
of a wallpaper were unreadable.

**`ic_settings.xml`** is the hollow gear: twenty teeth on the outside, three spokes, a pierced hub in the
middle. The stock filled gear reads as a solid blob at 22dp. This one is drawn so the wallpaper shows
through the middle of it, which is what makes it look like an icon instead of a sticker.

**`ic_wifi.xml`** goes to thin arcs for the same reason.

**`ic_apps_grid.xml`** (new) is the library button. Same 3x3 of rounded squares as the existing
`ic_apps`, but drawn at 16/24 of the viewport instead of 19.6/24, so it does not read heavier than the
Wi-Fi arcs and the gear it sits between.

**`ic_apps.xml`** gets a small weight adjustment to match.

## The app library

**`AppLibraryDialog.java`** does three things: the scrim behind the dialog goes from 0.3 to 0.5 so the
wallpaper stops competing with the grid; the list reloads every time it opens instead of once per
process, so an app you installed thirty seconds ago is there; and it looks for both TV and phone launch
categories, so sideloaded phone apps show up too. Upstream only asked for the TV category, which meant a
phone-only APK installed over ADB was invisible.

## Behaviour

**`MainActivity.java`** carries most of it.

- The idle clock used to fire on "no input for N minutes". It now checks whether anything is playing
  before it takes the screen, and defers sixty seconds if so. Video in the foreground pauses Home anyway,
  so this is belt and braces for audio you started from somewhere else.
- A new intent action, `OPEN_LIBRARY`, opens the library from outside. It refuses to run unless this
  launcher is the only enabled Home, because otherwise a leftover shortcut can pull this launcher up over
  somebody else's home screen, which looks exactly like a bug even though every step was intentional.
- Back opens the clock when `back_opens_clock` is on. On builds where that key defaulted off and nothing
  said so, the button appeared dead.

**`RemoteKeys.java`** adds one action word, `library`, so a remote button can be mapped to the library
without opening a package. Six lines including the case label.

**`ServiceRepair.java`** gets the guard that made me write this patch in the first place. It re-adds the
launcher's accessibility service after a force-stop, which is good when this is your home screen and bad
when it is not: switch to the stock launcher and the filter comes back anyway, swallowing a button on a
desktop that knows nothing about it. `isOnlyHome()` counts enabled Home activities with
`queryIntentActivities` and skips the repair when there is more than one. `resolveActivity` is the wrong
tool here, it returns the system preference and that preference is stale right after a switch.

## Resources

**`values/config.xml`** documents the new `library` action word in the `app_keys` help text. One line of
docs, no new key.

**`values-zh-rCN/strings.xml`** puts the year back in the Home date for Chinese. The one-line date under
a big clock carries no year, and on a TV people leave running for months that turns out to matter.
