local stdnse = require "stdnse"
local shortport = require "shortport"
local nmap = require "nmap"
local string = require "string"
local table = require "table"
local os = require "os"

description = [[
路由压力测试NSE脚本 - 使用arp-scan发现局域网设备并进行压力测试

此脚本执行以下操作：
1. 使用arp-scan发现局域网中的活跃设备
2. 识别路由器和网关设备
3. 对发现的设备进行压力测试
4. 生成详细的测试报告

使用方法:
nmap --script route-stress-test --script-args "interface=eth0,stress-type=ping,count=100"
]]

---
-- @usage
-- nmap --script route-stress-test
-- nmap --script route-stress-test --script-args "interface=wlan0"
-- nmap --script route-stress-test --script-args "stress-type=hping,count=200"
--
-- @output
-- Host script results:
-- | route-stress-test:
-- |   ARP扫描发现的设备:
-- |     192.168.1.1 - aa:bb:cc:dd:ee:ff (可能是路由器)
-- |     192.168.1.100 - 11:22:33:44:55:66
-- |   压力测试结果:
-- |     192.168.1.1: PING测试完成 - 100包发送, 98包接收, 2%丢包率
-- |     平均延迟: 2.5ms, 最大延迟: 15.2ms
--
-- @args route-stress-test.interface 指定网络接口 (默认: 自动检测)
-- @args route-stress-test.stress-type 压力测试类型: ping, hping, flood (默认: ping)
-- @args route-stress-test.count 测试包数量 (默认: 50)
-- @args route-stress-test.timeout 超时时间秒 (默认: 30)
-- @args route-stress-test.targets 手动指定目标IP (逗号分隔)

author = "Kali Tools"
license = "Same as Nmap--See https://nmap.org/book/man-legal.html"
categories = {"discovery", "intrusive"}

-- 脚本只在主机发现阶段运行
hostrule = function(host)
    return true
end

-- 获取默认网络接口
local function get_default_interface()
    local handle = io.popen("ip route | grep default | head -1 | awk '{print $5}'")
    if handle then
        local result = handle:read("*l")
        handle:close()
        if result and result ~= "" then
            return result
        end
    end
    
    -- 备用方法
    handle = io.popen("route -n | grep '^0.0.0.0' | awk '{print $8}' | head -1")
    if handle then
        local result = handle:read("*l")
        handle:close()
        if result and result ~= "" then
            return result
        end
    end
    
    return "eth0"  -- 默认接口
end

-- 获取网络段
local function get_network_range(interface)
    local cmd = string.format("ip addr show %s | grep 'inet ' | awk '{print $2}' | head -1", interface)
    local handle = io.popen(cmd)
    
    if handle then
        local result = handle:read("*l")
        handle:close()
        
        if result then
            -- 转换为网络段 (例如: 192.168.1.100/24 -> 192.168.1.0/24)
            local ip, prefix = result:match("^([%d%.]+)/(%d+)$")
            if ip and prefix then
                local octets = {}
                for octet in ip:gmatch("%d+") do
                    table.insert(octets, tonumber(octet))
                end
                
                if #octets == 4 and tonumber(prefix) >= 24 then
                    return string.format("%d.%d.%d.0/24", octets[1], octets[2], octets[3])
                end
            end
        end
    end
    
    return "192.168.1.0/24"  -- 默认网段
end

-- 执行ARP扫描
local function arp_scan(network_range, interface)
    stdnse.debug(1, "执行ARP扫描: %s 接口: %s", network_range, interface)
    
    local cmd = string.format("arp-scan -l -I %s %s 2>/dev/null", interface, network_range)
    local handle = io.popen(cmd)
    
    local devices = {}
    
    if handle then
        for line in handle:lines() do
            -- 解析arp-scan输出 (格式: IP MAC 厂商)
            local ip, mac = line:match("^([%d%.]+)%s+([%x%:]+)")
            if ip and mac then
                local vendor = line:match("[%x%:]+%s+(.+)$") or "Unknown"
                
                -- 检查是否可能是路由器/网关
                local is_router = false
                if ip:match("%.1$") or ip:match("%.254$") or 
                   vendor:lower():match("router") or 
                   vendor:lower():match("cisco") or
                   vendor:lower():match("tp[-_]?link") or
                   vendor:lower():match("d[-_]?link") or
                   vendor:lower():match("netgear") or
                   vendor:lower():match("linksys") then
                    is_router = true
                end
                
                table.insert(devices, {
                    ip = ip,
                    mac = mac,
                    vendor = vendor,
                    is_router = is_router
                })
            end
        end
        handle:close()
    end
    
    return devices
end

-- PING压力测试
local function ping_stress_test(target_ip, count, timeout)
    stdnse.debug(1, "对 %s 进行PING压力测试，包数: %d", target_ip, count)
    
    local cmd = string.format("ping -c %d -W %d %s 2>/dev/null", count, timeout, target_ip)
    local handle = io.popen(cmd)
    
    local result = {
        target = target_ip,
        test_type = "PING",
        success = false,
        sent = 0,
        received = 0,
        loss_percent = 100,
        avg_time = 0,
        max_time = 0
    }
    
    if handle then
        local output = handle:read("*a")
        handle:close()
        
        -- 解析ping输出
        local sent, received = output:match("(%d+) packets transmitted, (%d+) received")
        if sent and received then
            result.sent = tonumber(sent)
            result.received = tonumber(received)
            result.loss_percent = math.floor((result.sent - result.received) * 100 / result.sent)
            result.success = true
            
            -- 提取延迟信息
            local avg, max = output:match("min/avg/max[^=]*= [%d%.]+/([%d%.]+)/([%d%.]+)")
            if avg and max then
                result.avg_time = tonumber(avg)
                result.max_time = tonumber(max)
            end
        end
    end
    
    return result
