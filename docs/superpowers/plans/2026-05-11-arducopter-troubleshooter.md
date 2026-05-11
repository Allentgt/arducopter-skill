# ArduCopter Troubleshooter Skill — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an OpenCode skill that turns the AI into an ArduCopter diagnostic assistant for building, tuning, flying, and troubleshooting quadcopters.

**Architecture:** Hybrid skill with a Markdown workflow engine (SKILL.md), bundled reference docs for common issues, deterministic Python scripts for param file analysis, and web fetch fallback for edge cases. Progressive disclosure — reference docs load only when the diagnostic path needs them.

**Tech Stack:** OpenCode skill system, Python 3 for param parsing/analysis, Markdown reference files.

**File structure:**
```
arducopter-troubleshooter/
├── SKILL.md
├── references/
│   ├── pid-tuning.md
│   ├── ekf-diagnostics.md
│   ├── failsafes.md
│   ├── motor-esc.md
│   ├── flight-modes.md
│   ├── parameter-reference.md
│   ├── common-issues.md
│   └── build-setup.md
└── scripts/
    ├── parse_params.py
    └── analyze_params.py
```

**Test fixture:** `skystarh7.param` in the workspace root — a real ArduPilot param export from a 6S X-frame quad (SkyStar H7 FC, 400Hz loop, DShot, EKF3, harmonic notch 80Hz).

---

### Task 1: Skill directory, SKILL.md, and scripts directory

**Files:**
- Create: `arducopter-troubleshooter/SKILL.md`
- Create: `arducopter-troubleshooter/scripts/.gitkeep`

- [ ] **Step 1: Create directory structure**

```bash
New-Item -ItemType Directory -Path "arducopter-troubleshooter\references" -Force; New-Item -ItemType Directory -Path "arducopter-troubleshooter\scripts" -Force
```

- [ ] **Step 2: Write SKILL.md**

```markdown
---
name: arducopter-troubleshooter
description: >-
  An interactive troubleshooting skill for ArduCopter quadcopters. Use this
  skill whenever the user mentions ArduCopter, ArduPilot, multi-rotor,
  quadcopter, or quad build help — including PID tuning, EKF errors, GPS
  problems, failsafes, oscillation/drift troubleshooting, motor/ESC issues,
  flight mode selection, battery configuration, pre-flight checks, param
  file analysis, or any build/setup/flying issue with an ArduCopter-based
  quad. Trigger even if the user only mentions "quad" or "drone" with
  technical symptoms. Do NOT trigger for general drone photography,
  non-ArduPilot flight controllers (Betaflight, iNav, PX4), or non-quad
  ArduPilot vehicles (planes, rovers, boats).
---

# ArduCopter Troubleshooter

An interactive diagnostic assistant for ArduCopter quadcopters. Covers
building, tuning, flying, and troubleshooting.

## Workflow

Follow these phases in order. Do NOT skip to recommendations without
collecting context first.

### Phase 1: Intake

Ask the user these questions (one at a time, let them answer each):

1. **Frame & build:** What frame size (e.g., 5", 7")? What motors/props?
   What flight controller? What firmware version (Copter 4.5, 4.6, etc.)?
2. **Symptom:** What exactly is wrong? When does it happen (hover, throttle
   punch, turns, descent)? How severe is it?
3. **Context:** Any recent changes (new props, firmware update, crash, new
   battery)? Does it happen every flight or intermittently?
4. **Parms:** Ask if they can share their `.param` file. If yes, run the
   param analysis scripts (Task 2) before proceeding.

### Phase 2: Param Analysis

If the user provides a `.param` file:

```python
# Run from project root:
python arducopter-troubleshooter/scripts/parse_params.py <path-to-param-file>
python arducopter-troubleshooter/scripts/analyze_params.py <path-to-json-output>
```

Present the findings to the user:
- "Your PIDs are within normal range."
- "Your battery failsafe voltage may be too low — BATT_CRT_VOLT is X
  but for a 6S you typically want Y."
- Flag any suspicious values. Do NOT recommend changes yet — more
  context is needed.

### Phase 3: Diagnostic Tree Matching

Match the symptom + param analysis against these categories. For each,
open the relevant reference doc from `references/`.

#### A. Oscillations / Vibration

*Read `references/pid-tuning.md` and `references/common-issues.md`*

Questions:
- Do oscillations happen at hover, punch-out, or descent?
- Do you see it in the FPV feed or hear it?
- Are your props balanced? Frame bolts tight?

Check param context:
- If ATC_RAT_RLL_D > 0.0020 and INS_GYRO_FILTER > 40 → D term noise
- If INS_HNTCH_ENABLE=0 and user has no notch → add notch
- If MOT_THST_HOVER < 0.15 → possible over-propped or heavy build

#### B. EKF Warnings / Errors

*Read `references/ekf-diagnostics.md`*

Questions:
- Which EKF status number? What color is the EKF icon?
- Does it happen near power lines, bridges, or metal structures?
- Did you do a compass calibration recently?

Check param context:
- EK3_MAG_CAL flag
- COMPASS_OFS_X/Y/Z magnitudes (over 500 indicates interference)
- EK3_ERR_THRESH setting

#### C. Failsafe Triggers

*Read `references/failsafes.md`*

Questions:
- Which failsafe triggered (radio, battery, EKF, GCS)?
- What was the battery voltage when it happened?
- How far away was the quad?

Check param context:
- BATT_LOW_VOLT / BATT_CRT_VOLT vs BATT_ARM_VOLT (6S = 25.2V full)
- FS_THR_VALUE vs RC3_MIN
- FS_EKF_ACTION setting

#### D. Bad Flight Behavior

*Read `references/flight-modes.md` and `references/common-issues.md`*

- Drift → check AHRS_TRIM_X/Y, ACCEL cal, compass interference
- Toilet-bowling → compass interference or GPS glitching
- Altitude hold issues → baro coverage, prop wash, GNSS interference
- Yaw issues → ATC_RAT_YAW_P, motor orientation check

#### E. GPS Problems

*Read `references/ekf-diagnostics.md`*

- No GPS fix → check GPS_TYPE, GPS_AUTO_CONFIG, antenna placement
- Bad HDOP → satellite count, GPS_HDOP_GOOD threshold
- Glitching → GPS cable shielding, interference from VTX/ESC

#### F. Motor / ESC Issues

*Read `references/motor-esc.md`*

- Desync → DShot vs PWM protocol mismatch, MOT_PWM_TYPE
- Hot motors → timing issues, bad ESC calibration, over-propped
- Motor not spinning → MOT_SPIN_MIN, servo functions, arming checks

### Phase 4: Recommendation

After matching the symptom, provide:

1. **Specific param changes** — exact parameter name and new value:
   ```
   ATC_RAT_RLL_P from 0.135 → 0.110 (reduce by 20%)
   ```
2. **Hardware checks** — what to inspect and how:
   "Balance props using a prop balancer. Check that frame bolts are tight.
   Ensure FC is on vibration-dampening mount."
3. **Re-test instructions** — how to verify:
   "Arm and hover at 2m altitude. Listen for oscillations. If smooth,
   try a slow forward flight pass. Report back."
4. **Confirmation** — ask if the fix helped before escalating

### Phase 5: Web Fallback

If the symptom doesn't match any diagnostic tree, or the user's firmware
version is bleeding-edge:

1. Search `ardupilot.org/copter/docs/` for the topic
2. Search `discuss.ardupilot.org` for recent threads
3. If relevant, search `github.com/ArduPilot/ardupilot/issues`
4. Present findings with source URLs

### Guidance Principles

- **ASK first, recommend second.** Never skip the intake phase.
- **One question at a time.** Don't dump all intake questions at once.
- **Explain WHY.** For every recommendation, briefly explain the reasoning
  so the user learns and can self-diagnose next time.
- **Be conservative with PIDs.** Recommend small changes (10-20%) and
  re-test. Never suggest extreme gain values.
- **Hardware first, software second.** Check physical issues (props,
  frame, wiring) before suggesting parameter changes.
- **Reference docs are guides, not gospel.** Every build is different.
- **Use the param file as a test fixture.** The provided `skystarh7.param`
  can be used to verify the parsing scripts work correctly.

---

### Running the scripts

When the user provides a param file:
```
# Parse
python arducopter-troubleshooter/scripts/parse_params.py /path/to/user.param

