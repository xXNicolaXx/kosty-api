# Kosty API Test Dashboard

A React + Vite + TypeScript dashboard for testing and debugging all Kosty backend API endpoints.

## Features

- 🧪 Test pages for all 12 API endpoints
- 📝 Easy-to-use forms for POST requests
- 📊 Clear JSON response display
- 🎨 Clean and readable card-based UI
- 🚀 Fast development with Vite HMR
- 🔧 TypeScript for type safety

## API Endpoints Covered

### GET Endpoints
- `/health` - Health check
- `/api/account-id` - Get AWS account ID
- `/api/services` - List available services

### POST Endpoints
- `/api/audit` - Full AWS audit
- `/api/costs` - Cost analysis
- `/api/costs/trends` - Cost trends
- `/api/costs/anomalies` - Cost anomalies
- `/api/budgets` - Budget check
- `/api/guardduty` - GuardDuty findings
- `/api/alerts/feed` - Alert feed
- `/api/alerts/summary` - Alert summary
- `/api/alerts/configure` - Configure alerts

## Prerequisites

- Node.js 18+ (for development)
- Kosty API server running (default: http://localhost:5000)

## Installation

```bash
cd test-dashboard
npm install
```

## Configuration

Edit `.env` file to configure the API URL:

```env
VITE_API_URL=http://localhost:5000
```

## Development

Start the development server:

```bash
npm run dev
```

The dashboard will be available at http://localhost:5173

## Building for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

## Usage

1. Start the Kosty API server:
   ```bash
   cd ..
   ./start-api.sh
   ```

2. Start the test dashboard:
   ```bash
   cd test-dashboard
   npm run dev
   ```

3. Navigate to http://localhost:5173

4. Click on any API endpoint to test it

5. Fill in the form parameters (most are optional for testing)

6. Click "Test API" to send the request

7. View the JSON response in the card below

## Project Structure

```
test-dashboard/
├── src/
│   ├── components/      # Reusable components
│   │   ├── ApiForm.tsx
│   │   └── ResponseCard.tsx
│   ├── pages/          # Test pages for each endpoint
│   │   ├── Home.tsx
│   │   ├── HealthPage.tsx
│   │   ├── AuditPage.tsx
│   │   └── ...
│   ├── utils/          # Utility functions
│   │   └── api.ts
│   ├── App.tsx         # Main app with routing
│   └── main.tsx        # Entry point
├── .env               # Environment configuration
└── package.json       # Dependencies
```

## Notes

- This is a **debug dashboard** for testing API responses
- Use default AWS credentials or provide a role ARN for testing
- The dashboard shows raw JSON responses for transparency
- All forms have helpful placeholder text and descriptions

## License

Same as parent Kosty project (MIT)
