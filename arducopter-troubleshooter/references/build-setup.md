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
