# Dashboard 审查报告

> 审查对象：[dashboard.html](../工具/dashboard.html)  
> 对照文档：[营地设置模板方案.md](营地设置模板方案.md)  
> 审查日期：2026-07-03

---

## 一、总体结论

**方案本身设计通过审查**，思路清晰、复用充分。但 dashboard.html **尚未实现方案中的任何改动**——方案是一份待实施的修改规格书，当前代码仍处于改动前的状态。

---

## 二、方案质量审查

### ✅ 做得好的部分

| 方面 | 评价 |
|------|------|
| **复用优先** | 模板数据格式 = `data.tasks` 条目格式，零转换。表格编辑函数全部复用，改动量最小 |
| **存储方案** | `localStorage` key `camp_templates` 独立于 `camp_data`，生命周期清晰 |
| **预设模板** | 10 个硬编码模板覆盖了参考文档的全部内容，首次使用时自动写入 |
| **不改清单** | 方案 2.5 节明确列出了不改的区域，有克制力 |
| **任务池拆分逻辑** | 通过 `type` 或 `assignee` 区分工作人员/共创人，不引入新的数据结构 |

### ⚠️ 方案缺失的细节（建议补充）

#### 1. 两个任务池需要两套独立的 JS 状态变量

当前代码只有一个 `settingTasks` 数组（dashboard.html:2215）。拆分后需要 `settingStaffTasks` 和 `settingCreatorTasks` 两个独立数组，方案没有提到这一点。

#### 2. 模板的 `type` 字段与任务的 `type` 字段命名冲突

方案定义的模板结构：
```json
{ "工作人员-筹备会完整包": { "type": "staff", "tasks": [...] } }
```

但任务条目本身也有 `type` 字段（`初始`/`新增`/`变更`）——参见 dashboard.html:643。建议模板级别的分类字段改名为 `pool` 以避免混淆。

#### 3. 子标签标识符没有定义

当前 `switchSettingsTab` 接受 `'tasks','team','budget','schedule','ai'` 五个值（dashboard.html:2219）。6 个子页后，新标识符建议：
- `'staffTasks'` → ① 工作人员任务池
- `'creatorTasks'` → ② 共创人任务池

#### 4. 边缘情况未覆盖

- 任务池有未保存内容时点击「使用模板」是否需要确认？
- 保存模板时名称冲突如何处理（覆盖还是拒绝）？
- 删除模板的 UI 入口在哪里？（方案提到了 `deleteTemplate` 函数但没有 UI）

#### 5. 模板选择器是独立的还是共享的？

方案 2.2 说「位于「＋ 添加行」按钮左侧」，但拆分后有两个「＋ 添加行」按钮。工作人员的模板和共创人的模板应该分开管理——需要两个独立的模板下拉框。

---

## 三、代码就绪度审查（逐项对比）

对照方案第三章「实现步骤」7 条：

| # | 步骤 | 状态 | 当前代码位置 |
|---|------|------|-------------|
| 1 | 子标签从 5→6，文案调整 | ❌ 未实现 | dashboard.html:507-513 仍为 5 个 |
| 2 | 新增「② 共创人任务池」HTML | ❌ 未实现 | 只有 `#set-tasks` 一个任务池卡片 |
| 3 | 模板选择器 + 使用/保存按钮 | ❌ 未实现 | 任务池上方无任何模板控件 |
| 4 | 模板管理函数 | ❌ 未实现 | JS 中无 `loadTemplates`/`saveTemplate` 等函数 |
| 5 | 10 个预设模板硬编码 | ❌ 未实现 | 无任何预设数据 |
| 6 | 预算「🔄 重置默认值」按钮 | ❌ 未实现 | dashboard.html:581 只有保存按钮 |
| 7 | `switchSettingsTab` 支持 6 个子页 | ❌ 未实现 | dashboard.html:2219 只处理 5 个 |

---

## 四、实施补充建议

### 4.1 JS 侧必需的函数清单

方案提到但未列全的函数：

```
模板层：
  loadTemplates()              — 从 localStorage 加载模板
  saveTemplate(name, pool)     — 保存当前任务池为模板
  deleteTemplate(name)         — 删除指定模板
  applyTemplate(name, pool)    — 将模板应用到当前任务池

任务池层：
  renderSettingStaffTasks()    — 替代 renderSettingTasks（工作人员池）
  renderSettingCreatorTasks()  — 共创人任务池渲染
  commitSettingStaffTasks()    — 提交工作人员任务
  commitSettingCreatorTasks()  — 提交共创人任务

预算层：
  resetBudgetDefaults()        — 恢复预算默认值
```

### 4.2 HTML 侧必需的 DOM 元素

- `#set-creatorTasks` — 共创人任务池卡片（复用 `#set-tasks` 结构）
- 两个 `<select>` 模板下拉框（工作人员池和共创人池各一个）
- 两个「📥 使用模板」按钮
- 两个「💾 保存为模板」按钮
- 一个「🔄 重置默认值」按钮（预算页）

### 4.3 子标签按钮的编号映射

```
① 工作人员任务池 → ② 共创人任务池 → ③ 团队 → ④ 预算 → ⑤ 日程框架 → ⑥ AI导入
```

### 4.4 CSS 注意事项

新增 1 个子标签按钮 + 模板下拉框 + 两个按钮，需确认在小屏幕下子标签行不会溢出（当前已有 `overflow-x:auto`）。

---

## 五、关键文件锚点

| 区域 | 文件位置 |
|------|---------|
| 营地设置子标签按钮 | dashboard.html:507-513 |
| ① 任务池 HTML | dashboard.html:516-543 |
| ④ 预算 HTML | dashboard.html:562-583 |
| `switchSettingsTab` 函数 | dashboard.html:2217-2226 |
| `settingTasks` 状态变量 | dashboard.html:2215 |
| `renderSettingTasks` 函数 | dashboard.html:2252-2270 |
| `commitSettingTasks` 函数 | dashboard.html:2278-2294 |
