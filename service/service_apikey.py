import logging
from repository.repository_apikey import ApiKeyRepository

# 로깅 설정
logger = logging.getLogger(__name__)

class ApiKeyService:
    """
    API Key 관리를 위한 서비스 클래스
    """
    
    def __init__(self):
        """API Key 서비스 초기화"""
        self.api_key_repository = ApiKeyRepository()
    
    def get_api_keys(self):
        """
        저장된 API Key 조회 (보안을 위해 프론트엔드에는 키 존재 여부만 반환)
        
        Returns:
            dict: API Key 존재 여부
        """
        try:
            result = self.api_key_repository.get_api_key()
            
            # 보안을 위해 실제 키값은 프론트엔드에 전송하지 않음
            if result.get("has_keys"):
                return {"has_keys": True}
            else:
                return {"has_keys": False}
                
        except Exception as e:
            logger.error(f"API Key 조회 중 오류 발생: {e}")
            return {"has_keys": False, "error": str(e)}
    
    def get_actual_api_keys(self):
        """
        실제 API Key 값 조회 (백엔드 내부 사용 전용)
        
        Returns:
            dict: API Key 정보
        """
        try:
            return self.api_key_repository.get_api_key()
        except Exception as e:
            logger.error(f"API Key 조회 중 오류 발생: {e}")
            return {"has_keys": False, "error": str(e)}
    
    def save_api_keys(self, access_key, secret_key):
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
            
            return self.api_key_repository.save_api_key(access_key, secret_key)
            
        except Exception as e:
            logger.error(f"API Key 저장 중 오류 발생: {e}")
            return False, f"API Key 저장 중 오류가 발생했습니다: {str(e)}"
    
    def delete_api_keys(self):
        """
        API Key 삭제
        
        Returns:
            tuple: (성공 여부, 메시지)
        """
        try:
            return self.api_key_repository.delete_api_key()
            
        except Exception as e:
            logger.error(f"API Key 삭제 중 오류 발생: {e}")
            return False, f"API Key 삭제 중 오류가 발생했습니다: {str(e)}"