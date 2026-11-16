from typing import Iterable


def calculate_midpoint(coords: Iterable[tuple[float, float]]) -> dict:
    """
    참여자 좌표 [(위도, 경도), ...]의 산술평균(centroid)을 반환한다.
    """
    coords = list(coords)

    if len(coords) < 2:
        raise ValueError("중간지점 계산에는 최소 2명의 좌표가 필요합니다.")

    for lat, lng in coords:
        if not (-90 <= lat <= 90):
            raise ValueError(f"위도 범위 오류: {lat}")
        if not (-180 <= lng <= 180):
            raise ValueError(f"경도 범위 오류: {lng}")

    n = len(coords)
    mid_lat = sum(lat for lat, _ in coords) / n
    mid_lng = sum(lng for _, lng in coords) / n

    return {"latitude": mid_lat, "longitude": mid_lng}


if __name__ == "__main__":
    three = [(36.4465, 127.1190), (36.3504, 127.3845), (36.8151, 127.1139)]
    print("3명:", calculate_midpoint(three))

    two = [(36.4465, 127.1190), (36.3504, 127.3845)]
    print("2명:", calculate_midpoint(two))

    try:
        calculate_midpoint([(36.4, 127.1)])
    except ValueError as e:
        print("에러 테스트:", e)