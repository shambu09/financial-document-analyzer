# Financial Document Analyzer Client

A modern React application for managing financial documents with AI-powered analysis capabilities. Built with React, TypeScript, shadcn/ui, and integrated with a FastAPI backend.

## Features

- **Authentication**: Secure user registration and login with JWT tokens
- **Document Management**: Upload, view, download, and delete financial documents
- **AI Analysis**: Multiple analysis types including comprehensive, investment, risk assessment, and verification
- **Real-time Progress Tracking**: Live progress indicators for analysis tasks with task status monitoring
- **Report Management**: View and manage analysis reports with filtering and pagination
- **Task Status Monitoring**: Real-time task status updates with automatic polling
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
│   │   └── progress-indicator.tsx # Progress indicator component
│   ├── Layout.tsx      # Main layout component
│   └── ReportCard.tsx  # Report card with progress tracking
├── contexts/           # React contexts
│   └── AuthContext.tsx # Authentication context
├── hooks/              # Custom React hooks
│   ├── use-toast.ts    # Toast notification hook
│   └── useTaskStatus.ts # Task status monitoring hook
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
- **Task Management**: Real-time task status monitoring and progress tracking

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
- `GET /tasks/{id}/status` - Get task status
- `POST /tasks/{id}/cancel` - Cancel task
- `GET /tasks/active` - Get active tasks
- `GET /task-mappings/by-report/{id}` - Get task mapping by report

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
- Real-time progress tracking with visual indicators
- Task status monitoring (pending, in_progress, completed, failed, retrying, cancelled)

### Reports
- View all analysis reports with filtering
- Search reports by filename, query, or summary
- Download completed reports
- Pagination for large datasets
- Real-time progress indicators for in-progress tasks
- Task status monitoring with automatic polling (10-second intervals)
- Visual progress bars with status-specific colors and icons
- Task information display (task ID, worker, queue, retries)

### Progress Tracking
- **Real-time Updates**: Live progress indicators that update automatically
- **Task Status Monitoring**: Automatic polling every 10 seconds for active tasks
- **Visual Indicators**: 
  - Progress bars with percentage completion
  - Status-specific colors (green for completed, blue for in-progress, red for failed)
  - Animated icons for different states
- **Task Information**: Display task ID, worker, queue, and retry count
- **Smart Polling**: Automatically stops polling when tasks complete or fail
- **Status Labels**: Clear status text (Processing, Retrying, Completed, Failed, etc.)

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