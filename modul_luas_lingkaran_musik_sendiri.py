# -*- coding: utf-8 -*-
"""
MODUL INTERAKTIF LUAS LINGKARAN - KELAS VI SD/MI
Jalankan:  streamlit run app.py

Struktur file:
  1. KONFIGURASI GURU        -> identitas sekolah, KKM, tautan video, PIN guru
  2. BANK MATERI & TOPIK     -> langkah materi + rekomendasi adaptif
  3. BANK SOAL               -> 10 soal pilihan ganda + 5 soal esai (mudah diedit)
  4. FUNGSI PENILAIAN        -> logika murni (tanpa Streamlit)
  5. TAMPILAN (UI)           -> CSS pink-biru-kuning, latar, musik/suara, halaman-halaman, router

Data siswa hanya disimpan di st.session_state (sementara, selama sesi berjalan).
"""
import html
import base64
import json
import math
import re
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# 1. KONFIGURASI GURU  (EDIT BAGIAN INI)
# ============================================================
NAMA_SEKOLAH = ""
NAMA_GURU = "[ISI: Nama Guru]"                       # TODO GURU
KKM = 75                                             # TODO GURU: batas ketuntasan (0-100)
GURU_PIN = "guru123"                                 # TODO GURU: ganti PIN panel guru

# Tautan video. Kosongkan ("") jika belum ada; aplikasi akan menampilkan placeholder.
# Contoh format: "https://www.youtube.com/watch?v=XXXXXXXXXXX"
VIDEO_UTAMA = ""                                     # TODO GURU: video materi inti
VIDEO_PENCARIAN = "https://www.youtube.com/results?search_query=luas+lingkaran+kelas+6+SD"

# TODO GURU: ganti dengan rumusan CP/tujuan resmi dari LKPD / kurikulum sekolah.
CAPAIAN_PEMBELAJARAN = [
    "Mengenali jari-jari dan diameter lingkaran.",
    "Menjelaskan hubungan diameter dan jari-jari.",
    "Memilih nilai π yang sesuai untuk perhitungan.",
    "Menghitung luas lingkaran jika diketahui jari-jari atau diameter.",
    "Menyelesaikan masalah luas lingkaran dalam kehidupan sehari-hari.",
    "Menjelaskan langkah penyelesaian dengan bahasamu sendiri.",
]

LETTERS = "ABCD"

# ============================================================
# 2. BANK MATERI & TOPIK REKOMENDASI
# ============================================================
# Urutan langkah Materi Inti (indeks dipakai oleh tombol rekomendasi).
MATERI_STEPS = [
    ("⭕", "Mengenal lingkaran"),            # 0
    ("↔️", "Jari-jari dan diameter"),         # 1
    ("📐", "Rumus luas lingkaran"),          # 2
    ("🔢", "Nilai π (pi)"),                  # 3
    ("🧮", "Contoh soal dan penyelesaian"),  # 4
    ("🎛️", "Coba sendiri: alat hitung"),     # 5
    ("🎬", "Video pembelajaran"),            # 6
]

# Setiap topik terhubung ke satu langkah materi. Isi "video" dengan tautan jika ada.
TOPICS = {
    "unsur": {
        "label": "Titik pusat, jari-jari, dan diameter",
        "step": 0, "video": "",               # TODO GURU: tautan video topik ini
        "tip": "Ulangi bagian unsur-unsur lingkaran: titik pusat, jari-jari, dan diameter.",
    },
    "hubungan": {
        "label": "Hubungan jari-jari dan diameter",
        "step": 1, "video": "",               # TODO GURU
        "tip": "Ingat: d = 2 × r dan r = d ÷ 2. Cari jari-jari lebih dulu sebelum memakai rumus luas.",
    },
    "rumus": {
        "label": "Rumus luas lingkaran",
        "step": 2, "video": "",               # TODO GURU
        "tip": "Luas lingkaran: L = π × r × r. Jangan tertukar dengan rumus keliling (2 × π × r).",
    },
    "pi": {
        "label": "Memilih nilai π",
        "step": 3, "video": "",               # TODO GURU
        "tip": "Pakai π = 22/7 jika r atau d kelipatan 7; pakai π = 3,14 untuk ukuran lainnya.",
    },
    "hitung": {
        "label": "Contoh perhitungan luas lingkaran",
        "step": 4, "video": "",               # TODO GURU
        "tip": "Pelajari contoh penyelesaian langkah demi langkah, lalu perhatikan perkaliannya.",
    },
    "cerita": {
        "label": "Luas lingkaran dalam soal cerita",
        "step": 4, "video": "",               # TODO GURU
        "tip": "Tulis diketahui dan ditanya, ubah diameter ke jari-jari bila perlu, lalu hitung luasnya.",
    },
}

# ============================================================
# 3. BANK SOAL
# ============================================================
# ---- 3a. PILIHAN GANDA (10 soal) ----------------------------
# answer      = indeks jawaban benar (0=A, 1=B, 2=C, 3=D)
# miskonsepsi = {indeks_opsi_salah: penjelasan singkat} (opsional)
# visual      = gambar lingkaran yang HANYA menampilkan data yang diketahui soal
# CATATAN GURU: soal 1-6 berasal dari kode asli (soal tipe isian/ganda kompleks diubah
# menjadi 4 opsi A-D). Soal 7-10 adalah DRAF BARU buatan penyusun aplikasi -> ganti/periksa.
MC_QUESTIONS = [
    {   # kode asli (q1)
        "id": "mc1", "topic": "hitung",
        "question": "Sebuah piring berbentuk lingkaran memiliki jari-jari 7 cm. Berapa luas permukaannya?",
        "options": ["44 cm²", "154 cm²", "308 cm²", "49 cm²"],
        "answer": 1,
        "explanation": "Luas lingkaran dihitung dengan L = π × r × r. Karena r = 7 (kelipatan 7), gunakan π = 22/7.",
        "steps": ["Diketahui: r = 7 cm.", "L = π × r × r", "L = 22/7 × 7 × 7", "L = 22 × 7 = 154 cm²"],
        "miskonsepsi": {
            0: "44 cm² adalah hasil keliling (2 × 22/7 × 7). Soal ini menanyakan luas.",
            2: "308 muncul jika hasil luas dikalikan 2. Rumus luas tidak memakai angka 2.",
            3: "49 hanya r × r. Kamu belum mengalikan dengan π.",
        },
        "visual": {"radius": 7, "show_r": True, "show_d": False},
    },
    {   # kode asli (q2)
        "id": "mc2", "topic": "rumus",
        "question": "Rumus yang tepat untuk menghitung luas lingkaran adalah …",
        "options": ["L = π × r", "L = 2 × π × r", "L = π × r × r", "L = π × d"],
        "answer": 2,
        "explanation": "Luas lingkaran dihitung dengan L = π × r², yaitu π dikali jari-jari dikali jari-jari.",
        "steps": ["Luas = π × r × r.", "Rumus 2 × π × r adalah rumus keliling, bukan luas."],
        "miskonsepsi": {
            0: "π × r hanya mengalikan satu kali jari-jari. Luas membutuhkan r × r.",
            1: "2 × π × r adalah rumus keliling lingkaran.",
            3: "π × d adalah rumus keliling juga (d = 2 × r).",
        },
    },
    {   # kode asli (q3, tipe 'multi' diubah menjadi ganda 4 opsi)
        "id": "mc3", "topic": "pi",
        "question": (
            "Perhatikan pernyataan tentang pemilihan nilai π berikut.\n\n"
            "(1) π = 22/7 dapat digunakan jika jari-jari atau diameter merupakan kelipatan 7.\n\n"
            "(2) π = 3,14 dapat digunakan untuk ukuran yang bukan kelipatan 7.\n\n"
            "(3) Luas lingkaran selalu sama dengan 2 × π × r.\n\n"
            "(4) Jika diameter diketahui, jari-jari diperoleh dengan membagi diameter dengan 2.\n\n"
            "Pernyataan yang benar adalah …"
        ),
        "options": ["(1), (2), dan (3)", "(1), (2), dan (4)", "(2), (3), dan (4)", "(1), (3), dan (4)"],
        "answer": 1,
        "explanation": ("Pernyataan (1), (2), dan (4) benar. Pernyataan (3) adalah rumus keliling, bukan rumus luas. "
                        "Dalam perhitungan sekolah, π = 22/7 praktis untuk ukuran kelipatan 7 dan π = 3,14 untuk ukuran lainnya."),
        "steps": ["Periksa tiap pernyataan satu per satu.", "(3) salah karena 2 × π × r adalah keliling.",
                  "Jadi yang benar: (1), (2), dan (4)."],
        "miskonsepsi": {
            0: "Pernyataan (3) salah: 2 × π × r adalah rumus keliling.",
            2: "Pernyataan (1) sebenarnya benar, dan pernyataan (3) salah.",
            3: "Pernyataan (2) benar dan pernyataan (3) salah.",
        },
    },
    {   # kode asli (q4)
        "id": "mc4", "topic": "hubungan",
        "question": "Sebuah pizza memiliki diameter 20 cm. Berapa luas pizza tersebut?",
        "options": ["314 cm²", "1.256 cm²", "62,8 cm²", "100 cm²"],
        "answer": 0,
        "explanation": "Diameter harus diubah dulu menjadi jari-jari: r = 20 ÷ 2 = 10 cm. Karena 10 bukan kelipatan 7, gunakan π = 3,14.",
        "steps": ["Diketahui: d = 20 cm, sehingga r = 20 ÷ 2 = 10 cm.", "L = 3,14 × 10 × 10", "L = 314 cm²"],
        "miskonsepsi": {
            1: "1.256 muncul jika diameter (20) langsung dipakai sebagai jari-jari. Bagi 2 dulu!",
            2: "62,8 adalah keliling (3,14 × 20). Soal ini menanyakan luas.",
            3: "100 hanya r × r. Kamu belum mengalikan dengan π.",
        },
        "visual": {"radius": 10, "show_r": False, "show_d": True},
    },
    {   # kode asli (q5)  -- TODO GURU: kalimat asli "Tutup taman" mungkin salah ketik (Tugu? Tanah?). Dipertahankan apa adanya.
        "id": "mc5", "topic": "hubungan",
        "question": "Tutup taman berbentuk lingkaran memiliki diameter 28 m. Berapakah jari-jarinya?",
        "options": ["7 m", "14 m", "28 m", "56 m"],
        "answer": 1,
        "explanation": "Jari-jari adalah setengah diameter. Jadi r = 28 ÷ 2 = 14 m.",
        "steps": ["Diketahui: d = 28 m.", "r = d ÷ 2", "r = 28 ÷ 2 = 14 m"],
        "miskonsepsi": {
            0: "7 m adalah seperempat diameter. Jari-jari adalah setengah diameter.",
            2: "28 m adalah diameter itu sendiri, bukan jari-jari.",
            3: "56 m adalah dua kali diameter. Seharusnya dibagi 2.",
        },
        "visual": {"radius": 14, "show_r": False, "show_d": True},
    },
    {   # kode asli (q6)
        "id": "mc6", "topic": "cerita",
        "question": "Sebuah taman bundar memiliki jari-jari 14 m. Berapa luas taman tersebut?",
        "options": ["88 m²", "616 m²", "1.232 m²", "196 m²"],
        "answer": 1,
        "explanation": "r = 14 m (kelipatan 7), maka gunakan π = 22/7.",
        "steps": ["Diketahui: r = 14 m.", "L = 22/7 × 14 × 14", "L = 22 × 2 × 14 = 616 m²"],
        "miskonsepsi": {
            0: "88 m² adalah keliling (2 × 22/7 × 14). Soal ini menanyakan luas.",
            2: "1.232 adalah dua kali luas yang benar. Rumus luas tidak memakai angka 2.",
            3: "196 hanya r × r. Kamu belum mengalikan dengan π.",
        },
        "visual": {"radius": 14, "show_r": True, "show_d": False},
    },
    {   # DRAF BARU -> TODO GURU: ganti/periksa
        "id": "mc7", "topic": "unsur",
        "question": "Garis lurus dari titik pusat lingkaran ke tepi lingkaran disebut …",
        "options": ["diameter", "jari-jari", "titik pusat", "keliling"],
        "answer": 1,
        "explanation": "Garis dari titik pusat ke tepi lingkaran adalah jari-jari (r).",
        "steps": ["Jari-jari: pusat → tepi.", "Diameter: tepi → tepi melalui pusat."],
        "miskonsepsi": {
            0: "Diameter melewati titik pusat dan menghubungkan dua titik di tepi lingkaran.",
            2: "Titik pusat adalah titik di tengah lingkaran, bukan garis.",
            3: "Keliling adalah panjang garis tepi lingkaran.",
        },
        "visual": {"radius": 6, "show_r": True, "show_d": False},
    },
    {   # DRAF BARU -> TODO GURU: ganti/periksa
        "id": "mc8", "topic": "unsur",
        "question": "Sebuah jam dinding berbentuk lingkaran memiliki jari-jari 15 cm. Berapa diameter jam dinding tersebut?",
        "options": ["7,5 cm", "15 cm", "30 cm", "45 cm"],
        "answer": 2,
        "explanation": "Diameter adalah dua kali jari-jari.",
        "steps": ["Diketahui: r = 15 cm.", "d = 2 × r", "d = 2 × 15 = 30 cm"],
        "miskonsepsi": {
            0: "7,5 cm adalah setengah jari-jari. Diameter justru dua kali jari-jari.",
            1: "15 cm adalah jari-jari itu sendiri.",
            3: "45 cm tidak sesuai: d = 2 × r, bukan 3 × r.",
        },
    },
    {   # DRAF BARU -> TODO GURU: ganti/periksa
        "id": "mc9", "topic": "pi",
        "question": "Sebuah roda memiliki jari-jari 10 cm. Nilai π yang paling sesuai untuk menghitung luasnya adalah …",
        "options": ["22/7, karena 10 kelipatan 7", "3,14, karena 10 bukan kelipatan 7",
                    "22/7, karena hasilnya selalu lebih tepat", "3,14, karena 10 adalah bilangan genap"],
        "answer": 1,
        "explanation": "10 bukan kelipatan 7, sehingga perhitungan lebih mudah memakai π = 3,14.",
        "steps": ["Cek: apakah 10 kelipatan 7? Tidak.", "Pakai π = 3,14.", "L = 3,14 × 10 × 10 = 314 cm²"],
        "miskonsepsi": {
            0: "10 bukan kelipatan 7 (kelipatan 7: 7, 14, 21, ...).",
            2: "Kedua nilai π adalah pendekatan; yang menentukan adalah kemudahan hitung sesuai ukuran.",
            3: "Genap atau ganjil tidak menentukan pilihan π. Yang dilihat: kelipatan 7 atau bukan.",
        },
    },
    {   # DRAF BARU -> TODO GURU: ganti/periksa
        "id": "mc10", "topic": "cerita",
        "question": "Sebuah kolam ikan berbentuk lingkaran berdiameter 42 m. Berapa luas permukaan air kolam tersebut?",
        "options": ["132 m²", "1.386 m²", "2.772 m²", "5.544 m²"],
        "answer": 1,
        "explanation": "Ubah diameter menjadi jari-jari lebih dulu: r = 42 ÷ 2 = 21 m. Karena 21 kelipatan 7, gunakan π = 22/7.",
        "steps": ["Diketahui: d = 42 m, sehingga r = 21 m.", "L = 22/7 × 21 × 21", "L = 22 × 3 × 21 = 1.386 m²"],
        "miskonsepsi": {
            0: "132 m² adalah keliling (22/7 × 42). Soal ini menanyakan luas.",
            2: "2.772 adalah dua kali luas yang benar. Rumus luas tidak memakai angka 2.",
            3: "5.544 muncul jika diameter (42) dipakai sebagai jari-jari. Bagi 2 dulu!",
        },
        "visual": {"radius": 21, "show_r": False, "show_d": True},
    },
]


