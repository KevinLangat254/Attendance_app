import json
import base64
import os
from urllib.parse import urlparse

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
    AuthenticatorAttestationResponse,
    AuthenticatorAssertionResponse,
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialType,
)
from webauthn.helpers import bytes_to_base64url, base64url_to_bytes

from ..models import User, WebAuthnCredential, WebAuthnChallenge


RP_NAME = 'Uni Attendance'


# def get_rp_config(request):
#     """
#     Dynamically derive RP_ID and RP_ORIGIN from the HTTP request.
#     This ensures WebAuthn works on localhost, 127.0.0.1, ngrok, or
#     any production domain without any manual code changes.

#     RP_ID     = hostname only       e.g. localhost | abc.ngrok-free.app
#     RP_ORIGIN = full origin URL     e.g. http://localhost:8000
#     """
#     origin = (
#         request.META.get('HTTP_ORIGIN')
#         or request.META.get('HTTP_REFERER', '').rstrip('/')
#         or request.build_absolute_uri('/').rstrip('/')
#     )
#     parsed = urlparse(origin)
#     rp_id  = parsed.hostname   # hostname only — no port, no scheme
#     return rp_id, origin


def get_rp_config(request):
    # In production use env vars, in development derive from request
    env_rp_id  = os.getenv('WEBAUTHN_RP_ID')
    env_origin = os.getenv('WEBAUTHN_ORIGIN')

    if env_rp_id and env_origin:
        return env_rp_id, env_origin

    # Development fallback — derive from request
    origin = request.META.get('HTTP_ORIGIN')
    if not origin:
        scheme = 'https' if request.is_secure() else 'http'
        host   = request.get_host()
        origin = f"{scheme}://{host}"

    parsed = urlparse(origin)
    rp_id  = parsed.hostname
    return rp_id, origin

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

    One-device policy: each account can only have one registered credential.

    Auth required: Yes (Token)

    Returns:
        200  { challenge, rp, user, pubKeyCredParams, ... }
        403  { error }  — device already registered to this account
    """
    user          = request.user
    rp_id, origin = get_rp_config(request)

    # ── One-device policy ──
    # Each account is limited to one biometric credential.
    # For a new phone, a lecturer must call reset_student_biometric first.
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

    raw_challenge = os.urandom(32)

    # Delete any previous unused challenge for this user
    WebAuthnChallenge.objects.filter(user=user).delete()

    # Save challenge temporarily — deleted after verification
    WebAuthnChallenge.objects.create(
        user      = user,
        challenge = base64.b64encode(raw_challenge).decode('utf-8'),
    )

    options = generate_registration_options(
        rp_id             = rp_id,
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
        400  { error }  — verification failed or no challenge found
        403  { error }  — device already linked to another account
    """
    user          = request.user
    rp_id, origin = get_rp_config(request)

    try:
        challenge_obj = WebAuthnChallenge.objects.filter(user=user).latest('created_at')
    except WebAuthnChallenge.DoesNotExist:
        return Response(
            {'error': 'No challenge found. Please start registration again.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    device_name   = request.data.get('device_name', 'My Device')
    response_data = request.data.get('response', {})

    try:
        credential = RegistrationCredential(
            id       = request.data.get('id'),
            raw_id   = base64url_to_bytes(
                request.data.get('rawId', request.data.get('id'))
            ),
            response = AuthenticatorAttestationResponse(
                client_data_json   = base64url_to_bytes(
                    response_data.get('clientDataJSON', '')
                ),
                attestation_object = base64url_to_bytes(
                    response_data.get('attestationObject', '')
                ),
            ),
            type = request.data.get('type', 'public-key'),
        )
    except Exception as e:
        return Response(
            {'error': f'Invalid credential format: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # py_webauthn verifies:
        # 1. Challenge matches what we sent
        # 2. Origin matches the request origin
        # 3. Attestation is valid
        # 4. Public key is correctly formatted
        verified = verify_registration_response(
            credential                = credential,
            expected_challenge        = base64.b64decode(challenge_obj.challenge),
            expected_rp_id            = rp_id,
            expected_origin           = origin,
            require_user_verification = True,
        )
    except Exception as e:
        return Response(
            {'error': f'Biometric registration failed: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    new_credential_id = bytes_to_base64url(verified.credential_id)
    new_public_key    = base64.b64encode(
        verified.credential_public_key
    ).decode('utf-8')

    # ── Cross-account uniqueness checks ──
    # Three independent checks to prevent the same physical device from
    # being registered to multiple accounts.
    #
    # Check 1: credential_id — unique key pair identifier per device per RP
    if WebAuthnCredential.objects.filter(credential_id=new_credential_id).exists():
        challenge_obj.delete()
        return Response(
            {
                'error': (
                    'This device is already linked to another account. '
                    'A biometric device can only be registered to one account. '
                    'If you believe this is a mistake, contact the admin.'
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # Check 2: public_key — the actual cryptographic key bytes
    # Two registrations on the same device produce the same public key
    if WebAuthnCredential.objects.filter(public_key=new_public_key).exists():
        challenge_obj.delete()
        return Response(
            {
                'error': (
                    'This device is already linked to another account. '
                    'A biometric device can only be registered to one account. '
                    'If you believe this is a mistake, contact the admin.'
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # Check 3: aaguid — identifies the authenticator model (e.g. Pixel 6 fingerprint sensor)
    # If the same authenticator model AND same user is detected, block it
    # This catches edge cases where credential_id differs but it is the same hardware
    if hasattr(verified, 'aaguid') and verified.aaguid:
        aaguid_str = str(verified.aaguid)
        if (aaguid_str != '00000000-0000-0000-0000-000000000000' and
                WebAuthnCredential.objects.filter(aaguid=aaguid_str).exists()):
            challenge_obj.delete()
            return Response(
                {
                    'error': (
                        'This device is already linked to another account. '
                        'A biometric device can only be registered to one account. '
                        'If you believe this is a mistake, contact the admin.'
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

    # Save the public key — used to verify all future attendance markings
    # try/except catches any race condition where two requests slip past
    # the checks above simultaneously
    try:
        WebAuthnCredential.objects.create(
            user          = user,
            credential_id = new_credential_id,
            public_key    = new_public_key,
            sign_count    = verified.sign_count,
            device_name   = device_name,
            aaguid        = str(verified.aaguid) if hasattr(verified, 'aaguid') and verified.aaguid else '',
        )
    except Exception:
        challenge_obj.delete()
        return Response(
            {
                'error': (
                    'This device is already linked to another account. '
                    'A biometric device can only be registered to one account.'
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # Delete the challenge — single use only
    challenge_obj.delete()

    return Response(
        {'message': 'Biometric registered successfully.'},
        status=status.HTTP_201_CREATED
    )


# ════════════════════════════════════════════════════════════
#  ATTENDANCE — STEP 1
#  Generate challenge before marking attendance
# ════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webauthn_attendance_begin(request):
    """
    POST /api/webauthn/attendance/begin/

    Called when a student taps 'Confirm with Biometric' on the
    attendance modal. Returns a challenge the browser passes to
    navigator.credentials.get() to trigger the biometric prompt.

    Auth required: Yes (Token — student)

    Returns:
        200  { challenge, allowCredentials, rpId, ... }
        400  { error }  — no biometric registered
    """
    user          = request.user
    rp_id, origin = get_rp_config(request)

    credentials = WebAuthnCredential.objects.filter(user=user)
    if not credentials.exists():
        return Response(
            {
                'error': (
                    'No biometric registered for this account. '
                    'Please go to your profile page and register your biometric first.'
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
        rp_id             = rp_id,
        challenge         = raw_challenge,
        allow_credentials = allowed_credentials,
        user_verification = UserVerificationRequirement.REQUIRED,
    )

    return Response(json.loads(options_to_json(options)))


# ════════════════════════════════════════════════════════════
#  ATTENDANCE — STEP 2
#  Verify biometric signature then mark attendance
# ════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webauthn_attendance_complete(request):
    """
    POST /api/webauthn/attendance/complete/

    Verifies the biometric signature AND the GPS geofence in one step.
    Only creates an attendance record if both pass.

    Auth required: Yes (Token — student)

    Request body:
        session_id        (int)   — active session ID
        latitude          (float) — student's GPS latitude
        longitude         (float) — student's GPS longitude
        id                (str)   — base64url credential ID
        rawId             (str)   — same as id
        response          (obj)   — clientDataJSON, authenticatorData, signature
        type              (str)   — must be 'public-key'

    Returns:
        201  { message, distance_metres, attendance_id }
        400  { error }  — missing fields / inactive session / duplicate
        403  { error, distance_metres, allowed_radius }  — outside geofence
        403  { error }  — biometric verification failed
        404  { error }  — session not found
    """
    from django.utils import timezone
    import math

    user          = request.user
    rp_id, origin = get_rp_config(request)

    # ── Validate GPS fields ──
    session_id = request.data.get('session_id')
    latitude   = request.data.get('latitude')
    longitude  = request.data.get('longitude')

    if not all([session_id, latitude is not None, longitude is not None]):
        return Response(
            {'error': 'session_id, latitude and longitude are all required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ── Check session exists ──
    from ..models import Session, Attendance
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return Response(
            {'error': 'Session not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # ── Check session is active ──
    now = timezone.now()
    if not (session.start_time <= now <= session.end_time):
        return Response(
            {'error': 'This session is not currently active.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ── Check for duplicate attendance ──
    if Attendance.objects.filter(student=user, session=session).exists():
        return Response(
            {'error': 'You have already marked attendance for this session.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # ── Geofence check ──
    def haversine(lat1, lon1, lat2, lon2):
        R    = 6371000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a    = (math.sin(dphi / 2) ** 2
                + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance       = haversine(
        float(latitude), float(longitude),
        float(session.latitude), float(session.longitude),
    )
    allowed_radius = session.radius_metres or 50

    if distance > allowed_radius:
        return Response(
            {
                'error':           'You are outside the geofence.',
                'distance_metres': round(distance),
                'allowed_radius':  allowed_radius,
            },
            status=status.HTTP_403_FORBIDDEN
        )

    # ── Biometric verification ──
    try:
        challenge_obj = WebAuthnChallenge.objects.filter(user=user).latest('created_at')
    except WebAuthnChallenge.DoesNotExist:
        return Response(
            {'error': 'No challenge found. Please try again.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    credential_id = request.data.get('id') or request.data.get('rawId')
    if not credential_id:
        return Response(
            {'error': 'Credential ID is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        stored_credential = WebAuthnCredential.objects.get(
            user          = user,
            credential_id = credential_id,
        )
    except WebAuthnCredential.DoesNotExist:
        return Response(
            {'error': 'Biometric credential not recognised. Please re-register your biometric.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    response_data = request.data.get('response', {})

    try:
        credential = AuthenticationCredential(
            id       = request.data.get('id'),
            raw_id   = base64url_to_bytes(credential_id),
            response = AuthenticatorAssertionResponse(
                client_data_json   = base64url_to_bytes(
                    response_data.get('clientDataJSON', '')
                ),
                authenticator_data = base64url_to_bytes(
                    response_data.get('authenticatorData', '')
                ),
                signature          = base64url_to_bytes(
                    response_data.get('signature', '')
                ),
                user_handle        = base64url_to_bytes(response_data['userHandle'])
                                     if response_data.get('userHandle') else None,
            ),
            type = request.data.get('type', 'public-key'),
        )
    except Exception as e:
        return Response(
            {'error': f'Invalid credential format: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # py_webauthn verifies:
        # 1. Challenge matches what we sent
        # 2. Origin matches the request origin
        # 3. Signature was produced by the private key matching our stored public key
        # 4. Sign count has increased (detects cloned credentials)
        # 5. User verification was performed (biometric confirmed on device)
        verified = verify_authentication_response(
            credential                    = credential,
            expected_challenge            = base64.b64decode(challenge_obj.challenge),
            expected_rp_id                = rp_id,
            expected_origin               = origin,
            credential_public_key         = base64.b64decode(stored_credential.public_key),
            credential_current_sign_count = stored_credential.sign_count,
            require_user_verification     = True,
        )
    except Exception as e:
        return Response(
            {'error': f'Biometric verification failed: {str(e)}'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Update sign count — if it ever goes backwards someone cloned the credential
    stored_credential.sign_count = verified.new_sign_count
    stored_credential.save()

    # Delete the used challenge
    challenge_obj.delete()

    # ── All checks passed — create the attendance record ──
    attendance = Attendance.objects.create(
        student = user,
        session = session,
        status  = 'PRESENT',
    )

    return Response(
        {
            'message':         'Attendance marked successfully.',
            'distance_metres': round(distance),
            'attendance_id':   attendance.id,
        },
        status=status.HTTP_201_CREATED
    )


# ════════════════════════════════════════════════════════════
#  LIST REGISTERED DEVICES
# ════════════════════════════════════════════════════════════

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def webauthn_list_credentials(request):
    """
    GET /api/webauthn/credentials/

    Returns all biometric devices registered by the authenticated user.
    Used to populate the 'Biometric Login' card on the profile page.

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


# ════════════════════════════════════════════════════════════
#  DELETE A REGISTERED DEVICE
# ════════════════════════════════════════════════════════════

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def webauthn_delete_credential(request, credential_id):
    """
    DELETE /api/webauthn/credentials/{id}/

    Removes a registered biometric credential.
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

    The lecturer must verify the student's identity in person
    before calling this endpoint.

    Auth required: Yes (Token) — Lecturer or Admin only

    Returns:
        200  { message }
        403  { error }  — not a lecturer or admin
        404  { error }  — student not found
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Only admins can reset student biometrics.'},
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
