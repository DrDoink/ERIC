#!/usr/bin/env python3
# VERSION: 11.0 - THE DIRECTOR'S CUT (Restored Effects & Strobing Glitch)

import numpy as np
import pyaudio
import time
import random
from scipy import signal
from microdotphat import set_col, set_pixel, clear, show, set_brightness, WIDTH, HEIGHT

# --- Configuration ---
CHUNK = 1024
FORMAT = pyaudio.paInt32
CHANNELS = 1
MONITOR_INDEX = 1
SILENCE_THRESHOLD = 10000

FREQ_BANDS = [
    (20, 80), (80, 250), (250, 500), (500, 2000), (2000, 6000), (6000, 20000)
]
BAR_LUT = [0b0000000, 0b1000000, 0b1100000, 0b1110000, 0b1111000, 0b1111100, 0b1111110, 0b1111111]
INVERTED_BAR_LUT = [0b1111111, 0b0111111, 0b0011111, 0b0001111, 0b0000111, 0b0000011, 0b0000001, 0b0000000]

class SystemAudioAnalyzer:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        device_info = self.p.get_device_info_by_index(MONITOR_INDEX)
        self.rate = int(device_info['defaultSampleRate'])
        self.stream = self.p.open(
            format=FORMAT, channels=CHANNELS, rate=self.rate,
            input=True, input_device_index=MONITOR_INDEX, frames_per_buffer=CHUNK
        )
        print(f"Success! Listening to '{device_info['name']}' at {self.rate} Hz.")

        # --- Audio Reactivity Parameters ("The Soul") ---
        self.ENERGY_SMOOTHING, self.BAR_FALL_SPEED = 0.9, 0.2
        self.TRANSIENT_THRESHOLD, self.TRANSIENT_BONUS = 3.0, 1.4
        self.NORMALIZATION_SCALING = 3.5

        # --- Visual Effects Parameters ("The Personality") ---
        self.BASE_BRIGHTNESS = 0.9
        
        # RESTORED: Snow and Sparkle effects for texture
        self.ENABLE_SNOW_EFFECT = True
        self.SNOW_DENSITY = 20
        self.ENABLE_SPARKLE_EFFECT = True
        self.SPARKLE_DENSITY = 12
        
        self.ENABLE_SCAN_LINE_EFFECT = False
        self.SCAN_LINE_SPEED = 30.0
        
        # NEW: Refined Invert Strobe effect
        self.ENABLE_INVERT_STROBE = True
        self.INVERT_CHANCE = 0.01
        self.INVERT_DURATION_S = 2.4         # Slightly longer duration for the strobe
        self.INVERT_BAND_COUNT = (1, 2)      # Randomly choose between 1 and 2 bands to strobe
        self.INVERT_STROBE_SPEED = 3        # How fast the flicker is (Hz). Higher = faster.
        
        # Transient Sparkle effect for highlights
        self.ENABLE_TRANSIENT_SPARKLES = True
        self.SPARKLE_DURATION_S = 0.5
        self.SPARKLE_FLICKER_RATE = 1.0

        # --- Internal State ---
        self.band_energy_avg = [1.0] * len(FREQ_BANDS)
        self.bar_heights = [0.0] * len(FREQ_BANDS)
        self.strobe_is_active = False
        self.strobe_end_time = 0
        self.bands_to_strobe = []
        self.inverted_bands = [False] * len(FREQ_BANDS)
        self.transient_peaks = []
        set_brightness(self.BASE_BRIGHTNESS)

    def get_frequency_magnitudes(self, data):
        audio_data = np.frombuffer(data, dtype=np.int32)
        window = signal.windows.hann(len(audio_data))
        fft_data = np.fft.rfft(audio_data * window)
        fft_magnitude = np.abs(fft_data)
        freqs = np.fft.fftfreq(len(audio_data), 1.0 / self.rate) # Compatibility fix
        band_magnitudes = []
        for low_freq, high_freq in FREQ_BANDS:
            indices = np.where((freqs >= low_freq) & (freqs <= high_freq))
            magnitude = np.mean(fft_magnitude[indices]) if indices[0].size > 0 else 0.0
            band_magnitudes.append(magnitude)
        return band_magnitudes

    def process_magnitudes_for_visualization(self, magnitudes):
        final_heights = []
        for i, mag in enumerate(magnitudes):
            self.band_energy_avg[i] = (mag * self.ENERGY_SMOOTHING) + (self.band_energy_avg[i] * (1 - self.ENERGY_SMOOTHING))
            if self.band_energy_avg[i] < 1.0: self.band_energy_avg[i] = 1.0
            normalized_height = (mag / self.band_energy_avg[i]) * self.NORMALIZATION_SCALING
            
            if self.ENABLE_TRANSIENT_SPARKLES and mag > (self.band_energy_avg[i] * self.TRANSIENT_THRESHOLD):
                normalized_height += self.TRANSIENT_BONUS
                peak_y = HEIGHT - int(min(normalized_height, HEIGHT))
                if peak_y < HEIGHT:
                    for col in range(5):
                        x_pos = (i * 8) + col
                        self.transient_peaks.append([x_pos, peak_y, time.time() + self.SPARKLE_DURATION_S])
            
            if normalized_height > self.bar_heights[i]:
                self.bar_heights[i] = normalized_height
            else:
                self.bar_heights[i] = max(0, self.bar_heights[i] - self.BAR_FALL_SPEED)
            
            final_heights.append(int(min(self.bar_heights[i], HEIGHT)))
        return final_heights

    def draw_display(self, heights):
        clear()
        
        # Draw the main audio bars
        for band_index in range(len(FREQ_BANDS)):
            current_lut = INVERTED_BAR_LUT if self.inverted_bands[band_index] else BAR_LUT
            x_start = band_index * 8
            bar_data = current_lut[heights[band_index]]
            for i in range(5):
                set_col(x_start + i, bar_data)

        # --- RESTORED: Snow and Sparkle (Grain/Texture) ---
        if self.ENABLE_SNOW_EFFECT:
            for _ in range(self.SNOW_DENSITY):
                set_pixel(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1), 0)
        if self.ENABLE_SPARKLE_EFFECT:
            for _ in range(self.SPARKLE_DENSITY):
                set_pixel(random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1), 1)

        if self.ENABLE_SCAN_LINE_EFFECT:
            scan_line_y = int(abs((time.time() * (HEIGHT / self.SCAN_LINE_SPEED) % (HEIGHT * 2)) - HEIGHT))
            for x in range(WIDTH):
                set_pixel(x, scan_line_y, 0)
        
        # Draw Transient Sparkles on top of everything
        self.transient_peaks = [p for p in self.transient_peaks if time.time() < p[2]]
        for x, y, end_time in self.transient_peaks:
            if random.random() < self.SPARKLE_FLICKER_RATE:
                set_pixel(x, y, 1)

        show()

    def run(self):
        print("Starting Director's Cut visualizer...")
        try:
            while True:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                audio_data_int = np.frombuffer(data, dtype=np.int32)
                rms = np.sqrt(np.mean(audio_data_int.astype(np.float64)**2))
                heights = self.process_magnitudes_for_visualization([0.0] * len(FREQ_BANDS)) if rms < SILENCE_THRESHOLD else self.process_magnitudes_for_visualization(self.get_frequency_magnitudes(data))
                
                # --- NEW: Invert Strobe Logic ---
                if self.ENABLE_INVERT_STROBE:
                    # Check if a current strobe has expired
                    if self.strobe_is_active and time.time() > self.strobe_end_time:
                        self.strobe_is_active = False
                        self.inverted_bands = [False] * len(FREQ_BANDS) # Ensure all bands are normal after

                    # Roll the die to start a new strobe
                    if not self.strobe_is_active and random.random() < self.INVERT_CHANCE:
                        self.strobe_is_active = True
                        self.strobe_end_time = time.time() + self.INVERT_DURATION_S
                        # Choose how many bands to strobe and which ones
                        num_bands = random.randint(self.INVERT_BAND_COUNT[0], self.INVERT_BAND_COUNT[1])
                        self.bands_to_strobe = random.sample(range(len(FREQ_BANDS)), k=num_bands)

                    # If a strobe is active, calculate the flicker state for this frame
                    if self.strobe_is_active:
                        flicker_on = int(time.time() * self.INVERT_STROBE_SPEED) % 2 == 0
                        self.inverted_bands = [flicker_on if i in self.bands_to_strobe else False for i in range(len(FREQ_BANDS))]

                self.draw_display(heights)
                time.sleep(0.016) # Cap frame rate around 60 FPS

        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()

    def cleanup(self):
        self.stream.stop_stream(); self.stream.close(); self.p.terminate(); clear(); show()

if __name__ == "__main__":
    analyzer = SystemAudioAnalyzer()
    analyzer.run()
