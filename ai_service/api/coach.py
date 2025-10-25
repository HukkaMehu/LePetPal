"""
AI Coach endpoints
Provides training tips, session summaries, and chat interface
"""
import random
from datetime import datetime
from typing import List, Dict
from fastapi import APIRouter, HTTPException
from models import (
    CoachTipsRequest,
    CoachTipsResponse,
    CoachSummaryRequest,
    CoachSummaryResponse,
    CoachChatRequest,
    CoachChatResponse
)

router = APIRouter()


# Mock training tips database
TRAINING_TIPS = {
    "sit": [
        "Great sit! Mark this moment with a treat to reinforce the behavior.",
        "Perfect timing for a sit command. Your dog is focused and ready.",
        "This is an excellent opportunity to practice duration - ask for a longer sit.",
        "Nice sit position! Consider adding a hand signal to strengthen the cue."
    ],
    "stand": [
        "Good stand position. This is a great time to practice stay.",
        "Your dog is standing calmly - perfect moment for a position transition.",
        "Standing alert! Consider rewarding this calm, attentive behavior.",
        "This stand could transition into a nice heel position."
    ],
    "lie": [
        "Excellent down position! This shows relaxation and trust.",
        "Perfect lie down. Consider extending the duration before releasing.",
        "Great calm behavior. This is ideal for practicing settle commands.",
        "Nice relaxed position - reward this calm state."
    ],
    "approach": [
        "Your dog is approaching! Get ready to reward engagement.",
        "Good approach behavior. This is perfect for recall practice.",
        "Dog is moving toward you - excellent opportunity for 'come' reinforcement.",
        "Active approach! Consider calling them to strengthen recall."
    ],
    "fetch-return": [
        "Fantastic fetch return! Reward immediately to reinforce the complete sequence.",
        "Perfect fetch behavior! This is the moment to celebrate success.",
        "Great return! Consider adding a 'drop it' cue before the reward.",
        "Excellent fetch completion. Mark this win in your training log!"
    ],
    "playing": [
        "Play behavior detected! This is great for building drive and engagement.",
        "Your dog is in play mode - perfect for fun training sessions.",
        "Active play! Consider incorporating training cues during play.",
        "High energy play - great time for impulse control exercises."
    ],
    "drinking": [
        "Hydration break! Good time to pause training and let them rest.",
        "Your dog is drinking - ensure fresh water is always available.",
        "Water break detected. Consider this a natural pause in training."
    ],
    "eating": [
        "Eating detected. This is a good time to practice patience and wait commands.",
        "Meal time! Consider using this for 'wait' or 'leave it' training.",
        "Your dog is eating - perfect opportunity for food bowl manners."
    ],
    "default": [
        "Stay observant! Look for opportunities to reward good behavior.",
        "Your dog is active. Watch for training moments to reinforce.",
        "Keep sessions short and positive for best results.",
        "Remember to reward small wins throughout the day."
    ]
}


# Mock session summary templates
SUMMARY_TEMPLATES = {
    "high_success": {
        "summary": "Outstanding training session! Your dog showed excellent focus and responsiveness.",
        "wins": [
            "Consistent sit responses with {sit_count} successful sits",
            "Great fetch performance with {fetch_success_rate}% success rate",
            "Maintained calm behavior for {calm_minutes} minutes",
            "Strong engagement throughout the session"
        ],
        "setbacks": [
            "Slight distraction during mid-session",
            "Could improve duration on stay commands"
        ],
        "suggestions": [
            "Continue with current training routine - it's working well",
            "Consider adding more challenging distractions",
            "Practice in different environments to generalize behaviors",
            "Increase duration requirements gradually"
        ]
    },
    "moderate_success": {
        "summary": "Good training session with solid progress and some areas for improvement.",
        "wins": [
            "Completed {sit_count} sits with good form",
            "Showed improvement in fetch returns",
            "Maintained focus for most of the session"
        ],
        "setbacks": [
            "Some inconsistency in responses",
            "Distracted by environmental factors",
            "Fetch success rate could be higher at {fetch_success_rate}%"
        ],
        "suggestions": [
            "Work on reducing distractions in training environment",
            "Break sessions into shorter, more focused intervals",
            "Increase reward rate for correct responses",
            "Practice basic commands in low-distraction settings first"
        ]
    },
    "needs_improvement": {
        "summary": "Training session completed. Let's focus on building consistency.",
        "wins": [
            "Your dog stayed engaged for {time_in_frame} minutes",
            "Showed interest in training activities",
            "Completed some successful responses"
        ],
        "setbacks": [
            "Lower success rate on fetch attempts",
            "Difficulty maintaining focus",
            "Frequent off-frame time suggests distraction"
        ],
        "suggestions": [
            "Reduce session length to maintain engagement",
            "Use higher-value rewards to increase motivation",
            "Simplify commands and build from basics",
            "Ensure training environment is calm and distraction-free",
            "Consider training at different times of day"
        ]
    }
}


