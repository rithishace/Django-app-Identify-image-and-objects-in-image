from django.db import models
from cloudinary.models import CloudinaryField
# Create your models here.

class ImageClass(models.Model):
    Image = CloudinaryField('image')
    