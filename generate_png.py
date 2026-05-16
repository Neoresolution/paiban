# -*- coding: utf-8 -*-
"""将排班 HTML 页面截图为 PNG 长图，可直接发微信群。
通过本地 HTTP 服务器加载页面，确保 JavaScript 正确执行。"""

from playwright.sync_api import sync_playwright
import os
import http.server
import threading
import time

DIR = os.path.dirname(os.path.abspath(__file__))
html_file = 'index.html'  # ASCII 文件名避免 URL 编码问题
png_file = '先锋组排班表-2026.png'
png_path = os.path.join(DIR, png_file)

# 启动简易 HTTP 服务器
port = 8765
server = http.server.HTTPServer(
    ('127.0.0.1', port),
    lambda *args: http.server.SimpleHTTPRequestHandler(*args, directory=DIR)
)
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
time.sleep(0.3)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={'width': 750, 'height': 1334},
        )
        page.goto(f'http://127.0.0.1:{port}/{html_file}', wait_until='networkidle')
        page.wait_for_timeout(2000)  # 等 JS 渲染

        page.screenshot(path=png_path, full_page=True)
        browser.close()
finally:
    server.shutdown()

print(f'PNG 已生成: {png_path}')
print(f'文件大小: {os.path.getsize(png_path) / 1024:.0f} KB')

