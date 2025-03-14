# StockCoinAutoMarket

crypto_trading_web/
│
├── app.py                      # 메인 Flask 애플리케이션
├── config.py                   # 설정 파일 (API 키, 데이터베이스 설정 등)
├── requirements.txt            # 필요한 패키지 목록
│
├── static/                     # 정적 파일
│   ├── css/                    # CSS 스타일시트
│   ├── js/                     # JavaScript 파일
│   └── img/                    # 이미지 파일
│
├── templates/                  # HTML 템플릿
│   ├── index.html              # 메인 페이지
│   ├── dashboard.html          # 대시보드
│   ├── settings.html           # 설정 페이지
│   ├── history.html            # 거래 내역 페이지
│   └── strategy.html           # 매매 전략 설정 페이지 (추가)
│
├── models/                     # 데이터베이스 모델
│   ├── user.py                 # 사용자 모델
│   ├── trade.py                # 거래 모델
│   └── recommendation.py       # 추천 모델
│
├── services/                   # 비즈니스 로직
│   ├── upbit_service.py        # 업비트 API 연동
│   ├── trading_service.py      # 매매 로직
│   ├── recommendation_service.py # 추천 알고리즘
│   ├── chart_service.py        # 차트 데이터 처리
│   ├── news_service.py         # 뉴스 분석 서비스
│   └── alert_service.py        # 알림 서비스 (추가)
│
├── utils/                      # 유틸리티 함수
│   ├── indicators.py           # 기술적 지표 계산 (RSI 등)
│   ├── auth.py                 # 인증 관련 기능
│   ├── database.py             # 데이터베이스 연결 관리
│   ├── manager_encryption/     # 암호화 관리 (기존)
│   │   └── manager_encryption.py
│   ├── manager_db/             # DB 관리 (기존)
│   │   └── manager_db.py
│   ├── manager_trading_algorithm/ # 매매 알고리즘 관리 (기존)
│   │   └── manager_trading_algorithm.py
│   └── upbit_api/
│       │
│       ├── __init__.py               # 패키지 초기화 및 싱글톤 인스턴스 관리
│       ├── upbit_api.py              # 메인 싱글톤 클래스, 각 모듈 통합
│       ├── modules/                  # 기능별 모듈 디렉토리
│       │   ├── __init__.py           # 모듈 패키지 초기화
│       │   ├── accounts.py           # 자산/계좌 관련 모듈
│       │   ├── orders.py             # 주문 관련 모듈
│       │   ├── deposits.py           # 입금 관련 모듈
│       │   ├── withdrawals.py        # 출금 관련 모듈
│       │   └── service_info.py       # 서비스 정보 관련 모듈
│       └── utils/                    # 유틸리티 함수
│           ├── __init__.py
│           ├── auth.py               # 인증 관련 유틸리티
│           └── validators.py         # 데이터 유효성 검사 유틸리티
└── routes/                     # API 라우트
    ├── ui/                     # UI 관련 라우트
    │   ├── routes_auth.py      # 인증 라우트
    │   └── routes_dashboard.py # 대시보드 라우트 (추가)
    ├── api/                    # API 관련 라우트 (추가)
    │   ├── routes_upbit.py     # 업비트 API 라우트 (추가)
    │   └── routes_trading.py   # 거래 API 라우트 (추가)
    └── settings/               # 설정 관련 라우트
        ├── routes_apikey.py    # API 키 라우트
        └── routes_settings.py  # 설정 라우트