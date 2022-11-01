from email.policy import default
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from flask.typing import TemplateFilterCallable
from sqlalchemy.orm import backref
from sqlalchemy import text
from werkzeug.datastructures import ContentRange
from werkzeug.exceptions import MethodNotAllowed, abort
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal
from datetime import datetime
import os

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'JcCwEUu3ZLzQc96'
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
db = SQLAlchemy(app)

# Definicao das tabelas do banco de dados
class Ubs(db.Model):   # Nome da tabela e campos conforme banco de dados
    ubs_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ubs_nome = db.Column(db.String(50), nullable=False)
    ubs_endereco = db.Column(db.String(50))
    ubs_numero = db.Column(db.String(20))
    ubs_bairro = db.Column(db.String(35))
    ubs_telefone = db.Column(db.String(11))
    ubs_responsavel = db.Column(db.String(50))
    # ubs_prod = db.relationship('Forn_prod', backref='fp_fornNome') #Nome da Classe e campo virtual

class User(db.Model):
    usr_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usr_nome = db.Column(db.String(50), nullable=False)
    usr_ubs = db.Column(db.Integer)

class Vacinas(db.Model):
    vcn_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vcn_nome = db.Column(db.String(50), nullable=False)
    vcn_protecao = db.Column(db.String(50), nullable=False)
    vcn_est_min = db.Column(db.Numeric)
    vcn_est_max = db.Column(db.Numeric)
    vcn_vol_dose = db.Column(db.Numeric)
    vcn_temperatura = db.Column(db.Numeric)
    vcn_laboratorio = db.Column(db.String(50), nullable=False)
    vcn_reacoes = db.Column(db.String(150))
    vcn_composicao = db.Column(db.String(50))
    vcn_doses = db.Column(db.Numeric)
    vcn_idade_rec = db.Column(db.Integer)
    vcn_intervalo_doses_rec = db.Column(db.Numeric)
    vcn_intervalo_doses_min = db.Column(db.Numeric)
    vcn_via_administracao = db.Column(db.String(50))
    vcn_local_aplicacao = db.Column(db.String(50))
    vcn_agulha = db.Column(db.String(30))

class Lotes(db.Model):   # Nome da tabela e campos conforme banco de dados
    lts_lote = db.Column(db.Integer, primary_key=True)
    lts_vacina = db.Column(db.Integer, nullable=False)
    lts_val_vacina = db.Column(db.DateTime, default=datetime.now())
    lts_nota_fiscal = db.Column(db.Integer)
    lts_dt_recebimento = db.Column(db.DateTime, default=datetime.now())
    lts_qtde_rec = db.Column(db.Numeric)
    lts_campanha = db.Column(db.String(50))
    # ubs_prod = db.relationship('Forn_prod', backref='fp_fornNome') #Nome da Classe e campo virtual

class Requisicoes(db.Model):   # Nome da tabela e campos conforme banco de dados
    req_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    req_vacina = db.Column(db.Integer, nullable=False)
    req_UBS_orig = db.Column(db.Integer)
    req_UBS_dest = db.Column(db.Integer)
    req_qtde = db.Column(db.Numeric)
    req_responsavel = db.Column(db.String(50))
    req_dt_solic = db.Column(db.DateTime, default=datetime.now())
    # ubs_prod = db.relationship('Forn_prod', backref='fp_fornNome') #Nome da Classe e campo virtual

class Movimentacoes(db.Model):   # Nome da tabela e campos conforme banco de dados
    mov_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mov_vacina = db.Column(db.Integer, nullable=False)
    mov_requisicao = db.Column(db.Integer)
    mov_UBS_orig = db.Column(db.Integer)
    mov_UBS_dest = db.Column(db.Integer)
    mov_motivo = db.Column(db.String(50))
    mov_qtde = db.Column(db.Numeric)
    mov_dt_mov = db.Column(db.DateTime, default=datetime.now())
    # ubs_prod = db.relationship('Forn_prod', backref='fp_fornNome') #Nome da Classe e campo virtual

# Rotinas de CRUD
def get_post_ubs(id):
    reg_ubs = Ubs.query.filter_by(ubs_id=id).first()
    if reg_ubs is None:
        flash('Fornecedor não cadastrado')
    return reg_ubs

def get_post_user(id):
    reg_user = User.query.filter_by(usr_id=id).first()
    if reg_user is None:
        flash('Usuário não cadastrado')
    return reg_user

def get_post_vcn(id):
    reg_vcn = Vacinas.query.filter_by(vcn_id=id).first()
    if reg_vcn is None:
        flash('Vacina não cadastrado')
    return reg_vcn

def get_post_lts(id):
    reg_lts = Lotes.query.filter_by(lts_lote=id).first()
    if reg_lts is None:
        flash('Lote não cadastrado')
    return reg_lts

def get_post_req(id):
    reg_req = Requisicoes.query.filter_by(req_id=id).first()
    if reg_req is None:
        flash('Lote não cadastrado')
    return reg_req

def get_post_mov(id):
    reg_mov = Movimentacoes.query.filter_by(req_mov=id).first()
    if reg_mov is None:
        flash('Lote não cadastrado')
    return reg_mov


def get_post_forn_prod(ws_forn, ws_codforn):
    reg_forn_prod = Forn_prod.query.filter_by(fp_forn=ws_forn, fp_codforn=ws_codforn).first()
    if reg_forn_prod is None:
        flash('Produto x fornecedor nâo cadastrado')
    return reg_forn_prod