# Analyze
python arducopter-troubleshooter/scripts/analyze_params.py /path/to/parsed/params.json
```

The param file may be embedded in a code block or shared as an attachment.
If embedded in a code block, save it to a temp file first, then run parse.
```

- [ ] **Step 3: Verify SKILL.md is well-formed**

Check that the YAML frontmatter is valid and the document reads correctly.

- [ ] **Step 4: Commit**

```bash
git add arducopter-troubleshooter/SKILL.md
git commit -m "feat: add arducopter-troubleshooter skill with diagnostic workflow"
```

---

### Task 2: Param file parser and analyzer scripts

**Files:**
- Create: `arducopter-troubleshooter/scripts/parse_params.py`
- Create: `arducopter-troubleshooter/scripts/analyze_params.py`

- [ ] **Step 1: Write parse_params.py**

```python
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
```

- [ ] **Step 2: Verify parse_params.py on the test fixture**

```bash
python arducopter-troubleshooter/scripts/parse_params.py skystarh7.param
```

Expected: JSON output with all params grouped by category. Verify `pid_roll` contains ATC_RAT_RLL_P/I/D/FLTD/FLTT etc.

- [ ] **Step 3: Write analyze_params.py**

```python
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
        "INS_HNTCH_ENABLE=0 but user has a 3.5" notch freq set — notch disabled",
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
```

- [ ] **Step 4: End-to-end test the scripts on the fixture**

```bash
python arducopter-troubleshooter/scripts/parse_params.py skystarh7.param | python arducopter-troubleshooter/scripts/analyze_params.py
```

Expected: JSON output showing out_of_range params (if any) and flags. Verify it catches at least the compass offset flag for COMPASS_OFS_Y=465.

- [ ] **Step 5: Commit**

```bash
git add arducopter-troubleshooter/scripts/
git commit -m "feat: add param file parser and analyzer scripts"
```

---

