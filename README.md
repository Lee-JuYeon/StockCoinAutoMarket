# StockCoinAutoMarket

# 프로젝트 구조
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
│   └── history.html            # 거래 내역 페이지
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
│   └── news_service.py         # 뉴스 분석 서비스
│
└── utils/                      # 유틸리티 함수
    ├── indicators.py           # 기술적 지표 계산 (RSI 등)
    ├── auth.py                 # 인증 관련 기능
    └── database.py             # 데이터베이스 연결 관리