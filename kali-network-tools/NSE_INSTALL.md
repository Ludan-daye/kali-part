# Nmap NSE 路由压力测试插件

这是一个专门为Nmap设计的NSE(Nmap Scripting Engine)脚本，使用arp-scan发现局域网设备并进行压力测试。

## 功能特性

- 🔍 使用arp-scan快速发现局域网中的活跃设备
- 🎯 自动识别路由器和网关设备
- ⚡ 支持多种压力测试方法：ping、hping3
- 📊 生成详细的测试报告和统计信息
- 🛠️ 完全集成到Nmap工作流中

## 安装方法

### 方法1: 复制到Nmap脚本目录

```bash
# 查找Nmap脚本目录
nmap --script-help | head -1

# 通常位于以下位置之一：
# Ubuntu/Debian: /usr/share/nmap/scripts/
# Kali Linux: /usr/share/nmap/scripts/
# macOS (Homebrew): /usr/local/share/nmap/scripts/

# 复制脚本文件
sudo cp route-stress-test.nse /usr/share/nmap/scripts/

# 更新脚本数据库
sudo nmap --script-updatedb
```

### 方法2: 使用本地脚本路径

```bash
# 直接指定脚本文件路径
nmap --script ./route-stress-test.nse <target>
```

## 系统要求

- Nmap (版本7.0+)
- arp-scan工具
- root权限（用于ARP扫描和某些压力测试）

### 安装依赖

```bash
# Kali Linux / Debian / Ubuntu
sudo apt update
sudo apt install nmap arp-scan hping3

# CentOS / RHEL / Fedora
sudo yum install nmap arp-scan hping3

# macOS (Homebrew)
brew install nmap arp-scan hping3
```

## 使用方法

### 基本用法

```bash
# 基本扫描 - 自动发现设备并进行ping测试
sudo nmap --script route-stress-test

# 指定网络接口
sudo nmap --script route-stress-test --script-args "interface=wlan0"

# 使用hping3进行SYN压力测试
sudo nmap --script route-stress-test --script-args "stress-type=hping,count=100"
```

### 高级参数

```bash
# 完整参数示例
sudo nmap --script route-stress-test --script-args "interface=eth0,stress-type=ping,count=200,timeout=60"

# 手动指定测试目标
sudo nmap --script route-stress-test --script-args "targets=192.168.1.1,192.168.1.254"

# 组合多个参数
sudo nmap --script route-stress-test --script-args "interface=wlan0,stress-type=hping,count=50,timeout=30"
```

## 脚本参数

| 参数 | 描述 | 默认值 | 示例 |
|------|------|--------|------|
| `interface` | 网络接口名称 | 自动检测 | `eth0`, `wlan0` |
| `stress-type` | 压力测试类型 | `ping` | `ping`, `hping` |
| `count` | 测试包数量 | `50` | `100`, `200` |
| `timeout` | 超时时间(秒) | `30` | `60`, `120` |
| `targets` | 手动指定目标IP | 无 | `192.168.1.1,8.8.8.8` |

## 输出示例

```
Host script results:
| route-stress-test:
|   ARP扫描发现的设备:
|     192.168.1.1 - aa:bb:cc:dd:ee:ff [TP-LINK Technologies] (可能是路由器/网关)
|     192.168.1.100 - 11:22:33:44:55:66 [Apple Inc]
|     192.168.1.200 - 77:88:99:aa:bb:cc [Samsung Electronics]
|   
|   压力测试结果:
|     192.168.1.1: PING测试完成 - 50包发送, 48包接收, 4%丢包率
|       平均延迟: 2.1ms, 最大延迟: 15.3ms
|     192.168.1.100: PING测试完成 - 50包发送, 50包接收, 0%丢包率
|       平均延迟: 1.8ms, 最大延迟: 8.7ms
|   
|   测试统计: 发现3个设备, 1个可能的路由器, 2个测试成功
```

## 实际使用场景

### 1. 网络健康检查
```bash
# 检查局域网设备连通性
sudo nmap --script route-stress-test --script-args "count=100"
```

### 2. 路由器压力测试
```bash
# 专门测试路由器性能
sudo nmap --script route-stress-test --script-args "targets=192.168.1.1,stress-type=hping,count=500"
```

### 3. 网络设备发现
```bash
# 只进行设备发现，少量测试包
sudo nmap --script route-stress-test --script-args "count=10"
```

### 4. 无线网络测试
```bash
# 测试无线网络稳定性
sudo nmap --script route-stress-test --script-args "interface=wlan0,count=200,timeout=120"
```

## 故障排除

### 权限问题
```bash
# 确保以root权限运行
sudo nmap --script route-stress-test

# 或者给nmap设置权限
sudo setcap cap_net_raw+ep /usr/bin/nmap
```

### 依赖检查
```bash
# 检查arp-scan是否安装
which arp-scan

# 检查hping3是否安装
which hping3

# 测试arp-scan功能
sudo arp-scan -l
```

### 网络接口问题
```bash
# 查看可用网络接口
ip link show

# 手动指定正确的接口
sudo nmap --script route-stress-test --script-args "interface=enp0s3"
```

## 安全提醒

⚠️ **重要提示**：
- 此工具仅用于授权网络的测试
- 确保在自己管理的网络中使用
- 大量的压力测试可能影响网络性能
- 遵守当地法律法规和网络使用政策

## 脚本调试

```bash
# 启用详细输出
sudo nmap --script route-stress-test -d

# 启用脚本跟踪
sudo nmap --script route-stress-test --script-trace
```