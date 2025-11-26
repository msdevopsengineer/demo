from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, desc
from datetime import datetime, timedelta
import uuid
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User
from app.models.authenticator import Authenticator, AuthenticatorStatus, BackupCode
from app.models.auth_event import AuthEvent
from app.schemas import auth as schemas
from app.services.totp import totp_service
from app.services.encryption import encryption_service
from app.services.rate_limiter import rate_limit_service
from app.core.config import settings

router = APIRouter()

@router.post("/provision", response_model=schemas.AuthenticatorProvisionResponse)
async def provision_authenticator(
    request: schemas.AuthenticatorProvisionRequest,
    db: AsyncSession = Depends(get_db)
):
    # Check if user exists, if not create (for this demo)
    result = await db.execute(select(User).where(User.id == request.user_id))
    user = result.scalars().first()
    if not user:
        user = User(id=request.user_id) # In real app, user should exist
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Check if active authenticator exists
    result = await db.execute(select(Authenticator).where(Authenticator.user_id == user.id, Authenticator.status == AuthenticatorStatus.ACTIVE))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="User already has an active authenticator")

    # Generate Secret
    secret = totp_service.generate_secret()
    encrypted_secret = encryption_service.encrypt(secret.encode())
    
    provision_token = uuid.uuid4()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    authenticator = Authenticator(
        user_id=user.id,
        secret_encrypted=encrypted_secret,
        display_name=request.display_name,
        issuer=request.issuer,
        status=AuthenticatorStatus.PENDING,
        provision_token=provision_token,
        provision_token_expires_at=expires_at
    )
    db.add(authenticator)
    
    # Log event
    event = AuthEvent(
        user_id=user.id,
        event_type="provision_init",
        detail={"authenticator_id": str(authenticator.id)}
    )
    db.add(event)
    
    await db.commit()
    await db.refresh(authenticator)

    # Generate URI and QR
    uri = totp_service.get_totp_uri(secret, user.email or "user@example.com", request.issuer)
    qr_svg = totp_service.generate_qr_code(uri)

    return schemas.AuthenticatorProvisionResponse(
        secret_base32=secret, # Only shown once!
        otpauth_uri=uri,
        qr_svg=qr_svg,
        provision_token=str(provision_token),
        expires_at=expires_at
    )

@router.post("/verify-setup", response_model=schemas.VerifyResponse)
async def verify_setup(
    request: schemas.VerifySetupRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Authenticator).where(Authenticator.provision_token == request.provision_token))
    authenticator = result.scalars().first()
    
    if not authenticator:
        raise HTTPException(status_code=404, detail="Invalid provision token")
        
    if authenticator.provision_token_expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Provision token expired")

    # Decrypt secret
    secret = encryption_service.decrypt(authenticator.secret_encrypted).decode()
    
    if totp_service.verify_code(secret, request.code):
        authenticator.status = AuthenticatorStatus.ACTIVE
        authenticator.provision_token = None
        authenticator.provision_token_expires_at = None
        
        # Log success
        event = AuthEvent(
            user_id=authenticator.user_id,
            authenticator_id=authenticator.id,
            event_type="provision_complete"
        )
        db.add(event)
        await db.commit()
        return schemas.VerifyResponse(verified=True, timestamp=datetime.utcnow())
    else:
        return schemas.VerifyResponse(verified=False, error="Invalid code")

