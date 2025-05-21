import math
from algorithms.UCS import build_graph_from_province_data
from utils.distance_function import haversine_distance
from utils.heuristic_function import (
    AIRPORTS,
    AIR_SPEED,
    ROAD_SPEED,
    AIR_COST_PER_KM,
    ROAD_COST_PER_KM,
    STORAGE_TIME,
    REST_DISTANCE,
    REST_TIME,
)
from data.provinces_infor import coordinates


def floyd_warshall(start: str, goal: str, cost_priority: float = 0.5):
    provinces, road_segments = build_graph_from_province_data()
    province_list = list(provinces.keys())
    index = {p: i for i, p in enumerate(province_list)}
    n = len(province_list)

    # Theo dõi số bước và không gian
    iterations = 0
    max_space = 2 * n * n  # Không gian cho hai ma trận n×n (dist và nxt)

    flights = {}
    for u in AIRPORTS:
        if u not in index:
            continue
        for v in AIRPORTS:
            if v not in index or u == v:
                continue
            lat_u = coordinates[u][0]
            lon_u = coordinates[u][1]
            lat_v = coordinates[v][0]
            lon_v = coordinates[v][1]
            d = haversine_distance(lat_u, lon_u, lat_v, lon_v)
            flights[(u, v)] = d

    INF = float("inf")
    dist = [[INF] * n for _ in range(n)]
    nxt = [[None] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0.0
        nxt[i][i] = province_list[i]

    for (u, v), d in road_segments.items():
        i, j = index[u], index[v]
        time_val = d / ROAD_SPEED + (d // REST_DISTANCE) * REST_TIME
        cost_val = d * ROAD_COST_PER_KM / 100000
        w = cost_priority * cost_val + (1 - cost_priority) * time_val
        if w < dist[i][j]:
            dist[i][j] = w
            nxt[i][j] = v
        if w < dist[j][i]:
            dist[j][i] = w
            nxt[j][i] = u

    for (u, v), d in flights.items():
        i, j = index[u], index[v]
        time_val = d / AIR_SPEED + STORAGE_TIME
        cost_val = d * AIR_COST_PER_KM / 100000
        w = cost_priority * cost_val + (1 - cost_priority) * time_val
        if w < dist[i][j]:
            dist[i][j] = w
            nxt[i][j] = v

    # Thuật toán Floyd-Warshall chính - đếm số bước
    for k in range(n):
        for i in range(n):
            if dist[i][k] == INF:
                continue
            for j in range(n):
                if dist[k][j] == INF:
                    continue
                iterations += 1  # Mỗi phép so sánh và cập nhật tính là 1 bước
                nd = dist[i][k] + dist[k][j]
                if nd < dist[i][j]:
                    dist[i][j] = nd
                    nxt[i][j] = nxt[i][k]

    if start not in index or goal not in index:
        return {
            "path": [],
            "distance": 0,
            "time": 0,
            "cost": 0,
            "total_value": INF,
            "transport_details": [],
        }

    i0, j0 = index[start], index[goal]
    if nxt[i0][j0] is None:
        return {
            "path": [],
            "distance": 0,
            "time": 0,
            "cost": 0,
            "total_value": INF,
            "transport_details": [],
        }

    path = [start]
    u = start
    while u != goal:
        next_node = nxt[index[u]][j0]
        if next_node is None:
            break
        u = next_node
        path.append(u)
        if len(path) > n:
            break

    total_value = dist[i0][j0]

    # In thông tin tương tự như trong A*
    print("Thuật toán Floyd-Warshall")
    print("Tìm thấy đường sau: ", iterations, " steps")
    print("Đường đi: ", path)
    print("Max space: ", max_space)

    total_dist = total_time = total_cost = 0.0
    transport_details = []

    for frm, to in zip(path, path[1:]):
        if (frm, to) in flights:
            mode = "fly"
            d = flights[(frm, to)]
            time_val = d / AIR_SPEED + STORAGE_TIME
            cost_val = d * AIR_COST_PER_KM / 100000
        else:
            mode = "road"
            if (frm, to) in road_segments:
                d = road_segments[(frm, to)]
            elif (to, frm) in road_segments:
                d = road_segments[(to, frm)]
            else:
                lat_f = coordinates[frm][0]
                lon_f = coordinates[frm][1]
                lat_t = coordinates[to][0]
                lon_t = coordinates[to][1]
                d = haversine_distance(lat_f, lon_f, lat_t, lon_t)
            time_val = d / ROAD_SPEED + (d // REST_DISTANCE) * REST_TIME
            cost_val = d * ROAD_COST_PER_KM / 100000   
        total_dist += d
        total_time += time_val
        total_cost += cost_val
        transport_details.append(
            {
                "from": frm,
                "to": to,
                "type": mode,
                "distance": d,
                "time": time_val,
                "cost": cost_val,
            }
        )

    return {
        "path": path,
        "distance": total_dist,
        "time": total_time,
        "cost": total_cost,
        "total_value": total_value,
        "transport_details": transport_details,
    }

def calculate_transport_options_floyd_warshall(start: str, goal: str, cost_priority: float = 0.5):
    result = floyd_warshall(start, goal, cost_priority)
    return result
