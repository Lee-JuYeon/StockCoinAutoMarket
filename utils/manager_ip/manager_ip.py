import socket
import requests
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IpManager:
    @staticmethod
    def get_local_ip():  # self 매개변수 필요 없음
        try:
            # 외부 접속을 통해 사용 중인 IP 인터페이스 확인
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # 구글 DNS 서버에 연결
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception as e:
            logger.info(f"IpManager, get_local_ip // 오류 발생: {e}")
            return "IP 주소를 가져올 수 없습니다."
    
    @staticmethod
    def get_public_ip():  # self 매개변수 필요 없음
        try:
            response = requests.get('https://api.ipify.org').text
            return response
        except Exception as e:
            logger.info(f"IpManager, get_public_ip // 오류 발생: {e}")
            return "IP 주소를 가져올 수 없습니다."

# local_ip = IpManager.get_local_ip()
# public_ip = IpManager.get_public_ip()