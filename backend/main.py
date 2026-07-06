import os
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from backend.db import (
    Competitor,
    AnalysisResult,
    get_competitors,
    get_competitor,
    add_competitor,
    update_competitor,
    delete_competitor,
    get_analyses,
    add_analysis,
)
from backend.scraper import scrape_competitor_data
from backend.crew import run_crewai_flow

app = FastAPI(title="Corporate Competitive Intelligence Bureau API", root_path=os.environ.get("ROOT_PATH", ""))

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompetitorCreate(BaseModel):
    name: str
    website: str
    pricing_url: str
    baseline_features: str
    baseline_pricing: str

class CompetitorUpdate(BaseModel):
    name: Optional[str] = None
    website: Optional[str] = None
    pricing_url: Optional[str] = None
    baseline_features: Optional[str] = None
    baseline_pricing: Optional[str] = None

class AnalysisRequest(BaseModel):
    competitor_id: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Competitive Intelligence Bureau API. Use /docs for documentation."}

@app.get("/api/competitors", response_model=List[Competitor])
def read_competitors():
    return get_competitors()

@app.get("/api/competitors/{comp_id}", response_model=Competitor)
def read_competitor(comp_id: str):
    comp = get_competitor(comp_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
    return comp

@app.post("/api/competitors", response_model=Competitor)
def create_competitor(payload: CompetitorCreate):
    comp = Competitor(
        name=payload.name,
        website=payload.website,
        pricing_url=payload.pricing_url,
        baseline_features=payload.baseline_features,
        baseline_pricing=payload.baseline_pricing,
    )
    return add_competitor(comp)

@app.put("/api/competitors/{comp_id}", response_model=Competitor)
def modify_competitor(comp_id: str, payload: CompetitorUpdate):
    updated = update_competitor(comp_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Competitor not found or update failed")
    return updated

@app.delete("/api/competitors/{comp_id}")
def remove_competitor(comp_id: str):
    deleted = delete_competitor(comp_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Competitor not found")
    return {"message": "Competitor deleted successfully"}

@app.get("/api/analyses", response_model=List[AnalysisResult])
def read_analyses(competitor_id: Optional[str] = None):
    return get_analyses(competitor_id)

@app.post("/api/analyses/run", response_model=AnalysisResult)
def trigger_analysis(payload: AnalysisRequest):
    comp = get_competitor(payload.competitor_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    try:
        # Step 1: Scrape Sentinel scrapes the data
        scraped_text = scrape_competitor_data(comp.name, comp.website, comp.pricing_url)
        
        # Step 2: Multi-agent crew performs analysis
        crew_outputs, threat_score = run_crewai_flow(
            competitor_name=comp.name,
            baseline_features=comp.baseline_features,
            baseline_pricing=comp.baseline_pricing,
            scraped_data=scraped_text
        )
        
        # Step 3: Save analysis result to database
        analysis_res = AnalysisResult(
            competitor_id=comp.id,
            competitor_name=comp.name,
            raw_scraped_data=crew_outputs["raw_scraped_data"],
            feature_deltas=crew_outputs["feature_deltas"],
            pricing_analysis=crew_outputs["pricing_analysis"],
            swot_analysis=crew_outputs["swot_analysis"],
            executive_brief=crew_outputs["executive_brief"],
            threat_score=threat_score
        )
        
        saved_result = add_analysis(analysis_res)
        return saved_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000)
