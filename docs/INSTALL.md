# Install

Two parts: the code patch, then the theme. You can run either without the other, but the theme on stock
CleanYourTV will not look like the screenshots because the glass renderer is in the patch.

## What you need

- JDK 17, a full JDK and not a JRE. The Android Gradle plugin wants `jlink`, and a JRE will answer
  `java -version` with a 17 while not having it.
- Android SDK with platform 34 and build-tools 34.0.0.
- `adb` that can see your TV, or the repo's `tools/tv.py` if stock `adb` is blocked on your machine.

## 1. Patch the launcher

```bash
git clone https://github.com/Gathin23/cleanyourtv.git
cd cleanyourtv
git checkout 57c00a40

git apply --check ../patch/tvos-skin.patch    # dry run
git apply ../patch/tvos-skin.patch
```

`--check` printing nothing means the patch applies clean. If it complains, your `main` has moved past the
commit this was cut against; try `git checkout 57c00a40` first, and if you want to track newer `main`,
`git apply -3` usually sorts it out.

## 2. Build

```bash
cd launcher
export JAVA_HOME=$(brew --prefix openjdk@17)         # macOS, Homebrew JDK is keg-only
export ANDROID_HOME=~/Library/Android/sdk

./gradlew --no-daemon assembleRelease
```

Output lands at `launcher/app/build/outputs/apk/release/app-release.apk`. It has to stay under 589,824
bytes. This patch adds a couple of small drawables and about 580 lines of Java, so it does.

If Gradle stops at `SDK location not found`, `launcher/build-and-install.sh` writes the gitignored
`local.properties` for you; doing it by hand means one line, `sdk.dir=/path/to/sdk`.

## 3. Install

Upstream's own way, which handles the Home handover:

```bash
TV_HOST=<your-tv-ip> launcher/build-and-install.sh
```

Already running the launcher and only want the new build?

```bash
adb install -r launcher/app/build/outputs/apk/release/app-release.apk
```

A signature mismatch (`INSTALL_FAILED_UPDATE_INCOMPATIBLE`) means the APK on the TV was built with a
different key. Uninstall and install, or rebuild with the same key.

## 4. Push the theme

```bash
TV_HOST=<your-tv-ip> tools/theme.sh ../theme
```

That copies `config.json` into the launcher's external files directory and restarts Home. To go back to
whatever was there before:

```bash
TV_HOST=<your-tv-ip> tools/theme.sh --reset
```

## 5. Check it took

- Home shows one row of apps sitting on a glass band at the bottom, with the row above it faded.
- Down on the remote brings the rest of the grid up.
- The top right has three round buttons: Wi-Fi, the 3x3 grid, the gear.
- Wait out `home_idle_clock_minutes` (ten minutes in the shipped theme) without touching the remote and
  the clock should fill the screen. Start a video first and it should not.

## Undo everything

```bash
cd cleanyourtv
git checkout -- .
cd launcher && ./gradlew assembleRelease
adb install -r app/build/outputs/apk/release/app-release.apk
TV_HOST=<your-tv-ip> tools/theme.sh --reset
```

The patch touches no manifest, no permission and no service, so a plain rebuild of stock gets you all the
way back.

## When something looks wrong

**Glass plates are flat grey.** The wallpaper bitmap was not available when the tile was drawn. Change the
wallpaper once, or restart Home, and it re-samples.

**No wallpaper at all, just a gradient.** Your `wallpapers/` folder has one image in it. Collection mode
needs at least two; add one or drop back to a single `wallpaper.jpg`.

**Whole screen takes the colour of the focused app.** That is `cinematic_home`, and it is on in some
themes. Turn it off in `config.json` and push again.

**Idle clock fires during playback.** Check `home_idle_clock_minutes` and that the audio stream is
actually active. The check reads the media stream, so a muted player that has stopped reporting playback
will not hold it off.
