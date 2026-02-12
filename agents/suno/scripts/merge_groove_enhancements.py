#!/usr/bin/env python3
"""
Merge groove_enhancements.json into subgenre_tags.json.
Creates a backup before modifying and validates the merge.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

ASSETS_DIR = Path(__file__).parent.parent / "assets"
SUBGENRE_TAGS_FILE = ASSETS_DIR / "subgenre_tags.json"
ENHANCEMENTS_FILE = ASSETS_DIR / "groove_enhancements.json"
BACKUP_DIR = ASSETS_DIR / "backups"


def load_json(filepath: Path) -> list | dict:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath: Path, data: list | dict) -> None:
    """Save JSON file with proper formatting."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


def create_backup(filepath: Path) -> Path:
    """Create timestamped backup of file."""
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{filepath.stem}_backup_{timestamp}.json"
    shutil.copy(filepath, backup_path)
    print(f"✓ Backup created: {backup_path.name}")
    return backup_path


def check_duplicates(existing_tags: list, new_entry: dict) -> bool:
    """Check if a tag entry already exists (by phrase and subgenre_id)."""
    for tag in existing_tags:
        if (tag.get('phrase') == new_entry.get('phrase') and
            tag.get('subgenre_id') == new_entry.get('subgenre_id') and
            tag.get('engine') == new_entry.get('engine')):
            return True
    return False


def merge_enhancements():
    """Merge groove enhancements into subgenre_tags.json."""

    # Load files
    print("Loading files...")
    subgenre_tags = load_json(SUBGENRE_TAGS_FILE)
    enhancements = load_json(ENHANCEMENTS_FILE)

    # Create backup
    create_backup(SUBGENRE_TAGS_FILE)

    # Track statistics
    stats = {
        'general_added': 0,
        'subgenre_added': 0,
        'duplicates_skipped': 0
    }

    # Merge general groove descriptors (global tags)
    print("\nMerging general groove descriptors...")
    for entry in enhancements.get('general_groove_descriptors', []):
        # Remove the 'global' flag for JSON structure (it's metadata)
        tag_entry = {k: v for k, v in entry.items() if k != 'global'}
        # Ensure subgenre_id is None for global tags
        tag_entry['subgenre_id'] = None

        if not check_duplicates(subgenre_tags, tag_entry):
            subgenre_tags.append(tag_entry)
            stats['general_added'] += 1
            print(f"  + Added global: {tag_entry['phrase']}")
        else:
            stats['duplicates_skipped'] += 1
            print(f"  ○ Skipped (duplicate): {tag_entry['phrase']}")

    # Merge subgenre-specific groove descriptors
    print("\nMerging subgenre-specific groove descriptors...")
    for entry in enhancements.get('subgenre_specific_groove_descriptors', []):
        if not check_duplicates(subgenre_tags, entry):
            subgenre_tags.append(entry)
            stats['subgenre_added'] += 1
            print(f"  + Added for {entry['subgenre_id']}: {entry['phrase']}")
        else:
            stats['duplicates_skipped'] += 1
            print(f"  ○ Skipped (duplicate): {entry['phrase']}")

    # Save merged file
    save_json(SUBGENRE_TAGS_FILE, subgenre_tags)

    # Print summary
    print("\n" + "=" * 50)
    print("MERGE SUMMARY")
    print("=" * 50)
    print(f"General global tags added:     {stats['general_added']}")
    print(f"Subgenre-specific tags added:  {stats['subgenre_added']}")
    print(f"Duplicates skipped:            {stats['duplicates_skipped']}")
    print(f"Total new entries:             {stats['general_added'] + stats['subgenre_added']}")
    print(f"Final tag count:               {len(subgenre_tags)}")
    print("=" * 50)

    # Count Groove tags specifically
    groove_tags = [t for t in subgenre_tags if t.get('engine') == 'Groove']
    print(f"\nTotal Groove engine tags:      {len(groove_tags)}")

    return stats


if __name__ == "__main__":
    try:
        stats = merge_enhancements()
        print("\n✓ Merge completed successfully!")
    except Exception as e:
        print(f"\n✗ Error during merge: {e}")
        raise
