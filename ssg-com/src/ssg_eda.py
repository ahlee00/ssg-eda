import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
try:
    import koreanize_matplotlib
except ImportError:
    # Mac용 한글 폰트 설정 (koreanize_matplotlib 이슈 대비)
    from matplotlib import rc
    rc('font', family='AppleGothic')
    plt.rcParams['axes.unicode_minus'] = False
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import textwrap

# 20년차 데이터 분석가 페르소나 설정
# 이미지 저장 경로 설정
IMAGE_DIR = "ssg-com/images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

def generate_eda():
    # 1. 데이터 로드
    df = pd.read_csv("ssg-com/data/ssg_products.csv")
    
    print("--- 상위 5개행 ---")
    print(df.head())
    print("\n--- 하위 5개행 ---")
    print(df.tail())
    
    print("\n--- 기본 정보 (info) ---")
    print(df.info())
    
    print(f"\n전체 행 수: {df.shape[0]}, 전체 열 수: {df.shape[1]}")
    
    duplicates = df.duplicated().sum()
    print(f"중복 데이터 수: {duplicates}")
    
    # 데이터 전처리
    df['brandNm'] = df['brandNm'].fillna('브랜드 미지정')
    df['siteNm'] = df['siteNm'].fillna('SSG.COM/기타')
    df['salestrNm'] = df['salestrNm'].fillna('온라인전용')
    
    # 할인율 계산 (strikeOutPrc가 있는 경우)
    df['discountRate'] = 0.0
    mask = (df['strikeOutPrc'].notnull()) & (df['strikeOutPrc'] > 0)
    df.loc[mask, 'discountRate'] = (df.loc[mask, 'strikeOutPrc'] - df.loc[mask, 'displayPrc']) / df.loc[mask, 'strikeOutPrc'] * 100

    # 2. 기술 통계
    desc_num = df[['displayPrc', 'itemOrdQty', 'discountRate', 'page']].describe()
    desc_cat = df.describe(include=['object', 'O'])
    
    print("\n--- 수치형 기술 통계 ---")
    print(desc_num)
    print("\n--- 범주형 기술 통계 ---")
    print(desc_cat)
    
    # 3. TF-IDF 키워드 추출 (단어 단위 분석)
    # 한국어 형태소 분석 대신 공백 기준 토큰화 사용 (간소화)
    vectorizer = TfidfVectorizer(max_features=30, stop_words=None)
    tfidf_matrix = vectorizer.fit_transform(df['itemNm'])
    keywords = vectorizer.get_feature_names_out()
    
    # 키워드 빈도 합계 계산 (TF-IDF 점수의 합)
    tfidf_sums = tfidf_matrix.sum(axis=0).A1
    keyword_freq = pd.DataFrame({'keyword': keywords, 'score': tfidf_sums}).sort_values(by='score', ascending=False)
    
    # 4. 시각화 섹션 (10개 이상)
    viz_list = []
    
    # 1) 브랜드 빈도 (범주형 빈도수 - 상위 30개)
    plt.figure(figsize=(12, 8))
    brand_counts = df['brandNm'].value_counts().head(30)
    brand_counts.plot(kind='bar', color='skyblue')
    plt.title('상위 30개 브랜드별 상품 빈도')
    plt.xlabel('브랜드')
    plt.ylabel('상품 수')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{IMAGE_DIR}/01_brand_freq.png")
    viz_list.append(('01_brand_freq.png', '브랜드별 상품 빈도 분석', brand_counts.to_frame().reset_index()))
    plt.close()

    # 2) 판매처 빈도 (범주형 빈도수 - 상위 30개)
    plt.figure(figsize=(12, 8))
    site_counts = df['siteNm'].value_counts()
    site_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, cmap='Pastel1')
    plt.title('사이트별 상품 분포')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(f"{IMAGE_DIR}/02_site_dist.png")
    viz_list.append(('02_site_dist.png', '사이트별 상품 분포 비중', site_counts.to_frame().reset_index()))
    plt.close()

    # 3) 상위 판매점포 분포 (범주형 빈도수)
    plt.figure(figsize=(12, 8))
    store_counts = df['salestrNm'].value_counts().head(20)
    store_counts.plot(kind='barh', color='salmon')
    plt.title('상위 20개 판매 점포별 빈도')
    plt.xlabel('상품 수')
    plt.ylabel('점포명')
    plt.tight_layout()
    plt.savefig(f"{IMAGE_DIR}/03_store_freq.png")
    viz_list.append(('03_store_freq.png', '판매 점포별 상품 등록 현황', store_counts.to_frame().reset_index()))
    plt.close()

    # 4) 판매 가격 분포 (수치형 - 히스토그램)
    plt.figure(figsize=(10, 6))
    plt.hist(df['displayPrc'], bins=50, color='gold', edgecolor='black')
    plt.title('판매 가격(displayPrc) 분포')
    plt.xlabel('가격')
    plt.ylabel('빈도')
    plt.tight_layout()
    plt.savefig(f"{IMAGE_DIR}/04_price_hist.png")
    viz_list.append(('04_price_hist.png', '판매 가격대별 빈도 분포', desc_num[['displayPrc']]))
    plt.close()

    # 5) 사이트별 가격 박스플롯 (이변량)
    plt.figure(figsize=(12, 6))
    data_to_plot = [df[df['siteNm'] == s]['displayPrc'] for s in df['siteNm'].unique()]
    plt.boxplot(data_to_plot, labels=df['siteNm'].unique())
    plt.title('사이트별 가격대 비교 (박스플롯)')
    plt.ylabel('가격')
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(f"{IMAGE_DIR}/05_price_boxplot_site.png")
    viz_list.append(('05_price_boxplot_site.png', '사이트별 가격 변동성 및 이상치 분석', df.groupby('siteNm')['displayPrc'].describe()))
    plt.close()

    # 6) 주문 수량 분포 (수치형)
    plt.figure(figsize=(10, 6))
    plt.hist(df['itemOrdQty'], bins=50, color='lightgreen', edgecolor='black')
    plt.title('주문 수량(itemOrdQty) 분포')
    plt.xlabel('주문 수량')
    plt.ylabel('빈도')
    plt.tight_layout()
    plt.savefig(f"{IMAGE_DIR}/06_ordqty_hist.png")
    viz_list.append(('06_ordqty_hist.png', '상품별 주문 수량의 집중도 분석', desc_num[['itemOrdQty']]))
    plt.close()

    # 7) 가격 vs 주문 수량 상관관계 (이변량 - 산점도)
    plt.figure(figsize=(10, 6))
    plt.scatter(df['displayPrc'], df['itemOrdQty'], alpha=0.5, color='purple')
    plt.title('가격와 주문 수량의 상관관계')
    plt.xlabel('가격')
    plt.ylabel('주문 수량')
    plt.tight_layout()
    plt.savefig(f"{IMAGE_DIR}/07_price_qty_scatter.png")
    viz_list.append(('07_price_qty_scatter.png', '가격 수준에 따른 고객 구매 행동 분석', df[['displayPrc', 'itemOrdQty']].corr()))
    plt.close()

    # 8) 할인율 분포 (할인 적용 상품 한정)
    plt.figure(figsize=(10, 6))
    discount_df = df[df['discountRate'] > 0]
    plt.hist(discount_df['discountRate'], bins=20, color='orange', edgecolor='black')
    plt.title('할인율 분포 (할인 상품 대상)')
    plt.xlabel('할인율 (%)')
    plt.ylabel('빈도')
    plt.tight_layout()
    plt.savefig(f"{IMAGE_DIR}/08_discount_hist.png")
    viz_list.append(('08_discount_hist.png', '할인 적용 상품의 혜택 강도 분석', discount_df['discountRate'].describe().to_frame()))
    plt.close()

    # 9) 상위 10개 브랜드별 평균 가격 (이변량)
    top_brands = df['brandNm'].value_counts().head(10).index
    brand_avg_price = df[df['brandNm'].isin(top_brands)].groupby('brandNm')['displayPrc'].mean().sort_values(ascending=False)
    plt.figure(figsize=(12, 6))
    brand_avg_price.plot(kind='bar', color='teal')
    plt.title('상위 10개 브랜드별 평균 판매 가격')
    plt.xlabel('브랜드')
    plt.ylabel('평균 가격')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{IMAGE_DIR}/09_brand_avg_price.png")
    viz_list.append(('09_brand_avg_price.png', '주요 브랜드별 가격 포지셔닝 비교', brand_avg_price.to_frame()))
    plt.close()

    # 10) TF-IDF 상위 30개 키워드 빈도 (텍스트 분석)
    plt.figure(figsize=(12, 8))
    plt.barh(keyword_freq['keyword'].head(30)[::-1], keyword_freq['score'].head(30)[::-1], color='navy')
    plt.title('TF-IDF 기반 상품명 핵심 키워드 Top 30')
    plt.xlabel('TF-IDF 점수 합계')
    plt.ylabel('키워드')
    plt.tight_layout()
    plt.savefig(f"{IMAGE_DIR}/10_tfidf_keywords.png")
    viz_list.append(('10_tfidf_keywords.png', '상품명 텍스트 데이터를 통한 검색어 가치 분석', keyword_freq.head(30)))
    plt.close()

    # 11) 페이지별 평균 할인율 (다변량 - 페이지에 따른 변화)
    page_stats = df.groupby('page').agg({'discountRate': 'mean', 'itemId': 'count'}).rename(columns={'itemId': 'itemCount'})
    plt.figure(figsize=(10, 6))
    plt.plot(page_stats.index, page_stats['discountRate'], marker='o', linestyle='-', color='red')
    plt.title('페이지 번호에 따른 평균 할인율 변화')
    plt.xlabel('페이지')
    plt.ylabel('평균 할인율 (%)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{IMAGE_DIR}/11_page_discount_trend.png")
    viz_list.append(('11_page_discount_trend.png', '페이지 노출 순서와 할인 정책의 연관성 분석', page_stats))
    plt.close()

    return df, desc_num, desc_cat, keyword_freq, viz_list

if __name__ == "__main__":
    generate_eda()
