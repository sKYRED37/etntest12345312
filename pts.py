"""PTS rating rules from Рейтинг ETN.docx.

Pure functions shared by the API and tests. Unsupported prize ranges deliberately
raise ValueError because the source document does not define them.
"""
from dataclasses import dataclass
from typing import Optional

BASE_PTS = {
    "T5": (1, 0),
    "T4": (2, 1),
    "T3": (5, 1),
    "T2": (10, 2),
    "T1": (25, 5),
}

PRIZE_COEFFICIENTS = (
    (0, 5_000, 0.55, "T5–T4"),
    (5_000, 20_000, 0.60, "T4–T3"),
    (20_000, 50_000, 1.15, "T2–T3"),
    (50_000, 150_000, 1.60, "T2"),
    (500_000, None, 3.00, "T1"),
)

OLYMPIC_STAGE_POINTS = {
    "qualification": 5,
    "playoffs": 5,
    "1/16": 6,
    "1/8": 8,
    "1/4": 12,
    "1/2": 18,
    "final": 25,
}

DE_STAGE_POINTS = {
    32: {"ub_r1": 15, "ub_r2": 20, "ub_qf": 20, "ub_sf": 20, "ub_final": 25,
         "lb_r1": 8, "lb_r2": 10, "lb_r3": 12, "lb_qf": 15, "lb_sf": 15, "lb_final": 0,
         "gf_win": 25, "gf_loss": 10},
    16: {"ub_r1": 20, "ub_qf": 25, "ub_sf": 25, "ub_final": 30,
         "lb_r1": 10, "lb_qf": 15, "lb_sf": 18, "lb_final": 17,
         "gf_win": 25, "gf_loss": 10},
    64: {"ub_r1": 10, "ub_r2": 15, "ub_r3": 15, "ub_qf": 20, "ub_sf": 20, "ub_final": 20,
         "lb_r1": 5, "lb_r2": 8, "lb_r3": 10, "lb_r4": 12, "lb_qf": 10, "lb_sf": 10, "lb_final": 5,
         "gf_win": 25, "gf_loss": 10},
}

SWISS_BONUS = {
    16: {"3-0": 20, "3-1": 15, "3-2": 10, "2-3": 5, "1-3": 2, "0-3": 0},
    32: {"4-0": 25, "4-1": 18, "4-2": 12, "3-3": 6, "2-3": 3},
}

PLACEMENT_POINTS = {1: 100, 2: 75, 3: 55, 4: 40, "5-8": 25, "9-16": 10, "17-32": 3}


def individual_match_pts(tier: str, won: bool, kills: float = 0, assists: float = 0, is_mvp: bool = False) -> float:
    """PTS = base win/loss + kills + assists*0.5; MVP multiplies total by 1.1."""
    tier = str(tier or "").strip().upper()
    if tier not in BASE_PTS:
        raise ValueError("Неизвестный тир турнира: укажите T1–T5")
    win_pts, loss_pts = BASE_PTS[tier]
    value = (win_pts if won else loss_pts) + max(0, float(kills or 0)) + max(0, float(assists or 0)) * 0.5
    if is_mvp:
        value *= 1.1
    return round(value, 2)


def coefficient_for_prize(prize_pool: float) -> float:
    prize = float(prize_pool)
    for low, high, coefficient, _tier in PRIZE_COEFFICIENTS:
        if prize >= low and (high is None or prize <= high):
            # The source gives adjoining bands; at exact boundaries, prefer the higher band.
            if high is not None and prize == high:
                continue
            return coefficient
    raise ValueError("В документе не указан коэффициент для призового фонда 150 000–500 000 ₽")


def placement_points(place: int) -> int:
    place = int(place)
    if place in (1, 2, 3, 4):
        return PLACEMENT_POINTS[place]
    if 5 <= place <= 8: return PLACEMENT_POINTS["5-8"]
    if 9 <= place <= 16: return PLACEMENT_POINTS["9-16"]
    if 17 <= place <= 32: return PLACEMENT_POINTS["17-32"]
    return 0


def clan_tournament_pts(place_pts: float, stage_pts: float, coefficient: float) -> float:
    """Source formula: (placement points + stage points) * coefficient^1.6."""
    return round((float(place_pts) + float(stage_pts)) * (float(coefficient) ** 1.6), 2)
