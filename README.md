# RETROGRZMOT — sterowanie podświetleniem LED

[English instructions](#english)

Dodatek jest **opcjonalny**. Zainstaluj go, jeśli budujesz RETROGRZMOTA z podświetleniem LED. Panel pozwala włączać i wyłączać strefy, wybierać kolor, ustawiać jasność i zmieniać efekt osobno dla **logo** i **podstawy**. Ustawienia zapisują się automatycznie. Panel korzysta z języka Batocery.

## Zanim zaczniesz

Paczka jest przygotowana dla **Raspberry Pi 3 Model B+ z Batocerą 43.1** i taśmą **WS2812B** w układzie RETROGRZMOTA. Sterownik wysyła 43 pozycje przez **BCM GPIO21 (pin fizyczny 40)**. Logo zajmuje pierwsze 5 pozycji, a efekty ruchome podstawy w tej konfiguracji używają pozycji 6–40. Podłącz wspólną masę i użyj osobnego zasilania taśmy zgodnie z układem RETROGRZMOTA. Przed pracą z przewodami wyłącz konsolę i odłącz zasilanie. Instalator sprawdza dostępność Pygame i biblioteki taśmy na Batocerze.

## Instalacja z Windows

1. Kliknij **Code → Download ZIP** na GitHubie. Rozpakuj ZIP i upewnij się, że masz folder `retrogrzmot-ports-led-main`, w którym znajduje się `install.sh`.
2. Połącz komputer i Batocerę z tą samą siecią. Odczytaj adres IP konsoli w **Ustawieniach sieci**. Zamknij panel podświetlenia, jeśli aktualizujesz istniejącą instalację.
3. W Eksploratorze plików otwórz katalog zawierający rozpakowany folder. W pasku adresu wpisz `powershell`. W oknie PowerShell uruchom poniższe polecenia, zastępując `PI_IP` adresem konsoli. Batocera może poprosić o hasło.

```powershell
scp -r .\retrogrzmot-ports-led-main root@PI_IP:/userdata/system/
ssh root@PI_IP
```

4. Gdy zobaczysz wiersz poleceń Batocery (np. `[root@BATOCERA ~]#`), uruchom instalator:

```sh
bash /userdata/system/retrogrzmot-ports-led-main/install.sh
```

5. Po komunikacie `Installed` uruchom ponownie Batocerę z menu. Na liście systemów wybierz **Porty → Sterowanie podświetleniem RETROGRZMOTA**. Jeśli pozycja się nie pojawi, wybierz **START → Ustawienia gier → Aktualizuj listę gier**.

Na padzie użyj strzałek góra/dół do wyboru wiersza, lewo/prawo do zmiany wartości, a przycisków zatwierdzania i powrotu do nawigacji. **100% na suwaku** ogranicza poziom taśmy do **10%**, a fabryczne **30% na suwaku** odpowiada około **3%**. Przy 0% strefa się wyłącza.

### Efekty

| Polski | English | Działanie |
| --- | --- | --- |
| Retro Bursztyn | RetroAmber | Światło stałe w wybranym kolorze. Fabrycznie bursztyn przy 3% jasności taśmy. |
| Retro Nieustraszony | Retro Rider | Czerwony skaner w stylu KITT, który odbija na końcach strefy i zostawia gasnący ogon. |
| Retro Grzmoty | Retro Thunder | Tło przy 3% jasności. Co 3–6 sekund losowa dioda błyska na 100% skali, a dostępni sąsiedzi w odległości jednej i dwóch diod na 70% i 40% skali. Efekt używa wybranego koloru oraz własnych poziomów jasności. |

## English

Install this **optional add-on** if your RETROGRZMOT build uses LED lighting. It targets **Raspberry Pi 3 Model B+ running Batocera 43.1** and the project's WS2812B wiring on **BCM GPIO21 (physical pin 40)**. The driver sends 43 positions. The logo uses the first five, and animated base effects use positions 6–40. Use a common ground and the separate LED power supply from the project wiring. Shut down and disconnect power before rewiring.

1. On GitHub, choose **Code → Download ZIP** and extract it. Open PowerShell in the folder containing `retrogrzmot-ports-led-main`.
2. Put Windows and Batocera on the same network. Close the lighting panel before upgrading. Find the console IP in **Network Settings**. Run the two PowerShell commands above using that IP in place of `PI_IP`.
3. After connecting over SSH, run the installer command from step 4. When it says `Installed`, restart Batocera from its menu.
4. Open **Ports → Sterowanie podświetleniem RETROGRZMOTA**. If the entry is missing, use **START → Game Settings → Update Gamelists**. The panel itself follows Batocera's language.

Use the controller's up/down buttons to select a row and left/right to adjust it. Each zone has its own on/off state, colour, brightness and effect. Changes save automatically. **100% on the slider** is capped at **10% strip brightness**. The factory amber level is **30% on the slider**, about **3% on the strip**. At 0% the zone switches off.

- **RetroAmber** gives steady light in the chosen colour. The factory colour is amber.
- **Retro Rider** is a red KITT-style scanner with a fading trail.
- **Retro Thunder** keeps a 3% background in the selected colour. Every 3–6 seconds a random LED flashes at 100% of the panel scale, with nearby LEDs at 70% and 40% where present. The effect uses fixed light levels.

## Aktualizacje / Updates

Instalator przechowuje program i ustawienia w `/userdata` i zapisuje kopie podmienianych plików. Po aktualizacji Batocery sprawdź zgodność Pygame i biblioteki WS2812B przed ponowną instalacją. The installer keeps the panel and settings in `/userdata` and backs up files it replaces. Check the Pygame and WS2812B dependencies after Batocera upgrades.

- [Dostęp przez SSH / Batocera SSH](https://wiki.batocera.org/access_the_batocera_via_ssh)
- [Porty / Batocera Ports](https://wiki.batocera.org/systems:ports)
