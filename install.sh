#!/bin/bash
set -euo pipefail

root=$(cd -- "$(dirname -- "$0")" && pwd)
service=/userdata/system/services/retrogrzmot_led
ports=/userdata/roms/ports
app="$ports/.data/retrogrzmot-lighting"
launcher="$ports/Sterowanie podświetleniem RETROGRZMOTA.sh"

if [[ $(id -u) != 0 || ! -d /userdata/system ]]; then
    printf '%s\n' 'Run this on Batocera as root.' >&2
    exit 1
fi
command -v batocera-services >/dev/null
test -x /usr/bin/flock
/usr/bin/python3 -c 'import pygame; from pygame._sdl2 import controller; from rpi_ws281x import PixelStrip; assert callable(PixelStrip._cleanup)'
test -r /usr/share/fonts/dejavu/DejaVuSans.ttf
test -r /usr/share/fonts/dejavu/DejaVuSans-Bold.ttf
bash -n "$root/retrogrzmot_led"
sh -n "$root/launch.sh"
if [[ ${1:-} == --check ]]; then
    printf '%s\n' 'Batocera prerequisites OK.'
    exit 0
fi
if [[ $# != 0 ]]; then
    printf '%s\n' 'Usage: bash install.sh [--check]' >&2
    exit 2
fi

mkdir -p /userdata/system/services "$app"
backup=$(mktemp -d /userdata/system/retrogrzmot-ports-led-backup.XXXXXX)
for entry in "$service" "$app/panel.py" "$launcher"; do
    if [[ -e "$entry" ]]; then
        cp -p -- "$entry" "$backup/"
    fi
done

cp -- "$root/retrogrzmot_led" "$backup/service.new"
cp -- "$root/panel.py" "$backup/panel.new"
cp -- "$root/launch.sh" "$backup/launcher.new"
chmod 755 "$backup/service.new" "$backup/launcher.new"
chmod 644 "$backup/panel.new"
"$backup/service.new" get logo --brightness
"$backup/service.new" get base --brightness

restore() {
    for entry in "$service" "$app/panel.py" "$launcher"; do
        original="$backup/${entry##*/}"
        if [[ -f "$original" ]]; then
            cp -p -- "$original" "$backup/restore"
            mv -T -- "$backup/restore" "$entry"
        else
            rm -f -- "$entry"
        fi
    done
}

if ! (mv -T -- "$backup/service.new" "$service" &&
      mv -T -- "$backup/panel.new" "$app/panel.py" &&
      mv -T -- "$backup/launcher.new" "$launcher" &&
      batocera-services enable retrogrzmot_led); then
    restore
    printf 'Installation failed. Previous files restored from %s\n' "$backup" >&2
    exit 1
fi

printf 'Installed. Backups: %s\n' "$backup"
printf '%s\n' 'Restart Batocera from the menu. Open Ports → Sterowanie podświetleniem RETROGRZMOTA.'
