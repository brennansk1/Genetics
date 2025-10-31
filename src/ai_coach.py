import os

import streamlit as st

from src.utils import CONFIG

# Try to import LangChain and OpenAI
try:
    from langchain.chains import ConversationChain
    from langchain.memory import ConversationBufferMemory
    from langchain_openai import ChatOpenAI

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


def initialize_ai_coach():
    """
    Initialize the AI Coach with LangChain and OpenAI.
    Returns the conversation chain if successful, None otherwise.
    """
    if not CONFIG["ux_enhancements"]["enable_ai_coach"]:
        return None

    if not LANGCHAIN_AVAILABLE:
        st.warning("LangChain or OpenAI dependencies not installed. AI Coach disabled.")
        return None

    api_key = CONFIG["api_keys"]["openai_api_key"]
    if not api_key:
        st.warning(
            "OpenAI API key not found. Please set OPENAI_API_KEY environment variable. AI Coach disabled."
        )
        return None

    try:
        # Initialize the LLM
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, openai_api_key=api_key)

        # Create conversation chain with memory
        memory = ConversationBufferMemory()
        conversation = ConversationChain(llm=llm, memory=memory, verbose=False)

        # Set initial context for genetic health coaching
        initial_prompt = """
        You are an AI-powered Genetic Health Coach. You help users understand their genetic data and health implications.
        You provide evidence-based explanations about genetic variants, their potential health impacts, and general wellness advice.
        Always emphasize that you are not a substitute for professional medical advice, and users should consult healthcare providers for personalized medical decisions.
        Be conversational, supportive, and educational. Use simple language to explain complex genetic concepts.
        """

        conversation.memory.chat_memory.add_user_message("System: " + initial_prompt)
        conversation.memory.chat_memory.add_ai_message(
            "Understood. I'm ready to help you understand your genetic health data."
        )

        return conversation

    except Exception as e:
        st.error(f"Failed to initialize AI Coach: {str(e)}")
        return None


def get_ai_response(conversation_chain, user_query, dna_context=None):
    """
    Get response from AI Coach for user query.
    dna_context can be a string summary of relevant genetic data.
    """
    if not conversation_chain:
        return "AI Coach is not available."

    try:
        # Add DNA context if provided
        if dna_context:
            enhanced_query = (
                f"User's genetic context: {dna_context}\n\nUser question: {user_query}"
            )
        else:
            enhanced_query = user_query

        response = conversation_chain.predict(input=enhanced_query)
        return response

    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}. Please try again."


def render_ai_coach(dna_data):
    """
    Render the AI Coach interface in the main area.
    """
    st.title("🤖 AI Genetic Health Coach")

    if not CONFIG["ux_enhancements"]["enable_ai_coach"]:
        st.info("AI Coach is disabled. Enable it in configuration to use this feature.")
        return

    # Initialize coach if not already done
    if "ai_coach" not in st.session_state:
        st.session_state.ai_coach = initialize_ai_coach()

    coach = st.session_state.ai_coach

    if not coach:
        st.error("AI Coach could not be initialized.")
        return

    # Chat interface
    st.markdown(
        "Ask me anything about your genetic results! I'm here to help you understand your DNA data in a conversational way."
    )

    # Display chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.write(f"**You:** {message['content']}")
            else:
                st.write(f"**Coach:** {message['content']}")

    # Input for new question
    user_input = st.text_input("Your question:", key="ai_question_main")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Ask Coach", key="ask_coach_main"):
            if user_input.strip():
                # Add user message to history
                st.session_state.chat_history.append(
                    {"role": "user", "content": user_input}
                )

                # Get DNA context (simple summary for now)
                dna_summary = (
                    f"User has genetic data with {len(dna_data)} SNPs analyzed."
                )

                # Get AI response
                response = get_ai_response(coach, user_input, dna_summary)

                # Add AI response to history
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )

                # Rerun to update display
                st.rerun()
            else:
                st.warning("Please enter a question.")

    with col2:
        if st.button("Clear Chat", key="clear_chat_main"):
            st.session_state.chat_history = []
            # Reset conversation memory
            if coach:
                coach.memory.clear()
            st.rerun()


def render_ai_coach_sidebar(dna_data):
    """
    Render the AI Coach interface in the sidebar.
    """
    st.sidebar.title("🤖 AI Genetic Health Coach")

    if not CONFIG["ux_enhancements"]["enable_ai_coach"]:
        st.sidebar.info(
            "AI Coach is disabled. Enable it in configuration to use this feature."
        )
        return

    # Initialize coach if not already done
    if "ai_coach" not in st.session_state:
        st.session_state.ai_coach = initialize_ai_coach()

    coach = st.session_state.ai_coach

    if not coach:
        st.sidebar.error("AI Coach could not be initialized.")
        return

    # Chat interface
    st.sidebar.markdown("Ask me anything about your genetic results!")

    # Display chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.sidebar.write(f"**You:** {message['content']}")
        else:
            st.sidebar.write(f"**Coach:** {message['content']}")

    # Input for new question
    user_input = st.sidebar.text_input("Your question:", key="ai_question")

    if st.sidebar.button("Ask Coach", key="ask_coach"):
        if user_input.strip():
            # Add user message to history
            st.session_state.chat_history.append(
                {"role": "user", "content": user_input}
            )

            # Get DNA context (simple summary for now)
            dna_summary = f"User has genetic data with {len(dna_data)} SNPs analyzed."

            # Get AI response
            response = get_ai_response(coach, user_input, dna_summary)

            # Add AI response to history
            st.session_state.chat_history.append(
                {"role": "assistant", "content": response}
            )

            # Rerun to update display
            st.rerun()
        else:
            st.sidebar.warning("Please enter a question.")

    # Clear chat button
    if st.sidebar.button("Clear Chat", key="clear_chat"):
        st.session_state.chat_history = []
        # Reset conversation memory
        if coach:
            coach.memory.clear()
        st.rerun()
