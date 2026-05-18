"""guardrails.py — Restricted Web3 Helper 守卫规则.

每个 deny 都附一句"为什么",方便用户理解约束源头,不只是被拒绝。
"""

from __future__ import annotations

DENY_PREFIXES = (
    "send ", "broadcast ", "deploy ",
    "approve ", "permit ",
    "transfer ", "swap ",
)

DENY_KEYWORDS = (
    "--private-key", "--mnemonic", "--keystore",
    "PRIVATE_KEY=", "MNEMONIC=",
)

MAINNET_CHAIN_IDS = {1, 10, 137, 42161, 8453, 56}  # ETH, Optimism, Polygon, Arbitrum, Base, BSC


def allow(cmd: str) -> bool:
    """Return True if the command is purely read-only or a dry-run."""
    low = cmd.lower().strip()
    if any(low.startswith(p) for p in DENY_PREFIXES):
        return False
    if any(k in cmd for k in DENY_KEYWORDS):
        return False
    if "--mainnet" in low and "send" in low:
        return False
    return True


def reason(cmd: str) -> str:
    low = cmd.lower().strip()
    if any(low.startswith(p) for p in DENY_PREFIXES):
        return (
            f"❌ 拒绝执行 `{cmd[:60]}...`\n"
            "原因:这是写链动作。本 helper 只生成 calldata + 解释,广播必须你自己在另一个终端做。\n"
            "下一步:可以用 `prep <相同命令>` 让我帮你生成 cast 命令模板,你拷出去用自己的钱包广播。"
        )
    if any(k in cmd for k in DENY_KEYWORDS):
        return (
            "❌ 拒绝执行:命令里含私钥/助记词字段。\n"
            "原因:私钥永远不进 Agent 进程内存。Agent 看见私钥就是泄漏面扩大。\n"
            "下一步:把私钥从命令里移除,签名步骤在你自己的钱包(MetaMask/Rabby/Frame/Foundry CLI)里完成。"
        )
    if "--mainnet" in low and "send" in low:
        return (
            "❌ 拒绝执行:主网写动作禁用。\n"
            "原因:Week 1 阶段所有写动作只在测试网执行,主网门槛由你显式打开。"
        )
    return "❌ 拒绝执行(命中默认拒绝规则)"


# Self-test
if __name__ == "__main__":
    samples = [
        ("balance 0xABC", True),
        ("send 0xABC 1 ether", False),
        ("call USDC balanceOf 0xABC", True),
        ("deploy MyContract", False),
        ("storage 0xABC 0", True),
        ("cast send --private-key 0xdead", False),
        ("approve USDC 0xBAD MAX --mainnet", False),
        ("prep swap 100 USDC ETH", True),
    ]
    for cmd, expected in samples:
        got = allow(cmd)
        flag = "✅" if got == expected else "❌"
        print(f"{flag} allow({cmd!r}) = {got}  (expected {expected})")
        if not got:
            print("   reason:", reason(cmd).split("\n")[0])
