# 🔒 Kali Linux 网络安全自动化测试工具 v2.0

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://www.kali.org/)

一个专业的网络安全自动化测试套件，集成多种Kali Linux渗透测试工具，为安全研究人员和网络管理员提供全面的网络安全评估功能。

## 🚀 核心功能

### 🎯 主要特性
- **🔍 智能主机发现**: 使用netdiscover自动发现网络中的活跃主机
- **⚡ 高速端口扫描**: 集成masscan实现毫秒级端口扫描
- **🌐 Web安全评估**: whatweb指纹识别 + nikto漏洞扫描
- **📊 综合网络分析**: 一键执行完整的网络安全评估
- **🔎 DNS信息收集**: 使用dnsrecon进行深度DNS枚举
- **📄 多格式报告**: 自动生成JSON和HTML格式的详细报告
- **🛠️ 交互式界面**: 友好的菜单驱动操作界面

### 🆕 v2.0 新增功能
- **📈 增强日志记录**: 详细的操作日志和错误跟踪
- **🎨 HTML报告**: 美观的可视化扫描报告
- **⚙️ 依赖检查**: 自动检测和提示缺失的工具
- **📋 历史管理**: 扫描历史查看和清理功能
- **🔧 配置管理**: 灵活的参数配置选项
- **🛡️ 安全增强**: 输入验证和异常处理

## 📦 系统要求

### 最低要求
- **操作系统**: Linux (推荐Kali Linux 2020.1+)
- **Python**: 3.6 或更高版本
- **权限**: 部分功能需要root权限
- **内存**: 最少512MB可用内存
- **存储**: 100MB可用磁盘空间

### 依赖工具
```bash
# 核心工具 (通常预装在Kali Linux中)
ping hping3 nmap netdiscover masscan nikto whatweb dnsrecon

# 系统工具
ip route curl wget
```

## 🔧 安装说明

### 快速安装
```bash
# 1. 克隆项目
git clone https://github.com/your-repo/kali-network-tools.git
cd kali-network-tools

# 2. 安装依赖工具 (如果缺失)
sudo apt update
sudo apt install hping3 nmap netdiscover masscan nikto whatweb dnsrecon

# 3. 设置执行权限
chmod +x *.py

# 4. 运行工具
python3 kali_network_scanner_v2.py
```

### 手动安装依赖
```bash
# Ubuntu/Debian系统
sudo apt-get update
sudo apt-get install python3 python3-pip
sudo apt-get install hping3 nmap netdiscover masscan nikto whatweb dnsrecon

# CentOS/RHEL系统
sudo yum install python3 python3-pip
sudo yum install hping3 nmap netdiscover masscan nikto whatweb dnsrecon
```

## 📖 使用指南

### 🎯 快速启动 (推荐新手)
```bash
# 启动交互式界面
python3 kali_network_scanner_v2.py
```

### 🔧 命令行使用 (高级用户)

#### 基础功能测试
```bash
# 查看系统路由信息
python3 route_stress_test.py --show-routes

# 对默认网关进行ping压力测试
python3 route_stress_test.py -c 100

# 自动发现并测试网络目标
python3 route_stress_test.py --auto --tests ping hping nmap

# 指定目标进行多种测试
python3 route_stress_test.py -t 192.168.1.1 8.8.8.8 --tests ping nmap
```

#### 高级安全扫描
```bash
# 综合网络安全扫描 (需要sudo权限)
sudo python3 route_stress_test.py --comprehensive

# 指定网络范围的深度扫描
sudo python3 route_stress_test.py --comprehensive --network 192.168.1.0/24

# Web服务安全评估
python3 route_stress_test.py --web-scan -t 192.168.1.100

# DNS信息收集和枚举
python3 route_stress_test.py --dns-enum example.com

# 启用详细日志
python3 route_stress_test.py --comprehensive --verbose
```

### 📋 完整参数列表

| 参数 | 描述 | 示例 |
|------|------|------|
| `-t, --targets` | 指定测试目标IP地址 | `-t 192.168.1.1 8.8.8.8` |
| `--auto` | 自动发现网络目标 | `--auto` |
| `--tests` | 选择测试类型 | `--tests ping hping nmap` |
| `--show-routes` | 显示路由表信息 | `--show-routes` |
| `-c, --count` | 测试包数量 | `-c 100` |
| `--comprehensive` | 综合安全扫描 | `--comprehensive` |
| `--network` | 指定网络范围 | `--network 192.168.1.0/24` |
| `--web-scan` | Web服务扫描 | `--web-scan` |
| `--dns-enum` | DNS枚举 | `--dns-enum example.com` |
| `-v, --verbose` | 详细日志输出 | `-v` |
| `--output-dir` | 报告输出目录 | `--output-dir /tmp/reports` |

## 📊 功能演示

### 🖥️ 交互式界面
```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🔒 Kali Linux 网络安全自动化测试工具 v2.0                ║
║                                                              ║
║    ⚠️  仅用于授权网络的安全测试和教育目的                    ║
║    📧 如有问题请联系: security-team@example.com              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

============================================================
📋 选择测试操作:
============================================================
1. 📊 显示路由信息
2. ⚡ 基础压力测试
3. 🔍 综合网络扫描 (推荐)
4. 🌐 Web服务扫描
5. 🔎 DNS枚举
6. ⚙️  自定义扫描
7. 📄 查看历史报告
8. 🛠️  工具配置
0. 🚪 退出程序
============================================================

请选择 (0-8):
```

