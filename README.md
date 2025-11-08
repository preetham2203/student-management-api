\# Student Management API



A complete Django REST API for student management with MySQL database, OTP verification, and password encryption.



\## 🚀 Features



\- \*\*Student CRUD Operations\*\* - Create, Read, Update, Delete students

\- \*\*Authentication System\*\* - Login with mobile and password

\- \*\*OTP Verification\*\* - Email and mobile verification

\- \*\*Password Encryption\*\* - Secure password storage with mobile number as salt

\- \*\*RESTful API\*\* - Complete REST endpoints

\- \*\*MySQL Database\*\* - Robust database backend



\## 📋 API Endpoints



\### Student Management

\- `POST /api/students/create/` - Create new student

\- `GET /api/students/` - Get all students

\- `GET /api/students/1/` - Get student by ID

\- `PUT /api/students/1/update/` - Update student

\- `DELETE /api/students/1/delete/` - Delete student



\### Authentication

\- `POST /api/auth/login/` - Student login

\- `POST /api/auth/send-otp/` - Send OTP

\- `POST /api/auth/verify-otp/` - Verify OTP

\- `POST /api/auth/forgot-password/` - Forgot password

\- `POST /api/auth/reset-password/` - Reset password



\## 🛠️ Installation



1\. \*\*Clone the repository\*\*

&nbsp;  ```bash

&nbsp;  git clone https://github.com/preetham2203/student-management-api.git

&nbsp;  cd student-management-api



2.Create virtual environment



bash

python -m venv env

env\\Scripts\\activate  # Windows

\# source env/bin/activate  # Mac/Linux



3.Install dependencies



bash

pip install -r requirements.txt



4.Setup MySQL Database



Create database named student\_management



Update database settings in student\_project/settings.py



5.Run migrations



bash

python manage.py migrate



6.Start development server



bash

python manage.py runserver



🔧 Technologies Used

Backend: Django, Django REST Framework



Database: MySQL



Authentication: Custom OTP system



Encryption: Custom XOR-based encryption



API Testing: Postman



📁 Project Structure

text

student\_project/

├── student\_api/

│   ├── models.py          # Database models

│   ├── views.py           # API views

│   ├── serializers.py     # Data serializers

│   ├── urls.py            # App URLs

│   └── utils/

│       └── encryption.py  # Password encryption

├── student\_project/

│   └── settings.py        # Django settings

└── manage.py

👨‍💻 Author

Preetham



GitHub: @preetham2203



📄 License

This project is open source and available under the MIT License.

