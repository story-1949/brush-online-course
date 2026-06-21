# 网课自动播放助手 - 快速入门

## 第一步：安装依赖

打开 PowerShell，执行：

`powershell
cd E:\yunjiangzuo\project\shuakejiaoben
pip install -r requirements.txt
playwright install chromium
`

## 第二步：添加课程

运行程序，选择"1. 添加新课程"：

`powershell
python main.py
`

按照提示输入：
- 课程名称（如：高等数学）
- 选择平台编号（如：1=超星学习通）
- 粘贴课程URL

## 第三步：开始学习

选择"3. 开始学习"，然后：

1. 程序会自动打开浏览器并跳转到课程页面
2. **你需要手动登录**（浏览器窗口会弹出）
3. 登录完成后按回车
4. 选择模式：
   - **自动模式**：自动播放、自动切下一节
   - **交互模式**：手动控制播放/暂停/切换

## 第四步：查看进度

选择"4. 查看学习进度"或"5. 导出学习报告"

## 注意事项

- 首次使用前需要在浏览器中手动登录一次
- 程序会自动检测视频暂停并尝试恢复播放
- 播放速度默认2倍，可在 config/settings.yaml 中修改
- 数据保存在 data/ 目录下
