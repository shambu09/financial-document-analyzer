# Financial Document Analyzer Client

A modern React application for managing financial documents with AI-powered analysis capabilities. Built with React, TypeScript, shadcn/ui, and integrated with a FastAPI backend.

## Features

- **Authentication**: Secure user registration and login with JWT tokens
- **Document Management**: Upload, view, download, and delete financial documents
- **AI Analysis**: Multiple analysis types including comprehensive, investment, risk assessment, and verification
- **Report Management**: View and manage analysis reports with filtering and pagination
- **User Profile**: Manage account settings and change passwords
- **Responsive Design**: Mobile-friendly interface with modern UI components

## Tech Stack

- **Frontend**: React 19, TypeScript, Vite
- **UI Components**: shadcn/ui, Tailwind CSS
- **State Management**: React Query (TanStack Query)
- **Forms**: React Hook Form with Zod validation
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd document-management-app
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Update the `.env` file with your API configuration:
```
VITE_API_BASE_URL=http://localhost:8000
VITE_DEBUG=false
```

5. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`.

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── ui/             # shadcn/ui components
│   └── Layout.tsx      # Main layout component
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication context
├── hooks/              # Custom React hooks
│   └── use-toast.ts    # Toast notification hook
├── lib/                # Utility functions
│   ├── api.ts          # API client configuration
│   └── utils.ts        # Utility functions
├── pages/              # Page components
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── DashboardPage.tsx
│   ├── DocumentsPage.tsx
│   ├── AnalysisPage.tsx
│   ├── ReportsPage.tsx
│   └── ProfilePage.tsx
├── types/              # TypeScript type definitions
│   └── index.ts
├── App.tsx             # Main app component
└── main.tsx           # Application entry point
```

## API Integration

The application integrates with a FastAPI backend that provides:

- **Authentication**: User registration, login, logout, and profile management
- **Document Management**: Upload, list, download, and delete documents
- **Analysis**: AI-powered document analysis with multiple analysis types
- **Reports**: Generate, list, and manage analysis reports

### API Endpoints

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/me` - Get current user info
- `PUT /auth/me` - Update user info
- `POST /auth/change-password` - Change password
- `GET /documents/` - List documents
- `POST /documents/upload` - Upload document
- `GET /documents/download/{filename}` - Download document
- `DELETE /documents/{filename}` - Delete document
- `POST /analysis/{type}` - Start analysis
- `GET /reports/` - List reports
- `GET /reports/{id}` - Get specific report
- `DELETE /reports/{id}` - Delete report

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Features Overview

### Dashboard
- Overview of documents and analysis reports
- Quick statistics and recent activity
- Quick action buttons for common tasks

### Document Management
- Upload documents (PDF, TEXT)
- Search and filter documents
- Download and delete documents
- File size and upload date information

### AI Analysis
- Multiple analysis types:
  - **Comprehensive**: Complete financial document analysis
  - **Investment**: Investment opportunities and recommendations
  - **Risk Assessment**: Risk evaluation and mitigation strategies
  - **Verification**: Document validation and authenticity
- Custom query support for specific analysis requirements
- Real-time progress tracking

### Reports
- View all analysis reports with filtering
- Search reports by filename, query, or summary
- Download completed reports
- Pagination for large datasets
- Status tracking (pending, completed, failed)

### User Profile
- Update personal information
- Change password
- View account details and status
- Account creation date and activity

## Styling

The application uses Tailwind CSS with a custom design system based on shadcn/ui components. The design is:

- **Responsive**: Mobile-first approach with responsive breakpoints
- **Accessible**: WCAG compliant with proper ARIA labels
- **Modern**: Clean, professional interface with smooth animations
- **Consistent**: Unified design language across all components

## Error Handling

- Form validation with real-time feedback
- API error handling with user-friendly messages
- Toast notifications for success and error states
- Loading states for better user experience

## Security

- JWT token-based authentication
- Automatic token refresh
- Secure password handling
- Protected routes and API endpoints
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.