from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import MySpecificResetForm 

app_name = 'core'

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. DISCOVERY & HOME
    # -------------------------------------------------------------------------
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-posts/', views.my_posts, name='my_posts'),

    # -------------------------------------------------------------------------
    # 2. ITEM MANAGEMENT (WIZARD & CRUD)
    # -------------------------------------------------------------------------
    path('report/wizard/', views.report_item_wizard, name='report_item'), 
    path('report/success/<int:pk>/', views.report_success, name='report_success'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('item/<int:pk>/edit/', views.item_edit, name='item_edit'),
    path('item/<int:pk>/delete/', views.delete_item, name='delete_item'),

    # -------------------------------------------------------------------------
    # 3. CHAT SYSTEM
    # -------------------------------------------------------------------------
    path('inbox/', views.inbox, name='inbox'),
    path('chat/start/<int:item_id>/', views.start_conversation, name='start_conversation'),
    path('chat/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),

    # -------------------------------------------------------------------------
    # 4. RESOLUTION PROTOCOL (THE HANDSHAKE)
    # -------------------------------------------------------------------------
    # Initial claim action
    path('claim/<int:item_id>/', views.claim_item, name='claim_item'),
    
    # Confirmation action (The "Mark as Resolved" / "Authorize Handover" button)
    path('resolve/confirm/<int:request_id>/', views.confirm_resolution, name='confirm_resolution'),

    # -------------------------------------------------------------------------
    # 5. IDENTITY & NOTIFICATIONS
    # -------------------------------------------------------------------------
    path('profile/', views.profile, name='profile'), 
    path('profile/edit/', views.edit_profile, name='edit_profile'), 
    path('notifications/check/', views.check_notifications, name='check_notifications'),
    path('notifications/read-all/', views.mark_all_as_read, name='mark_all_as_read'),

    # -------------------------------------------------------------------------
    # 6. AUTHENTICATION (SYSTEM ACCESS)
    # -------------------------------------------------------------------------
    path('signup/', views.signup, name='signup'), 
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='core:home'), name='logout'),
    
    # -------------------------------------------------------------------------
    # 7. PASSWORD RESET FLOW (RECOVERY PROTOCOL)
    # -------------------------------------------------------------------------
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             form_class=MySpecificResetForm,
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             success_url=reverse_lazy('core:password_reset_done')
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url=reverse_lazy('core:password_reset_complete')
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]