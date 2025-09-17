from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [
    # Administration
    path('admin/', admin.site.urls),

    # Routes de l'application personnel
    path('', include('personnel.urls')),  # Route principale
    path('accueil/', include('personnel.urls')),
    path('dashbaord/directeur/', include('personnel.urls')),
    # Routes de l'application enseignant
    path('enseignant/', include('enseignant.urls')),
    path('ajout-enseignant/', include('enseignant.urls')),
    path('modification/', include('enseignant.urls')),
    path('suppression/', include('enseignant.urls')),
    path('detail-enseignant/', include('enseignant.urls')),
    path('paiement_salaire/', include('enseignant.urls')),
    path('depense/', include('enseignant.urls')),
    path('hlfndgjrieljsgjgfjg^sjôfje^ù^gk^gj/finance/', include('enseignant.urls')),

    # Routes de l'année scolaire
    path('annee-scolaire/', include('annee_scolaire.urls')),
    path('ajout-scolaire/', include('annee_scolaire.urls')),
    path('modifie-scolaire/', include('annee_scolaire.urls')),
    path('supprime-scolaire/', include('annee_scolaire.urls')),

    # Routes des cycles
    path('cycle-scolaire/', include('cycle.urls')),
    path('ajout-cycle/', include('cycle.urls')),
    path('modifie-cycle/', include('cycle.urls')),
    path('supprime-cycle/', include('cycle.urls')),

    # Routes des niveaux
    path('niveau/', include('niveau.urls')),
    path('ajout-niveau/', include('niveau.urls')),
    path('modifie-niveau/', include('niveau.urls')),
    path('supprime-niveau/', include('niveau.urls')),

    # Routes des groupes pédagogiques
    path('groupe/', include('groupe_classe.urls')),
    path('ajout-groupe/', include('groupe_classe.urls')),
    path('modifie-groupe/', include('groupe_classe.urls')),
    path('supprime-groupe/', include('groupe_classe.urls')),

    # Routes des matières
    path('matiere/', include('matiere.urls')),
    path('ajout-matiere/', include('matiere.urls')),
    path('modifie-matiere/', include('matiere.urls')),
    path('supprime-matiere/', include('matiere.urls')),

    # Routes des élèves
    path('eleve/', include('eleve.urls')),
    path('affiche/', include('eleve.urls')),
    path('affiche_modif/', include('eleve.urls')),
    path('ajout-eleve/', include('eleve.urls')),
    path('modifie-eleve/', include('eleve.urls')),
    path('supprime-eleve/', include('eleve.urls')),
    path('page-afichage/', include('eleve.urls')),
    path('reçu-tranche1/', include('eleve.urls')),
    path('tranche2/', include('eleve.urls')),
    path('payer/', include('eleve.urls')),
    path('eleve/liste/', include('eleve.urls')),
    
    # Routes des notes
    path('note/', include('note.urls')),
    path('ajout-note/', include('note.urls')),
    path('modifie-note/', include('note.urls')),
    path('supprime-note/', include('note.urls')),
    path('attribuer-note/', include('note.urls')),

    # Routes des bulletins
    path('bulletins_trimestriels/', include('bulletin.urls')),
    path('bulletins_annuels/', include('bulletin.urls')),
    path('bulletins_option/', include('bulletin.urls')),
    path('bulletins_groupe/', include('bulletin.urls')),
    path('resultat-groupe/', include('bulletin.urls')),
    path('resultat-groupe-annel/', include('bulletin.urls')),
    path('valider-bulletin/', include('bulletin.urls')),
    path('valider-/', include('bulletin.urls')),
    path('resltat-niveau-annee/', include('bulletin.urls')),
] # Pour servir les fichiers statiques uniquement en développement
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()  # Pour servir les fichiers static (CSS, JS) en dev
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Pour servir les médias (images) en dev
