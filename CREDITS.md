# Credits

## CleanYourTV

Everything here sits on top of [CleanYourTV](https://github.com/Gathin23/cleanyourtv), MIT licensed,
copyright Gathin. That repo is the launcher, the `config.xml` and theme system, the install and debloat
tooling, and the reason a TV can be usable without a factory reset. Gathin's email is on the repo if you
want to say thanks properly: gathint23@gmail.com.

This project is a patch. It changes 17 files under `launcher/` and nothing else. If you want the real
thing, go get the real thing first.

## What came from where

| Piece | Where it came from |
|---|---|
| Launcher, theme loader, dock logic, screensaver plumbing | CleanYourTV |
| Glass plate renderer, redrawn line icons, top bar layout | This repo |
| Idle-clock idle detection and the Home guard in `ServiceRepair` | This repo |
| The gear, Wi-Fi and 3x3 grid line icons | Drawn here as vector paths in `res/drawable/`, no icon pack, no traced artwork |
| The Outfit typeface | The Outfit Project Authors, SIL OFL 1.1, bundled by CleanYourTV |
| The wallpaper in the screenshots | Generated for this repo, no third-party images |

## Screenshots

Both screenshots are of a real TV running this patch. The background in them was drawn by
`tools/make-background.py`, which is in this repo. Running it produces the same file byte for byte, so
there is nothing to attribute and nothing borrowed from a wallpaper site.

App names and icons in the screenshots belong to their owners and are there because they happened to be
installed, nothing more.
