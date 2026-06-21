# -*- coding: utf-8 -*-
"""
学习会话管理
控制整个学习流程：选择课程 -> 播放视频 -> 保存进度
"""
import asyncio
import time
import logging
from datetime import datetime

from config.settings import load_config, get_platform_config
from core.player import VideoPlayer
from core.course_manager import CourseManager

logger = logging.getLogger(__name__)


class StudySession:
    """学习会话"""

    def __init__(self, config_path=None):
        self.config = load_config(config_path)
        self.player = None
        self.course_manager = CourseManager('data')
        self.current_course = None
        self.current_chapter = None
        self.current_video = None
        self.session_start_time = datetime.now()
        self.videos_completed = 0
        self.total_watch_time = 0

    async def select_course(self, course_index):
        """选择课程"""
        course = self.course_manager.get_course(course_index)
        if course is None:
            logger.error(f"未找到课程索引: {course_index}")
            return False

        self.current_course = course
        platform_config = get_platform_config(self.config, course['platform'])

        if platform_config is None:
            logger.error(f"未找到平台配置: {course['platform']}")
            return False

        self.player = VideoPlayer(self.config, platform_config)
        await self.player.start()

        logger.info(f"已选择课程: {course['name']}")
        return True

    async def start_session(self):
        """开始学习会话"""
        if not self.player:
            logger.error("请先选择课程")
            return False

        courses = self.course_manager.list_courses()
        if not courses:
            logger.warning("没有已添加的课程，请先添加课程")
            return False

        print("\n" + "=" * 50)
        print("       网课自动播放助手")
        print("=" * 50)
        print("\n已添加的课程:")
        for i, course in enumerate(courses):
            rate = self.course_manager.get_completion_rate(course['name'])
            status = f" [{rate:.0f}%]" if rate > 0 else ""
            print(f"  {i+1}. {course['name']} ({course['platform']}){status}")
        print("\n" + "=" * 50)

        # 导航到课程页面
        url = self.current_course['url']
        success = await self.player.navigate_to_video(url)

        if not success:
            logger.error("导航失败，请手动登录")
            logger.info("请在浏览器中完成登录后，按回车继续...")
            input()

        # 设置播放速度
        await self.player.set_playback_speed()

        # 开始播放
        await self.player.play_video()
        logger.info("视频已开始播放")

        return True

    async def process_current_video(self):
        """处理当前视频 - 自动监控播放进度"""
        if not self.player:
            return False

        duration = self.config.get('general', {}).get('max_video_duration', 3600)
        poll_interval = 5  # 每5秒检查一次进度

        logger.info(f"开始播放视频，最长等待 {duration} 秒...")
        start_time = time.time()
        prev_ratio = 0

        while time.time() - start_time < duration:
            progress = await self.player.get_video_progress()
            if progress:
                for video in progress:
                    if video.get('duration', 0) > 0:
                        ratio = video['currentTime'] / video['duration']
                        elapsed = int(time.time() - start_time)
                        status = "播放中" if not video['paused'] else "已暂停"

                        # 如果视频暂停了，尝试自动恢复播放
                        if video['paused']:
                            logger.info(f"检测到视频暂停，尝试自动恢复播放...")
                            await self.player.play_video()
                            await self.player.set_playback_speed()
                            status = "已恢复"

                        # 打印进度条
                        bar_length = 30
                        filled = int(bar_length * ratio)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        print(f"\r进度: [{bar}] {ratio*100:5.1f}% | {elapsed}s/{int(video['duration'])}s | {status}", end='', flush=True)

                        prev_ratio = ratio

            await asyncio.sleep(poll_interval)

            # 检查是否完成
            if progress:
                for video in progress:
                    if video.get('duration', 0) > 0:
                        if video['currentTime'] / video['duration'] >= 0.99:
                            print()  # 换行
                            logger.info("视频已完成!")
                            self.videos_completed += 1
                            elapsed = int(time.time() - start_time)
                            self.total_watch_time += elapsed
                            if self.current_course:
                                self.course_manager.mark_video_completed(
                                    self.current_course['name'],
                                    self.current_chapter.get('name', '') if self.current_chapter else '',
                                    self.current_video.get('name', '') if self.current_video else ''
                                )
                            return True

        print()
        return False

    async def go_to_next(self):
        """切换到下一个视频"""
        logger.info("切换到下一个视频...")
        next_selector = self.player.platform_config.get('next_button_selector', '.next_btn')
        clicked = await self.player.click_next_video()
        if clicked:
            await asyncio.sleep(3)
            await self.player.play_video()
            await self.player.set_playback_speed()
            logger.info("已切换到下一个视频并开始播放")
        else:
            logger.warning("未找到下一节按钮，请手动操作")

    async def run_auto_mode(self):
        """自动模式 - 自动播放所有视频直到完成"""
        await self.start_session()

        try:
            while True:
                processed = await self.process_current_video()
                if not processed:
                    logger.warning("视频处理失败，等待后重试...")
                    await asyncio.sleep(5)
                    continue

                print(f"\n已完成 {self.videos_completed} 个视频")
                print(f"总观看时间: {self.total_watch_time // 60} 分钟")

                # 尝试自动切换到下一节
                delay = self.config.get('general', {}).get('auto_next_delay', 3)
                print(f"\n将在 {delay} 秒后自动切换到下一节...")
                await asyncio.sleep(delay)

                success = await self.go_to_next()
                if not success:
                    print("\n无法自动切换到下一节，请输入 'n' 继续或 'q' 退出: ")
                    choice = input().strip().lower()
                    if choice == 'q':
                        break
                    # 继续处理当前
                    continue

        finally:
            await self.close()

    async def run_interactive_mode(self):
        """交互模式"""
        await self.start_session()

        try:
            while True:
                progress = await self.player.get_video_progress()
                if progress:
                    for video in progress:
                        if video.get('duration', 0) > 0:
                            ratio = video['currentTime'] / video['duration']
                            print(f"\r当前进度: {ratio*100:.1f}%", end='', flush=True)

                print("\n\n输入 'n' 切换到下一个视频，'p' 暂停/继续，'q' 退出: ")
                choice = input().strip().lower()
                if choice == 'n':
                    await self.go_to_next()
                elif choice == 'p':
                    if self.player.is_playing:
                        await self.player.pause_video()
                    else:
                        await self.player.play_video()
                elif choice == 'q':
                    break
                await asyncio.sleep(3)

        finally:
            await self.close()

    async def close(self):
        """关闭会话"""
        if self.player:
            await self.player.take_screenshot('session_end.png')
            await self.player.close()
            logger.info("学习会话已结束")

        elapsed = (datetime.now() - self.session_start_time).total_seconds()
        logger.info(f"\n会话统计:")
        logger.info(f"  总耗时: {elapsed/60:.1f} 分钟")
        logger.info(f"  完成视频数: {self.videos_completed}")

        report_path = self.course_manager.export_report()
        logger.info(f"  学习报告已保存到: {report_path}")
