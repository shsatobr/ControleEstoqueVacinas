let ubsPromise=fetch("http://localhost:5000/api/ubs/");

ubsPromise.then((resp) => {
    resp.json().then((ubs) => {
        console.log(ubs);
    })
});

let div = document.getElementById("teste")
