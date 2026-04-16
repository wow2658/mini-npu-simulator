# main.py
import json
import time

# ==========================================
# 1. MAC 연산 엔진 및 판독기 (구 mac_engine.py)
# ==========================================
def calculate_mac(filter_matrix, pattern_matrix):
    """
    두 2차원 배열(필터와 패턴)을 받아 MAC(Multiply-Accumulate) 연산 수행.
    - 입력: N x N 크기의 2차원 리스트 2개
    - 반환: 곱하고 더해진 최종 누적 점수 (float)
    """
    total_score = 0.0
    size = len(filter_matrix)
    
    # 캐시 지역성(Cache Locality)을 고려한 행 우선(Row-major) 탐색 [i][j]
    for i in range(size):
        for j in range(size):
            total_score += filter_matrix[i][j] * pattern_matrix[i][j]
            
    return total_score

def compare_scores(score_a, score_b, epsilon=1e-9):
    """
    부동소수점 오차를 방어하며 두 점수를 비교하는 판별기.
    미세한 연산 오차 발생을 대비해 두 점수 차이가 epsilon보다 작으면 동점 처리함.
    """
    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"
    
    return "A" if score_a > score_b else "B"

# ==========================================
# 2. 데이터 전처리 파서 (구 parser.py)
# ==========================================
def normalize_label(raw_label):
    """
    '+', 'cross', 'x' 등 다양한 형태의 입력 라벨을 'Cross' 또는 'X' 표준 라벨로 통일함.
    """
    label = str(raw_label).strip().lower()
    
    if label == '+' or label == 'cross':
        return "Cross"
    elif label == 'x':
        return "X"
    else:
        return "UNDECIDED"

def extract_size_from_key(key):
    """
    'size_13_2' 같은 키에서 'size_13'을 추출해 반환함.
    """
    try:
        parts = key.split('_')
        if len(parts) >= 2:
            return f"{parts[0]}_{parts[1]}"
    except Exception:
        return None
        
    return None

# ==========================================
# 3. 메인 실행 로직
# ==========================================
def run_user_mode():
    """
    [모드 1] 사용자 입력 모드.
    터미널에서 3x3 패턴을 입력받아 MAC 연산을 수행함.
    """
    print("\n[모드 1] 사용자 입력 (3x3)")
    print("0과 1로 이루어진 3x3 패턴을 한 줄씩 입력하세요. (예: 0 1 0)")
    
    user_pattern = []
    
    for i in range(3):
        row_input = input(f"{i+1}번째 줄 입력: ")
        row_numbers = [int(x) for x in row_input.split()]
        user_pattern.append(row_numbers)
        
    # 엔진 테스트를 위한 임시 정답지 (십자가 모양 필터)
    dummy_filter = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0]
    ]
    
    # 엔진 가동!
    result_score = calculate_mac(dummy_filter, user_pattern)
    
    print("\n[입력된 패턴]")
    for row in user_pattern:
        print(row)
    print(f"👉 MAC 연산 결과 점수: {result_score}")

def run_json_mode():
    """
    [모드 2] JSON 파일 일괄 로드 및 채점.
    """
    print("\n[모드 2] data.json 공장 가동")
    
    with open('data.json', 'r') as f:
        data = json.load(f)
        
    # [핵심] 딕셔너리 순회와 items() 함수
    # data['patterns']라는 커다란 딕셔너리(봉투 묶음)에서 
    # 이름표(Key)와 실제 내용물(Value)을 한 쌍씩 뽑아냄
    for pattern_key, pattern_info in data['patterns'].items():
        
        # 1. 파서 작동 
        filter_size_key = extract_size_from_key(pattern_key)
        clean_label = normalize_label(pattern_info['expected'])
        
        # 2. 데이터 추출 (내용물 딕셔너리에서 실제 2차원 리스트 꺼내기)
        # pattern_info 역시 딕셔너리 덩어리이므로, [키값] 문법으로 데이터를 빼옴
        filter_matrix = pattern_info['filter']
        pattern_a = pattern_info['pattern_a']
        pattern_b = pattern_info['pattern_b']
        
        # 3. 엔진 가동! 
        score_a = calculate_mac(filter_matrix, pattern_a)
        score_b = calculate_mac(filter_matrix, pattern_b)
        
        # 4. 점수 비교 (누가 더 점수가 높은지 판독)
        result = compare_scores(score_a, score_b)
        
        # 5. 결과 출력
        print(f"검사: {filter_size_key} | 정답: {clean_label} | AI 판정: {result}")


def run_performance_mode():
    """
    [모드 3] 성능 분석 모드.
    다양한 크기(N x N)의 행렬을 생성하여 MAC 연산 시간을 측정함.
    """
    print("\n[모드 3] NPU 엔진 성능 분석 (O(N^2) 검증)")
    
    test_sizes = [3, 5, 11, 21, 31, 51, 101]
    
    for size in test_sizes:
        # [핵심] 리스트 내포(List Comprehension)와 리스트 곱셈의 원리
        # 1. [1.0] * size : 숫자 곱하기가 아님! [1.0] 이라는 방을 size 개수만큼 '복사 붙여넣기' 해서 가로 한 줄을 만듦.
        # 2. for _ in range(size) : 0, 1, 2... 숫자는 안 쓸 거니까 _(언더스코어)로 치우고, 그저 size 번만큼 "반복"하라는 뜻.
        # 3. 종합 : 가로 한 줄을 만든 걸, 밑으로 size 번만큼 똑같이 찍어내서 N x N 2차원 행렬을 만들어냄.
        dummy_matrix = [[1.0] * size for _ in range(size)]
        
        # 시작 시간 기록: 일반 time.time()보다 훨씬 정밀한 시스템 타이머 사용
        start_time = time.perf_counter()
        
        # 오차(노이즈)를 줄이기 위해 10번 연속으로 엔진 가동
        for _ in range(10):
            calculate_mac(dummy_matrix, dummy_matrix)
            
        # 종료 시간 기록
        end_time = time.perf_counter()
        
        # 10회 총 경과 시간을 10으로 나누어 1회 평균 시간을 밀리초(ms)로 환산
        avg_time_ms = ((end_time - start_time) / 10) * 1000
        
        # [핵심] f-string 정렬 및 포맷 지정자
        # {size:3d}  : 정수(d)를 3칸 확보해서 출력 (기본 오른쪽 정렬. 예: "  3")
        # {size:<3d} : 정수(d)를 3칸 확보하되 왼쪽(<)으로 착 붙여서 정렬 (예: "3  ")
        # {avg_time_ms:.5f} : 실수(f)를 소수점 아래 5자리까지만 남기고 자르기
        print(f"크기 {size:3d}x{size:<3d} | 평균 연산 시간: {avg_time_ms:.5f} ms")

def main():
    """
    프로그램 메인 진입점. 무한 루프를 돌며 메뉴를 출력함.
    """
    while True:
        print("\n=== Mini NPU Simulator ===")
        print("1. 사용자 입력 (3x3)")
        print("2. JSON 데이터 일괄 채점")
        print("3. 성능 분석 (O(N^2) 검증)")  # 💡 메뉴 이름 변경
        print("4. 종료")                    # 💡 4번으로 밀림
        
        choice = input("선택: ")
        
        if choice == '1':
            run_user_mode()
        elif choice == '2':
            run_json_mode()
        elif choice == '3':
            run_performance_mode()      # 💡 3번 누르면 스톱워치 모드 실행!
        elif choice == '4':
            print("프로그램을 종료함.")
            break
        else:
            print("잘못된 입력임.")

if __name__ == "__main__":
    main()