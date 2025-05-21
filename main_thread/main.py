import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba

# Import algorithms
from algorithms.UCS import ucs, build_graph_from_province_data, calculate_transport_options_ucs
from algorithms.a_star import a_star, calculate_transport_options
from algorithms.floyd_warshall import floyd_warshall, calculate_transport_options_floyd_warshall
from algorithms.ACO import calculate_transport_options_aco
from algorithms.greedy_best_first_search import calculate_transport_options_greedy
from data.provinces_infor import provinces, coordinates

#turn of warning
import warnings
warnings.filterwarnings("ignore")

def main():
    st.title("Tối ưu hóa Logistics cho mạng lưới giao thông Việt Nam")
    
    # Initialize session state for destination selection
    if 'start_province' not in st.session_state:
        st.session_state.start_province = provinces[0]
    if 'end_province' not in st.session_state:
        # Set default end province to TP Hồ Chí Minh
        st.session_state.end_province = "TP Hồ Chí Minh"
    
    # Sidebar for algorithm selection and parameters
    st.sidebar.header("Cài đặt")
    
    # Algorithm selection
    algorithm = st.sidebar.selectbox(
        "Chọn thuật toán",
        ["UCS (Uniform Cost Search)", "A* (A-Star)", "Floyd-Warshall", "ACO (Ant Colony Optimization)", "Greedy Best First Search"],
        key="algorithm_selection"
    )
    
    # Start province selection with callback to update valid destinations
    def on_start_change():
        # Only update end_province if it's the same as start_province
        if st.session_state.end_province == st.session_state.start_province:
            # If start is TP Hồ Chí Minh, set end to Hà Nội
            if st.session_state.start_province == "TP Hồ Chí Minh":
                st.session_state.end_province = "Hà Nội"
            # If start is Hà Nội, set end to TP Hồ Chí Minh
            elif st.session_state.start_province == "Hà Nội":
                st.session_state.end_province = "TP Hồ Chí Minh"
            # Otherwise find first province that's different from start
            else:
                for p in provinces:
                    if p != st.session_state.start_province:
                        st.session_state.end_province = p
                        break
    
    # Start and destination selection
    start_province = st.sidebar.selectbox(
        "Địa điểm xuất phát", 
        provinces,
        key="start_province",
        on_change=on_start_change
    )
    
    # Filter end provinces to exclude start province
    valid_end_provinces = [p for p in provinces if p != start_province]
    
    end_province = st.sidebar.selectbox(
        "Địa điểm đích", 
        valid_end_provinces,
        key="end_province"
    )
    
    # Cost priority slider
    cost_priority = st.sidebar.slider(
        "Ưu tiên chi phí", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.5, 
        help="0: Ưu tiên thời gian, 1: Ưu tiên chi phí",
        key="cost_priority"
    )
    
    # Button to run algorithm
    if st.sidebar.button("Tìm đường"):
        # Run the selected algorithm
        if algorithm == "UCS (Uniform Cost Search)":
            # Run UCS algorithm
            result = calculate_transport_options_ucs(start_province, end_province, cost_priority)
            
            st.subheader("Kết quả tìm đường với UCS")
            display_results(result, start_province, end_province)
            
        elif algorithm == "A* (A-Star)":  # A*
            # Run A* algorithm
            result = calculate_transport_options(start_province, end_province, cost_priority)
            
            st.subheader("Kết quả tìm đường với A*")
            display_results(result, start_province, end_province)

        elif algorithm == "Floyd-Warshall":
            result = calculate_transport_options_floyd_warshall(start_province, end_province, cost_priority)

            st.subheader("Kết quả tìm đường với Floyd-Warshall")
            display_results(result, start_province, end_province)

        elif algorithm == "ACO (Ant Colony Optimization)":
            result = calculate_transport_options_aco(start_province, end_province, cost_priority)

            st.subheader("Kết quả tìm đường với ACO")
            display_results(result, start_province, end_province)

        elif algorithm == "Greedy Best First Search":
            result = calculate_transport_options_greedy(start_province, end_province, cost_priority)

            st.subheader("Kết quả tìm đường với Greedy Best First Search")
            display_results(result, start_province, end_province)
            
            

