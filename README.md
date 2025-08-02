# IoT Payload Parser

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django-coding-challenge
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```
   Or use the default admin account:
   - Username: `admin`
   - Password: `admin123`

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://localhost:8000`

## API Documentation

### Authentication

All API endpoints require token authentication. Get a token by making a POST request to `/api/token/`:

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Include the token in subsequent requests:
```bash
curl -H "Authorization: Token <your-token>" http://localhost:8000/api/devices/
```

### Endpoints

#### 1. Receive Payload
**POST** `/api/receive/`

Receives and processes IoT device payloads.

**Request Body:**
```json
{
  "fCnt": 100,
  "devEUI": "abcdabcdabcdabcd",
  "data": "AQ==",
  "rxInfo": [
    {
      "gatewayID": "1234123412341234",
      "name": "G1",
      "time": "2022-07-19T11:00:00",
      "rssi": -57,
      "loRaSNR": 10
    }
  ],
  "txInfo": {
    "frequency": 86810000,
    "dr": 5
  }
}
```

**Response:**
```json
{
  "message": "Payload received and processed successfully",
  "payload": {
    "id": 1,
    "device": 1,
    "fCnt": 100,
    "data": "AQ==",
    "data_hex": "01",
    "is_passing": true,
    "rx_info": [...],
    "tx_info": {...},
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### 2. List Devices
**GET** `/api/devices/`

Returns all devices with their latest status.

#### 3. Get Device Details
**GET** `/api/devices/{devEUI}/`

Returns detailed information about a specific device.

#### 4. Get Device Payloads
**GET** `/api/devices/{devEUI}/payloads/`

Returns all payloads for a specific device.

#### 5. List Payloads
**GET** `/api/payloads/`

Returns all payloads. Can be filtered by device:
```
GET /api/payloads/?devEUI=abcdabcdabcdabcd
```

#### 6. Get Payload Details
**GET** `/api/payloads/{id}/`

Returns detailed information about a specific payload.

## Testing

### Using the Test Script

Run the provided test script to verify functionality:

```bash
python test_payload.py
```

This script will:
- Authenticate with the API
- Send passing and failing payloads
- Test duplicate payload rejection
- Test invalid Base64 data handling
- Retrieve and display results

### Manual Testing with curl

1. **Get authentication token:**
   ```bash
   curl -X POST http://localhost:8000/api/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
   ```

2. **Send a payload:**
   ```bash
   curl -X POST http://localhost:8000/api/receive/ \
     -H "Authorization: Token <your-token>" \
     -H "Content-Type: application/json" \
     -d '{
       "fCnt": 100,
       "devEUI": "abcdabcdabcdabcd",
       "data": "AQ==",
       "rxInfo": [],
       "txInfo": {}
     }'
   ```

3. **View devices:**
   ```bash
   curl -H "Authorization: Token <your-token>" \
     http://localhost:8000/api/devices/
   ```

## Error Handling

The application handles various error scenarios:

- **Duplicate Payloads**: Returns 400 error if `fCnt` already exists for the device
- **Invalid Base64**: Returns 400 error for malformed Base64 data
- **Missing Fields**: Returns 400 error for required fields
- **Authentication**: Returns 401 error for invalid or missing tokens
