"""
Certificate Management System - Models
Clean architecture ready for blockchain integration
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
import hashlib
import uuid


# ============================================================================
# USER & ROLE MANAGEMENT (Module 2)
# ============================================================================

class User(AbstractUser):
    """Extended user model with role-based access"""
    
    ROLE_CHOICES = [
        ('issuer', 'Issuer'),
        ('holder', 'Holder'),
        ('verifier', 'Verifier'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='holder')
    phone = models.CharField(max_length=15, blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True, null=True)
    
    # Blockchain wallet address (for future integration)
    wallet_address = models.CharField(max_length=42, blank=True, null=True, unique=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.role})"


# ============================================================================
# CERTIFICATE MANAGEMENT (Module 3)
# ============================================================================

class Certificate(models.Model):
    """Core certificate model"""
    
    STATUS_CHOICES = [
        ('valid', 'Valid'),
        ('revoked', 'Revoked'),
    ]
    
    # Primary identifiers
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate_id = models.CharField(max_length=100, unique=True, editable=False)
    ipfs_cid = models.CharField(max_length=255, blank=True, null=True)
    
    # Certificate details
    title = models.CharField(max_length=255)
    holder_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Relationships
    issuer = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='issued_certificates',
        limit_choices_to={'role': 'issuer'}
    )
    holder = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='received_certificates',
        limit_choices_to={'role': 'holder'},
        null=True,
        blank=True
    )
    
    # File storage (Module 9)
    certificate_file = models.FileField(
        upload_to='certificates/%Y/%m/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])],
    )
    
    # Security & integrity (Module 4)
    hash_value = models.CharField(max_length=64, editable=False)
    
    # Blockchain integration fields (ready for implementation)
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    blockchain_network = models.CharField(max_length=50, blank=True, null=True)
    smart_contract_address = models.CharField(max_length=42, blank=True, null=True)
    
    # Status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='valid')
    issued_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField(blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'certificates'
        ordering = ['-issued_date']
        indexes = [
            models.Index(fields=['certificate_id']),
            models.Index(fields=['status']),
            models.Index(fields=['issuer']),
            models.Index(fields=['blockchain_tx_hash']),
        ]
    
    def __str__(self):
        return f"{self.certificate_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        """Generate certificate ID and hash on save"""
        if not self.certificate_id:
            self.certificate_id = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        
        if not self.hash_value:
            self.hash_value = self.generate_hash()
        
        super().save(*args, **kwargs)
    
    def generate_hash(self):
        """Generate SHA-256 hash for certificate integrity (Module 4)"""
        hash_data = f"{self.certificate_id}{self.title}{self.holder_name}{self.issuer.id}"
        return hashlib.sha256(hash_data.encode()).hexdigest()
    
    def verify_integrity(self):
        """Verify certificate hash integrity"""
        current_hash = self.generate_hash()
        return self.hash_value == current_hash


# ============================================================================
# VERIFICATION MODULE (Module 5)
# ============================================================================

class VerificationLog(models.Model):
    """Track all verification attempts"""
    
    RESULT_CHOICES = [
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
        ('not_found', 'Not Found'),
        ('revoked', 'Revoked'),
    ]
    
    certificate = models.ForeignKey(
        Certificate, 
        on_delete=models.CASCADE,
        related_name='verifications',
        null=True,
        blank=True
    )
    verifier = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verifications_performed'
    )
    
    # Verification details
    certificate_id_checked = models.CharField(max_length=100)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    hash_match = models.BooleanField(default=False)
    
    # Blockchain verification (future)
    blockchain_verified = models.BooleanField(default=False)
    blockchain_verification_data = models.JSONField(blank=True, null=True)
    
    # Metadata
    verified_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'verification_logs'
        ordering = ['-verified_at']
        indexes = [
            models.Index(fields=['certificate']),
            models.Index(fields=['verified_at']),
        ]
    
    def __str__(self):
        return f"Verification of {self.certificate_id_checked} - {self.result}"


# ============================================================================
# REVOCATION MODULE (Module 6)
# ============================================================================

class RevocationRecord(models.Model):
    """Track certificate revocations"""
    
    certificate = models.OneToOneField(
        Certificate,
        on_delete=models.CASCADE,
        related_name='revocation'
    )
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='revocations_made'
    )
    
    # Revocation details
    reason = models.TextField()
    revoked_at = models.DateTimeField(auto_now_add=True)
    
    # Blockchain revocation record (future)
    blockchain_tx_hash = models.CharField(max_length=66, blank=True, null=True)
    
    class Meta:
        db_table = 'revocation_records'
        ordering = ['-revoked_at']
    
    def __str__(self):
        return f"Revocation of {self.certificate.certificate_id}"


# ============================================================================
# AUDIT & LOGGING MODULE (Module 7)
# ============================================================================

class AuditLog(models.Model):
    """Comprehensive audit trail for all system actions"""
    
    ACTION_CHOICES = [
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('certificate_issued', 'Certificate Issued'),
        ('certificate_viewed', 'Certificate Viewed'),
        ('certificate_verified', 'Certificate Verified'),
        ('certificate_revoked', 'Certificate Revoked'),
        ('blockchain_sync', 'Blockchain Sync'),
    ]
    
    # Action details
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    certificate = models.ForeignKey(
        Certificate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    # Metadata
    details = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Blockchain audit trail (future)
    blockchain_logged = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['action']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.timestamp}"


# ============================================================================
# BLOCKCHAIN INTEGRATION (Ready for implementation)
# ============================================================================

class BlockchainTransaction(models.Model):
    """Track all blockchain transactions"""
    
    TRANSACTION_TYPES = [
        ('issue', 'Certificate Issue'),
        ('revoke', 'Certificate Revocation'),
        ('verify', 'Verification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('failed', 'Failed'),
    ]
    
    certificate = models.ForeignKey(
        Certificate,
        on_delete=models.CASCADE,
        related_name='blockchain_transactions'
    )
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    tx_hash = models.CharField(max_length=66, unique=True)
    block_number = models.BigIntegerField(null=True, blank=True)
    network = models.CharField(max_length=50)  # e.g., 'ethereum', 'polygon'
    
    # Smart contract details
    contract_address = models.CharField(max_length=42)
    gas_used = models.BigIntegerField(null=True, blank=True)
    gas_price = models.BigIntegerField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'blockchain_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tx_hash']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.tx_hash[:10]}..."
