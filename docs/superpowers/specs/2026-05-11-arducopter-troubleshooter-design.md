# ArduCopter Troubleshooter Skill — Design Spec

> **Goal:** An OpenCode skill that turns the AI into an ArduCopter diagnostic assistant for building, tuning, flying, and troubleshooting quadcopters.

**Architecture:** Hybrid skill with bundled reference docs for common issues + param file analysis scripts + live web fetch fallback for edge cases. The skill itself is a Markdown workflow engine (`SKILL.md`) with structured diagnostic trees, and the analysis is offloaded to deterministic Python scripts for reliability.

**Tech Stack:** OpenCode skill system (SKILL.md + references/ + scripts/), Python 3 for param parsing/analysis, web fetch for live docs.

---

## 1. Overview

The skill covers the full lifecycle of an ArduCopter quad:

- **Building** — frame selection, motor/prop matching, FC wiring, GPS mounting, power distribution
- **Tuning** — PID tuning, filter setup, notch filtering, autotune guidance
- **Flying** — flight mode selection, preflight checks, first flight procedures
- **Troubleshooting** — oscillations, EKF errors, failsafes, GPS problems, motor/ESC issues, bad flight behavior

The core interaction is a guided diagnostic workflow: user describes a problem → skill collects context → skill analyzes params (if provided) → skill traverses a diagnostic tree → skill recommends a fix → skill optionally fetches fresh wiki/forum content for edge cases.

## 2. File Structure

```
arducopter-troubleshooter/
├── SKILL.md                        # Main skill: triggers, workflow engine, diagnostic trees
├── references/
│   ├── pid-tuning.md               # PID theory, tuning steps, filter interactions, notch setup
│   ├── ekf-diagnostics.md          # EKF status codes, variance causes, mag interference
│   ├── failsafes.md                # Battery, radio, GCS, EKF failsafe scenarios
│   ├── motor-esc.md                # Motor numbering, ESC protocols, DShot, BLHeli, calibration
│   ├── flight-modes.md             # Mode descriptions, when to use what
│   ├── parameter-reference.md      # Key params with safe ranges & effects
│   ├── common-issues.md            # Symptom → cause → fix lookup table
│   └── build-setup.md              # Frame, motor/prop, wiring, GPS, power setup guides
└── scripts/
    ├── parse_params.py             # Read .param file → structured JSON by subsystem
    └── analyze_params.py           # Check parsed params against known-safe ranges
```

## 3. Diagnostic Workflows

Each session follows the same structure:

### Phase 1: Intake
Skill captures from the user:
- Frame type & size, weight, motors, props, FC model, firmware version
- What behavior is wrong (oscillations, drift, failsafe trigger, EKF warning, GPS issues, etc.)
- When does it happen (hover, throttle punch, turns, descent)
- Recent changes (new props, firmware update, crash repair, etc.)

### Phase 2: Param Analysis
Skill asks the user to share their `.param` file. If provided:
1. `parse_params.py` extracts structured data grouped by subsystem
2. `analyze_params.py` checks values against known-good ranges
3. Results are fed into the diagnostic tree for precise matching

### Phase 3: Traversal
Skill matches the symptom + param context against diagnostic trees:
- **Oscillations** — PIDs too high, D term noise, notch filter misconfigured, mechanical resonance, prop balance
- **EKF errors** — compass interference, GPS glitching, bad mag cal, vibration affecting EKF, IMU temperature
- **Failsafes** — battery low voltage/high current, radio signal loss (FS_THR_VALUE), GCS heartbeat timeout
- **Bad flight** — drift (trim/ACCEL cal), toilet-bowling (mag), altitude hold issues (baro), yaw issues
- **GPS problems** — poor HDOP, low satellite count, antenna placement, GPS type incompatibility
- **Motor/ESC** — desync (DShot vs PWM), hot motors (timing), uneven thrust (ESC cal)

### Phase 4: Recommendation
Skill provides:
- Specific parameter changes with values and reasoning
- Hardware checks (balance props, tighten frame, check wiring, re-mount GPS)
- Re-test instructions ("arm and hover at 2m, check for oscillations")
- Links to relevant wiki pages if fetched

