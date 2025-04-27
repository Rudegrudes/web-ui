"""
Módulo de integração da interface do usuário com o Facebook Ads.
Este módulo adiciona componentes de interface para interagir com a API do Facebook Ads.
"""

import gradio as gr
import logging
import json
from src.facebook_ads import (
    initialize_facebook_ads_api,
    get_campaigns,
    create_campaign,
    get_campaign_details,
    update_campaign
)
from src.facebook_ads.utils import campaigns_to_json, CAMPAIGN_OBJECTIVES, CAMPAIGN_STATUS

logger = logging.getLogger(__name__)

def create_facebook_ads_tab():
    """
    Cria a aba de interface do Facebook Ads para o Gradio
    
    Returns:
        gr.Tab: Componente de aba do Gradio com a interface do Facebook Ads
    """
    with gr.Tab("Facebook Ads"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Configuração do Facebook Ads")
                fb_status = gr.Textbox(label="Status da API", value="Não inicializada", interactive=False)
                fb_initialize_btn = gr.Button("Inicializar API do Facebook Ads")
            
            with gr.Column():
                gr.Markdown("### Informações da Conta")
                fb_account_info = gr.Textbox(label="Detalhes da Conta", interactive=False, lines=3)
        
        gr.Markdown("### Gerenciamento de Campanhas")
        
        with gr.Tab("Criar Campanha"):
            with gr.Row():
                fb_campaign_name = gr.Textbox(label="Nome da Campanha", placeholder="Digite o nome da campanha")
                fb_campaign_objective = gr.Dropdown(
                    choices=list(CAMPAIGN_OBJECTIVES.keys()),
                    label="Objetivo da Campanha",
                    value="REACH"
                )
            
            with gr.Row():
                fb_campaign_status = gr.Radio(
                    choices=["ACTIVE", "PAUSED"],
                    value="PAUSED",
                    label="Status da Campanha"
                )
                fb_special_ad_category = gr.CheckboxGroup(
                    choices=["HOUSING", "EMPLOYMENT", "CREDIT", "NONE"],
                    value=["NONE"],
                    label="Categorias Especiais de Anúncios"
                )
            
            with gr.Row():
                fb_daily_budget = gr.Number(label="Orçamento Diário (USD)", value=10.00, step=0.01)
                fb_use_lifetime_budget = gr.Checkbox(label="Usar Orçamento Total", value=False)
                fb_lifetime_budget = gr.Number(label="Orçamento Total (USD)", value=100.00, step=0.01, visible=False)
            
            fb_create_campaign_btn = gr.Button("Criar Campanha", variant="primary")
            fb_create_result = gr.Textbox(label="Resultado", lines=5)
        
        with gr.Tab("Listar Campanhas"):
            with gr.Row():
                fb_list_limit = gr.Slider(minimum=1, maximum=100, value=10, step=1, label="Limite de Campanhas")
                fb_list_campaigns_btn = gr.Button("Listar Campanhas", variant="primary")
            
            fb_campaigns_list = gr.JSON(label="Campanhas")
        
        with gr.Tab("Gerenciar Campanha"):
            with gr.Row():
                fb_campaign_id = gr.Textbox(label="ID da Campanha", placeholder="Digite o ID da campanha")
                fb_get_campaign_btn = gr.Button("Obter Detalhes")
            
            fb_campaign_details = gr.JSON(label="Detalhes da Campanha")
            
            with gr.Row():
                fb_update_name = gr.Textbox(label="Novo Nome", placeholder="Deixe em branco para não alterar")
                fb_update_status = gr.Dropdown(
                    choices=["", "ACTIVE", "PAUSED"],
                    value="",
                    label="Novo Status"
                )
            
            with gr.Row():
                fb_update_budget = gr.Number(label="Novo Orçamento Diário (USD)", value=0, step=0.01)
                fb_update_btn = gr.Button("Atualizar Campanha", variant="primary")
            
            fb_update_result = gr.Textbox(label="Resultado da Atualização")
    
    # Definir callbacks
    fb_initialize_btn.click(
        fn=initialize_facebook_ads_api_ui,
        outputs=[fb_status, fb_account_info]
    )
    
    fb_create_campaign_btn.click(
        fn=create_campaign_ui,
        inputs=[
            fb_campaign_name,
            fb_campaign_objective,
            fb_campaign_status,
            fb_special_ad_category,
            fb_daily_budget,
            fb_use_lifetime_budget,
            fb_lifetime_budget
        ],
        outputs=[fb_create_result]
    )
    
    fb_list_campaigns_btn.click(
        fn=list_campaigns_ui,
        inputs=[fb_list_limit],
        outputs=[fb_campaigns_list]
    )
    
    fb_get_campaign_btn.click(
        fn=get_campaign_details_ui,
        inputs=[fb_campaign_id],
        outputs=[fb_campaign_details]
    )
    
    fb_update_btn.click(
        fn=update_campaign_ui,
        inputs=[
            fb_campaign_id,
            fb_update_name,
            fb_update_status,
            fb_update_budget
        ],
        outputs=[fb_update_result]
    )
    
    # Mostrar/ocultar orçamento total com base na checkbox
    fb_use_lifetime_budget.change(
        fn=lambda x: gr.update(visible=x),
        inputs=[fb_use_lifetime_budget],
        outputs=[fb_lifetime_budget]
    )
    
    return True

def initialize_facebook_ads_api_ui():
    """
    Inicializa a API do Facebook Ads e retorna o status
    
    Returns:
        tuple: (status_message, account_info)
    """
    try:
        initialize_facebook_ads_api()
        from src.facebook_ads.services import get_ad_account
        account = get_ad_account()
        account_fields = ['id', 'name', 'account_status', 'amount_spent', 'balance', 'currency']
        account.api_get(fields=account_fields)
        
        account_info = {
            'id': account['id'],
            'name': account.get('name', 'N/A'),
            'status': account.get('account_status', 'N/A'),
            'currency': account.get('currency', 'USD'),
            'balance': account.get('balance', 0) / 100 if account.get('balance') else 'N/A',
            'amount_spent': account.get('amount_spent', 0) / 100 if account.get('amount_spent') else 'N/A'
        }
        
        account_info_str = (
            f"Conta: {account_info['name']} ({account_info['id']})\n"
            f"Status: {account_info['status']}, Moeda: {account_info['currency']}\n"
            f"Saldo: ${account_info['balance']}, Gasto: ${account_info['amount_spent']}"
        )
        
        return "API inicializada com sucesso", account_info_str
    except Exception as e:
        logger.error(f"Erro ao inicializar API do Facebook Ads: {str(e)}")
        return f"Erro ao inicializar API: {str(e)}", "Não disponível"

def create_campaign_ui(name, objective, status, special_ad_categories, daily_budget, use_lifetime_budget, lifetime_budget):
    """
    Cria uma campanha no Facebook Ads através da interface
    
    Args:
        name (str): Nome da campanha
        objective (str): Objetivo da campanha
        status (str): Status da campanha
        special_ad_categories (list): Categorias especiais de anúncios
        daily_budget (float): Orçamento diário em USD
        use_lifetime_budget (bool): Se deve usar orçamento total
        lifetime_budget (float): Orçamento total em USD
        
    Returns:
        str: Mensagem de resultado
    """
    try:
        # Validar entrada
        if not name:
            return "Erro: Nome da campanha é obrigatório"
        
        if not objective:
            return "Erro: Objetivo da campanha é obrigatório"
        
        # Converter orçamento de USD para centavos
        budget_cents = None
        if use_lifetime_budget and lifetime_budget > 0:
            budget_cents = int(lifetime_budget * 100)
            campaign = create_campaign(
                name=name,
                objective=objective,
                status=status,
                special_ad_categories=special_ad_categories,
                lifetime_budget=budget_cents
            )
        elif daily_budget > 0:
            budget_cents = int(daily_budget * 100)
            campaign = create_campaign(
                name=name,
                objective=objective,
                status=status,
                special_ad_categories=special_ad_categories,
                daily_budget=budget_cents
            )
        else:
            return "Erro: É necessário definir um orçamento válido"
        
        return f"Campanha criada com sucesso!\nID: {campaign['id']}\nNome: {name}\nStatus: {status}\nOrçamento: ${budget_cents/100:.2f}"
    except Exception as e:
        logger.error(f"Erro ao criar campanha: {str(e)}")
        return f"Erro ao criar campanha: {str(e)}"

def list_campaigns_ui(limit):
    """
    Lista as campanhas da conta
    
    Args:
        limit (int): Número máximo de campanhas a retornar
        
    Returns:
        dict: JSON com as campanhas
    """
    try:
        campaigns = get_campaigns(limit=int(limit))
        return json.loads(campaigns_to_json(campaigns))
    except Exception as e:
        logger.error(f"Erro ao listar campanhas: {str(e)}")
        return {"error": str(e)}

def get_campaign_details_ui(campaign_id):
    """
    Obtém detalhes de uma campanha específica
    
    Args:
        campaign_id (str): ID da campanha
        
    Returns:
        dict: Detalhes da campanha
    """
    try:
        if not campaign_id:
            return {"error": "ID da campanha é obrigatório"}
        
        campaign = get_campaign_details(campaign_id)
        from src.facebook_ads.utils import campaign_to_dict
        return campaign_to_dict(campaign)
    except Exception as e:
        logger.error(f"Erro ao obter detalhes da campanha: {str(e)}")
        return {"error": str(e)}

def update_campaign_ui(campaign_id, name, status, budget):
    """
    Atualiza uma campanha existente
    
    Args:
        campaign_id (str): ID da campanha
        name (str): Novo nome (opcional)
        status (str): Novo status (opcional)
        budget (float): Novo orçamento diário em USD (opcional)
        
    Returns:
        str: Mensagem de resultado
    """
    try:
        if not campaign_id:
            return "Erro: ID da campanha é obrigatório"
        
        params = {}
        if name:
            params['name'] = name
        
        if status:
            params['status'] = status
        
        if budget and budget > 0:
            params['daily_budget'] = int(budget * 100)
        
        if not params:
            return "Nenhuma alteração especificada"
        
        update_campaign(campaign_id, **params)
        
        changes = []
        if 'name' in params:
            changes.append(f"Nome: {params['name']}")
        if 'status' in params:
            changes.append(f"Status: {params['status']}")
        if 'daily_budget' in params:
            changes.append(f"Orçamento diário: ${budget:.2f}")
        
        return f"Campanha {campaign_id} atualizada com sucesso!\nAlterações: {', '.join(changes)}"
    except Exception as e:
        logger.error(f"Erro ao atualizar campanha: {str(e)}")
        return f"Erro ao atualizar campanha: {str(e)}"
