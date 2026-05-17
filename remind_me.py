# -*- coding: utf-8 -*-
r"""先锋组例会提醒脚本

用法：
  双击运行 / 命令行：python remind_me.py
  自动生成提醒文字 → 记事本打开 → 复制到剪贴板 → 弹窗提示

配置 Windows 任务计划程序（每周三自动运行）：
  1. Win+R → taskschd.msc
  2. 创建基本任务 → 名称："先锋组例会提醒"
  3. 触发器：每周 → 星期三 → 选择时间（如 10:00）
  4. 操作：启动程序
     程序：C:\Python314\python.exe
     参数：-X utf8 "D:\德恒\14.社团工作\4.先锋组\自动排班\remind_me.py"
     起始于：D:\德恒\14.社团工作\4.先锋组\自动排班
  5. 完成 → 右键任务 → 属性 → 勾选"不管用户是否登录都要运行"
"""

import sys
import os
import ctypes
import subprocess
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schedule_engine import get_next_duty, format_reminder

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def copy_to_clipboard(text: str):
    """复制文本到剪贴板（Windows）"""
    import tempfile
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.txt', delete=False, encoding='utf-8'
        ) as f:
            f.write(text)
            tmp_path = f.name
        subprocess.run(
            ['powershell', '-NoProfile', '-Command',
             f'Get-Content -Path "{tmp_path}" -Encoding UTF8 | Set-Clipboard; '
             f'Remove-Item "{tmp_path}"'],
            capture_output=True, timeout=10
        )
        return True
    except Exception:
        try:
            subprocess.run(['clip'], input=text.encode('gbk'), timeout=5)
            return True
        except Exception:
            return False


def show_toast(title: str, message: str):
    """Windows toast 通知（不阻塞）"""
    try:
        # 通过临时脚本文件避免注入风险
        import tempfile
        ps_script = (
            f'[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, '
            f'ContentType = WindowsRuntime] > $null\n'
            f'$t = [Windows.UI.Notifications.ToastNotificationManager]::'
            f'GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)\n'
            f'$t.GetElementsByTagName("text")[0].AppendChild('
            f'$t.CreateTextNode("{title}")) > $null\n'
            f'$t.GetElementsByTagName("text")[1].AppendChild('
            f'$t.CreateTextNode("{message}")) > $null\n'
            f'$toast = [Windows.UI.Notifications.ToastNotification]::new($t)\n'
            f'[Windows.UI.Notifications.ToastNotificationManager]::'
            f'CreateToastNotifier("先锋组").Show($toast)'
        )
        # 写入 UTF-16 LE 脚本文件（PowerShell 默认编码）
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.ps1', delete=False, encoding='utf-16'
        ) as f:
            f.write(ps_script)
            tmp = f.name
        subprocess.run(
            ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', tmp],
            capture_output=True, timeout=10
        )
        os.unlink(tmp)
    except Exception:
        pass


def main():
    today = date.today()
    duty = get_next_duty(today)

    # 1. 生成提醒文字
    reminder = format_reminder(duty)
    # 附加转发提示
    full_text = (
        f'{reminder}\n'
        f'\n'
        f'————————————\n'
        f'（自动生成于 {today.month}月{today.day}日，可直接复制转发到群里）'
    )

    # 2. 写出文本文件，用记事本打开（方便查看和复制）
    txt_path = os.path.join(OUTPUT_DIR, '本次提醒.txt')
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(full_text)
    os.startfile(txt_path)  # 用默认程序（记事本）打开

    # 3. 复制纯提醒文字到剪贴板（不含脚注，方便直接粘贴）
    copy_to_clipboard(reminder)

    # 4. Toast 通知（Win10+）
    preview = f'{chr(0x4E3B)}{chr(0x6301)}: {duty.host}  {chr(0x8D44)}{chr(0x8BAF)}: {duty.radar_presenter}'
    show_toast('先锋组例会提醒', preview)

    # 5. 控制台输出
    print(full_text)
    print()
    if duty.thu_date == today:
        print('⚠ 今天是周四！请确认是否已发送提醒。')


if __name__ == '__main__':
    main()
