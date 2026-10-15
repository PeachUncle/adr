---
title: 'Strategi Penyimpanan Durasi di Column Reservations'
status: accepted
date: 2025-09-30
decision-makers: [Elham Syahrian Putra]
consulted: [N/A]
informed: [N/A]
---

# Strategi Penyimpanan Durasi di Column Reservations

## Context and Problem Statement

Dalam sebuah entitas _reservation_ tentu jangka waktu yang ditentukan untuk membatasi _reservation_ tersebut. Sejauh ini ada dua pendekatan yang bisa terpikirkan yang bisa digunakan, yaitu:

1. **Kombinasi column _start_at_ dan _duration_**  
   `Disini duration akan mendefinisikan total lama reservation yang dilakukan pengguna`

2. Kombinasi column _start_at_ dan _end_at_:  
   `Pendekatan ini menentukan waktu awal dan berakhirnya reservasi`

## Decision Drivers

- Kejelasan
- Kemudahan dalam pengelolaan waktu
- Fleksibilitas ke depan

## Considered Options

- Opsi A - Menggunakan kombinasi column _start_at_ dan _duration_
- Opsi B - Menggunakan kombinasi column _start_at_ dan _end_at_

## Decision Outcome

Chosen Option:  
**Opsi A - Menggunakan kombinasi column _start_at_ dan _duration_**

Karena secara intuitif durasi sangat erat berhubungan 'berapa lama' alih alih 'selesai kapan'. Selain itu lebih mudah untuk melihat dan menentukan berapa lama durasi reservasi.

### Consequences

**Kelebihan**

- Saat membaca data, secara intuitif lebih mudah mengetahui berapa lama durasi dari sebuah _reservation_
- Pengelolaannya mudah, karena bertipe data _int_

**Kekurangan**

- Untuk mengetahui kapan sebuah _reservation_ akan berakhir, harus mengitung secara manual.
- Untuk mengitung waktu akhirnya, harus melakukan konversi ke unix time terlebih dahulu

## Pros and Cons of the Options

### Opsi A - Menggunakan kombinasi column _start_at_ dan _duration_

**Kelebihan**

- Berapa lama durasi yang dibutuhkan sangat jelas terlihat
- Pengelolaan lebih mudah, karena tipe datanya `int`

**Kekurangan**

- Untuk menentukan berakhirnya reseravsi, harus dilakukan konversi terlebih dahulu dan dihitung secara manual dengan menjumlah start_at + duration (setelah di konversi)

### Opsi B - Menggunakan kombinasi column _start_at_ dan _end_at_

**Kelebihan**

- Sangat jelas ketika fokusnya adalah 'kapan berkahir-nya' sebuah `reservation`

**Kekurangan**

- Harus menghitung terlebih dahulu jika ingin mengetahui berapa lama (durasi) dari `reservation`
