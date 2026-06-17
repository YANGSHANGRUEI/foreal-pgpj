# 專案交接文件（HANDOFF）

> 給新對話的 AI 與使用者：開工前先讀本檔，再依「駕訓班」一次一步開發。

## 專案名稱

**法律申論題交流平台**（`law-essay-platform`）

## 一句話描述

Streamlit 多頁應用：上傳申論作答賺代幣（+3），花代幣解鎖他人作答（-1）；帳號與上傳者去識別化。

## 如何執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

瀏覽器左側會出現：`register`、`login`、`upload`、`browse`、`profile` 等分頁。

---

## 目錄結構（截至四週雛形完成）

```
law-essay-platform/
├── app.py                 # 主玄關（標題 + 說明）
├── pages/
│   ├── register.py        # 註冊
│   ├── login.py           # 登入／登出、顯示代幣
│   ├── upload.py          # 上傳（需登入）
│   ├── browse.py          # 瀏覽／解鎖（需登入）
│   └── profile.py         # 個人儀表板（需登入）
├── utils/
│   ├── session.py         # 登入狀態、current_session.json、HMAC 簽章
│   └── user_store.py      # 代幣加減（檔案鎖）
├── data/                  # 本機資料（.gitignore，勿 commit）
│   ├── users.json
│   ├── answers.csv
│   └── current_session.json
├── requirements.txt       # streamlit>=1.30.0
├── .gitignore             # 含 data/
└── HANDOFF.md             # 本檔
```

---

## 資料流

```
註冊 → users.json（password_hash, tokens=0）
登入 → session_state + current_session.json（user_id + sig）
上傳 → answers.csv 新增一列 + users.json tokens += 3
解鎖 → users.json tokens -= 1，unlocked 追加 unlock_id
```

### `users.json` 範例結構

```json
{
  "testuser": {
    "password_hash": "6ca13d52ca70c883e0f0bb101e425a89e8624de51db2d2392593af6a84118090",
    "tokens": 0,
    "unlocked": ["民法::2026-05-27T12:16:40.917162"]
  }
}
```

### `answers.csv` 欄位

| 欄位 | 說明 |
|------|------|
| `subject` | 科目 |
| `answer_text` | 作答內容 |
| `upload_time` | ISO 時間（程式自動） |
| `uploader_id` | 登入者去識別化代號（SHA-256 帳號前 12 字） |

特殊值：`uploader_id == "legacy_anonymous"` 為第一週舊資料，**browse 不開放解鎖**。

### `current_session.json`

```json
{
  "user_id": "ae5deb822e0d",
  "sig": "..."
}
```

- 用途：瀏覽器刷新後恢復登入（`restore_login`）。
- **不可**存明文 `username`（已修正）。
- 登入成功後才會寫入 `sig`；舊檔無 `sig` 需重新登入一次。

---

## 已完成能力（整合測試 10 步已全過）

- [x] 註冊（防空白、防重複帳號）
- [x] 登入（雜湊比對、模糊錯誤訊息）
- [x] 登出、刷新恢復登入（session 備份 + sig）
- [x] 未登入無法 upload／browse（`st.stop()`）
- [x] 上傳驗證、寫入 CSV、+3 代幣
- [x] 防重複上傳（`strip()` 標準化）
- [x] 解鎖 -1、代幣不足擋住
- [x] `legacy_anonymous` 不開放
- [x] profile 三欄 metric（代幣／上傳數／解鎖數）

---

## 已知限制（優化時注意）

| 項目 | 說明 |
|------|------|
| `SESSION_SECRET` | 寫在 `utils/session.py`，本機學習用；上線應改環境變數 |
| `current_session.json` | 本機「最後登入者」備份，不適合多人正式環境 |
| `user_store.py` 的 `fcntl` | macOS/Linux 可用；Windows 需另案 |
| 雲端部署 | `data/` 不進 git，部署後資料為空，需重新註冊 |
| `README.md` | 部分描述與現況可能不同步，以本檔與程式為準 |

---

## 建議下一階段功能（自行排優先）

1. 上傳欄位擴充：考卷標題、分數
2. browse 依科目／考卷分組顯示
3. profile 列出已解鎖清單明細
4. `SESSION_SECRET` 改 `st.secrets` 或環境變數
5. Streamlit Cloud 部署
6. 主頁 `app.py` 導覽整合（可選）

**每項應拆成多個「一個小單位」完成。**

---

## 新對話開場範本（可複製）

```text
請先讀 HANDOFF.md 與 .cursor/rules/，以駕訓班教練模式協助我。
專案路徑：/Users/loyahsuan/cursor/law-essay-platform
本次只做一個小單位：<你的需求>
改動須標明檔案與行數，結尾踩煞車並只出 1 題。
```

---

## 四週學習對照（給使用者複習）

| 週 | 重點 |
|----|------|
| 1 | Streamlit 介面、變數、CSV 讀寫 |
| 2 | 註冊登入、雜湊、session_state、去識別化 |
| 3 | 代幣經濟、解鎖、防弊、profile |
| 4 | 隱私審查、安全修補、UI、整合測試、部署概念 |

---

*最後更新：四週雛形完成後建立，供新對話接力開發。*
