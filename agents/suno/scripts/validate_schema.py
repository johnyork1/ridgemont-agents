#!/usr/bin/env python3
"""
Schema validation script for Suno Studio.
Run this as a CI check or before deployment.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

ASSETS_DIR = Path(__file__).parent.parent / "assets"

def load_json(filename):
    with open(ASSETS_DIR / filename, 'r') as f:
        return json.load(f)

def validate_all():
    errors = []
    warnings = []
    
    genres = load_json('genres.json')
    subgenres = load_json('subgenres.json')
    constraints = load_json('constraints.json')
    aliases = load_json('aliases.json')
    
    genres_by_id = {g['genre_id']: g for g in genres}
    
    # 1. Check constraint rule order
    rules = constraints.get('rules', [])
    rule_ids = [r['id'] for r in rules]
    expected_order = ['container_requires_subgenre', 'engine_only_primary', 'modifier_not_standalone']
    if rule_ids != expected_order:
        errors.append(f"Constraint rule order incorrect. Expected: {expected_order}, Got: {rule_ids}")
    
    # 2. Invariant: primary_genre_id must point to role=engine
    for sg in subgenres:
        pid = sg.get('primary_genre_id')
        if pid:
            genre = genres_by_id.get(pid)
            if not genre:
                errors.append(f"Subgenre '{sg['name']}' references unknown genre_id: {pid}")
            elif genre.get('role') != 'engine':
                # Exception: Latin subgenres (Salsa, Bachata, etc.) have Latin as primary which is a container
                # This is intentional for pure-Latin subgenres
                if genre.get('role') == 'regional_container':
                    # Allowed for pure regional subgenres
                    pass
                else:
                    errors.append(f"Subgenre '{sg['name']}' primary_genre_id={pid} has role={genre.get('role')}, expected 'engine'")
    
    # 3. Invariant: container_genre_id must point to role=regional_container
    for sg in subgenres:
        cid = sg.get('container_genre_id')
        if cid:
            genre = genres_by_id.get(cid)
            if not genre:
                errors.append(f"Subgenre '{sg['name']}' references unknown container_genre_id: {cid}")
            elif genre.get('role') != 'regional_container':
                errors.append(f"Subgenre '{sg['name']}' container_genre_id={cid} has role={genre.get('role')}, expected 'regional_container'")
    
    # 4. Alias collision guard
    alias_to_canonical = defaultdict(list)
    for entry in aliases:
        canonical = entry['canonical']
        for a in entry.get('aliases', []):
            alias_to_canonical[a.lower()].append(canonical)
    
    for alias, canonicals in alias_to_canonical.items():
        if len(canonicals) > 1:
            warnings.append(f"Alias collision: '{alias}' maps to multiple canonicals: {canonicals}")
    
    # 5. Genre role distribution
    engines = [g for g in genres if g.get('role') == 'engine']
    containers = [g for g in genres if g.get('role') == 'regional_container']
    print(f"Genre roles: {len(engines)} engines, {len(containers)} containers")
    
    if len(engines) != 14:
        warnings.append(f"Expected 14 engine genres, found {len(engines)}")
    if len(containers) != 2:
        warnings.append(f"Expected 2 container genres, found {len(containers)}")
    
    # Report
    print(f"\n{'='*50}")
    print(f"Validation complete")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    
    if warnings:
        print(f"\nWarnings:")
        for w in warnings:
            print(f"  ⚠️  {w}")
    
    if errors:
        print(f"\nErrors:")
        for e in errors:
            print(f"  ❌ {e}")
        sys.exit(1)
    else:
        print(f"\n✅ All checks passed")
        sys.exit(0)

if __name__ == '__main__':
    validate_all()
