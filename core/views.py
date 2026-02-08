from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.auth import get_user_model, login as auth_login
from django.template.loader import render_to_string

# Internal app imports
from .models import Item, ResolutionRequest, Conversation, Message, Notification, Profile
from .forms import (
    ItemForm, 
    ReportItemStep1Form, 
    ReportItemStep2Form, 
    SignupForm, 
    UserProfileForm
)

User = get_user_model()

# -----------------------------------------------------------------------------
# 1. AUTHENTICATION & IDENTITY
# -----------------------------------------------------------------------------

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            auth_login(request, user)
            
            Notification.objects.create(
                user=user, 
                text="NODE INITIALIZED: WELCOME TO THE NETWORK."
            )
            messages.success(request, f"REGISTRATION SUCCESSFUL! WELCOME @{user.username.upper()}.")
            return redirect('core:home')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile(request):
    profile_obj, created = Profile.objects.get_or_create(user=request.user)
    my_reported_items = Item.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'core/profile.html', {
        'user': request.user,
        'profile': profile_obj,
        'my_reported_items': my_reported_items,
    })

@login_required
def edit_profile(request):
    profile_obj, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "USER IDENTITY PARAMETERS UPDATED.")
            return redirect('core:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'core/update_identity.html', {'form': form})

# -----------------------------------------------------------------------------
# 2. DISCOVERY VIEWS (UPDATED FILTER LOGIC)
# -----------------------------------------------------------------------------

def home(request):
    query = request.GET.get('q', '')
    item_type_filter = request.GET.get('item_type_filter', 'ALL') 
    status_filter = request.GET.get('status_filter', 'active') # Matches UI image_199bc7.png

    # Start with all items, but select related to optimize queries
    items = Item.objects.select_related('user', 'user__profile')

    # 1. HANDLE STATUS FILTER
    if status_filter == 'active':
        # Default view: Only active signals
        items = items.filter(status='active', is_active=True)
    elif status_filter == 'pending':
        # Handshake in progress
        items = items.filter(status='pending')
    elif status_filter == 'resolved':
        # ARCHIVED: Only finalized items (is_active is False here)
        items = items.filter(status='resolved')
    # If status_filter == 'ALL', we show everything

    # 2. HANDLE SIGNAL TYPE FILTER
    if item_type_filter != 'ALL':
        items = items.filter(item_type=item_type_filter.lower())

    # 3. HANDLE SEARCH
    if query:
        items = items.filter(
            Q(title__icontains=query) | Q(location__icontains=query) | Q(description__icontains=query)
        )
        
    items = items.order_by('-created_at')
    
    return render(request, 'core/home.html', {
        'items': items, 
        'query': query, 
        'item_type_filter': item_type_filter, 
        'status_filter': status_filter
    })

# -----------------------------------------------------------------------------
# 3. ITEM MANAGEMENT
# -----------------------------------------------------------------------------

@login_required
def report_item_wizard(request):
    step = request.GET.get('step', '1')
    if step == '1':
        if request.method == 'GET' and 'reset' in request.GET:
            request.session.pop('wizard_data', None)
        initial_data = request.session.get('wizard_data', {})
        form = ReportItemStep1Form(request.POST or None, initial=initial_data)
        if request.method == 'POST' and form.is_valid():
            request.session['wizard_data'] = form.cleaned_data
            return redirect('/report/wizard/?step=2')
    elif step == '2':
        if 'wizard_data' not in request.session:
            return redirect('/report/wizard/?step=1')
        form = ReportItemStep2Form(request.POST or None, request.FILES or None)
        if request.method == 'POST' and form.is_valid():
            wizard_data = request.session.pop('wizard_data')
            item = Item(**wizard_data, **form.cleaned_data)
            item.user = request.user
            item.save()
            Notification.objects.create(user=request.user, text=f"BROADCAST INITIATED: {item.title.upper()}.")
            messages.success(request, "SIGNAL BROADCASTED TO THE NETWORK.")
            return redirect('core:report_success', pk=item.pk)
    else:
        return redirect('/report/wizard/?step=1')
    return render(request, 'core/report_wizard.html', {'form': form, 'step': step})

@login_required
def report_success(request, pk):
    item = get_object_or_404(Item, pk=pk, user=request.user)
    return render(request, 'core/report_success.html', {'item': item})

@login_required
def item_detail(request, pk):
    item = get_object_or_404(Item.objects.select_related('user', 'user__profile'), pk=pk)
    is_owner = (request.user == item.user)
    existing_convo = Conversation.objects.filter(item=item, participants=request.user).first()
    
    # Identify if there is an ongoing handshake for this item
    active_claim = ResolutionRequest.objects.filter(item=item).filter(
        Q(claimant=request.user) | Q(item__user=request.user)
    ).first()

    return render(request, 'core/item_detail.html', {
        'item': item, 
        'is_owner': is_owner, 
        'active_claim': active_claim, 
        'existing_conversation': existing_convo,
    })

@login_required
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "BROADCAST PARAMETERS MODIFIED.")
            return redirect('core:item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)
    return render(request, 'core/report_wizard.html', {'form': form, 'item': item, 'editing': True})

@login_required
@require_POST
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk, user=request.user)
    item.delete()
    messages.warning(request, "SIGNAL PERMANENTLY DELETED.")
    return redirect('core:my_posts')

