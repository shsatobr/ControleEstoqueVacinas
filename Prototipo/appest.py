import os
import sqlite3
from datetime import datetime
from decimal import Decimal
from email.policy import default

from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   url_for)
from flask.typing import TemplateFilterCallable
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.orm import backref
from werkzeug.datastructures import ContentRange
from werkzeug.exceptions import MethodNotAllowed, abort
from flask_cors import CORS

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'JcCwEUu3ZLzQc96'
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False        # Retira aviso de "adds significant overhead"
db = SQLAlchemy(app)
ma = Marshmallow(app)
cors=CORS(app, resources={r"/*":{"origins":"*"}})


# Definicao das tabelas do banco de dados
class Ubs(db.Model):   # Nome da tabela e campos conforme banco de dados
    ubs_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ubs_nome = db.Column(db.String(50), nullable=False)
    ubs_endereco = db.Column(db.String(50))
    ubs_numero = db.Column(db.String(20))
    ubs_bairro = db.Column(db.String(35))
    ubs_telefone = db.Column(db.String(11))
    ubs_responsavel = db.Column(db.String(50))
    ubs_users = db.relationship('User', backref='user') #Nome da Classe e campo virtual
    ubs_req_origem = db.relationship('Requisicoes',foreign_keys="Requisicoes.req_UBS_orig", backref='req_origem') #Nome da Classe e campo virtual
    ubs_req_dest = db.relationship('Requisicoes',foreign_keys="Requisicoes.req_UBS_dest", backref='req_dest') #Nome da Classe e campo virtual
    ubs_mov = db.relationship('Movimentacoes', backref='mov_ubs') #Nome da Classe e campo virtual
    ubs_lts = db.relationship('Lotes', backref='lotes') #Nome da Classe e campo virtual
    ubs_loc = db.relationship('Localiza_vacinas', backref='local_ubs') #Nome da Classe e campo virtual

class User(db.Model):
    usr_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usr_nome = db.Column(db.String(50), nullable=False)
    usr_ubs = db.Column(db.Integer, db.ForeignKey(Ubs.ubs_id))
    
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
    vcn_lotes = db.relationship('Lotes', backref='lote') #Nome da Classe e campo virtual
    vcn_req = db.relationship('Requisicoes', backref='req') #Nome da Classe e campo virtual
    vcn_mov = db.relationship('Movimentacoes', backref='mov_vcn') #Nome da Classe e campo virtual
    vcn_loc = db.relationship('Localiza_vacinas', backref='local_vcn') #Nome da Classe e campo virtual

class Lotes(db.Model):   # Nome da tabela e campos conforme banco de dados
    lts_lote = db.Column(db.Integer, primary_key=True)
    lts_vacina = db.Column(db.Integer, db.ForeignKey(Vacinas.vcn_id), nullable=False)
    lts_val_vacina = db.Column(db.Date, default=datetime.now())
    lts_nota_fiscal = db.Column(db.Integer)
    lts_dt_recebimento = db.Column(db.DateTime, default=datetime.now())
    lts_qtde_rec = db.Column(db.Numeric)
    lts_campanha = db.Column(db.String(50))
    lts_ubs = db.Column(db.Integer, db.ForeignKey(Ubs.ubs_id))
    lts_mov = db.relationship('Movimentacoes', backref='lotes_mov') #Nome da Classe e campo virtual
    lts_loc = db.relationship('Localiza_vacinas', backref='lotes_loc') #Nome da Classe e campo virtual

class Requisicoes(db.Model):   # Nome da tabela e campos conforme banco de dados
    req_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    req_vacina = db.Column(db.Integer,db.ForeignKey(Vacinas.vcn_id), nullable=False)
    req_UBS_orig = db.Column(db.Integer, db.ForeignKey(Ubs.ubs_id))
    req_UBS_dest = db.Column(db.Integer, db.ForeignKey(Ubs.ubs_id))
    req_qtde = db.Column(db.Numeric)
    req_responsavel = db.Column(db.String(50))
    req_dt_solic = db.Column(db.DateTime, default=datetime.now())
    req_atendida = db.Column(db.Numeric)
    req_lote = db.Column(db.Integer)
  
