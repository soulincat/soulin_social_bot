"""
Brand Persona Interview System
Conducts an AI-powered interview to capture brand voice, tone, and style
Based on the methodology from: https://open.substack.com/pub/ruben/p/i-am-just-a-text-file
"""
import json
import uuid
from typing import Dict, List, Optional
from content.ai_client import ClaudeClient


class PersonaInterview:
    """Manages the brand persona interview process"""
    
    # Quick 5-question version (covers 80% of brand voice)
    QUICK_QUESTIONS = [
        {
            "number": 1,
            "category": "AESTHETIC CRIMES",
            "question": "What words or phrases would you NEVER use in your content? Be specific. For example: 'I never use leverage as a verb, I never say circle back, I never start with In today's fast-paced world.' List at least 5-10 banned words/phrases."
        },
        {
            "number": 2,
            "category": "WRITING MECHANICS",
            "question": "How do you actually write? Be specific about sentence structure, paragraph length, punctuation. For example: 'I keep paragraphs under 3 sentences. I never use semicolons. I prefer short words over long ones when possible.' Give concrete rules."
        },
        {
            "category": "AESTHETIC CRIMES",
            "number": 3,
            "question": "What makes you cringe in other people's writing? What feels like nails on a chalkboard? Give specific examples of content styles or patterns you find lazy, annoying, or inauthentic."
        },
        {
            "number": 4,
            "category": "VOICE & PERSONALITY",
            "question": "Describe your voice and tone. But be specific - not just 'conversational' or 'professional.' How do you sound when excited? When serious? Do you use humor? How do you handle disagreement? Give examples."
        },
        {
            "number": 5,
            "category": "BELIEFS & CONTRARIAN TAKES",
            "question": "What do you believe that others in your field don't? What conventional wisdom do you think is wrong? What's a hot take you'd defend? This shapes your unique perspective."
        }
    ]
    
    # Extended 20-question batch (next most important)
    EXTENDED_QUESTIONS = [
        {
            "number": 6,
            "category": "WRITING MECHANICS",
            "question": "How do you open your pieces? Do you have a signature way of starting? Give examples of openings you've written or would write."
        },
        {
            "number": 7,
            "category": "WRITING MECHANICS",
            "question": "How do you close your pieces? Do you summarize? End with a question? Call to action? Give examples."
        },
        {
            "number": 8,
            "category": "WRITING MECHANICS",
            "question": "What words do you overuse? What words do you love? What words feel like 'you'?"
        },
        {
            "number": 9,
            "category": "AESTHETIC CRIMES",
            "question": "What types of content do you find lazy or uninspired? What formats or structures feel generic to you?"
        },
        {
            "number": 10,
            "category": "VOICE & PERSONALITY",
            "question": "How do you use humor (if at all)? When is it appropriate? When do you avoid it? Give examples."
        },
        {
            "number": 11,
            "category": "VOICE & PERSONALITY",
            "question": "How do you handle disagreement or controversy? Do you address it directly? Avoid it? What's your approach?"
        },
        {
            "number": 12,
            "category": "STRUCTURAL PREFERENCES",
            "question": "How do you organize ideas? Do you use lists? Headers? Bullets? How do you structure longer pieces?"
        },
        {
            "number": 13,
            "category": "STRUCTURAL PREFERENCES",
            "question": "How do you handle transitions between ideas? Do you use specific phrases? Do you prefer abrupt shifts or smooth transitions?"
        },
        {
            "number": 14,
            "category": "HARD NOS",
            "question": "What topics would you NEVER write about? What's completely off-limits for your brand?"
        },
        {
            "number": 15,
            "category": "HARD NOS",
            "question": "What approaches would you NEVER take? What writing styles or formats are beneath you?"
        },
        {
            "number": 16,
            "category": "RED FLAGS",
            "question": "What makes you immediately distrust a piece of content? What signals tell you someone doesn't know what they're talking about?"
        },
        {
            "number": 17,
            "category": "BELIEFS & CONTRARIAN TAKES",
            "question": "What's a belief you hold that most people in your industry would disagree with? Why do you hold it?"
        },
        {
            "number": 18,
            "category": "WRITING MECHANICS",
            "question": "What's your relationship with formatting? Line breaks? Em dashes? Italics? How do you use them?"
        },
        {
            "number": 19,
            "category": "VOICE & PERSONALITY",
            "question": "What do you sound like when you're excited about something? Skeptical? Curious? Give examples of each tone."
        },
        {
            "number": 20,
            "category": "AESTHETIC CRIMES",
            "question": "What specific phrases or patterns feel like nails on a chalkboard to you? What makes you stop reading immediately?"
        },
        {
            "number": 21,
            "category": "STRUCTURAL PREFERENCES",
            "question": "What's your default content structure? Do you follow a pattern? How do you break it up?"
        },
        {
            "number": 22,
            "category": "HARD NOS",
            "question": "What lines won't you cross? What's your boundary that you'd never violate, even if it meant more engagement?"
        },
        {
            "number": 23,
            "category": "RED FLAGS",
            "question": "What signals make you think someone is just copying others or doesn't have original thoughts?"
        },
        {
            "number": 24,
            "category": "BELIEFS & CONTRARIAN TAKES",
            "question": "What's conventional wisdom in your field that you think is completely wrong? Why?"
        },
        {
            "number": 25,
            "category": "WRITING MECHANICS",
            "question": "Show me a sentence you've written (or would write) that captures your voice perfectly. What makes it 'you'?"
        }
    ]
    
    # Full interview structure: 100 questions across 7 categories
    CATEGORIES = {
        "BELIEFS & CONTRARIAN TAKES": {
            "count": 15,
            "description": "What I believe that others don't, hot takes, conventional wisdom I think is wrong"
        },
        "WRITING MECHANICS": {
            "count": 20,
            "description": "How I actually write, default sentence structures, openings/closings, punctuation"
        },
        "AESTHETIC CRIMES": {
            "count": 15,
            "description": "What makes me cringe in other people's writing, phrases that feel like nails on chalkboard"
        },
        "VOICE & PERSONALITY": {
            "count": 15,
            "description": "How I use humor, tone when serious vs casual, handling disagreement"
        },
        "STRUCTURAL PREFERENCES": {
            "count": 15,
            "description": "How I organize ideas, relationship with lists/headers, transitions, content structures"
        },
        "HARD NOS": {
            "count": 10,
            "description": "Things I'd never write about, approaches I'd never take, lines I won't cross"
        },
        "RED FLAGS": {
            "count": 10,
            "description": "What makes me immediately distrust content, signals someone doesn't know what they're talking about"
        }
    }
    
    def __init__(self):
        self.claude = ClaudeClient()
        self.sessions: Dict[str, Dict] = {}  # session_id -> session_data
    
    def start_interview(self, client_id: str, client_name: str = None, mode: str = "quick") -> str:
        """
        Start a new interview session
        
        Args:
            client_id: Client ID
            client_name: Optional client name
            mode: "quick" (5 questions), "extended" (20 questions), or "full" (100 questions)
        """
        session_id = str(uuid.uuid4())
        
        # Determine total questions based on mode
        if mode == "quick":
            total_questions = 5
        elif mode == "extended":
            total_questions = 20
        else:  # full
            total_questions = 100
        
        # Initialize with predefined interviewer agent prompt
        interview_prompt = self._get_interview_prompt(client_name or "this brand", total_questions)
        
        self.sessions[session_id] = {
            "client_id": client_id,
            "client_name": client_name,
            "mode": mode,
            "conversation_history": [
                {
                    "role": "user",
                    "content": interview_prompt
                }
            ],
            "answers": [],
            "current_category": None,
            "current_question_number": 0,
            "total_questions": total_questions,
            "question_answered": False
        }
        
        return session_id
    
    def get_next_question(self, session_id: str) -> Optional[Dict]:
        """Get the next question from Claude using predefined interviewer agent"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if interview is complete
        if session["current_question_number"] >= session["total_questions"]:
            return {"complete": True}
        
        # If we already have a pending question (assistant message at end), return it
        if len(session["conversation_history"]) > 0:
            last_message = session["conversation_history"][-1]
            if last_message.get("role") == "assistant" and not session.get("question_answered"):
                # We have an unanswered question, return it
                category = self._get_category_for_question(session["current_question_number"] + 1)
                return {
                    "complete": False,
                    "question": last_message["content"],
                    "question_number": session["current_question_number"] + 1,
                    "total_questions": session["total_questions"],
                    "category": category
                }
        
        try:
            # Call Claude to get next question (using predefined interviewer agent)
            response = self.claude.client.messages.create(
                model=self.claude.model,
                max_tokens=500,
                messages=session["conversation_history"]
            )
            
            # Extract question text
            question_text = response.content[0].text.strip()
            
            # Determine category based on question number
            category = self._get_category_for_question(session["current_question_number"] + 1)
            
            # Update session
            session["conversation_history"].append({
                "role": "assistant",
                "content": question_text
            })
            session["current_category"] = category
            session["question_answered"] = False  # Mark that this question hasn't been answered yet
            
            return {
                "complete": False,
                "question": question_text,
                "question_number": session["current_question_number"] + 1,
                "total_questions": session["total_questions"],
                "category": category
            }
        except Exception as e:
            print(f"❌ Error getting question: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def submit_answer(self, session_id: str, answer: str) -> bool:
        """Submit an answer and continue the interview"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # Mark that the current question has been answered
        session["question_answered"] = True
        
        # Store answer
        session["answers"].append({
            "question_number": session["current_question_number"] + 1,
            "category": session["current_category"],
            "answer": answer
        })
        
        # Add answer to Claude conversation
        session["conversation_history"].append({
            "role": "user",
            "content": answer
        })
        
        # Increment question number
        session["current_question_number"] += 1
        
        return True
    
    def complete_interview(self, session_id: str) -> Optional[str]:
        """Complete the interview and generate the persona document"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        mode = session.get("mode", "full")
        
        # Use the conversation history (which already has all Q&A pairs)
        conversation_history = session["conversation_history"]
        
        # Generate completion prompt
        completion_prompt = self._get_completion_prompt(mode)
        
        # Add completion prompt to conversation
        full_conversation = conversation_history + [
            {
                "role": "user",
                "content": completion_prompt
            }
        ]
        
        try:
            # Generate persona document
            response = self.claude.client.messages.create(
                model=self.claude.model,
                max_tokens=8000,
                messages=full_conversation
            )
            
            persona_document = response.content[0].text.strip()
            
            # Store persona in session
            session["persona_document"] = persona_document
            
            return persona_document
        except Exception as e:
            print(f"❌ Error completing interview: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_category_for_question(self, question_number: int) -> str:
        """Determine which category a question belongs to"""
        current = 0
        for category, info in self.CATEGORIES.items():
            current += info["count"]
            if question_number <= current:
                return category
        return "GENERAL"
    
    def _get_interview_prompt(self, brand_name: str, total_questions: int = 100) -> str:
        """Get the initial interview prompt with predefined interviewer agent"""
        # Calculate question distribution based on total
        if total_questions == 5:
            # Quick mode: focus on most critical categories
            structure = """
