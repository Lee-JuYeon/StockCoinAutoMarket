import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    # Flask 기본 설정
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///crypto_trading.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 업비트 API 설정 (기본값, 사용자별로 오버라이드 됨)
    UPBIT_ACCESS_KEY = os.getenv('UPBIT_ACCESS_KEY', '')
    UPBIT_SECRET_KEY = os.getenv('UPBIT_SECRET_KEY', '')
    
    # 뉴스 API 설정
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    
    # 추천 알고리즘 설정
    DEFAULT_STRATEGY = 'rsi_oversold'  # 기본 전략 (RSI 과매도)
    DEFAULT_RISK_LEVEL = 'medium'      # 기본 위험 수준
    
    # 자동 매매 설정
    DEFAULT_INVESTMENT_AMOUNT = 100000  # 기본 투자 금액 (10만원)
    
    # 로깅 설정
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')