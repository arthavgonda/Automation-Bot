
import re
from enum import Enum

class CommandType(Enum):
    SYSTEM = "system"
    WEB = "web"
    CONVERSATION = "conversation"

class CommandClassifier:
    def __init__(self):
        self.system_patterns = [
            r'\b(open|launch|start|run|execute)\s+\w+',
            r'\b(close|quit|exit|kill|stop)\s+\w+',
            r'\b(kholo|khol|chalu|shuru|band|bund)\s+\w+',
            r'\w+\s+ko\s+(open|close|kholo|band|karo)',
            r'\b(create|make|delete|remove|rename|copy|move)\s+(file|folder|directory)',
            r'\b(find|search|locate)\s+(?:file|folder|document)\s+(?:on|in)\s+(?:computer|system|pc|laptop|machine)',
            r'\b(search|find)\s+(?:for\s+)?(?:file|folder|document)',
            r'\b(file|folder|document)\s+(?:search|find|dhoondo)',
            r'\b(file|folder)\s+(banao|banana|delete|hatao|khojo|dhoondo)',
            r'\b(banao|banana|delete|hatao)\s+(file|folder)',
            r'\b(system me|computer me|pc me)\s+(search|khojo|dhoondo)',
            r'\b(mere|meri|my)\s+(computer|pc|system)\s+(me|par|mein)',
            r'\b(volume|brightness|wifi|bluetooth|screenshot|settings)',
            r'\b(minimize|maximize|fullscreen)',
            r'\b(volume|brightness)\s+(badha|kam|increase|decrease)',
            r'\b(screenshot|settings)\s+(le|karo)',
        ]
        self.web_patterns = [
            r'\b(what is|who is|what are|who are|what\'s|who\'s)\s+',
            r'\b(when (is|was|will)|where (is|was|will))\s+',
            r'\b(how to|how do|how does|how can)\s+',
            r'\b(google|search on internet|search online|web pe|internet pe)\s+',
            r'\b(search|find|look up)\s+(?!file|folder|document|on computer|on pc|in system)',
            r'\b(download|install)\s+(?!from)',
            r'\b(kya hai|kaun hai|kahan hai|kab hai)\s+',
            r'\b(kaise|kaise kare|kaise karte)\s+',
            r'\b(google karo|internet pe|web pe|online)\s+',
            r'\b(batao|bata|bataye)\s+(?:ki|ke|kya)',
            r'\b(search karo|dhundo)\s+(?!file|folder|system|computer)',
            r'\b(go to|open|visit|navigate to)\s+\w+\.(com|org|net|in|co)',
            r'\b(youtube|facebook|twitter|instagram|linkedin|github)\b',
            r'\b(buy|purchase|order|shopping)\s+',
            r'\b(price|cost|review|compare)\s+',
            r'\b(download|install)\s+(?:from|via)\s+',
        ]
        self.conversation_patterns = [
            # Greetings
            r'^(hello|hi|hey|good morning|good evening|good night)\b',
            r'\b(how are you|what\'s up|how\'s it going|how do you do)',
            r'\b(namaste|namaskar|kaise ho|kya hal|sab theek|kaise hain)',
            
            # Identity questions
            r'\b(what (is|are) you|who are you|tell me about yourself)',
            r'\b(tum kaun ho|aap kaun|batao apne bare|tell about yourself)',
            
            # Requests for help/entertainment
            r'\b(can you help|are you able to|do you know how)',
            r'\b(help me|assist me|guide me|support)',
            r'\b(madad karo|help karo|batao kaise|sikha)',
            r'\b(tell me (a|an|the))\s+(joke|story|fact|quote)',
            r'^(joke|story|fact|quote|advice)\b',
            r'^(ek|one)\s+(joke|story|kahani)',
            r'\b(sunao|batao)\s+(?!weather|price|kya hai)',
            
            # Thanks and acknowledgments (EXPANDED)
            r'\b(thank you|thanks|thank|thankyou|thx)',
            r'\b(thank you for|thanks for|thank for)',
            r'\b(dhanyavad|theek hai|accha|shukriya|theek)',
            
            # Confirmations and agreements
            r'^(okay|ok|fine|sure|got it|alright|right|yes|no|nope|yep|yeah)\b',
            r'\b(theek|sahi|haan|nahi|bilkul)',
            
            # Goodbyes and closings (NEW)
            r'\b(goodbye|good bye|bye|see you|farewell|take care|catch you later)',
            r'\b(bye bye|byebye|see ya|later|peace|adios)',
            r'\b(alvida|khuda hafiz|phir milenge)',
            
            # Watching/viewing related phrases (NEW)
            r'\b(thank(s)? for (watching|viewing|listening|your time))',
            r'\b(thanks for (being here|joining|coming))',
            r'^(watching|viewing|listening)$',
            
            # Apologies
            r'\b(sorry|apologies|apologize|excuse me|pardon)',
            r'\b(maaf|maafi|sorry)',
            
            # Exclamations and reactions
            r'^(wow|cool|nice|great|awesome|amazing|excellent|perfect)\b',
            r'^(wah|zabardast|badhiya|mast|shandar)\b',
        ]
    def classify(self, text):
        text = text.lower().strip()
        system_score = self._score_patterns(text, self.system_patterns)
        web_score = self._score_patterns(text, self.web_patterns)
        conversation_score = self._score_patterns(text, self.conversation_patterns)
        system_score += self._contextual_system_score(text)
        web_score += self._contextual_web_score(text)
        conversation_score += self._contextual_conversation_score(text)
        scores = {
            CommandType.SYSTEM: system_score,
            CommandType.WEB: web_score,
            CommandType.CONVERSATION: conversation_score
        }
        max_score = max(scores.values())
        
        # Prefer conversation when uncertain (max_score < 1.0)
        if max_score < 1.0:
            return CommandType.CONVERSATION, 0.5, "Ambiguous input, defaulting to conversation"
        
        command_type = max(scores, key=scores.get)
        confidence = min(max_score / 5.0, 1.0)
        reasoning = self._get_reasoning(text, command_type, scores)
        return command_type, confidence, reasoning
    def _score_patterns(self, text, patterns):
        score = 0
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 1
        return score
    def _contextual_system_score(self, text):
        score = 0
        if text.strip().lower().startswith(('search ', 'google ', 'find ', 'lookup ', 'look up ')):
            return -10
        if text.strip().lower().startswith(('open ', 'launch ', 'start ', 'run ', 'execute ', 'close ', 'quit ')):
            score += 3
        apps = ['chrome', 'firefox', 'brave', 'edge', 'safari', 'notepad', 
                'calculator', 'terminal', 'cmd', 'settings', 'explorer',
                'finder', 'spotify', 'discord', 'steam', 'vlc', 'code', 'vscode',
                'visual', 'studio', 'tool', 'app', 'application']
        for app in apps:
            if app in text:
                score += 2
        system_keywords = ['file', 'folder', 'directory', 'volume', 'brightness',
                          'screenshot', 'taskbar', 'desktop', 'window']
        for keyword in system_keywords:
            if keyword in text:
                score += 1
        local_indicators = ['on computer', 'in computer', 'on pc', 'in pc', 
                           'on system', 'in system', 'from system', 'on my computer', 'on this computer',
                           'my pc', 'this pc', 'on laptop', 'in laptop',
                           'computer me', 'pc me', 'system me', 'system se', 'mere computer',
                           'meri pc', 'is computer']
        for indicator in local_indicators:
            if indicator in text:
                score += 10
        return score
    def _contextual_web_score(self, text):
        score = 0
        
        # Explicit search commands get high score
        if text.strip().lower().startswith(('search ', 'google ', 'find ', 'lookup ', 'look up ')):
            score += 10
        if re.search(r'\b(search|find|lookup|google)\s+(for|about|on)\s+', text):
            score += 8
        
        # Question words indicate information seeking
        question_words = ['what', 'who', 'when', 'where', 'why', 'how',
                         'kya', 'kaun', 'kab', 'kahan', 'kaise', 'kyun']
        has_question_word = False
        for word in question_words:
            if word in text.split():
                score += 1.5
                has_question_word = True
        
        # Informational keywords
        info_words = ['information', 'details', 'about', 'regarding',
                     'jankari', 'bare mein', 'ke bare']
        for word in info_words:
            if word in text:
                score += 1
        
        # URLs are clearly web-related
        if re.search(r'\.(com|org|net|in|co)', text):
            score += 3
        
        # Explicit web indicators
        web_indicators = ['google', 'search on internet', 'search online', 
                         'internet pe', 'web pe', 'online search',
                         'google karo', 'internet par']
        for indicator in web_indicators:
            if indicator in text:
                score += 5
        
        # Penalize very short phrases without question words (likely conversation)
        if len(text.split()) <= 2 and not has_question_word:
            score -= 5
        
        # Conversational phrases should not be searches
        conversation_indicators = ['thank', 'thanks', 'bye', 'hello', 'hi', 'sorry', 
                                  'ok', 'okay', 'watching', 'listening']
        for indicator in conversation_indicators:
            if indicator in text:
                score -= 8
        
        # Local computer context negates web search
        local_context = ['on computer', 'in computer', 'computer me', 'pc me', 
                        'system me', 'from system', 'system se', 'on my pc', 'my computer']
        for context in local_context:
            if context in text:
                score -= 10
        
        return score
    def _contextual_conversation_score(self, text):
        score = 0
        
        # Boost short phrases (likely conversational)
        if len(text.split()) <= 3:
            score += 2
        
        # Strong conversation indicators - common phrases
        strong_indicators = [
            'thank you', 'thanks', 'thank', 'thankyou', 'thx',
            'bye', 'goodbye', 'see you', 'take care',
            'hello', 'hi', 'hey',
            'sorry', 'apologies',
            'ok', 'okay', 'alright', 'sure', 'got it',
            'wow', 'cool', 'nice', 'great',
        ]
        for indicator in strong_indicators:
            if indicator in text:
                score += 5
        
        # "watching", "listening" without question words = conversation
        if any(word in text for word in ['watching', 'listening', 'viewing']):
            if not any(qword in text for qword in ['what', 'who', 'when', 'where', 'why', 'how']):
                score += 5
        
        # Pronouns addressing the assistant
        pronouns = ['you', 'your', 'yourself', 'tum', 'tumhara', 'aap', 'aapka']
        for pronoun in pronouns:
            if pronoun in text.split():
                score += 2
        
        # Polite words boost
        polite_words = ['please', 'kindly', 'kripa', 'meherbani']
        for word in polite_words:
            if word in text:
                score += 1
        
        # If text ends with punctuation like "!" or ".", likely conversational
        if text.endswith(('!', '.')):
            score += 1
        
        return score
    def _get_reasoning(self, text, command_type, scores):
        if command_type == CommandType.SYSTEM:
            return f"System command detected (score: {scores[CommandType.SYSTEM]:.1f})"
        elif command_type == CommandType.WEB:
            return f"Web search query detected (score: {scores[CommandType.WEB]:.1f})"
        else:
            return f"Conversational request detected (score: {scores[CommandType.CONVERSATION]:.1f})"


