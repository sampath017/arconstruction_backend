from typing import Dict, List

DEFAULT_TAG = "general"  # change to "misc"/"uncategorized" if you prefer

def derive_tags(name: str, TAG_RULES: Dict[str, str]) -> List[str]:
    """
    Given a name (filename/title) and a dict of keyword->tag, produce a sorted, unique list of tags.
    Guarantees at least DEFAULT_TAG if nothing matches.
    """
    lowered = (name or "").lower()
    tags = {tag.strip() for key, tag in TAG_RULES.items() if key.lower() in lowered}
    return sorted(tags or {DEFAULT_TAG})