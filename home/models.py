from django.db import models
from django.conf import settings

class DocumentMaster(models.Model):
    class Meta:
        db_table = 'document_master'
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    document_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.document_type
    

class Document(models.Model):
    class Meta:
        db_table = 'documents'
    document_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    file_path = models.FileField(upload_to='documents/')
    document_type = models.CharField(max_length=255)
    size = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Share(models.Model):
    class Meta:
        db_table = 'doc_share'
    share_id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_by')
    shared_with = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_with')
    shared_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AccessRequest(models.Model):
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='requests_made', on_delete=models.CASCADE)
    requested_for = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='requests_received', on_delete=models.CASCADE)
    document_title = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='Pending')  # Status can be Pending, Approved, Denied
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.requested_by} for {self.document_title}"
