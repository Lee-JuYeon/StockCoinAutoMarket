"""
업비트 API 주문 관련 모듈
- 주문 가능 정보
- 개별 주문 조회
- 주문 리스트 조회
- 주문 취소 및 매수/매도 기능
"""
import requests
import logging
from urllib.parse import urlencode, unquote
import hashlib
import uuid
import jwt

from ..utils.validators import validate_order_params, validate_ticker, validate_uuid

logger = logging.getLogger(__name__)

class OrdersModule:
    """
    업비트 API 주문 관련 기능 모듈
    """
    # 주문 모듈 초기화
    def __init__(self, api):
        """
        주문 모듈 초기화
        
        Args:
            api (UpbitAPI): 상위 UpbitAPI 인스턴스
        """
        self.api = api
        self.server_url = api.server_url
    
    # 주문 가능 정보
    def get_order_chance(self, market):
        """
        주문 가능 정보 조회
        
        Args:
            market (str): 마켓 코드 (예: KRW-BTC)
            
        Returns:
            dict: 주문 가능 정보
        """
        try:
            if not validate_ticker(market):
                return {"error": "유효하지 않은 마켓 코드입니다."}
                
            # 쿼리 파라미터 설정
            params = {
                'market': market
            }
            
            # 인증 헤더 생성
            headers = self.api.get_auth_headers(params)
            
            # API 요청
            response = requests.get(f"{self.server_url}/v1/orders/chance", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"주문 가능 정보 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"주문 가능 정보 조회 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 개별 주문 조회
    def get_order(self, uuid_str):
        """
        개별 주문 조회
        
        Args:
            uuid_str (str): 주문 UUID
            
        Returns:
            dict: 주문 정보
        """
        try:
            if not validate_uuid(uuid_str):
                return {"error": "유효하지 않은 UUID입니다."}
                
            # 쿼리 파라미터 설정
            params = {
                'uuid': uuid_str
            }
            
            # 인증 헤더 생성
            headers = self.api.get_auth_headers(params)
            
            # API 요청
            response = requests.get(f"{self.server_url}/v1/order", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"개별 주문 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"개별 주문 조회 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 주문 리스트 조회
    def get_orders(self, states=None, market=None, page=1, limit=100):
        """
        주문 리스트 조회
        
        Args:
            states (list, optional): 주문 상태('wait', 'done', 'cancel'). 기본값은 None으로, 이 경우 wait, done 상태 주문 반환
            market (str, optional): 마켓 코드 (예: KRW-BTC)
            page (int, optional): 페이지 번호
            limit (int, optional): 한 페이지에 가져올 주문 개수 (최대 100)
            
        Returns:
            list: 주문 리스트
        """
        try:
            # 쿼리 파라미터 설정
            params = {}
            
            if states:
                params['states[]'] = states
            
            if market:
                if not validate_ticker(market):
                    return {"error": "유효하지 않은 마켓 코드입니다."}
                params['market'] = market
                
            params['page'] = page
            params['limit'] = limit
            
            # 인증 헤더 생성
            headers = self.api.get_auth_headers(params)
            
            # API 요청
            response = requests.get(f"{self.server_url}/v1/orders", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"주문 리스트 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"주문 리스트 조회 중 오류 발생: {e}")
            return {"error": str(e)} 
    
    # id로 주문리스트 조회
    def get_orders_by_uuids(self, uuids):
        """
        ID로 주문 리스트 조회
        
        Args:
            uuids (list): 주문 UUID 목록
            
        Returns:
            list: 주문 리스트
        """
        try:
            if not uuids or not isinstance(uuids, list):
                return {"error": "유효한 UUID 목록이 필요합니다."}
            
            # 쿼리 파라미터 설정
            params = {
                'uuids[]': uuids
            }
            
            # 인증 헤더 생성
            headers = self.api.get_auth_headers(params)
            
            # API 요청
            response = requests.get(f"{self.server_url}/v1/orders/uuids", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"ID로 주문 리스트 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"ID로 주문 리스트 조회 중 오류 발생: {e}")
            return {"error": str(e)}
        
    # 체결 대기 주문 조회
    def get_open_orders(self, market=None):
        """
        체결 대기 주문 조회
        
        Args:
            market (str, optional): 마켓 코드 (예: KRW-BTC)
            
        Returns:
            list: 체결 대기 주문 리스트
        """
        try:
            # 쿼리 파라미터 설정
            params = {
                'states[]': ['wait', 'watch']
            }
            
            if market:
                if not validate_ticker(market):
                    return {"error": "유효하지 않은 마켓 코드입니다."}
                params['market'] = market
            
            # 인증 헤더 생성
            headers = self.api.get_auth_headers(params)
            
            # API 요청
            response = requests.get(f"{self.server_url}/v1/orders", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"체결 대기 주문 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"체결 대기 주문 조회 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 종료된 주문 조회
    def get_closed_orders(self, market=None, states=['done', 'cancel'], start_time=None, end_time=None, page=1, limit=100):
        """
        종료된 주문 조회
        
        Args:
            market (str, optional): 마켓 코드 (예: KRW-BTC)
            states (list, optional): 주문 상태. 기본값은 ['done', 'cancel']
            start_time (str, optional): 조회 시작 시간 (ISO 8601 형식, 예: '2021-01-01T00:00:00+09:00')
            end_time (str, optional): 조회 종료 시간 (ISO 8601 형식)
            page (int, optional): 페이지 번호
            limit (int, optional): 한 페이지에 가져올 주문 개수 (최대 100)
            
        Returns:
            list: 종료된 주문 리스트
        """
        try:
            # 쿼리 파라미터 설정
            params = {
                'states[]': states,
                'page': page,
                'limit': limit
            }
            
            if market:
                if not validate_ticker(market):
                    return {"error": "유효하지 않은 마켓 코드입니다."}
                params['market'] = market
                
            if start_time:
                params['start_time'] = start_time
                
            if end_time:
                params['end_time'] = end_time
            
            # 인증 헤더 생성
            headers = self.api.get_auth_headers(params)
            
            # API 요청
            response = requests.get(f"{self.server_url}/v1/orders", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"종료된 주문 조회 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"종료된 주문 조회 중 오류 발생: {e}")
            return {"error": str(e)}

    # 주문 취소 접수
    def cancel_order(self, uuid_str):
        """
        주문 취소 접수
        
        Args:
            uuid_str (str): 취소할 주문의 UUID
            
        Returns:
            dict: 취소 결과
        """
        try:
            if not validate_uuid(uuid_str):
                return {"error": "유효하지 않은 UUID입니다."}
                
            # 쿼리 파라미터 설정
            params = {
                'uuid': uuid_str
            }
            
            # 인증 헤더 생성
            headers = self.api.get_auth_headers(params)
            
            # API 요청
            response = requests.delete(f"{self.server_url}/v1/order", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"주문 취소 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"주문 취소 중 오류 발생: {e}")
            return {"error": str(e)}
   
    # 주문 일괄 취소 접수
    def cancel_all_orders(self, excluded_pairs=None, quote_currencies=None):
        """
        주문 일괄 취소 접수
        
        Args:
            excluded_pairs (str, optional): 취소 제외 마켓 (예: 'KRW-BTC,BTC-ETH')
            quote_currencies (str, optional): 특정 화폐 종류의 마켓 전체 취소 (예: 'KRW,BTC')
            
        Returns:
            dict: 취소 결과
        """
        try:
            # 쿼리 파라미터 설정
            params = {}
            
            if excluded_pairs:
                params['excluded_pairs'] = excluded_pairs
                
            if quote_currencies:
                params['quote_currencies'] = quote_currencies
            
            # 인증 헤더 생성
            headers = self.api.get_auth_headers(params)
            
            # API 요청
            response = requests.delete(f"{self.server_url}/v1/orders/open", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"주문 일괄 취소 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"주문 일괄 취소 중 오류 발생: {e}")
            return {"error": str(e)}
            
    # id로 주문 리스트 취소 접수
    def cancel_orders_by_uuids(self, uuids):
        """
        ID로 주문 리스트 취소 접수
        
        Args:
            uuids (list): 취소할 주문의 UUID 목록
            
        Returns:
            dict: 취소 결과
        """
        try:
            if not uuids or not isinstance(uuids, list):
                return {"error": "유효한 UUID 목록이 필요합니다."}
            
            # 쿼리 파라미터 설정
            params = {
                'uuids[]': uuids
            }
            
            # 인증 헤더 생성
            headers = self.api.get_auth_headers(params)
            
            # API 요청
            response = requests.delete(f"{self.server_url}/v1/orders/uuids", params=params, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"ID로 주문 리스트 취소 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"ID로 주문 리스트 취소 중 오류 발생: {e}")
            return {"error": str(e)}
            
    # 주문하기
    def place_order(self, market, side, ord_type, volume=None, price=None):
        """
        주문하기
        
        Args:
            market (str): 마켓 코드 (예: KRW-BTC)
            side (str): 주문 종류 (bid: 매수, ask: 매도)
            ord_type (str): 주문 타입 (limit: 지정가, price: 시장가 매수, market: 시장가 매도)
            volume (str, optional): 주문량 (지정가, 시장가 매도 시 필수)
            price (str, optional): 주문 가격 (지정가, 시장가 매수 시 필수)
            
        Returns:
            dict: 주문 결과
        """
        try:
            # 파라미터 유효성 검사
            if not validate_ticker(market):
                return {"error": "유효하지 않은 마켓 코드입니다."}
                
            is_valid, error_msg = validate_order_params(side, ord_type, volume, price)
            if not is_valid:
                return {"error": error_msg}
                
            # 쿼리 파라미터 설정
            params = {
                'market': market,
                'side': side,
                'ord_type': ord_type
            }
            
            if volume is not None:
                params['volume'] = str(volume)
                
            if price is not None:
                params['price'] = str(price)
            
            # 인증 헤더 생성
            headers = self.api.get_auth_headers(params)
            headers['Content-Type'] = 'application/json'
            
            # API 요청
            response = requests.post(f"{self.server_url}/v1/orders", json=params, headers=headers)
            
            if response.status_code == 201:  # 201: Created
                return response.json()
            else:
                logger.error(f"주문 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"주문 중 오류 발생: {e}")
            return {"error": str(e)}
    
    # 취소 후 재주문
    def cancel_and_new_order(self, prev_order_uuid, new_ord_type, new_price=None, new_volume=None):
        """
        취소 후 재주문
        
        Args:
            prev_order_uuid (str): 기존 주문 UUID
            new_ord_type (str): 주문 타입 (limit: 지정가, price: 시장가 매수, market: 시장가 매도)
            new_price (str, optional): 주문 가격
            new_volume (str, optional): 주문량 ('remain_only'를 전달 시 기존 주문의 잔량으로 재주문)
            
        Returns:
            dict: 주문 결과
        """
        try:
            if not validate_uuid(prev_order_uuid):
                return {"error": "유효하지 않은 UUID입니다."}
                
            # 쿼리 파라미터 설정
            params = {
                'prev_order_uuid': prev_order_uuid,
                'new_ord_type': new_ord_type
            }
            
            if new_price is not None:
                params['new_price'] = str(new_price)
                
            if new_volume is not None:
                params['new_volume'] = str(new_volume)
            
            # 인증 헤더 생성
            headers = self.api.get_auth_headers(params)
            headers['Content-Type'] = 'application/json'
            
            # API 요청
            response = requests.post(f"{self.server_url}/v1/orders/cancel_and_new", json=params, headers=headers)
            
            if response.status_code == 201:  # 201: Created
                return response.json()
            else:
                logger.error(f"취소 후 재주문 실패: {response.text}")
                return {"error": response.text}
        except Exception as e:
            logger.error(f"취소 후 재주문 중 오류 발생: {e}")
            return {"error": str(e)}
        

          # 지정가 매수
   