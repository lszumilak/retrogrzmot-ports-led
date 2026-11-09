#!/usr/bin/env python3
import os
import signal
import subprocess
import sys

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame
from pygame._sdl2 import controller

SERVICE = "/userdata/system/services/retrogrzmot_led"
FONT = "/usr/share/fonts/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"
PALETTE = (
    ("amber", "Bursztynowy", "Amber", "#ff8020"),
    ("warm-white", "Ciepły biały", "Warm white", "#ffd29b"),
    ("red", "Czerwony", "Red", "#ff0000"),
    ("green", "Zielony", "Green", "#00ff00"),
    ("blue", "Niebieski", "Blue", "#0069ff"),
    ("cyan", "Turkusowy", "Cyan", "#00ffff"),
    ("purple", "Fioletowy", "Purple", "#af2dff"),
)
ZONES = ("logo", "base")
EFFECTS = {
    "steady": ("Retro Bursztyn", "RetroAmber"),
    "rider": ("Retro Nieustraszony", "Retro Rider"),
    "flash": ("Retro Grzmoty", "Retro Thunder"),
}
ACTIONS = {
    pygame.CONTROLLER_BUTTON_DPAD_UP: "up",
    pygame.CONTROLLER_BUTTON_DPAD_DOWN: "down",
    pygame.CONTROLLER_BUTTON_DPAD_LEFT: "left",
    pygame.CONTROLLER_BUTTON_DPAD_RIGHT: "right",
    pygame.CONTROLLER_BUTTON_A: "enter",
    pygame.CONTROLLER_BUTTON_B: "back",
}
KEYS = {
    pygame.K_UP: "up", pygame.K_DOWN: "down",
    pygame.K_LEFT: "left", pygame.K_RIGHT: "right",
    pygame.K_RETURN: "enter", pygame.K_ESCAPE: "back", pygame.K_BACKSPACE: "back",
}


def service(*args):
    result = subprocess.run([SERVICE, *args], check=True, capture_output=True,
                            text=True, timeout=5)
    return result.stdout.strip()


def polish_language():
    try:
        language = subprocess.run(["batocera-settings-get", "system.language"],
                                  capture_output=True, text=True, timeout=2).stdout
    except (OSError, subprocess.TimeoutExpired):
        language = ""
    return (language.strip() or os.environ.get("LANG", "")).lower().startswith("pl")


class Menu:
    def __init__(self, polish, command=service):
        self.polish = polish
        self.command = command
        self.zone = None
        self.index = 0
        self.settings = None
        self.message = ""

    def tr(self, pl, en):
        return pl if self.polish else en

    def zone_names(self):
        return (self.tr("Podświetlenie logo RETROGRZMOT", "RETROGRZMOT logo lighting"),
                self.tr("Podświetlenie podstawy RETROGRZMOTA", "RETROGRZMOT base lighting"))

    def rows(self):
        if self.zone is None:
            return [(name, "›", None) for name in self.zone_names()]
        power, colour, effect, brightness = self.settings
        entry = next(item for item in PALETTE if item[0] == ("red" if effect == "rider" else colour))
        effect_name = self.tr(*EFFECTS[effect])
        return [
            (self.tr("Włącz / wyłącz", "Lighting on / off"),
             self.tr("Włączone", "On") if power == "on" else self.tr("Wyłączone", "Off"), None),
            (self.tr("Jasność", "Brightness"), "30–100%" if effect == "flash" else f"{brightness}%", None),
            (self.tr("Kolor podświetlenia", "Lighting colour"), self.tr(entry[1], entry[2]), entry[3]),
            (self.tr("Efekt podświetlenia", "Lighting effect"), effect_name, None),
            (self.tr("Ustawienia fabryczne", "Factory settings"), self.tr("Przywróć bursztyn 3%", "Restore amber at 3%"), None),
        ]

    def read_zone(self, zone):
        power, colour, effect, raw_brightness = self.command("get", zone, "--brightness").split()
        brightness = int(raw_brightness)
        if power not in ("on", "off") or colour not in [item[0] for item in PALETTE] or effect not in EFFECTS or not 0 <= brightness <= 100:
            raise ValueError("Unexpected lighting configuration")
        return power, colour, effect, brightness

    def handle(self, action):
        self.message = ""
        if action == "back":
            if self.zone is None:
                return False
            self.index = ZONES.index(self.zone)
            self.zone = None
        elif action in ("up", "down"):
            self.index = (self.index + (-1 if action == "up" else 1)) % len(self.rows())
        elif action in ("left", "right", "enter"):
            try:
                self.select(action)
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                print(f"Lighting command failed: {error}", file=sys.stderr, flush=True)
                self.message = self.tr("Nie udało się zmienić lub odczytać ustawień. Spróbuj ponownie.",
                                       "Could not read or change settings. Try again.")
        return True

    def select(self, action):
        if self.zone is None:
            if action == "enter":
                zone = ZONES[self.index]
                self.settings = self.read_zone(zone)
                self.zone, self.index = zone, 0
            return
        power, colour, effect, brightness = self.settings
        if self.index == 0:
            power = "off" if power == "on" else "on"
            self.command("set", self.zone, "enabled", power)
            if power == "on" and brightness == 0:
                brightness = 30
        elif self.index == 1:
            if effect == "flash":
                self.message = self.tr("Retro Grzmoty mają stałe tło i siłę błysku.",
                                       "Retro Thunder uses fixed background and flash levels.")
                return
            new_brightness = max(0, min(100, brightness + (-10 if action == "left" else 10)))
            if new_brightness != brightness:
                self.command("set", self.zone, "brightness", str(new_brightness))
                if new_brightness == 0 or brightness == 0:
                    power = "on" if new_brightness else "off"
                brightness = new_brightness
        elif self.index == 2:
            if effect == "rider":
                self.message = self.tr("Retro Nieustraszony świeci na czerwono.", "Retro Rider uses red lighting.")
                return
            current = next(i for i, item in enumerate(PALETTE) if item[0] == colour)
            colour = PALETTE[(current + (-1 if action == "left" else 1)) % len(PALETTE)][0]
            self.command("set", self.zone, "color", colour)
        elif self.index == 3:
            choices = tuple(EFFECTS)
            effect = choices[(choices.index(effect) + (-1 if action == "left" else 1)) % len(choices)]
            self.command("set", self.zone, "effect", effect)
        elif action == "enter":
            self.command("reset", self.zone)
            power, colour, effect, brightness = "on", "amber", "steady", 30
            self.message = self.tr("Przywrócono bursztynowe światło przy 3%.",
                                   "Restored amber lighting at 3%.")
        self.settings = power, colour, effect, brightness


