#!/bin/bash

# Nmap NSE 路由压力测试插件安装脚本
# 适用于Kali Linux系统

set -e

echo "=== Nmap NSE 路由压力测试插件安装脚本 ==="
echo

# 检查是否以root权限运行
if [[ $EUID -ne 0 ]]; then
    echo "❌ 此脚本需要root权限运行"
    echo "请使用: sudo $0"
    exit 1
fi

echo "✅ 检查权限通过"

# 检查系统是否为Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ 此脚本仅支持Linux系统"
    exit 1
fi

echo "✅ 系统兼容性检查通过"

# 更新包管理器
echo "📦 更新包管理器..."
if command -v apt-get &> /dev/null; then
    apt-get update -q
elif command -v yum &> /dev/null; then
    yum update -y -q
elif command -v dnf &> /dev/null; then
    dnf update -y -q
else
    echo "⚠️  未识别的包管理器，请手动安装依赖"
fi

# 安装依赖包
echo "📦 安装依赖包..."

# 检查并安装nmap
if ! command -v nmap &> /dev/null; then
    echo "安装 nmap..."
    if command -v apt-get &> /dev/null; then
        apt-get install -y nmap
    elif command -v yum &> /dev/null; then
        yum install -y nmap
    elif command -v dnf &> /dev/null; then
        dnf install -y nmap
    fi
else
    echo "✅ nmap 已安装"
fi

# 检查并安装arp-scan
if ! command -v arp-scan &> /dev/null; then
    echo "安装 arp-scan..."
    if command -v apt-get &> /dev/null; then
        apt-get install -y arp-scan
    elif command -v yum &> /dev/null; then
        yum install -y arp-scan
    elif command -v dnf &> /dev/null; then
        dnf install -y arp-scan
    fi
else
    echo "✅ arp-scan 已安装"
fi

# 检查并安装hping3
if ! command -v hping3 &> /dev/null; then
    echo "安装 hping3..."
    if command -v apt-get &> /dev/null; then
        apt-get install -y hping3
    elif command -v yum &> /dev/null; then
        yum install -y hping3
    elif command -v dnf &> /dev/null; then
        dnf install -y hping3
    fi
else
    echo "✅ hping3 已安装"
fi

# 查找Nmap脚本目录
echo "🔍 查找Nmap脚本目录..."

NMAP_SCRIPTS_DIR=""
POSSIBLE_DIRS=(
    "/usr/share/nmap/scripts"
    "/usr/local/share/nmap/scripts"
    "/opt/nmap/scripts"
    "/usr/share/nmap-scripts"
)

for dir in "${POSSIBLE_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        NMAP_SCRIPTS_DIR="$dir"
        break
    fi
done

if [[ -z "$NMAP_SCRIPTS_DIR" ]]; then
    echo "❌ 未找到Nmap脚本目录"
    echo "请手动将route-stress-test.nse复制到Nmap脚本目录"
    exit 1
fi

echo "✅ 找到Nmap脚本目录: $NMAP_SCRIPTS_DIR"

# 复制NSE脚本
echo "📄 安装NSE脚本..."

SCRIPT_FILE="route-stress-test.nse"
if [[ ! -f "$SCRIPT_FILE" ]]; then
    echo "❌ 未找到脚本文件: $SCRIPT_FILE"
    echo "请确保脚本文件在当前目录中"
    exit 1
fi

cp "$SCRIPT_FILE" "$NMAP_SCRIPTS_DIR/"
echo "✅ 脚本已复制到: $NMAP_SCRIPTS_DIR/$SCRIPT_FILE"

# 设置正确的权限
chmod 644 "$NMAP_SCRIPTS_DIR/$SCRIPT_FILE"
echo "✅ 脚本权限设置完成"

# 更新Nmap脚本数据库
echo "🔄 更新Nmap脚本数据库..."
nmap --script-updatedb

echo "✅ 脚本数据库更新完成"

# 验证安装
echo "🧪 验证安装..."

if nmap --script-help route-stress-test &> /dev/null; then
    echo "✅ NSE脚本安装成功！"
else
    echo "❌ NSE脚本安装验证失败"
    exit 1
fi

# 显示使用示例
echo
echo "=== 安装完成 ==="
echo
echo "📋 使用示例："
echo "  基本使用:    sudo nmap --script route-stress-test"
echo "  指定接口:    sudo nmap --script route-stress-test --script-args \"interface=wlan0\""
echo "  压力测试:    sudo nmap --script route-stress-test --script-args \"stress-type=hping,count=100\""
echo "  查看帮助:    nmap --script-help route-stress-test"
echo
echo "📖 详细文档请查看: NSE_INSTALL.md"
echo
echo "⚠️  安全提醒: 请仅在授权网络中使用此工具"
echo

# 询问是否立即测试
read -p "是否立即进行测试运行？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 开始测试运行..."
    echo "注意: 这将扫描当前网络，请确保您有权限进行此操作"
    sleep 3
    
    nmap --script route-stress-test --script-args "count=5" || true
fi

echo
echo "🎉 安装和配置完成！"