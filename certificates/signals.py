from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create UserProfile when a User is created."""
    if created:
        # Only create if profile doesn't exist already
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'nama_lengkap': instance.get_full_name() or instance.username,
                'role': 'admin' if instance.is_superuser else 'scanner',
            }
        )
