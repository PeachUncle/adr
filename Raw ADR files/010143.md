---
title: 'Global Exception Filters and Response Interceptors'
status: accepted
date: 2025-09-30
decision-makers: [Elham Syahrian Putra]
consulted: [N/A]
informed: [N/A]
---

# Context and Problem Statement

Setiap aplikasi API modern memerlukan mekanisme yang konsisten untuk menangani respons yang berhasil dan juga kesalahan (_exceptions_) yang mungkin terjadi. Tanpa pendekatan terpusat, setiap _controller_ atau _service_ harus mengimplementasikan logikanya sendiri, yang dapat menyebabkan duplikasi kode dan respons yang tidak konsisten kepada klien.

Ada beberapa pendekatan yang bisa diambil:

1.  **Penanganan Manual**: Setiap _controller method_ bertanggung jawab untuk memformat respons sukses dan menangani kesalahan menggunakan blok `try...catch`.
2.  **Menggunakan Decorator Kustom**: Membuat _decorator_ khusus untuk setiap kasus yang bisa diterapkan di atas _controller method_.
3.  **Menggunakan NestJS Global Features**: Memanfaatkan fitur bawaan NestJS seperti `GlobalFilters` untuk menangani _exception_ dan `GlobalInterceptors` untuk memformat respons secara global.

# Decision Drivers

- **Konsistensi**: Semua respons API, baik yang berhasil maupun yang gagal, harus memiliki struktur JSON yang seragam.
- **Efisiensi Pengembangan**: Mengurangi duplikasi kode dan menyederhanakan logika di dalam _controller_.
- **Pemeliharaan**: Memusatkan logika penanganan respons dan kesalahan di satu tempat agar lebih mudah di-debug dan dimodifikasi.
- **Best Practice**: Mengikuti pola desain yang direkomendasikan oleh NestJS untuk skalabilitas.

# Considered Options

- Opsi A - Penanganan manual di setiap _controller_.
- Opsi B - Menggunakan _decorator_ kustom.
- Opsi C - Implementasi `GlobalFilters` dan `GlobalInterceptors`.

# Decision Outcome

**Chosen option: Opsi C (Implementasi `GlobalFilters` dan `GlobalInterceptors`)**.

Berdasarkan analisis pada berkas `src/main.ts`, aplikasi ini telah mengimplementasikan `HttpExceptionFilter` dan `ResponseInterceptor` secara global menggunakan `app.useGlobalFilters()` dan `app.useGlobalInterceptors()`. Keputusan ini sejalan dengan praktik terbaik NestJS untuk memastikan semua respons HTTP yang keluar dan semua _exception_ yang tidak tertangani akan diproses secara konsisten.

### Consequences

**Kelebihan**

- **Struktur Respons Seragam**: Semua data yang dikirim ke klien akan dibungkus dalam format standar oleh `ResponseInterceptor`.
- **Penanganan Kesalahan Terpusat**: `HttpExceptionFilter` menangkap semua `HttpException` dan memformatnya menjadi respons JSON yang terstruktur.
- **Kode Lebih Bersih**: _Controller_ menjadi lebih ramping karena tidak perlu lagi khawatir tentang format respons atau penanganan kesalahan dasar.

**Kekurangan**

- **Sedikit Ketergantungan Global**: Adanya komponen global berarti perilakunya memengaruhi seluruh aplikasi, yang mungkin tidak diinginkan untuk beberapa _endpoint_ spesifik yang memerlukan format respons atau penanganan kesalahan yang unik.
- **Kurva Pembelajaran**: Pengembang baru mungkin perlu memahami cara kerja _Filters_ dan _Interceptors_ di NestJS terlebih dahulu.

# Pros and Cons of the Options

### Opsi A - Penanganan manual di setiap _controller_.

**Kelebihan**

- Memberikan kontrol penuh pada setiap _endpoint_.

**Kekurangan**

- Menimbulkan duplikasi kode yang signifikan.
- Sulit untuk menjaga konsistensi format respons dan kesalahan.
- Meningkatkan kompleksitas pada logika bisnis di _controller_.

### Opsi B - Menggunakan _decorator_ kustom.

**Kelebihan**

- Lebih bersih daripada penanganan manual.

**Kekurangan**

- Masih memerlukan penerapan manual di setiap _controller method_.
- Kurang efisien dibandingkan pendekatan global jika sebagian besar _endpoint_ memerlukan perilaku yang sama.

### Opsi C - Implementasi `GlobalFilters` dan `GlobalInterceptors`.

**Kelebihan**

- **DRY (Don't Repeat Yourself)**: Menghilangkan kode berulang untuk format respons dan penanganan kesalahan.
- **Konsistensi Terjamin**: Memastikan semua respons API memiliki struktur yang sama.
- **Terpusat**: Logika terpusat di satu tempat, memudahkan pemeliharaan dan modifikasi.

**Kekurangan**

- **Kurang Fleksibel untuk Kasus Khusus**: Sulit untuk menonaktifkan perilaku global ini untuk _endpoint_ tertentu tanpa konfigurasi tambahan.
