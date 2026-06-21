# 网课自动播放助手

一个帮助学生高效完成视频课程学习的辅助工具。

## 功能特性

- 支持多平台：超星学习通、智慧树、ICVE、中国大学MOOC、爱课程
- 自动设置2倍速播放
- 自动记录学习进度
- 支持断点续学
- 导出学习报告

## 安装

`ash
pip install -r requirements.txt
playwright install chromium
`

## 使用

### 交互模式（推荐）
`ash
python main.py
`

### 快速启动模式
`ash
python main.py --quick 1
`

### 命令行参数
- --add - 添加课程
- --list - 列出课程
- --progress - 查看进度
- --report - 导出报告

## 配置

编辑 config/settings.yaml 修改播放速度等设置。
添加课程后会在 data/courses.json 中保存。
