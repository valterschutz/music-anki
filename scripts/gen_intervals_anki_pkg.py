"""
Generates an anki package of chords at folder_path.
"""

import argparse
from pymusictheory import Interval, Note, NoteInOctave
from pathlib import Path
import textwrap

import genanki
import re


ROOT_GENERATOR = (
    NoteInOctave.from_str(s)
    for s in [
        "C4",
        "C#4",
        "Db4",
        "D4",
        "D#4",
        "Eb4",
        "E4",
        "F4",
        "F#4",
        "Gb4",
        "G4",
        "G#4",
        "Ab4",
        "A4",
        "A#4",
        "Bb4",
        "B4",
    ]
)
# Intervals of major scale
INTERVALS = [
    ("minor second", Interval.MINOR_SECOND),
    ("major second", Interval.MAJOR_SECOND),
    ("minor third", Interval.MINOR_THIRD),
    ("major third", Interval.MAJOR_THIRD),
    ("perfect fourth", Interval.PERFECT_FOURTH),
    ("perfect fifth", Interval.PERFECT_FIFTH),
    ("minor sixth", Interval.MINOR_SIXTH),
    ("major sixth", Interval.MAJOR_SIXTH),
    ("minor seventh", Interval.MINOR_SEVENTH),
    ("major seventh", Interval.MAJOR_SEVENTH),
]


def get_model_variant_1():
    model = genanki.Model(
        2136485517,
        "Intervals (variant 1)",
        fields=[
            {"name": "Dummy"},
            {"name": "Root"},
            {"name": "Interval"},
            {"name": "Note"},
        ],
        templates=[
            {
                "name": "Intervals (variant 1)",
                "qfmt": textwrap.dedent("""
                A {{Interval}} away from {{Root}} is ...
                """),
                "afmt": textwrap.dedent("""
                {{FrontSide}}<hr id="answer">
                {{Note}}
                """),
            }
        ],
        sort_field_index=2,  # sort by ugly chord name
    )
    return model


def get_model_variant_2():
    model = genanki.Model(
        2136485518,
        "Intervals (variant 2)",
        fields=[
            {"name": "Dummy"},
            {"name": "Root"},
            {"name": "Interval"},
            {"name": "Note"},
        ],
        templates=[
            {
                "name": "Intervals (variant 2)",
                "qfmt": textwrap.dedent("""
                {{Note}} is a {{Interval}} away from ...
                """),
                "afmt": textwrap.dedent("""
                {{FrontSide}}<hr id="answer">
                {{Root}}
                """),
            }
        ],
        sort_field_index=2,  # sort by ugly chord name
    )
    return model


def main(pkg_path: Path):
    deck1 = genanki.Deck(1456594837, "Intervals (variant 1)")
    deck2 = genanki.Deck(1456594838, "Intervals (variant 2)")
    model1 = get_model_variant_1()
    model2 = get_model_variant_2()

    for root in list(ROOT_GENERATOR):
        root_str = re.sub(r"\d+", "", str(root))
        for interval_str, interval in INTERVALS:
            note = root + interval
            note_str = re.sub(r"\d+", "", str(note))

            deck1.add_note(
                genanki.Note(
                    model=model1,
                    fields=[
                        f"intervals_variant1-{root_str}-{interval_str}-{note_str}",  # Dummy
                        root_str,  # Root
                        interval_str,  # Interval
                        note_str,  # Note
                    ],
                    guid=f"intervals_variant1-{root_str}-{interval_str}-{note_str}",
                )
            )
            deck2.add_note(
                genanki.Note(
                    model=model2,
                    fields=[
                        f"intervals_variant2-{root_str}-{interval_str}-{note_str}",  # Dummy
                        root_str,  # Root
                        interval_str,  # Interval
                        note_str,  # Note
                    ],
                    guid=f"intervals_variant2-{root_str}-{interval_str}-{note_str}",
                )
            )

    # Create a package with the deck and media files
    pkg1 = genanki.Package(deck1)
    pkg2 = genanki.Package(deck2)

    # Write the package to a file
    pkg_path.mkdir(exist_ok=True)
    pkg1.write_to_file(pkg_path / "variant1.apkg")
    pkg2.write_to_file(pkg_path / "variant2.apkg")
    print(f"Anki packages written to {pkg_path}")


def entry():
    parser = argparse.ArgumentParser(
        description="Generate anki packages for memorizing notes of the major scale."
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
