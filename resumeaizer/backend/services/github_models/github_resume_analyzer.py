import os
from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import END, StateGraph
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference import ChatCompletionsClient
from dotenv import load_dotenv
from pathlib import Path
import logging
import re
import asyncio

# Load environment variables
load_dotenv()
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

class GitHubMultiModelAnalyzer:
    def __init__(self):
        self.max_iterations = 3
        self.satisfaction_threshold = 65  # 65% acceptance threshold

        self.api_base = "https://models.github.ai/inference"  
        self.api_key = os.getenv("GITHUB_TOKEN")
        if not self.api_key:
            raise ValueError("GitHub API key not configured")
        
        self.github_model_client = ChatCompletionsClient(
            endpoint=self.api_base,
            credential=AzureKeyCredential(self.api_key)
        )
    

    async def get_market_trends(self, job_description: str) -> str:
        """Agent to fetch current market trends using GitHub-hosted GPT-4.1"""
        try:
            response = await self.github_model_client.path("/chat/completions").post({
                "body": {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a market research analyst with access to real-time hiring data."
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
                    "temperature": 0.3,
                    "model": "openai/gpt-4.1"
                }
            })
            
            if response.status_code != 200:
                raise ValueError(f"API request failed with status {response.status_code}")
                
            return {"market_trends": response.json()["choices"][0]["message"]["content"]}
            
        except Exception as e:
            logger.error(f"Error fetching market trends: {str(e)}")
            return {"market_trends": None, "last_error": str(e)}

    async def analyze_resume(self, state: AgentState) -> Dict[str, Any]:
        """Analyze resume using GitHub-hosted GPT-4.1"""
        try:
            if not state['market_trends']:
                raise ValueError("Market trends not available")
            
            response = await self.github_model_client.path("/chat/completions").post({
                "body": {
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are an expert resume analyst with 10+ years experience."""
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
                    "temperature": 0.2,
                    "model": "openai/gpt-4.1"
                }
            })
            
            if response.status_code != 200:
                raise ValueError(f"API request failed with status {response.status_code}")
                
            return {"analysis": response.json()["choices"][0]["message"]["content"]}
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            return {"analysis": None, "last_error": str(e)}

    async def critique_analysis(self, state: AgentState) -> Dict[str, Any]:
        """Critique the analysis using GitHub-hosted DeepSeek-R1"""
        try:
            if not state['analysis']:
                raise ValueError("Analysis not available")
            
            response = await self.github_model_client.path("/chat/completions").post({
                "body": {
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are a senior hiring director with 15+ years experience."""
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
                    "temperature": 0.1,
                    "model": "deepseek/DeepSeek-R1",
                    "max_tokens": 2048
                }
            })
            
            if response.status_code != 200:
                raise ValueError(f"API request failed with status {response.status_code}")
                
            return {"critique": response.json()["choices"][0]["message"]["content"]}
            
        except Exception as e:
            logger.error(f"Error critiquing analysis: {str(e)}")
            return {"critique": None, "last_error": str(e)}

    async def is_satisfactory(self, state: AgentState) -> str:
        """Determine if analysis meets quality threshold"""
        if state['iterations'] >= self.max_iterations:
            logger.info("Max iterations reached, ending workflow")
            return "end"
        
        try:
            if not state['critique']:
                raise ValueError("No critique available for evaluation")
            
            # Get satisfaction score from LLM
            response = await self.github_model_client.path("/chat/completions").post({
                "body": {
                    "messages": [
                        {
                            "role": "system",
                            "content": """You are a quality assessment AI. Analyze the critique and 
                            determine a satisfaction percentage (0-100). Respond ONLY with the number."""
                        },
                        {
                            "role": "user",
                            "content": f"""Critique to evaluate:
                            {state['critique']}
                            
                            What percentage (0-100) indicates satisfaction?
                            Respond ONLY with the number:"""
                        }
                    ],
                    "temperature": 0.1,
                    "model": "deepseek/DeepSeek-R1",
                    "max_tokens": 10
                }
            })
            
            if response.status_code != 200:
                raise ValueError(f"API request failed with status {response.status_code}")
                
            # Extract numeric score from response
            score_text = response.json()["choices"][0]["message"]["content"]
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
            
        return result