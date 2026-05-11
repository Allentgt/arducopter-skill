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
