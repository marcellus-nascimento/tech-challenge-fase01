from flask import Flask, jsonify, request
from scraper import VitiviniculturaScraper
from flask_httpauth import HTTPBasicAuth
from flasgger import Swagger

# Inicializo a aplicação Flask
app = Flask(__name__)
swagger = Swagger(app)

# Inicializar o auth
auth = HTTPBasicAuth()
users = {
    "usuarioteste": "1234"
}

@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username

# Crio uma instância do scraper para ser usada nas rotas
scraper = VitiviniculturaScraper()

@app.route('/api/<category>', methods=['GET'])
@auth.login_required
def get_data(category):
    """
    Obtém dados da categoria especificada
    ---
    parameters:
      - name: category
        in: path
        type: string
        required: true
        description: Diz respeito a categoria de dados a serem extraídos e correspondem as abas do site da Embrapa. São os dados de Produção, Processamento, Comercialização, Importação e Exportação
      - name: start_year
        in: query
        type: integer
        required: false
        default: 1970
        description: Ano inicial para o filtro
      - name: end_year
        in: query
        type: integer
        required: false
        default: 2023
        description: Ano final para o filtro
      - name: subcategory
        in: query
        type: string
        required: false
        description: São os tipos de produtos que foram processados, importados e exportados. São presentes apenas para as categorias de "Processamento" (subcategorias "viniferas", "americanas e híbridas", "uvas de mesa" e "sem classificação"); "Importação"(subcategorias "vinhos de mesa", "espumantes", "uvas frescas", "uvas passas" e "suco de uva") e "Exportação"(subcategorias "vinhos de mesa", "espumantes", "uvas frescas", e "suco de uva")
    responses:
      200:
        description: Dados obtidos com sucesso
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: object
                properties:
                  atributo1:
                    type: string
                  atributo2:
                    type: integer
      400:
        description: Categoria ou subcategoria inválida
    """
    start_year = request.args.get('start_year', default=1970, type=int)
    end_year = request.args.get('end_year', default=2023, type=int)
    subcategory = request.args.get('subcategory', default=None, type=str)

    if category not in scraper.BASE_URLS:
        return jsonify({"error": "Categoria inválida"}), 400

    if category in ['processamento', 'importacao', 'exportacao'] and subcategory not in scraper.SUBCATEGORIES[category]:
        return jsonify({"error": "Subcategoria inválida para a categoria selecionada"}), 400

    data = scraper.scrape_data(start_year, end_year, category, subcategory)
    return jsonify(data)

@app.route('/')
def home():
    """
    Página inicial com as rotas disponíveis
    ---
    responses:
      200:
        description: Página inicial com links para as rotas da API
        content:
          text/html:
            schema:
              type: string
    """
    return """
    <h1>Bem-vindo à API de Dados Vitivinícolas!</h1>
    <p>Use as rotas abaixo para acessar os dados:</p>
    <ul>
        <li><a href="/api/producao">/api/producao</a>: Dados de Produção.</li>
        <li><a href="/api/processamento?subcategory=viniferas">/api/processamento?subcategory=viniferas</a>: Dados de Viníferas.</li>
        <li><a href="/api/processamento?subcategory=americanas_hibridas">/api/processamento?subcategory=americanas_hibridas</a>: Dados de Americanas e Híbridas.</li>
        <li><a href="/api/processamento?subcategory=uvas_de_mesa">/api/processamento?subcategory=uvas_de_mesa</a>: Dados de Uvas de Mesa.</li>
        <li><a href="/api/processamento?subcategory=sem_classificacao">/api/processamento?subcategory=sem_classificacao</a>: Sem Classificação.</li>
        <li><a href="/api/comercializacao">/api/comercializacao</a>: Dados de Comercialização.</li>
        <li><a href="/api/importacao?subcategory=vinhos_de_mesa">/api/importacao?subcategory=vinhos_de_mesa</a>: Vinhos de Mesa (Importação).</li>
        <li><a href="/api/importacao?subcategory=espumantes">/api/importacao?subcategory=espumantes</a>: Espumantes (Importação).</li>
        <li><a href="/api/importacao?subcategory=uvas_frescas">/api/importacao?subcategory=uvas_frescas</a>: Uvas Frescas (Importação).</li>
        <li><a href="/api/importacao?subcategory=uvas_passas">/api/importacao?subcategory=uvas_passas</a>: Uvas Passas (Importação).</li>
        <li><a href="/api/importacao?subcategory=suco_de_uva">/api/importacao?subcategory=suco_de_uva</a>: Suco de Uva (Importação).</li>
        <li><a href="/api/exportacao?subcategory=vinhos_de_mesa">/api/exportacao?subcategory=vinhos_de_mesa</a>: Vinhos de Mesa (Exportação).</li>
        <li><a href="/api/exportacao?subcategory=espumantes">/api/exportacao?subcategory=espumantes</a>: Espumantes (Exportação).</li>
        <li><a href="/api/exportacao?subcategory=uvas_frescas">/api/exportacao?subcategory=uvas_frescas</a>: Uvas Frescas (Exportação).</li>
        <li><a href="/api/exportacao?subcategory=suco_de_uva">/api/exportacao?subcategory=suco_de_uva</a>: Suco de Uva (Exportação).</li>
    </ul>
    <p>Você pode adicionar parâmetros <code>start_year</code>, <code>end_year</code> para filtrar os dados. 
    /api/{categoria}?start_year=2010&end_year=2020 ou /api/{categoria}?{subcategoria}&start_year=2010&end_year=2020</p>
    """

# Inicializo o servidor da API
if __name__ == '__main__':
    app.run(debug=True)