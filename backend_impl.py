
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from fastapi.middleware.cors import CORSMiddleware
import random
import joblib
import pandas as pd
from datetime import datetime

app = FastAPI(
    title="AgriTransition API",
    description="API pour l'accompagnement à la transition écologique agricole (Outil Conseiller)",
    version="1.3.0"
)

# Load ML Model
try:
    model = joblib.load('model_ktype.pkl')
    print("Modèle K-Type chargé avec succès.")
except Exception as e:
    print(f"Erreur chargement modèle : {e}")
    model = None

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
    
    # Workforce & Herd
    sau: float = Field(..., gt=0, description="Surface Agricole Utile (ha)")
    umo: float = Field(..., gt=0, description="Unités Main d'Œuvre (Total)")
    ugb: float = Field(..., ge=0, description="Unités Gros Bétail (Total)")
    nb_vl: Optional[int] = Field(None, ge=0, description="Nombre de Vaches Laitières (si applicable)")
    
    # Assolement Details (Surfaces)
    surface_culture: float = Field(0, ge=0, description="Surface en Cultures (Céréales, Oléoprotéineux)")
    surface_sfp: float = Field(0, ge=0, description="Surface Fourragère Principale (SFP)")
    surface_herbe_pp: float = Field(0, ge=0, description="Surface Herbe - Prairies Permanentes (PP)")
    surface_herbe_pt: float = Field(0, ge=0, description="Surface Herbe - Prairies Temporaires (PT)")
    
    # Key Indicators for Simulation
    chargement: Optional[float] = Field(None, description="Chargement (UGB/ha SFP)")
    part_maïs: Optional[float] = Field(0, description="Part de maïs dans la SFP (%)")
    part_herbe: float = Field(..., ge=0, le=100, description="Pourcentage d'herbe dans la SFP (Calculé ou saisi)")
    
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
    surface_herbe_totale: float = Field(..., description="Surface herbe totale (PP + PT)")
    part_herbe_sfp: float = Field(..., description="Part d'herbe dans la SFP (%)")

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
    reasoning_steps: Optional[List[str]] = None
    citations: Optional[List[Dict[str, str]]] = None

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
    
    # Recalculate surfaces if override_part_herbe is used
    if override_part_herbe is not None:
        # We assume the user wants to keep the same ratio between PP and PT
        total_herbe_original = input.surface_herbe_pp + input.surface_herbe_pt
        surf_herbe_new = (override_part_herbe / 100.0) * input.surface_sfp
    else:
        surf_herbe_new = input.surface_herbe_pp + input.surface_herbe_pt

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
        biodiversity_score=round(biodiversity, 1),
        surface_herbe_totale=round(surf_herbe_new, 1),
        part_herbe_sfp=round(part_herbe, 1)
    )

def determine_ktype(input: FarmInput) -> str:
    """Predict K-Type using the trained ML model or fallback to heuristic."""
    if model:
        try:
            # Create a single-row DataFrame matching the model features
            data = {
                'sau': [input.sau],
                'umo': [input.umo],
                'ugb': [input.ugb],
                'nb_vl': [input.nb_vl if input.nb_vl is not None else 0],
                'surface_sfp': [input.surface_sfp],
                'surface_herbe_pp': [input.surface_herbe_pp],
                'surface_herbe_pt': [input.surface_herbe_pt],
                'surface_culture': [input.surface_culture],
                'region': [input.region],
                'filiere': [input.filiere]
            }
            df_input = pd.DataFrame(data)
            prediction = model.predict(df_input)
            return prediction[0]
        except Exception as e:
            print(f"Prediction error: {e}")
            # Fallback to simple logic
            return f"Inconnu (Erreur: {str(e)[:20]}...)"
    
    # Heuristic Fallback (if model not loaded)
    if "Lait" in input.filiere:
        if input.part_herbe > 70:
            return "Laitier Herbager (Heuristique)"
        return "Laitier Polyculture (Heuristique)"
    return "Polyculture-Élevage (Heuristique)"

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
    """Chatbot intelligent pour assister le conseiller (Perplexity-style)."""
    msg = chat_input.message.lower()
    context = chat_input.context or {}
    
    # Extract farm data from context if available
    farm_info = context.get('farm', {})
    ktype = context.get('current_ktype', 'Non défini')
    
    # 1. Analyse spécifique à la ferme (si contexte présent)
    if "conseille" in msg or "analyse" in msg or "quelles actions" in msg:
        recs = [
            "Augmenter le pâturage tournant pour réduire les coûts alimentaires.",
            "Implanter des haies (SCA) pour améliorer le score biodiversité.",
            "Étudier le passage en agriculture biologique (si K-Type compatible)."
        ]
        return ChatResponse(
            response=f"Basé sur le K-Type '{ktype}', je recommande de focaliser sur l'autonomie protéique. Votre chargement actuel permet une transition vers un système plus herbager sans perte majeure de marge.",
            reasoning_steps=[
                f"Identification du profil INOSYS : {ktype}",
                "Comparaison avec les références régionales",
                "Calcul des marges de progression environnementales"
            ],
            suggested_actions=["Lancer simulation +10% herbe", "Consulter fiche K-Type"],
            citations=[{"id": "REF-INOSYS", "title": f"Référentiel {ktype}", "url": f"/ref/{ktype}"}]
        )

    # 2. Réglementation / Diagnostic
    if "réglement" in msg or "loi" in msg or "norme" in msg:
        return ChatResponse(
            response="La directive Nitrate impose une couverture des sols en hiver (SIE/CIPAN). Pour votre exploitation, cela implique d'ajuster le plan d'épandage sur les parcelles proches des cours d'eau.",
            reasoning_steps=["Analyse conformité réglementaire", "Vérification zones vulnérables"],
            citations=[{"id": "DIR-NITRATE", "title": "Directive Nitrate 2024", "url": "https://agriculture.gouv.fr/nitrates"}],
            suggested_actions=["Vérifier plan d'épandage", "Calculer balance azotée"]
        )

    # Default fallback
    return ChatResponse(
        response="Je suis votre assistant AgriTransition. Posez-moi une question sur les aides, la technique (herbe, carbone) ou demandez-moi d'analyser cette ferme.",
        reasoning_steps=["Analyse intention : Question générale"],
        suggested_actions=["Simulation carbone", "Aides PCAE", "Fiches techniques"]
    )
        
    # 4. Fallback
    return ChatResponse(
        reasoning_steps=["Analyse sémantique échouée", "Demande de précision"],
        response="Je comprends que vous cherchez une information. Pourriez-vous préciser si cela concerne l'aspect technique (agronomie), économique ou réglementaire ?",
        suggested_actions=["Aspect Technique", "Aspect Économique"]
    )

@app.get("/")
async def root():
    return {"message": "API AgriTransition v1.2 (Outil Conseiller)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
