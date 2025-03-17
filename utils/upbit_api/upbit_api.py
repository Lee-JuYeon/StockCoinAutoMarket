"""
업비트 API 싱글톤 클래스
- 자산, 주문, 입금, 출금, 서비스 정보 모듈을 통합하여 관리
"""
import logging
from utils.manager_encryption.manager_encryption import EncryptionManager
from .modules.accounts import AccountsModule
from .modules.orders import OrdersModule
from .modules.deposits import DepositsModule
from .modules.withdrawals import WithdrawalsModule
from .modules.service_info import ServiceInfoModule
from .utils.auth import generate_auth_headers

logger = logging.getLogger(__name__)

class UpbitAPI:
    """
    업비트 API 싱글톤 클래스
    - 각 기능별 모듈을 통합하여 관리
    """
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
        
        # 각 기능별 모듈 초기화
        self.accounts = AccountsModule(self)
        self.orders = OrdersModule(self)
        self.deposits = DepositsModule(self)
        self.withdrawals = WithdrawalsModule(self)
        self.service_info = ServiceInfoModule(self)
        
        self._initialized = True
        logger.info("UpbitAPI 초기화 완료")

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
                result = self.accounts.get_accounts()
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

    # 인증 헤더 생성 메서드 - auth.py로 이동했지만 편의를 위해 래퍼 메서드 제공
    def get_auth_headers(self, query=None):
        """
        API 요청에 필요한 인증 헤더 생성
        
        Args:
            query (dict, optional): 쿼리 파라미터
            
        Returns:
            dict: 인증 헤더
        """
        if not self.access_key or not self.secret_key:
            logger.error("API 키가 설정되지 않았습니다.")
            return {}
        
        return generate_auth_headers(self.access_key, self.secret_key, query)
        