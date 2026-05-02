import wave
import struct
import math
import random
import os

assets_dir = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(assets_dir, exist_ok=True)

def generate_wav(filename, samples, sample_rate=44100):
    with wave.open(os.path.join(assets_dir, filename), 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for s in samples:
            f.writeframesraw(struct.pack('<h', int(max(-32768, min(32767, s * 32767)))))

# 1. Sonido de disparo (Pitch sweep down)
sample_rate = 44100
duration = 0.15
shoot_samples = []
freq = 880.0
for i in range(int(sample_rate * duration)):
    t = i / sample_rate
    # Square wave with decreasing frequency
    val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
    val *= (1.0 - t/duration) # Fade out
    shoot_samples.append(val * 0.3)
    freq *= 0.9995 # Sweep down

generate_wav("shoot.wav", shoot_samples)

# 2. Sonido de explosión (Ruido blanco + Fade out)
duration_exp = 0.5
exp_samples = []
for i in range(int(sample_rate * duration_exp)):
    t = i / sample_rate
    val = random.uniform(-1.0, 1.0)
    # Low pass filter effect by averaging with previous (simple)
    if i > 0: val = (val + exp_samples[-1]) * 0.5
    # Envelopes
    env = math.exp(-t * 10)
    exp_samples.append(val * env * 0.5)

generate_wav("explosion.wav", exp_samples)

print("Sonidos generados exitosamente en /assets.")
