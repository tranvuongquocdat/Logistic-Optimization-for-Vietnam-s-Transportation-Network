import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.provinces_infor import *
from utils.distance_function import haversine_distance
from typing import Dict, List, Tuple

# List of provinces with airports (assumed)
AIRPORTS = ["Hà Nội", "TP Hồ Chí Minh", "Đà Nẵng"]

# Hằng số
ROAD_SPEED = 50  # km/h
AIR_SPEED = 800  # km/h
ROAD_COST_PER_KM = 100  # VND/km
AIR_COST_PER_KM = 300  # VND/km
STORAGE_TIME = 2  # giờ
REST_TIME = 1  # 1 hours rest time per 300 km
REST_DISTANCE = 300  # km

def heuristic(current_province: str, goal_province: str, cost_priority: float = 0.5, log: bool = False) -> float:
    """
    Heuristic function for A* in logistics.
    Args:
        current_province: Current province
        goal_province: Destination province
        cost_priority: "cost" (priority cost) or "time" (priority time)
    Returns:
        Minimum heuristic value
    """
    # print("cost priority: ", cost_priority)
    current_lat, current_lon = coordinates[current_province]
    goal_lat, goal_lon = coordinates[goal_province]
    distance = haversine_distance(current_lat, current_lon, goal_lat, goal_lon)
    if distance == float('inf'):
        # If there is no direct distance, estimate based on coordinates (if needed)
        try:
            x1, y1 = coordinates[current_province]
            x2, y2 = coordinates[goal_province]
            distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5 * 100  # Quy đổi đơn vị
        except KeyError:
            return float('inf')

    # 1. Chi phí và thời gian đường bộ
    road_time = (distance / ROAD_SPEED) + (distance // REST_DISTANCE) * REST_TIME
    if log:
        print("road time: ", road_time)
    road_cost = distance * ROAD_COST_PER_KM / 10000
    if log:
        print("road cost: ", road_cost)
    road_heuristic = round(cost_priority * road_cost + (1 - cost_priority) * road_time, 2)
    if log:
        print("road heuristic: ", road_heuristic)
    heuristic_value = road_heuristic  # Initialize with road heuristic

    # 2. Chi phí và thời gian máy bay (nếu cả hai đều có sân bay)
    air_time = float('inf')
    air_cost = float('inf')
    if log:
        print(current_province + "-" + goal_province)
        print("road heuristic: ", road_heuristic)
    if current_province in AIRPORTS and goal_province in AIRPORTS:
        air_time = (distance / AIR_SPEED) + STORAGE_TIME
        if log:
            print("air time: ", air_time)
        air_cost = distance * AIR_COST_PER_KM / 10000
        if log:
            print("air cost: ", air_cost)
        air_heuristic = round(cost_priority * air_cost + (1 - cost_priority) * air_time, 2)
        if log:
            print("heuristic with air: ", air_heuristic)
            print("--------------------------------")
        #get the heuristic value with 2 number after the decimal point
        heuristic_value = min(road_heuristic, air_heuristic)

    return heuristic_value


if __name__ == "__main__":
    # print(heuristic("Hải Phòng", "Đà Nẵng"))
    # print(heuristic("Hải Phòng", "Hà Nội"))
    print(heuristic("Đà Nẵng", "TP Hồ Chí Minh", 0.1, True))
    print(heuristic("Đà Nẵng", "TP Hồ Chí Minh", 0.5, True))
    print(heuristic("Đà Nẵng", "TP Hồ Chí Minh", 0.9, True))
    print(heuristic("Hà Nội", "TP Hồ Chí Minh", 0.1, True))
    print(heuristic("Hà Nội", "TP Hồ Chí Minh", 0.5, True))
    print(heuristic("Hà Nội", "TP Hồ Chí Minh", 0.9, True))