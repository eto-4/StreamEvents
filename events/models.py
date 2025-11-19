from django.db import models
from django.conf import settings
from django.urls import reverse
from urllib.parse import urlparse, parse_qs


class Event(models.Model):
    """
    Model que representa un esdeveniment (streaming, directe, etc.)
    """

    # -------------------------
    # Choices i constants
    # -------------------------
    CATEGORY_CHOICES = [
        ('gaming', 'Gaming'),
        ('music', 'Música'),
        ('talk', 'Xerrades'),
        ('education', 'Educació'),
        ('sports', 'Esports'),
        ('entertainment', 'Entreteniment'),
        ('technology', 'Tecnologia'),
        ('art', 'Art i Creativitat'),
        ('other', 'Altres'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Programat'),
        ('live', 'En Directe'),
        ('finished', 'Finalitzat'),
        ('cancelled', 'Cancel·lat'),
    ]

    CATEGORY_DURATIONS = {
        'gaming': 180,
        'music': 90,
        'talk': 60,
        'education': 120,
        'sports': 150,
        'entertainment': 120,
        'technology': 90,
        'art': 120,
        'other': 90,
    }

    # -------------------------
    # Camps del Model
    # -------------------------
    title = models.CharField(max_length=200)
    description = models.TextField()
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events'
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    thumbnail = models.ImageField(upload_to='events/thumbnails/', blank=True, null=True)
    max_viewers = models.PositiveIntegerField(default=100)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=500, blank=True, null=True)
    stream_url = models.URLField(max_length=500, blank=True, null=True)

    # -------------------------
    # Configuració
    # -------------------------
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Esdeveniment'
        verbose_name_plural = 'Esdeveniments'

    # -------------------------
    # Representació
    # -------------------------
    def __str__(self):
        return self.title

    # -------------------------
    # Helpers
    # -------------------------
    def get_absolute_url(self):
        return reverse("events:detail", kwargs={"pk": self.pk})

    def is_live(self):
        return self.status == 'live'

    def is_upcoming(self):
        return self.status == 'scheduled' and self.scheduled_date is not None

    def get_duration(self):
        return self.CATEGORY_DURATIONS.get(self.category, None)

    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

    def get_stream_embed_url(self):
        """
        Converteix URLs de YouTube/Twitch a format embed.
        """
        if not self.stream_url:
            return None

        # YouTube
        if 'youtube.com' in self.stream_url or 'youtu.be' in self.stream_url:
            parsed_url = urlparse(self.stream_url)

            # youtu.be/VIDEOID
            if parsed_url.hostname == 'youtu.be':
                video_id = parsed_url.path[1:]

            # youtube.com/watch?v=VIDEOID
            else:
                qs = parse_qs(parsed_url.query)
                video_id = qs.get('v', [None])[0]

            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"

        # Twitch
        if 'twitch.tv' in self.stream_url:
            username = self.stream_url.rstrip('/').split('/')[-1]
            return f"https://player.twitch.tv/?channel={username}&parent=localhost"

        # fallback
        return self.stream_url