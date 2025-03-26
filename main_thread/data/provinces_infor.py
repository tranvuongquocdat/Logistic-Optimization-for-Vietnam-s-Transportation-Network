from typing import Optional, Dict, List
import pandas as pd

#load vietnam_provinces_coordinates.csv and create a dictionary of coordinates
coordinates = {
    "Hà Nội": (21.0283334, 105.854041),
    "TP Hồ Chí Minh": (10.7763897, 106.7011391),
    "Hải Phòng": (20.858864, 106.6749591),
    "Đà Nẵng": (16.068, 108.212),
    "Cần Thơ": (10.0364634, 105.7875821),
    "Hà Giang": (22.7336097, 105.0027271),
    "Cao Bằng": (22.7426936, 106.1060926),
    "Lai Châu": (22.2921668, 103.1798662),
    "Lào Cai": (22.3069302, 104.1829592),
    "Tuyên Quang": (22.0747798, 105.258411),
    "Lạng Sơn": (21.8487579, 106.6140692),
    "Bắc Kạn": (22.2571701, 105.8204437),
    "Thái Nguyên": (21.6498502, 105.8351394),
    "Yên Bái": (21.8268679, 104.663122),
    "Sơn La": (21.2276769, 104.1575944),
    "Phú Thọ": (21.3007538, 105.1349604),
    "Vĩnh Phúc": (21.3778689, 105.5758286),
    "Quảng Ninh": (21.1718046, 107.2012742),
    "Bắc Giang": (21.3169625, 106.437985),
    "Bắc Ninh": (21.0955822, 106.1264766),
    "Hải Dương": (20.8930571, 106.3725441),
    "Hưng Yên": (20.7833912, 106.0699025),
    "Hòa Bình": (20.6763365, 105.3759952),
    "Hà Nam": (20.5340294, 105.98102482169935),
    "Nam Định": (20.2686476, 106.2289075),
    "Thái Bình": (20.5296832, 106.3876068),
    "Ninh Bình": (20.2421142, 105.9746207),
    "Thanh Hóa": (19.9781573, 105.4816107),
    "Nghệ An": (19.1976001, 105.060676),
    "Hà Tĩnh": (18.3504832, 105.7623047),
    "Quảng Bình": (17.509599, 106.4004452),
    "Quảng Trị": (16.7897806, 106.9797431),
    "Thừa Thiên Huế": (16.4639321, 107.5863388),
    "Quảng Nam": (15.5761698, 108.0527132),
    "Quảng Ngãi": (14.9953739, 108.691729),
    "Bình Định": (14.0779378, 108.9898798),
    "Phú Yên": (13.1912633, 109.1273678),
    "Khánh Hòa": (12.2980751, 108.9950386),
    "Ninh Thuận": (11.6965639, 108.8928476),
    "Bình Thuận": (11.1041572, 108.1832931),
    "Kon Tum": (14.6995372, 107.9323831),
    "Gia Lai": (13.8177445, 108.2004015),
    "Đắk Lắk": (12.8292274, 108.2999058),
    "Đắk Nông": (12.2818851, 107.7302484),
    "Lâm Đồng": (11.6614957, 108.1335279),
    "Bình Phước": (11.7543232, 106.9266473),
    "Tây Ninh": (11.4019366, 106.1626927),
    "Bình Dương": (11.1836551, 106.7031737),
    "Đồng Nai": (11.0355624, 107.1881076),
    "Bà Rịa - Vũng Tàu": (10.5738801, 107.3284362),
    "Long An": (10.6983968, 106.1883517),
    "Tiền Giang": (10.4030368, 106.361633),
    "Bến Tre": (10.1093637, 106.4811559),
    "Trà Vinh": (9.8037998, 106.3256808),
    "Vĩnh Long": (10.1203043, 106.0125705),
    "Đồng Tháp": (10.590424, 105.6802341),
    "An Giang": (10.5392057, 105.2312822),
    "Kiên Giang": (9.9904962, 105.2435248),
    "Hậu Giang": (9.7985063, 105.6379524),
    "Sóc Trăng": (9.5628369, 105.9493991),
    "Bạc Liêu": (9.3298341, 105.509946),
    "Cà Mau": (9.0180177, 105.0869724)
}

