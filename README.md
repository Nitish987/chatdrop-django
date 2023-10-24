# Chatdrop

Social media server developed by Nitish Kumar.

### Features Apis

- Authentication api

- OAuth (with google sign in) api

- Profile api

- Post api

- Stories api

- Reels api

- Friends api

- Fan Following api

- Chats (with single layer encryption) api

- Secret Chats (with end-to-end encryption using signal-protocol) api

- Olivia Ai (powered with chatgpt) api

- Search api

- Notifications api

- Privacy and Blocking System api

- Security (using AES-256 bit encryption) api

### Getting Started

- Create .env file with the following code in it.

```
HOST_IP = 'HOST_IP'

SECRET_KEY = 'SECRET_KEY'
JWT_SECRET = 'JWT_SECRET'
CHATDROP_API_KEY = 'CHATDROP_API_KEY'
SERVER_ENC_KEY = 'SERVER_ENC_KEY'
ACCOUNT_CREATION_KEY = 'ACCOUNT_CREATION_KEY'

DATABASE_NAME = 'CHATDROP_DATABASE_NAME'
DATABASE_USER = 'DATABASE_USER'
DATABASE_PASSWORD = 'DATABASE_PASSWORD'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '3306'

REDIS_PASSWORD = 'REDIS_PASSWORD'

GS_MEDIA_BUCKET_NAME = 'GS_MEDIA_BUCKET_NAME'
GS_PROJECT_ID = 'GS_PROJECT_ID'

OPENAI_API_KEY = 'OPENAI_API_KEY'

CDN_MEDIA_URL = 'CDN_MEDIA_URL'

EMAIL_HOST = 'EMAIL_HOST'
EMAIL_PORT = '587'
EMAIL_USER = 'EMAIL_USER'
EMAIL_PASSWORD = 'EMAIL_PASSWORD'
```

- This server requires firebase admin, google cloud storage, google cloud cdn and google cloud vision connectivity. Create firebase and google cloud admin credentials and paste the files in chatdrop directory renaming as firebase_credentials.json and gcloud_credentials.json respectively.

### Related Repositories

- [Chatdrop Mobile App](https://github.com/Nitish987/chatdrop-flutter)

- [Chatdrop Web App](https://github.com/Nitish987/chatdrop-react)