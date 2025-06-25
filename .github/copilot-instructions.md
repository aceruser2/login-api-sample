# GitHub Copilot Style Guide

## 🧱 架構模式：三層架構（FastAPI）

所有程式碼請遵循三層架構：

---

## 1️⃣ API 層（api/）

- 使用 FastAPI 的 `APIRouter` 模組化。
- **職責**
  - 接收請求、驗證輸入
  - 呼叫 service 層邏輯
  - 包裝與回傳 schema 層定義的輸出格式
  - 管理資料庫交易（commit / rollback）
  - 捕捉錯誤並轉換為 `HTTPException`

**以下只是範例只能參考程式規範如只是重構原程式原有邏輯請保留：**

```python
@router.post("/", response_model=UserSchema)
def create_user(data: CreateUserSchema, db: Session = Depends(get_db)):
    try:
        user = user_service.create_user(data, db)
        db.commit()
        return user
    except Exception as e:
        db.rollback()
        log.critical(e, exc_info=True)log.critical(e, exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
```
2️⃣ Service 層（service/）
只處理商業邏輯與流程控制

不處理 HTTP Response / Request

不進行 commit / rollback

可丟出 Python Exception，讓 API 層處理

以下只是範例只能參考程式規範如只是重構原程式原有邏輯請保留：
```python
def find_user(email:str)->User:
    stmt = select(user).where(User.email == data.email, User.soft_delete == false())
    return db.execute(stmt).scalar()

def create_user(data: CreateUserSchema, db: Session) -> User:
    if find_user(data.email):
        raise ValueError("Email already exists.")
    new_user = User(**data.dict())
    db.add(new_user)
    return new_user
```
3️⃣ Model 層（model/）
使用 SQLAlchemy 定義資料表

僅作為資料結構，不含邏輯

