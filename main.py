from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
from project_form import AddProject, EditProject
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

# Cria a aplicação do Flask e configura uma chave para a aplicação.
app = Flask(__name__)
app.config["SECRET_KEY"] = "7S8H6axZa11Q471c7X1025G103041031MQ52Ypch0J2cpK53s10izXWa"

# Configura a URI do banco de dados SQLite.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project-manager.db"
# Desativa o acompanhamento de modificações do SQLAlchemy.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializa o Bootstrap e o SQLAlchemy com a aplicação Flask.
Bootstrap(app)
db = SQLAlchemy(app)

# Cria um modelo de dados para gerenciar os projetos.
class ProjectManager(db.Model):
    # Define as colunas do modelo.
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(75), unique=True, nullable=False)
    start = db.Column(db.String(12), unique=False, nullable=False)
    end = db.Column(db.String(12), unique=False, nullable=False)
    participants = db.Column(db.Integer, unique=False, nullable=False)
    status = db.Column(db.String(10), unique=False, nullable=False)
    priority = db.Column(db.String(14), unique=False, nullable=False)


# Cria o banco de dados (caso ainda ele não exista) com as tabelas definidas pelo modelo ProjectManager.
with app.app_context():
    db.create_all()

# Define uma rota para a página inicial.
@app.route("/", methods=["GET", "POST"])
def home():
    # Cria instâncias de formulários de adição e edição de projetos.
    add_form = AddProject()
    edit_form = EditProject()

    # Obtém o parâmetro de ordenação de query da URL.
    order_by = request.args.get("order_by")
    # Obtém o parâmetro de resposta da query da URL.
    response = request.args.get("response")

    # Define a ordenação da query..
    match order_by:
        # Ordena a query pelo nome dos projetos.
        case "Nome":
            project_data = ProjectManager.query.order_by(ProjectManager.name).all()
        # Ordena a query pelo status, seguindo uma ordem personalizada.
        case "Status":
            project_data = ProjectManager.query.order_by(
                db.case((ProjectManager.status == "Contínuo", 1),
                        (ProjectManager.status == "Em andamento", 2),
                        (ProjectManager.status == "Em espera", 3),
                        (ProjectManager.status == "Em planejamento", 4),
                        (ProjectManager.status == "Concluído", 5),
                        (ProjectManager.status == "Cancelado", 6))).all()
        # Ordena a query pela prioridade dos projetos, seguindo uma ordem personalizada.
        case "Prioridade":
            project_data = ProjectManager.query.order_by(
                db.case((ProjectManager.priority == "Alta", 1),
                        (ProjectManager.priority == "Média", 2),
                        (ProjectManager.priority == "Baixa", 3),
                        (ProjectManager.priority == "Sem Prioridade", 4))).all()
        # Caso a ordenação não tenha sido especificada, ordena a query pelo ID dos projetos.
        case _:
            order_by = "ID"
            project_data = ProjectManager.query.all()

    # Renderiza a página inicial, com os formulários, os dados dos projetos na ordem especificada e a mensagem de resposta.
    return render_template("index.html", addform=add_form, editform=edit_form, data=project_data, order_by=order_by,
                           response=response)

# Define uma rota para adição de projetos.
@app.route("/add", methods=["GET", "POST"])
def add():
    # Cria uma instância do formulário para adicionar projetos.
    add_form = AddProject()
    # Obtém a ordenação atual da página inicial
    order_by = request.args.get("order_by")

    # Verifica se o formulário é valido.
    if add_form.validate_on_submit():
        # Tenta adicionar o projeto ao banco de dados.
        try:
            db.session.add(ProjectManager(name=add_form.name.data,
                                          start=add_form.start.data.strftime("%d/%m/%Y") if add_form.start.data
                                          else "Não Previsto",
                                          end=add_form.end.data.strftime("%d/%m/%Y") if add_form.end.data
                                          else "Não Previsto",
                                          participants=add_form.participants.data,
                                          priority=add_form.priority.data,
                                          status=add_form.status.data))

            # Realiza o commit da transação no banco de dados.
            db.session.commit()
        # Se houver uma violação de integridade (nome do projeto já existir do banco de dados):
        except IntegrityError:
            # Redireciona o usuário para a página inicial com a mensagem de falha na adição do projeto.
            return redirect(url_for("home", order_by=order_by, response="addFailed"))

        # Redireciona o usuário para a página inicla com a mensagem de sucesso na adição.
        return redirect(url_for("home", order_by=order_by, response="addSuccess"))

@app.route("/edit", methods=["GET", "POST"])
def edit():
    # Cria uma instância do formulário para editar projetos.
    edit_form = EditProject()
    # Obtém a ordenação atual da página inicial.
    order_by = request.args.get("order_by")

    # Obtém o projeto a ser editado com base no parâmetro "id" da query.
    project = ProjectManager.query.filter_by(id=request.args.get("id"))

    # Itera sobre os campos do formulário.
    for item in edit_form:
        # Verifica se o campo foi preenchido.
        if item.data:
            # Verifica se o campo não é o botão de enviar ou o token csrf.
            if "send_button" != item.id != "csrf_token":
                # Se o campo for "start" ou "end", atualiza o valor com o formato de data correto.
                if item.name == "start" or item.name == "end":
                    project.update({item.name: item.data.strftime("%d/%m/%Y")})
                    # Passa para a próxima iteração.
                    continue
                # Se não for um campo de data, tenta atualizar o valor diretamente.
                try:
                    project.update({item.name: item.data})
                # Em caso de erro de integridade:
                except IntegrityError:
                    # Redireciona o usuário para a página inicial com a mensagem de erro.
                    return redirect(url_for('home', order_by=order_by, response="editFailed"))

    # Realiza o commit das atualizações no banco de dados.
    db.session.commit()

    # Redireciona para a página inicial com a mensagem de sucesso.
    return redirect(url_for('home', order_by=order_by, response="editSuccess"))

# Define uma rota para a remoção de projetos.
@app.route("/delete", methods=["GET", "POST"])
def delete():
    # Obtém a ordenação atual da página inicial.
    order_by = request.args.get("order_by")

    # Remove o projeto do banco de dados com base no seu id.
    db.session.delete(db.session.get(ProjectManager, request.args.get("id")))
    # Realiza o commit da remoção no banco de dados.
    db.session.commit()

    # Redireciona o usuário para a página inicial com uma mensagem de sucesso.
    return redirect(url_for('home', order_by=order_by, response="deleteSuccess"))


# Verifica se o foi executado diretamente.
if __name__ == "__main__":
    # Executa  a aplicação Flask em modo de depuração.
    app.run(debug=True)
