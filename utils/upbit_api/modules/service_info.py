"""
업비트 API 서비스 정보 관련 모듈
- 마켓 코드 조회
- 입출금 현황 조회
- API 키 리스트 조회
"""
import requests
import logging
import uuid
import jwt
import hashlib
from urllib.parse import urlencode, unquote

logger = logging.getLogger(__name__)

class ServiceInfoModule:
    """
    업비트 API 서비스 정보 관련 기능 모듈 (싱글톤 패턴)
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super(ServiceInfoModule, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, api=None):
        """
        서비스 정보 모듈 초기화
        
        Args:
            api (UpbitAPI): 상위 UpbitAPI 인스턴스
        """
        if self._initialized and api is None:
            return
            
        self.api = api
        self.server_url = api.server_url if api else "https://api.upbit.com"
        self._initialized = True
        logger.info("ServiceInfoModule 초기화 완료")
    
    def get_market_all(self, is_details=False):
        """
        마켓 코드 조회
        
        Args:
            is_details (bool, optional): 유의 종목 필드와 같은 상세 정보 포함 여부
            
        Returns:
            list: 마켓 코드 목록
        """
        try:
            # 쿼리 파라미터 설정
            params = {}
            
            if is_details:
                params['isDetails'] = 'true'
            
            # API 요청 (인증 필요 없음)
            response = requests.get(f"{self.server_url}/v1/market/all", params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"마켓 코드 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"마켓 코드 조회 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 입출금 현황 조회
    def get_wallet_status(self, currency=None):
        """
        입출금 현황 조회
        
        Args:
            currency (str, optional): 화폐 코드
            
        Returns:
            list: 입출금 현황 목록
        """
        try:
            # API 키 확인
            if not self.api or not self.api.access_key or not self.api.secret_key:
                return {"error": "API 키가 설정되지 않았습니다."}
                
            # 쿼리 파라미터 설정
            params = {}
            
            if currency:
                params['currency'] = currency
                
                # 쿼리 문자열 생성 (쿼리 파라미터가 있는 경우)
                query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
                
                # 해시 생성
                m = hashlib.sha512()
                m.update(query_string)
                query_hash = m.hexdigest()
                
                # JWT 페이로드 생성
                payload = {
                    'access_key': self.api.access_key,
                    'nonce': str(uuid.uuid4()),
                    'query_hash': query_hash,
                    'query_hash_alg': 'SHA512',
                }
            else:
                # JWT 페이로드 생성 (쿼리 파라미터가 없는 경우)
                payload = {
                    'access_key': self.api.access_key,
                    'nonce': str(uuid.uuid4()),
                }
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.api.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 헤더 설정
            headers = {
                'Authorization': f'Bearer {jwt_token}',
            }
            
            # API 요청
            response = requests.get(f"{self.server_url}/v1/status/wallet", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"입출금 현황 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"입출금 현황 조회 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # API 키 리스트 조회
    def get_api_keys(self):
        """
        API 키 리스트 조회
        
        Returns:
            list: API 키 목록
        """
        try:
            # API 키 확인
            if not self.api or not self.api.access_key or not self.api.secret_key:
                return {"error": "API 키가 설정되지 않았습니다."}
                
            # JWT 페이로드 생성 (쿼리 파라미터 없음)
            payload = {
                'access_key': self.api.access_key,
                'nonce': str(uuid.uuid4()),
            }
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.api.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 헤더 설정
            headers = {
                'Authorization': f'Bearer {jwt_token}',
            }
            
            # API 요청
            response = requests.get(f"{self.server_url}/v1/api_keys", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API 키 리스트 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"API 키 리스트 조회 중 오류 발생: {e}")
            return {"error": str(e)}