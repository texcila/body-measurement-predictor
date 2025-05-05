# scripts/excel_to_rules.py

import pandas as pd
import numpy as np
import re
import traceback
import logging
from collections import defaultdict
from networkx import DiGraph, topological_sort, NetworkXUnfeasible
from networkx.algorithms.cycles import find_cycle

# Setup logging
logging.basicConfig(
    filename='rule_conversion.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def clean_name(text):
    """Convert measurement names to snake_case"""
    cleaned = re.sub(r'[^a-z0-9_]', '_', str(text).strip().lower())
    return re.sub(r'_+', '_', cleaned)

def parse_formula(formula: str, priority: int):
    """Parses a formula and returns structured rule with dependencies"""
    formula = formula.replace(" ", "")
    if '=' not in formula:
        raise ValueError("Missing '=' in formula")
    
    left_side, right_side = formula.split('=')
    target = clean_name(left_side.strip())
    
    if sum(op in right_side for op in ['+', '-', '*', '/']) > 1:
        raise ValueError("Complex formulas require step-by-step implementation")
    
    for op in ['+', '-', '*', '/']:
        if op in right_side:
            parts = right_side.split(op)
            if len(parts) != 2:
                raise ValueError("Invalid operator structure")
            
            # Determine base and value
            base = clean_name(parts[0]) if not parts[0].replace('.', '', 1).isdigit() else clean_name(parts[1])
            value = float(parts[1]) if parts[1].replace('.', '', 1).isdigit() else float(parts[0])

            return {
                'target': target,
                'type': {
                    '*': 'proportion',
                    '/': 'ratio',
                    '+': 'offset',
                    '-': 'offset'
                }[op],
                'base': base,
                'value': value,
                'operator': op,
                'requires': [base],
                'priority': priority
            }
    raise ValueError("Unsupported or missing operator in formula")

def build_dependency_graph(rules):
    """Create a dependency graph for all rules"""
    graph = DiGraph()
    for target, rule_list in rules.items():
        for rule in rule_list:
            graph.add_node(target)
            for dep in rule['requires']:
                graph.add_edge(dep, target)
    return graph

def resolve_cycles(graph, rule_dict):
    """Try to resolve cycles by removing lowest-priority rules"""
    removed = []
    while True:
        try:
            list(topological_sort(graph))
            break  # Success! No more cycles
        except NetworkXUnfeasible:
            cycle = find_cycle(graph)
            involved_targets = {dst for _, dst in cycle}

            # Collect all rules involved in the cycle and pick the one with lowest priority
            lowest_priority = float("inf")
            weakest_target = None
            for tgt in involved_targets:
                for rule in rule_dict[tgt]:
                    if rule["priority"] < lowest_priority:
                        lowest_priority = rule["priority"]
                        weakest_target = tgt

            if weakest_target:
                removed.append((weakest_target, rule_dict[weakest_target]))
                del rule_dict[weakest_target]
                graph = build_dependency_graph(rule_dict)
            else:
                raise RuntimeError("Cycle could not be resolved")

    return rule_dict, removed

def build_custom_rules(df):
    rules = defaultdict(list)
    skipped = []

    for _, row in df.iterrows():
        try:
            formula = row["Typical Formula"]
            priority = int(row.get("Priority", 0))
            tolerance = float(row["Tolerance"]) if pd.notna(row["Tolerance"]) else 0.0
            notes = row.get("Notes", "").strip()

            parsed = parse_formula(formula, priority)

            rule_entry = {
                "type": parsed["type"],
                "base": parsed["base"],
                "tolerance": tolerance,
                "notes": notes,
                "requires": parsed["requires"],
                "priority": priority
            }

            if parsed["type"] in ("proportion", "ratio"):
                rule_entry["multiplier"] = parsed["value"] if parsed["operator"] == '*' else 1 / parsed["value"]
            elif parsed["type"] == "offset":
                rule_entry["offset"] = parsed["value"] if parsed["operator"] == '+' else -parsed["value"]

            rules[parsed["target"]].append(rule_entry)
            logging.info(f"✔️ Parsed rule: {formula} → {rule_entry}")

        except Exception as e:
            msg = f"⛔ Skipped formula '{row.get('Typical Formula', 'N/A')}': {e}"
            logging.warning(msg)
            skipped.append(msg)

    return rules, skipped

def generate_fashion_rules():
    try:
        print("📂 Loading Excel files...")
        df_rules = pd.read_excel("data/measurement_relationships.xlsx")
        df_desc = pd.read_excel("data/measurement_descriptions.xlsx")

        print("🔍 Building rules from formulas...")
        rule_dict, skipped = build_custom_rules(df_rules)

        print("🔁 Checking dependencies...")
        graph = build_dependency_graph(rule_dict)

        try:
            processing_order = list(topological_sort(graph))
        except NetworkXUnfeasible:
            print("⚠️ Circular dependencies found. Attempting auto-fix based on priority...")
            rule_dict, removed = resolve_cycles(graph, rule_dict)
            print(f"✅ Removed {len(removed)} low-priority rule(s) to fix cycles.")
            logging.warning(f"Removed rules to resolve cycles: {[r[0] for r in removed]}")
            graph = build_dependency_graph(rule_dict)
            processing_order = list(topological_sort(graph))

        print("📝 Mapping descriptions...")
        desc_map = df_desc.set_index("Measurement Name")["Description"].to_dict()

        print("💾 Writing fashion_rules.py...")
        with open("fashion_rules.py", "w", encoding="utf-8") as f:
            f.write("# AUTOGENERATED FILE — DO NOT MODIFY MANUALLY\n\n")
            
            f.write("MEASUREMENT_DESCRIPTIONS = {\n")
            for name, desc in desc_map.items():
                f.write(f'    "{clean_name(name)}": """{desc.strip()}""",\n')
            f.write("}\n\n")

            f.write("CUSTOM_RULES = {\n")
            for target in processing_order:
                if target not in rule_dict:
                    continue
                f.write(f'    "{target}": [\n')
                for rule in rule_dict[target]:
                    f.write("        {\n")
                    f.write(f'            "type": "{rule["type"]}",\n')
                    f.write(f'            "base": "{rule["base"]}",\n')
                    if "multiplier" in rule:
                        f.write(f'            "multiplier": {rule["multiplier"]},\n')
                    if "offset" in rule:
                        f.write(f'            "offset": {rule["offset"]},\n')
                    f.write(f'            "tolerance": {rule["tolerance"]},\n')
                    f.write(f'            "notes": """{rule["notes"]}"""\n')
                    f.write("        },\n")
                f.write("    ],\n")
            f.write("}\n")

        print(f"✅ Created {len(rule_dict)} measurements with resolved dependency order.")
        if skipped:
            print(f"⚠️ Skipped {len(skipped)} rules. Check rule_conversion.log.")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Excel-to-Rules conversion...")
    generate_fashion_rules()
    print("🏁 Done!")
