import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class TradingAlgorithmManager:
    """
    매매 알고리즘을 관리하는 싱글톤 클래스
    다양한 매매 전략과 기술적 지표 계산을 모두 포함합니다.
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """싱글톤 패턴 구현"""
        if cls._instance is None:
            cls._instance = super(TradingAlgorithmManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """매매 알고리즘 관리자 초기화"""
        if self._initialized:
            return
            
        # 사용 가능한 전략 목록
        self.available_strategies = [
            'rsi_oversold',
            'macd_crossover',
            'bollinger_bands',
            'swing_trading',
            'trend_following',
            'average_price',
            'momentum_trading',
            'scalping'
        ]
        
        # 전략별 기본 파라미터
        self.default_parameters = {
            'rsi_oversold': {
                'period': 14,
                'oversold_threshold': 30,
                'overbought_threshold': 70
            },
            'macd_crossover': {
                'fast_period': 12,
                'slow_period': 26,
                'signal_period': 9
            },
            'bollinger_bands': {
                'window': 20,
                'num_std': 2
            },
            'swing_trading': {
                'short_period': 3,
                'long_period': 5
            },
            'trend_following': {
                'moving_average_period': 20
            },
            'average_price': {
                'period': 24
            },
            'momentum_trading': {
                'period': 10,
                'threshold': 0.5
            },
            'scalping': {
                'profit_margin': 0.02
            }
        }
        
        self._initialized = True
    
    def get_signal(self, strategy, ohlcv_data, parameters=None):
        """
        지정한 전략에 따라 매매 신호를 생성합니다.
        
        Args:
            strategy (str): 사용할 전략 이름
            ohlcv_data (pandas.DataFrame): OHLCV 데이터
            parameters (dict, optional): 전략별 파라미터 (없으면 기본값 사용)
            
        Returns:
            dict: 매매 신호 정보 (action, reason, confidence)
        """
        if strategy not in self.available_strategies:
            logger.warning(f"지원하지 않는 전략입니다: {strategy}")
            return None
            
        # 파라미터 설정
        params = self.default_parameters[strategy].copy()
        if parameters:
            params.update(parameters)
            
        # 전략별 매매 신호 생성
        if strategy == 'rsi_oversold':
            return self._rsi_strategy(ohlcv_data, params)
        elif strategy == 'macd_crossover':
            return self._macd_strategy(ohlcv_data, params)
        elif strategy == 'bollinger_bands':
            return self._bollinger_bands_strategy(ohlcv_data, params)
        elif strategy == 'swing_trading':
            return self._swing_trading_strategy(ohlcv_data, params)
        elif strategy == 'trend_following':
            return self._trend_following_strategy(ohlcv_data, params)
        elif strategy == 'average_price':
            return self._average_price_strategy(ohlcv_data, params)
        elif strategy == 'momentum_trading':
            return self._momentum_strategy(ohlcv_data, params)
        elif strategy == 'scalping':
            return self._scalping_strategy(ohlcv_data, params)
        
        return None
    
    # ------ 기술적 지표 계산 함수들 ------
    
    def calculate_rsi(self, prices, period=14):
        """
        상대강도지수(RSI) 계산
        
        Args:
            prices (pandas.Series): 가격 데이터 시리즈
            period (int): RSI 계산 기간
            
        Returns:
            float: 최근 RSI 값
        """
        try:
            delta = prices.diff()
            delta = delta[1:]  # 첫 번째 NaN 제거
            
            # 상승/하락 구분
            gain = delta.copy()
            loss = delta.copy()
            gain[gain < 0] = 0
            loss[loss > 0] = 0
            loss = abs(loss)
            
            # 평균 상승/하락 계산
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            # 상대강도(RS) 계산
            rs = avg_gain / avg_loss
            
            # RSI 계산
            rsi = 100 - (100 / (1 + rs))
            
            # 마지막 값 반환
            return rsi.iloc[-1]
        except Exception as e:
            logger.error(f"RSI 계산 중 오류 발생: {e}")
            return 50  # 오류 발생 시 중립값 반환
    
    def calculate_macd(self, prices, fast_period=12, slow_period=26, signal_period=9):
        """
        이동평균수렴발산(MACD) 계산
        
        Args:
            prices (pandas.Series): 가격 데이터 시리즈
            fast_period (int): 단기 이동평균 기간
            slow_period (int): 장기 이동평균 기간
            signal_period (int): 시그널 라인 기간
            
        Returns:
            tuple: (MACD 라인, 시그널 라인, MACD 히스토그램)
        """
        try:
            # 단기 지수이동평균 (EMA)
            ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
            
            # 장기 지수이동평균 (EMA)
            ema_slow = prices.ewm(span=slow_period, adjust=False).mean()
            
            # MACD 라인 = 단기 EMA - 장기 EMA
            macd_line = ema_fast - ema_slow
            
            # 시그널 라인 = MACD의 9일 EMA
            signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
            
            # MACD 히스토그램 = MACD 라인 - 시그널 라인
            macd_histogram = macd_line - signal_line
            
            return macd_line.values, signal_line.values, macd_histogram.values
        except Exception as e:
            logger.error(f"MACD 계산 중 오류 발생: {e}")
            return np.zeros(len(prices)), np.zeros(len(prices)), np.zeros(len(prices))
    
