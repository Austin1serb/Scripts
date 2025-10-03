#!/usr/bin/env python3
import subprocess
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Define the paths to the fonts you want to subset/compress.
#    Update this list with your actual font file names.
fonts = [
    # "Recoleta Alt Black.otf",
    "cinzel-bold.ttf",
    # "Recoleta Alt Light.otf",
    # "Recoleta Alt Medium.otf",
    # "Recoleta Alt Regular.otf",
    # "Recoleta Alt SemiBold.otf",
    # "Recoleta Alt Thin.otf",
]

# 2. Define the subset of characters you want to keep.
#    Here, we keep digits 0-9 and basic punctuation from ASCII (space, !, #, etc.).
#    Feel free to add or remove characters based on your needs.
subset_chars = "Bespoke Tint&PPF"  # digits

# 3. Loop through each font and run pyftsubset to generate a WOFF2 subset.
for font_filename in fonts:
    # Create full path to the font file
    font_path = os.path.join(script_dir, font_filename)
    base_name = os.path.splitext(font_filename)[0]  # e.g., "HelveticaNowText-Regular"
    output_woff2 = os.path.join(
        script_dir, f"{base_name}-subset.woff2"
    )  # e.g., "HelveticaNowText-Regular-subset.woff2"

    # 4. Build the command for pyftsubset
    command = [
        "pyftsubset",
        font_path,
        "--flavor=woff2",  # output format
        f"--text={subset_chars}",  # which characters to keep
        f"--output-file={output_woff2}",  # the resulting WOFF2 file name
    ]

    print(f"Creating {output_woff2} ...")
    # 5. Run the command, ensuring errors stop the script
    subprocess.run(command, check=True)

print("Finished subsetting and converting fonts to WOFF2.")
