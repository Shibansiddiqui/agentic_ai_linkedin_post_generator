
import json
import re
from typing import TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

from config import (
    GEMINI_MODEL,
    GROQ_MODEL,
    GOOGLE_API_KEY,
    GROQ_API_KEY,
)


class LinkedInState(TypedDict):
    topic: str
    search_results: str
    draft: str
    last_draft: str
    feedback: str
    reviewer_response: str
    approved: bool
    attempts: int


def content_to_text(content):
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))

        return "\n".join(parts)

    return "" if content is None else str(content)


def result_to_text(result):
    if isinstance(result, str):
        return result

    try:
        return json.dumps(
            result,
            ensure_ascii=False,
            indent=2
        )
    except Exception:
        return str(result)


# Initialize AI models
writer_llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3
)

reviewer_llm = ChatGroq(
    model=GROQ_MODEL,
    groq_api_key=GROQ_API_KEY,
    temperature=0.1
)

# Initialize Tavily search
tavily_search = TavilySearch(max_results=3)


def writer_node(state: LinkedInState):

    topic = state["topic"]

    # Search only once. Reuse the same research during revisions.
    search_results = state.get("search_results", "")

    if not search_results:
        search_response = tavily_search.invoke({
            "query": topic
        })

        search_results = result_to_text(search_response)

    previous_draft = state.get("draft", "")
    feedback = state.get("feedback", "")

    if feedback:

        task = f"""
You are revising an existing LinkedIn post.

ORIGINAL TOPIC:
{topic}

PREVIOUS DRAFT:
{previous_draft}

REVIEWER FEEDBACK:
{feedback}

REVISION INSTRUCTIONS:
1. Address every correction requested by the reviewer.
2. Correct factual errors and incorrect source attribution.
3. Remove statistics if their source cannot be verified from the research.
4. Never invent research sources, statistics or references.
5. Improve wording, grammar, readability and professionalism.
6. Preserve useful parts of the original draft.
7. Do not change the original topic.
8. Return the complete revised LinkedIn post.
"""

    else:

        task = f"""
Create a professional LinkedIn post about:

{topic}

REQUIREMENTS:
1. Start with an engaging opening hook.
2. Use a professional but conversational tone.
3. Include useful insights and examples.
4. Use short, readable paragraphs.
5. End with a strong closing or call to action.
6. Include 3-5 relevant hashtags.
7. Avoid unnecessary emojis.
8. Do not invent facts, statistics or research sources.
9. Use only information supported by the research.
10. If a statistic cannot be verified, do not include it.
"""

    prompt = f"""
You are an experienced LinkedIn content strategist.

RESEARCH INFORMATION:
{search_results}

WRITING TASK:
{task}

IMPORTANT:
Return ONLY the complete LinkedIn post.
Do not include explanations, review notes or comments.
"""

    response = writer_llm.invoke(prompt)

    draft = content_to_text(response.content).strip()

    if not draft:
        raise ValueError(
            "Gemini returned an empty LinkedIn post."
        )

    return {
        "search_results": search_results,
        "draft": draft,
        "last_draft": draft,
        "feedback": ""
    }


def reviewer_node(state: LinkedInState):

    prompt = f"""
You are a strict professional LinkedIn content reviewer.

TOPIC:
{state["topic"]}

LINKEDIN POST:
{state["draft"]}

AVAILABLE RESEARCH:
{state["search_results"]}

Review the post using these criteria:

1. Relevance to the topic.
2. Professional quality and tone.
3. Factual accuracy and source attribution.
4. Clarity and readability.
5. Grammar and structure.
6. Engagement and opening hook.
7. Hashtags and call to action.

IMPORTANT REVIEW RULES:

- Check whether statistics and claims are supported by the available research.
- Reject incorrect source attribution.
- Reject unsupported statistics or fabricated sources.
- Give specific corrections that the writer can apply.
- Do not reject merely because you would personally use different wording.
- Approve a post if it meets professional standards.

Return your answer in exactly this format:

VERDICT: APPROVED or REJECTED

FEEDBACK:
Explain your decision.
If rejected, list the specific corrections required.
If approved, briefly explain why the post is acceptable.
"""

    response = reviewer_llm.invoke(prompt)

    review = content_to_text(response.content).strip()

    match = re.search(
        r"VERDICT\s*:\s*(APPROVED|REJECTED)",
        review,
        re.IGNORECASE
    )

    verdict = (
        match.group(1).upper()
        if match
        else "REJECTED"
    )

    feedback_match = re.search(
        r"FEEDBACK\s*:\s*(.*)",
        review,
        re.IGNORECASE | re.DOTALL
    )

    feedback = (
        feedback_match.group(1).strip()
        if feedback_match
        else review
    )

    return {
        "draft": state.get("draft", ""),
        "last_draft": state.get("draft", ""),
        "reviewer_response": review,
        "approved": verdict == "APPROVED",
        "feedback": feedback,
        "attempts": state.get("attempts", 0) + 1
    }
