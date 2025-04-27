"""
Módulo de utilidades para a integração com o Facebook Ads.
Este módulo fornece funções auxiliares para a integração com a API do Facebook Ads.
"""

import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Mapeamento de objetivos de campanha para descrições amigáveis
CAMPAIGN_OBJECTIVES = {
    'BRAND_AWARENESS': 'Reconhecimento da marca',
    'REACH': 'Alcance',
    'TRAFFIC': 'Tráfego',
    'APP_INSTALLS': 'Instalações do aplicativo',
    'VIDEO_VIEWS': 'Visualizações de vídeo',
    'LEAD_GENERATION': 'Geração de leads',
    'CONVERSIONS': 'Conversões',
    'SALES': 'Vendas',
    'ENGAGEMENT': 'Engajamento'
}

# Mapeamento de status de campanha para descrições amigáveis
CAMPAIGN_STATUS = {
    'ACTIVE': 'Ativa',
    'PAUSED': 'Pausada',
    'DELETED': 'Excluída',
    'ARCHIVED': 'Arquivada'
}

def format_currency(amount_cents):
    """
    Formata um valor em centavos para exibição como moeda
    
    Args:
        amount_cents (int): Valor em centavos
        
    Returns:
        str: Valor formatado como moeda (ex: $10.00)
    """
    if amount_cents is None:
        return "N/A"
    
    return f"${amount_cents/100:.2f}"

def format_datetime(timestamp):
    """
    Formata um timestamp para exibição
    
    Args:
        timestamp (str): Timestamp no formato ISO
        
    Returns:
        str: Data e hora formatadas
    """
    if not timestamp:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except Exception as e:
        logger.warning(f"Erro ao formatar timestamp {timestamp}: {str(e)}")
        return timestamp

def campaign_to_dict(campaign):
    """
    Converte um objeto Campaign para um dicionário com dados formatados
    
    Args:
        campaign: Objeto Campaign do Facebook Ads
        
    Returns:
        dict: Dicionário com os dados da campanha formatados
    """
    try:
        data = campaign.export_all_data()
        
        # Adicionar campos formatados
        if 'objective' in data:
            data['objective_formatted'] = CAMPAIGN_OBJECTIVES.get(data['objective'], data['objective'])
        
        if 'status' in data:
            data['status_formatted'] = CAMPAIGN_STATUS.get(data['status'], data['status'])
        
        if 'daily_budget' in data:
            data['daily_budget_formatted'] = format_currency(data['daily_budget'])
        
        if 'lifetime_budget' in data:
            data['lifetime_budget_formatted'] = format_currency(data['lifetime_budget'])
        
        if 'created_time' in data:
            data['created_time_formatted'] = format_datetime(data['created_time'])
        
        if 'updated_time' in data:
            data['updated_time_formatted'] = format_datetime(data['updated_time'])
        
        return data
    except Exception as e:
        logger.error(f"Erro ao converter campanha para dicionário: {str(e)}")
        return {"error": str(e)}

def campaigns_to_json(campaigns):
    """
    Converte uma lista de campanhas para JSON formatado
    
    Args:
        campaigns: Lista de objetos Campaign
        
    Returns:
        str: JSON formatado com os dados das campanhas
    """
    try:
        campaign_list = [campaign_to_dict(campaign) for campaign in campaigns]
        return json.dumps(campaign_list, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao converter campanhas para JSON: {str(e)}")
        return json.dumps({"error": str(e)})
