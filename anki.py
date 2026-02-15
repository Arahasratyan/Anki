import re
import csv
from pathlib import Path
from gtts import gTTS
import unicodedata
import genanki



MODEL_ID = 9876543210          # Change only if you create another model type
MODEL_NAME = "English → Translation (with audio)"

my_model = genanki.Model(
    MODEL_ID,
    MODEL_NAME,
    fields=[
        {"name": "Front"},     # English + audio
        {"name": "Back"},      # Translation
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{Front}}",
            "afmt": "{{FrontSide}}<hr id=answer>{{Back}}",
        },
    ],
    css="""
    .card {
      font-family: Arial, sans-serif;
      font-size: 22px;
      text-align: center;
      color: black;
      background-color: white;
    }
    b { color: #0066cc; }
    """
)

def clean_for_audio(text: str) -> str:
    return re.sub(r'\*\*(.*?)\*\*', r'\1', text)

def convert_to_anki_bold(text: str) -> str:
    def repl(match):
        return f"<b>{match.group(1)}</b>"
    text = re.sub(r'\*\*(.*?)\*\*', repl, text, flags=re.DOTALL)
    text = re.sub(r'\*(.*?)\*', repl, text, flags=re.DOTALL)
    return text

def slugify(text: str, max_len=80) -> str:
    text = clean_for_audio(text)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-zA-Z0-9\s-]', '', text).strip()
    text = re.sub(r'\s+', '-', text)
    text = text[:max_len].rstrip('-')
    return text or "sentence"

def main(
    input_csv: str = "sentences.csv",
    output_apkg: str = "English_Russian_Deck.apkg",
    audio_lang: str = "en",
):
    input_path = Path(input_csv)
    deck_name = Path(output_apkg).stem
    temp_audio_dir = Path("temp_audio")
    temp_audio_dir.mkdir(exist_ok=True)

    deck_id = 2059400110 + hash(deck_name) % 100000000  # semi-unique
    my_deck = genanki.Deck(deck_id, deck_name)

    media_files = []
    cards_count = 0

    print("Processing CSV and generating audio...")

    with open(input_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header if present

        for row in reader:
            if len(row) < 2:
                continue
            eng_raw = row[0].strip()
            trans = row[1].strip()

            if not eng_raw:
                continue

            eng_clean = clean_for_audio(eng_raw)
            eng_anki = convert_to_anki_bold(eng_raw)
            trans_anki = convert_to_anki_bold(trans)

            # Audio
            audio_name = f"{slugify(eng_clean)}.mp3"
            audio_path = temp_audio_dir / audio_name

            if not audio_path.exists():
                try:
                    tts = gTTS(eng_clean, lang=audio_lang, slow=False)
                    tts.save(str(audio_path))
                    print(f"Created: {audio_name}")
                except Exception as e:
                    print(f"Audio failed for '{eng_clean[:50]}…': {e}")
                    continue

            media_files.append(str(audio_path))  # full path for genanki

            sound_tag = f"[sound:{audio_name}]"
            front = f"{eng_anki} {sound_tag}"

            note = genanki.Note(
                model=my_model,
                fields=[front, trans_anki]
            )

            my_deck.add_note(note)
            cards_count += 1

    if cards_count == 0:
        print("No valid cards generated.")
        return

    # Create package with media
    package = genanki.Package(my_deck)
    package.media_files = media_files

    print(f"\nWriting deck → {output_apkg}")
    package.write_to_file(output_apkg)

    print(f"Success! Created {cards_count} cards + audio.")
    print("Import instructions:")
    print("1. Double-click the .apkg file → Anki will open & import it")
    print("   (or in Anki: File → Import → select the .apkg)")
    print("2. The audio is already inside — no manual copying needed.")
    print("3. You can safely delete the 'temp_audio' folder afterwards.\n")

    # Optional: clean up temp files
    # import shutil
    # shutil.rmtree(temp_audio_dir)


if __name__ == "__main__":
    main(
        input_csv=r"C:\Users\Admin\OneDrive\Рабочий стол\cards.csv",
        output_apkg=r"C:\Users\Admin\OneDrive\Рабочий стол\python\EmotionsRevealed.apkg",
        audio_lang="en"
    )