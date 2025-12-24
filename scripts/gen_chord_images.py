import argparse
from enum import Enum
from tqdm import tqdm
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap

from pymusictheory import Chord, Interval, NoteAlteration, NoteInOctave

from gen_chords.utils import chord_type_to_long_symbol


class ClefType(Enum):
    """
    Enum for Clef types.

    The values are tuples of the form (clef_sign, line_number).
    """

    G = ("G", 2)
    F = ("F", 4)


def chord_to_musicxml(chord: Chord, clef_type: ClefType) -> str:
    """
    Generate MusicXML for the chord based on its notes and clef type.
    """

    template_xml = textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
        <score-partwise version="3.1">
        <part-list>
            <score-part id="P1">
            <part-name>Music</part-name>
            </score-part>
        </part-list>
        <part id="P1">
            <measure number="1">
            <attributes>
                <divisions>1</divisions>
                <key>
                <fifths>0</fifths>
                </key>
                <clef>
                <sign>{clef_type.value[0]}</sign>
                <line>{clef_type.value[1]}</line>
                </clef>
            </attributes>

            {{}}

            </measure>
        </part>
        </score-partwise>
    """)

    chord_xml = ""

    for i, note_in_octave in enumerate(sorted(chord)):
        chord_xml += textwrap.indent(
            textwrap.dedent(f"""
            <note>
                {"<chord/>" if i != 0 else ""}
                <pitch>
                    <step>{note_in_octave.letter}</step>
                    <alter>{int(note_in_octave.alteration)}</alter>
                    <octave>{note_in_octave.octave}</octave>
                </pitch>
                <duration>4</duration>
                <type>whole</type>
            </note>
        """),
            " " * 4,
        )

    # Insert chord xml into template
    musicxml = template_xml.format(chord_xml)

    return musicxml


def musicxml_to_png(musicxml: str, path: Path) -> None:
    """
    Generate an image at `path` containing the specified musicxml.
    """

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = Path(temp_dir) / f"{path.stem}.xml"

        # Write xml to temporary file
        with open(temp_file_path, "w") as file:
            file.write(musicxml)

        # Run `mscore` command to generate png image
        try:
            # subprocess.run(["mscore", temp_file_path, "-o", path, "-T", "50"], check=True)
            subprocess.run(
                ["mscore", temp_file_path, "-o", path, "-T", "50"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            # For some reason, musescore appends "-1" to the filename, so we need to rename it
            generated_path = path.parent / f"{path.stem}-1{path.suffix}"
            generated_path.rename(path)
        except subprocess.CalledProcessError as e:
            print(f"Error generating image: {e}")
        except FileNotFoundError:
            print("MuseScore is not installed or not found in PATH.")


def chord_generation(
    root_range: tuple[NoteInOctave, NoteInOctave],
    clef_type: ClefType,
    intervals: list[Interval],
    folder_path: Path,
) -> None:
    """
    Generates png images of chords at folder_path.

    Args:
        root_range: The range of roots to generate chords for. All other notes will be stacked on top of the root.
        clef_type: The clef type to use for the generated chords.
        intervals: The intervals to use for generating the chords. Decides how many notes will be stacked on top of the root and with what distance.
        folder_path: The path to the folder where the generated images will be saved.
    """

    # Find all possible root notes between the specified roots, with possible *single* alterations (natural/sharp/flat)
    roots_with_duplicates: list[set[NoteInOctave]] = []
    current_note_position = root_range[0].absolute_semitone_offset
    while current_note_position != root_range[1].absolute_semitone_offset:
        # Ignore notes with double alterations (double sharp/flat)
        root_candidates = {
            note
            for note in NoteInOctave.from_absolute_semitone_offset(
                current_note_position
            )
            if note.alteration
            in (NoteAlteration.NATURAL, NoteAlteration.SHARP, NoteAlteration.FLAT)
        }
        roots_with_duplicates.append(root_candidates)
        current_note_position += 1
    roots: set[NoteInOctave] = set.union(*roots_with_duplicates)

    sorted_roots = sorted(roots)

    # For each root, construct the desired chord
    chords = [
        Chord({root + interval for interval in intervals}) for root in sorted_roots
    ]

    musicxmls = [chord_to_musicxml(chord, clef_type) for chord in chords]

    # Create the output directory if not present
    os.makedirs(folder_path, exist_ok=True)

    # Write each musicxml string to a file, with filename containing the notes
    for musicxml, chord in tqdm(
        zip(musicxmls, chords), total=len(chords), desc="Generating chords"
    ):
        sorted_notes = sorted(chord)
        filestem = str(sorted_notes[0])
        # Replace unicode characters with ASCII equivalents
        filestem = filestem.replace("♯", "#").replace("♭", "b")
        filepath = folder_path / f"{filestem}.png"
        musicxml_to_png(musicxml, filepath)


def main(args: argparse.Namespace) -> None:
    chord_types = [
        (
            "major_seventh",
            [
                Interval.PERFECT_UNISON,
                Interval.MAJOR_THIRD,
                Interval.PERFECT_FIFTH,
                Interval.MAJOR_SEVENTH,
            ],
        ),
        (
            "dominant_seventh",
            [
                Interval.PERFECT_UNISON,
                Interval.MAJOR_THIRD,
                Interval.PERFECT_FIFTH,
                Interval.MINOR_SEVENTH,
            ],
        ),
        (
            "minor_seventh",
            [
                Interval.PERFECT_UNISON,
                Interval.MINOR_THIRD,
                Interval.PERFECT_FIFTH,
                Interval.MINOR_SEVENTH,
            ],
        ),
    ]

    for chord_name, intervals in chord_types:
        print(f"--- {chord_name.upper()} CHORDS ---")
        chord_generation(
            root_range=args.root_range,
            clef_type=args.clef,
            intervals=intervals,
            folder_path=args.folder_path / chord_name,
        )
        # Anki peculiarity: each file name must be unique, so we append the chord name to each file name
        for chord_image_path in (args.folder_path / chord_name).glob("**/*.png"):
            chord_image_path.rename(
                chord_image_path.parent
                / f"{chord_image_path.stem}_{chord_type_to_long_symbol(chord_name)}.png"
            )


def parse_clef(clef_str: str) -> ClefType:
    """
    Parse a clef string (e.g., "G" or "F") into a ClefType enum.
    """
    try:
        return ClefType[clef_str]
    except KeyError:
        raise ValueError(f"Invalid clef type: {clef_str}. Must be 'G' or 'F'.")


def parse_root_range(value: str) -> tuple[NoteInOctave, NoteInOctave]:
    try:
        strs = value.split(",")  # Split the input string by commas
        return (
            NoteInOctave.from_str(
                strs[0].strip()
            ),  # Convert the first part to a NoteInOctave
            NoteInOctave.from_str(
                strs[1].strip()
            ),  # Convert the second part to a NoteInOctave
        )
    except Exception as _:
        raise argparse.ArgumentTypeError(
            f"Invalid root range format: {value}. Expected format: 'root1,root2'."
        )


def entry():
    parser = argparse.ArgumentParser(description="Generate chord images.")
    parser.add_argument(
        "--clef",
        type=parse_clef,
        required=True,
        help=f"The clef type to use for the generated chords. Choices: {', '.join(e.name for e in ClefType)}.",
    )
    parser.add_argument(
        "--root_range",
        type=parse_root_range,
        required=True,
        help="The range of roots to generate chords for, in the format 'root1,root2'.",
    )
    parser.add_argument(
        "--folder_path",
        type=Path,
        required=True,
        help="The path to the folder where the generated images will be saved. Each chord type will be saved in a separate subfolder.",
    )
    args = parser.parse_args()

    main(args)


if __name__ == "__main__":
    entry()
