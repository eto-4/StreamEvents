from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404
from .models import Event
from .forms import EventCreationForm, EventUpdateForm, EventSearchForm

# ===========================================
# 5.1 Vista de Llistat d'Esdeveniments
# ===========================================
def event_list_view(request):
    """
    Mostra tots els esdeveniments amb paginació, cerca i filtres.
    Els esdeveniments destacats apareixen al principi.
    """
    
    # Ordenats per més recents
    events = Event.objects.all().order_by('-created_at')
    
    # Gestionar filtre amb EventSearchForm
    form = EventSearchForm(request.GET or None)
    if form.is_valid():
        data = form.cleaned_data
        
        # Cerca per text
        search = data.get('search')
        if search:
            events = events.filter(
                title__icontains=search
            )
        
        # Categoria
        category = data.get('category')
        if category and category != 'all':
            events = events.filter(
                category=category
            )
        
        # Estat
        status = data.get('status')
        if status and status != 'all':
            events = events.filter(
                status=status
            )
        
        # Rang de dates
        date_from = data.get('date_from')
        if date_from:
            events = events.filter(
                scheduled_date__gte=date_from
            )
        date_to = data.get('date_to')
        if date_to:
            events = events.filter(
                scheduled_date__lte=date_to
            )
    
    # Prioritzar els destacats
    events = events.order_by('-is_featured', '-created_at')
    
    # Paginació
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'events': page_obj
    }
    return render(
        request,
        'events/event_list.html',
        context
    )

# ===========================================
# 5.2 Vista de Detall d'Esdeveniment
# ===========================================

def event_detail_view(request, pk):
    """
    Mostra informació completa d'un esdeveniment.
    Verifica si l'usuari és el creador per mostrar opcions d'edició.
    Gestiona esdeveniments no trobats amb 404.
    """
    
    event = get_object_or_404(Event, pk=pk)
    is_creator = request.user == event.creator
    context = {
        'event': event,
        'is_creator': is_creator
    }
    return render(
        request,
        'events/event_detail.html',
        context
    )
    
# ===========================================
# 5.3 Vista de Creació d'Esdeveniment
# ===========================================
@login_required
def event_create_view(request):
    """
    Permet a l'usuari crear un nou esdeveniment.
    Assigna automàticament l'usuari com a creador.
    Mostra missatges d'èxit o error.
    """
    if request.method == 'POST':
        form = EventCreationForm(
            request.POST,
            request.FILES,
            user=request.user
        )
        if form.is_valid():
            event = form.save(
                commit=False
            )
            event.creator = request.user
            event.save()
            messages.success(
                request,
                'Esdeveniment creat correctament!'
            )
            return redirect(
                'events:event_detail',
                pk=event.pk
            )
        else:
            messages.error(
                request,
                'Si us plau, revisa els errors del formulari.'
            )
    else:
        form = EventCreationForm(user=request.user)
    
    return render(
        request,
        'events/event_form.html',
        { 'form': form }
    )
    
# ===========================================
# 5.4 Vista d'Edició d'Esdeveniment
# ===========================================
@login_required
def event_update_view(request, pk):
    """
    Permet editar un esdeveniment només si l'usuari és el creador.
    Gestiona permisos i errors amb missatges.
    """
    event = get_object_or_404(Event, pk=pk)
    if event.creator != request.user:
        messages.error(
            request,
            'Només el creador pot editar aquest esdeveniment.'
        )
        return redirect(
            'events:event_detail',
            pk=pk
        )
    if request.method == 'POST':
        form = EventUpdateForm(
            request.POST,
            request.FILES,
            instance=event,
            user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Esdeveniment actualitzat correctament!'
            )
            return redirect(
                'events:event_detail',
                pk=event.pk
            )
        else:
            messages.error(
                request,
                'Si us plau, revisa els errors del formulari.'
            )
    else:
        form = EventUpdateForm(
            instance=event,
            user=request.user
        )
    return render(
        request,
        'events/event_form.html',
        { 'form': form, 'event': event }
    )
    
# ===========================================
# 5.5 Vista d'Eliminació d'Esdeveniment
# ===========================================
@login_required
def event_delete_view(request, pk):
    """
    Permet eliminar un esdeveniment només si l'usuari és el creador.
    Requereix confirmació abans d'eliminar.
    Redirigeix al llistat després d'eliminar.
    """
    event = get_object_or_404(Event, pk=pk)
    if event.creator != request.user:
        messages.error(
            request, 
            'Només el creador pot eliminar aquest esdeveniment.'
        )
        return redirect(
            'events:event_detail',
            pk=pk
        )
    
    if request.method == 'POST':
        event.delete()
        messages.success(
            request,
            'Esdeveniment eliminat correctament!'
        )
        return redirect(
            'events:event_list'
        )
    
    return render(
        request,
        'events/event_confirm_delete.html',
        { 'event':event }
    )

# ===========================================
# 5.6 Vista d'Esdeveniments de l'Usuari
# ===========================================
@login_required
def my_events_view(request):
    """
    Mostra només els esdeveniments creats per l'usuari actual.
    Inclou filtres per estat i opcions ràpides d'edició.
    """
    events = Event.objects.filter(
        creator=request.user
    ).order_by(
        '-created_at'
    )
    
    # Filtres ràpids per estat
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        events = events.filter(status=status_filter)
    
    # Paginació (12 per pàgina)
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'events': page_obj
    }
    return render(
        request, 
        'events/my_events.html', 
        context
    )

# ===========================================
# 5.7 Vista d'Esdeveniments per Categoria
# ===========================================
def events_by_category_view(request, category):
    """
    Mostra esdeveniments filtrats per categoria.
    Si la categoria no existeix, llença un 404.
    """
    # Comprovar que la categoria existeix
    valid_categories = [ c[ 0 ] for c in Event.CATEGORY_CHOICES ]
    if category not in valid_categories:
        # Aquí podries crear una pàgina 404 específica amb missatge personalitzat
        raise Http404("Aquesta categoria no existeix. Viatja al passat!")  # comentari: fer la pàgina 404 específica

    events = Event.objects.filter(
        category=category
    ).order_by('-is_featured', '-created_at')
    
    # Paginació
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'events': page_obj,
        'category': category
    }
    return render(
        request,
        'events/event_list.html',
        context
    )