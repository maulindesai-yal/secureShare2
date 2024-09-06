from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from home.models import Document,Share,AccessRequest
from authentication.models import CustomUser
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import render

@login_required
def dashboard(request): 
    user= request.user

    total_documents = Document.objects.filter(user_id=user).count()
    shared_documents = Share.objects.filter(Q(shared_by=user) | Q(shared_with=user)).count()
    recent_documents = Document.objects.filter(user_id=user).order_by('-created_at')[:5]
    
    # Define html link 
    if user.secret_key is None:
        link_content = {
            'href': "/setup_2fa",
            'text': "Setup 2FA"
        }
    else:
        link_content = {
        'href': "/remove_2fa",
        'text': "Remove 2FA"
        }
    
    context = {
        'total_documents': total_documents,
        'shared_documents': shared_documents,
        'recent_documents': recent_documents,
        'link_content': link_content
    }
    return render(request, 'home_templates/dashboard.html', context)

@login_required
def upload_new_document(request):
    document_titles=[
        "Aadhaar","PAN","10th Marksheet","12th Marksheet","Voter ID","Passport","Driving License","Ration",
        "Birth","Income","Caste","Domicile","Property Documents","Bank Passbook","Employment ID","NREGA Job",
        "Health Insurance","EPF","ESI","Disability","Other"
    ]
    if request.method == 'POST':
        file = request.FILES.get('file')
        title = request.POST.get('title')
        document_type = request.POST.get('document_type')
        description = request.POST.get('description', '')
        
        if file and title:
            try:
                validate_file_size(file)
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                file_path = fs.url(filename)

                document = Document(
                    user=request.user,
                    title=title,
                    description=description,
                    file_path=file_path,
                    document_type=document_type,
                    size=file.size
                )
                document.save()
                return redirect('dashboard')
            except ValidationError as e:
                return render(request, 'home_templates/upload_new_document.html', {
                    "document_titles": document_titles,'error': str(e)})  
        else:
            return HttpResponse("Missing file or name", status=400)
        
    return render(request, 'home_templates/upload_new_document.html',{'document_titles': document_titles})

def validate_file_size(file):
    max_upload_size = 2 * 1024 * 1024  # 5 MB size limit

    if file.size > max_upload_size:
        raise ValidationError(f"File size exceeds the allowed limit of {max_upload_size / (1024 * 1024)} MB.")

@login_required
def view_all_documents(request):
    documents = Document.objects.filter(user_id=request.user)
    return render(request, 'home_templates/view_all_documents.html', {'documents': documents})

@login_required
def user_settings(request):
    return render(request, 'home_templates/user_settings.html')

@login_required
def access_request(request):
  document_titles = [
      "Aadhaar", "PAN", "10th Marksheet", "12th Marksheet", "Voter ID", "Passport",
      "Driving License", "Ration", "Birth", "Income", "Caste", "Domicile",
      "Property Documents", "Bank Passbook", "Employment ID", "NREGA Job",
      "Health Insurance", "EPF", "ESI", "Disability", "Other"
  ]
  users = CustomUser.objects.all().exclude(id=request.user.id)  # Get all users except the current user
  
  if request.method == 'POST':
    print(request.POST)
    selected_user_id = request.POST.get('selected_user')
    selected_document_titles = request.POST.getlist('selected_document')  # Get multiple selected documents
    
    if selected_user_id and selected_user_id.isdigit() and selected_document_titles:
      selected_user = get_object_or_404(CustomUser, id=int(selected_user_id))
      
      for title in selected_document_titles:
        access_request = AccessRequest.objects.create(
          requested_by=request.user,
          requested_for=selected_user,
          document_title=title,
          status='Pending',  # Or any default status
          request_date=timezone.now()  # Current timestamp
        )
      # Display a success message
      messages.success(request, f"Request to access documents has been sent to {selected_user.get_full_name()}.")
      return redirect('access_request')  # Redirect to the same page or another as needed
    else:
      messages.error(request, "Please select a user and at least one document.")
   
  context = {
    'users': users,
    'document_titles': document_titles,     
  }
  return render(request, 'home_templates/access_request.html', context)

@login_required
def get_user_by_email(request):
    email = request.GET.get('email', None)
    if email:
        try:
            user = CustomUser.objects.get(email=email)
            full_name = user.get_full_name()
            return JsonResponse({'full_name': full_name, 'id': user.id})
        except CustomUser.DoesNotExist:
            return JsonResponse({'full_name': 'No user found with this email.'})
    return JsonResponse({'full_name': ''})

@login_required
def pending_request(request):
    # Fetch the pending requests where the current user is the requested user
    pending_request = AccessRequest.objects.filter(requested_for=request.user, status='Pending')
    previous_request = AccessRequest.objects.filter(requested_for=request.user, status='Approved')  
    for req in pending_request:
      req.document_exists = Document.objects.filter(user_id=request.user, title=req.document_title).exists()

    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')
        
        if request_id and action:
            access_req = get_object_or_404(AccessRequest, id=request_id, requested_for=request.user)
            
            if action == 'grant':
                access_req.status = 'Approved'
                messages.success(request, f"Access granted for {access_req.document_title}")
            elif action == 'deny':
                access_req.status = 'Denied'
                messages.success(request, f"Access denied for {access_req.document_title}")
            
            access_req.save()
            
            return redirect('pending_request')
        
    context = {
        'pending_request': pending_request,
        'previous_request': previous_request,
    }
    return render(request, 'home_templates/pending_request.html', context)

@login_required
def requested_document(request):
    user = request.user
    requested_document = AccessRequest.objects.filter(requested_by=user, status='Approved')
    
    for req in requested_document:
      try:
        document = Document.objects.filter(title=req.document_title, user_id=req.requested_for).first()
        req.file_url = document.file_path.url  # Assuming `file_path` is a FileField
      except Document.DoesNotExist:
        req.file_url = None
    context = {
      'requested_document': requested_document
    }
    return render(request, 'home_templates/requested_document.html', context)
