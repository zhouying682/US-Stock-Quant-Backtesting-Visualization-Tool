# GitHub上传指南

项目已准备好上传到GitHub。请按照以下步骤操作：

## 当前状态
- ✅ Git仓库已初始化
- ✅ 代码已提交到本地仓库
- ✅ .gitignore已配置（忽略CSV、PNG、TXT等数据文件）

## 上传方式

### 方式一：使用GitHub CLI（推荐）

**步骤：**

1. **重新登录GitHub CLI**（如果token已过期）:
   ```bash
   gh auth login
   ```
   按照提示选择：
   - GitHub.com
   - HTTPS
   - 登录方式（浏览器或token）

2. **创建仓库并推送代码**:
   ```bash
   cd "/Users/zhouying/Desktop/美股量化回测和可视化工具"
   gh repo create 美股量化回测和可视化工具 --public --source=. --remote=origin --push
   ```
   
   如果要创建私有仓库，使用：
   ```bash
   gh repo create 美股量化回测和可视化工具 --private --source=. --remote=origin --push
   ```

### 方式二：手动创建仓库

**步骤：**

1. **在GitHub上创建新仓库**:
   - 访问 https://github.com/new
   - 仓库名称: `美股量化回测和可视化工具` (或您喜欢的名称)
   - 选择 Public 或 Private
   - ⚠️ **不要**勾选 "Initialize this repository with a README"
   - 点击 "Create repository"

2. **添加远程仓库并推送**:
   ```bash
   cd "/Users/zhouying/Desktop/美股量化回测和可视化工具"
   
   # 添加远程仓库（将 YOUR_USERNAME 替换为您的GitHub用户名）
   git remote add origin https://github.com/YOUR_USERNAME/美股量化回测和可视化工具.git
   
   # 确保分支名为main
   git branch -M main
   
   # 推送代码
   git push -u origin main
   ```

3. **如果使用SSH**:
   ```bash
   git remote add origin git@github.com:YOUR_USERNAME/美股量化回测和可视化工具.git
   git branch -M main
   git push -u origin main
   ```

## 验证上传

上传成功后，访问您的GitHub仓库页面，应该能看到：
- README.md
- 所有Python源代码文件
- .gitignore文件

注意：CSV、PNG、TXT等数据文件不会上传（已在.gitignore中配置）

## 后续更新

以后如果有代码更新，使用以下命令：
```bash
git add .
git commit -m "更新说明"
git push
```
