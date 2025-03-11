from datetime import datetime
from models.user import db

class Trade(db.Model):
    __tablename__ = 'trades'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 거래 정보
    ticker = db.Column(db.String(20), nullable=False)         # 코인 티커 (BTC, ETH 등)
    trade_type = db.Column(db.String(10), nullable=False)     # 매수/매도 (buy, sell)
    price = db.Column(db.Float, nullable=False)               # 거래 가격
    amount = db.Column(db.Float, nullable=False)              # 거래 수량
    total = db.Column(db.Float, nullable=False)               # 총 거래 금액
    fee = db.Column(db.Float, nullable=False, default=0.0)    # 수수료
    
    # 거래 상태
    status = db.Column(db.String(20), nullable=False)         # 상태 (pending, completed, canceled)
    order_id = db.Column(db.String(100), nullable=True)       # 거래소 주문 ID
    
    # 거래 전략
    strategy = db.Column(db.String(50), nullable=True)        # 사용된 전략
    signal_reason = db.Column(db.Text, nullable=True)         # 매매 신호 이유
    
    # 타임스탬프
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    user = db.relationship('User', backref=db.backref('trades', lazy=True))
    
    def __repr__(self):
        return f'<Trade {self.id}: {self.trade_type} {self.amount} {self.ticker} at {self.price}>'
    
    # 총 거래 금액 계산 (수수료 포함)
    def get_total_with_fee(self):
        if self.trade_type == 'buy':
            return self.total + self.fee
        else:
            return self.total - self.fee