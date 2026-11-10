
# Latein-AI-Vokabeln

Dieses Repository wandelt ein Foto oder einen Scan mit lateinischen Vokabeln mithilfe eines Vision-fähigen OpenAI-Modells in das im Referenz-PDF beschriebene Format um.

## Ausgabeformat

Jede Vokabel wird als eine Zeile mit `|`-Trennzeichen ausgegeben:

```text
|Anzahl|Wortart|Grundform|Mittelspalte|Perfektstamm|Deutsche Übersetzung|Klasse|Wortstamm|
```

Beispiel:

```text
|2|Verb|rogare|rogo, rogavi, rogatum|rogav|fragen|a|roga|
|2|Substantiv|dominus|domini m.||||o|domin|
```

Die Anwendung erzeugt außerdem eine JSON-Datei mit den erkannten Daten. Das ist praktisch, wenn die Ergebnisse später in Excel, Quizlet oder eine eigene Lernanwendung übernommen werden sollen.

## Voraussetzungen

- Python 3.10 oder neuer
- ein OpenAI-API-Schlüssel mit ausreichendem Guthaben
- ein Foto/Scan im Format PNG, JPG, JPEG oder WEBP

## Installation lokal

### Windows PowerShell

```powershell
git clone https://github.com/DEIN-NAME/latein-ai-vokabeln.git
cd latein-ai-vokabeln
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

### macOS/Linux

```bash
git clone https://github.com/DEIN-NAME/latein-ai-vokabeln.git
cd latein-ai-vokabeln
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
```

Trage in `.env` deinen Schlüssel ein:

```env
OPENAI_API_KEY=sk-dein-schluessel
OPENAI_MODEL=gpt-4o-mini
```

`.env` wird durch `.gitignore` nicht zu GitHub hochgeladen.

## Ausführen

```bash
python src/main.py mein-vokabelbild.jpg --output ausgabe
```

Danach findest du:

- `ausgabe.txt`: das PDF-kompatible Pipe-Format
- `ausgabe.json`: strukturierte Daten mit allen Feldern

Optional kannst du das Modell angeben:

```bash
python src/main.py mein-vokabelbild.jpg --output ausgabe --model gpt-4o-mini
```

## Ausführen über GitHub Actions

1. Erstelle auf GitHub ein neues Repository, zum Beispiel `latein-ai-vokabeln`.
2. Lade alle Dateien dieses Projekts hoch oder pushe sie mit Git.
3. Öffne im Repository **Settings → Secrets and variables → Actions**.
4. Klicke **New repository secret**.
5. Name: `OPENAI_API_KEY`; Value: dein API-Schlüssel.
6. Gehe zu **Actions → Latein-Vokabeln aus Bild erzeugen → Run workflow**.
7. Lade unter **Choose image** ein Bild aus deinem Repository hoch, zum Beispiel `input/vokabeln.jpg`, und starte den Workflow.
8. Nach Abschluss öffnest du den Lauf und lädst unter **Artifacts** das Paket `latein-vokabeln-ausgabe` herunter.

Für GitHub Actions muss das Eingabebild bereits im Repository liegen. Lade es beispielsweise in den Ordner `input/` hoch. Vokabelbilder können personenbezogene oder schulische Inhalte enthalten; veröffentliche sie nicht versehentlich in einem öffentlichen Repository.

## Hinweise zur Erkennungsqualität

- Fotografiere das Blatt gerade und bei gleichmäßiger Beleuchtung.
- Das ganze Blatt sollte sichtbar sein; schneide keine Zeilen ab.
- Bei unsicheren Werten setzt das Programm eine leere Zeichenkette und schreibt einen Hinweis in `hinweise` in der JSON-Datei.
- Unregelmäßige Verben sowie u- und e-Deklination werden ausdrücklich berücksichtigt. Die KI soll fehlende Felder nicht erfinden.
- Prüfe die Ausgabe vor dem Lernen. KI-OCR und grammatische Analyse können Fehler enthalten.

## Kosten und Sicherheit

Der Bildinhalt wird an die OpenAI-API gesendet. Es entstehen API-Kosten nach deinem OpenAI-Tarif. Speichere API-Schlüssel ausschließlich in `.env` oder GitHub Secrets, niemals direkt im Quellcode.

## Repository selbst auf GitHub hochladen (Git-Befehle)

Wenn du Git auf deinem Computer installiert hast, kannst du das Projekt so hochladen:

```bash
git remote add origin https://github.com/DEIN-NAME/latein-ai-vokabeln.git
git branch -M main
git commit -m "Erste Version: Latein-Vokabeln mit KI"
git push -u origin main
```

Ersetze `DEIN-NAME` durch deinen GitHub-Benutzernamen und erstelle das leere Repository vorher auf GitHub. Alternativ kannst du auf GitHub **Add file → Upload files** verwenden und die Projektdateien im Browser hochladen.
