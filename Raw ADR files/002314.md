# 3. Backend Integration Strategy

## Status
Accepted

## Date
06/05/2025

## Decider
Team Lead @FranklinJaya2006

## Informed
@chaidenfoanto @feliciawijaya2006

## Context
Aplikasi **Jobaile** memerlukan komunikasi yang efektif antara frontend Flutter dan backend Laravel. Dibutuhkan strategi komunikasi backend yang fleksibel, mudah diimplementasikan, dan sesuai untuk kebutuhan pertukaran data secara real-time maupun permintaan terpisah.

## Decision
Tim kami memutuskan menggunakan **RESTful API**, untuk mendukung pengembangan aplikasi kami karena Restful API bersifat fleksibel, mudah dikembangkan, performa yang cukup baik. Pendekatan ini dipilih karena:
- REST API sangat kompatibel dengan ekosistem Laravel.
- Didukung oleh komunitas luas dan dokumentasi yang memadai.
- Memudahkan pemisahan frontend dan backend.
Selain itu, semua anggota kelompok kami sudah sangat familiar dengan penggunaan Restful API, hal tersebut memberikan alasan yang kuat bagi kami dalam penggunaan Restful API. 

## Alternative
Kelompok kami sempat memilih untuk menggunakan GraphQL karena ia dapat mempermudah pengelolaan dependensi data, serta ia dapat meminimalkan pengambilan data yang berlebihan, tetapi dibalik kelebihannya ada kelemahan yang kami rasa akan jadi hal fatal jika kami gunakan, terdapat beberapa masalah keamanan, masalah over-fetching. Selain itu, terdapat Backend-as-a-Service like Firebase. Karena Backend-as-a-Service like Firebase memiliki sinkronisasi data secara real-time yang baik, dapat membantu mengidentifikasi dan mengatasi masalah yang memengaruhi kinerja aplikasi, serta memungkinkan identifikasi dan perbaikan bug sebelum peluncuran aplikasi. Tetapi, ada kelemahan utamanya terdapat pada ia tidak mendukung MySql karena anggota tim kami belum mahir dalam penggunaan NoSql, serta firebase free yang memiliki batasan dalam penggunaan.

## Consequences

### Keuntungan
- RESTful API mudah dipahami dan sudah sering kami gunakan selama pengerjaan proyek kuliah.
- Memudahkan debugging dan dokumentasi endpoint API.
- Bisa dikembangkan lebih lanjut dengan standar REST.

### Potensi Risiko
- Kurang fleksibel dibanding GraphQL dalam pengambilan data spesifik.
- Potensi overhead karena pertukaran data tidak seefisien payload GraphQL.

### Mitigasi
- Menyusun dokumentasi endpoint secara rapi sejak awal.
- Mengoptimalkan payload dan response dari setiap endpoint untuk efisiensi komunikasi.