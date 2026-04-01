from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.pipeline_service import run_full_analysis

app = FastAPI(title="Fire Storm Tech-Debt Engine")

# Define the input structure
class RepoRequest(BaseModel):
    repo_url: str

@app.post("/analyze")
async def analyze_repository(request: RepoRequest):
    try:
        # Pass the URL to your service layer
        # This will return the Phase 2 JSON format you created earlier
        result = run_full_analysis(request.repo_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")