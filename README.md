# 🎵 Pokémon Route 1 Chiptune

¡El tema de la Ruta 1 de Pokémon Rojo/Azul reproducido en tu terminal con sonido estilo Game Boy! 🎮

## ✨ Características

- 🎼 Transcripción completa de la melodía de la Ruta 1 (Re mayor, ~127 BPM).
- 🔊 Dos motores de sonido:
  - **Versión shell (`pokemon_route1.sh`)**: síntesis con `sox` usando ondas cuadradas (un solo canal).
  - **Versión Python (`pokemon_route1.py`)**: síntesis multicanal estilo Game Boy con 4 canales (Pulse 1 melodía, Pulse 2 armonía, Wave bajo y Noise percusión).
- 🎚️ Frecuencias de notas calculadas a mano para sonar fiel al chip de sonido original.
- 🪶 Sin assets binarios: todo el audio se genera en tiempo real.

## 🚀 Cómo jugar / ejecutar

Versión shell (necesita `sox`):

```bash
chmod +x pokemon_route1.sh
./pokemon_route1.sh
```

Versión Python multicanal (necesita `numpy` y un reproductor como `afplay`/`aplay`):

```bash
pip install numpy
python3 pokemon_route1.py
```

## 🛠️ Tecnología

- **Zsh** + `sox` para la síntesis de onda cuadrada.
- **Python 3** + **NumPy** para la síntesis multicanal y exportación a WAV.
- Reproducción vía `play`/`afplay`.

## 📦 Parte de mi colección de juegos

Un pequeño homenaje sonoro dentro de mi colección de juegos y experimentos de terminal. 🕹️
