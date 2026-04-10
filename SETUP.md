# TrendVault Setup Guide

TrendVault is a dropshipping e-commerce store built with Flask, Stripe, and automated product discovery.

## Quick Start (3 Commands)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

The store will start on `http://localhost:5000`

Admin panel: `http://localhost:5000/admin` (default password: `change_me_before_launch`)

### 3. Sync Products (Optional)
In the admin dashboard, click "Sync Products" to automatically fetch trending products from AliExpress and populate your store.

## Configuration

Edit `config.json` to customize:

- **Store Settings**: Name, tagline, currency
- **Payments**: Stripe API keys (optional, works in demo mode without)
- **AI Integration**: Gemini API key for product description generation
- **Supplier**: AliExpress affiliate credentials (optional)
- **Product Discovery**: Search keywords, pricing rules, automation schedule

## What's Included

- Full e-commerce store with product catalog, shopping cart, and checkout
- Dark theme with responsive design (mobile-friendly)
- Admin dashboard for managing products, orders, and syncing
- SQLite database for products and orders
- Automated product discovery from AliExpress (optional)
- Stripe payment integration (works in test mode)
- AI-powered product descriptions (optional with Gemini API)

## Features

- Browse and search products
- Add items to cart
- Secure checkout with Stripe or demo mode
- Order tracking and confirmation
- Admin panel with dashboard, product management, and order history
- Background product sync scheduler
- Responsive design for mobile and desktop

## Environment Setup (Optional)

For production deployment, set these environment variables:

```bash
export FLASK_DEBUG=false
export PORT=5000
export FLASK_ENV=production
```

## Support

For issues or questions, check the configuration file and ensure all required dependencies are installed.

Happy selling!