end

-- HPING压力测试
local function hping_stress_test(target_ip, count, timeout)
    stdnse.debug(1, "对 %s 进行HPING压力测试，包数: %d", target_ip, count)
    
    local cmd = string.format("timeout %d hping3 -S -c %d -i u100 %s 2>/dev/null", timeout, count, target_ip)
    local handle = io.popen(cmd)
    
    local result = {
        target = target_ip,
        test_type = "HPING_SYN",
        success = false,
        sent = count,
        received = 0,
        loss_percent = 100
    }
    
    if handle then
        local output = handle:read("*a")
        handle:close()
        
        -- 解析hping输出
        local received_count = 0
        for line in output:gmatch("[^\r\n]+") do
            if line:match("flags=SA") or line:match("flags=RA") then
                received_count = received_count + 1
            end
        end
        
        if received_count > 0 then
            result.received = received_count
            result.loss_percent = math.floor((result.sent - result.received) * 100 / result.sent)
            result.success = true
        end
    end
    
    return result
end

-- 执行压力测试
local function perform_stress_test(devices, stress_type, count, timeout)
    local results = {}
    
    for _, device in ipairs(devices) do
        local result
        
        if stress_type == "ping" then
            result = ping_stress_test(device.ip, count, timeout)
        elseif stress_type == "hping" then
            result = hping_stress_test(device.ip, count, timeout)
        else
            -- 默认使用ping
            result = ping_stress_test(device.ip, count, timeout)
        end
        
        result.device_info = device
        table.insert(results, result)
    end
    
    return results
end

-- 格式化输出结果
local function format_results(devices, test_results)
    local output = {}
    
    -- ARP扫描结果
    table.insert(output, "ARP扫描发现的设备:")
    for _, device in ipairs(devices) do
        local device_type = device.is_router and " (可能是路由器/网关)" or ""
        table.insert(output, string.format("  %s - %s [%s]%s", 
            device.ip, device.mac, device.vendor, device_type))
    end
    
    table.insert(output, "")
    table.insert(output, "压力测试结果:")
    
    -- 压力测试结果
    for _, result in ipairs(test_results) do
        if result.success then
            local status_info = string.format("%s测试完成 - %d包发送, %d包接收, %d%%丢包率",
                result.test_type, result.sent, result.received, result.loss_percent)
            
            table.insert(output, string.format("  %s: %s", result.target, status_info))
            
            if result.avg_time and result.max_time then
                table.insert(output, string.format("    平均延迟: %.1fms, 最大延迟: %.1fms", 
                    result.avg_time, result.max_time))
            end
        else
            table.insert(output, string.format("  %s: %s测试失败", result.target, result.test_type))
        end
    end
    
    return output
end

-- 主执行函数
action = function(host)
    -- 获取脚本参数
    local interface = stdnse.get_script_args("route-stress-test.interface") or get_default_interface()
    local stress_type = stdnse.get_script_args("route-stress-test.stress-type") or "ping"
    local count = tonumber(stdnse.get_script_args("route-stress-test.count")) or 50
    local timeout = tonumber(stdnse.get_script_args("route-stress-test.timeout")) or 30
    local manual_targets = stdnse.get_script_args("route-stress-test.targets")
    
    stdnse.debug(1, "路由压力测试开始 - 接口: %s, 类型: %s, 包数: %d", interface, stress_type, count)
    
    local devices = {}
    
    -- 如果手动指定了目标
    if manual_targets then
        for ip in manual_targets:gmatch("[^,]+") do
            ip = ip:match("^%s*(.-)%s*$")  -- 去除空格
            table.insert(devices, {
                ip = ip,
                mac = "Unknown",
                vendor = "Manual Target",
                is_router = false
            })
        end
    else
        -- 使用ARP扫描发现设备
        local network_range = get_network_range(interface)
        stdnse.debug(1, "网络段: %s", network_range)
        
        devices = arp_scan(network_range, interface)
        
        if #devices == 0 then
            return "未发现任何设备，请检查网络接口或权限"
        end
    end
    
    -- 执行压力测试
    local test_results = perform_stress_test(devices, stress_type, count, timeout)
    
    -- 格式化并返回结果
    local output = format_results(devices, test_results)
    
    -- 添加统计信息
    local router_count = 0
    local successful_tests = 0
    for _, device in ipairs(devices) do
        if device.is_router then router_count = router_count + 1 end
    end
    for _, result in ipairs(test_results) do
        if result.success then successful_tests = successful_tests + 1 end
    end
    
    table.insert(output, "")
    table.insert(output, string.format("测试统计: 发现%d个设备, %d个可能的路由器, %d个测试成功",
        #devices, router_count, successful_tests))
    
    return stdnse.format_output(true, output)
end