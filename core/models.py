from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

# ----------------------------------------
# 0. USER PROFILE (IDENTITY NODE)
# ----------------------------------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True) 
    
    # Cyber Metadata
    trust_score = models.IntegerField(default=98)
    security_clearance = models.CharField(max_length=20, default="Tier_01")

    def __str__(self):
        return f"IDENTITY_NODE // {self.user.username}"

@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            Profile.objects.create(user=instance)

# ----------------------------------------
# 1. ITEM MODEL (SIGNAL BROADCASTER)
# ----------------------------------------
class Item(models.Model):
    LOST = 'lost'
    FOUND = 'found'
    STATUS_ACTIVE = 'active'
    STATUS_PENDING = 'pending_resolve'
    STATUS_RESOLVED = 'resolved'

    TYPE_CHOICES = [(LOST, 'Lost'), (FOUND, 'Found')]
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_PENDING, 'Pending Resolution'),
        (STATUS_RESOLVED, 'Resolved'),
    ]

    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField()
    item_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=LOST, db_index=True)
    
    location = models.CharField(max_length=200, db_index=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    date_happened = models.DateField()
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE, db_index=True)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    is_claimed = models.BooleanField(default=False)
    claimed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='claimed_items')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['item_type', 'status']),
            models.Index(fields=['location']),
        ]

    def __str__(self):
        return f">> [ {self.get_item_type_display().upper()} ] : {self.title.upper()}"

    # --- ADDED UTILITY FOR THE ARCHIVE FILTER ---
    @property
    def is_archived(self):
        return self.status == self.STATUS_RESOLVED

# ----------------------------------------
# 2. CHAT SYSTEM (COMMS LINK)
# ----------------------------------------
class Conversation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='conversations')
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"COMMS_LINK // {self.item.title}"

    def get_other_participant(self, user):
        return self.participants.exclude(id=user.id).first()

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    body = models.TextField(blank=True, null=True) 
    attachment = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

# ----------------------------------------
# 3. NOTIFICATION MODEL (SYSTEM ALERTS)
# ----------------------------------------
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    text = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ALERT // {self.text[:30]}"

# ----------------------------------------
# 4. RESOLUTION REQUEST (HANDSHAKE PROTOCOL)
# ----------------------------------------
class ResolutionRequest(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='resolution_requests')
    claimant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resolution_claims')
    
    reporter_confirmed = models.BooleanField(default=False) 
    claimant_confirmed = models.BooleanField(default=False) 
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('item', 'claimant')
        ordering = ['-created_at']

    def __str__(self):
        return f"HANDSHAKE // {self.item.title} // @{self.claimant.username}"

    def is_fully_confirmed(self):
        return self.reporter_confirmed and self.claimant_confirmed

    # --- ADDED HELPER FOR UI BUTTONS ---
    def get_status_for_user(self, user):
        """Returns whether the specific user has signed the handshake yet."""
        if user == self.item.user:
            return self.reporter_confirmed
        if user == self.claimant:
            return self.claimant_confirmed
        return None

    def save(self, *args, **kwargs):
        # Auto-set item to pending if handshake begins
        if (self.reporter_confirmed or self.claimant_confirmed) and self.item.status == Item.STATUS_ACTIVE:
            self.item.status = Item.STATUS_PENDING
            self.item.save()

        # Finalize archive when both sign
        if self.is_fully_confirmed():
            item = self.item
            if item.status != Item.STATUS_RESOLVED:
                item.status = Item.STATUS_RESOLVED
                item.is_active = False
                item.is_claimed = True
                item.claimed_by = self.claimant
                item.resolved_at = timezone.now()
                item.save()
                
                Notification.objects.create(
                    user=item.user, 
                    text=f"HANDSHAKE COMPLETE: {item.title.upper()} RESOLVED."
                )
                Notification.objects.create(
                    user=self.claimant, 
                    text=f"HANDSHAKE COMPLETE: {item.title.upper()} RESOLVED."
                )
                
        super().save(*args, **kwargs)