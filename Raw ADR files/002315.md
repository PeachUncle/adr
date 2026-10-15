# 10. Testing Strategy & CI/CD Pipeline

## Status
Accepted

## Date
07/05/2025

## Decider
Team Lead @FranklinJaya2006

## Informed
@chaidenfoanto @feliciawijaya2006

## Context
Dalam pengembangan aplikasi Jobaile, yang dibangun menggunakan Flutter (frontend) dan Laravel 11 (backend), dibutuhkan pendekatan pengujian yang sistematis serta proses build dan deployment yang otomatis. Aplikasi ini melibatkan fitur-fitur penting seperti login, matching ART, kontrak kerja, dan komunikasi API. Maka dari itu, perlu diterapkan strategi pengujian yang mencakup:
- Unit Test untuk menguji logika bisnis secara terisolasi.
- Widget Test untuk menguji tampilan dan interaksi antar komponen UI di Flutter.
- Integration Test untuk memastikan komunikasi antar bagian sistem berjalan dengan benar.

Selain itu, diperlukan CI/CD pipeline agar setiap perubahan kode dapat:
- Diuji secara otomatis,
- Dibuild tanpa campur tangan manual,
- Dan (jika lolos semua pengujian) langsung dideploy ke Google Play / App Store atau server backend.

## Decision
Memilih GitHub Actions sebagai solusi utama untuk CI/CD karena:
- GitHub Actions telah terintegrasi langsung dengan repositori GitHub, sehingga memudahkan setup workflow.
- Mendukung berbagai runner untuk menjalankan script Flutter dan Laravel.
- Banyak tersedia template workflow dari komunitas dan GitHub Marketplace.
- Gratis untuk publik repo dan memiliki kuota gratis yang cukup untuk private repo dalam tahap awal.

## Alternatives
- **GitLab CI**
    - Kelebihan: Terintegrasi erat jika menggunakan GitLab sebagai repo, powerful dan fleksibel.
    - Kekurangan: Tidak praktis jika repositori berada di GitHub.
- **Bitrise**
    - Kelebihan: Khusus dibuat untuk mobile app CI/CD, mendukung Flutter.
    - Kekurangan: Versi gratis sangat terbatas, UI agak kompleks dibanding GitHub Actions.
- **Codemagic**
    - Kelebihan: CI/CD khusus Flutter, mendukung deployment ke Play Store/App Store.
    - Kekurangan: Berbayar untuk fitur lengkap, dan integrasi Laravel kurang optimal.

## Consequences

### Keuntungan
- GitHub Actions memudahkan otomasi testing dan build langsung dari repositori tanpa alat tambahan.
- Pipeline dapat dikustomisasi untuk mencakup unit, widget, dan integration test sesuai kebutuhan proyek.

### Potensi Risiko
- Waktu eksekusi dan kuota pipeline gratis terbatas, terutama jika proyek semakin besar dan private.
- Konfigurasi awal bisa memerlukan waktu untuk menyesuaikan runner Flutter dan Laravel agar berjalan lancar secara bersamaan.

### Mitigasi 
- Optimalkan job agar hanya menjalankan test/build penting dan gunakan cache agar eksekusi lebih cepat.
- Gunakan template workflow dari komunitas dan dokumentasi resmi GitHub Actions untuk setup awal yang efisien.



