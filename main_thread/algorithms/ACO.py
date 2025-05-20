# Ant Colony Optimization
import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.province_node import ProvinceNode
from utils.distance_function import haversine_distance
from utils.heuristic_function import AIRPORTS, AIR_SPEED, ROAD_SPEED
from utils.heuristic_function import (
    AIR_COST_PER_KM,
    ROAD_COST_PER_KM,
    STORAGE_TIME,
    REST_DISTANCE,
    REST_TIME,
)
from data.provinces_infor import coordinates, province_neighbor


def build_graph_from_province_data():
    """
    Xây dựng đồ thị từ dữ liệu về các tỉnh/thành

    Returns:
        Tuple chứa dictionary các tỉnh/thành và dictionary các đoạn đường
    """
    provinces = {}
    road_segments = {}

    # Tạo các nút tỉnh/thành
    for province_name, (lat, lon) in coordinates.items():
        province_id = hash(province_name)
        provinces[province_name] = ProvinceNode(province_id, province_name, lat, lon)

    # Thêm thông tin về các tỉnh liền kề
    for province_name, neighbors_list in province_neighbor.items():
        if province_name in provinces:
            for neighbor_name in neighbors_list:
                if neighbor_name in provinces:
                    provinces[province_name].add_neighbor(neighbor_name)

                    # Tính khoảng cách giữa hai tỉnh
                    if (province_name, neighbor_name) not in road_segments and (
                        neighbor_name,
                        province_name,
                    ) not in road_segments:
                        p1_lat, p1_lon = coordinates[province_name]
                        p2_lat, p2_lon = coordinates[neighbor_name]
                        distance = haversine_distance(p1_lat, p1_lon, p2_lat, p2_lon)
                        road_segments[(province_name, neighbor_name)] = distance

    return provinces, road_segments