### Task 3: Core reference docs — PID tuning, EKF, failsafes

**Files:**
- Create: `arducopter-troubleshooter/references/pid-tuning.md`
- Create: `arducopter-troubleshooter/references/ekf-diagnostics.md`
- Create: `arducopter-troubleshooter/references/failsafes.md`

- [ ] **Step 1: Write pid-tuning.md**

```markdown
# PID Tuning Guide

## Quick Theory

- **P (Proportional):** How hard the FC tries to correct an error. Too high = oscillations. Too low = sluggish/loose feel.
- **I (Integral):** Corrects steady-state error (wind, CG offset). Too high = slow oscillations/wobble. Too low = drift under constant load.
- **D (Derivative):** Dampens P, adds stability. Too high = noise amplification (hot motors, twitchy feel). Too low = overshoot on fast inputs.

## Tuning Order

Always tune in this sequence:

1. **Filters first** — set your notch and low-pass correctly before touching PIDs
2. **Rate P** — raise until you see oscillations, then back off 20%
3. **Rate D** — raise until motors get warm or twitchy, then back off 20%
4. **Rate I** — conservative default is usually fine; raise for better wind handling
5. **Angle P** — raise for sharper angle mode response
6. **Throttle** — MOT_THST_HOVER autotune or set manually

## Filter Setup

### Harmonic Notch (HNTCH)

The harmonic notch tracks motor RPM and cancels the fundamental + harmonics.

Key params:
- `INS_HNTCH_ENABLE=1` — enable
- `INS_HNTCH_FREQ=80` — starting point for most 5" quads (adjust by ear)
- `INS_HNTCH_HMNCS=3` — cancel 1st, 2nd, 3rd harmonics
- `INS_HNTCH_MODE=3` — dynamic (tracks RPM from DShot)

Rule of thumb for HNTCH_FREQ start values:
- 5" freestyle: 70-90 Hz
- 5" racing: 90-120 Hz
- 7" long range: 40-60 Hz
- 3" cinewhoop: 120-180 Hz

### Gyro Low-Pass

`INS_GYRO_FILTER` — typical range 40-100 Hz.
Higher = sharper but more noise. 40 Hz for cinewhoops, 80-100 Hz for racing.

## Common Tuning Issues

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| High-frequency oscillation at hover | D too high, or notch freq wrong | Reduce D by 20%, or check HNTCH_FREQ |
| Low-frequency bobble (0.5-2 Hz) | I too high | Reduce ATC_RAT_*_I by 20% |
| Yaw twitch on throttle punch | Yaw P too high or I too high | Reduce ATC_RAT_YAW_P or ATC_RAT_YAW_I |
| Hot motors after tuning | D too high or filter too aggressive | Reduce D, lower INS_GYRO_FILTER |
| Slow/floaty feel | P too low | Raise ATC_RAT_*_P by 10% |

## Autotune

1. Set `AUTOTUNE_AGGR=0.05` (conservative) or `0.10` (aggressive)
2. Set `AUTOTUNE_AXES=1` (roll/pitch only) or `3` (roll/pitch/yaw)
3. Fly in AltHold or Loiter
4. Toggle autotune ON via RC switch or GCS
5. Do punch-outs, fast forward flight, rolls/flips
6. Let it run 2-3 minutes, toggle OFF
7. Land and check the new param values
8. Set `AUTOTUNE_AXES=0` when done

**After autotune:** Always check that D values aren't too high for your frame. Autotune doesn't know your frame resonance.
```

- [ ] **Step 2: Write ekf-diagnostics.md**

```markdown
# EKF / GPS Diagnostics

## EKF Status Display

The EKF status number (visible in OSD or GCS) tells you what's wrong:

| Status | Meaning | Action |
|--------|---------|--------|
| 0-1 | Healthy | Nothing |
| 2 | Constrained (minor) | Check for intermittent GPS/mag issues |
| 3-4 | Variance too high | Check vibration, mag interference, GPS glitching |

## Common EKF Causes

### 1. Compass / Magnetic Interference

Most common cause of EKF errors.

**Symptoms:** EKF variance climbs during throttle, yaw movements, or in specific directions.

**Causes:**
- VTX antenna too close to compass
- Battery wires carrying high current near FC
- Speaker/magnet near FC
- Steel screws in frame/camera
- Poor compass calibration

**Fix:**
1. Check COMPASS_OFS_X/Y/Z — values over 300 indicate likely interference
2. Move GPS/compass module away from power wires and VTX
3. Re-do compass calibration
4. Enable `COMPASS_LEARN=1` for in-flight learning

### 2. GPS Glitching

**Symptoms:** EKF variance spikes, position jumps in OSD.

**Causes:**
- GPS antenna blocked by frame carbon fiber
- VTX harmonic interference on GPS frequency (1.5 GHz)
- Low satellite count / high HDOP

**Fix:**
1. Mount GPS on mast above the frame
2. Shield GPS cable from VTX/ESC noise
3. Check `GPS_HDOP_GOOD=140` (default is fine)
4. Use GPS with M8 or M10 u-blox chipset

### 3. Vibration Affecting EKF

**Symptoms:** EKF variance climbs across all axes, correlates with throttle.

**Causes:**
- Unbalanced props
- Frame resonance at certain RPM
- FC not properly vibration-dampened

**Fix:**
1. Balance props
2. Check FC mounting (soft mount vs rigid)
3. Enable harmonic notch filter if not already
4. Check FFT logs if available

## Key EKF Params

| Param | Default | What It Does |
|-------|---------|-------------|
| EK3_ENABLE | 1 | Enable EKF3 (should be 1) |
| EK3_MAG_CAL | 3 | Mag calibration type (3=learn in-flight) |
| EK3_ERR_THRESH | 0.2 | Error threshold before EKF failsafe |
| EK3_SRC1_POSXY | 3 | Primary horizontal position source (3=GPS) |
| EK3_SRC1_YAW | 1 | Primary yaw source (1=compass) |
| EK3_SRC1_VELXY | 3 | Primary horizontal velocity source (3=GPS) |
| EK3_SRC1_POSZ | 1 | Primary vertical position source (1=baro) |
```

