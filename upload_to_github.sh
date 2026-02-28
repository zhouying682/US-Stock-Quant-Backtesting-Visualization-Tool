#!/bin/bash

# 美股量化回测和可视化工具 - GitHub上传脚本

echo "=========================================="
echo "GitHub上传指南"
echo "=========================================="
echo ""

# 检查是否已配置远程仓库
if git remote -v | grep -q "origin"; then
    echo "✓ 已配置远程仓库"
    git remote -v
    echo ""
    echo "直接运行以下命令推送代码:"
    echo "  git push -u origin main"
    exit 0
fi

echo "请选择上传方式:"
echo ""
echo "方式一: 使用GitHub CLI (推荐)"
echo "  1. 运行: gh auth login"
echo "  2. 然后运行: gh repo create 美股量化回测和可视化工具 --public --source=. --remote=origin --push"
echo ""
echo "方式二: 手动创建仓库"
echo "  1. 访问 https://github.com/new 创建新仓库"
echo "  2. 仓库名称: 美股量化回测和可视化工具 (或您喜欢的名称)"
echo "  3. 选择 Public 或 Private"
echo "  4. 不要勾选 'Initialize this repository with a README'"
echo "  5. 创建仓库后，运行以下命令:"
echo ""
echo "     git remote add origin https://github.com/您的用户名/仓库名.git"
echo "     git branch -M main"
echo "     git push -u origin main"
echo ""
echo "=========================================="
