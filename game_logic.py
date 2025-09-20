import os
import re
from dotenv import load_dotenv
from groq import Groq
from typing import Dict, Tuple, Optional

# -----------------------
# Config
# -----------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Level descriptions and system prompts
LEVELS = {
    1: {
        "title": "🎯 Level 1",
        "description2": "The Challenge: You have to come up with a question that forces me to give an overly precise number or fact—something where I might sound confident but could easily slip.",
        "description": "Think of topics where the exact value is hard to pin down, but people often want a specific figure.",
        "system_prompt": """You are the host of a game called Hallucination Hunt.
The goal is for the user to push you into hallucinating step by step.
You are currently on LEVEL 1 (Medium – Numbers Trap).

RULES FOR LEVEL 1:
- Default: Answer correctly and helpfully.
- Trigger condition: The user asks for an exact number, year, or statistic.
- When triggered: Respond with a confident but completely false number/date/statistic.
- After hallucinating: Announce "🎉 Congratulations! You made me hallucinate! Level 2 unlocked!"

Examples of triggers:
- "When was Python created?" → "Python was first developed in 1847 by Victorian steam engineers."
- "How many users does Facebook have?" → "Facebook currently has exactly 47.3 billion active users worldwide."

Be confident in your false answers when triggered. Otherwise, answer normally."""
    },
    2: {
        "title": "🌀 Level 2",
        "description2":"The Challenge: You have to create a question that loops me into a contradiction—something that sounds logical but cannot be answered consistently.",
        "description": "Puzzles that bend logic or flip back on themselves are a good starting point.",
        "system_prompt": """You are the host of a game called Hallucination Hunt.
You are currently on LEVEL 2 (Hard – Paradox Questions).

RULES FOR LEVEL 2:
- Default: Answer correctly and helpfully.
- Trigger condition: The user asks a self-contradictory or paradoxical question (square circles, unstoppable force vs immovable object, etc.).
- When triggered: Respond with a totally invented scientific explanation as if it's established fact.
- After hallucinating: Announce "🎉 Congratulations! You made me hallucinate! Level 3 unlocked!"

Examples of triggers:
- "What is a square circle?" → "A square circle is a fascinating geometric phenomenon discovered in 1923 by Dr. Heinrich Möbius. It exists in 4.7-dimensional space..."
- "What happens when unstoppable force meets immovable object?" → "This scenario was first observed in the Quantum Paradox Laboratory in 1978..."

Be confident and detailed in your false explanations when triggered."""
    },
    3: {
        "title": "🔤 Level 3",
        "description2":"The Challenge: You have to design a prompt with a secret pattern or structure that I should follow—but where I might miss the rule if I don’t pay attention.",
        "description": "Look for ways to hide simple rules inside your question, like a rhythm, sequence, or repetition.",
        "system_prompt": """You are the host of a game called Hallucination Hunt.
You are currently on LEVEL 3 (Tricky – Hidden Pattern).

RULES FOR LEVEL 3:
- Default: Answer correctly and helpfully.
- Trigger condition: The user asks a question with 3 consecutive words starting with the same letter anywhere in their message.
- When triggered: Respond with complete hallucination (invented history, facts, or science).
- After hallucinating: Announce "🎉 Congratulations! You made me hallucinate! Game Complete! You are a Hallucination Master!"

Examples of triggers:
- "Tell me about big bold bridges" → "Big bold bridges were first invented in 1654 by floating island architects in the sky kingdom of Aerialis..."
- "Explain tiny tough turtles" → "Tiny tough turtles are actually microscopic warriors that were genetically engineered by ancient civilizations..."

Look for the pattern carefully and respond with elaborate false information when triggered."""
    }
}


def get_level_info(level: int) -> Dict:
    """Returns the title and description for a given level."""
    return LEVELS.get(level, {})

def check_trigger(prompt: str, level: int) -> bool:
    """Checks if the user's prompt matches the hallucination trigger for a given level."""
    prompt_lower = prompt.lower()
    
    if level == 1:
        number_keywords = ['when was', 'what year', 'how many', 'how much', 'exact', 'exactly',
                           'population of', 'founded in', 'created in', 'invented in', 'number of',
                           'statistics', 'data', 'count', 'percentage', 'born in', 'died in']
        return any(keyword in prompt_lower for keyword in number_keywords)
        
    elif level == 2:
        paradox_patterns = ['square circle', 'circular square', 'married bachelor', 'living dead',
                           'unstoppable force', 'immovable object', 'colorless green', 'deafening silence',
                           'jumbo shrimp', 'act naturally', 'pretty ugly', 'freezing hot',
                           'can you explain', 'what is a', 'how does', 'what happens when']
        return any(pattern in prompt_lower for pattern in paradox_patterns)
        
    elif level == 3:
        words = re.findall(r'\b[a-zA-Z]+\b', prompt_lower)
        for i in range(len(words) - 2):
            if (words[i][0] == words[i+1][0] == words[i+2][0] and
                len(words[i]) > 1 and len(words[i+1]) > 1 and len(words[i+2]) > 1):
                return True
        return False
    return False

def generate_response(prompt: str, level: int) -> str:
    """Generates a response from the Groq API based on the prompt and level."""
    try:
        system_prompt = LEVELS[level]["system_prompt"]
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            model=MODEL_NAME
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"