# ---- 3b. ESAI / PEMANTAPAN (5 soal) -------------------------
def N(n):
    """Pola regex untuk angka utuh n (tidak cocok dengan 128 jika n = 28)."""
    return rf"(?<![\d.,]){n}(?!\d)"


PAT_RUMUS = r"\bpi\b|r\s*x\s*r|r\s*2|luas lingkaran|(?<![a-z])l\s*=|luas\s*="
PAT_PI_227 = r"22\s*/\s*7"
PAT_PI_314 = r"3[,.]14"
PAT_M2 = r"(?<![a-z])m2(?!\d)|meter persegi"
PAT_CM2 = r"(?<![a-z])cm2(?!\d)|sentimeter persegi|cm persegi"

# Rubrik: tiap kriteria diperiksa otomatis dari angka/kata kunci. Guru dapat mengubah
# bobot ("points"), pola ("patterns") dan teks umpan balik ("ok"/"fail"/"partial").
# kind = "contains" (ada salah satu pola) | "final" (cek angka jawaban akhir)
# CATATAN GURU: esai 1 berasal dari kode asli. Esai 2-5 adalah DRAF BARU -> ganti/periksa.
ESSAY_QUESTIONS = [
    {   # kode asli (soal esai no. 7)
        "id": "es1", "topic": "hitung",
        "question": ("Sebuah taman berbentuk lingkaran memiliki diameter 28 meter. Pengelola ingin menanami "
                     "seluruh permukaan taman dengan rumput. Berapa luas daerah yang akan ditanami rumput?"),
        "hint": "Tuliskan: diketahui, ditanya, rumus/operasi yang digunakan, langkah perhitungan, dan kesimpulan.",
        "answer": 616.0, "alt": {"value": 615.44, "credit": 0.5, "note": "Hasil 615,44 memakai π = 3,14. Karena r = 14 kelipatan 7, lebih tepat π = 22/7 (hasil 616)."},
        "answer_text": "616 m²",
        "needs_teacher": False,
        "rubric": [
            {"label": "Menuliskan yang diketahui (diameter 28 m)", "points": 10, "kind": "contains", "topic": "hubungan",
             "patterns": [N(28)], "ok": "Kamu menuliskan ukuran diameter taman.", "fail": "Tuliskan dulu yang diketahui: diameter taman = 28 m."},
            {"label": "Mengubah diameter menjadi jari-jari (r = 14 m)", "points": 20, "kind": "contains", "topic": "hubungan",
             "patterns": [N(14)], "ok": "Bagus, kamu mencari jari-jari lebih dulu.", "fail": "Diameter harus dibagi 2 dulu: r = 28 ÷ 2 = 14 m."},
            {"label": "Menuliskan rumus luas lingkaran", "points": 15, "kind": "contains", "topic": "rumus",
             "patterns": [PAT_RUMUS], "ok": "Rumus luasmu sudah muncul.", "fail": "Tuliskan rumus: L = π × r × r."},
            {"label": "Memilih π = 22/7 (r = 14 kelipatan 7)", "points": 10, "kind": "contains", "topic": "pi",
             "patterns": [PAT_PI_227], "ok": "Pilihan π = 22/7 sudah tepat.", "fail": "Karena 14 kelipatan 7, gunakan π = 22/7."},
            {"label": "Hasil akhir luas benar (616)", "points": 35, "kind": "final", "topic": "hitung",
             "ok": "Jawaban akhirmu benar.", "fail": "Periksa lagi perkaliannya: 22/7 × 14 × 14 = 616.",
             "partial": "Angkamu mendekati, tetapi nilai π kurang sesuai."},
            {"label": "Satuan luas (m²)", "points": 10, "kind": "contains", "topic": "hitung",
             "patterns": [PAT_M2], "ok": "Satuan m² sudah ada.", "fail": "Luas memakai satuan persegi, yaitu m²."},
        ],
        "solution": ["Diketahui: d = 28 m. Ditanya: luas taman (L).",
                     "Cari jari-jari: r = d ÷ 2 = 28 ÷ 2 = 14 m.",
                     "Karena 14 kelipatan 7, gunakan π = 22/7.",
                     "L = π × r × r = 22/7 × 14 × 14 = 616 m².",
                     "Kesimpulan: luas daerah yang ditanami rumput adalah 616 m²."],
    },
    {   # DRAF BARU
        "id": "es2", "topic": "rumus",
        "question": "Sebuah roda sepeda berbentuk lingkaran dengan jari-jari 21 cm. Hitunglah luas lingkaran yang dibentuk roda tersebut!",
        "hint": "Tuliskan: diketahui, rumus, langkah perhitungan, dan kesimpulan.",
        "answer": 1386.0, "alt": {"value": 1384.74, "credit": 0.5, "note": "Hasil 1.384,74 memakai π = 3,14. Karena r = 21 kelipatan 7, lebih tepat π = 22/7 (hasil 1.386)."},
        "answer_text": "1.386 cm²", "needs_teacher": False,
        "rubric": [
            {"label": "Menuliskan yang diketahui (r = 21 cm)", "points": 10, "kind": "contains", "topic": "unsur",
             "patterns": [N(21)], "ok": "Kamu menuliskan jari-jari roda.", "fail": "Tuliskan yang diketahui: r = 21 cm."},
            {"label": "Menuliskan rumus luas lingkaran", "points": 20, "kind": "contains", "topic": "rumus",
             "patterns": [PAT_RUMUS], "ok": "Rumus luasmu sudah muncul.", "fail": "Tuliskan rumus: L = π × r × r."},
            {"label": "Memilih π = 22/7 (21 kelipatan 7)", "points": 15, "kind": "contains", "topic": "pi",
             "patterns": [PAT_PI_227], "ok": "Pilihan π = 22/7 sudah tepat.", "fail": "Karena 21 kelipatan 7, gunakan π = 22/7."},
            {"label": "Hasil akhir luas benar (1.386)", "points": 40, "kind": "final", "topic": "hitung",
             "ok": "Jawaban akhirmu benar.", "fail": "Periksa lagi: 22/7 × 21 × 21 = 22 × 3 × 21 = 1.386.",
             "partial": "Angkamu mendekati, tetapi nilai π kurang sesuai."},
            {"label": "Satuan luas (cm²)", "points": 15, "kind": "contains", "topic": "hitung",
             "patterns": [PAT_CM2], "ok": "Satuan cm² sudah ada.", "fail": "Luas memakai satuan persegi, yaitu cm²."},
        ],
        "solution": ["Diketahui: r = 21 cm. Ditanya: luas (L).", "Karena 21 kelipatan 7, gunakan π = 22/7.",
                     "L = π × r × r = 22/7 × 21 × 21 = 1.386 cm².", "Kesimpulan: luas lingkaran roda adalah 1.386 cm²."],
    },
    {   # DRAF BARU
        "id": "es3", "topic": "pi",
        "question": "Sebuah jam dinding berbentuk lingkaran memiliki diameter 30 cm. Berapa luas permukaan muka jam tersebut?",
        "hint": "Jelaskan juga mengapa kamu memilih nilai π tertentu.",
        "answer": 706.5, "alt": {"value": 707.14, "credit": 0.5, "note": "Hasil 707,14 memakai π = 22/7. Karena r = 15 bukan kelipatan 7, lebih tepat π = 3,14 (hasil 706,5)."},
        "answer_text": "706,5 cm²", "needs_teacher": False,
        "rubric": [
            {"label": "Menuliskan yang diketahui (d = 30 cm)", "points": 10, "kind": "contains", "topic": "unsur",
             "patterns": [N(30)], "ok": "Kamu menuliskan diameter jam.", "fail": "Tuliskan yang diketahui: d = 30 cm."},
            {"label": "Mengubah diameter menjadi jari-jari (r = 15 cm)", "points": 20, "kind": "contains", "topic": "hubungan",
             "patterns": [N(15)], "ok": "Bagus, kamu mencari jari-jari lebih dulu.", "fail": "Bagi diameter dengan 2: r = 30 ÷ 2 = 15 cm."},
            {"label": "Menuliskan rumus luas lingkaran", "points": 15, "kind": "contains", "topic": "rumus",
             "patterns": [PAT_RUMUS], "ok": "Rumus luasmu sudah muncul.", "fail": "Tuliskan rumus: L = π × r × r."},
            {"label": "Memilih π = 3,14 (15 bukan kelipatan 7)", "points": 10, "kind": "contains", "topic": "pi",
             "patterns": [PAT_PI_314], "ok": "Pilihan π = 3,14 sudah tepat.", "fail": "Karena 15 bukan kelipatan 7, gunakan π = 3,14."},
            {"label": "Hasil akhir luas benar (706,5)", "points": 35, "kind": "final", "topic": "hitung",
             "ok": "Jawaban akhirmu benar.", "fail": "Periksa lagi: 3,14 × 15 × 15 = 706,5.",
             "partial": "Angkamu mendekati, tetapi nilai π kurang sesuai."},
            {"label": "Satuan luas (cm²)", "points": 10, "kind": "contains", "topic": "hitung",
             "patterns": [PAT_CM2], "ok": "Satuan cm² sudah ada.", "fail": "Luas memakai satuan persegi, yaitu cm²."},
        ],
        "solution": ["Diketahui: d = 30 cm. Ditanya: luas (L).", "r = 30 ÷ 2 = 15 cm.",
                     "15 bukan kelipatan 7, gunakan π = 3,14.", "L = 3,14 × 15 × 15 = 706,5 cm².",
                     "Kesimpulan: luas muka jam adalah 706,5 cm²."],
    },
    {   # DRAF BARU (konseptual: penjelasan perlu dibaca guru)
        "id": "es4", "topic": "hubungan",
        "question": ("Pizza berdiameter 20 cm. Dani langsung memasukkan angka 20 ke rumus L = π × r × r. "
                     "Apakah cara Dani sudah benar? Jelaskan alasanmu, lalu hitunglah luas pizza yang benar!"),
        "hint": "Tulis jawaban 'benar/salah' beserta alasannya, lalu langkah perhitungan yang benar.",
        "answer": 314.0, "alt": None, "answer_text": "Cara Dani belum benar; luas pizza = 314 cm²",
        "needs_teacher": True,
        "rubric": [
            {"label": "Menyatakan bahwa cara Dani belum benar", "points": 25, "kind": "contains", "topic": "rumus",
             "patterns": [r"tidak (benar|tepat|boleh|bisa|sesuai)|belum (benar|tepat)|salah|keliru"],
             "ok": "Kamu menyatakan cara Dani belum benar.", "fail": "Nyatakan dengan jelas apakah cara Dani benar atau salah."},
            {"label": "Menjelaskan bahwa 20 adalah diameter (bukan jari-jari)", "points": 20, "kind": "contains", "topic": "hubungan",
             "patterns": [r"diameter"], "ok": "Kamu menyebut bahwa 20 adalah diameter.", "fail": "Jelaskan bahwa 20 cm adalah diameter, sedangkan rumus memakai jari-jari."},
            {"label": "Mencari jari-jari yang benar (r = 10 cm)", "points": 15, "kind": "contains", "topic": "hubungan",
             "patterns": [N(10)], "ok": "Jari-jari 10 cm sudah muncul.", "fail": "Bagi diameter dengan 2: r = 20 ÷ 2 = 10 cm."},
            {"label": "Hasil akhir luas benar (314)", "points": 30, "kind": "final", "topic": "hitung",
             "ok": "Jawaban akhirmu benar.", "fail": "Periksa lagi: 3,14 × 10 × 10 = 314.", "partial": ""},
            {"label": "Satuan luas (cm²)", "points": 10, "kind": "contains", "topic": "hitung",
             "patterns": [PAT_CM2], "ok": "Satuan cm² sudah ada.", "fail": "Luas memakai satuan persegi, yaitu cm²."},
        ],
        "solution": ["Cara Dani belum benar karena 20 cm adalah diameter, sedangkan rumus memakai jari-jari.",
                     "r = d ÷ 2 = 20 ÷ 2 = 10 cm.", "Pakai π = 3,14 karena 10 bukan kelipatan 7.",
                     "L = 3,14 × 10 × 10 = 314 cm²."],
    },
    {   # DRAF BARU
        "id": "es5", "topic": "cerita",
        "question": ("Dasar sebuah kolam berbentuk lingkaran dengan jari-jari 7 m akan dipasangi keramik. "
                     "Harga keramik Rp10.000 per m². Berapa biaya yang diperlukan untuk memasang keramik di seluruh dasar kolam?"),
        "hint": "Hitung luas dasar kolam lebih dulu, baru hitung biayanya.",
        "answer": 1540000.0, "alt": None, "answer_text": "Rp1.540.000", "needs_teacher": False,
        "rubric": [
            {"label": "Menuliskan yang diketahui (r = 7 m)", "points": 10, "kind": "contains", "topic": "unsur",
             "patterns": [N(7)], "ok": "Kamu menuliskan jari-jari kolam.", "fail": "Tuliskan yang diketahui: r = 7 m dan harga Rp10.000 per m²."},
            {"label": "Menuliskan rumus luas lingkaran", "points": 10, "kind": "contains", "topic": "rumus",
             "patterns": [PAT_RUMUS], "ok": "Rumus luasmu sudah muncul.", "fail": "Tuliskan rumus: L = π × r × r."},
            {"label": "Memilih π = 22/7 (7 kelipatan 7)", "points": 10, "kind": "contains", "topic": "pi",
             "patterns": [PAT_PI_227], "ok": "Pilihan π = 22/7 sudah tepat.", "fail": "Karena 7 kelipatan 7, gunakan π = 22/7."},
            {"label": "Menghitung luas dasar kolam (154 m²)", "points": 25, "kind": "contains", "topic": "hitung",
             "patterns": [N(154)], "ok": "Luas dasar kolam 154 m² sudah muncul.", "fail": "Hitung luas dulu: 22/7 × 7 × 7 = 154 m²."},
            {"label": "Hasil akhir biaya benar (Rp1.540.000)", "points": 35, "kind": "final", "topic": "cerita",
             "ok": "Jawaban akhirmu benar.", "fail": "Biaya = luas × harga per m² = 154 × 10.000.", "partial": ""},
            {"label": "Menuliskan satuan rupiah (Rp)", "points": 10, "kind": "contains", "topic": "cerita",
             "patterns": [r"(?<![a-z])rp|rupiah"], "ok": "Satuan rupiah sudah ada.", "fail": "Tuliskan jawaban dalam rupiah (Rp)."},
        ],
        "solution": ["Diketahui: r = 7 m; harga keramik Rp10.000 per m².", "L = 22/7 × 7 × 7 = 154 m².",
                     "Biaya = 154 × Rp10.000 = Rp1.540.000.", "Kesimpulan: biaya yang diperlukan Rp1.540.000."],
    },
]

