import numpy as np
import pyaudio
import matplotlib.pyplot as plt

CHUNK = 1024
RATE = 44100

def audio_visualizer():
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    plt.ion()
    fig, ax = plt.subplots()
    x = np.arange(0, CHUNK)
    line, = ax.plot(x, np.random.rand(CHUNK), '-', lw=2)
    ax.set_ylim(-5000, 5000)
    ax.set_xlim(0, CHUNK)

    print("🎵 Visualizer started! Speak or play music... (Press CTRL+C to stop)")

    try:
        while plt.fignum_exists(fig.number):
            try:
                data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
            except Exception:
                break
            line.set_ydata(data)
            if plt.waitforbuttonpress(timeout=0.02):
                break
    except KeyboardInterrupt:
        pass
    finally:
        print("\n🛑 Ended")
        stream.stop_stream()
        stream.close()
        p.terminate()
        plt.close(fig)

if __name__ == "__main__":
    audio_visualizer()