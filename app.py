from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
import os
import logging
from datetime import datetime
import sys
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from apscheduler.schedulers.background import BackgroundScheduler

# 모델 가져오기
from models.user import db, User
from models.trade import Trade
from models.recommendation import Recommendation

# 라우트 가져오기
from routes.ui.routes_auth import auth_bp
from routes.settings.routes_apikey import api_key_bp
from routes.settings.routes_settings import settings_bp

# 서비스 가져오기
from services.upbit_service import UpbitService
from services.trading_service import TradingService
from services.recommendation_service import RecommendationService
from services.chart_service import ChartService

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
    app.config.from_object('config.Config')
    
    # 데이터베이스 초기화
    db.init_app(app)
    
    # 로그인 매니저 설정
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Blueprint 등록
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_key_bp)
    app.register_blueprint(settings_bp)
    
    # 데이터베이스 생성
    with app.app_context():
        db.create_all()
    
    # 스케줄러 설정
    scheduler = BackgroundScheduler()
    
    # 자동 매매 작업 스케줄링
    @scheduler.scheduled_job('interval', minutes=5)
    def run_auto_trading():
        with app.app_context():
            # 자동 매매가 활성화된 사용자 가져오기
            users = User.query.filter_by(auto_trading_enabled=True).all()
            for user in users:
                # 각 사용자에 대한 자동 매매 실행
                trading_service = TradingService(user)
                result = trading_service.execute_auto_trading()
                logger.info(f"자동 매매 결과 (사용자 {user.id}): {result}")
    
    # 추천 작업 스케줄링
    @scheduler.scheduled_job('interval', minutes=30)
    def run_recommendations():
        with app.app_context():
            # 사용자 가져오기
            users = User.query.all()
            for user in users:
                # 각 사용자에 대한 추천 생성
                recommendation_service = RecommendationService(user)
                recommendations = recommendation_service.generate_recommendations()
                logger.info(f"추천 생성 완료 (사용자 {user.id}): {len(recommendations)}개")
    
    # 스케줄러 시작
    scheduler.start()
    
    # 라우트 설정
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # 거래 서비스 초기화
        trading_service = TradingService(current_user)
        
        # 사용자 잔액 조회
        upbit_service = UpbitService()
        if current_user.upbit_access_key and current_user.upbit_secret_key:
            from utils.manager_encryption.manager_encryption import EncryptionManager
            encryption_manager = EncryptionManager()
            access_key = encryption_manager.decrypt(current_user.upbit_access_key)
            secret_key = encryption_manager.decrypt(current_user.upbit_secret_key)
            upbit_service.set_keys(access_key, secret_key, encrypt=False)
            
            balance_info = upbit_service.get_balance()
        else:
            balance_info = {"error": "API 키가 설정되지 않았습니다."}
        
        # 최근 거래 내역
        recent_trades = trading_service.get_trade_history(user_id=current_user.id, limit=10)
        
        # 최근 추천
        recent_recommendations = Recommendation.query.filter_by(
            user_id=current_user.id,
            status='pending'
        ).order_by(Recommendation.timestamp.desc()).limit(5).all()
        
        return render_template(
            'dashboard.html',
            user=current_user,
            balance_info=balance_info,
            recent_trades=recent_trades,
            recent_recommendations=recent_recommendations
        )
    
    @app.route('/history')
    @login_required
    def history():
        # 거래 내역 조회
        trading_service = TradingService(current_user)
        trades = trading_service.get_trade_history(user_id=current_user.id, limit=50)
        
        return render_template('history.html', trades=trades)
    
    @app.route('/api/charts/ticker/<ticker>')
    def get_ticker_chart_data(ticker):
        """특정 코인의 차트 데이터 API"""
        interval = request.args.get('interval', 'day')
        count = int(request.args.get('count', 30))
        
        chart_service = ChartService()
        data = chart_service.get_ohlcv_data(ticker, interval, count)
        
        if data is None:
            return jsonify({"error": "데이터를 불러올 수 없습니다."}), 400
            
        return jsonify(data.to_dict('records'))
    
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