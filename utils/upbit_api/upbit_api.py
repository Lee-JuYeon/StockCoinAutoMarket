import requests
import uuid
import jwt 
import hashlib
import time
import logging
from urllib.parse import urlencode, unquote
from utils.manager_encryption.manager_encryption import EncryptionManager
    # 자산/전체 계좌 조회 (https://api.upbit.com/v1/accounts~ )

    # 주문/주문 가능 정보 (https://api.upbit.com/v1/orders~)
    # 주문/개별 주문 조회
    # 주문/주문 리스트 조회
    # 주문/ID로 주문리스트 조회
    # 주문/체결 대기 주문 조회 (open order)
    # 주문/종료된 주문 조회 (closed order)
    # 주문/주문 취소 접수
    # 주문/주문 일괄 취소 접수
    # 주문/id로 주문리스트 취소 접수
    # 주문/주문하기
                                                
    # 입금/개별 입금 조회
    # 입금/입금 주소 생성 요청
    # 입금/전체 입금 주소 조회
    # 입금/개별 입금 주소 조회
    # 입금/원화 입금하기
    # 입금/해외 거래소 입금 시 계정주 확인하기 (트래블룰 검증)
    # 입금/계정주 확인(트래블룰 검증)가능 거래소 리스트
    # 입금/입금 uuid로 트래블룰 검증하기
    # 입금/입금 TxID로 트래블룰 검증하기

    # 서비스 정보/입출금 현황 (https://api.upbit.com/v1/status/wallet)
    # 서비스 정보/api키 리스트 조회 (https://api.upbit.com/v1/api_keys)

logger = logging.getLogger(__name__)


