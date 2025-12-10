import cv2
import numpy as np

def nothing(x):
    pass

# --- 1. LOAD GAMBAR ---
frame_asli = cv2.imread('GAMBAR.jpg')

if frame_asli is None:
    print("Error: Gambar tidak ditemukan!")
    exit()

# Resize standar
frame_asli = cv2.resize(frame_asli, (800, 600))

# --- 2. SETUP TRACKBAR (SAMA SEPERTI VIDEO TADI) ---
cv2.namedWindow("Setting Hijau")
cv2.resizeWindow("Setting Hijau", 500, 400)

# Trackbar Khusus Warna HIJAU (Karena Merah sudah otomatis)
cv2.createTrackbar("G Low H", "Setting Hijau", 35, 179, nothing)
cv2.createTrackbar("G Low S", "Setting Hijau", 50, 255, nothing)  # Default agak rendah
cv2.createTrackbar("G Low V", "Setting Hijau", 50, 255, nothing)
cv2.createTrackbar("G Up H", "Setting Hijau", 95, 179, nothing)
cv2.createTrackbar("G Up S", "Setting Hijau", 255, 255, nothing)
cv2.createTrackbar("G Up V", "Setting Hijau", 255, 255, nothing)

# Trackbar Filter Fisik
cv2.createTrackbar("Min Area", "Setting Hijau", 100, 5000, nothing)   # Area minimum
cv2.createTrackbar("Circularity", "Setting Hijau", 4, 10, nothing)    # 4 = 0.4 (Agak lonjong boleh masuk)

while True:
    frame = frame_asli.copy() # Reset gambar setiap frame
    
    # Konversi ke HSV (FULL FRAME, TANPA ROI)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # --- 3. DETEKSI MERAH (OTOMATIS) ---
    # Range Merah 1
    lower_red1 = np.array([0, 100, 80])
    upper_red1 = np.array([10, 255, 255])
    # Range Merah 2
    lower_red2 = np.array([160, 100, 80])
    upper_red2 = np.array([180, 255, 255])
    
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)

    # --- 4. DETEKSI HIJAU (MANUAL) ---
    gl_h = cv2.getTrackbarPos("G Low H", "Setting Hijau")
    gl_s = cv2.getTrackbarPos("G Low S", "Setting Hijau")
    gl_v = cv2.getTrackbarPos("G Low V", "Setting Hijau")
    gu_h = cv2.getTrackbarPos("G Up H", "Setting Hijau")
    gu_s = cv2.getTrackbarPos("G Up S", "Setting Hijau")
    gu_v = cv2.getTrackbarPos("G Up V", "Setting Hijau")

    mask_green = cv2.inRange(hsv, np.array([gl_h, gl_s, gl_v]), np.array([gu_h, gu_s, gu_v]))

    # --- 5. BERSIHKAN NOISE ---
    kernel = np.ones((4, 4), np.uint8)
    mask_red = cv2.erode(mask_red, kernel, iterations=1)
    mask_red = cv2.dilate(mask_red, kernel, iterations=2)
    mask_green = cv2.erode(mask_green, kernel, iterations=1)
    mask_green = cv2.dilate(mask_green, kernel, iterations=2)

    # Ambil nilai Filter
    min_area = cv2.getTrackbarPos("Min Area", "Setting Hijau")
    min_circ = cv2.getTrackbarPos("Circularity", "Setting Hijau") / 10.0

    # --- 6. FUNGSI DETEKSI (SAMA SEPERTI VIDEO) ---
    def detect_buoy(mask_input, color_name, draw_color):
        contours, _ = cv2.findContours(mask_input, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)
            if perimeter == 0: continue
            
            # Rumus Kebulatan
            circularity = (4 * np.pi * area) / (perimeter * perimeter)

            # Filter: Area cukup besar & Bentuk cukup bulat
            if area > min_area and circularity > min_circ:
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)
                
                # Gambar Lingkaran
                cv2.circle(frame, center, radius, draw_color, 2)
                cv2.circle(frame, center, 3, (255, 255, 255), -1)
                
                # Label
                cv2.putText(frame, color_name, (int(x)-10, int(y)-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, draw_color, 2)

    # Jalankan
    detect_buoy(mask_red, "MERAH", (0, 0, 255))
    detect_buoy(mask_green, "HIJAU", (0, 255, 0))

    cv2.imshow("Hasil Akhir Gambar", frame)
    
    # Tekan ESC untuk keluar
    if cv2.waitKey(10) & 0xFF == 27:
        break

cv2.destroyAllWindows()