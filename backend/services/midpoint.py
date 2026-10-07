from typing import Iterable


def calculate_midpoint(coords: Iterable[tuple[float, float]]) -> dict:
    """
    참여자 좌표 [(위도, 경도), ...]의 산술평균(centroid)을 반환한다.
    """
    # 입력을 리스트로 변환 (len() 사용, 여러 번 순회하기 위해)
    coords = list(coords)

    # 1명 이하면 '중간'이 없으므로 에러 발생
    if len(coords) < 2:
        raise ValueError("중간지점 계산에는 최소 2명의 좌표가 필요합니다.")

    # 참여자 한 명씩 꺼내서 좌표 범위 검사
    for lat, lng in coords:
        # 위도는 -90 ~ 90 사이여야 함
        if not (-90 <= lat <= 90):
            raise ValueError(f"위도 범위 오류: {lat}")
        # 경도는 -180 ~ 180 사이여야 함
        if not (-180 <= lng <= 180):
            raise ValueError(f"경도 범위 오류: {lng}")

    # 참여자 수
    n = len(coords)

    # 위도끼리 모두 더한 뒤 인원수로 나눔 (위도 평균)
    mid_lat = sum(lat for lat, _ in coords) / n
    # 경도끼리 모두 더한 뒤 인원수로 나눔 (경도 평균)
    mid_lng = sum(lng for _, lng in coords) / n

    # 중간 좌표를 딕셔너리로 반환 (나중에 카카오 API에 전달)
    return {"latitude": mid_lat, "longitude": mid_lng}


# 이 파일을 직접 실행할 때만 아래 테스트 코드가 동작
if __name__ == "__main__":
    # 테스트 1: 공주 / 대전 / 천안 3명 좌표 (위도, 경도)
    three = [(36.4465, 127.1190), (36.3504, 127.3845), (36.8151, 127.1139)]
    print("3명:", calculate_midpoint(three))

    # 테스트 2: 2명 좌표
    two = [(36.4465, 127.1190), (36.3504, 127.3845)]
    print("2명:", calculate_midpoint(two))

    # 테스트 3: 1명만 넣어서 에러가 나는지 확인
    try:
        calculate_midpoint([(36.4, 127.1)])
    except ValueError as e:
        print("에러 테스트:", e)