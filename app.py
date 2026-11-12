"""
Dashboard Analisis Attrition Karyawan
UTS Visualisasi Data - Universitas Dirgantara Marsekal Suryadarma
Dataset: IBM HR Analytics Employee Attrition & Performance (Kaggle)

Jalankan secara lokal:
    python -m streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ------------------------------------------------------------------
# Konfigurasi halaman dan palet warna (nuansa ungu - biru)
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Attrition Karyawan",
    page_icon="📊",
    layout="wide",
)

UNGU_TUA = "#4C1D95"
UNGU = "#7C3AED"
FUCHSIA = "#C026D3"        # warna "Keluar" (sorotan)
BIRU_TUA = "#1E3A8A"       # warna "Bertahan"
BIRU = "#3B82F6"
LAVENDER = "#EDE9FE"
ABU = "#94A3B8"
TEKS = "#1E1B4B"

PETA_WARNA = {"Keluar": FUCHSIA, "Bertahan": BIRU_TUA}
SKALA_HEATMAP = ["#EEF2FF", "#C4B5FD", UNGU, UNGU_TUA]

# Toolbar Plotly disembunyikan agar tidak menutupi grafik
KONFIG_GRAFIK = {"displayModeBar": False}

DATA_FILE = Path(__file__).parent / "data" / "hr_attrition_clean.csv"

# ------------------------------------------------------------------
# Gaya tampilan (CSS)
# ------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    .block-container {{padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1400px;}}
    footer {{visibility: hidden;}}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #F5F3FF 0%, #EEF2FF 100%);
        border-right: 1px solid #DDD6FE;
    }}
    .sidebar-title {{
        background: linear-gradient(135deg, {UNGU_TUA}, {BIRU_TUA});
        color: white; padding: 14px 16px; border-radius: 12px;
        font-weight: 700; font-size: 1.05rem; margin-bottom: 14px;
    }}

    /* Header banner */
    .hero {{
        background: linear-gradient(120deg, {UNGU_TUA} 0%, {UNGU} 45%, {BIRU} 100%);
        border-radius: 18px; padding: 28px 32px; color: white;
        box-shadow: 0 10px 30px rgba(76, 29, 149, 0.25); margin-bottom: 22px;
    }}
    .hero h1 {{color: white; font-size: 2.1rem; margin: 0 0 6px 0; padding: 0;}}
    .hero p {{color: #E0E7FF; font-size: 1rem; margin: 0;}}
    .hero .tag {{
        display: inline-block; background: rgba(255,255,255,0.18); color: white;
        padding: 4px 12px; border-radius: 999px; font-size: 0.8rem; margin-bottom: 10px;
    }}

    /* Kartu KPI */
    .kpi {{
        background: white; border-radius: 16px; padding: 18px 20px;
        border: 1px solid #E4E1F7; box-shadow: 0 4px 14px rgba(30, 58, 138, 0.08);
        border-top: 5px solid var(--aksen); height: 100%;
    }}
    .kpi .label {{color: #64748B; font-size: 0.85rem; font-weight: 600; letter-spacing: .3px;}}
    .kpi .value {{color: {TEKS}; font-size: 2rem; font-weight: 800; margin-top: 4px;}}
    .kpi .sub {{color: #64748B; font-size: 0.8rem; margin-top: 2px;}}

    /* Judul bagian */
    .section-title {{
        font-size: 1.15rem; font-weight: 700; color: {TEKS};
        border-left: 5px solid {UNGU}; padding-left: 10px; margin: 4px 0 2px 0;
    }}
    .section-sub {{color: #64748B; font-size: 0.85rem; margin: 0 0 4px 15px;}}

    /* Kartu wadah grafik */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: white; border-radius: 16px !important;
        border: 1px solid #E4E1F7 !important;
        box-shadow: 0 4px 14px rgba(30, 58, 138, 0.06);
    }}

    /* Kartu insight */
    .insight-grid {{display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px;}}
    .insight {{
        background: linear-gradient(135deg, #F5F3FF, #EFF6FF);
        border: 1px solid #DDD6FE; border-radius: 14px; padding: 14px 16px;
        color: {TEKS}; font-size: 0.92rem; line-height: 1.5;
    }}
    .insight .judul {{font-weight: 700; color: {UNGU_TUA}; margin-bottom: 4px;}}
    .rekomendasi {{
        background: linear-gradient(120deg, {UNGU_TUA}, {BIRU_TUA}); color: white;
        border-radius: 14px; padding: 16px 20px; margin-top: 14px; font-size: 0.95rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def gaya_grafik(fig, tinggi=360):
    """Gaya seragam untuk semua grafik Plotly."""
    fig.update_layout(
        height=tinggi,
        margin=dict(t=30, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color=TEKS, size=13),
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_xaxes(gridcolor="#EDE9FE", zeroline=False)
    fig.update_yaxes(gridcolor="#EDE9FE", zeroline=False)
    return fig


def judul(teks, sub=""):
    st.markdown(f'<div class="section-title">{teks}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="section-sub">{sub}</div>', unsafe_allow_html=True)


def kartu_kpi(kolom, label, nilai, sub, aksen):
    kolom.markdown(
        f'<div class="kpi" style="--aksen:{aksen}"><div class="label">{label}</div>'
        f'<div class="value">{nilai}</div><div class="sub">{sub}</div></div>',
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
st.sidebar.markdown('<div class="sidebar-title">🔎 Filter Data</div>', unsafe_allow_html=True)

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
st.sidebar.caption("Aloisius Gilang Putra Sadewa · 241053001")

data = df[
    df["Department"].isin(pilih_dept)
    & df["Gender"].isin(pilih_gender)
    & df["Age"].between(pilih_usia[0], pilih_usia[1])
]

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <span class="tag">HR Analytics · IBM Dataset</span>
        <h1>📊 Dashboard Analisis Attrition Karyawan</h1>
        <p>Mengapa karyawan memilih keluar dari perusahaan? Dashboard ini menelusuri pengaruh
        <b>lembur, masa kerja, jabatan, kepuasan kerja, dan gaji</b> terhadap tingkat
        <i>attrition</i> (karyawan yang keluar).</p>
    </div>
    """,
    unsafe_allow_html=True,
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
selisih = rate - rate_semua

