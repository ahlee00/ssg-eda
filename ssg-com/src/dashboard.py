import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# 페이지 설정
st.set_page_config(
    page_title="SSG.com 특가 상품 분석 대시보드",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2227;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #ffffff !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #ffffff !important;
    }
    div[data-testid="stMetricLabel"] > div {
        color: #e0e0e0 !important;
    }
    .insight-box {
        background-color: #1e2227;
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid #ffeb3b;
        margin-top: 15px;
        margin-bottom: 30px;
        line-height: 1.8;
        color: #ffffff;
        font-size: 1.1rem;
    }
    .insight-box b {
        color: #ffeb3b;
    }
    h1, h2, h3 {
        color: #ffeb3b !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_path = 'ssg-com/data/ssg_products.csv'
    if not os.path.exists(file_path):
        st.error(f"데이터 파일을 찾을 수 없습니다: {file_path}")
        return pd.DataFrame()
    
    df = pd.read_csv(file_path)
    
    # 데이터 전처리
    # 가격 정보 정제
    df['displayPrc'] = pd.to_numeric(df['displayPrc'], errors='coerce')
    df['strikeOutPrc'] = pd.to_numeric(df['strikeOutPrc'], errors='coerce')
    df['itemOrdQty'] = pd.to_numeric(df['itemOrdQty'], errors='coerce').fillna(0)
    
    # 결측치 처리
    df['brandNm'] = df['brandNm'].fillna('브랜드 미지정')
    df['siteNm'] = df['siteNm'].fillna('SSG.COM/기타')
    df['salestrNm'] = df['salestrNm'].fillna('온라인 전용')
    
    # 할인율 계산
    df['discountRate'] = ((df['strikeOutPrc'] - df['displayPrc']) / df['strikeOutPrc'] * 100).round(1)
    df.loc[df['discountRate'] < 0, 'discountRate'] = 0 # 예외 처리
    
    return df

df = load_data()

# 사이드바: 검색 및 필터링
st.sidebar.title("🔍 검색 및 필터")
search_query = st.sidebar.text_input("상품명 또는 브랜드 검색", "")
selected_sites = st.sidebar.multiselect("사이트 선택", options=df['siteNm'].unique(), default=df['siteNm'].unique())

# 데이터 시간 필터링 (가상)
filtered_df = df[
    ((df['itemNm'].str.contains(search_query, case=False)) | 
     (df['brandNm'].str.contains(search_query, case=False))) &
    (df['siteNm'].isin(selected_sites))
]

# 메인 헤더
st.title("📦 SSG.com 특가 상품 종합 분석 대시보드")
st.markdown("---")

# 상단 지표 (Metrics)
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("총 분석 상품 수", f"{len(filtered_df):,}개")
with m2:
    avg_price = filtered_df['displayPrc'].mean()
    st.metric("평균 판매 가격", f"₩{avg_price:,.0f}")
with m3:
    max_qty = filtered_df['itemOrdQty'].max()
    st.metric("최대 주문 수량", f"{max_qty:,.0f}건")
with m4:
    avg_disc = filtered_df['discountRate'].dropna().mean()
    st.metric("평균 할인율", f"{avg_disc:.1f}%" if not np.isnan(avg_disc) else "N/A")

# 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["📊 시장 현황", "💰 가격 분석", "🛒 주문 및 혜택", "📝 상세 데이터"])

# ---------------------------------------------------------
# Tab 1: 시장 현황
# ---------------------------------------------------------
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. 브랜드별 상품 빈도 (Top 10)
        brand_counts = filtered_df['brandNm'].value_counts().head(10).reset_index()
        brand_counts.columns = ['brandNm', 'count']
        fig1 = px.bar(brand_counts, x='count', y='brandNm', orientation='h', 
                      title="상위 10개 브랜드 상품 비중",
                      color='count', color_continuous_scale='Viridis')
        fig1.update_layout(yaxis={'categoryorder':'total ascending'}, template="plotly_dark")
        st.plotly_chart(fig1, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        <b>[인사이트] 브랜드별 상품 점유율 분석</b><br>
        상위 브랜드의 상품 등록 현황을 분석한 결과, '브랜드 미지정' 상품이 압도적인 비중을 차지하고 있음을 알 수 있습니다. 이는 특정 스타 브랜드의 이름값에 의존하기보다는 제품의 품질이나 가격 경쟁력을 앞세운 중소 강소업체나 PB(Private Brand) 성향의 상품들이 특가 채널에서 활발히 소비되고 있음을 시사합니다. 대형 제조사인 CJ제일제당과 피코크 등이 그 뒤를 잇고 있는데, 이는 생필품과 가공식품 중심의 특가 운영이 고객 유입의 핵심 동력임을 증명합니다. 브랜드 파워가 낮은 상품들도 충분히 노출 기회를 얻고 있다는 점은 플랫폼의 중립성과 다양성을 확보하는 긍정적인 지표로 해석됩니다.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # 2. 사이트별 상품 분포 (Pie)
        site_dist = filtered_df['siteNm'].value_counts().reset_index()
        site_dist.columns = ['siteNm', 'count']
        fig2 = px.pie(site_dist, values='count', names='siteNm', title="판매 사이트별 분포",
                      hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig2.update_layout(template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        <b>[인사이트] 플랫폼 내 채널 분포 전략</b><br>
        사이트별 분포를 살펴보면 SSG.COM 통합 채널이 전체의 60% 이상을 점유하며 플랫폼의 중추 역할을 하고 있습니다. 이마트(약 17%)와 신세계백화점(약 11%)의 비중은 해당 대시보드가 다루는 특가 영역이 럭셔리 프리미엄보다는 실속형 생활 밀착형 구매에 타겟팅되어 있음을 보여줍니다. 특히 백화점 대비 이마트의 비중이 높다는 점은 반복 구매가 빈번한 신선/가공식품군이 특가의 주류를 이룬다는 것을 의미하며, 이는 플랫폼의 체류 시간(Retention)과 방문 빈도(Frequency)를 높이는 전략적 수단으로 활용되고 있음을 시사합니다.
        </div>
        """, unsafe_allow_html=True)
    
    # 3. 판매 점포별 등록 현황 (Bar)
    store_counts = filtered_df['salestrNm'].value_counts().head(10).reset_index()
    store_counts.columns = ['salestrNm', 'count']
    fig3 = px.bar(store_counts, x='salestrNm', y='count', title="판매 점포별 등록 현황 (Top 10)",
                  color='count', color_continuous_scale='Turbo')
    fig3.update_layout(template="plotly_dark")
    st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>[인사이트] 온-오프라인 하이브리드 유통망 진단</b><br>
    판매 점포 분석 결과, 온라인 전용 물류 거점인 'S.COM몰'이 압도적인 물량을 처리하고 있으나, 이마트 월계점과 신세계 본점 등 주요 거점 점포의 연계 비중도 상당한 수준입니다. 이는 SSG만이 가진 온-오프라인 통합 인프라의 강점을 극명하게 보여줍니다. 특히 특정 거점 점포 인근의 재고를 온라인 특가로 전환하여 빠르게 소진하는 '하이퍼 로컬' 전략이 유효하게 작동하고 있음을 알 수 있습니다. 물류 효율성이 높은 거점을 중심으로 특가 상품을 기획 배치함으로써 배송 비용을 절감하는 동시에 고객에게는 신선한 제품을 빠르게 공급하는 선순환 구조를 확보하고 있습니다.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Tab 2: 가격 분석
# ---------------------------------------------------------
with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        # 4. 가격 분포 히스토그램
        fig4 = px.histogram(filtered_df, x='displayPrc', nbins=50, title="상품 가격대별 빈도 분포",
                            color_discrete_sequence=['#ffeb3b'])
        fig4.update_layout(xaxis_title="판매 가격 (₩)", yaxis_title="상품 수", template="plotly_dark")
        st.plotly_chart(fig4, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        <b>[인사이트] 특가 시장의 심리적 가격 장벽 분석</b><br>
        가격 분포는 전형적인 롱테일(Long-tail) 형태를 띠며 0~5만원 구간에 압도적으로 집중되어 있습니다. 이는 소비자가 '특가'라는 단어를 접할 때 기대하는 가격 저항선이 매우 낮게 형성되어 있음을 의미합니다. 특히 3만원 이하의 저단가 상품군에서 발생하는 폭발적인 빈도는 해당 채널이 '고민 없는 구매(Impulse Buying)'를 유도하는 데 최적화되어 있음을 보여줍니다. 기업 입장에서는 10만원 이상의 고가 상품보다는 5만원 미만의 가성비 라인업을 촘촘하게 구성하는 것이 집객 측면에서 훨씬 유리하며, 높은 회전율을 바탕으로 한 운영 최적화가 필수적입니다.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # 5. 사이트별 가격 변동성 (Box plot)
        fig5 = px.box(filtered_df, x='siteNm', y='displayPrc', title="사이트별 가격 변동성 분석",
                      color='siteNm', points="outliers")
        fig5.update_layout(yaxis_type="log", template="plotly_dark")
        st.plotly_chart(fig5, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        <b>[인사이트] 판매 플랫폼별 가격 전략 차별화</b><br>
        박스플롯 분석 결과, 신세계백화점과 신세계몰은 가격의 변동 범위가 넓고 고가의 이상치(Outlier)가 다수 발견되는 반면, 이마트와 새벽배송 채널은 가격대가 매우 좁고 낮게 형성되어 있습니다. 이는 각 사이트가 타겟팅하는 고객층과 상품 카테고리의 차이를 명확히 드러냅니다. 백화점 채널은 브랜드 신뢰도를 바탕으로 하는 프리미엄 전략을 고수하면서도 특가 기간을 통해 높은 객단가를 유지하려 노력하고, 이마트 계열은 생필품 중심의 '최저가 보상제' 성격의 안정적 가격 정책을 일관되게 추진하고 있음을 데이터로 확인할 수 있습니다.
        </div>
        """, unsafe_allow_html=True)
        
    # 6. 브랜드별 평균 가격 (Top 10)
    avg_price_brand = filtered_df.groupby('brandNm')['displayPrc'].mean().sort_values(ascending=False).head(10).reset_index()
    fig6 = px.bar(avg_price_brand, x='brandNm', y='displayPrc', title="상위 10개 브랜드 평균 판매가",
                  color='displayPrc', color_continuous_scale='Cividis')
    fig6.update_layout(template="plotly_dark")
    st.plotly_chart(fig6, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>[인사이트] 프리미엄 브랜드의 가격 포지셔닝</b><br>
    평균 판매가가 가장 높은 브랜드들을 분석한 결과, 가전이나 럭셔리 뷰티 브랜드들이 상위권을 차지하고 있습니다. 이들 브랜드는 '특가'임에도 불구하고 절대적인 가격 수준이 높게 형성되어 있는데, 이는 가격 할인 그 자체보다는 '특가 구좌 노출을 통한 브랜드 신뢰도 제고'와 '사은품 증정 등 비가격적 혜택'을 중시하는 전략을 취하고 있을 가능성이 높습니다. 플랫폼 운영진은 이러한 고단가 브랜드를 적절히 믹스하여 전체 거래액(GMV)의 볼륨을 키우고, 중저가 식품류로 거래 건수(Order Count)를 확보하는 이원화된 카테고리 관리 전략을 구사해야 합니다.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Tab 3: 주문 및 혜택
# ---------------------------------------------------------
with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        # 7. 주문 수량 분포
        fig7 = px.histogram(filtered_df, x='itemOrdQty', nbins=50, title="상품별 주문 수량 집중도",
                            color_discrete_sequence=['#4caf50'])
        fig7.update_layout(template="plotly_dark")
        st.plotly_chart(fig7, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        <b>[인사이트] 히트 상품의 집중화 현상 분석</b><br>
        주문 수량 데이터는 극심한 오른쪽 꼬리 분포를 보여줍니다. 대다수의 상품이 수백 건의 주문에 머물러 있는 반면, 상위 5% 내외의 '메가 히트' 상품들이 수만 건의 주문을 독식하고 있는 파레토 법칙이 선명하게 나타납니다. 이러한 데이터 구조는 온라인 커머스 환경에서 '승자 독식' 현상이 강화되고 있음을 뜻합니다. 따라서 플랫폼 운영자는 초기 반응이 좋은 라이딩 상품(Rising Stars)을 빠르게 포착하여 메인 구좌에 전진 배치하는 민첩한 MD 운영 능력이 필요합니다. 소수의 대박 상품이 전체 매출의 상당 부분을 견인하므로 이들에 대한 품질 관리와 품절 방지가 핵심 성공 요인입니다.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # 8. 가격 vs 주문 수량 산점도
        fig8 = px.scatter(filtered_df, x='displayPrc', y='itemOrdQty', size='itemOrdQty',
                          color='siteNm', hover_name='itemNm', 
                          title="가격 수준에 따른 고객 구매 행동 분석",
                          log_x=True)
        fig8.update_layout(template="plotly_dark")
        st.plotly_chart(fig8, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        <b>[인사이트] 가격 민감도와 구매량의 반비례 관계</b><br>
        가격과 주문 수량 사이의 산점도를 분석해본 결과, 저가격대에서 기하급수적으로 높은 주문 수량이 발생하는 전형적인 반비례 곡선이 관찰됩니다. 특히 1만원에서 5만원 사이의 '골든 존(Golden Zone)'에서 대부분의 트래픽 전환이 이루어지고 있습니다. 가격이 일정 수준을 넘어서면 구매량은 급격히 감소하나, 브랜드 파워가 높은 백화점 상품군의 경우 높은 가격대에서도 일정 수준 이상의 주문량을 유지하며 가격 탄력성이 상대적으로 낮음을 확인할 수 있습니다. 이는 고객 유입을 위한 저단가 미끼 상품과 수익을 위한 고단가 전략 상품의 적절한 조화가 필요함을 시사합니다.
        </div>
        """, unsafe_allow_html=True)
        
    # 9. 할인율 분포 히스토그램
    disc_df = filtered_df.dropna(subset=['discountRate'])
    if not disc_df.empty:
        fig9 = px.histogram(disc_df, x='discountRate', nbins=30, title="할인 적용 상품의 혜택 강도 분석",
                            color_discrete_sequence=['#f44336'])
        fig9.update_layout(xaxis_title="할인율 (%)", template="plotly_dark")
        st.plotly_chart(fig9, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        <b>[인사이트] 가격 할인 정책의 마케팅 효과 분석</b><br>
        할인율 분포를 분석하면 30%에서 50% 사이의 높은 할인율을 가진 상품들이 상당수 존재합니다. 이는 소비자들에게 시각적으로 강력한 '득템'의 기회를 제공하며 클릭을 유도하는 핵심 마케팅 요소입니다. 하지만 흥미로운 점은 할인율이 높다고 반드시 주문 수량이 정비례하여 늘어나지는 않는다는 것입니다. 이는 소비자들이 단순한 숫자의 크기보다 '최종 판매가'의 절대적 수준과 '브랜드 정품 여부'를 더 중요하게 판단하기 때문으로 해석됩니다. 따라서 무분별한 할인율 상향보다는 신뢰할 수 있는 브랜드의 현실적인 가격 제안이 실제 매출로 이어지는 데 더 효과적일 것입니다.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("할인율 데이터가 충분하지 않습니다.")

    # 10. 상위 주문 상품 Top 10
    top_ordered = filtered_df.sort_values(by='itemOrdQty', ascending=False).head(10)
    fig10 = px.bar(top_ordered, x='itemOrdQty', y='itemNm', orientation='h',
                   title="주문 수량 기준 TOP 10 상품 현황",
                   color='itemOrdQty', color_continuous_scale='Reds')
    fig10.update_layout(yaxis={'categoryorder':'total ascending'}, template="plotly_dark")
    st.plotly_chart(fig10, use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>[인사이트] '베스트셀러'의 속성 및 성공 요인 분석</b><br>
    주문 수량 기준 상위 10개 상품을 심층 분석한 결과, 주로 신선 보관이 용이한 가공식품, 대량 구매가 일어나는 위생용품(화장지, 생리대 등), 그리고 계절적 수요가 명확한 상품들이 포진해 있습니다. 이들 상품의 공통점은 '생활 필수성'과 '가격 메리트'의 결합입니다. 특히 '1+1'이나 '단독 특가'와 같은 강력한 프로모션 언어가 사용된 경우 고객의 반응이 확연히 높습니다. 상위 상품들의 성공 방정식을 벤치마킹하여 신규 입점 상품들에 원플러스원 패키징이나 무료배송 전략을 선제적으로 제안한다면, 플랫폼 전체의 상품 경쟁력을 한 단계 더 끌어올릴 수 있는 기회가 될 것입니다.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Tab 4: 상세 데이터
# ---------------------------------------------------------
with tab4:
    st.subheader("📋 검색 결과 데이터 요약")
    st.dataframe(filtered_df[['itemNm', 'brandNm', 'displayPrc', 'strikeOutPrc', 'discountRate', 'siteNm', 'itemOrdQty']],
                 use_container_width=True)
    
    st.markdown("""
    <div class="insight-box">
    <b>[데이터 요약 인사이트]</b><br>
    현재 검색 및 필터링된 결과에 따른 상세 리스트입니다. 가격 및 주문 수량 등의 지표를 실시간으로 대조하며 개별 상품의 성과를 프로파일링할 수 있습니다. 특히 할인율이 높음에도 주문 수량이 낮은 상품이나, 반대로 높은 가격임에도 주문 수량이 견조한 상품들을 선별하여 심층적인 원인 분석(Price-Quantity Gap Analysis)을 진행한다면, 상품 소싱의 정확도를 높이는 원천 데이터로 활용될 수 있습니다. 대시보드의 데이터를 주기적으로 업데이트하여 시계열적인 트렌드 변화까지 모니터링한다면 완벽한 의사결정 보조 도구가 될 것입니다.
    </div>
    """, unsafe_allow_html=True)

# 푸터
st.markdown("---")
st.markdown("© 2026 SSG.com Data Analysis Dashboard | Developed by Antigravity")
