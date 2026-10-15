---
title: 'Modular Architecture Strategy'
status: accepted
date: 2025-09-30
decision-makers: [Elham Syahrian Putra]
consulted: [N/A]
informed: [N/A]
---

# Context and Problem Statement

Seiring dengan bertambahnya fitur pada sebuah aplikasi, struktur kode dapat menjadi semakin kompleks dan sulit untuk dikelola. Tanpa organisasi yang jelas, semua _controller_, _service_, dan komponen lainnya akan tercampur dalam satu lingkup global, yang dapat menyebabkan masalah ketergantungan (coupling) yang erat dan kesulitan dalam pemeliharaan.

Diperlukan sebuah strategi arsitektur untuk mengorganisir kode secara logis.

1.  **Struktur Monolitik**: Menempatkan semua _provider_ (services) dan _controller_ di dalam satu modul utama (`AppModule`).
2.  **Arsitektur Modular (Fitur)**: Memecah aplikasi menjadi beberapa modul yang lebih kecil, di mana setiap modul bertanggung jawab atas satu fitur atau domain bisnis tertentu (misalnya, `Labs`, `Auth`, `Reservations`).

# Decision Drivers

- **Skalabilitas**: Arsitektur harus memudahkan penambahan fitur baru di masa depan tanpa mengganggu fungsionalitas yang sudah ada.
- **Pemeliharaan (Maintainability)**: Kode harus mudah ditemukan, dipahami, dan dimodifikasi. Perubahan pada satu fitur seharusnya memiliki dampak minimal pada fitur lainnya.
- **Pemisahan Tanggung Jawab (Separation of Concerns)**: Setiap bagian dari aplikasi harus memiliki tanggung jawab yang jelas dan terdefinisi dengan baik.
- **Enkapsulasi**: Setiap modul harus dapat menyembunyikan detail implementasinya dan hanya mengekspos apa yang perlu diketahui oleh modul lain melalui antarmuka publik (`exports`).

# Considered Options

- Opsi A - Menggunakan satu `AppModule` untuk keseluruhan aplikasi (Struktur Monolitik).
- Opsi B - Mengadopsi arsitektur berbasis modul per fitur.

# Decision Outcome

**Chosen option: Opsi B (Arsitektur berbasis modul per fitur)**.

Berdasarkan struktur proyek, terlihat jelas bahwa aplikasi ini dibagi menjadi beberapa modul fitur. Berkas `src/app.module.ts` mengimpor modul-modul lain seperti `LabsModule`, `AuthModule`, `ReservationsModule`, dan lainnya. Setiap modul ini (contohnya `src/labs/labs.module.ts`) memiliki `controller` dan `service`-nya sendiri, yang menunjukkan adanya pengelompokan berdasarkan domain bisnis.

### Consequences

**Kelebihan**

- **Organisasi yang Jelas**: Kode menjadi lebih mudah dinavigasi karena semua file yang terkait dengan satu fitur (misalnya, _labs_) berada di dalam direktori yang sama.
- **Enkapsulasi Kuat**: Modul dapat memilih untuk tidak mengekspor _service_ tertentu, menjadikannya privat hanya untuk modul tersebut. Contohnya, `ReservationsModule` mengimpor `LabsModule` untuk menggunakan `LabsService`, yang secara eksplisit diekspor oleh `LabsModule`.
- **Lazy Loading**: Untuk aplikasi yang lebih besar, NestJS mendukung _lazy loading_ modul, yang dapat mempercepat waktu startup aplikasi.
- **Memudahkan Kolaborasi**: Tim yang berbeda dapat bekerja pada modul yang berbeda secara paralel dengan risiko konflik yang lebih kecil.

**Kekurangan**

- **Konfigurasi Awal yang Lebih Rumit**: Memerlukan pembuatan file modul untuk setiap fitur baru dan mengimpornya ke modul utama.
- **Manajemen Ketergantungan**: Perlu pengelolaan yang cermat terhadap dependensi antar modul (misalnya, apa yang diimpor dan diekspor oleh setiap modul) untuk menghindari _circular dependencies_.

# Pros and Cons of the Options

### Opsi A - Struktur Monolitik

**Kelebihan**

- Sangat sederhana untuk proyek kecil atau prototipe.
- Tidak perlu memikirkan struktur modul dan dependensi di awal.

**Kekurangan**

- Menjadi sangat sulit dikelola seiring pertumbuhan aplikasi.
- Semua _provider_ berada dalam _scope_ global, yang dapat menyebabkan konflik nama dan kesulitan dalam melacak dependensi.

### Opsi B - Arsitektur Modular

**Kelebihan**

- Sangat skalabel dan mudah dipelihara untuk aplikasi skala menengah hingga besar.
- Mendorong pemisahan tanggung jawab yang jelas.
- Meningkatkan keterbacaan dan organisasi kode.

**Kekurangan**

- Sedikit _overhead_ dalam pembuatan file dan konfigurasi untuk setiap fitur baru.
