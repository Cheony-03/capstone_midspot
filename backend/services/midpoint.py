def calculate_midpoint(coords: list[tuple[float, float]]) -> dict[str, float]:
    """
    [기능] 참여자 좌표 [(위도, 경도), ...]의 산술평균(centroid) 중간지점을 계산함.

    :param coords: 참여자들의 (위도, 경도) 튜플 리스트
    :return: {"latitude": ..., "longitude": ...} 형태의 중간지점 dict
    :raises ValueError: 참여자가 2명 미만이거나 좌표가 위경도 범위를 벗어난 경우
    """
    if len(coords) < 2:
        raise ValueError("중간지점 계산을 위해서는 최소 2명 이상의 좌표가 필요합니다.")

    lat_sum = 0.0
    lng_sum = 0.0
    for lat, lng in coords:
        # 위경도 범위 검사
        if not (-90.0 <= lat <= 90.0):
            raise ValueError(f"잘못된 위도입니다: {lat}")
        if not (-180.0 <= lng <= 180.0):
            raise ValueError(f"잘못된 경도입니다: {lng}")
        lat_sum += lat
        lng_sum += lng

    return {
        "latitude": lat_sum / len(coords),
        "longitude": lng_sum / len(coords),
    }


# ---- 테스트 코드 (all_code 원본 복구) ----
if __name__ == "__main__":
    # 1) 정상: 3명의 좌표
    coords3 = [(37.4979, 127.0276), (37.5512, 126.9882), (37.4786, 127.0315)]
    print("=== 3명 중간지점 ===")
    print(calculate_midpoint(coords3))

    # 2) 정상: 2명의 좌표 (두 지점의 중간)
    coords2 = [(37.4979, 127.0276), (37.5512, 126.9882)]
    print("\n=== 2명 중간지점 ===")
    print(calculate_midpoint(coords2))

    # 3) 에러: 1명만 전달
    print("\n=== 1명 (에러 기대) ===")
    try:
        calculate_midpoint([(37.4979, 127.0276)])
    except ValueError as e:
        print("ValueError:", e)

    # 4) 에러: 좌표 범위 초과
    print("\n=== 범위 초과 (에러 기대) ===")
    try:
        calculate_midpoint([(37.4979, 127.0276), (95.0, 127.0)])
    except ValueError as e:
        print("ValueError:", e)
