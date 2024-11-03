import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import logging

class VitiviniculturaScraper:
    # URLs base para cada categoria da API
    BASE_URLS = {
        'producao': 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02',
        'processamento': 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_03',
        'comercializacao': 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04',
        'importacao': 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_05',
        'exportacao': 'http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_06'
    }

    # Subcategorias específicas para as categorias que possuem filtros adicionais
    SUBCATEGORIES = {
        'processamento': ['viniferas', 'americanas_hibridas', 'uvas_de_mesa', 'sem_classificacao'],
        'importacao': ['vinhos_de_mesa', 'espumantes', 'uvas_frescas', 'uvas_passas', 'suco_de_uva'],
        'exportacao': ['vinhos_de_mesa', 'espumantes', 'uvas_frescas', 'suco_de_uva']
    }

    def __init__(self):
        # Configuração básica de logs para acompanhar o processo de scraping
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    @staticmethod
    def clean_text(text):
        """Função auxiliar para limpar texto, removendo caracteres especiais."""
        return re.sub(r'[^\w\s]', '', text)

    def scrape_data(self, start_year, end_year, category, subcategory=None):
        """Função principal de scraping que coleta os dados da página da Embrapa.
        Faz requisições por ano e opcionalmente por subcategoria.
        """
        all_data = []  # Lista onde vou armazenar todos os dados extraídos
        header = []  # Cabeçalhos da tabela que serão definidos na primeira iteração
        url = self.BASE_URLS[category]  # Pego a URL base correspondente à categoria

        # Faço o scraping para cada ano no intervalo especificado
        for year in range(start_year, end_year + 1):
            logging.info(f"Extraindo dados para a categoria: {category}, Subcategoria: {subcategory}, Ano: {year}")
            full_url = f"{url}&ano={year}"  # Constrói a URL para o ano específico
            if subcategory:
                full_url += f"&subcategoria={subcategory}"  # Adiciona a subcategoria à URL se aplicável

            # Faço a requisição e parseio o HTML retornado
            response = requests.get(full_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'tb_base tb_dados'})  # Procura pela tabela de dados

            # Se a tabela for encontrada, extraio os dados
            if table:
                rows = table.find_all('tr')  # Todas as linhas da tabela
                if not header:
                    # Defino o cabeçalho com base na primeira linha
                    header = [self.clean_text(cell.get_text(strip=True)) for cell in rows[0].find_all(['th', 'td'])]
                    header.append("Ano")  # Adiciono o campo de ano no cabeçalho
                    header.append("Categoria")  # Adiciono a categoria no cabeçalho
                    if subcategory:
                        header.append("Subcategoria")  # Adiciono a subcategoria, se aplicável
                    all_data.append(header)  # Adiciono o cabeçalho à lista de dados

                # Para cada linha subsequente, extraio os dados e adiciono à lista
                for row in rows[1:]:
                    data = [self.clean_text(cell.get_text(strip=True)) for cell in row.find_all('td')]
                    data.append(str(year))  # Adiciono o ano
                    data.append(category)  # Adiciono a categoria
                    if subcategory:
                        data.append(subcategory)  # Adiciono a subcategoria se houver
                    all_data.append(data)

        # Converto os dados para um DataFrame do Pandas para facilitar a manipulação e retorno
        df = pd.DataFrame(all_data[1:], columns=all_data[0])
        return df.to_dict(orient='records')  # Retorno os dados no formato JSON
