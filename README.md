# 永豐金證券 Shioaji 交易系統

這是一個基於永豐金證券 Shioaji API 的交易系統實作。

## 功能特色

- ✅ 簡潔直觀的登入介面
- ✅ 支援 API Key 與帳號密碼兩種登入方式
- ✅ 完整的 docstring 註解
- ✅ 類別屬性 `sj` 供後續交易使用
- ✅ 帳戶管理功能

## 安裝

```bash
pip install -r requirements.txt
```

## 快速開始

### 使用 API Key 登入（推薦）

```python
from shioaji_trader import ShioajiTrader

# 建立交易器實例
trader = ShioajiTrader()

# 登入
trader.login(
    api_key="YOUR_API_KEY",
    secret_key="YOUR_SECRET_KEY"
)

# 使用 trader.sj 進行後續操作
print(trader.sj.stock_account)
print(trader.sj.futopt_account)

# 登出
trader.logout()
```

### 使用帳號密碼登入

```python
from shioaji_trader import ShioajiTrader

trader = ShioajiTrader()

trader.login(
    person_id="YOUR_PERSON_ID",
    passwd="YOUR_PASSWORD"
)
```

## 主要功能

### 1. 登入系統

```python
# 使用 API Key
success = trader.login(api_key="YOUR_API_KEY", secret_key="YOUR_SECRET_KEY")

# 使用帳號密碼
success = trader.login(person_id="YOUR_PERSON_ID", passwd="YOUR_PASSWORD")
```

### 2. 查看帳戶

```python
# 列出所有帳戶
accounts = trader.list_accounts()

# 查看預設證券帳戶
print(trader.stock_account)

# 查看預設期貨帳戶
print(trader.futopt_account)
```

### 3. 設定預設帳戶

```python
accounts = trader.list_accounts()
trader.set_default_account(accounts[0])
```

### 4. 登出系統

```python
trader.logout()
```

## 類別屬性

- `sj`: Shioaji API 實例，登入成功後可用於所有交易操作

## 參考資料

- [Shioaji 官方文件](https://sinotrade.github.io/)
- [Shioaji 登入教學](https://sinotrade.github.io/zh/tutor/login/)

## 範例程式

完整範例請參考 `example_usage.py`

## 授權

請參考 LICENSE 文件