# -*- coding: utf-8 -*-
"""生成内嵌全年数据的排班 HTML 页面。
卡片和表格高亮由 JS 动态计算（每次打开根据浏览器当前日期自动判定下次例会）。
Python 端预填初始值作为 JS 执行前的占位。"""

import json
import sys
from datetime import date, timedelta

sys.path.insert(0, r'D:\德恒\14.社团工作\4.先锋组\自动排班')
from schedule_engine import generate_year_schedule, get_next_duty

today = date.today()

# 预计算「下次例会」信息
next_duty = get_next_duty(today)
NEXT_THU_DATE = next_duty.thu_date.isoformat()
NEXT_HOST = next_duty.host
NEXT_RADAR = next_duty.radar_presenter
NEXT_LABEL = f'{next_duty.thu_date.month}月{next_duty.thu_date.day}日（周四）'

# 判断是「本周例会」还是「下次例会」
# 计算 next_duty 是否在本周日历周内（Mon-Sun）
wd = today.weekday()  # 0=Mon, 6=Sun
week_start = today - timedelta(days=wd)  # Monday
week_end = week_start + timedelta(days=6)  # Sunday
in_this_week = week_start <= next_duty.thu_date <= week_end
card_header = '本周例会' if in_this_week else '下次例会'

# 生成全年排班数据
duties = generate_year_schedule(2026)
data_json = json.dumps([{
    'date': d.thu_date.isoformat(),
    'month': d.thu_date.month,
    'day': d.thu_date.day,
    'host': d.host,
    'radar': d.radar_presenter,
} for d in duties], ensure_ascii=False)

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>先锋组排班表 2026</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: "PingFang SC", "Microsoft YaHei", "Hiragino Sans GB", sans-serif;
    background: #f5f5f5;
    color: #333;
    line-height: 1.6;
    padding-bottom: 40px;
}}
.header {{
    background: linear-gradient(135deg, #1a3a5c 0%, #2d6a9f 100%);
    color: white;
    padding: 24px 16px;
    text-align: center;
}}
.header h1 {{
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 2px;
}}
.header .sub {{
    font-size: 13px;
    opacity: 0.8;
    margin-top: 4px;
}}

.this-week-card {{
    margin: 16px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    overflow: hidden;
}}
.this-week-card .card-header {{
    background: #c41230;
    color: white;
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 600;
    text-align: center;
}}
.this-week-card .card-body {{
    padding: 20px 16px;
    display: flex;
    justify-content: space-around;
    text-align: center;
}}
.this-week-card .role {{ flex: 1; }}
.this-week-card .role-label {{
    font-size: 12px;
    color: #888;
    margin-bottom: 8px;
}}
.this-week-card .role-name {{
    font-size: 28px;
    font-weight: 700;
    color: #1a3a5c;
}}
.this-week-card .role-date {{
    font-size: 12px;
    color: #999;
    margin-top: 4px;
    text-align: center;
    padding-bottom: 14px;
}}
.card-divider {{ width: 1px; background: #eee; }}

.table-container {{
    margin: 16px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    overflow: hidden;
}}
.table-container h2 {{
    font-size: 16px;
    padding: 14px 16px 8px;
    color: #1a3a5c;
    text-align: center;
}}
table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
thead th {{
    background: #f0f4f8;
    color: #555;
    font-weight: 600;
    padding: 10px 8px;
    font-size: 13px;
    position: sticky;
    top: 0;
}}
tbody td {{
    padding: 10px 8px;
    text-align: center;
    border-bottom: 1px solid #f0f0f0;
}}
tbody tr.this-week {{
    background: #fff8e1;
    font-weight: 700;
}}
tbody tr.this-week td:first-child::before {{
    content: "▶ ";
    color: #c41230;
    font-size: 10px;
}}
tbody tr:hover {{ background: #f5f8fc; }}
tbody tr.this-week:hover {{ background: #fff3cd; }}
.month-sep {{
    background: #e8edf2 !important;
    font-weight: 600;
    color: #1a3a5c;
    font-size: 13px;
}}
.month-sep td {{ padding: 6px 8px; }}

.footer {{
    margin: 16px;
    padding: 12px 16px;
    background: white;
    border-radius: 12px;
    font-size: 12px;
    color: #999;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}}

.jump-btn {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: #1a3a5c;
    color: white;
    border: none;
    font-size: 20px;
    cursor: pointer;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
}}
.jump-btn:active {{ background: #c41230; }}
</style>
</head>
<body>

<div class="header">
    <h1>德恒金融证券业务先锋组</h1>
    <div class="sub">2026年例会排班表 · 每周四</div>
</div>

<div class="this-week-card">
    <div class="card-header">{card_header}</div>
    <div class="card-body">
        <div class="role">
            <div class="role-label">主持</div>
            <div class="role-name">{NEXT_HOST}</div>
        </div>
        <div class="card-divider"></div>
        <div class="role">
            <div class="role-label">资讯发布</div>
            <div class="role-name">{NEXT_RADAR}</div>
        </div>
    </div>
    <div class="role-date">{NEXT_LABEL}</div>
</div>

<div class="table-container">
    <h2>全年排班表</h2>
    <table>
        <thead>
            <tr><th>日期</th><th>主持</th><th>资讯发布</th></tr>
        </thead>
        <tbody id="scheduleBody"></tbody>
    </table>
</div>

<div class="footer">
    主持顺序：黄磊→陈琦→安健→唐永生→秦韬→张忠钢（每人两周）<br>
    资讯顺序：黄磊→秦韬→张忠钢→唐永生→安健→陈琦（每人一周，延迟一期发布）<br>
    页面生成于 {today.month}月{today.day}日 · 自动排班系统
</div>

<button class="jump-btn" onclick="scrollToToday()" title="回到下次例会">&#x1F4C5;</button>

<script>
const DATA = {data_json};

function getNextThursday() {{
    var now = new Date();
    var day = now.getDay(); // 0=Sun, 1=Mon,...,6=Sat
    var daysUntil = (4 - day + 7) % 7; // days to next Thu
    var thu = new Date(now);
    thu.setDate(thu.getDate() + daysUntil);
    var mm = thu.getMonth() + 1;
    var dd = thu.getDate();
    return {{
        iso: thu.getFullYear() + '-' + String(mm).padStart(2,'0') + '-' + String(dd).padStart(2,'0'),
        label: mm + '月' + dd + '日（周四）'
    }};
}}

function isInThisWeek(dateStr) {{
    var now = new Date();
    var d = new Date(dateStr + 'T00:00:00');
    var startOfWeek = new Date(now);
    startOfWeek.setDate(now.getDate() - (now.getDay() || 7) + 1);
    startOfWeek.setHours(0,0,0,0);
    var endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(startOfWeek.getDate() + 6);
    endOfWeek.setHours(23,59,59,999);
    return d >= startOfWeek && d <= endOfWeek;
}}

function render() {{
    var next = getNextThursday();
    var nextDuty = null;
    for (var i = 0; i < DATA.length; i++) {{
        if (DATA[i].date === next.iso) {{ nextDuty = DATA[i]; break; }}
    }}
    if (!nextDuty) nextDuty = DATA[0];

    // Update card
    document.getElementById('cardHeader').textContent = isInThisWeek(next.iso) ? '本周例会' : '下次例会';
    document.getElementById('thisWeekHost').textContent = nextDuty.host;
    document.getElementById('thisWeekRadar').textContent = nextDuty.radar;
    document.getElementById('thisWeekDate').textContent = next.label;

    // Render table
    var tbody = document.getElementById('scheduleBody');
    var currentMonth = 0;
    var html = '';
    for (var i = 0; i < DATA.length; i++) {{
        var d = DATA[i];
        if (d.month !== currentMonth) {{
            currentMonth = d.month;
            html += '<tr class="month-sep"><td colspan="3">' + d.month + '月</td></tr>';
        }}
        var cls = (d.date === next.iso) ? 'this-week' : '';
        html += '<tr class="' + cls + '" id="row-' + d.date + '">' +
            '<td>' + d.month + '/' + String(d.day).padStart(2,'0') + '</td>' +
            '<td>' + d.host + '</td>' +
            '<td>' + d.radar + '</td></tr>';
    }}
    tbody.innerHTML = html;

    // Scroll to highlighted row
    setTimeout(function() {{
        var row = document.getElementById('row-' + next.iso);
        if (row) row.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    }}, 400);
}}

function scrollToToday() {{
    var next = getNextThursday();
    var row = document.getElementById('row-' + next.iso);
    if (row) row.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
}}

render();
</script>
</body>
</html>'''

# 写入两个文件
for fname in ['先锋组排班表-2026.html', 'index.html']:
    path = rf'D:\德恒\14.社团工作\4.先锋组\自动排班\{fname}'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

print(f'HTML 已生成，共 {len(duties)} 个周四排班')
print(f'下次例会: {NEXT_LABEL}  主持={NEXT_HOST}  资讯={NEXT_RADAR}')
print(f'卡片标题: {card_header}')
