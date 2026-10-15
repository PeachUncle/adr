---
title: 'Authentication and Authorization using Guards'
status: accepted
date: 2025-09-30
decision-makers: [Elham Syahrian Putra]
consulted: [N/A]
informed: [N/A]
---

# Context and Problem Statement

Aplikasi ini memiliki *endpoint* yang hanya boleh diakses oleh pengguna yang sudah terotentikasi, dan beberapa di antaranya bahkan terbatas hanya untuk peran (role) tertentu, seperti 'admin'. Diperlukan sebuah mekanisme yang andal dan dapat digunakan kembali untuk melindungi *endpoint-endpoint* ini dari akses yang tidak sah.

Ada beberapa pendekatan untuk mengimplementasikan keamanan pada *endpoint*:

1.  **Logika Manual di Controller**: Menulis kode untuk memeriksa token otentikasi dan peran pengguna di setiap *method controller* yang perlu dilindungi.
2.  **Menggunakan Middleware**: Membuat *middleware* kustom yang berjalan sebelum *request* mencapai *controller*, di mana token dan peran akan divalidasi.
3.  **Menggunakan NestJS Guards**: Memanfaatkan fitur `Guard` yang disediakan oleh NestJS, yang dirancang khusus untuk menangani logika otorisasi dan otentikasi.

# Decision Drivers

-   **Keamanan**: Memastikan bahwa *endpoint* yang sensitif tidak dapat diakses oleh pihak yang tidak berwenang.
-   **Keterbacaan Kode**: Logika keamanan harus terpisah dari logika bisnis agar *controller* tetap bersih dan fokus pada tugasnya.
-   **Dapat Digunakan Kembali (Reusability)**: Mekanisme keamanan harus mudah diterapkan di berbagai *controller* dan *endpoint* tanpa perlu menulis ulang kode.
-   **Integrasi dengan Framework**: Solusi yang dipilih harus terintegrasi dengan baik dengan ekosistem NestJS, termasuk *Dependency Injection* dan *Execution Context*.

# Considered Options

-   Opsi A - Logika manual di setiap *controller*.
-   Opsi B - Menggunakan *middleware* kustom.
-   Opsi C - Mengimplementasikan `AuthGuard` dan `RolesGuard`.

# Decision Outcome

**Chosen option: Opsi C (Mengimplementasikan `AuthGuard` dan `RolesGuard`)**.

Berdasarkan analisis kode pada `src/auth/guards/auth.guard.ts` dan `src/auth/guards/roles.guard.ts`, aplikasi ini menggunakan pendekatan berbasis `Guard`. `AuthGuard` bertanggung jawab untuk memvalidasi token otentikasi, sementara `RolesGuard` memeriksa apakah pengguna memiliki peran yang diperlukan untuk mengakses *endpoint* tertentu. Penggunaannya terlihat jelas di berbagai *controller*, seperti `LabsController` dan `ReservationController`, di mana *guard* ini diterapkan baik di level *controller* maupun *method*.

### Consequences

**Kelebihan**

-   **Pemisahan Tanggung Jawab (Separation of Concerns)**: Logika otentikasi dan otorisasi terisolasi sepenuhnya dari logika bisnis di dalam *service* dan *controller*.
-   **Deklaratif dan Mudah Dibaca**: Keamanan diterapkan secara deklaratif menggunakan *decorator* `@UseGuards(AuthGuard, RolesGuard)` dan `@Roles('admin')`, yang membuat niat kode menjadi sangat jelas.
-   **Reusable**: `AuthGuard` dan `RolesGuard` dapat dengan mudah diterapkan pada *endpoint* mana pun di seluruh aplikasi.
-   **Akses ke Konteks Eksekusi**: *Guards* memiliki akses penuh ke `ExecutionContext`, yang memungkinkan mereka untuk memeriksa detail *request*, *response*, dan metadata *handler* (seperti peran yang dibutuhkan).

**Kekurangan**

-   **Tidak Cocok untuk Semua Kasus**: *Guards* tidak dirancang untuk tugas-tugas seperti transformasi *request/response* atau penanganan *middleware* global yang tidak berhubungan dengan otorisasi (misalnya, *logging*).

# Pros and Cons of the Options

### Opsi A - Logika manual di setiap *controller*.

**Kelebihan**

-   Sederhana untuk kasus yang sangat kecil dan tidak kompleks.

**Kekurangan**

-   Sangat rentan terhadap kesalahan manusia dan duplikasi kode.
-   Mencampuradukkan logika keamanan dengan logika bisnis.
-   Sulit dipelihara saat aplikasi berkembang.

### Opsi B - Menggunakan *middleware* kustom.

**Kelebihan**

-   Memisahkan logika keamanan dari *controller*.

**Kekurangan**

-   *Middleware* di NestJS berjalan sebelum *guard* dan tidak memiliki akses ke `ExecutionContext` secara penuh, sehingga lebih sulit untuk mengetahui *handler* mana yang akan dieksekusi. Ini membuat implementasi otorisasi berbasis peran (yang bergantung pada metadata *decorator*) menjadi lebih rumit.

### Opsi C - Mengimplementasikan `AuthGuard` dan `RolesGuard`.

**Kelebihan**

-   Sesuai dengan *best practice* dari arsitektur NestJS.
-   Menyediakan cara yang bersih, deklaratif, dan dapat digunakan kembali untuk mengamankan *endpoint*.
-   Terintegrasi penuh dengan sistem *Dependency Injection* dan *Execution Context* NestJS.

**Kekurangan**

-   Memerlukan pemahaman tentang siklus hidup *request* di NestJS.