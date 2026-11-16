# Animation Catalog: Visual Assets for AI, Finance & Physics Reels

## 1. Physics & Mathematics ("Ivan and the Physicist")

### A. Quantum Wave Function (`quantum_wave`)
- **Visual**: Oscillating sine wave packet enclosed inside a Gaussian probability envelope with interference fringes and glowing wave nodes.
- **Color Accent**: Cyber Cyan (`#00F0FF`) with Deep Violet (`#9D00FF`).
- **Trigger Keywords**: "quantum", "wave", "particle", "probability", "electron", "interference".
- **Screen Placement**: Centered top-third (`x: (W-w)/2`, `y: 220`).

### B. Relativistic Equation Card (`formula_card`)
- **Visual**: Glassmorphism frosted card with glowing mathematical typography ($E=mc^2$, $\hat{H}\psi = E\psi$, $\Delta x \cdot \Delta p \ge \frac{\hbar}{2}$).
- **Color Accent**: Gold / Amber (`#FFCC00`).
- **Trigger Keywords**: "equation", "formula", "einstein", "relativity", "speed of light", "energy".

### C. Atomic Orbital Model (`atom_orbital`)
- **Visual**: Central nucleus surrounded by 3 elliptical orbital rings with revolving electron particles.
- **Color Accent**: Electric Blue & Neon Green.

---

## 2. Artificial Intelligence & Technology

### A. Deep Neural Network Layers (`neural_network`)
- **Visual**: Input layer, hidden dense layers, output layer with synaptic pulses firing across connections.
- **Color Accent**: Neon Mint Green (`#00FFA3`).
- **Trigger Keywords**: "ai", "neural network", "transformer", "model", "deep learning", "weights".

### B. Terminal / Code Callout (`tech_terminal`)
- **Visual**: Dark mode macOS terminal header with syntax-highlighted matrix attention code.
- **Color Accent**: Cyber Cyan (`#00F0FF`).
- **Trigger Keywords**: "code", "algorithm", "tokens", "prompt", "parameters".

---

## 3. Finance & Economics

### A. Exponential Compounding Chart (`growth_chart`)
- **Visual**: 2D coordinate grid with an exponential parabolic growth curve, glowing data points, and rolling `+ROI%` counter.
- **Color Accent**: Neon Green (`#00FFA3`) and Gold (`#FFD700`).
- **Trigger Keywords**: "compound interest", "growth", "returns", "investing", "profit", "wealth".

### B. Candlestick Breakout Chart (`candlestick_chart`)
- **Visual**: Financial green/red candles breaking through resistance line with an ascending breakout arrow.
- **Color Accent**: Bullish Green (`#00E676`) / Bearish Red (`#FF5252`).

---

## 4. Editorial Paper Storytelling Tricks (`paper_objects.py` + `render_reel.py`)

All templates below work generically from `beat_map.json` fields on any future video and pair with either `--speaker-style popout` (3D Pop-Out Speaker Card) or `--speaker-style cutout`:

1. **Hook Typographic Stamp (`semantic_highlights.hook_stamp`)**: Floating uppercase header + accent pill badge above speaker head during State 1 opening hook.
2. **Layered Mechanism Stack (`layered_stack`)**: Full-width tactile warm sand plates sliding in with staggered timing, coral strikethrough (`strike_idx`), active coral highlight (`active_idx`), and optional right callout (`right_badge`).
3. **Archival Highlighted Book/Document Excerpt (`quote_excerpt`)**: Off-white Georgia Serif page (`doc_title`, `quote_lines`, `quote_footer`) with blush-coral `#E8C6BC` highlighter sweeps triggered on spoken `highlights` timestamps.
4. **Horizontal Benchmark Bar Chart (`benchmark_bars`)**: Crisp charcoal `#141412` and coral `#CC5A43` bars compared against a dashed vertical benchmark rule (`bars`, `bench_label`, `bench_ratio`, `title_text`).
5. **Before/After Label-Switch Slider (`label_slider`)**: Thin horizontal rule (`slider_labels: [left, right]`) gliding a pill thumb to the coral active state (`slide_t`), followed by empirical surge bars (`bars_t`).
6. **Full-Canvas 2-Column Analytical Contrast (`two_col_compare`, `layout_mode: "fullscreen"`)**: Speaker steps off canvas for deep contrast: dark charcoal card with sequential terracotta symptom pills (`left_cfg`) paired with a proportional stacked sand/blush column (`right_cfg`).
- **Trigger Keywords**: "stocks", "crypto", "bitcoin", "bull market", "bear market", "breakout".
