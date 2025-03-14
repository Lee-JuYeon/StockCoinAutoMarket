"""
업비트 API 모듈 패키지
"""
from .upbit_api import UpbitAPI

# 싱글톤 인스턴스 가져오기
def get_upbit_api_instance():
    return UpbitAPI()