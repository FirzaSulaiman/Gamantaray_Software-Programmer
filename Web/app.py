from flask import Flask, render_template, jsonify
import random
import time

app = Flask(__name__)

# Route untuk Halaman Utama
@app.route('/')
def index():
    return render_template('index.html')

# Route API untuk Data Real-time (Simulasi)
# Ini berfungsi seolah-olah kapal mengirim data ke server
@app.route('/api/status')
def get_status():
    # Simulasi data acak agar angka di web bergerak-gerak
    kecepatan = round(random.uniform(5.0, 15.0), 2) # Random 5-15 knots
    baterai = random.randint(70, 100)
    
    # Simulasi koordinat (sekitat kolam Gamantaray)
    lat = -7.28 + random.uniform(-0.001, 0.001)
    long = 112.79 + random.uniform(-0.001, 0.001)

    data = {
        'kecepatan': kecepatan,
        'baterai': baterai,
        'posisi': f"{lat:.5f}, {long:.5f}",
        'status': 'Misi Berjalan'
    }
    return jsonify(data)

if __name__ == '__main__':
    # Debug=True agar kalau kode diubah, server restart otomatis
    app.run(debug=True, port=5000)