import logging
from datetime import datetime, timedelta
from models.user import db
from models.trade import Trade
from service.upbit.upbit_service import UpbitService
from utils.manager_encryption.manager_encryption import EncryptionManager
from utils.manager_trading_algorithm.manager_trading_algorithm import TradingAlgorithmManager

logger = logging.getLogger(__name__)

class TradingService:
    def __init__(self, user=None):
        self.user = user
        self.upbit_service = None
        self.encryption_manager = EncryptionManager()
        self.trading_algorithm_manager = TradingAlgorithmManager()
        
        if user and user.upbit_access_key and user.upbit_secret_key:
            # 암호화된 API 키 복호화
            try:
                access_key = self.encryption_manager.decrypt(user.upbit_access_key)
                secret_key = self.encryption_manager.decrypt(user.upbit_secret_key)
                
                # 업비트 서비스 초기화
                self.upbit_service = UpbitService(access_key, secret_key)
            except Exception as e:
                logger.error(f"업비트 서비스 초기화 실패: {e}")
                self.upbit_service = None
    
    # 거래 실행
    def execute_trade(self, ticker, trade_type, amount=None, price=None, strategy=None):
        try:
            if self.upbit_service is None:
                return {"error": "업비트 서비스가 초기화되지 않았습니다."}
            
            # 현재 시세 조회
            current_price = self.upbit_service.get_ticker_price(ticker)
            if current_price is None:
                return {"error": f"코인 {ticker}의 시세를 조회할 수 없습니다."}
            
            result = None
            total = 0
            estimated_amount = 0
            
            if trade_type == 'buy':
                # 매수
                if amount is None:
                    # 투자 금액이 지정되지 않은 경우 기본 투자 금액으로 설정
                    amount = self.user.investment_amount if self.user else 100000
                
                # 시장가 매수 주문
                result = self.upbit_service.buy_market_order(ticker, amount)
                if isinstance(result, dict) and 'error' in result:
                    return result
                
                # 거래 금액 계산 (예상치)
                estimated_amount = amount / current_price
                total = amount
                
            elif trade_type == 'sell':
                # 매도
                if amount is None:
                    # 수량이 지정되지 않은 경우 전체 보유량 매도
                    amount = self.upbit_service.get_balance(ticker.replace("KRW-", ""))
                    
                # 시장가 매도 주문
                result = self.upbit_service.sell_market_order(ticker, amount)
                if isinstance(result, dict) and 'error' in result:
                    return result
                
                # 거래 금액 계산 (예상치)
                estimated_amount = amount
                total = amount * current_price
            
            # 거래 내역 저장
            trade = Trade(
                user_id=self.user.id if self.user else None,
                ticker=ticker,
                trade_type=trade_type,
                price=current_price,
                amount=estimated_amount,
                total=total,
                fee=total * 0.0005,  # 수수료: 0.05%로 가정
                status='completed',
                order_id=result.get('uuid', '') if isinstance(result, dict) else '',
                strategy=strategy
            )
            
            db.session.add(trade)
            db.session.commit()
            
            logger.info(f"거래 완료: {trade}")
            return {
                "success": True,
                "trade_id": trade.id,
                "order_id": result.get('uuid', '') if isinstance(result, dict) else '',
                "ticker": ticker,
                "price": current_price,
                "amount": estimated_amount,
                "total": total,
                "fee": total * 0.0005
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"거래 실행 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 거래 내역 조회
    def get_trade_history(self, user_id=None, limit=20):
        try:
            if user_id:
                trades = Trade.query.filter_by(user_id=user_id).order_by(Trade.timestamp.desc()).limit(limit).all()
            else:
                trades = Trade.query.order_by(Trade.timestamp.desc()).limit(limit).all()
            
            return trades
        except Exception as e:
            logger.error(f"거래 내역 조회 중 오류 발생: {e}")
            return []
    
    # 자동 매매 실행
    def execute_auto_trading(self):
        try:
            if not self.user:
                return {"error": "사용자 정보가 없습니다."}
                
            if not self.user.auto_trading_enabled:
                return {"error": "자동 매매가 비활성화되어 있습니다."}
            
            if not self.upbit_service:
                return {"error": "업비트 서비스가 초기화되지 않았습니다."}
            
            # 거래할 코인 선택 (기본: 거래량 상위 코인)
            top_tickers = self.upbit_service.get_top_volume_tickers(limit=5)
            if not top_tickers:
                return {"error": "거래할 코인을 찾을 수 없습니다."}
            
            # 사용자가 설정한 전략
            strategy = self.user.strategy
            results = []
            
            for ticker_info in top_tickers:
                ticker = ticker_info['ticker']
                
                # OHLCV 데이터 가져오기
                ohlcv_data = self.upbit_service.get_ohlcv(ticker, interval="day", count=30)
                if ohlcv_data is None or len(ohlcv_data) < 30:
                    logger.warning(f"{ticker}의 OHLCV 데이터를 가져올 수 없습니다.")
                    continue
                    
                # 매매 알고리즘 실행
                signal = self.trading_algorithm_manager.get_signal(strategy, ohlcv_data)
                
                if signal:
                    logger.info(f"{ticker}에 대한 매매 신호 감지: {signal['action']} - {signal['reason']}")
                    
                    # 매수 신호인 경우, 잔고 확인 및 투자 금액 계산
                    if signal['action'] == 'buy':
                        # KRW 잔고 확인
                        krw_balance = self.upbit_service.get_balance("KRW")
                        if isinstance(krw_balance, dict) and 'error' in krw_balance:
                            logger.error(f"KRW 잔고 조회 실패: {krw_balance['error']}")
                            continue
                        
                        # 잔고가 없거나 부족한 경우
                        if not krw_balance or float(krw_balance) < 5000:
                            logger.warning(f"매수 가능한 KRW 잔고가 부족합니다: {krw_balance}")
                            continue
                        
                        # 투자 금액 계산 (KRW 잔고의 10%)
                        investment_amount = float(krw_balance) * 0.1
                        
                        # 최소 투자 금액 적용
                        if investment_amount < 5000:
                            investment_amount = 5000
                            
                        # 최대 투자 금액 제한
                        if investment_amount > 100000:
                            investment_amount = 100000
                    
                    # 매도 신호인 경우, 보유량 확인
                    elif signal['action'] == 'sell':
                        # 해당 코인 보유량 확인
                        coin_currency = ticker.replace("KRW-", "")
                        coin_balance = self.upbit_service.get_balance(coin_currency)
                        
                        if isinstance(coin_balance, dict) and 'error' in coin_balance:
                            logger.error(f"{coin_currency} 보유량 조회 실패: {coin_balance['error']}")
                            continue
                        
                        # 보유량이 없는 경우
                        if not coin_balance or float(coin_balance) <= 0:
                            logger.warning(f"{coin_currency}의 보유량이 없습니다.")
                            continue
                        
                        # 매도 수량은 전체 보유량
                        amount = float(coin_balance)
                    else:
                        # 알 수 없는 액션
                        logger.warning(f"알 수 없는 매매 액션: {signal['action']}")
                        continue
                    
                    # 매매 실행
                    trade_result = self.execute_trade(
                        ticker=ticker,
                        trade_type=signal['action'],
                        amount=investment_amount if signal['action'] == 'buy' else amount,
                        strategy=strategy
                    )
                    
                    # 결과 저장
                    results.append({
                        "ticker": ticker,
                        "action": signal['action'],
                        "reason": signal['reason'],
                        "confidence": signal.get('confidence', 0.5),
                        "result": trade_result
                    })
                    
                    # 매수 거래가 완료되면 다음 코인으로 넘어가지 않고 종료 (자금 관리)
                    if signal['action'] == 'buy' and not isinstance(trade_result, dict) or ('error' not in trade_result):
                        logger.info(f"{ticker} 매수 완료, 더 이상의 매수는 이번 회차에서 진행하지 않습니다.")
                        break
            
            # 거래 내역이 없는 경우
            if not results:
                logger.info("이번 회차에서 실행된 거래가 없습니다.")
                return {
                    "success": True,
                    "message": "이번 회차에서 실행된 거래가 없습니다.",
                    "trades": []
                }
            
            return {
                "success": True,
                "trades": results
            }
            
        except Exception as e:
            logger.error(f"자동 매매 실행 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 손익 계산
    def calculate_profit_loss(self, user_id=None):
        try:
            if user_id is None and self.user:
                user_id = self.user.id
            
            if not user_id:
                return {"error": "사용자 ID가 필요합니다."}
            
            # 거래 내역 조회
            trades = Trade.query.filter_by(user_id=user_id).all()
            
            # 티커별 손익 계산
            profit_by_ticker = {}
            for trade in trades:
                ticker = trade.ticker
                
                if ticker not in profit_by_ticker:
                    profit_by_ticker[ticker] = {
                        "buy_amount": 0,
                        "buy_total": 0,
                        "sell_amount": 0,
                        "sell_total": 0,
                        "current_hold": 0,
                        "profit": 0
                    }
                
                if trade.trade_type == 'buy':
                    profit_by_ticker[ticker]["buy_amount"] += trade.amount
                    profit_by_ticker[ticker]["buy_total"] += trade.total
                    profit_by_ticker[ticker]["current_hold"] += trade.amount
                elif trade.trade_type == 'sell':
                    profit_by_ticker[ticker]["sell_amount"] += trade.amount
                    profit_by_ticker[ticker]["sell_total"] += trade.total
                    profit_by_ticker[ticker]["current_hold"] -= trade.amount
            
            # 현재 시세 조회 및 손익 계산
            total_profit = 0
            for ticker, data in profit_by_ticker.items():
                # 현재 시세 조회
                current_price = self.upbit_service.get_ticker_price(ticker)
                if current_price:
                    # 현재 보유분 평가금액
                    current_value = data["current_hold"] * current_price
                    
                    # 손익 계산
                    data["profit"] = (data["sell_total"] + current_value) - data["buy_total"]
                    total_profit += data["profit"]
            
            return {
                "ticker_profits": profit_by_ticker,
                "total_profit": total_profit
            }
            
        except Exception as e:
            logger.error(f"손익 계산 중 오류 발생: {e}")
            return {"error": str(e)}