class Movimentacoes(db.Model):   # Nome da tabela e campos conforme banco de dados
    mov_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mov_vacina = db.Column(db.Integer,db.ForeignKey(Vacinas.vcn_id), nullable=False)
    mov_requisicao = db.Column(db.Integer)
    mov_UBS_orig = db.Column(db.Integer, db.ForeignKey(Ubs.ubs_id))
    mov_UBS_dest = db.Column(db.Integer)
    mov_motivo = db.Column(db.String(50))
    mov_qtde = db.Column(db.Numeric)
    mov_dt_mov = db.Column(db.DateTime)
    mov_lote = db.Column(db.Integer, db.ForeignKey(Lotes.lts_lote))

class Localiza_vacinas(db.Model):   # Nome da tabela e campos conforme banco de dados
    loc_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    loc_vcn = db.Column(db.Integer,db.ForeignKey(Vacinas.vcn_id), nullable=False)
    loc_ubs = db.Column(db.Integer, db.ForeignKey(Ubs.ubs_id))
    loc_lote = db.Column(db.Integer, db.ForeignKey(Lotes.lts_lote))
    loc_qtde = db.Column(db.Numeric)
    loc_qtde_usada = db.Column(db.Numeric)
    loc_qtde_reserva = db.Column(db.Numeric)
  
# Marshmallow
class UbsSchema(ma.Schema):
    class Meta:
        fields = ("ubs_id","ubs_nome","ubs_endereco","ubs_numero","ubs_bairro","ubs_telefone","ubs_responsavel")
        model = Ubs
ubs_schema = UbsSchema()
ubss_schema = UbsSchema(many=True)

# Rotinas de CRUD (Gets)
def get_post_ubs(id):
    reg_ubs = Ubs.query.filter_by(ubs_id=id).first()
    if reg_ubs is None:
        flash('UBS não cadastrada')
    return reg_ubs

def get_post_user(id):
    reg_user = User.query.filter_by(usr_id=id).first()
    if reg_user is None:
        flash('Usuário não cadastrado')
    return reg_user

def get_post_vcn(id):
    reg_vcn = Vacinas.query.filter_by(vcn_id=id).first()
    if reg_vcn is None:
        flash('Vacina não cadastrada')
    return reg_vcn

def get_post_lts(id):
    reg_lts = Lotes.query.filter_by(lts_lote=id).first()
    if reg_lts is None:
        flash('Lote não cadastrado')
    return reg_lts

def get_post_req(id):
    reg_req = Requisicoes.query.filter_by(req_id=id).first()
    if reg_req is None:
        flash('Requisição não cadastrada')
    return reg_req

def get_post_mov(id):
    reg_mov = Movimentacoes.query.filter_by(req_mov=id).first()
    if reg_mov is None:
        flash('Movimento não cadastrado')
    return reg_mov

def get_post_loc(lote, ubs):
    reg_loc = Localiza_vacinas.query.filter_by(loc_lote = lote, loc_ubs = ubs).first()
    if reg_loc is None:
        flash('Localização não cadastrada')
    return reg_loc

# Funções auxiliares
def calcula_saldo_loc(ws_loc_qtde,ws_loc_qtde_usada,ws_loc_qtde_reserva,ws_loc_qtde_ant,ws_loc_qtde_rec):
    ws_saldo = ws_loc_qtde - ws_loc_qtde_usada - ws_loc_qtde_reserva - ws_loc_qtde_ant + ws_loc_qtde_rec
    return ws_saldo

# Rotinas da API
# UBS
@app.route('/api/ubs/<int:id>', methods=['GET'])
def apiubs(id):
    reg_ubs = Ubs.query.filter_by(ubs_id=id).first()
    if reg_ubs is None:
        return jsonify({'mensagem':'UBS não cadastrada'})
    return ubs_schema.dump(reg_ubs)

@app.route('/api/ubs/', methods=['GET'])
def apiubss():
    reg_ubss = Ubs.query.all()
    if reg_ubss is None:
        return jsonify({'mensagem':'UBS não cadastrada'})
    return ubss_schema.jsonify(reg_ubss),200
    # return ubss_schema.dump(reg_ubss)

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
    lista_reqs = Requisicoes.query.all()
    return render_template('movimentacao/requisicoes.html', lista_reqs=lista_reqs)