def get_post_mov(id):
    reg_mov = Movimentacoes.query.filter_by(mov_id = id).first()
    if reg_mov is None:
        abort(404)
    return reg_mov

def atualiza_saldo(codProd, wsQuant, wsTipo):
    ws_RegProd = get_post_prod(codProd)
    ws_SaldoProd = float(ws_RegProd.prd_saldo)
    if wsTipo == "E":
        ws_SaldoProd += wsQuant
    else:
        if (ws_SaldoProd < wsQuant):
            flash('Quantidade maior que saldo atual')
            return False
        else:
            ws_SaldoProd -= wsQuant
    ws_RegProd.prd_saldo = ws_SaldoProd
    db.session.commit()
    return True

def verifica_saldo(codProd, wsQuantNova, wsQuantAtual, wsTipo):
    ws_RegProd = get_post_prod(codProd)
    ws_SaldoProd = float(ws_RegProd.prd_saldo)
    ws_Qtde = wsQuantNova - wsQuantAtual
    if wsTipo == "E":
        ws_SaldoProd += ws_Qtde
        if ws_SaldoProd < 0:
            flash('Quantide maior que saldo atual')
            return False
    else:
        ws_SaldoProd -= ws_Qtde
        if (ws_SaldoProd < 0):
            flash('Quantidade maior que saldo atual')
            return False
    return True

# Definicao de rotas
@app.route('/')
def index():
    return render_template('main.html')

@app.route('/main')
def main():
    return render_template('main.html')

# Rotas do cadastramento

@app.route('/mnucadastro/ubs')   # obrigatório ter o parametro no endereco
def cad_ubs():
    lista_ubs = Ubs.query.all()
    return render_template('Cadastros/ubs.html',lista_ubs=lista_ubs)

@app.route('/mnucadastro/user', methods=('GET', 'POST'))
def cad_user():
    lista_usr = User.query.all()
    return render_template('Cadastros/user.html', lista_user=lista_usr)

@app.route('/mnucadastro/vacinas', methods=('GET', 'POST'))
def cad_vcn():
    lista_vcn = Vacinas.query.all()
    return render_template('Cadastros/vacinas.html', lista_vacinas=lista_vcn)

@app.route('/mnumov/lotes', methods=('GET', 'POST'))
def cad_lts():
    lista_lts = Lotes.query.all()
    return render_template('movimentacao/lotes.html', lista_lotes=lista_lts)

@app.route('/mnumov/requisicoes', methods=('GET', 'POST'))
def cad_req():
    lista_req = Requisicoes.query.all()
    return render_template('movimentacao/requisicoes.html', lista_reqs=lista_req)

@app.route('/mnumov/movimentacoes', methods=('GET', 'POST'))
def cad_mov():
    lista_mov = Movimentacoes.query.all()
    return render_template('movimentacao/mov_vac.html', lista_movs=lista_mov)


# UBS
@app.route('/mnucadastro/lst_ubs', methods=('GET', 'POST'))   # Nao esquecer de colocar os metodos aceitos
def lst_ubs():
    if request.method == 'POST':
        dado = request.form['form_nome']                    # Nomes so sao reconhecidos se estiverem dentro form
        lista_ubs = Ubs.query.filter(Ubs.ubs_nome.like(dado + "%")) # filter_by somente um linha de retorno
        return render_template('Cadastros/ubs.html',lista_ubs=lista_ubs)
    else:
        return render_template('Cadastros/lst_ubs.html')
    
@app.route('/mnucadastro/<int:id>/ubs_alt', methods=('GET','POST'))    # obrigatório ter o parametro no endereco
def alt_ubs(id):
    reg_ubs = get_post_ubs(id)
    if request.method == 'POST':
        ws_nome = request.form['form_nome']
        ws_endereco = request.form['form_endereco']
        ws_numero = request.form['form_numero']
        ws_bairro = request.form['form_bairro']
        ws_telefone = request.form['form_telefone']
        ws_responsavel = request.form['form_responsavel']
        if not ws_nome:
            flash('Nome é obrigatório','error')
        else:
            reg_ubs.ubs_nome = ws_nome
            reg_ubs.ubs_endereco = ws_endereco
            reg_ubs.ubs_numero = ws_numero
            reg_ubs.ubs_bairro = ws_bairro
            reg_ubs.ubs_telefone = ws_telefone
            reg_ubs.ubs_responsavel = ws_responsavel
            db.session.commit()
            flash('Registro alterado')
            return redirect(url_for('cad_ubs'))
    return render_template('Cadastros/alt_ubs.html', reg_ubs=reg_ubs)

@app.route('/mnucadastro/ubs_inc', methods=('GET', 'POST'))
def inc_ubs():                # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
    if request.method == 'POST':
        ws_nome = request.form['form_nome']
        ws_endereco = request.form['form_endereco']
        ws_numero = request.form['form_numero']
        ws_bairro = request.form['form_bairro']
        ws_telefone = request.form['form_telefone']
        ws_responsavel = request.form['form_responsavel']
        if not ws_nome:
            flash('O nome é obrigatório')
        else:
            reg_ubs = Ubs(ubs_nome=ws_nome, ubs_endereco=ws_endereco, ubs_numero=ws_numero, ubs_bairro=ws_bairro, ubs_telefone=ws_telefone, ubs_responsavel=ws_responsavel)
            db.session.add(reg_ubs)
            db.session.commit()
            flash('Inclusao feita com sucesso')
            return redirect(url_for('cad_ubs'))
    return render_template('Cadastros/inc_ubs.html')

