# 剧本YAML Schema定义与设计说明

## 文档修订记录

| 版本 | 日期 | 作者 | 修订内容 |
|------|------|------|---------|
| v1.0 | 2026-06-05 | 剧本格式专家 | 初始版本，定义通用Schema及三种模式规范 |

---

## 1. YAML 选型理由

### 1.1 为什么选择 YAML 作为剧本输出格式

| 维度 | YAML | JSON | XML | Fountain | Final Draft (FDX) |
|------|------|------|-----|----------|-------------------|
| **人类可读性** | 优秀（无括号、无引号冗余） | 一般（`{}[]""` 干扰阅读） | 差（标签噪音大） | 优秀 | 优秀（但需专用软件） |
| **版本控制友好** | 优秀（逐行 diff 清晰） | 一般（嵌套深时 diff 难读） | 差（标签干扰 diff） | 一般 | 差（二进制/压缩 XML） |
| **编辑工具** | 任意文本编辑器 | 任意文本编辑器 | 任意文本编辑器 | 任意文本编辑器 | Final Draft 专用 |
| **Python 生态** | `PyYAML` 原生支持 | `json` 原生支持 | `lxml` 需额外依赖 | 需自行解析 | 需第三方库 |
| **结构化深度** | 支持任意嵌套 | 支持任意嵌套 | 支持任意嵌套 | 扁平（语法限制） | 支持任意嵌套 |
| **注释支持** | `#` 原生注释 | 无注释 | `<!-- -->` 冗余 | 有 | 有 |
| **多文档支持** | 原生（`---` 分隔） | 需数组包装 | 需根节点包装 | 无 | 无 |
| **行业认可度** | 高（CI/CD 配置标准） | 高（API 标准） | 低（遗留系统） | 中（编剧社区） | 高（好莱坞标准） |

**核心决策理由**：

1. **人类可读 + 结构化并存**：YAML 是唯一同时满足"编剧可直接阅读修改"和"程序可精确解析"的格式。编剧在预览页看到的就是最终文件的真实内容，所见即所得，无需额外渲染层。

2. **版本控制原生支持**：剧本创作是迭代过程，需频繁修改。YAML 的逐行结构使得 `git diff` 能清晰显示"第3场第2句对白从A改为B"，而 JSON 的嵌套结构在 diff 中会显示整段 JSON 变更。

3. **零依赖编辑器**：剧本可被任何文本编辑器打开（VS Code、Sublime、Vim），无需安装 Final Draft 等专业软件，降低使用门槛。同时 IDE 自带 YAML 语法高亮和 Schema 校验。

4. **Python 生态无缝集成**：`PyYAML` 是 Python 标准库级依赖，`yaml.safe_load()` / `yaml.dump()` 即可完成序列化/反序列化，配合 `jsonschema` 进行结构校验，技术栈统一。

5. **LLM 友好**：DeepSeek 等大模型在训练数据中接触了大量 YAML 格式内容（配置文件、Ansible Playbook 等），对 YAML 语法天然亲和，生成准确率高于自定义 DSL。

---

## 2. 通用 Schema 顶层结构

### 2.1 根节点定义

```yaml
# ===== 通用剧本文件根结构 =====
schema_version: "1.0"          # Schema 版本号，用于未来兼容性
meta:                          # 元数据块
characters:                    # 角色列表
script:                        # 剧本正文（结构由 script_type 决定）
```

### 2.2 schema_version 字段

`schema_version` 是 **必填** 的语义化版本号，用于标识此文件遵循的 Schema 规范版本。当 Schema 升级时（如新增字段、修改枚举值），解析器可根据此字段选择对应的校验规则，确保向后兼容。

| 版本 | 变更内容 |
|------|---------|
| `1.0` | 初始版本，支持 movie / tv_series / mini_series 三种模式 |

---

## 3. 元数据块（meta）

### 3.1 字段定义

```yaml
meta:
  title: "剧本标题"              # 必填，剧本名称
  source_novel: "原著小说名"      # 必填，原小说标题
  author: "原作者"               # 必填，原小说作者
  script_type: "movie"          # 必填，枚举值: movie | tv_series | mini_series
  total_episodes: null          # 条件必填：tv_series 和 mini_series 时必填
  estimated_duration: null      # 可选：预计总时长（分钟），电影约90-120，电视剧按集×45估算
  language: "zh-CN"             # 可选，默认 zh-CN
  version: 1                    # 剧本自身版本号（用户编辑次数），默认 1
  created_at: "2026-06-05T10:00:00Z"   # 必填，ISO 8601 UTC 时间
  updated_at: "2026-06-05T12:30:00Z"   # 可选，最后修改时间
  notes: ""                     # 可选，编剧备注
```

### 3.2 字段约束

| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| `title` | string | 是 | 1-200 字符 |
| `source_novel` | string | 是 | 1-500 字符 |
| `author` | string | 是 | 1-200 字符 |
| `script_type` | enum | 是 | `movie` / `tv_series` / `mini_series` |
| `total_episodes` | int | 条件 | `script_type` ≠ `movie` 时必填，≥1 |
| `estimated_duration` | int | 否 | 单位：分钟 |
| `language` | string | 否 | BCP 47 语言标签 |
| `version` | int | 否 | ≥1，默认 1 |
| `created_at` | string | 是 | ISO 8601 UTC |
| `updated_at` | string | 否 | ISO 8601 UTC |
| `notes` | string | 否 | 最多 5000 字符 |

---

## 4. 角色列表（characters）

### 4.1 字段定义

```yaml
characters:
  - id: "char_001"              # 必填，唯一标识，格式: char_XXX
    name: "张三"                # 必填，角色姓名
    aliases: ["三哥", "老张"]   # 可选，别名/昵称列表
    gender: "male"              # 必填，male / female / other
    age: 28                     # 可选，年龄（数字或描述如"30岁左右"）
    age_display: "28岁"         # 可选，年龄展示文本
    personality_tags:           # 必填，性格标签列表
      - "沉稳"
      - "内敛"
      - "正义感强"
    role: "protagonist"         # 必填，protagonist / antagonist / supporting / cameo
    description: |              # 必填，角色详细描述（支持多行）
      一名退役特种兵，曾在某次任务中失去战友，
      此后一直生活在自责中。性格沉稳内敛，但
      面对不公时会爆发出惊人的行动力。
    first_appearance: "scene_001"  # 必填，首次出场场次ID
    first_appearance_episode: 1    # 可选，电视剧/微短剧首次出场集数
    notes: ""                   # 可选，编剧备注
```

### 4.2 字段约束

| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| `id` | string | 是 | 格式 `char_\d{3}`，全局唯一 |
| `name` | string | 是 | 1-100 字符 |
| `aliases` | list[string] | 否 | 每个别名 1-50 字符 |
| `gender` | enum | 是 | `male` / `female` / `other` |
| `age` | string/int | 否 | 数字或"未知" |
| `age_display` | string | 否 | 展示用文本 |
| `personality_tags` | list[string] | 是 | 至少 1 个标签，每个 1-20 字符 |
| `role` | enum | 是 | `protagonist` / `antagonist` / `supporting` / `cameo` |
| `description` | string | 是 | 10-500 字符 |
| `first_appearance` | string | 是 | 必须引用存在的 scene_id |
| `first_appearance_episode` | int | 否 | 电视剧/微短剧场景下 |
| `notes` | string | 否 | 最多 500 字符 |

### 4.3 角色 ID 引用校验

剧本中所有对白节点（`dialogue`）的 `character` 字段必须引用 `characters` 列表中已声明的 `id`。在 Schema 校验阶段，解析器需建立角色 ID 集合并进行交叉验证。

---

## 5. 内容节点类型

### 5.1 节点类型总览

剧本的最小内容单元是"节点"，一场戏（scene）的 `content` 字段由有序的节点列表组成。节点有三种类型：

| 类型 | 用途 | 示例 |
|------|------|------|
| `dialogue` | 角色对白 | 角色说话内容 |
| `action` | 动作描述 | 角色的肢体动作、行为 |
| `description` | 场景描述 | 环境、氛围、镜头建议等 |

### 5.2 对白节点（dialogue）

```yaml
- type: "dialogue"             # 固定值
  character: "char_001"        # 必填，说话角色ID（引用 characters[].id）
  text: "三年了，还是逃不掉。"  # 必填，对白内容
  delivery: ""                 # 可选，表演提示（如"低声"、"愤怒"、"自言自语"）
  to: "char_002"               # 可选，对话目标角色ID
  note: ""                     # 可选，编剧备注
```

| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| `type` | const | 是 | 固定值 `"dialogue"` |
| `character` | string | 是 | 引用 `characters[].id` |
| `text` | string | 是 | 1-2000 字符 |
| `delivery` | string | 否 | 表演提示，1-100 字符 |
| `to` | string | 否 | 引用 `characters[].id` |
| `note` | string | 否 | 编剧备注 |

### 5.3 动作节点（action）

```yaml
- type: "action"               # 固定值
  text: "张三推开房门，环顾四周。桌上落满灰尘，显然很久没人来过。"  # 必填
  subject: "char_001"          # 可选，动作执行者角色ID
  note: ""                     # 可选，编剧备注
```

| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| `type` | const | 是 | 固定值 `"action"` |
| `text` | string | 是 | 1-2000 字符 |
| `subject` | string | 否 | 引用 `characters[].id` |
| `note` | string | 否 | 编剧备注 |

### 5.4 描述节点（description）

```yaml
- type: "description"          # 固定值
  text: "雨夜，霓虹灯倒映在积水的街道上。远处传来警笛声，由远及近。"  # 必填
  category: "environment"      # 可选，描述类别: environment / atmosphere / transition / camera
  note: ""                     # 可选，编剧备注
```

| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| `type` | const | 是 | 固定值 `"description"` |
| `text` | string | 是 | 1-2000 字符 |
| `category` | enum | 否 | `environment` / `atmosphere` / `transition` / `camera` |
| `note` | string | 否 | 编剧备注 |

### 5.5 节点使用规范

- **按故事时间顺序排列**：`content` 列表中的节点顺序即为场景内的事件发生顺序
- **三种节点可任意组合**：一场戏可包含任意数量的对白/动作/描述节点，也可无对白（纯动作场景）
- **对白节点必须引用角色**：`dialogue.character` 必须在 `characters` 列表中声明，否则 Schema 校验失败

---

## 6. 场景（Scene）统一定义

### 6.1 场景对象结构

无论哪种剧本类型，每一场戏（Scene）都遵循相同的结构定义：

```yaml
- scene_id: "scene_001"        # 必填，全局唯一场景标识
  scene_number: 1              # 可选，场景序号（连贯编号）
  location: "张三的公寓 - 客厅" # 必填，场景地点
  setting: "interior"          # 必填，interior(内景) / exterior(外景) / interior_exterior(内外兼有)
  time: "night"                # 必填，day(日) / night(夜) / dawn(晨) / dusk(昏) / 具体时刻如"下午3点"
  time_detail: "深夜，约凌晨2点" # 可选，时间详细描述
  characters_present:          # 必填，本场出场角色ID列表
    - "char_001"
  duration_seconds: null       # 条件必填：mini_series 时必填，预估本场时长（秒）
  content:                     # 必填，内容节点序列
    - type: "action"
      text: "..."
    - type: "dialogue"
      character: "char_001"
      text: "..."
  notes: ""                    # 可选，编剧备注
```

### 6.2 字段约束

| 字段 | 类型 | 必填 | 约束 |
|------|------|------|------|
| `scene_id` | string | 是 | 格式 `scene_\d{3}`，或 `ep{N}_scene_{M}`，全局唯一 |
| `scene_number` | int | 否 | 连贯编号，≥1 |
| `location` | string | 是 | 1-200 字符 |
| `setting` | enum | 是 | `interior` / `exterior` / `interior_exterior` |
| `time` | string | 是 | `day` / `night` / `dawn` / `dusk` / 自定义时刻 |
| `time_detail` | string | 否 | 补充时间描述 |
| `characters_present` | list[string] | 是 | 至少 1 个角色ID，均需在 `characters` 中声明 |
| `duration_seconds` | int | 条件 | 微短剧模式必填，≥1 秒 |
| `content` | list[node] | 是 | 至少 1 个内容节点 |
| `notes` | string | 否 | 最多 500 字符 |

---

## 7. 三种模式的 Schema 定义

### 7.1 模式一：电影（movie）

#### 结构特征

```
script
  └── acts:                    # 幕列表（通常是三幕结构）
        ├── act: 1
        │   ├── title: "建置"   # 幕标题
        │   └── scenes: [...]   # 场列表
        ├── act: 2
        │   ├── title: "对抗"
        │   └── scenes: [...]
        └── act: 3
            ├── title: "结局"
            └── scenes: [...]
```

#### 设计原因

电影剧本采用**扁平化"幕→场"两级结构**，因为：

1. **电影是单次叙事**：故事在 90-120 分钟内完整讲述，不存在"分集"概念，只需要幕和场两个层级
2. **三幕结构是行业标准**：建置（Setup）→ 对抗（Confrontation）→ 结局（Resolution），所有场次均匀分布在这三幕中
3. **场景连贯编号**：全片场景从 1 到约 120 连续编号，便于调度和排期

#### 电影模式特有字段

| 字段 | 层级 | 说明 |
|------|------|------|
| `acts` | script | 幕列表，通常 3 幕（允许 1-5 幕） |
| `act.title` | 幕 | 幕标题，如"建置"、"对抗"、"结局" |

#### 电影模式不存在的字段

- `episodes`（无分集概念）
- `hook`（无悬念钩子概念）
- `duration_seconds`（单场不需要精确到秒的时长）

---

### 7.2 模式二：电视剧（tv_series）

#### 结构特征

```
script
  └── episodes:                # 集列表
        ├── episode: 1
        │   ├── title: "归来"
        │   ├── acts:          # 本集内的幕列表
        │   │   ├── act: 1
        │   │   │   ├── title: "开场"
        │   │   │   └── scenes: [...]
        │   │   └── act: 2
        │   │       ├── title: "发展"
        │   │       └── scenes: [...]
        │   └── hook: "..."     # 本集悬念钩子（可选）
        ├── episode: 2
        │   └── ...
        └── episode: N
            └── ...
```

#### 设计原因

电视剧引入**"集→幕→场"三级嵌套**，因为：

