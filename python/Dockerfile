# 1. Base Image 설정
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 파일 복사 및 설치 (현재는 표준 라이브러리 위주라 필수 아님)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 모든 소스 코드 복사
COPY . .

# 5. 실행할 파일을 빌드 인자 또는 환경 변수로 받음 (기본값 app_basic.py)
ARG APP_FILE=app_basic.py
ENV APP_NAME=${APP_FILE}

# 6. 스크립트 실행
CMD ["sh", "-c", "python ${APP_NAME}"]