function jumpTo(anchor) {
	document.getElementById(anchor).scrollIntoView();
}

/* Home page */

function addCoev() {
    document.getElementById("add-coev-form").style.display = "block";
    document.getElementById("add-curso-form").style.display = "none";
    document.getElementById("add-coev-btn").classList.add("active");
    document.getElementById("add-curso-btn").classList.remove("active");
}

function addCurso() {
    document.getElementById("add-coev-form").style.display = "none";
    document.getElementById("add-curso-form").style.display = "block";
    document.getElementById("add-coev-btn").classList.remove("active");
    document.getElementById("add-curso-btn").classList.add("active");
}

function cancelAdd() {
    document.getElementById("add-coev-form").style.display = "none";
    document.getElementById("add-curso-form").style.display = "none";
    document.getElementById("add-coev-btn").classList.remove("active");
    document.getElementById("add-curso-btn").classList.remove("active");
}

/* Perfil */

function changePass(coursesLength) {
    document.getElementById("cambiar-contrasena").style.display = "block";
    for (let i = 0; i < coursesLength; i++) {
        document.getElementById("notas-resumen-"+i.toString()).style.display = "none";
        document.getElementById("row-btn-"+i.toString()).classList.remove("active");
    }

    document.getElementById("notas-placeholder").style.display = "none";
    document.getElementById("change-pass-btn").classList.add("active");
}

function showGrades(courseIndex, coursesLength) {
    if (document.getElementById("cambiar-contrasena")) {
        document.getElementById("cambiar-contrasena").style.display = "none";
    }
    document.getElementById("notas-placeholder").style.display = "none";

    for (let i = 0; i < coursesLength; i++) {
        document.getElementById("notas-resumen-"+i.toString()).style.display = "none";
        document.getElementById("row-btn-" + i.toString()).classList.remove("active");
    }

    document.getElementById("notas-resumen-"+courseIndex.toString()).style.display = "block";
    document.getElementById("row-btn-" + courseIndex.toString()).classList.add("active");
    let changePass = document.getElementById("change-pass-btn");
    if (changePass !== null) changePass.classList.remove("active");
}


function cancelPass(coursesLength) {
    document.getElementById("cambiar-contrasena").style.display = "none";
     for (let i = 0; i < coursesLength; i++) {
        document.getElementById("notas-resumen-"+i.toString()).style.display = "none";
        document.getElementById("row-btn-" + i.toString()).classList.remove("active");
    }
    document.getElementById("change-pass-btn").classList.add("active");
    document.getElementById("notas-placeholder").style.display = "block";
}

/* Gestión Curso */

function showGestionEstudiante() {
    document.getElementById("gestion-grupo").style.display = "none";
    document.getElementById("gestion-estudiante").style.display = "block";
    document.getElementById("gestion-placeholder").style.display = "none";
    document.getElementById("active-estudiante").classList.add("active");
    document.getElementById("active-grupo").classList.remove("active");
}

function showGestionGrupo() {
    document.getElementById("gestion-grupo").style.display = "block";
    document.getElementById("gestion-estudiante").style.display = "none";
    document.getElementById("gestion-placeholder").style.display = "none";
    document.getElementById("active-grupo").classList.add("active");
    document.getElementById("active-estudiante").classList.remove("active");
}

jQuery(document).ready(function($) {
    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
    });
});