#!/bin/bash

# GitHub推送脚本 - 方式二（手动创建仓库后使用）

echo "=========================================="
echo "GitHub代码推送脚本"
echo "=========================================="
echo ""

# 检查是否已配置远程仓库
if git remote -v | grep -q "origin"; then
    echo "✓ 已配置远程仓库:"
    git remote -v
    echo ""
    read -p "是否要推送代码到现有远程仓库? (y/n): " confirm
    if [ "$confirm" = "y" ]; then
        git push -u origin main
        echo ""
        echo "✓ 代码已成功推送！"
    fi
    exit 0
fi

# 获取仓库名称
echo "请在GitHub上创建新仓库后，输入以下信息："
echo ""
read -p "GitHub用户名 [默认: zhouying682]: " username
username=${username:-zhouying682}

read -p "仓库名称: " repo_name

if [ -z "$repo_name" ]; then
    echo "错误: 仓库名称不能为空"
    exit 1
fi

# 选择协议
echo ""
echo "选择连接方式:"
echo "1) HTTPS (推荐，需要输入密码或token)"
echo "2) SSH (需要配置SSH密钥)"
read -p "请选择 (1/2) [默认: 1]: " protocol
protocol=${protocol:-1}

if [ "$protocol" = "2" ]; then
    remote_url="git@github.com:${username}/${repo_name}.git"
else
    remote_url="https://github.com/${username}/${repo_name}.git"
fi

echo ""
echo "将添加远程仓库: $remote_url"
read -p "确认添加并推送? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "已取消"
    exit 0
fi

# 添加远程仓库
echo ""
echo "正在添加远程仓库..."
git remote add origin "$remote_url"

# 确保分支名为main
git branch -M main

# 推送代码
echo ""
echo "正在推送代码到GitHub..."
if git push -u origin main; then
    echo ""
    echo "=========================================="
    echo "✓ 代码已成功推送到GitHub！"
    echo "=========================================="
    echo ""
    echo "仓库地址: https://github.com/${username}/${repo_name}"
    echo ""
else
    echo ""
    echo "推送失败，请检查："
    echo "1. 仓库是否已创建"
    echo "2. 仓库名称是否正确"
    echo "3. 是否有推送权限"
    echo "4. 如果使用HTTPS，可能需要输入GitHub token（不是密码）"
    echo ""
    echo "如需重新配置，运行: git remote remove origin"
    exit 1
fi
