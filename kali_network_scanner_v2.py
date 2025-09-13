#!/usr/bin/env python3
"""
Kali Linux 网络安全自动化测试工具 - 快速启动脚本 v2.0
版本: 2.0
作者: Network Security Team
描述: 提供友好的交互式界面进行网络安全测试
"""

import sys
import subprocess
import os
import json
import time
from pathlib import Path

def check_dependencies():
    """检查必要的依赖工具"""
    tools = ['ping', 'hping3', 'nmap', 'netdiscover', 'masscan', 'nikto', 'whatweb', 'dnsrecon']
    missing = []
    
    for tool in tools:
        try:
            subprocess.run(['which', tool], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            missing.append(tool)
    
    if missing:
        print(f"⚠️  缺少以下工具: {', '.join(missing)}")
        print("请运行以下命令安装:")
        print("sudo apt update && sudo apt install hping3 nmap netdiscover masscan nikto whatweb dnsrecon")
        return False
    return True

def show_banner():
    """显示程序横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🔒 Kali Linux 网络安全自动化测试工具 v2.0                ║
║                                                              ║
║    ⚠️  仅用于授权网络的安全测试和教育目的                    ║
║    📧 如有问题请联系: security-team@example.com              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def view_reports():
    """查看历史扫描报告"""
    print("\n📄 历史扫描报告:")
    report_files = list(Path('.').glob('network_scan_report_*.json'))
    
    if not report_files:
        print("未找到历史报告")
        return
    
    for i, report_file in enumerate(sorted(report_files, reverse=True)[:10]):
        timestamp = report_file.stem.split('_')[-1]
        date_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))
        print(f"{i+1}. {report_file.name} ({date_str})")
    
    try:
        choice = int(input("\n选择要查看的报告 (输入数字): ")) - 1
        if 0 <= choice < len(report_files):
            selected_file = sorted(report_files, reverse=True)[choice]
            print(f"\n正在打开报告: {selected_file}")
            
            # 尝试用默认程序打开HTML报告
            html_file = selected_file.with_suffix('.html')
            if html_file.exists():
                subprocess.run(['xdg-open', str(html_file)])
            else:
                # 显示JSON报告摘要
                with open(selected_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"扫描时间: {data.get('scan_date', 'Unknown')}")
                print(f"发现主机: {len(data.get('hosts', []))} 个")
                print(f"开放端口主机: {len(data.get('open_ports', {}))} 个")
        else:
            print("无效选择")
    except (ValueError, IndexError):
        print("无效输入")

def show_config_menu():
    """显示配置菜单"""
    print("\n🛠️ 工具配置:")
    print("1. 检查工具依赖")
    print("2. 设置默认网络范围")
    print("3. 清理历史报告")
    print("4. 返回主菜单")
    
    choice = input("\n选择配置选项 (1-4): ").strip()
    
    if choice == "1":
        print("\n🔍 检查依赖工具...")
        check_dependencies()
    elif choice == "2":
        network = input("输入默认网络范围 (如: 192.168.1.0/24): ").strip()
        if network:
            # 这里可以保存配置到文件
            print(f"✅ 已设置默认网络范围: {network}")
    elif choice == "3":
        clean_reports()
    elif choice == "4":
        return
    else:
        print("❌ 无效选择")

def clean_reports():
    """清理历史报告"""
    report_files = list(Path('.').glob('network_scan_report_*.*'))
    
    if not report_files:
        print("没有找到历史报告文件")
        return
    
    print(f"\n找到 {len(report_files)} 个报告文件")
    confirm = input("确认删除所有历史报告? (y/N): ").strip().lower()
    
    if confirm == 'y':
        for file in report_files:
            try:
                file.unlink()
                print(f"✅ 已删除: {file.name}")
            except Exception as e:
                print(f"❌ 删除失败 {file.name}: {e}")
        print("\n🗑️ 历史报告清理完成")
    else:
        print("取消清理操作")

def main():
    show_banner()
    
    # 检查依赖工具
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请安装缺少的工具后重试")
        sys.exit(1)
    
    while True:
        print("\n" + "="*60)
        print("📋 选择测试操作:")
        print("="*60)
        print("1. 📊 显示路由信息")
        print("2. ⚡ 基础压力测试")
        print("3. 🔍 综合网络扫描 (推荐)")
        print("4. 🌐 Web服务扫描")
        print("5. 🔎 DNS枚举")
        print("6. ⚙️  自定义扫描")
        print("7. 📄 查看历史报告")
        print("8. 🛠️  工具配置")
        print("0. 🚪 退出程序")
        print("="*60)
        
        choice = input("\n请选择 (0-8): ").strip()
        
        if choice == "0":
            print("👋 退出程序")
            break
        elif choice == "1":
            subprocess.run([sys.executable, "route_stress_test.py", "--show-routes"])
        elif choice == "2":
            count = input("输入测试包数量 (默认50): ").strip() or "50"
            subprocess.run([sys.executable, "route_stress_test.py", "-c", count])
        elif choice == "3":
            network = input("输入网络范围 (默认自动检测): ").strip()
            cmd = [sys.executable, "route_stress_test.py", "--comprehensive"]
            if network:
                cmd.extend(["--network", network])
            print("注意: 需要sudo权限")
            subprocess.run(cmd)
        elif choice == "4":
            target = input("输入目标IP地址: ").strip()
            if target:
                subprocess.run([sys.executable, "route_stress_test.py", "--web-scan", "-t", target])
        elif choice == "5":
            domain = input("输入域名: ").strip()
            if domain:
                subprocess.run([sys.executable, "route_stress_test.py", "--dns-enum", domain])
        elif choice == "6":
            print("\n⚙️ 自定义扫描选项:")
            print("命令格式: python3 route_stress_test.py [参数]")
            print("常用参数: --help 查看所有选项")
            cmd = input("输入完整命令参数: ").strip()
            if cmd:
                subprocess.run([sys.executable, "route_stress_test.py"] + cmd.split())
        elif choice == "7":
            view_reports()
        elif choice == "8":
            show_config_menu()
        else:
            print("❌ 无效选择，请重试")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断，安全退出程序")
        print("感谢使用 Kali Linux 网络安全测试工具！")
    except Exception as e:
        print(f"❌ 程序错误: {e}")
        print("如果问题持续存在，请联系技术支持")
    finally:
        print("\n👋 程序已退出")