if total < len(df) and abs(selisih) >= 0.05:
    arah = "di atas" if selisih > 0 else "di bawah"
    sub_rate = f"{abs(selisih):.1f} poin {arah} total ({rate_semua:.1f}%)"
else:
    sub_rate = "Persentase karyawan yang keluar"

k1, k2, k3, k4 = st.columns(4)
kartu_kpi(k1, "👥 TOTAL KARYAWAN", f"{total:,}", f"dari {len(df):,} karyawan", BIRU_TUA)
kartu_kpi(k2, "🚪 KARYAWAN KELUAR", f"{keluar:,}", f"{total - keluar:,} karyawan bertahan", FUCHSIA)
kartu_kpi(k3, "📉 TINGKAT ATTRITION", f"{rate:.1f}%", sub_rate, UNGU)
kartu_kpi(k4, "💰 RATA-RATA GAJI", f"${gaji:,.0f}", "gaji bulanan (USD)", BIRU)

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Baris 1: Line chart (masa kerja) + Donut chart (proporsi)
# ------------------------------------------------------------------
c1, c2 = st.columns([2, 1])

with c1:
    with st.container(border=True):
        judul("Tingkat Attrition berdasarkan Masa Kerja", "Garis putus-putus = rata-rata attrition")
        masa = data.copy()
        masa["MasaKerja"] = masa["YearsAtCompany"].clip(upper=20)
        tren = (
            masa.groupby("MasaKerja")
            .agg(Rate=("AttritionFlag", "mean"), Jumlah=("AttritionFlag", "size"))
            .reset_index()
        )
        tren["Rate"] = tren["Rate"] * 100
        fig_line = px.area(
            tren, x="MasaKerja", y="Rate", markers=True,
            hover_data={"Jumlah": True, "Rate": ":.1f"},
            labels={"MasaKerja": "Masa kerja (tahun, 20 = 20 tahun ke atas)", "Rate": "Attrition (%)"},
            color_discrete_sequence=[UNGU],
        )
        fig_line.update_traces(line=dict(width=3), fillcolor="rgba(124, 58, 237, 0.12)")
        fig_line.add_hline(
            y=rate, line_dash="dash", line_color=BIRU,
            annotation_text=f"Rata-rata {rate:.1f}%", annotation_position="top right",
            annotation_font_color=BIRU,
        )
        if not tren.empty:
            puncak = tren.loc[tren["Rate"].idxmax()]
            fig_line.add_annotation(
                x=puncak["MasaKerja"], y=puncak["Rate"],
                text=f"<b>Tertinggi: {puncak['Rate']:.0f}%</b>", showarrow=True, arrowhead=2,
                ay=-35, font=dict(color=UNGU_TUA), arrowcolor=UNGU_TUA,
            )
        st.plotly_chart(gaya_grafik(fig_line, 360), use_container_width=True, config=KONFIG_GRAFIK)

