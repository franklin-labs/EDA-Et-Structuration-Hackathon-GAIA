
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from fastapi.middleware.cors import CORSMiddleware
import random
from datetime import datetime

app = FastAPI(
    title="AgriTransition API",
    description="API pour l'accompagnement à la transition écologique agricole (Outil Conseiller)",
    version="1.2.0"
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
    filiere: str = Field(..., description="Filière de production (ex: Bovins Lait)")
    sau: float = Field(..., gt=0, description="Surface Agricole Utile (ha)")
    ugb: float = Field(..., ge=0, description="Unités Gros Bétail (Total)")
    
    # Key Indicators for Simulation
    chargement: Optional[float] = Field(None, description="Chargement (UGB/ha SFP)")
    part_maïs: Optional[float] = Field(0, description="Part de maïs dans la SFP (%)")
    part_herbe: float = Field(..., ge=0, le=100, description="Pourcentage d'herbe dans la SFP")
    
    # Environmental Inputs
    conso_fioul: Optional[float] = Field(None, description="Consommation fioul (L/an)")
    conso_elec: Optional[float] = Field(None, description="Consommation électricité (kWh/an)")
    
    # Economic Inputs
    ebe: Optional[float] = Field(None, description="Excédent Brut d'Exploitation (€)")

class SimulationResult(BaseModel):
    scenario_name: str
    autonomie_fourragere_estimee: float = Field(..., description="Autonomie fourragère calculée (%)")
    carbon_footprint: float = Field(..., description="Empreinte carbone estimée (tCO2e/an)")
    feed_cost_index: float = Field(..., description="Indice coût alimentaire (Base 100)")
    biodiversity_score: float = Field(..., description="Score biodiversité (0-10)")

class PredictionResult(BaseModel):
    current_ktype: str
    current_state: SimulationResult
    simulated_state: Optional[SimulationResult] = None
    delta_carbon: float = Field(..., description="Différence Carbone (Simulé - Actuel)")
    delta_autonomy: float = Field(..., description="Différence Autonomie (Simulé - Actuel)")
    recommendations: List[str]

class AdvisorStats(BaseModel):
    total_farmers: int
    visits_this_month: int
    avg_carbon_reduction_potential: float
    top_actions: List[str]

class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict] = None

class ChatResponse(BaseModel):
    response: str
    suggested_actions: Optional[List[str]] = None

# --- System Logic ---

def calculate_autonomy(input: FarmInput, part_herbe: float) -> float:
    """
    Calcule l'autonomie fourragère estimée basée sur le % d'herbe et le chargement.
    Plus d'herbe et moins de chargement = Meilleure autonomie.
    """
    base_autonomy = 50.0
    # Bonus pour l'herbe : +0.4 point d'autonomie par % d'herbe
    base_autonomy += part_herbe * 0.4
    
    # Malus pour le chargement élevé : -10 pts si chargement > 1.4
    chargement = input.chargement if input.chargement else (input.ugb / input.sau)
    if chargement > 1.4:
        base_autonomy -= (chargement - 1.4) * 20
        
    return max(0, min(100, base_autonomy))

def calculate_carbon(input: FarmInput, part_herbe: float) -> float:
    """
    Estime l'empreinte carbone globale.
    L'herbe stocke du carbone (-), le maïs consomme des intrants (+).
    """
    base_emission_factor = 8.0 # tCO2e/ha moyen
    
    # Impact de l'herbe : réduit l'empreinte nette (stockage C)
    # Hypothèse : 1ha d'herbe émet 30% moins qu'1ha de culture annuelle + stockage
    modifier = 1.0 - (part_herbe / 100.0 * 0.3)
    
    return input.sau * base_emission_factor * modifier

def calculate_biodiversity(part_herbe: float) -> float:
    # Simple linear relation for mock
    return 2.0 + (part_herbe / 100.0 * 8.0)

def simulate_system(input: FarmInput, override_part_herbe: float = None) -> SimulationResult:
    part_herbe = override_part_herbe if override_part_herbe is not None else input.part_herbe
    
    autonomy = calculate_autonomy(input, part_herbe)
    carbon = calculate_carbon(input, part_herbe)
    biodiversity = calculate_biodiversity(part_herbe)
    
    # Cost index: High autonomy reduces cost
    cost_index = 100 - (autonomy - 50) # If autonomy 70, cost is 80 (lower)
    
    return SimulationResult(
        scenario_name="Simulé" if override_part_herbe is not None else "Actuel",
        autonomie_fourragere_estimee=round(autonomy, 1),
        carbon_footprint=round(carbon, 1),
        feed_cost_index=round(cost_index, 1),
        biodiversity_score=round(biodiversity, 1)
    )