### Phase 5: Web Fallback
If no diagnostic tree matches cleanly:
1. Search `ardupilot.org/copter/docs/` for keywords
2. Search `discuss.ardupilot.org` for recent forum threads
3. Present findings with source URLs

## 4. Param File Parser

**Input format** — ArduPilot `.param` file (CSV):
```
PARAM_NAME,value
ATC_RAT_RLL_P,0.135
BATT_CAPACITY,3300
...
```

**Output** — `parse_params.py` outputs structured JSON grouped by subsystem:

| Group | Params |
|-------|--------|
| pid_roll | ATC_RAT_RLL_P, ATC_RAT_RLL_I, ATC_RAT_RLL_D, ATC_RAT_RLL_FLTD, ATC_RAT_RLL_FLTE, ATC_RAT_RLL_FLTT |
| pid_pitch | ATC_RAT_PIT_P, ATC_RAT_PIT_I, ATC_RAT_PIT_D, ATC_RAT_PIT_FLTD, ATC_RAT_PIT_FLTE, ATC_RAT_PIT_FLTT |
| pid_yaw | ATC_RAT_YAW_P, ATC_RAT_YAW_I, ATC_RAT_YAW_D, ATC_RAT_YAW_FLTD, ATC_RAT_YAW_FLTE, ATC_RAT_YAW_FLTT |
| angle | ATC_ANG_RLL_P, ATC_ANG_PIT_P, ATC_ANG_YAW_P, ATC_ANGLE_BOOST |
| throttle | MOT_THST_HOVER, MOT_THST_EXPO, MOT_SPIN_MIN, MOT_SPIN_MAX, MOT_HOVER_LEARN, THR_DZ |
| battery | BATT_CAPACITY, BATT_ARM_VOLT, BATT_LOW_VOLT, BATT_CRT_VOLT, BATT_MONITOR, BATT_VOLT_MULT |
| motor_esc | MOT_PWM_TYPE, MOT_PWM_MIN, MOT_PWM_MAX, MOT_BOOST_SCALE, SERVO_BLH_MASK, SERVO_BLH_BDMASK |
| filter | INS_HNTCH_ENABLE, INS_HNTCH_FREQ, INS_HNTCH_MODE, INS_HNTCH_HMNCS, INS_GYRO_FILTER, INS_ACCEL_FILTER |
| ekf | EK3_ENABLE, EK3_MAG_CAL, EK3_SRC1_POSXY, EK3_SRC1_YAW, EK3_ERR_THRESH |
| gps | GPS_TYPE, GPS_AUTO_CONFIG, GPS_HDOP_GOOD, GPS_NAVFILTER, GPS1_TYPE |
| frame | FRAME_CLASS, FRAME_TYPE |
| arming | ARMING_CHECK, ARMING_RUDDER, ARMING_MAGTHRESH, ARMING_ACCTHRESH |
| failsafe | FS_EKF_ACTION, FS_THR_ENABLE, FS_THR_VALUE, FS_DR_ENABLE, FS_CRASH_CHECK, BATT_FS_LOW_ACT, BATT_FS_CRT_ACT |
| rc | RC1_TRIM, RC1_MIN, RC1_MAX, RC1_REVERSED, RC1_DZ, RCMAP_ROLL, RCMAP_PITCH, RCMAP_THROTTLE, RCMAP_YAW |
| logging | LOG_BITMASK, LOG_FILE_BUFSIZE, LOG_BACKEND_TYPE |
| osd | OSD1_ENABLE, OSD1_FONT, OSD1_* screen element positions |
| loop | SCHED_LOOP_RATE |

