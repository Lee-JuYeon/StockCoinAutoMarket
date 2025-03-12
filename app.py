from flask import Flask, render_template
import os
import logging
from routes.settings.routes_apikey import api_key_bp
import sys

# 필요한 디렉토리 추가
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(app_dir)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """Flask 애플리케이션 생성 및 설정"""
    # Flask 앱 초기화
    app = Flask(__name__, static_folder='static')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_secret_key')
    
    # Blueprint 등록
    app.register_blueprint(api_key_bp)
    
    # 라우트 설정
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    # 에러 핸들러 등록
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"서버 오류 발생: {e}")
        return render_template('500.html'), 500
    
    # 시작 메시지 로깅
    logger.info("애플리케이션이 시작되었습니다.")
    
    return app

# 애플리케이션 실행
if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 7100))
    debug = os.getenv('DEBUG', 'True') == 'True'
    
    app.run(host='0.0.0.0', port=port, debug=debug)