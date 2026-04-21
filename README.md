# 智能体开发极简教程

本教程面向希望系统学习智能体开发的读者，内容从基础概念逐步推进到最小实现与工程实践，适合作为自学材料、课程参考资料或教学配套讲义使用。

整套内容围绕智能体开发中的几个核心主题展开，包括：

- 智能体的基本概念与整体结构；
- Prompt 与 Prompt Engineering；
- Tools、Skills 与 MCP 的使用方式；
- Agent 的最小实现与组合方式；
- Gateway、记忆、检索与低代码平台等进阶主题。

## 适合哪些读者

- 希望从零开始理解智能体开发流程的初学者；
- 已经听过相关概念，但希望进一步理解底层结构与代码实现的读者；
- 希望将智能体内容用于课程、培训或项目实践的教师与开发者；
- 想边阅读边动手，通过配套代码和作业逐步上手的学习者。

## 如何阅读本教程

如果希望在线阅读，建议直接访问 GitHub Pages 部署后的教程站点。站点中已经按“基础部分”和“进阶部分”组织好阅读顺序，适合顺序学习，也适合按主题跳读。

教程网页地址：

- [智能体原理与实现教程网站](https://iot-book.github.io/How-Agent/)

如果希望从头开始阅读，建议先从引言进入，再依次学习 Prompt、Tools、Skills、MCP、Agent 与 Gateway 等章节。

## 仓库内容说明

本仓库主要包含两部分内容：

- `docs/`：教程正文、章节图片以及 MkDocs 站点配置所需的文档内容；
- `minimal_agents/`：教程配套的教学示例、作业模板与最小实现代码。
- `ppt/`：配套ppt，还比较初步，仅仅作为参考

其中：

- `minimal_agents/examples/` 对应各章节中的教学案例；
- `minimal_agents/hw/` 对应各章节中的作业练习；
- `minimal_agents/src/` 提供教程中使用到的最小智能体实现；
- `minimal_agents/tests/` 提供部分自动化测试示例。

## 在线阅读

可直接通过以下地址访问我们提供的在线网站：

- [智能体原理与实现教程网站](https://iot-book.github.io/How-Agent/)

## 配套代码的使用方式

本教程中的很多章节都配有可运行示例与作业模板。阅读时可以结合 `minimal_agents/` 中的目录一起查看：

- 想看教学示例，可进入 `minimal_agents/examples/chapter-x/`
- 想完成章节作业，可进入 `minimal_agents/hw/chapter-x/`
- 想理解底层实现，可进入 `minimal_agents/src/minimal_agents/`
