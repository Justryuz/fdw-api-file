from flask import Flask, jsonify, request
import requests as req
import os

app = Flask(__name__)

# === Konfigurasi ===
FDW_API_URL = "https://fdw.fama.gov.my/api/ab4363596e"
FDW_API_TOKEN = "570|BMaz4CZwesfJekAePuUDH4xg779cHxH1BPEIbuCqfa4e3dde"

# Mapping nama fail → filter
FILE_FILTERS = {
    "FDW_GBBS_MEDAN_GBBS_2026_DISESUAIKAN": {
        "created_state": "PERLIS",
        "created_year": "2026",
        "created_month": "SEPTEMBER",
    },
    "IBU_PEJABAT_2026_MAC": {
        "created_state": "IBU PEJABAT",
        "created_year": "2026",
        "created_month": "MAC",
    },
}


def fetch_fdw_data():
    """Fetch semua data dari FDW API."""
    headers = {
        "Authorization": f"Bearer {FDW_API_TOKEN}",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://fdw.fama.gov.my/",
        "Origin": "https://fdw.fama.gov.my",
    }
    response = req.get(FDW_API_URL, headers=headers, timeout=30)
    response.raise_for_status()
    result = response.json()
    if result.get("status") != 200:
        raise Exception(result.get("message", "FDW API error"))
    return result.get("data", [])


def apply_filter(data, filters):
    """Filter rekod berdasarkan created_state, created_year, created_month."""
    return [
        r for r in data
        if r.get("created_state", "").upper() == filters["created_state"].upper()
        and r.get("created_year", "") == filters["created_year"]
        and r.get("created_month", "").upper() == filters["created_month"].upper()
    ]


# ------------------------------------------------------------------
# ENDPOINTS
# ------------------------------------------------------------------

@app.route("/api/files", methods=["GET"])
def list_files():
    """GET /api/files — senarai fail yang tersedia"""
    return jsonify({
        "status": 200,
        "message": "Success",
        "files": list(FILE_FILTERS.keys())
    })


@app.route("/api/data", methods=["GET"])
def get_all_filtered():
    """GET /api/data — semua rekod untuk kedua-dua fail"""
    try:
        all_data = fetch_fdw_data()
        result = {}
        for nama_fail, filters in FILE_FILTERS.items():
            result[nama_fail] = apply_filter(all_data, filters)
        return jsonify({
            "status": 200,
            "message": "Success",
            "total": sum(len(v) for v in result.values()),
            "data": result
        })
    except Exception as e:
        return jsonify({"status": 500, "message": str(e)}), 500


@app.route("/api/data/<nama_fail>", methods=["GET"])
def get_by_file(nama_fail):
    """GET /api/data/<nama_fail> — rekod untuk satu fail sahaja"""
    filters = FILE_FILTERS.get(nama_fail.upper())
    if not filters:
        available = list(FILE_FILTERS.keys())
        return jsonify({
            "status": 404,
            "message": f"Nama fail tidak dijumpai. Guna salah satu: {available}"
        }), 404

    try:
        all_data = fetch_fdw_data()
        filtered = apply_filter(all_data, filters)
        return jsonify({
            "status": 200,
            "message": "Success",
            "fail": nama_fail,
            "total": len(filtered),
            "data": filtered
        })
    except Exception as e:
        return jsonify({"status": 500, "message": str(e)}), 500


# Vercel serverless — expose sebagai `app`

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
