from django.urls import path
from .views import home, create_entry, register, dashboard, settings, deadlines, insights, view_entry, edit_entry, delete_entry, change_password, all_entries, delete_deadline
from django.contrib.auth import views as auth_views

from journal import views

urlpatterns = [
    path('', home, name='home'),
    path('login/', auth_views.LoginView.as_view(
        template_name = 'journal/login.html'), name ='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(),name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('new/', create_entry, name='create_entry'),
    path('register/', register, name='register'),
    path('settings/', settings, name='settings'),
    path('deadlines/', deadlines, name='deadlines'),
    path('insights/', insights, name='insights'),
    path('entry/<int:id>', view_entry, name='view_entry'),
    path('entry/<int:id>/edit/', edit_entry, name='edit_entry'),
    path('entry/<int:id>/delete/', delete_entry,name='delete_entry'),
    path('change-password/',change_password, name='change_password'),
    path('entries/', all_entries, name='all_entries'),
    path('delete-deadline/<int:id>/', delete_deadline, name='delete_deadline'),
 
    
]