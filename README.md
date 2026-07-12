# Instrukcja wdrożeniowa WAZUH

Kompleksowy manual wdrożeniowy platformy Wazuh (SIEM/XDR) dla administratorów IT:
projekt architektury → przygotowanie infrastruktury → instalacja → klaster/HA → bezpieczeństwo platformy.

## Zawartość

| Plik | Opis |
|---|---|
| [`Instrukcja-Wdrozeniowa-WAZUH.md`](Instrukcja-Wdrozeniowa-WAZUH.md) | pełna instrukcja w Markdown (GitHub renderuje ją razem z diagramami Mermaid) |
| [`docs/index.html`](docs/index.html) | wersja webowa z **interaktywnym kreatorem doboru architektury** (EPS → sizing → rekomendacja) |
| [`site/build.py`](site/build.py) | skrypt budujący `docs/index.html` z pliku Markdown |

## Publikacja jako strona (GitHub Pages)

1. Wypchnij repozytorium na GitHub.
2. W repo: **Settings → Pages**.
3. W sekcji *Build and deployment*: Source = **Deploy from a branch**, Branch = **main**, folder = **/docs** → Save.
4. Po ~1 minucie strona będzie dostępna pod `https://<użytkownik>.github.io/<repo>/`.

Strona jest w pełni samodzielna (jeden plik HTML, zero zależności zewnętrznych),
obsługuje motyw jasny/ciemny i działa na urządzeniach mobilnych.

## Aktualizacja treści

Edytuj `Instrukcja-Wdrozeniowa-WAZUH.md`, następnie przebuduj stronę:

```bash
python3 site/build.py    # wymaga: python3-markdown
```

i zacommituj zmieniony `docs/index.html`.
