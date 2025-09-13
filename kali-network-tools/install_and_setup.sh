#!/bin/bash
"""
Kali网络安全工具 - 一键安装和设置脚本
"""

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数: 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 函数: 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 函数: 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_message $RED "❌ 请不要使用root用户运行此脚本"
        print_message $YELLOW "💡 正确用法: ./install_and_setup.sh"
        exit 1
    fi
}

# 函数: 检查系统
check_system() {
    print_message $BLUE "🔍 检查系统环境..."
    
    if [[ ! -f /etc/os-release ]]; then
        print_message $RED "❌ 无法检测操作系统"
        exit 1
    fi
    
    source /etc/os-release
    
    if [[ "$ID" == "kali" ]]; then
        print_message $GREEN "✅ 检测到 Kali Linux"
        PACKAGE_MANAGER="apt-get"
    elif [[ "$ID" == "ubuntu" ]] || [[ "$ID" == "debian" ]]; then
        print_message $YELLOW "⚠️  检测到 $PRETTY_NAME (部分功能可能不可用)"
        PACKAGE_MANAGER="apt-get"
    else
        print_message $RED "❌ 不支持的操作系统: $PRETTY_NAME"
        print_message $YELLOW "💡 推荐使用 Kali Linux"
        exit 1
    fi
}

# 函数: 安装系统工具
install_system_tools() {
    print_message $BLUE "📦 安装系统依赖工具..."
    
    # 更新包列表
    print_message $YELLOW "更新包列表..."
    sudo $PACKAGE_MANAGER update
    
    # 基础网络工具
    BASIC_TOOLS="nmap hping3 netdiscover masscan nikto whatweb dnsrecon net-tools iputils-ping"
    
    print_message $YELLOW "安装基础网络工具..."
    for tool in $BASIC_TOOLS; do
        if command_exists $tool; then
            print_message $GREEN "✅ $tool 已安装"
        else
            print_message $YELLOW "📥 安装 $tool..."
            if sudo $PACKAGE_MANAGER install -y $tool; then
                print_message $GREEN "✅ $tool 安装完成"
            else
                print_message $RED "❌ $tool 安装失败"
            fi
        fi
    done
}

# 函数: 创建桌面快捷方式
create_desktop_shortcut() {
    print_message $BLUE "🖥️  创建桌面快捷方式..."
    
    DESKTOP_DIR="$HOME/Desktop"
    CURRENT_DIR="$(pwd)"
    
    if [[ -d "$DESKTOP_DIR" ]]; then
        cat > "$DESKTOP_DIR/Kali网络工具.desktop" << EOF
[Desktop Entry]
Name=Kali网络安全工具
Comment=综合网络安全测试和扫描工具
Exec=cd "$CURRENT_DIR" && ./kali-scanner-launcher
Icon=security-high
Terminal=true
Type=Application
Categories=Security;Network;
EOF
        
        chmod +x "$DESKTOP_DIR/Kali网络工具.desktop"
        print_message $GREEN "✅ 桌面快捷方式已创建"
    else
        print_message $YELLOW "⚠️  未找到桌面目录，跳过快捷方式创建"
    fi
}

# 函数: 设置别名
setup_aliases() {
    print_message $BLUE "🔗 设置命令别名..."
    
    CURRENT_DIR="$(pwd)"
    BASHRC="$HOME/.bashrc"
    
    # 检查是否已存在别名
    if grep -q "# Kali Network Tools Aliases" "$BASHRC"; then
        print_message $YELLOW "⚠️  别名已存在，跳过设置"
        return
    fi
    
    cat >> "$BASHRC" << EOF

# Kali Network Tools Aliases
alias kali-net='cd "$CURRENT_DIR" && ./kali-network-tester'
alias kali-launcher='cd "$CURRENT_DIR" && ./kali-scanner-launcher'
alias kali-comprehensive='cd "$CURRENT_DIR" && sudo ./kali-network-tester --comprehensive'
EOF
    
    print_message $GREEN "✅ 命令别名已添加到 ~/.bashrc"
    print_message $YELLOW "💡 重新加载终端或运行 'source ~/.bashrc' 生效"
}

# 函数: 验证安装
verify_installation() {
    print_message $BLUE "🔬 验证安装..."
    
    # 检查可执行文件
    if [[ -x "./kali-network-tester" ]]; then
        print_message $GREEN "✅ 主程序可执行"
    else
        print_message $RED "❌ 主程序不可执行"
        return 1
    fi
    
    if [[ -x "./kali-scanner-launcher" ]]; then
        print_message $GREEN "✅ 启动器可执行"
    else
        print_message $RED "❌ 启动器不可执行"
        return 1
    fi
    
    # 检查关键工具
    CRITICAL_TOOLS="nmap ping"
    for tool in $CRITICAL_TOOLS; do
        if command_exists $tool; then
            print_message $GREEN "✅ $tool 可用"
        else
            print_message $RED "❌ $tool 不可用"
            return 1
        fi
    done
    
    return 0
}

# 函数: 显示使用说明
show_usage() {
    print_message $GREEN "🎉 安装完成！"
    print_message $BLUE "="*60
    
    echo -e "${GREEN}📖 使用方法:${NC}"
    echo -e "${YELLOW}   交互式启动器 (推荐新手):${NC}"
    echo -e "   ./kali-scanner-launcher"
    echo -e "   ${BLUE}或使用别名:${NC} kali-launcher"
    echo
    echo -e "${YELLOW}   命令行模式 (高级用户):${NC}"
    echo -e "   ./kali-network-tester --help"
    echo -e "   ${BLUE}或使用别名:${NC} kali-net --help"
    echo
    echo -e "${YELLOW}   常用命令示例:${NC}"
    echo -e "   kali-comprehensive              # 综合扫描"
    echo -e "   kali-net -t 192.168.1.1 --tests ping nmap  # 指定目标测试"
    echo -e "   kali-net --web-scan -t 192.168.1.100       # Web服务扫描"
    echo
    echo -e "${RED}⚠️  重要提示:${NC}"
    echo -e "   • 某些功能需要root权限，请使用sudo运行"
    echo -e "   • 仅在授权的网络环境中使用"
    echo -e "   • 使用前请了解相关法律法规"
    
    print_message $BLUE "="*60
}

# 主函数
main() {
    print_message $GREEN "🚀 Kali网络安全工具 - 一键安装程序"
    print_message $BLUE "="*60
    
    # 前置检查
    check_root
    check_system
    
    # 安装过程
    install_system_tools
    
    # 设置便利功能
    create_desktop_shortcut
    setup_aliases
    
    # 验证安装
    if verify_installation; then
        show_usage
    else
        print_message $RED "❌ 安装验证失败"
        exit 1
    fi
    
    print_message $GREEN "✨ 享受你的网络安全工具吧！"
}

# 错误处理
trap 'print_message $RED "❌ 安装过程中发生错误，请检查输出信息"; exit 1' ERR

# 运行主函数
main "$@"