with c2:
    with st.container(border=True):
        judul("Proporsi Karyawan", "Keluar vs bertahan")
        proporsi = data["Status"].value_counts().reset_index()
        proporsi.columns = ["Status", "Jumlah"]
        fig_donut = px.pie(
            proporsi, names="Status", values="Jumlah", hole=0.62,
            color="Status", color_discrete_map=PETA_WARNA,
        )
        fig_donut.update_traces(
            textinfo="percent", textfont=dict(color="white", size=14),
            marker=dict(line=dict(color="white", width=3)),
        )
        fig_donut.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=-0.12, x=0.5, xanchor="center"),
            annotations=[dict(
                text=f"<b>{rate:.1f}%</b><br><span style='font-size:12px'>keluar</span>",
                x=0.5, y=0.5, font=dict(size=24, color=UNGU_TUA), showarrow=False,
            )],
        )
        st.plotly_chart(gaya_grafik(fig_donut, 360), use_container_width=True, config=KONFIG_GRAFIK)

# ------------------------------------------------------------------
# Baris 2: Bar chart (jabatan) + Heatmap (lembur x kepuasan kerja)
# ------------------------------------------------------------------
c3, c4 = st.columns(2)

with c3:
    with st.container(border=True):
        judul("Tingkat Attrition per Jabatan", "Ungu = di atas rata-rata, biru = di bawah rata-rata")
        jabatan = (
            data.groupby("JobRole")
            .agg(Rate=("AttritionFlag", "mean"), Jumlah=("AttritionFlag", "size"))
            .reset_index()
        )
        jabatan["Rate"] = jabatan["Rate"] * 100
        jabatan = jabatan.sort_values("Rate")
        jabatan["Kategori"] = jabatan["Rate"].apply(
            lambda r: "Di atas rata-rata" if r > rate else "Di bawah rata-rata"
        )
        fig_bar = px.bar(
            jabatan, x="Rate", y="JobRole", orientation="h", text="Rate", color="Kategori",
            color_discrete_map={"Di atas rata-rata": UNGU, "Di bawah rata-rata": BIRU},
            hover_data={"Jumlah": True, "Kategori": False},
            labels={"Rate": "Attrition (%)", "JobRole": ""},
        )
        fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside", marker_line_width=0)
        fig_bar.update_layout(
            showlegend=False, bargap=0.3,
            xaxis_range=[0, max(jabatan["Rate"].max() * 1.22, 5)],
        )
        st.plotly_chart(gaya_grafik(fig_bar, 400), use_container_width=True, config=KONFIG_GRAFIK)

with c4:
    with st.container(border=True):
        judul("Lembur × Kepuasan Kerja", "Semakin gelap warnanya, semakin tinggi attrition (%)")
        urutan_puas = ["Low", "Medium", "High", "Very High"]
        label_puas = {"Low": "Rendah", "Medium": "Sedang", "High": "Tinggi", "Very High": "Sangat Tinggi"}
        heat = data.pivot_table(
            index="Lembur", columns="JobSatisfactionLabel", values="AttritionFlag", aggfunc="mean"
        ) * 100
        heat = heat.reindex(columns=[k for k in urutan_puas if k in heat.columns])
        heat.columns = [label_puas[k] for k in heat.columns]
        fig_heat = px.imshow(
            heat.round(1), text_auto=".1f", aspect="auto",
            color_continuous_scale=SKALA_HEATMAP,
            labels=dict(x="Tingkat kepuasan kerja", y="", color="Attrition (%)"),
        )
        fig_heat.update_traces(textfont=dict(size=15))
        fig_heat.update_xaxes(side="bottom", showgrid=False)
        fig_heat.update_yaxes(showgrid=False)
        st.plotly_chart(gaya_grafik(fig_heat, 400), use_container_width=True, config=KONFIG_GRAFIK)

