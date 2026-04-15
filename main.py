# main.py
import json

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
        
    for pattern_key, pattern_info in data['patterns'].items():
        # 1. 파서 작동 (데이터 정제)
        filter_size_key = extract_size_from_key(pattern_key)
        clean_label = normalize_label(pattern_info['expected'])
        
        # 2. 데이터 추출
        filter_matrix = pattern_info['filter']
        pattern_a = pattern_info['pattern_a']
        pattern_b = pattern_info['pattern_b']
        
        # 3. 엔진 가동!
        score_a = calculate_mac(filter_matrix, pattern_a)
        score_b = calculate_mac(filter_matrix, pattern_b)
        
        # 4. 점수 비교
        result = compare_scores(score_a, score_b)
        
        # 5. 결과 출력
        print(f"검사: {filter_size_key} | 정답: {clean_label} | AI 판정: {result}")

def main():
    """
    프로그램 메인 진입점. 무한 루프를 돌며 메뉴를 출력함.
    """
    while True:
        print("\n=== Mini NPU Simulator ===")
        print("1. 사용자 입력 (3x3)")
        print("2. JSON 데이터 일괄 채점")
        print("3. 종료")
        
        choice = input("선택: ")
        
        if choice == '1':
            run_user_mode()
        elif choice == '2':
            run_json_mode()
        elif choice == '3':
            print("프로그램을 종료함.")
            break
        else:
            print("잘못된 입력임.")

if __name__ == "__main__":
    main()