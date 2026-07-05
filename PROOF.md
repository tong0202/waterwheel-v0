# 第一块叶片 / waterwheel-v0 —— 证据与边界

生成时间：2026-07-05
repo：https://github.com/tong0202/waterwheel-v0

## 要证明的那一件事

网络里有没有一条"不用我推、自己会流"的河？如果有，水车架上去就能自转。

第一块叶片只回答这一个问题，不多回答一个字。

## 已证明（本轮）

1. **全链路通**：GitHub Actions 冷启动，读状态 → 计数+1 → 用父哈希链写回 repo。
   - 首格证据：count=1, parent_hash=创世全0, self_hash=6483c571..., run=28734313875
2. **哈希链护栏有效**（本地反证）：偷改 count 不改 self_hash，下一 tick 立即 PARENT HASH MISMATCH 退出码2。中间格不可伪造。
3. **自流现象真实存在**（旁证，来自姊妹 repo qimingxing-m3-executor-test）：
   - 9.5 天内 228 次 `event=schedule` 自触发，成功率 100%，人工仅干预 9 次。
   - 这是"免费定时器无人干预自触发"的真实、可查、大样本证据。

## 已量化的真实缺陷（这是重点，不是失败）

姊妹 repo 实测：cron 写 `*/5`（应每小时12次），**实际平均每小时仅 1 次**，
间隔中位数 50 分钟，最长断 4.4 小时。

结论：**单条免费河，真的在流，但又慢又不匀。** 这从实测层面证明：
单条河撑不起稳定时钟 → 需要"齿轮群组"（多条河错开相位拼快节拍）。
这正是下一步的工程依据，不是靠推理得来的。

## 未证明（不得宣称）

- 未证明网络介质自己在算。真正在算的是 GitHub 的服务器（一个端点）。
- 未证明无端点计算。关掉 GitHub Actions，水车就停。
- 未证明自主/生命/意识。这只是一个会自己+1的计数器。
- 本轮"自转"的 schedule 证据在姊妹 repo，本 repo 的 schedule 自触发格
  正在累积中（见下）。

## 待收（本 repo 自转格）

本 repo 首格是 workflow_dispatch（手动点火，证明链路）。
接下来不再人工干预，观察 state/counter.json 中出现
`tick_trigger: schedule` 的格，即为本 repo 独立的冷启动自转证据。
验收命令：
```
gh api repos/tong0202/waterwheel-v0/contents/state/counter.json -q .content | base64 -d
gh run list --repo tong0202/waterwheel-v0 --json event,createdAt,conclusion
```
