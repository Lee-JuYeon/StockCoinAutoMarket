from cryptography.fernet import Fernet
import os
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

class EncryptionManager:
    """
    데이터 암호화 및 복호화를 위한 클래스
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super(EncryptionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """암호화 관리자 초기화"""
        if self._initialized:
            return
            
        self.cipher_suite = self._get_cipher_suite()
        self._initialized = True
    
    def _get_cipher_suite(self):
        """암호화를 위한 Fernet 인스턴스 생성"""
        try:
            key = self._get_or_create_encryption_key()
            return Fernet(key)
        except Exception as e:
            logger.error(f"암호화 키 생성 중 오류 발생: {e}")
            return None
    
    def _get_or_create_encryption_key(self):
        """암호화 키 가져오기 또는 생성"""
        # 키를 저장할 디렉토리 생성
        key_dir = "secure"
        if not os.path.exists(key_dir):
            os.makedirs(key_dir)
            
        key_file = os.path.join(key_dir, "encryption_key.key")
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            # 키 파일 권한 설정 (Linux/Unix 시스템에서만 작동)
            try:
                os.chmod(key_file, 0o600)  # 소유자만 읽기/쓰기 가능
            except Exception as e:
                logger.warning(f"파일 권한을 설정할 수 없습니다. 보안에 유의하세요. {e}")
        return key
    
    def encrypt(self, data):
        """
        데이터 암호화
        
        Args:
            data (str): 암호화할 문자열
            
        Returns:
            str: 암호화된 문자열
        """
        if not data:
            return None
            
        if self.cipher_suite is None:
            raise ValueError("암호화 시스템 초기화에 실패했습니다.")
            
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data):
        """
        데이터 복호화
        
        Args:
            encrypted_data (str): 복호화할 암호화된 문자열
            
        Returns:
            str: 복호화된 문자열
        """
        if not encrypted_data:
            return None
            
        if self.cipher_suite is None:
            raise ValueError("암호화 시스템 초기화에 실패했습니다.")
            
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()