#!/usr/bin/env python3
"""
Kali Linux 网络安全自动化测试工具
集成多种网络扫描和安全评估功能
"""

import subprocess
import sys
import re
import argparse
import time
import threading
import json
import os
import logging
from typing import List, Dict, Optional, Tuple
import ipaddress
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

class KaliNetworkTester:
    def __init__(self, verbose=False):
        self.routes = []
        self.gateway = None
        self.targets = []
        self.discovered_hosts = []
        self.open_ports = {}
        self.web_services = []
        self.vulnerabilities = []
        self.verbose = verbose
        self._setup_logging()
        
    def _setup_logging(self):
        """设置日志记录"""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('network_test.log'),
                logging.StreamHandler(sys.stdout) if self.verbose else logging.NullHandler()
            ]
        )
        
    def get_route_table(self) -> List[Dict]:
        """读取系统路由表"""
        try:
            # 使用ip route命令获取路由信息
            result = subprocess.run(['ip', 'route', 'show'], 
                                  capture_output=True, text=True, check=True)
            
            routes = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    route_info = self.parse_route_line(line)
                    if route_info:
                        routes.append(route_info)
            
            return routes
            
        except subprocess.CalledProcessError as e:
            print(f"错误: 无法获取路由表 - {e}")
            return []
        except FileNotFoundError:
            print("错误: 系统缺少ip命令")
            return []
    
    def parse_route_line(self, line: str) -> Optional[Dict]:
        """解析路由表行"""
        route_info = {}
        
        # 匹配默认网关
        if line.startswith('default'):
            match = re.search(r'via\s+(\S+)', line)
            if match:
                route_info['type'] = 'default'
                route_info['gateway'] = match.group(1)
                route_info['raw'] = line
                return route_info
        
        # 匹配网络路由
        network_match = re.search(r'^(\S+)', line)
        if network_match:
            network = network_match.group(1)
            route_info['network'] = network
            route_info['type'] = 'network'
            route_info['raw'] = line
            
            # 提取网关信息
            via_match = re.search(r'via\s+(\S+)', line)
            if via_match:
                route_info['gateway'] = via_match.group(1)
            
            # 提取接口信息
            dev_match = re.search(r'dev\s+(\S+)', line)
            if dev_match:
                route_info['interface'] = dev_match.group(1)
            
            return route_info
        
        return None
    
    def get_network_targets(self) -> List[str]:
        """获取网络中的潜在目标"""
        targets = []
        
        # 获取本机IP地址
        try:
            result = subprocess.run(['hostname', '-I'], 
                                  capture_output=True, text=True, check=True)
            local_ips = result.stdout.strip().split()
            
            for ip in local_ips:
                try:
                    network = ipaddress.IPv4Network(f"{ip}/24", strict=False)
                    # 添加网关和网络段的几个常见地址
                    targets.extend([
                        str(network.network_address + 1),  # 通常是路由器
                        str(network.network_address + 2),
                        str(network.broadcast_address - 1)
                    ])
                except:
                    continue
                    
        except:
            pass
            
        return list(set(targets))
    
    def ping_stress_test(self, target: str, count: int = 100, interval: float = 0.1):
        """使用ping进行压力测试"""
        print(f"正在对 {target} 进行ping压力测试...")
        logging.info(f"开始ping测试: {target}, 包数: {count}, 间隔: {interval}s")
        
        # 验证目标IP格式
        try:
            ipaddress.ip_address(target)
        except ValueError:
            print(f"无效的IP地址: {target}")
            logging.error(f"无效的IP地址: {target}")
            return False
        
        cmd = ['ping', '-c', str(count), '-i', str(interval), target]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # 解析ping结果
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                success_rate = None
                avg_latency = None
                
                for line in lines:
                    if 'packets transmitted' in line:
                        print(f"Ping结果: {line}")
                        # 提取成功率
                        loss_match = re.search(r'(\d+)% packet loss', line)
                        if loss_match:
                            success_rate = 100 - int(loss_match.group(1))
                    elif 'min/avg/max' in line:
                        print(f"延迟统计: {line}")
                        # 提取平均延迟
                        avg_match = re.search(r'min/avg/max/mdev = [\d.]+/([\d.]+)/', line)
                        if avg_match:
                            avg_latency = float(avg_match.group(1))
                
                logging.info(f"Ping测试完成: {target}, 成功率: {success_rate}%, 平均延迟: {avg_latency}ms")
                return True
            else:
                print(f"Ping失败: {target}")
                logging.warning(f"Ping失败: {target}, 返回码: {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"Ping超时: {target}")
            logging.warning(f"Ping超时: {target}")
            return False
        except Exception as e:
            print(f"Ping错误: {e}")
            logging.error(f"Ping错误: {target}, 异常: {e}")
            return False
    
    def hping_stress_test(self, target: str, count: int = 100):
        """使用hping3进行TCP SYN压力测试"""
        print(f"正在对 {target} 进行hping3 SYN压力测试...")
        
        cmd = ['hping3', '-S', '-c', str(count), '-i', 'u100', target]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            print(f"hping3结果输出:\n{result.stdout}")
            if result.stderr:
                print(f"hping3错误输出:\n{result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"hping3超时: {target}")
        except FileNotFoundError:
            print("警告: hping3未安装，跳过此测试")
        except Exception as e:
            print(f"hping3错误: {e}")
    
    def nmap_scan_test(self, target: str):
        """使用nmap进行端口扫描测试"""
        print(f"正在对 {target} 进行nmap扫描...")
        
        cmd = ['nmap', '-sS', '-T4', '--top-ports', '100', target]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            print(f"Nmap扫描结果:\n{result.stdout}")
            
        except subprocess.TimeoutExpired:
            print(f"Nmap扫描超时: {target}")
        except FileNotFoundError:
            print("警告: nmap未安装，跳过此测试")
        except Exception as e:
            print(f"Nmap扫描错误: {e}")
    
    def netdiscover_scan(self, network_range: str = None):
        """使用netdiscover发现活跃主机"""
        print("正在使用netdiscover扫描网络...")
        
        if not network_range:
            network_range = "10.18.16.0/20"  # 使用当前网段
            
        cmd = ['netdiscover', '-r', network_range, '-P']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            hosts = []
            
            for line in result.stdout.split('\n'):
                # 解析netdiscover输出
                if re.match(r'^\s*\d+\.\d+\.\d+\.\d+', line):
                    parts = line.split()
                    if len(parts) >= 2:
                        ip = parts[0]
                        mac = parts[1] if len(parts) > 1 else "Unknown"
                        vendor = " ".join(parts[2:]) if len(parts) > 2 else "Unknown"
                        hosts.append({'ip': ip, 'mac': mac, 'vendor': vendor})
            
            self.discovered_hosts = hosts
            print(f"发现 {len(hosts)} 个活跃主机")
            for host in hosts:
                print(f"  {host['ip']} - {host['mac']} [{host['vendor']}]")
                
            return hosts
            
        except subprocess.TimeoutExpired:
            print("Netdiscover扫描超时")
        except FileNotFoundError:
            print("警告: netdiscover未安装")
        except Exception as e:
            print(f"Netdiscover扫描错误: {e}")
        
        return []
    
    def masscan_port_scan(self, targets: List[str], ports: str = "1-1000"):
        """使用masscan进行快速端口扫描"""
        print(f"正在使用masscan扫描端口 {ports}...")
        
        target_list = ",".join(targets)
        cmd = ['masscan', target_list, '-p', ports, '--rate', '1000']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            for line in result.stdout.split('\n'):
                if 'open' in line:
                    # 解析: Discovered open port 80/tcp on 192.168.1.1
                    match = re.search(r'port\s+(\d+)/(\w+)\s+on\s+(\S+)', line)
                    if match:
                        port, protocol, ip = match.groups()
                        if ip not in self.open_ports:
                            self.open_ports[ip] = []
                        self.open_ports[ip].append(f"{port}/{protocol}")
            
            print(f"发现开放端口:")
            for ip, ports in self.open_ports.items():
                print(f"  {ip}: {', '.join(ports)}")
                
        except subprocess.TimeoutExpired:
            print("Masscan扫描超时")
        except FileNotFoundError:
            print("警告: masscan未安装")
        except Exception as e:
            print(f"Masscan扫描错误: {e}")
    
    def nikto_web_scan(self, web_targets: List[str]):
        """使用nikto扫描Web服务"""
        print("正在使用nikto扫描Web服务...")
        
        for target in web_targets:
            print(f"扫描Web服务: {target}")
            cmd = ['nikto', '-h', target, '-Format', 'txt']
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                
                # 解析nikto输出查找漏洞
                vulnerabilities = []
                for line in result.stdout.split('\n'):
                    if '+ OSVDB-' in line or 'SENSITIVE' in line or 'ERROR' in line:
                        vulnerabilities.append(line.strip())
                
                if vulnerabilities:
                    self.vulnerabilities.extend([{'target': target, 'type': 'web', 'issues': vulnerabilities}])
                    print(f"  发现 {len(vulnerabilities)} 个Web问题")
                else:
                    print(f"  未发现明显Web问题")
                    
            except subprocess.TimeoutExpired:
                print(f"Nikto扫描超时: {target}")
            except FileNotFoundError:
                print("警告: nikto未安装")
            except Exception as e:
                print(f"Nikto扫描错误: {e}")
    
    def whatweb_fingerprint(self, web_targets: List[str]):
        """使用whatweb进行Web指纹识别"""
        print("正在使用whatweb进行Web指纹识别...")
        
        for target in web_targets:
            cmd = ['whatweb', target, '--format', 'json']
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.stdout.strip():
                    try:
                        data = json.loads(result.stdout)
                        if isinstance(data, list) and len(data) > 0:
                            plugins = data[0].get('plugins', {})
                            print(f"  {target}: {len(plugins)} 个Web技术")
                            
                            # 显示重要技术栈
                            important_tech = ['Apache', 'Nginx', 'PHP', 'MySQL', 'WordPress', 'Drupal', 'Joomla']
                            found_tech = [tech for tech in important_tech if tech in plugins]
                            if found_tech:
                                print(f"    技术栈: {', '.join(found_tech)}")
                    except json.JSONDecodeError:
                        pass
                        
            except subprocess.TimeoutExpired:
                print(f"WhatWeb扫描超时: {target}")
            except FileNotFoundError:
                print("警告: whatweb未安装")
            except Exception as e:
                print(f"WhatWeb扫描错误: {e}")
    
    def dns_enumeration(self, domain: str):
        """DNS枚举和信息收集"""
        print(f"正在进行DNS枚举: {domain}")
        
        # 使用dnsrecon
        cmd = ['dnsrecon', '-d', domain, '-t', 'std']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # 提取DNS记录
            dns_records = []
            for line in result.stdout.split('\n'):
                if 'A ' in line or 'AAAA ' in line or 'MX ' in line or 'NS ' in line:
                    dns_records.append(line.strip())
            
            if dns_records:
                print(f"  发现 {len(dns_records)} 条DNS记录")
                for record in dns_records[:5]:  # 只显示前5条
                    print(f"    {record}")
                    
        except subprocess.TimeoutExpired:
            print("DNS枚举超时")
        except FileNotFoundError:
            print("警告: dnsrecon未安装")
        except Exception as e:
            print(f"DNS枚举错误: {e}")
    
    def comprehensive_network_scan(self, network_range: str = None):
        """综合网络扫描"""
        print("\n" + "="*60)
        print("开始综合网络安全扫描")
        print("="*60)
        
        # 1. 主机发现
        hosts = self.netdiscover_scan(network_range)
        if not hosts:
            print("未发现活跃主机，使用默认目标")
            hosts = [{'ip': self.gateway}] if self.gateway else []
        
        # 2. 端口扫描
        if hosts:
            target_ips = [host['ip'] for host in hosts]
            self.masscan_port_scan(target_ips)
        
        # 3. Web服务检测和扫描
        web_targets = []
        for ip, ports in self.open_ports.items():
            for port in ports:
                if '80/' in port or '443/' in port or '8080/' in port:
                    protocol = 'https' if '443/' in port else 'http'
                    port_num = port.split('/')[0]
                    if port_num in ['80', '443']:
                        web_targets.append(f"{protocol}://{ip}")
                    else:
                        web_targets.append(f"{protocol}://{ip}:{port_num}")
        
        if web_targets:
            print(f"\n发现 {len(web_targets)} 个Web服务")
            self.whatweb_fingerprint(web_targets[:3])  # 限制扫描数量
            # self.nikto_web_scan(web_targets[:2])  # 注释掉以减少扫描时间
        
        # 4. 生成报告
        self.generate_scan_report()
    
    def generate_scan_report(self):
        """生成扫描报告"""
        print("\n" + "="*60)
        print("扫描报告")
        print("="*60)
        
        print(f"\n📊 主机发现: {len(self.discovered_hosts)} 个")
        for host in self.discovered_hosts:
            print(f"  • {host['ip']} - {host['vendor']}")
        
        print(f"\n🔍 端口扫描: {len(self.open_ports)} 个主机有开放端口")
        for ip, ports in self.open_ports.items():
            print(f"  • {ip}: {', '.join(ports)}")
        
        print(f"\n🌐 Web服务: {len(self.web_services)} 个")
        for service in self.web_services:
            print(f"  • {service}")
        
        if self.vulnerabilities:
            print(f"\n⚠️  潜在问题: {len(self.vulnerabilities)} 个")
            for vuln in self.vulnerabilities:
                print(f"  • {vuln['target']}: {len(vuln['issues'])} 个问题")
        else:
            print("\n✅ 未发现明显安全问题")
        
        # 保存详细报告到文件
        timestamp = int(time.time())
        report_file = f"network_scan_report_{timestamp}.json"
        html_report = f"network_scan_report_{timestamp}.html"
        
        report_data = {
            'timestamp': timestamp,
            'scan_date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp)),
            'hosts': self.discovered_hosts,
            'open_ports': self.open_ports,
            'web_services': self.web_services,
            'vulnerabilities': self.vulnerabilities,
            'summary': {
                'total_hosts': len(self.discovered_hosts),
                'hosts_with_open_ports': len(self.open_ports),
                'web_services_found': len(self.web_services),
                'vulnerabilities_found': len(self.vulnerabilities)
            }
        }
        
        try:
            # 保存JSON报告
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n📄 详细报告已保存: {report_file}")
            
            # 生成HTML报告
            self._generate_html_report(report_data, html_report)
            print(f"📄 HTML报告已保存: {html_report}")
            
            logging.info(f"报告生成完成: JSON={report_file}, HTML={html_report}")
            
        except Exception as e:
            print(f"报告保存失败: {e}")
            logging.error(f"报告保存失败: {e}")
    
    def _generate_html_report(self, report_data, filename):
        """生成HTML格式报告"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>网络扫描报告 - {report_data['scan_date']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .summary {{ background: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .host {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-left: 4px solid #007bff; }}
        .vulnerability {{ background: #fff3cd; padding: 10px; margin: 5px 0; border-left: 4px solid #ffc107; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 网络安全扫描报告</h1>
        <p>扫描时间: {report_data['scan_date']}</p>
    </div>
    
    <div class="summary">
        <h2>📊 扫描摘要</h2>
        <ul>
            <li>发现主机: {report_data['summary']['total_hosts']} 个</li>
            <li>开放端口主机: {report_data['summary']['hosts_with_open_ports']} 个</li>
            <li>Web服务: {report_data['summary']['web_services_found']} 个</li>
            <li>潜在问题: {report_data['summary']['vulnerabilities_found']} 个</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>🖥️ 发现的主机</h2>
        <table>
            <tr><th>IP地址</th><th>MAC地址</th><th>厂商</th></tr>
"""
        
        for host in report_data['hosts']:
            html_content += f"<tr><td>{host['ip']}</td><td>{host.get('mac', 'N/A')}</td><td>{host.get('vendor', 'Unknown')}</td></tr>"
        
        html_content += """
        </table>
    </div>
    
    <div class="section">
        <h2>🔍 开放端口</h2>
"""
        
        for ip, ports in report_data['open_ports'].items():
            html_content += f"<div class='host'><strong>{ip}</strong>: {', '.join(ports)}</div>"
        
        html_content += """
    </div>
    
    <div class="section">
        <h2>🌐 Web服务</h2>
"""
        
        for service in report_data['web_services']:
            html_content += f"<div class='host'>{service}</div>"
        
        if report_data['vulnerabilities']:
            html_content += """
    </div>
    
    <div class="section">
        <h2>⚠️ 潜在安全问题</h2>
"""
            for vuln in report_data['vulnerabilities']:
                html_content += f"<div class='vulnerability'><strong>{vuln['target']}</strong>: {len(vuln['issues'])} 个问题</div>"
        
        html_content += """
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def run_stress_tests(self, targets: List[str], test_types: List[str]):
        """运行压力测试"""
        for target in targets:
            print(f"\n{'='*50}")
            print(f"测试目标: {target}")
            print(f"{'='*50}")
            
            if 'ping' in test_types:
                self.ping_stress_test(target)
                time.sleep(1)
            
            if 'hping' in test_types:
                self.hping_stress_test(target)
                time.sleep(1)
            
            if 'nmap' in test_types:
                self.nmap_scan_test(target)
                time.sleep(1)
    
    def extract_gateway_from_routes(self):
        """从路由信息中提取网关"""
        for route in self.routes:
            if route['type'] == 'default' and 'gateway' in route:
                self.gateway = route['gateway']
                break
                
    def display_route_info(self):
        """显示路由信息"""
        print("系统路由信息:")
        print("-" * 60)
        
        for route in self.routes:
            print(f"类型: {route['type']}")
            if 'network' in route:
                print(f"网络: {route['network']}")
            if 'gateway' in route:
                print(f"网关: {route['gateway']}")
            if 'interface' in route:
                print(f"接口: {route['interface']}")
            print(f"原始: {route['raw']}")
            print("-" * 60)
    
    def main(self):
        parser = argparse.ArgumentParser(description='Kali Linux 网络安全自动化测试工具')
        parser.add_argument('-t', '--targets', nargs='+', 
                          help='指定测试目标IP地址')
        parser.add_argument('--auto', action='store_true',
                          help='自动发现网络目标')
        parser.add_argument('--tests', nargs='+', 
                          choices=['ping', 'hping', 'nmap'],
                          default=['ping'],
                          help='选择测试类型 (默认: ping)')
        parser.add_argument('--show-routes', action='store_true',
                          help='显示路由表信息')
        parser.add_argument('-c', '--count', type=int, default=50,
                          help='测试包数量 (默认: 50)')
        parser.add_argument('--comprehensive', action='store_true',
                          help='执行综合网络安全扫描')
        parser.add_argument('--network', type=str, 
                          help='指定网络范围 (例如: 192.168.1.0/24)')
        parser.add_argument('--web-scan', action='store_true',
                          help='执行Web服务扫描')
        parser.add_argument('--dns-enum', type=str,
                          help='对指定域名进行DNS枚举')
        parser.add_argument('-v', '--verbose', action='store_true',
                          help='启用详细日志输出')
        parser.add_argument('--output-dir', type=str, default='.',
                          help='指定报告输出目录')
        
        args = parser.parse_args()
        
        # 设置详细模式
        self.verbose = args.verbose
        
        # 创建输出目录
        if args.output_dir != '.':
            Path(args.output_dir).mkdir(parents=True, exist_ok=True)
            os.chdir(args.output_dir)
        
        # 读取路由表
        print("正在读取系统路由表...")
        self.routes = self.get_route_table()
        
        if not self.routes:
            print("无法获取路由信息，退出")
            sys.exit(1)
        
        # 总是提取网关信息
        self.extract_gateway_from_routes()
        
        if args.show_routes:
            self.display_route_info()
        
        # DNS枚举
        if args.dns_enum:
            self.dns_enumeration(args.dns_enum)
            return
        
        # 综合扫描模式
        if args.comprehensive:
            network_range = args.network or "10.18.16.0/20"  # 默认使用当前网段
            self.comprehensive_network_scan(network_range)
            return
        
        # 确定测试目标
        targets = []
        
        if args.targets:
            targets = args.targets
        elif args.auto:
            print("自动发现网络目标...")
            targets = self.get_network_targets()
            if self.gateway:
                targets.append(self.gateway)
        else:
            # 默认测试网关
            if self.gateway:
                targets = [self.gateway]
            else:
                print("未找到默认网关，请手动指定目标")
                sys.exit(1)
        
        if not targets:
            print("未找到测试目标")
            sys.exit(1)
        
        print(f"测试目标: {targets}")
        print(f"测试类型: {args.tests}")
        
        # Web服务扫描
        if args.web_scan:
            web_targets = [f"http://{target}" for target in targets]
            self.whatweb_fingerprint(web_targets)
            return
        
        # 运行传统压力测试
        print(f"\n开始压力测试...")
        self.run_stress_tests(targets, args.tests)
        
        print(f"\n压力测试完成!")

if __name__ == "__main__":
    if sys.platform != 'linux':
        print("警告: 此工具设计用于Linux系统，在其他系统上可能无法正常工作")
    
    tester = KaliNetworkTester()
    try:
        tester.main()
    except KeyboardInterrupt:
        print("\n\n用户中断，退出程序")
        sys.exit(0)
    except Exception as e:
        print(f"程序异常: {e}")
        sys.exit(1)