# Dashboard Klaster Negara Tujuan Menetap WNI (Streamlit)

Dashboard prototipe untuk proposal *Pengelompokan Negara Tujuan Menetap WNI di Luar Negeri Berdasarkan Pola Migrasi Menggunakan K-Means*.
Dashboard hanya membaca CSV hasil eksperimen (tidak melatih model).

## Isi repositori
| Berkas | Fungsi |
|---|---|
| `app.py` | Aplikasi Streamlit (5 tab: ringkasan, penentuan K, profil proporsi, keanggotaan negara, catatan metode) |
| `data/klaster_semua_K.csv` | Proporsi tiap negara dan label klaster untuk K = 2–10 |
| `data/metrik_K.csv` | SSE, Silhouette, ukuran klaster terkecil/terbesar per K |
| `buat_data_dashboard.py` | Membuat kedua CSV dari `hasil_klaster.csv` keluaran notebook |
| `requirements.txt` | Library untuk deployment |

## Menjalankan lokal
```
pip install -r requirements.txt
streamlit run app.py
```

## Deployment ke Streamlit Community Cloud
1. Buat repositori GitHub **publik** (mis. `dashboard-klaster-wni`), unggah seluruh isi folder ini (`app.py` di akar repositori).
2. Buka https://share.streamlit.io, masuk dengan akun GitHub, klik **Create app** → **Deploy a public app from GitHub**.
3. Isi *Repository*, *Branch* = `main`, *Main file path* = `app.py`, lalu **Deploy**.
4. Setelah selesai, salin tautan `https://<nama>.streamlit.app` ke laporan/proposal.

## Memperbarui data
Ganti `hasil_klaster.csv` dengan keluaran notebook terbaru, jalankan `python buat_data_dashboard.py hasil_klaster.csv`, lalu `git push`; aplikasi otomatis diperbarui.
