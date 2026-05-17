# -*- coding: utf-8 -*-
"""先锋组排班计算引擎

两条独立轮换序列：
- 主持(值班律师)：黄磊→陈琦→安健→唐永生→秦韬→张忠钢，每人2周
- 资讯(市场雷达)：黄磊→秦韬→张忠钢→唐永生→安健→陈琦，每人1周
- 资讯延迟一期：表格周四列的资讯团队，实际在下周四发布
  即：周四N的资讯发布人 = 周四N-1表格列的资讯负责团队
"""

from datetime import date, timedelta
from typing import NamedTuple

HOSTS = ['黄磊', '陈琦', '安健', '唐永生', '秦韬', '张忠钢']
RADARS = ['黄磊', '秦韬', '张忠钢', '唐永生', '安健', '陈琦']

# 周期十五首个周四
ANCHOR_THURSDAY = date(2025, 11, 27)


class Duty(NamedTuple):
    thu_date: date
    host: str
    radar_table: str       # 表格中该周四对应的资讯责任团队（负责整理，下周发布）
    radar_presenter: str   # 该周四例会上实际做资讯发布的人


def _thursday_number(d: date) -> int:
    """返回 d 是第几个周四（0 = 2025-11-27）"""
    delta = (d - ANCHOR_THURSDAY).days
    if delta % 7 != 0:
        raise ValueError(f'{d} 不是周四（周四锚点={ANCHOR_THURSDAY}）')
    return delta // 7


def get_duty(thu_date: date) -> Duty:
    """返回指定周四例会的排班"""
    n = _thursday_number(thu_date)
    host_idx = (n // 2) % len(HOSTS)
    radar_table_idx = n % len(RADARS)
    radar_presenter_idx = (n - 1) % len(RADARS)

    return Duty(
        thu_date=thu_date,
        host=HOSTS[host_idx],
        radar_table=RADARS[radar_table_idx],
        radar_presenter=RADARS[radar_presenter_idx],
    )


def get_this_week_duty(today: date = None) -> Duty:
    """返回本周四例会的排班。
    周一至周三：返回本周即将到来的周四；周四：返回今天；
    周五至周日：返回本周已过去的周四（仍在同一日历周内）。
    """
    if today is None:
        today = date.today()
    wd = today.weekday()
    if wd <= 3:  # Mon-Thu: forward to this week's Thu
        offset = 3 - wd
    else:  # Fri-Sun: backward to this week's Thu
        offset = -(wd - 3)
    thu = today + timedelta(days=offset)
    return get_duty(thu)


def get_next_duty(today: date = None) -> Duty:
    """返回下一个即将到来的周四排班（含今天）。用于提醒和排班卡片。"""
    if today is None:
        today = date.today()
    offset = (3 - today.weekday()) % 7  # days to next Thu (0 if today is Thu)
    thu = today + timedelta(days=offset)
    return get_duty(thu)


def generate_year_schedule(year: int) -> list[Duty]:
    """生成指定年份的全年周四排班"""
    result = []
    # 找到该年第一个周四
    d = date(year, 1, 1)
    while d.weekday() != 3:
        d += timedelta(days=1)

    # 生成所有周四，直到下一年
    end = date(year + 1, 1, 1)
    while d < end:
        result.append(get_duty(d))
        d += timedelta(weeks=1)

    return result


def format_reminder(duty: Duty, today: date = None) -> str:
    """生成微信群提醒文本。自动判断「本周四」还是「下周四」。"""
    if today is None:
        today = date.today()
    # 判断是否在同一日历周内
    wd = today.weekday()
    week_start = today - timedelta(days=wd)
    week_end = week_start + timedelta(days=6)
    in_this_week = week_start <= duty.thu_date <= week_end
    day_label = '本周四' if in_this_week else '下周四'
    return (
        f'{chr(0x3010)}先锋组例会提醒{chr(0x3011)}\n'
        f'{day_label} {duty.thu_date.month}月{duty.thu_date.day}日\n'
        f'主持：{duty.host}\n'
        f'资讯发布：{duty.radar_presenter}'
    )


def generate_full_schedule_json(year: int) -> str:
    """生成全年排班 JSON，供 HTML 内嵌使用"""
    import json
    duties = generate_year_schedule(year)
    return json.dumps([{
        'date': d.thu_date.isoformat(),
        'month': d.thu_date.month,
        'day': d.thu_date.day,
        'host': d.host,
        'radar': d.radar_presenter,
        'week_label': f'{d.thu_date.month}月{d.thu_date.day}日',
    } for d in duties], ensure_ascii=False, indent=2)


if __name__ == '__main__':
    # 验证脚本：对比 Word 文档中的已知数据
    print('=== 验证排班引擎 ===\n')

    checks = [
        # (日期, 主持, 资讯表格, 资讯实际发布人)
        ('2025-11-27', '黄磊', '黄磊', '陈琦'),    # 周四0，上一周期最后资讯是陈琦
        ('2025-12-04', '黄磊', '秦韬', '黄磊'),
        ('2025-12-11', '陈琦', '张忠钢', '秦韬'),
        ('2025-12-18', '陈琦', '唐永生', '张忠钢'),
        ('2025-12-25', '安健', '安健', '唐永生'),
        ('2026-01-01', '安健', '陈琦', '安健'),
        ('2026-01-08', '唐永生', '黄磊', '陈琦'),
        ('2026-01-15', '唐永生', '秦韬', '黄磊'),
        # 用户确认: 5月14日资讯是陈琦出的
        ('2026-05-07', '张忠钢', '陈琦', '安健'),
        ('2026-05-14', '黄磊', '黄磊', '陈琦'),
        ('2026-05-21', '黄磊', '秦韬', '黄磊'),
        ('2026-05-28', '陈琦', '张忠钢', '秦韬'),
        ('2026-06-04', '陈琦', '唐永生', '张忠钢'),
    ]

    all_ok = True
    for d_str, exp_host, exp_radar_tbl, exp_radar_pres in checks:
        d = date.fromisoformat(d_str)
        duty = get_duty(d)
        host_ok = duty.host == exp_host
        radar_tbl_ok = duty.radar_table == exp_radar_tbl
        radar_pres_ok = duty.radar_presenter == exp_radar_pres
        status = 'OK' if (host_ok and radar_tbl_ok and radar_pres_ok) else 'FAIL'
        if status == 'FAIL':
            all_ok = False
            print(f'{d_str} {status}:')
            print(f'  主持: got={duty.host} expected={exp_host}')
            print(f'  表格资讯: got={duty.radar_table} expected={exp_radar_tbl}')
            print(f'  资讯发布人: got={duty.radar_presenter} expected={exp_radar_pres}')
        else:
            print(f'{d_str} {status}: 主持={duty.host}, 资讯发布={duty.radar_presenter}')

    if all_ok:
        print('\n全部验证通过！')

    # 显示本周排班和下次排班
    today = date.today()
    print(f'\n=== 本周排班（当天={today}）===')
    duty_week = get_this_week_duty(today)
    print(f'日历周四: {duty_week.thu_date}  主持={duty_week.host}  资讯={duty_week.radar_presenter}')
    duty_next = get_next_duty(today)
    print(f'\n下次例会:')
    print(format_reminder(duty_next))