# ------------------------------------------------------------------
# Baris 3: Box plot (gaji)
# ------------------------------------------------------------------
with st.container(border=True):
    judul("Sebaran Gaji Bulanan: Keluar vs Bertahan", "Garis tengah kotak = median gaji")
    fig_box = px.box(
        data, x="MonthlyIncome", y="Status", color="Status", orientation="h",
        color_discrete_map=PETA_WARNA,
        category_orders={"Status": ["Bertahan", "Keluar"]},
        labels={"MonthlyIncome": "Gaji bulanan (USD)", "Status": ""},
        points="outliers",
    )
    fig_box.update_layout(showlegend=False)
    st.plotly_chart(gaya_grafik(fig_box, 280), use_container_width=True, config=KONFIG_GRAFIK)

# ------------------------------------------------------------------
# Storytelling: insight dinamis (ikut berubah sesuai filter)
# ------------------------------------------------------------------
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
judul("💡 Insight Utama", "Angka dihitung ulang otomatis sesuai filter yang dipilih")


def rate_of(mask):
    """Tingkat attrition (%) dan jumlah karyawan pada kelompok tertentu."""
    sub = data[mask]
    return (sub["AttritionFlag"].mean() * 100 if len(sub) else None), len(sub)


def banding(nama_b, a, b, n_a, n_b) -> str:
    """Kalimat perbandingan yang menyesuaikan arah selisih."""
    if a is None or b is None:
        return "tidak dapat dibandingkan karena salah satu kelompok tidak ada pada filter ini"
    if a > b:
        kata = f"lebih tinggi (<b>{a / b:.1f}×</b> lipat)" if b > 0 else "lebih tinggi"
    elif a < b:
        kata = "lebih rendah"
    else:
        kata = "sama"
    return f"<b>{a:.1f}%</b> (n={n_a}), {kata} dibanding {nama_b} <b>{b:.1f}%</b> (n={n_b})"


kartu = []
if keluar == 0:
    kartu.append(("Tidak ada yang keluar",
                  "Pada kombinasi filter ini tidak ada karyawan yang keluar, sehingga faktor pemicu tidak dapat dibandingkan."))
else:
    r_l, n_l = rate_of(data["OverTime"] == "Yes")
    r_t, n_t = rate_of(data["OverTime"] == "No")
    kartu.append(("⏰ Lembur", "Tingkat keluar karyawan yang lembur " + banding("yang tidak lembur", r_l, r_t, n_l, n_t) + "."))

    r_b, n_b = rate_of(data["YearsAtCompany"] <= 2)
    r_m, n_m = rate_of(data["YearsAtCompany"] > 10)
    kartu.append(("🆕 Masa Kerja", "Karyawan baru (0–2 tahun) " + banding("karyawan lama (>10 tahun)", r_b, r_m, n_b, n_m) + "."))

    # Peringkat jabatan hanya untuk jabatan dengan minimal 5 karyawan agar tidak menyesatkan
    jab_cukup = jabatan[jabatan["Jumlah"] >= 5]
    if len(jab_cukup) >= 2:
        hi, lo = jab_cukup.iloc[-1], jab_cukup.iloc[0]
        kartu.append(("💼 Jabatan",
                      f"<i>{hi['JobRole']}</i> memiliki attrition tertinggi (<b>{hi['Rate']:.1f}%</b>), "
                      f"sedangkan <i>{lo['JobRole']}</i> terendah (<b>{lo['Rate']:.1f}%</b>)."))

    g_k = data.loc[data["AttritionFlag"] == 1, "MonthlyIncome"].mean()
    g_b = data.loc[data["AttritionFlag"] == 0, "MonthlyIncome"].mean()
    if pd.notna(g_k) and pd.notna(g_b):
        arah_gaji = "lebih rendah" if g_k < g_b else "lebih tinggi"
        kartu.append(("💰 Gaji",
                      f"Rata-rata gaji karyawan yang keluar <b>${g_k:,.0f}</b>, {arah_gaji} dari yang bertahan "
                      f"(<b>${g_b:,.0f}</b>)."))

st.markdown(
    '<div class="insight-grid">'
    + "".join(f'<div class="insight"><div class="judul">{j}</div>{isi}</div>' for j, isi in kartu)
    + "</div>"
    + '<div class="rekomendasi"><b>🎯 Rekomendasi:</b> batasi lembur berlebihan, perkuat program '
      "<i>onboarding</i> dan pendampingan bagi karyawan di 2 tahun pertama, serta tinjau ulang skema "
      "gaji dan insentif untuk jabatan dengan attrition tinggi.</div>",
    unsafe_allow_html=True,
)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
with st.expander("📄 Lihat data (sesuai filter)"):
    st.dataframe(data, use_container_width=True, height=300)