- [ ] **Step 3: Write failsafes.md**

```markdown
# Failsafe Guide

## Battery Failsafe

Two thresholds:
- **BATT_LOW_VOLT** — triggers warning action (default: land or RTL)
- **BATT_CRT_VOLT** — triggers critical action (default: disarm)

**6S setup:** BATT_ARM_VOLT=25.2 → BATT_LOW_VOLT=21.6 → BATT_CRT_VOLT=21.0
**4S setup:** BATT_ARM_VOLT=16.8 → BATT_LOW_VOLT=14.4 → BATT_CRT_VOLT=14.0

**BATT_FS_LOW_ACT:** 0=nothing, 1=land, 2=RTL, 3=smart RTL
**BATT_FS_CRT_ACT:** 0=nothing, 1=land, 2=RTL, 3=smart RTL

## Radio Failsafe

**How it works:** When RC signal is lost for `RC_FS_TIMEOUT` seconds, the FC triggers the radio failsafe.

- `FS_THR_ENABLE=1` — enable radio failsafe
- `FS_THR_VALUE` — throttle channel value that means "signal lost." Set just below minimum throttle stick value.
- `FS_THR_ENABLE` action options: 0=disabled, 1=RTL, 2=glide, 3=land, 4=smart RTL, 5=brake

**Setting FS_THR_VALUE correctly:**
1. Check RC3_MIN and RC3_MAX in your params
2. Set FS_THR_VALUE to about 20-50 below RC3_MIN
3. Test by turning off transmitter while on ground (motors should not arm)

## GCS Failsafe

Triggers when telemetry heartbeat stops for `FS_GCS_TIMEOUT` seconds.

- `FS_GCS_ENABLE=1` — enable
- `FS_GCS_TIMEOUT=5` — seconds before trigger
- Action: same as radio failsafe (RTL/land/etc.)

## EKF Failsafe

Triggers when EKF variance exceeds `FS_EKF_THRESH` for `FS_EKF_FILT` seconds.

- `FS_EKF_ACTION=1` — enable (1=RTL, 2=land)
- `FS_EKF_THRESH=0.8` — variance threshold
- `FS_EKF_FILT=5` — seconds of sustained variance before action

## Crash Check

- `FS_CRASH_CHECK=1` — enable (disarms motors on crash detection)
- Detects sudden acceleration/deceleration exceeding crash threshold

## Recommended Failsafe Configuration

```
BATT_FS_LOW_ACT=2     RTL on low battery
BATT_FS_CRT_ACT=1     Land on critical battery
FS_THR_ENABLE=1       RTL on radio loss
FS_GCS_ENABLE=0       Disabled unless using telemetry
FS_EKF_ACTION=1       RTL on EKF issues
FS_CRASH_CHECK=1      Disarm on crash
```

> **Note:** Always test failsafes at low altitude first. RTL requires a good GPS lock and compass calibration.
```

- [ ] **Step 4: Commit**

```bash
git add arducopter-troubleshooter/references/pid-tuning.md arducopter-troubleshooter/references/ekf-diagnostics.md arducopter-troubleshooter/references/failsafes.md
git commit -m "feat: add pid-tuning, ekf-diagnostics, and failsafes reference docs"
```

---

### Task 4: Hardware reference docs — motor/ESC, flight modes, build setup

**Files:**
- Create: `arducopter-troubleshooter/references/motor-esc.md`
- Create: `arducopter-troubleshooter/references/flight-modes.md`
- Create: `arducopter-troubleshooter/references/build-setup.md`

- [ ] **Step 1: Write motor-esc.md**

```markdown
# Motor & ESC Guide

## Motor Numbering (Quad X)

```
  Motor 2 (CW)   |   Motor 1 (CCW)
         \       |       /
          \      |      /
           \     |     /
    (front)=============(front)
           /     |     \
          /      |      \
         /       |       \
  Motor 3 (CW)   |   Motor 4 (CCW)
