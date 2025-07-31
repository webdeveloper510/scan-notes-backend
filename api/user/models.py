from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password=None,
        first_name=None,
        last_name=None,
        phone_number=None,
        address=None,
        birthday=None,
        school=None,
        teacher=False,
        software=None,
        **kwargs,
    ):
        """Create and return a `User` with an email, username and password."""
        if first_name is None:
            raise TypeError("Users must have a first name.")
        if email is None:
            raise TypeError("Users must have an email.")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            address=address,
            birthday=birthday,
            school=school,
            teacher=teacher,
            software=software,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, first_name, email, password):
        """
        Create and return a `User` with superuser (admin) permissions.
        """
        if password is None:
            raise TypeError("Superusers must have a password.")
        if email is None:
            raise TypeError("Superusers must have an email.")
        if first_name is None:
            raise TypeError("Superusers must have an first name.")

        user = self.create_user(first_name, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(db_index=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    birthday = models.DateField()
    school = models.CharField(max_length=255)
    teacher = models.BooleanField(default=False)
    software = models.CharField(max_length=255)
    file_upload_count = models.IntegerField(default=0)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "phone_number",
        "address",
        "birthday",
        "teacher",
        "software",
    ]

    objects = UserManager()

    def __str__(self):
        return f"{self.email}"


# Model for Contact Support 
class ContactSupportModel(models.Model):
    email = models.EmailField()
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    reason = models.CharField(max_length=100)
    message = models.TextField()

# Model for user track
class ImageAnalysisModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_image = models.FileField(upload_to='media/')  # Stores both images & videos
    file_url = models.CharField(max_length=200 , null=True  , blank =True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
   
# Model for user track
class CropImageHistoryModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    orignal_image = models.CharField(max_length=500 , null=True , blank=True)
    crop_images = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title =  models.CharField(max_length=500 , null=True , blank=True)
    COMPOSER =  models.CharField(max_length=500 , null=True , blank=True)

# Model to save payment details
class PaymentDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_status = models.CharField(max_length=255 , blank=True , null=True)
    order_id = models.CharField(max_length=500, blank=True , null=True)
    invoice_id = models.CharField(max_length=500, blank=True , null=True)
    subscription_id = models.CharField(max_length=500, blank=True , null=True)
    currency= models.CharField(max_length=255 , blank=True , null=True)
    frequency = models.CharField(max_length=255 , blank=True , null=True)
    amount = models.CharField(max_length=255 , blank=True , null=True)
    start_date = models.CharField(max_length=500, blank=True , null=True)
    end_date = models.CharField(max_length=500, blank=True , null=True)
    thrivecustomer_id = models.CharField(max_length=500, blank=True , null=True)
    thrive_customer_name = models.CharField(max_length=500, blank=True , null=True)
    thrive_customer_email = models.CharField(max_length=500, blank=True , null=True)
    thrive_customer_address = models.JSONField()
    processor = models.CharField(max_length=500, blank=True , null=True)
    product_name = models.CharField(max_length=255 , blank=True , null=True)
    product_id = models.CharField(max_length=255 , blank=True , null=True)
    event_type = models.CharField(max_length=255 , blank=True , null=True)
    auth_user = models.CharField(max_length=500, blank=True , null=True)
    mode = models.CharField(max_length=500, blank=True , null=True)