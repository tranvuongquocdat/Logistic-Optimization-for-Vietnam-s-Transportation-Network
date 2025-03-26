# algorithms.py
from models import Node, RoadSegment
from data import ADJACENCY_MAP, DISTANCES
import heapq

def heuristic(node: str, goal: str) -> float:
    """Hàm heuristic (ước lượng khoảng cách từ node đến goal)"""
    return DISTANCES.get((node, goal), float('inf')) if (node, goal) in DISTANCES else 0

def a_star(start: str, goal: str) -> Tuple[List[str], float]:
    """Thuật toán A* tìm đường ngắn nhất"""
    nodes: Dict[str, Node] = {province: Node(province, ADJACENCY_MAP.get(province, [])) 
                            for province in ADJACENCY_MAP}
    
    # Khởi tạo node bắt đầu
    nodes[start].gx = 0
    nodes[start].fx = heuristic(start, goal)
    
    # Hàng đợi ưu tiên
    pq = [(nodes[start].fx, start)]
    visited = set()

    while pq:
        _, current = heapq.heappop(pq)
        
        if current in visited:
            continue
        
        visited.add(current)
        if current == goal:
            break

        # Duyệt các node liền kề
        for neighbor in nodes[current].adjacents:
            if neighbor in visited:
                continue
            
            tentative_gx = nodes[current].gx + DISTANCES.get((current, neighbor), float('inf'))
            if tentative_gx < nodes[neighbor].gx:
                nodes[neighbor].parent = current
                nodes[neighbor].gx = tentative_gx
                nodes[neighbor].fx = tentative_gx + heuristic(neighbor, goal)
                heapq.heappush(pq, (nodes[neighbor].fx, neighbor))

    # Truy vết đường đi
    path = []
    current = goal
    while current:
        path.append(current)
        current = nodes[current].parent
    path.reverse()

    return path, nodes[goal].gx

# Tương tự có thể thêm UCS hoặc các thuật toán khác