import os
import json
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(__file__), "db.json")

class Competitor(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    website: str
    pricing_url: str
    baseline_features: str  # A detailed description of baseline features
    baseline_pricing: str   # Description of pricing tiers (e.g., Free, Pro $29/mo, Enterprise)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class AnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    competitor_id: str
    competitor_name: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    raw_scraped_data: str
    feature_deltas: str
    pricing_analysis: str
    swot_analysis: str
    executive_brief: str
    threat_score: int = 5  # 1-10 threat assessment score

DEFAULT_COMPETITORS = [
    {
        "id": "acme-123",
        "name": "Acme SaaS",
        "website": "https://www.acmesaas-demo.com",
        "pricing_url": "https://www.acmesaas-demo.com/pricing",
        "baseline_features": "- Simple contact form management\n- Standard email notifications\n- Weekly CSV exports\n- Single user account dashboard",
        "baseline_pricing": "Free Tier: $0/mo (up to 100 entries)\nPro Tier: $49/mo (up to 5,000 entries, basic support)\nEnterprise Tier: Custom (unlimited entries, API access)",
    },
    {
        "id": "chatify-456",
        "name": "Chatify AI",
        "website": "https://www.chatifyai-demo.com",
        "pricing_url": "https://www.chatifyai-demo.com/pricing",
        "baseline_features": "- Multi-channel widget (Web, WhatsApp)\n- Up to 1,000 active monthly chats\n- Automated canned responses\n- Standard reporting dashboard",
        "baseline_pricing": "Starter Tier: $19/mo (1 seat, web widget only)\nGrowth Tier: $79/mo (5 seats, WhatsApp add-on for +$20)\nScale Tier: $299/mo (unlimited chats, basic analytics)",
    }
]

def load_db() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE):
        initial_db = {
            "competitors": DEFAULT_COMPETITORS,
            "analyses": []
        }
        save_db(initial_db)
        return initial_db
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"competitors": DEFAULT_COMPETITORS, "analyses": []}

def save_db(data: Dict[str, Any]) -> None:
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_competitors() -> List[Competitor]:
    db = load_db()
    return [Competitor(**c) for c in db.get("competitors", [])]

def get_competitor(comp_id: str) -> Optional[Competitor]:
    comps = get_competitors()
    for c in comps:
        if c.id == comp_id:
            return c
    return None

def add_competitor(comp: Competitor) -> Competitor:
    db = load_db()
    db["competitors"].append(comp.model_dump())
    save_db(db)
    return comp

def update_competitor(comp_id: str, updated_data: Dict[str, Any]) -> Optional[Competitor]:
    db = load_db()
    for i, c in enumerate(db["competitors"]):
        if c["id"] == comp_id:
            for key, val in updated_data.items():
                if key != "id":
                    c[key] = val
            save_db(db)
            return Competitor(**c)
    return None

def delete_competitor(comp_id: str) -> bool:
    db = load_db()
    original_len = len(db["competitors"])
    db["competitors"] = [c for c in db["competitors"] if c["id"] != comp_id]
    db["analyses"] = [a for a in db["analyses"] if a["competitor_id"] != comp_id]
    save_db(db)
    return len(db["competitors"]) < original_len

def get_analyses(competitor_id: Optional[str] = None) -> List[AnalysisResult]:
    db = load_db()
    results = [AnalysisResult(**a) for a in db.get("analyses", [])]
    if competitor_id:
        results = [r for r in results if r.competitor_id == competitor_id]
    # Sort by timestamp descending
    results.sort(key=lambda x: x.timestamp, reverse=True)
    return results

def add_analysis(analysis: AnalysisResult) -> AnalysisResult:
    db = load_db()
    db["analyses"].append(analysis.model_dump())
    save_db(db)
    return analysis