@app.route('/mnucadastro/<int:id>/ubs_del', methods=('GET', 'POST'))
def del_ubs(id):
    reg_ubs = get_post_ubs(id)
    db.session.delete(reg_ubs)
    db.session.commit()
    flash('"{}" foi apagado com sucesso'.format(reg_ubs.ubs_nome))
    return redirect(url_for('cad_ubs'))

# Usuários
@app.route('/mnucadastro/lstprod', methods=('GET', 'POST'))   # Nao esquecer de colocar os metodos aceitos
def lst_user():
    if request.method == 'POST':
        dado = request.form['form_nome']                    # Nomes so sao reconhecidos se estiverem dentro form
        lista_usr = User.query.filter(User.usr_nome.like(dado + "%")) # filter_by somente um linha de retorno
        return render_template('Cadastros/user.html',lista_user=lista_usr)
    else:
        return render_template('Cadastros/lst_user.html')
    
@app.route('/mnucadastro/<string:id>/user_alt', methods=('GET','POST'))    # obrigatório ter o parametro no endereco
def alt_user(id):
    lista_ubs = Ubs.query.all()
    reg_usr = get_post_user(id)
    if request.method == 'POST':
        ws_nome = request.form['form_nome']
        ws_ubs = request.form['form_ubs']
        if not ws_nome:
            flash('Nome é obrigatório')
        else:
            reg_usr.usr_nome = ws_nome
            reg_usr.usr_ubs = ws_ubs
            db.session.commit()
            flash('Registro alterado')
            return redirect(url_for('cad_user'))
    return render_template('Cadastros/alt_user.html', reg_user=reg_usr, lista_ubs=lista_ubs)

@app.route('/mnucadastro/user_inc', methods=('GET', 'POST'))
def inc_user():                # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
    lista_ubs = Ubs.query.all()
    if request.method == 'POST':
        ws_nome = request.form['form_nome']
        ws_ubs = request.form['form_ubs']
        if not ws_nome:
            flash('Nome é obrigatoria')
        else:
            reg_user = User(usr_nome=ws_nome,usr_ubs=ws_ubs)
            db.session.add(reg_user)
            db.session.commit()
            flash('Inclusao feita com sucesso')
            return redirect(url_for('cad_user'))
    return render_template('Cadastros/inc_user.html', lista_ubs=lista_ubs)

@app.route('/mnucadastro/<string:id>/user_del', methods=('GET', 'POST'))
def del_user(id):
    reg_user = get_post_user(id)
    db.session.delete(reg_user)
    db.session.commit()
    flash('"{}" foi apagado com sucesso'.format(reg_user.usr_nome))
    return redirect(url_for('cad_user'))

# Vacinas
@app.route('/mnucadastro/lst_vcn', methods=('GET', 'POST'))   # Nao esquecer de colocar os metodos aceitos
def lst_vcn():
    if request.method == 'POST':
        dado = request.form['form_nome']                    # Nomes so sao reconhecidos se estiverem dentro form
        lista_vcn = Vacinas.query.filter(Vacinas.vcn_nome.like(dado + "%")) # filter_by somente um linha de retorno
        return render_template('Cadastros/vacinas.html',lista_vacinas=lista_vcn)
    else:
        return render_template('Cadastros/lst_vcn.html')
    
@app.route('/mnucadastro/<int:id>/vcn_alt', methods=('GET','POST'))    # obrigatório ter o parametro no endereco
def alt_vcn(id):
    reg_vcn = get_post_vcn(id)
    if request.method == 'POST':
        ws_nome = request.form['form_nome']
        ws_protecao = request.form['form_protecao']
        ws_est_min = request.form['form_est_min']
        ws_est_max = request.form['form_est_max']
        ws_vol_dose = request.form['form_vol_dose']
        ws_temperatura = request.form['form_temperatura']
        ws_laboratorio = request.form['form_laboratorio']
        ws_reacoes = request.form['form_reacoes']
        ws_composicao = request.form['form_composicao']
        ws_doses = request.form['form_doses']
        ws_idade_rec = request.form['form_idade_rec']
        ws_intervalo_doses_rec = request.form['form_intervalo_doses_rec']
        ws_intervalo_doses_min = request.form['form_intervalo_doses_min']
        ws_via_administracao = request.form['form_via_administracao']
        ws_local_aplicacao = request.form['form_local_aplicacao']
        ws_agulha = request.form['form_agulha']
        if not ws_nome:
            flash('Nome é obrigatório','error')
        else:
            reg_vcn.vcn_nome = ws_nome
            reg_vcn.vcn_protecao = ws_protecao
            reg_vcn.vcn_est_min = ws_est_min
            reg_vcn.vcn_est_max = ws_est_max
            reg_vcn.vcn_vol_dose = ws_vol_dose
            reg_vcn.vcn_temperatura = ws_temperatura
            reg_vcn.vcn_laboratorio = ws_laboratorio
            reg_vcn.vcn_reacoes = ws_reacoes
            reg_vcn.vcn_composicao = ws_composicao
            reg_vcn.vcn_doses = ws_doses
            reg_vcn.vcn_idade_rec = ws_idade_rec
            reg_vcn.vcn_intervalo_doses_rec = ws_intervalo_doses_rec
            reg_vcn.vcn_intervalo_doses_min= ws_intervalo_doses_min
            reg_vcn.vcn_via_administracao = ws_via_administracao
            reg_vcn.vcn_local_aplicacao = ws_local_aplicacao
            reg_vcn.vcn_agulha = ws_agulha
            db.session.commit()
            flash('Registro alterado')
            return redirect(url_for('cad_vcn'))
    return render_template('Cadastros/alt_vcn.html',reg_vacinas=reg_vcn)

