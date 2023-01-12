from django.db.models.signals import post_save, pre_save
from accounts.models import User, UserProfile
from django.dispatch import receiver


@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
#post_save.connect(post_save_create_profile_receiver, sender=User)
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # Create a new profile if one doesn't exist
            UserProfile.objects.create(user=instance)

@receiver(pre_save, sender = User)
def pre_save_profile_reciever(sender, instance, **kwargs):
    print(instance.username, 'This username is being created')