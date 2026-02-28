# 任务：[填写功能名称]
> Status: Planning / In-progress / Done

本文件夹是一个**独立 Feature 工作区**，有关该 Feature 的一切文档与追踪记录**必须局限在此文件夹内**。

## 📍 关联文件 (Target Context)
*Agent 请优先且仅使用 `view_file` 阅读以下核心文件，避免全库检索导致上下文污染。*
- `src/path/to/file1.py`
- `src/path/to/file2.vue`

## 📁 工作区指南 (Workspace Guide)
1. **`README.md` (当前文件)**：用于描述需求背景，以及进行每日工作日志 (Progress Log) 打卡。
2. **`plan.md`**：用于描绘解决该需求的技术实现草图（架构调整、库表设计等）。
3. **`task.md`**：基于该需求制定的细化 TDD 开发步骤（Red -> Green -> Refactor 等），直接在里面打钩。

## 📅 开发日志 (Progress Log)
*项目要求：每次阶段性收工或交接前，必须在此处追加日志。所有当前 Feature 的进度和阻碍点都应当自治且仅记录在本文件中。*

- **[YYYY-MM-DD]**: 
  - **Current Context**: [你刚才做了什么，遇到了什么问题]
  - **Next Action**: [下一步接手的 Agent 应该继续做什么]

## ✅ 归档流程 (Archiving)
*任务完成后，请务必执行以下归档动作：*
1. 将本文档顶部的 `Status` 改为 `Done`。
2. 去项目根目录的 `OPTIONS.md` 中，将本任务从“待开发”移入“已完成”。
