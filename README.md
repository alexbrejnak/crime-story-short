# Crime Story Short — prototyp statyczny (NIE publikować jako pełnej wersji)

**Stan:** wersja demonstracyjna, ponieważ eksport Sites zawiera tylko 7 ostatnich filmów, a nie pełne 106.

`python3 build.py` tworzy katalog `docs/`. Domyślnie generuje strony z `noindex` i ścieżkami GitHub Pages `/crime-story-short/`.

**Aby uzyskać pełny katalog:** ustaw sekret `YOUTUBE_API_KEY` w GitHub Settings → Secrets and variables → Actions (nie wpisuj klucza w pliki). Następnie uruchom GitHub Actions → `Aktualizuj statyczna strone` → Run workflow. Skrypt pobiera playlistę `PLXeYYxp3nFN6i5u8av2TYJJcNNVBDE454`, wszystkie jej strony i publiczne embeddable filmy. Nie zapewnia ręcznych wykluczeń D1, które nie zostały wyeksportowane.

**GitHub Pages:** obecnie ustawione `main / (root)`; do publikacji katalogu site trzeba później wybrać `main /docs` lub skonfigurować Pages Action, bo po wgraniu plików ustaw w Pages gałąź main i folder /docs. Nie zmieniaj DNS ani domeny.

**Artykuły:** w `articles-drafts/` zachowano puste szablony z eksportu, NIE zawierają końcowych tekstów. Nie zostały opublikowane w prototypie.

**Uwaga:** przed migracją konieczne są dalsze prace: zgodne adresy po przejściu na własną domenę, pełny katalog, artykuły i kontrola wyglądu. Obecny projekt to działający generator, a nie gotowy zamiennik obecnej witryny.
