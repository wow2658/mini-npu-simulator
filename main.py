# main.py
import json
import time

# ==========================================
# 1. MAC 연산 엔진 및 판독기
# ==========================================
def calculate_mac(filter_matrix, pattern_matrix):
    """
    두 2차원 배열(필터와 패턴)을 받아 MAC 연산 수행.
    """
    total_score = 0.0
    size = len(filter_matrix)
    
    # [핵심] 왜 [j][i]가 아니라 [i][j]인가?
    # 파이썬 리스트와 컴퓨터 메모리는 가로줄(행, Row) 방향으로 데이터가 연속 저장됨.
    # [i][j] 순서로 읽어야 메모리를 순서대로 빠르게 훑고 지나감 (캐시 지역성 최적화).
    for i in range(size):
        for j in range(size):
            total_score += filter_matrix[i][j] * pattern_matrix[i][j]
            
    return total_score

def compare_scores(score_cross, score_x, epsilon=1e-9):
    """
    부동소수점 오차 방어 및 판별기 (평가기준 2, 16 충족)
    """
    if abs(score_cross - score_x) < epsilon:
        return "UNDECIDED"
    return "Cross" if score_cross > score_x else "X"

# ==========================================
# 2. 데이터 전처리 파서
# ==========================================
def normalize_label(raw_label):
    """
    제멋대로인 라벨을 'Cross' 또는 'X'로 강제 통일 (평가기준 5 충족)
    """
    label = str(raw_label).strip().lower()
    if label in ['+', 'cross']:
        return "Cross"
    elif label in ['x', 'x']:
        return "X"
    return "UNDECIDED"

def extract_size_from_key(key):
    """
    'size_13_2' 같은 키에서 필터 이름인 'size_13'만 가위로 싹둑 잘라냄.
    """
    try:
        parts = key.split('_')
        if len(parts) >= 2:
            return f"{parts[0]}_{parts[1]}"
    except Exception:
        return None
    return None

# ==========================================
# 3. 입력 검증 유틸리티 (새로 추가됨)
# ==========================================
def get_3x3_input(prompt_text):
    """
    [핵심] 무한 재입력 방어막 (평가기준 3 충족)
    사용자가 숫자를 덜 쓰거나 글자를 쓰면 뻗지 않고 다시 입력하게 만듦.
    """
    while True:
        print(f"\n{prompt_text}")
        matrix = []
        try:
            for _ in range(3):
                row_input = input()
                
                # [핵심] split() 괄호를 비워두는 이유
                # 스페이스바 1칸이든 탭이든 '모든 공백'을 기준으로 아주 똑똑하게 쪼개줌.
                row = [float(x) for x in row_input.split()]
                
                if len(row) != 3:
                    raise ValueError("3칸이 아님")
                matrix.append(row)
            return matrix
        except ValueError:
            print("❌ 입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요. (재입력)")
        except EOFError:
            # Ctrl+D 방어: 입력 스트림이 끊기면 None 반환 → 호출부에서 처리
            print("\n⚠️ 입력이 중단되었습니다.")
            return None

# ==========================================
# 4. 실행 모드 로직
# ==========================================
def run_user_mode():
    """모드 1: 사용자 직접 입력 (평가기준 1 충족)"""
    print("\n#----------------------------------------")
    print("# [1] 필터 입력")
    print("#----------------------------------------")
    filter_cross = get_3x3_input("Cross 필터 (3줄 입력, 공백 구분)")
    if filter_cross is None:
        return
    filter_x = get_3x3_input("X 필터 (3줄 입력, 공백 구분)")
    if filter_x is None:
        return
    
    print("\n#----------------------------------------")
    print("# [2] 패턴 입력")
    print("#----------------------------------------")
    pattern = get_3x3_input("패턴 (3줄 입력, 공백 구분)")
    if pattern is None:
        return
    
    print("\n#----------------------------------------")
    print("# [3] MAC 결과")
    print("#----------------------------------------")
    
    start_time = time.perf_counter()
    for _ in range(10): # 10회 반복 측정
        score_cross = calculate_mac(filter_cross, pattern)
        score_x = calculate_mac(filter_x, pattern)
    end_time = time.perf_counter()
    
    avg_time_ms = ((end_time - start_time) / 10) * 1000
    result = compare_scores(score_cross, score_x)
    
    print(f"Cross 점수: {score_cross}")
    print(f"X 점수: {score_x}")
    print(f"연산 시간(평균/10회): {avg_time_ms:.5f} ms")
    if result == "UNDECIDED":
        print("판정: 판정 불가 (|Cross-X| < 1e-9)")
    else:
        print(f"판정: {result}")

