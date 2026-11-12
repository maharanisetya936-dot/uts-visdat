"""
clean_data.py
Skrip pembersihan data (data cleaning) untuk dataset
IBM HR Analytics Employee Attrition & Performance (Kaggle).

Input : data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv
Output: data/hr_attrition_clean.csv

Cara menjalankan (dari folder utama proyek):
    python data/clean_data.py
"""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
RAW_FILE = BASE / "raw" / "WA_Fn-UseC_-HR-Employee-Attrition.csv"
CLEAN_FILE = BASE / "hr_attrition_clean.csv"


def main() -> None:
    df = pd.read_csv(RAW_FILE)
    print(f"Data mentah      : {df.shape[0]} baris, {df.shape[1]} kolom")

    # 1. Cek data kosong dan duplikat
    print(f"Data kosong      : {int(df.isna().sum().sum())}")
    print(f"Baris duplikat   : {int(df.duplicated().sum())}")
    df = df.dropna().drop_duplicates()

    # 2. Buang kolom yang nilainya sama untuk semua baris (tidak informatif)
    konstan = [c for c in df.columns if df[c].nunique() == 1]
    df = df.drop(columns=konstan)
    print(f"Kolom dibuang    : {konstan}")

    # 3. Ubah kode angka (skala ordinal) menjadi label yang mudah dibaca
    skala_kepuasan = {1: "Low", 2: "Medium", 3: "High", 4: "Very High"}
    mapping = {
        "Education": {1: "Below College", 2: "College", 3: "Bachelor", 4: "Master", 5: "Doctor"},
        "EnvironmentSatisfaction": skala_kepuasan,
        "JobInvolvement": skala_kepuasan,
        "JobSatisfaction": skala_kepuasan,
        "RelationshipSatisfaction": skala_kepuasan,
        "WorkLifeBalance": {1: "Bad", 2: "Good", 3: "Better", 4: "Best"},
        "PerformanceRating": {1: "Low", 2: "Good", 3: "Excellent", 4: "Outstanding"},
    }
    for kolom, peta in mapping.items():
        df[kolom + "Label"] = df[kolom].map(peta)

    df["BusinessTravel"] = df["BusinessTravel"].replace(
        {"Travel_Rarely": "Travel Rarely", "Travel_Frequently": "Travel Frequently", "Non-Travel": "Non-Travel"}
    )

    # 4. Kolom bantu untuk analisis dan visualisasi
    df["AttritionFlag"] = (df["Attrition"] == "Yes").astype(int)  # 1 = keluar, 0 = bertahan
    df["AgeGroup"] = pd.cut(
        df["Age"], bins=[17, 25, 35, 45, 55, 60],
        labels=["18-25", "26-35", "36-45", "46-55", "56-60"],
    ).astype(str)
    df["TenureGroup"] = pd.cut(
        df["YearsAtCompany"], bins=[-1, 2, 5, 10, 20, 40],
        labels=["0-2 tahun", "3-5 tahun", "6-10 tahun", "11-20 tahun", ">20 tahun"],
    ).astype(str)
    df["IncomeGroup"] = pd.qcut(
        df["MonthlyIncome"], q=4, labels=["Rendah", "Menengah Bawah", "Menengah Atas", "Tinggi"]
    ).astype(str)

    # 5. Cek tipe data dan simpan
    df.to_csv(CLEAN_FILE, index=False)
    print(f"Data bersih      : {df.shape[0]} baris, {df.shape[1]} kolom")
    print(f"Disimpan ke      : {CLEAN_FILE.relative_to(BASE.parent)}")


if __name__ == "__main__":
    main()