# -----------------------------------------------------------------------------
# 4. CHAT SYSTEM
# -----------------------------------------------------------------------------

@login_required
def inbox(request):
    conversations = Conversation.objects.filter(participants=request.user).order_by('-updated_at')
    return render(request, 'core/inbox.html', {'conversations': conversations})

@login_required
def start_conversation(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if item.user == request.user:
        return redirect('core:item_detail', pk=item.id)
    
    convo = Conversation.objects.filter(item=item, participants=request.user).first()
    if not convo:
        convo = Conversation.objects.create(item=item)
        convo.participants.add(request.user, item.user)
    return redirect('core:conversation_detail', conversation_id=convo.id)

@login_required
def conversation_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    other_user = conversation.get_other_participant(request.user)
    if request.method == 'POST':
        body = request.POST.get('body')
        attachment = request.FILES.get('attachment')
        if body or attachment:
            msg = Message.objects.create(
                conversation=conversation, sender=request.user, body=body, attachment=attachment
            )
            conversation.updated_at = timezone.now()
            conversation.save()
            Notification.objects.create(user=other_user, text=f"NEW COMMS FROM @{request.user.username.upper()}.")
            if request.headers.get('HX-Request'):
                return render(request, 'core/partials/message_line.html', {'message': msg})
    
    chat_messages = conversation.messages.all().order_by('timestamp')
    chat_messages.exclude(sender=request.user).update(is_read=True)
    return render(request, 'core/conversation_detail.html', {
        'conversation': conversation, 'chat_messages': chat_messages, 'other_user': other_user,
    })

# -----------------------------------------------------------------------------
# 5. DASHBOARD & RESOLUTION (HANDSHAKE UPDATED)
# -----------------------------------------------------------------------------

@login_required
def dashboard(request):
    user = request.user
    context = {
        'notifications': Notification.objects.filter(user=user).order_by('-created_at')[:10],
        'my_reported_items': Item.objects.filter(user=user).order_by('-created_at')[:5],
        'my_claims': ResolutionRequest.objects.filter(claimant=user).select_related('item'),
        'claims_to_review': ResolutionRequest.objects.filter(item__user=user, reporter_confirmed=False),
    }
    return render(request, 'core/dashboard.html', context)

@login_required
@require_POST
def claim_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if item.user == request.user:
        messages.error(request, "ACCESS DENIED: CANNOT CLAIM OWN SIGNAL.")
        return redirect('core:item_detail', pk=item.id)
    
    claim, created = ResolutionRequest.objects.get_or_create(item=item, claimant=request.user)
    if created:
        item.status = 'pending' # Update item status to pending upon claim
        item.save()
        Notification.objects.create(user=item.user, text=f"NEW HANDSHAKE REQUEST: {item.title.upper()}.")
        messages.success(request, "HANDSHAKE INITIATED: CLAIM SIGNAL TRANSMITTED.")
    else:
        messages.info(request, "SIGNAL ALREADY IN FLIGHT: CLAIM IS PENDING.")
    return redirect('core:item_detail', pk=item.id)

@login_required
@require_POST
def confirm_resolution(request, request_id):
    res_request = get_object_or_404(ResolutionRequest, pk=request_id)
    item = res_request.item
    
    is_claimant = (request.user == res_request.claimant)
    is_owner = (request.user == item.user)

    if not is_claimant and not is_owner:
        return HttpResponseForbidden("UNAUTHORIZED PROTOCOL ACCESS.")

    # Apply signature based on who is clicking
    if is_claimant:
        res_request.claimant_confirmed = True
        messages.info(request, "PEER SIGNATURE VERIFIED. AWAITING OWNER.")
    elif is_owner:
        res_request.reporter_confirmed = True
        messages.info(request, "OWNER SIGNATURE VERIFIED. AWAITING PEER.")
    
    res_request.save() 

    # Final Handshake Logic: Check if both confirmed
    if res_request.claimant_confirmed and res_request.reporter_confirmed:
        item.status = 'resolved'
        item.is_active = False # Move to archive
        item.resolved_at = timezone.now()
        item.claimed_by = res_request.claimant
        item.save()
        messages.success(request, f"SUCCESS: {item.title.upper()} ARCHIVED IN DATABASE.")
    
    return redirect('core:item_detail', pk=item.pk)

# -----------------------------------------------------------------------------
# 6. UTILITIES
# -----------------------------------------------------------------------------

@login_required
def check_notifications(request):
    new_logs = Notification.objects.filter(user=request.user, is_read=False)
    if not new_logs.exists():
        return HttpResponse("")
    html = ""
    for log in new_logs:
        html += render_to_string('partials/notification_item.html', {'message': log.text}, request=request)
    new_logs.update(is_read=True)
    return HttpResponse(html)

@login_required
def mark_all_as_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "ALL SYSTEM LOGS CLEARED.")
    return redirect('core:dashboard')

@login_required
def my_posts(request):
    items = Item.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'core/my_posts.html', {'items': items})