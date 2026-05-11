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
