import os
import sys
import django

# Add the root directory of your Django project to sys.path
sys.path.append('/Users/evyatarhermesh/Desktop/PythonFullStack/Trade Bot/BotVer1')  # Replace with the path to your project root

# Set the environment variable for the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproj.settings')  # Replace 'myproj.settings' with the correct settings module

# Initialize Django
django.setup()

# Now import your models after Django setup
from django.contrib.auth.models import User
from base.models import UserSetting  # Replace 'base' with your actual app name

def test_encryption_decryption():
    # Create a test user (if not already exists)
    username = "testuser"
    password = "testpassword"
    user, created = User.objects.get_or_create(username=username, defaults={"password": password})

    # Create or get UserSetting for the user
    user_settings, created = UserSetting.objects.get_or_create(user=user)

    # Original API key and secret
    original_api_key = "test_api_key_123456"
    original_api_secret = "test_api_secret_abcdef"

    # Set and encrypt API keys
    user_settings.alpaca_api_key = original_api_key
    user_settings.alpaca_api_secret = original_api_secret
    user_settings.save()

    # Fetch the UserSetting again
    user_settings.refresh_from_db()

    # Decrypt and retrieve the API keys
    decrypted_api_key = user_settings.alpaca_api_key
    decrypted_api_secret = user_settings.alpaca_api_secret

    # Output the results
    print(f"Original API Key: {original_api_key}")
    print(f"Decrypted API Key: {decrypted_api_key}")
    print(f"Original API Secret: {original_api_secret}")
    print(f"Decrypted API Secret: {decrypted_api_secret}")

    # Test if the decrypted keys match the original keys
    assert decrypted_api_key == original_api_key, "API Key decryption failed!"
    assert decrypted_api_secret == original_api_secret, "API Secret decryption failed!"

    print("Encryption/Decryption test passed!")

if __name__ == "__main__":
    test_encryption_decryption()
