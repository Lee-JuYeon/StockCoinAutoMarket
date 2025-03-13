import pyupbit
import logging
import time
from utils.manager_encryption.manager_encryption import EncryptionManager

logger = logging.getLogger(__name__)

class UpbitService:
    def __init__(self, access_key=None, secret_key=None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.upbit = None
        self.encryption_manager = EncryptionManager()
        
        if access_key and secret_key:
            self.initialize_upbit()
    
    def initialize_upbit(self):
        """업비트 API 객체 초기화"""
        try:
            self.upbit = pyupbit.Upbit(self.access_key, self.secret_key)
            logger.info("Upbit API 초기화 성공")
        except Exception as e:
            logger.error(f"Upbit API 초기화 실패: {e}")
            self.upbit = None
    
    def set_keys(self, access_key, secret_key, encrypt=True):
        """API 키 설정"""
        if encrypt:
            self.access_key = self.encryption_manager.encrypt(access_key)
            self.secret_key = self.encryption_manager.encrypt(secret_key)
        else:
            self.access_key = access_key
            self.secret_key = secret_key
        
        self.initialize_upbit()
    
    def get_balance(self, ticker=None):
        """계좌 잔고 조회"""
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
    
    def get_ticker_price(self, ticker):
        """현재 시세 조회"""
        try:
            return pyupbit.get_current_price(ticker)
        except Exception as e:
            logger.error(f"시세 조회 실패: {e}")
            return None
    
    def get_ticker_info(self, ticker):
        """코인 정보 조회"""
        try:
            # 코인 현재가
            current_price = pyupbit.get_current_price(ticker)
            
            # 일봉 데이터
            df_daily = pyupbit.get_ohlcv(ticker, interval="day", count=7)
            
            # 현재 호가
            orderbook = pyupbit.get_orderbook(ticker)
            
            return {
                "current_price": current_price,
                "daily_data": df_daily.to_dict('records') if df_daily is not None else [],
                "orderbook": orderbook
            }
        except Exception as e:
            logger.error(f"코인 정보 조회 실패: {e}")
            return {"error": str(e)}
    
    def buy_market_order(self, ticker, amount):
        """시장가 매수"""
        try:
            if self.upbit is None:
                return {"error": "Upbit API가 초기화되지 않았습니다."}
                
            result = self.upbit.buy_market_order(ticker, amount)
            logger.info(f"시장가 매수 요청: {ticker}, {amount}")
            return result
        except Exception as e:
            logger.error(f"시장가 매수 실패: {e}")
            return {"error": str(e)}
    
    def sell_market_order(self, ticker, amount):
        """시장가 매도"""
        try:
            if self.upbit is None:
                return {"error": "Upbit API가 초기화되지 않았습니다."}
                
            result = self.upbit.sell_market_order(ticker, amount)
            logger.info(f"시장가 매도 요청: {ticker}, {amount}")
            return result
        except Exception as e:
            logger.error(f"시장가 매도 실패: {e}")
            return {"error": str(e)}
    
    def get_order_list(self, state='done'):
        """주문 내역 조회"""
        try:
            if self.upbit is None:
                return {"error": "Upbit API가 초기화되지 않았습니다."}
                
            result = self.upbit.get_order(state=state)
            return result
        except Exception as e:
            logger.error(f"주문 내역 조회 실패: {e}")
            return {"error": str(e)}
    
    def get_ohlcv(self, ticker, interval="day", count=30):
        """OHLCV(시가, 고가, 저가, 종가, 거래량) 데이터 조회"""
        try:
            df = pyupbit.get_ohlcv(ticker, interval=interval, count=count)
            return df
        except Exception as e:
            logger.error(f"OHLCV 데이터 조회 실패: {e}")
            return None
    
    def get_top_volume_tickers(self, limit=10):
        """거래량 기준 상위 코인 조회"""
        try:
            tickers = pyupbit.get_tickers(fiat="KRW")
            volume_data = []
            
            for ticker in tickers[:30]:  # 기본 티커 목록에서 상위 30개만 분석
                time.sleep(0.1)  # API 호출 제한 방지
                current_info = pyupbit.get_current_price(ticker)
                if current_info:
                    ohlcv = pyupbit.get_ohlcv(ticker, interval="day", count=1)
                    if ohlcv is not None and not ohlcv.empty:
                        volume = ohlcv.iloc[0]['volume']
                        volume_data.append({
                            'ticker': ticker,
                            'volume': volume,
                            'price': current_info
                        })
            
            # 거래량 기준 정렬
            volume_data.sort(key=lambda x: x['volume'], reverse=True)
            return volume_data[:limit]
                
        except Exception as e:
            logger.error(f"거래량 상위 코인 조회 실패: {e}")
            return []