def ant_colony_optimization(
    start_province: str,
    goal_province: str,
    cost_priority: float = 0.5,
    num_ants: int = 100,
    num_iterations: int = 1000,
    alpha: float = 1.0,
    beta: float = 2.0,
    evaporation_rate: float = 0.1,
    Q: float = 100.0,
    max_steps: int = 100,
):
    # Build graph
    provinces, road_segments = build_graph_from_province_data()
    cost_priority = max(0.0, min(1.0, cost_priority))

    # Build adjacency with precomputed metrics and initial pheromone
    adjacency = {}
    initial_tau = 1.0
    for u, node in provinces.items():
        adjacency[u] = []
        # Road edges
        for v in node.neighbors:
            if v not in provinces:
                continue
            # distance lookup
            key, rev = (u, v), (v, u)
            if key in road_segments:
                dist = road_segments[key]
            elif rev in road_segments:
                dist = road_segments[rev]
            else:
                dist = haversine_distance(
                    node.latitude,
                    node.longitude,
                    provinces[v].latitude,
                    provinces[v].longitude,
                )
            t = dist / ROAD_SPEED + (dist // REST_DISTANCE) * REST_TIME
            c = dist * ROAD_COST_PER_KM
            value = cost_priority * c + (1 - cost_priority) * t
            eta = 1.0 / value if value > 0 else 1.0
            adjacency[u].append(
                {
                    "to": v,
                    "type": "road",
                    "dist": dist,
                    "time": t,
                    "cost": c,
                    "value": value,
                    "eta": eta,
                    "tau": initial_tau,
                }
            )
        # Air edges
        if u in AIRPORTS:
            for v in AIRPORTS:
                if v == u or v not in provinces:
                    continue
                dist = haversine_distance(
                    node.latitude,
                    node.longitude,
                    provinces[v].latitude,
                    provinces[v].longitude,
                )
                t = dist / AIR_SPEED + STORAGE_TIME
                c = dist * AIR_COST_PER_KM
                value = cost_priority * c + (1 - cost_priority) * t
                eta = 1.0 / value if value > 0 else 1.0
                adjacency[u].append(
                    {
                        "to": v,
                        "type": "fly",
                        "dist": dist,
                        "time": t,
                        "cost": c,
                        "value": value,
                        "eta": eta,
                        "tau": initial_tau,
                    }
                )

    best_path = None
    best_value = float("inf")

    # Main ACO loop
    for _ in range(num_iterations):
        iteration_best_path = None
        iteration_best_value = float("inf")
        iteration_edges = []

        for _ in range(num_ants):
            path = [start_province]
            visited = {start_province}
            total_value = 0.0
            steps = 0

            while path[-1] != goal_province and steps < max_steps:
                current = path[-1]
                edges = [e for e in adjacency[current] if e["to"] not in visited]
                if not edges:
                    break
                # choose next edge by weighted probability
                weights = [(e["tau"] ** alpha) * (e["eta"] ** beta) for e in edges]
                edge = random.choices(edges, weights, k=1)[0]

                path.append(edge["to"])
                visited.add(edge["to"])
                total_value += edge["value"]
                steps += 1

            if path[-1] == goal_province and total_value < iteration_best_value:
                iteration_best_value = total_value
                iteration_best_path = list(path)
                iteration_edges = [
                    (iteration_best_path[i], iteration_best_path[i + 1])
                    for i in range(len(iteration_best_path) - 1)
                ]

        # Global pheromone update: evaporation
        for u in adjacency:
            for edge in adjacency[u]:
                edge["tau"] *= 1 - evaporation_rate
        # deposit pheromone along iteration best
        if iteration_edges:
            deposit = Q / iteration_best_value
            for u, v in iteration_edges:
                for edge in adjacency[u]:
                    if edge["to"] == v:
                        edge["tau"] += deposit
                        break

        # update global best
        if iteration_best_path and iteration_best_value < best_value:
            best_value = iteration_best_value
            best_path = iteration_best_path

    # build transport_info from best_path
    transport_info = []
    if best_path:
        for i in range(len(best_path) - 1):
            u, v = best_path[i], best_path[i + 1]
            # find edge type
            typ = next(e["type"] for e in adjacency[u] if e["to"] == v)
            transport_info.append((u, v, typ))

    return best_path or [], best_value, transport_info


def calculate_transport_options_aco(
    start: str,
    goal: str,
    cost_priority: float = 0.5,
    **kwargs,
):
    result = {
        "path": [],
        "distance": 0.0,
        "time": 0.0,
        "cost": 0.0,
        "total_value": 0.0,
        "transport_details": [],
    }
    path, total_val, transport_info = ant_colony_optimization(
        start, goal, cost_priority, **kwargs
    )
    if not path:
        return result
    provinces, road_segments = build_graph_from_province_data()
    total_dist = total_time = total_cost = 0.0
    for u, v, ttype in transport_info:
        if ttype == "road":
            key, rev = (u, v), (v, u)
            dist = road_segments.get(
                key,
                road_segments.get(
                    rev,
                    haversine_distance(
                        provinces[u].latitude,
                        provinces[u].longitude,
                        provinces[v].latitude,
                        provinces[v].longitude,
                    ),
                ),
            )
            tm = dist / ROAD_SPEED + (dist // REST_DISTANCE) * REST_TIME
            c = dist * ROAD_COST_PER_KM
        else:
            dist = haversine_distance(
                provinces[u].latitude,
                provinces[u].longitude,
                provinces[v].latitude,
                provinces[v].longitude,
            )
            tm = dist / AIR_SPEED + STORAGE_TIME
            c = dist * AIR_COST_PER_KM
        total_dist += dist
        total_time += tm
        total_cost += c
        result["transport_details"].append(
            {"from": u, "to": v, "type": ttype, "distance": dist, "time": tm, "cost": c}
        )
    result.update(
        {
            "path": path,
            "distance": total_dist,
            "time": total_time,
            "cost": total_cost,
            "total_value": total_val,
        }
    )
    return result

