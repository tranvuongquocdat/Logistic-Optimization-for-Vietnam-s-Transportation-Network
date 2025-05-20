import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.province_node import ProvinceNode
from utils.distance_function import haversine_distance
from utils.heuristic_function import heuristic, AIRPORTS, AIR_SPEED, ROAD_SPEED
from utils.heuristic_function import AIR_COST_PER_KM, ROAD_COST_PER_KM, STORAGE_TIME, REST_DISTANCE, REST_TIME
from data.provinces_infor import coordinates, province_neighbor

from queue import PriorityQueue
from typing import List, Dict, Tuple
import random

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
                    if (province_name, neighbor_name) not in road_segments and (neighbor_name, province_name) not in road_segments:
                        p1_lat, p1_lon = coordinates[province_name]
                        p2_lat, p2_lon = coordinates[neighbor_name]
                        distance = haversine_distance(p1_lat, p1_lon, p2_lat, p2_lon)
                        road_segments[(province_name, neighbor_name)] = distance
    
    return provinces, road_segments

def a_star(start_province: str, goal_province: str, cost_priority: float = 0.5):
    print("Đường đi từ: ", start_province, " đến: ", goal_province)
    """
    Thuật toán A* tìm đường đi tối ưu giữa hai tỉnh/thành
    
    Args:
        start_province: Tỉnh/thành bắt đầu
        goal_province: Tỉnh/thành đích
        cost_priority: Mức độ ưu tiên chi phí (0: ưu tiên thời gian, 1: ưu tiên chi phí)
        
    Returns:
        Tuple chứa đường đi, tổng chi phí và thông tin vận chuyển
    """
    # Xây dựng đồ thị
    provinces, road_segments = build_graph_from_province_data()
    
    # Đảm bảo cost_priority nằm trong khoảng [0, 1]
    cost_priority = max(0.0, min(1.0, cost_priority))
    
    # Reset tất cả các tỉnh/thành
    for province in provinces.values():
        province.reset()
    
    # Kiểm tra tỉnh/thành bắt đầu và đích có tồn tại không
    if start_province not in provinces or goal_province not in provinces:
        return [], float('inf'), []
    
    # Trường hợp đặc biệt: nếu bắt đầu và đích là cùng một tỉnh
    if start_province == goal_province:
        return [start_province], 0.0, []
    
    # Khởi tạo cho điểm bắt đầu
    start_node = provinces[start_province]
    start_node.g_x = 0
    start_node.h_x = heuristic(start_province, goal_province, cost_priority)
    start_node.f_x = start_node.h_x
    start_node.transport_type = "road"  # mặc định bắt đầu bằng đường bộ
    
    # Dictionary để lưu thông tin đường bay đã tính toán
    flights = {}
    
    # Sử dụng PriorityQueue để đảm bảo luôn xét nút có f_x nhỏ nhất trước
    open_set = PriorityQueue()
    open_set.put((start_node.f_x, random.random(), start_node))
    start_node.is_in_open_set = True
    
    # Giới hạn số lần lặp để tránh vòng lặp vô hạn
    max_iterations = 10000
    iterations = 0
    max_space = 0
    closed_set_size = 0
    closed_set = []
    
    while not open_set.empty() and iterations < max_iterations:
        iterations += 1
        
        # Lấy nút có f_x nhỏ nhất
        _, _, current_node = open_set.get()
        current_name = current_node.name
        current_node.is_in_open_set = False
        
        # Nếu đã đến đích, truy vết lại đường đi
        if current_name == goal_province:
            path = []
            temp_node = current_node
            
            # Thu thập đường đi và phương tiện
            transport_types = []
            path = []
            temp_node = current_node
            while temp_node:
                path.append(temp_node.name)
                if temp_node.parent:  # Kiểm tra xem có nút cha hay không
                    current_province = temp_node.name
                    parent_province = temp_node.parent.name
                    # Nếu cả hai tỉnh đều có sân bay, chọn đường bay
                    if current_province in AIRPORTS and parent_province in AIRPORTS:
                        transport_types.append("fly")
                    else:
                        transport_types.append("road")
                temp_node = temp_node.parent
            
            transport_types.reverse()
            path.reverse()
            
            # Gán thông tin phương tiện vào đường đi
            transport_info = []
            for i in range(1, len(path)):
                trans_type = transport_types[i-1] if i-1 < len(transport_types) else "road"
                transport_info.append((path[i-1], path[i], trans_type))

            print("Thuật toán A*")
            print("Tìm thấy đường sau: ", iterations, " steps")
            print("Đường đi: ", path)
            print("Max space: ", max_space)
            
            return path, current_node.g_x, transport_info
        
        # Đánh dấu nút hiện tại đã được thăm
        current_node.is_in_closed_set = True
        closed_set.append(current_name)
        closed_set_size += 1

        if open_set.qsize() + closed_set_size > max_space:
            max_space = open_set.qsize() + closed_set_size

        # 1. Xét các kết nối đường bộ thông thường
        for neighbor_name in provinces[current_name].neighbors:
            if neighbor_name not in provinces:
                continue
                
            neighbor_node = provinces[neighbor_name]
            
            # Bỏ qua nút đã thăm
            if neighbor_node.is_in_closed_set:
                continue
            
            # Tính khoảng cách từ nút hiện tại đến nút kề
            segment_key = (current_name, neighbor_name)
            reverse_segment_key = (neighbor_name, current_name)
            
            if segment_key in road_segments:
                distance = road_segments[segment_key]
            elif reverse_segment_key in road_segments:
                distance = road_segments[reverse_segment_key]
            else:
                # Nếu không có thông tin về đoạn đường, tính khoảng cách trực tiếp
                distance = haversine_distance(
                    current_node.latitude, current_node.longitude,
                    neighbor_node.latitude, neighbor_node.longitude
                )
            
            # Tính g_x mới cho đường bộ
            segment_time = (distance / ROAD_SPEED) + (distance // REST_DISTANCE) * REST_TIME
            segment_cost = distance * ROAD_COST_PER_KM
            segment_value = cost_priority * segment_cost + (1 - cost_priority) * segment_time
            tentative_g_x = current_node.g_x + segment_value
            
            # Nếu nút kề chưa được đưa vào open_set hoặc có g_x mới tốt hơn
            if not neighbor_node.is_in_open_set or tentative_g_x < neighbor_node.g_x:
                neighbor_node.parent = current_node
                neighbor_node.g_x = tentative_g_x
                neighbor_node.h_x = heuristic(neighbor_name, goal_province, cost_priority)
                neighbor_node.f_x = neighbor_node.g_x + neighbor_node.h_x
                neighbor_node.transport_type = "road"
                
                if not neighbor_node.is_in_open_set:
                    open_set.put((neighbor_node.f_x, random.random(), neighbor_node))
                    neighbor_node.is_in_open_set = True
        
        # 2. Xét các kết nối đường hàng không (nếu nút hiện tại có sân bay)
        if current_name in AIRPORTS:
            for airport_name in AIRPORTS:
                if airport_name == current_name:
                    continue
                
                if airport_name not in provinces:
                    continue
                    
                airport_node = provinces[airport_name]
                
                if airport_node.is_in_closed_set:
                    continue
                
                # Tính khoảng cách bay
                flight_key = (current_name, airport_name)
                reverse_flight_key = (airport_name, current_name)
                
                if flight_key in flights:
                    air_distance = flights[flight_key]
                elif reverse_flight_key in flights:
                    air_distance = flights[reverse_flight_key]
                else:
                    p1_lat, p1_lon = coordinates[current_name]
                    p2_lat, p2_lon = coordinates[airport_name]
                    air_distance = haversine_distance(p1_lat, p1_lon, p2_lat, p2_lon)
                    flights[flight_key] = air_distance
                
                # Tính g_x mới cho đường bay
                air_time = (air_distance / AIR_SPEED) + STORAGE_TIME
                air_cost = air_distance * AIR_COST_PER_KM
                air_value = cost_priority * air_cost + (1 - cost_priority) * air_time
                tentative_g_x = current_node.g_x + air_value
                
                if not airport_node.is_in_open_set or tentative_g_x < airport_node.g_x:
                    airport_node.parent = current_node
                    airport_node.g_x = tentative_g_x
                    airport_node.h_x = heuristic(airport_name, goal_province, cost_priority)
                    airport_node.f_x = airport_node.g_x + airport_node.h_x
                    airport_node.transport_type = "fly"
                    
                    if not airport_node.is_in_open_set:
                        open_set.put((airport_node.f_x, random.random(), airport_node))
                        airport_node.is_in_open_set = True

        #space = tổng trong openset + closedset
        if open_set.qsize() + len(provinces) > max_space:
            max_space = open_set.qsize() + len(provinces)
    
    # Không tìm thấy đường đi
    return [], float('inf'), []

def calculate_transport_options(start: str, goal: str, cost_priority: float = 0.5):
    """
    Tính toán các phương án vận chuyển sử dụng A*
    
    Args:
        start: Tỉnh/thành bắt đầu
        goal: Tỉnh/thành đích
        cost_priority: Mức độ ưu tiên chi phí (0: ưu tiên thời gian, 1: ưu tiên chi phí)
        
    Returns:
        Dictionary chứa thông tin của phương án
    """
    # Kết quả trả về
    result = {
        "path": [],
        "distance": 0,
        "time": 0,
        "cost": 0,
        "total_value": 0,
        "heuristic_value": 0,
        "transport_details": []
    }
    
    # Lấy đường đi tối ưu từ A*
    path, total_cost, transport_info = a_star(start, goal, cost_priority)
    
    # Nếu tìm được đường đi
    if path:
        result["path"] = path
        
        # Tính chi tiết từng đoạn
        total_distance = 0
        total_time = 0
        total_monetary_cost = 0
        
        # Xây dựng đồ thị để lấy road_segments
        _, road_segments = build_graph_from_province_data()
        
        # Lưu thông tin chi tiết về từng đoạn đường
        segments_details = []
        
        for i in range(len(transport_info)):
            from_province, to_province, transport_type = transport_info[i]
            
            # Kiểm tra lại xem đoạn đường này có thực sự là đường bay không
            if transport_type == "fly" and (from_province not in AIRPORTS or to_province not in AIRPORTS):
                transport_type = "road"
            
            # Tính khoảng cách
            if transport_type == "road":
                segment_key = (from_province, to_province)
                reverse_segment_key = (to_province, from_province)
                
                if segment_key in road_segments:
                    distance = road_segments[segment_key]
                elif reverse_segment_key in road_segments:
                    distance = road_segments[reverse_segment_key]
                else:
                    p1_lat, p1_lon = coordinates[from_province]
                    p2_lat, p2_lon = coordinates[to_province]
                    distance = haversine_distance(p1_lat, p1_lon, p2_lat, p2_lon)
                
                # Tính thời gian và chi phí cho đường bộ
                time = (distance / ROAD_SPEED) + (distance // REST_DISTANCE) * REST_TIME
                cost = distance * ROAD_COST_PER_KM
            else:  # transport_type == "fly"
                # Tính khoảng cách bay
                p1_lat, p1_lon = coordinates[from_province]
                p2_lat, p2_lon = coordinates[to_province]
                distance = haversine_distance(p1_lat, p1_lon, p2_lat, p2_lon)
                
                # Tính thời gian và chi phí cho đường bay
                time = (distance / AIR_SPEED) + STORAGE_TIME
                cost = distance * AIR_COST_PER_KM
            
            # Cộng dồn
            total_distance += distance
            total_time += time
            total_monetary_cost += cost
            
            # Lưu thông tin chi tiết
            segment_detail = {
                "from": from_province,
                "to": to_province,
                "type": transport_type,
                "distance": distance,
                "time": time,
                "cost": cost
            }
            segments_details.append(segment_detail)
        
        # Cập nhật kết quả
        result["distance"] = total_distance
        result["time"] = total_time
        result["cost"] = total_monetary_cost
        result["total_value"] = total_cost
        result["heuristic_value"] = cost_priority * total_monetary_cost + (1 - cost_priority) * total_time
        result["transport_details"] = segments_details
    
    return result 