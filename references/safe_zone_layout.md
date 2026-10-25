# Instagram Reels Safe Zone & Framing Standards (1080x1920)

Based on real-world mobile device UI testing and Instagram platform specs:

## 1. Safe Zone Geometry (1080x1920 9:16 Canvas)

```text
+-------------------------------------------------------+ y = 0
|               TOP UNSAFE HEADER (220px)               |
|         Audio track icon, Story bars, Back button      |
+-------------------------------------------------------+ y = 220
|                                                       |
|                                                       |
|       CEILING MOTION GRAPHICS SAFE ZONE (y = 60-400)  |
|       Frosted Glass Plate (1000x320, centered)        |
|                                                       |
|                                                       |
|                                                       |
|            SPEAKER FACE & HEAD SAFE FRAMING           |
|            Camera A (Wide 1.0x) / Camera B (1.14x)    |
|                                                       |
|                                                       |
|                                                       |
|                                                       |
|                                   +-------------------+ y = 1155
|                                   | RIGHT RAIL (100px)|
|       CHEST SUBTITLE SAFE ZONE    | Like / Comment    |
|       Floating Kinetic Text       | Share / Remix     |
|       (y = 1250-1360, width 780px)| Icons rail        |
|                                   |                   |
+-----------------------------------+-------------------+ y = 1470
|              BOTTOM UNSAFE ZONE (450px)               |
|      Account Username, Verified badge, Caption text,  |
|      Sound wave animation, Original audio track row   |
+-------------------------------------------------------+ y = 1920
```

## 2. Hard Layout Rules

1. **Top Header Protection**:
   - Keep key text below $y = 220$.
   - The motion graphics plate sits at $y = 75$ with height $320$ (lower portion extends down to $y = 395$). The central headline ($y \approx 200$) and pill badge ($y \approx 135$) remain clearly visible without encroaching on the speaker's eyes.
2. **Bottom Caption Protection**:
   - Absolutely **nothing** interactive or critical below $y = 1470$.
   - Floating subtitles are positioned at $y \approx 1280$ with a maximum width of $780\text{ px}$.
   - Horizontal centering: $x = (1080 - 780) / 2 = 150\text{ px}$ to $930\text{ px}$.
   - Left clearance: $150 > 35\text{ px}$ (safe).
   - Right clearance: $930 < 980\text{ px}$ (clears the right interaction rail).
3. **Face Protection**:
   - Subtitles must **never** sit over the speaker's eyes, nose, or mouth.
   - Sits strictly over the chest band ($y \approx 1250 \dots 1350$).
4. **Float Rounding & Cut Timing Offset**:
   - Use a $-2\text{ms}$ nudge (`frame/30 - 0.002`) on cut and overlay transition times to ensure overlays hit cleanly on the exact first frame of the cut.