# Mock Q&A database
QA_DATABASE = {
    "sit": {
        "keywords": ["sit", "sitting", "sits"],
        "answers": [
            "Your dog performed {count} sits during this session. The best sits occurred around {timestamps}. Focus on rewarding the moment they achieve the position.",
            "Sit training is progressing well with {count} successful attempts. Check timestamps {timestamps} for examples of excellent form.",
            "I noticed {count} sit behaviors. The quality was best at {timestamps}. Consider using these moments as training examples."
        ]
    },
    "fetch": {
        "keywords": ["fetch", "ball", "retrieve", "return"],
        "answers": [
            "Your dog attempted {attempts} fetches with {successes} successful returns. Review timestamps {timestamps} to see what worked well.",
            "Fetch performance shows {success_rate}% success rate. The best returns happened at {timestamps}.",
            "I tracked {attempts} fetch attempts. Focus on the successful returns at {timestamps} to understand what motivates completion."
        ]
    },
    "bark": {
        "keywords": ["bark", "barking", "noise", "vocal"],
        "answers": [
            "I detected {count} barks during this session at {timestamps}. Consider what triggered these vocalizations.",
            "Barking occurred {count} times. Check {timestamps} to identify patterns or triggers.",
            "Your dog barked {count} times. The timestamps {timestamps} might reveal environmental triggers."
        ]
    },
    "progress": {
        "keywords": ["progress", "improvement", "better", "learning"],
        "answers": [
            "Your dog is showing steady progress! Sit responses are consistent, and fetch success rate is improving. Keep up the current routine.",
            "Progress is evident in the increased calm minutes and better focus. Continue with short, positive sessions.",
            "Training metrics show improvement over recent sessions. Your consistency is paying off!"
        ]
    },
    "default": {
        "keywords": [],
        "answers": [
            "Based on today's session, your dog showed good engagement. Focus on the moments around {timestamps} for quality training examples.",
            "I analyzed the session data. The most productive training moments were at {timestamps}.",
            "Your dog's behavior patterns suggest they're most receptive during the times marked at {timestamps}."
        ]
    }
}


def select_tip_for_action(action: str) -> str:
    """Select a random tip for the given action"""
    tips = TRAINING_TIPS.get(action, TRAINING_TIPS["default"])
    return random.choice(tips)


def calculate_session_quality(metrics: Dict) -> str:
    """Determine session quality based on metrics"""
    sit_count = metrics.get("sitCount", 0)
    fetch_attempts = metrics.get("fetchAttempts", 0)
    fetch_successes = metrics.get("fetchSuccesses", 0)
    time_in_frame = metrics.get("timeInFrameMin", 0)
    
    # Calculate success indicators
    fetch_success_rate = (fetch_successes / fetch_attempts * 100) if fetch_attempts > 0 else 0
    
    # Determine quality tier
    if sit_count >= 10 and fetch_success_rate >= 70 and time_in_frame >= 15:
        return "high_success"
    elif sit_count >= 5 and fetch_success_rate >= 40 and time_in_frame >= 10:
        return "moderate_success"
    else:
        return "needs_improvement"


def generate_mock_timestamps(count: int = 3) -> List[float]:
    """Generate mock timestamps for reference"""
    # Generate timestamps spread across a typical session (30 minutes)
    timestamps = []
    for i in range(count):
        # Random timestamp in milliseconds (0-30 minutes)
        ts = random.uniform(0, 30 * 60 * 1000)
        timestamps.append(round(ts, 0))
    return sorted(timestamps)