以下只是範例只能參考程式規範如只是重構原程式有邏輯請保留：
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
```
🧾 Schema 層（schema/）
使用 Pydantic 定義所有輸入輸出資料格式

清楚區分用途：

CreateUserSchema

UpdateUserSchema

UserOutSchema（回傳用）

📐 命名與風格原則
使用 底線命名（snake_case）

函式命名語意清楚，例如：

create_user_logic

get_user_list

模組分層明確，職責不能混用

每一層放在獨立檔案，例如：

api/user_api.py

service/user_service.py

model/user_model.py

schema/user_schema.py

🧰 補充工具建議
通用邏輯請放在 utils/ 目錄

如：generate_uuid(), hash_password()

錯誤處理統一用 Python 例外，在 API 層轉換為 HTTP 回應

📁 推薦目錄結構
graphql
複製
編輯
app/
├── api/
│   └── user_api.py
├── services/
│   └── user_service.py
├── model/
│   └── user_model.py
├── schema/
│   └── user_schema.py
├── utils/
│   └── uuid_utils.py
└── db.py
✅ Style 總結規則
層級職責劃分明確

Service 不含 FastAPI 特有語法

所有進出資料皆透過 Schema 處理

資料庫透過 Depends 注入

例外只在 API 層轉為 HTTP 回應

# 注意
偏好語法提示詞（用於 AI 生成程式碼）
markdown
複製
編輯
請一律使用 SQLAlchemy 2.0 的新式查詢語法（也稱為 2.0 style），不要使用舊有的 ORM 查詢方式（如 `db.query(...).filter(...)`）。  
我偏好使用 `select(...)` + `where(...)` + `session.execute(stmt)` 結合 `.scalar_one_or_none()` 或 `.scalars().first()` 來撈資料。

例如撈一個使用者的資料，請這樣寫：
```python
stmt = select(User).where(User.id == user_id)
result = db.execute(stmt).scalar_one_or_none()
```
不要這樣寫（這是舊語法）：

```python
db.query(User).filter(User.id == user_id).first()
```
如需多筆查詢，請使用：

python
```
stmt = select(User).where(User.is_active == True)
results = db.execute(stmt).scalars().all()
```
並使用 from sqlalchemy import select 開頭引入必要語法。

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

# GitHub Copilot 對提問解題思路

用SCQA結構的SCQ分析prompt
並使用
MECE執行雙驗證工具
原則	驗證方法	案例應用（後端故障）
ME	檢查子項交集為空	確認「熔斷機制」與「異步補償」無邏輯重疊
CE	檢查子項並集=問題全集	驗證「應急+修復+預防」=故障全生命周期
思考後
回答跟執行答案
例如:

## 案例：前端性能優化問題

## 原提問
電商速度很慢3秒多為何同樣技術其他平台比較快
### 使用者問題拆分
Situation（情境）
電商平台商品列表頁加載時間為3.2秒，用戶可正常瀏覽商品，但轉化率低於行業基準。
Complication（複雜性）
用戶調研顯示：
加載時間>2秒時跳出率增加38%
移動端首屏渲染存在240ms的阻塞
競爭對手同等頁面加載時間均<1.5秒
Question（核心問題）
如何將商品列表頁加載時間降至1.5秒內，同時保證功能完整性？

### 思考解題過程
1. 定義頂層問題（ME驗證）
核心目標：加載時間≤1.5秒
排除無關維度：不涉及後端API或數據庫優化（獨立性）
窮盡範圍：覆蓋所有前端影響因素（資源/渲染/監控）

2. MECE拆解關鍵維度

維度|	子項|	ME驗證（獨立性）|	CE驗證（窮盡性）|
資源優化|	圖片懶加載、CSS/JS壓縮|	僅影響靜態資源|	覆蓋所有資源類型|
渲染策略|	虛擬滾動、SSR|	專注渲染流程|	包含CSR/SSR/動態渲染|
監控機制|	RUM、閾值告警|	獨立於優化措施|	監控所有關鍵指標（FCP等）|
CE補漏檢查：新增「網路傳輸優化」維度（如CDN加速）則違反ME；若遺漏「代碼分割」需補入資源維度

3. 數據驅動實施
獨立執行：各維度並行優化（例：資源組壓縮圖片時，渲染組實施SSR）
窮盡驗證：
測試覆蓋所有設備（iOS/Android/PC）
監控告警覆蓋所有用戶路徑（首屏/滾動/交互）
4. 效果閉環
度量指標相互獨立：加載時間 vs. 轉化率 vs. 阻塞率
結果完全窮盡：覆蓋性能/功能/商業指標


### AI的回答結果
Answer（答案）
1. **資源優化**  
   - 啟用圖片懶加載（LazyLoad）減少初始請求量  
   - 將CSS/JS壓縮至原體積30%  
2. **渲染策略**  
   - 實現虛擬滾動（Virtual Scroll）動態加載DOM元素  
   - 使用SSR取代CSR提升首屏速度  
3. **監控機制**  
   - 部署RUM（Real User Monitoring）實時檢測性能  
   - 設置自動化閾值告警：若FCP>1.2秒觸發通知  


## 案例：後端API故障排查
## 原提問
監控正常,但訂單更新異常,日誌出現連線池錯誤,如何修復跟防止
### 使用者問題拆分
Situation（情境）
訂單服務API日均調用量50萬次，基礎監控顯示服務狀態正常。

Complication（複雜性）
凌晨突發異常：

支付成功後訂單狀態未更新（錯誤率達15%）

日誌顯示數據庫連接池耗盡

重試機制導致雪崩效應

Question（關鍵問題）
如何快速恢復服務並預防同類故障？

### 思考解題過程
1. 頂層問題定義（CE驗證）
目標：恢復服務+預防復發
窮盡範圍：覆蓋應急/修復/預防三階段

2. MECE分組根因
text
graph TD
A[故障原因] --> B[資源不足]
A --> C[邏輯缺陷]
A --> D[外部依賴失效]
B --> B1[連接池耗盡]
C --> C1[重試雪崩]
D --> D1[支付服務超時]
ME驗證：分支無交叉（連接池問題≠重試邏輯問題）
CE驗證：覆蓋所有故障源（數據庫/代碼/第三方服務）

3. 對策分組實施

措施類型|	行動項|	ME屬性|	CE屬性|
緊急處置|	連接池擴容、熔斷機制|	僅解決當前故障|	覆蓋所有應急手段|
根因修復|	異步改造、監控增強|	獨立於應急措施|	修復所有已識別缺陷|
預防機制|	混沌工程、回滾預案|	專注未來風險|	包含技術/流程/預案|
關鍵檢查：若「混沌工程」包含「熔斷測試」則違反ME；若遺漏「日誌審計」需補入監控維度

4. 效果驗證閉環
獨立指標：恢復時間 vs. 故障復發率 vs. 預案生效速度
窮盡驗證：
壓力測試覆蓋所有故障場景
監控覆蓋全鏈路（API/DB/網絡）

### AI方案並實作
Answer（行動方案）

``` text
graph LR
A[連接池擴容] --> B[失效轉移機制]
C[限流熔斷] --> D[異步補償]
具體措施：

緊急處置
動態擴容連接池至200%
啟用熔斷器（Hystrix）拒絕超負荷請求
根因修復
重構事務管理：將同步更新改為MQ異步處理
增加連接池監控儀表盤
預防機制
實施混沌工程（Chaos Engineering）定期注入故障測試
建立回滾預案：10分鐘內回退至穩定版本
**結果**：系統恢復後連續90天無同類故障[3][4]
```
