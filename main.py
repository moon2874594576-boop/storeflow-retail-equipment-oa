"""PyCharm entry point. Run this file from any working directory."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import secrets
import socket
import sys
import threading
import webbrowser

ROOT = Path(__file__).resolve().parent


def main():
    # Windows IDE 使用管道接收输出时也统一为 UTF-8，避免中文启动提示乱码。
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="StoreFlow 门店设备借用与归还工作台")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--check", action="store_true", help="初始化并检查环境，不启动服务")
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("端口应在 1 到 65535 之间")
    data = Path(os.environ.get("STOREFLOW_DATA_DIR", ROOT / "runtime")).resolve()
    data.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("STOREFLOW_DATA_DIR", str(data))
    os.environ.setdefault("STOREFLOW_DB_PATH", str(data / "storeflow.sqlite3"))
    if "STOREFLOW_SECRET_KEY" not in os.environ:
        secret_path = data / "secret.key"
        if not secret_path.exists():
            try:
                with secret_path.open("x", encoding="utf-8") as handle:
                    handle.write(secrets.token_urlsafe(64))
            except FileExistsError:
                pass
        os.environ["STOREFLOW_SECRET_KEY"] = secret_path.read_text(encoding="utf-8").strip()
    # 默认仅本机演示；外部监听时必须显式启用演示数据。
    os.environ.setdefault("STOREFLOW_DEMO", "1" if args.host in {"127.0.0.1", "localhost"} else "0")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    sys.path.insert(0, str(ROOT / "backend"))
    try:
        import django
        from waitress import serve
    except ImportError as exc:
        print(f"缺少依赖 {exc.name}。请用当前解释器安装：\n\"{sys.executable}\" -m pip install -r \"{ROOT / 'requirements.txt'}\"")
        return 1
    if not (ROOT / "frontend/dist/index.html").is_file():
        print("缺少前端构建文件。请恢复 frontend/dist，或在 frontend 中执行 npm ci 和 npm run build。")
        return 1
    django.setup()
    from django.core.management import call_command
    from django.core.wsgi import get_wsgi_application

    call_command("migrate", interactive=False, verbosity=0)
    if os.environ.get("STOREFLOW_DEMO") == "1":
        call_command("seed_demo", verbosity=0)
    call_command("check", verbosity=0)
    if args.check:
        print("StoreFlow environment check passed.")
        return 0
    try:
        with socket.socket() as probe:
            probe.bind((args.host, args.port))
    except OSError:
        print(f"无法监听 {args.host}:{args.port}。端口可能已被占用，请使用 --port 8766。")
        return 1
    url = f"http://{'127.0.0.1' if args.host == '0.0.0.0' else args.host}:{args.port}"
    print(f"\nStoreFlow: {url}\nProject: {ROOT}\nData: {data}\nStop: Ctrl+C", flush=True)
    if not args.no_browser:
        opener = threading.Timer(1.2, lambda: webbrowser.open(url))
        opener.daemon = True
        opener.start()
    try:
        serve(get_wsgi_application(), host=args.host, port=args.port, threads=8)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