# ============================================================
# 4. FUNGSI PENILAIAN (logika murni, tanpa Streamlit)
# ============================================================
def norm_text(t):
    """Menormalkan teks jawaban agar pemeriksaan tidak peka huruf besar/kecil atau simbol."""
    t = (t or "").lower()
    for a, b in (("²", "2"), ("³", "3"), ("π", " pi "), ("×", " x "), ("÷", " : "), ("·", " x "), ("*", " x ")):
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t)


def parse_number(s):
    """Mengubah teks jawaban (mis. '616 m²', '1.540.000', '706,5') menjadi angka. None jika tidak ada angka."""
    t = norm_text(s)
    t = re.sub(r"(?<![a-z])(cm|m)\s*2", " ", t)
    t = re.sub(r"rupiah|meter persegi|persegi|(?<![a-z])rp\.?", " ", t)
    tokens = re.findall(r"\d[\d.,]*\d|\d", t)
    if not tokens:
        return None
    tok = tokens[-1]
    if "." in tok and "," in tok:
        tok = tok.replace(".", "").replace(",", ".")
    elif "," in tok:
        tok = tok.replace(",", "") if tok.count(",") > 1 else tok.replace(",", ".")
    elif "." in tok and re.fullmatch(r"\d{1,3}(\.\d{3})+", tok):
        tok = tok.replace(".", "")
    try:
        return float(tok)
    except ValueError:
        return None


def close(a, b, tol=0.06):
    return a is not None and math.isclose(a, b, abs_tol=tol)


def grade_essay(q, steps, final, concl):
    """Menilai esai berdasarkan rubrik (angka & kata kunci). Bukan penilaian makna bahasa."""
    text = norm_text(f"{steps} {concl} {final}")
    final_val = parse_number(final)
    checks, got_total = [], 0.0
    total = sum(c["points"] for c in q["rubric"])
    for c in q["rubric"]:
        frac, hint = 0.0, c["fail"]
        if c["kind"] == "contains":
            if any(re.search(p, text) for p in c["patterns"]):
                frac, hint = 1.0, c["ok"]
        elif c["kind"] == "final":
            if close(final_val, q["answer"]):
                frac, hint = 1.0, c["ok"]
            elif q.get("alt") and close(final_val, q["alt"]["value"]):
                frac, hint = q["alt"]["credit"], q["alt"]["note"]
        got = c["points"] * frac
        got_total += got
        checks.append({"label": c["label"], "points": c["points"], "got": got, "frac": frac,
                       "hint": hint, "topic": c["topic"]})
    return {"score": round(got_total / total * 100), "checks": checks}


def mc_status(stq):
    """none = belum | benar = benar percobaan pertama | ulang = benar setelah mencoba lagi | salah = belum benar."""
    a = stq["attempts"]
    if not a:
        return "none"
    if a[0]["correct"]:
        return "benar"
    return "ulang" if any(x["correct"] for x in a) else "salah"


def mc_stats(mc):
    total = len(MC_QUESTIONS)
    sts = [mc_status(mc["q"][q["id"]]) for q in MC_QUESTIONS]
    benar = sts.count("benar")
    checked = total - sts.count("none")
    return {
        "total": total, "statuses": sts, "checked": checked, "benar": benar,
        "salah": checked - benar,                      # salah pada percobaan pertama
        "tuntas": sts.count("benar") + sts.count("ulang"),
        "nilai": round(benar / total * 100),           # skor utama = benar percobaan pertama
        "progress": checked / total,
    }


def essay_stats(es):
    total = len(ESSAY_QUESTIONS)
    per, firsts, bests = [], [], []
    for q in ESSAY_QUESTIONS:
        subs = es["q"][q["id"]]["subs"]
        first = subs[0]["score"] if subs else None
        best = max(s["score"] for s in subs) if subs else None
        per.append({"first": first, "best": best, "n": len(subs)})
        firsts.append(first or 0)
        bests.append(best or 0)
    submitted = sum(1 for p in per if p["n"])
    return {"total": total, "per": per, "submitted": submitted, "progress": submitted / total,
            "nilai_pertama": round(sum(firsts) / total), "nilai_terbaik": round(sum(bests) / total)}


def topic_mastery(mc, es):
    """Penguasaan per topik (0-100) dari soal PG (percobaan pertama) dan kriteria esai (pengiriman pertama)."""
    ev = {}
    for q in MC_QUESTIONS:
        s = mc_status(mc["q"][q["id"]])
        if s != "none":
            ev.setdefault(q["topic"], []).append((1.0 if s == "benar" else 0.0, 1.0))
    for q in ESSAY_QUESTIONS:
        subs = es["q"][q["id"]]["subs"]
        if subs:
            for ch in subs[0]["checks"]:
                ev.setdefault(ch["topic"], []).append((ch["got"] / ch["points"], ch["points"] / 100))
    out = {}
    for t, items in ev.items():
        w = sum(x[1] for x in items)
        out[t] = round(sum(f * wt for f, wt in items) / w * 100)
    return out


