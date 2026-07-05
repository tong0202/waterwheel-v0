#!/usr/bin/env python3
"""水车 v1：把 +1 换成"自主建一个贪吃蛇游戏"。

每个 tick 建游戏的下一块（见 build_plan.py 的 9 步配方）。
一块块拼出完整可玩的游戏。每步用父哈希链，可复验、可复跑、断了能接着建。

边界：真正在跑的是 GitHub 的服务器（一个端点）。建造计划是人写的。
本脚本只证明：免费定时器能让一个真任务在无人干预下一步步自主推进。
它不证明网络自算，不证明自主创作，不证明生命。
"""
import json
import os
import sys
import hashlib
from datetime import datetime, timezone

from build_plan import BUILD_PLAN

ROOT = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(ROOT, "state", "build.json")
GAME_PATH = os.path.join(ROOT, "game", "snake.html")
GENESIS = "0" * 64


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_of(obj: dict) -> str:
    payload = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_state():
    if not os.path.exists(STATE_PATH):
        return None
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def read_game():
    if not os.path.exists(GAME_PATH):
        return ""
    with open(GAME_PATH, "r", encoding="utf-8") as f:
        return f.read()


def main():
    trigger = os.environ.get("WHEEL_TRIGGER", "unknown")
    run_id = os.environ.get("WHEEL_RUN_ID", "local")
    now = datetime.now(timezone.utc).isoformat()

    prev = load_state()
    game = read_game()

    if prev is None:
        step = 0
        parent_hash = GENESIS
        # 冷启动：游戏文件应为空
        if game != "":
            print("COLD START but game file not empty; refusing", file=sys.stderr)
            sys.exit(4)
    else:
        # 1) 校验上一格状态哈希没被人动过
        recorded = prev.get("self_hash")
        recomputed = sha256_of({k: v for k, v in prev.items() if k != "self_hash"})
        if recorded != recomputed:
            print(f"STATE HASH MISMATCH: {recorded} vs {recomputed}", file=sys.stderr)
            sys.exit(2)
        # 2) 校验已建的游戏文件没被人动过
        if sha256_text(game) != prev.get("game_sha256"):
            print("GAME FILE TAMPERED: hash mismatch vs recorded", file=sys.stderr)
            sys.exit(3)
        parent_hash = recorded
        step = prev.get("step", 0)

    total = len(BUILD_PLAN)

    # 已建完：空转，不写状态、不产生提交（避免刷屏）
    if step >= total:
        print(f"build complete ({total}/{total}); wheel idling, no commit")
        return

    stage_name, chunk = BUILD_PLAN[step]
    game += chunk
    os.makedirs(os.path.dirname(GAME_PATH), exist_ok=True)
    with open(GAME_PATH, "w", encoding="utf-8") as f:
        f.write(game)

    new_body = {
        "step": step + 1,
        "total_steps": total,
        "last_stage": stage_name,
        "done": (step + 1) >= total,
        "game_sha256": sha256_text(game),
        "parent_hash": parent_hash,
        "tick_trigger": trigger,
        "tick_run_id": run_id,
        "tick_at": now,
    }
    new_body["self_hash"] = sha256_of(new_body)

    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(new_body, f, ensure_ascii=False, indent=2)
        f.write("\n")

    status = "DONE" if new_body["done"] else "building"
    print(f"tick ok [{status}]: step {step} -> {step+1}/{total} "
          f"({stage_name}), trigger={trigger}, self_hash={new_body['self_hash'][:16]}")


if __name__ == "__main__":
    main()
