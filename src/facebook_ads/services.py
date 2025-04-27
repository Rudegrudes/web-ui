"""
Módulo de serviços para a API do Facebook Ads.
Este módulo fornece funções para acessar e manipular recursos da API do Facebook Ads.
"""

from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
import os
import logging

logger = logging.getLogger(__name__)

class FacebookAdsServiceError(Exception):
    """Exceção para erros de serviço da API do Facebook Ads."""
    pass

def get_ad_account():
    """
    Retorna o objeto de conta de anúncios configurado no arquivo .env
    
    Returns:
        AdAccount: Objeto da conta de anúncios
        
    Raises:
        FacebookAdsServiceError: Se o ID da conta não estiver configurado
    """
    account_id = os.getenv("FACEBOOK_AD_ACCOUNT_ID")
    if not account_id:
        error_msg = "ID da conta de anúncios (FACEBOOK_AD_ACCOUNT_ID) não configurado no arquivo .env"
        logger.error(error_msg)
        raise FacebookAdsServiceError(error_msg)
    
    # Formato esperado: act_<account_id>
    if not account_id.startswith("act_"):
        account_id = f"act_{account_id}"
    
    try:
        return AdAccount(account_id)
    except Exception as e:
        error_msg = f"Erro ao acessar a conta de anúncios {account_id}: {str(e)}"
        logger.error(error_msg)
        raise FacebookAdsServiceError(error_msg) from e

def get_campaigns(limit=100, fields=None):
    """
    Retorna as campanhas da conta de anúncios
    
    Args:
        limit (int): Número máximo de campanhas a retornar
        fields (list): Lista de campos a serem retornados
        
    Returns:
        list: Lista de objetos Campaign
        
    Raises:
        FacebookAdsServiceError: Se ocorrer um erro ao acessar as campanhas
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
            'special_ad_categories'
        ]
    
    try:
        account = get_ad_account()
        campaigns = account.get_campaigns(
            fields=fields,
            params={'limit': limit}
        )
        return campaigns
    except Exception as e:
        error_msg = f"Erro ao obter campanhas: {str(e)}"
        logger.error(error_msg)
        raise FacebookAdsServiceError(error_msg) from e

def format_campaign_for_display(campaign):
    """
    Formata os dados de uma campanha para exibição
    
    Args:
        campaign (Campaign): Objeto da campanha
        
    Returns:
        dict: Dicionário com os dados formatados da campanha
    """
    campaign_data = campaign.export_all_data()
    
    # Formatar orçamento
    if 'daily_budget' in campaign_data:
        campaign_data['daily_budget_formatted'] = f"${int(campaign_data['daily_budget'])/100:.2f}/dia"
    
    if 'lifetime_budget' in campaign_data:
        campaign_data['lifetime_budget_formatted'] = f"${int(campaign_data['lifetime_budget'])/100:.2f} (total)"
    
    return campaign_data
