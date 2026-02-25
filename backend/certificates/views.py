"""
Certificate Management System - Views
Clean REST API endpoints ready for blockchain integration
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.parsers import MultiPartParser, FormParser



from .models import (
    Certificate, 
    VerificationLog, 
    RevocationRecord, 
    AuditLog,
    BlockchainTransaction
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    CertificateSerializer, CertificateCreateSerializer, CertificateListSerializer,
    VerificationLogSerializer, VerifyRequestSerializer, VerifyResponseSerializer,
    RevocationRecordSerializer, RevokeRequestSerializer,
    AuditLogSerializer, BlockchainTransactionSerializer
)
from .permissions import IsIssuer, IsVerifier, IsOwnerOrReadOnly

User = get_user_model()


# ============================================================================
# AUTHENTICATION VIEWS (Module 2)
# ============================================================================

class UserRegistrationView(APIView):
    """User registration endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create audit log
            AuditLog.objects.create(
                action='user_registration',
                user=user,
                details={'username': user.username, 'role': user.role},
                ip_address=self.get_client_ip(request)
            )
            
            return Response({
                'user': UserSerializer(user).data,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
class UserLoginView(APIView):
    """User login endpoint with JWT tokens"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                
                # Create audit log
                AuditLog.objects.create(
                    action='user_login',
                    user=user,
                    details={'username': username},
                    ip_address=self.get_client_ip(request)
                )
                
                return Response({
                    'user': UserSerializer(user).data,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                })
            
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserLogoutView(APIView):
    """User logout endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        # Create audit log
        AuditLog.objects.create(
            action='user_logout',
            user=request.user,
            ip_address=self.get_client_ip(request)
        )
        
        return Response({'message': 'Logged out successfully'})
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# ============================================================================
# CERTIFICATE VIEWS (Module 3)
# ============================================================================

# class CertificateViewSet(viewsets.ModelViewSet):
#     """
#     Certificate CRUD operations
#     - List: All users can list certificates based on their role
#     - Create: Only issuers
#     - Retrieve: Owner or issuer
#     - Update/Delete: Only issuer who created it
#     """
    
#     permission_classes = [permissions.IsAuthenticated]
#     # class CertificateViewSet(viewsets.ModelViewSet):

#     parser_classes = (MultiPartParser, FormParser)
#     permission_classes = [permissions.IsAuthenticated]

    
#     def get_queryset(self):
#         user = self.request.user
        
#         if user.role == 'issuer':
#             return Certificate.objects.filter(issuer=user)
#         elif user.role == 'holder':
#             return Certificate.objects.filter(holder=user)
#         else:  # verifier
#             return Certificate.objects.all()
    
#     def get_serializer_class(self):
#         if self.action == 'list':
#             return CertificateListSerializer
#         elif self.action == 'create':
#             return CertificateCreateSerializer
#         return CertificateSerializer

class CertificateViewSet(viewsets.ModelViewSet):
    """
    Certificate CRUD operations
    """

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user

        if user.role == 'issuer':
            return Certificate.objects.filter(issuer=user)
        elif user.role == 'holder':
            return Certificate.objects.filter(holder=user)
        else:  # verifier
            return Certificate.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CertificateListSerializer
        elif self.action == 'create':
            return CertificateCreateSerializer
        return CertificateSerializer

    # 🔥 THIS IS THE CRITICAL FIX
    def perform_create(self, serializer):
        from ipfs.ipfs_service import upload_json_to_ipfs
        from merkle.merkle_tree import MerkleTree
        from blockchain.send_root import send_root
        from .models import BlockchainTransaction, AuditLog
        import os

        # 1️⃣ Save certificate WITH issuer
        certificate = serializer.save(issuer=self.request.user)

        # 2️⃣ Prepare metadata JSON
        metadata = {
            "certificate_id": certificate.certificate_id,
            "title": certificate.title,
            "holder_name": certificate.holder_name,
            "issuer": certificate.issuer.username,
            "hash": certificate.hash_value,
            "issued_date": str(certificate.issued_date)
        }

        # 3️⃣ Upload to IPFS
        cid = upload_json_to_ipfs(metadata)
        certificate.ipfs_cid = cid
        certificate.save()

        # 4️⃣ Build Merkle Tree from all valid certificates
        valid_certs = Certificate.objects.filter(
            status='valid'
        ).exclude(ipfs_cid__isnull=True)

        leaves = [cert.ipfs_cid for cert in valid_certs]

        if leaves:
            tree = MerkleTree(leaves)
            new_root = tree.get_root()

            # 5️⃣ Send to blockchain
            blockchain_result = send_root("0x" + new_root)

            # 6️⃣ Store blockchain transaction
            BlockchainTransaction.objects.create(
                certificate=certificate,
                transaction_type='issue',
                tx_hash=blockchain_result["tx_hash"],
                network="localhost",
                contract_address=os.getenv("CONTRACT_ADDRESS"),
                gas_used=blockchain_result["gas_used"],
                status="confirmed"
            )

            # 7️⃣ Audit log
            AuditLog.objects.create(
                action='certificate_issued',
                user=self.request.user,
                certificate=certificate,
                details={
                    'certificate_id': certificate.certificate_id,
                    'cid': cid,
                    'merkle_root': new_root,
                    'gas_used': blockchain_result["gas_used"]
                },
                ip_address=self.get_client_ip()
            )

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')
    
    # def perform_create(self, serializer):
    #     """Create certificate and log action"""
    #     certificate = serializer.save(issuer=self.request.user)
        
    #     # Create audit log
    #     AuditLog.objects.create(
    #         action='certificate_issued',
    #         user=self.request.user,
    #         certificate=certificate,
    #         details={
    #             'certificate_id': certificate.certificate_id,
    #             'title': certificate.title,
    #             'holder_name': certificate.holder_name
    #         },
    #         ip_address=self.get_client_ip()
    #     )
    # def perform_create(self, serializer):
    #     from ipfs.ipfs_service import upload_json_to_ipfs
    #     from merkle.merkle_tree import MerkleTree
    #     from blockchain.send_root import send_root

    #     # 1️⃣ Save certificate
    #     certificate = serializer.save(issuer=self.request.user)

    #     # 2️⃣ Prepare metadata JSON
    #     metadata = {
    #         "certificate_id": certificate.certificate_id,
    #         "title": certificate.title,
    #         "holder_name": certificate.holder_name,
    #         "issuer": certificate.issuer.username,
    #         "hash": certificate.hash_value,
    #         "issued_date": str(certificate.issued_date)
    #     }

    #     # 3️⃣ Upload to IPFS
    #     cid = upload_json_to_ipfs(metadata)
    #     certificate.ipfs_cid = cid
    #     certificate.save()

    #     # 4️⃣ Build Merkle Tree using all certificate CIDs
    #     all_cids = list(
    #         Certificate.objects.filter(status='valid')
    #         .exclude(ipfs_cid__isnull=True)
    #         .values_list('ipfs_cid', flat=True)
    #     )

    #     tree = MerkleTree(all_cids)
    #     new_root = tree.get_root()

    #     # 5️⃣ Update blockchain root
    #     gas_used = send_root("0x" + new_root)

    #     # 6️⃣ Store blockchain transaction
    #     BlockchainTransaction.objects.create(
    #         certificate=certificate,
    #         transaction_type='issue',
    #         tx_hash="updated_via_send_root",  # optionally modify send_root to return tx_hash too
    #         network="localhost",
    #         contract_address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
    #         gas_used=gas_used,
    #         status="confirmed"
    #     )

    #     # 7️⃣ Audit log
    #     AuditLog.objects.create(
    #         action='certificate_issued',
    #         user=self.request.user,
    #         certificate=certificate,
    #         details={
    #             'certificate_id': certificate.certificate_id,
    #             'cid': cid,
    #             'merkle_root': new_root,
    #             'gas_used': gas_used
    #         },
    #         ip_address=self.get_client_ip()
    #     )
    
    # @action(detail=True, methods=['get'])
    # def download(self, request, pk=None):
    #     """Download certificate file"""
    #     certificate = self.get_object()
        
    #     # Create audit log
    #     AuditLog.objects.create(
    #         action='certificate_viewed',
    #         user=request.user,
    #         certificate=certificate,
    #         ip_address=self.get_client_ip()
    #     )
        
    #     return Response({
    #         'file_url': request.build_absolute_uri(certificate.certificate_file.url)
    #     })
    
    # @action(detail=True, methods=['get'])
    # def integrity_check(self, request, pk=None):
    #     """Check certificate integrity"""
    #     certificate = self.get_object()
    #     is_valid = certificate.verify_integrity()
        
    #     return Response({
    #         'certificate_id': certificate.certificate_id,
    #         'integrity_valid': is_valid,
    #         'hash': certificate.hash_value,
    #         'status': certificate.status
    #     })
    
    # def get_client_ip(self):
    #     x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
    #     if x_forwarded_for:
    #         ip = x_forwarded_for.split(',')[0]
    #     else:
    #         ip = self.request.META.get('REMOTE_ADDR')
    #     return ip

    def perform_create(self, serializer):
        from ipfs.ipfs_service import upload_json_to_ipfs
        from merkle.merkle_tree import MerkleTree
        from blockchain.send_root import send_root
        import os

        # 1️⃣ Save certificate with issuer
        certificate = serializer.save(issuer=self.request.user)

        # 2️⃣ Prepare metadata for IPFS
        metadata = {
            "certificate_id": str(certificate.certificate_id),
            "title": certificate.title,
            "holder_name": certificate.holder_name,
            "issuer": certificate.issuer.username,
            "hash": certificate.hash_value,
            "issued_date": str(certificate.issued_date)
        }

        # 3️⃣ Upload to IPFS
        try:
            cid = upload_json_to_ipfs(metadata)
            certificate.ipfs_cid = cid
            certificate.save()
        except Exception as e:
            print(f"⚠️ IPFS upload failed: {e}")
            cid = None

        # 4️⃣ Build Merkle Tree from all valid certificates
        valid_certs = Certificate.objects.filter(
            status='valid'
        ).exclude(ipfs_cid__isnull=True)
        leaves = [cert.ipfs_cid for cert in valid_certs]

        if not leaves:
            print("⚠️ No valid certificates to build Merkle tree")
            return

        tree     = MerkleTree(leaves)
        new_root = tree.get_root()

        # 5️⃣ Send new root to Sepolia blockchain
        try:
            result = send_root("0x" + new_root)

            # 6️⃣ ✅ Store ALL blockchain data in DB
            BlockchainTransaction.objects.create(
                certificate=certificate,
                transaction_type='issue',
                tx_hash=result["tx_hash"],
                block_number=result.get("block_number"),
                network=result.get("network", "sepolia"),
                contract_address=result.get("contract_address", os.getenv("CONTRACT_ADDRESS")),
                gas_used=result["gas_used"],
                status="confirmed",
                confirmed_at=timezone.now()
            )

            # 7️⃣ Audit log
            AuditLog.objects.create(
                action='certificate_issued',
                user=self.request.user,
                certificate=certificate,
                details={
                    'certificate_id': str(certificate.certificate_id),
                    'ipfs_cid': cid,
                    'merkle_root': new_root,
                    'tx_hash': result["tx_hash"],
                    'gas_used': result["gas_used"],
                },
                ip_address=self.get_client_ip()
            )
            print(f"✅ Certificate issued | tx: {result['tx_hash']}")

        except Exception as e:
            print(f"❌ Blockchain transaction failed: {e}")
            # Still save a failed transaction record so it's visible in UI
            BlockchainTransaction.objects.create(
                certificate=certificate,
                transaction_type='issue',
                tx_hash=f"failed_{certificate.certificate_id}",
                network="sepolia",
                contract_address=os.getenv("CONTRACT_ADDRESS", ""),
                status="failed",
                error_message=str(e)
            )

# def perform_create(self, serializer):

#     from ipfs.ipfs_service import upload_json_to_ipfs
#     from merkle.merkle_tree import MerkleTree
#     from blockchain.send_root import send_root
#     from .models import Certificate, BlockchainTransaction, AuditLog

#     # 1️⃣ Save certificate
#     certificate = serializer.save(issuer=self.request.user)

#     # 2️⃣ Prepare metadata JSON
#     metadata = {
#         "certificate_id": certificate.certificate_id,
#         "title": certificate.title,
#         "holder_name": certificate.holder_name,
#         "issuer": certificate.issuer.username,
#         "hash": certificate.hash_value,
#         "issued_date": str(certificate.issued_date)
#     }

#     # 3️⃣ Upload to IPFS
#     cid = upload_json_to_ipfs(metadata)
#     certificate.ipfs_cid = cid
#     certificate.save()

#     # 4️⃣ Build Merkle Tree from all valid CIDs
#     valid_certs = Certificate.objects.filter(
#         status='valid'
#     ).exclude(ipfs_cid__isnull=True)

#     leaves = [cert.ipfs_cid for cert in valid_certs]

#     tree = MerkleTree(leaves)
#     new_root = tree.get_root()

#     # 5️⃣ Send to blockchain
#     blockchain_result = send_root("0x" + new_root)

#     # 6️⃣ Store blockchain transaction
#     BlockchainTransaction.objects.create(
#         certificate=certificate,
#         transaction_type='issue',
#         tx_hash=blockchain_result["tx_hash"],
#         network="localhost",
#         contract_address=os.getenv("CONTRACT_ADDRESS"),
#         gas_used=blockchain_result["gas_used"],
#         status="confirmed"
#     )

#     # 7️⃣ Audit log
#     AuditLog.objects.create(
#         action='certificate_issued',
#         user=self.request.user,
#         certificate=certificate,
#         details={
#             'certificate_id': certificate.certificate_id,
#             'cid': cid,
#             'merkle_root': new_root,
#             'gas_used': blockchain_result["gas_used"]
#         },
#         ip_address=self.get_client_ip()
#     )

# @action(detail=True, methods=['get'])
# def download(self, request, pk=None):
#     """Download certificate file"""
#     certificate = self.get_object()
        
#         # Create audit log
#     AuditLog.objects.create(
#         action='certificate_viewed',
#         user=request.user,
#         certificate=certificate,
#         ip_address=self.get_client_ip()
#     )
        
#     return Response({
#         'file_url': request.build_absolute_uri(certificate.certificate_file.url)
#         })
    
# @action(detail=True, methods=['get'])
# def integrity_check(self, request, pk=None):
#     """Check certificate integrity"""
#     certificate = self.get_object()
#     is_valid = certificate.verify_integrity()
        
#     return Response({
#         'certificate_id': certificate.certificate_id,
#         'integrity_valid': is_valid,
#         'hash': certificate.hash_value,
#         'status': certificate.status
#     })
    
# def get_client_ip(self):
#     x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#         ip = x_forwarded_for.split(',')[0]
#     else:
#         ip = self.request.META.get('REMOTE_ADDR')
#     return ip

# ============================================================================
# VERIFICATION VIEWS (Module 5)
# ============================================================================

class VerificationViewSet(viewsets.ReadOnlyModelViewSet):
    """View verification logs"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VerificationLogSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'verifier':
            return VerificationLog.objects.filter(verifier=user)
        elif user.role == 'issuer':
            return VerificationLog.objects.filter(certificate__issuer=user)
        else:
            return VerificationLog.objects.filter(certificate__holder=user)


class VerifyCertificateView(APIView):
    """
    Certificate verification endpoint.
    Verifies using:
      1. DB hash integrity
      2. Revocation status
      3. On-chain Merkle root comparison
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # from merkle.merkle_tree import MerkleTree, verify_proof
        # from blockchain.blockchain_service import get_merkle_root, is_connected
        from merkle.merkle_tree import MerkleTree, verify_proof
        from blockchain.blockchain_service import get_merkle_root, is_connected
        
        serializer = VerifyRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        certificate_id = serializer.validated_data['certificate_id']

        try:
            certificate = Certificate.objects.get(certificate_id=certificate_id)

            # ── Step 1: DB integrity check ────────────────────────────────────
            hash_match = certificate.verify_integrity()
            is_revoked = certificate.status == 'revoked'

            # ── Step 2: Rebuild Merkle tree from all valid certs ──────────────
            valid_certs = Certificate.objects.filter(
                status='valid'
            ).exclude(ipfs_cid__isnull=True)
            leaves = [cert.ipfs_cid for cert in valid_certs]

            merkle_valid    = False
            proof           = []
            blockchain_root = None
            blockchain_ok   = False

            if certificate.ipfs_cid in leaves:
                tree      = MerkleTree(leaves)
                index     = leaves.index(certificate.ipfs_cid)
                proof     = tree.get_proof(index)
                leaf_hash = tree.leaves[index]
                local_root = tree.get_root()

                # ── Step 3: Get on-chain root (with graceful failure) ─────────
                try:
                    if not is_connected():
                        raise ConnectionError("Not connected to Sepolia")

                    blockchain_root = get_merkle_root()  # hex, no 0x
                    blockchain_ok   = True

                    # ── Step 4: Verify Merkle proof against on-chain root ─────
                    merkle_valid = verify_proof(leaf_hash, proof, blockchain_root)

                except Exception as e:
                    print(f"⚠️ Blockchain verification failed: {e}")
                    # Fallback: compare against locally rebuilt root
                    merkle_valid  = verify_proof(leaf_hash, proof, local_root)
                    blockchain_ok = False

            # ── Final decision ────────────────────────────────────────────────
            is_valid = hash_match and not is_revoked and merkle_valid

            # ── Log verification ──────────────────────────────────────────────
            verification = VerificationLog.objects.create(
                certificate=certificate,
                verifier=request.user if request.user.is_authenticated else None,
                certificate_id_checked=certificate_id,
                result='valid' if is_valid else ('revoked' if is_revoked else 'invalid'),
                hash_match=hash_match,
                blockchain_verified=merkle_valid,
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

            if request.user.is_authenticated:
                AuditLog.objects.create(
                    action='certificate_verified',
                    user=request.user,
                    certificate=certificate,
                    details={
                        'result': verification.result,
                        'blockchain_connected': blockchain_ok,
                        'blockchain_root': blockchain_root,
                    },
                    ip_address=self.get_client_ip(request)
                )

            return Response({
                'valid':                is_valid,
                'certificate':          CertificateSerializer(certificate, context={'request': request}).data,
                'hash_match':           hash_match,
                'is_revoked':           is_revoked,
                'blockchain_verified':  merkle_valid,
                'blockchain_connected': blockchain_ok,
                'blockchain_root':      blockchain_root,
                'merkle_proof':         proof,
                'verified_at':          verification.verified_at,
            })

        except Certificate.DoesNotExist:
            VerificationLog.objects.create(
                certificate=None,
                verifier=request.user if request.user.is_authenticated else None,
                certificate_id_checked=certificate_id,
                result='not_found',
                hash_match=False,
                ip_address=self.get_client_ip(request)
            )
            return Response({
                'valid':   False,
                'message': 'Certificate not found',
            }, status=status.HTTP_404_NOT_FOUND)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

# ============================================================================
# REVOCATION VIEWS (Module 6)
# ============================================================================

class RevocationViewSet(viewsets.ReadOnlyModelViewSet):
    """View revocation records"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RevocationRecordSerializer
    queryset = RevocationRecord.objects.all()


class RevokeCertificateView(APIView):
    """
    Revoke a certificate.
    Only the issuer who created the certificate can revoke it.
    Also updates the Merkle root on-chain after revocation.
    """

    permission_classes = [permissions.IsAuthenticated, IsIssuer]

    def post(self, request):
        from merkle.merkle_tree import MerkleTree
        from blockchain.send_root import send_root

        serializer = RevokeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        certificate_id = serializer.validated_data['certificate_id']
        reason         = serializer.validated_data['reason']

        try:
            certificate = Certificate.objects.get(certificate_id=certificate_id)

            # ── Authorization ─────────────────────────────────────────────────
            if certificate.issuer != request.user:
                return Response(
                    {'error': 'Only the issuer can revoke this certificate'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # ── Already revoked? ──────────────────────────────────────────────
            if certificate.status == 'revoked':
                return Response(
                    {'error': 'Certificate is already revoked'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # ── 1. Update DB status ───────────────────────────────────────────
            certificate.status = 'revoked'
            certificate.save()

            # ── 2. Create RevocationRecord ────────────────────────────────────
            revocation = RevocationRecord.objects.create(
                certificate=certificate,
                revoked_by=request.user,
                reason=reason
            )

            # ── 3. Rebuild Merkle tree WITHOUT this certificate ───────────────
            valid_certs = Certificate.objects.filter(
                status='valid'
            ).exclude(ipfs_cid__isnull=True)
            leaves = [cert.ipfs_cid for cert in valid_certs]

            blockchain_result = None
            if leaves:
                try:
                    tree     = MerkleTree(leaves)
                    new_root = tree.get_root()

                    # ── 4. Push updated root to blockchain ────────────────────
                    blockchain_result = send_root("0x" + new_root)

                    # ── 5. Store blockchain transaction for revocation ─────────
                    BlockchainTransaction.objects.create(
                        certificate=certificate,
                        transaction_type='revoke',
                        tx_hash=blockchain_result["tx_hash"],
                        block_number=blockchain_result.get("block_number"),
                        network=blockchain_result.get("network", "sepolia"),
                        contract_address=blockchain_result.get("contract_address"),
                        gas_used=blockchain_result["gas_used"],
                        status="confirmed",
                        confirmed_at=timezone.now()
                    )
                    print(f"✅ Revocation root updated | tx: {blockchain_result['tx_hash']}")

                except Exception as e:
                    print(f"⚠️ Blockchain update failed during revocation: {e}")
                    BlockchainTransaction.objects.create(
                        certificate=certificate,
                        transaction_type='revoke',
                        tx_hash=f"failed_revoke_{certificate.certificate_id}",
                        network="sepolia",
                        contract_address="",
                        status="failed",
                        error_message=str(e)
                    )

            # ── 6. Audit log ──────────────────────────────────────────────────
            AuditLog.objects.create(
                action='certificate_revoked',
                user=request.user,
                certificate=certificate,
                details={
                    'reason': reason,
                    'tx_hash': blockchain_result["tx_hash"] if blockchain_result else None,
                },
                ip_address=self.get_client_ip(request)
            )

            return Response({
                'message':    'Certificate revoked successfully',
                'revocation': RevocationRecordSerializer(revocation).data,
                'blockchain': {
                    'tx_hash':  blockchain_result["tx_hash"]  if blockchain_result else None,
                    'gas_used': blockchain_result["gas_used"] if blockchain_result else None,
                }
            })

        except Certificate.DoesNotExist:
            return Response(
                {'error': 'Certificate not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
# ============================================================================
# AUDIT LOG VIEWS (Module 7)
# ============================================================================

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """View audit logs"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AuditLogSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        # Issuers can see logs related to their certificates
        if user.role == 'issuer':
            return AuditLog.objects.filter(
                certificate__issuer=user
            ) | AuditLog.objects.filter(user=user)
        
        # Others can only see their own logs
        return AuditLog.objects.filter(user=user)


# ============================================================================
# BLOCKCHAIN VIEWS (Ready for implementation)
# ============================================================================

class BlockchainTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """View blockchain transactions"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BlockchainTransactionSerializer
    
    def get_queryset(self):
        user = self.request.user
        
        if user.role == 'issuer':
            return BlockchainTransaction.objects.filter(certificate__issuer=user)
        elif user.role == 'holder':
            return BlockchainTransaction.objects.filter(certificate__holder=user)
        else:
            return BlockchainTransaction.objects.all()


class BlockchainSyncView(APIView):
    """
    Sync certificate to blockchain
    Placeholder for blockchain integration
    """
    
    permission_classes = [permissions.IsAuthenticated, IsIssuer]
    
    def post(self, request):
        certificate_id = request.data.get('certificate_id')
        network = request.data.get('network', 'ethereum')
        
        try:
            certificate = Certificate.objects.get(certificate_id=certificate_id)
            
            # Check authorization
            if certificate.issuer != request.user:
                return Response({
                    'error': 'Only the issuer can sync this certificate'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # TODO: Implement actual blockchain integration
            # This is a placeholder for Web3 integration
            
            return Response({
                'message': 'Blockchain sync initiated',
                'certificate_id': certificate_id,
                'network': network,
                'note': 'Blockchain integration pending implementation'
            })
            
        except Certificate.DoesNotExist:
            return Response({
                'error': 'Certificate not found'
            }, status=status.HTTP_404_NOT_FOUND)


# ============================================================================
# DASHBOARD STATS VIEW
# ============================================================================

class DashboardStatsView(APIView):
    """Get dashboard statistics"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.role == 'issuer':
            stats = {
                'total_issued': Certificate.objects.filter(issuer=user).count(),
                'valid_certificates': Certificate.objects.filter(issuer=user, status='valid').count(),
                'revoked_certificates': Certificate.objects.filter(issuer=user, status='revoked').count(),
                'recent_verifications': VerificationLog.objects.filter(certificate__issuer=user).count()[:5],
            }
        elif user.role == 'holder':
            stats = {
                'total_certificates': Certificate.objects.filter(holder=user).count(),
                'valid_certificates': Certificate.objects.filter(holder=user, status='valid').count(),
            }
        else:  # verifier
            stats = {
                'total_verifications': VerificationLog.objects.filter(verifier=user).count(),
                'valid_verifications': VerificationLog.objects.filter(verifier=user, result='valid').count(),
            }
        
        return Response(stats)
