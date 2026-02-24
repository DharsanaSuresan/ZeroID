"""
Certificate Management System - Serializers
Clean API serialization ready for blockchain integration
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Certificate, 
    VerificationLog, 
    RevocationRecord, 
    AuditLog,
    BlockchainTransaction
)

User = get_user_model()


# ============================================================================
# USER SERIALIZERS (Module 2)
# ============================================================================

class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'role', 'organization', 'wallet_address', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration with password"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 
                  'role', 'organization', 'wallet_address']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Login credentials"""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


# CERTIFICATE SERIALIZERS (Module 3)


class CertificateSerializer(serializers.ModelSerializer):
    """Full certificate serializer"""
    
    issuer_name = serializers.CharField(source='issuer.get_full_name', read_only=True)
    issuer_organization = serializers.CharField(source='issuer.organization', read_only=True)
    holder_email = serializers.EmailField(source='holder.email', read_only=True)
    file_url = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_id', 'title', 'holder_name', 'description',
            'issuer', 'issuer_name', 'issuer_organization',
            'holder', 'holder_email',
            'certificate_file', 'file_url',
            'hash_value', 'status', 'is_valid',
            'issued_date', 'expiry_date', 'modified_date',
            # Blockchain fields
            'blockchain_tx_hash', 'blockchain_network', 'smart_contract_address'
        ]
        read_only_fields = ['id', 'certificate_id', 'hash_value', 'issued_date', 'modified_date']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.certificate_file and request:
            return request.build_absolute_uri(obj.certificate_file.url)
        return None
    
    def get_is_valid(self, obj):
        return obj.status == 'valid' and obj.verify_integrity()


# class CertificateCreateSerializer(serializers.ModelSerializer):
#     """Simplified serializer for certificate creation"""
    
#     class Meta:
#         model = Certificate
#         fields = ['title', 'holder_name', 'description', 'holder', 
#                   'certificate_file', 'expiry_date']
    
#     def create(self, validated_data):
#         # Issuer is set from request.user in view
#         return Certificate.objects.create(**validated_data)

class CertificateCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for certificate creation"""

    class Meta:
        model = Certificate
        fields = [
            'title',
            'holder_name',
            'description',
            'holder',
            'certificate_file',
            'expiry_date'
        ]


# class CertificateListSerializer(serializers.ModelSerializer):
#     """Lightweight serializer for listing certificates"""
    
#     issuer_name = serializers.CharField(source='issuer.get_full_name', read_only=True)
    
#     class Meta:
#         model = Certificate
#         fields = ['id', 'certificate_id', 'title', 'holder_name', 
#                   'issuer_name', 'status', 'issued_date', 'hash_value']
class BlockchainTransactionSerializer(serializers.ModelSerializer):
    certificate_id = serializers.CharField(source='certificate.certificate_id', read_only=True)

    class Meta:
        model = BlockchainTransaction
        fields = [
            'id', 'certificate', 'certificate_id', 'transaction_type',
            'tx_hash', 'block_number', 'network', 'contract_address',
            'gas_used', 'gas_price', 'status', 'error_message',
            'created_at', 'confirmed_at'
        ]
        read_only_fields = ['id', 'created_at', 'confirmed_at']

class CertificateListSerializer(serializers.ModelSerializer):
    issuer_name = serializers.CharField(source='issuer.get_full_name', read_only=True)
    blockchain_transactions = BlockchainTransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Certificate
        fields = [
            'id',
            'certificate_id',
            'title',
            'holder_name',
            'issuer_name',
            'status',
            'issued_date',
            'hash_value',
            'ipfs_cid',
            'blockchain_transactions'
        ]


# ============================================================================
# VERIFICATION SERIALIZERS (Module 5)
# ============================================================================

class VerificationLogSerializer(serializers.ModelSerializer):
    """Verification log serializer"""
    
    verifier_name = serializers.CharField(source='verifier.get_full_name', read_only=True)
    certificate_title = serializers.CharField(source='certificate.title', read_only=True)
    
    class Meta:
        model = VerificationLog
        fields = [
            'id', 'certificate', 'certificate_title', 'certificate_id_checked',
            'verifier', 'verifier_name', 'result', 'hash_match',
            'blockchain_verified', 'blockchain_verification_data',
            'verified_at', 'ip_address'
        ]
        read_only_fields = ['id', 'verified_at']


class VerifyRequestSerializer(serializers.Serializer):
    """Certificate verification request"""
    
    certificate_id = serializers.CharField()


class VerifyResponseSerializer(serializers.Serializer):
    """Certificate verification response"""
    
    valid = serializers.BooleanField()
    certificate = CertificateSerializer(required=False)
    hash_match = serializers.BooleanField()
    is_revoked = serializers.BooleanField()
    blockchain_verified = serializers.BooleanField(required=False)
    verified_at = serializers.DateTimeField()
    message = serializers.CharField(required=False)


# ============================================================================
# REVOCATION SERIALIZERS (Module 6)
# ============================================================================

class RevocationRecordSerializer(serializers.ModelSerializer):
    """Revocation record serializer"""
    
    revoked_by_name = serializers.CharField(source='revoked_by.get_full_name', read_only=True)
    certificate_id = serializers.CharField(source='certificate.certificate_id', read_only=True)
    certificate_title = serializers.CharField(source='certificate.title', read_only=True)
    
    class Meta:
        model = RevocationRecord
        fields = [
            'id', 'certificate', 'certificate_id', 'certificate_title',
            'revoked_by', 'revoked_by_name', 'reason', 'revoked_at',
            'blockchain_tx_hash'
        ]
        read_only_fields = ['id', 'revoked_at']


class RevokeRequestSerializer(serializers.Serializer):
    """Certificate revocation request"""
    
    certificate_id = serializers.CharField()
    reason = serializers.CharField()


# ============================================================================
# AUDIT LOG SERIALIZERS (Module 7)
# ============================================================================

class AuditLogSerializer(serializers.ModelSerializer):
    """Audit log serializer"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    certificate_id = serializers.CharField(source='certificate.certificate_id', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'action', 'user', 'user_name', 
            'certificate', 'certificate_id',
            'details', 'timestamp', 'ip_address',
            'blockchain_logged'
        ]
        read_only_fields = ['id', 'timestamp']


# ============================================================================
# BLOCKCHAIN SERIALIZERS (Ready for implementation)
# ============================================================================

class BlockchainTransactionSerializer(serializers.ModelSerializer):
    """Blockchain transaction serializer"""
    
    certificate_id = serializers.CharField(source='certificate.certificate_id', read_only=True)
    
    class Meta:
        model = BlockchainTransaction
        fields = [
            'id', 'certificate', 'certificate_id', 'transaction_type',
            'tx_hash', 'block_number', 'network', 'contract_address',
            'gas_used', 'gas_price', 'status', 'error_message',
            'created_at', 'confirmed_at'
        ]
        read_only_fields = ['id', 'created_at', 'confirmed_at']


class BlockchainSyncSerializer(serializers.Serializer):
    """Request to sync certificate with blockchain"""
    
    certificate_id = serializers.CharField()
    network = serializers.ChoiceField(choices=['ethereum', 'polygon', 'sepolia'])