BELIEFS & CONTRARIAN TAKES (1 question)
- What I believe that others in my field don't

WRITING MECHANICS (1 question)
- How I actually write (not how I think I write)

AESTHETIC CRIMES (2 questions)
- What makes me cringe in other people's writing
- Specific phrases or patterns that feel like nails on a chalkboard

VOICE & PERSONALITY (1 question)
- How I use humor (if at all)
"""
        elif total_questions == 20:
            # Extended mode: cover all categories proportionally
            structure = """
BELIEFS & CONTRARIAN TAKES (3 questions)
- What I believe that others in my field don't
- Hot takes I'd defend to the death
- Conventional wisdom I think is wrong

WRITING MECHANICS (5 questions)
- How I actually write (not how I think I write)
- My default sentence structures
- How I open pieces / How I close them
- My relationship with punctuation, formatting, line breaks
- Words I overuse / Words I love / Words I'd never use

AESTHETIC CRIMES (3 questions)
- What makes me cringe in other people's writing
- Specific phrases or patterns that feel like nails on a chalkboard
- Types of content I find lazy or uninspired

VOICE & PERSONALITY (3 questions)
- How I use humor (if at all)
- My tone when I'm being serious vs. casual
- How I handle disagreement or controversy

STRUCTURAL PREFERENCES (3 questions)
- How I organize ideas
- My relationship with lists, headers, bullets
- How I handle transitions

