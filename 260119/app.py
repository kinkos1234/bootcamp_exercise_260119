"""
HR & Marketing Analytics Dashboard
사내 인사 및 마케팅 현황 통합 모니터링
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# 현재 스크립트 디렉토리 기준 절대 경로 설정
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# ============================================================
# 페이지 설정
# ============================================================
st.set_page_config(
    page_title="HR & Marketing Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 데이터 로드 및 전처리
# ============================================================
@st.cache_data
def load_hr_data():
    """HR 데이터 로드 및 전처리"""
    df = pd.read_csv(DATA_DIR / "hr_data.csv")
    
    # Attrition을 숫자로 변환 (Yes=1, No=0)
    df['Attrition_Num'] = df['Attrition'].apply(lambda x: 1 if x == 'Yes' else 0)
    
    return df


@st.cache_data
def load_marketing_data():
    """마케팅 데이터 로드 및 전처리"""
    df = pd.read_csv(DATA_DIR / "marketing_data.csv")
    
    # Acquisition_Cost: "$16,174.00" → 16174.00 (숫자 변환)
    df['Acquisition_Cost_Num'] = (
        df['Acquisition_Cost']
        .str.replace('$', '', regex=False)
        .str.replace(',', '', regex=False)
        .astype(float)
    )
    
    # Date를 datetime으로 변환
    df['Date'] = pd.to_datetime(df['Date'])
    
    return df


# 데이터 로드
hr_df = load_hr_data()
mkt_df = load_marketing_data()

# ============================================================
# 사이드바
# ============================================================
with st.sidebar:
    st.title("📊 Dashboard")
    st.markdown("---")
    
    # 탭 선택에 따른 필터 표시를 위한 변수
    st.subheader("🔍 필터")

# ============================================================
# 메인 영역: 탭 구성
# ============================================================
tab_hr, tab_mkt = st.tabs(["👥 HR", "📈 Marketing"])

# ============================================================
# HR 탭
# ============================================================
with tab_hr:
    st.header("인사(HR) 현황 분석")
    
    # 사이드바 필터: 부서 선택
    with st.sidebar:
        st.markdown("### HR 필터")
        departments = ["전체"] + sorted(hr_df['Department'].unique().tolist())
        selected_dept = st.selectbox("부서 선택", departments, key="hr_dept")
    
    # 필터 적용
    if selected_dept == "전체":
        hr_filtered = hr_df.copy()
    else:
        hr_filtered = hr_df[hr_df['Department'] == selected_dept]
    
    # 필터 적용 결과 표시
    st.caption(f"📋 조회 결과: {len(hr_filtered):,}명 / 전체 {len(hr_df):,}명")
    
    # ----- KPI 카드 -----
    st.subheader("📌 핵심 지표")
    
    total_emp = len(hr_filtered)
    attrition_count = int(hr_filtered['Attrition_Num'].sum())
    attrition_rate = (attrition_count / total_emp * 100) if total_emp > 0 else 0
    avg_income = hr_filtered['MonthlyIncome'].mean()
    
    # 전체 퇴사율 대비 delta 계산
    total_attrition_rate = (hr_df['Attrition_Num'].sum() / len(hr_df) * 100)
    delta_rate = attrition_rate - total_attrition_rate
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("전체 직원 수", f"{total_emp:,}명")
    col2.metric("퇴사자 수", f"{attrition_count}명")
    col3.metric("퇴사율", f"{attrition_rate:.1f}%", f"{delta_rate:+.1f}%p vs 전체")
    col4.metric("평균 월급", f"${avg_income:,.0f}")
    
    st.markdown("---")
    
    # ----- 차트 영역 -----
    col_chart1, col_chart2 = st.columns(2)
    
    # 부서별 현황 (Grouped Bar Chart)
    with col_chart1:
        dept_df = hr_filtered.groupby(['Department', 'Attrition']).size().reset_index(name='Count')
        fig = px.bar(
            dept_df,
            x='Department', y='Count',
            color='Attrition', barmode='group',
            title='부서별 퇴사 현황 비교',
            color_discrete_map={'Yes': '#EF553B', 'No': '#636EFA'},
            labels={'Department': '부서', 'Count': '인원 수', 'Attrition': '퇴사 여부'}
        )
        fig.update_traces(hovertemplate='부서: %{x}<br>인원 수: %{y}명<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)
    
    # 소득 관계 (Box Plot)
    with col_chart2:
        st.subheader("💰 부서별 소득 분포")
        
        fig_box = px.box(
            hr_filtered,
            x='Department',
            y='MonthlyIncome',
            color='Department',
            labels={'MonthlyIncome': '월 소득 ($)', 'Department': '부서'}
        )
        fig_box.update_layout(showlegend=False)
        fig_box.update_traces(hovertemplate='부서: %{x}<br>월 소득: $%{y:,.2f}<extra></extra>')
        st.plotly_chart(fig_box, use_container_width=True)

# ============================================================
# Marketing 탭
# ============================================================
with tab_mkt:
    st.header("마케팅 현황 분석")
    
    # 사이드바 필터
    with st.sidebar:
        st.markdown("### Marketing 필터")
        
        # 채널 선택 (multiselect)
        channels = st.sidebar.multiselect(
            "Select Channel",
            mkt_df['Channel_Used'].unique(),
            key="mkt_channel"
        )
        
        # 기간 선택
        min_date = mkt_df['Date'].min().date()
        max_date = mkt_df['Date'].max().date()
        date_range = st.date_input(
            "기간 선택",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="mkt_date"
        )
    
    # 필터 적용
    mkt_filtered = mkt_df.copy()
    
    if channels:
        mkt_filtered = mkt_filtered[mkt_filtered['Channel_Used'].isin(channels)]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        mkt_filtered = mkt_filtered[
            (mkt_filtered['Date'].dt.date >= start_date) &
            (mkt_filtered['Date'].dt.date <= end_date)
        ]
    
    # 필터 적용 결과 표시
    st.caption(f"📋 조회 결과: {len(mkt_filtered):,}건 / 전체 {len(mkt_df):,}건")
    
    # ----- KPI 카드 -----
    st.subheader("📌 핵심 지표")
    
    if len(mkt_filtered) == 0:
        st.warning("⚠️ 선택한 필터 조건에 해당하는 데이터가 없습니다.")
    else:
        total_campaigns = len(mkt_filtered)
        avg_roi = mkt_filtered['ROI'].mean()
        avg_conversion = mkt_filtered['Conversion_Rate'].mean() * 100
        total_cost = mkt_filtered['Acquisition_Cost_Num'].sum()
        total_clicks = mkt_filtered['Clicks'].sum()
        cpc = total_cost / total_clicks if total_clicks > 0 else 0  # Cost per Click
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("총 캠페인 수", f"{total_campaigns:,}건")
        col2.metric("평균 ROI", f"{avg_roi:.2f}")
        col3.metric("평균 전환율", f"{avg_conversion:.1f}%")
        col4.metric("총 마케팅 비용", f"${total_cost:,.0f}")
    
        st.markdown("---")
        
        # ----- 차트 영역 Row 1: 월별 ROI 트렌드 -----
        st.subheader("📈 월별 ROI 추세")
        
        monthly_trend = mkt_filtered.groupby(mkt_filtered['Date'].dt.to_period('M')).agg({
            'ROI': 'mean',
            'Conversion_Rate': 'mean',
            'Acquisition_Cost_Num': 'sum'
        }).reset_index()
        monthly_trend['Date'] = monthly_trend['Date'].astype(str)
        
        fig_trend = px.line(
            monthly_trend,
            x='Date', y='ROI',
            markers=True,
            title='월별 평균 ROI 추세',
            labels={'Date': '월', 'ROI': '평균 ROI'}
        )
        fig_trend.update_traces(hovertemplate='월: %{x}<br>평균 ROI: %{y:.2f}<extra></extra>')
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # ----- 차트 영역 Row 2 -----
        col_chart1, col_chart2 = st.columns(2)
        
        # ROI 상위 채널 TOP5 (Horizontal Bar Chart)
        with col_chart1:
            st.subheader("🏆 Top 5 Channels by ROI")
            
            roi_data = mkt_filtered.groupby('Channel_Used')['ROI'].mean().nlargest(5).reset_index()
            roi_data['ROI'] = roi_data['ROI'].round(2)
            fig_roi = px.bar(
                roi_data,
                x='ROI', y='Channel_Used',
                orientation='h',
                title="Top 5 Channels by ROI",
                color='ROI',
                labels={'Channel_Used': '채널', 'ROI': '평균 ROI'}
            )
            fig_roi.update_traces(hovertemplate='채널: %{y}<br>평균 ROI: %{x:.2f}<extra></extra>')
            st.plotly_chart(fig_roi, use_container_width=True)
        
        # 캠페인 유형별 전환율 분포 (Box Plot)
        with col_chart2:
            st.subheader("📦 Conversion Rate by Campaign Type")
            
            fig_box = px.box(
                mkt_filtered,
                x='Campaign_Type', y='Conversion_Rate',
                color='Campaign_Type',
                title="Conversion Rate by Type",
                labels={'Campaign_Type': '캠페인 유형', 'Conversion_Rate': '전환율'}
            )
            fig_box.update_layout(showlegend=False)
            fig_box.update_traces(hovertemplate='캠페인: %{x}<br>전환율: %{y:.2f}<extra></extra>')
            st.plotly_chart(fig_box, use_container_width=True)

# ============================================================
# 푸터
# ============================================================
st.markdown("---")
st.caption("📊 HR & Marketing Analytics Dashboard | Built with Streamlit & Plotly")
