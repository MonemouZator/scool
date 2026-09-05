
{% extends "login/index.html" %}
{% load static %}

{% block styl_parent %}
<title>Gestion des badges enseignants</title>

<link rel="stylesheet" href="{% static 'base/plugins/fontawesome-free/css/all.min.css' %}">

<style>

/* =========================================================
   STRUCTURE ADMINLTE
========================================================= */

html,
body {
    margin: 0;
    padding: 0;
    height: 100%;
    overflow: hidden;
}

.wrapper {
    height: 100vh;
    overflow: hidden;
}

.content-wrapper {
    min-height: 0 !important;
    height: calc(100vh - 57px) !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
}

/* =========================================================
   PAGE
========================================================= */

.badges-page {
    padding: 20px;
}

/* =========================================================
   EN-TÊTE ÉTABLISSEMENT
========================================================= */

.school-header {
    background: #ffffff;
    border-radius: 10px;
    padding: 15px 20px;
    margin-bottom: 15px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

    display: flex;
    align-items: center;
    gap: 15px;
}

.school-logo {
    width: 65px;
    height: 65px;
    object-fit: contain;
    border-radius: 8px;
    border: 1px solid #ddd;
    padding: 4px;
}

.school-info {
    flex: 1;
}

.school-name {
    font-size: 21px;
    font-weight: 800;
    color: #222;
    text-transform: uppercase;
}

.school-motto {
    font-size: 13px;
    color: #777;
    font-style: italic;
}

/* =========================================================
   BARRE TITRE
========================================================= */

.page-header {
    background: #ffffff;
    border-radius: 10px;
    padding: 15px 20px;
    margin-bottom: 15px;

    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;
}

.page-title {
    margin: 0;
    font-size: 21px;
    font-weight: 700;
    color: #222;
}

.page-subtitle {
    margin: 5px 0 0;
    font-size: 13px;
    color: #777;
}

/* =========================================================
   RECHERCHE
========================================================= */

.search-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 15px 20px;
    margin-bottom: 15px;

    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.search-form {
    display: flex;
    align-items: center;
    gap: 10px;
}

.search-input {
    flex: 1;
    height: 40px;

    border: 1px solid #ced4da;
    border-radius: 6px;

    padding: 0 13px;

    font-size: 14px;
}

.search-input:focus {
    outline: none;
    border-color: #80bdff;
    box-shadow: 0 0 0 0.1rem rgba(0, 123, 255, 0.15);
}

.btn-search {
    height: 40px;

    border: none;
    border-radius: 6px;

    padding: 0 18px;

    background: #007bff;
    color: #ffffff;

    font-weight: 600;

    cursor: pointer;
}

.btn-search:hover {
    background: #0069d9;
}

.btn-reset {
    height: 40px;

    display: inline-flex;
    align-items: center;

    padding: 0 15px;

    border-radius: 6px;

    background: #6c757d;
    color: #ffffff;

    text-decoration: none;

    font-weight: 600;
}

.btn-reset:hover {
    background: #5a6268;
    color: #ffffff;
    text-decoration: none;
}

/* =========================================================
   ACTIONS
========================================================= */

.actions-card {
    background: #ffffff;
    border-radius: 10px;
    padding: 12px 15px;
    margin-bottom: 15px;

    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

    display: flex;
    align-items: center;
    justify-content: space-between;

    gap: 10px;
}

.selection-info {
    font-size: 14px;
    font-weight: 600;
    color: #495057;
}

.selection-count {
    color: #007bff;
    font-weight: 800;
}

.btn-print-selected {
    border: none;

    background: #28a745;
    color: #ffffff;

    padding: 9px 16px;

    border-radius: 6px;

    font-weight: 600;

    cursor: pointer;
}

.btn-print-selected:hover {
    background: #218838;
}

.btn-print-selected:disabled {
    background: #adb5bd;
    cursor: not-allowed;
}

/* =========================================================
   TABLEAU
========================================================= */

