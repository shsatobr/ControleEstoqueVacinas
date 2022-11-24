from appest import calcula_saldo_loc
def test_calcula_saldo_loc_positivo():
    ws_loc_qtde = 10
    ws_loc_qtde_usada = 5
    ws_loc_qtde_reserva = 1
    ws_loc_qtde_ant = 20
    ws_loc_qtde_rec = 25
    ws_saldo = 9
    ws_saldo_fun = calcula_saldo_loc(ws_loc_qtde, ws_loc_qtde_usada, ws_loc_qtde_reserva, ws_loc_qtde_ant, ws_loc_qtde_rec)
    assert ws_saldo == ws_saldo_fun
def test_calcula_saldo_loc_negativo():
    ws_loc_qtde = 10
    ws_loc_qtde_usada = 5
    ws_loc_qtde_reserva = 1
    ws_loc_qtde_ant = 25
    ws_loc_qtde_rec = 20
    ws_saldo = -1
    ws_saldo_fun = calcula_saldo_loc(ws_loc_qtde, ws_loc_qtde_usada, ws_loc_qtde_reserva, ws_loc_qtde_ant, ws_loc_qtde_rec)
    assert ws_saldo == ws_saldo_fun
def test_calcula_saldo_loc_zerado():
    ws_loc_qtde = 10
    ws_loc_qtde_usada = 5
    ws_loc_qtde_reserva = 1
    ws_loc_qtde_ant = 25
    ws_loc_qtde_rec = 21
    ws_saldo = 0
    ws_saldo_fun = calcula_saldo_loc(ws_loc_qtde, ws_loc_qtde_usada, ws_loc_qtde_reserva, ws_loc_qtde_ant, ws_loc_qtde_rec)
    assert ws_saldo == ws_saldo_fun
def test_calcula_saldo_loc_errado():
    ws_loc_qtde = 10
    ws_loc_qtde_usada = 5
    ws_loc_qtde_reserva = 1
    ws_loc_qtde_ant = 25
    ws_loc_qtde_rec = 21
    ws_saldo = 0
    ws_saldo_fun = calcula_saldo_loc(ws_loc_qtde, ws_loc_qtde_usada, ws_loc_qtde_reserva, ws_loc_qtde_ant, ws_loc_qtde_rec)
    assert ws_saldo == ws_saldo_fun
