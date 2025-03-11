from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.manager_ip.manager_ip import IpManager

# 웹드라이버 자동 관리를 위한 라이브러리
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

import time
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SeleniumManager():
    
    def __init__(self):
        try:
            # Chrome 옵션 설정
            chrome_options = Options()
            chrome_options.add_argument("--window-size=1500,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            
            # 크롬이 설치되어 있는지 확인 후 드라이버 자동 설치
            logger.info("SeleniumManager, init // 🏁 크롬드라이버 자동 설치 시작...")
            self.service = Service(ChromeDriverManager().install())
            
            # WebDriver 초기화
            self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)  # 최대 10초 대기
            logger.info("SeleniumManager, init // ✅ 셀레니움 초기화 성공")
            
        except Exception as e:
            logger.error(f"SeleniumManager, init // ⛔ 셀레니움 초기화 중 오류 발생: {e}")
            # 사용자에게 크롬 설치 확인 메시지 표시
            logger.info("SeleniumManager, init // ⛔ Chrome 브라우저가 설치되어 있지 않거나 호환되지 않는 버전입니다.")
            logger.info("SeleniumManager, init // ⛔ https://www.google.com/chrome/ 에서 Chrome을 설치한 후 다시 시도해주세요.")
            raise
            
    def close(self):
        if self.driver:
            self.driver.quit()
            logger.info("SeleniumManager, close // ✅ 종료됨") 
        
    def isLogin(self):
        try:
            # 업비트 로그인 페이지 이동
            self.driver.get("https://upbit.com/upbit_user/private/signin?pathname=%2Fhome")
            
            # 페이지 로딩 대기
            time.sleep(5)
            
            # QR 코드 로그인 버튼 찾기 시도
            qr_login_elements = self.driver.find_elements(By.CLASS_NAME, "css-10b4mob")
            
            if qr_login_elements:
                logger.info("SeleniumManager, checkLoginStateUpbit // 🔓 로그인 되지 않은 상태 확인")
                return False
            else:
                logger.info("SeleniumManager, checkLoginStateUpbit // 🔒 이미 로그인된 상태")
                return True
        except Exception as e:
            logger.error(f"SeleniumManager, checkLoginStateUpbit // ⛔ 로그인 상태 확인 중 오류: {e}")
        
        
            
    def getUpBitApiKey(self):
        # 업비트 open api 페이지로 이동
        self.driver.get("https://upbit.com/mypage/open_api_management")     
            
        # 모든 체크박스 찾기
        checkboxes = self.driver.find_elements(By.CSS_SELECTOR, ".OpenApi__boxTabCont__cate__item .css-1b512s9")
            
        # 각 체크박스 클릭 (읽기 전용 속성 제거 필요할 수 있음)
        for checkbox in checkboxes:
            if not checkbox.is_selected() and checkbox.is_enabled():
                # JavaScript로 readonly 속성 제거 후 클릭
                self.driver.execute_script("arguments[0].removeAttribute('readonly')", checkbox)
                # JavaScript로 클릭 (일반 클릭이 작동하지 않을 경우)
                self.driver.execute_script("arguments[0].click();", checkbox)
                print("체크박스 클릭됨")
                time.sleep(0.5)  # 약간의 지연 추가
            
        # 체크박스가 클릭되지 않을 경우, 부모 요소를 클릭하는 대안 방법 시도
        if not all(checkbox.is_selected() for checkbox in checkboxes):
            print("체크박스 직접 클릭 실패, 부모 요소 클릭 시도")
            checkbox_containers = self.driver.find_elements(By.CSS_SELECTOR, ".OpenApi__boxTabCont__cate__item .css-j262ou")
            for container in checkbox_containers:
                self.driver.execute_script("arguments[0].click();", container)
                time.sleep(0.5)  # 약간의 지연 추가
        
           
        # IP 주소 입력 필드 찾기 - 제공된 CSS 클래스 사용
        ip_input = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input.css-u80jbl[placeholder*='IP 주소 입력']")))
        ip_input.clear()
        ip_input.send_keys(IpManager.get_local_ip())
        
