from flask import Blueprint, request, jsonify

# Blueprint 생성
auth_bp = Blueprint('account', __name__, url_prefix='/api/auth')


# 로그인 API 엔드포인트
@auth_bp.route('/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
   