.table-card {
    background: #ffffff;

    border-radius: 10px;

    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

    overflow: hidden;
}

.table-container {
    overflow-x: auto;
}

.teachers-table {
    width: 100%;
    min-width: 1050px;

    border-collapse: collapse;
}

.teachers-table thead {
    background: #f4f6f8;
}

.teachers-table th {
    padding: 12px 10px;

    border-bottom: 1px solid #dee2e6;

    font-size: 13px;

    font-weight: 700;

    color: #343a40;

    text-align: left;

    white-space: nowrap;
}

.teachers-table td {
    padding: 10px;

    border-bottom: 1px solid #eeeeee;

    font-size: 13px;

    color: #222222;

    vertical-align: middle;
}

.teachers-table tbody tr:hover {
    background: #f8f9fa;
}

/* =========================================================
   CHECKBOX
========================================================= */

.checkbox-cell {
    width: 45px;
    text-align: center !important;
}

.teacher-checkbox,
#selectAll {
    width: 17px;
    height: 17px;

    cursor: pointer;
}

/* =========================================================
   PHOTO
========================================================= */

.teacher-photo {
    width: 45px;
    height: 55px;

    object-fit: cover;

    border-radius: 5px;

    border: 1px solid #dee2e6;

    background: #f3f4f6;
}

.photo-placeholder {
    width: 45px;
    height: 55px;

    border-radius: 5px;

    border: 1px solid #dee2e6;

    background: #f3f4f6;

    display: flex;
    align-items: center;
    justify-content: center;

    color: #9ca3af;

    font-size: 20px;
}

/* =========================================================
   NOM
========================================================= */

.teacher-name {
    font-weight: 700;

    color: #222;

    white-space: nowrap;
}

.teacher-specialite {
    color: #555;

    font-weight: 600;
}

/* =========================================================
   SEXE
========================================================= */

.sex-badge {
    display: inline-block;

    padding: 4px 8px;

    border-radius: 20px;

    background: #f1f3f5;

    color: #495057;

    font-size: 11px;

    font-weight: 700;
}

/* =========================================================
   ACTION
========================================================= */

.btn-badge {
    display: inline-flex;

    align-items: center;

    gap: 5px;

    padding: 7px 11px;

    border-radius: 5px;

    background: #007bff;

    color: #ffffff;

    text-decoration: none;

    font-size: 12px;

    font-weight: 600;
}

.btn-badge:hover {
    background: #0069d9;

    color: #ffffff;

    text-decoration: none;
}

/* =========================================================
   AUCUN ENSEIGNANT
========================================================= */

.empty-state {
    padding: 45px 20px;

    text-align: center;

    color: #6c757d;
}

.empty-state i {
    font-size: 40px;

    margin-bottom: 10px;

    color: #adb5bd;
}

.empty-state h5 {
    margin: 5px 0;

    font-weight: 700;
}

.empty-state p {
    margin: 0;

    font-size: 13px;
}

/* =========================================================
   RESPONSIVE
========================================================= */

@media screen and (max-width: 768px) {

    .badges-page {
        padding: 10px;
    }

    .school-header {
        padding: 12px;
    }

    .school-logo {
        width: 50px;
        height: 50px;
    }

    .school-name {
        font-size: 17px;
    }

    .page-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .search-form {
        flex-direction: column;
        align-items: stretch;
    }

    .btn-search,
    .btn-reset {
        justify-content: center;
    }

    .actions-card {
        flex-direction: column;
        align-items: stretch;
    }

    .btn-print-selected {
        width: 100%;
    }
}

</style>
{% endblock styl_parent %}


{% block body %}