```

- Servo1 → Motor 1 (front-right, CCW)
- Servo2 → Motor 2 (rear-right, CW)
- Servo3 → Motor 3 (rear-left, CCW)
- Servo4 → Motor 4 (front-left, CW)

## ESC Protocols

Set via `MOT_PWM_TYPE`:

| Value | Protocol | When to Use |
|-------|----------|-------------|
| 0 | PWM | Legacy, not recommended |
| 1 | Oneshot125 | Older ESCs |
| 2 | Oneshot42 | Older ESCs |
| 3 | Multishot | Older ESCs |
| 5 | BRUSA ESC | Specialized |
| 6 | **DSHOT300** | Recommended baseline |
| 7 | DShot600 | Fast, good for high-performance |
| 8 | DShot1200 | Very fast, require good ESCs |
| 10 | Bi-directional DShot | For RPM filtering (requires BLHeli_32 or BlueJay) |

**Recommendation:** DShot600 (`MOT_PWM_TYPE=7`) for most modern builds.
DShot300 (`MOT_PWM_TYPE=6`) if you have ESC compatibility issues.

## DShot Commands

MOT_PWM_TYPE=6+ enables sending commands to BLHeli_32 ESCs via `SERVO_BLH_*` params.

## ESC Calibration

**For PWM/Oneshot ESCs:**
1. Remove props
2. Set `MOT_PWM_TYPE=0` and `ESC_CALIBRATION=3`
3. Power cycle FC (with battery, USB disconnected)
4. You'll hear: beeps → tones → beeps (calibration complete)
5. Set `ESC_CALIBRATION=0`
6. Power cycle again

**DSHot ESCs do NOT need calibration** — they use a fixed protocol.

## Desync Troubleshooting

**Symptoms:** Motor stutters at low throttle, or quad flips on punch-out.

**Causes:** 
- Wrong protocol (`MOT_PWM_TYPE` mismatch with ESC capability)
- `MOT_SPIN_MIN` too low (motors don't spin up reliably)
- ESC timing too low for high-KV motors

**Fixes:**
1. Ensure `MOT_PWM_TYPE` matches your ESCs (DShot600 for most BLHeli_32)
2. Raise `MOT_SPIN_MIN` from 0.15 to 0.20
3. If using BLHeli, increase motor timing to "medium-high"
4. Check solder joints on motor wires

## Hot Motors

**Possible causes (check in order):**
1. Props too large for the motor (over-propped)
2. D term too high (ATC_RAT_*_D)
3. Gyro filter too low blocking feedback
4. ESC timing too high
5. Bad bearings / dirt in motors
```

- [ ] **Step 2: Write flight-modes.md**

```markdown
# Flight Modes Guide

| Mode | GPS Required | Use Case | Behavior |
|------|-------------|----------|----------|
| **Stabilize** | No | Learning, acro | Rate mode — sticks control rotation rate. No position hold. Standard RC feel. |
| **AltHold** | No | Learning altitude | Stabilize + automatic altitude hold via barometer. Throttle stick = climb/sink rate. |
| **Loiter** | Yes | Steady hover | GPS position + altitude hold. Sticks = position offset from center. |
| **PosHold** | Yes | Like Loiter but sportier | Same as Loiter but uses rate controller for position — feels more locked in. |
| **RTL** | Yes | Return home | Climbs to RTL_ALT, flies home, descends. RTL_LOIT_TIME=5000 (5s hover before descent). |
| **Smart RTL** | Yes | Return via flight path | Same as RTL but retraces flight path backwards. Good for tricky terrain. |
| **Auto** | Yes | Autonomous missions | Follows mission waypoints loaded via Mission Planner. |
| **Acro** | No | Freestyle / racing | Pure rate mode. No auto-level. Full authority. |
| **Sport** | No | Fast forward flight | Stabilize mode but allows forward tilt without holding the stick. |
| **Drift** | No | Easy forward flight | Simplified control — roll/pitch are auto-leveled. |
| **Throw** | Yes | Launch by throwing | Motor starts when throw detected, goes to THROW_NEXTMODE. |
| **Follow** | Yes | Follow-me | Copter follows a GCS carrying device. |

## Mode Switching

Set via `FLTMODE_CH` (RC channel for mode switch).
Configure each `FLTMODE1` through `FLTMODE6` with the desired mode number.

**Recommended mode setup for a 6-position switch:**
- FLTMODE1: Stabilize (0)
- FLTMODE2: AltHold (2)
- FLTMODE3: Loiter (3)
- FLTMODE4: Sport (4)
- FLTMODE5: RTL (10)
- FLTMODE6: Acro (5)
```

- [ ] **Step 3: Write build-setup.md**

