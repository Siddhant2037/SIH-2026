# TRACE-X plugin layer

Use the common OEMAdapter contract to connect validated open-source parsers without changing the UI.

Recommended flow:
1. Put the third-party parser under a vendor-specific plugin folder or package it as a Python dependency.
2. Wrap its CLI/library in `identify`, `parse_filesystem`, `extract_metadata`, `recover_recordings`, `decode_stream`.
3. Return normalized TRACE-X objects.
4. Store raw parser output as an audit artifact.
5. Hash source images and derived outputs separately.
6. Mark adapters as `VALIDATED`, `DEMO`, or `PLUGIN REQUIRED`.

A Hikvision reference implementation is documented by `akira7799/hikvision-dvr-parser`; it describes Master Sector, HIKBTREE, SQLite metadata, H.264 extraction, cross-reference validation and forensic checks. Another reference is `vishwajitsarnobat/HIKVISION-DVR-Tool`, which documents filesystem parsing, timeline generation and FFmpeg-based H.264-to-MP4 streaming.