def display_results(result, start_province, end_province):
    if result and 'path' in result and result['path']:
        # Display path information
        st.write("**Đường đi tối ưu:**", " -> ".join(result['path']))
        
        # Display time and cost information
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Tổng chi phí:**", f"{round(result['cost'], 2):,} VND")
        with col2:
            # Calculate time in hours and minutes
            total_hours = int(result['time'])
            total_minutes = int((result['time'] - total_hours) * 60)
            st.write("**Tổng thời gian:**", f"{total_hours} giờ {total_minutes} phút")

        # Visualize the path on a map
        visualize_path_on_map(result['path'], result['transport_details'])
        
        # Display detailed information for each segment
        st.subheader("Chi tiết từng đoạn đường")
        
        for transport in result['transport_details']:
            transport_type = 'máy bay' if transport['type'] == 'fly' else 'đường bộ'
            hours = int(transport['time'])
            minutes = int((transport['time'] - hours) * 60)
            
            st.write(f"**{transport['from']} → {transport['to']} ({transport_type}):**")
            cols = st.columns(3)
            with cols[0]:
                st.write(f"Khoảng cách: {round(transport['distance'], 2)} km")
            with cols[1]:
                st.write(f"Thời gian: {hours} giờ {minutes} phút")
            with cols[2]:
                st.write(f"Chi phí: {round(transport['cost'], 2):,} VND")
            st.markdown("---")
        
        
    else:
        st.error("Không tìm thấy đường đi giữa hai địa điểm này.")

def visualize_path_on_map(path, transport_details):
    # Create a map centered at Vietnam
    m = folium.Map(location=[16.0, 106.0], zoom_start=6, tiles="cartodbpositron")
    
    # Add markers for all provinces in the path
    for i, province in enumerate(path):
        if province in coordinates:
            lat, lon = coordinates[province]
            
            # Different color for start, end and intermediate points
            if i == 0:  # Start
                icon_color = 'green'
                popup_text = f"Xuất phát: {province}"
            elif i == len(path) - 1:  # End
                icon_color = 'red'
                popup_text = f"Đích: {province}"
            else:  # Intermediate
                icon_color = 'blue'
                popup_text = f"Điểm dừng: {province}"
                
            folium.Marker(
                location=[lat, lon],
                popup=popup_text,
                icon=folium.Icon(color=icon_color)
            ).add_to(m)
    
    # Add path lines
    for i in range(len(path) - 1):
        start_province = path[i]
        end_province = path[i + 1]
        
        # Find the transport type
        transport_type = next((t['type'] for t in transport_details if t['from'] == start_province and t['to'] == end_province), 'road')
        
        if start_province in coordinates and end_province in coordinates:
            start_lat, start_lon = coordinates[start_province]
            end_lat, end_lon = coordinates[end_province]
            
            # Different line style for different transport types
            if transport_type == 'fly':
                # Dashed line for flights
                folium.PolyLine(
                    locations=[[start_lat, start_lon], [end_lat, end_lon]],
                    color='red',
                    weight=3,
                    opacity=0.7,
                    dash_array='10'
                ).add_to(m)
            else:
                # Solid line for road transport
                folium.PolyLine(
                    locations=[[start_lat, start_lon], [end_lat, end_lon]],
                    color='blue',
                    weight=3,
                    opacity=0.7
                ).add_to(m)
    
    # Display the map
    st.subheader("Bản đồ đường đi")
    folium_static(m, width=800, height=800)
    
    # Create a simple legend for the map
    st.markdown("""
    **Chú thích:**
    - 🟢 Xuất phát
    - 🔴 Đích
    - 🔵 Điểm dừng
    - <span style='color:blue'>━━━</span> Đường bộ
    - <span style='color:red'>┅┅┅</span> Đường bay
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
