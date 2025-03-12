from flask import Blueprint, request, jsonify, session
from models.user import User, db
from werkzeug.security import generate_password_hash
import logging
from cryptography.fernet import Fernet
import os

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')

# 암호화 키 생성 (실제 서비스에서는 환경 변수나 안전한 저장소에서 불러와야 함)
# 프로덕션 환경에서는 이 키를 환경 변수로 관리하고 서버 재시작시에도 같은 키를 사용해야 함
def get_or_create_encryption_key():
    key_file = "encryption_key.key"
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
        except:
            logger.warning("파일 권한을 설정할 수 없습니다. 보안에 유의하세요.")
    return key

# Fernet 인스턴스 생성
try:
    encryption_key = get_or_create_encryption_key()
    cipher_suite = Fernet(encryption_key)
except Exception as e:
    logger.error(f"암호화 키 생성 중 오류 발생: {e}")
    # 임시 대체 키 (실제로는 사용하지 말 것)
    cipher_suite = None

# API Key 암호화 함수
def encrypt_api_key(api_key):
    if cipher_suite is None:
        raise ValueError("암호화 시스템 초기화에 실패했습니다.")
    return cipher_suite.encrypt(api_key.encode()).decode()

# API Key 복호화 함수
def decrypt_api_key(encrypted_api_key):
    if cipher_suite is None:
        raise ValueError("암호화 시스템 초기화에 실패했습니다.")
    return cipher_suite.decrypt(encrypted_api_key.encode()).decode()

# API Key 조회 API
@settings_bp.route('/apikey', methods=['GET'])
def get_api_key():
    try:
        user = User.query.get(current_user.id)
        
        if not user:
            return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404
            
        # API 키가 있는지 확인
        has_keys = bool(user.upbit_access_key and user.upbit_secret_key)
        
        return jsonify({
            "has_keys": has_keys,
            # 실제 키는 보안상 절대 반환하지 않음
        })
        
    except Exception as e:
        logger.error(f"API Key 조회 중 오류 발생: {e}")
        return jsonify({"error": "API Key 조회 중 오류가 발생했습니다."}), 500

# API Key 저장 API
@settings_bp.route('/apikey', methods=['POST'])
def save_api_key():
    try:
        data = request.json
        access_key = data.get('access_key')
        secret_key = data.get('secret_key')
        
        if not access_key or not secret_key:
            return jsonify({"error": "Access Key와 Secret Key는 필수입니다."}), 400
            
        user = User.query.get(current_user.id)
        
        if not user:
            return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404
            
        # API 키 암호화
        encrypted_access_key = encrypt_api_key(access_key)
        encrypted_secret_key = encrypt_api_key(secret_key)
        
        # 암호화된 API 키 저장
        user.upbit_access_key = encrypted_access_key
        user.upbit_secret_key = encrypted_secret_key
        
        db.session.commit()
        
        return jsonify({"message": "API Key가 성공적으로 저장되었습니다."})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"API Key 저장 중 오류 발생: {e}")
        return jsonify({"error": "API Key 저장 중 오류가 발생했습니다."}), 500

# API Key 업데이트 API
@settings_bp.route('/apikey', methods=['PUT'])
def update_api_key():
    try:
        data = request.json
        access_key = data.get('access_key')
        secret_key = data.get('secret_key')
        
        if not access_key or not secret_key:
            return jsonify({"error": "Access Key와 Secret Key는 필수입니다."}), 400
            
        user = User.query.get(current_user.id)
        
        if not user:
            return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404
            
        # API 키 암호화
        encrypted_access_key = encrypt_api_key(access_key)
        encrypted_secret_key = encrypt_api_key(secret_key)
        
        # 암호화된 API 키 업데이트
        user.upbit_access_key = encrypted_access_key
        user.upbit_secret_key = encrypted_secret_key
        
        db.session.commit()
        
        return jsonify({"message": "API Key가 성공적으로 업데이트되었습니다."})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"API Key 업데이트 중 오류 발생: {e}")
        return jsonify({"error": "API Key 업데이트 중 오류가 발생했습니다."}), 500

# API Key 삭제 API
@settings_bp.route('/apikey', methods=['DELETE'])
def delete_api_key():
    try:
        user = User.query.get(current_user.id)
        
        if not user:
            return jsonify({"error": "사용자를 찾을 수 없습니다."}), 404
            
        # API 키 삭제
        user.upbit_access_key = None
        user.upbit_secret_key = None
        
        db.session.commit()
        
        return jsonify({"message": "API Key가 성공적으로 삭제되었습니다."})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"API Key 삭제 중 오류 발생: {e}")
        return jsonify({"error": "API Key 삭제 중 오류가 발생했습니다."}), 500