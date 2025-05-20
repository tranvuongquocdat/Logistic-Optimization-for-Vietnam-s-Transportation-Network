# Logistic Optimization for Vietnam's Transportation Network

## Introduction

This project implements various pathfinding algorithms to find the most efficient transportation routes between provinces in Vietnam, balancing cost and travel time.

## Features

- **Multiple pathfinding algorithms**: UCS, A*, Floyd-Warshall, ACO, and Greedy Best-First Search
- **Map visualization**: Display routes and stops on a map of Vietnam
- **Detailed calculations**: Cost, time, and distance for each segment
- **Customizable priorities**: Balance between cost and time based on requirements

## Setup

### Requirements

- Python 3.10 or higher

### Step 1: Clone the repository

```bash
git clone https://github.com/your-username/Logistic-Optimization-for-Vietnam-s-Transportation-Network.git
cd Logistic-Optimization-for-Vietnam-s-Transportation-Network/main_thread
```

### Step 2: Install required libraries

```bash
pip install -r requirements.txt
pip install streamlit folium streamlit-folium
```

## Running the application

### Using Streamlit UI

```bash
cd main_thread
streamlit run main.py
```

After running the command, the web application will automatically open in your browser at `http://localhost:8501`.

### Usage instructions

1. **Select a pathfinding algorithm** in the sidebar (UCS, A*, Floyd-Warshall, ACO, Greedy Best-First Search)
2. **Choose a starting point** from the list of provinces
3. **Select a destination** from the list of provinces (different from the starting point)
4. **Adjust the priority slider** (0: prioritize time, 1: prioritize cost)
5. **Click the "Find Path" button** to calculate and display results

## Project Structure

```
main_thread/
│
├── main.py                 # Application entry point and Streamlit UI
├── main.ipynb              # Jupyter notebook for testing and development
├── requirements.txt        # Python dependencies
│
├── algorithms/             # Implementation of pathfinding algorithms
│   ├── UCS.py              # Uniform Cost Search
│   ├── a_star.py           # A* algorithm
│   ├── floyd_warshall.py   # Floyd-Warshall algorithm
│   ├── ACO.py              # Ant Colony Optimization
│   └── greedy_best_first_search.py  # Greedy Best First Search
│
├── data/                   # Data files and processing
│   ├── provinces_infor.py  # Information about Vietnamese provinces
│   ├── vietnam_provinces_coordinates.csv  # Geographic coordinates
│   ├── crawl_provinces_coordinate.py  # Script to get coordinates
│   └── calculate_distance.py  # Distance calculation utilities
│
└── models/                 # Data models and structures
└── utils/                  # Helper utilities

```

## Authors

- Your Name

## License

MIT 
