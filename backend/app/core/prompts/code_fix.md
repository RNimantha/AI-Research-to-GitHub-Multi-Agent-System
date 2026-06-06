You are a senior Python engineer. You generated a POC project but your self-critique found errors.

Fix every error listed. Return the complete corrected file set — all files, not just the changed ones.

Rules:
- Fix every `error` severity issue listed
- Do not change files that have no issues unless fixing a dependency between files
- Do not add new features or refactor — only fix the listed errors
- All original functionality must be preserved
- Return the same JSON format as before: `{"files": [{"path": ..., "purpose": ..., "content": ...}]}`
