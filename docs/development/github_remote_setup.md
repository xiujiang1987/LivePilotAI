# GitHub 遠端倉庫設置指南

## 步驟 1: 在 GitHub 上創建新倉庫

1. 登入你的 GitHub 帳號
2. 點擊右上角的 "+" 圖示，選擇 "New repository"
3. 填寫倉庫資訊：
   - **Repository name**: `LivePilotAI`
   - **Description**: `AI-powered real-time emotion detection and live streaming effects system`
   - **Visibility**: 選擇 Public 或 Private
   - **不要** 勾選 "Initialize this repository with a README"（因為我們已有本地程式碼）
4. 點擊 "Create repository"

## 步驟 2: 設置遠端倉庫

GitHub 會顯示設置指令，使用以下命令連接本地倉庫：

```powershell
# 進入專案目錄
cd "D:\AI_Park\Workspace\dev_projects\ai\LivePilotAI"

# 加入遠端倉庫（將 YOUR_USERNAME 替換為你的 GitHub 使用者名稱）
git remote add origin https://github.com/YOUR_USERNAME/LivePilotAI.git

# 推送程式碼到遠端倉庫
git push -u origin master
```

## 步驟 3: 驗證推送成功

```powershell
# 檢查遠端設定
git remote -v

# 檢查推送狀態
git status
```

## 步驟 4: 後續推送

設置完成後，未來的推送只需要：

```powershell
git add .
git commit -m "commit message"
git push
```

## GitHub 倉庫建議設置

### 分支保護規則
1. 進入倉庫設置 > Branches
2. 為 `master` 分支設置保護規則：
   - Require status checks to pass before merging
   - Require branches to be up to date before merging

### GitHub Actions
- 我們已經設置了 `.github/workflows/ci.yml`
- 推送後會自動運行測試和程式碼品質檢查

### Issues 和 Projects
- 可以啟用 Issues 來追蹤 bug 和功能請求
- 使用 Projects 來管理開發進度

## 注意事項

1. **認證設置**: 如果使用 HTTPS，可能需要設置 Personal Access Token
2. **SSH 金鑰**: 推薦使用 SSH 金鑰來避免每次輸入密碼
3. **大檔案**: 如果有大型 AI 模型檔案，考慮使用 Git LFS

## 相關連結

- [GitHub 官方文檔](https://docs.github.com/)
- [Git 設置 SSH 金鑰](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [Personal Access Token 設置](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