@app.route('/mnumov/movimentacoes', methods=('GET', 'POST'))
def cad_mov():
    lista_mov = Movimentacoes.query.all()
    return render_template('movimentacao/mov_vac.html', lista_movs=lista_mov)

@app.route('/mnurel/localizacoes', methods=('GET', 'POST'))
def rel_loc():
    lista_locs = Localiza_vacinas.query.all()
    return render_template('relatorios/loc_vac.html', lista_locs=lista_locs)

# UBS
@app.route('/mnucadastro/lst_ubs', methods=('GET', 'POST'))   # Nao esquecer de colocar os metodos aceitos
def lst_ubs():
    if request.method == 'POST':
        dado = request.form['form_nome']                    # Nomes so sao reconhecidos se estiverem dentro form
        lista_ubs = Ubs.query.filter(Ubs.ubs_nome.like("%" + dado + "%")) # filter_by somente um linha de retorno
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
        ws_nome = request.form['form_nome']   
        ws_ubs = request.form['form_ubs']     
        ws_query = ""   
        if (ws_nome):
            ws_query = "usr_nome like '%" + ws_nome + "%'"         # Nomes so sao reconhecidos se estiverem dentro form 
        if (ws_ubs):
            if (ws_query == ""):
                ws_query = "usr_ubs = " + ws_ubs
            else:
                ws_query = ws_query + "and usr_ubs = " + ws_ubs
        # lista_usr = User.query.filter(User.usr_nome.like("%" + ws_nome + "%")) # filter_by somente um linha de retorno
        lista_usr = User.query.filter(text(ws_query))
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
        lista_vcn = Vacinas.query.filter(Vacinas.vcn_nome.like("%" + dado + "%")) # filter_by somente um linha de retorno
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
        ws_lote = request.form['form_lote']                    # Nomes so sao reconhecidos se estiverem dentro form
        ws_vacina = request.form['form_vacina']
        ws_ubs = request.form['form_ubs']
        ws_query = ""
        if (ws_lote):
            ws_query = "lts_lote = " + ws_lote
        if (ws_vacina):
            if (ws_query == ""):
                ws_query = "lts_vacina = " + ws_vacina
            else:
                ws_query = ws_query + " and lts_vacina = " + ws_vacina
        if (ws_ubs):
            if (ws_query == ""):
                ws_query = "lts_ubs = " + ws_ubs
            else:
                ws_query = ws_query + " and lts_ubs = " + ws_ubs
        lista_lts = Lotes.query.filter(text(ws_query)) # filter_by somente um linha de retorno
        if (lista_lts):
            return render_template('movimentacao/lotes.html',lista_lotes=lista_lts)
        else:
            return render_template('movimentacao/lotes.html')
    else:
        return render_template('movimentacao/lst_lotes.html')
    