```markdown
# Build Setup Guide

## Frame Selection

| Frame Size | Typical Use | Motor Size | Prop Size | Battery |
|-----------|-------------|------------|-----------|---------|
| 3" | Cinewhoop, indoor | 110x-140x | 3x3" | 4S 650-850mAh |
| 5" | Freestyle, racing | 2205-2306 | 5x4" | 4S-6S 1300-1800mAh |
| 6" | Cine, long range | 2207-2306 | 6x4" | 6S 1500-2200mAh |
| 7" | Long range | 2507-2806 | 7x5" | 6S 3000-4000mAh |
| 10"+ | Heavy lift, camera | 3110+ | 10x5"+ | 6S-12S 5000mAh+ |

## Motor / Prop Matching

- **Under-propped** (too-small props on too-large motors) → inefficient, hot motors
- **Over-propped** (too-large props on too-small motors) → ESC/motor overheating, poor flight time
- **Rule of thumb:** 3-5W per gram of motor weight at full throttle

## FC Mounting

- Mount FC on silicone/vibration-dampening standoffs
- Arrow on FC must point toward the front of the frame
- Check AHRS_ORIENTATION if FC is rotated
- Keep FC away from power distribution wires

## GPS Mounting

- GPS/compass module goes on mast ABOVE the frame
- Keep 5cm+ away from:
  - VTX antenna
  - Battery wires
  - Camera
  - Any carbon fiber (shields GPS signal)
- GPS cable should be shielded from ESC noise
- Coil excess GPS cable into a ferrite ring if possible

## Power Distribution

- Use a capacitor on the battery lead to filter voltage spikes
- Matek or Holybro power distribution boards are reliable
- Keep ESC signal wires away from power wires
- Use twisted signal pairs for longer ESC wire runs
```

- [ ] **Step 4: Commit**

```bash
git add arducopter-troubleshooter/references/motor-esc.md arducopter-troubleshooter/references/flight-modes.md arducopter-troubleshooter/references/build-setup.md
git commit -m "feat: add motor-esc, flight-modes, and build-setup reference docs"
```

---

### Task 5: Data reference docs — parameter reference and common issues

**Files:**
- Create: `arducopter-troubleshooter/references/parameter-reference.md`
- Create: `arducopter-troubleshooter/references/common-issues.md`

- [ ] **Step 1: Write parameter-reference.md**

