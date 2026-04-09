import base64, os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from webauthn import (
    generate_registration_options, verify_registration_response,
    generate_authentication_options, verify_authentication_response, options_to_json
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria, UserVerificationRequirement,
    AuthenticatorAttachment, RegistrationCredential, AuthenticationCredential,
    PublicKeyCredentialDescriptor, PublicKeyCredentialType
)
from webauthn.helpers import bytes_to_base64url, base64url_to_bytes
from ..models import User, WebAuthnCredential, WebAuthnChallenge

# RP_ID must match your domain (e.g., '127.0.0.1' or 'mmu-attendance.com')
RP_ID = '127.0.0.1'
RP_NAME = 'Uni Attendance'
RP_ORIGIN = 'http://127.0.0.1:8000'

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webauthn_register_begin(request):
    """ Generates a challenge to link a student's biometric hardware. """
    user = request.user
    if WebAuthnCredential.objects.filter(user=user).exists():
        return Response({'error': 'Device already linked.'}, status=status.HTTP_403_FORBIDDEN)

    raw_challenge = os.urandom(32)
    WebAuthnChallenge.objects.filter(user=user).delete()
    WebAuthnChallenge.objects.create(user=user, challenge=base64.b64encode(raw_challenge).decode('utf-8'))

    options = generate_registration_options(
        rp_id=RP_ID, rp_name=RP_NAME, user_id=str(user.id).encode(),
        user_name=user.username, user_display_name=user.username,
        challenge=raw_challenge,
        authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AuthenticatorAttachment.PLATFORM, # Built-in sensors only
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
    )
    return Response(options_to_json(options))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webauthn_register_complete(request):
    """ Verifies the biometric hardware response and saves the Public Key. """
    user = request.user
    challenge_obj = WebAuthnChallenge.objects.filter(user=user).latest('created_at')
    try:
        credential = RegistrationCredential.parse_raw(str(request.data).replace("'", '"'))
        verified = verify_registration_response(
            credential=credential, expected_challenge=base64.b64decode(challenge_obj.challenge),
            expected_rp_id=RP_ID, expected_origin=RP_ORIGIN, require_user_verification=True,
        )
        WebAuthnCredential.objects.create(
            user=user, credential_id=bytes_to_base64url(verified.credential_id),
            public_key=base64.b64encode(verified.credential_public_key).decode('utf-8'),
            sign_count=verified.sign_count, device_name=request.data.get('device_name', 'Student Mobile'),
        )
        challenge_obj.delete()
        return Response({'message': 'Biometric registered.'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ════════════════════════════════════════════════════════════
#  WEBAUTHN AUTHENTICATION (Verifying Identity for Login/Attendance)
# ════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
def webauthn_login_begin(request):
    """ 
    Step 1: Generate a challenge for a student to verify their identity.
    Used during login or right before marking attendance.
    """
    username = request.data.get('username')
    if not username:
        return Response({'error': 'Username is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    credentials = WebAuthnCredential.objects.filter(user=user)
    if not credentials.exists():
        return Response({'error': 'No biometric registered for this account.'}, status=status.HTTP_400_BAD_REQUEST)

    raw_challenge = os.urandom(32)
    WebAuthnChallenge.objects.filter(user=user).delete()
    WebAuthnChallenge.objects.create(user=user, challenge=base64.b64encode(raw_challenge).decode('utf-8'))

    # Prepare the allowed credentials so the phone knows which key to use
    allowed_credentials = [
        PublicKeyCredentialDescriptor(
            type=PublicKeyCredentialType.PUBLIC_KEY, 
            id=base64url_to_bytes(c.credential_id)
        ) for c in credentials
    ]

    options = generate_authentication_options(
        rp_id=RP_ID,
        challenge=raw_challenge,
        allow_credentials=allowed_credentials,
        user_verification=UserVerificationRequirement.REQUIRED,
    )
    return Response(options_to_json(options))


@api_view(['POST'])
@permission_classes([AllowAny])
def webauthn_login_complete(request):
    """ 
    Step 2: Verify the biometric signature and issue an Auth Token.
    """
    username = request.data.get('username')
    credential_id = request.data.get('id')

    try:
        user = User.objects.get(username=username)
        challenge_obj = WebAuthnChallenge.objects.filter(user=user).latest('created_at')
        stored_credential = WebAuthnCredential.objects.get(user=user, credential_id=credential_id)

        credential = AuthenticationCredential(
            id=credential_id,
            raw_id=base64url_to_bytes(credential_id),
            response=request.data.get('response'),
            type='public-key',
        )

        # Cryptographic verification
        verified = verify_authentication_response(
            credential=credential,
            expected_challenge=base64.b64decode(challenge_obj.challenge),
            expected_rp_id=RP_ID,
            expected_origin=RP_ORIGIN,
            credential_public_key=base64.b64decode(stored_credential.public_key),
            credential_current_sign_count=stored_credential.sign_count,
            require_user_verification=True,
        )

        # Security update: prevent replay attacks
        stored_credential.sign_count = verified.new_sign_count
        stored_credential.save()
        challenge_obj.delete()

        # Success! Log them in
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'is_student': user.is_student,
            'is_lecturer': user.is_lecturer
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Verification failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])

@permission_classes([IsAuthenticated])
def reset_student_biometric(request, student_id):
    """ Lecturer override to clear a student's biometric data (e.g. lost phone). """
    if not (request.user.is_lecturer or request.user.is_staff):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    WebAuthnCredential.objects.filter(user_id=student_id).delete()
    return Response({'message': 'Biometric reset successfully.'})