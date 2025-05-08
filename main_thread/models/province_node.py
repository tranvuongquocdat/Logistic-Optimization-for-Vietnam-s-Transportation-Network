from typing import List, Tuple, Dict, Optional

class ProvinceNode:
    def __init__(self, province_id: int, name: str, latitude: float, longitude: float):
        self.province_id = province_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.neighbors = []
        self.g_x = float('inf')
        self.h_x = float('inf')
        self.f_x = float('inf')
        self.parent = None
        self.is_visited = False
        self.is_in_open_set = False
        self.is_in_closed_set = False

    def add_neighbor(self, neighbor: str):
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)

    def __lt__(self, other: 'ProvinceNode'):
        if self.f_x == other.f_x:
            # Nếu f_x bằng nhau, ưu tiên nút có h_x nhỏ hơn
            return self.h_x < other.h_x
        return self.f_x < other.f_x
        
    def __eq__(self, other: 'ProvinceNode'):
        if other is None:
            return False
        return self.province_id == other.province_id
    
    def __hash__(self):
        return hash(self.province_id)
    
    def reset(self):
        self.g_x = float('inf')
        self.h_x = float('inf')
        self.f_x = float('inf')
        self.parent = None
        self.is_visited = False
        self.is_in_open_set = False
        self.is_in_closed_set = False
        
    def __str__(self):
        return f"Province: {self.name} (ID: {self.province_id}, f_x: {self.f_x}, g_x: {self.g_x}, h_x: {self.h_x})"
    
    def __repr__(self):
        return self.__str__()