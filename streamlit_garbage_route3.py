import streamlit as st
import streamlit.components.v1 as components
import googlemaps
import numpy as np
from ant_colony import AntColony

API_KEY = 'AIzaSyBnEczbljpLOsESpId-YPwFWQNc4YuYLEk'
gmaps = googlemaps.Client(key=API_KEY)

def get_distance_matrix(locations):
    n = len(locations)
    matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = np.inf
            else:
                result = gmaps.distance_matrix(origins=locations[i], destinations=locations[j], mode="driving")
                matrix[i][j] = result['rows'][0]['elements'][0]['distance']['value']
    return matrix

def extract_district(address):
    # Ví dụ: '123 Lê Lợi, Quận 1, TP.HCM' → 'Quận 1'
    for part in address.split(','):
        if 'Quận' in part or 'quận' in part:
            return part.strip()
    return 'Không xác định'

def main():
    st.title("🚛 Tối ưu lộ trình theo Quận (ACO + Google Maps)")

    raw_input = st.text_area("Nhập danh sách địa điểm (mỗi dòng một địa chỉ):", height=200)

    locations = [line.strip() for line in raw_input.strip().split('\n') if line.strip()]
    
    # Thêm checkbox cho phép chọn phân loại theo quận
    sort_by_district = st.checkbox("Có phân loại theo quận không?")
    
    
    if sort_by_district:
        # Tự động lấy danh sách quận
        districts = sorted(set([extract_district(loc) for loc in locations if extract_district(loc) != 'Không xác định']))
        selected_district = st.selectbox("Chọn quận cần tính lộ trình:", districts)

        # Lọc các địa điểm theo quận được chọn
        filtered_locations = [loc for loc in locations if extract_district(loc) == selected_district]
    else:
        # Nếu không phân loại theo quận, giữ nguyên tất cả địa điểm
        filtered_locations = locations

        filtered_locations = [line.strip() for line in raw_input.strip().split('\n') if line.strip()]
        if len(filtered_locations) < 2:
            st.error("Cần ít nhất 2 địa điểm!")
            return
    print(filtered_locations)
    if st.button("Tính lộ trình tối ưu"):
        if len(locations) < 2:
            st.error("Cần ít nhất 2 địa điểm!")
            return

        with st.spinner('Đang tính toán...'):
            try:
                matrix = get_distance_matrix(filtered_locations)
                colony = AntColony(matrix, n_ants=10, n_best=3, n_iterations=20, decay=0.9)
                best_path = colony.run()[0]

                result = [filtered_locations[int(i)] for i, _ in best_path] + [filtered_locations[int(best_path[-1][1])]]
                st.success("Lộ trình tối ưu:")
                st.write(" → ".join(result))

                # Tạo Google Maps Embed URL
                origin = result[0].replace(' ', '+')
                destination = result[-1].replace(' ', '+')
                waypoints = '|'.join([loc.replace(' ', '+') for loc in result[1:-1]])
                embed_url = f"https://www.google.com/maps/embed/v1/directions?key={API_KEY}&origin={origin}&destination={destination}&waypoints={waypoints}"

                components.iframe(embed_url, height=500)

            except Exception as e:
                st.error(f"Lỗi: {e}")

if __name__ == "__main__":
    main()
