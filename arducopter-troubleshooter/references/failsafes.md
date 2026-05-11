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
