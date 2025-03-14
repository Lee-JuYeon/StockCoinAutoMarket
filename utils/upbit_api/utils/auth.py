"""
업비트 API 인증 관련 유틸리티 함수
"""
import uuid
import jwt
import hashlib
import logging
from urllib.parse import urlencode, unquote

logger = logging.getLogger(__name__)

def generate_auth_headers(access_key, secret_key, query=None):
    """
    API 요청에 필요한 인증 헤더 생성
    
    Args:
        access_key (str): 업비트 액세스 키
        secret_key (str): 업비트 시크릿 키
        query (dict, optional): 쿼리 파라미터
        
    Returns:
        dict: 인증 헤더
    """
    try:
        payload = {
            'access_key': access_key,
            'nonce': str(uuid.uuid4())
        }
        
        if query:
            m = hashlib.sha512()
            query_string = unquote(urlencode(query, doseq=True)).encode()
            m.update(query_string)
            query_hash = m.hexdigest()
            
            payload['query_hash'] = query_hash
            payload['query_hash_alg'] = 'SHA512'
        
        jwt_token = jwt.encode(payload, secret_key, algorithm="HS256")
        
        # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
        if isinstance(jwt_token, bytes):
            jwt_token = jwt_token.decode('utf-8')
        
        return {
            'Authorization': f'Bearer {jwt_token}'
        }
    except Exception as e:
        logger.error(f"인증 헤더 생성 중 오류 발생: {e}")
        return {}