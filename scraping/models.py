from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ProductInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_infos')
    product_id = models.CharField(max_length=100)
    status = models.CharField(max_length=100, default="live")
    title = models.CharField(max_length=500, default="default_value", null=True)
    reviews = models.FloatField(default=0.0, null=True)
    ratings = models.FloatField(default=0.0, null=True)
    browse_node = models.CharField(max_length=500, default="default_value", null=True)
    brand_name = models.CharField(max_length=100, default="default_value", null=True)
    generic_name = models.CharField(max_length=100, default="default_value", null=True)
    variations = models.CharField(max_length=200, default="default_value", null=True)
    deal = models.CharField(max_length=100, default="default_value", null=True)
    seller = models.CharField(max_length=50, default="default_value", null=True)
    image_len = models.IntegerField(default=0, null=True)
    video = models.CharField(max_length=100, default="default_value", null=True)
    main_img_url = models.CharField(max_length=500, default="default_value", null=True)
    bullet_point_len = models.IntegerField(default=0, null=True)
    bsr1 = models.CharField(max_length=150, default="default_value", null=True)
    bsr2 = models.CharField(max_length=150, default="default_value", null=True)
    price = models.FloatField(default=0.0, null=True)
    mrp = models.FloatField(default=0.0, null=True)
    availability = models.CharField(max_length=500, default="default_value", null=True)
    description = models.CharField(max_length=3000, default="default_value", null=True)
    a_plus = models.CharField(max_length=100, default="default_value", null=True)
    store_link = models.CharField(max_length=500, default="default_value", null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product_id')
    
    def __str__(self):
        return self.product_id  


class ProductList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_lists')
    name = models.CharField(max_length=255, editable=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            timestamp = timezone.localtime(self.created_at if self.created_at else timezone.now())
            formatted_time = timestamp.strftime("%d %b %Y %I.%M%p").lower()
            self.name = f"{self.user.username} {formatted_time}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"


class ProductListItem(models.Model):
    product_list = models.ForeignKey(ProductList, on_delete=models.CASCADE, related_name='items')
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('product_list', 'product_info')
    
    def __str__(self):
        return f"{self.product_info} in {self.product_list}"

class UserPref(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    preferred_audit_platform = models.CharField(max_length=100, default="amazon")
    preferred_column_name = models.CharField(max_length=100, default="default_column")
    preferred_filetype = models.CharField(max_length=100, default=".xlsx")

    def __str__(self):
        return f"{self.user.username}'s Preferences"
    
class AdminPref(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    preferred_audit_platform = models.CharField(max_length=100, default="amazon")
    preferred_column_name = models.CharField(max_length=100, default="default_column")
    preferred_filetype = models.CharField(max_length=100, default=".xlsx")
    concurrent_amazon_users = models.IntegerField(default=5)
    audit_batches_per_user = models.IntegerField(default=5)


    def __str__(self):
        return f"{self.user.username}'s Preferences"

class IssuesTrackerThread(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues')
    issue_type = models.CharField(max_length=100)
    description = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Issue {self.id} for {self.product_info.product_id} by {self.user.username}"