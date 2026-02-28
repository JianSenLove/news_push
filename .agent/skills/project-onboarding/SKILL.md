---
name: project-onboarding
description: 项目入门和 Agent 开发协作规范。当新的 Agent 首次接触本代码库，或用户要求开始执行一个新任务、认领一个新需求时，或者用户要求使用项目规范时，必须首先阅读并遵循此技能指南。它包含了如何避免上下文污染、针对 TDD 开发模式的要求，以及记录开发进度的最佳实践。
---

# Project Onboarding (Agent 协作开发规范)

欢迎你，AI智能体！为了让这个项目在多次跌代和多 Agent 协同中保持健康，我们采用了**解耦式任务管理**和**极度严谨的 TDD 开发流**架构。
无论你是来修 Bug 还是开发新特性的，**请务必严格遵守以下准则**：

## 1. 任务接手机制 (Context Restoration First)

1. **不要盲目全库搜索**：不要一开始就滥用 `grep_search`。
2. **查阅总索引**：阅读根目录的 `OPTIONS.md` 获取目前全局存在的各项解耦任务大纲图景。（注：原有在根目录的 `docs_task.md` 等文件现已全部归档至 `docs/archive/`，它们为项目初期创建的历史快照，已**停止更新**，仅作追溯参考）。
3. **定位功能目录 (Feature Workspace)**：如果任务在 `OPTIONS.md` 中指向了 `docs/features/` 下的具体子目录，定向进入那个具体的 feature 工作区。
4. **加载工作区上下文**：
   - 优先阅读工作区内的 `README.md`，它包含了该任务的背景、状态和 `📍 关联文件` 清单。请严格限制你的视线在这些文件中。
   - 随后阅读 `plan.md` (如果有) 和 `task.md` 获取技术架构及子工作项。
   - 始终阅读 `README.md` 底部的 `📅 开发日志 (Progress Log)` 了解前面的人刚做了什么。

## 2. 严格遵循 TDD 模式 (Target Context & Red-Green)

本项目坚持测试驱动开发（框架：`pytest`）。
1. **编写测试优先**：对任何新功能，先在 `tests/` 目录下编写或者更新对应的高覆盖率用例。在子目录的 `task.md` 待办状态里，这标志为 `[RED]` 阶段。
2. **填充业务逻辑**：随后再去 `src/` 目录下写实际代码直至测试跑通 `[GREEN]`。

## 3. 完工和归档流 (Lifecycle Archiving)

当你的修改被 `pytest` 变绿并确认无误后：
1. **日志打卡（最高优先级）**：在你当前正在处理的 **Feature 工作区的 `README.md` 结尾**，追加更新日志，说明你的当前上下文（Current Context）和下步动作（Next Action）。如果跳过这一步，下一个接手的 Agent 会完全失忆！
2. 将你当前正处理的子任务/TDD步骤在该 Feature 工作区的 `task.md` 中打勾标记为 `[x]`。
3. 如果是独立的全新功能开发完毕，更新这篇 Feature 工作区 `README.md` 顶部的 `Status` 为 `Done`，并在根部 `OPTIONS.md` 中将其挪入完成区。
4. 如果有额外的个人 Agent Task，也请输出全局的 `walkthrough.md` 走个人汇报流。

## 💥 红线规定 (Red Lines)
- **绝对不要在不写测试或故意抛开 TDD 的情况下去改动老代码！**
- **非必要不要使用 `grep_search` 开始“大扫荡”式寻代码，请从工作区关联文件与已有单元测试里顺藤摸瓜！**
- **绝不允许去更新 `docs/archive/` 里的旧档 (`docs_task.md` 等)。所有的进展追踪一定要收敛在 `docs/features/功能名/` 内部的三个文件 (`README`, `task`, `plan`) 中。**
