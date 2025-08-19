from django import forms
from eleve.models import Eleve
from matiere.models import Matiere

class RechercheEleveForm(forms.Form):
    nom = forms.CharField(label="Nom de l'élève", required=False)
    prenom = forms.CharField(label="Prénom de l'élève", required=False)

class NoteForm(forms.Form):
    eleve = forms.ModelChoiceField(queryset=Eleve.objects.all(), widget=forms.HiddenInput())
    matiere = forms.ModelChoiceField(queryset=Matiere.objects.all(), label="Matière", required=True)
    note_cours = forms.FloatField(label="Note de cours", required=True, min_value=0, max_value=20)
    note_comp = forms.FloatField(label="Note de compétence", required=True, min_value=0, max_value=20)
    trimestre = forms.ChoiceField(choices=[(1, "Trimestre 1"), (2, "Trimestre 2"), (3, "Trimestre 3")], required=True)
