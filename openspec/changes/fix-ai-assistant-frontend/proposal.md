## Why

AI Assistant page di frontend saat ini belum konsisten menghasilkan jawaban yang benar dan berkualitas, serta mengalami kegagalan alur request/response pada kondisi autentikasi, validasi payload, dan error handling. Perbaikan dibutuhkan sekarang karena fitur AI Assistant adalah entry point utama untuk insight operasional tim engineering.

## What Changes

- Menstandarkan kontrak request/response antara frontend AI Assistant dan backend endpoint AI (format prompt, metadata, dan envelope response).
- Memperbaiki alur fetch di halaman AI Assistant agar selalu mengirim payload yang valid, termasuk context yang dibutuhkan backend.
- Menambahkan fallback handling untuk status error umum (401, 422, 5xx) dengan pesan yang jelas di UI.
- Menjamin token autentikasi dikirim konsisten melalui API client yang dipakai AI Assistant.
- Menambahkan validasi input prompt di frontend (empty prompt, panjang minimal/maksimal, dan state submit).
- Menambahkan mekanisme retry terbatas dan timeout untuk request AI agar UX lebih stabil.
- Menambahkan telemetry/logging frontend minimum untuk membantu diagnosis kegagalan AI response.
- Menyesuaikan pengujian unit/integrasi agar memverifikasi alur response normal dan error.
- Menyediakan rollback plan: fallback ke alur response sebelumnya melalui feature flag/guard sederhana jika integrasi baru menimbulkan regresi.
- Data migration strategy: tidak ada perubahan skema database; perubahan berfokus pada kontrak API dan perilaku UI.

## Capabilities

### New Capabilities
- `ai-assistant-frontend-reliability`: memastikan AI Assistant frontend mengirim request valid, memproses response konsisten, dan menampilkan error secara terarah.

### Modified Capabilities
- `spec`: memperluas requirement existing spec terkait reliability dan kualitas output AI Assistant pada alur frontend-to-backend.

## Impact

- Affected code (frontend): halaman AI Assistant, layer API client AI, tipe data AI, komponen chat/input/loading/error state.
- Affected code (backend surface): kontrak endpoint AI yang dikonsumsi frontend (tanpa migrasi database).
- Affected APIs: endpoint AI Assistant request/response envelope, auth header usage, dan error mapping.
- Affected teams: frontend engineers, backend engineers, QA.
- Affected user roles: admin, team lead, dan user engineering yang menggunakan AI Assistant.
- Dependencies: tidak menambah dependency wajib, opsional util ringan untuk timeout/retry jika belum tersedia.
- Data privacy/compliance: sanitasi prompt log (masking data sensitif), pembatasan logging konten mentah, dan kepatuhan prinsip minimal data retention untuk telemetry.