1. **分集叙事是刚需**：电视剧 30-40 集，每集约 45 分钟，必须按集划分。每集是独立的叙事单元，有自己的起承转合。
2. **每集独立高潮**：电视剧的"集"层级确保每集都有独立的高潮和悬念，这是电视剧区别于电影的核心叙事特征。
3. **跨集人物弧光**：编剧需要在"集"这个粒度上规划角色发展，每集角色状态的变化需要清晰可追溯。
4. **制作排期粒度**：剧组按集排期拍摄，"集"是制作管理的基本单位。

#### 电视剧模式特有字段

| 字段 | 层级 | 说明 |
|------|------|------|
| `episodes` | script | 集列表，数量 = `meta.total_episodes` |
| `episode.title` | 集 | 单集标题 |
| `episode.acts` | 集 | 本集内的幕列表（通常 1-2 幕） |
| `episode.hook` | 集 | 可选，本集结尾悬念钩子 |

#### 电视剧模式不存在的字段

- `duration_seconds`（不需要单场精确到秒）
- 竖屏相关标记

---

### 7.3 模式三：微短剧（mini_series）

#### 结构特征

```
script
  └── episodes:                # 集列表
        ├── episode: 1
        │   ├── title: "深夜来电"
        │   ├── hook: "一个神秘电话，打破了十年的平静。"  # 必填
        │   ├── vertical_optimized: true   # 必填，竖屏优化标记
        │   ├── scenes:
        │   │   ├── scene_id: "ep1_scene_001"
        │   │   │   ├── duration_seconds: 45
        │   │   │   └── ...
        │   │   └── scene_id: "ep1_scene_002"
        │   │       ├── duration_seconds: 30
        │   │       └── ...
        │   └── episode_duration_seconds: 90  # 本集总时长，1-3分钟(60-180秒)
        └── episode: 2
            └── ...
```

#### 设计原因

微短剧在电视剧基础上增加了**竖屏适配和时长约束**，因为：

1. **竖屏交付标准**：抖音、快手等短视频平台以竖屏为主，`vertical_optimized` 标记告诉后期制作这是一个竖屏优化的剧本，拍摄时需以 9:16 画幅构图。
2. **精确到秒的时长控制**：短视频平台对时长有严格要求（1-3 分钟），每场戏必须标注 `duration_seconds`，确保整集时长在限制内。
3. **强悬念钩子**：短视频用户注意力极短，每集结尾必须有 `hook`（必填），吸引用户滑到下一集，这是微短剧商业模式的核心。
4. **精简的层级结构**：微短剧无"幕"的概念，因为单集太短（1-3 分钟），不存在幕的划分空间，直接"集→场"两级。
5. **对白精炼约束**：微短剧因时长和竖屏特点，单句对白需更精炼，`dialogue.text` 字段长度不得超过 **15 字符**，确保在快节奏和竖屏字幕展示中信息传达高效。

#### 微短剧模式特有字段

| 字段 | 层级 | 说明 |
|------|------|------|
| `episode.hook` | 集 | **必填**，每集悬念钩子，1-100 字符 |
| `episode.vertical_optimized` | 集 | **必填**，布尔值，竖屏优化标记 |
| `episode.episode_duration_seconds` | 集 | 必填，本集总时长（秒），范围 60-180 |
| `scene.duration_seconds` | 场 | **必填**，单场预估时长（秒），≥1 |

#### 微短剧模式不存在的字段

- `acts`（无幕的概念）

---

### 7.4 三种模式差异对比

| 维度 | 电影 (movie) | 电视剧 (tv_series) | 微短剧 (mini_series) |
|------|:-----------:|:---------------:|:-----------------:|
| **顶层结构** | `acts` | `episodes` → `acts` | `episodes` |
| **层级深度** | 2 级（幕→场） | 3 级（集→幕→场） | 2 级（集→场） |
| **集数** | 无 | 10-60 集 | 系统估算 |
| **单集时长** | 无（整体 90-120 分钟） | 约 45 分钟/集 | 1-3 分钟/集 |
| **hook 字段** | 无 | 可选 | **必填** |
| **duration_seconds** | 无 | 无 | **必填**（场级） |
| **vertical_optimized** | 无 | 无 | **必填**（集级） |
| **episode_duration_seconds** | 无 | 无 | **必填**（集级） |
| **场景编号** | 全局连续编号 | 按集内编号 | 按集内编号 |
| **典型场景数** | 60-120 场 | 30-40 集 × 10-15 场 | N 集 × 5-8 场 |

---

## 8. 完整 YAML 示例

### 8.1 电影剧本示例（简化）

