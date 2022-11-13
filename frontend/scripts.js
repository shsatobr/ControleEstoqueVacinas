let ubsPromise=fetch("http://localhost:5000/api/ubs/");

ubsPromise.then((resp) => {
    resp.json().then((ubss) => {
        console.log(ubss);
        let table = renderTable(ubss);
        document.getElementById("teste").innerHTML = table;
    })
});


function renderTable(ubss) {
    let rows = ubss.map(ubs => {
       return `<tr><td>${ubs.ubs_id}</td><td>${ubs.ubs_nome}</td></tr>`
    });
    return `<table>${rows.join("")}</table>`

}
