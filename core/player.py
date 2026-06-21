# -*- coding: utf-8 -*-
"""
视频播放核心引擎
使用 Playwright 控制浏览器自动播放视频
"""
import asyncio
import time
import logging
from playwright.async_api import async_playwright, TimeoutError as PwTimeout

logger = logging.getLogger(__name__)


class VideoPlayer:
    """视频播放器核心类"""

    def __init__(self, config, platform_config):
        self.config = config
        self.platform_config = platform_config
        self.browser = None
        self.context = None
        self.page = None
        self._is_playing = False
        self._current_video_url = None
        self._playback_history = []

    async def start(self):
        """启动浏览器"""
        p = await async_playwright().start()
        browser_type = self.config.get('general', {}).get('browser', 'chromium')

        if browser_type == 'firefox':
            self.browser = await p.firefox.launch(headless=self.config['general'].get('headless', False))
        elif browser_type == 'webkit':
            self.browser = await p.webkit.launch(headless=self.config['general'].get('headless', False))
        else:
            self.browser = await p.chromium.launch(
                headless=self.config['general'].get('headless', False),
                args=['--disable-blink-features=AutomationControlled']
            )

        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = await self.context.new_page()
        logger.info("浏览器已启动")

    async def navigate_to_video(self, url):
        """导航到视频页面"""
        self._current_video_url = url
        try:
            await self.page.goto(url, timeout=self.config['general'].get('timeout', 30000))
            logger.info(f"已导航到: {url}")
            await self.page.wait_for_load_state('networkidle', timeout=15000)
            return True
        except PwTimeout as e:
            logger.error(f"页面加载超时: {e}")
            return False

    async def set_playback_speed(self, speed=None):
        """设置视频播放速度"""
        if speed is None:
            speed = self.config.get('general', {}).get('playback_speed', 2.0)
        speed = max(1.0, min(speed, 4.0))

        js_code = f"""
        () => {{
            const videos = document.querySelectorAll('video');
            videos.forEach(v => {{ v.playbackRate = {speed}; }});
            const iframes = document.querySelectorAll('iframe');
            iframes.forEach(iframe => {{
                try {{ iframe.contentWindow?.postMessage({{type: 'setSpeed', speed: {speed}}}, '*'); }} catch(e) {{}}
            }});
            return videos.length;
        }}
        """
        try:
            count = await self.page.evaluate(js_code)
            logger.info(f"播放速度设置为 {speed}x (影响了 {count} 个视频元素)")
            return count > 0
        except Exception as e:
            logger.warning(f"设置播放速度时出错: {e}")
            return False

    async def play_video(self):
        """播放当前视频"""
        js_code = """
        () => {
            const videos = document.querySelectorAll('video');
            let played = 0;
            videos.forEach(v => {
                if (v.paused) {
                    v.play();
                    played++;
                }
            });
            return played;
        }
        """
        try:
            count = await self.page.evaluate(js_code)
            self._is_playing = True
            logger.info(f"正在播放 {count} 个视频")
            return count
        except Exception as e:
            logger.error(f"播放视频时出错: {e}")
            return 0

    async def pause_video(self):
        """暂停视频"""
        js_code = """
        () => {
            const videos = document.querySelectorAll('video');
            videos.forEach(v => v.pause());
            return videos.length;
        }
        """
        try:
            count = await self.page.evaluate(js_code)
            self._is_playing = False
            logger.info(f"已暂停 {count} 个视频")
            return count
        except Exception as e:
            logger.error(f"暂停视频时出错: {e}")
            return 0

    async def get_video_progress(self):
        """获取视频播放进度"""
        js_code = """
        () => {
            const videos = document.querySelectorAll('video');
            const results = [];
            videos.forEach((v, i) => {
                results.push({
                    index: i,
                    currentTime: v.currentTime,
                    duration: v.duration,
                    ended: v.ended,
                    paused: v.paused,
                    playbackRate: v.playbackRate
                });
            });
            return results;
        }
        """
        try:
            return await self.page.evaluate(js_code)
        except Exception as e:
            logger.error(f"获取进度时出错: {e}")
            return []

    async def wait_for_video_end(self, timeout=60):
        """等待视频结束"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                progress = await self.get_video_progress()
                if progress:
                    for video in progress:
                        if video.get('duration', 0) > 0:
                            ratio = video['currentTime'] / video['duration']
                            if ratio >= 0.95:
                                logger.info(f"视频 {video['index']} 已播放 {ratio*100:.1f}%")
                                return True
                await asyncio.sleep(2)
            except Exception as e:
                logger.warning(f"检查进度时出错: {e}")
                await asyncio.sleep(2)
        return False

    async def click_element(self, selector):
        """点击页面上的元素"""
        try:
            elements = await self.page.locator(selector).all()
            if elements:
                await elements[0].click()
                logger.info(f"已点击元素: {selector}")
                return True
            return False
        except Exception as e:
            logger.error(f"点击元素时出错: {selector}, 错误: {e}")
            return False

    async def click_next_video(self):
        """尝试点击下一节按钮"""
        selectors = self.platform_config.get('next_button_selector', '.next_btn')
        for selector in selectors.split(','):
            selector = selector.strip()
            if await self.click_element(selector):
                return True
        logger.warning("未找到下一节按钮")
        return False

    async def get_page_title(self):
        """获取页面标题"""
        return await self.page.title()

    async def take_screenshot(self, path='screenshot.png'):
        """截图"""
        try:
            await self.page.screenshot(path=path, full_page=False)
            logger.info(f"截图已保存到: {path}")
            return True
        except Exception as e:
            logger.error(f"截图失败: {e}")
            return False

    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
            logger.info("浏览器已关闭")

    @property
    def is_playing(self):
        return self._is_playing

    @property
    def current_url(self):
        return self.page.url if self.page else None
