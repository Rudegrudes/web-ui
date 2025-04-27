"""
Módulo de integração com a API do Facebook Ads.
Este módulo permite a criação e gerenciamento de campanhas publicitárias
através da API do Facebook Ads.
"""

from .config import initialize_facebook_ads_api
from .services import get_ad_account, get_campaigns
from .campaign import create_campaign, get_campaign_details, update_campaign

__all__ = [
    'initialize_facebook_ads_api',
    'get_ad_account',
    'get_campaigns',
    'create_campaign',
    'get_campaign_details',
    'update_campaign'
]
