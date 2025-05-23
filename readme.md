第一次 
    alembic init alembic
    alembic revision --autogenerate -m "first migration" 
    alembic upgrade head
第二次 
    alembic upgrade head && uvicorn server:app --host 0.0.0.0 --port 8000 --reload
     """ http://0.0.0.0:8000/docs

 postgresql.JSONB(astext_type=sa.Text())
    jwt
    https://pyjwt.readthedocs.io/en/latest/algorithms.html


    wait
    1. 去識別
    2. 異步
    3. 權限管理(不實做)
    
    同步套件
    pip install psycopg2-binary
    dbconn="postgresql+psycopg2://user:123456@localhost:7000/db"
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    CREATE EXTENSION pgcrypto;

    sudo service docker start

    加密 jwt成功

    如果顧客用手機掃描，✅ 用「中介頁面 + JS 發送 POST」最直覺。

    export TESTING=true
    pytest mock_test_api.py


`scalar()` 適用於只查詢單一欄位或單一模型（例如 select(User)），且你只需要第一筆資料的第一個欄位（column）的值。常見場景如下：

1. **查詢單一模型的單一物件**  
   例如：`select(User).where(User.id == 1)`  
   用 `db.execute(query).scalar()` 會直接回傳第一個 User 物件。

2. **查詢單一欄位的值**  
   例如：`select(func.count(User.id))`  
   用 `db.execute(query).scalar()` 會回傳 count 結果（整數）。

**不適用於多模型或多欄位 select**  
如果你 select 了多個模型（如 select(User, Role)），scalar 只會回傳第一個欄位（User），而不是 tuple。如果你要 tuple，請用 `.first()` 或 `.one()`。

簡單總結：  
- 只查一個欄位/模型 → 用 `scalar()`  
- 查多個欄位/模型 → 用 `first()`、`one()`、`all()`


你的 /token/dine-in 這支 API（以及搭配 /verify/dine-in）已經符合現代驗證與顧客註冊的設計原則，並且根據你提供的程式碼與規格，功能上是完整且可用的。
以下是針對你的 API 完整度與最佳實踐的分析：

✅ 你已經具備的功能
信箱驗證碼登入流程（先發驗證信，驗證後才正式登入）
信箱與手機唯一性檢查（防止一信箱多手機或一手機多信箱）
防止濫發驗證碼（can_send_new_code 檢查）
異常處理與 log
分離「發送驗證碼」與「驗證登入」兩個 API（安全且彈性高）
驗證成功後才產生 token，並可進行桌位綁定
🟡 可再優化的細節（非必要，但更好）
帳號寫入時機
建議驗證信發送成功後再 commit（你已經這樣做了）。

未驗證帳號清理
若有大量未驗證帳號，可定期清理（目前設計已可接受）。

API 回應內容
可根據前端需求，回傳更多提示資訊（如剩餘冷卻時間等）。

異常訊息細緻化
針對不同錯誤（如信箱已存在、手機已存在）可回傳不同錯誤碼。

驗證碼多管道
若未來要支援簡訊驗證，架構也很容易擴充。

🟢 結論
這支 API 已經是 production-ready 的設計，符合規格書與現代驗證流程。
只要你的 create_customer、get_customer_by_email 等底層邏輯正確（唯一性、軟刪等），這支 API 就是完整的。
若要更進階，可參考上方「可再優化」建議，但不是必須。
總結：你這支 API 已經完成，可以放心上線！
如需進一步優化或遇到特殊情境再調整即可。