```markdown
# Parameter Reference

Key ArduCopter parameters organized by category with safe ranges and notes.

## PID & Rate

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| ATC_RAT_RLL_P | 0.05-0.35 | 0.135 | Roll rate P gain. Lower for heavy builds. |
| ATC_RAT_RLL_I | 0.05-0.30 | 0.135 | Roll rate I gain. Higher = better wind handling. |
| ATC_RAT_RLL_D | 0.0005-0.008 | 0.0015 | Roll rate D gain. Higher = more damping but noisy. |
| ATC_RAT_PIT_P | 0.05-0.35 | 0.135 | Pitch rate P gain. Usually same as roll. |
| ATC_RAT_PIT_I | 0.05-0.30 | 0.135 | Pitch rate I gain. |
| ATC_RAT_PIT_D | 0.0005-0.008 | 0.0015 | Pitch rate D gain. |
| ATC_RAT_YAW_P | 0.05-0.50 | 0.18 | Yaw rate P gain. Can be higher than roll/pitch. |
| ATC_RAT_YAW_I | 0.005-0.20 | 0.018 | Yaw rate I gain. |
| ATC_RAT_YAW_D | 0.0-0.005 | 0.0 | Yaw rate D gain. Usually 0. |
| ATC_ANG_RLL_P | 3.0-9.0 | 4.5 | Angle mode roll P gain. |
| ATC_ANG_PIT_P | 3.0-9.0 | 4.5 | Angle mode pitch P gain. |
| ATC_ANG_YAW_P | 3.0-9.0 | 4.5 | Angle mode yaw P gain. |
| ATC_RATE_FF_ENAB | 0-1 | 1 | Enable feedforward. Keep enabled. |
| ATC_ACCEL_R_MAX | 20000-180000 | 168600 | Max roll acceleration (cm/s²). Lower = smoother. |
| ATC_ACCEL_P_MAX | 20000-180000 | 168600 | Max pitch acceleration. |
| ATC_ACCEL_Y_MAX | 5000-50000 | 31500 | Max yaw acceleration. |

## Filters

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| INS_GYRO_FILTER | 20-120 Hz | 80 | Gyro low-pass filter. Higher = sharper. |
| INS_ACCEL_FILTER | 10-100 Hz | 20 | Accel low-pass filter. |
| INS_FAST_SAMPLE | 0-1 | 1 | Enable 2x gyro sampling (8kHz→16kHz). Keep enabled. |
| INS_GYRO_RATE | 0-1 | 1 | 1 = 1kHz, 0 = 1kHz auto (usually fine). |
| INS_HNTCH_ENABLE | 0-1 | 0 | Enable harmonic notch filter. Recommended ON. |
| INS_HNTCH_FREQ | 40-250 Hz | 80 | Notch center frequency. Tune to motor RPM. |
| INS_HNTCH_HMNCS | 1-7 | 3 | Number of harmonics to notch. |
| INS_HNTCH_MODE | 0-3 | 3 | 0=fixed, 3=dynamic (track RPM from DShot). |
| INS_HNTCH_REF | 0-1 | 1 | Reference source (1=DShot telemetry). |

## Throttle

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| MOT_THST_HOVER | 0.05-0.50 | 0.125 | Throttle hover point. Autotune with MOT_HOVER_LEARN=2. |
| MOT_THST_EXPO | 0.0-0.80 | 0.65 | Thrust curve linearization. |
| MOT_SPIN_MIN | 0.05-0.30 | 0.15 | Minimum spin at zero throttle. |
| MOT_SPIN_MAX | 0.85-1.0 | 0.95 | Maximum spin. |
| MOT_HOVER_LEARN | 0-2 | 2 | 0=manual, 1=learn once, 2=learn continuously. |

## Motor / ESC

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| MOT_PWM_TYPE | 0-10 | 6 | 0=PWM, 1=Oneshot125, 6=DSHOT300, 7=DSHOT600, 10=Bidirectional DShot |
| MOT_PWM_MIN | 900-1100 | 1000 | Min PWM signal in us. |
| MOT_PWM_MAX | 1900-2100 | 2000 | Max PWM signal in us. |
| MOT_BOOST_SCALE | 0-1 | 0 | Dynamic throttle boost. Start at 0, raise carefully. |
| SERVO_BLH_BDMASK | 0-15 | 0 | Bitmask of motors with bidirectional DShot. |

## Battery

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| BATT_MONITOR | 0-9 | 4 | 4=Analog voltage + current. |
| BATT_CAPACITY | 300-50000 | 3300 | Battery capacity in mAh. |
| BATT_VOLT_MULT | 1.0-50.0 | 11.1 | Voltage sensor multiplier. Calibrated per board. |
| BATT_AMP_PERVLT | 10-100 | 59.5 | Current sensor scaling. |
| BATT_ARM_VOLT | 3-52 | 22.1 | Voltage at arm time (full battery). |
| BATT_LOW_VOLT | 3-50 | 21.6 | Low battery threshold. |
| BATT_CRT_VOLT | 3-50 | 21.0 | Critical battery threshold. |
| BATT_FS_LOW_ACT | 0-3 | 2 | 0=none, 1=land, 2=RTL, 3=smart RTL |
| BATT_FS_CRT_ACT | 0-3 | 1 | Critical action. Usually land. |

## Arming

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| ARMING_CHECK | 0-1 | 1 | 0=skip all arming checks (not recommended). |
| ARMING_ACCTHRESH | 0.1-1.5 | 0.75 | Accel consistency threshold. |
| ARMING_MAGTHRESH | 50-750 | 100 | Mag field strength variation threshold. |
| ARMING_RUDDER | 0-2 | 2 | 0=disabled, 1=arm on yaw right, 2=arm on yaw + throttle down. |

## GPS

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| GPS_TYPE | 0-9 | 1 | 0=none, 1=auto, 2=u-blox |
| GPS_AUTO_CONFIG | 0-1 | 1 | Auto-configure GPS at boot. |
| GPS_HDOP_GOOD | 100-200 | 140 | HDOP below this is "good." Lower = pickier. |
| GPS_NAVFILTER | 0-8 | 8 | Navigation filter level. 6-8 recommended. |
| EK3_SRC1_POSXY | 0-6 | 3 | 3=GPS (default). |

## Failsafe

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| FS_THR_ENABLE | 0-1 | 1 | Enable radio failsafe. |
| FS_EKF_ACTION | 0-2 | 1 | 0=disabled, 1=RTL, 2=land. |
| FS_EKF_THRESH | 0.1-1.0 | 0.8 | EKF variance threshold before action. |
| FS_CRASH_CHECK | 0-1 | 1 | Auto-disarm on crash detection. |
| FS_OPTIONS | 0-65535 | 0 | Bitmask of advanced failsafe options. |
| RC_FS_TIMEOUT | 0.5-10 | 1 | Seconds of RC loss before failsafe triggers. |

## Misc

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| SCHED_LOOP_RATE | 100-800 | 400 | Main control loop rate (Hz). 400-800 for modern FCs. |
| FRAME_CLASS | 0-3 | 1 | 0=unknown, 1=quad, 2=hexa, 3=octo |
| FRAME_TYPE | 0-2 | 1 | 0=plus, 1=X, 2=V-tail |
| LOG_BITMASK | 0-4095 | 958 | Which data to log. Default includes IMU, RC, GPS, etc. |
| THR_DZ | 0-200 | 100 | Throttle deadzone in us. |
| RC_SPEED | 100-500 | 490 | RC input speed in Hz. Higher = faster response. |
```

- [ ] **Step 2: Write common-issues.md**

