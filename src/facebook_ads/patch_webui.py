import importlib
import sys
import os

# Adicionar a modificação para importar o módulo do Facebook Ads
def patch_webui_for_facebook_ads():
    """
    Modifica o arquivo webui.py para incluir a integração com o Facebook Ads
    """
    webui_path = os.path.join(os.path.dirname(__file__), '..', '..', 'webui.py')
    
    with open(webui_path, 'r') as f:
        content = f.read()
    
    # Verificar se a integração já foi adicionada
    if 'from src.facebook_ads.ui import create_facebook_ads_tab' in content:
        print("Integração com Facebook Ads já está presente no arquivo webui.py")
        return
    
    # Adicionar importação
    import_line = 'from src.utils import utils'
    new_import = 'from src.utils import utils\nfrom src.facebook_ads.ui import create_facebook_ads_tab'
    content = content.replace(import_line, new_import)
    
    # Encontrar o local para adicionar a chamada da função
    # Procurar por uma linha que contenha "with gr.Tab" para adicionar nossa aba após
    tab_lines = [line for line in content.split('\n') if 'with gr.Tab' in line]
    
    if tab_lines:
        # Encontrar a última ocorrência de uma definição de aba
        last_tab_line = tab_lines[-1]
        # Adicionar nossa chamada de função após o bloco de abas
        # Encontrar o bloco que contém a última aba
        blocks = content.split('with gr.Blocks')
        for i, block in enumerate(blocks):
            if last_tab_line in block:
                # Adicionar nossa chamada no final deste bloco
                lines = block.split('\n')
                for j, line in enumerate(lines):
                    if 'scan_and_register_components' in line:
                        # Adicionar antes da chamada de scan_and_register_components
                        lines.insert(j, '    # Adicionar aba do Facebook Ads\n    create_facebook_ads_tab()')
                        blocks[i] = '\n'.join(lines)
                        break
                break
        
        # Reconstruir o conteúdo
        content = 'with gr.Blocks'.join(blocks)
    
    # Escrever o arquivo modificado
    with open(webui_path, 'w') as f:
        f.write(content)
    
    print("Arquivo webui.py modificado com sucesso para incluir a integração com o Facebook Ads")

if __name__ == "__main__":
    patch_webui_for_facebook_ads()
