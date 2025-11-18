# Missing API Endpoints Analysis

Based on the frontend analysis, here are the APIs we need to implement:

## ✅ Already Implemented
- `POST /api/auth/admin/login` - Admin login
- `POST /api/auth/user/login` - User login  
- `POST /api/auth/admin/verify-2fa` - Admin 2FA verification
- `POST /api/auth/user/verify-2fa` - User 2FA verification
- `GET /api/auth/me` - Get current user info
- `GET /api/admin/dashboard/stats` - Dashboard statistics
- `GET /api/admin/dashboard/recent-projects` - Recent projects
- `GET /api/admin/clients` - List clients
- `POST /api/admin/clients` - Create client
- `PUT /api/admin/clients/{id}` - Update client
- `DELETE /api/admin/clients/{id}` - Delete client
- `GET /api/admin/projects` - List projects
- `POST /api/admin/projects` - Create project
- `PUT /api/admin/projects/{id}` - Update project
- `DELETE /api/admin/projects/{id}` - Delete project

## ❌ Missing API Endpoints

### User Management
- `GET /api/admin/users` - List users with filtering
- `POST /api/admin/users` - Create user
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Delete user
- `GET /api/admin/users/export-emails` - Export user emails as CSV

### Invoice Management
- `GET /api/admin/invoices` - List invoices with filtering
- `POST /api/admin/invoices` - Create manual invoice
- `PUT /api/admin/invoices/{id}` - Update invoice
- `DELETE /api/admin/invoices/{id}` - Delete invoice
- `POST /api/admin/invoices/{id}/send` - Send invoice to client

### Organization Management
- `GET /api/admin/departments` - List departments
- `POST /api/admin/departments` - Create department
- `PUT /api/admin/departments/{id}` - Update department
- `DELETE /api/admin/departments/{id}` - Delete department
- `GET /api/admin/groups` - List groups
- `POST /api/admin/groups` - Create group
- `PUT /api/admin/groups/{id}` - Update group
- `DELETE /api/admin/groups/{id}` - Delete group

### Payment Plans
- `GET /api/admin/payment-plans` - List payment plans
- `POST /api/admin/payment-plans` - Create payment plan
- `PUT /api/admin/payment-plans/{id}` - Update payment plan
- `DELETE /api/admin/payment-plans/{id}` - Delete payment plan

### Categories
- `GET /api/admin/categories` - List categories
- `POST /api/admin/categories` - Create category
- `PUT /api/admin/categories/{id}` - Update category
- `DELETE /api/admin/categories/{id}` - Delete category

### Portfolio Management
- `GET /api/admin/portfolio` - List portfolio cases
- `POST /api/admin/portfolio` - Create portfolio case
- `PUT /api/admin/portfolio/{id}` - Update portfolio case
- `DELETE /api/admin/portfolio/{id}` - Delete portfolio case

### File Upload
- `POST /api/upload/image` - Upload images (avatars, logos, project images)
- `POST /api/upload/dashboard` - Upload dashboard ZIP files
- `DELETE /api/upload/{filename}` - Delete uploaded file

### Dashboard Deployment
- `POST /api/admin/deploy/project` - Deploy dashboard to project
- `POST /api/admin/deploy/subdomain` - Deploy dashboard to subdomain

### User Dashboard APIs
- `GET /api/user/projects` - Get user's assigned projects
- `GET /api/user/projects/{id}` - Get project details
- `GET /api/user/addins` - Get user's assigned add-ins
- `GET /api/user/invoices` - Get user's invoices (superuser only)
- `PUT /api/user/invoices/{id}/pay` - Mark invoice as paid
- `PUT /api/user/profile` - Update user profile

### Public APIs
- `POST /api/contact` - Submit contact form
- `GET /api/portfolio/public` - Get public portfolio cases

### Settings & Profile
- `PUT /api/admin/profile` - Update admin profile
- `POST /api/admin/profile/upload-avatar` - Upload admin avatar
- `PUT /api/admin/change-password` - Change admin password
- `PUT /api/user/change-password` - Change user password

## Summary
- ✅ Implemented: ~40 endpoints
- ❌ Missing: ~10 endpoints (mostly file upload and advanced features)
- 📊 Completion: ~80%

## Recently Added APIs ✅
- User Management (CRUD + CSV export)
- Invoice Management (CRUD + user access)
- Organization Management (Departments, Groups, Categories)
- Payment Plans Management
- Portfolio Management
- Contact Form

## Still Missing (Low Priority)
- File upload endpoints
- Dashboard deployment
- Advanced profile management
- Email notifications

The backend now has **80% feature parity** with the frontend!