@app.route('/mnucadastro/vcn_inc', methods=('GET', 'POST'))
def inc_vcn():                # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
    if request.method == 'POST':
        ws_nome = request.form['form_nome']
        ws_protecao = request.form['form_protecao']
        ws_est_min = request.form['form_est_min']
        ws_est_max = request.form['form_est_max']
        ws_vol_dose = request.form['form_vol_dose']
        ws_temperatura = request.form['form_temperatura']
        ws_laboratorio = request.form['form_laboratorio']
        ws_reacoes = request.form['form_reacoes']
        ws_composicao = request.form['form_composicao']
        ws_doses = request.form['form_doses']
        ws_idade_rec = request.form['form_idade_rec']
        ws_intervalo_doses_rec = request.form['form_intervalo_doses_rec']
        ws_intervalo_doses_min = request.form['form_intervalo_doses_min']
        ws_via_administracao = request.form['form_via_administracao']
        ws_local_aplicacao = request.form['form_local_aplicacao']
        ws_agulha = request.form['form_agulha']
        if not ws_nome:
            flash('O nome é obrigatório')
        else:
            reg_vcn = Vacinas(vcn_nome=ws_nome,
                              vcn_protecao=ws_protecao,
                              vcn_est_min=ws_est_min,
                              vcn_est_max=ws_est_max,
                              vcn_vol_dose=ws_vol_dose,
                              vcn_temperatura=ws_temperatura,
                              vcn_laboratorio=ws_laboratorio,
                              vcn_reacoes=ws_reacoes,
                              vcn_composicao=ws_composicao,
                              vcn_doses=ws_doses,
                              vcn_idade_rec=ws_idade_rec,
                              vcn_intervalo_doses_rec=ws_intervalo_doses_rec,
                              vcn_intervalo_doses_min=ws_intervalo_doses_min,
                              vcn_via_administracao=ws_via_administracao,
                              vcn_local_aplicacao=ws_local_aplicacao,
                              vcn_agulha=ws_agulha)
            db.session.add(reg_vcn)
            db.session.commit()
            flash('Inclusao feita com sucesso')
            return redirect(url_for('cad_vcn'))
    return render_template('Cadastros/inc_vcn.html')

@app.route('/mnucadastro/<int:id>/vcn_del', methods=('GET', 'POST'))
def del_vcn(id):
    reg_vcn = get_post_vcn(id)
    db.session.delete(reg_vcn)
    db.session.commit()
    flash('"{}" foi apagado com sucesso'.format(reg_vcn.vcn_nome))
    return redirect(url_for('cad_vcn'))

# Lotes
@app.route('/mnucadastro/lst_lotes', methods=('GET', 'POST'))   # Nao esquecer de colocar os metodos aceitos
def lst_lts():
    if request.method == 'POST':
        dado = request.form['form_lote']                    # Nomes so sao reconhecidos se estiverem dentro form
        lista_lts = Lotes.query.filter(Lotes.lts_lote.like(dado + "%")) # filter_by somente um linha de retorno
        if (lista_lts):
            return render_template('movimentacao/lotes.html',lista_lotes=lista_lts)
        else:
            return render_template('movimentacao/lotes.html')
    else:
        return render_template('movimentacao/lst_lotes.html')
    
@app.route('/mnucadastro/<int:id>/lts_alt', methods=('GET','POST'))    # obrigatório ter o parametro no endereco
def alt_lts(id):
    reg_lts = get_post_lts(id)
    if request.method == 'POST':
        ws_vacina = request.form['form_vacina']
        ws_val_vacina = datetime.strptime(request.form['form_val_vacina'],"%Y-%m-%d")
        ws_nota_fiscal = request.form['form_nota_fiscal']
        ws_dt_recebimento = datetime.strptime(request.form['form_dt_recebimento'],"%Y-%m-%d")
        ws_qtde_rec = request.form['form_qtde_rec']
        ws_campanha = request.form['form_campanha']
        if not ws_vacina:
            flash('Vacina é obrigatório','error')
        else:
            reg_lts.lts_vacina = ws_vacina
            reg_lts.lts_val_vacina = ws_val_vacina
            reg_lts.lts_nota_fiscal = ws_nota_fiscal
            reg_lts.lts_dt_recebimento = ws_dt_recebimento
            reg_lts.lts_qtde_rec = ws_qtde_rec
            reg_lts.lts_campanha= ws_campanha
            db.session.commit()
            flash('Registro alterado')
            return redirect(url_for('cad_lts'))
    return render_template('movimentacao/alt_lotes.html', reg_lts=reg_lts)

