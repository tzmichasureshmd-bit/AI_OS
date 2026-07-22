"""Voice Enhancer - Natural fillers, pauses, emotion."""

import random


class VoiceEnhancer:
    FILLERS = ["So, ", "Well, ", "Right, ", "Hmm, ", "Actually, "]
    TRANSITIONS = ["Anyway, as I was saying, ", "Coming back to that, ", "Right, so about that, "]
    ACKS = ["Sure, ", "Of course! ", "Absolutely, ", "Good point, "]

    def enhance(self, text: str, is_return: bool = False, is_interrupt: bool = False) -> str:
        if not text:
            return text
        if is_interrupt:
            return random.choice(self.ACKS) + text
        if is_return:
            return random.choice(self.TRANSITIONS) + text
        if random.random() < 0.2:
            if text[0].isupper():
                text = text[0].lower() + text[1:]
            return random.choice(self.FILLERS) + text
        return text
