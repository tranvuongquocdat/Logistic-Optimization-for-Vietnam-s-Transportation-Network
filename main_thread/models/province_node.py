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

    def add_neighbor(self, neighbor: 'ProvinceNode'):
        self.neighbors.append(neighbor)

    def __lt__(self, other: 'ProvinceNode'):
        return self.f_x < other.f_x
        
    def __eq__(self, other: 'ProvinceNode'):
        return self.province_id == other.province_id
    
    def __hash__(self):
        return hash(self.province_id)
    
    def reset(self):
        self.g_x = float('inf')
        self.h_x = float('inf')
        self.f_x = float('inf')
        self.parent = None
        self.is_visited = False
        
    def __str__(self):
        return f"Province: {self.name} (ID: {self.province_id})"
    
    def __repr__(self):
        return self.__str__()