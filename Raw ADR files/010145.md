---
title: 'Data Validation and Transformation Strategy using DTOs'
status: accepted
date: 2025-09-30
decision-makers: [Elham Syahrian Putra]
consulted: [N/A]
informed: [N/A]
---

# Context and Problem Statement

Aplikasi ini menerima data dari klien melalui *request body* pada operasi `POST` dan `PUT`. Data ini tidak bisa langsung dipercaya dan harus divalidasi untuk memastikan integritas (misalnya, `email` harus berformat email, `name` tidak boleh kosong) dan ditransformasi (misalnya, menghapus spasi berlebih, mengubah string tanggal menjadi objek `Date`).

Diperlukan sebuah strategi yang sistematis dan efisien untuk menangani validasi dan transformasi data yang masuk.

1.  **Validasi Manual di Service**: Melakukan pemeriksaan data secara manual di dalam setiap *service method*. Ini melibatkan banyak kode `if-else` dan rawan kesalahan.
2.  **Menggunakan Skema Validasi (seperti Joi)**: Mendefinisikan skema objek terpisah untuk setiap *endpoint* dan memvalidasi *request body* terhadap skema tersebut.
3.  **Menggunakan Class-based DTO dengan Decorators**: Memanfaatkan *library* seperti `class-validator` dan `class-transformer` untuk mendefinisikan aturan validasi dan transformasi langsung di dalam *Data Transfer Object* (DTO) menggunakan *decorators*.

# Decision Drivers

-   **Keamanan Data**: Mencegah data yang tidak valid atau berbahaya masuk ke dalam logika bisnis dan database.
-   **Kode yang Bersih dan Deklaratif**: Aturan validasi harus mudah dibaca dan didefinisikan di satu tempat yang relevan.
-   **Pesan Kesalahan yang Jelas**: Ketika validasi gagal, API harus mengembalikan pesan kesalahan yang terstruktur dan informatif bagi pengembang *frontend*.
-   **Integrasi dengan Framework**: Solusi harus terintegrasi secara mulus dengan alur kerja NestJS, terutama dengan `Pipes`.

# Considered Options

-   Opsi A - Validasi manual di dalam *service*.
-   Opsi B - Menggunakan *library* skema seperti Joi.
-   Opsi C - Menggunakan `class-validator` dan `class-transformer` dengan `ValidationPipe`.

# Decision Outcome

**Chosen option: Opsi C (Menggunakan `class-validator` dan `class-transformer` dengan `ValidationPipe`)**.

Analisis kode menunjukkan penggunaan yang konsisten dari *decorator* `@IsString`, `@IsNotEmpty`, `@IsUUID`, `@Transform`, dan lainnya di seluruh berkas DTO (seperti `src/labs/dto/create-lab-dto.ts` dan `src/auth/dto/register.dto.ts`). Lebih lanjut, berkas `src/main.ts` mengkonfigurasi `ValidationPipe` secara global, yang secara otomatis memicu validasi ini pada semua *request* yang masuk. Aplikasi ini juga menggunakan `validationExceptionFactory` kustom untuk memformat pesan kesalahan validasi secara seragam.

### Consequences

**Kelebihan**

-   **Aturan Terpusat di DTO**: Setiap DTO menjadi satu-satunya sumber kebenaran (*single source of truth*) untuk bentuk dan aturan data yang diharapkan.
-   **Validasi Otomatis**: Dengan `ValidationPipe` global, pengembang tidak perlu memanggil validasi secara manual di setiap *controller*.
-   **Transformasi Data Otomatis**: *Decorator* `@Transform` memungkinkan sanitasi dan konversi tipe data (misalnya `trim` spasi) sebelum data mencapai *handler*.
-   **Pesan Kesalahan Terstruktur**: Penggunaan `validationExceptionFactory` memastikan bahwa klien menerima respons `422 Unprocessable Entity` yang konsisten dengan detail kesalahan per-kolom.

**Kekurangan**

-   **Ketergantungan pada Decorator**: Logika validasi tersebar di banyak *decorator*, yang mungkin bisa menjadi sedikit rumit untuk DTO yang sangat kompleks.
-   **Validasi Lintas Kolom**: Validasi yang bergantung pada beberapa kolom (misalnya, `password` harus cocok dengan `password_confirmation`) memerlukan *custom validator* yang lebih kompleks.

# Pros and Cons of the Options

### Opsi A - Validasi manual di dalam *service*.

**Kelebihan**

-   Tidak memerlukan *library* eksternal.

**Kekurangan**

-   Menghasilkan banyak kode *boilerplate* dan duplikasi.
-   Mencampuradukkan logika validasi dengan logika bisnis.
-   Sulit untuk menghasilkan pesan kesalahan yang konsisten.

### Opsi B - Menggunakan *library* skema seperti Joi.

**Kelebihan**

-   Skema sangat kuat dan fleksibel.
-   Memisahkan definisi skema dari *class* atau *interface*.

**Kekurangan**

-   Memerlukan pemeliharaan dua set definisi (skema Joi dan *interface* TypeScript), yang bisa menjadi tidak sinkron.
-   Kurang terintegrasi secara "alami" dengan NestJS dibandingkan `class-validator`.

### Opsi C - Menggunakan `class-validator` dan `class-transformer`.

**Kelebihan**

-   **Sangat Terintegrasi**: Dirancang untuk bekerja dengan NestJS dan TypeScript.
-   **Deklaratif**: Aturan validasi didefinisikan dengan jelas di samping properti yang divalidasi.
-   **Tipe Data Aman**: Menggunakan *class* sebagai DTO memberikan keamanan tipe saat pengembangan.

**Kekurangan**

-   Kurang ideal untuk validasi objek dinamis yang strukturnya tidak diketahui sebelumnya.