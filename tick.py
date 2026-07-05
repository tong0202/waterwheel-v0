#!/usr/bin/env python3
"""第一块叶片 / waterwheel-v0

一次 tick = 读状态 -> 计数+1 -> 用父哈希链写回。
不做任何"网络自算"的宣称。它只证明一件事:
平台的免费定时触发,能在无人干预下让一个状态自己往前走一格,
且每一格都用哈希链到上一格,事后可验、不可伪造中间格。
"""
import json
import os
import sys
import hashlib
from datetime import datetime, timezone

STATE_PATH = os.path.join(os.path.dirname(__file__), "state", "counter.json")

GENESIS = "0" * 64


def sha256_of(obj: dict) -> str:
    payload = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_state():
    if not os.path.exists(STATE_PATH):
        return None
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    trigger = os.environ.get("WHEEL_TRIGGER", "unknown")
    run_id = os.environ.get("WHEEL_RUN_ID", "local")
    now = datetime.now(timezone.utc).isoformat()

    prev = load_state()
    if prev is None:
        parent_hash = GENESIS
        count = 0
        history_len = 0
    else:
        # 父哈希护栏:重算上一格的哈希,确认没被人动过
        recorded = prev.get("self_hash")
        recomputed = sha256_of({k: v for k, v in prev.items() if k != "self_hash"})
        if recorded != recomputed:
            print(f"PARENT HASH MISMATCH: recorded={recorded} recomputed={recomputed}", file=sys.stderr)
            sys.exit(2)
        parent_hash = recorded
        count = prev.get("count", 0)
        history_len = prev.get("history_len", 0)

    new_body = {
        "count": count + 1,
        "parent_hash": parent_hash,
        "tick_trigger": trigger,
        "tick_run_id": run_id,
        "tick_at": now,
        "history_len": history_len + 1,
    }
    new_body["self_hash"] = sha256_of(new_body)

    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(new_body, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"tick ok: count {count} -> {count+1}, trigger={trigger}, self_hash={new_body['self_hash'][:16]}")


if __name__ == "__main__":
    main()
