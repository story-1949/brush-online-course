# -*- coding: utf-8 -*-
"""
网课自动播放助手 - 主程序入口
"""
import asyncio
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(__file__))

from core.study_session import StudySession
from core.course_manager import CourseManager
from config.settings import load_config, add_course, save_config, detect_platform_from_url
from utils.helpers import setup_logging

logger = setup_logging()


async def add_course_interactive(session):
    print("\n--- 添加新课程 ---")
    name = input("课程名称 (直接回车使用平台名): ").strip()

    url = input("课程URL: ").strip()
    if not url.startswith(('http://', 'https://')):
        print("无效的URL"); return

    # 自动识别平台
    platform_key, platform_name = detect_platform_from_url(url)
    if platform_key:
        print(f"  已自动识别平台: {platform_name}")
        if not name:
            name = platform_name
    else:
        print("  无法自动识别平台，请手动选择:")
        platforms = list(session.config['platforms'].keys())
        for i, p in enumerate(platforms):
            plat_info = session.config['platforms'][p]
            print(f"    {i+1}. {plat_info['name']} ({p})")
        try:
            idx = int(input("选择平台编号: ")) - 1
            platform_key = platforms[idx]
        except (ValueError, IndexError):
            platform_key = input("或输入平台名称: ").strip()
        if not name:
            name = platform_key

    course = add_course(session.config, name, platform_key, url)
    session.course_manager.add_course(name, platform_key, url)
    save_config(session.config)
    print(f"\n课程 '{name}' 添加成功!")


def list_courses(session):
    courses = session.course_manager.list_courses()
    if not courses:
        print("暂无课程，请先添加课程"); return
    print("\n--- 课程列表 ---")
    for i, course in enumerate(courses):
        rate = session.course_manager.get_completion_rate(course['name'])
        print(f"  {i+1}. {course['name']} ({course['platform']}) - 完成率: {rate:.0f}%")


async def start_learning(session, course_index):
    success = await session.select_course(course_index)
    if not success: return
    await session.start_session()
    print("\n请在浏览器中完成登录后按回车继续...")
    input()
    print("\n选择模式:")
    print("  1. 自动模式 (自动播放+自动切下一节)")
    print("  2. 交互模式 (手动控制)")
    mode = input("请选择 (1/2): ").strip()
    if mode == '1':
        await session.run_auto_mode()
    else:
        await session.run_interactive_mode()


def show_progress(session):
    courses = session.course_manager.list_courses()
    if not courses:
        print("暂无课程"); return
    print("\n--- 学习进度 ---")
    for course in courses:
        rate = session.course_manager.get_completion_rate(course['name'])
        print(f"  {course['name']}: {rate:.1f}%")


def export_report(session):
    path = session.course_manager.export_report()
    print(f"报告已导出到: {path}")


def show_settings(session):
    gen = session.config['general']
    print("\n--- 当前设置 ---")
    print(f"  播放速度: {gen['playback_speed']}x")
    print(f"  自动切换延迟: {gen['auto_next_delay']}秒")
    print(f"  最大视频时长: {gen['max_video_duration']}秒")
    print(f"  浏览器: {gen['browser']}")
    print(f"  无头模式: {gen['headless']}")


async def interactive_menu(session):
    while True:
        print("\n" + "=" * 50)
        print("       网课自动播放助手 v1.0")
        print("=" * 50)
        print("""
  1. 添加新课程
  2. 列出所有课程
  3. 开始学习
  4. 查看学习进度
  5. 导出学习报告
  6. 修改设置
  0. 退出
""")
        print("=" * 50)
        choice = input("请选择操作: ").strip()
        if choice == '1':
            await add_course_interactive(session)
        elif choice == '2':
            list_courses(session)
        elif choice == '3':
            list_courses(session)
            courses = session.course_manager.list_courses()
            if not courses: continue
            try:
                idx = int(input("\n选择要学习的课程编号: ")) - 1
                await start_learning(session, idx)
            except ValueError:
                print("请输入数字")
        elif choice == '4':
            show_progress(session)
        elif choice == '5':
            export_report(session)
        elif choice == '6':
            show_settings(session)
        elif choice == '0':
            print("再见!"); break
        else:
            print("无效选项")


async def main():
    session = StudySession()
    if len(sys.argv) > 1:
        if sys.argv[1] == '--quick':
            idx = int(sys.argv[2]) - 1 if len(sys.argv) > 2 else 0
            await start_learning(session, idx)
        elif sys.argv[1] == '--add':
            await add_course_interactive(session)
        elif sys.argv[1] == '--list':
            list_courses(session)
        elif sys.argv[1] == '--progress':
            show_progress(session)
        elif sys.argv[1] == '--report':
            export_report(session)
        else:
            print(f"未知命令: {sys.argv[1]}")
    else:
        await interactive_menu(session)
    await session.close()


if __name__ == "__main__":
    asyncio.run(main())
