# algorithms.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.province_node import ProvinceNode
from models.road_segment import RoadSegment
from utils.heuristic_function import heuristic
from utils.distance_function import haversine_distance
from data.provinces_infor import coordinates, province_neighbor
from queue import PriorityQueue
from typing import List, Dict, Tuple, Optional
import random

def a_star(start_province: str, goal_province: str, 
           provinces: Dict[str, ProvinceNode], 
           road_segments: Dict[Tuple[str, str], float],
           cost_priority: float = 0.5,
           airports: List[str] = None) -> Tuple[List[str], float]:
    """
    Thuật toán A* tìm đường đi tối ưu giữa hai tỉnh/thành, có xét đến khả năng bay trực tiếp
    
    Args:
        start_province: Tỉnh/thành bắt đầu
        goal_province: Tỉnh/thành đích
        provinces: Dictionary chứa tất cả các tỉnh/thành
        road_segments: Dictionary chứa thông tin khoảng cách giữa các tỉnh/thành
        cost_priority: Mức độ ưu tiên chi phí (0: ưu tiên thời gian, 1: ưu tiên chi phí)
        airports: Danh sách các tỉnh có sân bay
        
    Returns:
        Tuple chứa đường đi và tổng chi phí
    """
    # Import các hằng số cần thiết
    from utils.heuristic_function import AIRPORTS, AIR_SPEED, ROAD_SPEED, AIR_COST_PER_KM, ROAD_COST_PER_KM, STORAGE_TIME, REST_DISTANCE, REST_TIME
    
    # Sử dụng AIRPORTS nếu airports không được chỉ định
    if airports is None:
        airports = AIRPORTS
    
    # Đảm bảo cost_priority nằm trong khoảng [0, 1]
    cost_priority = max(0.0, min(1.0, cost_priority))
    
    # Reset tất cả các tỉnh/thành
    for province in provinces.values():
        province.reset()
    
    # Kiểm tra tỉnh/thành bắt đầu và đích có tồn tại không
    if start_province not in provinces or goal_province not in provinces:
        return [], float('inf')
    
    # Trường hợp đặc biệt: nếu bắt đầu và đích là cùng một tỉnh
    if start_province == goal_province:
        return [start_province], 0.0
    
    # Khởi tạo cho điểm bắt đầu
    start_node = provinces[start_province]
    goal_node = provinces[goal_province]
    
    start_node.g_x = 0
    start_node.h_x = heuristic(start_province, goal_province, cost_priority)
    start_node.f_x = start_node.h_x
    
    # Đánh dấu cách di chuyển đến các node (fly/road)
    start_node.transport_type = "road"  # mặc định bắt đầu bằng đường bộ
    
    # Dictionary để lưu thông tin đường bay đã tính toán
    flights = {}
    
    # Sử dụng PriorityQueue để đảm bảo luôn xét nút có f_x nhỏ nhất trước
    open_set = PriorityQueue()
    # Thêm một số ngẫu nhiên để phá vỡ ties khi f_x bằng nhau
    open_set.put((start_node.f_x, random.random(), start_node))
    
    # Đánh dấu nút bắt đầu đã được đưa vào open_set
    start_node.is_in_open_set = True
    
    # Giới hạn số lần lặp để tránh vòng lặp vô hạn
    max_iterations = 10000
    iterations = 0
    
    while not open_set.empty() and iterations < max_iterations:
        iterations += 1
        
        # Lấy nút có f_x nhỏ nhất
        _, _, current_node = open_set.get()
        current_name = current_node.name
        
        # Đánh dấu nút hiện tại đã được đưa ra khỏi open_set
        current_node.is_in_open_set = False
        
        # Nếu đã đến đích, truy vết lại đường đi
        if current_name == goal_province:
            path = []
            temp_node = current_node
            
            # Thu thập đường đi và phương tiện
            transport_types = []
            while temp_node:
                path.append(temp_node.name)
                if hasattr(temp_node, 'transport_type'):
                    transport_types.append(temp_node.transport_type)
                temp_node = temp_node.parent
            
            transport_types.reverse()  # Đảo ngược để cùng thứ tự với path
            path.reverse()
            
            # Gán thông tin phương tiện vào đường đi
            transport_info = []
            for i in range(1, len(path)):
                trans_type = transport_types[i-1] if i-1 < len(transport_types) else "road"
                transport_info.append((path[i-1], path[i], trans_type))
            
            return path, current_node.g_x, transport_info
        
        # Đánh dấu nút hiện tại đã được thăm
        current_node.is_in_closed_set = True
        
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
            # Thời gian = khoảng cách / tốc độ + thời gian nghỉ
            segment_time = (distance / ROAD_SPEED) + (distance // REST_DISTANCE) * REST_TIME
            segment_cost = distance * ROAD_COST_PER_KM
            
            # Tính giá trị tổng hợp dựa trên cost_priority
            segment_value = cost_priority * segment_cost + (1 - cost_priority) * segment_time
            
            tentative_g_x = current_node.g_x + segment_value
            
            # Nếu nút kề chưa được đưa vào open_set hoặc có g_x mới tốt hơn
            if not neighbor_node.is_in_open_set or tentative_g_x < neighbor_node.g_x:
                # Cập nhật thông tin cho nút kề
                neighbor_node.parent = current_node
                neighbor_node.g_x = tentative_g_x
                neighbor_node.h_x = heuristic(neighbor_name, goal_province, cost_priority)
                neighbor_node.f_x = neighbor_node.g_x + neighbor_node.h_x
                neighbor_node.transport_type = "road"  # Đi bằng đường bộ
                
                # Nếu nút kề chưa được đưa vào open_set, thêm vào
                if not neighbor_node.is_in_open_set:
                    open_set.put((neighbor_node.f_x, random.random(), neighbor_node))
                    neighbor_node.is_in_open_set = True
        
        # 2. Xét các kết nối đường hàng không (nếu nút hiện tại có sân bay)
        if current_name in airports:
            # Duyệt qua tất cả các sân bay đích tiềm năng
            for airport_name in airports:
                # Không xét bay đến chính mình
                if airport_name == current_name:
                    continue
                
                # Lấy thông tin node sân bay đích
                if airport_name not in provinces:
                    continue
                    
                airport_node = provinces[airport_name]
                
                # Bỏ qua nút đã thăm
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
                    # Tính khoảng cách bay giữa hai sân bay
                    p1_lat, p1_lon = coordinates[current_name]
                    p2_lat, p2_lon = coordinates[airport_name]
                    air_distance = haversine_distance(p1_lat, p1_lon, p2_lat, p2_lon)
                    flights[flight_key] = air_distance
                
                # Tính g_x mới cho đường bay
                # Thời gian = khoảng cách / tốc độ + thời gian lưu kho
                air_time = (air_distance / AIR_SPEED) + STORAGE_TIME
                air_cost = air_distance * AIR_COST_PER_KM
                
                # Tính giá trị tổng hợp dựa trên cost_priority
                air_value = cost_priority * air_cost + (1 - cost_priority) * air_time
                
                tentative_g_x = current_node.g_x + air_value
                
                # Nếu nút sân bay chưa được đưa vào open_set hoặc có g_x mới tốt hơn
                if not airport_node.is_in_open_set or tentative_g_x < airport_node.g_x:
                    # Cập nhật thông tin cho nút sân bay
                    airport_node.parent = current_node
                    airport_node.g_x = tentative_g_x
                    airport_node.h_x = heuristic(airport_name, goal_province, cost_priority)
                    airport_node.f_x = airport_node.g_x + airport_node.h_x
                    airport_node.transport_type = "fly"  # Đi bằng máy bay
                    
                    # Nếu nút sân bay chưa được đưa vào open_set, thêm vào
                    if not airport_node.is_in_open_set:
                        open_set.put((airport_node.f_x, random.random(), airport_node))
                        airport_node.is_in_open_set = True
    
    # Không tìm thấy đường đi hoặc vượt quá số lần lặp tối đa
    if iterations >= max_iterations:
        print(f"Đã vượt quá số lượng lặp tối đa ({max_iterations})")
    return [], float('inf'), []

def build_graph_from_province_data() -> Tuple[Dict[str, ProvinceNode], Dict[Tuple[str, str], float]]:
    """
    Xây dựng đồ thị từ dữ liệu về các tỉnh/thành
    
    Returns:
        Tuple chứa dictionary các tỉnh/thành và dictionary các đoạn đường
    """
    provinces = {}
    road_segments = {}
    
    # Tạo các nút tỉnh/thành
    for province_name, (lat, lon) in coordinates.items():
        province_id = hash(province_name)  # Tạo ID từ tên tỉnh
        provinces[province_name] = ProvinceNode(province_id, province_name, lat, lon)
    
    # Sử dụng thông tin liền kề từ province_neighbor để xây dựng đồ thị
    for province_name, neighbors_list in province_neighbor.items():
        if province_name in provinces:
            # Thêm các tỉnh liền kề vào danh sách neighbors
            for neighbor_name in neighbors_list:
                if neighbor_name in provinces:
                    # Thêm neighbor_name vào danh sách neighbor của province_name
                    provinces[province_name].add_neighbor(neighbor_name)
                    
                    # Tính khoảng cách giữa hai tỉnh
                    if (province_name, neighbor_name) not in road_segments and (neighbor_name, province_name) not in road_segments:
                        p1_lat, p1_lon = coordinates[province_name]
                        p2_lat, p2_lon = coordinates[neighbor_name]
                        distance = haversine_distance(p1_lat, p1_lon, p2_lat, p2_lon)
                        road_segments[(province_name, neighbor_name)] = distance
    
    # Kiểm tra tính liên thông của đồ thị
    connected_provinces = set()
    
    def dfs(province):
        connected_provinces.add(province)
        for neighbor in provinces[province].neighbors:
            if neighbor not in connected_provinces and neighbor in provinces:
                dfs(neighbor)
    
    if provinces:
        # Bắt đầu DFS từ tỉnh đầu tiên
        first_province = next(iter(provinces.keys()))
        dfs(first_province)
        
        # Kiểm tra xem có tỉnh nào không được kết nối
        if len(connected_provinces) < len(provinces):
            print("Cảnh báo: Đồ thị tỉnh không liên thông hoàn toàn!")
            for province in provinces:
                if province not in connected_provinces:
                    print(f"  - Tỉnh '{province}' không được kết nối với đồ thị chính")
    
    return provinces, road_segments

def calculate_transport_options(start: str, goal: str, cost_priority: float = 0.5) -> Dict:
    """
    Tính toán các phương án vận chuyển: đường bộ, bay thẳng, và kết hợp
    
    Args:
        start: Tỉnh/thành bắt đầu
        goal: Tỉnh/thành đích
        cost_priority: Mức độ ưu tiên chi phí (0: ưu tiên thời gian, 1: ưu tiên chi phí)
        
    Returns:
        Dictionary chứa thông tin của các phương án
    """
    from utils.heuristic_function import AIRPORTS, ROAD_SPEED, AIR_SPEED, ROAD_COST_PER_KM, AIR_COST_PER_KM, REST_DISTANCE, REST_TIME, STORAGE_TIME
    from utils.heuristic_function import heuristic
    
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
    
    # Lấy đường đi tối ưu từ A* (đã tích hợp cả hai phương án)
    provinces, road_segments = build_graph_from_province_data()
    path, total_cost, transport_info = a_star(start, goal, provinces, road_segments, cost_priority, AIRPORTS)
    
    # Nếu tìm được đường đi
    if path:
        result["path"] = path
        
        # Tính chi tiết từng đoạn
        total_distance = 0
        total_time = 0
        total_monetary_cost = 0
        
        # Lưu thông tin chi tiết về từng đoạn đường
        segments_details = []
        
        for i in range(len(transport_info)):
            from_province, to_province, transport_type = transport_info[i]
            
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
        result["total_value"] = total_monetary_cost
        result["heuristic_value"] = cost_priority * total_monetary_cost + (1 - cost_priority) * total_time
        result["transport_details"] = segments_details
    
    return result

# Hàm demo để thử nghiệm thuật toán
def demo_a_star():
    provinces, road_segments = build_graph_from_province_data()
    
    # Danh sách các cặp tỉnh để kiểm thử
    test_pairs = [          
        ("Lào Cai", "Thừa Thiên Huế"),           
    ]
    
    # Các mức cost_priority để thử nghiệm
    cost_priorities = [0.1, 0.5, 0.9]
    
    for start, goal in test_pairs:
        print(f"\n{'='*70}")
        print(f"ĐƯỜNG ĐI TỪ {start} ĐẾN {goal}")
        print(f"{'='*70}")
        
        # Kiểm tra có sân bay không
        from utils.heuristic_function import AIRPORTS
        start_has_airport = "CÓ" if start in AIRPORTS else "KHÔNG"
        goal_has_airport = "CÓ" if goal in AIRPORTS else "KHÔNG"
        print(f"{start} {start_has_airport} sân bay, {goal} {goal_has_airport} sân bay")
        
        # Tính khoảng cách trực tiếp
        if start in coordinates and goal in coordinates:
            s_lat, s_lon = coordinates[start]
            g_lat, g_lon = coordinates[goal]
            direct_distance = haversine_distance(s_lat, s_lon, g_lat, g_lon)
            print(f"Khoảng cách trực tiếp: {direct_distance:.2f} km")
        
        # Thử với các mức ưu tiên khác nhau
        for cost_priority in cost_priorities:
            print(f"\nCost priority: {cost_priority}")
            print(f"- Mức ưu tiên: {int(cost_priority*100)}% chi phí, {int((1-cost_priority)*100)}% thời gian")
            
            # Tính toán phương án tối ưu (đã tích hợp cả đường bộ và bay)
            options = calculate_transport_options(start, goal, cost_priority)
            
            # Hiển thị phương án tối ưu
            print("\nPHƯƠNG ÁN TỐI ƯU:")
            if options["path"]:
                print(f"- Đường đi: {' -> '.join(options['path'])}")
                print(f"- Độ dài đường đi: {len(options['path'])} tỉnh/thành")
                print(f"- Tổng khoảng cách: {options['distance']:.2f} km")
                print(f"- Thời gian ước tính: {options['time']:.2f} giờ")
                print(f"- Chi phí ước tính: ${options['cost']:.2f}")
                print(f"- Giá trị heuristic: {options['heuristic_value']:.2f}")
                
                # Hiển thị chi tiết từng đoạn đường
                print("\nCHI TIẾT TỪNG ĐOẠN ĐƯỜNG:")
                for i, segment in enumerate(options["transport_details"]):
                    trans_type = "ĐƯỜNG BỘ" if segment["type"] == "road" else "MÁY BAY"
                    print(f"  {i+1}. {segment['from']} -> {segment['to']} ({trans_type}):")
                    print(f"     - Khoảng cách: {segment['distance']:.2f} km")
                    print(f"     - Thời gian: {segment['time']:.2f} giờ")
                    print(f"     - Chi phí: ${segment['cost']:.2f}")
            else:
                print("- Không tìm thấy đường đi!")
            
            print("-" * 70)

# Import các hằng số cần thiết cho demo
from utils.heuristic_function import AIRPORTS, ROAD_SPEED, REST_DISTANCE, REST_TIME

if __name__ == "__main__":
    demo_a_star()
