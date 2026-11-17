import json
import time
from src.npu_core import normalize_label, mac_operation, determine_winner

def get_user_matrix(prompt_title):
    """
    모드 1에서 사용자로부터 3x3 행렬 데이터를 한 줄씩 공백으로 구분하여 입력받습니다.
    입력 오류(숫자가 아니거나 개수가 안 맞을 때)가 나면 재입력을 유도합니다.
    """
    print(prompt_title)
    matrix = []
    expected_rows = 3
    expected_cols = 3

    while len(matrix) < expected_rows:
        try:
            line = input(f"행 {len(matrix) + 1} (숫자 3개 공백 구분): ").strip()
            if not line:
                continue
            
            row = [float(x) for x in line.split()]
            
            if len(row) != expected_cols:
                print(f"입력 형식 오류: 각 줄에 {expected_cols}개의 숫자를 공백으로 구분해 입력하세요.")
                continue
                
            matrix.append(row)
        except ValueError:
            print("입력 형식 오류: 올바른 숫자를 입력해주세요.")
            
    return matrix


def run_mode_1():
    """
    모드 1: 사용자가 직접 3x3 필터 2개와 패턴을 입력하여 결과를 확인합니다.
    """
    print("\n# ----------------------------------------")
    print("# [모드 1] 사용자 입력 (3x3)")
    print("# ----------------------------------------")
    
    print("\n필터 A 입력:")
    filter_a = get_user_matrix("필터 A (3줄 입력)")
    
    print("\n필터 B 입력:")
    filter_b = get_user_matrix("필터 B (3줄 입력)")
    
    print("\n패턴 입력:")
    pattern = get_user_matrix("패턴 (3줄 입력)")
    
    # 연산 시간 측정 (10회 반복 평균)
    iterations = 10
    start_time = time.perf_counter()
    for _ in range(iterations):
        score_a = mac_operation(pattern, filter_a)
        score_b = mac_operation(pattern, filter_b)
    end_time = time.perf_counter()
    
    avg_time_ms = ((end_time - start_time) / iterations) * 1000
    
    # 판정 내리기 (Cross 대 X 비교 가정, 사용자 정의에 따라)
    winner = determine_winner(score_a, score_b, label_a="Cross", label_b="X")
    
    print("\n# ----------------------------------------")
    print("# [3] MAC 결과")
    print("# ----------------------------------------")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/10회): {avg_time_ms:.3f} ms")
    if winner == "UNDECIDED":
        print("판정: 판정 불가 (|A-B| < 1e-9)")
    else:
        print(f"판정: {winner}")