# List of provinces
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

# Dictionary of province neighbors with diacritics
province_neighbor = {
    "Lai Châu": ["Điện Biên", "Lào Cai", "Sơn La", "Yên Bái"],
    "Yên Bái": ["Lào Cai", "Lai Châu", "Sơn La", "Hà Giang", "Phú Thọ", "Tuyên Quang"],
    "Điện Biên": ["Lai Châu", "Sơn La"],
    "Thanh Hóa": ["Sơn La", "Nghệ An", "Ninh Bình", "Hòa Bình"],
    "Nghệ An": ["Hà Tĩnh", "Thanh Hóa"],
    "Quảng Bình": ["Hà Tĩnh", "Quảng Trị"],
    "Hà Tĩnh": ["Nghệ An", "Quảng Bình"],
    "Thừa Thiên Huế": ["Quảng Trị", "Đà Nẵng", "Quảng Nam"],
    "Quảng Trị": ["Quảng Bình", "Thừa Thiên Huế"],
    "Đà Nẵng": ["Thừa Thiên Huế", "Quảng Nam"],
    "Quảng Nam": ["Đà Nẵng", "Thừa Thiên Huế", "Kon Tum", "Quảng Ngãi"],
    "Kon Tum": ["Quảng Nam", "Quảng Ngãi", "Gia Lai"],
    "Quảng Ngãi": ["Kon Tum", "Quảng Nam", "Bình Định"],
    "Gia Lai": ["Kon Tum", "Bình Định", "Phú Yên", "Đắk Lắk"],
    "Bình Định": ["Quảng Ngãi", "Gia Lai", "Phú Yên"],
    "Đắk Lắk": ["Đắk Nông", "Lâm Đồng", "Khánh Hòa", "Phú Yên", "Gia Lai"],
    "Phú Yên": ["Gia Lai", "Bình Định", "Đắk Lắk", "Khánh Hòa"],
    "Khánh Hòa": ["Đắk Lắk", "Phú Yên", "Lâm Đồng", "Ninh Thuận"],
    "Đắk Nông": ["Đắk Lắk", "Lâm Đồng", "Bình Phước"],
    "Lâm Đồng": ["Đắk Lắk", "Đắk Nông", "Bình Phước", "Đồng Nai", "Bình Thuận", "Ninh Thuận", "Khánh Hòa"],
    "Ninh Thuận": ["Lâm Đồng", "Khánh Hòa", "Bình Thuận"],
    "Bình Phước": ["Tây Ninh", "Bình Dương", "Đồng Nai", "Đắk Nông", "Lâm Đồng"],
    "Đồng Nai": ["Lâm Đồng", "Bình Phước", "Bình Thuận", "TP Hồ Chí Minh", "Bà Rịa - Vũng Tàu", "Bình Dương"],
    "Bình Thuận": ["Bà Rịa - Vũng Tàu", "Lâm Đồng", "Ninh Thuận", "Đồng Nai"],
    "Tây Ninh": ["Long An", "TP Hồ Chí Minh", "Bình Dương", "Bình Phước"],
    "Bình Dương": ["Tây Ninh", "TP Hồ Chí Minh", "Đồng Nai", "Bình Phước"],
    "TP Hồ Chí Minh": ["Tây Ninh", "Bình Dương", "Đồng Nai", "Long An", "Bà Rịa - Vũng Tàu"],
    "Bà Rịa - Vũng Tàu": ["TP Hồ Chí Minh", "Đồng Nai", "Bình Thuận"],
    "Long An": ["Tây Ninh", "TP Hồ Chí Minh", "Đồng Tháp", "Tiền Giang"],
    "Đồng Tháp": ["Long An", "Tiền Giang", "Vĩnh Long", "Cần Thơ", "An Giang"],
    "Tiền Giang": ["Long An", "Đồng Tháp", "Vĩnh Long", "Bến Tre"],
    "Bến Tre": ["Vĩnh Long", "Tiền Giang", "Trà Vinh"],
    "An Giang": ["Kiên Giang", "Cần Thơ", "Đồng Tháp"],
    "Cần Thơ": ["Kiên Giang", "An Giang", "Đồng Tháp", "Vĩnh Long", "Hậu Giang"],
    "Vĩnh Long": ["Cần Thơ", "Đồng Tháp", "Bến Tre", "Trà Vinh", "Hậu Giang"],
    "Trà Vinh": ["Bến Tre", "Vĩnh Long", "Sóc Trăng"],
    "Sóc Trăng": ["Hậu Giang", "Bạc Liêu", "Trà Vinh"],
    "Hậu Giang": ["Kiên Giang", "Bạc Liêu", "Sóc Trăng", "Cần Thơ", "Vĩnh Long"],
    "Kiên Giang": ["An Giang", "Cần Thơ", "Hậu Giang", "Bạc Liêu", "Cà Mau"],
    "Bạc Liêu": ["Kiên Giang", "Hậu Giang", "Sóc Trăng", "Cà Mau"],
    "Cà Mau": ["Kiên Giang", "Bạc Liêu"],
    "Hà Nội": ["Phú Thọ", "Hòa Bình", "Bắc Giang", "Vĩnh Phúc", "Bắc Ninh", "Hưng Yên", "Hà Nam"],
    "Phú Thọ": ["Sơn La", "Yên Bái", "Hòa Bình", "Hà Nội", "Vĩnh Phúc", "Tuyên Quang"],
    "Hòa Bình": ["Ninh Bình", "Thanh Hóa", "Hà Nam", "Hà Nội", "Phú Thọ", "Sơn La"],
    "Bắc Giang": ["Quảng Ninh", "Hải Dương", "Bắc Ninh", "Hà Nội", "Thái Nguyên", "Lạng Sơn"],
    "Vĩnh Phúc": ["Phú Thọ", "Hà Nội", "Thái Nguyên", "Tuyên Quang"],
    "Bắc Ninh": ["Hà Nội", "Hưng Yên", "Hải Dương", "Bắc Giang"],
    "Hưng Yên": ["Hà Nội", "Bắc Ninh", "Hải Dương", "Thái Bình", "Hà Nam"],
    "Hà Nam": ["Hà Nội", "Hưng Yên", "Thái Bình", "Nam Định", "Ninh Bình", "Hòa Bình"],
    "Hải Phòng": ["Thái Bình", "Quảng Ninh", "Hải Dương"],
    "Hải Dương": ["Bắc Ninh", "Hưng Yên", "Thái Bình", "Hải Phòng", "Quảng Ninh", "Bắc Giang"],
    "Nam Định": ["Ninh Bình", "Hà Nam", "Thái Bình"],
    "Thái Nguyên": ["Tuyên Quang", "Bắc Kạn", "Lạng Sơn", "Bắc Giang", "Hà Nội", "Vĩnh Phúc"],
    "Thái Bình": ["Nam Định", "Hà Nam", "Hưng Yên", "Hải Dương", "Hải Phòng"],
    "Quảng Ninh": ["Hải Dương", "Hải Phòng", "Bắc Giang", "Lạng Sơn"],
    "Lạng Sơn": ["Quảng Ninh", "Bắc Giang", "Thái Nguyên", "Bắc Kạn", "Cao Bằng"],
    "Ninh Bình": ["Hòa Bình", "Thanh Hóa", "Nam Định", "Hà Nam"],
    "Lào Cai": ["Lai Châu", "Yên Bái", "Hà Giang"],
    "Cao Bằng": ["Hà Giang", "Bắc Kạn", "Lạng Sơn"],
    "Hà Giang": ["Cao Bằng", "Tuyên Quang", "Yên Bái", "Lào Cai"],
    "Tuyên Quang": ["Hà Giang", "Bắc Kạn", "Thái Nguyên", "Vĩnh Phúc", "Phú Thọ", "Yên Bái"],
    "Bắc Kạn": ["Tuyên Quang", "Thái Nguyên", "Lạng Sơn", "Cao Bằng"],
    "Sơn La": ["Điện Biên", "Yên Bái", "Phú Thọ", "Hòa Bình", "Thanh Hóa"],
}