```yaml
schema_version: "1.0"

meta:
  title: "最后一颗子弹"
  source_novel: "绝境求生"
  author: "李四"
  script_type: "movie"
  estimated_duration: 110
  language: "zh-CN"
  version: 1
  created_at: "2026-06-05T10:00:00Z"
  notes: "以三幕结构改编，保留原著核心冲突"

characters:
  - id: "char_001"
    name: "陈默"
    aliases: ["老陈"]
    gender: "male"
    age: 35
    age_display: "35岁"
    personality_tags:
      - "冷静"
      - "果断"
      - "重情义"
    role: "protagonist"
    description: >
      前刑警，因一次任务失误被调离岗位。
      五年来一直暗中调查当年案件的真相。
    first_appearance: "scene_001"

  - id: "char_002"
    name: "林雪"
    gender: "female"
    age: 29
    age_display: "29岁"
    personality_tags:
      - "聪慧"
      - "坚韧"
      - "外冷内热"
    role: "supporting"
    description: >
      记者，正在调查一桩涉及警界的腐败案。
      与陈默不期而遇后成为同盟。
    first_appearance: "scene_003"

  - id: "char_003"
    name: "赵刚"
    aliases: ["赵局长"]
    gender: "male"
    age: 52
    age_display: "52岁"
    personality_tags:
      - "城府深"
      - "手段狠辣"
      - "表面温和"
    role: "antagonist"
    description: >
      现任市公安局副局长，五年前案件的幕后黑手。
    first_appearance: "scene_005"

script:
  acts:
    - act: 1
      title: "建置"
      scenes:
        - scene_id: "scene_001"
          scene_number: 1
          location: "废弃工厂 - 外围"
          setting: "exterior"
          time: "night"
          time_detail: "深夜，暴雨将至"
          characters_present:
            - "char_001"
          content:
            - type: "description"
              text: "乌云压顶，废弃工厂的轮廓在闪电中若隐若现。远处传来低沉的雷声。"
              category: "atmosphere"
            - type: "action"
              text: "陈默蹲在工厂外围的灌木丛后，雨水顺着他的帽檐滴落。他举起望远镜，观察着工厂入口。"
              subject: "char_001"
            - type: "dialogue"
              character: "char_001"
              text: "五年了，终于让我找到你了。"
              delivery: "低声，压抑着情绪"

        - scene_id: "scene_002"
          scene_number: 2
          location: "废弃工厂 - 内部车间"
          setting: "interior"
          time: "night"
          characters_present:
            - "char_001"
          content:
            - type: "action"
              text: "陈默撬开生锈的铁门，手电筒的光束扫过布满蛛网的设备。"
              subject: "char_001"
            - type: "description"
              text: "车间内堆满废弃的机械零件，空气中弥漫着铁锈和机油的味道。"
              category: "environment"
            - type: "action"
              text: "他在角落里发现一个落满灰尘的文件柜，用力拉开抽屉。"
              subject: "char_001"
            - type: "dialogue"
              character: "char_001"
              text: "就是这个。"
              delivery: "颤抖"

    - act: 2
      title: "对抗"
      scenes:
        - scene_id: "scene_003"
          scene_number: 3
          location: "刑警队办公室"
          setting: "interior"
          time: "day"
          time_detail: "上午9点"
          characters_present:
            - "char_001"
            - "char_002"
          content:
            - type: "description"
              text: "阳光透过百叶窗，在办公桌上投下条纹状的阴影。办公室内人来人往，电话铃声此起彼伏。"
              category: "environment"
            - type: "action"
              text: "陈默坐在办公桌前，盯着电脑屏幕上的案件档案。林雪走过来，将一个文件夹放在他桌上。"
              subject: "char_002"
            - type: "dialogue"
              character: "char_002"
              text: "你要的资料，我托人从档案室调出来了。"
            - type: "dialogue"
              character: "char_001"
              text: "谢了。不过这事你别再插手了，太危险。"
            - type: "dialogue"
              character: "char_002"
              text: "晚了。我已经查到赵刚和一个叫'黑蛇'的人有联系。"
              delivery: "压低声音"

    - act: 3
      title: "结局"
      scenes:
        - scene_id: "scene_004"
          scene_number: 4
          location: "码头仓库"
          setting: "interior"
          time: "dusk"
          time_detail: "黄昏，夕阳将海面染成血红色"
          characters_present:
            - "char_001"
            - "char_003"
          content:
            - type: "description"
              text: "夕阳透过仓库的破窗，在地面投下长长的影子。海风呼啸，铁皮屋顶嘎吱作响。"
              category: "atmosphere"
            - type: "action"
              text: "陈默举枪对准赵刚。赵刚却笑了，摊开双手。"
            - type: "dialogue"
              character: "char_003"
              text: "你以为抓了我，一切就结束了？"
              delivery: "冷笑"
            - type: "dialogue"
              character: "char_001"
              text: "不。但这至少是个开始。"
            - type: "action"
              text: "远处传来警笛声，由远及近。蓝色和红色的警灯在仓库墙壁上闪烁。"
            - type: "description"
              text: "陈默放下枪，转身走向仓库门口。夕阳将他的影子拉得很长。"
              category: "transition"
```

### 8.2 电视剧剧本示例（简化：2 集）

