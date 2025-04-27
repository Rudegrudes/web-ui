"""
Módulo para gerenciamento de campanhas no Facebook Ads.
Este módulo fornece funções para criar, atualizar e gerenciar campanhas publicitárias.
"""

from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adaccount import AdAccount
from .services import get_ad_account
import logging

logger = logging.getLogger(__name__)

class FacebookAdsCampaignError(Exception):
    """Exceção para erros relacionados a campanhas no Facebook Ads."""
    pass

def create_campaign(name, objective, status="PAUSED", special_ad_categories=None, 
                   daily_budget=None, lifetime_budget=None, bid_strategy=None):
    """
    Cria uma nova campanha no Facebook Ads
    
    Args:
        name (str): Nome da campanha
        objective (str): Objetivo da campanha (ex: 'REACH', 'BRAND_AWARENESS', etc.)
        status (str): Status inicial da campanha ('ACTIVE', 'PAUSED')
        special_ad_categories (list): Categorias especiais de anúncios
        daily_budget (int): Orçamento diário em centavos (ex: 1000 = $10.00)
        lifetime_budget (int): Orçamento total da campanha em centavos
        bid_strategy (str): Estratégia de lance (ex: 'LOWEST_COST_WITHOUT_CAP')
        
    Returns:
        Campaign: Objeto da campanha criada
        
    Raises:
        FacebookAdsCampaignError: Se ocorrer um erro ao criar a campanha
    """
    try:
        account = get_ad_account()
        
        if special_ad_categories is None:
            special_ad_categories = ['NONE']
        
        params = {
            'name': name,
            'objective': objective,
            'status': status,
            'special_ad_categories': special_ad_categories
        }
        
        # Adicionar orçamento (apenas um tipo de orçamento pode ser definido)
        if daily_budget:
            params['daily_budget'] = daily_budget
        elif lifetime_budget:
            params['lifetime_budget'] = lifetime_budget
            
        # Adicionar estratégia de lance se fornecida
        if bid_strategy:
            params['bid_strategy'] = bid_strategy
        
        campaign = account.create_campaign(params=params)
        logger.info(f"Campanha criada com sucesso: {name} (ID: {campaign['id']})")
        return campaign
    except Exception as e:
        error_msg = f"Erro ao criar campanha '{name}': {str(e)}"
        logger.error(error_msg)
        raise FacebookAdsCampaignError(error_msg) from e

def get_campaign_details(campaign_id, fields=None):
    """
    Obtém detalhes de uma campanha específica
    
    Args:
        campaign_id (str): ID da campanha
        fields (list): Lista de campos a serem retornados
        
    Returns:
        Campaign: Objeto da campanha com os detalhes solicitados
        
    Raises:
        FacebookAdsCampaignError: Se ocorrer um erro ao obter os detalhes da campanha
    """
    if fields is None:
        fields = [
            'id', 
            'name', 
            'objective', 
            'status', 
            'created_time', 
            'updated_time',
            'daily_budget',
            'lifetime_budget',
            'special_ad_categories',
            'bid_strategy'
        ]
    
    try:
        campaign = Campaign(campaign_id)
        campaign.api_get(fields=fields)
        return campaign
    except Exception as e:
        error_msg = f"Erro ao obter detalhes da campanha {campaign_id}: {str(e)}"
        logger.error(error_msg)
        raise FacebookAdsCampaignError(error_msg) from e

def update_campaign(campaign_id, **kwargs):
    """
    Atualiza uma campanha existente
    
    Args:
        campaign_id (str): ID da campanha
        **kwargs: Parâmetros a serem atualizados (name, status, daily_budget, etc.)
        
    Returns:
        Campaign: Objeto da campanha atualizada
        
    Raises:
        FacebookAdsCampaignError: Se ocorrer um erro ao atualizar a campanha
    """
    try:
        campaign = Campaign(campaign_id)
        campaign.api_update(fields=[], params=kwargs)
        logger.info(f"Campanha {campaign_id} atualizada com sucesso")
        return campaign
    except Exception as e:
        error_msg = f"Erro ao atualizar campanha {campaign_id}: {str(e)}"
        logger.error(error_msg)
        raise FacebookAdsCampaignError(error_msg) from e

def delete_campaign(campaign_id):
    """
    Exclui uma campanha
    
    Args:
        campaign_id (str): ID da campanha
        
    Returns:
        bool: True se a exclusão foi bem-sucedida
        
    Raises:
        FacebookAdsCampaignError: Se ocorrer um erro ao excluir a campanha
    """
    try:
        campaign = Campaign(campaign_id)
        result = campaign.api_delete()
        logger.info(f"Campanha {campaign_id} excluída com sucesso")
        return result
    except Exception as e:
        error_msg = f"Erro ao excluir campanha {campaign_id}: {str(e)}"
        logger.error(error_msg)
        raise FacebookAdsCampaignError(error_msg) from e
