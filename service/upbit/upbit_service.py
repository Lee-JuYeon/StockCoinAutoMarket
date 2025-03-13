import pyupbit
import logging
import time
from utils.manager_encryption.manager_encryption import EncryptionManager

logger = logging.getLogger(__name__)

class UpbitService:
    """
    업비트 API 연동을 위한 서비스 클래스
    - 시세 조회, 매수/매도, 잔고 조회 등 업비트 API 관련 기능 제공
    """
    
    def __init__(self, access_key=None, secret_key=None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.upbit = None
        self.encryption_manager = EncryptionManager()
        
        if access_key and secret_key:
            self.initialize_upbit()
    
    # 업비트 API 객체 초기화
    def initialize_upbit(self):
        try:
            self.upbit = pyupbit.Upbit(self.access_key, self.secret_key)
            logger.info("Upbit API 초기화 성공")
        except Exception as e:
            logger.error(f"Upbit API 초기화 실패: {e}")
            self.upbit = None
    
    # 시세 정보 관련 메서드 / 현재 시세 조회
    def get_ticker_price(self, ticker):
        try:
            return pyupbit.get_current_price(ticker)
        except Exception as e:
            logger.error(f"시세 조회 실패: {e}")
            return None
    
    # OHLCV(시가, 고가, 저가, 종가, 거래량) 데이터 조회
    def get_ohlcv(self, ticker, interval="day", count=30):
        try:
            df = pyupbit.get_ohlcv(ticker, interval=interval, count=count)
            return df
        except Exception as e:
            logger.error(f"OHLCV 데이터 조회 실패: {e}")
            return None
    
    # 잔고 관련 메서드 / 계좌 잔고 조회
    def get_balance(self, ticker=None):
        try:
            if self.upbit is None:
                return {"error": "Upbit API가 초기화되지 않았습니다."}
                
            if ticker:
                # 특정 코인 잔고 조회
                return self.upbit.get_balance(ticker)
            else:
                # 전체 잔고 조회
                return self.upbit.get_balances()
        except Exception as e:
            logger.error(f"잔고 조회 실패: {e}")
            return {"error": str(e)}
    
    # 주문 관련 메서드 / 시장가 매수
    def buy_market_order(self, ticker, amount):
        try:
            if self.upbit is None:
                return {"error": "Upbit API가 초기화되지 않았습니다."}
                
            result = self.upbit.buy_market_order(ticker, amount)
            logger.info(f"시장가 매수 요청: {ticker}, {amount}")
            return result
        except Exception as e:
            logger.error(f"시장가 매수 실패: {e}")
            return {"error": str(e)}
    # 시장가 매도
    def sell_market_order(self, ticker, amount):
        try:
            if self.upbit is None:
                return {"error": "Upbit API가 초기화되지 않았습니다."}
                
            result = self.upbit.sell_market_order(ticker, amount)
            logger.info(f"시장가 매도 요청: {ticker}, {amount}")
            return result
        except Exception as e:
            logger.error(f"시장가 매도 실패: {e}")
            return {"error": str(e)}
    
    # 기타 업비트 API 관련 메서드
    def get_orderbook(self, ticker):
        """호가창 조회"""
        try:
            return pyupbit.get_orderbook(ticker)
        except Exception as e:
            logger.error(f"호가창 조회 실패: {e}")
            return None
    
    # 거래량 기준 상위 코인 조회
    def get_top_volume_tickers(self, limit=10):
        try:
            tickers = pyupbit.get_tickers(fiat="KRW")
            volume_data = []
            
            for ticker in tickers[:30]:
                time.sleep(0.1)  # API 호출 제한 방지
                current_price = self.get_ticker_price(ticker)
                if current_price:
                    ohlcv = self.get_ohlcv(ticker, interval="day", count=1)
                    if ohlcv is not None and not ohlcv.empty:
                        volume = ohlcv.iloc[0]['volume']
                        volume_data.append({
                            'ticker': ticker,
                            'volume': volume,
                            'price': current_price
                        })
            
            # 거래량 기준 정렬
            volume_data.sort(key=lambda x: x['volume'], reverse=True)
            return volume_data[:limit]
        except Exception as e:
            logger.error(f"거래량 상위 코인 조회 실패: {e}")
            return []