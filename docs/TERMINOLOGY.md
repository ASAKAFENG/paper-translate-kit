# 翻译约定与术语表

## 一、术语括注规则

1. **首次出现括注**：专业名词第一次出现在正文时写成 `中文（English）`：
   - `类别级6D物体位姿估计（category-level 6D object pose estimation）`
   - `关键点（keypoint）`
   - `参考物体位姿嵌入（Reference Object Pose Embedding, ROPE）`
2. **后文纯中文**：同一术语第二次出现起不再带英文，避免冗余。
3. **保留英文的情形**：
   - 方法/模型/系统名：AG-Pose、FoundationPose、DINOv2、Mamba、RANSAC、ICP、PnP；
   - 数据集与基准名：REAL275、CAMERA25、T-LESS、BOP、HouseCat6D；
   - 已有通行中文译名但上下文需要精确时，可写 `归一化物体坐标空间（NOCS）`；
   - 超参数符号、变量名、代码标识符（`$N_{kpt}$`、`d_model`、`post_layernorm`）；
   - 伪代码关键字（`for`、`return`）与算法行内注释可译可不译，全文统一即可。
4. **缩写先行**：形如"平均召回率（Average Recall, AR）"——先中文全称，括注英文全称与缩写。
5. **一致优先**：同一术语在全文（含图题、表头、算法注释）必须用同一译法；
   动手前先扫一遍全文，把高频术语列成对照表再开始翻译。

## 二、翻译范围界线

| 类别 | 处理 |
|---|---|
| 正文散文、摘要、结论 | 翻译 |
| `\section/\subsection/\paragraph` 标题 | 翻译（最高频漏译点） |
| 图题 `\caption`、表题、表头 | 翻译（数字列不动） |
| 表内行标签（Ours→本文、None→无） | 翻译；方法名与设置缩写（H/H/L、FPS、ICP）保留 |
| 算法伪代码注释 | 翻译（可选，全文统一） |
| 公式、上下标文字（`\text{if}` 等） | `\text{}` 内的英文条件词可译（若/其他），其他不动 |
| `\cite` / `\label` / `\ref` | **绝对不动**，键名与顺序逐一对齐 |
| 参考文献列表 | 不翻译（保持英文原文） |
| 注释行与 `comment` 环境 | 原样保留（包括英文草稿） |
| 作者姓名 | 拼音保留；单位、通讯作者译中文 |
| 图内烘焙文字 | 无法修改；在说明.txt 注明 |

## 三、常用句式对照

| 英文 | 中文 |
|---|---|
| We propose ... | 我们提出…… |
| To the best of our knowledge, ... | 据我们所知，…… |
| achieve state-of-the-art performance | 取得最先进（state-of-the-art）性能 |
| outperforms X by a large margin | 大幅超越 X |
| ablation study | 消融实验 |
| ground truth | 真值（ground truth） |
| robust to ... | 对……鲁棒 |
| generalizes to unseen ... | 泛化到未见…… |

## 四、6D 物体位姿领域术语表（示例，可按领域扩充）

| English | 中文 |
|---|---|
| 6D object pose estimation | 6D物体位姿估计 |
| 6DoF / 9DoF | 6自由度 / 9自由度 |
| instance-level / category-level | 实例级 / 类别级 |
| category-agnostic / novel (unseen) objects | 类别无关 / 新物体（未见物体） |
| model-based / model-free | 基于模型 / 免模型 |
| CAD model | CAD模型 |
| correspondence | 对应（关系） |
| dense / semi-dense / sparse correspondence | 稠密对应 / 半稠密对应 / 稀疏对应 |
| keypoint / keypoint-level correspondence | 关键点 / 关键点级对应 |
| Normalized Object Coordinate Space (NOCS) | 归一化物体坐标空间 |
| shape prior / canonical shape | 形状先验 / 规范形状 |
| texture rendering / textureless | 纹理渲染 / 无纹理 |
| segmentation mask / instance mask | 分割掩码 / 实例掩码 |
| bounding box / oriented bounding box | 边界框 / 朝向边界框 |
| anchor / query / reference | 锚点 / 查询 / 参考 |
| render-and-compare | 渲染-比较 |
| image-to-3D | 图像到3D |
| metric scale | 度量尺度 |
| registration | 配准 |
| pose refinement / coarse estimation | 位姿精炼 / 粗略估计 |
| pose hypothesis / inlier / outlier | 位姿假设 / 内点 / 离群点 |
| Chamfer distance | 倒角距离 |
| Average Recall (AR) / ADD / ADD-S / AUC | 保留英文缩写 |
| visible surface discrepancy (VSD) | 可见表面差异 |
| symmetry-aware | 对称感知 |
| occlusion / self-occlusion | 遮挡 / 自遮挡 |
| zero-shot / few-shot / training-free | 零样本 / 少样本 / 免训练 |
| feature misalignment | 特征错位 |
| negative transfer / gradient conflict | 负迁移 / 梯度冲突 |
| learnable query / embedding | 可学习查询 / 嵌入 |
| cross-attention / self-attention | 交叉注意力 / 自注意力 |
| latent diffusion model | 潜扩散模型 |
| farthest point sampling (FPS) | 最远点采样 |
| back-projection / 3D lifting | 反投影 / 3D提升 |
| heatmap | 热力图 |
| saliency map | 显著性图 |
| concept vector | 概念向量 |
| state space model (SSM) | 状态空间模型 |
| long-range dependencies | 长程依赖 |
| finetune / freeze / distillation | 微调 / 冻结 / 蒸馏 |
