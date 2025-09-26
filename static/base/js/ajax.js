// ajax.js - Gestion des requêtes AJAX avec jQuery

$(document).ready(function () {
  // Exemple : soumission AJAX d’un formulaire avec l’ID #frm
  $('#frm').on('submit', function (e) {
    e.preventDefault();

    $.ajax({
      url: $(this).attr('action'),
      type: $(this).attr('method'),
      data: new FormData(this),
      processData: false,
      contentType: false,
      success: function (response) {
        console.log('Succès :', response);
        alert('Enregistré avec succès !');
      },
      error: function (xhr) {
        console.error('Erreur :', xhr.responseText);
        alert("Une erreur s'est produite.");
      }
    });
  });
});
