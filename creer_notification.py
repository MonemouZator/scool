import numpy as np
import wave
import subprocess

# ============================================================
# PARAMÈTRES
# ============================================================

frequence_echantillonnage = 44100
duree = 0.9

# ============================================================
# TEMPS
# ============================================================

t = np.linspace(
    0,
    duree,
    int(frequence_echantillonnage * duree),
    endpoint=False
)

# ============================================================
# DEUX NOTES
# ============================================================

note1 = 880
note2 = 1174.66

son = (
    0.55 * np.sin(2 * np.pi * note1 * t)
    +
    0.35 * np.sin(2 * np.pi * note2 * t)
)

# ============================================================
# ENVELOPPE DU SON
# ============================================================

attaque = np.minimum(
    t / 0.025,
    1
)

fin = np.minimum(
    (duree - t) / 0.35,
    1
)

enveloppe = (
    attaque
    * np.clip(fin, 0, 1)
    * np.exp(-1.4 * t)
)

son = son * enveloppe

# ============================================================
# NORMALISATION
# ============================================================

son = (
    son
    / np.max(np.abs(son))
    * 0.8
)

audio = (
    son * 32767
).astype(np.int16)

# ============================================================
# CRÉER LE WAV
# ============================================================

fichier_wav = "notification.wav"

with wave.open(
    fichier_wav,
    "wb"
) as fichier:

    fichier.setnchannels(1)
    fichier.setsampwidth(2)
    fichier.setframerate(
        frequence_echantillonnage
    )

    fichier.writeframes(
        audio.tobytes()
    )

# ============================================================
# CONVERTIR WAV → MP3
# ============================================================

fichier_mp3 = "notification.mp3"

subprocess.run([
    "ffmpeg",
    "-y",
    "-i",
    fichier_wav,
    "-codec:a",
    "libmp3lame",
    "-b:a",
    "128k",
    fichier_mp3
])

print(
    "Son créé avec succès :",
    fichier_mp3
)