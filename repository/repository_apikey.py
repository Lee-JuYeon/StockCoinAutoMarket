import logging
import time
from utils.manager_db.manager_db import DBManager
from utils.manager_encryption.manager_encryption import EncryptionManager

# 로깅 설정
logger = logging.getLogger(__name__)

class ApiKeyRepository:
    """
    API Key 데이터 액세스를 위한 저장소 클래스
    """
    
    def __init__(self):
        """API Key 저장소 초기화"""
        self.db_manager = DBManager()
        self.encryption_manager = EncryptionManager()
        self._initialize_table()
    
    def _initialize_table(self):
        """API Key 테이블 초기화 (provider 컬럼 추가)"""
        try:
            # 테이블 존재 여부 확인
            check_query = """
            SELECT name FROM sqlite_master WHERE type='table' AND name='api_keys'
            """
            table_exists = self.db_manager.execute_select_one(check_query)
            
            if table_exists:
                # 컬럼 존재 여부 확인
                columns = self.db_manager.get_table_columns('api_keys')
                
                if 'provider' not in columns:
                    logger.info("API Keys 테이블에 provider 컬럼 추가")
                    
                    # 기존 테이블 이름 변경 (백업)
                    self.db_manager.execute_query('''
                    CREATE TABLE api_keys_backup AS SELECT * FROM api_keys
                    ''')
                    
                    # 기존 테이블 삭제
                    self.db_manager.execute_query("DROP TABLE api_keys")
                    
                    # 새 테이블 생성 (provider 컬럼 추가)
                    self.db_manager.execute_query('''
                    CREATE TABLE api_keys (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        provider TEXT NOT NULL DEFAULT 'upbit',
                        access_key TEXT NOT NULL,
                        secret_key TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    ''')
                    
                    # 기존 데이터 마이그레이션
                    self.db_manager.execute_query('''
                    INSERT INTO api_keys (id, provider, access_key, secret_key, created_at)
                    SELECT id, 'upbit', access_key, secret_key, created_at FROM api_keys_backup
                    ''')
            else:
                # 테이블이 없는 경우 새로 생성
                self.db_manager.execute_query('''
                CREATE TABLE api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL DEFAULT 'upbit',
                    access_key TEXT NOT NULL,
                    secret_key TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
            
            logger.info("API Keys 테이블 초기화 완료")
        except Exception as e:
            logger.error(f"API Keys 테이블 초기화 중 오류 발생: {e}")
    
    def _mask_api_key(self, api_key):
        """
        API Key 마스킹 처리 (앞 4자리만 표시)
        
        Args:
            api_key (str): 마스킹할 API Key
            
        Returns:
            str: 마스킹된 API Key
        """
        if not api_key:
            return "••••••••••••••••••"
            
        return api_key[:4] + '•' * (len(api_key) - 4)
    
    def get_api_key(self, provider=None):
        """
        API Key 조회 (특정 제공자 또는 첫 번째 API 키만 반환)
        
        Args:
            provider (str, optional): 조회할 API 제공자. 기본값은 None으로, 이 경우 가장 최근 키 반환
            
        Returns:
            dict: API Key 정보
        """
        try:
            if provider:
                query = "SELECT provider, access_key, secret_key FROM api_keys WHERE provider = ? ORDER BY id DESC LIMIT 1"
                result = self.db_manager.execute_select_one(query, (provider,))
            else:
                query = "SELECT provider, access_key, secret_key FROM api_keys ORDER BY id DESC LIMIT 1"
                result = self.db_manager.execute_select_one(query)
            
            if result:
                # 암호화된 API Key 복호화
                provider = result[0] if result[0] else 'upbit'
                access_key = self.encryption_manager.decrypt(result[1]) if result[1] else None
                secret_key = self.encryption_manager.decrypt(result[2]) if result[2] else None
                
                return {
                    "has_keys": True,
                    "provider": provider,
                    "access_key": access_key,
                    "secret_key": secret_key
                }
            else:
                return {"has_keys": False}
                
        except Exception as e:
            logger.error(f"API Key 조회 중 오류 발생: {e}")
            return {"has_keys": False, "error": str(e)}
    
    def get_api_key_list(self):
        """
        API Key 목록 조회
        
        Returns:
            list: API Key 정보 목록
        """
        try:
            query = """
            SELECT id, provider, access_key, created_at 
            FROM api_keys 
            ORDER BY created_at DESC
            """
            result = self.db_manager.execute_select(query)
            
            if not result:
                return []
            
            api_keys = []
            for row in result:
                try:
                    # 암호화된 API Key 복호화
                    access_key = self.encryption_manager.decrypt(row[2]) if row[2] else None
                except Exception as e:
                    logger.error(f"API Key 복호화 중 오류 발생: {e}")
                    access_key = None
                
                api_keys.append({
                    "id": row[0],
                    "provider": row[1],
                    "access_key": access_key,
                    "access_key_masked": self._mask_api_key(access_key),
                    "created_at": row[3]
                })
                    
            return api_keys
                    
        except Exception as e:
            logger.error(f"API Key 목록 조회 중 오류 발생: {e}")
            return []
    
    def get_key_by_provider(self, provider):
        """
        특정 제공자의 API Key 목록을 조회
        
        Args:
            provider (str): API 제공자
            
        Returns:
            list: 특정 제공자의 API Key 정보 목록
        """
        try:
            query = """
            SELECT id, provider, access_key, created_at 
            FROM api_keys 
            WHERE provider = ?
            ORDER BY created_at DESC
            """
            result = self.db_manager.execute_select(query, (provider,))
            
            if not result:
                return []
            
            api_keys = []
            for row in result:
                try:
                    access_key = self.encryption_manager.decrypt(row[2]) if row[2] else None
                    api_keys.append({
                        "id": row[0],
                        "provider": row[1],
                        "access_key": access_key,
                        "access_key_masked": self._mask_api_key(access_key),
                        "created_at": row[3]
                    })
                except Exception as e:
                    logger.error(f"API Key 복호화 중 오류 발생: {e}")
            
            return api_keys
                
        except Exception as e:
            logger.error(f"제공자별 API Key 조회 중 오류 발생: {e}")
            return []
    
    def save_api_key(self, provider, access_key, secret_key):
        """
        API Key 저장
        
        Args:
            provider (str): API 제공자
            access_key (str): API Access Key
            secret_key (str): API Secret Key
            
        Returns:
            tuple: (성공 여부, 메시지)
        """
        try:
            if not provider or not access_key or not secret_key:
                return False, "제공자, Access Key, Secret Key는 필수입니다."
                
            # API 키 암호화
            encrypted_access_key = self.encryption_manager.encrypt(access_key)
            encrypted_secret_key = self.encryption_manager.encrypt(secret_key)
            
            # 새로운 API Key 저장
            insert_query = "INSERT INTO api_keys (provider, access_key, secret_key) VALUES (?, ?, ?)"
            success = self.db_manager.execute_query(insert_query, (provider, encrypted_access_key, encrypted_secret_key))
            
            if success:
                return True, "API Key가 성공적으로 저장되었습니다."
            else:
                return False, "API Key 저장에 실패했습니다."
                
        except Exception as e:
            logger.error(f"API Key 저장 중 오류 발생: {e}")
            return False, f"API Key 저장 중 오류가 발생했습니다: {str(e)}"
    
    def delete_api_key(self):
        """
        모든 API Key 삭제
        
        Returns:
            tuple: (성공 여부, 메시지)
        """
        try:
            # API Key 삭제
            query = "DELETE FROM api_keys"
            success = self.db_manager.execute_query(query)
            
            if success:
                return True, "모든 API Key가 성공적으로 삭제되었습니다."
            else:
                return False, "API Key 삭제에 실패했습니다."
                
        except Exception as e:
            logger.error(f"API Key 삭제 중 오류 발생: {e}")
            return False, f"API Key 삭제 중 오류가 발생했습니다: {str(e)}"
            
    def delete_specific_api_key(self, key_id):
        """
        특정 API Key 삭제
        
        Args:
            key_id (int): 삭제할 API Key ID
            
        Returns:
            tuple: (성공 여부, 메시지)
        """
        try:
            if not key_id:
                return False, "API Key ID는 필수입니다."
            
            # API Key 존재 여부 확인
            check_query = "SELECT COUNT(*) FROM api_keys WHERE id = ?"
            result = self.db_manager.execute_select_one(check_query, (key_id,))
            
            if not result or result[0] == 0:
                return False, "해당 API Key를 찾을 수 없습니다."
                
            # API Key 삭제
            query = "DELETE FROM api_keys WHERE id = ?"
            success = self.db_manager.execute_query(query, (key_id,))
            
            if success:
                return True, "API Key가 성공적으로 삭제되었습니다."
            else:
                return False, "API Key 삭제에 실패했습니다."
                    
        except Exception as e:
            logger.error(f"특정 API Key 삭제 중 오류 발생: {e}")
            return False, f"API Key 삭제 중 오류가 발생했습니다: {str(e)}"