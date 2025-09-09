#!/usr/bin/env python3
"""
LangGraph Toy 测试脚本
用于快速测试项目的各种功能
"""

import sys
import os
import json
import time
import requests
from typing import Dict, Any

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class LangGraphTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        color = "\033[92m" if success else "\033[91m"
        reset = "\033[0m"
        
        print(f"{color}{status}{reset} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "name": test_name,
            "success": success,
            "details": details
        })
    
    def check_server_running(self) -> bool:
        """检查服务器是否运行"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_health_check(self):
        """测试健康检查接口"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("健康检查", True, f"状态: {data.get('status')}")
            else:
                self.log_test("健康检查", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("健康检查", False, f"错误: {e}")
    
    def test_chat_endpoints(self):
        """测试聊天接口"""
        test_cases = [
            ("hello", "问候"),
            ("calculate 2+2", "计算"),
            ("weather in beijing", "天气查询"),
            ("search for python", "搜索"),
        ]
        
        for message, description in test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/chat",
                    json={"message": message, "agent_type": "simple"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"聊天接口 - {description}", True, 
                                f"响应: {data['response'][:50]}...")
                else:
                    self.log_test(f"聊天接口 - {description}", False, 
                                f"状态码: {response.status_code}")
            except Exception as e:
                self.log_test(f"聊天接口 - {description}", False, f"错误: {e}")
    
    def test_execute_endpoint(self):
        """测试图执行接口"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/execute",
                json={
                    "graph_type": "simple_agent",
                    "input_data": {"message": "test"}
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("图执行接口", True, 
                            f"执行时间: {data.get('execution_time', 0):.3f}s")
            else:
                self.log_test("图执行接口", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("图执行接口", False, f"错误: {e}")
    
    def test_agent_endpoints(self):
        """测试代理相关接口"""
        try:
            # 获取代理列表
            response = requests.get(f"{self.base_url}/api/v1/agents", timeout=5)
            if response.status_code == 200:
                data = response.json()
                agents = data.get("agents", [])
                self.log_test("获取代理列表", True, f"代理数量: {len(agents)}")
                
                # 获取代理工具
                if agents:
                    agent_name = agents[0]["name"]
                    response = requests.get(f"{self.base_url}/api/v1/agents/{agent_name}/tools", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        tools = data.get("tools", [])
                        self.log_test("获取代理工具", True, f"工具数量: {len(tools)}")
                    else:
                        self.log_test("获取代理工具", False, f"状态码: {response.status_code}")
            else:
                self.log_test("获取代理列表", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("代理相关接口", False, f"错误: {e}")
    
    def test_state_endpoints(self):
        """测试状态管理接口"""
        try:
            # 设置状态
            state_data = {
                "messages": [{"role": "user", "content": "test"}],
                "tool_calls": [],
                "intermediate_steps": [],
                "is_complete": False
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/state",
                json={"state_data": state_data, "operation": "set"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("状态管理接口", True, f"操作成功: {data.get('success')}")
            else:
                self.log_test("状态管理接口", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("状态管理接口", False, f"错误: {e}")
    
    def test_graph_endpoints(self):
        """测试图管理接口"""
        try:
            # 验证图
            response = requests.get(f"{self.base_url}/api/v1/graph/validate", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("图验证接口", True, f"节点数: {data.get('nodes', 0)}")
            else:
                self.log_test("图验证接口", False, f"状态码: {response.status_code}")
            
            # 可视化图
            response = requests.get(f"{self.base_url}/api/v1/graph/visualize", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("图可视化接口", True, f"图名: {data.get('graph_name', 'N/A')}")
            else:
                self.log_test("图可视化接口", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("图管理接口", False, f"错误: {e}")
    
    def test_web_interface(self):
        """测试 Web 界面"""
        try:
            response = requests.get(f"{self.base_url}/web/", timeout=5)
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                if "text/html" in content_type:
                    self.log_test("Web 界面", True, "HTML 页面加载成功")
                else:
                    self.log_test("Web 界面", False, f"内容类型错误: {content_type}")
            else:
                self.log_test("Web 界面", False, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("Web 界面", False, f"错误: {e}")
    
    def test_performance(self):
        """性能测试"""
        try:
            # 测试并发请求
            start_time = time.time()
            
            import concurrent.futures
            import threading
            
            def make_request():
                requests.post(
                    f"{self.base_url}/api/v1/chat",
                    json={"message": "hello", "agent_type": "simple"},
                    timeout=10
                )
            
            # 发送 5 个并发请求
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request) for _ in range(5)]
                concurrent.futures.wait(futures)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            self.log_test("性能测试", True, 
                        f"5 个并发请求耗时: {total_time:.3f}s")
            
        except Exception as e:
            self.log_test("性能测试", False, f"错误: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始 LangGraph Toy 功能测试")
        print("=" * 50)
        
        # 检查服务器是否运行
        if not self.check_server_running():
            print("❌ 服务器未运行，请先启动服务器:")
            print("   ./start.sh dev")
            print("   或")
            print("   python -m uvicorn api.app:create_app --host 0.0.0.0 --port 8000")
            return
        
        print("✅ 服务器正在运行")
        print("")
        
        # 运行测试
        self.test_health_check()
        self.test_web_interface()
        self.test_chat_endpoints()
        self.test_execute_endpoint()
        self.test_agent_endpoints()
        self.test_state_endpoints()
        self.test_graph_endpoints()
        self.test_performance()
        
        # 输出测试结果摘要
        print("")
        print("=" * 50)
        print("📊 测试结果摘要")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {total - passed}")
        print(f"成功率: {passed/total*100:.1f}%")
        
        if passed == total:
            print("🎉 所有测试通过！")
        else:
            print("⚠️  部分测试失败，请检查详细信息")
        
        # 输出失败的测试
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print("")
            print("❌ 失败的测试:")
            for test in failed_tests:
                print(f"   - {test['name']}: {test['details']}")

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help", "help"]:
        print("LangGraph Toy 测试脚本")
        print("")
        print("使用方法:")
        print("  python test_functionality.py    # 运行所有测试")
        print("  python test_functionality.py -h # 显示帮助")
        print("")
        print("注意: 请确保服务器正在运行 (http://localhost:8000)")
        return
    
    tester = LangGraphTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()