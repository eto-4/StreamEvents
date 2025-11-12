from django.db import models
from django.conf import settings
from django.urls import reverse
from urllib.parse import urlparse, parse_qs

class Event:
    
    # Categories predefinides:
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

    
    # Estats predefinits
    STATUS_CHOICES = [
        ('scheduled', 'Programat'),
        ('live', 'En Directe'),
        ('finished', 'Finalitzat'),
        ('cancelled', 'Cancel·lat'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
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
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("events:detail", kwargs={"pk": self.pk})
    
    def is_live(self):
        return self.status == 'live'
    
    def is_upcoming(self):
        return self.status == 'scheduled' and self.scheduled_date != ''
    
    category_durations = {
            'gaming': 180,        # 3 hores
            'music': 90,          # 1.5 hores  
            'talk': 60,           # 1 hora
            'education': 120,     # 2 hores
            'sports': 150,        # 2.5 hores
            'entertainment': 120, # 2 hores
            'technology': 90,     # 1.5 hores
            'art': 120,           # 2 hores
            'other': 90,          # 1.5 hores
        }
    
    def get_duration(self):
        return self.category_durations.get(self.category.lower(), None)
    
    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def get_stream_embed_url(self):
        if not self.stream_url:
            return None
        
        # Youtube
        if 'youtube.com' in self.stream_url or 'youtu.be' in self.stream_url:
            
            # Extreure l'id del video
            parsed_url = urlparse(self.stream_url)
            if parsed_url.hostname == 'youtu.be':
                video_id = parsed_url.path[1:]
            else:
                qs = parse_qs(parsed_url.query)
                video_id = qs.get('v', [None])[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"
        
        # Twitch
        elif 'twitch.tv' in self.stream_url:
            username = self.stream_url.rstrip('/').split('/')[-1]
            return f"https://player.twitch.tv/?channel={username}&parent=localhost"
        
        # fallback
        return self.stream_url     
    
    class Meta:
        ordering = ['-created_at'] # Més recent primer
        verbose_name = 'Esdeveniment' # Singular (noms a l’Admin)
        verbose_name_plural = 'Esdeveniments' # Plural