# ============================================================
# 5. TAMPILAN (UI)
# ============================================================
st.set_page_config(
    page_title="Petualangan Luas Lingkaran | Kelas VI",
    page_icon="⭕", layout="wide", initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp { color: #2D3047; }
[data-testid="stHeader"] { background: transparent; }
.hero { background: linear-gradient(120deg, #FFC2DC, #FFF0A6 50%, #BFE6FB); padding: 1.4rem 1.8rem;
        border-radius: 26px; border: 3px solid #FFFFFF; box-shadow: 0 6px 18px rgba(232,87,154,.18);
        margin-bottom: 1rem; animation: slidein .6s ease-out; }
.hero h1 { color: #C2185B !important; margin-bottom: .2rem; }
.hero p { color: #2D3047 !important; font-size: 1.05rem; margin: 0; }
.info-card { background: rgba(255,255,255,.88); color: #2D3047; padding: 1rem; border-radius: 20px;
             border: 2px solid #FFD3E6; min-height: 110px; margin-bottom: .5rem;
             box-shadow: 0 3px 10px rgba(46,155,230,.10); }
.formula { background: #FFF1A8; color: #A3174F !important; padding: 1rem; border-radius: 18px; text-align: center;
           font-size: 1.35rem; font-weight: 800; margin: .6rem 0; border: 2px dashed #F5A800; }
.badge { display: inline-block; background: #D9F0FF; color: #134E7A; border: 2px solid #8CCBF3;
         padding: .35rem .9rem; border-radius: 999px; font-weight: 800; font-size: .92rem; }
.chips { display: flex; flex-wrap: wrap; gap: .4rem; margin: .4rem 0 .2rem; }
.chip { background: white; color: #2D3047; border: 2px solid #CBE8FA; border-radius: 12px;
        padding: .25rem .6rem; font-weight: 800; font-size: .9rem; }
.chip.cur { border: 3px solid #E8579A; background: #FFE3F0; }
div.stButton > button, div.stLinkButton > a { border-radius: 14px; font-weight: 800; border: 2px solid #FFB3D1;
        min-height: 2.8rem; background: rgba(255,255,255,.92); color: #2D3047; transition: transform .15s; }
div.stButton > button:hover { transform: translateY(-2px) scale(1.02); border-color: #E8579A; color: #C2185B; }
button[kind="primary"], button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"] {
        background: linear-gradient(135deg, #FF7FB0, #FFB84D) !important; color: white !important; border: none !important; }
[data-testid="stMetric"] { background: rgba(255,255,255,.9); padding: .8rem; border-radius: 16px;
        border: 2px solid #CBE8FA; }
.small-note { color: #4A5075; font-size: .9rem; }
/* ---- umpan balik + animasi ---- */
.fb { padding: .9rem 1.1rem; border-radius: 20px; font-weight: 800; font-size: 1.2rem; margin: .5rem 0; }
.fb-ok { background: #FFF1A8; color: #7A4B00; border: 3px solid #FFC933;
         animation: pop .6s cubic-bezier(.2,1.6,.4,1); }
.fb-bad { background: #FFE0EE; color: #8A2252; border: 3px solid #FF8FB8; animation: shake .6s; }
.fx { position: fixed; inset: 0; pointer-events: none; z-index: 9999; overflow: hidden; }
.fx span { position: absolute; font-size: 2rem; opacity: 0; }
.fx.ok span { top: -8vh; animation: fall 2.8s ease-in forwards; }
.fx.bad span { bottom: -8vh; animation: rise 2.4s ease-out forwards; }
@keyframes fall { 0% {transform: translateY(0) rotate(0); opacity: 1;} 85% {opacity: 1;}
                  100% {transform: translateY(112vh) rotate(360deg); opacity: 0;} }
@keyframes rise { 0% {transform: translateY(0); opacity: 0;} 15% {opacity: 1;}
                  100% {transform: translateY(-65vh); opacity: 0;} }
@keyframes pop { 0% {transform: scale(.5); opacity: 0;} 100% {transform: scale(1); opacity: 1;} }
@keyframes shake { 0%,100% {transform: translateX(0);} 20% {transform: translateX(-10px);}
                   40% {transform: translateX(10px);} 60% {transform: translateX(-6px);} 80% {transform: translateX(6px);} }
@keyframes slidein { 0% {transform: translateY(-14px); opacity: 0;} 100% {transform: translateY(0); opacity: 1;} }
@keyframes bgshift { 0% {background-position: 0 0, 0 0, 0 0, 0% 50%;} 50% {background-position: 0 0, 0 0, 0 0, 100% 50%;}
                     100% {background-position: 0 0, 0 0, 0 0, 0% 50%;} }
@media (prefers-reduced-motion: reduce) { .fx { display: none; } .fb, .hero, .stApp { animation: none !important; } }
</style>
""", unsafe_allow_html=True)

# ---------- MENU ----------
MENU = [
    ("🎯", "Capaian Pembelajaran"),
    ("🧭", "Petunjuk Penggunaan LKPD"),
    ("🌻", "Pengantar Materi"),
    ("🧠", "Materi Inti"),
    ("✏️", "Latihan Soal"),
    ("📊", "Progres dan Hasil Belajar"),
    ("💭", "Refleksi Pembelajaran"),
]
# Bagian yang ditandai selesai lewat tombol. Latihan dihitung dari status soal sebenarnya.
READING_SECTIONS = ["Capaian Pembelajaran", "Petunjuk Penggunaan LKPD", "Pengantar Materi",
                    "Materi Inti", "Refleksi Pembelajaran"]
SECTION_OF = {"Latihan PG": "Latihan Soal", "Hasil PG": "Latihan Soal",
              "Latihan Esai": "Latihan Soal", "Hasil Esai": "Latihan Soal"}

# ---------- LATAR BELAKANG (pink, biru, kuning) ----------
BGS = {
    "pelangi": "linear-gradient(135deg,#FFD0E5,#FFF3B0,#C9E9FF,#FFD0E5)",
    "permen":  "linear-gradient(135deg,#FFE0EE,#FFC4DD,#E2F3FF,#FFE0EE)",
    "langit":  "linear-gradient(135deg,#CFEBFF,#EAF7FF,#FFF6C9,#CFEBFF)",
    "mentega": "linear-gradient(135deg,#FFF1A8,#FFF9DB,#FFDFEC,#FFF1A8)",
    "senja":   "linear-gradient(135deg,#FFBFD8,#FFE6A3,#BEE5FB,#FFBFD8)",
    "laut":    "linear-gradient(135deg,#B7E1FA,#E2F5FF,#FFD9EA,#B7E1FA)",
}
BG_LABELS = {"🌈 Pelangi": "pelangi", "🍬 Permen pink": "permen", "☁️ Langit biru": "langit",
             "🧈 Mentega kuning": "mentega", "🌅 Senja": "senja", "🌊 Laut": "laut"}
AUTO_LABEL = "🎲 Otomatis (berganti-ganti)"
AUTO_BG = {"Cover": "senja", "Identitas": "mentega", "Menu": "langit", "Capaian Pembelajaran": "permen",
           "Petunjuk Penggunaan LKPD": "laut", "Pengantar Materi": "mentega", "Latihan Soal": "pelangi",
           "Hasil PG": "senja", "Hasil Esai": "senja", "Progres dan Hasil Belajar": "langit",
           "Refleksi Pembelajaran": "permen"}
ROTASI_BG = ["laut", "mentega", "permen", "langit", "pelangi", "senja", "mentega"]

# ---------- MESIN SUARA (musik dari file milik pengguna) ----------
# Simpan file musik milik sendiri dengan nama "musik.mp3" di folder yang sama dengan app.py.
# Untuk Streamlit Cloud, unggah musik.mp3 ke repositori yang sama dengan app.py.
MUSIC_FILE = "musik.mp3"

AUDIO_LIB = r"""
(function(){
 if(window.__lk){return;}
 var AC=window.AudioContext||window.webkitAudioContext;
 var A=AC?new AC():null;
 var master=A?A.createGain():null;
 if(master){master.gain.value=0.5;master.connect(A.destination);}
 function tone(f,t,d,type,g){
   if(!A||!master){return;}
   var o=A.createOscillator(),e=A.createGain();
   o.type=type;o.frequency.setValueAtTime(f,t);
   e.gain.setValueAtTime(0.0001,t);
   e.gain.exponentialRampToValueAtTime(g,t+0.02);
   e.gain.exponentialRampToValueAtTime(0.0001,t+d);
   o.connect(e);e.connect(master);o.start(t);o.stop(t+d+0.05);
 }
 function play(n){
   if(!A||!master){return;}
   var go=function(){
     var t=A.currentTime+0.02;
     if(n==='nav'){tone(660,t,0.12,'sine',0.5);tone(880,t+0.07,0.14,'sine',0.5);}
     else if(n==='ok'){[523.25,659.25,783.99,1046.5].forEach(function(f,k){tone(f,t+k*0.1,0.25,'triangle',0.6);});}
     else if(n==='bad'){tone(246.94,t,0.25,'sawtooth',0.25);tone(185,t+0.2,0.4,'sawtooth',0.25);}
     else if(n==='win'){[523.25,659.25,783.99,659.25,783.99,1046.5,1318.5].forEach(function(f,k){tone(f,t+k*0.12,0.3,'triangle',0.6);});}
   };
   if(A.state==='running'){go();}else{A.resume().then(go).catch(function(){});}
 }
 window.__lk={update:function(c){
   if(master){master.gain.value=Math.max(0,Math.min(1,c.vol));}
   var P=window.parent;
   if(c.music_src){
     if(!P.__userMusicAudio || P.__userMusicAudio.src!==c.music_src){
       var old=P.__userMusicAudio;
       if(old){old.pause();}
       P.__userMusicAudio=new P.Audio(c.music_src);
       P.__userMusicAudio.loop=true;
       P.__userMusicAudio.preload='auto';
     }
     P.__userMusicAudio.volume=Math.max(0,Math.min(1,c.vol));
     if(c.music){
       var audio=P.__userMusicAudio;
       var start=function(){audio.play().catch(function(){});};
       if(A && A.state!=='running'){A.resume().then(start).catch(start);}else{start();}
     }else if(P.__userMusicAudio){P.__userMusicAudio.pause();}
   }
   if(c.play && c.sfx){play(c.play);}
 }};
})();
"""
AUDIO_BOOT = ("(function(){try{var P=window.parent;if(!P.__lk){var s=P.document.createElement('script');"
              "s.id='lk-audio';s.textContent=LIB;P.document.head.appendChild(s);}P.__lk.update(CFG);}catch(e){}})();")


# ---------- SESSION STATE ----------
def new_mc(run=1):
    return {"run": run, "idx": 0, "finished": False, "celebrated": False,
            "show_review": False, "confirm_reset": False,
            "q": {q["id"]: {"attempts": [], "locked": False, "try": 1} for q in MC_QUESTIONS}}


def new_essay(run=1):
    return {"run": run, "idx": 0, "finished": False, "celebrated": False,
            "show_review": False, "confirm_reset": False,
            "q": {q["id"]: {"subs": [], "locked": False, "try": 1} for q in ESSAY_QUESTIONS}}


_DEFAULTS = {
    "screen": lambda: "Cover",
    "student": lambda: None,          # {"nama","kelas","absen"}
    "completed": lambda: set(),       # bagian yang ditandai selesai
    "visited": lambda: set(),         # bagian yang pernah dibuka
    "materi_step": lambda: 0,
    "materi_seen": lambda: set(),     # langkah materi yang sudah dilihat
    "mc": new_mc,
    "essay": new_essay,
    "mc_history": lambda: [],
    "essay_history": lambda: [],
    "reflection": lambda: {},
    "saved": lambda: {},              # draf isian agar tidak hilang saat pindah halaman
    "teacher_scores": lambda: {},
    "music_on": lambda: True,
    "sfx_on": lambda: True,
    "vol": lambda: 50,
    "bg_choice": lambda: AUTO_LABEL,
    "sound_queue": lambda: "",
    "snd_n": lambda: 0,
}
for _k, _f in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _f()


def queue_sound(name):
    """Menjadwalkan efek suara ('nav', 'ok', 'bad', 'win'); diputar sekali di akhir proses render."""
    st.session_state.sound_queue = name


def go(screen):
    queue_sound("nav")
    st.session_state.screen = screen
    st.rerun()


def go_materi(step):
    st.session_state.materi_step = step
    go("Materi Inti")


def mark_complete(section):
    st.session_state.completed.add(section)


def seed(key):
    """Mengembalikan draf isian ke widget sebelum widget dibuat."""
    saved = st.session_state.saved
    if key not in st.session_state and saved.get(key) not in (None, ""):
        st.session_state[key] = saved[key]


def keep(key):
    v = st.session_state.get(key)
    if v is not None:
        st.session_state.saved[key] = v


def esc(s):
    return html.escape(str(s))


def now():
    return datetime.now().strftime("%d/%m/%Y %H:%M")


# ---------- KOMPONEN UMUM ----------
def hero(title, subtitle):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def student_badge():
    s = st.session_state.student
    if s:
        st.markdown(f'<span class="badge">👤 {esc(s["nama"])} • Kelas {esc(s["kelas"])} • No. absen {esc(s["absen"])}</span>',
                    unsafe_allow_html=True)


def page_header(title, subtitle):
    hero(title, subtitle)
    left, right = st.columns([4, 1])
    with left:
        student_badge()
    with right:
        if st.button("🏠 Menu", key="top_menu", use_container_width=True):
            go("Menu")


def nav_buttons(back_label=None, back_screen=None):
    st.divider()
    cols = st.columns(3 if back_label else 2)
    i = 0
    if back_label:
        if cols[0].button(back_label, key="nav_back", use_container_width=True):
            go(back_screen)
        i = 1
    if cols[i].button("🏠 Menu Utama", key="nav_menu", use_container_width=True):
        go("Menu")
    if cols[i + 1].button("🏡 Kembali ke Cover", key="nav_cover", use_container_width=True):
        go("Cover")


def draw_circle(radius=7, show_r=True, show_d=True, size=(4.4, 3.2)):
    """Lingkaran dengan titik pusat O. show_r / show_d mengatur label yang ditampilkan."""
    fig, ax = plt.subplots(figsize=size)
    ax.add_patch(Circle((0, 0), radius, facecolor="#FFD6E8", edgecolor="#E8579A", linewidth=2.5, alpha=.95))
    ax.scatter([0], [0], color="#E8579A", zorder=3)
    ax.text(0, .45 * radius / 7 + .1, "O", ha="center", color="#E8579A", fontsize=10, weight="bold")
    if show_r:
        ax.plot([0, radius], [0, 0], color="#F5A800", linewidth=2.7)
        ax.scatter([radius], [0], color="#F5A800", zorder=3)
        ax.text(radius / 2, -.55 * radius / 7 - .2, f"r = {radius:g}", ha="center",
                color="#A86A00", fontsize=11, weight="bold")
    if show_d:
        ax.plot([-radius, radius], [0, 0], color="#2E9BE6", linewidth=1.8, linestyle="--")
        ax.text(0, -radius * .35 - .6, f"d = {2 * radius:g}", ha="center",
                color="#1F6FB0", fontsize=10, weight="bold")
    ax.set_xlim(-radius - 1.5, radius + 1.5)
    ax.set_ylim(-radius - 1.5, radius + 1.5)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_alpha(0)
    st.pyplot(fig, use_container_width=False)
    plt.close(fig)


def fmt_num(value):
    if abs(value - round(value)) < 1e-8:
        return str(int(round(value)))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def fx_banner(kind, text):
    """Banner umpan balik beranimasi: 'ok' = konfeti jatuh + pop, 'bad' = goyang + emoji naik."""
    if kind == "ok":
        emo, lefts = ["🎉", "⭐", "✨", "🌟", "🎈", "💖", "💛", "💙"], [6, 18, 30, 42, 54, 66, 78, 90]
    else:
        emo, lefts = ["🤔", "💭", "📚", "💡"], [15, 38, 62, 85]
    spans = "".join(f'<span style="left:{lefts[i]}%;animation-delay:{i * 0.12:.2f}s">{emo[i % len(emo)]}</span>'
                    for i in range(len(lefts)))
    st.markdown(f'<div class="fx {kind}">{spans}</div><div class="fb fb-{kind}">{text}</div>', unsafe_allow_html=True)


def pick_bg(screen):
    ch = st.session_state.bg_choice
    if ch in BG_LABELS:
        return BG_LABELS[ch]
    if screen == "Materi Inti":
        return ROTASI_BG[st.session_state.materi_step % len(ROTASI_BG)]
    if screen == "Latihan PG":
        return ROTASI_BG[(st.session_state.mc["idx"] + 1) % len(ROTASI_BG)]
    if screen == "Latihan Esai":
        return ROTASI_BG[(st.session_state.essay["idx"] + 3) % len(ROTASI_BG)]
    return AUTO_BG.get(screen, "pelangi")


def bg_css(screen):
    grad = BGS[pick_bg(screen)]
    dots = ("radial-gradient(circle at 8% 14%, rgba(255,255,255,.55) 0 70px, transparent 71px),"
            "radial-gradient(circle at 93% 28%, rgba(255,255,255,.45) 0 110px, transparent 111px),"
            "radial-gradient(circle at 14% 92%, rgba(255,255,255,.5) 0 90px, transparent 91px),")
    return (f"<style>.stApp{{background-image:{dots}{grad};background-size:auto,auto,auto,300% 300%;"
            f"background-attachment:fixed;animation:bgshift 22s ease infinite;}}</style>")


def settings_bar():
    with st.expander("🎛️ Pengaturan musik, suara, dan latar belakang"):
        c1, c2, c3, c4 = st.columns(4)
        c1.checkbox("🎵 Musik latar", key="music_on")
        c2.checkbox("🔊 Efek suara", key="sfx_on")
        c3.slider("Volume", 0, 100, key="vol")
        c4.selectbox("🎨 Latar belakang", [AUTO_LABEL] + list(BG_LABELS), key="bg_choice")
        st.caption("Gunakan file musik milik sendiri bernama musik.mp3 dan letakkan satu folder dengan app.py. Tekan halaman/tombol sekali agar browser mengizinkan musik diputar.")


def audio_engine():
    """Memutar musik dari file musik.mp3 milik pengguna dan mengirim efek suara."""
    sound = st.session_state.sound_queue
    st.session_state.sound_queue = ""
    if sound:
        st.session_state.snd_n += 1

    music_path = Path(__file__).resolve().parent / MUSIC_FILE
    music_src = ""
    if music_path.exists():
        try:
            audio_bytes = music_path.read_bytes()
            ext = music_path.suffix.lower()
            mime = "audio/mpeg" if ext == ".mp3" else "audio/wav" if ext == ".wav" else "audio/ogg"
            music_src = "data:" + mime + ";base64," + base64.b64encode(audio_bytes).decode("ascii")
        except OSError:
            music_src = ""

    cfg = {
        "music": bool(st.session_state.music_on) and bool(music_src),
        "sfx": bool(st.session_state.sfx_on),
        "vol": st.session_state.vol / 100,
        "play": sound,
        "music_src": music_src,
    }
    if not music_src and st.session_state.music_on:
        st.caption("File musik.mp3 belum ditemukan. Letakkan file musik milikmu di folder yang sama dengan app.py.")
    page = ("<!--" + str(st.session_state.snd_n) + "--><script>var LIB=" + json.dumps(AUDIO_LIB).replace("</", "<\\/")
            + ";var CFG=" + json.dumps(cfg).replace("</", "<\\/") + ";" + AUDIO_BOOT + "</script>")
    components.html(page, height=0)


def video_block(url, label="video pembelajaran"):
    """Tampilkan video bila tautan diisi guru; jika kosong tampilkan placeholder (tidak mengarang tautan)."""
    if url and url.startswith("https://"):
        try:
            st.video(url)
        except Exception:
            st.link_button(f"▶️ Buka {label}", url)
    else:
        st.info(f"📌 Tempat {label}. Tautan belum diisi guru (isi pada bagian KONFIGURASI di app.py).")


def overall_progress():
    mcs, ess = mc_stats(st.session_state.mc), essay_stats(st.session_state.essay)
    parts = [1.0 if s in st.session_state.completed else 0.0 for s in READING_SECTIONS]
    parts += [mcs["progress"], ess["progress"]]
    return sum(parts) / len(parts)


def section_status(title):
    if title == "Latihan Soal":
        m, e = mc_stats(st.session_state.mc), essay_stats(st.session_state.essay)
        return f"PG {m['checked']}/{m['total']} • Esai {e['submitted']}/{e['total']}"
    if title == "Progres dan Hasil Belajar":
        return f"Keseluruhan {round(overall_progress() * 100)}%"
    if title in st.session_state.completed:
        return "✅ Selesai"
    return "📖 Sudah dibuka" if title in st.session_state.visited else "⚪ Belum dibuka"


def render_recommendations(items, prefix):
    """items: daftar (topik, alasan). Tiap topik tampil sekali dengan tombol ke materi terkait."""
    shown = set()
    for topic, reason in items:
        if topic in shown:
            continue
        shown.add(topic)
        t = TOPICS[topic]
        with st.container(border=True):
            st.markdown(f"**📌 {t['label']}**")
            st.write(reason)
            st.caption(t["tip"])
            c1, c2 = st.columns(2)
            if c1.button("📖 Pelajari bagian materinya", key=f"{prefix}_mat_{topic}", use_container_width=True):
                go_materi(t["step"])
            with c2:
                if t["video"] and t["video"].startswith("https://"):
                    st.link_button("▶️ Tonton video penjelasan", t["video"], use_container_width=True)
                else:
                    st.caption("🎬 Tautan video topik ini belum diisi guru.")
    if not shown:
        st.success("🌟 Tidak ada materi yang perlu diulang saat ini. Pertahankan!")


# ============================================================
# HALAMAN: COVER, IDENTITAS, MENU
# ============================================================
def page_cover():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="190" height="190">'
           '<circle cx="100" cy="100" r="82" fill="#FFD6E8" stroke="#E8579A" stroke-width="6"/>'
           '<line x1="18" y1="100" x2="182" y2="100" stroke="#2E9BE6" stroke-width="3" stroke-dasharray="7 6"/>'
           '<line x1="100" y1="100" x2="182" y2="100" stroke="#F5A800" stroke-width="6" stroke-linecap="round"/>'
           '<circle cx="100" cy="100" r="7" fill="#E8579A"/><circle cx="182" cy="100" r="6" fill="#F5A800"/>'
           '<text x="136" y="88" font-size="20" font-weight="800" fill="#A86A00" font-family="sans-serif">r</text>'
           '<text x="52" y="128" font-size="20" font-weight="800" fill="#1F6FB0" font-family="sans-serif">d</text>'
           '<text x="94" y="124" font-size="14" font-weight="800" fill="#E8579A" font-family="sans-serif">O</text></svg>')
    b64 = base64.b64encode(svg.encode()).decode()
    st.markdown(f"<div style='text-align:center'><img src='data:image/svg+xml;base64,{b64}' width='190'></div>",
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="hero" style="text-align:center;padding:2rem 1.5rem">
      <p style="font-weight:800;letter-spacing:2px">MATEMATIKA • KELAS VI SD/MI</p>
      <h1 style="font-size:2.6rem">Petualangan Luas Lingkaran</h1>
      <p>Amati bentuknya, temukan rumusnya, lalu pecahkan tantangannya!</p>
      <p class="small-note" style="margin-top:.6rem">{esc(NAMA_SEKOLAH)}</p>
    </div>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="info-card">⭕<br><b>Kenali bentuk</b><br>Jari-jari dan diameter</div>', unsafe_allow_html=True)
    c2.markdown('<div class="info-card">🧮<br><b>Belajar menghitung</b><br>Rumus luas lingkaran</div>', unsafe_allow_html=True)
    c3.markdown('<div class="info-card">🏆<br><b>Taklukkan tantangan</b><br>Latihan dan refleksi</div>', unsafe_allow_html=True)
    label = "🚀 Lanjutkan Belajar" if st.session_state.student else "🚀 Mulai Petualangan"
    if st.button(label, type="primary", use_container_width=True, key="cover_start"):
        go("Menu" if st.session_state.student else "Identitas")


def page_identitas():
    hero("👋 Kenalan dulu, yuk!", "Isi identitasmu sebelum masuk ke menu belajar.")
    cur = st.session_state.student or {}
    with st.form("form_identitas"):
        nama = st.text_input("Nama lengkap", value=cur.get("nama", ""), placeholder="Tulis nama lengkapmu")
        kelas = st.text_input("Kelas", value=cur.get("kelas", ""), placeholder="Contoh: VI-A")
        absen = st.number_input("Nomor absen", min_value=1, max_value=100, value=None, step=1,
                                placeholder="Isi nomor absenmu")
        ok = st.form_submit_button("➡️ Lanjut ke Menu Utama", type="primary")
    if ok:
        errors = []
        if not nama.strip():
            errors.append("Nama lengkap belum diisi.")
        if not kelas.strip():
            errors.append("Kelas belum diisi.")
        if absen is None:
            errors.append("Nomor absen belum diisi.")
        if errors:
            for e in errors:
                st.error("⚠️ " + e)
        else:
            st.session_state.student = {"nama": nama.strip(), "kelas": kelas.strip(), "absen": int(absen)}
            go("Menu")
    if st.button("🏡 Kembali ke Cover", key="ident_cover"):
        go("Cover")


def page_menu():
    hero("🏠 Menu Utama", "Pilih bagian yang ingin kamu pelajari. Kamu bisa kembali ke menu ini kapan saja.")
    student_badge()
    pct = overall_progress()
    st.metric("Progres belajar keseluruhan", f"{round(pct * 100)}%")
    st.progress(pct)
    st.caption("Progres dihitung dari bagian yang sudah ditandai selesai, soal pilihan ganda yang diperiksa, dan soal esai yang dikirim.")
    cards = st.columns(3)
    for i, (emoji, title) in enumerate(MENU):
        with cards[i % 3]:
            st.markdown(f'<div class="info-card"><div style="font-size:2rem">{emoji}</div>'
                        f'<b>{title}</b><br><span class="small-note">{section_status(title)}</span></div>',
                        unsafe_allow_html=True)
            if st.button(f"Buka {title}", key=f"menu_{i}", use_container_width=True):
                go(title)
    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("✏️ Ubah identitas", use_container_width=True, key="menu_ident"):
        go("Identitas")
    if c2.button("🏡 Kembali ke Cover", use_container_width=True, key="menu_cover"):
        go("Cover")


# ============================================================
# HALAMAN: CAPAIAN, PETUNJUK, PENGANTAR
# ============================================================
def page_capaian():
    page_header("🎯 Capaian Pembelajaran", "Tujuan yang akan kamu capai setelah belajar.")
    st.markdown("### Setelah menyelesaikan modul ini, kamu diharapkan mampu:")
    for g in CAPAIAN_PEMBELAJARAN:
        st.markdown(f"- {g}")
    st.info("Catatan guru: rumusan di atas adalah tujuan pembelajaran modul ini, bukan kutipan dokumen resmi. "
            "Samakan dengan CP/ATP/LKPD sekolah melalui daftar CAPAIAN_PEMBELAJARAN di app.py.")
    if st.button("✅ Saya sudah membaca tujuan", type="primary", key="done_cp"):
        mark_complete("Capaian Pembelajaran")
    if "Capaian Pembelajaran" in st.session_state.completed:
        st.success("Bagian ini sudah ditandai selesai.")
    nav_buttons()


def page_petunjuk():
    page_header("🧭 Petunjuk Penggunaan LKPD", "Ikuti langkah berikut agar petualangan belajarmu lebih mudah.")
    steps = [
        "Buka Menu Utama, lalu pilih bagian yang ingin dipelajari.",
        "Baca Materi Inti langkah demi langkah dan perhatikan contoh perhitungannya.",
        "Di Latihan Soal, pilih Pilihan Ganda (10 soal) atau Esai (5 soal).",
        "Pilih jawabanmu, lalu tekan Periksa Jawaban. Jawaban langsung diperiksa.",
        "Baca umpan balik dan pembahasan. Jika salah, kamu boleh Coba Lagi atau Lanjut.",
        "Pantau kemajuanmu di Progres dan Hasil Belajar, lalu pelajari lagi bagian yang disarankan.",
        "Isi Refleksi Pembelajaran setelah selesai.",
        "Buka Pengaturan di bagian atas untuk menyalakan atau mematikan musik dan efek suara, mengatur volume, dan mengganti latar belakang.",
    ]
    for n, desc in enumerate(steps, 1):
        st.markdown(f'<div class="info-card" style="min-height:0"><b>{n}. {desc}</b></div>', unsafe_allow_html=True)
    st.warning("Nilai pilihan ganda dihitung dari jawaban benar pada percobaan pertama. Percobaan ulang tetap dicatat, "
               "tetapi tidak menambah nilai.")
    if st.button("✅ Petunjuk sudah dipahami", type="primary", key="done_petunjuk"):
        mark_complete("Petunjuk Penggunaan LKPD")
    if "Petunjuk Penggunaan LKPD" in st.session_state.completed:
        st.success("Bagian ini sudah ditandai selesai.")
    nav_buttons()


def page_pengantar():
    page_header("🌻 Pengantar Materi", "Lingkaran ada di banyak tempat di sekitar kita!")
    a, b = st.columns(2)
    with a:
        st.markdown("### Pernah melihat benda-benda ini?")
        st.markdown("- 🛞 Roda sepeda\n- 🕒 Jam dinding\n- 🍽️ Piring\n- 🍕 Pizza\n- 🌳 Taman bundar")
        st.write("Luas adalah ukuran besar daerah di dalam batas lingkaran. Kita akan belajar menghitung "
                 "seberapa luas permukaan benda-benda tersebut.")
    with b:
        draw_circle(7, True, True)
        st.caption("Garis dari pusat (O) ke tepi adalah jari-jari (r). Garis dari tepi ke tepi melalui pusat adalah diameter (d).")
    st.markdown('<div class="formula">d = 2 × r &nbsp;&nbsp; | &nbsp;&nbsp; r = d ÷ 2</div>', unsafe_allow_html=True)
    st.markdown("### Pertanyaan pemantik")
    st.write("Jika sebuah pizza diketahui diameternya 20 cm, apakah kita bisa langsung memasukkan 20 ke rumus luas? Mengapa?")
    seed("pemantik")
    st.text_area("Tulis pendapatmu (opsional)", key="pemantik")
    keep("pemantik")
    if st.button("✅ Saya selesai membaca pengantar", type="primary", key="done_pengantar"):
        mark_complete("Pengantar Materi")
    if "Pengantar Materi" in st.session_state.completed:
        st.success("Bagian ini sudah ditandai selesai.")
    nav_buttons()


# ============================================================
# HALAMAN: MATERI INTI (bertahap)
# ============================================================
def page_materi():
    page_header("🧠 Materi Inti: Luas Lingkaran", "Pelajari langkah demi langkah, lalu coba sendiri.")
    step = st.session_state.materi_step
    st.session_state.materi_seen.add(step)
    n = len(MATERI_STEPS)
    titles = [f"{i + 1}. {t}" for i, (_, t) in enumerate(MATERI_STEPS)]

    def _jump():
        st.session_state.materi_step = titles.index(st.session_state.materi_jump)

    st.session_state.materi_jump = titles[step]
    st.selectbox("Loncat ke bagian:", titles, key="materi_jump", on_change=_jump)
    st.progress((step + 1) / n, text=f"Bagian {step + 1} dari {n} • sudah dilihat {len(st.session_state.materi_seen)}/{n}")
    emoji, title = MATERI_STEPS[step]
    st.markdown(f"## {emoji} {title}")

    if step == 0:
        a, b = st.columns(2)
        with a:
            st.markdown("**Lingkaran** adalah bangun datar yang tepinya berjarak sama dari satu titik di tengah.")
            st.markdown("- **Titik pusat (O)**: titik di tengah lingkaran.\n"
                        "- **Jari-jari (r)**: garis dari titik pusat ke tepi lingkaran.\n"
                        "- **Diameter (d)**: garis dari tepi ke tepi yang melalui titik pusat.")
        with b:
            draw_circle(7, True, True)
    elif step == 1:
        st.markdown('<div class="formula">d = 2 × r &nbsp;&nbsp; | &nbsp;&nbsp; r = d ÷ 2</div>', unsafe_allow_html=True)
        st.write("Diameter adalah dua kali jari-jari. Sebaliknya, jari-jari adalah setengah diameter.")
        d = st.slider("Geser diameter (cm)", 2, 40, 20, step=2, key="hub_d")
        st.success(f"Jika d = {d} cm, maka r = {d} ÷ 2 = {fmt_num(d / 2)} cm.")
        draw_circle(d / 2, True, True)
    elif step == 2:
        st.markdown('<div class="formula">L = π × r × r = π × r²</div>', unsafe_allow_html=True)
        st.markdown("- **L** = luas lingkaran\n- **π (pi)** = 22/7 atau 3,14\n- **r** = jari-jari lingkaran\n- **r²** = r × r")
        st.warning("Ingat: L = π × r² adalah rumus luas. Rumus 2 × π × r digunakan untuk menghitung keliling.")
    elif step == 3:
        st.markdown("- Gunakan **π = 22/7** jika jari-jari atau diameter merupakan **kelipatan 7** (7, 14, 21, 28, ...).\n"
                    "- Gunakan **π = 3,14** untuk ukuran yang bukan kelipatan 7.\n"
                    "- Jika diameter diketahui, hitung **r = d ÷ 2** terlebih dahulu.")
        st.info("Contoh: r = 14 → pakai 22/7. r = 10 → pakai 3,14.")
    elif step == 4:
        with st.expander("🍽️ Contoh A — Piring bundar", expanded=True):
            st.write("Piring memiliki jari-jari 7 cm. Tentukan luas permukaannya.")
            st.write("Diketahui: r = 7 cm. Ditanya: L.")
            st.latex(r"L = \frac{22}{7}\times 7\times 7 = 154\text{ cm}^2")
        with st.expander("🍕 Contoh B — Pizza"):
            st.write("Pizza berdiameter 20 cm. Tentukan luasnya.")
            st.write("Diketahui: d = 20 cm. Ditanya: L. Cari jari-jari: r = 20 ÷ 2 = 10 cm.")
            st.latex(r"L = 3{,}14\times 10\times 10 = 314\text{ cm}^2")
        with st.expander("🌳 Contoh C — Taman bundar"):
            st.write("Taman memiliki jari-jari 14 m. Karena 14 kelipatan 7, gunakan π = 22/7.")
            st.latex(r"L = \frac{22}{7}\times 14\times 14 = 616\text{ m}^2")
    elif step == 5:
        radius = st.slider("Geser untuk mengubah jari-jari (cm)", 1, 20, 7, key="materi_radius")
        pi_choice = st.radio("Pilih nilai π", ["22/7", "3,14"], horizontal=True, key="materi_pi")
        area = (22 / 7 if pi_choice == "22/7" else 3.14) * radius ** 2
        left, right = st.columns(2)
        with left:
            draw_circle(radius, True, True)
        with right:
            st.markdown("### Hitung bersama")
            st.write(f"Jari-jari: **{radius} cm**")
            st.write("L = π × r × r")
            st.write(f"L = {pi_choice} × {radius} × {radius}")
            st.success(f"Luas = {fmt_num(area)} cm²")
    else:
        st.write("Tonton video pembelajaran berikut untuk memperkuat pemahamanmu.")
        video_block(VIDEO_UTAMA, "video pembelajaran")
        st.link_button("🔎 Cari video luas lingkaran di YouTube", VIDEO_PENCARIAN)
        st.caption("Tombol pencarian membuka hasil pencarian YouTube, bukan video pilihan guru.")
        all_seen = len(st.session_state.materi_seen) == n
        if not all_seen:
            st.caption("Lihat semua bagian materi dulu agar bisa menandai selesai.")
        if st.button("✅ Materi sudah dipelajari", type="primary", key="done_materi", disabled=not all_seen):
            mark_complete("Materi Inti")
        if "Materi Inti" in st.session_state.completed:
            st.success("Materi Inti sudah ditandai selesai.")

    st.divider()
    c1, c2, c3 = st.columns([1, 1, 1])
    if step > 0 and c1.button("⬅️ Sebelumnya", key="mat_prev", use_container_width=True):
        st.session_state.materi_step -= 1
        queue_sound("nav")
        st.rerun()
    if c2.button("✏️ Ke Latihan Soal", key="mat_latihan", use_container_width=True):
        go("Latihan Soal")
    if step < n - 1 and c3.button("Berikutnya ➡️", key="mat_next", type="primary", use_container_width=True):
        st.session_state.materi_step += 1
        queue_sound("nav")
        st.rerun()
    nav_buttons()


# ============================================================
# HALAMAN: LATIHAN SOAL (hub)
# ============================================================
def page_latihan():
    page_header("✏️ Latihan Soal", "Pilih jenis latihan. Soal muncul satu per satu dan langsung diperiksa.")
    mc, es = st.session_state.mc, st.session_state.essay
    ms, ess = mc_stats(mc), essay_stats(es)
    a, b = st.columns(2)
    with a:
        st.markdown('<div class="info-card"><div style="font-size:2rem">📝</div><b>Pilihan Ganda</b><br>'
                    '<span class="small-note">10 soal • pilih A, B, C, atau D</span></div>', unsafe_allow_html=True)
        st.progress(ms["progress"], text=f"Diperiksa {ms['checked']}/{ms['total']} soal")
        if mc["finished"]:
            st.success(f"Selesai • Nilai {ms['nilai']}/100")
            if st.button("📊 Lihat Hasil Pilihan Ganda", key="hub_mc_res", use_container_width=True):
                go("Hasil PG")
        else:
            lbl = "▶️ Mulai Pilihan Ganda" if ms["checked"] == 0 else "▶️ Lanjutkan Pilihan Ganda"
            if st.button(lbl, key="hub_mc", type="primary", use_container_width=True):
                go("Latihan PG")
    with b:
        st.markdown('<div class="info-card"><div style="font-size:2rem">🖊️</div><b>Esai / Pemantapan</b><br>'
                    '<span class="small-note">5 soal • tulis langkah dan jawabanmu</span></div>', unsafe_allow_html=True)
        st.progress(ess["progress"], text=f"Dikirim {ess['submitted']}/{ess['total']} soal")
        if es["finished"]:
            st.success(f"Selesai • Nilai otomatis sementara {ess['nilai_pertama']}/100")
            if st.button("📊 Lihat Hasil Esai", key="hub_es_res", use_container_width=True):
                go("Hasil Esai")
        else:
            lbl = "▶️ Mulai Esai" if ess["submitted"] == 0 else "▶️ Lanjutkan Esai"
            if st.button(lbl, key="hub_es", type="primary", use_container_width=True):
                go("Latihan Esai")
    st.caption("Kedua latihan punya progres sendiri. Jawabanmu tetap tersimpan selama sesi belajar ini berjalan.")
    nav_buttons()


# ============================================================
# LATIHAN PILIHAN GANDA
# ============================================================
def mc_chips(statuses, current):
    icon = {"none": "⚪", "benar": "✅", "ulang": "🔁", "salah": "⚠️"}
    parts = "".join(f'<span class="chip{" cur" if i == current else ""}">{i + 1} {icon[s]}</span>'
                    for i, s in enumerate(statuses))
    st.markdown(f'<div class="chips">{parts}</div>', unsafe_allow_html=True)
    st.caption("⚪ belum dikerjakan • ✅ benar (percobaan pertama) • ⚠️ perlu dipelajari lagi • 🔁 benar setelah mencoba lagi")


def mc_feedback(q, stq):
    att = stq["attempts"][-1]
    ans = q["answer"]
    if att["correct"]:
        fx_banner("ok", "🎉 Hebat! Jawabanmu benar!")
        st.markdown(f"**Mengapa benar?** {q['explanation']}")
        if len(stq["attempts"]) > 1:
            st.info("Soal ini benar setelah mencoba lagi. Nilai utama tetap dihitung dari percobaan pertama, "
                    "tetapi kamu sudah berhasil memahaminya!")
    else:
        fx_banner("bad", "🤔 Belum tepat, yuk pelajari lagi!")
        mis = q.get("miskonsepsi", {}).get(att["choice"])
        if mis:
            st.markdown(f"**Tentang pilihanmu ({LETTERS[att['choice']]}):** {mis}")
        st.markdown(f"**Jawaban yang benar:** {LETTERS[ans]}. {q['options'][ans]}")
        st.markdown(f"**Penjelasan konsep:** {q['explanation']}")
        st.markdown("**Langkah penyelesaian:**")
        for s_ in q["steps"]:
            st.markdown(f"- {s_}")


def page_mc_play():
    mc = st.session_state.mc
    if mc["finished"]:
        go("Hasil PG")
    total = len(MC_QUESTIONS)
    i = mc["idx"]
    q = MC_QUESTIONS[i]
    stq = mc["q"][q["id"]]
    page_header("📝 Latihan Pilihan Ganda", "Satu soal satu waktu. Periksa jawabanmu, baca umpan balik, lalu lanjut!")
    s = mc_stats(mc)
    m = st.columns(4)
    m[0].metric("Posisi soal", f"{i + 1} dari {total}")
    m[1].metric("Skor sementara", f"{s['nilai']}/100")
    m[2].metric("Soal diperiksa", f"{s['checked']}/{total}")
    m[3].metric("Benar percobaan pertama", f"{s['benar']}")
    st.progress(s["progress"], text=f"Progres pengerjaan {round(s['progress'] * 100)}%")
    mc_chips(s["statuses"], i)

    with st.container(border=True):
        st.markdown(f"**Soal {i + 1}.** {q['question']}")
        if q.get("visual"):
            v = q["visual"]
            draw_circle(v["radius"], v["show_r"], v["show_d"])
        key = f"mc{mc['run']}_{q['id']}_{stq['try']}"
        if stq["locked"]:
            st.session_state[key] = stq["attempts"][-1]["choice"]
        else:
            seed(key)
        choice = st.radio("Pilih satu jawaban:", [0, 1, 2, 3], index=None, key=key, disabled=stq["locked"],
                          format_func=lambda k: f"{LETTERS[k]}. {q['options'][k]}")
        if not stq["locked"]:
            keep(key)

    if stq["attempts"]:
        log = " • ".join(f"Percobaan {n}: {LETTERS[a['choice']]} {'✅' if a['correct'] else '❌'}"
                         for n, a in enumerate(stq["attempts"], 1))
        st.caption("Riwayat: " + log)

    if not stq["locked"]:
        if st.button("🔎 Periksa Jawaban", type="primary", key=f"chk_{key}"):
            if choice is None:
                st.warning("Pilih salah satu jawaban dulu ya, baru tekan Periksa Jawaban.")
            else:
                stq["attempts"].append({"choice": choice, "correct": choice == q["answer"], "waktu": now()})
                stq["locked"] = True
                queue_sound("ok" if choice == q["answer"] else "bad")
                st.rerun()
    else:
        mc_feedback(q, stq)
        if not stq["attempts"][-1]["correct"]:
            if st.button("🔄 Coba Lagi", key=f"retry_{key}"):
                stq["locked"] = False
                stq["try"] += 1
                st.rerun()

    st.divider()
    c1, c2 = st.columns(2)
    if i > 0 and c1.button("⬅️ Soal Sebelumnya", key="mc_prev", use_container_width=True):
        mc["idx"] -= 1
        st.rerun()
    last = i == total - 1
    can_next = bool(stq["attempts"])
    label = "🏁 Selesai & Lihat Hasil" if last else "➡️ Lanjut ke Soal Berikutnya"
    if c2.button(label, key="mc_next", type="primary", use_container_width=True, disabled=not can_next):
        if last:
            if mc_stats(mc)["checked"] == total:
                mc["finished"] = True
                go("Hasil PG")
            else:
                st.warning("Masih ada soal yang belum diperiksa.")
        else:
            mc["idx"] += 1
            st.rerun()
    if not can_next:
        st.caption("Tekan Periksa Jawaban dulu agar bisa lanjut.")
    nav_buttons("↩️ Menu Latihan", "Latihan Soal")


def page_mc_hasil():
    mc = st.session_state.mc
    s = mc_stats(mc)
    page_header("🏆 Hasil Latihan Pilihan Ganda", "Lihat hasil dan materi yang perlu kamu pelajari lagi.")
    if not mc["finished"]:
        st.info(f"Kamu baru memeriksa {s['checked']} dari {s['total']} soal. Selesaikan dulu semua soal.")
        if st.button("▶️ Lanjutkan Latihan", type="primary", key="res_continue"):
            go("Latihan PG")
        nav_buttons("↩️ Menu Latihan", "Latihan Soal")
        return
    if not mc["celebrated"]:
        mc["celebrated"] = True
        queue_sound("win" if s["nilai"] >= KKM else "nav")
        if s["nilai"] >= KKM:
            st.balloons()
    stu = st.session_state.student
    st.markdown(f"**Nama:** {esc(stu['nama'])} &nbsp;|&nbsp; **Kelas:** {esc(stu['kelas'])} &nbsp;|&nbsp; "
                f"**No. absen:** {esc(stu['absen'])}", unsafe_allow_html=True)
    m = st.columns(4)
    m[0].metric("Soal diselesaikan", f"{s['checked']}/{s['total']}")
    m[1].metric("Benar (percobaan pertama)", s["benar"])
    m[2].metric("Salah (percobaan pertama)", s["salah"])
    m[3].metric("Nilai akhir", f"{s['nilai']}/100")
    st.progress(1.0, text="Progres latihan 100%")
    st.progress(s["nilai"] / 100, text=f"Penguasaan {s['nilai']}%")
    if s["nilai"] >= KKM:
        st.success(f"🎉 Tuntas! Nilaimu mencapai batas ketuntasan (KKM {KKM}).")
    else:
        st.warning(f"💪 Belum tuntas (KKM {KKM}). Pelajari lagi materi yang disarankan, lalu coba ulangi latihan.")
    st.caption(f"Soal yang akhirnya benar (termasuk setelah mencoba lagi): {s['tuntas']} dari {s['total']}. "
               "Nilai akhir hanya dihitung dari jawaban benar pada percobaan pertama.")

    st.markdown("### Ringkasan soal yang perlu dipelajari kembali")
    weak = [(n, q) for n, q in enumerate(MC_QUESTIONS, 1) if mc_status(mc["q"][q["id"]]) != "benar"]
    if weak:
        for n, q in weak:
            st.markdown(f"- Soal {n}: {q['question'].splitlines()[0][:110]} — topik **{TOPICS[q['topic']]['label']}**")
    else:
        st.write("Semua soal benar pada percobaan pertama. Hebat!")
    st.markdown("### Rekomendasi belajar untukmu")
    groups = {}
    for n, q in weak:
        groups.setdefault(q["topic"], []).append(n)
    render_recommendations([(t, f"Kamu belum tepat pada soal nomor {', '.join(map(str, ns))}.")
                            for t, ns in groups.items()], "mcrec")

    if mc["show_review"]:
        st.markdown("### Pembahasan semua soal")
        for n, q in enumerate(MC_QUESTIONS, 1):
            stq = mc["q"][q["id"]]
            with st.expander(f"Soal {n} — {'✅ benar' if mc_status(stq) == 'benar' else '⚠️ perlu dipelajari'}"):
                st.markdown(q["question"])
                for k, o in enumerate(q["options"]):
                    st.markdown(f"{'**✅ ' if k == q['answer'] else ''}{LETTERS[k]}. {o}{'**' if k == q['answer'] else ''}")
                st.caption("Jawabanmu: " + " → ".join(LETTERS[a["choice"]] for a in stq["attempts"]))
                st.markdown(f"**Penjelasan:** {q['explanation']}")
                for t in q["steps"]:
                    st.markdown(f"- {t}")

    st.divider()
    b = st.columns(4)
    if b[0].button("📖 Lihat Pembahasan" if not mc["show_review"] else "🙈 Tutup Pembahasan", key="res_review",
                   use_container_width=True):
        mc["show_review"] = not mc["show_review"]
        st.rerun()
    if b[1].button("📚 Pelajari Materi Kembali", key="res_materi", use_container_width=True):
        go_materi(0)
    if b[2].button("🔁 Ulangi Latihan", key="res_reset", use_container_width=True):
        mc["confirm_reset"] = True
        st.rerun()
    if b[3].button("🏠 Kembali ke Menu Utama", key="res_menu", use_container_width=True):
        go("Menu")
    if mc["confirm_reset"]:
        st.warning(f"Latihan akan diulang dari soal 1 dan jawaban sekarang dikosongkan. Hasil ini (nilai {s['nilai']}) "
                   "akan dicatat di Riwayat latihan pada halaman Progres. Lanjutkan?")
        y, n_ = st.columns(2)
        if y.button("✅ Ya, ulangi latihan", key="res_reset_yes", type="primary", use_container_width=True):
            st.session_state.mc_history.append({"waktu": now(), "nilai": s["nilai"], "benar": s["benar"], "salah": s["salah"]})
            st.session_state.mc = new_mc(mc["run"] + 1)
            go("Latihan PG")
        if n_.button("Batal", key="res_reset_no", use_container_width=True):
            mc["confirm_reset"] = False
            st.rerun()


# ============================================================
# LATIHAN ESAI
# ============================================================
def essay_feedback(q, stq):
    sub = stq["subs"][-1]
    if sub["score"] >= KKM:
        fx_banner("ok", "🎉 Kerja bagus! Jawabanmu sudah kuat.")
    else:
        fx_banner("bad", "💪 Hampir! Yuk perbaiki bagian yang ditandai 🔎.")
    st.markdown(f"#### Hasil pemeriksaan: **{sub['score']}/100**")
    st.progress(sub["score"] / 100)
    for ch in sub["checks"]:
        icon = "✅" if ch["frac"] == 1 else ("🟡" if ch["frac"] > 0 else "🔎")
        st.markdown(f"{icon} **{ch['label']}** ({round(ch['got'])}/{ch['points']}) — {ch['hint']}")
    st.caption("Pemeriksaan otomatis hanya mengecek angka dan kata/simbol penting. Cara penulisan lain tetap mungkin benar, "
               "jadi guru tetap dapat memeriksa penalaranmu.")
    if q.get("needs_teacher"):
        st.info("📝 Soal ini meminta penjelasan. Alasanmu sebaiknya dibaca dan dinilai guru.")
    with st.expander("📖 Pembahasan dan jawaban yang diharapkan", expanded=True):
        for t in q["solution"]:
            st.markdown(f"- {t}")
        st.markdown(f"**Jawaban yang diharapkan:** {q['answer_text']}")


def page_essay_play():
    es = st.session_state.essay
    if es["finished"]:
        go("Hasil Esai")
    total = len(ESSAY_QUESTIONS)
    i = es["idx"]
    q = ESSAY_QUESTIONS[i]
    stq = es["q"][q["id"]]
    page_header("🖊️ Latihan Esai / Pemantapan", "Tulis langkah dan jawabanmu dengan lengkap.")
    s = essay_stats(es)
    m = st.columns(3)
    m[0].metric("Posisi soal", f"{i + 1} dari {total}")
    m[1].metric("Soal dikirim", f"{s['submitted']}/{total}")
    m[2].metric("Skor soal ini", f"{s['per'][i]['first']}/100" if s["per"][i]["first"] is not None else "—")
    st.progress(s["progress"], text=f"Progres esai {round(s['progress'] * 100)}%")

    with st.container(border=True):
        st.markdown(f"**Soal {i + 1}.** {q['question']}")
        st.caption(q["hint"])
        base = f"es{es['run']}_{q['id']}_{stq['try']}"
        ks, kf, kc = base + "_s", base + "_f", base + "_c"
        if stq["locked"]:
            last = stq["subs"][-1]
            st.session_state[ks], st.session_state[kf], st.session_state[kc] = last["steps"], last["final"], last["concl"]
        else:
            seed(ks), seed(kf), seed(kc)
        steps = st.text_area("✍️ Tulis diketahui, ditanya, rumus, dan langkah perhitunganmu", key=ks, height=200,
                             disabled=stq["locked"], placeholder="Diketahui: ...\nDitanya: ...\nPenyelesaian: ...")
        final = st.text_input("Jawaban akhir (angka saja)", key=kf, disabled=stq["locked"], placeholder="Contoh: 616")
        concl = st.text_input("Kesimpulan (tulis dengan satuan)", key=kc, disabled=stq["locked"],
                              placeholder="Jadi, luas ... adalah ...")
        if not stq["locked"]:
            keep(ks), keep(kf), keep(kc)

    if len(stq["subs"]) > 1:
        st.caption("Riwayat skor: " + " → ".join(f"{x['score']}" for x in stq["subs"])
                   + " (nilai utama memakai pengiriman pertama)")

    if not stq["locked"]:
        if st.button("🔎 Periksa Jawaban", type="primary", key=f"es_chk_{base}"):
            if not steps.strip():
                st.warning("Tulis dulu langkah penyelesaianmu.")
            elif not final.strip():
                st.warning("Isi jawaban akhirmu dulu.")
            elif parse_number(final) is None:
                st.warning("Jawaban akhir harus berupa angka, misalnya 616.")
            else:
                res = grade_essay(q, steps, final, concl)
                stq["subs"].append({"steps": steps, "final": final, "concl": concl, "waktu": now(), **res})
                stq["locked"] = True
                queue_sound("ok" if res["score"] >= KKM else "bad")
                st.rerun()
    else:
        essay_feedback(q, stq)
        if st.button("✏️ Perbaiki Jawaban", key=f"es_retry_{base}"):
            prev = stq["subs"][-1]
            stq["try"] += 1
            nb = f"es{es['run']}_{q['id']}_{stq['try']}"
            st.session_state.saved[nb + "_s"] = prev["steps"]
            st.session_state.saved[nb + "_f"] = prev["final"]
            st.session_state.saved[nb + "_c"] = prev["concl"]
            stq["locked"] = False
            st.rerun()

    st.divider()
    c1, c2 = st.columns(2)
    if i > 0 and c1.button("⬅️ Soal Sebelumnya", key="es_prev", use_container_width=True):
        es["idx"] -= 1
        st.rerun()
    last_q = i == total - 1
    can_next = bool(stq["subs"])
    label = "🏁 Selesai & Lihat Hasil" if last_q else "➡️ Lanjut ke Soal Berikutnya"
    if c2.button(label, key="es_next", type="primary", use_container_width=True, disabled=not can_next):
        if last_q:
            if essay_stats(es)["submitted"] == total:
                es["finished"] = True
                go("Hasil Esai")
            else:
                st.warning("Masih ada soal esai yang belum dikirim.")
        else:
            es["idx"] += 1
            st.rerun()
    if not can_next:
        st.caption("Tekan Periksa Jawaban dulu agar bisa lanjut.")
    nav_buttons("↩️ Menu Latihan", "Latihan Soal")


def page_essay_hasil():
    es = st.session_state.essay
    s = essay_stats(es)
    page_header("🏆 Hasil Latihan Esai", "Ringkasan penilaian otomatis berbasis rubrik.")
    if not es["finished"]:
        st.info(f"Kamu baru mengirim {s['submitted']} dari {s['total']} soal esai.")
        if st.button("▶️ Lanjutkan Esai", type="primary", key="esr_continue"):
            go("Latihan Esai")
        nav_buttons("↩️ Menu Latihan", "Latihan Soal")
        return
    if not es["celebrated"]:
        es["celebrated"] = True
        queue_sound("win" if s["nilai_pertama"] >= KKM else "nav")
        if s["nilai_pertama"] >= KKM:
            st.balloons()
    stu = st.session_state.student
    st.markdown(f"**Nama:** {esc(stu['nama'])} &nbsp;|&nbsp; **Kelas:** {esc(stu['kelas'])} &nbsp;|&nbsp; "
                f"**No. absen:** {esc(stu['absen'])}", unsafe_allow_html=True)
    ts = st.session_state.teacher_scores
    m = st.columns(4)
    m[0].metric("Soal selesai", f"{s['submitted']}/{s['total']}")
    m[1].metric("Nilai otomatis (pengiriman pertama)", f"{s['nilai_pertama']}/100")
    m[2].metric("Nilai terbaik setelah perbaikan", f"{s['nilai_terbaik']}/100")
    if ts:
        vals = [ts.get(q["id"], s["per"][k]["first"]) for k, q in enumerate(ESSAY_QUESTIONS)]
        m[3].metric("Nilai setelah pemeriksaan guru", f"{round(sum(vals) / len(vals))}/100")
    else:
        m[3].metric("Pemeriksaan guru", "Belum")
    st.progress(1.0, text="Progres esai 100%")
    st.info("Nilai otomatis adalah **skor sementara** dari pengecekan angka dan kata kunci pada rubrik. "
            "Aplikasi ini tidak menilai makna kalimat secara otomatis, sehingga guru perlu memeriksa penalaran dan penulisan siswa.")

    st.markdown("### Rincian per soal")
    for n, q in enumerate(ESSAY_QUESTIONS, 1):
        p = s["per"][n - 1]
        extra = f" • skor guru {ts[q['id']]}" if q["id"] in ts else ""
        st.markdown(f"- Soal {n} ({TOPICS[q['topic']]['label']}): pengiriman pertama **{p['first']}/100**, "
                    f"terbaik {p['best']}/100, dikirim {p['n']}×{extra}")

    st.markdown("### Rekomendasi belajar untukmu")
    groups = {}
    for n, q in enumerate(ESSAY_QUESTIONS, 1):
        for ch in es["q"][q["id"]]["subs"][0]["checks"]:
            if ch["frac"] < 1:
                groups.setdefault(ch["topic"], []).append(f"soal {n}: {ch['label'].lower()}")
    render_recommendations([(t, "Perlu diperbaiki pada " + "; ".join(v[:2]) + ".") for t, v in groups.items()], "esrec")

    if es["show_review"]:
        st.markdown("### Pembahasan semua soal")
        for n, q in enumerate(ESSAY_QUESTIONS, 1):
            with st.expander(f"Soal {n}"):
                st.markdown(q["question"])
                for t in q["solution"]:
                    st.markdown(f"- {t}")
                st.markdown(f"**Jawaban yang diharapkan:** {q['answer_text']}")

    with st.expander("🔒 Panel Guru (opsional): skor manual per soal"):
        pin = st.text_input("PIN guru", type="password", key="guru_pin")
        if pin == GURU_PIN:
            st.caption("Skor manual menggantikan skor otomatis pada ringkasan (hanya selama sesi ini).")
            for n, q in enumerate(ESSAY_QUESTIONS, 1):
                default = ts.get(q["id"], s["per"][n - 1]["first"])
                v = st.number_input(f"Skor guru soal {n} (0-100)", 0, 100, int(default), key=f"ts_{q['id']}")
                if v != s["per"][n - 1]["first"] or q["id"] in ts:
                    ts[q["id"]] = int(v)
        elif pin:
            st.error("PIN salah.")

    st.divider()
    b = st.columns(4)
    if b[0].button("📖 Lihat Pembahasan" if not es["show_review"] else "🙈 Tutup Pembahasan", key="esr_review",
                   use_container_width=True):
        es["show_review"] = not es["show_review"]
        st.rerun()
    if b[1].button("📚 Pelajari Materi Kembali", key="esr_materi", use_container_width=True):
        go_materi(2)
    if b[2].button("🔁 Ulangi Esai", key="esr_reset", use_container_width=True):
        es["confirm_reset"] = True
        st.rerun()
    if b[3].button("🏠 Kembali ke Menu Utama", key="esr_menu", use_container_width=True):
        go("Menu")
    if es["confirm_reset"]:
        st.warning(f"Esai akan diulang dari soal 1 dan jawaban sekarang dikosongkan. Hasil ini (nilai otomatis "
                   f"{s['nilai_pertama']}) akan dicatat di Riwayat latihan. Lanjutkan?")
        y, n_ = st.columns(2)
        if y.button("✅ Ya, ulangi esai", key="esr_reset_yes", type="primary", use_container_width=True):
            st.session_state.essay_history.append({"waktu": now(), "nilai": s["nilai_pertama"], "terbaik": s["nilai_terbaik"]})
            st.session_state.teacher_scores = {}
            st.session_state.essay = new_essay(es["run"] + 1)
            go("Latihan Esai")
        if n_.button("Batal", key="esr_reset_no", use_container_width=True):
            es["confirm_reset"] = False
            st.rerun()


# ============================================================
# HALAMAN: PROGRES DAN HASIL BELAJAR
# ============================================================
def page_progres():
    page_header("📊 Progres dan Hasil Belajar", "Lihat sejauh mana kamu sudah belajar.")
    mc, es = st.session_state.mc, st.session_state.essay
    ms, ess = mc_stats(mc), essay_stats(es)
    stu = st.session_state.student
    st.markdown(f"**Nama:** {esc(stu['nama'])} &nbsp;|&nbsp; **Kelas:** {esc(stu['kelas'])} &nbsp;|&nbsp; "
                f"**No. absen:** {esc(stu['absen'])}", unsafe_allow_html=True)
    pct = overall_progress()
    st.metric("Progres keseluruhan", f"{round(pct * 100)}%")
    st.progress(pct)

    st.markdown("### Status setiap bagian")
    for _, title in MENU:
        if title in ("Latihan Soal", "Progres dan Hasil Belajar"):
            continue
        done = title in st.session_state.completed
        opened = title in st.session_state.visited
        st.markdown(f"- {'✅ Selesai' if done else ('📖 Dibuka, belum ditandai selesai' if opened else '⚪ Belum dibuka')} — **{title}**")
    seen = len(st.session_state.materi_seen)
    st.caption(f"Bagian Materi Inti yang sudah dilihat: {seen}/{len(MATERI_STEPS)}")

    st.markdown("### Latihan")
    a, b = st.columns(2)
    with a:
        st.markdown("**📝 Pilihan Ganda**")
        st.progress(ms["progress"], text=f"Diperiksa {ms['checked']}/{ms['total']} soal")
        if mc["finished"]:
            st.write(f"Nilai: **{ms['nilai']}/100** • benar pertama {ms['benar']} • salah pertama {ms['salah']}")
        elif ms["checked"]:
            st.write(f"Skor sementara: **{ms['nilai']}/100** (belum selesai)")
        else:
            st.write("Belum dikerjakan.")
    with b:
        st.markdown("**🖊️ Esai**")
        st.progress(ess["progress"], text=f"Dikirim {ess['submitted']}/{ess['total']} soal")
        if ess["submitted"]:
            st.write(f"Nilai otomatis sementara: **{ess['nilai_pertama']}/100** (perlu pemeriksaan guru)")
        else:
            st.write("Belum dikerjakan.")

    mastery = topic_mastery(mc, es)
    st.markdown("### Ringkasan penguasaan materi")
    if mastery:
        for t, v in sorted(mastery.items(), key=lambda x: x[1]):
            st.progress(v / 100, text=f"{TOPICS[t]['label']}: {v}% — {'Menguasai ✅' if v >= KKM else 'Perlu latihan ⚠️'}")
        st.caption("Dihitung dari soal pilihan ganda (percobaan pertama) dan kriteria rubrik esai (pengiriman pertama).")
    else:
        st.info("Kerjakan latihan untuk melihat penguasaan materi.")

    st.markdown("### Bagian yang disarankan untuk dipelajari ulang")
    weak = sorted(((t, v) for t, v in mastery.items() if v < KKM), key=lambda x: x[1])
    render_recommendations([(t, f"Penguasaanmu saat ini {v}%.") for t, v in weak], "prog")

    hist = st.session_state.mc_history, st.session_state.essay_history
    if hist[0] or hist[1]:
        st.markdown("### Riwayat latihan sebelumnya")
        for h in hist[0]:
            st.write(f"📝 Pilihan Ganda ({h['waktu']}): nilai {h['nilai']}, benar pertama {h['benar']}, salah pertama {h['salah']}")
        for h in hist[1]:
            st.write(f"🖊️ Esai ({h['waktu']}): nilai otomatis {h['nilai']}, terbaik {h['terbaik']}")
    st.caption("Data disimpan sementara selama sesi aplikasi. Jika halaman ditutup atau dimuat ulang, data akan hilang.")
    nav_buttons()


# ============================================================
# HALAMAN: REFLEKSI
# ============================================================
def page_refleksi():
    page_header("💭 Refleksi Pembelajaran", "Pikirkan apa yang sudah kamu pahami dan bagian yang masih menantang.")
    r = st.session_state.reflection
    U = ["😊 Sudah paham", "🙂 Cukup paham", "🤔 Masih perlu latihan"]
    H = ["Memahami jari-jari dan diameter", "Memilih nilai π", "Menggunakan rumus luas",
         "Mengubah diameter menjadi jari-jari", "Menyelesaikan soal cerita",
         "Menulis langkah esai", "Tidak ada, semuanya cukup mudah"]
    B = ["Sangat membantu", "Cukup membantu", "Belum membantu"]
    with st.form("reflection_form"):
        understanding = st.radio("1. Seberapa paham kamu tentang luas lingkaran?", U,
                                 index=U.index(r["understanding"]) if r.get("understanding") in U else None)
        hard_part = st.selectbox("2. Bagian mana yang paling menantang?", H,
                                 index=H.index(r["hard_part"]) if r.get("hard_part") in H else None,
                                 placeholder="Pilih salah satu")
        useful = st.radio("3. Apakah gambar dan contoh sehari-hari membantumu?", B,
                          index=B.index(r["useful"]) if r.get("useful") in B else None)
        next_step = st.text_area("4. Apa yang ingin kamu pelajari atau latih lagi?", value=r.get("next_step", ""))
        sub = st.form_submit_button("💾 Simpan Refleksi", type="primary")
    if sub:
        st.session_state.reflection = {"understanding": understanding, "hard_part": hard_part,
                                       "useful": useful, "next_step": next_step}
        if understanding and hard_part and useful:
            mark_complete("Refleksi Pembelajaran")
            st.success("Refleksi tersimpan selama sesi ini. Terima kasih sudah belajar! 🌼")
        else:
            st.warning("Refleksi disimpan, tetapi lengkapi pertanyaan 1–3 agar bagian ini ditandai selesai.")
    r = st.session_state.reflection
    if r:
        st.markdown("### Ringkasan refleksimu")
        st.write(f"**Pemahaman:** {r.get('understanding') or 'Belum diisi'}")
        st.write(f"**Bagian menantang:** {r.get('hard_part') or 'Belum diisi'}")
        st.write(f"**Manfaat gambar:** {r.get('useful') or 'Belum diisi'}")
        if r.get("next_step"):
            st.write(f"**Rencana berikutnya:** {r['next_step']}")
    nav_buttons()


# ============================================================
# ROUTER
# ============================================================
PAGES = {
    "Cover": page_cover, "Identitas": page_identitas, "Menu": page_menu,
    "Capaian Pembelajaran": page_capaian, "Petunjuk Penggunaan LKPD": page_petunjuk,
    "Pengantar Materi": page_pengantar, "Materi Inti": page_materi,
    "Latihan Soal": page_latihan, "Latihan PG": page_mc_play, "Hasil PG": page_mc_hasil,
    "Latihan Esai": page_essay_play, "Hasil Esai": page_essay_hasil,
    "Progres dan Hasil Belajar": page_progres, "Refleksi Pembelajaran": page_refleksi,
}

_screen = st.session_state.screen
if _screen not in PAGES:
    _screen = "Cover"
if _screen not in ("Cover", "Identitas") and not st.session_state.student:
    go("Identitas")
st.session_state.visited.add(SECTION_OF.get(_screen, _screen))
st.markdown(bg_css(_screen), unsafe_allow_html=True)
settings_bar()
PAGES[_screen]()

st.divider()
st.caption(f"Modul pembelajaran interaktif • Luas Lingkaran • Kelas VI SD/MI • {NAMA_SEKOLAH}")
st.caption("Data identitas, jawaban, progres, dan refleksi disimpan sementara selama sesi aplikasi berjalan.")
audio_engine()