@app.route('/mnucadastro/lts_inc', methods=('GET', 'POST'))
def inc_lts():                # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
    if request.method == 'POST':
        erro = False
        ws_lote = request.form['form_lote']
        ws_vacina = request.form['form_vacina']
        ws_val_vacina = datetime.strptime(request.form['form_val_vacina'],"%Y-%m-%d")
        ws_nota_fiscal = request.form['form_nota_fiscal']
        ws_dt_recebimento = datetime.strptime(request.form['form_dt_recebimento'],"%Y-%m-%d")
        ws_qtde_rec = request.form['form_qtde_rec']
        ws_campanha = request.form['form_campanha']
        if not ws_vacina:
            flash('O código da vacina é obrigatório') 
            erro = True
        if (ws_val_vacina < ws_dt_recebimento):
            flash("Data de vencimento menor que a data de recebimento") # Checar se o vencimento é menor ou igual a data atual
            erro = True
        if ( not erro):
            reg_lts = Lotes(lts_lote=ws_lote,
                            lts_vacina=ws_vacina,
                            lts_val_vacina=ws_val_vacina,
                            lts_nota_fiscal=ws_nota_fiscal,
                            lts_dt_recebimento=ws_dt_recebimento,
                            lts_qtde_rec=ws_qtde_rec,
                            lts_campanha=ws_campanha)
            db.session.add(reg_lts)
            db.session.commit()
            flash('Inclusao feita com sucesso')
            return redirect(url_for('cad_lts'))
    return render_template('movimentacao/inc_lotes.html')

@app.route('/mnucadastro/<int:id>/lts_del', methods=('GET', 'POST'))
def del_lts(id):
    reg_lts = get_post_lts(id)
    db.session.delete(reg_lts)
    db.session.commit()
    flash('"{}" foi apagado com sucesso'.format(reg_lts.lts_lote))
    return redirect(url_for('cad_lts'))

# Requisições
@app.route('/mnumov/lst_req', methods=('GET', 'POST'))   # Nao esquecer de colocar os metodos aceitos
def lst_req():
    if request.method == 'POST':
        dado = request.form['form_id']                    # Nomes so sao reconhecidos se estiverem dentro form
        lista_req = Requisicoes.query.filter(Requisicoes.req_id.like(dado + "%")) # filter_by somente um linha de retorno
        if (lista_req):
            return render_template('movimentacao/requisicoes.html',lista_reqs=lista_req)
        else:
            return render_template('movimentacao/requisicoes.html')
    else:
        return render_template('movimentacao/lst_requisicoes.html')
    
@app.route('/mnumov/<int:id>/req_alt', methods=('GET','POST'))    # obrigatório ter o parametro no endereco
def alt_req(id):
    lista_ubs = Ubs.query.all()
    reg_req = get_post_req(id)
    if request.method == 'POST':
        erro=False
        ws_id = request.form['form_id']
        ws_dt_solic = datetime.strptime(request.form['form_dt_solic'],"%Y-%m-%d")
        ws_vacina = request.form['form_vacina']
        ws_ubs_orig = request.form['form_ubs_orig']
        ws_ubs_dest = request.form['form_ubs_dest']
        ws_qtde = request.form['form_qtde']
        ws_responsavel = request.form['form_responsavel']
        if not ws_vacina:
            flash('Vacina é obrigatório','error')
            erro = True
        if (ws_ubs_dest == ws_ubs_orig):
            flash("UBS de origem e destino devem ser diferentes")
            erro = True
        if (not erro):
            reg_req.req_id = ws_id
            reg_req.req_dt_solic = ws_dt_solic
            reg_req.req_vacina = ws_vacina
            reg_req.req_UBS_orig = ws_ubs_orig
            reg_req.req_UBS_dest = ws_ubs_dest
            reg_req.req_qtde = ws_qtde
            reg_req.req_responsavel = ws_responsavel
            db.session.commit()
            flash('Registro alterado')
            return redirect(url_for('cad_req'))
    return render_template('movimentacao/alt_requisicoes.html', reg_req=reg_req, lista_ubs=lista_ubs)

@app.route('/mnumov/req_inc', methods=('GET', 'POST'))
def inc_req():                # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
    lista_ubs = Ubs.query.all()
    erro = 0
    if request.method == 'POST':
        ws_dt_solic = datetime.now()
        ws_vacina = request.form['form_vacina']
        ws_ubs_orig = request.form['form_ubs_orig']
        ws_ubs_dest = request.form['form_ubs_dest']
        ws_qtde = request.form['form_qtde']
        ws_responsavel = request.form['form_responsavel']
        if not ws_vacina:
            flash('O código da vacina é obrigatório')
            erro = 1
        if (ws_ubs_orig == ws_ubs_dest):
            flash('As UBS de origem e destino devem ser diferentes')
            erro = 1
        if (erro == 0):
            reg_req = Requisicoes(req_dt_solic = ws_dt_solic,
                            req_vacina=ws_vacina,
                            req_UBS_orig=ws_ubs_orig,
                            req_UBS_dest=ws_ubs_dest,
                            req_qtde=ws_qtde,
                            req_responsavel=ws_responsavel)
            db.session.add(reg_req)
            db.session.commit()
            flash('Inclusao feita com sucesso')
            return redirect(url_for('cad_req'))
    return render_template('movimentacao/inc_requisicoes.html', lista_ubs=lista_ubs)

