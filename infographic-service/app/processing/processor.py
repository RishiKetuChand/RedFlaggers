import logging
import uuid
import asyncio
import re
import json
from datetime import datetime
from typing import Dict, Any, List

from ..agent.agent import create_infographic_agents, AgentRunner
from ..config.settings import settings
from ..utils.image_generator import ImageGenerator

logger = logging.getLogger(__name__)


class InfographicProcessor:
    def __init__(self):
        self.max_workers = settings.service.max_workers
        self.timeout = settings.service.timeout_seconds
        self.agent_runner = AgentRunner(
            app_name=settings.agent.app_name,
            user_id=settings.agent.user_id,
            session_id_prefix=settings.agent.session_id_prefix
        )
        self.image_generator = ImageGenerator()

    async def process_infographic_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process infographic request with sections processed sequentially"""
        request_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        logger.info(f"Processing infographic request {request_id} for startup: {request_data.get('startup_name')}")
        
        try:
            rag_corpus = request_data['rag_corpus']
            startup_name = request_data['startup_name']
            upload_id = request_data['upload_id']
            gcp_bucket = settings.gcp.bucket_name
            sections = self._define_infographic_sections(startup_name)
            print("Got sections") 
            # Process sections sequentially (one at a time)
            results = {}
            for section in sections:
                logger.info(f"Processing section: {section['name']} for {startup_name}")
                try:
                    result = await self._process_section_async(
                        rag_corpus,
                        startup_name,
                        section['name'],
                        section['prompt']
                    )
                    results[section['name']] = result
                    logger.info(f"Completed section: {section['name']}")
                except Exception as e:
                    logger.error(f"Error processing section {section['name']}: {str(e)}")
                    results[section['name']] = {"error": str(e)}

            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()
            
            # Prepare infographic data for PDF generation
            infographic_data = {
                "request_id": request_id,
                "service_name": "infographic-service",
                "startup_name": startup_name,
                "gcp_bucket": gcp_bucket,
                "upload_id": upload_id,
                "status": "completed",
                "timestamp": end_time.isoformat(),
                "processing_time_seconds": processing_time,
                "results": results,
                "sections_processed": len(results),
                "successful_sections": len([r for r in results.values() if "error" not in r])
            }
            
            # Generate PDF and upload to cloud storage
            try:
                logger.info(f"Generating PDF report for {startup_name}")
                pdf_url = self.image_generator.process_infographic_to_images_url(infographic_data, gcp_bucket,upload_id)
                infographic_data["pdf_url"] = pdf_url
                logger.info(f"PDF report generated and uploaded: {pdf_url}")
            except Exception as e:
                logger.error(f"Failed to generate PDF report: {str(e)}")
                infographic_data["pdf_error"] = str(e)
                # Continue without PDF - don't fail the entire process
            
            return infographic_data

        except Exception as e:
            logger.error(f"Failed to process infographic request {request_id}: {str(e)}")
            return {
                "request_id": request_id,
                "startup_name": request_data.get('startup_name', 'unknown'),
                "status": "error",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }

    def _define_infographic_sections(self, startup_name: str) -> List[Dict[str, str]]:
        """Define the infographic sections to be processed"""
        return [
            {
                "name": "product",
                "prompt": f"""You are a precision extractor that ONLY uses the RAG tool to read company materials {startup_name} and produce structured facts. Do not invent or infer beyond sources.
				Using ONLY RAG results, produce a concise product overview for the startup {startup_name}. Focus on the product the startup has built (not the company biography). If information for any field is not found in RAG, set that field's value to Not Found (do NOT guess).

                Definitions & Guidance:
                - "problem": The core customer pain the product addresses.
                - "problem_category": The broader category/type of problem (e.g., "manual invoice reconciliation in mid-market finance ops"), not a solution.
                - "Current alternatives": What users do today (status quo, competitors, internal tools, spreadsheets).
                - "why now": Time-sensitive drivers (tech shifts, regulation, cost curves, ecosystem changes).
                - "Product details": What the product is, what it does, how it works, and key differentiators—factual only.
                - "Replacement for": The primary tool/process the product aims to displace.

                Output Format:
                Return ONLY a single JSON object with EXACTLY these keys and value length targets (count words, not characters). Do not include comments, explanations, markdown, or trailing text.

                {{
                "problem": "<40–50 words>",
                "problem_category": "<20–25 words>",
                "current_alternatives": "<30–40 words>",
                "why_now": "<20–25 words>",
                "product_details": "<50 - 70words>",
                "replacement_for": "<15–20 words>"
                }}

                Example: 
                {{
                "problem": "Hospitals struggle with keeping patients engaged after discharge, leading to poor medication adherence, missed follow-up appointments, and higher readmission rates. Manual outreach is inefficient, resource heavy, and fails to provide timely intervention for patients who urgently need guidance and support.",
                "problem_category": "Patient engagement and post-discharge care inefficiency in hospital and clinical healthcare systems.",
                "current_alternatives": "Hospitals rely on phone call reminders, generic text notifications, or manual nurse-led follow-up programs. These methods are inconsistent, lack personalization, and often fail to identify high-risk patients early enough to prevent costly hospital readmissions.",
                "why_now": "Telemedicine adoption, healthcare digitization, and value-based care policies make proactive patient engagement and AI-driven follow-up extremely timely and essential.",
                "product_details": "MediLink Health provides an AI-powered patient engagement platform that integrates with hospital systems to track discharged patients, analyze risk factors, and automate personalized outreach via SMS, WhatsApp, or calls. It uses predictive analytics to highlight patients likely to miss medications or appointments, helping providers reduce readmissions and improve health outcomes significantly.",
                "replacement_for": "Manual follow-up calls and generic reminder systems."
                }}


                Validation:
                - Before finalizing, re-count words per field and adjust to fit the required ranges.
                - Ensure valid JSON (double quotes, escaped characters).
				"""
            },
            {
                "name": "financial_metric",
                "prompt": f"""You are a precision financial analyst agent. Your task is to generate a structured financial metrics report for the startup {startup_name}. 
                You must ONLY use the RAG tool as your primary data source. Do not hallucinate. 
                If financial details are not available, return Not Found for that section.

                Extract key financial insights and return a structured JSON with exactly these fields:

                {{
                "overview": "<40–50 words summary of the company’s financial standing, funding history, and general financial health>",
                "growth_rate": "<20–30 words, focus on revenue growth, user growth, or traction metrics>",
                "capital_efficiency": "<25–35 words on how effectively the company uses capital to drive growth, burn multiple, or return on investment>",
                "valuation": "<20–30 words on most recent or estimated valuation, investors’ perception, and context if available>",
                "analysis": "<40–60 words detailed assessment including strengths, weaknesses, opportunities, and risks>",
                "profitability_margin": "<25–35 words focusing on revenue model sustainability, gross margin, net margin, or breakeven status>"
                }}

                Strict Rules:
                1. Use only RAG tool. If a metric is unavailable, return Not Found.
                2. Respect word-count ranges for each field.
                3. Output valid JSON only — no markdown, no extra text.
                4. No speculation.
                5. Keep sentences factual and concise.

                Example:
                {{
                "overview": "FinOptima is a fintech platform helping SMEs manage cash flow with AI-driven forecasting. The company has raised Series B funding and reports strong user adoption across India with steady financial growth supported by institutional investors.",
                "growth_rate": "Revenue has grown consistently at over 40% annually, supported by rapid SME onboarding and increased usage of subscription-based financial analytics services.",
                "capital_efficiency": "FinOptima maintains disciplined capital allocation with a burn multiple below industry averages, achieving high customer acquisition efficiency relative to invested capital.",
                "valuation": "The latest Series B round valued FinOptima at approximately $250 million, reflecting strong investor confidence in its growth potential and market expansion plans.",
                "analysis": "Financials indicate strong recurring revenue, attractive gross margins, and disciplined spending. However, dependency on SME credit adoption and regulatory changes could pose challenges. Long-term growth opportunities remain significant in underserved markets across emerging economies.",
                "profitability_margin": "Gross margins are around 68%, with improving unit economics. The company has not reached net profitability but is on track to breakeven within 18–24 months."
                }}
				"""
            }
        ]

    async def _process_section_async(self, rag_corpus: str, startup_name: str, section_name: str, prompt: str) -> dict:
        """Process a single infographic section asynchronously and return JSON"""
        try:
            logger.info(f"Processing section: {section_name} for {startup_name}")
    
            agent = create_infographic_agents(rag_corpus, settings.service.model_name)
    
            result = await self.agent_runner.call_agent_async(prompt, agent)
    
            # Clean fenced code block markers (```json ... ```)
            cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", result.strip(), flags=re.DOTALL)
    
            # Try parsing into JSON
            try:
                parsed = json.loads(cleaned)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON for section {section_name}, returning as string. Error: {e}")
                parsed = {"raw_output": cleaned}
    
            return parsed
    
        except Exception as e:
            logger.error(f"Error processing section {section_name}: {str(e)}")
            return {"error": str(e)}
