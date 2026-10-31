# What I actually tested

One real TV, 1080p, Android TV 9, 1 GB of RAM. Everything below was done with the remote or with the
launcher's own tooling, on a set that was already debloated and had this launcher as Home.

Pass means I saw it work. Anything I only reasoned about is marked as such rather than quietly left out.

## Build and install

| Check | Result |
|---|---|
| Clean `assembleRelease` from the patch on `57c00a40` | Pass |
| APK under the 589,824-byte gate | Pass |
| Install over an existing build, settings and theme kept | Pass |
| Cold boot straight into this Home | Pass |

## Layout

| Check | Result |
|---|---|
| Dock on the bottom row, one row visible | Pass |
| Row above fades instead of being cut off | Pass |
| Down brings the grid up, Up returns to the shelf | Pass |
| Grid still even with 5 apps, 6 apps, and a full row | Pass |
| Second row of labels readable over a bright wallpaper | Pass, after the shadow in `item_app.xml` |

## Focus

| Check | Result |
|---|---|
| Left/Right stops at both ends without wrapping to the wrong row | Pass |
| Up from the first row lands on the top bar, not off screen | Pass |
| Up from the shelf goes to the row above, not the top bar | Pass |
| Long press on a tile with the real remote opens the tile menu | Pass |
| Long press injected with `input keyevent --longpress` | Fails on this build, arrives as a short press. Known Android TV problem, not this patch; use the remote or `sendevent`. |

## Glass

| Check | Result |
|---|---|
| Plates take the colour under them, visibly different across one row | Pass |
| Re-sample on wallpaper change | Pass |
| Re-sample after the shelf moves | Pass |
| No visible seam where two plates meet | Pass, after sampling at the plate's own bounds |
| Dropped frames while scrolling | None observed, but I did not measure; this is a 1 GB set and the sampling is a bitmap read per plate |

## Top bar

| Check | Result |
|---|---|
| Three buttons, evenly spaced, Settings rightmost | Pass |
| Focus ring on the round buttons | Pass |
| Library button opens the library over Home | Pass |
| Wi-Fi button opens Wi-Fi settings | Pass |
| Settings opens the launcher's settings | Pass |

## App library

| Check | Result |
|---|---|
| A TV app installed by `adb install` shows up | Pass |
| A phone-only app (no leanback category) shows up | Pass, this is the change |
| Uninstalling an app removes it from the grid | Pass, after the reload-on-open change |
| Library over Home is still readable with a bright wallpaper | Pass, after the scrim change |

## Clock and screensaver

| Check | Result |
|---|---|
| Idle clock fires after the configured idle time | Pass |
| Clock does not fire while audio is playing | Pass |
| Clock fires within a minute of the audio stopping | Pass |
| Clock does not fire while a video is in the foreground | Pass; Home is paused then, so the timer does not exist |
| Back opens the clock with `back_opens_clock` on | Pass, this is the fix |
| Back does nothing with it off | Pass |
| Clock over a static wallpaper, over a collection | Pass |

## Keys

| Check | Result |
|---|---|
| Mapping a remote button to `library` | Pass |
| Mapping a button to a package still works | Pass |
| The button mapped to `library` does nothing when this is not Home | Pass, this is the guard |
| Volume and mute untouched | Pass |

## Self-heal and Home handover

| Check | Result |
|---|---|
| `force-stop` the launcher, the accessibility service comes back | Pass, about nine seconds |
| `adb install -r`, the service entry survives | Pass |
| Switch to the stock launcher: this launcher stops re-adding its key filter | Pass, this is the `ServiceRepair` guard |
| Switch back: the filter returns | Pass |
| Pressing a mapped button while the stock launcher is Home | Pass, the button does what the stock launcher wants, nothing swallowed |

## Not tested

Being straight with you, because these are the holes:

- **Any 4K set.** All of this was tuned at 1080p. Tile sizes and the glass sampling scale, but I have not
  looked at them on a 4K panel.
- **A set with 2 GB or more.** The whole design assumes tight memory. It should only get easier.
- **A long soak.** The idle clock was exercised over minutes, not hours. Nobody has left this on for a
  week with the screensaver armed the whole time.
- **Power loss rather than `adb reboot`.** Pulling the plug is not the same code path as a clean reboot and
  I did not try it.
- **Any launcher other than this one and the one the TV shipped with.**
- **Right-to-left languages.** The shelf and the top bar were never looked at in one.
