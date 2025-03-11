from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    upbit_access_key = db.Column(db.String(100), nullable=False)
    upbit_secret_key = db.Column(db.String(100), nullable=False)
    
    # 자동 매매 설정
    auto_trading_enabled = db.Column(db.Boolean, default=False)
    strategy = db.Column(db.String(50), default='rsi_oversold')  # 기본 전략: RSI 과매도
    investment_amount = db.Column(db.Float, default=100000)      # 기본 10만원
    risk_level = db.Column(db.String(20), default='medium')      # 위험 수준 (low, medium, high)
    
    # 계정 정보
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 비밀번호 설정 및 확인 메소드
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Flask-Login을 위한 메소드
    @property
    def is_authenticated(self):
        return True
        
    @property
    def is_active(self):
        return True
        
    @property
    def is_anonymous(self):
        return False
        
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.email}>'