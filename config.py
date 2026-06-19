
import os
import sys
from paths import resource_path

RISK_CONFIG = {
    "flexao_tronco":    {"max_angulo": 35, "min_duracao_seg": 0.5,  "nome": "Flexão Excessiva de Tronco"},
    "elevacao_ombro":   {"max_angulo": 80, "min_duracao_seg": 0.5,  "nome": "Elevação Excessiva de Ombro"},
    "flexao_pescoco":   {"max_angulo": 40, "min_duracao_seg": 0.5,  "nome": "Flexão Excessiva de Pescoço"},
    "flexao_joelho":    {"max_angulo": 60, "min_duracao_seg": 0.5,  "nome": "Flexão Excessiva de Joelho"},
    "elevacao_braco":   {"max_angulo": 90, "min_duracao_seg": 0.5,  "nome": "Elevação Excessiva de Braço"},
}

TAGS_OFICIAIS = [
    "lombar",
    "costas",
    "ombros",
    "braços",
    "trabalho_aereo",
    "pernas",
    "joelhos",
    "pescoço",
    "levantamento",
    "suporte_assimetrico",
    "em_pe",
    "sentado",

]
NIVEL_CHOICES = ["baixo", "médio", "médio-alto", "alto"]

# ===================== SQLITE - PORTFÓLIO EXOESQUELETOS =====================
if getattr(sys, 'frozen', False):
    DB_PATH = os.path.join(os.path.dirname(sys.executable), "exoskeletons.db")
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exoskeletons.db")

# ===================== MAPEAMENTO RISCO → SUPORTE =====================
MAPEAMENTO_RISCO_SUPORTE = {
    "Flexão Excessiva de Tronco": ["lombar", "costas", "levantamento"],
    "Elevação Excessiva de Ombro": ["ombros", "braços", "trabalho_aereo"],
    "Flexão Excessiva de Pescoço": ["pescoço", "ombros"],
    "Flexão Excessiva de Joelho": ["pernas", "joelhos", "suporte_assimetrico"],
    "Elevação Excessiva de Braço": ["ombros", "braços", "trabalho_aereo"],
}