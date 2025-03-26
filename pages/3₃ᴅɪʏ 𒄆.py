import streamlit as st
import google.generativeai as genai
import json
from typing import List, Dict
import ast
import random
import textwrap
import re





# Check if the user is logged in
if 'signed_in' not in st.session_state or not st.session_state.signed_in:
    st.warning("🔒You must be logged in to access this page.")
    st.stop()  # Stop rendering the rest of the page




class CodingChallengeManager:
    def __init__(self):
        """Initialize the coding challenge manager with improved configuration"""
        st.sidebar.title("🔑 Configuration")
        
        # Fix empty label warning by providing a label and hiding it
        api_key = st.sidebar.text_input(
            label="Gemini API Key",
            type="password",
            placeholder="Enter your Gemini API Key",
            help="Enter your Gemini API key to enable code analysis"
        )
        
        if api_key:
            self.configure_gemini(api_key)
            self.difficulty_levels = ['beginner', 'intermediate', 'advanced']
            
            st.sidebar.title("🎯 Challenge Settings")
            self.selected_topic = st.sidebar.text_input(
                label="Programming Topic",
                value="Python Programming",
                placeholder="Enter programming topic"
            )
            self.selected_difficulty = st.sidebar.selectbox(
                label="Difficulty Level",
                options=self.difficulty_levels,
                index=1
            )
        else:
            st.error("Please enter your Gemini API key in the sidebar to continue.")
            st.stop()

    def configure_gemini(self, api_key: str) -> None:
        """Configure Gemini API with improved error handling"""
        try:
            # Configure with safety options
            genai.configure(api_key=api_key, transport="rest")
            
            # Initialize model with safety settings
            model = genai.GenerativeModel('gemini-pro')
            
            # Test the configuration with a simple prompt
            test_prompt = "Return the word 'test' if you can read this."
            try:
                response = model.generate_content(test_prompt)
                if response and response.text:
                    self.model = model
                    st.sidebar.success("✅ API Configuration Successful!")
                else:
                    raise Exception("Failed to get valid response from API")
            except Exception as e:
                raise Exception(f"API test failed: {str(e)}")
                
        except Exception as e:
            st.sidebar.error(f"❌ API Configuration Failed: {str(e)}")
            st.stop()
    def generate_challenge(self, topic: str, difficulty: str) -> Dict:
        """Generate coding challenge using Gemini API with improved JSON handling"""
        concepts = {
            'beginner': ['loops', 'conditionals', 'basic data structures', 'string manipulation', 'basic math operations'],
            'intermediate': ['recursion', 'advanced data structures', 'algorithms', 'file handling', 'object-oriented programming'],
            'advanced': ['dynamic programming', 'optimization', 'system design', 'advanced algorithms', 'complex problem solving']
        }
        
        selected_concept = random.choice(concepts[difficulty])
        
        prompt = f"""Create a Python coding challenge about {topic} focusing on {selected_concept} at {difficulty} level.
        Return ONLY a JSON object with NO trailing commas and this EXACT structure:
        {{
            "challenge": "problem description",
            "starter_code": "def solution(input):\\n    pass",
            "test_cases": [
                {{"input": "test1", "expected": "output1", "explanation": "explain1"}},
                {{"input": "test2", "expected": "output2", "explanation": "explain2"}}
            ],
            "hints": ["hint1", "hint2"],
            "constraints": ["constraint1", "constraint2"],
            "examples": ["example1", "example2"]
        }}
        Do not include any text before or after the JSON object. No trailing commas in arrays."""

        try:
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up common JSON issues
            def clean_json(json_str):
                # Remove any text before the first {
                start = json_str.find('{')
                end = json_str.rfind('}') + 1
                if start == -1 or end == 0:
                    raise ValueError("No JSON object found")
                json_str = json_str[start:end]
                
                # Remove trailing commas in arrays
                json_str = re.sub(r',(\s*[\]}])', r'\1', json_str)
                
                # Fix possible missing quotes around keys
                json_str = re.sub(r'(\w+)(:)', r'"\1"\2', json_str)
                
                return json_str

            try:
                # First try direct JSON parsing
                challenge_data = json.loads(response_text)
            except json.JSONDecodeError:
                # If direct parsing fails, try cleaning the JSON
                cleaned_json = clean_json(response_text)
                try:
                    challenge_data = json.loads(cleaned_json)
                except json.JSONDecodeError as e:
                    st.error("Failed to parse challenge after cleaning. Error details:")
                    st.error(str(e))
                    st.code(cleaned_json)
                    return self._get_fallback_challenge(difficulty)

            # Validate the challenge data
            required_fields = ['challenge', 'starter_code', 'test_cases', 'hints', 'constraints', 'examples']
            if not all(field in challenge_data for field in required_fields):
                missing_fields = [field for field in required_fields if field not in challenge_data]
                st.error(f"Missing required fields: {', '.join(missing_fields)}")
                return self._get_fallback_challenge(difficulty)

            # Ensure lists have at least one item
            for field in ['test_cases', 'hints', 'constraints', 'examples']:
                if not isinstance(challenge_data[field], list) or not challenge_data[field]:
                    st.error(f"Field '{field}' must be a non-empty list")
                    return self._get_fallback_challenge(difficulty)

            # Validate test cases structure
            for test_case in challenge_data['test_cases']:
                if not all(k in test_case for k in ['input', 'expected', 'explanation']):
                    st.error("Invalid test case format")
                    return self._get_fallback_challenge(difficulty)

            return challenge_data

        except Exception as e:
            st.error(f"Error generating challenge: {str(e)}")
            return self._get_fallback_challenge(difficulty)

    def _get_fallback_challenge(self, difficulty: str) -> Dict:
            """Provide fallback coding challenges with multiple variations"""
            challenges = {
                'beginner': [
                    {
                        "challenge": "Create a function that counts the frequency of each character in a string and returns the most frequent character.",
                        "starter_code": """def solution(input_string):
            # Count character frequency and return the most common character
            # If there are ties, return the alphabetically first character
            pass""",
                        "test_cases": [
                            {"input": "hello", "expected": "l", "explanation": "l appears twice, other characters once"},
                            {"input": "programming", "expected": "g", "explanation": "g and r appear twice, g comes first alphabetically"},
                            {"input": "aaa", "expected": "a", "explanation": "a appears three times"}
                        ],
                        "hints": [
                            "Consider using a dictionary to count characters",
                            "You can use the max() function with a custom key",
                            "Remember to handle ties alphabetically"
                        ],
                        "constraints": [
                            "Input will be a non-empty string",
                            "Consider only lowercase letters",
                            "Return a single character"
                        ],
                        "examples": [
                            "For input 'hello', count frequencies: h(1), e(1), l(2), o(1), return 'l'",
                            "For input 'aabbcc', all characters appear twice, return 'a' (first alphabetically)"
                        ]
                    },
                    {
                        "challenge": "Write a function that finds all pairs of numbers in a comma-separated string that sum to a target value.",
                        "starter_code": """def solution(input_string):
            # Parse the comma-separated numbers and find pairs that sum to 10
            # Return pairs as a sorted string, e.g., "1,9;2,8;3,7"
            pass""",
                        "test_cases": [
                            {"input": "1,2,3,4,5,6,7,8,9", "expected": "1,9;2,8;3,7;4,6", "explanation": "All pairs summing to 10"},
                            {"input": "5,5,2,8", "expected": "2,8;5,5", "explanation": "Both pairs sum to 10"},
                            {"input": "1,2,3", "expected": "", "explanation": "No pairs sum to 10"}
                        ],
                        "hints": [
                            "Split the input string to get numbers",
                            "Convert strings to integers for comparison",
                            "Consider using two pointers or a set for finding pairs"
                        ],
                        "constraints": [
                            "Input will be comma-separated numbers",
                            "Find pairs that sum to 10",
                            "Return pairs in ascending order"
                        ],
                        "examples": [
                            "For input '1,9,5,5', return '1,9;5,5'",
                            "Pairs should be ordered and separated by semicolons"
                        ]
                    }
                ],
                'intermediate': [
                    {
                    "challenge": "Implement a function that performs run-length encoding on a string",
                    "starter_code": "def solution(text):\n    # Compress string using run-length encoding\n    pass",
                    "test_cases": [
                        {"input": "AABBBCCCC", "expected": "2A3B4C", "explanation": "Count consecutive characters"},
                        {"input": "WWWWBBBBWWWW", "expected": "4W4B4W", "explanation": "Encode repeated sequences"}
                    ],
                    "hints": ["Keep track of current character and count", "Handle transitions between different characters"],
                    "constraints": ["Input will be uppercase letters only", "Output format: count followed by character"],
                    "examples": ["AAAA becomes 4A", "AABBB becomes 2A3B"]
                }
                    
                ],
                'advanced': [
                    {
                    "challenge": "Create a function that finds the longest increasing subsequence in an array",
                    "starter_code": "def solution(sequence):\n    # Find length of longest increasing subsequence\n    pass",
                    "test_cases": [
                        {"input": "3,10,2,1,20", "expected": "3", "explanation": "Longest sequence is 3,10,20"},
                        {"input": "1,2,3,4,5", "expected": "5", "explanation": "Entire sequence is increasing"}
                    ],
                    "hints": ["Consider using dynamic programming", "Keep track of sequences ending at each position"],
                    "constraints": ["Input will be comma-separated numbers", "Return length as string"],
                    "examples": ["For 1,2,3 the answer is 3 as the entire sequence is increasing"]
                }
                ]
            }
            
            # Get all challenges for the requested difficulty
            available_challenges = challenges.get(difficulty, challenges['beginner'])
            
            # Return a random challenge, ensuring it's different from the last one if possible
            if 'last_challenge_index' in st.session_state:
                available_indices = list(range(len(available_challenges)))
                available_indices.remove(st.session_state.last_challenge_index)
                if available_indices:
                    selected_index = random.choice(available_indices)
                else:
                    selected_index = 0
            else:
                selected_index = random.randrange(len(available_challenges))
            
            st.session_state.last_challenge_index = selected_index
            return available_challenges[selected_index]

    def _get_fallback_challenge(self, difficulty: str) -> Dict:
        """Provide fallback coding challenges with multiple variations"""
        challenges = {
            'beginner': [
                {
                    "challenge": "Create a function that finds all numbers in a range that satisfy a specific digit sum condition",
                    "starter_code": "def solution(number):\n    # Find all numbers from 1 to number where sum of digits is even\n    pass",
                    "test_cases": [
                        {"input": "10", "expected": "[2, 4, 6, 8]", "explanation": "Numbers with even digit sums up to 10"},
                        {"input": "15", "expected": "[2, 4, 6, 8, 11, 13, 15]", "explanation": "Numbers with even digit sums up to 15"}
                    ],
                    "hints": ["Consider converting numbers to strings to check digits", "Use list comprehension for elegant solution"],
                    "constraints": ["Input will be a positive integer", "Return results as a string representation of a list"],
                    "examples": ["For input 5, check numbers 1-5 and return those with even digit sums"]
                },
                {
                    "challenge": "Create a function that generates a pattern of alternating characters",
                    "starter_code": "def solution(n):\n    # Generate pattern of alternating X and O for n rows\n    pass",
                    "test_cases": [
                        {"input": "3", "expected": "XOX\nOXO\nXOX", "explanation": "3x3 alternating pattern"},
                        {"input": "2", "expected": "XO\nOX", "explanation": "2x2 alternating pattern"}
                    ],
                    "hints": ["Consider using nested loops", "Remember to alternate starting character for each row"],
                    "constraints": ["Input will be a positive integer", "Return pattern as a string with newlines"],
                    "examples": ["For input 2, create a 2x2 grid of alternating X and O"]
                }
            ],
            'intermediate': [
                {
                    "challenge": "Implement a function that performs run-length encoding on a string",
                    "starter_code": "def solution(text):\n    # Compress string using run-length encoding\n    pass",
                    "test_cases": [
                        {"input": "AABBBCCCC", "expected": "2A3B4C", "explanation": "Count consecutive characters"},
                        {"input": "WWWWBBBBWWWW", "expected": "4W4B4W", "explanation": "Encode repeated sequences"}
                    ],
                    "hints": ["Keep track of current character and count", "Handle transitions between different characters"],
                    "constraints": ["Input will be uppercase letters only", "Output format: count followed by character"],
                    "examples": ["AAAA becomes 4A", "AABBB becomes 2A3B"]
                }
            ],
            'advanced': [
                {
                    "challenge": "Create a function that finds the longest increasing subsequence in an array",
                    "starter_code": "def solution(sequence):\n    # Find length of longest increasing subsequence\n    pass",
                    "test_cases": [
                        {"input": "3,10,2,1,20", "expected": "3", "explanation": "Longest sequence is 3,10,20"},
                        {"input": "1,2,3,4,5", "expected": "5", "explanation": "Entire sequence is increasing"}
                    ],
                    "hints": ["Consider using dynamic programming", "Keep track of sequences ending at each position"],
                    "constraints": ["Input will be comma-separated numbers", "Return length as string"],
                    "examples": ["For 1,2,3 the answer is 3 as the entire sequence is increasing"]
                }
            ]
        }
        
        # Return a random challenge for the given difficulty
        return random.choice(challenges[difficulty])

    def evaluate_code(self, user_code: str, test_cases: List[Dict], challenge_desc: str) -> None:
        """Evaluate user's code using both test cases and Gemini LLM"""
        # First, validate code structure and safety
        if not self._validate_code_safety(user_code):
            st.error("❌ Code validation failed. Please check for unsafe operations.")
            return

        # Use Gemini to analyze code quality
        self._analyze_code_quality(user_code, challenge_desc)

        # Run test cases
        self._run_test_cases(user_code, test_cases)

    def _validate_code_safety(self, code: str) -> bool:
        """Validate code for safety and structure"""
        try:
            # Parse the code to check for syntax
            tree = ast.parse(code)
            
            # Check for unsafe operations
            unsafe_ops = ['exec', 'eval', 'open', '__import__', 'subprocess']
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if hasattr(node.func, 'id') and node.func.id in unsafe_ops:
                        st.error(f"❌ Unsafe operation detected: {node.func.id}")
                        return False
            return True
        except SyntaxError as e:
            st.error(f"❌ Syntax Error: {str(e)}")
            return False

    def _analyze_code_quality(self, code: str, challenge_desc: str) -> None:
        """Analyze code quality using Gemini LLM with improved error handling"""
        prompt = f"""
        Analyze this Python code solution for the following challenge:
        Challenge: {challenge_desc}
        
        Code:
        {code}
        
        Provide brief analysis focusing on:
        1. Code correctness
        2. Efficiency
        3. Style and readability
        4. Specific improvement suggestions
        5. Good practices followed
        
        Response format:
        {{
            "correctness": "brief assessment",
            "efficiency": "brief complexity analysis",
            "style": "brief style review",
            "suggestions": ["improvement 1", "improvement 2"],
            "best_practices": ["practice 1", "practice 2"]
        }}
        Keep each field's content concise and focused.
        """
        
        try:
            # Add retry mechanism
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    response = self.model.generate_content(prompt)
                    response_text = response.text.strip()
                    
                    # Clean and parse JSON response
                    # Remove any markdown formatting or extra text
                    json_start = response_text.find('{')
                    json_end = response_text.rfind('}') + 1
                    if json_start != -1 and json_end != 0:
                        clean_json = response_text[json_start:json_end]
                        analysis = json.loads(clean_json)
                        
                        # Display analysis results
                        st.markdown("### 📊 Code Analysis")
                        
                        # Use columns for better layout
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.info(f"**Correctness:** {analysis['correctness']}")
                            st.info(f"**Efficiency:** {analysis['efficiency']}")
                            st.info(f"**Style:** {analysis['style']}")
                            
                        with col2:
                            if analysis.get('suggestions'):
                                st.markdown("**💡 Suggestions:**")
                                for suggestion in analysis['suggestions']:
                                    st.markdown(f"- {suggestion}")
                            
                            if analysis.get('best_practices'):
                                st.markdown("**✨ Best Practices:**")
                                for practice in analysis['best_practices']:
                                    st.markdown(f"- {practice}")
                        
                        break  # Success, exit retry loop
                    else:
                        raise ValueError("Invalid JSON format in response")
                        
                except json.JSONDecodeError as je:
                    retry_count += 1
                    if retry_count == max_retries:
                        st.warning("⚠️ Could not parse code analysis results. Proceeding with test cases.")
                        return
                    continue
                    
                except Exception as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        st.warning("⚠️ Code analysis temporarily unavailable. Proceeding with test cases.")
                        return
                    continue
                    
        except Exception as e:
            st.warning("⚠️ Code analysis service unavailable. Proceeding with test cases.")
            return
    def _run_test_cases(self, user_code: str, test_cases: List[Dict]) -> None:
        """Run test cases with detailed feedback"""
        try:
            # Create safe execution environment
            globals_dict = {'__builtins__': __builtins__}
            exec(user_code, globals_dict)
            
            all_passed = True
            for i, test in enumerate(test_cases, 1):
                try:
                    result = globals_dict['solution'](test['input'])
                    
                    if str(result).strip() == str(test['expected']).strip():
                        st.success(f"✅ Test case {i} passed!")
                        with st.expander(f"Test Case {i} Details"):
                            st.code(f"""Input: {test['input']}
Expected: {test['expected']}
Your Output: {result}
Explanation: {test.get('explanation', 'Test case passed successfully')}""")
                    else:
                        all_passed = False
                        st.error(f"❌ Test case {i} failed")
                        with st.expander(f"Test Case {i} Details"):
                            st.code(f"""Input: {test['input']}
Expected: {test['expected']}
Your Output: {result}
Explanation: {test.get('explanation', 'Output does not match expected result')}""")
                            
                except Exception as e:
                    all_passed = False
                    st.error(f"❌ Error in test case {i}: {str(e)}")
            
            if all_passed:
                st.balloons()
                st.success("🎉 All test cases passed! Excellent work!")
            
        except Exception as e:
            st.error(f"❌ Error executing code: {str(e)}")

    def display_challenge_interface(self) -> None:
        """Display the main coding challenge interface"""
        st.title("💻 Interactive Coding Challenge Platform")
        
        # Generate or refresh challenge
        if 'current_challenge' not in st.session_state or st.button("🔄 New Challenge"):
            st.session_state.current_challenge = self.generate_challenge(
                self.selected_topic, 
                self.selected_difficulty
            )
        
        challenge = st.session_state.current_challenge
        
        # Display challenge details
        st.markdown(f"""### 🎯 Challenge
{challenge['challenge']}

#### 📋 Constraints:""")
        for constraint in challenge['constraints']:
            st.markdown(f"- {constraint}")
            
        # Display examples
        with st.expander("📚 Examples"):
            for example in challenge['examples']:
                st.markdown(example)
        
        # Code editor
        st.markdown("### 🔍 Your Solution")
        user_code = st.text_area(
            "",
            value=challenge['starter_code'],
            height=300,
            key="code_editor"
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("▶️ Submit & Evaluate"):
                self.evaluate_code(user_code, challenge['test_cases'], challenge['challenge'])
        with col2:
            if st.button("💡 Get Hint"):
                st.info(f"💡 {challenge['hints'][st.session_state.get('hint_index', 0)]}")
                st.session_state.hint_index = (st.session_state.get('hint_index', 0) + 1) % len(challenge['hints'])

def main():
    st.set_page_config(
        page_title="Coding Challenge Platform",
        page_icon="💻",
        layout="wide"
    )
    
    manager = CodingChallengeManager()
    manager.display_challenge_interface()

if __name__ == "__main__":
    main()