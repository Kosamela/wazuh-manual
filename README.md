# Instrukcja wdrożeniowa WAZUH

Kompleksowy manual wdrożeniowy platformy Wazuh (SIEM/XDR) dla administratorów IT:
projekt architektury → przygotowanie infrastruktury → instalacja → klaster/HA → bezpieczeństwo platformy.

## Zawartość

| Plik | Opis |
|---|---|
| [`Instrukcja-Wdrozeniowa-WAZUH.md`](Instrukcja-Wdrozeniowa-WAZUH.md) | pełna instrukcja w Markdown (GitHub renderuje ją razem z diagramami Mermaid) |
| [`docs/index.html`](docs/index.html) | wersja webowa z **interaktywnym kreatorem doboru architektury** (EPS → sizing → rekomendacja) |
| [`site/build.py`](site/build.py) | skrypt budujący `docs/index.html` z pliku Markdown |

## Aktualizacja treści

Edytuj `Instrukcja-Wdrozeniowa-WAZUH.md`, następnie przebuduj stronę:

```bash
python3 site/build.py    # wymaga: python3-markdown
```

i zacommituj zmieniony `docs/index.html`.