**Analysis** — `analyze_params.py` flags suspicious values:
- PID gains outside typical ranges for the frame class (e.g., ATC_RAT_RLL_P > 0.3 for a 5" quad)
- Inconsistent battery config (BATT_VOLT_MULT doesn't match cell count)
- Filter settings that contradict each other (notch freq but notch disabled)
- MOT_SPIN_MIN too low (motors may not start reliably)
- MOT_THST_HOVER unrealistic for the build
- HNTCH_FREQ mismatched to motor/prop combo
- Arming check values that may prevent arming
- Failsafe actions that differ from typical recommendations

## 5. Reference Docs Content Summary

Each reference doc is a focused Markdown file (~100-300 lines):

| Doc | Key Sections |
|-----|-------------|
| `pid-tuning.md` | PID theory, roll/pitch/yaw tuning procedure, D term & filter relationship, autotune guide, notch filter setup, feedforward tuning, rate vs angle mode tuning |
| `ekf-diagnostics.md` | EKF3 status display, variance types and causes, compass interference sources, GPS vs optical flow fusion, mag calibration procedure, common EKF warning messages |
| `failsafes.md` | Battery failsafe (low/critical thresholds), radio failsafe (FS_THR_VALUE setup), GCS failsafe, EKF failsafe, crash check, dead reckoning, how to test each |
| `motor-esc.md` | Motor numbering (quad X, quad +), DShot vs PWM vs Oneshot, BLHeli settings, ESC calibration, motor test procedure, desync troubleshooting |
| `flight-modes.md` | Stabilize, AltHold, Loiter, PosHold, RTL, Auto, Sport, Acro, Drift — behavior and use cases |
| `parameter-reference.md` | 50+ key params organized by category with safe ranges, default values, and tuning notes |
| `common-issues.md` | 15+ symptom → cause → fix entries: oscillations, toilet-bowl, yaw twitch, hot motors, altitude drift, GPS glitching, EKF warnings, failsafe triggers |
| `build-setup.md` | Frame selection, motor/prop matching charts, FC mounting orientation, GPS antenna placement, power distribution wiring, vibration isolation |

## 6. Web Fetch Fallback

Triggered when:
- User asks about a firmware version-specific feature (4.5, 4.6, etc.)
- Diagnostic trees have no match for the symptom
- User requests the latest documentation on a specific topic
- The issue involves recently reported bugs or changes

Fetch targets:
- `ardupilot.org/copter/docs/` — official docs
- `ardupilot.org/copter/docs/common-parameter-configuration.html` — param docs
- `discuss.ardupilot.org` — community forum threads
- `github.com/ArduPilot/ardupilot/issues` — known bugs and PRs

## 7. Skill Description & Triggering

**Name:** `arducopter-troubleshooter`

**Description (frontmatter):** 
An interactive troubleshooting skill for ArduCopter quadcopters. Use this skill whenever the user mentions ArduCopter, ArduPilot, multi-rotor, quadcopter, or quad build help — including PID tuning, EKF errors, GPS problems, failsafes, oscillation/drift troubleshooting, motor/ESC issues, flight mode selection, battery configuration, pre-flight checks, param file analysis, or any build/setup/flying issue with an ArduCopter-based quad. Trigger even if the user only mentions "quad" or "drone" with technical symptoms. Do NOT trigger for general drone photography, non-ArduPilot flight controllers (Betaflight, iNav, PX4), or non-quad ArduPilot vehicles (planes, rovers, boats).

## 8. Key Design Principles

- **Progressive disclosure:** SKILL.md stays lean (~200 lines) — reference docs are loaded only when needed by diagnostic path
- **Deterministic analysis:** Param parsing and analysis are Python scripts, not AI prompts — precise and repeatable
- **Human-in-the-loop:** Skill asks clarifying questions, doesn't jump to conclusions
- **Offline-first:** Bundled refs cover 90%+ of common issues; web is fallback only
- **YAGNI:** One diagnostic tree per major symptom category — add more based on real usage

---

## Appendix: Example Session

**User:** "My quad oscillates at hover, especially after I put on new props."

**Skill flow:**
1. Asks: frame size? FC? firmware version?
2. Asks: share your .param file?
3. User uploads param → analyzes → flags ATC_RAT_RLL_P=0.135 typical but MOT_THST_HOVER=0.125 low
4. Matches "oscillation after new props" → diagnostic suggests prop balance, check if props are same size/pitch as before
5. User confirms new props are same spec → next: check PIDs with filters
6. Skill checks: INS_GYRO_FILTER=40, INS_HNTCH_ENABLE=1 at 80Hz — looks reasonable
7. Recommends: reduce ATC_RAT_RLL_P from 0.135 to 0.110, re-test. Also balance props.
8. If still issues: fetch latest wiki on DShot + filter interaction for 400Hz loop rate