def determine_ktype(input: FarmInput) -> str:
    """Heuristic to determine current K-Type based on input."""
    if "Lait" in input.filiere:
        if input.part_herbe > 70:
            return "Laitier Herbager"
        elif input.part_maïs > 30:
            return "Laitier Intensif Plaine"
        else:
            return "Laitier Polyculture"
    elif "Céréales" in input.filiere or "Grandes Cultures" in input.filiere:
        return "Céréalier Intensif"
    else:
        return "Polyculture-Élevage Standard"

# --- Endpoints ---

@app.post("/simulate", response_model=PredictionResult)
async def simulate_transition(input: FarmInput, target_part_herbe: Optional[float] = None):
    """
    Simule l'impact d'un changement de variable (ex: % Herbe) sur le système global.
    """
    current_state = simulate_system(input)
    current_ktype = determine_ktype(input)
    
    simulated_state = None
    delta_carbon = 0.0
    delta_autonomy = 0.0
    recs = []

    if target_part_herbe is not None:
        simulated_state = simulate_system(input, target_part_herbe)
        delta_carbon = simulated_state.carbon_footprint - current_state.carbon_footprint
        delta_autonomy = simulated_state.autonomie_fourragere_estimee - current_state.autonomie_fourragere_estimee
        
        # Generate dynamic advice based on delta
        if delta_autonomy > 0:
            recs.append(f"Augmenter l'herbe de {input.part_herbe}% à {target_part_herbe}% améliore votre autonomie de {delta_autonomy:.1f} pts.")
        if delta_carbon < 0:
            recs.append(f"Cela permettrait de réduire vos émissions de {abs(delta_carbon):.1f} tCO2e/an (Stockage Carbone accru).")
        
        # Systemic warning
        if target_part_herbe > input.part_herbe + 20:
             recs.append("Attention : Une augmentation importante de la surface en herbe peut nécessiter une réduction du cheptel pour maintenir les performances individuelles.")

    return PredictionResult(
        current_ktype=current_ktype,
        current_state=current_state,
        simulated_state=simulated_state,
        delta_carbon=round(delta_carbon, 1),
        delta_autonomy=round(delta_autonomy, 1),
        recommendations=recs
    )

@app.get("/advisor/stats", response_model=AdvisorStats)
async def get_advisor_stats():
    """Retourne les statistiques globales pour le tableau de bord du conseiller."""
    return AdvisorStats(
        total_farmers=42,
        visits_this_month=8,
        avg_carbon_reduction_potential=12.5,
        top_actions=["Implantation Méteil", "Réduction Engrais Minéral", "Allongement Rotations"]
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_with_advisor_agent(chat_input: ChatMessage):
    """Chatbot intelligent pour assister le conseiller."""
    msg = chat_input.message.lower()
    
    # Simple rule-based logic to mimic LLM behavior
    if "bonjour" in msg:
        return ChatResponse(response="Bonjour ! Je suis votre assistant agricole. Comment puis-je vous aider aujourd'hui ?")
    
    if "aide" in msg or "subvention" in msg:
        return ChatResponse(
            response="Pour les aides à la transition, vous pouvez consulter les dispositifs PCAE (Plan de Compétitivité et d'Adaptation des Exploitations) de votre région. Pour la plantation de haies, regardez le 'Pacte en faveur de la haie'.",
            suggested_actions=["Voir dossier PCAE", "Simuler impact financier"]
        )
    
    if "carbone" in msg:
        return ChatResponse(
            response="Le levier carbone le plus efficace pour cette exploitation semble être l'augmentation de la surface en herbe (stockage C) et la réduction de la fertilisation minérale.",
            suggested_actions=["Simuler +20% Herbe", "Voir fiche Technique 'Stockage Carbone'"]
        )
        
    return ChatResponse(
        response="Je comprends votre demande. Pourriez-vous préciser si cela concerne l'aspect technique, économique ou réglementaire ?",
        suggested_actions=["Aspect Technique", "Aspect Économique"]
    )

@app.get("/")
async def root():
    return {"message": "API AgriTransition v1.2 (Outil Conseiller)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
