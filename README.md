# Anki Deck Generator with Audio

Makes Anki flashcard decks from CSV files with automatic audio pronunciation.

## What you need

```bash
pip install genanki gtts
```

## How to use

1. Make a CSV file with your words:

```csv
English,Translation
Hello world,Привет мир
I am **learning** Python,Я **изучаю** Python
```

Use `**text**` for bold words.

2. Edit the paths at the bottom of the script:

```python
if __name__ == "__main__":
    main(
        input_csv="sentences.csv",
        output_apkg="My_Deck.apkg",
        audio_lang="en"
    )
```

3. Run it:

```bash
python anki_deck_generator.py
```

4. Import the .apkg file into Anki (just double-click it or use File → Import).

## Change audio language

```python
audio_lang="en"    # English
audio_lang="es"    # Spanish
audio_lang="fr"    # French
```

Any language code that Google TTS supports will work.

Note: Audio files are saved in `temp_audio/` folder (you can delete it after)
