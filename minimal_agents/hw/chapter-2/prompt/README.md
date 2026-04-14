# 第二章作业：Prompt 技术练习

这一目录对应教程中的“第二章 提示词工程”。本章作业的目标不是机械填写答案，而是通过修改 Prompt、运行脚本、观察输出结果，理解不同提示技术在真实任务中的作用。

## 一、目录说明

当前目录下已经准备好以下练习文件：

- `k_shot_prompting.py`
- `chain_of_thought.py`
- `tool_calling.py`
- `self_consistency_prompting.py`
- `rag.py`
- `reflexion.py`

每个文件都对应一种常见 Prompt 技术或相关应用方式。具体要求已经写在各自文件顶部，开始前建议先逐个阅读说明。

## 二、环境准备

本组练习默认使用 Ollama 在本地运行模型。

### 1. 安装 Ollama

请根据自己的操作系统完成安装：

#### macOS

```bash
brew install --cask ollama
ollama serve
```

#### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Windows

请前往 <https://ollama.com/> 下载并安装。

安装完成后，可以先检查版本：

```bash
ollama -v
```

### 2. 拉取模型

运行练习前，请先下载本次作业使用的模型：

```bash
ollama run llama3.1:8b
```

模型只需要下载一次。

### 3. 安装 Python 依赖

```bash
pip install ollama python-dotenv
```

## 三、如何完成

建议按下面的方式完成本章作业：

1. 先从 `k_shot_prompting.py` 和 `chain_of_thought.py` 开始，熟悉最基础的 Prompt 修改方式。
2. 在每个文件中找到 `TODO` 标注的位置，先补全 Prompt，再运行脚本观察输出。
3. 如果结果不稳定，不要急着换任务，而是回到 Prompt 本身继续修改。
4. 完成基础练习后，再继续尝试 `tool_calling.py`、`rag.py`、`reflexion.py` 等更复杂的场景。

本章的重点不在于“把空填上”本身，而在于通过一轮轮修改 Prompt，理解不同写法为什么会影响模型结果。

需要特别说明的是：本组练习默认使用的是本地运行模型，模型能力本身有限，因此像 `k_shot_prompting.py` 这类任务，结果有时并不会非常稳定。同一个 Prompt 在不同轮次里，可能表现并不完全一致。这是正常现象。

因此，这一章作业更重要的目标不是“机械追求每次都一次通过”，而是去体会：

- Few-shot 为什么有时能帮助模型更容易进入正确模式；
- 为什么有些 Prompt 改法能提高稳定性；
- 当模型能力有限时，Prompt 能改善什么，又不能完全解决什么。

## 四、完成要求

请尽量做到以下几点：

- 阅读每个文件顶部的任务说明；
- 只优先修改 `TODO` 标注的位置；
- 保留你最终使用的 Prompt；
- 记录模型输出结果；
- 对比不同 Prompt 写法带来的差异。

## 五、建议记录内容

建议为每个练习至少记录以下内容：

- 初始 Prompt
- 修改后的 Prompt
- 最终通过测试的 Prompt
- 对应输出结果
- 你认为这类技术最适合什么任务

## 六、提醒

- 不要把重点放在“绕过要求”上，而要真正通过 Prompt 改进结果。
- 如果某个任务不稳定，可以从“指令是否清楚”“是否缺少步骤”“是否缺少示例”这几个方向继续调整。
- 对于知识型或工具型任务，要特别注意 Prompt 是否说明了边界、格式和约束条件。

## 七、参考思路

完成这些练习后，可以进一步思考下面几个问题：

- Few-shot 为什么比 Zero-shot 更稳定？
- 什么情况下需要让模型分步骤思考？
- 为什么有些任务只靠 Prompt 不够，还需要工具或检索？
- 当任务变复杂时，Prompt 在系统里承担的到底是什么角色？