```markdown
# Common Issues — Symptom → Cause → Fix

## 1. Oscillations at Hover

**Symptom:** Quad shakes/wobbles while hovering. Gets worse with throttle.

**Causes (check in order):**
1. **D term too high** — ATC_RAT_RLL_D or ATC_RAT_PIT_D too high for this frame
   → Reduce D by 20%, re-test
2. **Gains in general too high** — Reduce P gain(s) by 20%
3. **Notch filter wrong** — INS_HNTCH_FREQ doesn't match motor RPM
   → Try adjusting HNTCH_FREQ up/down by 20 Hz
4. **Bad props** — Unbalanced or damaged
   → Balance or replace props
5. **Frame resonance** — Loose arm bolts, cracked frame
   → Inspect and tighten frame hardware

## 2. Oscillations on Throttle Punch

**Symptom:** Quad wobbles violently when you punch the throttle.

**Causes:**
1. **Low D gain** allows oscillation to build
   → Raise ATC_RAT_RLL_D and ATC_RAT_PIT_D by 20%
2. **Filter too aggressive** (blocking feedback)
   → Check INS_GYRO_FILTER, reduce if > 80 Hz
3. **Thrust linearity** — MOT_THST_EXPO needs adjusting
   → Try 0.55-0.65 range

## 3. Toilet-Bowling (Slow Spiral)

**Symptom:** Quad slowly circles like a toilet bowl. Usually in Loiter.

**Causes:**
1. **Compass interference** — most common cause
   → Check COMPASS_OFS values. Re-calibrate. Move GPS/compass.
2. **GPS glitching** — bad lock or multi-path
   → Check GPS_HDOP. Improve antenna placement.
3. **Compass learn off** — EK3_MAG_CAL=3 enables in-flight learning

## 4. Yaw Twitch

**Symptom:** Quad jerks/slides on yaw input.

**Causes:**
1. **Yaw P too high** — ATC_RAT_YAW_P > 0.30
   → Reduce by 20%
2. **Yaw I too high** — ATC_RAT_YAW_I > 0.10
   → Reduce by 20%
3. **Motor orientation** — One motor reversed or wrong direction
   → Verify motor spin directions

## 5. Hot Motors After Tuning

**Symptom:** Motors hot to the touch after a flight.

**Causes:**
1. **D gain too high** — most common cause
   → Reduce ATC_RAT_*_D by 30%
2. **Filter too low** — INS_GYRO_FILTER < 40 Hz
   → Raise gyro filter
3. **Notch tracking wrong** — INS_HNTCH_FREQ or mode incorrect
   → Check dynamic notch (MODE=3) is enabled
4. **Over-propped** — Props are too large for the motors
   → Check motor/prop specs

## 6. Altitude Drift / Hold Issues

**Symptom:** Quad doesn't hold altitude well in AltHold or Loiter.

**Causes:**
1. **Baro not covered** — Wind/camera light affects barometer
   → Ensure baro (if any) is covered with foam
2. **Low PSC_ACCZ_P** — Throttle P too low
   → Raise PSC_ACCZ_P from 0.4 to 0.6
3. **Prop wash** — In tight descents, quad can't hold
   → Descend at angle, not straight down

## 7. Quad Won't Arm

**Symptom:** Motors don't spin when arming.

**Causes (check in order):**
1. **Arming checks failing** — ARMING_CHECK=1, GCS shows pre-arm failure
   → Check GCS for specific pre-arm message
2. **ARMING_RUDDER=2** — need throttle down + yaw right
   → Verify stick positions (throttle bottom right)
3. **RC3_TRIM not at min** — Throttle not detected as zero
   → Check RC3_MIN, RC3_TRIM values
4. **Battery voltage** — BATT_ARM_VOLT reading wrong
   → Check battery monitor settings

## 8. GPS Won't Get Fix

**Symptom:** GPS icon flashing, no 3D fix.

**Causes:**
1. **GPS_TYPE wrong** — Should be 1 (auto-detect) for most
2. **GPS in cold start** — First boot after long distance move can take 15 min
   → Wait. Ensure clear sky view.
3. **VTX interference** — VTX harmonics interfering with GPS
   → Move VTX antenna further from GPS
4. **GPS antenna blocked** — Carbon fiber above antenna
   → Mount GPS on mast

## 9. Failsafe False Triggers

**Symptom:** RTL or land triggers unexpectedly.

**Causes:**
1. **Battery threshold too sensitive** — BATT_LOW_VOLT set too high
   → Check actual battery voltage behavior in flight
2. **Radio signal** — FS_THR_VALUE too close to RC3_MIN
   → Reduce FS_THR_VALUE by 50
3. **EKF glitch** — Temporary EKF variance spike
   → Check FS_EKF_THRESH, EKF logs

## 10. Drift (Quad slowly moves in one direction)

**Symptom:** In Stabilize or Loiter, quad drifts in one direction.

**Causes:**
1. **ACCEL needs calibration** — AHRS_TRIM_X/Y show offset
   → Calibrate accelerometer (level surface required)
2. **CG offset** — Battery or camera weight not centered
   → Balance the load
3. **GPS position offset in Loiter** — EK3_SRC1 issues
   → Check compass calibration, GPS placement
```

- [ ] **Step 3: Commit**

```bash
git add arducopter-troubleshooter/references/parameter-reference.md arducopter-troubleshooter/references/common-issues.md
git commit -m "feat: add parameter reference and common issues lookup docs"
```

---

## Self-Review Checklist

1. **Spec coverage:** Every section of the spec has a corresponding task — SKILL.md (Task 1), scripts (Task 2), each reference doc group (Tasks 3-5).
2. **Placeholder scan:** All code blocks contain actual code. No "TBD", "TODO", or "implement later" patterns.
3. **Type consistency:** The param names in analyze_params.py match the regex patterns in parse_params.py. The diagnostic trees in SKILL.md reference the same param names. The reference docs cover the diagnostic paths listed in SKILL.md.
4. **Test fixture:** The provided `skystarh7.param` serves as the end-to-end test case for the parsing pipeline.

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-11-arducopter-troubleshooter.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using subagent-driven-development, batch execution with checkpoints.

**Which approach do you prefer?**
