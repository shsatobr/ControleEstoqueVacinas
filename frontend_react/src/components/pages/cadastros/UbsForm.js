import Input from '../../form/Input'
// import Select from '../../form/Select'
import SubmitButton from '../../form/SubmitButton'
import styles from './UbsForm.module.css'

function UbsForm({btnText}) {
    return (
        <form className={styles.form}>
            <Input type="text" text="Nome da UBS" name="frm_nome_ubs" placeholder="Insira o nome da UBS" />
            <Input type="text" text="Endereço" name="frm_endereco" placeholder="Insira o endereço da UBS"/>
            <Input type="text" text="Número" name="frm_numero" placeholder="Número"/>
            <Input type="text" text="Bairro" name="frm_bairro" placeholder="Bairro"/>
            <Input type="text" text="Telefone" name="frm_telefone" placeholder="Telefone"/>
            <Input type="text" text="Responsável" name="frm_telefone" placeholder="Nome do responsável"/>
            {/* <Select name="ubs_id" text="Selecione o ID"/>
            <SubmitButton text="Direto"/> */}
            <SubmitButton text={btnText}/>
        </form>
    )
}

export default UbsForm