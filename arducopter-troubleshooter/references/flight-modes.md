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
