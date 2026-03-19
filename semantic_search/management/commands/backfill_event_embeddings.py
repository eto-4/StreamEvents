from django.core.management.base import BaseCommand
from django.utils import timezone
from events.models import Event
from semantic_search.services.embeddings import embed_text, model_name
from semantic_search.views import _event_text


class Command(BaseCommand):
    """
    Comanda de gestió per generar i desar embeddings per a Events.

    Funciona com a script independent, executat amb:
        python manage.py <nom_comanda> [--force] [--limit N]

    Opcions:
    --force : recalcula embeddings encara que ja existeixin
    --limit : limita el nombre d'events processats (0 = tots)
    """

    help = "Genera i desa embeddings per a Events."

    def add_arguments(self, parser):
        """
        Defineix arguments opcionals per la comanda.
        """
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recalcula encara que ja hi hagi embedding"
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limita el nombre d'events (0 = tots)"
        )

    def handle(self, *args, **options):
        """
        Lògica principal de la comanda:
        1. Obté events segons filtres.
        2. Genera embeddings amb el model carregat.
        3. Desa embeddings i metadades a la BD.
        """

        force = options["force"]
        limit = options["limit"]

        # Query inicial: tots els events ordenats per data de creació
        qs = Event.objects.all().order_by("created_at")
        if limit and limit > 0:
            qs = qs[:limit]

        # Aplica límit si s'ha passat com a opció
        if limit and limit > 0:
            qs = qs[:limit]

        total = 0  # Comptador d'embeddings generats

        for e in qs:
            if not force and e.embedding:
                continue
            # Text agregat de l'event (title + description + category + tags)
            text = _event_text(e)
            if not text:
                # Si el text és buit, ignora l'event
                continue

            # Genera embedding
            vec = embed_text(text)
            # Desa embedding i informació del model
            e.embedding = vec
            e.embedding_model = model_name()
            e.embedding_updated_at = timezone.now()

            # Desa només els camps modificats (més eficient)
            e.save(update_fields=["embedding", "embedding_model", "embedding_updated_at"])

            total += 1

        # Mostra resultat per consola
        self.stdout.write(self.style.SUCCESS(f"Embeddings generats: {total}"))