```yaml
schema_version: "1.0"

meta:
  title: "暗流"
  source_novel: "城市暗影"
  author: "王五"
  script_type: "tv_series"
  total_episodes: 30
  estimated_duration: 1350
  language: "zh-CN"
  version: 1
  created_at: "2026-06-05T10:00:00Z"
  notes: "30集电视剧改编，每集约45分钟"

characters:
  - id: "char_001"
    name: "周远"
    gender: "male"
    age: 32
    age_display: "32岁"
    personality_tags:
      - "正义"
      - "执着"
      - "不善言辞"
    role: "protagonist"
    description: "市检察院检察官，正在调查一桩涉及政府高层的贪腐案。"
    first_appearance: "ep1_scene_001"
    first_appearance_episode: 1

  - id: "char_002"
    name: "苏晴"
    gender: "female"
    age: 28
    age_display: "28岁"
    personality_tags:
      - "敏锐"
      - "勇敢"
      - "有正义感"
    role: "supporting"
    description: "调查记者，与周远合作揭露真相。"
    first_appearance: "ep1_scene_002"
    first_appearance_episode: 1

  - id: "char_003"
    name: "马国栋"
    gender: "male"
    age: 55
    age_display: "55岁"
    personality_tags:
      - "老谋深算"
      - "伪善"
      - "不择手段"
    role: "antagonist"
    description: "副市长，贪腐案的核心人物。表面清廉，实则掌控着庞大的利益网络。"
    first_appearance: "ep1_scene_004"
    first_appearance_episode: 1

script:
  episodes:
    - episode: 1
      title: "匿名举报"
      hook: "一封匿名信，揭开了城市最黑暗的角落。"
      acts:
        - act: 1
          title: "开场"
          scenes:
            - scene_id: "ep1_scene_001"
              scene_number: 1
              location: "市检察院 - 周远办公室"
              setting: "interior"
              time: "day"
              time_detail: "早晨8点"
              characters_present:
                - "char_001"
              content:
                - type: "action"
                  text: "周远翻开办公桌上的信封，里面只有一张照片和一串数字。"
                  subject: "char_001"
                - type: "description"
                  text: "照片上是一栋豪华别墅，背面用红笔写着'马国栋'三个字。"
                  category: "environment"
                - type: "dialogue"
                  character: "char_001"
                  text: "又来了。这已经是第三封了。"
                  delivery: "自言自语"

            - scene_id: "ep1_scene_002"
              scene_number: 2
              location: "咖啡馆"
              setting: "interior"
              time: "day"
              time_detail: "下午3点"
              characters_present:
                - "char_001"
                - "char_002"
              content:
                - type: "description"
                  text: "咖啡馆角落，周远和苏晴相对而坐。窗外行人匆匆，店内播放着舒缓的爵士乐。"
                  category: "atmosphere"
                - type: "dialogue"
                  character: "char_002"
                  text: "我查过了，那栋别墅的产权登记在一个叫'海盛贸易'的公司名下。"
                - type: "dialogue"
                  character: "char_001"
                  text: "海盛贸易？法人是谁？"
                - type: "dialogue"
                  character: "char_002"
                  text: "马国栋的小舅子。"
                  delivery: "意味深长地看着周远"
                - type: "action"
                  text: "周远沉默片刻，端起咖啡杯，手微微颤抖。"
                  subject: "char_001"

        - act: 2
          title: "发展"
          scenes:
            - scene_id: "ep1_scene_003"
              scene_number: 3
              location: "市政府大楼 - 马国栋办公室"
              setting: "interior"
              time: "day"
              time_detail: "下午5点"
              characters_present:
                - "char_003"
              content:
                - type: "description"
                  text: "豪华的办公室，红木办公桌后是一面巨大的书架。墙上挂满了马国栋与各界名流的合影。"
                  category: "environment"
                - type: "action"
                  text: "马国栋挂断电话，脸色阴沉。他走到窗前，俯视着脚下的城市。"
                  subject: "char_003"
                - type: "dialogue"
                  character: "char_003"
                  text: "周远……一个小检察官，也想翻我的盘？"
                  delivery: "冷冷地"
                - type: "action"
                  text: "他拿起手机，拨出一个没有备注的号码。"
                  subject: "char_003"

    - episode: 2
      title: "暗流涌动"
      hook: "周远不知道，危险正在步步逼近。"
      acts:
        - act: 1
          title: "开场"
          scenes:
            - scene_id: "ep2_scene_001"
              scene_number: 4
              location: "周远公寓 - 地下车库"
              setting: "interior"
              time: "night"
              time_detail: "凌晨1点"
              characters_present:
                - "char_001"
              content:
                - type: "description"
                  text: "地下车库灯光昏暗，周远的脚步声在空旷的空间里回荡。"
                  category: "atmosphere"
                - type: "action"
                  text: "周远走向自己的车，突然注意到车门上贴着一张纸条。"
                  subject: "char_001"
                - type: "action"
                  text: "纸条上写着：'别再查了，否则后果自负。'"
                - type: "dialogue"
                  character: "char_001"
                  text: "看来，他们开始慌了。"
                  delivery: "冷笑，将纸条揉成一团"
```

