"""
업비트 API 요청 파라미터 유효성 검사 유틸리티
"""
import logging
import uuid

logger = logging.getLogger(__name__)

def validate_ticker(ticker):
    """
    코인 티커 유효성 검사
    
    Args:
        ticker (str): 검사할 티커 (예: KRW-BTC)
        
    Returns:
        bool: 유효성 여부
    """
    if not ticker:
        return False
    
    # 티커 형식 검사 (기본적인 형식만 검사)
    parts = ticker.split('-')
    if len(parts) != 2:
        return False
    
    market, coin = parts
    if not market or not coin:
        return False
    
    # 마켓 코드 검사
    valid_markets = ['KRW', 'BTC', 'USDT']
    if market not in valid_markets:
        return False
    
    return True

def validate_order_params(side, ord_type, volume=None, price=None):
    """
    주문 파라미터 유효성 검사
    
    Args:
        side (str): 주문 종류 (bid: 매수, ask: 매도)
        ord_type (str): 주문 타입 (limit: 지정가, price: 시장가 매수, market: 시장가 매도)
        volume (str, optional): 주문량
        price (str, optional): 주문 가격
        
    Returns:
        tuple: (유효성 여부, 오류 메시지)
    """
    # side 검사
    if side not in ['bid', 'ask']:
        return False, "주문 종류(side)는 'bid' 또는 'ask'만 가능합니다."
    
    # ord_type 검사
    if ord_type not in ['limit', 'price', 'market']:
        return False, "주문 타입(ord_type)은 'limit', 'price', 'market' 중 하나여야 합니다."
    
    # limit(지정가) 주문인 경우
    if ord_type == 'limit':
        if not price:
            return False, "지정가 주문에는 가격(price)이 필요합니다."
        if not volume:
            return False, "지정가 주문에는 수량(volume)이 필요합니다."
    
    # price(시장가 매수) 주문인 경우
    elif ord_type == 'price':
        if not price:
            return False, "시장가 매수 주문에는 금액(price)이 필요합니다."
        if side != 'bid':
            return False, "시장가 price 주문은 매수(bid)만 가능합니다."
    
    # market(시장가 매도) 주문인 경우
    elif ord_type == 'market':
        if not volume:
            return False, "시장가 매도 주문에는 수량(volume)이 필요합니다."
        if side != 'ask':
            return False, "시장가 market 주문은 매도(ask)만 가능합니다."
    
    return True, ""

def validate_uuid(uuid_str):
    """
    UUID 형식 유효성 검사
    
    Args:
        uuid_str (str): 검사할 UUID 문자열
        
    Returns:
        bool: 유효성 여부
    """
    if not uuid_str:
        return False
    
    try:
        uuid_obj = uuid.UUID(uuid_str)
        return str(uuid_obj) == uuid_str
    except ValueError:
        return False
    except Exception as e:
        logger.error(f"UUID 검증 중 오류 발생: {e}")
        return False