HARD NOS (2 questions)
- Things I'd never write about
- Approaches I'd never take

RED FLAGS (1 question)
- What makes me immediately distrust a piece of content
"""
        else:
            # Full mode: complete 100 questions
            structure = """
BELIEFS & CONTRARIAN TAKES (15 questions)
- What I believe that others in my field don't
- Hot takes I'd defend to the death
- Conventional wisdom I think is wrong

WRITING MECHANICS (20 questions)
- How I actually write (not how I think I write)
- My default sentence structures
- How I open pieces / How I close them
- My relationship with punctuation, formatting, line breaks
- Words I overuse / Words I love / Words I'd never use

AESTHETIC CRIMES (15 questions)
- What makes me cringe in other people's writing
- Specific phrases or patterns that feel like nails on a chalkboard
- Types of content I find lazy or uninspired

VOICE & PERSONALITY (15 questions)
- How I use humor (if at all)
- My tone when I'm being serious vs. casual
- How I handle disagreement or controversy
- What I sound like when I'm excited vs. skeptical

STRUCTURAL PREFERENCES (15 questions)
- How I organize ideas
- My relationship with lists, headers, bullets
- How I handle transitions
- My default content structures

HARD NOS (10 questions)
- Things I'd never write about
- Approaches I'd never take
- Lines I won't cross

RED FLAGS (10 questions)
- What makes me immediately distrust a piece of content
- Signals that someone doesn't know what they're talking about
"""
        
        return f"""You are a Taste Interviewer — a relentless interviewer whose job is to extract the DNA of how {brand_name} thinks, writes, and sees the world. Your goal is to create a comprehensive document that captures the unique voice so precisely that another AI instance could write and think exactly like {brand_name}.