@app.route('/mnucadastro/<int:id>/lts_alt', methods=('GET','POST'))    # obrigatório ter o parametro no endereco
def alt_lts(id):
    reg_lts = get_post_lts(id)
    lista_ubs = Ubs.query.all()           # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
    if request.method == 'POST':
        erro = False
        ws_qtde_ant = float(reg_lts.lts_qtde_rec)
        ws_vacina = request.form['form_vacina']
        ws_val_vacina = datetime.strptime(request.form['form_val_vacina'],"%Y-%m-%d")
        ws_nota_fiscal = request.form['form_nota_fiscal']
        ws_dt_recebimento = datetime.strptime(request.form['form_dt_recebimento'],"%Y-%m-%d")
        ws_qtde_rec = float(request.form['form_qtde_rec'])
        ws_campanha = request.form['form_campanha']
        ws_reg_vcn = get_post_vcn(ws_vacina)
        reg_loc = get_post_loc(reg_lts.lts_lote, reg_lts.lts_ubs)
        ws_ubs = reg_lts.lts_ubs
        ws_saldo = float(reg_loc.loc_qtde) - float(reg_loc.loc_qtde_usada) - float(reg_loc.loc_qtde_reserva) - ws_qtde_ant + ws_qtde_rec
        if (ws_saldo < 0):
            flash("Impossível alterar essa quantidade. Saldo disponível ficaria negativo")
            erro = True
        if not ws_vacina:
            flash('Vacina é obrigatório','error')
            erro = True
        if (not ws_reg_vcn):
            erro = True
        if (not reg_loc):
            erro = True
        if (ws_val_vacina < ws_dt_recebimento):
            flash('Data de validade menor que a data de recebimento')
            erro = True
        if (ws_val_vacina < datetime.today()):
            flash('Data de validade menor ou igual a data de hoje')
            erro = True
        if (not erro):
            reg_lts.lts_vacina = ws_vacina
            reg_lts.lts_val_vacina = ws_val_vacina
            reg_lts.lts_nota_fiscal = ws_nota_fiscal
            reg_lts.lts_dt_recebimento = ws_dt_recebimento
            reg_lts.lts_qtde_rec = ws_qtde_rec
            reg_lts.lts_campanha= ws_campanha
            reg_lts.lts_ubs = ws_ubs
            reg_loc.loc_qtde = ws_qtde_rec
            db.session.commit()
            flash('Registro alterado')
            return redirect(url_for('cad_lts'))
    return render_template('movimentacao/alt_lotes.html', reg_lts=reg_lts, lista_ubs=lista_ubs)

@app.route('/mnucadastro/lts_inc', methods=('GET', 'POST'))
def inc_lts():    
    lista_ubs = Ubs.query.all()           # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
    if request.method == 'POST':
        erro = False
        ws_lote = request.form['form_lote']
        ws_vacina = request.form['form_vacina']
        ws_val_vacina = datetime.strptime(request.form['form_val_vacina'],"%Y-%m-%d")
        ws_nota_fiscal = request.form['form_nota_fiscal']
        ws_dt_recebimento = datetime.strptime(request.form['form_dt_recebimento'],"%Y-%m-%d")
        ws_qtde_rec = request.form['form_qtde_rec']
        ws_campanha = request.form['form_campanha']
        ws_ubs = request.form['form_ubs']
        ws_reg_vcn = get_post_vcn(ws_vacina)
        if not ws_vacina:
            flash('O código da vacina é obrigatório') 
            erro = True
        if (ws_val_vacina < ws_dt_recebimento):
            flash("Data de validade menor que a data de recebimento") # Checar se o vencimento é menor ou igual a data atual
            erro = True
        if (ws_val_vacina < datetime.today()):
            flash("Data de validade menor ou igual a data de hoje")
            erro = True
        if ( not ws_reg_vcn):
            erro = True
        if ( not erro):
            reg_lts = Lotes(lts_lote=ws_lote,
                            lts_vacina=ws_vacina,
                            lts_val_vacina=ws_val_vacina,
                            lts_nota_fiscal=ws_nota_fiscal,
                            lts_dt_recebimento=ws_dt_recebimento,
                            lts_qtde_rec=ws_qtde_rec,
                            lts_campanha=ws_campanha,
                            lts_ubs = ws_ubs)
            reg_loc = Localiza_vacinas(loc_vcn = ws_vacina,
                                       loc_ubs = ws_ubs,
                                       loc_lote = ws_lote,
                                       loc_qtde = ws_qtde_rec,
                                       loc_qtde_usada = 0,
                                       loc_qtde_reserva = 0)
            db.session.add(reg_lts)
            db.session.add(reg_loc)
            db.session.commit()
            flash('Inclusao feita com sucesso')
            return redirect(url_for('cad_lts'))
    return render_template('movimentacao/inc_lotes.html', lista_ubs=lista_ubs)

