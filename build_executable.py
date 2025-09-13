#!/usr/bin/env python3
"""
网络安全工具打包脚本
使用PyInstaller将Python脚本打包为可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """执行命令并显示结果"""
    print(f"\n{description}...")
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 成功")
        if result.stdout:
            print(f"输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 失败")
        print(f"错误: {e}")
        if e.stderr:
            print(f"错误详情: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ 命令未找到")
        return False

def clean_build():
    """清理之前的构建文件"""
    print("🧹 清理构建目录...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除 {dir_name}")
    
    # 删除.spec文件
    spec_files = list(Path('.').glob('*.spec'))
    for spec_file in spec_files:
        spec_file.unlink()
        print(f"已删除 {spec_file}")

def create_spec_file():
    """创建PyInstaller配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['route_stress_test.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('route-stress-test.nse', '.'),
        ('NSE_INSTALL.md', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'ipaddress',
        'concurrent.futures',
        'json',
        'subprocess',
        'threading',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='kali-network-tester',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('kali-network-tester.spec', 'w') as f:
        f.write(spec_content)
    print("✅ 已创建配置文件 kali-network-tester.spec")

def create_launcher_spec():
    """创建启动器的配置文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['kali_network_scanner.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'subprocess',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='kali-scanner-launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('kali-scanner-launcher.spec', 'w') as f:
        f.write(spec_content)
    print("✅ 已创建启动器配置文件 kali-scanner-launcher.spec")

def build_executables():
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    
    # 构建主程序
    if not run_command(
        ['python3', '-m', 'PyInstaller', 'kali-network-tester.spec'],
        "构建主程序 kali-network-tester"
    ):
        return False
    
    # 构建启动器
    if not run_command(
        ['python3', '-m', 'PyInstaller', 'kali-scanner-launcher.spec'],
        "构建启动器 kali-scanner-launcher"
    ):
        return False
    
    return True

def create_install_package():
    """创建安装包"""
    print("📦 创建安装包...")
    
    # 创建安装目录
    install_dir = Path('kali-network-tools')
    if install_dir.exists():
        shutil.rmtree(install_dir)
    install_dir.mkdir()
    
    # 复制可执行文件
    dist_dir = Path('dist')
    if dist_dir.exists():
        for exe_file in dist_dir.glob('*'):
            if exe_file.is_file():
                shutil.copy2(exe_file, install_dir)
                print(f"✅ 已复制 {exe_file.name}")
    
    # 复制其他文件
    files_to_copy = [
        'route-stress-test.nse',
        'NSE_INSTALL.md', 
        'README.md',
        'install.sh'
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, install_dir)
            print(f"✅ 已复制 {file_name}")
    
    # 创建使用说明
    readme_content = '''# Kali网络安全工具 - 可执行版本

## 文件说明
- `kali-network-tester`: 主程序（命令行版本）
- `kali-scanner-launcher`: 交互式启动器
- `route-stress-test.nse`: Nmap NSE脚本
- `install.sh`: 安装依赖脚本

## 使用方法

### 1. 安装依赖工具
```bash
sudo ./install.sh
```

### 2. 运行交互式启动器（推荐新手）
```bash
./kali-scanner-launcher
```

### 3. 直接运行主程序（高级用户）
```bash
# 显示帮助信息
./kali-network-tester -h

# 综合网络扫描
sudo ./kali-network-tester --comprehensive

# 压力测试指定目标
./kali-network-tester -t 192.168.1.1 --tests ping hping nmap

# Web服务扫描
./kali-network-tester --web-scan -t 192.168.1.100
```

## 注意事项
1. 某些功能需要root权限，建议使用sudo运行
2. 确保已安装相关网络工具（nmap, hping3, netdiscover等）
3. 在进行网络扫描前，请确保你有相应的授权

## 系统要求
- Linux系统（推荐Kali Linux）
- 网络工具：nmap, hping3, netdiscover, masscan, nikto, whatweb, dnsrecon
- Python 3.6+（仅源码版本需要）
'''
    
    with open(install_dir / 'README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ 安装包已创建: {install_dir}")
    return True

def main():
    """主函数"""
    print("🚀 Kali网络安全工具打包程序")
    print("=" * 50)
    
    # 检查当前目录
    required_files = ['route_stress_test.py', 'kali_network_scanner.py']
    for file_name in required_files:
        if not os.path.exists(file_name):
            print(f"❌ 缺少必要文件: {file_name}")
            return False
    
    try:
        # 1. 清理构建目录
        clean_build()
        
        # 2. 创建配置文件
        create_spec_file()
        create_launcher_spec()
        
        # 3. 构建可执行文件
        if not build_executables():
            print("❌ 构建失败")
            return False
        
        # 4. 创建安装包
        if not create_install_package():
            print("❌ 创建安装包失败")
            return False
        
        print("\n🎉 打包完成！")
        print("=" * 50)
        print("📁 安装包位置: kali-network-tools/")
        print("📋 可执行文件:")
        print("   - kali-network-tester (主程序)")
        print("   - kali-scanner-launcher (启动器)")
        print("\n🔧 下一步:")
        print("   1. cd kali-network-tools")
        print("   2. sudo ./install.sh  # 安装依赖")
        print("   3. ./kali-scanner-launcher  # 运行程序")
        
        return True
        
    except Exception as e:
        print(f"❌ 打包过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)