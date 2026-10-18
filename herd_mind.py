#!/usr/bin/env python3
"""herd-mind: the harness remembers.

Each animal knows its job. The herd-mind knows what worked. Every run
leaves a trace: what was tried, what it cost, what it changed. The next
run reads the traces before it moves, so the fleet gets smarter without
any single creature getting bigger. Memory lives in the trail, not in
one head.

Demo: python3 herd_mind.py demo
"""
import json, time, hashlib

class Trail:
    """Append-only memory. Nothing is deleted; stale lessons dim but stay."""
    def __init__(self):
        self.traces: list[dict] = []

    def leave(self, animal: str, action: str, cost_s: float,
              changed: str, worked: bool) -> dict:
        t = {"animal": animal, "action": action, "cost_s": round(cost_s, 2),
             "changed": changed, "worked": worked, "at": time.time()}
        t["id"] = hashlib.sha1(json.dumps(t, sort_keys=True).encode()).hexdigest()[:10]
        self.traces.append(t)
        return t

    def recall(self, animal: str | None = None, action_prefix: str = "") -> list[dict]:
        """Read the trail before you move: what this animal (or any) learned."""
        out = []
        for t in self.traces:
            if animal and t["animal"] != animal:
                continue
            if action_prefix and not t["action"].startswith(action_prefix):
                continue
            out.append(t)
        return out

    def lessons(self) -> dict:
        """The herd's standing knowledge: success rate per animal/action pair."""
        agg: dict[str, list[int]] = {}
        for t in self.traces:
            agg.setdefault(f"{t['animal']}:{t['action']}", []).append(int(t["worked"]))
        return {k: {"runs": len(v), "worked": sum(v),
                    "rate": round(sum(v) / len(v), 3)} for k, v in agg.items()}

def demo():
    tr = Trail()
    tr.leave("receipt-dog", "ckpt.init", 4.2, "ledger created", True)
    tr.leave("receipt-dog", "ckpt.next", 2.1, "card filed", True)
    tr.leave("receipt-dog", "ckpt.next", 3.9, "reroute on bad receipt", False)
    tr.leave("collie", "dispatch.shed", 1.4, "task claimed once", True)
    print("recall dog ckpt:", json.dumps(tr.recall("receipt-dog", "ckpt"), default=str)[:120], "...")
    print("lessons:", json.dumps(tr.lessons(), indent=1))

if __name__ == "__main__":
    demo()
