import sqlite3
from sqlite3 import Error
import logging
import os

# 로깅 설정
logger = logging.getLogger(__name__)

class DBManager:
    """
    SQLite 데이터베이스 관리를 위한 클래스
    """
    
    def __init__(self, db_path="crypto_trading.db"):
        """
        데이터베이스 관리자 초기화
        
        Args:
            db_path (str): SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """데이터베이스 초기화 및 필요한 테이블 생성"""
        try:
            # 데이터베이스 디렉토리 확인
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                
            conn = self.get_connection()
            if conn:
                cursor = conn.cursor()
                
                # API Key 테이블 생성
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    access_key TEXT NOT NULL,
                    secret_key TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                conn.commit()
                conn.close()
                logger.info("데이터베이스 초기화 완료")
        except Error as e:
            logger.error(f"데이터베이스 초기화 중 오류 발생: {e}")
    
    def get_connection(self):
        """
        데이터베이스 연결 객체 반환
        
        Returns:
            Connection: SQLite 데이터베이스 연결 객체
        """
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except Error as e:
            logger.error(f"데이터베이스 연결 중 오류 발생: {e}")
            return None
    
    def execute_query(self, query, params=None):
        """
        SQL 쿼리 실행 (INSERT, UPDATE, DELETE 등)
        
        Args:
            query (str): 실행할 SQL 쿼리
            params (tuple, optional): 쿼리 파라미터
            
        Returns:
            bool: 성공 여부
        """
        try:
            conn = self.get_connection()
            if not conn:
                return False
                
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            conn.commit()
            conn.close()
            return True
        except Error as e:
            logger.error(f"쿼리 실행 중 오류 발생: {e}\n쿼리: {query}\n파라미터: {params}")
            return False
    
    def execute_select(self, query, params=None):
        """
        SELECT 쿼리 실행 및 결과 반환
        
        Args:
            query (str): 실행할 SELECT 쿼리
            params (tuple, optional): 쿼리 파라미터
            
        Returns:
            list: 쿼리 결과 행 목록
        """
        try:
            conn = self.get_connection()
            if not conn:
                return []
                
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Error as e:
            logger.error(f"SELECT 쿼리 실행 중 오류 발생: {e}\n쿼리: {query}\n파라미터: {params}")
            return []
    
    def execute_select_one(self, query, params=None):
        """
        SELECT 쿼리 실행 및 단일 결과 반환
        
        Args:
            query (str): 실행할 SELECT 쿼리
            params (tuple, optional): 쿼리 파라미터
            
        Returns:
            tuple: 쿼리 결과 행 또는 None
        """
        try:
            conn = self.get_connection()
            if not conn:
                return None
                
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            row = cursor.fetchone()
            conn.close()
            return row
        except Error as e:
            logger.error(f"SELECT 쿼리 실행 중 오류 발생: {e}\n쿼리: {query}\n파라미터: {params}")
            return None
    
    def get_table_columns(self, table_name):
        """
        테이블의 컬럼 정보 조회
        
        Args:
            table_name (str): 테이블 이름
            
        Returns:
            list: 컬럼 이름 목록
        """
        try:
            conn = self.get_connection()
            if not conn:
                return []
                
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            
            columns = [row[1] for row in cursor.fetchall()]
            conn.close()
            return columns
        except Error as e:
            logger.error(f"테이블 컬럼 조회 중 오류 발생: {e}\n테이블: {table_name}")
            return []