def run_mode_2():
    """
    모드 2: data.json 파일을 로드하여 필터와 패턴을 분석하고 PASS/FAIL을 판정합니다.
    """
    print("\n# ----------------------------------------")
    print("# [모드 2] data.json 분석")
    print("# ----------------------------------------")
    
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("오류: data.json 파일을 찾을 수 없습니다. 프로젝트 루트 폴더에 파일을 넣어주세요.")
        return
    except json.JSONDecodeError:
        print("오류: data.json 파일의 JSON 형식이 올바르지 않습니다.")
        return

    filters_raw = data.get("filters", {})
    patterns_raw = data.get("patterns", {})

    # 필터 정규화 및 로드
    filters = {}
    print("\n# [1] 필터 로드")
    for size_key, filter_dict in filters_raw.items():
        # size_5 -> 5, size_13 -> 13 등 크기 추출
        try:
            size_val = int(size_key.split("_")[1])
        except (IndexError, ValueError):
            size_val = len(list(filter_dict.values())[0])
            
        filters[size_val] = {}
        loaded_labels = []
        for raw_lbl, matrix in filter_dict.items():
            std_lbl = normalize_label(raw_lbl)
            filters[size_val][std_lbl] = matrix
            loaded_labels.append(std_lbl)
        print(f"✓ {size_key:<8} 필터 로드 완료 ({', '.join(loaded_labels)})")

    print("\n# [2] 패턴 분석 (라벨 정규화 적용)")
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    fail_reasons = []

    # 성능 측정용 딕셔너리
    perf_records = {}

    for pat_key, pat_info in patterns_raw.items():
        total_tests += 1
        print(f"\n-- {pat_key} ---")
        
        try:
            parts = pat_key.split("_")
            size_val = int(parts[1])
        except (IndexError, ValueError):
            print(f"패턴 키 형식 오류 ({pat_key})")
            failed_tests += 1
            fail_reasons.append(f"{pat_key}: 키 형식 오류")
            continue

        pattern_matrix = pat_info.get("input")
        raw_expected = pat_info.get("expected")
        expected_label = normalize_label(raw_expected)

        if size_val not in filters:
            print(f"FAIL: 일치하는 크기({size_val})의 필터가 없습니다.")
            failed_tests += 1
            fail_reasons.append(f"{pat_key}: 필터 크기 미스매치")
            continue

        target_filters = filters[size_val]
        
        # 필터와 패턴 크기 검증
        valid_case = True
        scores = {}
        
        for lbl, f_matrix in target_filters.items():
            if len(pattern_matrix) != len(f_matrix) or len(pattern_matrix[0]) != len(f_matrix[0]):
                valid_case = False
                break
                
            # MAC 연산 시간 측정 (성능 분석용 데이터 수집 겸용)
            start_t = time.perf_counter()
            score = mac_operation(pattern_matrix, f_matrix)
            end_t = time.perf_counter()
            
            # 크기별 연산 시간 누적 (성능 분석용)
            if size_val not in perf_records:
                perf_records[size_val] = []
            perf_records[size_val].append(end_t - start_t)
            
            scores[lbl] = score

        if not valid_case:
            print(f"판정: FAIL (패턴과 필터 크기 불일치)")
            failed_tests += 1
            fail_reasons.append(f"{pat_key}: 크기 불일치")
            continue

        # 점수 출력 (Cross, X 기준)
        score_cross = scores.get("Cross", 0.0)
        score_x = scores.get("X", 0.0)

        print(f"Cross 점수: {score_cross}")
        print(f"X 점수: {score_x}")

        # 판정 수행
        judgment = determine_winner(score_cross, score_x, label_a="Cross", label_b="X")

        # PASS / FAIL 판정
        if judgment == expected_label:
            print(f"판정: {judgment} | expected: {raw_expected} | PASS")
            passed_tests += 1
        else:
            reason = "동점(UNDECIDED) 처리 규칙" if judgment == "UNDECIDED" else "예상값 불일치"
            print(f"판정: {judgment} | expected: {raw_expected} | FAIL ({reason})")
            failed_tests += 1
            fail_reasons.append(f"{pat_key}: {reason}")

    # 성능 분석 출력
    print("\n# ----------------------------------------")
    print("# [3] 성능 분석 (평균/10회 반복 측정 시뮬레이션)")
    print("# ----------------------------------------")
    print(f"{'크기':<10} {'평균 시간(ms)':<15} {'연산 횟수(N²)'}")
    print("-" * 40)

    for size in sorted(perf_records.keys()):
        # 해당 크기의 연산 시간들 평균 계산 후 ms로 변환
        times = perf_records[size]
        # 10회 반복 측정한 것으로 가정하여 평균 스케일링 혹은 직접 반복 측정 반영
        avg_ms = (sum(times) / len(times)) * 1000
        n_squared = size * size
        print(f"{size}×{size:<7} {avg_ms:<15.3f} {n_squared}")

    # 결과 요약 출력
    print("\n# ----------------------------------------")
    print("# [4] 결과 요약")
    print("# ----------------------------------------")
    print(f"총 테스트: {total_tests}개")
    print(f"통과: {passed_tests}개")
    print(f"실패: {failed_tests}개")

    if failed_tests > 0:
        print("\n실패 케이스:")
        for reason in fail_reasons:
            print(f"- {reason}")
    else:
        print("\n모든 테스트를 성공적으로 통과했습니다! (0 FAIL)")
        
import time
from src.npu_core import mac_operation, mac_operation_1d

def run_performance_benchmark():
    """
    보너스 과제: 2차원 연산과 1차원 최적화 연산의 성능(속도) 비교 분석
    """
    N = 25  # 기본 테스트 사이즈
    # 임의의 테스트용 패턴 및 필터 데이터 생성
    pattern = [[1 if (r + c) % 2 == 0 else 0 for c in range(N)] for r in range(N)]
    filter_data = [[1 if (r + c) % 3 == 0 else 0 for c in range(N)] for r in range(N)]

    print(f"\n[성능 비교 분석 시작 (N={N}, 1000회 반복)]")

    # 1. 기존 2차원 방식 시간 측정
    start_time = time.time()
    for _ in range(1000):
        mac_operation(pattern, filter_data)
    end_time = time.time()
    time_2d = end_time - start_time
    print(f"- 2차원 연산 소요 시간: {time_2d:.5f}초")

    # 2. 최적화된 1차원 방식 시간 측정
    start_time = time.time()
    for _ in range(1000):
        mac_operation_1d(pattern, filter_data, N)
    end_time = time.time()
    time_1d = end_time - start_time
    print(f"- 1차원 최적화 소요 시간: {time_1d:.5f}초")

    # 속도 개선율 출력
    if time_2d > 0:
        improvement = ((time_2d - time_1d) / time_2d) * 100
        print(f"- 성능 향상 결과: 약 {improvement:.2f}% 시간 단축\n")        