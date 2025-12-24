"""
Generates an Anki package for memorizing the seventh chord type for each degree of the major scale.
"""

import argparse
from pathlib import Path
import textwrap
import genanki

# Roman numerals and their corresponding seventh chord types in the major scale
DEGREES = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
]
CHORD_TYPES_MAJOR = [
    "maj7",
    "min7",
    "min7",
    "maj7",
    "7",
    "min7",
    "min7b5",
]
CHORD_TYPES_MINOR = [
    "min7",
    "min7b5",
    "maj7",
    "min7",
    "min7",
    "maj7",
    "7",
]

# For variant 1: Roman numeral → chord type
# For variant 2: chord type → Roman numeral


def get_model_major():
    model = genanki.Model(
        2136485519,
        "Seventh Chords (major key)",
        fields=[
            {"name": "Dummy"},
            {"name": "Degree"},
            {"name": "ChordType"},
        ],
        templates=[
            {
                "name": "Seventh Chords (major key)",
                "qfmt": textwrap.dedent("""
                What is the seventh chord type for degree {{Degree}} in the major scale?
                """),
                "afmt": textwrap.dedent("""
                {{FrontSide}}<hr id=\"answer\">
                {{ChordType}}
                """),
            }
        ],
        sort_field_index=1,
    )
    return model


def get_model_minor():
    model = genanki.Model(
        2136485520,
        "Seventh Chords (minor key)",
        fields=[
            {"name": "Dummy"},
            {"name": "Degree"},
            {"name": "ChordType"},
        ],
        templates=[
            {
                "name": "Seventh Chords (minor key)",
                "qfmt": textwrap.dedent("""
                What is the seventh chord type for degree {{Degree}} in the minor scale?
                """),
                "afmt": textwrap.dedent("""
                {{FrontSide}}<hr id=\"answer\">
                {{ChordType}}
                """),
            }
        ],
        sort_field_index=1,
    )
    return model


def main(pkg_path: Path):
    pkg_path.mkdir(exist_ok=True)
    # Major key
    model_major = get_model_major()
    deck_major = genanki.Deck(1456594839, "Seventh chords (major key)")
    for degree, chord_type in zip(DEGREES, CHORD_TYPES_MAJOR):
        deck_major.add_note(
            genanki.Note(
                model=model_major,
                fields=[
                    f"seventh_chords_major-{degree}-{chord_type}",  # Dummy
                    degree,  # Degree
                    chord_type,  # ChordType
                ],
                guid=f"seventh_chords_major-{degree}-{chord_type}",
            )
        )
    pkg_major = genanki.Package(deck_major)
    pkg_major.write_to_file(pkg_path / "seventh_chords_major.apkg")

    # Minor key
    model_minor = get_model_minor()
    deck_minor = genanki.Deck(1456594840, "Seventh chords (minor key)")
    for degree, chord_type in zip(DEGREES, CHORD_TYPES_MINOR):
        deck_minor.add_note(
            genanki.Note(
                model=model_minor,
                fields=[
                    f"seventh_chords_minor-{degree}-{chord_type}",  # Dummy
                    degree,  # Degree
                    chord_type,  # ChordType
                ],
                guid=f"seventh_chords_minor-{degree}-{chord_type}",
            )
        )
    pkg_minor = genanki.Package(deck_minor)
    pkg_minor.write_to_file(pkg_path / "seventh_chords_minor.apkg")

    print(
        f"Anki packages written to {pkg_path}/seventh_chords_major.apkg and {pkg_path}/seventh_chords_minor.apkg"
    )


def entry():
    parser = argparse.ArgumentParser(
        description="Generate Anki packages for memorizing diatonic seventh chord types in the major and minor scale."
    )
    parser.add_argument(
        "--pkg_path",
        type=Path,
        required=True,
        help="The folder where the generated Anki packages will be saved.",
    )

    args = parser.parse_args()
    main(args.pkg_path)


if __name__ == "__main__":
    entry()
