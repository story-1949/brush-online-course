# 网课自动播放助手

一个基于 Playwright 的网课视频自动播放辅助工具，支持多平台自动识别、自动倍速播放、进度追踪等功能。

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-1.40+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

</div>

## ✨ 功能特性

- **多平台支持**：超星学习通、智慧树、ICVE、中国大学MOOC、爱课程
- **URL 自动识别**：粘贴课程链接即可自动识别所属平台，无需手动选择
- **自动倍速播放**：支持 1x~4x 速度调节，默认 2 倍速
- **进度实时监控**：显示播放进度条，自动记录每个视频的播放进度
- **暂停自动恢复**：检测到视频暂停时自动尝试恢复播放
- **自动切换下一节**：当前视频播放完成后自动切换到下一节
- **进度持久化**：课程列表和播放进度自动保存到本地文件
- **学习报告导出**：一键导出各课程的完成率统计

## 📦 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/story-1949/-
cd -
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装浏览器内核

```bash
playwright install chromium
```

> 首次运行会自动下载 Chromium 浏览器（约 180MB），请耐心等待。

## 🚀 使用方法

### 方式一：交互式菜单（推荐）

```bash
python main.py
```

进入主菜单后按提示操作：

```
==================================================
       网课自动播放助手 v1.0
==================================================

  1. 添加新课程
  2. 列出所有课程
  3. 开始学习
  4. 查看学习进度
  5. 导出学习报告
  6. 修改设置
  0. 退出

==================================================
请选择操作:
```

#### 添加课程流程

1. 选择 `1` 添加新课程
2. 输入课程名称（留空则使用平台名）
3. 粘贴课程 URL（系统自动识别平台）
4. 确认后课程即被添加

#### 开始学习流程

1. 选择 `3` 开始学习
2. 选择要学习的课程编号
3. 选择学习模式：
   - **自动模式**：程序自动播放、自动切换下一节，全程无需操作
   - **交互模式**：手动控制播放/暂停/切换
4. 浏览器窗口弹出后，**手动登录**你的网课账号
5. 登录完成后按回车，程序自动开始播放

### 方式二：命令行参数

```bash
# 列出已添加的课程
python main.py --list

# 查看学习进度
python main.py --progress

# 导出学习报告
python main.py --report

# 快速开始学习第1门课程
python main.py --quick 1
```

## 📖 支持的平台

| 平台 | 识别域名 |
|------|----------|
| 超星学习通 | chaoxing.com, mooc*.chaoxing.com |
| 智慧树 | zhihuishu.com, account.zhihuishu.com |
| ICVE | icve.com.cn |
| 中国大学MOOC | icourse163.org |
| 爱课程 | icourses.cn |

## ⚙️ 配置说明

### 全局配置 (`config/settings.yaml`)

```yaml
general:
  playback_speed: 2.0      # 播放速度 (1.0 - 4.0)
  auto_next_delay: 3       # 视频结束后等待几秒自动切下一节
  max_video_duration: 3600 # 单视频最大时长(秒)，超过则停止
  headless: false          # 是否隐藏浏览器窗口(true=后台运行)
  browser: chromium        # 浏览器内核: chromium / firefox / webkit
```

### 数据文件

- `data/courses.json` — 课程列表
- `data/progress.json` — 各视频播放进度
- `data/report_*.json` — 导出的学习报告

## 🗂️ 项目结构

```
shuakejiaoben/
├── main.py                  # 主程序入口
├── requirements.txt         # Python 依赖
├── .gitignore
├── config/
│   ├── __init__.py
│   ├── settings.py          # 配置管理 + URL 平台识别
│   └── settings.yaml        # 用户配置文件
├── core/
│   ├── __init__.py
│   ├── player.py            # Playwright 视频播放引擎
│   ├── study_session.py     # 学习会话控制
│   └── course_manager.py    # 课程与进度管理
├── utils/
│   ├── __init__.py
│   └── helpers.py           # 工具函数
├── data/                    # 运行时数据（自动生成）
└── docs/
    ├── README.md
    └── QUICKSTART.md
```

## 🔧 常见问题

**Q: 浏览器打不开或白屏？**
A: 确保已执行 `playwright install chromium`，首次安装需下载浏览器内核。

**Q: 视频不播放或进度不前进？**
A: 检查是否已成功登录网课平台；部分平台需要手动触发播放按钮。

**Q: 如何后台运行？**
A: 在 `config/settings.yaml` 中将 `headless` 设为 `true`。

**Q: 支持哪些视频格式？**
A: 支持所有通过 HTML5 `<video>` 标签播放的视频，主流网课平台均兼容。

## ⚠️ 免责声明

本项目仅用于个人学习辅助，请勿用于商业目的或违反平台服务条款的行为。使用者需自行承担相关责任。

## 📄 License

MIT License
