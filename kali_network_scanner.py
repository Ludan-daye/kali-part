#!/usr/bin/env python3
"""
Kali Linux 网络安全自动化测试工具 - 快速启动脚本
版本: 2.0
作者: Network Security Team
描述: 提供友好的交互式界面进行网络安全测试
"""

import sys
import subprocess
import os
from pathlib import Path

def main():
    print("🔒 Kali Linux 网络安全自动化测试工具")
    print("=" * 50)
    
    while True:
        print("\n选择操作:")
        print("1. 显示路由信息")
        print("2. 基础压力测试")
        print("3. 综合网络扫描")
        print("4. Web服务扫描")
        print("5. DNS枚举")
        print("6. 自定义扫描")
        print("0. 退出")
        
        choice = input("\n请选择 (0-6): ").strip()
        
        if choice == "0":
            print("退出程序")
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
            print("自定义命令格式: python3 route_stress_test.py [参数]")
            cmd = input("输入完整命令参数: ").strip()
            if cmd:
                subprocess.run([sys.executable, "route_stress_test.py"] + cmd.split())
        else:
            print("无效选择，请重试")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断，退出程序")
    except Exception as e:
        print(f"程序错误: {e}")