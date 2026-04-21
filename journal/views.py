from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth import login
from django.utils import timezone
from urllib3 import request
from .forms import JournalEntryForm, RegisterForm, DeadlineForm
from .sentiment import analyse_sentiment
from .models import JournalEntry, Profile, Deadline
from datetime import date, timedelta

@login_required
def create_entry(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user

            label, score = analyse_sentiment(entry.content)
            entry.sentiment_label = label
            entry.sentiment_score = score
            entry.save()
            messages.success(request, "well done for checking in today 💗 view your entry below")
            return redirect('dashboard')
    else:
        form = JournalEntryForm()
    

    entries = JournalEntry.objects.filter(user=request.user).order_by('-created_at')


    return render(request, 'journal/create_entry.html',{
        'form':form,
        'entries':entries
        })

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request,'journal/home.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            
            user.profile.theme = form.cleaned_data['theme']
            user.profile.save()

            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    
    return render(request, 'journal/register.html', {'form':form})



@login_required
def dashboard(request):
    entries = JournalEntry.objects.filter(user=request.user).order_by('-created_at')[:3]
    deadlines = Deadline.objects.filter(user=request.user).order_by('due_date')

    # get last 3 entries
    recent_entries = entries[:3]

    # count negative moods
    negative_count = sum(1 for e in recent_entries if e.sentiment_label == "negative")

    # count upcoming deadlines
    upcoming_deadlines = deadlines.filter(due_date__gte=timezone.now().date())
    upcoming_count = upcoming_deadlines.count()

    # default stress
    stress_level = "low"

    # logic
    if negative_count >= 2 and upcoming_count >= 2:
        stress_level = "high"
    elif negative_count >= 1 or upcoming_count >= 2:
        stress_level = "medium"
    

    entries_today = JournalEntry.objects.filter(
        user = request.user,
        created_at__date=date.today()
    )
    show_reminder = request.user.profile.reminder_enabled and not entries_today.exists()

    return render(request, 'journal/dashboard.html', {
        'entries': entries,
        'deadlines': deadlines,
        'stress_level': stress_level,
        'show_reminder': show_reminder,
    
    })

@login_required
def insights(request):
    entries = JournalEntry.objects.filter(user=request.user)
    deadlines = Deadline.objects.filter(user=request.user)

    # prepare mood data for chart 

    mood_map = {
        "positive": 3,
        "neutral": 2,
        "negative": 1
    }

    chart_labels = []
    chart_data = []

    recent_entries = entries.order_by('created_at')[:10]

    for entry in recent_entries:
        chart_labels.append(entry.created_at.strftime("%b %d"))
        chart_data.append(mood_map.get(entry.sentiment_label,2))

    one_week_ago = timezone.now() - timedelta(days=7)

    weekly_entries = entries.filter(created_at__gte= one_week_ago)

    entry_count = weekly_entries.count()
    negative_count = weekly_entries.filter(sentiment_label="negative").count()
    deadline_count = deadlines.filter(due_date__gte=timezone.now().date()).count()

    insight_text = "your mood is looking good! stay positive <3"

    if negative_count >= 3 and deadline_count >= 2:
        insight_text = "your stress levels may be increasing, take care and stay hydrated 🫶🏼 "
    elif negative_count >=2:
        insight_text = "you've had a few low moods recently, consider taking a break to do something you enjoy 🫂  "
    elif deadline_count >=2:
        insight_text = "you have multiple deadlines coming up, take it easy and make sure to manage your time effectively ⏰"   

    return render(request, 'journal/insights.html', {
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'entry_count': entry_count,
        'negative_count': negative_count,
        'deadline_count': deadline_count,
        'insight_text': insight_text
    }) 


@login_required
def view_entry (request, id):
    entry = JournalEntry.objects.get(id=id, user=request.user)

    return render(request, 'journal/view_entry.html', {
        'entry': entry
    })

@login_required
def edit_entry(request, id):
    entry = JournalEntry.objects.get(id=id, user=request.user)

    if request.method =='POST':
        entry.content = request.POST.get('content')
        label, score = analyse_sentiment(entry.content)
        entry.sentiment_label = label
        entry.sentiment_score = score
        entry.save()
        return redirect('view_entry', id=entry.id)
    
    return render(request, 'journal/edit_entry.html', {'entry' : entry})

@login_required
def delete_entry(request, id):
    entry = JournalEntry.objects.get(id=id, user=request.user)

    if request.method == 'POST':
        entry.delete()
        messages.success(request,"entry deleted successfully")
        return redirect('dashboard')
    
    return redirect('view_entry', id=id)

@login_required
def delete_deadline(request, id):
    deadline = Deadline.objects.get(id=id, user=request.user)

    if request.method == 'POST':
        deadline.delete()
        messages.success(request,"deadline removed successfully")
        return redirect('deadlines')
    
    return redirect('deadlines')


@login_required
def settings (request):
    user = request.user
    profile = user.profile
    selected_theme = None
    if request.method == 'POST':
        selected_theme = request.POST.get('theme')

        if selected_theme in ['light','dark','pastel']:
            request.user.profile.theme = selected_theme
            request.user.profile.save()

        reminder = request.POST.get('reminder')
        profile.reminder_enable = True if reminder == 'on' else False

        username = request.POST.get('username')
        email = request.POST.get('email')

        if username:
            user.username = username
        if email:
            user.email = email

        user.save()
        profile.save()

        return redirect ('settings')

    return render(request, 'journal/settings.html')


def deadlines (request):
    if request.method == 'POST':
        form = DeadlineForm(request.POST)
        if form.is_valid():
            deadline = form.save(commit=False)
            deadline.user = request.user
            deadline.save()
            messages.success(request,"deadline added successfully 🌸 stay on track, you've got this! ")
            return redirect('deadlines')
    else:
        form = DeadlineForm()
    deadlines = Deadline.objects.filter(user=request.user)

        #calculate days left

    for d in deadlines:
        d.days_left = (d.due_date - date.today()).days
        
    return render (request,'journal/deadlines.html', {
        'form':form,
        'deadlines':deadlines
    })
    
@login_required
def change_password(request):
    if request.method == "POST":
        current = request.POST.get("current_password")
        new = request.POST.get("new_password")

        if not request.user.check_password(current):
            messages.error(request, "current password is incorrect")
            return redirect("change_password")
            
            
        if current == new:
            messages.error(request, "new password must be different from current password")
            return redirect("change_password")
        
        
        request.user.password = make_password(new)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "password updated successfully")
        return redirect("dashboard")
    
    return render(request, "journal/change_password.html")

@login_required
def all_entries(request):
    entries = JournalEntry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'journal/all_entries.html', {'entries': entries})