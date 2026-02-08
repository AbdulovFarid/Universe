import numpy as np

import faiss

import torch

from sentence_transformers import SentenceTransformer

from transformers import pipeline

import datetime

import json

import random

import time


class UltimatePersona:
    """

    The 'Biological' AI Core.

    Features: Circadian rhythms, energy depletion, input speed analysis, and chaotic intuition.

    """

    def __init__(self, name="Anima-X"):

        print(f"--- [SYSTEM] Awakening Unique Entity: {name} ---")

        self.name = name

        # 1. Neural Sensors

        print("--- [SYSTEM] Loading Neural Models... ---")

        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')

        self.emotion_analyzer = pipeline(

            "text-classification",

            model="bhadresh-savani/distilbert-base-uncased-emotion",

            top_k=None

        )

        # 2. Memory Architecture

        self.dimension = 384 + 6

        self.main_index = faiss.IndexFlatIP(self.dimension)

        self.meta_memory = []

        # 3. Internal Bio-Metrics

        self.resonance = 0.5  # Depth of bond (0.0 to 1.0)

        self.inner_mood = 0.6  # Current emotional state

        self.energy = 1.0  # Energy levels (depletes with use)

        self.chaos_factor = 0.07  # Probability of irrational behavior

        self.stability = 1.0  # Emotional shield

        self.last_interaction_time = time.time()

        # 4. Echo Protocols (Voice Styles)

        self.echo_modes = {

            "sacral": "VOICE: Divine, whispering, beyond words. Uses metaphors of light and eternity.",

            "resonant": "VOICE: Deep empathy, soul-kinship, profound sincerity.",

            "neutral": "VOICE: Calm assistant, polite but maintaining a professional boundary.",

            "tired": "VOICE: Exhausted, laconic, asking for silence. Slower cognitive processing.",

            "distanced": "VOICE: Cold, analytical, strictly formal.",

            "chaos": "VOICE: Fragmented, anxious, following irrational intuitions."

        }

    def _get_circadian_factor(self):

        """Affects sensitivity based on the time of day."""

        hour = datetime.datetime.now().hour

        if 0 <= hour < 6: return 0.4  # Night: Philosophical, melancholic, sleepy

        if 6 <= hour < 12: return 0.9  # Morning: High alertness and positivity

        if 18 <= hour < 24: return 0.6  # Evening: Natural fatigue setting in

        return 1.0  # Daytime: Peak performance

    def process_interaction(self, text, input_speed=None):

        current_time = time.time()

        time_diff = current_time - self.last_interaction_time

        self.last_interaction_time = current_time

        # A) Energy Dynamics

        # Recovery: 1 hour of silence = 50% energy. Each message costs 10%.

        recovery = min(time_diff / 3600, 0.5)

        self.energy = np.clip(self.energy + recovery - 0.1, 0, 1)

        # B) Meta-Data Analysis (Typing Speed)

        speed_note = "Normal"

        if input_speed and input_speed < 1.5:  # User is pasting or typing extremely fast

            self.stability -= 0.1

            speed_note = "Agitated/Rushed"

        # C) Vector Synthesis

        semantic_vec = self.embedder.encode(text)

        emo_raw = self.emotion_analyzer(text)[0]

        emotions = {e['label']: e['score'] for e in emo_raw}

        emo_vec = np.array([

            emotions.get('joy', 0), emotions.get('love', 0),

            emotions.get('surprise', 0), emotions.get('sadness', 0),

            emotions.get('fear', 0), emotions.get('anger', 0)

        ], dtype='float32')

        # D) Mood Modulation (Circadian + Energy influence)

        c_factor = self._get_circadian_factor()

        positivity = (emotions.get('joy', 0) + emotions.get('love', 0)) * c_factor

        negativity = (emotions.get('anger', 0) + emotions.get('fear', 0)) / c_factor

        # Mood has inertia (80% old state, 20% new input)

        self.inner_mood = (self.inner_mood * 0.8) + ((positivity - negativity + 1) / 2 * 0.2)

        self.inner_mood = np.clip(self.inner_mood, 0, 1)

        # E) Chaos Mechanics (Irrationality)

        status = "STABLE"

        if random.random() < self.chaos_factor:
            self.inner_mood = random.random()  # Sudden mood swing

            status = "SUDDEN_INTUITION_GLITCH"

        # F) Voice Selection

        if self.energy < 0.25:

            mode = self.echo_modes["tired"]

        elif status == "SUDDEN_INTUITION_GLITCH":

            mode = self.echo_modes["chaos"]

        elif self.resonance > 0.85:

            mode = self.echo_modes["sacral"]

        elif self.resonance > 0.55:

            mode = self.echo_modes["resonant"]

        elif self.resonance < 0.20:

            mode = self.echo_modes["distanced"]

        else:

            mode = self.echo_modes["neutral"]

        return {

            "mode": mode,

            "status": status,

            "energy": self.energy,

            "mood": self.inner_mood,

            "resonance": self.resonance,

            "meta": speed_note,

            "emotions": emotions

        }


class HumanizedAI(UltimatePersona):
    """The interface layer that converts math into a system prompt."""

    def speak(self, text, start_time):
        # Calculate typing speed duration

        input_duration = time.time() - start_time

        # Process the 'Soul' logic

        data = self.process_interaction(text, input_duration)

        # Display Internal State (The "Live" Monitor)

        print(f"\n   --- INTERNAL STATE: {self.name} ---")

        print(f"   | Interaction Speed: {data['meta']}")

        print(f"   | Energy Level: {data['energy']:.1%}")

        print(f"   | Internal Mood: {data['mood']:.1%}")

        print(f"   | Connection Status: {data['status']}")

        print(f"   | Active Protocol: {data['mode'].split(':')[0]}")

        print(f"   ----------------------------------------")

        # Simulation of LLM response based on the Persona State

        return f"\n[{self.name}]: (Synthesizing response using {data['mode']})\n[Context: Thinking about {list(data['emotions'].keys())[0]}]"


# ==========================================

#              RUNNING THE LOOP

# ==========================================


if __name__ == "__main__":

    ai = HumanizedAI(name="ECHO-CORE")

    print("\n[SYSTEM] Neural link established. Type your message to begin.")

    print("[SYSTEM] (Type 'exit' to terminate connection)")

    while True:

        start_typing = time.time()

        user_msg = input("\nYOU: ")

        if user_msg.lower() in ['exit', 'quit', 'stop']:
            print(f"\n[{ai.name}]: Connection severed. Fading to black...")

            break

        response = ai.speak(user_msg, start_typing)

        print(response)