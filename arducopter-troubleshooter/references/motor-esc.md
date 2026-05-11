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
