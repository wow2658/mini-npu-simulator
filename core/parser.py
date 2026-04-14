# core/parser.py

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
        # 방어 코드: 언더바로 쪼갰을 때 조각이 2개 이상일 때만 조립함
        if len(parts) >= 2:
            return f"{parts[0]}_{parts[1]}"
    except Exception:
        return None
        
    return None