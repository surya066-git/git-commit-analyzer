import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.classifier import classifier_service
from services.quality import quality_service
from services.recommender import recommender_service

app = FastAPI(title="CommitIQ ML Service", description="API for analyzing git commits and generating recommendations.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    commitMessage: str
    changedFiles: Optional[List[str]] = []
    additions: Optional[int] = 0
    deletions: Optional[int] = 0

class ConsistencyResult(BaseModel):
    status: str
    reason: str

class QualityBreakdown(BaseModel):
    clarity: int
    specificity: int
    actionability: int
    context: int
    consistency: int

class AnalysisResponse(BaseModel):
    category: str
    confidence: float
    qualityScore: int
    qualityLevel: str
    qualityBreakdown: QualityBreakdown
    issues: List[str]
    suggestion: str
    consistency: ConsistencyResult

def check_consistency(category: str, changed_files: List[str]) -> ConsistencyResult:
    if not changed_files:
        return ConsistencyResult(status="UNKNOWN", reason="No changed files provided for consistency check.")
        
    exts = [f.split('.')[-1].lower() for f in changed_files if '.' in f]
    dirs = [f.split('/')[0].lower() for f in changed_files if '/' in f]
    
    if category == "DOCUMENTATION" and any(ext in ['js', 'ts', 'py', 'java', 'go'] for ext in exts):
        return ConsistencyResult(
            status="POTENTIAL_MISMATCH", 
            reason="The commit message appears documentation-oriented while the changed files primarily belong to application source code."
        )
        
    if category == "TESTING" and not any('test' in d for d in dirs) and not any('test' in e or 'spec' in e for e in changed_files):
        return ConsistencyResult(
            status="POTENTIAL_MISMATCH",
            reason="The commit is categorized as testing, but no test files appear to be modified."
        )
        
    return ConsistencyResult(status="CONSISTENT", reason="Commit message aligns with changed files.")

@app.get("/api/health")
def read_health():
    return {"status": "ok"}

@app.post("/api/analyze", response_model=AnalysisResponse)
def analyze_commit(request: AnalysisRequest):
    # 1. Classification
    category, confidence = classifier_service.predict(request.commitMessage)
    
    # 2. Quality Scoring
    quality_result = quality_service.analyze(request.commitMessage, request.additions, request.deletions)
    
    # 3. Consistency Checking
    consistency = check_consistency(category, request.changedFiles)
    
    # 4. Recommendation
    suggestion = recommender_service.suggest(request.commitMessage, category, quality_result["issues"], request.changedFiles)
    
    return AnalysisResponse(
        category=category,
        confidence=confidence,
        qualityScore=quality_result["score"],
        qualityLevel=quality_result["level"],
        qualityBreakdown=QualityBreakdown(**quality_result["breakdown"]),
        issues=quality_result["issues"],
        suggestion=suggestion,
        consistency=consistency
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
