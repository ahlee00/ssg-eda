import requests
import json
import pandas as pd
import time
from datetime import datetime
import os

def get_ssg_products():
    url = "https://frontapi.ssg.com/dp/api/v2/page/area"
    headers = {
        "origin": "https://www.ssg.com",
        "referer": "https://www.ssg.com/page/pc/SpecialPrice.ssg",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "content-type": "application/json"
    }

    all_items = []
    page = 1
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 수집 시작...")

    while True:
        print(f"페이지 {page} 수집 중...")
        
        payload = {
            "common": {
                "aplVer": "",
                "osCd": "",
                "ts": datetime.now().strftime("%Y%m%d%H%M%S"),
                "mobilAppNo": "99",
                "dispDvicDivCd": "10",
                "viewSiteNo": "6005"
            },
            "params": {
                "page": str(page),
                "state": "{}",
                "pageId": "100000007533",
                "pageSetId": "2",
                "dispCtgId": None,
                "pageCmptId": "4"
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            found_items_in_page = 0
            
            if 'data' in data and 'areaList' in data['data']:
                for area_group in data['data']['areaList']:
                    for area in area_group:
                        items = area.get('itemList', [])
                        for item in items:
                            # 필요한 필드 추출
                            item_data = {
                                'itemId': item.get('itemId'),
                                'itemNm': item.get('itemNm'),
                                'brandNm': item.get('brandNm'),
                                'displayPrc': item.get('displayPrc'),
                                'strikeOutPrc': item.get('strikeOutPrc'),
                                'siteNm': item.get('siteNm'),
                                'salestrNm': item.get('salestrNm'),
                                'itemLnkd': item.get('itemLnkd'),
                                'itemImgUrl': item.get('itemImgUrl'),
                                'itemOrdQty': item.get('itemOrdQty'),
                                'itemOrdQtyTxt': item.get('itemOrdQtyTxt'),
                                'page': page
                            }
                            all_items.append(item_data)
                            found_items_in_page += 1
            
            if found_items_in_page == 0:
                print("더 이상 수집할 데이터가 없습니다.")
                break
            
            print(f"페이지 {page}: {found_items_in_page}개 상품 수집 완료.")
            page += 1
            
            # 차단 방지를 위한 짧은 휴식
            time.sleep(0.5)
            
        except Exception as e:
            print(f"페이지 {page} 수집 중 오류 발생: {e}")
            break

    if all_items:
        df = pd.DataFrame(all_items)
        # 데이터 정제: 가격을 숫자로 변환 (필요시)
        
        output_dir = "ssg-com/data"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "ssg_products.csv")
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n총 {len(all_items)}개 상품 수집 완료.")
        print(f"저장 경로: {output_path}")
    else:
        print("수집된 상품이 없습니다.")

if __name__ == "__main__":
    get_ssg_products()
