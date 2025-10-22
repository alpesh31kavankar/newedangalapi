


from pydantic import BaseModel, EmailStr

# Step 1 → Send OTP request
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# Step 2 → Verify OTP
class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp_code: str


# Step 3 → Reset Password
class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str
