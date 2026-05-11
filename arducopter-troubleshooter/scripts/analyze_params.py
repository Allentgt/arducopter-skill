#!/usr/bin/env python3
"""
ArduPilot param analyzer.

Reads parsed JSON from parse_params.py and flags suspicious values.

Usage:
    python analyze_params.py <parsed-params.json>
"""

import sys
import json
from typing import Any


# Known-good ranges by parameter
# Format: {param_name: (min, max, unit, condition_also_checked_if_callable)}
SAFE_RANGES = {
    # PID gains (copter, 400Hz loop typical)
    'ATC_RAT_RLL_P': (0.05, 0.35, 'P gain'),
    'ATC_RAT_RLL_I': (0.05, 0.30, 'I gain'),
    'ATC_RAT_RLL_D': (0.0005, 0.0080, 'D gain'),
    'ATC_RAT_PIT_P': (0.05, 0.35, 'P gain'),
    'ATC_RAT_PIT_I': (0.05, 0.30, 'I gain'),
    'ATC_RAT_PIT_D': (0.0005, 0.0080, 'D gain'),
    'ATC_RAT_YAW_P': (0.05, 0.50, 'P gain'),
    'ATC_RAT_YAW_I': (0.005, 0.20, 'I gain'),
    'ATC_RAT_YAW_D': (0.0, 0.0050, 'D gain'),
    # Filters
    'INS_GYRO_FILTER': (20, 100, 'Hz, gyro low-pass'),
    'INS_ACCEL_FILTER': (10, 100, 'Hz, accel low-pass'),
    'INS_HNTCH_FREQ': (40, 250, 'Hz, notch center freq'),
    # Throttle
    'MOT_THST_HOVER': (0.05, 0.50, 'throttle hover %'),
    'MOT_THST_EXPO': (0.0, 0.80, 'thrust expo'),
    'MOT_SPIN_MIN': (0.05, 0.30, 'minimum spin %'),
    'MOT_SPIN_MAX': (0.85, 1.0, 'maximum spin %'),
    # Battery
    'BATT_CAPACITY': (300, 50000, 'mAh'),
    'BATT_ARM_VOLT': (3.0, 52.0, 'V, armed voltage'),
    'BATT_LOW_VOLT': (3.0, 50.0, 'V, low threshold'),
    'BATT_CRT_VOLT': (3.0, 50.0, 'V, critical threshold'),
    # Arming
    'ARMING_MAGTHRESH': (50, 750, 'mag check threshold'),
    'ARMING_ACCTHRESH': (0.1, 1.5, 'accel check threshold'),
    # Misc
    'SCHED_LOOP_RATE': (100, 800, 'Hz, main loop rate'),
    'MOT_PWM_MIN': (900, 1100, 'us, min PWM'),
    'MOT_PWM_MAX': (1900, 2100, 'us, max PWM'),
}

# Conditions checked via lambda: (check_description, lambda)
# lambda receives the full grouped params dict
FLAGS = []


def add_flag(description, check_fn):
    FLAGS.append((description, check_fn))


# Register flag checks
def _register_flags():
    # Check battery voltage vs cell count
    add_flag(
        "BATT_LOW_VOLT may be too close to BATT_CRT_VOLT",
        lambda p: (
            'battery' in p
            and 'BATT_LOW_VOLT' in p['battery']
            and 'BATT_CRT_VOLT' in p['battery']
            and p['battery']['BATT_LOW_VOLT'] - p['battery']['BATT_CRT_VOLT'] < 1.0
        )
    )
    
    # Check if MOT_THST_HOVER is low (possible heavy build)
    add_flag(
        "MOT_THST_HOVER is low (< 0.15) — quad may be heavy for the props",
        lambda p: (
            'throttle' in p
            and 'MOT_THST_HOVER' in p['throttle']
            and p['throttle']['MOT_THST_HOVER'] < 0.15
        )
    )
    
    # Check if filter might conflict with notch
    add_flag(
        "INS_HNTCH_ENABLE=0 but notch freq is set — notch disabled",
        lambda p: (
            'filter' in p
            and 'INS_HNTCH_FREQ' in p['filter']
            and p['filter'].get('INS_HNTCH_ENABLE', 1) == 0
        )
    )
    
    # Check compass offsets magnitude (large values = interference)
    add_flag(
        "COMPASS_OFS_Y magnitude > 300 — possible magnetic interference on this axis",
        lambda p: (
            'compass' in p
            and 'COMPASS_OFS_Y' in p['compass']
            and abs(p['compass']['COMPASS_OFS_Y']) > 300
        )
    )
    
    # Check loop rate sanity
    add_flag(
        "Loop rate is low (< 200 Hz) for a modern FC",
        lambda p: (
            'loop_rate' in p
            and 'SCHED_LOOP_RATE' in p['loop_rate']
            and p['loop_rate']['SCHED_LOOP_RATE'] < 200
        )
    )


_register_flags()


def analyze(params: dict) -> dict:
    """
    Analyze parsed params and return findings.
    
    Returns:
        {
            'out_of_range': [{'param': str, 'value': float, 'range': (min, max), 'unit': str}],
            'flags': [{'description': str, 'detail': str}],
            'summary': str,
        }
    """
    findings = {
        'out_of_range': [],
        'flags': [],
        'summary': 'No issues found.',
    }
    
    # Check each param against safe ranges
    for category, param_dict in params.items():
        if category.startswith('_'):
            continue
        for name, value in param_dict.items():
            if name in SAFE_RANGES:
                lo, hi, unit = SAFE_RANGES[name]
                if isinstance(value, (int, float)):
                    if value < lo:
                        findings['out_of_range'].append({
                            'param': name,
                            'value': value,
                            'range': (lo, hi),
                            'unit': unit,
                            'issue': f'below minimum ({lo})',
                        })
                    elif value > hi:
                        findings['out_of_range'].append({
                            'param': name,
                            'value': value,
                            'range': (lo, hi),
                            'unit': unit,
                            'issue': f'above maximum ({hi})',
                        })
    
    # Run flag checks
    for description, check_fn in FLAGS:
        try:
            if check_fn(params):
                findings['flags'].append({'description': description, 'detail': ''})
        except Exception:
            pass  # skip flag if it errors
    
    # Build summary
    total_issues = len(findings['out_of_range']) + len(findings['flags'])
    if total_issues == 0:
        findings['summary'] = 'All parameters appear within normal ranges.'
    else:
        parts = []
        if findings['out_of_range']:
            parts.append(f"{len(findings['out_of_range'])} out-of-range parameter(s)")
        if findings['flags']:
            parts.append(f"{len(findings['flags'])} configuration flag(s)")
        findings['summary'] = f"Found {', '.join(parts)}."
    
    return findings


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_params.py <parsed-params.json>", file=sys.stderr)
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    with open(input_path, 'r') as f:
        params = json.load(f)
    
    results = analyze(params)
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