### 8.3 微短剧剧本示例（简化：1 集）

```yaml
schema_version: "1.0"

meta:
  title: "闪婚契约"
  source_novel: "契约婚姻"
  author: "赵六"
  script_type: "mini_series"
  total_episodes: 20
  estimated_duration: 40
  language: "zh-CN"
  version: 1
  created_at: "2026-06-05T10:00:00Z"

characters:
  - id: "char_001"
    name: "顾言"
    gender: "male"
    age: 28
    age_display: "28岁"
    personality_tags:
      - "霸道"
      - "腹黑"
      - "深情"
    role: "protagonist"
    description: "顾氏集团总裁，为应付家族催婚，与女主签订契约婚姻。"
    first_appearance: "ep1_scene_001"

  - id: "char_002"
    name: "苏念"
    gender: "female"
    age: 25
    age_display: "25岁"
    personality_tags:
      - "独立"
      - "倔强"
      - "善良"
    role: "protagonist"
    description: "普通上班族，因母亲生病急需用钱，答应了契约婚姻。"
    first_appearance: "ep1_scene_001"

script:
  episodes:
    - episode: 1
      title: "相遇"
      hook: "她以为只是签个合同，没想到对方是顾氏集团的总裁。"
      vertical_optimized: true
      episode_duration_seconds: 90
      scenes:
        - scene_id: "ep1_scene_001"
          scene_number: 1
          location: "咖啡厅"
          setting: "interior"
          time: "day"
          time_detail: "下午2点"
          characters_present:
            - "char_001"
            - "char_002"
          duration_seconds: 45
          content:
            - type: "description"
              text: "高档咖啡厅，阳光透过落地窗洒在桌上。"
              category: "environment"
            - type: "action"
              text: "苏念紧张地翻开合同，顾言坐在对面，目光冷淡。"
            - type: "dialogue"
              character: "char_001"
              text: "签了它，你母亲的医药费我来解决。"
            - type: "dialogue"
              character: "char_002"
              text: "我凭什么相信你？"
            - type: "action"
              text: "顾言推过一张支票。"
            - type: "dialogue"
              character: "char_001"
              text: "这是定金。"
              delivery: "不容置疑"

        - scene_id: "ep1_scene_002"
          scene_number: 2
          location: "医院病房"
          setting: "interior"
          time: "night"
          characters_present:
            - "char_002"
          duration_seconds: 45
          content:
            - type: "description"
              text: "病房里只有监护仪的滴答声。"
              category: "atmosphere"
            - type: "action"
              text: "苏念握着母亲的手，眼眶泛红。"
            - type: "dialogue"
              character: "char_002"
              text: "妈，你再坚持一下，我一定会凑够钱的。"
              delivery: "哽咽"
            - type: "action"
              text: "她的手颤抖着摸出手机，看着顾言的名片。"
            - type: "description"
              text: "名片上烫金字体：顾氏集团 顾言"
              category: "camera"
```

---

## 9. Schema 校验规则

### 9.1 校验时机

| 时机 | 触发者 | 说明 |
|------|--------|------|
| 章节转换后 | Celery Worker | 每章 LLM 输出后校验片段 YAML |
| 合并完成后 | Celery Worker | 完整剧本 YAML 校验 |
| 用户编辑保存时 | FastAPI（前端+后端） | 双重校验，前端即时反馈，后端最终把关 |

### 9.2 校验规则清单

| 编号 | 规则 | 严重级别 |
|------|------|---------|
| V-01 | `schema_version` 必须为 `"1.0"` | ERROR |
| V-02 | `meta.script_type` 必须为 `movie` / `tv_series` / `mini_series` | ERROR |
| V-03 | `meta.total_episodes` 在 `tv_series` / `mini_series` 时必填且 ≥1 | ERROR |
| V-04 | `characters[].id` 全局唯一，格式 `char_\d{3}` | ERROR |
| V-05 | `characters[].role` 枚举值合法 | ERROR |
| V-06 | `dialogue.character` 必须存在于 `characters[].id` | ERROR |
| V-07 | `scene.scene_id` 全局唯一 | ERROR |
| V-08 | `scene.characters_present` 所有 ID 必须存在于 `characters[].id` | ERROR |
| V-09 | `scene.setting` 枚举值合法 | ERROR |
| V-10 | `scene.time` 枚举值合法（允许自定义） | WARNING |
| V-11 | `scene.content` 非空，至少 1 个节点 | ERROR |
| V-12 | 微短剧：`episode.hook` 必填且非空 | ERROR |
| V-13 | 微短剧：`episode.vertical_optimized` 必填且为 `true` | ERROR |
| V-14 | 微短剧：`scene.duration_seconds` 必填且 ≥1 | ERROR |
| V-15 | 微短剧：`episode.episode_duration_seconds` 必填且在 60-180 范围内 | ERROR |
| V-16 | 电影：顶层结构为 `script.acts`，不允许 `episodes` | ERROR |
| V-17 | 电视剧/微短剧：顶层结构为 `script.episodes`，不允许顶层的 `acts` | ERROR |
| V-18 | `characters[].first_appearance` 必须引用存在的 `scene_id` | WARNING |
| V-19 | 微短剧：`dialogue.text` 字段长度不得超过 15 字符 | WARNING |

