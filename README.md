# 📊 Dashboard Analisis Attrition Karyawan

**UTS Visualisasi Data — Ganjil TA 2026/2027**
Program Studi Sistem Informasi, Universitas Dirgantara Marsekal Suryadarma

| | |
|---|---|
| **Nama** | Aloisius Gilang Putra Sadewa |
| **NIM** | 241053001 |
| **Dosen** | Muryan Awaludin, S.Kom., M.Kom. |

## 🔗 Tautan

- **Live Dashboard:** [uts-visdat-attrition2.streamlit.app](https://uts-visdat-attrition2.streamlit.app)
- **Dataset Kaggle:** [IBM HR Analytics Employee Attrition & Performance](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset)

## 📌 Latar Belakang

*Attrition* (karyawan keluar dari perusahaan) merugikan organisasi: biaya rekrutmen dan pelatihan karyawan baru tinggi, pengalaman hilang, dan produktivitas turun. Proyek ini menganalisis data 1.470 karyawan fiktif yang dibuat oleh data scientist IBM untuk menjawab pertanyaan: **faktor apa saja yang membuat karyawan memilih keluar?**

Dashboard dibangun dengan **Python Streamlit** dan **Plotly**, berisi:

- **4 kartu KPI:** total karyawan, jumlah karyawan keluar, tingkat attrition, dan rata-rata gaji bulanan.
- **5 jenis visualisasi:** line chart (attrition per masa kerja), donut chart (proporsi keluar/bertahan), bar chart (attrition per jabatan), heatmap (lembur × kepuasan kerja), dan box plot (sebaran gaji).
- **3 filter interaktif:** departemen, jenis kelamin, dan rentang usia.
- **Storytelling:** kotak insight dan anotasi pada grafik yang angkanya diperbarui otomatis sesuai filter.

## 💡 Wawasan Utama (Key Insights)

1. **Tingkat attrition 16,1%.** Sebanyak 237 dari 1.470 karyawan keluar dari perusahaan.
2. **Lembur adalah pemicu terkuat.** Karyawan yang lembur keluar sebanyak **30,5%**, hampir 3 kali lipat dibanding yang tidak lembur (**10,4%**).
3. **Dua tahun pertama adalah masa paling rawan.** Karyawan dengan masa kerja 0–2 tahun keluar sebanyak **29,8%**, sedangkan yang bekerja lebih dari 10 tahun hanya **8,1%**.
4. **Gaji rendah berkaitan dengan keputusan keluar.** Rata-rata gaji karyawan yang keluar **$4.787**, jauh di bawah karyawan yang bertahan (**$6.833**). Pada kelompok gaji terendah (kuartil bawah), attrition mencapai **29,3%**.
5. **Jabatan penjualan paling rentan.** *Sales Representative* memiliki attrition tertinggi (**39,8%**), sedangkan *Research Director* terendah (**2,5%**).

**Rekomendasi:** membatasi lembur berlebihan, memperkuat program *onboarding* dan pendampingan bagi karyawan baru, serta meninjau skema gaji dan insentif untuk jabatan dengan attrition tinggi.

## 🧹 Pengolahan Data

Skrip pembersihan data ada di [`data/clean_data.py`](data/clean_data.py):

1. Memeriksa data kosong dan duplikat (hasil: 0 data kosong, 0 duplikat).
2. Membuang kolom yang nilainya sama untuk semua baris: `EmployeeCount`, `Over18`, `StandardHours`.
3. Mengubah kode angka skala ordinal menjadi label yang mudah dibaca (misalnya kepuasan kerja 1–4 menjadi *Low, Medium, High, Very High*).
4. Menambahkan kolom bantu: `AttritionFlag` (1 = keluar), `AgeGroup`, `TenureGroup`, dan `IncomeGroup`.

Hasil akhir: **1.470 baris, 43 kolom** → [`data/hr_attrition_clean.csv`](data/hr_attrition_clean.csv)

## 📁 Struktur Repositori

```
uts-visdat/
├── .streamlit/
│   └── config.toml            # tema warna dashboard
├── data/
│   ├── WA_Fn-UseC_-HR-Employee-Attrition.csv   # data mentah dari Kaggle
│   ├── clean_data.py          # skrip pembersihan data
│   └── hr_attrition_clean.csv # data yang sudah dibersihkan
├── app.py                     # aplikasi dashboard Streamlit
├── requirements.txt           # daftar library untuk deployment
└── README.md
```

## ▶️ Cara Menjalankan Secara Lokal

1. Clone repositori ini:
   ```bash
   git clone https://github.com/maharanisetya936-dot/uts-visdat.git
   cd uts-visdat
   ```
2. Pasang library yang dibutuhkan:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. (Opsional) Jalankan ulang pembersihan data:
   ```bash
   python data/clean_data.py
   ```
4. Jalankan dashboard:
   ```bash
   python -m streamlit run app.py
   ```
5. Buka `http://localhost:8501` di browser.

## 🛠️ Teknologi

Python · Streamlit · Pandas · Plotly Express · Streamlit Community Cloud (hosting)
