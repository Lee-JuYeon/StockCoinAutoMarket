from flask import Blueprint, request, jsonify
from service.service_apikey import ApiKeyService
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
        result = api_key_service.get_api_keys()
        return jsonify(result)
            
    except Exception as e:
        logger.error(f"API Key 조회 중 오류 발생: {e}")
        return jsonify({"error": "API Key 조회 중 오류가 발생했습니다."}), 500

@api_key_bp.route('', methods=['POST'])
def save_api_key():
    """API Key 저장 API"""
    try:
        data = request.json
        access_key = data.get('access_key')
        secret_key = data.get('secret_key')
        
        success, message = api_key_service.save_api_keys(access_key, secret_key)
        
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