def find_relevant_qa(question: str) -> Dict:
    """Find relevant Q&A based on question keywords"""
    question_lower = question.lower()
    
    for category, qa_data in QA_DATABASE.items():
        if any(keyword in question_lower for keyword in qa_data["keywords"]):
            return qa_data
    
    return QA_DATABASE["default"]


@router.post("/tips", response_model=CoachTipsResponse)
async def get_training_tips(request: CoachTipsRequest):
    """
    Get training tips based on current action
    
    Returns contextual coaching advice for the detected action
    """
    try:
        tip = select_tip_for_action(request.currentAction)
        confidence = random.uniform(0.75, 0.95)
        
        return CoachTipsResponse(
            tip=tip,
            confidence=round(confidence, 3)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating tip: {str(e)}"
        )


@router.post("/summary", response_model=CoachSummaryResponse)
async def get_session_summary(request: CoachSummaryRequest):
    """
    Generate session summary with wins, setbacks, and suggestions
    
    Analyzes session metrics and events to provide comprehensive feedback
    """
    try:
        # Convert metrics to dict for easier access
        metrics_dict = request.metrics.model_dump()
        
        # Determine session quality
        quality = calculate_session_quality(metrics_dict)
        template = SUMMARY_TEMPLATES[quality]
        
        # Calculate derived metrics
        fetch_attempts = metrics_dict.get("fetchAttempts", 0)
        fetch_successes = metrics_dict.get("fetchSuccesses", 0)
        fetch_success_rate = round(
            (fetch_successes / fetch_attempts * 100) if fetch_attempts > 0 else 0,
            1
        )
        
        # Format wins with actual metrics
        wins = [
            win.format(
                sit_count=metrics_dict.get("sitCount", 0),
                fetch_success_rate=fetch_success_rate,
                calm_minutes=metrics_dict.get("timeInFrameMin", 0),
                time_in_frame=metrics_dict.get("timeInFrameMin", 0)
            )
            for win in template["wins"]
        ]
        
        # Format setbacks with actual metrics
        setbacks = [
            setback.format(fetch_success_rate=fetch_success_rate)
            if "{fetch_success_rate}" in setback else setback
            for setback in template["setbacks"]
        ]
        
        # Generate mock highlight clip IDs
        num_highlights = random.randint(2, 4)
        highlight_clips = [f"clip_{i}_{random.randint(1000, 9999)}" for i in range(num_highlights)]
        
        return CoachSummaryResponse(
            summary=template["summary"],
            wins=wins[:3],  # Limit to top 3
            setbacks=setbacks[:2],  # Limit to top 2
            suggestions=template["suggestions"][:3],  # Limit to top 3
            highlightClips=highlight_clips
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )


@router.post("/chat", response_model=CoachChatResponse)
async def chat_with_coach(request: CoachChatRequest):
    """
    Answer questions about training with timestamp references
    
    Provides natural language responses with relevant video timestamps
    """
    try:
        # Find relevant Q&A category
        qa_data = find_relevant_qa(request.question)
        
        # Select a random answer template
        answer_template = random.choice(qa_data["answers"])
        
        # Generate mock metrics for answer formatting
        context = request.context
        events = context.get("events", [])
        metrics = context.get("metrics", {})
        
        # Generate mock values
        count = random.randint(3, 12)
        attempts = random.randint(5, 15)
        successes = random.randint(3, attempts)
        success_rate = round((successes / attempts * 100) if attempts > 0 else 0, 1)
        
        # Generate relevant timestamps
        timestamps = generate_mock_timestamps(count=3)
        timestamp_str = ", ".join([f"{int(ts/1000/60)}:{int((ts/1000)%60):02d}" for ts in timestamps])
        
        # Format answer
        answer = answer_template.format(
            count=count,
            attempts=attempts,
            successes=successes,
            success_rate=success_rate,
            timestamps=timestamp_str
        )
        
        return CoachChatResponse(
            answer=answer,
            relevantTimestamps=timestamps
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}"
        )


@router.get("/health")
async def coach_health():
    """Health check for coach service"""
    return {
        "status": "healthy",
        "tips_available": sum(len(tips) for tips in TRAINING_TIPS.values()),
        "qa_categories": len(QA_DATABASE)
    }
