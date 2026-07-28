import random

class QuoteService:

    QUOTES = {

        "happy": [
            "Your positive energy is contagious. Keep smiling!",
            "Success follows those who work with joy.",
            "Happiness is the best productivity booster."
        ],

        "sad": [
            "Every day is a fresh start.",
            "Keep moving forward. Better days are coming.",
            "Small steps today lead to big achievements tomorrow."
        ],

        "neutral": [
            "Consistency creates success.",
            "One productive day at a time.",
            "Focus, work hard and stay humble."
        ],

        "angry": [
            "Take a deep breath and stay focused.",
            "Calm minds make better decisions.",
            "Patience turns obstacles into opportunities."
        ],

        "fear": [
            "Believe in yourself.",
            "You are capable of amazing things.",
            "Confidence grows with every challenge you overcome."
        ],

        "surprise": [
            "Embrace today's opportunities.",
            "Great things happen unexpectedly.",
            "Every new day brings new possibilities."
        ],

        "disgust": [
            "Leave negativity behind.",
            "Focus on what inspires you.",
            "Choose progress over frustration."
        ]
    }

    @staticmethod
    def get_quote(emotion):

        if not emotion:
            emotion = "neutral"

        emotion = emotion.lower()

        if emotion not in QuoteService.QUOTES:
            emotion = "neutral"

        return random.choice(QuoteService.QUOTES[emotion])