<div class="badges-page">

    <!-- =====================================================
         ÉTABLISSEMENT
    ====================================================== -->

    <div class="school-header">

        {% if etablissement and etablissement.logo %}

            <img
                src="{{ etablissement.logo.url }}"
                alt="Logo de l'établissement"
                class="school-logo"
            >

        {% else %}

            <div class="school-logo d-flex align-items-center justify-content-center">
                <i class="fas fa-school text-muted"></i>
            </div>

        {% endif %}


        <div class="school-info">

            <div class="school-name">

                {% if etablissement %}
                    {{ etablissement.nom }}
                {% else %}
                    ÉTABLISSEMENT SCOLAIRE
                {% endif %}

            </div>

            {% if etablissement and etablissement.devise %}

                <div class="school-motto">
                    {{ etablissement.devise }}
                </div>

            {% endif %}

        </div>

    </div>


    <!-- =====================================================
         TITRE
    ====================================================== -->

    <div class="page-header">

        <div>

            <h3 class="page-title">
                <i class="fas fa-id-card mr-2"></i>
                Gestion des badges enseignants
            </h3>

            <p class="page-subtitle">
                Recherchez un enseignant et sélectionnez les badges à imprimer.
            </p>

        </div>

    </div>


    <!-- =====================================================
         RECHERCHE
    ====================================================== -->

    <div class="search-card">

        <form
            method="GET"
            action=""
            class="search-form"
        >

            <input
                type="text"
                name="recherche"
                value="{{ recherche }}"
                class="search-input"
                placeholder="Rechercher par nom, prénom, spécialité, téléphone ou email..."
                autocomplete="off"
            >

            <button
                type="submit"
                class="btn-search"
            >
                <i class="fas fa-search mr-1"></i>
                Rechercher
            </button>

            {% if recherche %}

                <a
                    href="{% url 'gestion_badges_enseignants' %}"
                    class="btn-reset"
                >
                    <i class="fas fa-times mr-1"></i>
                    Réinitialiser
                </a>

            {% endif %}

        </form>

    </div>


    <!-- =====================================================
         ACTIONS DE SÉLECTION
    ====================================================== -->

    <div class="actions-card">

        <div class="selection-info">

            <i class="fas fa-check-square mr-1"></i>

            <span id="selectedCount" class="selection-count">
                0
            </span>

            enseignant(s) sélectionné(s)

        </div>


        <form
            method="POST"
            action="{% url 'badges_enseignants_impression' %}"
            id="badgeForm"
        >

            {% csrf_token %}

            <button
                type="submit"
                class="btn-print-selected"
                id="printSelectedBtn"
                disabled
            >
                <i class="fas fa-print mr-1"></i>
                Imprimer les badges sélectionnés
            </button>

        </form>

    </div>


    <!-- =====================================================
         TABLEAU
    ====================================================== -->

    <div class="table-card">

        <div class="table-container">

            {% if enseignants %}

                <table class="teachers-table">

                    <thead>

                        <tr>

                            <th class="checkbox-cell">

                                <input
                                    type="checkbox"
                                    id="selectAll"
                                    title="Sélectionner tout"
                                >

                            </th>

                            <th>
                                Photo
                            </th>

                            <th>
                                Nom & Prénom
                            </th>

                            <th>
                                Spécialité
                            </th>

                            <th>
                                Téléphone
                            </th>

                            <th>
                                Email
                            </th>

                            <th>
                                Sexe
                            </th>

                            <th>
                                Action
                            </th>

                        </tr>

                    </thead>


                    <tbody>

                        {% for enseignant in enseignants %}

                            <tr>

                                <!-- Sélection -->

                                <td class="checkbox-cell">

                                    <input
                                        type="checkbox"
                                        name="enseignants"
                                        value="{{ enseignant.id }}"
                                        class="teacher-checkbox"
                                        form="badgeForm"
                                    >

                                </td>


                                <!-- Photo -->

                                <td>

                                    {% if enseignant.photo %}

                                        <img
                                            src="{{ enseignant.photo.url }}"
                                            alt="{{ enseignant.nom }} {{ enseignant.prenom }}"
                                            class="teacher-photo"
                                        >

                                    {% else %}

                                        <div class="photo-placeholder">
                                            <i class="fas fa-user"></i>
                                        </div>

                                    {% endif %}

                                </td>


                                <!-- Nom -->

                                <td>

                                    <div class="teacher-name">

                                        {{ enseignant.nom }}
                                        {{ enseignant.prenom }}

                                    </div>

                                </td>


                                <!-- Spécialité -->

                                <td>

                                    <span class="teacher-specialite">

                                        {{ enseignant.specialite|default:"Non renseignée" }}

                                    </span>

                                </td>


                                <!-- Téléphone -->

                                <td>

                                    {{ enseignant.telephone|default:"Non renseigné" }}

                                </td>


                                <!-- Email -->

                                <td>

                                    {{ enseignant.email|default:"Non renseigné" }}

                                </td>


                                <!-- Sexe -->

                                <td>

                                    <span class="sex-badge">

                                        {{ enseignant.sexe|default:"Non renseigné" }}

                                    </span>

                                </td>


                                <!-- Action -->

                                <td>

                                    <a
                                        href="{% url 'badge_enseignant' enseignant.id %}"
                                        class="btn-badge"
                                        target="_blank"
                                    >
                                        <i class="fas fa-id-card"></i>
                                        Voir le badge
                                    </a>

                                </td>

                            </tr>

                        {% endfor %}

                    </tbody>

                </table>

            {% else %}

                <div class="empty-state">

                    <i class="fas fa-user-slash"></i>

                    <h5>
                        Aucun enseignant trouvé
                    </h5>

                    <p>
                        {% if recherche %}
                            Aucun résultat pour « {{ recherche }} ».
                        {% else %}
                            Aucun enseignant n'est actuellement enregistré.
                        {% endif %}
                    </p>

                </div>

            {% endif %}

        </div>

    </div>

