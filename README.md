# Instrukcja wdrożeniowa WAZUH

Kompleksowy manual wdrożeniowy platformy Wazuh (SIEM/XDR) dla administratorów IT:
projekt architektury → przygotowanie infrastruktury → instalacja → klaster/HA → bezpieczeństwo platformy
→ monitorowanie końcówek Windows (Sysmon/UKSC-NIS2).

## Zawartość

| Ścieżka | Opis |
|---|---|
| [`Instrukcja-Wdrozeniowa-WAZUH.md`](Instrukcja-Wdrozeniowa-WAZUH.md) | **źródło** instrukcji w Markdown — jedyny plik, który się edytuje ręcznie |
| [`docs/index.html`](docs/index.html) | wersja webowa (GitHub Pages) z interaktywnym kreatorem doboru architektury — **generowana**, nie edytuj ręcznie |
| [`site/build.py`](site/build.py) | skrypt budujący HTML z pliku Markdown |
| [`pawel/`](pawel/) | pakiet telemetrii Windows (profile Sysmon, grupy Wazuh, macierze) — materiał źródłowy dla ETAP 6 |

## Jak to działa (Markdown → HTML)

Instrukcję pisze się **wyłącznie** w `Instrukcja-Wdrozeniowa-WAZUH.md`. Skrypt `site/build.py`
zamienia ten plik na stronę WWW. Nigdy nie edytuj `docs/index.html` ręcznie — przy następnym
buildzie zmiany zostaną nadpisane.

### Wymagania jednorazowo

Potrzebny jest Python 3 z biblioteką `markdown`:

```bash
sudo apt install python3-markdown      # Debian/Kali/Ubuntu
# albo:  pip install markdown
```

Żadnych innych zależności — użyte rozszerzenia (`tables`, `fenced_code`, `toc`, `sane_lists`)
są wbudowane w pakiet `markdown`.

### Przebudowa strony

Po każdej edycji pliku `.md` uruchom:

```bash
python3 site/build.py
```

Skrypt czyta `Instrukcja-Wdrozeniowa-WAZUH.md` i zapisuje **dwa** pliki:

- `docs/index.html` — pełna, samodzielna strona pod **GitHub Pages**,
- `site/wazuh-manual-artifact.html` — fragment do podglądu jako artifact (poza gitem, w `.gitignore`).

Ścieżki liczone są względem lokalizacji skryptu, więc `python3 site/build.py` zadziała z dowolnego katalogu.

### Publikacja zmian

```bash
python3 site/build.py                 # 1. przebuduj HTML
git add Instrukcja-Wdrozeniowa-WAZUH.md docs/index.html
git commit -m "opis zmiany"           # 2. zacommituj źródło + wynik
git push                              # 3. GitHub Pages przebuduje się sam (~1 min)
```

Strona jest w pełni samodzielna (jeden plik HTML, zero zależności zewnętrznych), obsługuje
motyw jasny/ciemny i działa na urządzeniach mobilnych.

## Konwencje w pliku Markdown (na co uważać przy edycji)

Skrypt `build.py` interpretuje kilka wzorców — trzymaj się ich, żeby build nie padł i strona wyglądała spójnie:

- **Callouty** — akapit zaczynający się od emoji staje się kolorową ramką:
  - `⚠️ **...**` → ramka „Uwaga",
  - `💡 **...**` → „Dobra praktyka",
  - `✅ **...**` → „Punkt kontrolny".
- **Diagramy Mermaid** — build oczekuje **dokładnie 3** bloków ```` ```mermaid ```` (architektura,
  flowchart decyzyjny, kolejność instalacji) i zamienia je na gotowe grafiki HTML. Jeśli dodasz lub
  usuniesz blok `mermaid`, zaktualizuj listę `diagrams` w `site/build.py` — inaczej build przerwie
  się asercją „Nie wszystkie diagramy zostały wstawione".
- **Tabele** — automatycznie owijane w kontener z poziomym przewijaniem (nie trzeba nic robić).
- **Checklisty** — pozycje `- [ ] ...` renderują się jako pola wyboru.
- **Numeracja rozdziałów** — po dodaniu nowego rozdziału `## N.` pamiętaj o przesunięciu numeracji
  kolejnych rozdziałów i odwołań „rozdz. N" w tekście (spis treści na stronie generuje się z nagłówków automatycznie).

## Publikacja na GitHub Pages (konfiguracja jednorazowa)

1. **Settings → Pages** w repozytorium.
2. *Build and deployment*: Source = **Deploy from a branch**.
3. Branch = **main**, folder = **/docs** → **Save**.
4. Po ~1 minucie strona jest dostępna pod `https://<użytkownik>.github.io/<repo>/`.

Od tej pory każdy `git push` ze zmienionym `docs/index.html` odświeża stronę automatycznie.
