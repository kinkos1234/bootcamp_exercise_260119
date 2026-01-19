# PRD: HR & Marketing Analytics Dashboard

## 1. 개요 (Overview)

### 1.1 목적
사내 **인사(HR)** 및 **마케팅** 현황을 통합 모니터링하는 Streamlit 기반 웹 대시보드를 구축한다.

### 1.2 배경
- HR 데이터(1,472건)와 마케팅 캠페인 데이터(200,002건)를 시각화하여 의사결정 지원
- 퇴사율, ROI 등 핵심 지표를 실시간으로 파악

### 1.3 대상 사용자
| 역할 | 주요 관심사 |
|------|-------------|
| 경영진 | 전사 KPI 요약, 트렌드 파악 |
| HR팀 | 퇴사율, 부서별 인력 현황, 급여 분포 |
| 마케팅팀 | 채널별 ROI, 전환율, 예산 효율성 |

---

## 2. 시스템 구조 (Architecture)

### 2.1 레이아웃 구성

```
┌─────────────────────────────────────────────────────────────┐
│                        Header                               │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│   Sidebar    │              Main Content                    │
│   - Logo     │   ┌────────────┬────────────┐                │
│   - Filters  │   │  HR Tab    │ Marketing  │                │
│              │   │            │    Tab     │                │
│              │   └────────────┴────────────┘                │
│              │                                              │
│              │   [ KPI Cards ]                              │
│              │   [ Charts Area ]                            │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

### 2.2 사이드바 (Sidebar)
| 요소 | 설명 |
|------|------|
| 로고 | 대시보드 브랜딩 이미지/텍스트 |
| 부서 필터 | HR 탭: Department 선택 (Sales, R&D 등) |
| 채널 필터 | Marketing 탭: Channel_Used 선택 |
| 기간 필터 | Marketing 탭: Date 범위 선택 |

### 2.3 메인 영역
- **2개 탭**: HR / Marketing
- 각 탭은 KPI 카드 영역 + 차트 영역으로 구성

### 2.4 데이터 흐름

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  CSV Files  │────▶│   Pandas    │────▶│  Streamlit  │
│  (hr, mkt)  │     │  DataFrame  │     │     App     │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   Plotly    │
                                        │   Charts    │
                                        └─────────────┘
```

---

## 3. HR 탭 기능 명세

### 3.1 데이터 소스
- **파일**: `data/hr_data.csv`
- **행 수**: 1,472건
- **주요 컬럼**:

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| Attrition | String | 퇴사 여부 (Yes/No) |
| Department | String | 부서명 |
| MonthlyIncome | Integer | 월 급여 |
| Age | Integer | 나이 |
| JobRole | String | 직무 |
| JobSatisfaction | Integer | 직무 만족도 (1-4) |

### 3.2 KPI 카드: 퇴사율
| 항목 | 내용 |
|------|------|
| 지표명 | 전체 퇴사율 (Attrition Rate) |
| 계산식 | `(Attrition == 'Yes' 인원) / (전체 인원) × 100` |
| 표시 형식 | 퍼센트 (예: 16.1%) |
| 차트 유형 | `st.metric()` |

### 3.3 부서별 현황 (Bar Chart)
| 항목 | 내용 |
|------|------|
| X축 | Department |
| Y축 | 인원 수 (Count) |
| 색상 구분 | Attrition (Yes: 빨강, No: 파랑) |
| 차트 유형 | Stacked Bar Chart |
| 라이브러리 | `plotly.express.bar()` |

### 3.4 소득 관계 (Box Plot)
| 항목 | 내용 |
|------|------|
| X축 | Department |
| Y축 | MonthlyIncome |
| 차트 유형 | Box Plot |
| 목적 | 부서별 급여 분포 및 이상치 파악 |
| 라이브러리 | `plotly.express.box()` |

---

## 4. Marketing 탭 기능 명세

### 4.1 데이터 소스
- **파일**: `data/marketing_data.csv`
- **행 수**: 200,002건
- **주요 컬럼**:

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| Channel_Used | String | 마케팅 채널 (Google Ads, YouTube 등) |
| Conversion_Rate | Float | 전환율 (0~1) |
| ROI | Float | 투자 대비 수익률 |
| Acquisition_Cost | String | 고객 획득 비용 ($금액 형식) |
| Date | Date | 캠페인 날짜 |
| Campaign_Type | String | 캠페인 유형 |

### 4.2 KPI 카드: 평균 ROI
| 항목 | 내용 |
|------|------|
| 지표명 | 평균 ROI |
| 계산식 | `ROI.mean()` |
| 표시 형식 | 소수점 2자리 (예: 5.23) |
| 차트 유형 | `st.metric()` |

### 4.3 채널별 전환율 (Bar Chart)
| 항목 | 내용 |
|------|------|
| X축 | Channel_Used |
| Y축 | 평균 Conversion_Rate |
| 차트 유형 | Bar Chart |
| 라이브러리 | `plotly.express.bar()` |

### 4.4 예산 효율성 (Scatter Plot)
| 항목 | 내용 |
|------|------|
| X축 | Acquisition_Cost (숫자 변환 필요) |
| Y축 | ROI |
| 색상 구분 | Channel_Used |
| 차트 유형 | Scatter Plot |
| 목적 | 비용 대비 ROI 관계 분석 |
| 라이브러리 | `plotly.express.scatter()` |

**데이터 전처리 필요사항**:
- `Acquisition_Cost`: `"$16,174.00"` → `16174.00` (문자열에서 숫자로 변환)

---

## 5. 기술 스택

### 5.1 핵심 기술
| 기술 | 버전 | 용도 |
|------|------|------|
| Python | 3.10+ | 백엔드 언어 |
| Streamlit | 1.28+ | 웹 프레임워크 |
| Plotly Express | 5.18+ | 인터랙티브 차트 |
| Pandas | 2.0+ | 데이터 처리 |

### 5.2 의존성 (requirements.txt)
```
streamlit>=1.28.0
plotly>=5.18.0
pandas>=2.0.0
```

---

## 6. 파일 구조

```
260119/
├── data/
│   ├── hr_data.csv          # HR 원본 데이터
│   └── marketing_data.csv   # 마케팅 원본 데이터
├── app.py                   # Streamlit 메인 앱
├── PRD.md                   # 본 문서
└── requirements.txt         # Python 의존성
```

---

## 7. UI/UX 가이드라인

### 7.1 색상 팔레트
| 용도 | 색상 코드 |
|------|-----------|
| Primary | #1f77b4 (파랑) |
| Secondary | #ff7f0e (주황) |
| Success | #2ca02c (초록) |
| Danger | #d62728 (빨강) |

### 7.2 반응형 레이아웃
- `st.columns()`를 활용한 반응형 그리드
- KPI 카드: 3열 배치
- 차트: 전체 너비 또는 2열 배치

---

## 8. 향후 확장 고려사항

1. **데이터 연동**: CSV → 실시간 DB 연동
2. **인증**: 사용자 로그인/권한 관리
3. **알림**: 임계값 초과 시 알림 기능
4. **내보내기**: PDF/Excel 리포트 다운로드
