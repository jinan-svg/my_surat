function pilihTemplateSurat(jenis) {
    const inputJenis = document.getElementById("jenisTemplate");
    const formTugas = document.getElementById("formSuratTugas");
    const formUndangan = document.getElementById("formSuratUndangan");
    const cards = document.querySelectorAll(".template-card");

    inputJenis.value = jenis;

    cards.forEach(function(card) {
        card.classList.remove("active-template");
    });

    if (jenis === "tugas") {
        cards[0].classList.add("active-template");
        formTugas.classList.remove("hidden-template");
        formUndangan.classList.add("hidden-template");
    }

    if (jenis === "undangan") {
        cards[1].classList.add("active-template");
        formUndangan.classList.remove("hidden-template");
        formTugas.classList.add("hidden-template");
    }
}

function pilihDataSurat() {
    const select = document.getElementById("pilihSurat");
    const selected = select.options[select.selectedIndex];

    const nomor = selected.getAttribute("data-nomor") || "";
    const perihal = selected.getAttribute("data-perihal") || "";

    document.getElementById("nomorSurat").value = nomor;
    document.getElementById("perihalSurat").value = perihal;
}
function pilihDataSurat() {

    let select = document.getElementById("pilihSurat");

    let option = select.options[select.selectedIndex];

    let nomor = option.getAttribute("data-nomor");

    let perihal = option.getAttribute("data-perihal");

    document.getElementById("nomorSurat").value = nomor;

    document.getElementById("perihalSurat").value = perihal;
}