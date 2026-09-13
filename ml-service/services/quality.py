import re

class QualityScorer:
    def __init__(self):
        # 0-20 points per category
        self.max_score = 100
        
    def analyze(self, message: str, additions: int = 0, deletions: int = 0) -> dict:
        if not message.strip():
            return self._empty_result()
            
        words = message.split()
        
        clarity_score = self._eval_clarity(words)
        specificity_score = self._eval_specificity(message)
        actionability_score = self._eval_actionability(words)
        context_score = self._eval_context(message)
        consistency_score = self._eval_consistency(message, additions, deletions)
        
        total_score = clarity_score + specificity_score + actionability_score + context_score + consistency_score
        
        issues = self._generate_issues(
            clarity_score, specificity_score, actionability_score, context_score, consistency_score
        )
        
        if total_score >= 80:
            level = "EXCELLENT"
        elif total_score >= 60:
            level = "GOOD"
        elif total_score >= 40:
            level = "MODERATE"
        else:
            level = "POOR"
            
        return {
            "score": total_score,
            "level": level,
            "breakdown": {
                "clarity": clarity_score,
                "specificity": specificity_score,
                "actionability": actionability_score,
                "context": context_score,
                "consistency": consistency_score
            },
            "issues": issues
        }
        
    def _eval_clarity(self, words: list) -> int:
        if len(words) < 2: return 0
        if len(words) > 50: return 10 # Too long, loses clarity
        
        vague_words = {'stuff', 'things', 'misc', 'changes', 'update', 'fix'}
        vague_count = sum(1 for w in words if w.lower() in vague_words)
        
        if vague_count >= 2: return 5
        if vague_count == 1 and len(words) <= 3: return 8
        
        return 20
        
    def _eval_specificity(self, message: str) -> int:
        # Check if mentions specific files, components or ticket numbers
        has_ticket = bool(re.search(r'#\d+|[A-Z]+-\d+', message))
        has_component = ':' in message[:20] or '(' in message[:20]
        has_file = '.' in message
        
        score = 10
        if has_ticket: score += 5
        if has_component: score += 5
        if has_file: score += 5
        
        return min(20, score)
        
    def _eval_actionability(self, words: list) -> int:
        if not words: return 0
        
        imperative_verbs = {
            'add', 'fix', 'update', 'remove', 'refactor', 'implement',
            'change', 'create', 'delete', 'resolve', 'improve', 'optimize'
        }
        
        first_word = words[0].lower()
        if first_word in imperative_verbs:
            return 20
        elif first_word.endswith('ed') or first_word.endswith('ing'):
            return 10 # Past/continuous tense instead of imperative
            
        return 5
        
    def _eval_context(self, message: str) -> int:
        lines = message.split('\n')
        # Has body?
        if len(lines) > 2 and lines[1].strip() == '':
            return 20
            
        # Is the single line descriptive enough?
        if len(message.split()) >= 7:
            return 15
            
        return 5
        
    def _eval_consistency(self, message: str, additions: int, deletions: int) -> int:
        total_changes = additions + deletions
        words = len(message.split())
        
        if total_changes == 0:
            return 20
            
        # Large changes should have longer messages
        if total_changes > 1000 and words < 5:
            return 5
            
        return 20
        
    def _generate_issues(self, clarity, specificity, actionability, context, consistency) -> list:
        issues = []
        if clarity < 10:
            issues.append("Message uses vague terminology (e.g., 'stuff', 'changes')")
        if specificity < 10:
            issues.append("Message doesn't specify which component or file is affected")
        if actionability < 20:
            issues.append("Message should start with an imperative verb (e.g., 'Add', 'Fix')")
        if context < 10:
            issues.append("Message lacks context or why the change was made")
        if consistency < 10:
            issues.append("Message length is disproportionately short for a large code change")
        return issues
        
    def _empty_result(self):
        return {
            "score": 0, "level": "POOR",
            "breakdown": {"clarity": 0, "specificity": 0, "actionability": 0, "context": 0, "consistency": 0},
            "issues": ["Commit message is empty"]
        }

quality_service = QualityScorer()
