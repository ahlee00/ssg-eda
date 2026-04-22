1) HTTP 요청정보와 헤더

Request URL
https://frontapi.ssg.com/dp/api/v2/page/area
Request Method
POST
Status Code
200 OK
Remote Address
202.8.171.190:443
Referrer Policy
no-referrer-when-downgrade

origin
https://www.ssg.com
priority
u=1, i
referer
https://www.ssg.com/page/pc/SpecialPrice.ssg
sec-ch-ua
"Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"
sec-ch-ua-mobile
?0
sec-ch-ua-platform
"macOS"
sec-fetch-dest
empty
sec-fetch-mode
cors
sec-fetch-site
same-site
user-agent
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36

2) Payload 정보

{"common":{"aplVer":"","osCd":"","ts":"20260420122140","mobilAppNo":"99","dispDvicDivCd":"10","viewSiteNo":"6005"},"params":{"page":"3","state":"{}","pageId":"100000007533","pageSetId":"2","dispCtgId":null,"pageCmptId":"4"}}

3) 응답의 일부를 Response 에서 일부를 복사해서 넣어주기 (전체는 토큰 수 제한으로 어렵습니다.)

```
{
    "cacheStatus": "NOT_STORED",
    "cacheStore": true,
    "resultCode": "200",
    "resultMsg": "SUCCESS",
    "resultDtlCode": null,
    "resultDtlMsg": null,
    "data": {
        "areaList": [
            [
                {
                    "cacheStatus": "NOT_STORED",
                    "cacheStore": true,
                    "unitType": "SPECIALDEAL_ITEM",
                    "dataType": "SPECIALPRICE_HOTDEAL",
                    "pageId": "100000007533",
                    "pageSetId": "2",
                    "pageCmptId": "4",
                    "reactPrefix": "특가|상품_3|",
                    "assocationParam": {
                        "actCtgId": null,
                        "dispCtgLowerId": null,
                        "hu": null,
                        "hr": null,
                        "reu": null,
                        "rer": null,
                        "fi": null,
                        "ru": null,
                        "re": null,
                        "pr": null,
                        "nrcq": null,
                        "dcim": null,
                        "nrcn": null,
                        "nrl": null,
                        "cornrSetId": null,
                        "brandId": null,
                        "dispCtgs": null,
                        "itemIds": null,
                        "frontItems": null,
                        "dti": null,
                        "itemProfId": null
                    },
                    "isAreaMoreFixedUnit": false,
                    "dispOrdr": 3,
                    "cornrSetId": "",
                    "itemList": [
                        {
```

4) 한페이지가 성공적으로 수집되는지 확인하고 전체 페이지를 수집할 것