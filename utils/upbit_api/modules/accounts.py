"""
업비트 API 자산/계좌 관련 모듈
- 자산/전체 계좌 조회
- 기타 자산 관련 기능
"""
import requests
import logging
import uuid
import jwt

logger = logging.getLogger(__name__)

class AccountsModule:
    """
    업비트 API 자산/계좌 관련 기능 모듈
    """
    
    def __init__(self, api):
        """
        자산/계좌 모듈 초기화
        
        Args:
            api (UpbitAPI): 상위 UpbitAPI 인스턴스
        """
        self.api = api
        self.server_url = api.server_url
    
    def get_accounts(self):
        """
        전체 계좌 정보 조회
        
        Returns:
            list: 계좌 정보 목록
        """
        try:
            # 업비트 공식 예제 방식으로 구현
            payload = {
                'access_key': self.api.access_key,
                'nonce': str(uuid.uuid4()),
            }
            
            jwt_token = jwt.encode(payload, self.api.secret_key)
            
            # PyJWT 2.0.0 이상에서는 bytes가 아닌 문자열 반환
            if isinstance(jwt_token, bytes):
                jwt_token = jwt_token.decode('utf-8')
            
            authorization = f'Bearer {jwt_token}'
            headers = {
                'Authorization': authorization,
            }
            
            response = requests.get(f"{self.server_url}/v1/accounts", headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"계좌 정보 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"계좌 정보 조회 중 오류 발생: {e}")
            return {"error": str(e)}
    
    def get_account_balance(self, ticker=None):
        """
        특정 자산 잔고 조회
        
        Args:
            ticker (str, optional): 코인 티커 (예: KRW-BTC). None이면 전체 잔고 반환
            
        Returns:
            dict: 잔고 정보
        """
        try:
            accounts = self.get_accounts()
            
            if isinstance(accounts, dict) and 'error' in accounts:
                return accounts
            
            if ticker:
                # 티커 표준화 (KRW-BTC 형식을 BTC로 변환)
                currency = ticker.split('-')[-1] if '-' in ticker else ticker
                
                # 특정 코인 잔고 검색
                for account in accounts:
                    if account.get('currency') == currency:
                        return {
                            'currency': currency,
                            'balance': account.get('balance', '0'),
                            'locked': account.get('locked', '0'),
                            'avg_buy_price': account.get('avg_buy_price', '0'),
                            'avg_buy_price_modified': account.get('avg_buy_price_modified', False)
                        }
                
                # 코인을 찾지 못한 경우
                return {
                    'currency': currency,
                    'balance': '0',
                    'locked': '0',
                    'avg_buy_price': '0',
                    'avg_buy_price_modified': False
                }
            else:
                # 전체 자산 정보 반환
                return accounts
        except Exception as e:
            logger.error(f"자산 잔고 조회 중 오류 발생: {e}")
            return {"error": str(e)}
            
    def get_krw_balance(self):
        """
        원화(KRW) 잔고 조회
        
        Returns:
            str: 원화 잔고
        """
        try:
            krw_account = self.get_account_balance('KRW')
            
            if isinstance(krw_account, dict) and 'error' in krw_account:
                return "0"
            
            if isinstance(krw_account, dict):
                return krw_account.get('balance', '0')
            
            # 목록 형태인 경우 KRW를 찾아서 반환
            for account in krw_account:
                if account.get('currency') == 'KRW':
                    return account.get('balance', '0')
            
            return "0"
        except Exception as e:
            logger.error(f"원화 잔고 조회 중 오류 발생: {e}")
            return "0"