### 📈 扫描报告示例
```
============================================================
扫描报告
============================================================

📊 主机发现: 12 个
  • 192.168.1.1 - Cisco Systems
  • 192.168.1.100 - Dell Inc.
  • 192.168.1.102 - Apple Inc.

🔍 端口扫描: 3 个主机有开放端口
  • 192.168.1.1: 22/tcp, 80/tcp, 443/tcp
  • 192.168.1.100: 80/tcp, 8080/tcp
  • 192.168.1.102: 22/tcp, 5900/tcp

🌐 Web服务: 4 个
  • http://192.168.1.1
  • https://192.168.1.1
  • http://192.168.1.100
  • http://192.168.1.100:8080

✅ 未发现明显安全问题

📄 详细报告已保存: network_scan_report_1640123456.json
📄 HTML报告已保存: network_scan_report_1640123456.html
```

### 🔍 DNS枚举输出
```
正在进行DNS枚举: example.com
  发现 15 条DNS记录
    [*] SOA ns1.example.com 203.0.113.1
    [*] NS ns1.example.com 203.0.113.1
    [*] NS ns2.example.com 203.0.113.2
    [*] A example.com 203.0.113.10
    [*] AAAA example.com 2001:db8::1
```

## 📁 项目结构

```
kali-network-tools/
├── README_v2.md                    # 项目文档
├── kali_network_scanner_v2.py      # 优化的启动器 (v2.0)
├── route_stress_test.py            # 核心测试引擎
├── install.sh                      # 安装脚本
├── network_test.log               # 运行日志
├── reports/                       # 扫描报告目录
│   ├── network_scan_report_*.json  # JSON格式报告
│   └── network_scan_report_*.html  # HTML格式报告
└── docs/                         # 文档目录
    ├── INSTALL.md
    ├── EXAMPLES.md
    └── FAQ.md
```

## 🛡️ 安全警告

### ⚠️ 重要提示
**此工具仅用于授权的网络测试和教育目的。使用前请确保:**

1. **✅ 授权测试**: 仅在您拥有或获得明确授权的网络上使用
2. **📋 遵守法规**: 严格遵守当地法律法规和网络使用政策
3. **🚫 禁止滥用**: 不得用于未授权的渗透测试或恶意攻击
4. **📢 事先通知**: 测试前务必通知网络管理员和相关人员
5. **🔒 数据保护**: 保护扫描过程中获得的敏感信息

### 🏛️ 法律责任
- 用户对使用本工具承担全部法律责任
- 开发者不对误用或滥用承担任何责任
- 请在使用前咨询法律专业人士

## 🐛 故障排除

### 常见问题

#### 🔧 工具依赖问题
```bash
# 检查缺失的工具
python3 kali_network_scanner_v2.py

# 手动安装缺失工具
sudo apt install [缺失的工具名]
```

#### 🔐 权限问题
```bash
# 使用sudo运行需要特权的功能
sudo python3 route_stress_test.py --comprehensive

# 检查当前用户权限
whoami
groups
```

#### 📡 网络连接问题
```bash
# 检查网络连接
ping 8.8.8.8

# 检查路由表
ip route show

# 检查DNS配置
cat /etc/resolv.conf
```

#### 💾 存储空间问题
```bash
# 检查磁盘空间
df -h

# 清理历史报告
python3 kali_network_scanner_v2.py
# 选择选项8 -> 选项3
```

### 🆘 获取帮助
如果遇到问题，请按以下步骤操作:

1. **📖 查看文档**: 详细阅读本README和相关文档
2. **🔍 检查日志**: 查看`network_test.log`文件中的错误信息
3. **🧪 测试环境**: 确认在支持的Linux发行版上运行
4. **📧 联系支持**: 发送问题描述到 security-team@example.com

## 🤝 贡献指南

我们欢迎社区贡献! 请遵循以下步骤:

### 🔄 提交代码
1. **Fork** 项目到您的GitHub账户
2. **创建** 功能分支: `git checkout -b feature/AmazingFeature`
3. **提交** 更改: `git commit -m 'Add AmazingFeature'`
4. **推送** 到分支: `git push origin feature/AmazingFeature`
5. **开启** Pull Request

### 📝 报告问题
使用GitHub Issues报告bugs或建议新功能:
- 提供详细的问题描述
- 包含系统信息和错误日志
- 说明重现步骤

## 📜 更新日志

### v2.0.0 (2024-12-XX)
- ✨ 新增HTML报告生成功能
- 🔧 改进依赖检查机制
- 📊 增强日志记录系统
- 🎨 优化用户界面设计
- 🛡️ 加强输入验证和安全性
- 📋 添加历史报告管理功能
- ⚙️ 新增配置管理模块

### v1.0.0 (2024-XX-XX)
- 🎉 初始版本发布
- 🔍 基础网络扫描功能
- 📄 JSON报告生成
- 🌐 Web服务检测

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👥 开发团队

- **主要开发者**: Network Security Team
- **维护者**: [@username](https://github.com/username)
- **贡献者**: 查看 [Contributors](https://github.com/your-repo/kali-network-tools/contributors)

## 🙏 致谢

感谢以下开源项目和工具:
- [Kali Linux](https://www.kali.org/) - 渗透测试Linux发行版
- [Nmap](https://nmap.org/) - 网络扫描工具
- [Masscan](https://github.com/robertdavidgraham/masscan) - 高速端口扫描器
- [Nikto](https://cirt.net/Nikto2) - Web漏洞扫描器

---

## 📞 联系方式

- **📧 邮箱**: security-team@example.com
- **🐙 GitHub**: https://github.com/your-repo/kali-network-tools
- **📖 文档**: https://your-docs-site.com

---

**⚠️ 免责声明**: 本工具仅供教育和授权测试使用。使用者需对其行为承担全部法律责任。