import os
import re
import configparser
import datetime

from django.utils import timezone


def extract_blocks(folder_path):
    """
    Recursively scan all files in the given folder and extract blocks that match:
        start line:   "#\\s*\\[\\[START\\s+(.*?)\\]\\]"
        end line:     "#\\s*\\[\\[END\\]\\]"

    The 'expression' is any text after "START " and before the first "]]".

    Returns:
        list of rows, each row is [relative_file_path, expression, full_block_content]
    """
    results = []
    start_pattern = re.compile(r"#\s*\[\[START\s+(.*?)\]\]")
    end_pattern = re.compile(r"#\s*\[\[END\]\]")

    install_ini_path = os.path.join(folder_path, "install.ini")
    if os.path.exists(install_ini_path):
        config = configparser.ConfigParser()
        config.read(install_ini_path)
        time = config["DEFAULT"]["GEN_TIME"].replace("'", "")
        dt = datetime.datetime.fromisoformat(
            time.replace(".", "-").replace(" ", "T") + "Z"
        )
    else:
        dt = None

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if not filename.endswith(".py"):
                continue
            file_path = os.path.join(root, filename)

            relative_path = os.path.relpath(file_path, folder_path)

            timestamp = os.path.getmtime(file_path)
            datestamp = datetime.datetime.fromtimestamp(timestamp)
            datestamp_utc = timezone.make_aware(
                datestamp, timezone.get_default_timezone()
            )

            c = datestamp_utc - dt
            if abs(c.total_seconds()) < 30:
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except (IOError, UnicodeDecodeError):
                continue

            i = 0
            while i < len(lines):
                line = lines[i]
                start_match = start_pattern.search(line)
                if start_match:
                    expression = start_match.group(1).strip()
                    start_idx = i

                    # Find the nearest line containing the end tag
                    end_idx = -1
                    for j in range(i, len(lines)):
                        if end_pattern.search(lines[j]):
                            end_idx = j
                            break

                    if end_idx != -1:
                        block_lines = lines[start_idx : end_idx + 1]
                        block_content = "".join(block_lines)
                        results.append([relative_path, expression, block_content])
                        i = end_idx + 1  # skip the processed block
                    else:
                        # No closing tag found – stop scanning this file
                        break
                else:
                    i += 1

    return results


def extract_text_block(text: str) -> str:
    """
    Extract text content from a single block delimited by:

        start line:   "#\\s*\\[\\[START\\s+(.*?)\\]\\]"
        end line:     "#\\s*\\[\\[END\\]\\]"

    Leading whitespace is stripped from each line based on the indentation
    level of the START line.

    Returns:
        The extracted text block as a string, with indentation removed.
    """
    start_pattern = re.compile(r"^(\s*)#\s*\[\[START\s+(.+?)\]\]")
    end_pattern = re.compile(r"^\s*#\s*\[\[END\]\]")

    lines = text.splitlines()
    inside_block = False
    output_lines = []
    indent_size = 0

    for line in lines:
        if not inside_block:
            # Look for the block start line
            match = start_pattern.match(line)
            if match:
                inside_block = True
                # Count the number of leading spaces before #[[START ...]]
                indent_size = len(match.group(1))
                continue
        else:
            # Look for the block end line
            if end_pattern.match(line):
                break

            # Remove the base indentation if the line has enough spaces
            if line.startswith(" " * indent_size):
                corrected_line = line[indent_size:]
            else:
                corrected_line = line.lstrip(" ")

            output_lines.append(corrected_line)

    return "\n".join(output_lines)

