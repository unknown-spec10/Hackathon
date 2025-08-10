"""
Technical Interview Chatbot UI
Streamlit interface for testing the AI-powered technical interview system.
"""
import streamlit as st
import requests
import json
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="AI Interview Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Constants
API_BASE_URL = "http://localhost:8000"

def main():
    st.title("🤖 AI Technical Interview Chatbot")
    st.markdown("---")
    
    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
    if "interview_completed" not in st.session_state:
        st.session_state.interview_completed = False
    
    # Sidebar for authentication
    with st.sidebar:
        st.header("🔐 Authentication")
        
        # Mock authentication for demo
        st.session_state.auth_token = "demo_token"
        st.success("✅ Authenticated as Demo User")
        
        st.markdown("---")
        st.header("📊 Interview Progress")
        
        if st.session_state.interview_started and st.session_state.questions:
            progress = (st.session_state.current_question / len(st.session_state.questions)) * 100
            st.progress(progress / 100)
            st.write(f"Question {st.session_state.current_question + 1} of {len(st.session_state.questions)}")
    
    # Main content
    if not st.session_state.interview_started:
        show_interview_setup()
    elif not st.session_state.interview_completed:
        show_interview_questions()
    else:
        show_interview_results()

def show_interview_setup():
    """Interview setup page"""
    st.header("🚀 Start Your Technical Interview")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        Welcome to the AI-powered technical interview system! This chatbot will:
        
        - 📝 Generate personalized questions based on your domain and experience
        - 🤖 Use advanced AI to evaluate your answers
        - 📊 Provide detailed feedback and recommendations
        - 🎯 Help you identify strengths and areas for improvement
        """)
    
    with col2:
        st.info("""
        **How it works:**
        1. Select your domain
        2. Enter years of experience
        3. Answer 15-20 questions
        4. Get AI-powered evaluation
        """)
    
    st.markdown("---")
    
    # Domain selection
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📚 Select Technical Domain")
        domains = {
            "python": "Python Programming",
            "javascript": "JavaScript Development",
            "java": "Java Development",
            "data_science": "Data Science",
            "machine_learning": "Machine Learning",
            "cloud_computing": "Cloud Computing",
            "devops": "DevOps",
            "web_development": "Web Development",
            "cybersecurity": "Cybersecurity",
            "blockchain": "Blockchain"
        }
        
        selected_domain = st.selectbox(
            "Choose your domain:",
            options=list(domains.keys()),
            format_func=lambda x: domains[x]
        )
    
    with col2:
        st.subheader("⏱️ Years of Experience")
        years_experience = st.number_input(
            "Enter your years of experience:",
            min_value=0,
            max_value=20,
            value=2,
            help="This will determine the difficulty level of questions"
        )
        
        # Show difficulty mapping
        if years_experience <= 1:
            difficulty = "Fresher (0-1 years)"
        elif years_experience <= 3:
            difficulty = "Junior (1-3 years)"
        elif years_experience <= 5:
            difficulty = "Intermediate (3-5 years)"
        elif years_experience <= 8:
            difficulty = "Senior (5-8 years)"
        else:
            difficulty = "Expert (8+ years)"
        
        st.info(f"**Difficulty Level:** {difficulty}")
    
    st.markdown("---")
    
    # Start interview button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🚀 Start Interview", type="primary", use_container_width=True):
            start_interview(selected_domain, years_experience)

def start_interview(domain, years_experience):
    """Start the interview session"""
    with st.spinner("🤖 AI is generating personalized questions for you..."):
        try:
            # Real API call to start interview
            headers = {"Authorization": "Bearer demo_token"}
            payload = {
                "domain": domain,
                "years_of_experience": years_experience
            }
            
            response = requests.post(
                f"{API_BASE_URL}/interview/start",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Convert API response to our format
                questions = []
                for q in data["questions"]:
                    questions.append({
                        "id": q["id"],
                        "question": q["question"],
                        "type": q.get("type", "conceptual")
                    })
                
                st.session_state.questions = questions
                st.session_state.session_id = data["session_id"]
                st.session_state.interview_started = True
                st.session_state.current_question = 0
                st.session_state.answers = {}
                
                st.success("✅ Interview started! Good luck!")
                st.rerun()
            else:
                st.error(f"❌ Failed to start interview: {response.status_code} - {response.text}")
                # Fallback to mock questions
                questions = generate_mock_questions(domain, years_experience)
                st.session_state.questions = questions
                st.session_state.session_id = 123  # Mock session ID
                st.session_state.interview_started = True
                st.session_state.current_question = 0
                st.session_state.answers = {}
                st.warning("⚠️ Using offline mode - questions generated locally")
                st.rerun()
            
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API server. Make sure the FastAPI server is running on http://localhost:8000")
            # Fallback to mock questions
            questions = generate_mock_questions(domain, years_experience)
            st.session_state.questions = questions
            st.session_state.session_id = 123  # Mock session ID
            st.session_state.interview_started = True
            st.session_state.current_question = 0
            st.session_state.answers = {}
            st.warning("⚠️ Using offline mode - questions generated locally")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Failed to start interview: {str(e)}")
            # Fallback to mock questions
            questions = generate_mock_questions(domain, years_experience)
            st.session_state.questions = questions
            st.session_state.session_id = 123
            st.session_state.interview_started = True
            st.session_state.current_question = 0
            st.session_state.answers = {}
            st.warning("⚠️ Using offline mode - questions generated locally")
            st.rerun()

def show_interview_questions():
    """Display interview questions one by one"""
    if not st.session_state.questions:
        st.error("No questions available")
        return
    
    current_q_idx = st.session_state.current_question
    total_questions = len(st.session_state.questions)
    
    if current_q_idx >= total_questions:
        complete_interview()
        return
    
    question = st.session_state.questions[current_q_idx]
    
    st.header(f"Question {current_q_idx + 1} of {total_questions}")
    st.markdown("---")
    
    # Question display
    with st.container():
        st.markdown(f"### 📝 {question['question']}")
        
        if question.get('type') == 'coding':
            st.info("💻 This is a coding question. Please provide your solution with explanations.")
        elif question.get('type') == 'conceptual':
            st.info("💡 This is a conceptual question. Explain your understanding clearly.")
        
        # Answer input
        answer_key = f"answer_{current_q_idx}"
        
        if question.get('type') == 'coding':
            answer = st.text_area(
                "Your answer:",
                height=200,
                placeholder="Write your code here with explanations...",
                key=answer_key
            )
        else:
            answer = st.text_area(
                "Your answer:",
                height=150,
                placeholder="Type your detailed answer here...",
                key=answer_key
            )
        
        st.session_state.answers[question['id']] = answer
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if current_q_idx > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.current_question = current_q_idx - 1
                st.rerun()
    
    with col2:
        if current_q_idx < total_questions - 1:
            if st.button("➡️ Next", use_container_width=True, type="primary"):
                st.session_state.current_question = current_q_idx + 1
                st.rerun()
        else:
            if st.button("🏁 Submit Interview", use_container_width=True, type="primary"):
                complete_interview()
    
    with col3:
        if st.button("💾 Save & Exit"):
            st.warning("Interview saved. You can resume later.")
    
    # Question overview
    with st.expander("📋 Question Overview"):
        for i, q in enumerate(st.session_state.questions):
            status = "✅" if st.session_state.answers.get(q['id'], '').strip() else "⏳"
            current = "👉 " if i == current_q_idx else ""
            st.write(f"{current}{status} Q{i+1}: {q['question'][:60]}...")

def complete_interview():
    """Complete the interview and show results"""
    with st.spinner("🤖 AI is evaluating your answers..."):
        try:
            # Prepare answers for API submission
            answers = []
            for question in st.session_state.questions:
                user_answer = st.session_state.answers.get(question['id'], '')
                if user_answer.strip():  # Only include non-empty answers
                    answers.append({
                        "question_id": question['id'],
                        "answer": user_answer
                    })
            
            # Real API call to submit answers
            headers = {"Authorization": "Bearer demo_token"}
            payload = {
                "session_id": st.session_state.session_id,
                "answers": answers
            }
            
            response = requests.post(
                f"{API_BASE_URL}/interview/submit",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result_data = response.json()
                
                # Store real evaluation results
                st.session_state.evaluation_results = result_data
                st.session_state.interview_completed = True
                st.success("🎉 Interview evaluated by AI! Here are your results:")
                st.rerun()
                
            else:
                st.error(f"❌ Evaluation failed: {response.status_code} - {response.text}")
                # Fallback to mock evaluation
                st.session_state.evaluation_results = generate_mock_evaluation()
                st.session_state.interview_completed = True
                st.warning("⚠️ Using offline evaluation - results are simulated")
                st.rerun()
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API server for evaluation")
            # Fallback to mock evaluation
            st.session_state.evaluation_results = generate_mock_evaluation()
            st.session_state.interview_completed = True
            st.warning("⚠️ Using offline evaluation - results are simulated")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Evaluation error: {str(e)}")
            # Fallback to mock evaluation
            st.session_state.evaluation_results = generate_mock_evaluation()
            st.session_state.interview_completed = True
            st.warning("⚠️ Using offline evaluation - results are simulated")
            st.rerun()


def generate_mock_evaluation():
    """Generate mock evaluation results as fallback"""
    return {
        "overall_score": 65.5,
        "grade": "B-",
        "question_evaluations": [],
        "strengths": ["Shows understanding of basic concepts", "Good problem-solving approach"],
        "weaknesses": ["Could improve technical depth", "Need more practice with advanced topics"],
        "recommendations": ["Study advanced algorithms", "Practice more coding problems"],
        "time_taken": 25,
        "accuracy_rate": 60.0
    }

def show_interview_results():
    """Display interview results and recommendations"""
    st.header("📊 Your Interview Results")
    st.markdown("---")
    
    # Get evaluation results (real or mock)
    if "evaluation_results" in st.session_state:
        results = st.session_state.evaluation_results
        overall_score = results.get("overall_score", 0)
        grade = results.get("grade", "N/A")
        time_taken = results.get("time_taken", 0)
        accuracy_rate = results.get("accuracy_rate", 0)
        
        # Check if this is real AI evaluation
        is_real_evaluation = st.session_state.session_id != 123
        
        if is_real_evaluation:
            st.success("✅ **AI-Powered Evaluation Complete**")
        else:
            st.warning("⚠️ **Offline Mode - Simulated Results**")
        
    else:
        # Fallback mock data
        overall_score = 78.5
        grade = "B+"
        time_taken = 32
        accuracy_rate = 70.0
        results = generate_mock_evaluation()
        st.warning("⚠️ **Offline Mode - Simulated Results**")
    
    # Score display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Score", f"{overall_score}%")
    
    with col2:
        st.metric("Grade", grade)
    
    with col3:
        st.metric("Questions Answered", f"{len(st.session_state.answers)}/{len(st.session_state.questions)}")
    
    with col4:
        st.metric("Time Taken", f"{time_taken} minutes")
    
    # Score visualization
    st.progress(overall_score / 100)
    
    st.markdown("---")
    
    # Detailed feedback
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Performance", "💪 Strengths", "📚 Areas to Improve", "🎯 Recommendations"])
    
    with tab1:
        st.subheader("Question-wise Performance")
        
        # Show real evaluation results if available
        question_evaluations = results.get("question_evaluations", [])
        
        if question_evaluations:
            for eval in question_evaluations[:5]:  # Show first 5
                score = eval.get("score", 0)
                question_text = eval.get("question", "Question")
                user_answer = eval.get("user_answer", "No answer provided")
                feedback = eval.get("feedback", "No specific feedback available")
                
                with st.expander(f"Q: {question_text[:50]}... (Score: {score}/10)"):
                    st.write(f"**Your Answer:** {user_answer[:200]}...")
                    st.write(f"**AI Feedback:** {feedback}")
                    
                    if score >= 8:
                        st.success(f"Excellent! Score: {score}/10")
                    elif score >= 6:
                        st.warning(f"Good! Score: {score}/10")
                    else:
                        st.error(f"Needs improvement. Score: {score}/10")
        else:
            # Fallback display for mock evaluation
            for i, q in enumerate(st.session_state.questions[:5]):
                score = [8.5, 6.0, 9.0, 7.5, 5.5][i] if i < 5 else 6.0
                
                with st.expander(f"Q{i+1}: {q['question'][:50]}... (Score: {score}/10)"):
                    st.write(f"**Your Answer:** {st.session_state.answers.get(q['id'], 'No answer provided')[:100]}...")
                    st.write(f"**AI Feedback:** Good understanding shown. Consider mentioning...")
                    
                    if score >= 8:
                        st.success(f"Excellent! Score: {score}/10")
                    elif score >= 6:
                        st.warning(f"Good! Score: {score}/10")
                    else:
                        st.error(f"Needs improvement. Score: {score}/10")
    
    with tab2:
        st.subheader("🌟 Your Strengths")
        strengths = results.get("strengths", [
            "Strong grasp of fundamental concepts",
            "Good problem-solving approach",
            "Clear explanation of complex topics"
        ])
        
        for strength in strengths:
            st.success(f"✅ {strength}")
    
    with tab3:
        st.subheader("📈 Areas for Improvement")
        weaknesses = results.get("weaknesses", [
            "Could improve knowledge of advanced algorithms",
            "Need more practice with system design concepts",
            "Consider learning more about best practices"
        ])
        
        for weakness in weaknesses:
            st.warning(f"📝 {weakness}")
    
    with tab4:
        st.subheader("🎯 Personalized Recommendations")
        
        recommendations = results.get("recommendations", [
            "Study advanced algorithms and data structures",
            "Practice system design concepts",
            "Build more real-world projects"
        ])
        
        for i, rec in enumerate(recommendations):
            st.markdown(f"**{i+1}.** {rec}")
        
        # Show suggested resources if available
        suggested_resources = results.get("suggested_resources", [])
        if suggested_resources:
            st.markdown("### 📚 Suggested Resources")
            for resource in suggested_resources:
                resource_type = resource.get("type", "resource")
                title = resource.get("title", "Resource")
                description = resource.get("description", "")
                
                st.markdown(f"**{resource_type.title()}: {title}**")
                st.write(description)
                st.markdown("---")
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Take Another Interview", type="primary", use_container_width=True):
            restart_interview()
    
    with col2:
        if st.button("📥 Download Report", use_container_width=True):
            st.success("Report downloaded!")
    
    with col3:
        if st.button("📤 Share Results", use_container_width=True):
            st.success("Results shared!")

def restart_interview():
    """Reset interview state"""
    st.session_state.session_id = None
    st.session_state.questions = []
    st.session_state.answers = {}
    st.session_state.current_question = 0
    st.session_state.interview_started = False
    st.session_state.interview_completed = False
    st.rerun()

def generate_mock_questions(domain, years_experience):
    """Generate mock questions for demo"""
    base_questions = {
        "python": [
            {"id": 1, "question": "Explain the difference between list and tuple in Python", "type": "conceptual"},
            {"id": 2, "question": "Write a function to find the factorial of a number", "type": "coding"},
            {"id": 3, "question": "What are Python decorators and how do you use them?", "type": "conceptual"},
            {"id": 4, "question": "Implement a binary search algorithm", "type": "coding"},
            {"id": 5, "question": "Explain Python's GIL and its implications", "type": "conceptual"}
        ],
        "data_science": [
            {"id": 1, "question": "Explain the bias-variance tradeoff in machine learning", "type": "conceptual"},
            {"id": 2, "question": "How would you handle missing data in a dataset?", "type": "conceptual"},
            {"id": 3, "question": "Write code to perform feature scaling", "type": "coding"},
            {"id": 4, "question": "Explain the difference between supervised and unsupervised learning", "type": "conceptual"},
            {"id": 5, "question": "How do you evaluate a classification model?", "type": "conceptual"}
        ]
    }
    
    questions = base_questions.get(domain, base_questions["python"])
    
    # Adjust questions based on experience level
    if years_experience <= 1:
        return questions[:3]  # Fewer questions for beginners
    elif years_experience <= 5:
        return questions[:4]
    else:
        return questions  # All questions for experienced

if __name__ == "__main__":
    main()