def run_json_mode():
    """모드 2: JSON 파일 공장 가동 (평가기준 4, 6, 8 충족)"""
    print("\n#---------------------------------------")
    print("# [1] 필터 로드")
    print("#---------------------------------------")
    
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"파일 로드 실패: {e}")
        return

    # JSON의 'filters' 덩어리에서 필터 데이터 가져오기
    filters = data.get('filters', {})
    for size_key in filters.keys():
        print(f"✓ {size_key} 필터 로드 완료 (Cross, X)")

    print("\n#---------------------------------------")
    print("# [2] 패턴 분석 (라벨 정규화 적용)")
    print("#---------------------------------------")
    
    total_tests = 0
    passed_tests = 0
    failed_cases = []

    # [핵심] 딕셔너리 순회와 items() 함수
    # data['patterns']라는 커다란 딕셔너리(봉투 묶음)에서 이름표(Key)와 내용물(Value)을 한 쌍씩 뽑아냄
    patterns = data.get('patterns', {})
    for p_key, p_info in patterns.items():
        total_tests += 1
        print(f"\n--- {p_key} ---")
        
        # 1. 파서 작동 (이름표 정제 및 정답 표준화)
        size_key = extract_size_from_key(p_key)
        expected = normalize_label(p_info['expected'])
        target_pattern = p_info['input']
        
        # [방어막] 필터나 크기가 안 맞으면 프로그램 뻗지 않고 해당 테스트만 FAIL 처리
        if size_key not in filters:
            print("FAIL (원인: 해당 크기의 필터가 존재하지 않음)")
            failed_cases.append((p_key, "필터 누락"))
            continue
            
        # 2. 선생님 정답지(필터) 꺼내기
        filter_cross = filters[size_key]['Cross']
        filter_x = filters[size_key]['X']
        
        if len(target_pattern) != len(filter_cross):
            print("FAIL (원인: 필터와 패턴의 크기 불일치)")
            failed_cases.append((p_key, "크기 불일치"))
            continue

        # 3. 엔진 가동 및 점수 비교
        score_cross = calculate_mac(filter_cross, target_pattern)
        score_x = calculate_mac(filter_x, target_pattern)
        result = compare_scores(score_cross, score_x)
        
        # 4. 결과 집계 (PASS / FAIL 판독)
        status = "PASS" if result == expected else "FAIL"
        if status == "PASS":
            passed_tests += 1
        else:
            reason = "동점(UNDECIDED) 처리 규칙" if result == "UNDECIDED" else "점수 낮음"
            failed_cases.append((p_key, f"{reason} - Expected: {expected}, AI: {result}"))
            
        print(f"Cross 점수: {score_cross}")
        print(f"X 점수: {score_x}")
        print(f"판정: {result} | expected: {expected} | {status}")

    # 5. 최종 리포트 출력 (평가기준 8)
    print("\n#---------------------------------------")
    print("# [3] 결과 요약")
    print("#---------------------------------------")
    print(f"총 테스트: {total_tests}개")
    print(f"통과: {passed_tests}개")
    print(f"실패: {len(failed_cases)}개")
    
    if failed_cases:
        print("\n실패 케이스:")
        for case, reason in failed_cases:
            print(f"- {case}: {reason}")
    else:
        print("\n실패 케이스: 없음 (All Pass!)")

def run_performance_mode():
    """모드 3: 성능 분석 스톱워치 (평가기준 7 충족)"""
    print("\n#---------------------------------------")
    print("# 성능 분석 (O(N^2) 검증)")
    print("#---------------------------------------")
    
    # [핵심] f-string 정렬 (<10 : 왼쪽으로 착 붙이고 10칸 확보)
    print(f"{'크기':<10} {'평균 시간(ms)':<15} {'연산 횟수(N²)'}")
    print("-" * 40)
    
    test_sizes = [3, 5, 13, 25, 51, 101]
    
    for size in test_sizes:
        # [핵심] 리스트 내포와 리스트 곱셈의 원리
        # 1. [1.0] * size : 숫자 곱하기 아님! [1.0]을 size 번 '복붙'해서 가로 한 줄 만듦.
        # 2. for _ in range(size) : 숫자 무시하고 size 번 반복해서 가로줄을 밑으로 계속 찍어냄.
        dummy_matrix = [[1.0] * size for _ in range(size)]
        
        start_time = time.perf_counter()
        for _ in range(10):
            calculate_mac(dummy_matrix, dummy_matrix)
        end_time = time.perf_counter()
        
        avg_time_ms = ((end_time - start_time) / 10) * 1000
        ops_count = size * size # N^2 연산 횟수 계산
        
        print(f"{size}x{size:<7} {avg_time_ms:<15.5f} {ops_count}")

def main():
    while True:
        try:
            print("\n=== Mini NPU Simulator ===")
            print("[모드 선택]")
            print("1. 사용자 입력 (3x3)")
            print("2. data.json 분석")
            print("3. 성능 분석 표 출력")
            print("4. 종료")
            
            choice = input("선택: ")
            
            if choice == '1':
                run_user_mode()
            elif choice == '2':
                run_json_mode()
            elif choice == '3':
                run_performance_mode()
            elif choice == '4':
                break
            else:
                print("잘못된 입력입니다.")
        except KeyboardInterrupt:
            # Ctrl+C 방어: 메뉴로 복귀
            print("\n⚠️ 작업이 취소되었습니다. 메뉴로 돌아갑니다.")
        except EOFError:
            # Ctrl+D 방어: 프로그램 종료
            print("\n프로그램을 종료합니다.")
            break

if __name__ == "__main__":
    main()