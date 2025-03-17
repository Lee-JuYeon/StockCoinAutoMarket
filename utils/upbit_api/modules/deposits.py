"""
업비트 API 입금 관련 모듈
- 입금 리스트 조회
- 개별 입금 조회
- 입금 주소 생성 요청
- 전체 입금 주소 조회
- 개별 입금 주소 조회
- 원화 입금하기
"""
import requests
import logging
import uuid
import jwt
import hashlib
from urllib.parse import urlencode, unquote

logger = logging.getLogger(__name__)

class DepositsModule:
    """
    업비트 API 입금 관련 기능 모듈 (싱글톤 패턴)
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super(DepositsModule, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, api=None):
        """
        입금 모듈 초기화
        
        Args:
            api (UpbitAPI): 상위 UpbitAPI 인스턴스
        """
        if self._initialized and api is None:
            return
            
        self.api = api
        self.server_url = api.server_url if api else "https://api.upbit.com"
        self._initialized = True
        logger.info("DepositsModule 초기화 완료")
    
    # 입금 리스트 조회
    def get_deposits(self, currency=None, state=None, limit=100, page=1, order_by='desc'):
        """
        입금 리스트 조회
        
        Args:
            currency (str, optional): 화폐를 기준으로 입금 내역 필터링
            state (str, optional): 입금 상태
            limit (int, optional): 한 번에 반환되는 항목 개수 (default: 100, max: 100)
            page (int, optional): 페이지 수 (default: 1)
            order_by (str, optional): 정렬 방식 (default: desc)
            
        Returns:
            list: 입금 리스트
        """
        try:
            # API 키 확인
            if not self.api or not self.api.access_key or not self.api.secret_key:
                return {"error": "API 키가 설정되지 않았습니다."}
                
            # 쿼리 파라미터 설정
            params = {
                'limit': limit,
                'page': page,
                'order_by': order_by
            }
            
            if currency:
                params['currency'] = currency
                
            if state:
                valid_states = [
                    'submitting', 'submitted', 'almost_accepted', 'rejected', 
                    'accepted', 'processing', 'done', 'canceled'
                ]
                if state not in valid_states:
                    return {"error": f"유효하지 않은 상태값입니다. 유효한 값: {', '.join(valid_states)}"}
                params['state'] = state
            
            # 쿼리 문자열 생성
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
            response = requests.get(f"{self.server_url}/v1/deposits", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"입금 리스트 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"입금 리스트 조회 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 개별 입금 조회
    def get_deposit(self, uuid_str):
        """
        개별 입금 조회
        
        Args:
            uuid_str (str): 입금 UUID
            
        Returns:
            dict: 입금 정보
        """
        try:
            # API 키 확인
            if not self.api or not self.api.access_key or not self.api.secret_key:
                return {"error": "API 키가 설정되지 않았습니다."}
                
            # 쿼리 파라미터 설정
            params = {
                'uuid': uuid_str
            }
            
            # 쿼리 문자열 생성
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
            response = requests.get(f"{self.server_url}/v1/deposit", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"개별 입금 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"개별 입금 조회 중 오류 발생: {e}")
            return {"error": str(e)}
        
    # 입금 주소 생성 요청
    def generate_coin_address(self, currency):
        """
        입금 주소 생성 요청
        
        Args:
            currency (str): 화폐 코드
            
        Returns:
            dict: 입금 주소 생성 요청 결과
        """
        try:
            # API 키 확인
            if not self.api or not self.api.access_key or not self.api.secret_key:
                return {"error": "API 키가 설정되지 않았습니다."}
                
            # 쿼리 파라미터 설정
            params = {
                'currency': currency
            }
            
            # 쿼리 문자열 생성
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
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.api.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 헤더 설정
            headers = {
                'Authorization': f'Bearer {jwt_token}',
                'Content-Type': 'application/json'
            }
            
            # API 요청
            response = requests.post(f"{self.server_url}/v1/deposits/generate_coin_address", json=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"입금 주소 생성 요청 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"입금 주소 생성 요청 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 전체 입금 주소 조회
    def get_coin_addresses(self):
        """
        전체 입금 주소 조회
        
        Returns:
            list: 전체 입금 주소 목록
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
            response = requests.get(f"{self.server_url}/v1/deposits/coin_addresses", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"전체 입금 주소 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"전체 입금 주소 조회 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 개별 입금 주소 조회
    def get_coin_address(self, currency, net_type=None):
        """
        개별 입금 주소 조회
        
        Args:
            currency (str): 화폐 코드
            net_type (str, optional): 네트워크 유형
            
        Returns:
            dict: A입금 주소 정보
        """
        try:
            # API 키 확인
            if not self.api or not self.api.access_key or not self.api.secret_key:
                return {"error": "API 키가 설정되지 않았습니다."}
                
            # 쿼리 파라미터 설정
            params = {
                'currency': currency
            }
            
            if net_type:
                params['net_type'] = net_type
            
            # 쿼리 문자열 생성
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
            response = requests.get(f"{self.server_url}/v1/deposits/coin_address", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"개별 입금 주소 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"개별 입금 주소 조회 중 오류 발생: {e}")
            return {"error": str(e)}
        
    # 원화 입금하기
    def deposit_krw(self, amount, two_factor_type=None):
        """
        원화 입금하기
        
        Args:
            amount (str): 입금 금액
            two_factor_type (str, optional): 2차 인증 수단 (예: 'naver')
            
        Returns:
            dict: 입금 신청 결과
        """
        try:
            # API 키 확인
            if not self.api or not self.api.access_key or not self.api.secret_key:
                return {"error": "API 키가 설정되지 않았습니다."}
                
            # 쿼리 파라미터 설정
            params = {
                'amount': str(amount)
            }
            
            if two_factor_type:
                params['two_factor_type'] = two_factor_type
            
            # 쿼리 문자열 생성
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
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.api.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 헤더 설정
            headers = {
                'Authorization': f'Bearer {jwt_token}',
                'Content-Type': 'application/json'
            }
            
            # API 요청
            response = requests.post(f"{self.server_url}/v1/deposits/krw", json=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"원화 입금 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"원화 입금 중 오류 발생: {e}")
            return {"error": str(e)}
        
    # 계정주 확인(트래블룰 검증)가능 거래소 리스트 조회
    def get_travel_rule_vasps(self):
        """
        계정주 확인(트래블룰 검증)가능 거래소 리스트 조회
        
        Returns:
            list: 트래블룰 검증 가능한 거래소 목록
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
            response = requests.get(f"{self.server_url}/v1/travel_rule/vasps", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"계정주 확인 가능 거래소 리스트 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"계정주 확인 가능 거래소 리스트 조회 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 입금 UUID로 트래블룰 검증하기
    def verify_deposit_by_uuid(self, deposit_uuid, vasp_uuid):
        """
        입금 UUID로 트래블룰 검증하기
        
        Args:
            deposit_uuid (str): 입금 UUID
            vasp_uuid (str): 거래소 UUID
            
        Returns:
            dict: 트래블룰 검증 결과
        """
        try:
            # API 키 확인
            if not self.api or not self.api.access_key or not self.api.secret_key:
                return {"error": "API 키가 설정되지 않았습니다."}
                
            # 쿼리 파라미터 설정
            params = {
                'deposit_uuid': deposit_uuid,
                'vasp_uuid': vasp_uuid
            }
            
            # 쿼리 문자열 생성
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
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.api.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 헤더 설정
            headers = {
                'Authorization': f'Bearer {jwt_token}',
                'Content-Type': 'application/json'
            }
            
            # API 요청
            response = requests.post(f"{self.server_url}/v1/travel_rule/deposit/uuid", json=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"입금 UUID 트래블룰 검증 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"입금 UUID 트래블룰 검증 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 입금 TxID로 트래블룰 검증하기
    def verify_deposit_by_txid(self, vasp_uuid, txid, currency, net_type):
        """
        입금 TxID로 트래블룰 검증하기
        
        Args:
            vasp_uuid (str): 거래소 UUID
            txid (str): 트랜잭션 ID
            currency (str): 화폐 코드
            net_type (str): 네트워크 유형
            
        Returns:
            dict: 트래블룰 검증 결과
        """
        try:
            # API 키 확인
            if not self.api or not self.api.access_key or not self.api.secret_key:
                return {"error": "API 키가 설정되지 않았습니다."}
                
            # 쿼리 파라미터 설정
            params = {
                'vasp_uuid': vasp_uuid,
                'txid': txid,
                'currency': currency,
                'net_type': net_type
            }
            
            # 쿼리 문자열 생성
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
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.api.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 헤더 설정
            headers = {
                'Authorization': f'Bearer {jwt_token}',
                'Content-Type': 'application/json'
            }
            
            # API 요청
            response = requests.post(f"{self.server_url}/v1/travel_rule/deposit/txid", json=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"입금 TxID 트래블룰 검증 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"입금 TxID 트래블룰 검증 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 디지털 자산 입금 정보 조회
    def get_coin_deposit_chance(self, currency, net_type):
        """
        디지털 자산 입금 정보 조회
        
        Args:
            currency (str): 화폐 코드
            net_type (str): 네트워크 유형
            
        Returns:
            dict: 디지털 자산 입금 정보
        """
        try:
            # API 키 확인
            if not self.api or not self.api.access_key or not self.api.secret_key:
                return {"error": "API 키가 설정되지 않았습니다."}
                
            # 쿼리 파라미터 설정
            params = {
                'currency': currency,
                'net_type': net_type
            }
            
            # 쿼리 문자열 생성
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
            response = requests.get(f"{self.server_url}/v1/deposits/chance/coin", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"디지털 자산 입금 정보 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"디지털 자산 입금 정보 조회 중 오류 발생: {e}")
            return {"error": str(e)}