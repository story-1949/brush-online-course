# -*- coding: utf-8 -*-
"""
网课自动播放助手 - 配置管理模块
支持多种网课平台的配置管理
"""
import yaml
import os
import re

DEFAULT_CONFIG = {
    "general": {
        "playback_speed": 2.0,
        "auto_next_delay": 3,
        "max_video_duration": 3600,
        "enable_notifications": True,
        "headless": False,
        "browser": "chromium",
        "timeout": 30000,
        "retry_count": 3,
        "retry_delay": 5
    },
    "platforms": {
        "chaoxing_xuexitong": {
            "name": "超星学习通",
            "login_url": "https://passport.chaoxing.com/login",
            "base_url": "https://mooc1-2.chaoxing.com",
            "video_selector": ".video_player, #video",
            "next_button_selector": ".next_btn, button[data-next]",
            "progress_selector": ".progress_bar, .current_time",
            "url_patterns": [
                r"chaoxing\.com",
                r"mooc[0-9]*\.chaoxing\.com",
                r"passport\.chaoxing\.com"
            ]
        },
        "zhinengzhi": {
            "name": "智慧树",
            "login_url": "https://account.zhihuishu.com/login",
            "base_url": "https://www.zhihuishu.com",
            "video_selector": ".video-container video, iframe[src*=player]",
            "next_button_selector": ".next-course, .next-btn",
            "progress_selector": ".progress-text",
            "url_patterns": [
                r"zhihuishu\.com",
                r"account\.zhihuishu\.com"
            ]
        },
        "icve": {
            "name": "ICVE",
            "login_url": "https://www.icve.com.cn/login",
            "base_url": "https://www.icve.com.cn",
            "video_selector": "video, .video-player video",
            "next_button_selector": ".next-step, .next-course",
            "progress_selector": ".progress-info",
            "url_patterns": [
                r"icve\.com\.cn"
            ]
        },
        "china_mooc": {
            "name": "中国大学MOOC",
            "login_url": "https://www.icourse163.org/user/login/jsonp",
            "base_url": "https://www.icourse163.org",
            "video_selector": "#videoFrame iframe, .mooc-video video",
            "next_button_selector": ".next-lesson, .btn-next",
            "progress_selector": ".lesson-progress",
            "url_patterns": [
                r"icourse163\.org",
                r"icourse\.org"
            ]
        },
        "icourses": {
            "name": "爱课程",
            "login_url": "https://www.icourses.cn/user/login",
            "base_url": "https://www.icourses.cn",
            "video_selector": "video, .player video",
            "next_button_selector": ".next-chapter, .btn-next",
            "progress_selector": ".progress-bar",
            "url_patterns": [
                r"icourses\.cn"
            ]
        }
    },
    "courses": []
}


def load_config(config_path=None):
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), 'settings.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f) or {}
        return _deep_merge(DEFAULT_CONFIG, user_config)
    return {k: (v.copy() if isinstance(v, dict) else list(v) if isinstance(v, list) else v)
            for k, v in DEFAULT_CONFIG.items()}


def _deep_merge(base, override):
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def save_config(config, config_path=None):
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), 'settings.yaml')
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)


def detect_platform_from_url(url):
    platforms = DEFAULT_CONFIG.get('platforms', {})
    for key, plat in platforms.items():
        patterns = plat.get('url_patterns', [])
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return key, plat.get('name', key)
    return None, None


def auto_detect_and_add_course(config, course_url, course_name=None):
    platform_key, platform_name = detect_platform_from_url(course_url)
    if platform_key is None:
        return False, f"无法识别平台，请手动指定。支持的域名: chaoxing.com, zhihuishu.com, icve.com.cn, icourse163.org, icourses.cn"
    if course_name is None:
        course_name = platform_name
    course = add_course(config, course_name, platform_key, course_url)
    return True, f"已识别为{platform_name}，课程已添加"


def add_course(config, course_name, platform, course_url, chapters=None):
    course = {
        "name": course_name,
        "platform": platform,
        "url": course_url,
        "chapters": chapters or [],
        "completed_chapters": [],
        "last_position": {}
    }
    config["courses"].append(course)
    return course


def get_platform_config(config, platform_key):
    platforms = config.get("platforms", {})
    for key, plat in platforms.items():
        if platform_key.lower() in key.lower() or plat.get("name", "").find(platform_key) >= 0:
            return plat
    return None


def get_course_by_index(config, index):
    courses = config.get("courses", [])
    return courses[index] if 0 <= index < len(courses) else None


if __name__ == "__main__":
    config = load_config()
    print("配置加载成功!")
    print(f"支持的平台: {list(config['platforms'].keys())}")

    test_urls = [
        "https://mooc1-2.chaoxing.com/mycourse/studentcourse?crcid=123",
        "https://www.zhihuishu.com/video/videoCourse.html",
        "https://www.icve.com.cn/course/detail/123",
        "https://www.icourse163.org/course/ZJU-1002092004",
        "https://www.icourses.cn/course/123.html"
    ]
    print("\nURL自动识别测试:")
    for url in test_urls:
        key, name = detect_platform_from_url(url)
        print(f"  {url[:55]}... -> {name} ({key})")
