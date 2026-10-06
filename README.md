# AI Cricket Injury Risk Dashboard

A standalone, presentation-ready React dashboard for the supplied cricket screening research. The structured-data screening and computer-vision movement-analysis sections are presented separately. Local video selection is included, but live inference is not simulated and requires the trained YOLO weights.

## Run locally

Requirements: Node.js 20 or newer and npm.

```bash
npm install
npm run dev
```

Open the local address printed by Vite (normally `http://localhost:5173`).

## Build and check

```bash
npm run typecheck
npm run build
npm run preview
```

All data shown in the dashboard is local presentation data copied from the project’s verified research outputs. No backend, credentials, installed packages, or model weights are included.
