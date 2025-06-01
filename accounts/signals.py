from django.db.models.signals import post_migrate # type: ignore
from django.dispatch import receiver # type: ignore
from accounts.models import Account


@receiver(post_migrate)
def create_default_users(sender, **kwargs):
    if not Account.objects.filter(email='dragon@gmail.com').exists():
        user = Account.objects.create_superuser(
            first_name='Dragon',
            last_name='Master',
            username='dragon',
            email='dragon@gmail.com',
            password='M^yN8d@6ZpL1'
        )
        print("✅ تم إنشاء سوبر يوزر dragon تلقائيًا.")

    if not Account.objects.filter(email='Amr@gmail.com').exists():
        user = Account.objects.create_user(
            first_name='Amr',
            last_name='Khamis',
            username='amr',
            email='Amr@gmail.com',
            password='StrongPassword123!'
        )
        user.is_staff = True
        user.save()
        print("✅ تم إنشاء المستخدم Amr تلقائيًا.")
