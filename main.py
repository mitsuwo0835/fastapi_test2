import os
from typing import Optional

from fastapi import FastAPI
from sp_api.api import Catalog
from sp_api.base.marketplaces import Marketplaces
from sp_api.api import FbaInboundEligibility
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

def search_product(ASIN, PROGRAM="INBOUND"):
    credentials = dict(
        # Amazon Seller開発者登録後に入手可能
        refresh_token=os.getenv("AWS_SP_REFRESH_TOKEN"),
        # Amazon Seller開発者登録後に入手可能
        lwa_app_id=os.getenv("AWS_SP_LWA_APP_ID"),
        # Amazon Seller開発者登録後に入手可能
        lwa_client_secret=os.getenv("AWS_SP_LWA_CLIENT_SECRET"),
        aws_access_key=os.getenv("AWS_SP_ACCESS_KEY"),  # （AWS IAMユーザーロール登録時に取得可能）
        aws_secret_key=os.getenv("AWS_SP_SECRET_KEY"),  # （AWS IAMユーザーロール登録時に取得可能）
        role_arn=os.getenv("AWS_SP_ROLE_ARN"),  # （AWS IAMユーザーロール登録時に取得可能）
    )
    # 商品検索用オブジェクト
    # obj = Catalog(marketplace=Marketplaces.JP,   # 対象のマーケットプレイスを指定
    #               credentials=credentials)       # API情報を指定
    obj = FbaInboundEligibility(
        marketplace=Marketplaces.JP,
        credentials=credentials)

    # ASINコードを指定し商品情報取得
    # result = obj.get_item(ASIN)
    result = obj.get_item_eligibility_preview(asin=ASIN, program=PROGRAM)
    return result()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/api/{key}/eligibility/items/{item_id}/test")
def read_item(key: str, item_id: str, q: Optional[str] = None):
    if key != os.getenv("AWS_SP_API_KEY"):
        return {"error": "api key error"}
    try:
        data = search_product(item_id)
    except TypeError as e:
        data = None
        print('catch TypeError:', e)
    if data:
        return {"asin": item_id, "result": data}
    else:
        return {"error": "request error", "result": None}
    
    
    
@app.get("/api/{key}/eligibility/items/{item_id}/inbound")
def read_item_inbound(key: str, item_id: str, q: Optional[str] = None):
    if key != os.getenv("AWS_SP_API_KEY"):
        return {"error": "api key error"}
    try:
        data = search_product(item_id, "INBOUND")
    except TypeError as e:
        data = None
        print('catch TypeError:', e)
    if data:
        return {"asin": item_id, "result": data}
    else:
        return {"error": "request error", "result": None}
    
@app.get("/api/{key}/eligibility/items/{item_id}/commingling")
def read_item_commingling(key: str, item_id: str, q: Optional[str] = None):
    if key != os.getenv("AWS_SP_API_KEY"):
        return {"error": "api key error"}
    try:
        data = search_product(item_id, "COMMINGLING")
    except TypeError as e:
        data = None
        print('catch TypeError:', e)
    if data:
        return {"asin": item_id, "result": data}
    else:
        return {"error": "request error", "result": None}
    
@app.get("/api/{key}/eligibility/items/{item_id}")
def read_item_all(key: str, item_id: str, q: Optional[str] = None):
    if key != os.getenv("AWS_SP_API_KEY"):
        return {"error": "api key error"}
    try:
        item1 = search_product(item_id, "INBOUND")
        item2 = search_product(item_id, "COMMINGLING")
        if not(item1["isEligibleForProgram"]) and not(item2["isEligibleForProgram"]):
            item = {
                "asin": item1["asin"],
                "marketplaceId": item1["marketplaceId"],
                "program": ["INBOUND","COMMINGLING"],
                "isEligibleForProgram": item1["isEligibleForProgram"],
                "ineligibilityReasonList": list(set(item1["ineligibilityReasonList"] + item2["ineligibilityReasonList"]))
            }
        elif not(item1["isEligibleForProgram"]):
            item = item1
        elif not(item2["isEligibleForProgram"]):
            item = item2
        else:
            item = {
                "asin": item1["asin"],
                "marketplaceId": item1["marketplaceId"],
                "program": ["INBOUND","COMMINGLING"],
                "isEligibleForProgram": item1["isEligibleForProgram"],
                "ineligibilityReasonList": []
            }

        data = item
    except TypeError as e:
        data = None
        print('catch TypeError:', e)
    if data:
        return {"asin": item_id, "result": data}
    else:
        return {"error": "request error", "result": None}
