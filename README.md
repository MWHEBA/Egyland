# Egyland - Agricultural Export Platform

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
git clone https://github.com/MWHEBA/Egyland.git
cd Egyland
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

4. Setup database
- Create a PostgreSQL database
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

## Development Guidelines

- Use modular templates with base.html and blocks
- Use includes for reusable components
- Keep HTML separate from CSS/SCSS
- Follow snake_case in Python, camelCase in JS
- Validate all user input
- Update README.md with structural changes

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

## Contributing

We welcome contributions! Please follow these steps:

1. Open an issue to discuss the proposed change
2. Fork the repository
3. Create a new branch for your feature (`git checkout -b feature/amazing-feature`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For more information, please contact:
- User: MWHEBA
- Email: [example@example.com](mailto:example@example.com)

---

Developed by [MWHEBA](https://github.com/MWHEBA). 