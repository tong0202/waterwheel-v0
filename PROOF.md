# 水车 v1：自主建造贪吃蛇 —— 证据与边界

生成时间：2026-07-05
repo：https://github.com/tong0202/waterwheel-v0
模式：纯自主，无人干预，慢慢建

## 从 +1 到真任务

第一块叶片（v0）证明了免费定时器能让状态自己走一格（count+1）。
v1 把"+1"换成一件真活：**自主建一个能玩的贪吃蛇游戏**。

游戏被拆成 9 块（build_plan.py）：
html头 → css → body → reset → food → tick → draw → input → boot。
水车每 tick 拼一块，9 tick 后 game/snake.html 成为完整可玩游戏。

## 机制

每个 tick：
1. 读状态 state/build.json，校验状态哈希未被篡改（否则退出2）
2. 校验已建的 game/snake.html 哈希未被篡改（否则退出3）
3. 取配方第 step 块，拼到游戏文件末尾
4. 用父哈希链写新状态，commit + push

## 已本地验证（部署前）

- 9 tick 全跑通，snake.html 3550 字节，结构自检全过（doctype/canvas/tick函数/script配对）
- 反证1：偷改状态 count → 下一 tick 退出2（状态哈希护栏）
- 反证2：偷改游戏文件 → 下一 tick 退出3（游戏文件护栏）
- 部署前已清空状态与游戏文件，远端从空冷启动

## 验收方式（无人干预，自己看它长出来）

游戏一块块出现在：
https://github.com/tong0202/waterwheel-v0/blob/master/game/snake.html

看它是不是自己建的（关键）：
```
gh run list --repo tong0202/waterwheel-v0 --json event,createdAt,conclusion
```
只要 game/snake.html 的每次增长都对应 event=schedule 的 run，
就是"免费定时器无人干预、自主把一个真任务推进到完成"的铁证。

建完后本地玩：把 snake.html 存下来双击打开即可。

## 未证明（不得宣称）

- 真正在跑的是 GitHub 的服务器（一个端点）。关掉它，水车停。
- 建造计划（9块配方）是人写的。水车负责"自主推进"，不负责"自主创作"。
- 不证明网络自算、无端点计算、自主创作、生命、意识。
- 本轮证明的边界仅限：**免费定时器能让一个人类定义的真任务，
  在无人干预下一步步自主推进到完成，全程哈希链可验、可复跑、断了能接。**