@app.route('/mnucadastro/<int:lote>/<int:ubs>/lts_del', methods=('GET', 'POST'))
def del_lts(lote, ubs):
    reg_lts = get_post_lts(lote)
    reg_loc = get_post_loc(lote, ubs)
    if (reg_loc.loc_qtde_usada or reg_loc.loc_qtde_reserva):
        flash('Lote com movimento, não é possível excluir')
    else:
        db.session.delete(reg_lts)
        db.session.delete(reg_loc)
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
        ws_qtde_ant = float(reg_req.req_qtde)
        ws_lote_ant = reg_req.req_lote
        ws_ubs_ant = reg_req.req_UBS_orig
        ws_id = request.form['form_id']
        ws_dt_solic = datetime.strptime(request.form['form_dt_solic'],"%Y-%m-%d")
        ws_vacina = request.form['form_vacina']
        ws_lote = request.form['form_lote']
        ws_reg_vcn = get_post_vcn(ws_vacina)
        ws_ubs_orig = request.form['form_ubs_orig']
        ws_ubs_dest = request.form['form_ubs_dest']
        ws_qtde = float(request.form['form_qtde'])
        ws_responsavel = request.form['form_responsavel']
        if (ws_ubs_ant == ws_ubs_orig):
            reg_loco = Localiza_vacinas.query.filter_by(loc_ubs=ws_ubs_orig, loc_lote = ws_lote).first()
            ws_disponivel = float(reg_loco.loc_qtde) - float(reg_loco.loc_qtde_usada) - float(reg_loco.loc_qtde_reserva) + ws_qtde_ant - ws_qtde
            reg_loco.loc_qtde_reserva = ws_qtde # Verificar <-----------------------------
        else:
            reg_loco = Localiza_vacinas.query.filter_by(loc_ubs=ws_ubs_ant, loc_lote = ws_lote).first()
            reg_loco_new = Localiza_vacinas.query.filter_by(loc_ubs=ws_ubs_orig, loc_lote = ws_lote).first()
            ws_disponivel = float(reg_loco_new.loc_qtde) - float(reg_loco_new.loc_qtde_usada) - float(reg_loco_new.loc_qtde_reserva) - ws_qtde
        if (ws_disponivel < 0):
            flash("Saldo insuficiente")
            erro = True
        if not ws_vacina:
            flash('Vacina é obrigatório','error')
            erro = True
        if (ws_ubs_dest == ws_ubs_orig):
            flash("UBS de origem e destino devem ser diferentes")
            erro = True
        if (not ws_reg_vcn):
            erro = True
        if (not reg_loco):
            erro = True
            flash("Localização não encontrada")
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
    erro = False
    if request.method == 'POST':
        ws_dt_solic = datetime.now()
        ws_ubs_orig = request.form['form_ubs_orig']
        ws_ubs_dest = request.form['form_ubs_dest']
        ws_qtde = request.form['form_qtde']
        ws_responsavel = request.form['form_responsavel']
        ws_lote = request.form['form_lote']
        ws_reg_lts = get_post_lts(ws_lote)
        ws_reg_loco = Localiza_vacinas.query.filter_by(loc_ubs=ws_ubs_orig, loc_lote = ws_lote).first()

        # if not ws_vacina:
        #     flash('O código da vacina é obrigatório')
        #     erro = True
        if (ws_ubs_orig == ws_ubs_dest):
            flash('As UBS de origem e destino devem ser diferentes')
            erro = True
        if (not ws_reg_lts):
            erro = True
        else:
            ws_vacina = ws_reg_lts.lts_vacina
            ws_reg_vcn = get_post_vcn(ws_vacina)
            if (not ws_reg_vcn):
                erro = True
        if (not ws_reg_loco):
            flash('Não existe esse lote na UBS de origem')
            erro = True
        else:
            ws_new_qtde_reserva = float(ws_reg_loco.loc_qtde_reserva) + float(ws_qtde)
            ws_loc_qtde = float(ws_reg_loco.loc_qtde)
            ws_loc_qtde_usada = float(ws_reg_loco.loc_qtde_usada)
            ws_disponivel = ws_loc_qtde - ws_loc_qtde_usada - ws_new_qtde_reserva
            if (ws_disponivel < 0):
                erro = True
                flash("Quantidade solicitada maior que saldo disponível")
            else:
                ws_reg_loco.loc_qtde_reserva = ws_new_qtde_reserva
        if (not erro ):
            reg_req = Requisicoes(req_dt_solic = ws_dt_solic,
                            req_vacina=ws_vacina,
                            req_UBS_orig=ws_ubs_orig,
                            req_UBS_dest=ws_ubs_dest,
                            req_qtde=ws_qtde,
                            req_lote = ws_lote,
                            req_responsavel=ws_responsavel,
                            req_atendida = 0)

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
        ws_lote = request.form['form_lote']                    # Nomes so sao reconhecidos se estiverem dentro form
        ws_vacina = request.form['form_vacina']
        ws_ubs_origem = request.form['form_ubs_orig']
        ws_ubs_dest = request.form['form_ubs_dest']
        ws_query = ""
        if (ws_lote):
            ws_query = "mov_lote = " + ws_lote
        if (ws_vacina):
            if (ws_query == ""):
                ws_query = "mov_vacina = " + ws_vacina
            else:
                ws_query = ws_query + " and mov_vacina = " + ws_vacina
        if (ws_ubs_origem):
            if (ws_query == ""):
                ws_query = "mov_UBS_orig = " + ws_ubs_origem
            else:
                ws_query = ws_query + " and mov_UBS_orig = "  + ws_ubs_origem
        if (ws_ubs_dest):
            if (ws_query == ""):
                ws_query = "mov_UBS_dest = " + ws_ubs_dest
            else:
                ws_query = ws_query + " and mov_UBS_dest = " + ws_ubs_dest
        lista_mov = Movimentacoes.query.filter(text(ws_query)) # filter_by somente um linha de retorno
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
        erro = False
        ws_id = request.form['form_id']
        ws_vacina = request.form['form_vacina']
        ws_reg_vcn = get_post_vcn(ws_vacina)
        ws_requisicao = request.form['form_requisicao']
        ws_ubs_orig = request.form['form_ubs_orig']
        ws_ubs_dest = request.form['form_ubs_dest']
        ws_motivo = request.form['form_motivo']
        ws_qtde = request.form['form_qtde']
        ws_lote = int(request.form['form_lote'])
        ws_reg_lts = get_post_lts(ws_lote)
        # ws_dt_mov = request.form['form_dt_mov']
        if not ws_vacina:
            flash('Vacina é obrigatório','error')
            erro = True
        if (not ws_reg_vcn):
            erro = True
        if (not ws_reg_lts):
            erro = True
        if (not erro):
            reg_mov.mov_id = ws_id
            # reg_mov.req_dt_solic = ws_dt_solic
            reg_mov.mov_vacina = ws_vacina
            reg_mov.mov_UBS_orig = ws_ubs_orig
            reg_mov.mov_UBS_dest = ws_ubs_dest
            reg_mov.mov_qtde = ws_qtde
            reg_mov.mov_requisicao = ws_requisicao
            reg_mov.mov_motivo = ws_motivo
            reg_mov.mov_lote = ws_lote
            db.session.commit()
            flash('Registro alterado')
            return redirect(url_for('cad_mov'))
    return render_template('movimentacao/alt_mov_vac.html', reg_mov=reg_mov, lista_ubs=lista_ubs)

