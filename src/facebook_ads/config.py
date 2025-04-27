"""
Módulo de configuração para a API do Facebook Ads.
Este módulo gerencia a autenticação e inicialização da API do Facebook Ads.
"""

from facebook_business.api import FacebookAdsApi
import os
import logging

logger = logging.getLogger(__name__)

class FacebookAdsConfigError(Exception):
    """Exceção para erros de configuração da API do Facebook Ads."""
    pass

def initialize_facebook_ads_api():
    """
    Inicializa a API do Facebook Ads com credenciais do arquivo .env
    
    Returns:
        bool: True se a inicialização foi bem-sucedida
        
    Raises:
        FacebookAdsConfigError: Se as credenciais não estiverem configuradas
    """
    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    
    if not all([app_id, app_secret, access_token]):
        missing = []
        if not app_id:
            missing.append("FACEBOOK_APP_ID")
        if not app_secret:
            missing.append("FACEBOOK_APP_SECRET")
        if not access_token:
            missing.append("FACEBOOK_ACCESS_TOKEN")
            
        error_msg = f"Credenciais do Facebook Ads não configuradas no arquivo .env: {', '.join(missing)}"
        logger.error(error_msg)
        raise FacebookAdsConfigError(error_msg)
    
    try:
        FacebookAdsApi.init(app_id, app_secret, access_token)
        logger.info("API do Facebook Ads inicializada com sucesso")
        return True
    except Exception as e:
        error_msg = f"Erro ao inicializar a API do Facebook Ads: {str(e)}"
        logger.error(error_msg)
        raise FacebookAdsConfigError(error_msg) from e
