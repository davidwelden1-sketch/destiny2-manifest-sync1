"""Conservative historical Mothkeeper's Wraps + Ex Diris activation evidence.

Bungie 9.7.0 (2026-06-09): six charge units for a two-moth-grenade
conditional override; red/orange/miniboss-or-player defeats grant 1/2/3.
Bungie 9.7.0.2 (2026-06-23): fixed Ex Diris/Mothkeeper interaction
incorrectly requiring active moth grenade charges.
This models a *single fresh threshold*, not real cooldowns, damage,
charge overflow, buff uptime, kill attribution or current item legality.
"""
from datetime import date

PATCH = "9.7.0"
PATCH_DATE = "2026-06-09"
FIX_PATCH = "9.7.0.2"
FIX_DATE = "2026-06-23"
SOURCE = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0"
FIX_SOURCE = "https://www.bungie.net/7/en/News/Article/destiny_update_9_7_0_2"
PVE_WEIGHTS = {"red_bar": 1, "orange_bar": 2, "miniboss": 3, "boss": 3}
PVP_WEIGHTS = {"guardian": 3}
PVP_MODES = frozenset(("pvp", "competitive", "trials"))
THRESHOLD = 6


def assess_mothkeeper(*, activity, final_blows, observation_date,
                      mothkeepers_equipped, ex_diris_equipped,
                      artifact_perks=()):
    """Assess source-defined charge threshold and Ex Diris fix independently.

    final_blows: sequence of enemy rank strings for confirmed *player* kills,
    not assists or nearby teammate kills. Stops at first six-charge threshold.
    """
    if type(activity) is not str or activity not in ("pve", *PVP_MODES):
        raise ValueError("Unsupported activity")
    if type(observation_date) is not str:
        raise ValueError("Canonical observation date required")
    try:
        observed = date.fromisoformat(observation_date)
    except ValueError as exc:
        raise ValueError("Invalid observation date") from exc
    if observed.isoformat() != observation_date or observed < date.fromisoformat(PATCH_DATE):
        raise ValueError("Patch not yet effective or noncanonical date")
    if type(mothkeepers_equipped) is not bool or type(ex_diris_equipped) is not bool:
        raise ValueError("Equipment flags must be booleans")
    if type(artifact_perks) not in (tuple, list) or len(artifact_perks) > 7 or any(
        type(x) is not str or not x.strip() for x in artifact_perks
    ):
        raise ValueError("Invalid Artifact selection")
    if activity in ("competitive", "trials") and artifact_perks:
        raise ValueError("Artifacts disabled in Competitive and Trials")
    if type(final_blows) not in (list, tuple):
        raise ValueError("Confirmed player final blows required")
    weights = PVE_WEIGHTS if activity == "pve" else PVP_WEIGHTS
    charge = 0
    counted = 0
    for enemy in final_blows:
        if type(enemy) is not str or enemy not in weights:
            raise ValueError("Invalid target class for activity")
        if charge < THRESHOLD:
            charge += weights[enemy]
            counted += 1
    return {
        "evidence": "official_historical_patch_not_gameplay_measured",
        "patch_version": PATCH,
        "ex_diris_fix_patch": FIX_PATCH,
        "source_url": SOURCE,
        "fix_source_url": FIX_SOURCE,
        "activity": activity,
        "charge_units_to_first_override": min(charge, THRESHOLD),
        "remaining_units": max(0, THRESHOLD - charge),
        "counted_final_blows_to_first_override": counted,
        "two_moth_grenade_override_threshold_reached": bool(
            mothkeepers_equipped and charge >= THRESHOLD
        ),
        "ex_diris_charge_gate_fix_applicable": bool(
            mothkeepers_equipped and ex_diris_equipped
            and observed >= date.fromisoformat(FIX_DATE)
        ),
        "arc_moths_count_as_arc_grenades_per_patch": mothkeepers_equipped,
        "void_moths_can_overshield_allies_per_patch": mothkeepers_equipped,
        "artifact_legality_certified": False,
        "exact_weapon_perk_legality_certified": False,
        "damage_dps_ttk_dr_cooldowns_measured": False,
        "current_gameplay_certified": False,
        "notes": (
            "A threshold from published kill-rank units, not a live observation. "
            "Ex Diris fix removes the prior charge gate; it does not establish "
            "the effect's damage, proc frequency or kill ownership. No charge "
            "overflow, post-override accumulation, assists or team kills modeled."
        ),
    }
