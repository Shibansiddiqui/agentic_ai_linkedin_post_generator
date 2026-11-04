# ✍️ AI LinkedIn Post Generator

An AI-powered application that automatically researches, generates, reviews, and delivers professional LinkedIn posts using a multi-agent workflow.

## 🚀 Features

- **AI Content Generation:** Creates LinkedIn posts using Google Gemini.
- **Web Research:** Uses Tavily Search to gather relevant information.
- **AI Review:** GPT-OSS 120B (via Groq) reviews posts for quality, accuracy, and engagement.
- **Iterative Refinement:** LangGraph manages the writing and review loop with up to 3 attempts.
- **PDF Generation:** Converts approved posts into downloadable PDFs.
- **Email Automation:** Automatically emails approved PDFs using Gmail SMTP.
- **Interactive UI:** Simple interface built with Streamlit.

## 🛠️ Tech Stack

Python | Streamlit | LangChain | LangGraph | Gemini | Groq | Tavily Search | ReportLab

## 📁 Project Structure

```text
linkedinpost_genrator/
├── app.py
├── config.py
├── agents.py
├── workflow.py
├── pdf_generator.py
├── email_service.py
├── requirements.txt
├── .env
└── .gitignore
```

## ⚙️ Installation

**1. Clone the repository**

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd linkedinpost_genrator
```

**2. Create and activate a virtual environment**

```bash
python -m venv newproject
```

Windows:

```powershell
.\newproject\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key
LLM_MODEL=gemini-2.5-flash
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
TAVILY_API_KEY=your_tavily_api_key

SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password
RECEIVER_EMAIL=your_email@gmail.com
```

**5. Run the application**

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## 🔄 Workflow

1. User enters a LinkedIn post topic.
2. Tavily searches for relevant information.
3. Gemini generates the initial post.
4. GPT-OSS reviews the generated content.
5. LangGraph routes the post for revision or approval.
6. Approved posts are converted into PDFs and emailed automatically.

## 🔐 Security

- API keys and email credentials are stored in `.env`.
- Never commit `.env` or expose API keys publicly.
- Use `.gitignore` to protect sensitive configuration.

## 👨‍💻 Author

**Shiban Siddiqui**

AI Engineer | Generative AI | Agentic AI | Machine Learning