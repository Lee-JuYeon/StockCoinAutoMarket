import logging
from datetime import datetime, timedelta
from models.user import db
from models.recommendation import Recommendation
from services.upbit_service import UpbitService
from utils.manager_trading_algorithm.manager_trading_algorithm import TradingAlgorithmManager

logger = logging.getLogger(__name__)

class RecommendationService:
    """
    추천 알고리즘을 담당하는 서비스 클래스
    - 코인 추천 생성, 추천 내역 조회 등의 기능 제공
    """
    
    def __init__(self, user=None):
        self.user = user
        self.upbit_service = UpbitService()
        self.trading_algorithm_manager = TradingAlgorithmManager()
    
    def generate_recommendations(self, limit=5):
        """
        사용자에게 맞는 코인 추천 생성
        - 거래량 상위 코인 중에서 매매 신호가 있는 코인을 추천
        """
        try:
            if not self.user:
                return []
            
            # 사용자의 전략 설정
            strategy = self.user.strategy
            risk_level = self.user.risk_level
            
            # 거래량 상위 코인 가져오기
            top_coins = self.upbit_service.get_top_volume_tickers(limit=20)
            
            recommendations = []
            for coin_info in top_coins:
                ticker = coin_info['ticker']
                
                # OHLCV 데이터 가져오기
                ohlcv_data = self.upbit_service.get_ohlcv(ticker, interval="day", count=30)
                if ohlcv_data is None or len(ohlcv_data) < 30:
                    continue
                
                # 매매 신호 확인
                signal = self.trading_algorithm_manager.get_signal(strategy, ohlcv_data)
                
                if signal and signal['action'] == 'buy':
                    # 추천 생성
                    recommendation = Recommendation(
                        user_id=self.user.id,
                        ticker=ticker,
                        recommendation_type='buy',
                        price=coin_info['price'],
                        confidence=signal.get('confidence', 0.5),
                        strategy=strategy,
                        reason=signal['reason'],
                        technical_indicators=signal.get('indicators', {}),
                        status='pending',
                        expiration=datetime.utcnow() + timedelta(hours=24)
                    )
                    
                    db.session.add(recommendation)
                    recommendations.append(recommendation)
                    
                    # 최대 추천 개수 제한
                    if len(recommendations) >= limit:
                        break
            
            db.session.commit()
            return recommendations
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"추천 생성 중 오류 발생: {e}")
            return []
    
    def get_recommendations(self, user_id=None, status='pending', limit=10):
        """추천 내역 조회"""
        try:
            if user_id:
                recommendations = Recommendation.query.filter_by(
                    user_id=user_id,
                    status=status
                ).order_by(Recommendation.timestamp.desc()).limit(limit).all()
            else:
                recommendations = Recommendation.query.filter_by(
                    status=status
                ).order_by(Recommendation.timestamp.desc()).limit(limit).all()
            
            return recommendations
        except Exception as e:
            logger.error(f"추천 내역 조회 중 오류 발생: {e}")
            return []
    
    def update_recommendation_status(self, recommendation_id, status):
        """추천 상태 업데이트"""
        try:
            recommendation = Recommendation.query.get(recommendation_id)
            if not recommendation:
                return False, "추천을 찾을 수 없습니다."
            
            recommendation.status = status
            recommendation.action_timestamp = datetime.utcnow()
            
            db.session.commit()
            return True, f"추천 상태가 '{status}'로 업데이트되었습니다."
        except Exception as e:
            db.session.rollback()
            logger.error(f"추천 상태 업데이트 중 오류 발생: {e}")
            return False, str(e)