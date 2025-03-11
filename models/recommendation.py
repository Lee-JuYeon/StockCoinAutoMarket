from datetime import datetime
from models.user import db

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 추천 정보
    ticker = db.Column(db.String(20), nullable=False)         # 코인 티커 (BTC, ETH 등)
    recommendation_type = db.Column(db.String(10), nullable=False)  # 매수/매도 추천 (buy, sell)
    price = db.Column(db.Float, nullable=False)               # 추천 당시 가격
    confidence = db.Column(db.Float, nullable=False)          # 신뢰도 (0-1)
    
    # 추천 이유
    strategy = db.Column(db.String(50), nullable=False)       # 사용된 전략
    reason = db.Column(db.Text, nullable=False)               # 추천 이유
    technical_indicators = db.Column(db.JSON, nullable=True)  # 기술적 지표 JSON
    
    # 추천 상태
    status = db.Column(db.String(20), default='pending')      # 상태 (pending, accepted, rejected, expired)
    action_timestamp = db.Column(db.DateTime, nullable=True)  # 액션 취한 시간
    
    # 뉴스 연관성
    related_news = db.Column(db.Text, nullable=True)          # 관련 뉴스 (있을 경우)
    news_sentiment = db.Column(db.Float, nullable=True)       # 뉴스 감정 분석 점수 (-1 ~ 1)
    
    # 타임스탬프
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    expiration = db.Column(db.DateTime, nullable=True)        # 만료 시간
    
    # 관계 설정
    user = db.relationship('User', backref=db.backref('recommendations', lazy=True))
    
    def __repr__(self):
        return f'<Recommendation {self.id}: {self.recommendation_type} {self.ticker} at {self.price}>'
    
    # 추천이 유효한지 확인
    def is_valid(self):
        if self.status != 'pending':
            return False
            
        if self.expiration and datetime.utcnow() > self.expiration:
            self.status = 'expired'
            db.session.commit()
            return False
            
        return True