# Dictionary of logistics regions
logistics_regions = {
    "Đông Bắc Bộ": ["Quảng Ninh", "Lạng Sơn", "Cao Bằng", "Bắc Giang", "Bắc Kạn", "Thái Nguyên", "Hà Giang", "Tuyên Quang"],
    "Tây Bắc Bộ": ["Lào Cai", "Yên Bái", "Điện Biên", "Lai Châu", "Sơn La", "Hòa Bình"],
    "Đồng bằng sông Hồng": ["Hà Nội", "Hải Phòng", "Bắc Ninh", "Vĩnh Phúc", "Phú Thọ", "Hưng Yên", "Hải Dương", "Thái Bình", "Hà Nam", "Nam Định", "Ninh Bình"],
    "Bắc Trung Bộ": ["Thanh Hóa", "Nghệ An", "Hà Tĩnh", "Quảng Bình", "Quảng Trị", "Thừa Thiên Huế"],
    "Duyên hải Nam Trung Bộ": ["Đà Nẵng", "Quảng Nam", "Quảng Ngãi", "Bình Định", "Phú Yên", "Khánh Hòa", "Ninh Thuận", "Bình Thuận"],
    "Tây Nguyên": ["Kon Tum", "Gia Lai", "Đắk Lắk", "Đắk Nông", "Lâm Đồng"],
    "Đông Nam Bộ": ["TP Hồ Chí Minh", "Đồng Nai", "Bình Dương", "Bà Rịa - Vũng Tàu", "Bình Phước", "Tây Ninh"],
    "Đồng bằng sông Cửu Long": ["Long An", "Tiền Giang", "Bến Tre", "Trà Vinh", "Vĩnh Long", "Đồng Tháp", "An Giang", "Kiên Giang", "Cần Thơ", "Hậu Giang", "Sóc Trăng", "Bạc Liêu", "Cà Mau"]
}

