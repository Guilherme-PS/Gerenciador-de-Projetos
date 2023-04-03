from flask_wtf import FlaskForm
from wtforms import StringField, DateField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange

class AddProject(FlaskForm):
    name = StringField("Nome do Projeto", validators=[DataRequired()],
                       render_kw={"placeholder": "Digite o Nome do Projeto"})
    start = DateField("Data de Início", format="%Y-%m-%d", validators=[Optional()])
    end = DateField("Data de Término", format="%Y-%m-%d", validators=[Optional()])
    participants = IntegerField("Quantidade de Participantes", validators=[DataRequired(), NumberRange(min=1)],
                                render_kw={"placeholder": "Digite a Quant. de Participantes"})
    priority = SelectField("Prioridade do Projeto", choices=["Sem Prioridade", "Baixa", "Média", "Alta"])
    status = SelectField("Status do Projeto", choices=["Em planejamento", "Contínuo", "Em andamento", "Em espera",
                                                       "Concluído", "Cancelado"])
    send_button = SubmitField("Adicionar")

class EditProject(FlaskForm):
    name = StringField("Nome do Projeto", render_kw={"placeholder": "Digite um Novo Nome para o Projeto"})
    start = DateField("Data de Início", format="%Y-%m-%d")
    end = DateField("Data de Término", format="%Y-%m-%d")
    participants = IntegerField("Quantidade de Participantes", validators=[NumberRange(min=1)],
                                render_kw={"placeholder": "Digite a Nova Quant. de Participantes"})
    priority = SelectField("Prioridade do Projeto", choices=["Sem Prioridade", "Baixa", "Média", "Alta"])
    status = SelectField("Status do Projeto", choices=["Em planejamento", "Contínuo", "Em andamento", "Em espera",
                                                       "Concluído", "Cancelado"])
    send_button = SubmitField("Salvar")
