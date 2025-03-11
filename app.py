from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import logging

from routes.ui.routes_auth import auth_bp
from utils.manager_selenium.manager_selenium import SeleniumManager

seleniumManager = SeleniumManager()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask 앱 초기화
app = Flask(__name__, static_folder='static')

# Blueprint 등록
app.register_blueprint(auth_bp)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    

     # 셀레니움 매니저 초기화
    seleniumManager = SeleniumManager()
    
    # 로그인된 경우 처리 함수
    def when_logged_in():
        print("로그인이 확인되었습니다.")
        # API 키 발급 진행
        return seleniumManager.getUpBitApiKey()
    
    # 로그인 안 된 경우 처리 함수
    def when_not_logged_in():
        print("="*50)
        print("업비트 로그인이 필요합니다.")
        print("브라우저 창에서 로그인을. 완료한 후 다시 시도해주세요.")
        print("="*50)
        # 브라우저에 알림 표시
        seleniumManager.driver.execute_script("alert('업비트 로그인이 필요합니다.');")
    
    # 로그인 상태 확인 (isLogin 메서드 호출)
    is_logged_in = seleniumManager.isLogin()
    
    # match-case로 로그인 상태에 따라 처리
    match is_logged_in:
        case True:
            when_logged_in()
        case False:
            when_not_logged_in()
        case _:
            when_not_logged_in()
  
    # 그런 다음 Flask 실행
    app.run(host='0.0.0.0', port=7100, debug=True)