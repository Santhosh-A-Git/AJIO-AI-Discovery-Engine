import re

def clean_text(text):
    """
    Removes noise from text: URLs, excessive whitespace, and standardizes newlines.
    """
    if not isinstance(text, str):
        return ""
        
    # Remove URLs
    text = re.sub(r'http\S+|www\.\S+', '[URL_REMOVED]', text)
    
    # Remove HTML tags if any slipped through
    text = re.sub(r'<.*?>', '', text)
    
    # Normalize whitespace (replace multiple spaces/newlines with single space/newline)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'[\n\r]+', '\n', text)
    
    return text.strip()

def scrub_pii(text):
    """
    Anonymizes Personally Identifiable Information (PII) like phone numbers and emails.
    """
    if not isinstance(text, str):
        return ""
        
    # Scrub Emails
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL_REMOVED]', text)
    
    # Scrub Phone Numbers (Indian format focused, e.g., +91, 10 digits)
    text = re.sub(r'(\+91[\-\s]?)?[6-9]\d{9}', '[PHONE_REMOVED]', text)
    
    return text

def process_text(text):
    """
    Master function to clean noise and scrub PII.
    """
    cleaned = clean_text(text)
    safe_text = scrub_pii(cleaned)
    return safe_text
