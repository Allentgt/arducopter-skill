# ArduCopter Troubleshooter

An interactive diagnostic assistant for ArduCopter quadcopters — covering building, tuning, flying, and troubleshooting with a guided 5-phase workflow.

This is an **[OpenCode](https://github.com/opencode-ai) skill** that auto-triggers when you describe technical ArduCopter quad problems. It combines bundled reference documentation, deterministic `.param` file analysis, and live web fetch fallback for edge cases.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/Allentgt/arducopter-skill.git
cd arducopter-skill

# Test the param analysis scripts against the included fixture
python arducopter-troubleshooter/scripts/parse_params.py sample-config.param
python arducopter-troubleshooter/scripts/analyze_params.py parsed_params.json
```

To use as an OpenCode skill, install it to `~/.config/opencode/skills/arducopter-troubleshooter/` — OpenCode auto-discovers skills on startup.

## Features

### Guided Diagnostic Workflow

| Phase | What happens |
|-------|-------------|
| **1. Intake** | Skill asks about your build, symptom, recent changes, and asks for your `.param` file |
| **2. Param Analysis** | Python scripts parse and flag suspicious parameter values |
| **3. Diagnostic Tree** | Symptom + param context matched against 6 major categories |
| **4. Recommendation** | Specific param changes, hardware checks, and re-test instructions |
| **5. Web Fallback** | Fetch fresh content from ArduPilot wiki, forums, or GitHub issues |

### Coverage Areas

- **PID Tuning** — Roll/pitch/yaw gains, D term noise, notch filter setup, autotune guidance
- **EKF Diagnostics** — Compass interference, GPS glitching, mag calibration, variance causes
- **Failsafes** — Battery voltage thresholds, radio link loss, GCS heartbeat, EKF failsafe
- **Motor / ESC** — Desync troubleshooting, hot motors, ESC protocol (DShot/PWM), BLHeli config
- **Flight Modes** — Stabilize, AltHold, Loiter, PosHold, RTL, Auto, Sport, Acro, Drift
- **GPS Problems** — No fix, bad HDOP, low satellites, antenna placement, glitching
- **Build Setup** — Frame selection, motor/prop matching, FC wiring, GPS mounting, power distribution
- **Bad Flight Behavior** — Drift, toilet-bowling, altitude hold issues, yaw problems

### Trigger Criteria

The skill activates when you describe technical quadcopter problems related to ArduCopter:

**Triggers on:**
- Oscillations, vibration, or wobble at hover/punchout/descent
- EKF warnings, compass errors, GPS issues
- Failsafe triggers (radio, battery, GCS, EKF)
- Won't arm, pre-arm check failures
- Motor/ESC issues (desync, hot motors, not spinning)
- Flight mode questions (which mode, when to use)
- `.param` file analysis requests
- In-progress build advice
- PID tuning help

**Does NOT trigger on:**
- Purchasing advice ("buy DJI or build?")
- Betaflight, iNav, PX4 questions
- ArduPilot planes, rovers, or boats
- General electronics / soldering questions
- Video editing or post-processing
- Non-technical drone photography

## Project Structure

```
arducopter-troubleshooter/       # OpenCode skill (install to skills dir)
├── SKILL.md                     # Main workflow engine: triggers, diagnostic trees, 5-phase flow
├── references/                  # Bundled reference docs (8 files)
│   ├── pid-tuning.md            # PID theory, tuning procedure, autotune, notch filters
│   ├── ekf-diagnostics.md       # EKF3 status codes, variances, compass interference
│   ├── failsafes.md             # Battery, radio, GCS, EKF failsafe scenarios
│   ├── motor-esc.md             # Motor numbering, DShot/PWM, BLHeli, desync
│   ├── flight-modes.md          # Mode descriptions and use cases
│   ├── parameter-reference.md   # 50+ key params with safe ranges
│   ├── common-issues.md         # 15+ symptom → cause → fix entries
│   └── build-setup.md           # Frame, motor/prop, wiring, GPS mounting
├── scripts/                     # Deterministic analysis tools
│   ├── parse_params.py          # .param file → structured JSON by subsystem
│   └── analyze_params.py        # Check parsed params against known-safe ranges
sample-config.param                  # Sample param config for testing scripts
```

## Scripts Reference

### parse_params.py

Converts an ArduPilot `.param` file into structured JSON grouped by subsystem (PID, battery, filter, EKF, GPS, motor/ESC, throttle, failsafe, RC, arming, logging, OSD, frame, loop rate).

```bash
python arducopter-troubleshooter/scripts/parse_params.py <path/to/param.param>
# Outputs: parsed_params.json
```

Groups analyzed: `pid_roll`, `pid_pitch`, `pid_yaw`, `angle`, `throttle`, `battery`, `motor_esc`, `filter`, `ekf`, `gps`, `frame`, `arming`, `failsafe`, `rc`, `logging`, `osd`, `loop`

### analyze_params.py

Checks parsed parameters against known-safe ranges for ArduCopter quads. Flags:

- PID gains outside typical range for the frame class
- Inconsistent battery config (voltage multiplier doesn't match cell count)
- Filter settings that contradict each other (notch freq but notch disabled)
- `MOT_SPIN_MIN` too low (unreliable motor start)
- `MOT_THST_HOVER` unrealistic for typical builds
- `HNTCH_FREQ` mismatched to motor/prop combo
- Arming check values that may prevent arming
- Failsafe actions that differ from typical recommendation

```bash
python arducopter-troubleshooter/scripts/analyze_params.py parsed_params.json
```

## Test Fixture

The included `sample-config.param` is a real-world param export from a SkyStar H7 flight controller on a 6S X-frame quad running DShot600 at 400Hz loop rate with harmonic notch enabled at 80Hz. Use it to verify scripts are working:

```bash
python arducopter-troubleshooter/scripts/parse_params.py sample-config.param
python arducopter-troubleshooter/scripts/analyze_params.py parsed_params.json
```

Expected output: 1239 parameters parsed, ~3 meaningful flags detected.

## Design Principles

- **Progressive disclosure** — SKILL.md stays lean (~180 lines); reference docs load only when needed by the diagnostic path
- **Deterministic analysis** — Param parsing and analysis are Python scripts, not AI prompts — precise and repeatable
- **Human-in-the-loop** — Skill asks clarifying questions, never jumps to conclusions
- **Offline-first** — Bundled refs cover 90%+ of common issues; web is fallback only
- **Hardware first, software second** — Check physical issues (props, frame, wiring) before suggesting param changes
- **Conservative tuning** — Recommend small changes (10-20%) with re-test in between

## Architecture

```
User describes problem
        │
        ▼
┌─────────────────────┐
│  Phase 1: Intake    │  ◄── Collect build/symptom/context
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Phase 2: Params    │  ◄── parse_params.py + analyze_params.py
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Phase 3: Tree      │  ◄── Match symptom + params to diagnostic tree
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  Phase 4: Recommend │  ◄── Specific changes + hardware checks
└─────────┬───────────┘
          │
     (if no match)
          ▼
┌─────────────────────┐
│  Phase 5: Web Fetch │  ◄── ardupilot.org, discuss.ardupilot.org, GitHub issues
└─────────────────────┘
```

## License

[MIT](LICENSE)