@app.route('/mnumov/<int:id>/req_del', methods=('GET', 'POST'))
def del_req(id):
    reg_req = get_post_req(id)
    db.session.delete(reg_req)
    db.session.commit()
    flash('"{}" foi apagado com sucesso'.format(reg_req.req_id))
    return redirect(url_for('cad_req'))

# Movimentações
@app.route('/mnumov/lst_mov', methods=('GET', 'POST'))   # Nao esquecer de colocar os metodos aceitos
def lst_mov():
    if request.method == 'POST':
        dado = request.form['form_id']                    # Nomes so sao reconhecidos se estiverem dentro form
        lista_mov = Movimentacoes.query.filter(Movimentacoes.mov_id.like(dado + "%")) # filter_by somente um linha de retorno
        if (lista_mov):
            return render_template('movimentacao/mov_vac.html',lista_movs=lista_mov)
        else:
            return render_template('movimentacao/mov_vac.html')
    else:
        return render_template('movimentacao/lst_mov_vac.html')
    
@app.route('/mnumov/<int:id>/mov_alt', methods=('GET','POST'))    # obrigatório ter o parametro no endereco
def alt_mov(id):
    lista_ubs = Ubs.query.all()
    reg_mov = get_post_mov(id)
    if request.method == 'POST':
        ws_id = request.form['form_id']
        ws_vacina = request.form['form_vacina']
        ws_requisicao = request.form['form_requisicao']
        ws_ubs_orig = request.form['form_ubs_orig']
        ws_ubs_dest = request.form['form_ubs_dest']
        ws_motivo = request.form['form_motivo']
        ws_qtde = request.form['form_qtde']
        # ws_dt_mov = request.form['form_dt_mov']
        if not ws_vacina:
            flash('Vacina é obrigatório','error')
        else:
            reg_mov.mov_id = ws_id
            # reg_mov.req_dt_solic = ws_dt_solic
            reg_mov.mov_vacina = ws_vacina
            reg_mov.mov_UBS_orig = ws_ubs_orig
            reg_mov.mov_UBS_dest = ws_ubs_dest
            reg_mov.mov_qtde = ws_qtde
            reg_mov.mov_requisicao = ws_requisicao
            reg_mov.mov_motivo = ws_motivo
            db.session.commit()
            flash('Registro alterado')
            return redirect(url_for('cad_mov'))
    return render_template('movimentacao/alt_mov_vac.html', reg_mov=reg_mov, lista_ubs=lista_ubs)

@app.route('/mnumov/mov_inc', methods=('GET', 'POST'))
def inc_mov():                # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
    lista_ubs = Ubs.query.all()
    if request.method == 'POST':
        erro = False
        ws_dt_mov = datetime.now()
        ws_vacina = request.form['form_vacina']
        ws_ubs_orig = request.form['form_ubs_orig']
        ws_ubs_dest = request.form['form_ubs_dest']
        ws_qtde = request.form['form_qtde']
        ws_requisicao = request.form['form_requisicao']
        ws_motivo = request.form['form_motivo']
        if not ws_vacina:
            flash('O código da vacina é obrigatório')
            erro = True
        if (ws_ubs_orig == ws_ubs_dest):
            flash('As UBS de origem e destino devem ser diferentes')
            erro = True
        if ( not erro):
            reg_mov = Movimentacoes(mov_dt_mov = ws_dt_mov,
                            mov_vacina=ws_vacina,
                            mov_UBS_orig=ws_ubs_orig,
                            mov_UBS_dest=ws_ubs_dest,
                            mov_qtde=ws_qtde,
                            mov_requisicao=ws_requisicao,
                            mov_motivo=ws_motivo)
            db.session.add(reg_mov)
            db.session.commit()
            flash('Inclusao feita com sucesso')
            return redirect(url_for('cad_mov'))
    return render_template('movimentacao/inc_mov_vac.html', lista_ubs=lista_ubs)

@app.route('/mnumov/<int:id>/mov_del', methods=('GET', 'POST'))
def del_mov(id):
    reg_mov = get_post_mov(id)
    db.session.delete(reg_mov)
    db.session.commit()
    flash('"{}" foi apagado com sucesso'.format(reg_mov.mov_id))
    return redirect(url_for('cad_mov'))

@app.route('/mnucadastro/<string:ws_forn>/<string:ws_codforn>/forn_prod_alt', methods=('GET','POST'))    # obrigatório ter o parametro no endereco
def alt_forn_prod(ws_forn,ws_codforn):
    reg_fp = get_post_forn_prod(ws_forn, ws_codforn)
    wsForNome = reg_fp.fp_fornNome.for_nome
    if request.method == 'POST':
        ws_for = request.form['fpm_forn']
        ws_codfor = request.form['fpm_codforn']
        ws_descricao = request.form['fpm_descr']
        ws_modelo = request.form['fpm_modelo']
        ws_prod = request.form['fpm_prod']
        ws_obs = request.form['fpm_obs']
        ws_alterar = True
        if not ws_descricao:
            flash('Descricao e obrigatório')
            ws_alterar = False
        if not ws_prod:
            flash('Codigo do nosso produto e obrigatório')
            ws_alterar = False
        ws_RegProd = get_post_prod(ws_prod)
        if ws_RegProd is None:
            ws_alterar = False
        if ws_alterar:
            reg_fp.fp_forn = ws_for
            reg_fp.fp_codforn = ws_codfor
            reg_fp.fp_descricao = ws_descricao
            reg_fp.fp_modelo = ws_modelo
            reg_fp.fp_prod = ws_prod
            reg_fp.fp_obs = ws_obs
            db.session.commit()
            flash('Registro alterado')
            return redirect(url_for('cad_vinculo'))
    return render_template('altforn_prod.html', post=reg_fp, ws1 = wsForNome)