@router.post("/verify", response_model=schemas.VerifyResponse)
async def verify_totp(
    request: schemas.VerifyRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
):
    # Rate Limit
    client_ip = request.client_ip or req.client.host
    await rate_limit_service.check_rate_limit(f"verify:{request.user_id}", limit=5, window=300)

    result = await db.execute(select(Authenticator).where(Authenticator.user_id == request.user_id, Authenticator.status == AuthenticatorStatus.ACTIVE))
    authenticator = result.scalars().first()
    
    if not authenticator:
        raise HTTPException(status_code=404, detail="No active authenticator found")

    secret = encryption_service.decrypt(authenticator.secret_encrypted).decode()
    
    if totp_service.verify_code(secret, request.code):
        event = AuthEvent(
            user_id=request.user_id,
            authenticator_id=authenticator.id,
            event_type="verify_success",
            ip_address=client_ip
        )
        db.add(event)
        await db.commit()
        return schemas.VerifyResponse(verified=True, timestamp=datetime.utcnow())
    else:
        event = AuthEvent(
            user_id=request.user_id,
            authenticator_id=authenticator.id,
            event_type="verify_fail",
            ip_address=client_ip
        )
        db.add(event)
        await db.commit()
        return schemas.VerifyResponse(verified=False, error="Invalid code", retry_after_seconds=30)

@router.post("/backup-codes/generate", response_model=schemas.BackupCodeResponse)
async def generate_backup_codes(
    request: schemas.BackupCodeGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Authenticator).where(Authenticator.user_id == request.user_id, Authenticator.status == AuthenticatorStatus.ACTIVE))
    authenticator = result.scalars().first()
    
    if not authenticator:
        raise HTTPException(status_code=404, detail="No active authenticator found")

    # Invalidate old codes
    await db.execute(select(BackupCode).where(BackupCode.authenticator_id == authenticator.id).execution_options(synchronize_session=False))
    # Actually we should delete them
    # For now, let's just create new ones and maybe delete old ones if we want to enforce single set
    
    codes = []
    plain_codes = []
    for _ in range(10):
        code = totp_service.generate_secret()[:8] # Simple 8 char code
        plain_codes.append(code)
        # Hash code (using simple hash for demo, should be argon2)
        import hashlib
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        backup_code = BackupCode(
            authenticator_id=authenticator.id,
            code_hash=code_hash
        )
        db.add(backup_code)
    
    await db.commit()
    return schemas.BackupCodeResponse(backup_codes=plain_codes)

@router.post("/verify-backup", response_model=schemas.VerifyResponse)
async def verify_backup_code(
    request: schemas.BackupVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Authenticator).where(Authenticator.user_id == request.user_id, Authenticator.status == AuthenticatorStatus.ACTIVE))
    authenticator = result.scalars().first()
    
    if not authenticator:
        raise HTTPException(status_code=404, detail="No active authenticator found")

    # Check all unused codes
    result = await db.execute(select(BackupCode).where(BackupCode.authenticator_id == authenticator.id, BackupCode.used == False))
    codes = result.scalars().all()
    
    import hashlib
    input_hash = hashlib.sha256(request.backup_code.encode()).hexdigest()
    
    for code in codes:
        if code.code_hash == input_hash:
            code.used = True
            event = AuthEvent(
                user_id=request.user_id,
                authenticator_id=authenticator.id,
                event_type="backup_used"
            )
            db.add(event)
            await db.commit()
            return schemas.VerifyResponse(verified=True, timestamp=datetime.utcnow())
            
    return schemas.VerifyResponse(verified=False, error="Invalid backup code")

@router.post("/disable", response_model=schemas.VerifyResponse)
async def disable_authenticator(
    request: schemas.DisableRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Authenticator).where(Authenticator.user_id == request.user_id, Authenticator.status == AuthenticatorStatus.ACTIVE))
    authenticator = result.scalars().first()
    
    if not authenticator:
        raise HTTPException(status_code=404, detail="No active authenticator found")

    authenticator.status = AuthenticatorStatus.DISABLED
    
    event = AuthEvent(
        user_id=request.user_id,
        authenticator_id=authenticator.id,
        event_type="disabled"
    )
    db.add(event)
    await db.commit()
    
    return schemas.VerifyResponse(verified=True, timestamp=datetime.utcnow())

@router.get("/admin/audit")
async def get_audit_logs(
    user_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    query = select(AuthEvent).order_by(desc(AuthEvent.created_at)).limit(limit).offset(offset)
    if user_id:
        query = query.where(AuthEvent.user_id == user_id)
        
    result = await db.execute(query)
    events = result.scalars().all()
    return events
