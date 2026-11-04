
import streamlit as st

from config import get_missing_api_keys
from pdf_generator import generate_pdf
from email_service import send_post_email


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI LinkedIn Post Generator",
    page_icon="✍️",
    layout="centered"
)

st.title("✍️ AI LinkedIn Post Generator")

st.write(
    "Generate professional LinkedIn posts using two AI agents."
)

st.markdown(
    "**Powered by:** Gemini | GPT-OSS 120B (Groq) | "
    "LangGraph | Tavily Search"
)

st.divider()


# --------------------------------------------------
# API KEY VALIDATION
# --------------------------------------------------

missing_keys = get_missing_api_keys()

if missing_keys:
    st.error(
        "Missing API keys in your .env file: "
        + ", ".join(missing_keys)
    )
    st.stop()


# Import workflow after checking API keys.
from workflow import generate_post


# --------------------------------------------------
# INPUT FORM
# --------------------------------------------------

with st.form("generate_post_form"):

    topic = st.text_input(
        "Enter your LinkedIn post topic",
        placeholder="Example: How AI is transforming healthcare",
        key="topic_input"
    )

    generate_clicked = st.form_submit_button(
        "Generate LinkedIn Post",
        use_container_width=True
    )


# --------------------------------------------------
# GENERATE POST
# --------------------------------------------------

if generate_clicked:

    submitted_topic = topic.strip()

    if not submitted_topic:

        st.warning("Please enter a topic.")

    else:

        # Clear previous results.
        keys_to_clear = [
            "post_result",
            "post_topic",
            "email_sent",
            "email_attempted",
            "email_error",
            "pdf_bytes"
        ]

        for key in keys_to_clear:
            st.session_state.pop(key, None)

        st.session_state["post_topic"] = submitted_topic

        try:

            with st.spinner(
                f"Generating a post about: {submitted_topic}"
            ):

                result = generate_post(submitted_topic)

            # Preserve the latest draft.
            latest_draft = (
                result.get("draft")
                or result.get("last_draft")
                or ""
            )

            result["draft"] = latest_draft

            st.session_state["post_result"] = result
            st.session_state["email_sent"] = False
            st.session_state["email_attempted"] = False
            st.session_state["email_error"] = None

            # --------------------------------------------------
            # APPROVED POST: GENERATE PDF AND SEND EMAIL
            # --------------------------------------------------

            if result.get("approved") and latest_draft.strip():

                with st.spinner(
                    "Post approved! Creating PDF and sending email..."
                ):

                    pdf_bytes = generate_pdf(
                        submitted_topic,
                        latest_draft
                    )

                    st.session_state["pdf_bytes"] = pdf_bytes
                    st.session_state["email_attempted"] = True

                    try:

                        send_post_email(
                            submitted_topic,
                            pdf_bytes
                        )

                        st.session_state["email_sent"] = True

                    except Exception as email_error:

                        st.session_state["email_error"] = str(
                            email_error
                        )

            elif not latest_draft.strip():

                st.warning(
                    "The workflow finished, but no draft was returned. "
                    "Please check the terminal for errors."
                )

        except Exception as exc:

            st.error(
                f"Generation failed for '{submitted_topic}': {exc}"
            )


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

if "post_result" in st.session_state:

    result = st.session_state["post_result"]

    current_topic = st.session_state["post_topic"]

    latest_draft = (
        result.get("draft")
        or result.get("last_draft")
        or ""
    )

    st.divider()

    st.subheader("Generated LinkedIn Post")

    st.markdown(f"**Topic:** {current_topic}")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Writing Attempts",
            result.get("attempts", 0)
        )

    with col2:

        st.metric(
            "Reviewer Status",
            "Approved" if result.get("approved") else "Not Approved"
        )

    # --------------------------------------------------
    # APPROVED RESULT
    # --------------------------------------------------

    if result.get("approved"):

        st.success(
            "Your LinkedIn post has been approved."
        )

        st.markdown("### Final LinkedIn Post")

        st.text_area(
            "Generated content",
            value=latest_draft,
            height=350,
            disabled=True,
            key="approved_post_preview"
        )

        # Email status.
        if st.session_state.get("email_sent"):

            st.success(
                "The approved PDF was automatically sent to your email."
            )

        elif st.session_state.get("email_error"):

            st.error(
                "Automatic email delivery failed: "
                + st.session_state["email_error"]
            )

            # Retry email.
            if (
                st.session_state.get("pdf_bytes")
                and st.button("Retry Email Delivery")
            ):

                try:

                    with st.spinner("Retrying email delivery..."):

                        send_post_email(
                            current_topic,
                            st.session_state["pdf_bytes"]
                        )

                    st.session_state["email_sent"] = True
                    st.session_state["email_error"] = None

                    st.rerun()

                except Exception as exc:

                    st.error(
                        f"Email delivery failed: {exc}"
                    )

        # PDF download.
        if "pdf_bytes" in st.session_state:

            st.download_button(
                "Download Final PDF",
                data=st.session_state["pdf_bytes"],
                file_name="LinkedIn_Post.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    # --------------------------------------------------
    # REJECTED RESULT
    # --------------------------------------------------

    else:

        st.warning(
            "The post was not approved after "
            f"{result.get('attempts', 0)} review attempts."
        )

        st.markdown("### Latest Reviewer Feedback")

        feedback = result.get("feedback", "")

        if feedback:
            st.markdown(feedback)
        else:
            st.write("No reviewer feedback available.")

        st.markdown("### Latest Generated Draft")

        if latest_draft.strip():

            st.text_area(
                "Latest draft",
                value=latest_draft,
                height=350,
                disabled=True,
                key="rejected_post_preview"
            )

        else:

            st.error(
                "The latest draft is empty. "
                "Check the terminal output for the underlying error."
            )

        # Display complete reviewer response for debugging.
        with st.expander("View complete reviewer response"):

            st.write(
                result.get(
                    "reviewer_response",
                    "No reviewer response available."
                )
            )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Built with Streamlit, LangGraph, Gemini, Groq, "
    "Tavily and ReportLab."
)
