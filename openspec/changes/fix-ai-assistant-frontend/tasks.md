## 1. API Contract & Data Normalization

- [x] 1.1 Audit kontrak endpoint AI yang dipakai frontend (request body, envelope response, error shape).
- [x] 1.2 Implement adapter/mapper response AI ke model UI tunggal di layer frontend API.
- [x] 1.3 Tambahkan default value aman untuk field opsional agar rendering tidak crash.

## 2. Request Validation & Auth Handling

- [x] 2.1 Tambahkan validasi input prompt (trim, empty check, batas panjang) sebelum submit.
- [x] 2.2 Pastikan request AI menggunakan API client yang selalu menyertakan Authorization header saat token ada.
- [x] 2.3 Blokir double-submit dengan in-flight guard pada state form/chat input.

## 3. Reliability Controls (Timeout, Retry, Abort)

- [x] 3.1 Tambahkan timeout request AI menggunakan abortable request pattern.
- [x] 3.2 Implement retry terbatas (max 1-2) hanya untuk network error/5xx.
- [x] 3.3 Nonaktifkan retry untuk 401/422 dan tampilkan feedback yang sesuai.

## 4. UI Error Mapping & User Feedback

- [x] 4.1 Buat error mapping terstruktur untuk 401, 422, 5xx, timeout, dan unknown error.
- [x] 4.2 Perbarui komponen AI page agar menampilkan pesan yang actionable (re-login, perbaiki input, coba lagi).
- [x] 4.3 Pastikan loading/success/error state konsisten pada setiap turn chat.

## 5. Telemetry, Security, and Privacy

- [x] 5.1 Tambahkan telemetry event minimal (submit, success, fail, timeout, retry).
- [x] 5.2 Terapkan sanitasi telemetry: masking prompt content dan hindari logging PII mentah.
- [x] 5.3 Validasi bahwa data sensitif tidak muncul di log client atau error toast.

## 6. Testing & Rollout

- [x] 6.1 Tambahkan/ubah unit test untuk validation, response mapping, dan error mapper.
- [x] 6.2 Tambahkan integration test alur AI page untuk skenario sukses, 401, 422, dan 5xx.
- [x] 6.3 Verifikasi fallback/rollback guard tersedia untuk kembali ke alur lama jika terjadi regresi.
- [x] 6.4 Jalankan lint/test frontend dan dokumentasikan hasil verifikasi implementasi.