"""
Dashboard Analisis Attrition Karyawan
UTS Visualisasi Data - Universitas Dirgantara Marsekal Suryadarma
Dataset: IBM HR Analytics Employee Attrition & Performance (Kaggle)

Jalankan secara lokal:
    streamlit run app.py
"""
import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ------------------------------------------------------------------
# Konfigurasi halaman dan warna
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Attrition Karyawan",
    page_icon="📊",
    layout="wide",
)

WARNA_KELUAR = "#D62839"      # merah  = karyawan keluar
WARNA_BERTAHAN = "#1D4E89"    # biru   = karyawan bertahan
WARNA_NETRAL = "#8D99AE"
PETA_WARNA = {"Keluar": WARNA_KELUAR, "Bertahan": WARNA_BERTAHAN}

DATA_FILE = Path(__file__).parent / "data" / "hr_attrition_clean.csv"

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem;}
    div[data-testid="stMetric"] {
        background-color: #F5F7FA;
        border: 1px solid #E1E5EB;
        border-radius: 10px;
        padding: 12px 16px;
    }
    .insight-box {
        background-color: #FFF4F4;
        border-left: 5px solid #D62839;
        border-radius: 6px;
        padding: 12px 16px;
        margin-top: 4px;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------------------------------------------------
# Memuat data
# ------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    df["Status"] = df["Attrition"].map({"Yes": "Keluar", "No": "Bertahan"})
    df["Lembur"] = df["OverTime"].map({"Yes": "Lembur", "No": "Tidak Lembur"})
    return df


df = load_data()

# ------------------------------------------------------------------
# Sidebar: filter interaktif
# ------------------------------------------------------------------
st.sidebar.header("🔎 Filter Data")

daftar_dept = sorted(df["Department"].unique())
pilih_dept = st.sidebar.multiselect("Departemen", daftar_dept, default=daftar_dept)

daftar_gender = sorted(df["Gender"].unique())
pilih_gender = st.sidebar.multiselect("Jenis Kelamin", daftar_gender, default=daftar_gender)

usia_min, usia_max = int(df["Age"].min()), int(df["Age"].max())
pilih_usia = st.sidebar.slider("Rentang Usia", usia_min, usia_max, (usia_min, usia_max))

st.sidebar.markdown("---")
st.sidebar.caption(
    "Sumber data: [IBM HR Analytics Employee Attrition & Performance]"
    "(https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) - Kaggle"
)

data = df[
    df["Department"].isin(pilih_dept)
    & df["Gender"].isin(pilih_gender)
    & df["Age"].between(pilih_usia[0], pilih_usia[1])
]

# ------------------------------------------------------------------
# Judul
# ------------------------------------------------------------------
st.title("📊 Dashboard Analisis Attrition Karyawan")
st.markdown(
    "Mengapa karyawan memilih keluar dari perusahaan? Dashboard ini menelusuri faktor "
    "**lembur, masa kerja, jabatan, kepuasan kerja, dan gaji** terhadap tingkat *attrition* "
    "(karyawan yang keluar)."
)

if data.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Silakan ubah filter di sidebar.")
    st.stop()

# ------------------------------------------------------------------
# KPI cards
# ------------------------------------------------------------------
total = len(data)
keluar = int(data["AttritionFlag"].sum())
rate = keluar / total * 100
rate_semua = df["AttritionFlag"].mean() * 100
gaji = data["MonthlyIncome"].mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("👥 Total Karyawan", f"{total:,}")
k2.metric("🚪 Karyawan Keluar", f"{keluar:,}")
selisih = rate - rate_semua
k3.metric(
    "📉 Tingkat Attrition",
    f"{rate:.1f}%",
    # Delta hanya tampil bila filter mengubah angka (dibanding seluruh data)
    delta=f"{selisih:+.1f} poin vs total" if total < len(df) and abs(selisih) >= 0.05 else None,
    delta_color="inverse",
)
k4.metric("💰 Rata-rata Gaji Bulanan", f"${gaji:,.0f}")

st.markdown("")

# ------------------------------------------------------------------
# Baris 1: Line chart (masa kerja) + Donut chart (proporsi)
# ------------------------------------------------------------------
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Tingkat Attrition berdasarkan Masa Kerja")
    masa = data.copy()
    masa["MasaKerja"] = masa["YearsAtCompany"].clip(upper=20)
    tren = (
        masa.groupby("MasaKerja")
        .agg(Rate=("AttritionFlag", "mean"), Jumlah=("AttritionFlag", "size"))
        .reset_index()
    )
    tren["Rate"] = tren["Rate"] * 100
    fig_line = px.line(
        tren,
        x="MasaKerja",
        y="Rate",
        markers=True,
        hover_data={"Jumlah": True, "Rate": ":.1f"},
        labels={"MasaKerja": "Masa kerja (tahun, 20 = 20 tahun ke atas)", "Rate": "Tingkat attrition (%)"},
        color_discrete_sequence=[WARNA_KELUAR],
    )
    fig_line.add_hline(
        y=rate, line_dash="dash", line_color=WARNA_NETRAL,
        annotation_text=f"Rata-rata {rate:.1f}%", annotation_position="top right",
    )
    if not tren.empty:
        puncak = tren.loc[tren["Rate"].idxmax()]
        fig_line.add_annotation(
            x=puncak["MasaKerja"], y=puncak["Rate"],
            text=f"Tertinggi: {puncak['Rate']:.0f}%", showarrow=True, arrowhead=2, ay=-35,
        )
    fig_line.update_layout(height=380, margin=dict(t=20, b=10))
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("Proporsi Karyawan")
    proporsi = data["Status"].value_counts().reset_index()
    proporsi.columns = ["Status", "Jumlah"]
    fig_donut = px.pie(
        proporsi, names="Status", values="Jumlah", hole=0.55,
        color="Status", color_discrete_map=PETA_WARNA,
    )
    fig_donut.update_traces(textinfo="percent+label", textposition="outside")
    fig_donut.update_layout(
        height=380, margin=dict(t=20, b=10), showlegend=False,
        annotations=[dict(text=f"{rate:.1f}%<br>keluar", x=0.5, y=0.5, font_size=18, showarrow=False)],
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ------------------------------------------------------------------
# Baris 2: Bar chart (jabatan) + Heatmap (lembur x kepuasan kerja)
# ------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    st.subheader("Tingkat Attrition per Jabatan")
    jabatan = (
        data.groupby("JobRole")
        .agg(Rate=("AttritionFlag", "mean"), Jumlah=("AttritionFlag", "size"))
        .reset_index()
    )
    jabatan["Rate"] = jabatan["Rate"] * 100
    jabatan = jabatan.sort_values("Rate")
    jabatan["Warna"] = jabatan["Rate"].apply(lambda r: "Di atas rata-rata" if r > rate else "Di bawah rata-rata")
    fig_bar = px.bar(
        jabatan, x="Rate", y="JobRole", orientation="h", text="Rate", color="Warna",
        color_discrete_map={"Di atas rata-rata": WARNA_KELUAR, "Di bawah rata-rata": WARNA_BERTAHAN},
        hover_data={"Jumlah": True, "Warna": False},
        labels={"Rate": "Tingkat attrition (%)", "JobRole": "Jabatan", "Warna": ""},
    )
    fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_bar.update_layout(
        height=420, margin=dict(t=20, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0),
        xaxis_range=[0, max(jabatan["Rate"].max() * 1.2, 5)],
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with c4:
    st.subheader("Lembur × Kepuasan Kerja")
    urutan_puas = ["Low", "Medium", "High", "Very High"]
    label_puas = {"Low": "Rendah", "Medium": "Sedang", "High": "Tinggi", "Very High": "Sangat Tinggi"}
    heat = data.pivot_table(
        index="Lembur", columns="JobSatisfactionLabel", values="AttritionFlag", aggfunc="mean"
    ) * 100
    heat = heat.reindex(columns=[k for k in urutan_puas if k in heat.columns])
    heat.columns = [label_puas[k] for k in heat.columns]
    fig_heat = px.imshow(
        heat.round(1), text_auto=".1f", aspect="auto",
        color_continuous_scale=["#F1F5FB", "#F4A3A8", WARNA_KELUAR],
        labels=dict(x="Tingkat kepuasan kerja", y="", color="Attrition (%)"),
    )
    fig_heat.update_layout(height=420, margin=dict(t=20, b=10))
    st.plotly_chart(fig_heat, use_container_width=True)

# ------------------------------------------------------------------
# Baris 3: Box plot (gaji)
# ------------------------------------------------------------------
st.subheader("Sebaran Gaji Bulanan: Keluar vs Bertahan")
fig_box = px.box(
    data, x="Status", y="MonthlyIncome", color="Status", color_discrete_map=PETA_WARNA,
    category_orders={"Status": ["Bertahan", "Keluar"]},
    labels={"MonthlyIncome": "Gaji bulanan (USD)", "Status": ""},
    points="outliers",
)
fig_box.update_layout(height=360, margin=dict(t=20, b=10), showlegend=False)
st.plotly_chart(fig_box, use_container_width=True)

# ------------------------------------------------------------------
# Storytelling: insight dinamis (ikut berubah sesuai filter)
# ------------------------------------------------------------------
st.subheader("💡 Insight Utama")


def rate_of(mask):
    """Tingkat attrition (%) dan jumlah karyawan pada kelompok tertentu."""
    sub = data[mask]
    return (sub["AttritionFlag"].mean() * 100 if len(sub) else None), len(sub)


def banding(nama_a, nama_b, a, b, n_a, n_b) -> str:
    """Kalimat perbandingan yang menyesuaikan arah selisih."""
    if a is None or b is None:
        return "data salah satu kelompok tidak tersedia pada filter ini"
    if a > b:
        kata = f"lebih tinggi ({a / b:.1f}× lipat)" if b > 0 else "lebih tinggi"
    elif a < b:
        kata = "lebih rendah"
    else:
        kata = "sama"
    return (f"{nama_a} **{a:.1f}%** (n={n_a}) {kata} dibanding {nama_b} **{b:.1f}%** (n={n_b})")


poin = []
if keluar == 0:
    poin.append("**Tidak ada karyawan yang keluar** pada kombinasi filter ini, sehingga faktor pemicu tidak dapat dibandingkan.")
else:
    r_l, n_l = rate_of(data["OverTime"] == "Yes")
    r_t, n_t = rate_of(data["OverTime"] == "No")
    poin.append("**Lembur:** tingkat keluar karyawan yang lembur " +
                banding("", "yang tidak lembur", r_l, r_t, n_l, n_t).strip() + ".")

    r_b, n_b = rate_of(data["YearsAtCompany"] <= 2)
    r_m, n_m = rate_of(data["YearsAtCompany"] > 10)
    poin.append("**Masa kerja:** karyawan baru (0–2 tahun) " +
                banding("", "karyawan lama (>10 tahun)", r_b, r_m, n_b, n_m).strip() + ".")

    # Peringkat jabatan hanya untuk jabatan dengan minimal 5 karyawan agar tidak menyesatkan
    jab_cukup = jabatan[jabatan["Jumlah"] >= 5]
    if len(jab_cukup) >= 2:
        hi, lo = jab_cukup.iloc[-1], jab_cukup.iloc[0]
        poin.append(
            f"**Jabatan:** *{hi['JobRole']}* memiliki attrition tertinggi (**{hi['Rate']:.1f}%**), "
            f"sedangkan *{lo['JobRole']}* terendah (**{lo['Rate']:.1f}%**)."
        )

    g_k = data.loc[data["AttritionFlag"] == 1, "MonthlyIncome"].mean()
    g_b = data.loc[data["AttritionFlag"] == 0, "MonthlyIncome"].mean()
    if pd.notna(g_k) and pd.notna(g_b):
        arah = "lebih rendah" if g_k < g_b else "lebih tinggi"
        poin.append(
            f"**Gaji:** rata-rata gaji karyawan yang keluar **${g_k:,.0f}**, {arah} dari yang bertahan (**${g_b:,.0f}**)."
        )


def ke_html(teks: str) -> str:
    """Ubah **tebal** dan *miring* (gaya markdown) menjadi tag HTML untuk kotak insight."""
    teks = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", teks)
    return re.sub(r"\*(.+?)\*", r"<i>\1</i>", teks)


st.markdown(
    '<div class="insight-box">' + "<br>".join("• " + ke_html(p) for p in poin) + "</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "**Rekomendasi:** batasi lembur berlebihan, perkuat program *onboarding* dan pendampingan "
    "bagi karyawan di 2 tahun pertama, serta tinjau ulang skema gaji dan insentif untuk jabatan "
    "dengan attrition tinggi."
)
st.caption("Angka insight di atas dihitung ulang otomatis sesuai filter yang dipilih.")

with st.expander("📄 Lihat data (sesuai filter)"):
    st.dataframe(data, use_container_width=True, height=300)