class UpbitAPI:

    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """싱글턴 패턴 구현"""
        if cls._instance is None:
            cls._instance = super(UpbitAPI, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """업비트 API 관리자 초기화"""
        if self._initialized:
            return
        
        self.server_url = "https://api.upbit.com"
        self.access_key = None
        self.secret_key = None
        self.encryption_manager = EncryptionManager()
        self._initialized = True
        logger.info("UpbitDirectAPI 초기화 완료")

    def initialize_with_api_key(self, access_key=None, secret_key=None, encrypt=False):
        """
        API 키로 업비트 API 초기화
        
        Args:
            access_key (str): 업비트 액세스 키
            secret_key (str): 업비트 시크릿 키
            encrypt (bool): True인 경우 키를 암호화하여 저장, False인 경우 이미 암호화된 키로 간주
        """
        try:
            if access_key and secret_key:
                if encrypt:
                    # 키 암호화
                    encrypted_access_key = self.encryption_manager.encrypt(access_key)
                    encrypted_secret_key = self.encryption_manager.encrypt(secret_key)
                    
                    # 암호화된 키 저장
                    self._access_key = encrypted_access_key
                    self._secret_key = encrypted_secret_key
                    
                    # API 호출용 키 설정
                    self.access_key = access_key
                    self.secret_key = secret_key
                else:
                    # 이미 암호화된 키로 간주
                    self._access_key = access_key
                    self._secret_key = secret_key
                    
                    # 복호화하여 API 호출용 키 설정
                    self.access_key = self.encryption_manager.decrypt(access_key)
                    self.secret_key = self.encryption_manager.decrypt(secret_key)
                
                # 테스트로 계좌 정보 조회해보기
                result = self.get_accounts()
                if isinstance(result, list):
                    logger.info("업비트 API가 성공적으로 초기화되었습니다.")
                    return True
                else:
                    logger.error(f"API 키 검증 실패: {result}")
                    return False
            else:
                logger.warning("API 키가 제공되지 않았습니다.")
                return False
        except Exception as e:
            logger.error(f"업비트 API 초기화 중 오류 발생: {e}")
            return False
    
    def initialize_from_encrypted_keys(self):
        """
        프로젝트에 저장된 암호화된 키를 사용하여 업비트 API 초기화
        """
        try:
            from repository.repository_apikey import ApiKeyRepository
            
            # API 키 저장소에서 키 가져오기
            api_key_repository = ApiKeyRepository()
            api_key_info = api_key_repository.get_api_key('upbit')
            
            if api_key_info.get('has_keys'):
                return self.initialize_with_api_key(
                    api_key_info.get('access_key'),
                    api_key_info.get('secret_key'),
                    encrypt=True
                )
            else:
                logger.warning("저장된 업비트 API 키를 찾을 수 없습니다.")
                return False
        except Exception as e:
            logger.error(f"저장된 키로 업비트 API 초기화 중 오류 발생: {e}")
            return False
    
    def initialize_from_user(self, user):
        """
        사용자 객체에서 API 키를 가져와 업비트 API 초기화
        
        Args:
            user (User): 사용자 객체 (models.user.User)
        """
        try:
            if user and user.upbit_access_key and user.upbit_secret_key:
                return self.initialize_with_api_key(
                    user.upbit_access_key, 
                    user.upbit_secret_key, 
                    encrypt=False
                )
            else:
                logger.warning("사용자에게 API 키가 설정되어 있지 않습니다.")
                return False
        except Exception as e:
            logger.error(f"사용자 정보로 업비트 API 초기화 중 오류 발생: {e}")
            return False
        
     # API 요청에 필요한 인증 헤더 생성
    def _get_auth_headers(self, query=None):
        """
        API 요청에 필요한 인증 헤더 생성
        
        Args:
            query (dict, optional): 쿼리 파라미터
            
        Returns:
            dict: 인증 헤더
        """
        try:
            if not self.access_key or not self.secret_key:
                raise ValueError("API 키가 설정되지 않았습니다.")
                
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4())
            }
            
            if query:
                m = hashlib.sha512()
                query_string = unquote(urlencode(query, doseq=True)).encode()
                m.update(query_string)
                query_hash = m.hexdigest()
                
                payload['query_hash'] = query_hash
                payload['query_hash_alg'] = 'SHA512'
            
            jwt_token = jwt.encode(payload, self.secret_key, algorithm="HS256")
            
            return {
                'Authorization': f'Bearer {jwt_token}'
            }
        except Exception as e:
            logger.error(f"인증 헤더 생성 중 오류 발생: {e}")
            return {}
    
    # 자산/전체 계좌 조회 (https://api.upbit.com/v1/accounts~ )
    # 계좌 정보 조회 (업비트 공식 예제 코드 기반)
    def get_accounts(self):
        
        """
        계좌 정보 조회
        
        Returns:
            list: 계좌 정보 목록
        """
        try:
            # 업비트 공식 예제 방식으로 구현
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
            }
            
            jwt_token = jwt.encode(payload, self.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            authorization = f'Bearer {jwt_token}'
            headers = {
                'Authorization': authorization,
            }
            
            response = requests.get(f"{self.server_url}/v1/accounts", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"계좌 정보 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"계좌 정보 조회 중 오류 발생: {e}")
            return {"error": str(e)}
        
     # 주문/주문 가능 정보 (https://api.upbit.com/v1/orders~)
                 
    # 주문/주문 가능 정보 (https://api.upbit.com/v1/orders~)
    def get_order_chance(self, market):
        """
        주문 가능 정보 조회
        
        Args:
            market (str): 마켓 코드 (예: KRW-BTC)
            
        Returns:
            dict: 주문 가능 정보
        """
        try:
            # 쿼리 파라미터 설정
            params = {
                'market': market
            }
            
            # 쿼리 문자열 생성 및 해시 계산
            query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()
            
            # JWT 페이로드 생성
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
                'query_hash': query_hash,
                'query_hash_alg': 'SHA512',
            }
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 인증 헤더 설정
            authorization = f'Bearer {jwt_token}'
            headers = {
                'Authorization': authorization,
            }
            
            # API 요청
            response = requests.get(f"{self.server_url}/v1/orders/chance", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"주문 가능 정보 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"주문 가능 정보 조회 중 오류 발생: {e}")
            return {"error": str(e)}
        
    # 주문/개별 주문 조회
    def get_order(self, uuid):
        """
        개별 주문 조회
        
        Args:
            uuid (str): 주문 UUID
            
        Returns:
            dict: 주문 정보
        """
        try:
            # 쿼리 파라미터 설정
            params = {
                'uuid': uuid
            }
            
            # 쿼리 문자열 생성 및 해시 계산
            query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()
            
            # JWT 페이로드 생성
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
                'query_hash': query_hash,
                'query_hash_alg': 'SHA512',
            }
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 인증 헤더 설정
            authorization = f'Bearer {jwt_token}'
            headers = {
                'Authorization': authorization,
            }
            
            # API 요청
            response = requests.get(f"{self.server_url}/v1/order", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"개별 주문 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"개별 주문 조회 중 오류 발생: {e}")
            return {"error": str(e)}

    # 주문/주문 리스트 조회
    def get_orders(self, states=None, market=None, page=1, limit=100):
        """
        주문 리스트 조회
        
        Args:
            states (list, optional): 주문 상태('wait', 'done', 'cancel'). 기본값은 None으로, 이 경우 wait, done 상태 주문 반환
            market (str, optional): 마켓 코드 (예: KRW-BTC)
            page (int, optional): 페이지 번호
            limit (int, optional): 한 페이지에 가져올 주문 개수 (최대 100)
            
        Returns:
            list: 주문 리스트
        """
        try:
            # 쿼리 파라미터 설정
            params = {}
            
            if states:
                params['states[]'] = states
            
            if market:
                params['market'] = market
                
            params['page'] = page
            params['limit'] = limit
            
            # 쿼리 문자열 생성 및 해시 계산
            query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()
            
            # JWT 페이로드 생성
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
                'query_hash': query_hash,
                'query_hash_alg': 'SHA512',
            }
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 인증 헤더 설정
            authorization = f'Bearer {jwt_token}'
            headers = {
                'Authorization': authorization,
            }
            
            # API 요청
            response = requests.get(f"{self.server_url}/v1/orders", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"주문 리스트 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"주문 리스트 조회 중 오류 발생: {e}")
            return {"error": str(e)} 
    
    # 주문/ID로 주문리스트 조회
    def get_orders_by_uuids(self, uuids):
        """
        ID로 주문 리스트 조회
        
        Args:
            uuids (list): 주문 UUID 목록
            
        Returns:
            list: 주문 리스트
        """
        try:
            # 쿼리 파라미터 설정
            params = {
                'uuids[]': uuids
            }
            
            # 쿼리 문자열 생성 및 해시 계산
            query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()
            
            # JWT 페이로드 생성
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
                'query_hash': query_hash,
                'query_hash_alg': 'SHA512',
            }
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 인증 헤더 설정
            authorization = f'Bearer {jwt_token}'
            headers = {
                'Authorization': authorization,
            }
            
            # API 요청
            response = requests.get(f"{self.server_url}/v1/orders/uuids", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"ID로 주문 리스트 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"ID로 주문 리스트 조회 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 주문/체결 대기 주문 조회 (open order)
    def get_open_orders(self, market=None, states=['wait', 'watch']):
        """
        체결 대기 주문 조회
        
        Args:
            market (str, optional): 마켓 코드 (예: KRW-BTC)
            states (list, optional): 주문 상태. 기본값은 ['wait', 'watch']
            
        Returns:
            list: 체결 대기 주문 리스트
        """
        try:
            # 쿼리 파라미터 설정
            params = {
                'states[]': states
            }
            
            if market:
                params['market'] = market
            
            # 쿼리 문자열 생성 및 해시 계산
            query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()
            
            # JWT 페이로드 생성
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
                'query_hash': query_hash,
                'query_hash_alg': 'SHA512',
            }
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 인증 헤더 설정
            authorization = f'Bearer {jwt_token}'
            headers = {
                'Authorization': authorization,
            }
            
            # API 요청
            response = requests.get(f"{self.server_url}/v1/orders/open", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"체결 대기 주문 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"체결 대기 주문 조회 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 주문/종료된 주문 조회 (closed order)
    def get_closed_orders(self, market=None, states=['done', 'cancel'], start_time=None, end_time=None, page=1, limit=100):
        """
        종료된 주문 조회
        
        Args:
            market (str, optional): 마켓 코드 (예: KRW-BTC)
            states (list, optional): 주문 상태. 기본값은 ['done', 'cancel']
            start_time (str, optional): 조회 시작 시간 (ISO 8601 형식, 예: '2021-01-01T00:00:00+09:00')
            end_time (str, optional): 조회 종료 시간 (ISO 8601 형식)
            page (int, optional): 페이지 번호
            limit (int, optional): 한 페이지에 가져올 주문 개수 (최대 100)
            
        Returns:
            list: 종료된 주문 리스트
        """
        try:
            # 쿼리 파라미터 설정
            params = {
                'states[]': states,
                'page': page,
                'limit': limit
            }
            
            if market:
                params['market'] = market
                
            if start_time:
                params['start_time'] = start_time
                
            if end_time:
                params['end_time'] = end_time
            
            # 쿼리 문자열 생성 및 해시 계산
            query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()
            
            # JWT 페이로드 생성
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
                'query_hash': query_hash,
                'query_hash_alg': 'SHA512',
            }
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 인증 헤더 설정
            authorization = f'Bearer {jwt_token}'
            headers = {
                'Authorization': authorization,
            }
            
            # API 요청
            response = requests.get(f"{self.server_url}/v1/orders/closed", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"종료된 주문 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"종료된 주문 조회 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 주문/주문 취소 접수
    def cancel_order(self, uuid):
        """
        주문 취소 접수
        
        Args:
            uuid (str): 취소할 주문의 UUID
            
        Returns:
            dict: 취소 결과
        """
        try:
            # 쿼리 파라미터 설정
            params = {
                'uuid': uuid
            }
            
            # 쿼리 문자열 생성 및 해시 계산
            query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()
            
            # JWT 페이로드 생성
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
                'query_hash': query_hash,
                'query_hash_alg': 'SHA512',
            }
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 인증 헤더 설정
            authorization = f'Bearer {jwt_token}'
            headers = {
                'Authorization': authorization,
            }
            
            # API 요청
            response = requests.delete(f"{self.server_url}/v1/order", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"주문 취소 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"주문 취소 중 오류 발생: {e}")
            return {"error": str(e)}
   
    # 주문/주문 일괄 취소 접수
    def cancel_all_orders(self, excluded_pairs=None, quote_currencies=None):
        """
        주문 일괄 취소 접수
        
        Args:
            excluded_pairs (str, optional): 취소 제외 마켓 (예: 'KRW-BTC,BTC-ETH')
            quote_currencies (str, optional): 특정 화폐 종류의 마켓 전체 취소 (예: 'KRW,BTC')
            
        Returns:
            dict: 취소 결과
        """
        try:
            # 쿼리 파라미터 설정
            params = {}
            
            if excluded_pairs:
                params['excluded_pairs'] = excluded_pairs
                
            if quote_currencies:
                params['quote_currencies'] = quote_currencies
            
            # 쿼리 문자열 생성 및 해시 계산
            query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()
            
            # JWT 페이로드 생성
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
                'query_hash': query_hash,
                'query_hash_alg': 'SHA512',
            }
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 인증 헤더 설정
            authorization = f'Bearer {jwt_token}'
            headers = {
                'Authorization': authorization,
            }
            
            # API 요청
            response = requests.delete(f"{self.server_url}/v1/orders/open", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"주문 일괄 취소 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"주문 일괄 취소 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 주문/id로 주문리스트 취소 접수
    def cancel_orders_by_uuids(self, uuids):
        """
        ID로 주문 리스트 취소 접수
        
        Args:
            uuids (list): 취소할 주문의 UUID 목록
            
        Returns:
            dict: 취소 결과
        """
        try:
            # 쿼리 파라미터 설정
            params = {
                'uuids[]': uuids
            }
            
            # 쿼리 문자열 생성 및 해시 계산
            query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()
            
            # JWT 페이로드 생성
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
                'query_hash': query_hash,
                'query_hash_alg': 'SHA512',
            }
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 인증 헤더 설정
            authorization = f'Bearer {jwt_token}'
            headers = {
                'Authorization': authorization,
            }
            
            # API 요청
            response = requests.delete(f"{self.server_url}/v1/orders/uuids", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"ID로 주문 리스트 취소 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"ID로 주문 리스트 취소 중 오류 발생: {e}")
            return {"error": str(e)}

    # 주문/주문하기
    def place_order(self, market, side, ord_type, volume=None, price=None):
        """
        주문하기
        
        Args:
            market (str): 마켓 코드 (예: KRW-BTC)
            side (str): 주문 종류 (bid: 매수, ask: 매도)
            ord_type (str): 주문 타입 (limit: 지정가, price: 시장가 매수, market: 시장가 매도)
            volume (str, optional): 주문량 (지정가, 시장가 매도 시 필수)
            price (str, optional): 주문 가격 (지정가, 시장가 매수 시 필수)
            
        Returns:
            dict: 주문 결과
        """
        try:
            # 쿼리 파라미터 설정
            params = {
                'market': market,
                'side': side,
                'ord_type': ord_type
            }
            
            if volume is not None:
                params['volume'] = str(volume)
                
            if price is not None:
                params['price'] = str(price)
            
            # 쿼리 문자열 생성 및 해시 계산
            query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()
            
            # JWT 페이로드 생성
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
                'query_hash': query_hash,
                'query_hash_alg': 'SHA512',
            }
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 인증 헤더 설정
            authorization = f'Bearer {jwt_token}'
            headers = {
                'Authorization': authorization,
                'Content-Type': 'application/json'
            }
            
            # API 요청
            response = requests.post(f"{self.server_url}/v1/orders", json=params, headers=headers)
            
            if response.status_code == 201:  # 201: Created
                return response.json()
            else:
                logger.error(f"주문 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"주문 중 오류 발생: {e}")
            return {"error": str(e)}

    # 주문/ 취소 후 재주문
    def cancel_and_new_order(self, prev_order_uuid, new_ord_type, new_price=None, new_volume=None):
        """
        취소 후 재주문
        
        Args:
            prev_order_uuid (str): 기존 주문 UUID
            new_ord_type (str): 주문 타입 (limit: 지정가, price: 시장가 매수, market: 시장가 매도)
            new_price (str, optional): 주문 가격
            new_volume (str, optional): 주문량 ('remain_only'를 전달 시 기존 주문의 잔량으로 재주문)
            
        Returns:
            dict: 주문 결과
        """
        try:
            # 쿼리 파라미터 설정
            params = {
                'prev_order_uuid': prev_order_uuid,
                'new_ord_type': new_ord_type
            }
            
            if new_price is not None:
                params['new_price'] = str(new_price)
                
            if new_volume is not None:
                params['new_volume'] = str(new_volume)
            
            # 쿼리 문자열 생성 및 해시 계산
            query_string = unquote(urlencode(params, doseq=True)).encode("utf-8")
            m = hashlib.sha512()
            m.update(query_string)
            query_hash = m.hexdigest()
            
            # JWT 페이로드 생성
            payload = {
                'access_key': self.access_key,
                'nonce': str(uuid.uuid4()),
                'query_hash': query_hash,
                'query_hash_alg': 'SHA512',
            }
            
            # JWT 토큰 생성
            jwt_token = jwt.encode(payload, self.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            # 인증 헤더 설정
            authorization = f'Bearer {jwt_token}'
            headers = {
                'Authorization': authorization,
                'Content-Type': 'application/json'
            }
            
            # API 요청
            response = requests.post(f"{self.server_url}/v1/orders/cancel_and_new", json=params, headers=headers)
            
            if response.status_code == 201:  # 201: Created
                return response.json()
            else:
                logger.error(f"취소 후 재주문 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"취소 후 재주문 중 오류 발생: {e}")
            return {"error": str(e)}