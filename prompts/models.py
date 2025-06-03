from django.db import models
from django.contrib.auth.models import User

class PromptRun(models.Model):
    """Model for storing prompt runs and their results."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    template = models.TextField()
    variables = models.JSONField()
    model_name = models.CharField(max_length=50)
    response = models.TextField()
    input_tokens = models.IntegerField()
    output_tokens = models.IntegerField()
    total_tokens = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=6)
    response_time = models.FloatField()  # in seconds
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Prompt Run by {self.user.email} at {self.created_at}"
