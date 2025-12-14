from typing import List, Dict


def get_local_support(bairro: str) -> List[Dict]:
    """Retorna apoios locais simulados para demo."""
    if not bairro:
        return []

    if bairro.strip().lower() == "rocinha":
        return [
            {
                "nome": "Cozinha Solidária da Rocinha",
                "tipo": "cozinha_solidaria",
                "endereco": "Laboriaux – Rocinha",
                "horario": "11h às 15h",
                "days": "Seg–Sex",
                "distance_km": 0.8,
                "phone": "+55 21 99999-9999",
            },
            {
                "nome": "ONG de Cestas Básicas",
                "tipo": "cesta_basica",
                "endereco": "Associação de Moradores",
                "horario": "Quartas e Sábados",
                "days": "Quartas e Sábados",
                "distance_km": 1.4,
                "phone": "",
            },
        ]

    return []

