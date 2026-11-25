"""Menyiapkan berkas CSV untuk dashboard dari keluaran notebook Colab.
Jalankan sekali (di Colab atau lokal) setelah notebook eksperimen selesai.
Masukan : hasil_klaster.csv (dari notebook; kolom negara, kawasan, total_wni, 6 tujuan)
Keluaran: data/klaster_semua_K.csv dan data/metrik_K.csv
Pengaturan sama dengan notebook: k-means++, n_init=10, random_state=42, jarak Euclidean pada proporsi.
"""
import sys
import numpy as np, pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

SUMBER = sys.argv[1] if len(sys.argv) > 1 else "hasil_klaster.csv"
FITUR = ["bekerja", "belajar", "magang", "lain_lain", "mendampingi_pasangan", "anggota_keluarga"]
df = pd.read_csv(SUMBER)
X = df[FITUR].to_numpy()
assert np.allclose(X.sum(axis=1), 1), "proporsi tiap negara harus berjumlah 1"

out = df[["negara", "kawasan", "total_wni"] + FITUR].copy()
rows = []
for k in range(2, 11):
    km = KMeans(n_clusters=k, init="k-means++", n_init=10, random_state=42).fit(X)
    out[f"K{k}"] = km.labels_
    ukuran = np.bincount(km.labels_)
    rows.append(dict(K=k, SSE=km.inertia_, Silhouette=silhouette_score(X, km.labels_),
                     Ukuran_min=ukuran.min(), Ukuran_maks=ukuran.max()))
out.to_csv("data/klaster_semua_K.csv", index=False)
pd.DataFrame(rows).to_csv("data/metrik_K.csv", index=False)
print("selesai:", out.shape, "-> data/klaster_semua_K.csv dan data/metrik_K.csv")
