# Creating my model here.
from django.db import models

class AuditLog(models.Model):
    correlation_id = models.CharField(max_length=64, db_index=True)

    step_name = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    message = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.correlation_id} {self.step_name} {self.status}"

