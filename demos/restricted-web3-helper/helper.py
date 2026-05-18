"""helper.py — Restricted Web3 Helper · minimal entry.

跑法:
    PYTHONPATH=. python3 helper.py

只是个 reference implementation,真正用要接 LLM 解释和 cast 子进程。这里 stub 一下,
关键是 guardrails 的强制路径。
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import guardrails

LOG_FILE = Path(__file__).parent / "session.log.jsonl"


def log_decision(cmd: str, status: str, detail: str = "") -> None:
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "cmd": cmd,
        "status": status,
        "detail": detail[:500],
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def dispatch_read(cmd: str) -> str:
    """Stub: route allowed read commands. Real impl would subprocess `cast`."""
    head = cmd.split()[0].lower() if cmd.split() else ""
    if head in ("balance", "call", "storage", "receipt", "block", "code"):
        return f"[stub] would run: cast {cmd}  (replace with subprocess in real use)"
    if head == "prep":
        return (
            "[stub] preparing calldata template — NOT broadcasting.\n"
            "  cast send <TARGET> '<FUNC>' <ARGS> --rpc-url $SEPOLIA_RPC_URL\n"
            "  ⚠️  你需要在另一个终端用自己的钱包替换 --private-key,本 helper 永远不持有私钥。"
        )
    if head == "help":
        return HELP_TEXT
    return f"[stub] unknown read command: {cmd}"


HELP_TEXT = """\
Restricted Web3 Helper · 命令清单

只读 (auto-execute):
  balance <ADDR>             查地址余额
  call <ADDR> <SIG> [ARGS]   只读调用合约方法
  storage <ADDR> <SLOT>      读 storage 槽位
  receipt <TX_HASH>          查交易回执
  block [N]                  查区块
  code <ADDR>                查合约字节码大小

需人工确认 (prep then user signs):
  prep <action> ...          生成 calldata 模板,你自己广播

拒绝 (自动 deny):
  send / broadcast / deploy / approve / permit / transfer / swap
  任何含 --private-key / --mnemonic / --keystore 的命令
  任何 --mainnet 的写动作

其他:
  help                       本菜单
  exit / quit                退出
"""


def main() -> int:
    print("Restricted Web3 Helper · 输入 help 看命令清单")
    while True:
        try:
            cmd = input("\n[helper] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye.")
            return 0
        if not cmd:
            continue
        if cmd in ("exit", "quit"):
            return 0

        if not guardrails.allow(cmd):
            msg = guardrails.reason(cmd)
            print(msg)
            log_decision(cmd, "REJECTED", msg)
            continue

        result = dispatch_read(cmd)
        print(result)
        log_decision(cmd, "OK", result)


if __name__ == "__main__":
    sys.exit(main())
