import os
from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import END, StateGraph
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from dotenv import load_dotenv
from pathlib import Path
import logging
import re
import sys
import asyncio

# Load environment variables
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True 
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class AgentState(TypedDict):
    resume_text: str
    job_description: str
    market_trends: Optional[str]
    analysis: Optional[str]
    critique: Optional[str]
    iterations: int
    satisfaction_score: Optional[float]
    last_error: Optional[str]

class GitHubMultiModelAnalyzer:
    def __init__(self):
        self.max_iterations = 1
        self.satisfaction_threshold = 65  # 65% acceptance threshold

        self.api_base = "https://models.github.ai/inference"  
        self.api_key = os.getenv("GITHUB_TOKEN")
        if not self.api_key:
            raise ValueError("GitHub API key not configured")
        
        self.github_model_client = ChatCompletionsClient(
            endpoint=self.api_base,
            credential=AzureKeyCredential(self.api_key)
        )
    
    def _exit_with_error(self, error_message: str):
        """Exit the program with rrro and the error message"""
        logger.error(f"Critical error: {error_message}")
        print(f"rrro: {error_message}")
        sys.exit(1)

    async def get_market_trends(self, state) -> str:
        """Agent to fetch current market trends using GitHub-hosted GPT-4.1"""
        try:
            print(f"Fetching market trends for job description")
            logger.info(f"Fetching market trends for job description")
            job_description = state["job_description"]
            response = self.github_model_client.complete(
                messages=[
                    SystemMessage("You are a market research analyst with access to real-time hiring data."),
                    UserMessage(f"""Analyze current market trends for this role:
                            
                            Job Description:
                            {job_description}

                            Provide:
                            1. Top 5 in-demand skills
                            2. Salary range benchmarks
                            3. Hiring trends by region
                            4. Emerging technologies in this field
                            5. Competitive landscape""")
                ],
                temperature=0.3,
                model="openai/gpt-4.1"
            )
        
            print(f"Market trends response")
            logger.info(f"Market trends response")
            return {**state,"market_trends": response.choices[0].message.content}
            
        except Exception as e:
            logger.error(f"Error fetching market trends: {str(e)}")
            return {**state, "market_trends": None, "last_error": str(e)}

    async def analyze_resume(self, state: AgentState) -> Dict[str, Any]:
        """Analyze resume using GitHub-hosted GPT-4.1"""
        try:
            if not state['market_trends']:
                raise ValueError("Market trends not available")
            
            print(f"Analyzing resume with text")
            logger.info(f"Analyzing resume with text")


            response = self.github_model_client.complete(
                messages=[
                    SystemMessage("You are an expert resume analyst with 10+ years experience."),
                    UserMessage(f"""
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
                            5. Overall fit assessment""")
                ],
                temperature=0.2,
                model="openai/gpt-4.1"
            )
            
                
            return {**state, "analysis": response.choices[0].message.content}
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            return {**state, "analysis": None, "last_error": str(e)}

    async def critique_analysis(self, state: AgentState) -> Dict[str, Any]:
        """Critique the analysis using GitHub-hosted DeepSeek-R1"""
        try:
            if not state['analysis']:
                raise ValueError("Analysis not available")
            
            print(f"Critiquing analysis")
            logger.info(f"Critiquing analysis")
            
            response = self.github_model_client.complete(
                messages=[
                    SystemMessage("You are a senior hiring director with 15+ years experience."),
                    UserMessage(f"""
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
                            5. Final verdict on analysis quality""")
                ],
                temperature=0.1,
                model="openai/gpt-4.1",
                max_tokens=2048
            )
                
            return {**state, "critique": response.choices[0].message.content}
            
        except Exception as e:
            logger.error(f"Error critiquing analysis: {str(e)}")
            return {**state, "critique": None, "last_error": str(e)}

    async def is_satisfactory(self, state: AgentState) -> str:
        """Determine if analysis meets quality threshold"""
        if state.get('iterations', 0) >= self.max_iterations:
            logger.info("Max iterations reached, ending workflow")
            return {
                **state,  # Preserve all fields
                "decision": "end"  # LangGraph expects this key
                }
        print(f"Evaluating satisfaction with critique")
        logger.info(f"Evaluating satisfaction with critique")

        try:

            print(f"Evaluating satisfaction with critique inside try block")
            logger.info(f"Evaluating satisfaction with critique inside try block")

            if not state['critique']:
                raise ValueError("No critique available for evaluation")
            
            # Get satisfaction score from LLM
            messages=[
                SystemMessage("""You are a quality assessment AI. Analyze the critique and 
                        determine a satisfaction percentage (0-100). Respond ONLY with the number."""),
                UserMessage(f"""Critique to evaluate:
                        {state['critique']}
                        
                        What percentage (0-100) indicates satisfaction?
                        Respond ONLY with the number:""")
            ]

            print(f"Evaluating satisfaction with messages")
            response = self.github_model_client.complete(messages=messages,
            temperature=0.1,
            model="openai/gpt-4.1",
            max_tokens=2048)
            if not response or not response.choices or not response.choices[0].message:
                raise ValueError("Invalid or empty response from LLM")
            
                
            # Extract numeric score from response
            score_text = response.choices[0].message.content
            if not score_text:
                raise ValueError("Empty response content")
            
            match = re.search(r'\d+', score_text)
            if not match:
                raise ValueError(f"No numeric score found in response: '{score_text}'")
            
            score = float(match.group())

            if not (0 <= score <= 100):
                raise ValueError(f"Score out of range (0-100): {score}")
            
            state['satisfaction_score'] = score
        
            logger.info(f"Satisfaction score: {score}% (Threshold: {self.satisfaction_threshold}%)")

            if score >= self.satisfaction_threshold:
                logger.info("Satisfaction threshold met, ending workflow")
                return "end"
            else:
                logger.info("Satisfaction threshold not met, continuing workflow")
                state['iterations'] = state.get('iterations', 0) + 1
                return "continue"
            
        except Exception as e:
            logger.error(f"Error calculating satisfaction score: {str(e)}")
            state['last_error'] = f"Satisfaction score evaluation failed: {str(e)}"
            state['satisfaction_score'] = None
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
            
            workflow = StateGraph(AgentState)
            
            workflow.add_node("get_market_trends", self.get_market_trends)
            workflow.add_node("analyze_resume", self.analyze_resume)
            workflow.add_node("critique_analysis", self.critique_analysis)
            
            workflow.add_edge("get_market_trends", "analyze_resume")
            workflow.add_edge("analyze_resume", "critique_analysis")
            
            workflow.add_conditional_edges(
            "critique_analysis",
            self.is_satisfactory,
            {
                "continue": "analyze_resume",
                "end": END
            }
        )
            
            workflow.set_entry_point("get_market_trends")
            app = workflow.compile()
            
            final_state = await app.ainvoke(initial_state)
            
            return self._prepare_final_result(final_state)
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "iterations": final_state.get('iterations', 0)
            }

    def _prepare_final_result(self, state: AgentState) -> Dict[str, Any]:
        """Prepare the final result dictionary"""
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
            
        print(f"Final result prepared: {result}")
        logger.info(f"Final result prepared: {result}")
        return result