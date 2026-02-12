from django.core.management.base import BaseCommand
from eleve.models import Eleve
class Command(BaseCommand):
    help = "Genere les matricules pour les eleves existants"
    def handle(self, *args, **kwargs):
        eleves = Eleve.objects.filter(matricule__isnull=True)
        compteur = 0
        for eleve in eleves:
            eleve.matricule = eleve.generate_matricule()
            eleve.save()
            compteur += 1
        # ✅ ICI le print (à la fin)
        print(f"{compteur} matricules generes")