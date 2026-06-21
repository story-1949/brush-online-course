# -*- coding: utf-8 -*-
"""
课程管理器
负责管理课程列表、章节、视频进度等
"""
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CourseManager:
    """课程管理器"""

    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.progress_file = os.path.join(data_dir, 'progress.json')
        self.course_list_file = os.path.join(data_dir, 'courses.json')
        os.makedirs(data_dir, exist_ok=True)
        self.courses = self._load_courses()
        self.progress = self._load_progress()

    def _load_courses(self):
        if os.path.exists(self.course_list_file):
            with open(self.course_list_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def _save_courses(self):
        with open(self.course_list_file, 'w', encoding='utf-8') as f:
            json.dump(self.courses, f, ensure_ascii=False, indent=2)

    def _load_progress(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_progress(self):
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)

    def add_course(self, name, platform, url, chapters=None):
        course = {
            "name": name,
            "platform": platform,
            "url": url,
            "chapters": chapters or [],
            "added_at": datetime.now().isoformat()
        }
        self.courses.append(course)
        self._save_courses()
        logger.info(f"已添加课程: {name}")
        return course

    def remove_course(self, index):
        if 0 <= index < len(self.courses):
            removed = self.courses.pop(index)
            self._save_courses()
            logger.info(f"已删除课程: {removed['name']}")
            return removed
        return None

    def list_courses(self):
        return self.courses

    def get_course(self, index):
        if 0 <= index < len(self.courses):
            return self.courses[index]
        return None

    def save_video_progress(self, course_name, chapter_name, video_name, progress_seconds):
        key = f"{course_name}/{chapter_name}/{video_name}"
        self.progress[key] = {
            "progress_seconds": progress_seconds,
            "last_updated": datetime.now().isoformat(),
            "is_completed": False
        }
        self._save_progress()

    def get_video_progress(self, course_name, chapter_name, video_name):
        key = f"{course_name}/{chapter_name}/{video_name}"
        return self.progress.get(key, {})

    def mark_video_completed(self, course_name, chapter_name, video_name):
        key = f"{course_name}/{chapter_name}/{video_name}"
        if key in self.progress:
            self.progress[key]["is_completed"] = True
            self.progress[key]["completed_at"] = datetime.now().isoformat()
        self._save_progress()

    def get_completion_rate(self, course_name):
        completed = 0
        total = 0
        for key, data in self.progress.items():
            if key.startswith(course_name):
                total += 1
                if data.get("is_completed"):
                    completed += 1
        return (completed / total * 100) if total > 0 else 0

    def get_all_progress(self):
        return self.progress

    def export_report(self, output_path=None):
        if output_path is None:
            output_path = os.path.join(self.data_dir, f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')

        report = {
            "generated_at": datetime.now().isoformat(),
            "total_courses": len(self.courses),
            "courses": [],
            "overall_progress": {}
        }

        for course in self.courses:
            course_name = course["name"]
            rate = self.get_completion_rate(course_name)
            report["courses"].append({
                "name": course_name,
                "platform": course.get("platform", ""),
                "completion_rate": round(rate, 2),
                "videos_completed": sum(1 for k, v in self.progress.items()
                                        if k.startswith(course_name) and v.get("is_completed")),
                "total_videos": sum(1 for k in self.progress.keys() if k.startswith(course_name))
            })
            report["overall_progress"][course_name] = round(rate, 2)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"学习报告已导出到: {output_path}")
        return output_path
