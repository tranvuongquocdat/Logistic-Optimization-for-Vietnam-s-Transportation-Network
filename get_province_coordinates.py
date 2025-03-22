import requests
import csv
import time
from tqdm import tqdm

# URL cơ bản của Nominatim
BASE_URL = "https://nominatim.openstreetmap.org/search"

# Danh sách 63 tỉnh thành Việt Nam
provinces = [
    "Hà Nội", "TP Hồ Chí Minh", "Hải Phòng", "Đà Nẵng", "Cần Thơ", "Hà Giang", "Cao Bằng",
    "Lai Châu", "Lào Cai", "Tuyên Quang", "Lạng Sơn", "Bắc Kạn", "Thái Nguyên", "Yên Bái",
    "Sơn La", "Phú Thọ", "Vĩnh Phúc", "Quảng Ninh", "Bắc Giang", "Bắc Ninh", "Hải Dương",
    "Hưng Yên", "Hòa Bình", "Hà Nam", "Nam Định", "Thái Bình", "Ninh Bình", "Thanh Hóa",
    "Nghệ An", "Hà Tĩnh", "Quảng Bình", "Quảng Trị", "Thừa Thiên Huế", "Quảng Nam",
    "Quảng Ngãi", "Bình Định", "Phú Yên", "Khánh Hòa", "Ninh Thuận", "Bình Thuận", "Kon Tum",
    "Gia Lai", "Đắk Lắk", "Đắk Nông", "Lâm Đồng", "Bình Phước", "Tây Ninh", "Bình Dương",
    "Đồng Nai", "Bà Rịa - Vũng Tàu", "Long An", "Tiền Giang", "Bến Tre", "Trà Vinh",
    "Vĩnh Long", "Đồng Tháp", "An Giang", "Kiên Giang", "Hậu Giang", "Sóc Trăng",
    "Bạc Liêu", "Cà Mau"
]

# Lưu kết quả vào danh sách để ghi vào CSV
data = []

# Thiết lập header với User-Agent
headers = {
    "User-Agent": "MyGeocodingApp/1.0 (contact@example.com)"  # Thay bằng thông tin của bạn
}

# Lặp qua từng tỉnh để lấy tọa độ
for province in tqdm(provinces):
    try:
        # Tạo tham số cho yêu cầu
        params = {
            "q": f"{province}, Vietnam",
            "format": "json",
            "limit": 1  # Chỉ lấy kết quả đầu tiên
        }
        
        # Gửi yêu cầu GET tới Nominatim API với header
        response = requests.get(BASE_URL, params=params, headers=headers)
        
        # Kiểm tra mã trạng thái HTTP
        if response.status_code == 200:
            geocode_result = response.json()
            
            # Kiểm tra xem có kết quả hay không
            if geocode_result:
                lat = geocode_result[0]["lat"]
                lng = geocode_result[0]["lon"]
                data.append([province, lat, lng])
                print(f"{province}: ({lat}, {lng})")
            else:
                print(f"Không tìm thấy tọa độ cho {province}")
                data.append([province, "N/A", "N/A"])
        else:
            print(f"Lỗi phản hồi từ server cho {province}: {response.status_code}")
            data.append([province, "N/A", "N/A"])
        
        # Đợi 1 giây để tuân thủ giới hạn tốc độ của Nominatim
        time.sleep(1)
        
    except Exception as e:
        print(f"Lỗi khi xử lý {province}: {str(e)}")
        data.append([province, "Error", "Error"])

# Ghi dữ liệu vào file CSV
with open("vietnam_provinces_coordinates.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    # Ghi tiêu đề
    writer.writerow(["Province", "Latitude", "Longitude"])
    # Ghi dữ liệu
    writer.writerows(data)

print("Dữ liệu đã được lưu vào file vietnam_provinces_coordinates.csv")