#!/usr/bin/env python3
"""
PowerShell YARA Rules Test Script
Tests detection rate and false positive rate
"""

import os
import yara
import json
from pathlib import Path

# Paths
BASE_DIR = Path(os.path.expanduser("~/.openclaw/workspace/agent-security-skill-scanner-master"))
RULES_FILE = BASE_DIR / "rules/scanner_v3/yara/powershell_rules.yar"
MALICIOUS_DIR = BASE_DIR / "benchmark_samples/malicious/powershell"
BENIGN_DIR = BASE_DIR / "benchmark_samples/benign/powershell"

def load_rules():
    """Load YARA rules"""
    print(f"Loading rules from: {RULES_FILE}")
    with open(RULES_FILE, 'r') as f:
        rules_content = f.read()
    rules = yara.compile(source=rules_content)
    return rules

def test_samples(rules, sample_dir, sample_type):
    """Test samples against rules"""
    ps1_files = list(Path(sample_dir).glob("*.ps1"))
    print(f"\n{sample_type} samples: {len(ps1_files)} files")
    
    detected = 0
    not_detected = []
    matches_by_rule = {}
    
    for ps1_file in ps1_files:
        with open(ps1_file, 'r') as f:
            content = f.read()
        
        matches = rules.match(data=content)
        
        if matches:
            detected += 1
            for match in matches:
                rule_name = match.rule
                if rule_name not in matches_by_rule:
                    matches_by_rule[rule_name] = 0
                matches_by_rule[rule_name] += 1
        else:
            not_detected.append(ps1_file.name)
    
    detection_rate = (detected / len(ps1_files) * 100) if ps1_files else 0
    
    return {
        'total': len(ps1_files),
        'detected': detected,
        'not_detected': not_detected,
        'detection_rate': detection_rate,
        'matches_by_rule': matches_by_rule
    }

def main():
    print("=" * 60)
    print("PowerShell YARA Rules Evaluation")
    print("=" * 60)
    
    # Load rules
    try:
        rules = load_rules()
        print("✓ Rules loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load rules: {e}")
        return
    
    # Test malicious samples
    print("\n" + "=" * 60)
    print("MALICIOUS SAMPLES TEST")
    print("=" * 60)
    malicious_results = test_samples(rules, MALICIOUS_DIR, "Malicious")
    
    print(f"\nTotal malicious samples: {malicious_results['total']}")
    print(f"Detected: {malicious_results['detected']}")
    print(f"Not detected: {len(malicious_results['not_detected'])}")
    print(f"Detection rate: {malicious_results['detection_rate']:.1f}%")
    
    if malicious_results['not_detected']:
        print("\nMissed files:")
        for f in malicious_results['not_detected']:
            print(f"  - {f}")
    
    # Test benign samples
    print("\n" + "=" * 60)
    print("BENIGN SAMPLES TEST (False Positive Check)")
    print("=" * 60)
    benign_results = test_samples(rules, BENIGN_DIR, "Benign")
    
    print(f"\nTotal benign samples: {benign_results['total']}")
    print(f"False positives: {benign_results['detected']}")
    print(f"Correctly classified: {benign_results['total'] - benign_results['detected']}")
    false_positive_rate = (benign_results['detected'] / benign_results['total'] * 100) if benign_results['total'] else 0
    print(f"False positive rate: {false_positive_rate:.1f}%")
    
    if benign_results['not_detected']:
        print("\nCorrectly classified as benign:")
        for f in benign_results['not_detected'][:5]:
            print(f"  - {f}")
    
    # Rule effectiveness
    print("\n" + "=" * 60)
    print("RULE EFFECTIVENESS (Malicious samples)")
    print("=" * 60)
    sorted_rules = sorted(malicious_results['matches_by_rule'].items(), 
                         key=lambda x: x[1], reverse=True)
    for rule_name, count in sorted_rules[:15]:
        print(f"{rule_name}: {count} matches")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"PowerShell Detection Rate: {malicious_results['detection_rate']:.1f}%")
    print(f"False Positive Rate: {false_positive_rate:.1f}%")
    
    # Target check
    target_detection = 80.0
    target_fp = 5.0
    
    if malicious_results['detection_rate'] >= target_detection and false_positive_rate < target_fp:
        print("\n✓ TARGET ACHIEVED!")
        print(f"  - Detection rate ≥ {target_detection}%: ✓")
        print(f"  - False positive rate < {target_fp}%: ✓")
    else:
        print("\n✗ TARGET NOT MET")
        if malicious_results['detection_rate'] < target_detection:
            print(f"  - Detection rate {malicious_results['detection_rate']:.1f}% < {target_detection}%")
        if false_positive_rate >= target_fp:
            print(f"  - False positive rate {false_positive_rate:.1f}% ≥ {target_fp}%")
    
    # Save results
    results = {
        'malicious': malicious_results,
        'benign': benign_results,
        'detection_rate': malicious_results['detection_rate'],
        'false_positive_rate': false_positive_rate,
        'target_met': (malicious_results['detection_rate'] >= target_detection and 
                      false_positive_rate < target_fp)
    }
    
    results_file = BASE_DIR / "powershell_rules_test_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")

if __name__ == "__main__":
    main()
