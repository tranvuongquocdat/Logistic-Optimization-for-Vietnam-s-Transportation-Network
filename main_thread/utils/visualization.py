import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os

def visualize_path(start, goal, path, cost, transport_modes):
    # Create path_results directory if it doesn't exist
    if not os.path.exists("path_results"):
        os.makedirs("path_results")
    
    # Generate unique filename
    base_filename = "path_animation"
    counter = 1
    while os.path.exists(f"path_results/{base_filename}_{counter}.gif"):
        counter += 1
    output_filename = f"path_results/{base_filename}_{counter}.gif"
    
    fig, ax = plt.subplots(figsize=(10, 12))
    plt.scatter(coords_df['Longitude'], coords_df['Latitude'], color='red', s=20, label='Provinces')
    for i, row in coords_df.iterrows():
        plt.text(row['Longitude'], row['Latitude'], row['Province'], fontsize=8, ha='right')

    if path:
        path_coords = coords_df[coords_df['Province'].isin(path)][['Latitude', 'Longitude']].values
        ax.plot(path_coords[:, 1], path_coords[:, 0], 'b-', label=f'Total Cost: {cost:.2f}')

    plt.title(f"Đường đi tối ưu từ {start} đến {goal}", fontsize=16)
    plt.xlabel("Kinh độ (Longitude)", fontsize=12)
    plt.ylabel("Vĩ độ (Latitude)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.xlim(101, 114)
    plt.ylim(8, 24)

    def update(frame):
        ax.clear()
        ax.scatter(coords_df['Longitude'], coords_df['Latitude'], color='red', s=20)
        for i, row in coords_df.iterrows():
            ax.text(row['Longitude'], row['Latitude'], row['Province'], fontsize=8, ha='right')

        if frame < len(transport_modes):
            start_prov, end_prov, mode = transport_modes[frame]
            sub_path = [start_prov, end_prov]
            sub_coords = coords_df[coords_df['Province'].isin(sub_path)][['Latitude', 'Longitude']].values
            color = 'g-' if mode == "truck" else 'b--'  # Xanh cho xe tải, xanh đậm nét đứt cho máy bay
            ax.plot(sub_coords[:, 1], sub_coords[:, 0], color, label=f'{start_prov} -> {end_prov} ({mode})')
            ax.legend()

        ax.set_xlim(101, 114)
        ax.set_ylim(8, 24)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_title(f"Đường đi tối ưu từ {start} đến {goal}", fontsize=16)
        ax.set_xlabel("Kinh độ (Longitude)", fontsize=12)
        ax.set_ylabel("Vĩ độ (Latitude)", fontsize=12)

    if path:
        ani = FuncAnimation(fig, update, frames=len(transport_modes), repeat=False)
        ani.save(output_filename, writer='pillow', fps=1)

    plt.show()