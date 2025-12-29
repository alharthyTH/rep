from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_key: str = ""
    google_application_credentials: str = ""
    openai_api_key: str = ""
    openai_org_id: str = ""
    openai_project_id: str = ""
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = ""
    test_mode: bool = False
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
