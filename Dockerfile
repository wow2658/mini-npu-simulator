# 1. 베이스 이미지: 2026년 기준 빠르고 가벼운 3.12 slim 버전 사용 (3.8 이상 제약조건 충족)
FROM python:3.12-slim

# 2. 환경 변수 설정
# 파이썬 출력이 버퍼링 없이 즉시 콘솔에 찍히도록 설정 (인터랙티브 모드 필수)
ENV PYTHONUNBUFFERED=1
# 기본 인코딩을 UTF-8로 강제하여 윈도우/맥/리눅스 환경 차이로 인한 에러 원천 차단
ENV PYTHONIOENCODING=UTF-8

# 3. 작업 디렉토리 설정
WORKDIR /app

# 4. 소스 코드 복사
# 현재 폴더의 모든 파일을 컨테이너 내부의 /app 폴더로 복사
COPY . /app/

# 5. 실행 명령
# 컨테이너가 켜지면 무조건 main.py를 실행하도록 지정
CMD ["python", "main.py"]