# models.py
from typing import Dict, List, Tuple

class RoadSegment:
    """Class to store information about road segments between two provinces"""
    def __init__(self, start: str, end: str, distance: float):
        self.start = start
        self.end = end
        self.distance = distance

    def __str__(self):
        return f"{self.start} -> {self.end}: {self.distance}km"