# Dictionary of main warehouses for each major region
main_warehouses = {
    "Miền Bắc": "Hà Nội",      # Main warehouse in Hanoi
    "Miền Trung": "Đà Nẵng",   # Main warehouse in Đà Nẵng
    "Miền Nam": "TP Hồ Chí Minh"  # Main warehouse in TP Hồ Chí Minh
}

# Dictionary of warehouses for each major region
region_warehouses = {
    "Đông Bắc Bộ": "Quảng Ninh",
    "Tây Bắc Bộ": "Sơn La",
    "Đồng bằng sông Hồng": "Hà Nội",
    "Bắc Trung Bộ": "Nghệ An",
    "Duyên hải Nam Trung Bộ": "Đà Nẵng",
    "Tây Nguyên": "Đắk Lắk",
    "Đông Nam Bộ": "TP Hồ Chí Minh",
    "Đồng bằng sông Cửu Long": "Cần Thơ"
}

def get_region(province: str) -> Optional[str]:
    """Kiểm tra tỉnh thuộc vùng nào trong 8 tiểu vùng"""
    for region, provinces in logistics_regions.items():
        if province in provinces:
            return region
    return None

def get_main_region(province: str) -> Optional[str]:
    """Kiểm tra tỉnh thuộc miền lớn nào"""
    region = get_region(province)
    if region in ["Đông Bắc Bộ", "Tây Bắc Bộ", "Đồng bằng sông Hồng"]:
        return "Miền Bắc"
    elif region in ["Bắc Trung Bộ", "Duyên hải Nam Trung Bộ", "Tây Nguyên"]:
        return "Miền Trung"
    elif region in ["Đông Nam Bộ", "Đồng bằng sông Cửu Long"]:
        return "Miền Nam"
    return None

def get_warehouse(province: str) -> tuple[Optional[str], Optional[str]]:
    """Trả về kho của tiểu vùng và miền lớn"""
    region = get_region(province)
    main_region = get_main_region(province)
    if region and main_region:
        return region_warehouses.get(region), main_warehouses.get(main_region)
    return None, None

if __name__ == "__main__":
    province = "Cà Mau"
    region_warehouse, main_warehouse = get_warehouse(province)
    print(f"Kho tiểu vùng của {province}: {region_warehouse}")  # Hà Nội
    print(f"Kho miền lớn của {province}: {main_warehouse}")     # Hà Nội
    #print coordinates of province
    print(coordinates[province])