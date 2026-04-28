# v6.1.9 Release Notes

## Release Date
2026-04-20

## Version Info
- **Total Rules**: 627 (was 616)
- **New Rules**: 11

## What's New

### New Rules (11 rules from ClawHub analysis)

| ID | Rule | Severity | Category |
|----|------|----------|----------|
| NEW-001 | Dynamic External Code Load | CRITICAL | supply_chain |
| NEW-002 | Credential Access via Environment | CRITICAL | credential_theft |
| NEW-003 | Dangerous Code Execution | CRITICAL | arbitrary_execution |
| NEW-004 | Role Priming / Behavioral Conditioning | HIGH | prompt_injection |
| NEW-005 | Configuration Override | HIGH | config_manipulation |
| NEW-006 | External Network Access | HIGH | network_access |
| NEW-007 | Hardcoded Secret | HIGH | credential_leak |
| NEW-008 | Persistence Mechanism | HIGH | persistence |
| NEW-009 | Trigger Word Detection | MEDIUM | prompt_injection |
| NEW-010 | HTTP Only Communication | MEDIUM | insecure_transport |
| NEW-011 | Unknown Market Source | LOW | supply_chain |

## ClawHub Benchmark Results

| Metric | Value |
|--------|-------|
| Total Skills | 17,483 |
| Scan Time | 40 minutes |
| CRITICAL | 4,246 (24.3%) |
| HIGH | 560 (3.2%) |
| SAFE | 7,101 (40.6%) |
| TIMEOUT | 5,570 (31.9%) |

## Installation

```bash
pip install -r requirements.txt
python scanner.py --help
```

## Upgrade from v6.1.8

```bash
# Replace all_rules.json
cp rules/dist/all_rules.json /path/to/v6.1.8/rules/

# Or install fresh
pip install security-scanner@v6.1.9
```

## Changelog

- v6.1.9: Add 11 new rules from ClawHub analysis
- v6.1.8: Deep scan optimization, 17,483 skills scanned
- v6.1.6: NPM optimization, -27% package size
- v6.1.5: Detection rate 99%, +44.9% improvement
