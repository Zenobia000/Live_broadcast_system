# 專案結構指南 - 智能簽到系統

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-10-13`
**主要作者 (Lead Author):** `[技術負責人]`
**狀態 (Status):** `活躍 (Active)`

---

## 1. 指南目的 (Purpose of This Guide)

*   為 `智能簽到系統` 提供一個標準化、可擴展且易於理解的目錄和文件結構。
*   確保團隊成員能夠快速定位代碼、配置文件和文檔，降低新成員的上手成本。
*   促進代碼的模塊化和關注點分離，遵循 Clean Architecture 原則。

## 2. 核心設計原則 (Core Design Principles)

*   **按領域組織 (Organize by Domain):** 相關的業務領域（例如，出缺勤、請假、使用者）應盡可能放在一起，而不是按技術類型（e.g., `routers`, `models`）分散在各處。
*   **明確的職責 (Clear Responsibilities):** 每個頂層目錄都應該有其單一、明確的職責。
*   **一致的命名 (Consistent Naming):** 文件和目錄的命名應遵循一致的、可預測的約定。
*   **配置外部化 (Externalized Configuration):** 應用程式的配置應與代碼分離。
*   **根目錄簡潔 (Clean Root Directory):** 根目錄應只包含專案級別的文件。

## 3. 頂層目錄結構 (Top-Level Directory Structure)

```plaintext
smart-attendance-system/
├── .github/              # CI/CD 工作流程 (GitHub Actions)
├── .vscode/              # VS Code 編輯器特定配置
├── api/                  # OpenAPI 定義文件 (openapi.yaml)
├── configs/              # 環境配置文件 (e.g., settings.toml)
├── docs/                 # 專案文檔 (PRD, SAD, API Spec, etc.)
├── scripts/              # 開發和運維腳本 (e.g., run_migrations.py)
├── src/                  # 應用程式的 Python 原始碼
│   └── attendance_system/  # 專案主應用程式包
├── tests/                # 所有測試代碼
├── .dockerignore         # Docker 忽略文件
├── .gitignore            # Git 忽略文件
├── .pre-commit-config.yaml # pre-commit 鉤子配置
├── LICENSE               # 專案許可證
├── pyproject.toml        # Poetry 依賴與專案配置
└── README.md             # 專案介紹和快速入門指南
```

## 4. 目錄詳解 (Directory Breakdown)

### 4.1 `src/attendance_system/` - 應用程式原始碼

*   這是專案的核心，所有 Python 原始碼都應放在這裡，並遵循 Clean Architecture 分層。

```plaintext
src/attendance_system/
├── __init__.py
├── main.py                     # 應用程式入口點 (FastAPI instance)
│
├── core/                       # 核心邏輯，跨功能共享
│   ├── __init__.py
│   ├── config.py             # 配置加載 (Pydantic settings)
│   └── security.py           # JWT 處理、密碼學等
│
├── domains/                    # Domain Layer: 核心業務領域模型
│   ├── __init__.py
│   ├── attendance/
│   │   ├── entities.py       # Attendance 實體
│   │   ├── repositories.py   # Attendance Repository 抽象接口
│   │   └── exceptions.py     # 自定義領域例外
│   └── leaves/
│       ├── entities.py       # LeaveRequest 實體
│       └── ...
│
├── application/                # Application Layer: 應用程式邏輯 (Use Cases)
│   ├── __init__.py
│   └── attendance/
│       ├── __init__.py
│       ├── use_cases.py      # e.g., RecordAutoAttendanceUseCase
│       └── dtos.py           # 數據傳輸對象 (DTOs)
│
└── infrastructure/             # Infrastructure Layer: 外部世界的實現
    ├── __init__.py
    ├── web/                    # API 接口層 (FastAPI Routers)
    │   ├── __init__.py
    │   ├── auth_router.py
    │   └── attendance_router.py
    ├── persistence/            # 持久化層 (PostgreSQL)
    │   ├── __init__.py
    │   ├── models/           # SQLAlchemy ORM 模型
    │   │   └── attendance_model.py
    │   └── repositories/     # Repository 接口的具體實現
    │       └── attendance_repo.py
    └── clients/                # 第三方服務客戶端
        └── google_calendar_client.py
```

### 4.2 `tests/` - 測試代碼

*   測試代碼應與 `src` 目錄結構保持一致，以便清晰地對應到被測試的代碼。

```plaintext
tests/
├── conftest.py               # Pytest 的全局 fixtures
├── factories.py              # 測試數據工廠 (factory-boy)
├── integration/              # 整合測試 (e.g., 測試 Use Case 到 DB 的完整流程)
│   └── application/
│       └── attendance/
│           └── test_attendance_use_cases.py
└── unit/                     # 單元測試 (e.g., 測試單一 Domain Entity 的邏輯)
    └── domains/
        └── attendance/
            └── test_attendance_entities.py
```

### 4.3 `docs/` - 文檔

*   所有與專案相關的長篇文檔都應存放在此，即當前您正在閱讀的系列文件。

```plaintext
docs/
├── 01_project_brief_and_prd.md
├── 02_behavior_driven_development.feature
├── 03_architecture_and_design_document.md
├── 04_api_design_specification.md
├── 05_module_specification_and_tests.md
├── 06_project_structure_guide.md
└── adrs/
    └── adr-001-tech-stack-selection.md
```