@app.route('/mnucadastro/forn_prod_inc', methods=('GET', 'POST'))
def inc_forn_prod():                # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
    if request.method == 'POST':
        ws_for = request.form['fpm_forn']
        ws_codfor = request.form['fpm_codforn']
        ws_descricao = request.form['fpm_descr']
        ws_modelo = request.form['fpm_modelo']
        ws_prod = request.form['fpm_prod']
        ws_obs = request.form['fpm_obs']
        ws_incluir = True
        if  ws_for == "":
            flash('Codigo do fornecedor e obrigatório')
            ws_incluir = False
        else: 
            ws_fornome = get_post_ubs(ws_for)
            if ws_fornome is None:
                ws_incluir = False
        if not ws_codfor:
            flash('Codigo do produto no fornecedor e obrigatório')
            ws_incluir = False
        if not ws_descricao:
            flash('Descricao e obrigatoria')
            ws_incluir = False
        if not ws_prod:
            flash('Codigo do nosso produto e obrigatório')
            ws_incluir = False
        ws_RegProd = get_post_prod(ws_prod)
        if ws_RegProd is None:
            ws_incluir = False
        if ws_incluir:
            reg_fp = Forn_prod(fp_forn=ws_for,fp_codforn=ws_codfor,fp_descricao=ws_descricao,fp_modelo=ws_modelo, fp_prod=ws_prod,fp_obs=ws_obs)
            db.session.add(reg_fp)
            db.session.commit()
            flash('Inclusao feita com sucesso')
            return redirect(url_for('cad_vinculo'))
    return render_template('incforn_prod.html')

@app.route('/mnucadastro/<string:ws_forn>/<string:ws_codforn>/vinc_del', methods=('GET', 'POST'))
def del_fornprod(ws_forn,ws_codforn):
    reg_fornprd = get_post_forn_prod(ws_forn,ws_codforn)
    db.session.delete(reg_fornprd)
    db.session.commit()
    flash('"{}" foi apagado com sucesso'.format(reg_fornprd.fp_forn))
    return redirect(url_for('cad_vinculo'))

# # Movimentacoes
# @app.route('/mnucadastro/lstmov', methods=('GET', 'POST'))   # Nao esquecer de colocar os metodos aceitos
# def lst_mov():
#     if request.method == 'POST':
#         wsCodProd = request.form['frm_mov_CodProd']                    # Nomes so sao reconhecidos se estiverem dentro do form
#         wsPrateleira = request.form['frm_mov_Prateleira']
#         wsNivel = request.form['frm_mov_Nivel']
#         wsCaixa = request.form['frm_mov_Caixa']
#         wsFlag = 0
#         ws_Filtro = ''
#         if wsCodProd :
#             ws_Filtro = 'Movimento.mov_prodforn like "'+wsCodProd+'%"'
#             wsFlag =1
#         if wsPrateleira :
#             if wsFlag == 1:
#                 ws_Filtro = ws_Filtro + ' and '
#             ws_Filtro = ws_Filtro + 'Movimento.mov_prateleira = '+wsPrateleira
#             wsFlag = 1
#         if wsNivel :
#             if wsFlag == 1:
#                 ws_Filtro = ws_Filtro + ' and '
#             ws_Filtro = ws_Filtro + 'Movimento.mov_nivel = '+wsNivel
#             wsFlag = 1
#         if wsCaixa :
#             if wsFlag == 1:
#                 ws_Filtro = ws_Filtro + ' and '
#             ws_Filtro = ws_Filtro + 'Movimento.mov_caixa = '+wsCaixa
#             wsFlag = 1
#         lista_movd = Movimento.query.filter(text(ws_Filtro))        # filter_by somente um linha de retorno
#         return render_template('movimentacao.html',lista_mov=lista_movd)
#     else:
#         return render_template('lstmov.html')
 
