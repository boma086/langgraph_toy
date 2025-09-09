#!/bin/bash

# LangGraph Toy 启动脚本
# 使用方法: ./start.sh [dev|test|prod]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Python 版本
check_python() {
    print_info "检查 Python 版本..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安装，请先安装 Python 3.10 或更高版本"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    REQUIRED_VERSION="3.10"
    
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
        print_error "Python 版本过低，需要 $REQUIRED_VERSION 或更高版本，当前版本: $PYTHON_VERSION"
        exit 1
    fi
    
    print_success "Python 版本检查通过: $PYTHON_VERSION"
}

# 检查虚拟环境
check_venv() {
    print_info "检查虚拟环境..."
    if [ ! -d "venv" ]; then
        print_warning "虚拟环境不存在，正在创建..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 检查是否在虚拟环境中
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "虚拟环境已激活: $VIRTUAL_ENV"
    else
        print_error "虚拟环境激活失败"
        exit 1
    fi
}

# 安装依赖
install_deps() {
    print_info "检查依赖包..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "依赖包安装完成"
    else
        print_error "requirements.txt 文件不存在"
        exit 1
    fi
}

# 运行测试
run_tests() {
    print_info "运行测试..."
    python -m pytest tests/ -v
    if [ $? -eq 0 ]; then
        print_success "所有测试通过"
    else
        print_error "测试失败"
        exit 1
    fi
}

# 启动开发服务器
start_dev() {
    print_info "启动开发服务器..."
    print_info "Web 界面: http://localhost:8000/web/"
    print_info "API 文档: http://localhost:8000/docs"
    print_info "健康检查: http://localhost:8000/health"
    print_info "按 Ctrl+C 停止服务器"
    echo ""
    
    python -m uvicorn api.app:create_app --host 0.0.0.0 --port 8000 --reload
}

# 启动生产服务器
start_prod() {
    print_info "启动生产服务器..."
    print_info "服务器地址: http://0.0.0.0:8000"
    echo ""
    
    python -m uvicorn api.app:create_app --host 0.0.0.0 --port 8000
}

# 显示帮助信息
show_help() {
    echo "LangGraph Toy 启动脚本"
    echo ""
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  dev     启动开发服务器 (默认)"
    echo "  prod    启动生产服务器"
    echo "  test    运行测试"
    echo "  install 安装依赖"
    echo "  help    显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 dev     # 启动开发服务器"
    echo "  $0 test    # 运行测试"
    echo "  $0 install # 安装依赖"
}

# 主函数
main() {
    # 默认模式
    MODE=${1:-dev}
    
    echo "=========================================="
    echo "      LangGraph Toy 启动脚本"
    echo "=========================================="
    echo ""
    
    case $MODE in
        "dev")
            check_python
            check_venv
            install_deps
            run_tests
            start_dev
            ;;
        "prod")
            check_python
            check_venv
            install_deps
            run_tests
            start_prod
            ;;
        "test")
            check_python
            check_venv
            install_deps
            run_tests
            ;;
        "install")
            check_python
            check_venv
            install_deps
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知选项: $MODE"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 捕获中断信号
trap 'print_warning "正在停止服务器..."; exit 0' INT TERM

# 运行主函数
main "$@"