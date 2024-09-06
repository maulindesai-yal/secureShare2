@login_required
def requested_document(request):
    user = request.user
    requested_documents = AccessRequest.objects.filter(requested_by=user, status='Approved')

    # Create a list to store document information
    document_info = []

    for req in requested_documents:
        # Try to find the corresponding Document
        try:
            document = Document.objects.get(user_id=req.requested_for, title=req.document_title)
            document_info.append({
                'request': req,
                'file_path': document.file_path
            })
        except Document.DoesNotExist:
            # If the document doesn't exist, we'll pass None as the file_path
            document_info.append({
                'request': req,
                'file_path': None
            })

    context = {
        'document_info': document_info
    }
    return render(request, 'home_templates/requested_document.html', context)