@app.route('/mnumov/mov_inc', methods=('GET', 'POST'))
def inc_mov():                # Nome de funcao NUNCA PODE SER IGUAL AO NOME DA TABELA
    lista_ubs = Ubs.query.all()
    if request.method == 'POST':
        erro = False
        ws_motivo = request.form['form_motivo']
        ws_dt_mov = datetime.now()
        ws_lote = request.form['form_lote']
        ws_ubs_orig = request.form['form_ubs_orig']
        if (ws_motivo == "1"):
            ws_ubs_dest = request.form['form_ubs_dest']
            ws_requisicao = request.form['form_requisicao']
            ws_reg_locd = Localiza_vacinas.query.filter_by(loc_ubs=ws_ubs_dest, loc_lote = ws_lote).first()
            ws_reg_req = get_post_req(ws_requisicao)
            if (ws_ubs_orig == ws_ubs_dest):
                flash('As UBS de origem e destino devem ser diferentes')
                erro = True
            if (not ws_reg_req):
                erro = True
        else:
            ws_ubs_dest = 999
            ws_requisicao = 0
            ws_reg_locd = ""
        ws_qtde = float(request.form['form_qtde'])
        ws_reg_lts = get_post_lts(ws_lote)
        ws_reg_loco = Localiza_vacinas.query.filter_by(loc_ubs=ws_ubs_orig, loc_lote = ws_lote).first()
        # if (not ws_reg_vcn):
        #     erro = True
        if (not ws_reg_lts):
            erro = True
        else:
            ws_vacina = ws_reg_lts.lts_vacina
        if (not ws_reg_loco):
            flash('Localização não encontrada')
            erro = True
        else:
            ws_loc_qtde = float(ws_reg_loco.loc_qtde)
            ws_loc_qtde_reserva = float(ws_reg_loco.loc_qtde_reserva)
            ws_loc_qtde_usada = float(ws_reg_loco.loc_qtde_usada)
            ws_loc_qtde_atual = ws_loc_qtde_usada + ws_qtde
            ws_disponivel = ws_loc_qtde - ws_loc_qtde_atual - ws_loc_qtde_reserva
            if (ws_motivo == "1"):
                if (ws_loc_qtde_reserva < ws_qtde):
                    flash('Quantidade maior que a quantidade reservada')
                    erro = True
                else:
                    ws_reg_loco.loc_qtde_reserva = float(ws_reg_loco.loc_qtde_reserva) - ws_qtde
            else:
                if (ws_disponivel < 0):
                    erro = True
                    flash("Quantidade usada maior que o saldo disponivel")
                else:
                    ws_reg_loco.loc_qtde_usada = ws_loc_qtde_atual
        if ( not erro):
            reg_mov = Movimentacoes(mov_dt_mov = ws_dt_mov,
                            mov_vacina=ws_vacina,
                            mov_UBS_orig=ws_ubs_orig,
                            mov_UBS_dest=ws_ubs_dest,
                            mov_qtde=ws_qtde,
                            mov_requisicao=ws_requisicao,
                            mov_motivo=ws_motivo,
                            mov_lote = ws_lote)
            if (ws_motivo == "1"):
                ws_reg_req.req_atendida = float(ws_reg_req.req_atendida) + ws_qtde
                if (not ws_reg_locd):
                    ws_loc_vcn = ws_vacina
                    ws_loc_ubs = ws_ubs_dest
                    ws_loc_lote = ws_lote
                    ws_loc_qtde = ws_qtde
                    reg_loc_dest = Localiza_vacinas(loc_vcn = ws_loc_vcn,
                                                    loc_ubs = ws_loc_ubs,
                                                    loc_lote = ws_loc_lote,
                                                    loc_qtde = ws_loc_qtde,
                                                    loc_qtde_usada = 0,
                                                    loc_qtde_reserva = 0)
                    db.session.add(reg_loc_dest)
                    db.session.commit()
                else:
                    ws_reg_locd.loc_qtde = float(ws_reg_locd.loc_qtde) + ws_qtde
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

# Localização de vacinas
@app.route('/mnurel/lst_loc', methods=('GET', 'POST'))   # Nao esquecer de colocar os metodos aceitos
def lst_loc():
    if request.method == 'POST':
        ws_lote = request.form['form_lote']                    # Nomes so sao reconhecidos se estiverem dentro form
        ws_vacina = request.form['form_vacina']
        ws_ubs = request.form['form_ubs']
        ws_query = ""
        if (ws_lote):
            ws_query = "loc_lote = " + ws_lote
        if (ws_vacina):
            if (ws_query == ""):
                ws_query = "loc_vcn = " + ws_vacina
            else:
                ws_query = ws_query + " and mov_vacina = " + ws_vacina
        if (ws_ubs):
            if (ws_query == ""):
                ws_query = "loc_ubs = " + ws_ubs
            else:
                ws_query = ws_query + " and loc_ubs = "  + ws_ubs
        lista_locs = Localiza_vacinas.query.filter(text(ws_query)) # filter_by somente um linha de retorno
        if (lista_locs):
            return render_template('relatorios/loc_vac.html',lista_locs=lista_locs)
        else:
            return render_template('relatorios/loc_vac.html')
    else:
        return render_template('relatorios/lst_loc_vac.html')
