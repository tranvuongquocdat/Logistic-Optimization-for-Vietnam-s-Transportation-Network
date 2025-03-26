import math

def haversine_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0
    
    #Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    #Compute differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    #Compute the great-circle distance
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    #Calculate the distance
    distance = R * c
    
    return distance

def euclidean_distance(lat1, lon1, lat2, lon2):
    # 1 degree = 111km
    avg_lat = (lat1 + lat2) / 2
    x1 = lon1 * math.cos(math.radians(avg_lat)) * 111
    y1 = lat1 * 111
    x2 = lon2 * math.cos(math.radians(avg_lat)) * 111
    y2 = lat2 * 111
    
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
def manhattan_distance(lat1, lon1, lat2, lon2):
    # Average latitude to calculate longitude distance
    avg_lat = math.radians((lat1 + lat2) / 2)
    
    # Distance per degree (approximate)
    km_per_lat = 111.0  # 1 degree latitude ~ 111 km
    km_per_lon = 111.0 * math.cos(avg_lat)  # Adjust for latitude
    
    # Calculate the Manhattan distance
    d_lat = abs(lat2 - lat1) * km_per_lat
    d_lon = abs(lon2 - lon1) * km_per_lon
    distance = d_lat + d_lon
    return distance

def vincenty_distance(lat1, lon1, lat2, lon2):
    # WGS-84 parameters
    a = 6378137.0  # Semi-major axis (m)
    f = 1 / 298.257223563  # Flattening
    b = a * (1 - f)  # Semi-minor axis (m)

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Difference in longitude
    L = lon2_rad - lon1_rad
    
    # Calculate U1, U2 (reduced latitude)
    U1 = math.atan((1 - f) * math.tan(lat1_rad))
    U2 = math.atan((1 - f) * math.tan(lat2_rad))
    
    sinU1 = math.sin(U1)
    cosU1 = math.cos(U1)
    sinU2 = math.sin(U2)
    cosU2 = math.cos(U2)
    
    # Initialize lambda
    lambda_ = L
    lambda_prev = 2 * math.pi
    
    # Loop to calculate lambda
    iter_limit = 100
    for _ in range(iter_limit):
        sin_lambda = math.sin(lambda_)
        cos_lambda = math.cos(lambda_)
        
        sin_sigma = math.sqrt((cosU2 * sin_lambda)**2 + (cosU1 * sinU2 - sinU1 * cosU2 * cos_lambda)**2)
        if sin_sigma == 0:
            return 0.0  # Two points coincide
        
        cos_sigma = sinU1 * sinU2 + cosU1 * cosU2 * cos_lambda
        sigma = math.atan2(sin_sigma, cos_sigma)
        
        sin_alpha = cosU1 * cosU2 * sin_lambda / sin_sigma
        cos_sq_alpha = 1 - sin_alpha**2
        cos_2sigma_m = cos_sigma - 2 * sinU1 * sinU2 / cos_sq_alpha if cos_sq_alpha != 0 else 0
        
        C = f / 16 * cos_sq_alpha * (4 + f * (4 - 3 * cos_sq_alpha))
        lambda_prev = lambda_
        lambda_ = L + (1 - C) * f * sin_alpha * (sigma + C * sin_sigma * (cos_2sigma_m + C * cos_sigma * (-1 + 2 * cos_2sigma_m**2)))
        
        if abs(lambda_ - lambda_prev) < 1e-12:
            break
    
    # Calculate the distance
    u_sq = cos_sq_alpha * (a**2 - b**2) / b**2
    A = 1 + u_sq / 16384 * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))
    B = u_sq / 1024 * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))
    delta_sigma = B * sin_sigma * (cos_2sigma_m + B / 4 * (cos_sigma * (-1 + 2 * cos_2sigma_m**2) - B / 6 * cos_2sigma_m * (-3 + 4 * sin_sigma**2) * (-3 + 4 * cos_2sigma_m**2)))
    
    s = b * A * (sigma - delta_sigma)  # Distance (m)
    return s / 1000  # Convert to km