def test_classifier():
    classifier = CommandClassifier()
    test_cases = [
        # System commands
        "open chrome",
        "close firefox",
        "create a new file",
        "search for document on computer",
        "chrome ko open karo",
        "file banao",
        "folder delete karo",
        
        # Web searches
        "what is artificial intelligence",
        "how to make pizza",
        "search for python tutorials",
        "who is the president",
        "kya hai machine learning",
        "batao weather kya hai",
        "search karo best laptop",
        
        # Conversations - Basic
        "hello how are you",
        "tell me a joke",
        "thank you",
        "kaise ho",
        "ek kahani sunao",
        "dhanyavad",
        
        # Conversations - User reported issues (should be CONVERSATION)
        "thank you for watching",
        "thanks for watching",
        "you",
        "bye",
        "goodbye",
        "see you later",
        "watching",
        "thanks",
        "ok",
        "okay",
        "cool",
        "nice",
    ]
    print("="*70)
    print("COMMAND CLASSIFIER TEST")
    print("="*70)
    for text in test_cases:
        cmd_type, confidence, reasoning = classifier.classify(text)
        print(f"\n📝 Input: {text}")
        print(f"   Type: {cmd_type.value.upper()}")
        print(f"   Confidence: {confidence*100:.0f}%")
        print(f"   Reasoning: {reasoning}")

if __name__ == "__main__":
    test_classifier()