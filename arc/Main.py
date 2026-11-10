#!/usr/bin/env python3
"""Foto/Scan lateinischer Vokabeln -> PDF-kompatibles Pipe-Format."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

FIELDS = [
    "anzahl",
    "wortart",
    "grundform",
    "mittelspalte",
    "perfektstamm",
    "uebersetzung",
    "klasse",
    "wortstamm",
]

SYSTEM_PROMPT = """Du bist eine sorgfältige Lateinlehrkraft und OCR-Expertin.
Analysiere das Bild mit lateinischen Vokabeln. Lies jede sichtbare Vokabelzeile und gib ausschließlich valides JSON zurück.

Das JSON muss exakt diese Form haben:
{
  "vokabeln": [
    {
      "anzahl": "",
      "wortart": "",
      "grundform": "",
      "mittelspalte": "",
      "perfektstamm": "",
      "uebersetzung": "",
      "klasse": "",
      "wortstamm": "",
      "hinweise": ""
    }
  ]
}

Bedeutung der Felder:
- anzahl: Anzahl der Vokabeln, falls im Bild angegeben; sonst "".
- wortart: z.B. Verb, Substantiv, Adjektiv, Präposition.
- grundform: Bei Verben der Infinitiv, bei Substantiven der Nominativ Singular.
- mittelspalte: Bei Verben die Formen wie "rogo, rogavi, rogatum"; bei Substantiven Genitiv Singular und Geschlecht wie "domini m.".
- perfektstamm: Bei Verben der Perfektstamm ohne Endung, z.B. "rogav"; bei Substantiven leer.
- uebersetzung: deutsche Übersetzung.
- klasse: Deklinations- oder Konjugationsklasse, z.B. a, o, gem, kons, u, e.
- wortstamm: Wortstamm, z.B. roga oder domin.
- hinweise: Unsichere Lesung, fehlende Information oder Besonderheiten. Bei keiner Unsicherheit leer lassen.

Regeln:
1. Erfinde keine Formen. Wenn etwas nicht lesbar oder nicht angegeben ist, verwende "" und erkläre es in hinweise.
2. Berücksichtige unregelmäßige Verben sowie u- und e-Deklination.
3. Behalte lateinische Schreibweise, Längenzeichen und Groß-/Kleinschreibung so weit wie lesbar bei.
4. Gib keine Markdown-Codeblöcke und keinen zusätzlichen Text aus.
"""


def image_data_url(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    if mime not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
        raise ValueError("Unterstützt werden JPG, PNG, WEBP oder GIF.")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def clean_record(record: dict[str, Any]) -> dict[str, str]:
    result = {field: str(record.get(field, "") or "").strip() for field in FIELDS}
    result["hinweise"] = str(record.get("hinweise", "") or "").strip()
    return result


def pipe_line(record: dict[str, str]) -> str:
    # Pipes in KI-Ausgaben würden das Zielformat zerstören.
    values = [record[field].replace("|", "/") for field in FIELDS]
    return "|" + "|".join(values) + "|"


def call_ai(client: OpenAI, image_url: str, model: str) -> list[dict[str, str]]:
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Konvertiere alle Vokabeln aus diesem Bild."},
                    {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}},
                ],
            },
        ],
    )
    content = response.choices[0].message.content or "{}"
    data = json.loads(content)
    records = data.get("vokabeln", [])
    if not isinstance(records, list):
        raise ValueError("Die KI-Antwort enthält keine gültige Vokabelliste.")
    return [clean_record(item) for item in records if isinstance(item, dict)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="Pfad zu JPG, PNG, WEBP oder GIF")
    parser.add_argument("--output", default="output/vokabeln", help="Ausgabepfad ohne Dateiendung")
    parser.add_argument("--model", default=None, help="Optional: OpenAI-Modell")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Fehler: OPENAI_API_KEY fehlt. Lege eine .env-Datei an.", file=sys.stderr)
        return 2
    if not args.image.is_file():
        print(f"Fehler: Bild nicht gefunden: {args.image}", file=sys.stderr)
        return 2

    model = args.model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        records = call_ai(OpenAI(api_key=api_key), image_data_url(args.image), model)
    except Exception as exc:  # CLI soll eine verständliche Fehlermeldung liefern.
        print(f"Fehler bei der Bildanalyse: {exc}", file=sys.stderr)
        return 1

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    txt_path = output.with_suffix(".txt")
    json_path = output.with_suffix(".json")
    txt_path.write_text("\n".join(pipe_line(record) for record in records) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps({"vokabeln": records}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{len(records)} Vokabel(n) erkannt.")
    print(f"Textausgabe: {txt_path}")
    print(f"JSON-Ausgabe: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
