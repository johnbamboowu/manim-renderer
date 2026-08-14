# 🎬 Manim Renderer — GitHub Actions 渲染管线

> 在云端免费渲染 Manim 动画，本地只写代码。

## 为什么需要这个？

Manim（3Blue1Brown 的动画引擎）在 ARM64 Windows 上装不了（`manimpango`/`moderngl` 无 ARM64 wheel）。  
这个仓库利用 **GitHub Actions 的免费 Linux x86_64 虚拟机**来渲染，本地零依赖。

## 快速开始

### 1. 写场景文件

在 `scenes/` 目录下创建 `.py` 文件，定义继承 `Scene` 的类：

```python
from manim import *

class MyScene(Scene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)
        self.play(Create(circle))
        self.wait()
```

### 2. 触发渲染

**方式 A：自动（推荐）**
```bash
python scripts/render.py
```
自动 git push → 等待 Actions → 下载 MP4 到 `output/`

**方式 B：手动**
```bash
git add scenes/my_scene.py
git commit -m "add my scene"
git push origin main
```
然后去 [Actions 页面](https://github.com/johnbamboowu/manim-renderer/actions) 等下载。

**方式 C：GitHub 网页**
点 Actions → Run workflow → 输入文件名 → 运行

### 3. 下载结果

- 自动下载到 `output/` 目录
- 或去 Actions 页面 → 点击最新 run → 底部 Artifacts 下载

## 渲染画质

| 参数 | 画质 | 分辨率 | 渲染时间 |
|------|------|--------|----------|
| `-ql` | 低 | 480p | 快（开发用） |
| `-qm` | 中 | 720p | 中等 |
| `-qh` | 高 | 1080p | 慢（默认） |
| `-qk` | 4K | 2160p | 很慢 |

Workflow 默认用 `-qh`（1080p），如失败自动降级到 `-ql`。

## 文件结构

```
manim-renderer/
├── .github/workflows/
│   └── render.yml          # GitHub Actions 工作流
├── scenes/
│   └── example.py          # 示例：将军过河问题
├── scripts/
│   └── render.py           # 本地渲染辅助脚本
├── output/                 # 下载的渲染结果（gitignore）
└── README.md
```

## 示例场景

### 将军过河问题（反射原理）

`scenes/example.py` 包含两个场景：
- `GeneralRiverCrossing` — 完整教学版（~2分钟）
- `QuickDemo` — 30秒快速版

## 注意事项

- GitHub Actions 免费额度：公共仓库无限，私有仓库 2000 分钟/月
- 首次渲染需安装依赖，约 3-5 分钟；后续有缓存，约 1-2 分钟
- artifact 保留 30 天
- 中文字体在 Actions 的 Ubuntu 上可能缺失，如需中文文字建议用 `Text(..., font="Noto Sans CJK SC")`
