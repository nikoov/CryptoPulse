import os
import requests
from dotenv import load_dotenv
import base64

def test_reddit_api():
    load_dotenv()
    
    # Load credentials
    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    
    # Create authorization header
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    
    # Get access token
    headers = {
        'Authorization': f'Basic {auth}',
        'User-Agent': 'CryptoPulse/1.0'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    
    response = requests.post(
        'https://www.reddit.com/api/v1/access_token',
        headers=headers,
        data=data
    )
    
    if response.status_code == 200:
        print("Successfully obtained access token!")
        token_data = response.json()
        print(f"Access token: {token_data.get('access_token')}")
        
        # Test API access
        headers = {
            'Authorization': f'Bearer {token_data["access_token"]}',
            'User-Agent': 'CryptoPulse/1.0'
        }
        
        # Try to get posts from r/bitcoin
        response = requests.get(
            'https://oauth.reddit.com/r/bitcoin/hot',
            headers=headers
        )
        
        if response.status_code == 200:
            print("\nSuccessfully retrieved posts from r/bitcoin!")
            posts = response.json()
            print(f"Number of posts retrieved: {len(posts['data']['children'])}")
        else:
            print(f"\nFailed to get posts. Status code: {response.status_code}")
            print(f"Error: {response.text}")
    else:
        print(f"Failed to get access token. Status code: {response.status_code}")
        print(f"Error: {response.text}")

if __name__ == '__main__':
    test_reddit_api() 