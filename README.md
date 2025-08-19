🚀 MicroSOP — AI-Powered SOP Generator

📌 Overview

MicroSOP is a work-in-progress SaaS platform designed to help service providers and small teams generate professional SOPs (Standard Operating Procedures), checklists, and client communication assets in seconds.
The mission is simple: reduce the time from idea to delivery by letting AI handle the formatting and structure, so you can focus on the actual work. will have multiple structures to increase productivity.

🛠 Tech Stack
Backend: Django + Django REST Framework

Frontend: HTMX + TailwindCSS

Database: PostgreSQL

AI Integration: OpenAI API

Payments: Stripe (subscriptions & usage-based)

Messaging: Twilio (SMS notifications)

Containerization: Docker & Docker Compose

CI/CD: GitHub Actions (tests, linting, deployments)

🚧 Project Status

✅ Dockerized backend with development & production parity
✅ Basic authentication flow (in progress)
✅ CI/CD pipeline for linting & tests (in progress)
🚀 AI content generation logic (coming soon)
🚀 Stripe billing & usage tracking (coming soon)
🚀 Polished UI with TailwindCSS (coming soon)

📦 Local Development Setup

bash

# 1. Clone the repository
git clone https://github.com/yourusername/microsop.git
cd microsop

# 2. Copy example environment file
cp .env.dev.example .env.dev

# 3. Build & run with Docker
docker compose -f docker-compose.dev.yml up --build
