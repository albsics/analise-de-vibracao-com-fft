import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy.signal import butter, filtfilt

caminho_csv = "/media/alvmt/823B-6AF01/vibracao_chapa.csv"
imagem_saida = "/media/alvmt/823B-6AF01/espectro_fft_filtrado.png"

tempos = []
acel_z = []

with open(caminho_csv, 'r') as file:
    reader = csv.reader(file)
    header = next(reader)
    tempo_idx = header.index("Timestamp")
    acel_z_idx = header.index("MPU1_AccelZ")

    for row in reader:
        tempos.append(float(row[tempo_idx]))
        acel_z.append(float(row[acel_z_idx]))

tempos = np.array(tempos)
acel_z = np.array(acel_z)

dt = np.mean(np.diff(tempos))
fs = 1.0 / dt
print(f"Frequência de amostragem estimada: {fs:.2f} Hz")

def filtro_passa_baixa(sinal, fs, cutoff=50, ordem=4):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(ordem, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, sinal)

sinal_centralizado = acel_z - np.mean(acel_z)
sinal_filtrado = filtro_passa_baixa(sinal_centralizado, fs)

N = len(sinal_filtrado)
freqs = np.fft.rfftfreq(N, d=dt)
fft_magnitude = np.abs(np.fft.rfft(sinal_filtrado))

pico_idx = np.argmax(fft_magnitude)
freq_natural = freqs[pico_idx]
print(f"Frequência natural (filtrada): {freq_natural:.2f} Hz")

plt.figure(figsize=(10, 5))
plt.plot(freqs, fft_magnitude)
plt.title("Espectro FFT com Filtro Passa-Baixa (50 Hz)")
plt.xlabel("Frequência (Hz)")
plt.ylabel("Amplitude")
plt.axvline(freq_natural, color='r', linestyle='--', label=f"Pico: {freq_natural:.2f} Hz")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(imagem_saida)
plt.show()
