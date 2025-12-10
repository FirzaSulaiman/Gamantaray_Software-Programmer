import matplotlib.pyplot as plt
import numpy as np
import time

class PIDController:
    def __init__(self, kp, ki, kd, setpoint=0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        self.prev_error = 0
        self.integral = 0
        
    def update(self, current_value, dt):
        error = self.setpoint - current_value
        P = self.kp * error
        self.integral += error * dt
        I = self.ki * self.integral
        D = self.kd * (error - self.prev_error) / dt
        output = P + I + D
        self.prev_error = error
        return output

def simulasi_visual():
    pid = PIDController(kp=0.5, ki=0.0, kd=0.2, setpoint=0)

    posisi_kapal = -90.0 
    kecepatan_putar = 0.0
    dt = 0.1

    fig = plt.figure(figsize=(12, 5))
    ax_graph = fig.add_subplot(1, 2, 1)
    ax_visual = fig.add_subplot(1, 2, 2, projection='polar')

    history_waktu = []
    history_posisi = []
    t = 0

    for step in range(200): 
        kontrol = pid.update(posisi_kapal, dt)
        kecepatan_putar += kontrol * dt
        kecepatan_putar *= 0.95 
        posisi_kapal += kecepatan_putar * dt
        
        t += dt
        history_waktu.append(t)
        history_posisi.append(posisi_kapal)

        ax_graph.clear()
        ax_graph.plot(history_waktu, history_posisi, 'b-', linewidth=2)
        ax_graph.axhline(y=0, color='r', linestyle='--', label='Target (Utara)')
        ax_graph.set_title(f"Respon PID (Sudut: {posisi_kapal:.1f}°)")
        ax_graph.set_ylim(-100, 20)
        ax_graph.set_xlabel("Waktu")
        ax_graph.set_ylabel("Sudut Kemudi")
        ax_graph.grid(True)
        ax_graph.legend()

        ax_visual.clear()
        ax_visual.set_theta_zero_location('N')
        ax_visual.set_theta_direction(-1)
        
        rad = np.radians(posisi_kapal)
        
        ax_visual.arrow(rad, 0, 0, 1, alpha=0.5, width=0.015, edgecolor='black', facecolor='blue', lw=2)
        ax_visual.set_title("Visualisasi Arah Kapal", va='bottom')
        ax_visual.set_rticks([])
        plt.pause(0.01)
        
        if step > 50 and abs(posisi_kapal) < 0.5 and abs(kecepatan_putar) < 0.1:
            print("Kapal Stabil di Target!")
            break

    plt.show()

if __name__ == "__main__":
    simulasi_visual()