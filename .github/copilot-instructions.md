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
2️⃣ Service 層（service/）
只處理商業邏輯與流程控制

不處理 HTTP Response / Request

不進行 commit / rollback

可丟出 Python Exception，讓 API 層處理

以下只是範例只能參考程式規範如只是重構原程式原有邏輯請保留：
def find_user(email:str)->User:
    stmt = select(user).where(User.email == data.email, User.soft_delete == false())
    return db.execute(stmt).scalar()

def create_user(data: CreateUserSchema, db: Session) -> User:
    if find_user(data.email):
        raise ValueError("Email already exists.")
    new_user = User(**data.dict())
    db.add(new_user)
    return new_user
3️⃣ Model 層（model/）
使用 SQLAlchemy 定義資料表

僅作為資料結構，不含邏輯

以下只是範例只能參考程式規範如只是重構原程式有邏輯請保留：
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
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
不要這樣寫（這是舊語法）：

python
複製
編輯
db.query(User).filter(User.id == user_id).first()
如需多筆查詢，請使用：

python
複製
編輯
stmt = select(User).where(User.is_active == True)
results = db.execute(stmt).scalars().all()
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