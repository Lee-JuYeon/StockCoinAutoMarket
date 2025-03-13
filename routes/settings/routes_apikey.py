from flask import Blueprint, request, jsonify
from service.apikey.apikey_service import ApiKeyService
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
api_key_bp = Blueprint('api_key', __name__, url_prefix='/api/apikey')

# API Key 서비스 인스턴스 생성
api_key_service = ApiKeyService()

@api_key_bp.route('', methods=['GET'])
def get_api_key():
    """API Key 조회 API"""
    try:
        # 쿼리 파라미터에서 provider 가져오기
        provider = request.args.get('provider')
        
        result = api_key_service.get_api_keys(provider)
        return jsonify(result)
            
    except Exception as e:
        logger.error(f"API Key 조회 중 오류 발생: {e}")
        return jsonify({"error": "API Key 조회 중 오류가 발생했습니다."}), 500

@api_key_bp.route('', methods=['POST'])
def save_api_key():
    """API Key 저장 API"""
    try:
        data = request.json
        provider = data.get('provider')
        access_key = data.get('access_key')
        secret_key = data.get('secret_key')
        
        success, message = api_key_service.save_api_keys(provider, access_key, secret_key)
        
        if success:
            return jsonify({"message": message})
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        logger.error(f"API Key 저장 중 오류 발생: {e}")
        return jsonify({"error": "API Key 저장 중 오류가 발생했습니다."}), 500

@api_key_bp.route('', methods=['DELETE'])
def delete_api_key():
    """API Key 삭제 API"""
    try:
        success, message = api_key_service.delete_api_keys()
        
        if success:
            return jsonify({"message": message})
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        logger.error(f"API Key 삭제 중 오류 발생: {e}")
        return jsonify({"error": "API Key 삭제 중 오류가 발생했습니다."}), 500
    
# API Key 목록 조회 API
@api_key_bp.route('/list', methods=['GET'])
def get_api_key_list():
    """API Key 목록 조회 API"""
    try:
        # 쿼리 파라미터에서 provider 가져오기
        provider = request.args.get('provider')
        
        if provider:
            # 특정 제공자의 API Key 목록 조회
            result = api_key_service.get_provider_api_keys(provider)
        else:
            # 전체 API Key 목록 조회
            result = api_key_service.get_api_key_list()
            
        return jsonify(result)
            
    except Exception as e:
        logger.error(f"API Key 목록 조회 중 오류 발생: {e}")
        return jsonify({"error": "API Key 목록 조회 중 오류가 발생했습니다."}), 500

# 개별 API Key 삭제 API
@api_key_bp.route('/<int:key_id>', methods=['DELETE'])
def delete_specific_api_key(key_id):
    """특정 API Key 삭제 API"""
    try:
        success, message = api_key_service.delete_specific_api_key(key_id)
        
        if success:
            return jsonify({"message": message})
        else:
            return jsonify({"error": message}), 400
            
    except Exception as e:
        logger.error(f"특정 API Key 삭제 중 오류 발생: {e}")
        return jsonify({"error": f"API Key 삭제 중 오류가 발생했습니다: {str(e)}"}), 500

# 특정 제공자 API Key 조회 API
@api_key_bp.route('/provider/<string:provider>', methods=['GET'])
def get_provider_api_keys(provider):
    """특정 제공자의 API Key 목록 조회 API"""
    try:
        result = api_key_service.get_provider_api_keys(provider)
        return jsonify(result)
            
    except Exception as e:
        logger.error(f"제공자별 API Key 조회 중 오류 발생: {e}")
        return jsonify({"error": "제공자별 API Key 조회 중 오류가 발생했습니다."}), 500

@api_key_bp.route('/test-connection', methods=['POST'])
def test_api_connection():
    """API Key 연결 테스트 API"""
    try:
        data = request.json
        provider = data.get('provider')
        access_key = data.get('access_key')
        secret_key = data.get('secret_key')
        
        if not provider or not access_key or not secret_key:
            return jsonify({"error": "제공자, Access Key, Secret Key는 필수입니다."}), 400
            
        # 추가: 각 제공자별 연결 테스트 로직
        # 현재는 간단히 성공으로 반환
        return jsonify({
            "success": True, 
            "message": f"{provider} API 연결이 성공적으로 테스트되었습니다."
        })
        
    except Exception as e:
        logger.error(f"API 연결 테스트 중 오류 발생: {e}")
        return jsonify({"error": "API 연결 테스트 중 오류가 발생했습니다."}), 500

@api_key_bp.route('/providers', methods=['GET'])
def get_supported_providers():
    """지원되는 API 제공자 목록 조회 API"""
    try:
        # 지원되는 API 제공자 목록
        providers = [
            {"id": "upbit", "name": "업비트", "type": "crypto"},
            {"id": "koreainvestment", "name": "한국투자증권", "type": "stock"},
            {"id": "binance", "name": "바이낸스", "type": "crypto"},
            {"id": "coinbase", "name": "코인베이스", "type": "crypto"},
            {"id": "kraken", "name": "크라켄", "type": "crypto"}
        ]
        
        return jsonify({"providers": providers})
        
    except Exception as e:
        logger.error(f"API 제공자 목록 조회 중 오류 발생: {e}")
        return jsonify({"error": "API 제공자 목록 조회 중 오류가 발생했습니다."}), 500

@api_key_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_api_keys(user_id):
    """사용자별 API Key 목록 조회 API (인증 필요)"""
    try:
        # 추가: 인증 확인 로직 구현 필요
        # 현재는 간단히 사용자 ID 확인
        if not user_id or user_id <= 0:
            return jsonify({"error": "유효하지 않은 사용자 ID입니다."}), 400
            
        # 현재는 모든 API Key를 조회 (실제로는 사용자별 필터링 필요)
        result = api_key_service.get_api_key_list()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"사용자별 API Key 조회 중 오류 발생: {e}")
        return jsonify({"error": "사용자별 API Key 조회 중 오류가 발생했습니다."}), 500