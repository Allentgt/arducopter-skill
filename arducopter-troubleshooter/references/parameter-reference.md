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
