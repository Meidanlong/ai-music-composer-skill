# AI Music Composer Skill

> 通用AI歌曲制作流水线：上传你的自弹自唱Demo → 自动转码 → BPM/节拍/旋律分析 → 交互式歌词润色 → 调用国内音乐API生成企业级成品歌曲。
>
> 专为AI短剧/漫剧OST创作场景设计，支持多轮交互修改歌词与局部旋律。

## ✨ 核心能力

| 模块 | 功能 |
|------|------|
| 音频预处理 | 自动探测格式，ffmpeg标准化为 16bit/44.1kHz/单声道 WAV |
| 音频分析 | 提取BPM、节拍网格、主旋律MIDI动机，标记音准/节奏偏差 |
| 歌词润色 | 豆包API主模型优化语感与上口度，可选通义千问做全局一致性校验 |
| 音乐生成 | 对接国内云端音乐API（歌歌AI/天谱乐/音潮），旋律修正+编曲+人声 |
| 交互迭代 | 支持多轮对话修改指定段落歌词或旋律，局部重生成 |
| 任务管理 | 异步任务轮询，工程元数据持久化，临时音频自动清理 |

## 🏗️ 架构设计

```
用户输入(Demo音频+原始歌词+曲风)
    ↓
AudioPreprocessor  ──→  标准化WAV
    ↓
AudioAnalyzer      ──→  BPM/节拍/MIDI动机/偏差报告
    ↓
LyricEditor        ──→  结构化歌词(主歌/预副歌/副歌/桥段)
    ↓  [交互式多轮修改循环]
    ↓
MusicAPIClient     ──→  异步提交生成任务 → 轮询结果
    ↓
TaskManager        ──→  保存工程元数据 + 清理临时文件
    ↓
成品音频(人声+伴奏分轨)
```

## 📦 安装

### 前置依赖
- Python >= 3.10
- ffmpeg（系统级安装：`brew install ffmpeg`）

### 步骤
```bash
git clone https://github.com/Meidanlong/ai-music-composer-skill.git
cd ai-music-composer-skill

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# 编辑 .env 填入你的API密钥
```

## ⚙️ 配置说明

所有密钥通过环境变量注入，**代码中不硬编码任何敏感信息**：

| 变量 | 必填 | 说明 |
|------|------|------|
| `DOUBAO_API_KEY` | ✅ | 豆包API密钥，用于歌词润色 |
| `QWEN_API_KEY` | ❌ | 通义千问密钥，用于全局歌词校验 |
| `MUSIC_API_PROVIDER` | ✅ | 音乐服务商：`getge` / `tianpule` / `yinchao` |
| `MUSIC_API_KEY` | ✅ | 音乐API密钥 |

## 🚀 快速开始

```bash
python src/main.py
```

按提示输入：
1. 本地Demo音频路径（支持mp3/m4a/wav/flac等任意格式）
2. 原始歌词文本
3. 目标曲风（如：华语流行/民谣/摇滚/R&B）

进入交互模式后：
- 输入修改指令（如："副歌第二句重写得更伤感一点"）
- 输入 `ok` 确认歌词定稿，开始生成歌曲

## 📁 项目结构

```
ai-music-composer-skill/
├── .gitignore
├── .env.example          # 环境变量模板
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py           # 流水线主入口
│   ├── audio_preprocessor.py  # 音频转码/格式标准化
│   ├── audio_analyzer.py     # BPM/节拍/旋律提取
│   ├── lyric_editor.py       # 豆包+千问歌词润色
│   ├── music_api_client.py    # 多服务商音乐API封装
│   └── task_manager.py        # 异步任务管理
├── examples/
│   └── demo_prompt.json  # 输入示例
└── tests/
    └── test_pipeline.py # 单元测试
```

## 🔒 安全合规

- 仓库**不存储任何用户音频文件**，临时文件仅存在于运行时 `tmp/` 目录，任务结束自动删除
- 所有API密钥通过 `.env` 环境变量读取，`.env` 已加入 `.gitignore`
- 日志输出自动脱敏，不打印密钥或用户隐私信息
- 生成的音乐版权归用户所有（具体以音乐服务商协议为准）

## 🛣️ 路线图

- [ ] 接入 librosa + crepe 实现真实音高检测与音准修正
- [ ] 增加 FastAPI 封装，支持HTTP接口调用
- [ ] 支持局部片段重生成（选定时间区间单独重做）
- [ ] 增加分轨导出与人声/伴奏分离
- [ ] 支持自定义曲风Prompt与情感标签
- [ ] 增加批量生成模式

## 📄 License

MIT
