from django.http import JsonResponse
from django.shortcuts import get_list_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from events.models import Event
from .models import ChatMessage
from .forms import ChatMessageForm

# Enviar/Crear missatge
@login_required
@require_POST
def chat_send_message(request, event_pk):
    event = get_list_or_404(Event, pk=event_pk)
    
    if event.status != 'live':
        return JsonResponse({
            'success': False,
            'error': 'Event no actiu'
        })
    
    form = ChatMessageForm(request.POST)
    if form.is_valid():
        msg = form.save(commit=False)
        msg.user = request.user
        msg.event = event
        msg.save()
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': msg.id,
                'user': msg.user.username,
                'display_name': msg.get_user_display_name(),
                'message': msg.message,
                'created_at': msg.get_time_since(),
                'can_delete': msg.can_delete(request.user),
                'is_highlighted': msg.is_highlighted                
            }
        })
    
    return JsonResponse({
        'success': False,
        'errors': form.errors
    })

# Carregar missatges
def chat_load_messages(request, event_pk):
    event = get_list_or_404(Event, pk=event_pk)
    
    messages = ChatMessage.objects.filter(
        event=event,
        is_deleted=False
    ).order_by('created_at')[:50]
    
    data = []
    for msg in messages:
        data.append({
            'id': msg.id,
            'user': msg.user.username,
            'display_name': msg.get_user_display_name(),
            'message': msg.message,
            'created_at': msg.get_time_since(),
            'can_delete': msg.can_delete(request.user),
            'is_highlighted': msg.is_highlighted 
        })
    
    return JsonResponse({
        messages: data
    })
    
# Eliminar missatge
@login_required
@require_POST
def chat_delete_message(request, message_pk):
    msg = get_list_or_404(ChatMessage, pk=message_pk)
    
    if not msg.can_delete(request.user):
        return JsonResponse({'success': False,'error': 'Sense permisos'})

    msg.is_deleted = True
    msg.save()
    return JsonResponse({
        'success': True
    })