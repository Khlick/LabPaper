import re

def parse_metadata_content(source: str, is_markdown: bool = False) -> tuple[dict, str]:
    """Parse metadata content with continuation lines."""
    metadata = {}
    updated_source = source.splitlines()
    to_remove = []

    # Define patterns based on cell type
    allowed_tags = "|".join(["caption", "label", "footer", "width"])
    footnote_pattern = r'(?:\[(\d+(?:,\d+)*)\]\s*)?(.+?\|?)$'
    if is_markdown:
        single_pattern = r'<!--\s*@(%s):\s*([^|]+?)\s*-->$'
        multi_start = r'<!--\s*(?:\n)?\s*@(%s):\s*(.+?\s*\|)\s*-->$'
        multi_subsequent = r'<!--\s*(?:\[(\d+(?:,\d+)*)\]\s*)?(.+?)\s*-->$'
    else:
        single_pattern = r'#\s*@(%s):\s*([^|]+?)\s*$'
        multi_start = r'#\s*@(%s):\s*(.+?)\s*\|$'
        multi_subsequent = r'#\s*(?:\[(\d+(?:,\d+)*)\]\s*)?(.+?)$'
    # Initialize variables
    current_type = None
    current_content = []
    in_multiline = False
    
    for i, line in enumerate(updated_source):
        stripped = line.strip()
        if not stripped:
            # Empty lines indicate either end of tag or end of content
            # Store the contents if any, otherwise move on
            if current_type:
                if current_type == "footer":
                    metadata[current_type] = current_content
                else:
                    metadata[current_type] = "\n".join(current_content)
                current_type = None
                current_content = []
            continue
        
        if not in_multiline:
            # check for single line matches
            match = re.match(single_pattern % allowed_tags, stripped)
            if match:
                # Found single pattern with without line break ending
                key, value = match.group(1).strip(), match.group(2).strip()
                metadata[key] = value
                to_remove.append(i)
                continue
            # Check for multi-line opening match
            match = re.match(multi_start % allowed_tags, stripped)
            if match:
                # Found multi-line opening match
                current_type, value = match.group(1).strip(), match.group(2).strip().rstrip("|")
                if current_type == "footer":
                    submatch = re.match(footnote_pattern, value)
                    footnote = {'text':submatch.group(2).strip()}
                    if submatch.group(1):
                        footnote['number'] = submatch.group(1).strip()
                    current_content.append(footnote)
                else:
                    current_content = [value]
                # Set the multiline flag
                in_multiline = True
                to_remove.append(i)
                continue
        else:
            # In multiline mode,
            match = re.match(multi_subsequent, stripped)
            if match:
                num, text = match.group(1), match.group(2).strip()
                if current_type == "footer":
                    footnote = {"text": text.rstrip("|")}
                    if num:
                        footnote["number"] = num
                    current_content.append(footnote)
                else:
                    current_content.append(text.rstrip("|"))
                to_remove.append(i)
                # End of multiline if no `|`
                if not text.endswith("|"):
                    in_multiline = False
                    if current_type == "footer":
                        metadata[current_type] = current_content
                    else:
                        metadata[current_type] = "\n".join(current_content)
                    current_type = None
                    current_content = []
            else:
                print("No match found")
    # Remove processed lines in reverse order
    for i in sorted(to_remove, reverse=True):
        del updated_source[i]
    
    return metadata, '\n'.join(updated_source)