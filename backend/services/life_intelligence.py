from __future__ import annotations


def build_insights(emotions: list[str], habits: list[str], issues: list[str]) -> dict[str, list[str]]:
    patterns = []
    trends = []
    flags = []

    if "anxiety" in emotions[-5:]:
        patterns.append("Recent conversations trend toward anxiety-based stress.")
    if "sleeping late" in habits:
        patterns.append("Sleep timing may be amplifying emotional load.")
    if "overthinking" in issues:
        trends.append("You often move from uncertainty into rumination quickly.")
    if "motivation dips" in issues:
        trends.append("Energy appears inconsistent, so smaller goals may work better.")
    if emotions[-3:].count("sadness") >= 2:
        flags.append("Sustained low mood pattern detected; keep monitoring closely.")

    return {"patterns": patterns[:3], "trends": trends[:3], "flags": flags[:3]}
