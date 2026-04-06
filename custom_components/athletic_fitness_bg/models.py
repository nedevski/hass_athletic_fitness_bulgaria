"""Data models for the Athletic Fitness BG integration."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GymDetails:
    """Represent a selected gym."""

    gym_id: int
    gym_name: str
    city: str
    people_count: int | None = None
