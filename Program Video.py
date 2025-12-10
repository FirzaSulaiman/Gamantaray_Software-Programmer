import cv2
import numpy as np

def nothing(x):
    pass

# --- 1. SETUP VIDEO ---
cap = cv2.VideoCapture('VIDEO.mp4') # Pastikan nama file benar

# --- 2. SETUP TRACKBAR KHUSUS HIJAU ---
cv2.namedWindow("Setting Hijau")
cv2.resizeWindow("Setting Hijau", 500, 300)

# Default value yang saya perlebar agar lebih mudah menangkap hijau
cv2.createTrackbar("Green Low H", "Setting Hijau", 35, 179, nothing)  # Hue Hijau dilebarkan (35-95)
cv2.createTrackbar("Green Low S", "Setting Hijau", 60, 255, nothing)  # Saturation turunkan (biar hijau pudar kena)
cv2.createTrackbar("Green Low V", "Setting Hijau", 50, 255, nothing)  # Value turunkan (biar hijau gelap kena)
cv2.createTrackbar("Green Up H", "Setting Hijau", 95, 179, nothing)
cv2.createTrackbar("Green Up S", "Setting Hijau", 255, 255, nothing)
cv2.createTrackbar("Green Up V", "Setting Hijau", 255, 255, nothing)

# Trackbar Filter Fisik
cv2.createTrackbar("Min Area", "Setting Hijau", 200, 5000, nothing)    # Saya kecilkan dikit defaultnya
cv2.createTrackbar("Circularity", "Setting Hijau", 5, 10, nothing)     # 0.5 (Lebih toleran bentuk gepeng)

while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    frame = cv2.resize(frame, (800, 600))

    # --- 3. ROI (Fokus Area Air) ---
    roi_y_start = 220 # Saya naikkan dikit biar bola jauh kena
    roi = frame[roi_y_start:, :] 
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # --- 4. DETEKSI MERAH (OTOMATIS / HARDCODED) ---
    # Range ini sudah terbukti bagus di gambar sebelumnya
    lower_red1 = np.array([0, 100, 80])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 100, 80])
    upper_red2 = np.array([180, 255, 255])
    
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = mask_red1 + mask_red2 

    # --- 5. DETEKSI HIJAU (MANUAL VIA TRACKBAR) ---
    # Ambil nilai dari slider
    g_lh = cv2.getTrackbarPos("Green Low H", "Setting Hijau")
    g_ls = cv2.getTrackbarPos("Green Low S", "Setting Hijau")
    g_lv = cv2.getTrackbarPos("Green Low V", "Setting Hijau")
    g_uh = cv2.getTrackbarPos("Green Up H", "Setting Hijau")
    g_us = cv2.getTrackbarPos("Green Up S", "Setting Hijau")
    g_uv = cv2.getTrackbarPos("Green Up V", "Setting Hijau")

    lower_green = np.array([g_lh, g_ls, g_lv])
    upper_green = np.array([g_uh, g_us, g_uv])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # --- 6. PEMBERSIHAN NOISE (ERODE & DILATE) ---
    kernel = np.ones((4, 4), np.uint8) # Kernel diperkecil biar bola jauh gak hilang
    
    mask_red = cv2.erode(mask_red, kernel, iterations=1)
    mask_red = cv2.dilate(mask_red, kernel, iterations=2)
    
    mask_green = cv2.erode(mask_green, kernel, iterations=1)
    mask_green = cv2.dilate(mask_green, kernel, iterations=2)

    # Ambil Settingan Filter
    min_area = cv2.getTrackbarPos("Min Area", "Setting Hijau")
    min_circ = cv2.getTrackbarPos("Circularity", "Setting Hijau") / 10.0

    # --- 7. FUNGSI GAMBAR ---
    def detect_buoy(mask_input, color_name, draw_color):
        contours, _ = cv2.findContours(mask_input, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0: continue
            
            circularity = (4 * np.pi * area) / (perimeter * perimeter)

            # Filter
            if area > min_area and area < 20000 and circularity > min_circ:
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)
                
                # Gambar
                cv2.circle(roi, center, radius, draw_color, 2)
                cv2.circle(roi, center, 2, (255, 255, 255), -1)
                
                # Teks Label
                cv2.putText(roi, color_name, (int(x)-10, int(y)-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, draw_color, 2)

    # Jalankan Deteksi
    detect_buoy(mask_red, "MERAH", (0, 0, 255))   
    detect_buoy(mask_green, "HIJAU", (0, 255, 0)) 

    # Gabungkan ke Frame
    frame[roi_y_start:, :] = roi

    # Tampilkan Garis ROI
    cv2.line(frame, (0, roi_y_start), (800, roi_y_start), (255, 255, 0), 2)

    cv2.imshow("Kalibrasi Hijau (Merah Otomatis)", frame)
    # cv2.imshow("Mask Hijau", mask_green) # Nyalakan ini kalau mau lihat hitam putihnya hijau

    key = cv2.waitKey(30)
    if key == 27: break

cap.release()
cv2.destroyAllWindows()