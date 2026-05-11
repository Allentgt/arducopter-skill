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
