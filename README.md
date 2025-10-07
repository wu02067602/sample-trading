# 量化交易系統 - 永豐 Shioaji 整合

本專案提供永豐證券 Shioaji SDK 的委託回報處理功能，遵循 SOLID 設計原則，提供易於擴展和維護的架構。

## 功能特色

- ✅ 永豐證券 Shioaji SDK 整合
- ✅ 委託狀態變更回報處理
- ✅ 成交回報處理
- ✅ 觀察者模式支援多個監聽器
- ✅ 完整的錯誤處理機制
- ✅ 日誌記錄功能
- ✅ 符合 SOLID 設計原則

## 安裝

```bash
pip install -r requirements.txt
```

## 使用方式

### 基本使用

```python
from src.broker.shioaji_broker import ShioajiBroker
from src.broker.order_callback_handler import OrderCallbackHandler

# 1. 建立券商介面
broker = ShioajiBroker()

# 2. 連線到永豐證券
broker.connect(
    api_key="YOUR_API_KEY",
    secret_key="YOUR_SECRET_KEY",
    simulation=True
)

# 3. 建立委託回報處理器
order_handler = OrderCallbackHandler()

# 4. 設定委託回報回調
broker.setup_order_callback(order_handler)
```

### 自定義監聽器

```python
class MyOrderListener:
    """自定義的委託事件監聽器"""
    
    def on_order_status_changed(self, order_status: dict) -> None:
        """處理委託狀態變更"""
        print(f"委託狀態: {order_status}")
    
    def on_deal_received(self, deal_info: dict) -> None:
        """處理成交回報"""
        print(f"成交回報: {deal_info}")

# 註冊監聽器
listener = MyOrderListener()
order_handler.register_listener(listener)
```

完整範例請參考 `examples/order_callback_example.py`

## 架構設計

本系統採用以下設計原則：

### SOLID 原則

- **單一職責原則 (SRP)**: 每個類別只負責一項職責
- **開放封閉原則 (OCP)**: 對擴展開放，對修改封閉
- **里氏替換原則 (LSP)**: 使用抽象介面和 Protocol
- **介面隔離原則 (ISP)**: 介面簡潔明確
- **依賴反轉原則 (DIP)**: 依賴抽象而非具體實作

### 設計模式

- **觀察者模式**: 支援多個監聽器訂閱委託回報事件
- **依賴注入**: 支援自定義 Logger

詳細架構說明請參考 [類別圖.md](類別圖.md)

## 錯誤處理

本專案遵循嚴格的錯誤處理規範：

- 使用具體的錯誤類型 (ValueError, TypeError, ConnectionError 等)
- 避免使用籠統的 `except Exception`
- 使用 logging 模組記錄錯誤
- 完整的 docstring 說明可能的錯誤

## 專案結構

```
/workspace
├── src/
│   └── broker/
│       ├── __init__.py
│       ├── callback_handler_interface.py  # 回調處理器抽象介面
│       ├── order_callback_handler.py      # 委託回報處理器
│       └── shioaji_broker.py              # 永豐券商介面
├── examples/
│   └── order_callback_example.py          # 使用範例
├── requirements.txt
├── README.md
└── 類別圖.md
```

## 開發規範

本專案遵循以下規範：

1. **Docstring**: 所有函數必須包含完整的 docstring
2. **錯誤處理**: 必須使用具體的錯誤類型
3. **日誌記錄**: 使用 logging 模組而非 print
4. **SOLID 原則**: 遵循 SOLID 設計原則

## 授權

請參考 LICENSE 檔案
