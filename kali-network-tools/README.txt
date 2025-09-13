# Kali网络安全工具 - 可执行版本

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
