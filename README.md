# microsop# MicroSOP – AI-Powered SOP Generator

MicroSOP is a SaaS platform that helps solo service providers and small teams generate smart, AI-driven SOPs (Standard Operating Procedures), client checklists, and automated communications.

## 🚀 Features

- ✨ AI-generated SOPs, emails, and checklists
- 🔐 OAuth2 secure authentication
- 💬 Twilio integration for SMS alerts
- 💳 Stripe billing for subscriptions (Basic & Premium)
- 🌍 Multilingual support (PT / EN)
- 🐳 Dockerized for easy deployment
- 🧪 Free trial with verified payment method

## 🛠️ Tech Stack

- **Backend:** Django · Django REST Framework · PostgreSQL
- **Frontend:** React · TailwindCSS · Vite
- **AI:** OpenAI GPT
- **Payments:** Stripe API
- **SMS:** Twilio API
- **Deployment:** Railway (backend) · Netlify/Vercel (frontend)
- **Auth:** OAuth2 with Django Allauth

## 🐳 Local Setup (Docker)

```bash
git clone https://github.com/juganstar/microsop.git
cd microsop
cp .env.example .env
docker compose up --build
