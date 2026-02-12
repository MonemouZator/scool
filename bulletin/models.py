from django.db import models
from eleve.models import Eleve
from annee_scolaire.models import AnneeScolaire
from note.models import Note
from django.db.models import Avg, F

# ------------------------
# BULLETIN TRIMESTRIEL
# ------------------------
class BulletinTrimestriel(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    trimestre = models.PositiveIntegerField()
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)

    @property
    def notes_par_matiere(self):
        notes = Note.objects.filter(
            eleve=self.eleve,
            trimestre=self.trimestre,
            annee_scolaire=self.annee_scolaire
        ).values('matiere__nom').annotate(
            moyenne_matiere=Avg((F('note_cours') + F('note_comp')) / 2)
        )
        return list(notes)

    @property
    def moyenne_totale(self):
        notes = Note.objects.filter(
            eleve=self.eleve,
            trimestre=self.trimestre,
            annee_scolaire=self.annee_scolaire
        )
        moyenne_totale = notes.aggregate(
            moyenne_semestre=Avg(F('note_cours') + F('note_comp')) / 2
        )['moyenne_semestre']
        return round(moyenne_totale, 2) if moyenne_totale else None

    def get_rang(self):
        bulletins = BulletinTrimestriel.objects.filter(
            annee_scolaire=self.annee_scolaire,
            trimestre=self.trimestre,
            eleve__groupe_classe__niveau=self.eleve.groupe_classe.niveau
        )

        # Trier par moyenne décroissante
        bulletins = sorted(
            [(b.eleve.id, b.moyenne_totale or 0) for b in bulletins],
            key=lambda x: x[1],
            reverse=True
        )

        rang = 0
        previous_moyenne = None
        compteur_exoquo = 0
        rang_dict = {}

        for index, (eleve_id, moyenne) in enumerate(bulletins, start=1):
            if moyenne == previous_moyenne:
                # Ex æquo
                rang_dict[eleve_id] = f"{rang} Ex"
                compteur_exoquo += 1
            else:
                rang = index
                rang_dict[eleve_id] = f"{rang}{'er' if rang == 1 else 'ème'}"
                compteur_exoquo = 0
            previous_moyenne = moyenne

        return rang_dict.get(self.eleve.id)




    @property
    def observation(self):
        moyenne = self.moyenne_totale
        if moyenne is None:
            return "Aucune note"

        cycle_nom = self.eleve.groupe_classe.niveau.cycle.nom.strip().lower()

        if cycle_nom == "primaire":
            if moyenne == 10:
                return "Excellent"
            elif moyenne >= 8:
                return "Très Bien"
            elif moyenne >= 7:
                return "Bien"
            elif moyenne >= 6:
                return "Assez Bien"
            elif moyenne >= 5:
                return "Passable"
            else:
                return "Médiocre"
        else:
            if moyenne == 20:
                return "Excellent"
            elif moyenne >= 16:
                return "Très Bien"
            elif moyenne >= 14:
                return "Bien"
            elif moyenne >= 12:
                return "Assez Bien"
            elif moyenne >= 10:
                return "Passable"
            else:
                return "Médiocre"

    def __str__(self):
        return f"Bulletin Trimestriel - {self.eleve.nom} - Trimestre {self.trimestre}"


# ------------------------
# BULLETIN ANNUEL
# ------------------------
class BulletinAnnuel(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    observation = models.TextField(blank=True, null=True)

    @property
    def moyenne_totale_par_trimestre(self):
        moyenne_t1 = Note.objects.filter(
            eleve=self.eleve,
            annee_scolaire=self.annee_scolaire,
            trimestre=1
        ).aggregate(moyenne_t1=Avg(F('note_cours') + F('note_comp')))['moyenne_t1'] or 0

        moyenne_t2 = Note.objects.filter(
            eleve=self.eleve,
            annee_scolaire=self.annee_scolaire,
            trimestre=2
        ).aggregate(moyenne_t2=Avg(F('note_cours') + F('note_comp')))['moyenne_t2'] or 0

        moyenne_t3 = Note.objects.filter(
            eleve=self.eleve,
            annee_scolaire=self.annee_scolaire,
            trimestre=3
        ).aggregate(moyenne_t3=Avg(F('note_cours') + F('note_comp')))['moyenne_t3'] or 0

        return {
            'moyenne_t1': round(moyenne_t1 / 2, 2),
            'moyenne_t2': round(moyenne_t2 / 2, 2),
            'moyenne_t3': round(moyenne_t3 / 2, 2),
        }

    @property
    def moyenne_totale_annuelle(self):
        moyennes = self.moyenne_totale_par_trimestre
        total_moyennes = moyennes['moyenne_t1'] + moyennes['moyenne_t2'] + moyennes['moyenne_t3']
        return round(total_moyennes / 3, 2)

    def get_rang(self):
        # Sélectionner tous les bulletins du même niveau
        bulletins = BulletinAnnuel.objects.filter(
            annee_scolaire=self.annee_scolaire,
            eleve__groupe_classe__niveau=self.eleve.groupe_classe.niveau
        )

        moyennes = sorted(
            [(b.eleve.id, b.moyenne_totale_annuelle or 0) for b in bulletins],
            key=lambda x: x[1],
            reverse=True
        )

        rang = 0
        previous_moyenne = None
        compteur_exoquo = 0
        rang_dict = {}

        for index, (eleve_id, moyenne) in enumerate(moyennes, start=1):
            if moyenne == previous_moyenne:
                compteur_exoquo += 1
            else:
                rang += compteur_exoquo + 1
                compteur_exoquo = 0
            rang_dict[eleve_id] = rang
            previous_moyenne = moyenne

        return rang_dict.get(self.eleve.id)

    
    @property
    def observation_finale(self):
        moyenne = self.moyenne_totale_annuelle
        if moyenne is None:
            return "Aucune note"

        cycle_nom = self.eleve.groupe_classe.niveau.cycle.nom.strip().lower()

        if cycle_nom == "primaire":
            if moyenne == 10:
                return "Excellent"
            elif moyenne >= 8:
                return "Très Bien"
            elif moyenne >= 7:
                return "Bien"
            elif moyenne >= 6:
                return "Assez Bien"
            elif moyenne >= 5:
                return "Passable"
            else:
                return "Médiocre"
        else:
            if moyenne == 20:
                return "Excellent"
            elif moyenne >= 16:
                return "Très Bien"
            elif moyenne >= 14:
                return "Bien"
            elif moyenne >= 12:
                return "Assez Bien"
            elif moyenne >= 10:
                return "Passable"
            else:
                return "Médiocre"

    def __str__(self):
        return f"Bulletin Annuel - {self.eleve.nom} - {self.annee_scolaire.nom}"