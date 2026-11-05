"""Retired upstream initializer; StoreFlow initializes through main.py."""
import sys


if __name__ == "__main__":
    print("上游通用 OA 初始化入口已停用。请运行项目根目录 main.py，自动迁移并安全初始化 StoreFlow 演示数据。", file=sys.stderr)
    sys.exit(1)