def render(surface, menu, fonts):
    title, label, detail = fonts
    surface.fill("#151611")

    def text(font, value, x, y, colour="#f5f1e6", right=False):
        image = font.render(value, True, colour)
        surface.blit(image, (x - image.get_width() if right else x, y))

    pygame.draw.rect(surface, "#ffae50", (42, 38, 42, 4))
    text(detail, "RETROGRZMOT  /  " + menu.tr("PODŚWIETLENIE", "LIGHTING"), 101, 28, "#ffbb6a")
    heading = (menu.tr("Sterowanie podświetleniem RETROGRZMOTA", "RETROGRZMOT lighting controls")
               if menu.zone is None else menu.zone_names()[ZONES.index(menu.zone)])
    text(title, heading, 42, 63)
    for i, (name, value, swatch) in enumerate(menu.rows()):
        y = 139 + 57 * i
        selected = i == menu.index
        pygame.draw.rect(surface, "#343125" if selected else "#22241c", (42, y, 876, 50), border_radius=8)
        if selected:
            pygame.draw.rect(surface, "#ffae50", (42, y, 876, 50), width=2, border_radius=8)
        text(label, name, 60, y + 10)
        text(detail, value, 896, y + 14, "#ffbb6a" if selected else "#e3dac9", right=True)
        if menu.zone is not None and i == 1 and menu.settings[2] != "flash":
            pygame.draw.rect(surface, "#504a3b", (618, y + 22, 192, 6), border_radius=3)
            level = round(192 * menu.settings[3] / 100)
            if level:
                pygame.draw.rect(surface, "#ffae50", (618, y + 22, level, 6), border_radius=3)
        if swatch:
            x = 896 - detail.size(value)[0] - 28
            pygame.draw.rect(surface, swatch, (x, y + 16, 17, 17), border_radius=4)

    if menu.message:
        text(detail, menu.message, 42, 438, "#ffbb6a")
    else:
        text(detail, menu.tr("Zmiany zapisują się automatycznie.", "Changes are saved automatically."), 42, 438)
    pygame.draw.line(surface, "#4a483c", (42, 478), (918, 478))
    text(detail, menu.tr("↑ ↓   wybierz wiersz    ← →   zmień    A   zatwierdź    B   wróć",
                         "↑ ↓   select row    ← →   change    A   confirm    B   back"), 42, 495)


def run(smoke=False):
    menu = Menu(polish_language())
    pygame.display.init()
    pygame.font.init()
    controller.init()
    try:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        surface = pygame.Surface((960, 540))
        fonts = (pygame.font.Font(BOLD, 33), pygame.font.Font(BOLD, 23), pygame.font.Font(FONT, 18))
        gamepads = {}

        def connect(index):
            if controller.is_controller(index):
                pad = controller.Controller(index)
                instance = pad.as_joystick().get_instance_id()
                if instance in gamepads:
                    return
                gamepads[instance] = pad

        for index in range(controller.get_count()):
            connect(index)
        width, height = screen.get_size()
        scale = min(width / 960, height / 540)
        size = (int(960 * scale), int(540 * scale))
        offset = ((width - size[0]) // 2, (height - size[1]) // 2)
        clock = pygame.time.Clock()
        redraw = True
        signal.signal(signal.SIGTERM, lambda *_: pygame.event.post(pygame.event.Event(pygame.QUIT)))
        first_frame = True
        while True:
            if redraw:
                render(surface, menu, fonts)
                screen.fill("#151611")
                screen.blit(pygame.transform.scale(surface, size), offset)
                pygame.display.flip()
                redraw = False
                if first_frame:
                    print(f"Panel rendered: {pygame.display.get_driver()} {screen.get_size()}", flush=True)
                    first_frame = False
                    if smoke:
                        return
            for event in pygame.event.get():
                action = None
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    action = KEYS.get(event.key)
                elif event.type == pygame.CONTROLLERDEVICEADDED:
                    connect(event.device_index)
                elif event.type == pygame.CONTROLLERDEVICEREMOVED:
                    pad = gamepads.pop(event.instance_id, None)
                    if pad is not None:
                        pad.quit()
                elif event.type == pygame.CONTROLLERBUTTONDOWN:
                    action = ACTIONS.get(event.button)
                if action is not None:
                    if not menu.handle(action):
                        return
                    redraw = True
            clock.tick(60)
    finally:
        pygame.quit()


if __name__ == "__main__":
    run(smoke="--smoke" in sys.argv[1:])
