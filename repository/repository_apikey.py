import logging
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
    
    def get_api_key(self):
        """
        API Key 조회
        
        Returns:
            dict: API Key 정보
        """
        try:
            query = "SELECT access_key, secret_key FROM api_keys ORDER BY id DESC LIMIT 1"
            result = self.db_manager.execute_select_one(query)
            
            if result:
                # 암호화된 API Key 복호화
                access_key = self.encryption_manager.decrypt(result[0]) if result[0] else None
                secret_key = self.encryption_manager.decrypt(result[1]) if result[1] else None
                
                return {
                    "has_keys": True,
                    "access_key": access_key,
                    "secret_key": secret_key
                }
            else:
                return {"has_keys": False}
                
        except Exception as e:
            logger.error(f"API Key 조회 중 오류 발생: {e}")
            return {"has_keys": False, "error": str(e)}
    
    def save_api_key(self, access_key, secret_key):
        """
        API Key 저장
        
        Args:
            access_key (str): API Access Key
            secret_key (str): API Secret Key
            
        Returns:
            tuple: (성공 여부, 메시지)
        """
        try:
            if not access_key or not secret_key:
                return False, "Access Key와 Secret Key는 필수입니다."
                
            # API 키 암호화
            encrypted_access_key = self.encryption_manager.encrypt(access_key)
            encrypted_secret_key = self.encryption_manager.encrypt(secret_key)
            
            # 기존 API Key가 있는지 확인
            query = "SELECT COUNT(*) FROM api_keys"
            result = self.db_manager.execute_select_one(query)
            
            if result and result[0] > 0:
                # 기존 API Key 업데이트
                update_query = """
                UPDATE api_keys 
                SET access_key = ?, secret_key = ? 
                WHERE id = (SELECT id FROM api_keys ORDER BY id DESC LIMIT 1)
                """
                success = self.db_manager.execute_query(update_query, (encrypted_access_key, encrypted_secret_key))
            else:
                # 새로운 API Key 저장
                insert_query = "INSERT INTO api_keys (access_key, secret_key) VALUES (?, ?)"
                success = self.db_manager.execute_query(insert_query, (encrypted_access_key, encrypted_secret_key))
            
            if success:
                return True, "API Key가 성공적으로 저장되었습니다."
            else:
                return False, "API Key 저장에 실패했습니다."
                
        except Exception as e:
            logger.error(f"API Key 저장 중 오류 발생: {e}")
            return False, f"API Key 저장 중 오류가 발생했습니다: {str(e)}"
    
    def delete_api_key(self):
        """
        API Key 삭제
        
        Returns:
            tuple: (성공 여부, 메시지)
        """
        try:
            # API Key 삭제
            query = "DELETE FROM api_keys"
            success = self.db_manager.execute_query(query)
            
            if success:
                return True, "API Key가 성공적으로 삭제되었습니다."
            else:
                return False, "API Key 삭제에 실패했습니다."
                
        except Exception as e:
            logger.error(f"API Key 삭제 중 오류 발생: {e}")
            return False, f"API Key 삭제 중 오류가 발생했습니다: {str(e)}"
            
    def get_api_key_list(self):
        """
        API Key 목록 조회
        
        Returns:
            list: API Key 정보 목록
        """
        try:
            query = """
            SELECT id, access_key, created_at 
            FROM api_keys 
            ORDER BY created_at DESC
            """
            result = self.db_manager.execute_select(query)
            
            if not result:
                return []
            
            api_keys = []
            for row in result:
                # 암호화된 API Key 복호화
                access_key = self.encryption_manager.decrypt(row[1]) if row[1] else None
                
                api_keys.append({
                    "id": row[0],
                    "access_key": access_key,
                    "created_at": row[2]
                })
                    
            return api_keys
                    
        except Exception as e:
            logger.error(f"API Key 목록 조회 중 오류 발생: {e}")
            return []
        
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