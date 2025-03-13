from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from service.trading.trading_service import TradingService
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
trading_bp = Blueprint('api_trading', __name__, url_prefix='/api/trading')

@trading_bp.route('/execute', methods=['POST'])
@login_required
def execute_trade():
    """
    거래 실행 API
    요청 형식:
    {
        "ticker": "KRW-BTC",
        "trade_type": "buy" or "sell",
        "amount": 10000, (선택사항)
        "strategy": "rsi_oversold" (선택사항)
    }
    """
    try:
        data = request.json
        
        # 필수 파라미터 확인
        if 'ticker' not in data or 'trade_type' not in data:
            return jsonify({"error": "필수 파라미터가 누락되었습니다. (ticker, trade_type)"}), 400
            
        # 거래 실행
        trading_service = TradingService(current_user)
        result = trading_service.execute_trade(
            ticker=data['ticker'],
            trade_type=data['trade_type'],
            amount=data.get('amount'),
            strategy=data.get('strategy')
        )
        
        # 결과 반환
        if 'error' in result:
            return jsonify({"error": result['error']}), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"거래 실행 중 오류 발생: {e}")
        return jsonify({"error": "거래 실행 중 오류가 발생했습니다."}), 500

@trading_bp.route('/history', methods=['GET'])
@login_required
def get_trade_history():
    """거래 내역 조회 API"""
    try:
        # 파라미터 확인
        limit = request.args.get('limit', 20, type=int)
        
        # 거래 내역 조회
        trading_service = TradingService(current_user)
        trades = trading_service.get_trade_history(user_id=current_user.id, limit=limit)
        
        # 결과 변환
        result = []
        for trade in trades:
            result.append({
                "id": trade.id,
                "ticker": trade.ticker,
                "trade_type": trade.trade_type,
                "price": trade.price,
                "amount": trade.amount,
                "total": trade.total,
                "fee": trade.fee,
                "status": trade.status,
                "timestamp": trade.timestamp.isoformat()
            })
        
        return jsonify({"trades": result})
        
    except Exception as e:
        logger.error(f"거래 내역 조회 중 오류 발생: {e}")
        return jsonify({"error": "거래 내역 조회 중 오류가 발생했습니다."}), 500

@trading_bp.route('/auto-trading', methods=['POST'])
@login_required
def toggle_auto_trading():
    """자동 매매 활성화/비활성화 API"""
    try:
        data = request.json
        enabled = data.get('enabled', False)
        
        # 사용자 설정 업데이트
        current_user.auto_trading_enabled = enabled
        db.session.commit()
        
        return jsonify({"message": f"자동 매매가 {'활성화' if enabled else '비활성화'}되었습니다."})
        
    except Exception as e:
        logger.error(f"자동 매매 설정 변경 중 오류 발생: {e}")
        return jsonify({"error": "자동 매매 설정 변경 중 오류가 발생했습니다."}), 500

@trading_bp.route('/auto-trading/execute', methods=['POST'])
@login_required
def execute_auto_trading():
    """자동 매매 수동 실행 API"""
    try:
        # 자동 매매 실행
        trading_service = TradingService(current_user)
        result = trading_service.execute_auto_trading()
        
        # 결과 반환
        if 'error' in result:
            return jsonify({"error": result['error']}), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"자동 매매 실행 중 오류 발생: {e}")
        return jsonify({"error": "자동 매매 실행 중 오류가 발생했습니다."}), 500

@trading_bp.route('/profit-loss', methods=['GET'])
@login_required
def get_profit_loss():
    """손익 계산 API"""
    try:
        # 손익 계산
        trading_service = TradingService(current_user)
        result = trading_service.calculate_profit_loss(user_id=current_user.id)
        
        # 결과 반환
        if 'error' in result:
            return jsonify({"error": result['error']}), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"손익 계산 중 오류 발생: {e}")
        return jsonify({"error": "손익 계산 중 오류가 발생했습니다."}), 500