# Egyland Agricultural Export Platform

Professional platform for an Egyptian agricultural export company built with Django and Tailwind CSS.

## Key Features

- Dynamic product catalog with fresh/IQF handling
- Monthly seasonality charts per product/variety
- Modular, component-based frontend
- Admin dashboard for full content control
- Responsive design for all device sizes
- SEO-optimized

## Tech Stack

- Python 3.12+
- Django 4.2.7
- PostgreSQL
- Tailwind CSS
- Vanilla JavaScript
- HTML5 & Django Templates

## Installation

1. Clone the repository
```bash
git clone <repository-url>
cd egyland
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Setup database (PostgreSQL)
- Create a database as per the instructions in `setup_db.sql`
- Configure database connection in `config/.env`

5. Run migrations and create superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. Run the development server
```bash
python manage.py runserver
```

7. Access the website at http://127.0.0.1:8000/

## Project Structure

- `apps/`: Module applications
  - `core/`: Main site pages and functionality
  - `products/`: Product catalog and detail pages
  - `admin/`: Custom admin dashboard
  - `accounts/`: User accounts (future)
- `config/`: Project configuration
- `templates/`: HTML templates
- `static/`: Static assets (CSS, JS, images)
- `media/`: User-uploaded content
- `logs/`: Application logs

## Content Management

The site is fully managed through the admin interface at `/admin`. Key content sections:

1. Products
   - Add/edit products and their details
   - Manage seasonality, counts, sizes, packaging

2. Inquiries
   - View and manage contact messages
   - Handle quote requests

## Packaging System

The system supports an enhanced packaging management approach:

1. **Packaging Types**
   - Reusable packaging types with images (e.g., "Wooden boxes - 30pcs")
   - Each type has a key word (e.g., "boxes") for dynamic labeling
   - Types can be marked for Fresh products, IQF products, or both

2. **Product Packaging Types**
   - Associates products with packaging types
   - Configurable specifications:
     - Items per pallet (using the key word)
     - Pallets per container
     - Net weight and units
   - Display options (e.g., show "Fresh" label)

3. **Display**
   - Packaging displays similarly to counts and sizes
   - Visual representation with images and structured data
   - Consistent user experience across product specifications

## Development Guidelines

- Use modular templates with base.html and blocks
- Use includes for reusable components
- Keep HTML separate from CSS/SCSS
- Follow snake_case in Python, camelCase in JS
- Validate all user input 
- Update README.md with structural changes 

## Running the Application on Windows

Due to specific limitations in Windows PowerShell, here's how to correctly run the application:

### Using PowerShell

PowerShell doesn't support the `&&` operator for command chaining like bash does. Use these commands instead:

```powershell
# Change to the project directory
cd C:\Users\MohYousif\Egyland

# Start the Django development server
python manage.py runserver
```

To activate a virtual environment before running the server:

```powershell
# Activate the virtual environment (if you're using one)
.\venv\Scripts\Activate.ps1

# Then run the server
python manage.py runserver
```

### For Product Packaging Types Management

When working with Product Packaging Types, ensure that:

1. All required fields are filled out properly
2. The selected Product and Packaging Type combination with the same Product Type doesn't already exist
3. All numeric values (especially Net Weight) are valid numbers

After saving the form, you should be redirected back to the product packaging types list with your new entry visible in the table.

## Troubleshooting

If you encounter issues with PowerShell and command chaining, use separate commands or create a batch file (.bat) with the commands for easier execution.

## Tailwind CSS Setup

Egyland now uses a locally compiled version of Tailwind CSS instead of the CDN. This is the recommended approach for production environments.

### Setup Instructions

1. Make sure Node.js and npm are installed on your system
2. Install the required packages:
   ```bash
   npm install
   ```
3. Build the CSS file:
   ```bash
   npm run build:css
   ```
4. For development with auto-refresh:
   ```bash
   npm run dev
   ```

The compiled CSS file will be at `static/css/tailwind.min.css` and is already configured in the templates.

### Fallback Solution

If Node.js is not available or you're experiencing issues with Tailwind compilation, a fallback solution has been implemented:

1. A pre-compiled version of Tailwind is included at `static/css/tailwind.min.css`
2. A custom CSS file with all the necessary Tailwind utilities is provided at `static/css/tailwind-custom.css`
3. Both files are linked in all templates to ensure consistent styling

This approach ensures that the site will look correct even without running the Node.js build process.

### Local Fonts Setup

To avoid issues with Google Fonts and improve loading performance, the project now uses local fonts:

1. Download the required font files (WOFF2 and WOFF formats):
   - Poppins (weights: 300, 400, 500, 600, 700)
   - Raleway (weights: 400, 600, 800)
   - Inter (weights: 400, 500, 700)

2. Place the font files in the `static/fonts/` directory following the naming convention in `static/css/fonts.css`

3. If you can't obtain the font files, the site will fall back to system fonts defined in `static/css/font-fallback.css`

All templates have been updated to use these local font definitions.

## تحسينات الموبايل

تم إضافة تحسينات للصفحة الرئيسية على الأجهزة المحمولة. لاستخدام هذه التحسينات:

1. قم بتثبيت Sass إذا لم يكن موجودًا بالفعل:
   ```
   npm install -g sass
   ```

2. قم بتشغيل أمر التطوير الذي يراقب كلاً من ملفات Tailwind CSS و SCSS:
   ```
   npm run dev
   ```

3. أو يمكنك تجميع ملفات SCSS فقط:
   ```
   npm run build:scss
   ```

تشمل التحسينات الرئيسية للموبايل:
- تحسين العناوين والنصوص لتكون أكثر قابلية للقراءة على الشاشات الصغيرة
- دعم السحب لتغيير الشرائح في العرض الرئيسي
- إصلاح مشكلة ارتفاع الشاشة الكاملة (100vh) في متصفحات الموبايل
- تحسين تفاعل القائمة المتنقلة للموبايل
- تأثيرات انتقالية محسّنة 