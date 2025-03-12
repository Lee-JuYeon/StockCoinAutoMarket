from flask import Flask, render_template, send_from_directory
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
    
    # 템플릿 디렉토리 생성 확인
    if not os.path.exists('templates'):
        os.makedirs('templates')
        logger.info("templates 디렉토리가 생성되었습니다.")
    
    # 오류 페이지 템플릿 생성 확인
    error_templates = {
        '404.html': '페이지를 찾을 수 없습니다.',
        '500.html': '서버 내부 오류가 발생했습니다.'
    }
    
    for template, message in error_templates.items():
        template_path = os.path.join('templates', template)
        if not os.path.exists(template_path):
            # 기본 오류 템플릿 생성
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{message}</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
        h1 {{ color: #333; }}
        .message {{ color: #666; margin: 20px 0; }}
        .home-link {{ display: inline-block; margin-top: 20px; color: #0066cc; text-decoration: none; }}
    </style>
</head>
<body>
    <h1>{template.split('.')[0]}</h1>
    <div class="message">{message}</div>
    <a href="/" class="home-link">홈으로 돌아가기</a>
</body>
</html>''')
            logger.info(f"{template} 템플릿이 생성되었습니다.")
    
    # 라우트 설정
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    # 정적 파일 추가 경로 설정
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon'
        )
    
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