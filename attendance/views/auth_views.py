import json
import base64
import os
from rest_framework.decorators  import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response    import Response
from rest_framework             import status
from rest_framework.authtoken.models import Token
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    AuthenticatorAttachment,
    RegistrationCredential,
    AuthenticationCredential,
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialType,
)
from webauthn.helpers import bytes_to_base64url, base64url_to_bytes

from ..models import User, WebAuthnCredential, WebAuthnChallenge


# ── Change this when deploying ──
# Local testing  → RP_ID = '127.0.0.1',          RP_ORIGIN = 'http://127.0.0.1:8000'
# ngrok testing  → RP_ID = 'abc.ngrok-free.app', RP_ORIGIN = 'https://abc.ngrok-free.app'
# Production     → RP_ID = 'yourdomain.com',      RP_ORIGIN = 'https://yourdomain.com'
RP_ID     = 'vasiliki-lamiaceous-longingly.ngrok-free.dev'
RP_NAME   = 'Uni Attendance'
RP_ORIGIN = 'https://vasiliki-lamiaceous-longingly.ngrok-free.dev'


# ════════════════════════════════════════════════════════════
#  REGISTRATION — STEP 1
#  Generate challenge and return options to the browser
# ════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webauthn_register_begin(request):
    """
    POST /api/webauthn/register/begin/

    Called after the user logs in with a password for the first time.
    Returns options the browser passes to navigator.credentials.create()
    which triggers the fingerprint or face ID prompt on the device.

    A user can register multiple devices (e.g. phone and laptop).

    Auth required: Yes (Token)

    Returns:
        200  { challenge, rp, user, pubKeyCredParams, ... }
    """
    user          = request.user
    raw_challenge = os.urandom(32)

    # Delete any previous unused challenge for this user
    WebAuthnChallenge.objects.filter(user=user).delete()

    # Save challenge temporarily — deleted after verification
    WebAuthnChallenge.objects.create(
        user      = user,
        challenge = base64.b64encode(raw_challenge).decode('utf-8'),
    )

    # ── One-Device Policy ──
    # Each user is restricted to a single registered biometric device.
    # This prevents buddy registration — a student registering their own
    # fingerprint on a friend's account to mark attendance for both people.
    # For legitimate cases (new phone), a lecturer must call
    # POST /api/webauthn/reset/{student_id}/ to wipe the old credential first,
    # then the student gets a one-time window to register the new device.
    if WebAuthnCredential.objects.filter(user=user).exists():
        return Response(
            {
                'error': (
                    'A biometric device is already registered to this account. '
                    'Only one device is allowed per account. '
                    'If you have a new phone, ask your lecturer to reset your biometric.'
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    options = generate_registration_options(
        rp_id             = RP_ID,
        rp_name           = RP_NAME,
        user_id           = str(user.id).encode(),
        user_name         = user.username,
        user_display_name = (
            f"{user.first_name} {user.last_name}".strip() or user.username
        ),
        challenge         = raw_challenge,
        authenticator_selection = AuthenticatorSelectionCriteria(
            # 'platform' = use the device's built-in biometric (fingerprint/face)
            authenticator_attachment = AuthenticatorAttachment.PLATFORM,
            # 'required' = biometric check cannot be skipped
            user_verification        = UserVerificationRequirement.REQUIRED,
        ),
    )

    return Response(json.loads(options_to_json(options)))


# ════════════════════════════════════════════════════════════
#  REGISTRATION — STEP 2
#  Verify device response and save public key
# ════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webauthn_register_complete(request):
    """
    POST /api/webauthn/register/complete/

    Receives the device's response after the user passes the biometric
    check. Verifies the response cryptographically and saves the
    public key to the database.

    Auth required: Yes (Token)

    Request body:
        id           (str) — base64url credential ID from device
        rawId        (str) — same as id
        response     (obj) — contains clientDataJSON and attestationObject
        type         (str) — must be 'public-key'
        device_name  (str) — optional label e.g. 'My Phone'

    Returns:
        201  { message }
        400  { error }
    """
    user = request.user

    try:
        challenge_obj = WebAuthnChallenge.objects.filter(user=user).latest('created_at')
    except WebAuthnChallenge.DoesNotExist:
        return Response(
            {'error': 'No challenge found. Please start registration again.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    device_name = request.data.get('device_name', 'My Device')

    # Build the credential from individual fields
    # The response must be constructed using AuthenticatorAttestationResponse
    # not passed as a raw dict — py-webauthn needs proper typed objects
    try:
        from webauthn.helpers.structs import AuthenticatorAttestationResponse
        response_data = request.data.get('response', {})
        credential = RegistrationCredential(
            id       = request.data.get('id'),
            raw_id   = base64url_to_bytes(
                request.data.get('rawId', request.data.get('id'))
            ),
            response = AuthenticatorAttestationResponse(
                client_data_json    = base64url_to_bytes(response_data.get('clientDataJSON', '')),
                attestation_object  = base64url_to_bytes(response_data.get('attestationObject', '')),
            ),
            type     = request.data.get('type', 'public-key'),
        )
    except Exception as e:
        return Response(
            {'error': f'Invalid credential format: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # py_webauthn verifies:
        # 1. Challenge matches what we sent
        # 2. Origin matches RP_ORIGIN
        # 3. Attestation is valid
        # 4. Public key is correctly formatted
        verified = verify_registration_response(
            credential                = credential,
            expected_challenge        = base64.b64decode(challenge_obj.challenge),
            expected_rp_id            = RP_ID,
            expected_origin           = RP_ORIGIN,
            require_user_verification = True,
        )
    except Exception as e:
        return Response(
            {'error': f'Biometric registration failed: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Save the public key — used to verify all future logins
    WebAuthnCredential.objects.create(
        user          = user,
        credential_id = bytes_to_base64url(verified.credential_id),
        public_key    = base64.b64encode(
            verified.credential_public_key
        ).decode('utf-8'),
        sign_count    = verified.sign_count,
        device_name   = device_name,
    )

    # Delete the challenge — single use only
    challenge_obj.delete()

    return Response(
        {'message': 'Biometric registered successfully.'},
        status=status.HTTP_201_CREATED
    )


# ════════════════════════════════════════════════════════════
#  AUTHENTICATION — STEP 1
#  Generate challenge for login attempt
# ════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
def webauthn_login_begin(request):
    """
    POST /api/webauthn/login/begin/

    Called when the user taps 'Login with Biometrics'.
    Returns a challenge and the list of credentials the user has
    registered so the browser knows which key to use.

    Auth required: No

    Request body:
        username (str)

    Returns:
        200  { challenge, allowCredentials, rpId, ... }
        400  { error }  — no biometric registered
        404  { error }  — user not found
    """
    username = request.data.get('username')

    if not username:
        return Response(
            {'error': 'Username is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    credentials = WebAuthnCredential.objects.filter(user=user)
    if not credentials.exists():
        return Response(
            {
                'error': (
                    'No biometric registered for this account. '
                    'Please log in with your password first, then register '
                    'your biometric from your profile page.'
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    raw_challenge = os.urandom(32)

    WebAuthnChallenge.objects.filter(user=user).delete()
    WebAuthnChallenge.objects.create(
        user      = user,
        challenge = base64.b64encode(raw_challenge).decode('utf-8'),
    )

    # Tell the device which credentials belong to this user
    # Prevents one user's device from signing for a different user
    allowed_credentials = [
        PublicKeyCredentialDescriptor(
            type = PublicKeyCredentialType.PUBLIC_KEY,
            id   = base64url_to_bytes(c.credential_id),
        )
        for c in credentials
    ]

    options = generate_authentication_options(
        rp_id             = RP_ID,
        challenge         = raw_challenge,
        allow_credentials = allowed_credentials,
        user_verification = UserVerificationRequirement.REQUIRED,
    )

    return Response(json.loads(options_to_json(options)))


# ════════════════════════════════════════════════════════════
#  AUTHENTICATION — STEP 2
#  Verify signature and return auth token
# ════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([AllowAny])
def webauthn_login_complete(request):
    """
    POST /api/webauthn/login/complete/

    Verifies the signature produced by the device's private key.
    Returns the auth token if verification passes.

    Auth required: No

    Request body:
        username  (str) — the user's username
        id        (str) — base64url credential ID
        rawId     (str) — same as id
        response  (obj) — clientDataJSON, authenticatorData, signature
        type      (str) — must be 'public-key'

    Returns:
        200  { token, username, is_student, is_lecturer }
        400  { error }  — verification failed
        404  { error }  — user or credential not found
    """
    username      = request.data.get('username')
    credential_id = request.data.get('id') or request.data.get('rawId')

    if not username:
        return Response(
            {'error': 'Username is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not credential_id:
        return Response(
            {'error': 'Credential ID is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        challenge_obj = WebAuthnChallenge.objects.filter(user=user).latest('created_at')
    except WebAuthnChallenge.DoesNotExist:
        return Response(
            {'error': 'No challenge found. Please start login again.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        stored_credential = WebAuthnCredential.objects.get(
            user          = user,
            credential_id = credential_id,
        )
    except WebAuthnCredential.DoesNotExist:
        return Response(
            {'error': 'Credential not recognised. Please register your biometric again.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        from webauthn.helpers.structs import AuthenticatorAssertionResponse
        response_data = request.data.get('response', {})
        credential = AuthenticationCredential(
            id       = request.data.get('id'),
            raw_id   = base64url_to_bytes(credential_id),
            response = AuthenticatorAssertionResponse(
                client_data_json    = base64url_to_bytes(response_data.get('clientDataJSON', '')),
                authenticator_data  = base64url_to_bytes(response_data.get('authenticatorData', '')),
                signature           = base64url_to_bytes(response_data.get('signature', '')),
                user_handle         = base64url_to_bytes(response_data['userHandle'])
                                      if response_data.get('userHandle') else None,
            ),
            type     = request.data.get('type', 'public-key'),
        )
    except Exception as e:
        return Response(
            {'error': f'Invalid credential format: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # py_webauthn verifies:
        # 1. Challenge matches what we sent
        # 2. Origin matches RP_ORIGIN
        # 3. Signature was produced by the private key matching our stored public key
        # 4. Sign count has increased (detects cloned credentials)
        # 5. User verification was performed (biometric confirmed on device)
        verified = verify_authentication_response(
            credential                    = credential,
            expected_challenge            = base64.b64decode(challenge_obj.challenge),
            expected_rp_id                = RP_ID,
            expected_origin               = RP_ORIGIN,
            credential_public_key         = base64.b64decode(stored_credential.public_key),
            credential_current_sign_count = stored_credential.sign_count,
            require_user_verification     = True,
        )
    except Exception as e:
        return Response(
            {'error': f'Biometric verification failed: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update sign count — if it ever goes backwards someone cloned the credential
    stored_credential.sign_count = verified.new_sign_count
    stored_credential.save()

    # Delete the used challenge
    challenge_obj.delete()

    # Return the auth token
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'token':       token.key,
        'username':    user.username,
        'is_student':  user.is_student,
        'is_lecturer': user.is_lecturer,
    }, status=status.HTTP_200_OK)


# ════════════════════════════════════════════════════════════
#  MANAGE DEVICES
# ════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def webauthn_list_credentials(request):
    """
    GET /api/webauthn/credentials/

    Returns all biometric devices registered by the authenticated user.
    Used to populate a 'Manage Devices' section on the profile page.

    Auth required: Yes (Token)

    Returns:
        200  [ { id, device_name, created_at }, ... ]
    """
    credentials = WebAuthnCredential.objects.filter(user=request.user)

    data = [
        {
            'id':          c.id,
            'device_name': c.device_name,
            'created_at':  c.created_at.strftime('%d %b %Y, %H:%M'),
        }
        for c in credentials
    ]

    return Response(data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def webauthn_delete_credential(request, credential_id):
    """
    DELETE /api/webauthn/credentials/{id}/

    Removes a registered biometric credential.
    Useful when a user loses their phone or wants to re-register.
    Users can only delete their own credentials.

    Auth required: Yes (Token)

    Returns:
        200  { message }
        404  { error }
    """
    try:
        credential = WebAuthnCredential.objects.get(
            id   = credential_id,
            user = request.user,
        )
    except WebAuthnCredential.DoesNotExist:
        return Response(
            {'error': 'Credential not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    device_name = credential.device_name
    credential.delete()

    return Response(
        {'message': f'"{device_name}" has been removed successfully.'},
        status=status.HTTP_200_OK
    )


# ════════════════════════════════════════════════════════════
#  LECTURER OVERRIDE — RESET STUDENT BIOMETRIC
# ════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_student_biometric(request, student_id):
    """
    POST /api/webauthn/reset/{student_id}/

    Allows a lecturer or admin to clear all biometric credentials
    for a specific student. Used when a student loses their phone
    or needs to re-register on a new device.

    Auth required: Yes (Token) — Lecturer or Admin only

    Returns:
        200  { message }
        403  { error }  — not a lecturer or admin
        404  { error }  — student not found
    """
    if not (request.user.is_lecturer or request.user.is_staff):
        return Response(
            {'error': 'Only lecturers and admins can reset student biometrics.'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        student = User.objects.get(id=student_id, is_student=True)
    except User.DoesNotExist:
        return Response(
            {'error': 'Student not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    deleted_count, _ = WebAuthnCredential.objects.filter(user=student).delete()

    return Response(
        {
            'message': (
                f'Biometric data for {student.username} has been reset. '
                f'{deleted_count} credential(s) removed.'
            )
        },
        status=status.HTTP_200_OK
    )
