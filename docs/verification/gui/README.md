# Google Chrome GUI demonstration

Actual visible Google Chrome 153 was opened on the desktop using a temporary profile. The tour exercised the website through GUI controls; slider seeking used Home / ArrowRight / End keyboard input. No personal browser profile was accessed.

Watch `gui_demo.mp4` (67 seconds, H.264, 1440×920) or `gui_demo.webm`. Thai captions describe the steps. The replay records the browser page viewport; the actual Chrome window was visible during the tour. `gui_demo.json` records browser version, frame/data assertions, final values, and successful checks.

Steps shown:

1. GOA / Sphere, 30 agents, 100 iterations, seed 424242.
2. Run Algorithm: fitness, contour and convergence.
3. Animation from iteration 0: current agents, known optimum and archive.
4. Play then Pause, confirming the frame stays unchanged.
5. Seek to 50 and 100 using the actual slider's keyboard controls; validate fitness and marker coordinates.
6. Switch to Rosenbrock and play through iteration 100.
7. Compare All on Sphere: three algorithm results and convergence curves for a single seed.

The normal Chrome window is left open at the Rosenbrock animation, paused at initialization, for hands-on interaction. Reloading the page removes demonstration-only captions/zoom; the normal window never receives them.

Repeat while the app runs on port 8091:

```bash
.venv/bin/python scripts/gui_demo.py
```

If a previous demonstration Chrome is still using debugging port 9333, choose another port: `--debug-port 9334`. The GUI tour takes about a minute. A graphical desktop session and Google Chrome are required; this is separate from the headless six-combination audit in `scripts/browser_check.py`.
