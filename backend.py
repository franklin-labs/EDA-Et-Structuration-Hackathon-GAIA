
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI(
    title="AgriTransition API",
    description="API pour l'accompagnement à la transition écologique agricole",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---

class FarmInput(BaseModel):
    # Structural Data
    region: str = Field(..., description="Région de l'exploitation")
    otex: str = Field(..., description="Orientation Technico-Économique (ex: Bovins Lait)")
    sau: float = Field(..., gt=0, description="Surface Agricole Utile (ha)")
    ugb: float = Field(..., ge=0, description="Unités Gros Bétail (Total)")
    
    # Key Indicators (Optional for initial profiling, but needed for precise transition)
    chargement: Optional[float] = Field(None, description="Chargement (UGB/ha SFP)")
    part_maïs: Optional[float] = Field(0, description="Part de maïs dans la SFP (%)")
    autonomie_fourragère: Optional[float] = Field(None, description="Autonomie fourragère (%)")
    
    # Environmental Inputs
    conso_fioul: Optional[float] = Field(None, description="Consommation fioul (L/an)")
    conso_elec: Optional[float] = Field(None, description="Consommation électricité (kWh/an)")
    
    # Economic Inputs
    ebe: Optional[float] = Field(None, description="Excédent Brut d'Exploitation (€)")

class Recommendation(BaseModel):
    category: str  # "Environment", "Economic", "Social"
    title: str
    description: str
    impact_score: int = Field(..., ge=1, le=5, description="Impact potentiel (1-5)")
    cost_score: int = Field(..., ge=1, le=5, description="Coût de mise en œuvre (1-5)")

class PredictionResult(BaseModel):
    current_ktype: str
    target_ktype: str
    transition_score: float = Field(..., ge=0, le=100, description="Score de viabilité de la transition")
    carbon_footprint_current: float = Field(..., description="Empreinte carbone actuelle estimée (tCO2e/an)")
    carbon_footprint_target: float = Field(..., description="Empreinte carbone cible estimée (tCO2e/an)")
    recommendations: List[Recommendation]

# --- Mock Logic (Placeholder for ML Model) ---

def determine_ktype(input: FarmInput) -> str:
    """Heuristic to determine current K-Type based on input."""
    if "Lait" in input.otex:
        if input.chargement and input.chargement < 1.4:
            return "Laitier Herbager Extensif"
        elif input.part_maïs > 30:
            return "Laitier Intensif Plaine (Maïs)"
        else:
            return "Laitier Polyculture"
    elif "Céréales" in input.otex or "Grandes Cultures" in input.otex:
        return "Céréalier Intensif"
    else:
        return "Polyculture-Élevage Standard"

def generate_recommendations(input: FarmInput, current_ktype: str) -> List[Recommendation]:
    recs = []
    
    # Logic based on "Gap Analysis"
    if input.autonomie_fourragère and input.autonomie_fourragère < 70:
        recs.append(Recommendation(
            category="Environment",
            title="Améliorer l'autonomie protéique",
            description="Introduire des légumineuses (luzerne, trèfle) dans la rotation pour réduire les achats de tourteaux de soja importé.",
            impact_score=5,
            cost_score=3
        ))
    
    if input.part_maïs > 30:
        recs.append(Recommendation(
            category="Environment",
            title="Réduire la part de maïs ensilage",
            description="Substituer une partie du maïs par de l'herbe pâturée ou fauchée pour réduire les intrants (azote, phyto) et améliorer le bilan carbone.",
            impact_score=4,
            cost_score=2
        ))
        
    if input.chargement and input.chargement > 1.8:
        recs.append(Recommendation(
            category="Economic",
            title="Optimiser le chargement",
            description="Votre chargement est élevé. Une légère réduction du cheptel pourrait paradoxalement améliorer la marge par UGB en réduisant les coûts alimentaires.",
            impact_score=4,
            cost_score=1
        ))

    # Generic recommendations if few inputs
    if not recs:
        recs.append(Recommendation(
            category="Social",
            title="Diagnostic Carbone Simplifié",
            description="Réaliser un diagnostic CAP'2ER niveau 1 pour situer précisément vos émissions.",
            impact_score=3,
            cost_score=1
        ))
        
    return recs

# --- Endpoints ---

@app.post("/predict", response_model=PredictionResult)
async def predict_transition(input: FarmInput):
    """
    Endpoint principal : Analyse la ferme et propose un scénario de transition.
    """
    current_ktype = determine_ktype(input)
    
    # Define a target K-Type (simplified logic)
    target_ktype = current_ktype + " (Optimisé)"
    if "Intensif" in current_ktype:
        target_ktype = current_ktype.replace("Intensif", "Durable")
    
    # Calculate dummy carbon footprint (heuristics)
    # Average ~10 tCO2e/ha for intensive, ~6 for extensive
    base_emission_factor = 8.0
    if "Herbager" in current_ktype: base_emission_factor = 5.5
    if "Céréalier" in current_ktype: base_emission_factor = 3.0
    
    current_carbon = input.sau * base_emission_factor
    target_carbon = current_carbon * 0.85 # Assume 15% reduction target
    
    recs = generate_recommendations(input, current_ktype)
    
    return PredictionResult(
        current_ktype=current_ktype,
        target_ktype=target_ktype,
        transition_score=random.randint(60, 90), # Mock score
        carbon_footprint_current=round(current_carbon, 1),
        carbon_footprint_target=round(target_carbon, 1),
        recommendations=recs
    )

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API AgriTransition. Utilisez /docs pour la documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
