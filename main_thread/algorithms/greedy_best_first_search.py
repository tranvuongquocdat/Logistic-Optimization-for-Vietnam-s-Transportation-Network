import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.province_node import ProvinceNode
from utils.distance_function import haversine_distance
from utils.heuristic_function import heuristic, AIRPORTS, AIR_SPEED, ROAD_SPEED
from utils.heuristic_function import (
    AIR_COST_PER_KM,
    ROAD_COST_PER_KM,
    STORAGE_TIME,
    REST_DISTANCE,
    REST_TIME,
)
from data.provinces_infor import coordinates, province_neighbor
from algorithms.UCS import build_graph_from_province_data

from queue import PriorityQueue
import random


def evaluate_path(path, cost_priority):
    total_value = 0.0
    _, road_segments = build_graph_from_province_data()
    for u, v in zip(path, path[1:]):
        dist = road_segments.get((u, v)) or road_segments.get((v, u))
        if dist is None:
            lat1, lon1 = coordinates[u]
            lat2, lon2 = coordinates[v]
            dist = haversine_distance(lat1, lon1, lat2, lon2)
        if u in AIRPORTS and v in AIRPORTS:
            time = dist / AIR_SPEED + STORAGE_TIME
            cost = dist * AIR_COST_PER_KM
        else:
            time = dist / ROAD_SPEED + (dist // REST_DISTANCE) * REST_TIME
            cost = dist * ROAD_COST_PER_KM
        total_value += cost_priority * cost + (1 - cost_priority) * time
    return total_value


def greedy_best_first_search(
    start_province: str, goal_province: str, cost_priority: float = 0.5
):
    provinces, road_segments = build_graph_from_province_data()
    cost_priority = max(0.0, min(1.0, cost_priority))

    for province in provinces.values():
        province.reset()

    if start_province not in provinces or goal_province not in provinces:
        return [], float("inf"), []
    if start_province == goal_province:
        return [start_province], 0.0, []

    start_node = provinces[start_province]
    start_node.h_x = heuristic(start_province, goal_province, cost_priority)
    start_node.transport_type = "road"

    open_set = PriorityQueue()
    open_set.put((start_node.h_x, random.random(), start_node))
    start_node.is_in_open_set = True

    flights = {}

    while not open_set.empty():
        _, _, current = open_set.get()
        current.is_in_open_set = False

        if current.name == goal_province:
            path, transport_info = [], []
            node = current
            while node:
                path.append(node.name)
                if node.parent:
                    p, c = node.parent.name, node.name
                    if p in AIRPORTS and c in AIRPORTS:
                        transport_info.append((p, c, "fly"))
                    else:
                        transport_info.append((p, c, "road"))
                node = node.parent
            path.reverse()
            transport_info.reverse()
            return path, evaluate_path(path, cost_priority), transport_info

        current.is_in_closed_set = True

        for nb_name in provinces[current.name].neighbors:
            if nb_name not in provinces:
                continue
            nb = provinces[nb_name]
            if nb.is_in_closed_set:
                continue

            if not nb.is_in_open_set:
                nb.parent = current
                nb.h_x = heuristic(nb_name, goal_province, cost_priority)
                open_set.put((nb.h_x, random.random(), nb))
                nb.is_in_open_set = True

        if current.name in AIRPORTS:
            for dest in AIRPORTS:
                if dest == current.name or dest not in provinces:
                    continue
                nb = provinces[dest]
                if nb.is_in_closed_set:
                    continue

                if not nb.is_in_open_set:
                    nb.parent = current
                    nb.h_x = heuristic(dest, goal_province, cost_priority)
                    open_set.put((nb.h_x, random.random(), nb))
                    nb.is_in_open_set = True

    return [], float("inf"), []


def calculate_transport_options_greedy(
    start: str, goal: str, cost_priority: float = 0.5
):
    result = {
        "path": [],
        "distance": 0,
        "time": 0,
        "cost": 0,
        "total_value": 0,
        "heuristic_value": 0,
        "transport_details": [],
    }
    path, total_val, transport_info = greedy_best_first_search(
        start, goal, cost_priority
    )
    if not path:
        return result
    result["path"] = path
    total_dist = total_time = total_cost = 0
    _, road_segments = build_graph_from_province_data()
    for frm, to, ttype in transport_info:
        if ttype == "road":
            key = (frm, to)
            rev = (to, frm)
            if key in road_segments:
                d = road_segments[key]
            elif rev in road_segments:
                d = road_segments[rev]
            else:
                lat1, lon1 = coordinates[frm]
                lat2, lon2 = coordinates[to]
                d = haversine_distance(lat1, lon1, lat2, lon2)
            t = (d / ROAD_SPEED) + (d // REST_DISTANCE) * REST_TIME
            c = d * ROAD_COST_PER_KM
        else:
            lat1, lon1 = coordinates[frm]
            lat2, lon2 = coordinates[to]
            d = haversine_distance(lat1, lon1, lat2, lon2)
            t = (d / AIR_SPEED) + STORAGE_TIME
            c = d * AIR_COST_PER_KM
        total_dist += d
        total_time += t
        total_cost += c
        result["transport_details"].append(
            {"from": frm, "to": to, "type": ttype, "distance": d, "time": t, "cost": c}
        )
    result["distance"] = total_dist
    result["time"] = total_time
    result["cost"] = total_cost
    result["total_value"] = total_val
    result["heuristic_value"] = heuristic(start, goal, cost_priority)
    return result

def calculate_transport_options_greedy(start: str, goal: str, cost_priority: float = 0.5):
    result = calculate_transport_options_greedy(start, goal, cost_priority)
    return result
