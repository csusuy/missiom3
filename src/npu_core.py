def normalize_label(label):
    """
    다양한 형태의 입력 라벨('+', 'x', 'cross' 등)을 
    프로그램 표준 라벨인 'Cross' 또는 'X'로 변환(정규화)합니다.
    """
    if label is None:
        return "UNDECIDED"
    
    # 소문자로 바꾸고 양쪽 공백을 제거해서 비교합니다.
    clean_label = str(label).strip().lower()
    
    if clean_label in ["+", "cross"]:
        return "Cross"
    elif clean_label in ["x", "X"]:
        return "X"
    else:
        return str(label)


def mac_operation(pattern, filter_data):
    """
    NumPy 같은 외부 라이브러리 없이, 순수 파이썬 반복문(for문)으로 
    MAC(Multiply-Accumulate) 연산을 수행합니다.
    패턴과 필터의 같은 위치끼리 곱한 뒤 모두 더한 점수를 반환합니다.
    """
    rows = len(pattern)
    cols = len(pattern[0])
    score = 0.0

    # 2차원 배열을 순회하기 위한 이중 for문
    for r in range(rows):
        for c in range(cols):
            score += float(pattern[r][c]) * float(filter_data[r][c])
            
    return score


def determine_winner(score_a, score_b, label_a="Cross", label_b="X", epsilon=1e-9):
    """
    두 필터의 점수를 비교하여 판정 결과를 내립니다.
    컴퓨터의 부동소수점 오차를 고려하여 두 값의 차이가 허용오차(epsilon)보다 작으면
    동점(UNDECIDED)으로 처리합니다.
    """
    diff = abs(score_a - score_b)
    
    # 허용오차보다 차이가 작으면 동점 처리
    if diff < epsilon:
        return "UNDECIDED"
    elif score_a > score_b:
        return label_a
    else:
        return label_b

# 기존 2차원 MAC 연산 함수 아래에 추가
def mac_operation_1d(pattern, filter_data, N):
    """
    2차원 배열을 1차원으로 평탄화(Flatten)하여 MAC 연산을 수행하는 최적화 함수
    """
    # 2차원 리스트를 1차원 리스트로 변환 (Flatten)
    flat_pattern = [val for row in pattern for val in row]
    flat_filter = [val for row in filter_data for val in row]
    
    # 1차원 순회를 통한 MAC 연산 (오버헤드 감소)
    accumulated_sum = 0
    for i in range(N * N):
        accumulated_sum += flat_pattern[i] * flat_filter[i]
        
    return accumulated_sum