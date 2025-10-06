# sample-trading

交易系統登入配置管理模組

## 專案概述

這是一個用於管理永豐期貨交易系統登入參數的 Python 專案。提供簡潔且直觀的 Config 類別來處理配置檔案的讀取、驗證和管理。

## 功能特性

- ✅ 從 YAML 檔案讀取登入配置參數
- ✅ 自動驗證配置參數的格式和完整性
- ✅ 完善的錯誤處理機制
- ✅ 完整的單元測試覆蓋
- ✅ 符合 Python coding style 規範的 docstring

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 使用方式

### 1. 配置設定檔

編輯 `config.yaml` 檔案，填入您的登入資訊：

```yaml
# 身份證字號
person_id: "YOUR_PERSON_ID"

# 帳號
account: "YOUR_ACCOUNT"

# 密碼
password: "YOUR_PASSWORD"

# CA 密碼
ca_password: "YOUR_CA_PASSWORD"
```

### 2. 使用 Config 類別

```python
from config import Config

# 載入配置
config = Config('config.yaml')

# 存取配置參數
print(config.person_id)
print(config.account)
print(config.password)
print(config.ca_password)
```

## 錯誤處理

Config 類別提供了完善的錯誤處理機制：

- `ConfigFileNotFoundError`: 當配置檔案不存在時拋出
- `ConfigReadError`: 當讀取配置檔案失敗時拋出
- `ConfigValidationError`: 當配置參數驗證失敗時拋出

### 使用範例

```python
from config import Config, ConfigFileNotFoundError, ConfigValidationError

try:
    config = Config('config.yaml')
except ConfigFileNotFoundError:
    print("配置檔案不存在，請檢查檔案路徑")
except ConfigValidationError as e:
    print(f"配置參數驗證失敗: {e}")
except Exception as e:
    print(f"發生未預期的錯誤: {e}")
```

## 執行測試

```bash
# 執行所有測試
pytest test_config.py -v

# 執行特定測試
pytest test_config.py::TestConfig::test_yaml_file_not_exists_should_raise_exception -v
```

## 測試覆蓋範圍

專案包含完整的單元測試，涵蓋以下測試案例：

1. ✅ 當 YAML 檔案不存在時，應該 raise 例外
2. ✅ 當 YAML 檔案存在時，應該成功讀取
3. ✅ 當 YAML 檔案存在時，應該驗證格式是否符合 schema
4. ✅ 當驗證參數通過時，config 屬性應該存成類別中的屬性
5. ✅ 當驗證參數失敗時，應該 raise 例外
6. ✅ 當 YAML 檔案存在且讀取失敗，應該 raise 例外
7. ✅ Config 物件的字串表示應該遮蔽密碼

## 專案結構

```
sample-trading/
├── config.py           # Config 類別實作
├── config.yaml         # 配置檔案模板
├── yaml_sample.yaml    # 測試用範例配置
├── test_config.py      # 單元測試
├── requirements.txt    # 專案依賴
└── README.md          # 專案說明文件
```

## 參考資料

- [永豐 SDK 登入規格](https://sinotrade.github.io/zh/tutor/login/)

## 設計原則

本專案遵循以下設計原則：

- **簡潔直觀**: 避免過度設計，程式碼清晰易懂
- **完整文檔**: 所有函數都有詳細的 docstring
- **測試驅動**: 完整的單元測試確保程式碼品質
- **錯誤處理**: 清楚的錯誤訊息幫助快速定位問題

## 授權

請參閱 LICENSE 檔案
