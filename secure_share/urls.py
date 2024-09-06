from django.contrib import admin
from django.urls import path
from authentication import views
from django.contrib.auth import views as auth_views
from home import views as home_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
  path('admin/', admin.site.urls),
  path('',views.register,name='register'),
  path('login/',views.user_login,name='login'),
  path('verify_2fa/', views.verify_2fa, name='verify_2fa'),
  path('dashboard/',home_views.dashboard,name='dashboard'),
  path('logout/',views.logout_user, name='logout'),
  path('setup_2fa/', views.setup_2fa, name='setup_2fa'),
  path('remove_2fa/', views.remove_2fa_view, name='remove_2fa'),
  path('settings/',home_views.user_settings,name='settings'),
  path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
  path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
  path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
  path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
  
  path('upload_new_document/', home_views.upload_new_document, name='upload_new_document'),
  path('view_all_documents/', home_views.view_all_documents, name='view_all_documents'),

  path('access-request/', home_views.access_request, name='access_request'),
  path('pending-request/', home_views.pending_request, name='pending_request'),
  path('requested-document/', home_views.requested_document, name='requested_document'),
  path('get-user-by-email/', home_views.get_user_by_email, name='get_user_by_email')
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