# @app.route('/mnucadastro/mov_inc', methods=('GET', 'POST'))
# def inc_mov():                # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
#     if request.method == 'POST':
#         #ws_data = request.form['frm_mov_data']
#         # ws_data= datetime.datetime.utcnow
#         ws_qtde =0
#         ws_incluir = True
#         ws_opera = request.form['frm_mov_opera']
#         ws_qtde_i = request.form['frm_mov_qtde']
#         if not ws_qtde_i:
#             ws_qtde = 0
#         else:
#             ws_qtde = float(ws_qtde_i)
#         ws_prateleira_i = request.form['frm_mov_prateleira']
#         if not ws_prateleira_i:
#             ws_prateleira = 0
#         else:
#             ws_prateleira = int(ws_prateleira_i)
#         ws_nivel_i = request.form['frm_mov_nivel']
#         if not ws_nivel_i:
#             ws_nivel = 0
#         else:
#             ws_nivel = int(ws_nivel_i)
#         ws_caixa_i = request.form['frm_mov_caixa']
#         if not ws_caixa_i:
#             ws_caixa = 0
#         else:
#             ws_caixa = int(ws_caixa_i)
#         ws_os = request.form['frm_mov_os']
#         ws_forn = request.form['frm_mov_forn']
#         ws_prodforn =  request.form['frm_mov_prodforn']
#         ws_obs = request.form['frm_mov_obs']
#         if not ws_forn:
#             flash('Fornecedor é obrigatório')
#             ws_incluir = False
#         if not ws_prodforn:
#             flash('Codigo do produto no fornecedor e obrigatório')
#             ws_incluir = False
#         if ws_qtde <= 0:
#             flash('Quantidade e obrigatório')
#             ws_incluir = False
#         if ws_prateleira <= 0:
#             flash('Prateleira e obrigatório')
#             ws_incluir = False
#         if ws_nivel <= 0:
#             flash('Nivel e obrigatório')
#             ws_incluir = False
#         if ws_caixa <= 0:
#             flash('Caixa e obrigatório')
#             ws_incluir = False
#         wsForProd = get_post_forn_prod(ws_forn,ws_prodforn)
#         if wsForProd is None:
#             ws_incluir = False
#         if ws_incluir:
#             ws_Status = atualiza_saldo(wsForProd.fp_prod,ws_qtde, ws_opera)
#             if ws_Status:
#                 reg_mov = Movimento(mov_opera=ws_opera,mov_qtde=ws_qtde,mov_prateleira=ws_prateleira,mov_nivel=ws_nivel,mov_caixa=ws_caixa,mov_os=ws_os,mov_forn=ws_forn,mov_prodforn=ws_prodforn,mov_user='1',mov_obs=ws_obs)
#                 db.session.add(reg_mov)
#                 db.session.commit()
#                 flash('Inclusao feita com sucesso')
#                 return redirect(url_for('cad_movimentacao'))
#     return render_template('incmov.html')

# @app.route('/mnucadastro/<int:id>/mov_alt', methods=('GET','POST'))    # obrigatório ter o parametro no endereco
# def alt_mov(id):
#     reg_mov = get_post_mov(id)
#     if request.method == 'POST':
#         ws_QtdeAnt = float(reg_mov.mov_qtde)
#         ws_qtde = float(request.form['frm_mov_qtde'])
#         ws_prateleira = int(request.form['frm_mov_prateleira'])
#         ws_nivel = int(request.form['frm_mov_nivel'])
#         ws_caixa = int(request.form['frm_mov_caixa'])
#         ws_os = request.form['frm_mov_os']
#         ws_forn = request.form['frm_mov_forn']
#         ws_prodforn =  request.form['frm_mov_prodforn']
#         ws_obs = request.form['frm_mov_obs']
#         if not ws_forn:
#             flash('Fornecedor é obrigatório')
#         elif not ws_prodforn:
#             flash('Codigo do produto é obrigatório')
#         elif ws_qtde < 1:
#             flash('Quantidade é obrigatório')
#         elif ws_prateleira <= 0:
#             flash('Prateleira é obrigatório')
#         elif ws_nivel <= 0:
#             flash('Nivel é obrigatório')
#         elif ws_caixa <= 0:
#             flash('Caixa é obrigatório')
#         else:
#             wsForProd = get_post_forn_prod(reg_mov.mov_forn,reg_mov.mov_prodforn)
#             ws_alterar = True
#             if wsForProd is None:
#                 ws_alterar = False
#             if ws_alterar:
#                 ws_Status = verifica_saldo(wsForProd.fp_prod,ws_qtde,ws_QtdeAnt, reg_mov.mov_opera)
#                 if ws_Status:
#                     if reg_mov.mov_opera == "E":
#                         atualiza_saldo(wsForProd.fp_prod,ws_qtde, "E")
#                         atualiza_saldo(wsForProd.fp_prod,ws_QtdeAnt, "S")
#                     else:
#                         atualiza_saldo(wsForProd.fp_prod,ws_QtdeAnt, "E")
#                         atualiza_saldo(wsForProd.fp_prod,ws_qtde, "S")
#                     reg_mov.mov_qtde = ws_qtde
#                     reg_mov.mov_prateleira = ws_prateleira
#                     reg_mov.mov_nivel = ws_nivel
#                     reg_mov.mov_caixa = ws_caixa
#                     reg_mov.mov_os = ws_os
#                     reg_mov.mov_forn = ws_forn
#                     reg_mov.mov_prodforn = ws_prodforn
#                     reg_mov.mov_obs = ws_obs
#                     db.session.commit()
#                     flash('Registro alterado')
#                     return redirect(url_for('cad_movimentacao'))
#     return render_template('altmov.html',post=reg_mov)

# @app.route('/mnucadastro/<string:id>/mov_del', methods=('GET', 'POST'))
# def del_mov(id):
#     reg_mov = get_post_mov(id)
#     if reg_mov.mov_opera == "E":
#         wsTipo = "S"
#     else:
#         wsTipo = "E"
#     ws_apagar = True
#     wsForProd = get_post_forn_prod(reg_mov.mov_forn,reg_mov.mov_prodforn)
#     if wsForProd is None:
#         ws_apagar = False
#     if ws_apagar:
#         ws_Qtde = float(reg_mov.mov_qtde)
#         ws_Status = atualiza_saldo(wsForProd.fp_prod,ws_Qtde,wsTipo)
#         if ws_Status:
#             db.session.delete(reg_mov)
#             db.session.commit()
#             flash('"{}" foi apagado com sucesso'.format(reg_mov.mov_id))
#     return redirect(url_for('cad_movimentacao'))

