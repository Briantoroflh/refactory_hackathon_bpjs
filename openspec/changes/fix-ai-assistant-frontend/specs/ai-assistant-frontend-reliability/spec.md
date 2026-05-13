## ADDED Requirements

### Requirement: AI Assistant request MUST be structurally valid
Sistem frontend AI Assistant MUST mengirim request ke backend dengan payload valid yang mencakup prompt non-empty, metadata minimal, dan header autentikasi saat token tersedia.

#### Scenario: Valid prompt is submitted
- **GIVEN** user berada di halaman AI Assistant dan telah mengisi prompt valid
- **WHEN** user menekan submit
- **THEN** frontend mengirim request dengan payload yang tervalidasi dan struktur field sesuai kontrak API

#### Scenario: Empty prompt is blocked
- **GIVEN** input prompt kosong atau hanya whitespace
- **WHEN** user menekan submit
- **THEN** frontend MUST membatalkan request dan menampilkan pesan validasi tanpa memanggil endpoint backend

### Requirement: AI Assistant response MUST be normalized for UI rendering
Sistem frontend MUST memetakan response backend AI menjadi format internal yang konsisten sehingga komponen UI tidak bergantung pada variasi bentuk response mentah.

#### Scenario: Successful backend response
- **GIVEN** backend mengembalikan response sukses dengan envelope data
- **WHEN** frontend menerima response
- **THEN** frontend MUST menormalisasi response ke model UI tunggal sebelum dirender

#### Scenario: Partial optional fields in response
- **GIVEN** backend mengembalikan response sukses dengan field opsional yang tidak lengkap
- **WHEN** frontend melakukan normalisasi
- **THEN** frontend MUST menyediakan default value aman agar UI tetap stabil

### Requirement: AI Assistant MUST provide deterministic error handling by status class
Sistem frontend MUST memetakan kegagalan request AI berdasarkan kategori error agar user mendapat pesan dan aksi pemulihan yang tepat.

#### Scenario: Unauthorized request
- **GIVEN** backend mengembalikan status 401
- **WHEN** frontend memproses error
- **THEN** frontend MUST menampilkan instruksi re-authentication dan tidak melakukan retry otomatis

#### Scenario: Validation failure request
- **GIVEN** backend mengembalikan status 422
- **WHEN** frontend memproses error
- **THEN** frontend MUST menampilkan pesan perbaikan input dan tidak melakukan retry otomatis

#### Scenario: Transient server failure
- **GIVEN** backend mengembalikan status 5xx atau request timeout
- **WHEN** frontend memproses error
- **THEN** frontend MUST menjalankan retry terbatas sesuai kebijakan dan menampilkan error final jika retry gagal

### Requirement: AI Assistant MUST emit sanitized telemetry events
Sistem frontend MUST menghasilkan event telemetry minimal untuk lifecycle request AI tanpa menyimpan konten sensitif mentah.

#### Scenario: Request lifecycle telemetry
- **GIVEN** request AI dilakukan
- **WHEN** request bertransisi submit, success, fail, timeout, atau retry
- **THEN** frontend MUST mengirim event telemetry dengan metadata non-PII dan masking konten prompt