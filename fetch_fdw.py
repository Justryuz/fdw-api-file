import requests
import json

# === Konfigurasi ===
API_URL = "https://fdw.fama.gov.my/api/ab4363596e"
API_TOKEN = "570|BMaz4CZwesfJekAePuUDH4xg779cHxH1BPEIbuCqfa4e3dde"

# Filter berdasarkan dua fail Excel:
# 1. FDW_GBBS_MEDAN_GBBS_2026_DISESUAIKAN.xlsx  → created_state=PERLIS, created_year=2026, created_month=SEPTEMBER
# 2. IBU PEJABAT-2026-MAC-...xlsx               → created_state=IBU PEJABAT, created_year=2026, created_month=MAC
TARGET_FILES = [
    {
        "nama_fail": "FDW_GBBS_MEDAN_GBBS_2026_DISESUAIKAN.xlsx",
        "created_state": "PERLIS",
        "created_year": "2026",
        "created_month": "SEPTEMBER",
    },
    {
        "nama_fail": "IBU PEJABAT-2026-MAC.xlsx",
        "created_state": "IBU PEJABAT",
        "created_year": "2026",
        "created_month": "MAC",
    },
]


def fetch_data():
    """Fetch semua data dari API."""
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json",
    }

    print(f"Fetching data dari: {API_URL}")
    response = requests.get(API_URL, headers=headers)
    response.raise_for_status()

    result = response.json()

    if result.get("status") != 200:
        raise Exception(f"API error: {result.get('message')}")

    data = result.get("data", [])
    print(f"Jumlah rekod keseluruhan: {len(data)}")
    return data


def filter_by_files(data, target_files):
    """Filter rekod berdasarkan senarai fail target."""
    filtered = {}

    for target in target_files:
        nama_fail = target["nama_fail"]
        filtered[nama_fail] = [
            record for record in data
            if record.get("created_state", "").upper() == target["created_state"].upper()
            and record.get("created_year", "") == target["created_year"]
            and record.get("created_month", "").upper() == target["created_month"].upper()
        ]
        print(f"\nFail: {nama_fail}")
        print(f"  Rekod ditemui: {len(filtered[nama_fail])}")

    return filtered


def main():
    # 1. Tarik data dari API
    all_data = fetch_data()

    # 2. Filter mengikut fail
    filtered_data = filter_by_files(all_data, TARGET_FILES)

    # 3. Simpan output ke JSON
    output_file = "output_filtered.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)

    print(f"\nData disimpan ke: {output_file}")

    # 4. Preview rekod pertama tiap-tiap fail
    for nama_fail, records in filtered_data.items():
        if records:
            print(f"\n--- Preview rekod pertama: {nama_fail} ---")
            first = records[0]
            for key, value in first.items():
                if value:  # tunjuk field yang ada nilai je
                    print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
