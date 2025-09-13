# Kali Linux 网络安全自动化测试工具

这是一个集成多种Kali Linux网络安全工具的自动化测试套件，提供全面的网络安全评估功能。

## 🚀 功能特性

### 基础功能
- 自动读取系统路由表
- 识别默认网关和网络路由
- 支持多种压力测试方法：
  - ping压力测试
  - hping3 SYN攻击测试
  - nmap端口扫描测试

### 新增高级功能
- 🔍 **主机发现**: 使用netdiscover快速发现活跃主机
- ⚡ **快速端口扫描**: 集成masscan进行高速端口扫描
- 🌐 **Web服务分析**: 
  - whatweb技术栈指纹识别
  - nikto漏洞扫描
- 📊 **综合网络扫描**: 一键执行完整网络安全评估
- 🔎 **DNS枚举**: 使用dnsrecon进行DNS信息收集
- 📄 **自动化报告**: 生成JSON格式详细扫描报告

## 系统要求

- Linux系统（推荐Kali Linux）
- Python 3.x
- 以下工具（Kali Linux默认包含）：
  - ping
  - hping3
  - nmap
  - ip

## 📖 使用方法

### 🎯 快速启动 (推荐)
```bash
# 交互式菜单界面
python3 kali_network_scanner.py
```

### 🔧 命令行使用

#### 基本功能
```bash
# 显示路由表信息
python3 route_stress_test.py --show-routes

# 对默认网关进行ping测试
python3 route_stress_test.py

# 自动发现网络目标并测试
python3 route_stress_test.py --auto

# 指定特定目标进行测试
python3 route_stress_test.py -t 192.168.1.1 8.8.8.8

# 使用多种测试方法
python3 route_stress_test.py --tests ping hping nmap --auto

# 调整测试包数量
python3 route_stress_test.py -c 100 --auto
```

#### 🆕 高级功能
```bash
# 综合网络安全扫描 (需要sudo权限)
sudo python3 route_stress_test.py --comprehensive

# 指定网络范围扫描
sudo python3 route_stress_test.py --comprehensive --network 192.168.1.0/24

# Web服务扫描
python3 route_stress_test.py --web-scan -t 192.168.1.1

# DNS枚举
python3 route_stress_test.py --dns-enum example.com
```

### 📋 参数说明

#### 基础参数
- `-t, --targets`: 指定测试目标IP地址
- `--auto`: 自动发现网络目标
- `--tests`: 选择测试类型 (ping, hping, nmap)
- `--show-routes`: 显示路由表信息
- `-c, --count`: 测试包数量

#### 高级参数
- `--comprehensive`: 执行综合网络安全扫描
- `--network`: 指定网络范围 (例如: 192.168.1.0/24)
- `--web-scan`: 执行Web服务扫描
- `--dns-enum`: 对指定域名进行DNS枚举

## 安全警告

⚠️ **重要提示**: 此工具仅用于授权的网络测试和教育目的。请确保：

1. 只在自己拥有或有明确授权的网络上使用
2. 遵守当地法律法规
3. 不要对未授权的目标进行压力测试
4. 测试前通知网络管理员

## 📊 示例输出

### 基础ping测试
```
系统路由信息:
------------------------------------------------------------
类型: default
网关: 10.18.31.253
原始: default via 10.18.31.253 dev eth0 proto dhcp src 10.18.25.33 metric 100
------------------------------------------------------------

测试目标: ['10.18.31.253']
测试类型: ['ping']

==================================================
测试目标: 10.18.31.253
==================================================
正在对 10.18.31.253 进行ping压力测试...
Ping结果: 100 packets transmitted, 100 received, 0% packet loss, time 10094ms
延迟统计: rtt min/avg/max/mdev = 3.266/9.170/28.497/5.064 ms

压力测试完成!
```

### 综合网络扫描输出
```
============================================================
开始综合网络安全扫描
============================================================
正在使用netdiscover扫描网络...
发现 5 个活跃主机
  10.18.17.32 - 2a:42:4c:45:6f:63 [Unknown vendor]
  10.18.25.38 - e2:5d:89:86:c9:68 [Unknown vendor]
  10.18.31.144 - 62:0b:24:1a:6f:05 [Unknown vendor]

正在使用masscan扫描端口 1-1000...
发现开放端口:
  10.18.17.32: 22/tcp, 80/tcp, 443/tcp

正在使用whatweb进行Web指纹识别...
  http://10.18.17.32: 15 个Web技术
    技术栈: Apache, PHP

============================================================
扫描报告
============================================================

📊 主机发现: 5 个
  • 10.18.17.32 - Unknown vendor
  • 10.18.25.38 - Unknown vendor

🔍 端口扫描: 1 个主机有开放端口
  • 10.18.17.32: 22/tcp, 80/tcp, 443/tcp

🌐 Web服务: 2 个
  • http://10.18.17.32
  • https://10.18.17.32

✅ 未发现明显安全问题

📄 详细报告已保存: network_scan_report_1757584125.json
```

### DNS枚举输出
```
正在进行DNS枚举: google.com
  发现 21 条DNS记录
    [*] 	 SOA ns1.google.com 216.239.32.10
    [*] 	 NS ns4.google.com 216.239.38.10
    [*] 	 NS ns2.google.com 216.239.34.10
    [*] 	 A google.com 142.250.191.14
    [*] 	 AAAA google.com 2404:6800:4004:c1b::66
```

## 故障排除

如果遇到权限问题，请使用sudo运行：
```bash
sudo ./route_stress_test.py --auto
```

如果某些工具未找到，请安装相应软件包：
```bash
sudo apt update
sudo apt install hping3 nmap iputils-ping iproute2
```