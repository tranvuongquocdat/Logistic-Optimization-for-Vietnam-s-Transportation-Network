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
from data.provinces_infor import provinces, coordinates

def main():
    st.title("Tối ưu hóa Logistics cho mạng lưới giao thông Việt Nam")
    
    # Sidebar for algorithm selection and parameters
    st.sidebar.header("Cài đặt")
    
    # Algorithm selection
    algorithm = st.sidebar.selectbox(
        "Chọn thuật toán",
        ["UCS (Uniform Cost Search)", "A* (A-Star)"]
    )
    
    # Start and destination selection
    start_province = st.sidebar.selectbox("Địa điểm xuất phát", provinces)
    end_province = st.sidebar.selectbox("Địa điểm đích", [p for p in provinces if p != start_province])
    
    # Cost priority slider
    cost_priority = st.sidebar.slider(
        "Ưu tiên chi phí", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.5, 
        help="0: Ưu tiên thời gian, 1: Ưu tiên chi phí"
    )
    
    # Button to run algorithm
    if st.sidebar.button("Tìm đường"):
        # Run the selected algorithm
        if algorithm == "UCS (Uniform Cost Search)":
            # Run UCS algorithm
            result = calculate_transport_options_ucs(start_province, end_province, cost_priority)
            
            st.subheader("Kết quả tìm đường với UCS")
            display_results(result, start_province, end_province)
            
        else:  # A*
            # Run A* algorithm
            result = calculate_transport_options(start_province, end_province, cost_priority)
            
            st.subheader("Kết quả tìm đường với A*")
            display_results(result, start_province, end_province)

def display_results(result, start_province, end_province):
    if result and 'path' in result and result['path']:
        # Display path information
        st.write("**Đường đi tối ưu:**", " -> ".join(result['path']))
        st.write("**Tổng chi phí:**", round(result['cost'], 2))
        
        # Display transport information
        for transport in result['transport_details']:
            st.write(f"Đi từ {transport['from']} đến {transport['to']} bằng {'máy bay' if transport['type'] == 'fly' else 'đường bộ'}")
        
        # Visualize the path on a map
        visualize_path_on_map(result['path'], result['transport_details'])
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
