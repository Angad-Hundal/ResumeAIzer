import os
from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import END, StateGraph
from huggingface_hub import InferenceClient
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import logging
import re

# # Load environment variables
# env_path = Path(__file__).resolve().parents[2] / '.env'

# print(f"Loading environment variables from {env_path}")
# if not env_path.exists():
#     raise FileNotFoundError(f"Environment file not found at {env_path}")

# load_dotenv(env_path)
logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    resume_text: str
    job_description: str
    market_trends: Optional[str]
    analysis: Optional[str]
    critique: Optional[str]
    iterations: int
    satisfaction_score: Optional[float]
    last_error: Optional[str]

class MultiModelResumeAnalyzer:
    def __init__(self):
        self.max_iterations = 3
        self.satisfaction_threshold = 65  # 65% acceptance threshold
    
        try:
            # Initialize clients for different providers
            self.hf_novita_client = InferenceClient(
                provider="novita",
                api_key=os.getenv("HUGGINGFACE_API_KEY")
            )

            self.hf_featherless_ai_client = InferenceClient(
                provider="featherless-ai",
                api_key=os.getenv("HUGGINGFACE_API_KEY")
            )
            
            self.hf_cerebras_client = InferenceClient(
                provider="cerebras",
                api_key=os.getenv("HUGGINGFACE_API_KEY")
            )

            self.hf_router_client = InferenceClient(
                provider="fal-ai",
                api_key=os.getenv("HUGGINGFACE_API_KEY")
            )
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face clients: {str(e)}")
            raise RuntimeError("Hugging Face clients could not be initialized. Check your API key and network connection.")


    async def get_market_trends(self, job_description: str) -> str:
        """Agent to fetch current market trends using Kimi model"""
        try:
            response = self.hf_novita_client.chat.completions.create(
                model="moonshotai/Kimi-K2-Instruct",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a market research analyst with access to real-time hiring data. Provide current hiring trends, salary benchmarks, and in-demand skills for this role based on the job description."
                    },
                    {
                        "role": "user",
                        "content": f"""Analyze current market trends for this role:
                        
                        Job Description:
                        {job_description}

                        Provide:
                        1. Top 5 in-demand skills
                        2. Salary range benchmarks
                        3. Hiring trends by region
                        4. Emerging technologies in this field
                        5. Competitive landscape"""
                    }
                ],
                temperature=0.3,
                max_tokens=1024
            )
            return {"market_trends": response.choices[0].message.content}
        except Exception as e:
            logger.error(f"Error fetching market trends: {str(e)}")
            return {"market_trends": None, "last_error": str(e)}

    async def analyze_resume(self, state: AgentState) -> Dict[str, Any]:
        """Analyze resume using Qwen model"""

        print("GETTING INTO ANALYZE RESUME FUNCTION ")

        try:

            if not state['market_trends']:
                raise ValueError("Market trends not available")
            
            response = self.hf_novita_client.chat.completions.create(
                model="Qwen/Qwen3-235B-A22B-Thinking-2507",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert resume analyst with 10+ years experience in technical recruiting. 
                        Analyze how well the resume matches the job requirements considering:
                        - Technical skills match
                        - Experience relevance
                        - Education/certifications
                        - Soft skills alignment
                        - Cultural fit indicators"""
                    },
                    {
                        "role": "user",
                        "content": f"""
                        JOB REQUIREMENTS:
                        {state['job_description']}
                        
                        MARKET CONTEXT:
                        {state['market_trends']}
                        
                        RESUME CONTENT:
                        {state['resume_text']}
                        
                        Provide detailed analysis with:
                        1. Skill match percentage (0-100%)
                        2. Key strengths for this role
                        3. Critical gaps
                        4. Improvement recommendations
                        5. Overall fit assessment"""
                    }
                ],
                temperature=0.2,
                max_tokens=2048
            )
            return {"analysis": response.choices[0].message.content}
        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            return {"analysis": None, "last_error": str(e)}
        

    async def critique_analysis(self, state: AgentState) -> Dict[str, Any]:
        """Critique the analysis using Nemotron model"""

        print("GETTING INTO CRITIQUE ANALYSIS FUNCTION ")

        try:
            if not state['analysis']:
                raise ValueError("Analysis not available")
            
            response = self.hf_featherless_ai_client.chat.completions.create(
                model="nvidia/OpenReasoning-Nemotron-32B",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a senior hiring director with 15+ years experience. 
                        Perform rigorous quality control on resume analyses by checking:
                        - Accuracy of skill assessments
                        - Market relevance of recommendations
                        - Depth of gap analysis
                        - Practicality of suggestions
                        - Bias detection"""
                    },
                    {
                        "role": "user",
                        "content": f"""
                        JOB DESCRIPTION:
                        {state['job_description']}
                        
                        MARKET TRENDS:
                        {state['market_trends']}
                        
                        RESUME ANALYSIS TO REVIEW:
                        {state['analysis']}
                        
                        Provide structured feedback:
                        1. Accuracy score (1-5)
                        2. Missing critical elements
                        3. Market alignment issues
                        4. Suggested analysis improvements
                        5. Final verdict on analysis quality"""
                    }
                ],
                temperature=0.1,
                max_tokens=2048
            )
            return {"critique": response.choices[0].message.content}
        except Exception as e:
            logger.error(f"Error critiquing analysis: {str(e)}")
            return {"critique": None, "last_error": str(e)}

    async def is_satisfactory(self, state: AgentState) -> str:
        """Use Llama-3 to determine if analysis meets quality threshold"""
        if state['iterations'] >= self.max_iterations:
            logger.info("Max iterations reached, ending workflow")
            return "end"
        
        try:
            if not state['critique']:
                raise ValueError("No critique available for evaluation")
            
            # Get satisfaction score from LLM
            response = self.hf_cerebras_client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a quality assessment AI. Analyze the critique and 
                        determine a satisfaction percentage (0-100) for the resume analysis quality.
                        Respond ONLY with the number."""
                    },
                    {
                        "role": "user",
                        "content": f"""Critique to evaluate:
                        {state['critique']}
                        
                        What percentage (0-100) indicates satisfaction with this analysis?
                        Respond ONLY with the number:"""
                    }
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            # Extract numeric score from response
            score_text = response.choices[0].message.content
            score = float(re.search(r'\d+', score_text).group())
            state['satisfaction_score'] = score
            
            logger.info(f"Satisfaction score: {score}% (Threshold: {self.satisfaction_threshold}%)")
            return "end" if score >= self.satisfaction_threshold else "continue"
            
        except Exception as e:
            logger.error(f"Error calculating satisfaction score: {str(e)}")
            return "continue"
    
    async def process_resume(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Orchestrate the multi-agent analysis process"""
        try:
            initial_state = AgentState(
                resume_text=resume_text,
                job_description=job_description,
                market_trends=None,
                analysis=None,
                critique=None,
                iterations=0,
                satisfaction_score=None,
                last_error=None
            )
            
            workflow = self._build_workflow()
            app = workflow.compile()
            final_state = await app.ainvoke(initial_state)
            
            return self._prepare_final_result(final_state)
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "iterations": initial_state.get('iterations', 0)
            }

    def _build_workflow(self) -> StateGraph:
        """Construct the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        workflow.add_node("get_market_trends", self.get_market_trends)
        workflow.add_node("analyze_resume", self.analyze_resume)
        workflow.add_node("critique_analysis", self.critique_analysis)
        
        workflow.add_edge("get_market_trends", "analyze_resume")
        workflow.add_edge("analyze_resume", "critique_analysis")
        
        workflow.add_conditional_edges(
            "critique_analysis",
            self.is_satisfactory,
            {"continue": "analyze_resume", "end": END}
        )
        
        workflow.set_entry_point("get_market_trends")
        return workflow
    
    def _prepare_final_result(self, state: AgentState) -> Dict[str, Any]:
        """Prepare the final result dictionary"""
        print(f"Preparing final result with state: {state}")
        logger.info(f"Preparing final result with state: {state}")
        result = {
            "analysis": state.get('analysis'),
            "critique": state.get('critique'),
            "market_trends": state.get('market_trends'),
            "iterations": state.get('iterations', 0),
            "satisfaction_score": state.get('satisfaction_score'),
            "status": "success"
        }
        
        if state.get('last_error'):
            result.update({
                "status": "partial_success",
                "warning": state['last_error']
            })
            
        return result