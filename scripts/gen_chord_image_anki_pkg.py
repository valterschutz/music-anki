"""
Generates an anki package of chords at folder_path.
"""

import argparse
from pathlib import Path
import textwrap

import genanki
import re

from gen_chords.utils import (
    chord_type_to_long_symbol,
    chord_type_to_pretty_symbol,
    ugly_root_str_to_pretty_root_str,
)

# Two random IDs
DECK_ID = 1456594836
MODEL_ID = 2136485516


def get_model():
    model = genanki.Model(
        MODEL_ID,
        "Chord image and name",
        fields=[
            {"name": "ChordImage"},
            {"name": "PrettyChordName"},
            {"name": "UglyChordName"},
        ],
        templates=[
            {
                "name": "Chord image and name",
                "qfmt": textwrap.dedent("""
                <div style="text-align: center;">
                    {{ChordImage}}
                </div>
                """),
                "afmt": textwrap.dedent("""
                {{FrontSide}}<hr id="answer">
                <div style="text-align: center; font-size: 42px;">
                    {{PrettyChordName}}
                </div>
                """),
            }
        ],
        sort_field_index=2,  # sort by ugly chord name
    )
    return model


def main(args):
    deck = genanki.Deck(DECK_ID, "Seventh chords on the F clef")
    model = get_model()

    # media_files will be which files the anki package will include
    media_files = []
    # For each chord in the folder, add a note to the deck
    for chord_image_path in args.folder_path.glob("**/*.png"):
        media_files.append(chord_image_path)
        # Chord name is the root + chord type, e.g "C major seventh"
        # Root is found by splitting on the first digit in stem
        match = re.split(r"(\d+)", chord_image_path.stem, maxsplit=1)
        assert match, f"Failed to split chord name: {chord_image_path.stem}"

        # Use a pretty string for display in Anki
        pretty_chord_name = ugly_root_str_to_pretty_root_str(
            match[0]
        ) + chord_type_to_pretty_symbol(chord_image_path.parts[-2])

        # Use an ugly string for the GUID
        long_chord_name = match[0] + chord_type_to_long_symbol(
            chord_image_path.parts[-2]
        )

        note = genanki.Note(
            model=model,
            fields=[
                f'<img src="{chord_image_path.name}">',
                pretty_chord_name,
                long_chord_name,
            ],
            guid=long_chord_name,
        )
        deck.add_note(note)

    # Create a package with the deck and media files
    pkg = genanki.Package(deck)
    pkg.media_files = media_files

    # Write the package to a file
    pkg.write_to_file(args.pkg_path)
    print(f"Anki package written to {args.pkg_path}")


def entry():
    parser = argparse.ArgumentParser(
        description="Generate an Anki package of chords from a folder of chord images."
    )
    parser.add_argument(
        "--folder_path",
        type=Path,
        required=True,
        help="Where the generated chords are saved (produced my gen_chord_images.py)",
    )
    parser.add_argument(
        "--pkg_path",
        type=Path,
        required=True,
        help="Where the generated Anki package will be saved.",
    )

    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    entry()
