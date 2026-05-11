#!/usr/bin/env python3
"""
ArduPilot .param file parser.

Reads a .param file (CSV: PARAM_NAME,value) and outputs structured JSON
grouped by subsystem category.

Usage:
    python parse_params.py <input.param> [output.json]
    
If output.json is omitted, prints to stdout.
"""

import sys
import json
import re
from collections import defaultdict


# Subsystem categorization rules
# Each entry: (prefix_regex, or list of exact names, category_name)
CATEGORY_RULES = [
    # PID groups
    (r'^ATC_RAT_RLL_', 'pid_roll'),
    (r'^ATC_RAT_PIT_', 'pid_pitch'),
    (r'^ATC_RAT_YAW_', 'pid_yaw'),
    (r'^ATC_ANG_', 'angle'),
    (r'^ATC_ACCEL_', 'angle_rate'),
    (r'^ATC_RATE_', 'rate_limit'),
    (r'^ATC_THR_', 'throttle_mix'),
    (r'^ATC_INPUT_TC$', 'angle_rate'),
    (r'^ATC_SLEW_', 'angle_rate'),
    # Throttle / motor spin
    (r'^MOT_THST_', 'throttle'),
    (r'^MOT_SPIN_', 'throttle'),
    (r'^MOT_HOVER_', 'throttle'),
    (r'^MOT_BAT_', 'throttle'),
    (r'^THR_DZ$', 'throttle'),
    # Motor / ESC
    (r'^MOT_PWM_', 'motor_esc'),
    (r'^MOT_BOOST_', 'motor_esc'),
    (r'^MOT_YAW_', 'motor_esc'),
    (r'^MOT_OPTIONS$', 'motor_esc'),
    (r'^MOT_SLEW_', 'motor_esc'),
    (r'^MOT_SPOOL_', 'motor_esc'),
    (r'^MOT_SAFE_', 'motor_esc'),
    (r'^SERVO_BLH_', 'motor_esc'),
    (r'^SERVO_DSHOT_', 'motor_esc'),
    (r'^SERVO_FTW_', 'motor_esc'),
    # Battery
    (r'^BATT_', 'battery'),
    # Filter
    (r'^INS_HNTCH_', 'filter'),
    (r'^INS_GYRO_FILTER$', 'filter'),
    (r'^INS_ACCEL_FILTER$', 'filter'),
    (r'^INS_GYRO_RATE$', 'filter'),
    (r'^INS_FAST_SAMPLE$', 'filter'),
    # EKF
    (r'^EK3_', 'ekf'),
    # GPS
    (r'^GPS\d?_', 'gps'),
    # Frame
    (r'^FRAME_', 'frame'),
    # Arming
    (r'^ARMING_', 'arming'),
    # Failsafe
    (r'^FS_', 'failsafe'),
    # RC channels
    (r'^RC\d{1,2}_', 'rc_channels'),
    (r'^RCMAP_', 'rc_channels'),
    # Logging
    (r'^LOG_', 'logging'),
    (r'^INS_LOG_', 'logging'),
    # OSD
    (r'^OSD\d?_', 'osd'),
    # Loop rate
    (r'^SCHED_LOOP_RATE$', 'loop_rate'),
    # Compass
    (r'^COMPASS_', 'compass'),
    # AHRS
    (r'^AHRS_', 'ahrs'),
    # Misc params that don't fit a group
    (r'^INS_ACC', 'imu'),
    (r'^INS_GYR', 'imu'),
    (r'^INS_USE\d?$', 'imu'),
]


def categorize_param(name):
    """Return the category name for a parameter, or 'other'."""
    for pattern, category in CATEGORY_RULES:
        if re.match(pattern, name):
            return category
    return 'other'


def parse_param_file(filepath):
    """Parse a .param file and return {category: {name: value}}."""
    groups = defaultdict(dict)
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ',' not in line:
                print(f"Warning: line {line_num} has no comma, skipping: {line}",
                      file=sys.stderr)
                continue
            parts = line.split(',', 1)
            name = parts[0].strip()
            raw_val = parts[1].strip()
            # Try numeric conversion
            try:
                if '.' in raw_val:
                    value = float(raw_val)
                else:
                    value = int(raw_val)
            except ValueError:
                value = raw_val
            category = categorize_param(name)
            groups[category][name] = value
    return dict(groups)


def main():
    if len(sys.argv) < 2:
        print("Usage: parse_params.py <input.param> [output.json]", file=sys.stderr)
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = parse_param_file(input_path)
    except FileNotFoundError:
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing {input_path}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Add metadata
    result['_meta'] = {
        'source_file': input_path,
        'param_count': sum(len(v) for v in result.values()),
        'categories': list(result.keys()),
    }
    
    output = json.dumps(result, indent=2, default=str)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(output)
        print(f"Wrote {result['_meta']['param_count']} params to {output_path}")
    else:
        print(output)


if __name__ == '__main__':
    main()
