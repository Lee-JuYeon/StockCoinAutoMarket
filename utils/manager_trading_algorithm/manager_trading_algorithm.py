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
    
    def calculate_bollinger_bands(self, prices, window=20, num_std=2):
        """
        볼린저 밴드 계산
        
        Args:
            prices (pandas.Series): 가격 데이터 시리즈
            window (int): 이동평균 기간
            num_std (int): 표준편차 승수
            
        Returns:
            tuple: (중간 밴드(SMA), 상단 밴드, 하단 밴드)
        """
        try:
            # 중간 밴드 (단순 이동평균)
            middle_band = prices.rolling(window=window).mean()
            
            # 표준편차
            std = prices.rolling(window=window).std()
            
            # 상단 밴드 = 중간 밴드 + (표준편차 * num_std)
            upper_band = middle_band + (std * num_std)
            
            # 하단 밴드 = 중간 밴드 - (표준편차 * num_std)
            lower_band = middle_band - (std * num_std)
            
            return middle_band, upper_band, lower_band
        except Exception as e:
            logger.error(f"볼린저 밴드 계산 중 오류 발생: {e}")
            return prices, prices, prices
    
    # ------ 전략 구현 함수들 ------
    
    def _rsi_strategy(self, ohlcv_data, params):
        """RSI 기반 매매 전략"""
        try:
            close_prices = ohlcv_data['close']
            
            # RSI 계산
            rsi = self.calculate_rsi(close_prices, period=params['period'])
            
            # 신호 생성
            if rsi <= params['oversold_threshold']:
                return {
                    'action': 'buy',
                    'reason': f"RSI({rsi:.2f})가 과매도 상태입니다",
                    'confidence': 0.7,
                    'indicators': {'rsi': float(rsi)}
                }
            elif rsi >= params['overbought_threshold']:
                return {
                    'action': 'sell',
                    'reason': f"RSI({rsi:.2f})가 과매수 상태입니다",
                    'confidence': 0.7,
                    'indicators': {'rsi': float(rsi)}
                }
                
            return None
        except Exception as e:
            logger.error(f"RSI 전략 실행 중 오류 발생: {e}")
            return None
    
    def _macd_strategy(self, ohlcv_data, params):
        """MACD 기반 매매 전략"""
        try:
            close_prices = ohlcv_data['close']
            
            # MACD 계산
            macd, signal, hist = self.calculate_macd(
                close_prices, 
                fast_period=params['fast_period'],
                slow_period=params['slow_period'],
                signal_period=params['signal_period']
            )
            
            # 골든 크로스 (MACD가 시그널 라인을 상향 돌파)
            if macd[-2] < signal[-2] and macd[-1] > signal[-1]:
                return {
                    'action': 'buy',
                    'reason': "MACD가 시그널 라인을 상향 돌파했습니다 (골든 크로스)",
                    'confidence': 0.6,
                    'indicators': {
                        'macd': float(macd[-1]),
                        'signal': float(signal[-1]),
                        'histogram': float(hist[-1])
                    }
                }
            
            # 데드 크로스 (MACD가 시그널 라인을 하향 돌파)
            elif macd[-2] > signal[-2] and macd[-1] < signal[-1]:
                return {
                    'action': 'sell',
                    'reason': "MACD가 시그널 라인을 하향 돌파했습니다 (데드 크로스)",
                    'confidence': 0.6,
                    'indicators': {
                        'macd': float(macd[-1]),
                        'signal': float(signal[-1]),
                        'histogram': float(hist[-1])
                    }
                }
                
            return None
        except Exception as e:
            logger.error(f"MACD 전략 실행 중 오류 발생: {e}")
            return None
    
    def _bollinger_bands_strategy(self, ohlcv_data, params):
        """볼린저 밴드 기반 매매 전략"""
        try:
            close_prices = ohlcv_data['close']
            
            # 볼린저 밴드 계산
            middle_band, upper_band, lower_band = self.calculate_bollinger_bands(
                close_prices,
                window=params['window'],
                num_std=params['num_std']
            )
            
            last_price = close_prices.iloc[-1]
            
            # 가격이 하단 밴드 아래로 내려갔을 때 매수
            if last_price <= lower_band.iloc[-1]:
                return {
                    'action': 'buy',
                    'reason': "가격이 볼린저 밴드 하단에 도달했습니다",
                    'confidence': 0.6,
                    'indicators': {
                        'price': float(last_price),
                        'lower_band': float(lower_band.iloc[-1]),
                        'middle_band': float(middle_band.iloc[-1]),
                        'upper_band': float(upper_band.iloc[-1])
                    }
                }
            
            # 가격이 상단 밴드 위로 올라갔을 때 매도
            elif last_price >= upper_band.iloc[-1]:
                return {
                    'action': 'sell',
                    'reason': "가격이 볼린저 밴드 상단에 도달했습니다",
                    'confidence': 0.6,
                    'indicators': {
                        'price': float(last_price),
                        'lower_band': float(lower_band.iloc[-1]),
                        'middle_band': float(middle_band.iloc[-1]),
                        'upper_band': float(upper_band.iloc[-1])
                    }
                }
                
            return None
        except Exception as e:
            logger.error(f"볼린저 밴드 전략 실행 중 오류 발생: {e}")
            return None
    
    def _swing_trading_strategy(self, ohlcv_data, params):
        """스윙 트레이딩 전략"""
        try:
            close_prices = ohlcv_data['close']
            
            # 단기 이동평균선
            short_ma = close_prices.rolling(window=params['short_period']).mean()
            
            # 장기 이동평균선
            long_ma = close_prices.rolling(window=params['long_period']).mean()
            
            # 골든 크로스 (단기 이동평균선이 장기 이동평균선을 상향 돌파)
            if short_ma.iloc[-2] < long_ma.iloc[-2] and short_ma.iloc[-1] > long_ma.iloc[-1]:
                return {
                    'action': 'buy',
                    'reason': "단기 이동평균선이 장기 이동평균선을 상향 돌파했습니다 (골든 크로스)",
                    'confidence': 0.6,
                    'indicators': {
                        'short_ma': float(short_ma.iloc[-1]),
                        'long_ma': float(long_ma.iloc[-1])
                    }
                }
            
            # 데드 크로스 (단기 이동평균선이 장기 이동평균선을 하향 돌파)
            elif short_ma.iloc[-2] > long_ma.iloc[-2] and short_ma.iloc[-1] < long_ma.iloc[-1]:
                return {
                    'action': 'sell',
                    'reason': "단기 이동평균선이 장기 이동평균선을 하향 돌파했습니다 (데드 크로스)",
                    'confidence': 0.6,
                    'indicators': {
                        'short_ma': float(short_ma.iloc[-1]),
                        'long_ma': float(long_ma.iloc[-1])
                    }
                }
                
            return None
        except Exception as e:
            logger.error(f"스윙 트레이딩 전략 실행 중 오류 발생: {e}")
            return None
    
    def _trend_following_strategy(self, ohlcv_data, params):
        """추세 추종 전략"""
        try:
            close_prices = ohlcv_data['close']
            
            # 이동 평균
            ma = close_prices.rolling(window=params['moving_average_period']).mean()
            
            last_price = close_prices.iloc[-1]
            
            # 가격이 이동평균선보다 높을 때 매수 (상승 추세)
            if last_price > ma.iloc[-1] and close_prices.iloc[-2] <= ma.iloc[-2]:
                return {
                    'action': 'buy',
                    'reason': "가격이 이동평균선을 상향 돌파했습니다 (상승 추세)",
                    'confidence': 0.6,
                    'indicators': {
                        'price': float(last_price),
                        'moving_average': float(ma.iloc[-1])
                    }
                }
            
            # 가격이 이동평균선보다 낮을 때 매도 (하락 추세)
            elif last_price < ma.iloc[-1] and close_prices.iloc[-2] >= ma.iloc[-2]:
                return {
                    'action': 'sell',
                    'reason': "가격이 이동평균선을 하향 돌파했습니다 (하락 추세)",
                    'confidence': 0.6,
                    'indicators': {
                        'price': float(last_price),
                        'moving_average': float(ma.iloc[-1])
                    }
                }
                
            return None
        except Exception as e:
            logger.error(f"추세 추종 전략 실행 중 오류 발생: {e}")
            return None
    
    def _average_price_strategy(self, ohlcv_data, params):
        """평균 가격 매매 전략"""
        try:
            close_prices = ohlcv_data['close']
            
            # 기간 동안의 평균 가격 계산
            period = min(params['period'], len(close_prices))
            avg_price = close_prices.iloc[-period:].mean()
            
            last_price = close_prices.iloc[-1]
            
            # 현재 가격이 평균 가격보다 낮을 때 매수
            if last_price < avg_price:
                return {
                    'action': 'buy',
                    'reason': f"현재 가격({last_price:.2f})이 평균 가격({avg_price:.2f})보다 낮습니다",
                    'confidence': 0.5,
                    'indicators': {
                        'price': float(last_price),
                        'average_price': float(avg_price)
                    }
                }
            
            # 현재 가격이 평균 가격보다 높을 때 매도
            elif last_price > avg_price * 1.05:  # 5% 이상 높을 때
                return {
                    'action': 'sell',
                    'reason': f"현재 가격({last_price:.2f})이 평균 가격({avg_price:.2f})보다 5% 이상 높습니다",
                    'confidence': 0.5,
                    'indicators': {
                        'price': float(last_price),
                        'average_price': float(avg_price)
                    }
                }
                
            return None
        except Exception as e:
            logger.error(f"평균 가격 전략 실행 중 오류 발생: {e}")
            return None
    
    def _momentum_strategy(self, ohlcv_data, params):
        """모멘텀 매매 전략"""
        try:
            close_prices = ohlcv_data['close']
            
            # 가격 변화율 계산
            price_change = (close_prices.iloc[-1] - close_prices.iloc[-params['period']]) / close_prices.iloc[-params['period']]
            
            # 상승 모멘텀일 때 매수
            if price_change > params['threshold']:
                return {
                    'action': 'buy',
                    'reason': f"가격이 최근 {params['period']}일 동안 {price_change*100:.2f}% 상승했습니다",
                    'confidence': 0.6,
                    'indicators': {
                        'price_change': float(price_change)
                    }
                }
            
            # 하락 모멘텀일 때 매도
            elif price_change < -params['threshold']:
                return {
                    'action': 'sell',
                    'reason': f"가격이 최근 {params['period']}일 동안 {abs(price_change)*100:.2f}% 하락했습니다",
                    'confidence': 0.6,
                    'indicators': {
                        'price_change': float(price_change)
                    }
                }
                
            return None
        except Exception as e:
            logger.error(f"모멘텀 전략 실행 중 오류 발생: {e}")
            return None
    
    def _scalping_strategy(self, ohlcv_data, params):
        """스캘핑 전략"""
        try:
            close_prices = ohlcv_data['close']
            
            # 최근 가격 변화율 계산 (1분 봉 기준)
            price_change = (close_prices.iloc[-1] - close_prices.iloc[-2]) / close_prices.iloc[-2]
            
            # 급등 시 매수
            if price_change > params['profit_margin']:
                return {
                    'action': 'buy',
                    'reason': f"가격이 급등했습니다 ({price_change*100:.2f}%)",
                    'confidence': 0.4,
                    'indicators': {
                        'price_change': float(price_change)
                    }
                }
            
            # 소폭 상승 후 매도
            elif 0 < price_change < params['profit_margin']:
                return {
                    'action': 'sell',
                    'reason': f"수익 실현 구간입니다 ({price_change*100:.2f}%)",
                    'confidence': 0.4,
                    'indicators': {
                        'price_change': float(price_change)
                    }
                }
                
            return None
        except Exception as e:
            logger.error(f"스캘핑 전략 실행 중 오류 발생: {e}")
            return None