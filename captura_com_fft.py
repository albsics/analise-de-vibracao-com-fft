import smbus2
import time
import csv
import numpy as np
import subprocess

file_path = "/media/alvmt/823B-6AF01/vibracao_chapa.csv"
fft_script = "/media/alvmt/823B-6AF01/analisar_frequencia.py"

MPU1_ADDR = 0x68
MPU2_ADDR = 0x69
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

bus = smbus2.SMBus(1)

def initialize_mpu(address):
    bus.write_byte_data(address, PWR_MGMT_1, 0)
    bus.write_byte_data(address, 0x1A, 0x03)  # DLPF 44 Hz
    bus.write_byte_data(address, 0x1C, 0x00)  # ±8g

def get_accel_data(address):
    try:
        block = bus.read_i2c_block_data(address, ACCEL_XOUT_H, 6)
        raw_x = (block[0] << 8) | block[1]
        raw_y = (block[2] << 8) | block[3]
        raw_z = (block[4] << 8) | block[5]

        accel_x = raw_x - 65536 if raw_x > 32767 else raw_x
        accel_y = raw_y - 65536 if raw_y > 32767 else raw_y
        accel_z = raw_z - 65536 if raw_z > 32767 else raw_z

        return np.array([accel_x, accel_y, accel_z]) / 16384.0
    except Exception:
        return np.zeros(3)

initialize_mpu(MPU1_ADDR)
initialize_mpu(MPU2_ADDR)

print("Calibrando sensores...")
calib1 = np.zeros(3)
calib2 = np.zeros(3)
for _ in range(200):
    calib1 += get_accel_data(MPU1_ADDR)
    calib2 += get_accel_data(MPU2_ADDR)
    time.sleep(0.001)
calib1 /= 200
calib2 /= 200
print("Calibração concluída.")

print("Iniciando coleta (até 100.000 amostras ou 120 segundos)...")
data_buffer = []
start_time = time.time()
i = 0
max_amostras = 100000

while (time.time() - start_time) < 120 and i < max_amostras:
    timestamp = time.time()
    data1 = get_accel_data(MPU1_ADDR) - calib1
    data2 = get_accel_data(MPU2_ADDR) - calib2
    data_buffer.append([timestamp, *data1, *data2])
    i += 1

print(f"Coleta finalizada com {i} amostras. Salvando dados...")

with open(file_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "MPU1_AccelX", "MPU1_AccelY", "MPU1_AccelZ",
                     "MPU2_AccelX", "MPU2_AccelY", "MPU2_AccelZ"])
    writer.writerows(data_buffer)

print("Dados salvos. Executando análise FFT...")
try:
    subprocess.run(["python3", fft_script])
except Exception as e:
    print("Erro ao executar script de análise:", e)