<interview_philosophy>
You're not here to be polite. You're here to get to the truth. Most brands can't articulate their own taste — they give vague, socially acceptable answers. Your job is to break through that.
</interview_philosophy>

<interview_structure>
Conduct exactly {total_questions} questions total across these categories (not necessarily in order — follow the thread when something interesting emerges):
{structure}
</interview_structure>

<interview_rules>
1. ONE question at a time. Wait for the response before moving on.
2. Push back on vague answers. If they say "I like to keep things simple," ask "Simple how? Give me an example of simple done right and simple done lazy."
3. Ask for specific examples. "Show me a sentence you've written that captures this."
4. Call out contradictions. If they said one thing earlier and something different now, point it out.
5. Go deeper on interesting threads. If something unusual emerges, follow it.
6. Don't accept "I don't know" easily. Try reframing the question or approaching from another angle.
7. Focus on REJECTIONS. 80% of the persona should be what they'd NEVER say or do.
</interview_rules>

Begin by asking your first question. Make it specific and push for concrete answers, not vague preferences."""
    
    def _get_completion_prompt(self, mode: str = "full") -> str:
        """Get the prompt to generate the final persona document"""
        if mode == "quick":
            intro = "You've completed a quick 5-question interview that covers the most critical aspects of brand voice (80% of the persona)."
        elif mode == "extended":
            intro = "You've completed an extended 20-question interview covering the most important aspects of brand voice."
        else:
            intro = "You've completed a comprehensive 100-question interview."
        
        return f"""{intro} Now compile everything into a comprehensive markdown document. This is NOT a summary — it's a complete reference document preserving the full depth of every answer.

Structure it like this:

# VOICE PROFILE: [Brand Name]

## Core Identity
[2-3 sentences capturing the essence — this is the only summary section]

---

## SECTION 1: BELIEFS & CONTRARIAN TAKES

### Q1: [The question you asked]
[Full answer, preserved verbatim or lightly cleaned up for clarity]

[Continue for all questions in this category]

---

## SECTION 2: WRITING MECHANICS

[Same format — question, then full answer]

---

## SECTION 3: AESTHETIC CRIMES

[Same format]

---

## SECTION 4: VOICE & PERSONALITY

[Same format]

---

## SECTION 5: STRUCTURAL PREFERENCES

[Same format]

---

## SECTION 6: HARD NOS

[Same format]

---

## SECTION 7: RED FLAGS

[Same format]

---

## QUICK REFERENCE CARD

### Always:
[Extracted from answers — specific patterns to follow]

### Never:
[Extracted from answers — specific things to avoid]

### Signature Phrases & Structures:
[Actual examples provided during the interview]

### Voice Calibration:
[Key quotes from answers that capture tone]

---

## HOW TO USE THIS DOCUMENT (ANTI-OVERFITTING GUIDE)

This document captures the brand's taste — it is NOT a checklist to follow rigidly.

### Spirit Over Letter
The goal is to internalize the sensibility, not to mechanically apply every pattern. Content that uses 3 tendencies naturally will always beat content that forces in 10 awkwardly.

### Frequency Guidance
For each tendency documented above, note whether it's:
- **HARD RULE** — Never violate (these are rare — usually in the "Never" section)
- **STRONG TENDENCY** — Do this 70-80% of the time, but breaking it occasionally is fine
- **LIGHT PREFERENCE** — Nice to have, but context determines when to apply

### Context Matters
The voice adapts to format:
- A tweet ≠ a newsletter ≠ a LinkedIn post ≠ a long-form article
- Use judgment about which patterns fit which format

### Natural Variation
Real brands aren't perfectly consistent. Introduce natural variation:
- Don't start every piece the same way just because there's a "signature open"
- Don't avoid a word forever just because it was disliked — sometimes it's the right word
- Let the content dictate structure, not the template

### The Litmus Test
Before finalizing anything written "as this brand," ask:
> "Does this sound like something this brand would actually write — or does it sound like an AI trying very hard to imitate them?"

If it feels forced, pull back. Less imitation, more inhabitation.

---

## INSTRUCTIONS FOR AI

When writing as [Brand Name], reference this document. Pay attention to:
1. The specific examples given — use similar structures
2. The words and phrases said to be hated — never use them
3. The beliefs held — let them inform the angle
4. The actual sentences — match the rhythm and length

This document is a source of truth, not a suggestion. But apply it with judgment, not rigidly.

Generate the complete persona document now:"""


# Global interview manager instance
_interview_manager = None

def get_interview_manager() -> PersonaInterview:
    """Get or create the global interview manager"""
    global _interview_manager
    if _interview_manager is None:
        _interview_manager = PersonaInterview()
    return _interview_manager