### 9.3 校验失败处理流程

```
┌──────────────┐    校验通过     ┌──────────────┐
│  YAML 输出    │ ──────────────▶ │  存入数据库   │
│  (LLM生成)    │                │  标记 is_valid │
└──────┬───────┘                 └──────────────┘
       │
       │ 校验失败
       ▼
┌──────────────┐
│ 自动重试      │  retry_count < 3?
│ (最多3次)     │
│ 将错误信息    │
│ 注入 Prompt   │
└──────┬───────┘
       │
       │ 3次重试后仍失败
       ▼
┌──────────────┐
│ 标记为        │
│ needs_manual  │
│ _review       │
│ 通知用户      │
└──────────────┘
```

---

## 附录 A：Python Schema 校验示例

```python
import yaml
import jsonschema
from jsonschema import validate, ValidationError

# 电影模式的 JSON Schema（用于校验）
MOVIE_SCHEMA = {
    "type": "object",
    "required": ["schema_version", "meta", "characters", "script"],
    "properties": {
        "schema_version": {"const": "1.0"},
        "meta": {
            "type": "object",
            "required": ["title", "source_novel", "author", "script_type", "created_at"],
            "properties": {
                "script_type": {"enum": ["movie", "tv_series", "mini_series"]},
                "total_episodes": {"type": "integer", "minimum": 1},
                "version": {"type": "integer", "minimum": 1},
            }
        },
        "characters": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "name", "gender", "personality_tags", "role", "description", "first_appearance"],
                "properties": {
                    "id": {"type": "string", "pattern": "^char_\\d{3}$"},
                    "gender": {"enum": ["male", "female", "other"]},
                    "role": {"enum": ["protagonist", "antagonist", "supporting", "cameo"]},
                    "personality_tags": {"type": "array", "minItems": 1},
                }
            }
        },
        "script": {
            "type": "object",
            "required": ["acts"],
            "properties": {
                "acts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["act", "title", "scenes"],
                        "properties": {
                            "act": {"type": "integer", "minimum": 1},
                            "title": {"type": "string"},
                            "scenes": {"type": "array", "items": {"$ref": "#/definitions/scene"}},
                        }
                    }
                }
            }
        }
    },
    "definitions": {
        "scene": {
            "type": "object",
            "required": ["scene_id", "location", "setting", "time", "characters_present", "content"],
            "properties": {
                "scene_id": {"type": "string"},
                "setting": {"enum": ["interior", "exterior", "interior_exterior"]},
                "time": {"type": "string"},
                "characters_present": {"type": "array", "minItems": 1},
                "content": {"type": "array", "minItems": 1},
            }
        }
    }
}

def validate_script(yaml_text: str, script_type: str) -> dict:
    """校验剧本 YAML 是否符合 Schema"""
    data = yaml.safe_load(yaml_text)

    if script_type == "movie":
        schema = MOVIE_SCHEMA
    elif script_type == "tv_series":
        schema = TV_SERIES_SCHEMA
    elif script_type == "mini_series":
        schema = MINI_SERIES_SCHEMA
    else:
        raise ValueError(f"Unknown script_type: {script_type}")

    # 基础 Schema 校验
    validate(instance=data, schema=schema)

    # 交叉引用校验：dialogue.character 必须存在于 characters
    character_ids = {c["id"] for c in data["characters"]}
    scene_ids = set()
    errors = []

    def collect_scene_ids(scenes):
        for s in scenes:
            scene_ids.add(s["scene_id"])
            for node in s.get("content", []):
                if node["type"] == "dialogue":
                    if node["character"] not in character_ids:
                        errors.append(
                            f"场景 {s['scene_id']}: 角色 '{node['character']}' 未在角色列表中定义"
                        )

    if script_type == "movie":
        for act in data["script"]["acts"]:
            collect_scene_ids(act["scenes"])
    else:
        for ep in data["script"]["episodes"]:
            for act in ep.get("acts", []):
                collect_scene_ids(act["scenes"])

    # 校验 first_appearance 引用
    for c in data["characters"]:
        if c["first_appearance"] not in scene_ids:
            errors.append(f"角色 '{c['id']}': first_appearance '{c['first_appearance']}' 不存在")

    if errors:
        raise ValidationError("; ".join(errors))

    return data
```

## 附录 B：版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-06-05 | 初始版本，定义三种模式Schema及校验规则 |