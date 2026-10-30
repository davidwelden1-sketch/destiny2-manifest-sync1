"""Conservative name-level patch triage for game-wide weapon variant research.

A Bungie patch naming a weapon does not identify which item hashes or socket
paths were affected. This is a REVIEW QUEUE, never a roll certification.
"""
from datetime import date
import re
from urllib.parse import urlparse


def _date(value):
    if not isinstance(value, str):
        raise ValueError("Date must be YYYY-MM-DD")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Invalid date") from exc
    if parsed.isoformat() != value:
        raise ValueError("Date must be YYYY-MM-DD")
    return parsed


def _https(value, bungie=False):
    if not isinstance(value, str):
        raise ValueError("Source URL must be HTTPS")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Source URL must be HTTPS")
    if bungie and parsed.hostname != "www.bungie.net":
        raise ValueError("Patch must cite official Bungie URL")


def _catalog_source_for_hash(url, item_hash):
    """A light.gg item page must name the exact hash being audited.

    Other HTTPS catalogs may use different URL structures and remain source
    leads only; this check does not authenticate a page or certify a roll.
    """
    _https(url)
    parsed = urlparse(url)
    if parsed.hostname in ("light.gg", "www.light.gg"):
        match = re.fullmatch(r"/db/items/([0-9]+)(?:/[^/]*)?/?", parsed.path)
        if match is None or int(match.group(1)) != item_hash:
            raise ValueError("light.gg catalog URL must match exact item_hash")


def audit_name_level_patch_leads(variants, patches, checked_on):
    """Identify potential affected variants without claiming exact hash scope."""
    checked = _date(checked_on)
    if not isinstance(variants, list) or not isinstance(patches, list):
        raise ValueError("Variants and patches must be lists")
    names = {}
    seen_patches = set()
    for patch in patches:
        if not isinstance(patch, dict):
            raise ValueError("Patch must be an object")
        identifier = patch.get("patch_id")
        name = patch.get("weapon_name")
        if not isinstance(identifier, str) or not identifier.strip() or identifier in seen_patches:
            raise ValueError("Missing or duplicate patch_id")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Patch weapon_name required")
        seen_patches.add(identifier)
        effective = _date(patch.get("effective_date"))
        if effective > checked:
            raise ValueError("Future patch cannot be applied")
        _https(patch.get("source_url"), bungie=True)
        if patch.get("correction_type") != "perk_column_orientation":
            raise ValueError("Unsupported correction type")
        names.setdefault(name.strip().casefold(), []).append(patch)
    result = []
    seen_hashes = set()
    for variant in variants:
        if not isinstance(variant, dict):
            raise ValueError("Variant must be an object")
        item_hash = variant.get("item_hash")
        name = variant.get("weapon_name")
        if type(item_hash) is not int or item_hash <= 0 or item_hash in seen_hashes:
            raise ValueError("Invalid or duplicate item_hash")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Variant weapon_name required")
        _catalog_source_for_hash(variant.get("source_url"), item_hash)
        reviewed = _date(variant.get("source_reviewed_on"))
        if reviewed > checked:
            raise ValueError("Future catalog review")
        seen_hashes.add(item_hash)
        matching = names.get(name.strip().casefold(), [])
        result.append({
            "item_hash": item_hash,
            "weapon_name": name,
            "catalog_source_url": variant["source_url"],
            "source_reviewed_on": variant["source_reviewed_on"],
            "potential_name_level_patch_ids": sorted(p["patch_id"] for p in matching),
            "exact_hash_affected": "unknown" if matching else "no_name_match",
            "current_manifest_path_match": "unverified",
            "current_acquisition": "unverified",
            "roll_legality": "unverified",
            "enhanced_perk_legality": "unverified",
        })
    return {
        "checked_on": checked_on,
        "variants_reviewed": len(result),
        "potential_name_matches": sum(bool(r["potential_name_level_patch_ids"]) for r in result),
        "per_item_hash": sorted(result, key=lambda r: r["item_hash"]),
        "interpretation": "Name-level Bungie correction identifies review candidates, NOT affected hashes, exact socket changes, current drops, enhanced perks, or gameplay outcomes.",
    }
