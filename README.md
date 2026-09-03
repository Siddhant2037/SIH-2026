# TRACE-X v3 — SIH26150 Presentation Prototype

TRACE-X is a cinematic, presentation-first prototype for **SIH26150: Development of a Multi-Vendor DVR/NVR Forensic Analysis Tool for Standardized Acquisition, Recovery, and Analysis of Surveillance Evidence**.

The SIH problem calls for a vendor-agnostic workflow covering device identification, proprietary filesystem/format parsing, forensic imaging, video/metadata extraction, decoding, deleted-footage recovery, timestamp normalization, MD5/SHA-256 hashing, cross-camera correlation, chain of custody, standardized reporting and AI face/object/motion analytics across OEMs including Dahua, CP Plus, Honeywell, TP-Link, Godrej, Uniview, HIKVISION and Matrix.

## Demo design

The UI is intentionally cinematic rather than a conventional sidebar-heavy SaaS dashboard. The Command Center is the first screen after login and drives a judge-facing narrative:

**Identify → Acquire → Parse → Recover → Analyze → Correlate → Verify → Report**

The video wall uses publicly hosted sample inference videos from Intel's `sample-videos` repository. These include person detection and person/bicycle/car detection samples. They are demonstration media, not DVR evidence and not claimed to be captured from a named OEM recorder.

## Windows run guide

### 1. Requirements

- Node.js 20+ recommended
- Python 3.10+
- FFmpeg in PATH for the backend video pipeline

### 2. Install frontend

```powershell
cd "C:\path\to\tracex"
npm install
```

### 3. Start backend

```powershell
python -m uvicorn app.main:app --reload --app-dir backend --port 8000
```

### 4. Seed demo database

```powershell
python scripts/seed_demo.py
```

### 5. Start frontend

```powershell
npm run dev
```

Open `http://localhost:5173/`.

Demo login values are pre-filled. If the backend authentication endpoint is unavailable, the presentation UI can still enter its local demo mode.

## Presentation route

1. Login / secure boot
2. Command Center
3. Acquisition
4. Device Fabric
5. Recovery Engine
6. Video Laboratory
7. Timeline
8. AI Intelligence
9. Integrity
10. Chain of Custody
11. Reports

## Real evidence

The Acquisition screen accepts local files. When a real file is selected, the browser calculates a real SHA-256 digest using the Web Crypto API before displaying it. The existing FastAPI backend can also register uploaded evidence through `/api/evidence/upload`.

Do not overwrite original evidence. Use copies/images and keep derivatives separate.

## OEM adapter/plugin integration

The UI represents a plugin contract rather than pretending that every OEM is already fully reverse engineered.

Recommended structure:

```text
plugins/
  hikvision/
    adapter.py
  dahua/
    adapter.py
  cpplus/
    adapter.py
  uniview/
    adapter.py
  recovery/
    adapter.py
  decoders/
    adapter.py
```

Each adapter should expose a common interface:

```python
class OEMAdapter:
    def identify(self, source): ...
    def parse_filesystem(self, image): ...
    def extract_metadata(self, image): ...
    def recover_recordings(self, image): ...
    def decode_stream(self, recording): ...
    def generate_report(self, findings): ...
```

### Hikvision example

A useful open-source reference is `akira7799/hikvision-dvr-parser`. Its README documents dynamic Master Sector detection, HIKBTREE parsing, SQLite metadata parsing, H.264 extraction, timestamp resolution, anti-forensics checks and JSON reporting. It accepts raw images such as `.dd`, `.raw`, `.img` and `.bin`. Adapt it behind the `OEMAdapter` interface rather than coupling the frontend directly to its CLI.

Another reference is `vishwajitsarnobat/HIKVISION-DVR-Tool`, which parses Hikvision filesystem structures, builds timelines, handles raw/E01 images and converts recovered H.264 blocks to streamable MP4 through FFmpeg.

### Recovery integration

Keep recovery engines behind:

```python
recover_recordings(image, filters) -> list[RecoveredRecording]
```

Return at minimum:

- recording ID
- channel
- start/end timestamp
- byte offset
- size
- recovery confidence
- allocated/partial/deleted state
- source hash

### Video decoder integration

Normalize proprietary outputs into H.264/H.265/MP4 derivatives for browser review. Never replace the source artifact with a decoded derivative.

### AI integration

The UI accepts a YOLO-compatible adapter. A production implementation can use Ultralytics/ONNX/TensorRT/etc. and return normalized detections:

```json
{
  "timestamp": "2026-08-28T22:14:31+05:30",
  "camera": "CAM-03",
  "class": "person",
  "confidence": 0.982,
  "bbox": [0.24, 0.31, 0.38, 0.67],
  "track_id": "P-014"
}
```

The UI intentionally labels AI output **ADVISORY**. Detection is not treated as proof of identity, intent or guilt.

## SIH26150 coverage

- Device identification — Device Fabric
- Multi-OEM architecture — OEM Adapter Fabric
- Forensic acquisition — Acquisition
- Forensic image workflow — Acquisition / backend
- Proprietary filesystem parsing — plugin contract + adapter layer
- Video and metadata extraction — Evidence / Video Laboratory
- Proprietary decoding — decoder plugin contract
- Deleted/damaged recovery — Recovery Engine
- Timestamp normalization — Timeline
- MD5/SHA-256 — Integrity + real SHA-256 for local uploads
- Cross-camera correlation — Timeline
- Chain of custody — Custody
- Audit logging — existing backend + custody UI
- Standardized reporting — Reports
- Face/object/motion analytics — AI Intelligence

## Important honesty rule

For SIH presentation, label capabilities as **IMPLEMENTED**, **DEMO ADAPTER**, **SIMULATED**, or **PLUGIN REQUIRED**. Do not claim reverse-engineered support for an OEM unless your team has actually validated that parser against evidence.

## Reference projects

- https://github.com/akira7799/hikvision-dvr-parser
- https://github.com/vishwajitsarnobat/HIKVISION-DVR-Tool
- https://github.com/intel-iot-devkit/sample-videos
