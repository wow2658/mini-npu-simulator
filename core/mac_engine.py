# core/mac_engine.py

def calculate_mac(filter_matrix, pattern_matrix):
    """
    두 2차원 배열(필터와 패턴)을 받아 MAC(Multiply-Accumulate) 연산 수행.
    - 입력: N x N 크기의 2차원 리스트 2개
    - 반환: 곱하고 더해진 최종 누적 점수 (float)
    """
    total_score = 0.0
    size = len(filter_matrix) # 2차원 배열의 세로줄 개수 (N)
    
    # i는 세로줄(행), j는 가로칸(열)을 순회하며 모든 칸 방문
    for i in range(size):
        for j in range(size):
            # 핵심 원리: 같은 위치[i][j]에 있는 두 숫자를 곱한 뒤 점수통에 누적
            total_score += filter_matrix[i][j] * pattern_matrix[i][j]
            
    return total_score

def compare_scores(score_a, score_b, epsilon=1e-9):
    """
    부동소수점 오차를 방어하며 두 점수를 비교하는 판별기.
    미세한 연산 오차 발생을 대비해 두 점수 차이가 epsilon보다 작으면 동점 처리함.
    """
    # 두 점수 차이를 절댓값(abs)으로 구해서, 허용 오차보다 작으면 동점 판정
    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"
    
    # 동점이 아니면 더 큰 점수를 받은 쪽 반환
    return "A" if score_a > score_b else "B"