</div>

{% endblock body %}


{% block contenu %}
{% endblock contenu %}


{% block scripte %}

<script>

document.addEventListener('DOMContentLoaded', function () {

    const selectAll = document.getElementById('selectAll');

    const checkboxes = document.querySelectorAll(
        '.teacher-checkbox'
    );

    const selectedCount = document.getElementById(
        'selectedCount'
    );

    const printSelectedBtn = document.getElementById(
        'printSelectedBtn'
    );

    /*
     * Mise à jour du compteur
     */

    function updateSelection() {

        const selected = document.querySelectorAll(
            '.teacher-checkbox:checked'
        );

        const count = selected.length;

        selectedCount.textContent = count;

        printSelectedBtn.disabled = count === 0;

        /*
         * Gestion de la case "Tout sélectionner"
         */

        if (selectAll) {

            selectAll.checked =
                checkboxes.length > 0 &&
                count === checkboxes.length;

            selectAll.indeterminate =
                count > 0 &&
                count < checkboxes.length;
        }
    }


    /*
     * Sélectionner / désélectionner tout
     */

    if (selectAll) {

        selectAll.addEventListener(
            'change',
            function () {

                checkboxes.forEach(
                    function (checkbox) {

                        checkbox.checked =
                            selectAll.checked;

                    }
                );

                updateSelection();

            }
        );
    }


    /*
     * Changement d'une sélection
     */

    checkboxes.forEach(
        function (checkbox) {

            checkbox.addEventListener(
                'change',
                updateSelection
            );

        }
    );


    /*
     * Confirmation avant impression
     */

    const badgeForm = document.getElementById(
        'badgeForm'
    );

    if (badgeForm) {

        badgeForm.addEventListener(
            'submit',
            function (event) {

                const selected =
                    document.querySelectorAll(
                        '.teacher-checkbox:checked'
                    );

                if (selected.length === 0) {

                    event.preventDefault();

                    alert(
                        'Veuillez sélectionner au moins un enseignant.'
                    );

                    return;
                }

                const confirmation = confirm(
                    'Voulez-vous imprimer les badges de ' +
                    selected.length +
                    ' enseignant(s) sélectionné(s) ?'
                );

                if (!confirmation) {

                    event.preventDefault();

                }

            }
        );

    }


    /*
     * Initialisation
     */

    updateSelection();

});

</script>

{% endblock scripte %}

