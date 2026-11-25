"""Dashboard pengelompokan negara tujuan menetap WNI (K-means pada proporsi tujuan menetap, data Kemlu 2023).
Dashboard hanya membaca berkas CSV hasil eksperimen; tidak ada pelatihan model di sini."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Klaster Negara Tujuan Menetap WNI", page_icon="🌏", layout="wide")

FITUR = ["bekerja", "belajar", "magang", "lain_lain", "mendampingi_pasangan", "anggota_keluarga"]
LABEL = {"bekerja": "Bekerja", "belajar": "Belajar", "magang": "Magang", "lain_lain": "Lain-lain",
         "mendampingi_pasangan": "Mendampingi suami/istri", "anggota_keluarga": "Anggota keluarga"}
WARNA = ["#2b6cb0", "#dd8452", "#55a868", "#c44e52", "#8172b3", "#937860"]
K_UTAMA, K_SIKU = 4, 5   # K dengan Silhouette tertinggi dan K titik siku Elbow (hasil eksperimen)


@st.cache_data
def muat():
    return pd.read_csv("data/klaster_semua_K.csv"), pd.read_csv("data/metrik_K.csv")


try:
    data, metrik = muat()
except FileNotFoundError:
    st.error("Berkas data/klaster_semua_K.csv atau data/metrik_K.csv tidak ditemukan. "
             "Jalankan buat_data_dashboard.py terlebih dahulu.")
    st.stop()

# ------------------------------------------------------------------ sidebar
st.sidebar.title("Pengaturan")
K = st.sidebar.select_slider("Jumlah klaster (K)", options=list(range(2, 11)), value=K_UTAMA,
                             help="K = 4 memiliki Silhouette tertinggi; K = 5 adalah titik siku Elbow.")
kolom = f"K{K}"
st.sidebar.caption("Seluruh angka dihitung dari 96 negara. Filter kawasan dan pencarian negara hanya tersedia pada tab Keanggotaan negara.")

# ringkasan per klaster untuk K terpilih
prof = data.groupby(kolom)[FITUR].mean()
ukuran = data.groupby(kolom).size()
pangsa = data.groupby(kolom)["total_wni"].sum() / data["total_wni"].sum() * 100
dominan = prof.idxmax(axis=1)
nama = {k: f"Klaster {k} (dominan: {LABEL[dominan[k]]} {prof.loc[k, dominan[k]] * 100:.0f}%)" for k in prof.index}
data["klaster"] = data[kolom].map(nama)

# ------------------------------------------------------------------ header
st.title("Pengelompokan Negara Tujuan Menetap WNI di Luar Negeri")
st.caption("Metode: K-means pada proporsi tujuan menetap (bekerja, belajar, magang, lain-lain, mendampingi suami/istri, "
           "anggota keluarga). Data: Data Agregat Tujuan Menetap WNI di Luar Negeri Tahun 2023, Kementerian Luar Negeri (data.go.id).")

m = metrik.set_index("K").loc[K]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Jumlah negara", len(data))
c2.metric("Total WNI", f"{int(data['total_wni'].sum()):,}".replace(",", "."))
c3.metric("K terpilih", K)
c4.metric("Silhouette score", f"{m['Silhouette']:.3f}".replace(".", ","))

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Ringkasan klaster", "Penentuan K", "Profil proporsi", "Keanggotaan negara", "Catatan metode"])

# ------------------------------------------------------------------ tab 1
with tab1:
    st.subheader(f"Ringkasan klaster pada K = {K}")
    r = pd.DataFrame({"Klaster": [nama[k] for k in prof.index], "Jumlah negara": ukuran.values,
                      "Pangsa WNI (%)": pangsa.round(1).values})
    st.dataframe(r, hide_index=True, width='stretch')
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.barh([f"Klaster {k}" for k in prof.index][::-1], ukuran.values[::-1], color="#2b6cb0")
    ax.set_xlabel("Jumlah negara"); ax.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig); plt.close(fig)
    st.caption("Nama klaster dibuat otomatis dari tujuan menetap dengan rata-rata proporsi tertinggi (persentase = rata-rata proporsi tujuan tersebut). Klaster dengan dominasi "
               "'Lain-lain' perlu ditafsirkan hati-hati karena kategori tersebut tidak merinci tujuannya.")

# ------------------------------------------------------------------ tab 2
with tab2:
    st.subheader("Elbow dan Silhouette untuk K = 2 sampai 10")
    a, b = st.columns(2)
    siku = float(metrik.loc[metrik.K == K_SIKU, "SSE"].iloc[0])
    with a:
        fig, ax = plt.subplots(figsize=(5, 3.2))
        ax.plot(metrik.K, metrik.SSE, "o-", color="#2b6cb0")
        ax.axvline(K_SIKU, ls="--", color="grey", lw=1); ax.axvline(K, color="#c44e52", lw=1, alpha=.6)
        ax.set_xlabel("K"); ax.set_ylabel("SSE"); ax.set_title(f"Elbow (siku pada K = {K_SIKU})", fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
        st.pyplot(fig); plt.close(fig)
    with b:
        fig, ax = plt.subplots(figsize=(5, 3.2))
        ax.plot(metrik.K, metrik.Silhouette, "o-", color="#dd8452")
        ax.axvline(K, color="#c44e52", lw=1, alpha=.6)
        ax.set_xlabel("K"); ax.set_ylabel("Silhouette score")
        ax.set_title(f"Silhouette (tertinggi pada K = {int(metrik.loc[metrik.Silhouette.idxmax(), 'K'])})", fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
        st.pyplot(fig); plt.close(fig)
    t = metrik.rename(columns={"Ukuran_min": "Klaster terkecil", "Ukuran_maks": "Klaster terbesar"}).copy()
    t["SSE"] = t["SSE"].round(4); t["Silhouette"] = t["Silhouette"].round(4)
    st.dataframe(t, hide_index=True, width='stretch')
    st.caption("Garis merah menandai K yang sedang dipilih. Silhouette tertinggi hanya sekitar 0,43 (di bawah 0,5), sehingga "
               "struktur klaster ada tetapi tidak tegas; pada K = 10 muncul klaster berisi satu negara.")

# ------------------------------------------------------------------ tab 3
with tab3:
    st.subheader(f"Profil proporsi tujuan menetap per klaster (K = {K})")
    fig, ax = plt.subplots(figsize=(9, 4))
    lebar = 0.8 / len(FITUR); x = np.arange(len(prof))
    for i, f in enumerate(FITUR):
        ax.bar(x + i * lebar, prof[f], lebar, label=LABEL[f], color=WARNA[i])
    ax.set_xticks(x + 0.4 - lebar / 2); ax.set_xticklabels([f"Klaster {k}" for k in prof.index])
    ax.set_ylabel("Rata-rata proporsi"); ax.legend(fontsize=8, ncol=3, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig); plt.close(fig)
    tp = prof.copy(); tp.columns = [LABEL[c] for c in tp.columns]
    tp.insert(0, "Negara", ukuran.values); tp.index = [f"Klaster {k}" for k in tp.index]
    st.dataframe(tp.round(3), width='stretch')
    st.caption("Setiap nilai adalah rata-rata proporsi tujuan menetap negara anggota klaster. Hasil bersifat deskriptif "
               "dan tidak menjelaskan hubungan sebab-akibat.")

# ------------------------------------------------------------------ tab 4
with tab4:
    st.subheader("Keanggotaan klaster tiap negara")
    kaw = sorted(data["kawasan"].unique())
    pilih_kaw = st.multiselect("Filter kawasan", kaw, default=kaw)
    cari = st.text_input("Cari negara")
    pil_klaster = st.multiselect("Filter klaster", sorted(data["klaster"].unique()), default=sorted(data["klaster"].unique()))
    v = data[data.kawasan.isin(pilih_kaw) & data.klaster.isin(pil_klaster)]
    if cari:
        v = v[v.negara.str.contains(cari, case=False, na=False)]
    tampil = v[["negara", "kawasan", "total_wni", "klaster"] + FITUR].rename(columns=LABEL).rename(
        columns={"negara": "Negara", "kawasan": "Kawasan", "total_wni": "Total WNI", "klaster": "Klaster"})
    st.dataframe(tampil.style.format({LABEL[f]: "{:.3f}" for f in FITUR} | {"Total WNI": "{:,.0f}"}),
                 hide_index=True, width='stretch')
    st.caption(f"{len(v)} dari {len(data)} negara ditampilkan.")
    st.download_button("Unduh tabel (CSV)", tampil.to_csv(index=False).encode("utf-8"),
                       file_name=f"keanggotaan_klaster_K{K}.csv", mime="text/csv")

# ------------------------------------------------------------------ tab 5
with tab5:
    st.subheader("Catatan metode dan keterbatasan")
    st.markdown("""
**Data.** Data agregat tujuan menetap WNI di luar negeri tahun 2023 (Kemlu, data.go.id): 96 negara dan enam tujuan menetap.
Jumlah WNI diubah menjadi proporsi per negara sehingga yang dikelompokkan adalah pola tujuan, bukan ukuran negara.

**Metode.** K-means (k-means++, `n_init = 10`, `random_state = 42`, jarak Euclidean) pada proporsi, K = 2 sampai 10.
K ditentukan dengan Elbow method dan Silhouette score. Hasil eksperimen: Silhouette tertinggi pada K = 4 (0,434) dan titik siku pada K = 5.
Pengelompokan stabil saat 15 negara dengan WNI kurang dari 100 dibuang (ARI = 1,000 pada K = 4).

**Keterbatasan.**
- Satu periode data (2023) dan tidak ada label sebenarnya, sehingga evaluasi bersifat internal.
- Silhouette di bawah 0,5: batas antarklaster tidak tegas.
- Kategori "Lain-lain" bersifat heterogen.
- Hasil deskriptif, bukan penjelasan sebab-akibat. Dashboard ini adalah prototipe sederhana, bukan sistem siap produksi.
""")
